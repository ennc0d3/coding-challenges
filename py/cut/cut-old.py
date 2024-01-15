#!/usr/bin/env python3


import argparse
import io
import logging
import re
import sys
from collections.abc import Sequence
from io import BytesIO, IOBase, StringIO
from typing import Any, Dict, Sequence

LOG = logging.getLogger()

PROG = "cut"
VERSION = "0.0.1"
DESCRIPTION = """Print selected parts of lines from each FILE to standard output.


                 With no FILE, or when FILE is -, read standard input.
              """

EPILOG = """
        Use one, and only one of -b, -c or -f.  Each LIST is made up of one
        range, or many ranges separated by commas.  Selected input is written
        in the same order that it is read, and is written exactly once.
        Each range is one of:

        N     N'th byte, character or field, counted from 1
        N-    from N'th byte, character or field, to end of line
        N-M   from N'th to M'th (included) byte, character or field
        -M    from first to M'th (included) byte, character or field
    """

DEFAULT_DELIM = "\t"


def run(args):
    files = args.infiles
    result = process(args, files)
    output(args, result)


def process(args: argparse.Namespace, fileObjs: Sequence[IOBase]) -> Dict[int, Any]:
    result = {}
    linenum = 0
    for fp in fileObjs:
        raw_bytes = fp.read()
        fp.close()
        content = raw_bytes
        if not isinstance(fp, io.TextIOBase):
            content = raw_bytes.decode("utf8")
        if args.bytes:
            content = raw_bytes
            LOG.debug("The raw byte content: %r", raw_bytes)

        for line in content.splitlines():
            LOG.debug("Processing line:", line)
            if args.fields:
                columns = line.split(args.delimiter)
                # Don't include lines that doesn't have delimiters
                if args.only_delimited and len(columns) == 1:
                    continue
                else:
                    result[linenum] = columns
            if args.characters:
                columns = list(line)
                result[linenum] = columns
            if args.bytes:
                result[linenum] = line
            linenum += 1
    return result


def output(args, result):
    args = args
    field_ranges = []
    if args.fields:
        field_ranges = normalize_field_ranges(args.fields)
        LOG.debug(">>>THe final FR:", field_ranges)

    if args.characters:
        field_ranges = normalize_field_ranges(args.characters)
        LOG.debug(">>>THe final FR:", field_ranges)

    byte_ranges_array = []

    if args.bytes:
        field_ranges = normalize_field_ranges(args.bytes)
        LOG.debug(">>>THe final FR:", field_ranges)

    buf = StringIO()

    # For fields, the delimiter is applicable, so the result.Values is a list of columns for that particular
    # line, which can be 1 or more columns
    if not args.bytes:
        LOG.debug(
            ">>>>>>>>[[[[[[[[[The result values: %s, type: %s]]]]]]]<<<<<<",
            result.values(),
            type(result),
        )
        for cols in result.values():
            LOG.debug("THe type of colume is %s, value: %s", type(cols), cols)
            for i, fr in enumerate(field_ranges):
                for j in range(fr):
                    LOG.debug(
                        "Print field no: %s, idx: %d, columns: <%r>\n, at idx: <%r>\n",
                        fr,
                        i,
                        cols,
                        cols[j],
                    )
                    if fr[1] <= len(cols):
                        if i > 0:
                            buf.write(f"{args.output_delimiter}")
                        LOG.debug(
                            "Writing to buf, type: %s, data: %s",
                            type(cols),
                            cols[j],
                        )
                        buf.write(f"{cols[j]}")
            buf.write("\n")

        buf.flush()

    if args.bytes:
        outbuf = BytesIO()
        LOG.debug(
            "The number of overalapping ranges array: %s ",
            byte_ranges_array,
        )
        for cols in result.values():
            # print("CCONTENT---", columns)
            for i, num in enumerate(byte_ranges_array):
                LOG.debug(
                    "Print byte end-offset: %d, columns:%r" "bytes[%d:%d]=%r",
                    num,
                    cols,
                    num[0],
                    num[1],
                    cols[num[0] - 1 : num[1]],
                )
                if num[1] <= len(cols):
                    if i > 0:
                        # FIXME: Add the delimiter only in the non-overlaping range
                        LOG.debug("Writing the delimiter to the buffer")
                        outbuf.write(args.output_delimiter.encode())
                    outbuf.write((cols[num[0] - 1 : num[1]]))
            outbuf.write(b"\n")
        outbuf.flush()
        # outbuf.seek(0)
        data = outbuf.getvalue()

        print(data.decode("utf-8", errors="replace"), end="\n")
        # works
    else:
        LOG.debug("Writing to stream")
        print(f"{buf.getvalue()}", end="")
    buf.close()


def merge_intervals(A):
    if not A:
        return []
    A.sort(key=lambda x: x[0])
    LOG.debug("The A: %s", A)
    merged = [A[0]]
    for cur in A[1:]:
        LOG.debug(">>>>>CHecking: %s", merged)
        prev = merged[-1]
        if cur[0] <= prev[1]:
            prev[1] = max(prev[1], cur[1])
        else:
            merged.append(cur)
    print("The merged:", merged)
    return merged


def normalized_merge_intervals(A):
    # this is a list of tuples
    if not A:
        return []
    A.sort(key=lambda x: x[0])
    merged = [A[0]]
    LOG.debug("The input A : %s", A)
    for cur in A[1:]:
        LOG.debug("The cur: %s", cur)
        prev = merged[-1]
        if cur[0] <= prev[1]:
            prev_aslist = list(prev)

            prev_aslist[1] = max(prev[1], cur[1])
            prev = tuple(prev_aslist)
            if prev not in merged:
                merged.append(prev)

        else:
            merged.append(cur)
    LOG.debug("The merged: %s", merged)
    return merged

    # Normalize the tuple pairs to range
    frs = []
    for pair in merged:
        if pair[0] != pair[1]:
            frs.extend(range(pair[0], pair[1] + 1))
        else:
            frs.append(pair[0])

    # Remove duplicates, preserving order
    # normalized_frs = []
    # for i, e in enumerate(frs):
    # if e not in frs[i + 1 :]:
    # normalized_frs.append(e)
    # return normalized_frs


class ListRangeAction(argparse.Action):
    """Parses the comma separated range to list

    Args:
        argparse (_type_): Parse the comma separated range into the namespace option
    """

    def __init__(self, option_strings, dest, **kwargs) -> None:
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, _, namespace, values, option_string=None):
        ranges = []
        if values and isinstance(values, str):
            ranges = values.split(",")

        setattr(namespace, self.dest, ranges)


def normalize_field_ranges(field_ranges):  # -> list[Any]:
    """Given a list of ranges of the form,
    n,m,n-m, n-, -m "n m" ** repeating form
    returns an normalized range of the form ignoring the duplicates and in the
    order of the input.

    [(n,m), (n,n),...]"""
    max_fields = 1 << 16  # FIXME
    intervals = []
    out_field_ranges = []
    LOG.debug("The input field ranges: <%s>", field_ranges)
    for field_range in field_ranges:
        LOG.debug("Field-Range: %s", field_range)
        if " " in field_range:
            indices = field_range.split()
            out_field_ranges.append(tuple(**indices))

        elif "-" in field_range:
            indices = field_range.split("-")
            if len(indices) > 2:
                print("cut: invalid field range")
                sys.exit(2)
            start, end = 1, max_fields
            if len(indices[0]):
                start = int(indices[0])
            if len(indices[1]):
                end = int(indices[1])
            out_field_ranges.append((start, end))

        elif re.search(r"\d+", field_range):
            out_field_ranges.append((int(field_range), int(field_range)))

    LOG.debug("The sections to print : %s", out_field_ranges)
    intervals = normalized_merge_intervals(out_field_ranges)
    LOG.debug("The ranges to print : %s", intervals)
    return intervals


def getargs():
    parser = argparse.ArgumentParser(
        prog=PROG,
        usage="%(prog)s OPTION... [FILE]...",
        description=DESCRIPTION,
        epilog=EPILOG,
    )
    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "-b",
        "--bytes",
        action=ListRangeAction,
        metavar="LIST",
        type=str,
        help="select only these bytes",
    )
    group.add_argument(
        "-c",
        "--characters",
        action=ListRangeAction,
        metavar="LIST",
        type=str,
        help="""select only these characters
             (is same not same as bytes option, it understands utf-8)""",
    )
    group.add_argument(
        "-f",
        "--fields",
        action=ListRangeAction,
        metavar="LIST",
        type=str,
        help="""Select only these fields; also print any line
                that contains no delimiter character, unless
                the -s option is specified""",
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        action="store",
        default=DEFAULT_DELIM,
        help="Use DELIM instead of TAB for field delimiter",
    )
    parser.add_argument(
        "-s",
        "--only-delimited",
        action="store_true",
        help="do not print lines not containing delimiters, Only applicable in case of fields option",
    )
    parser.add_argument(
        "--output-delimiter",
        action="store",
        type=str,
        default="",
        help="""use STRING as the output delimiter
                the default is to use the input delimter""",
    )
    parser.add_argument(
        "-z",
        "--zero-terminated",
        action="store_true",
        help="line delimiter is NUL, not newline",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=" ".join(["%(prog)s", VERSION]),
        help="output the version and exit",
    )

    parser.add_argument(
        "infiles",
        nargs="*",
        metavar="FILE",
        type=argparse.FileType("rb"),
        default=[sys.stdin],
        help="The name of the input files",
    )

    # Debug options
    parser.add_argument(
        "-v",
        "--verbose",
        default=0,
        action="count",
        help="Increase the verbosity",
    )

    args = parser.parse_args()

    if args.delimiter != DEFAULT_DELIM and any([args.bytes, args.characters]):
        parser.error(
            "an input delimiter may be specified only when operating on fields"
        )

    # By default the input delimiter is used for output_delimiter
    if not args.output_delimiter:
        args.output_delimiter = args.delimiter if args.fields else ""  # FIXME:

    return args


def setup_logging(args):
    LOG = logging.getLogger()
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    ch.setLevel(logging.DEBUG)
    LOG.addHandler(ch)
    logLevel = logging.WARN
    if args.verbose == 1:
        logLevel = logging.INFO
    elif args.verbose > 1:
        logLevel = logging.DEBUG
    LOG.setLevel(logLevel)
    LOG.info("Setup logger")


def main():
    args = getargs()
    setup_logging(args)
    LOG.info("Starting %s", PROG)
    run(args)


if __name__ == "__main__":
    main()
