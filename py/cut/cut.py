#!/usr/bin/env python3


import argparse
import logging
import re
import sys
import textwrap
from ast import Tuple

LOG = logging.getLogger()

PROG = "cut"
VERSION = "0.0.1"

DESCRIPTION = textwrap.dedent(
    """
    Print selected parts of lines from each FILE to standard output.

    With no FILE, or when FILE is -, read standard input.
    """
)

EPILOG = textwrap.dedent(
    """
        Use one, and only one of -b, -c or -f.  Each LIST is made up of one
        range, or many ranges separated by commas.  Selected input is written
        in the same order that it is read, and is written exactly once.
        Each range is one of:

            N     N'th byte, character or field, counted from 1
            N-    from N'th byte, character or field, to end of line
            N-M   from N'th to M'th (included) byte, character or field
             -M   from first to M'th (included) byte, character or field
        """
)

DEFAULT_DELIM = "\t"


def run(args):
    process(args)


def process(args: argparse.Namespace):
    LOG.debug("Processing, %s ", args)

    for fileobj in args.infiles:
        data = fileobj.read()
        if not args.bytes:
            if isinstance(data, bytes):
                data = data.decode("utf-8")

        for line in data.splitlines():
            fields = []

            if args.fields:
                fields = line.split(args.delimiter)

                if args.only_delimited and len(fields) == 1:
                    continue

                for idx, (start, end) in enumerate(args.fields):
                    end = min(end, len(fields))
                    delim = args.output_delimiter
                    if idx == len(args.fields) - 1 or end >= len(fields):
                        delim = ""

                    print(
                        *fields[start - 1 : end],
                        sep=args.output_delimiter,
                        end=delim,
                    )

            elif args.characters:
                fields = list(line)
                delim = args.output_delimiter
                for idx, (start, end) in enumerate(args.characters):
                    end = min(end, len(fields))
                    if idx == len(args.characters) - 1 or end >= len(fields):
                        delim = ""
                    if len(fields[start - 1 : end]) > 0:
                        print(*fields[start - 1 : end], sep="", end=delim)

            elif args.bytes:
                fields = line
                delim = args.output_delimiter
                for idx, (start, end) in enumerate(args.bytes):
                    if idx == len(args.bytes) - 1:
                        delim = ""
                    # FIXME: Just print the raw bytes and leave the decoding to terminal?
                    print(
                        str(
                            fields[start - 1 : end], encoding="utf-8", errors="replace"
                        ),
                        sep="",
                        end=delim,
                    )

            print()


def normalize_list_ranges(field_ranges) -> list[Tuple]:
    r = []
    for field_range in field_ranges:
        if " " in field_range:
            indices = field_range.split()
            r.append(list(**indices))

        elif "-" in field_range:
            max_fields = 1 << 16
            indices = field_range.split("-")
            if len(indices) > 2:
                raise InvalidFieldRangeValueError(
                    f"cut: invalid field range '{field_range}'"
                )
            start, end = 1, max_fields
            if len(indices[0]):
                start = int(indices[0])
            if len(indices[1]):
                end = int(indices[1])
            if start > end:
                raise InvalidFieldRangeValueError("invalid decreasing range")
            r.append([start, end])

        elif re.search(r"\d+", field_range):
            try:
                v = int(field_range)
                r.append([v, v])
            except ValueError as e:
                LOG.debug(e)
                raise InvalidFieldRangeValueError(
                    f"cut: invalid field value '{field_range}'"
                )

    LOG.debug("The normalized interval: %s", r)
    intervals = merge_overlapping_intervals(r)
    LOG.debug("The ranges to print : %s", intervals)
    return intervals


def merge_overlapping_intervals(x):
    """Merge overlapping intervals without preserving order."""
    x.sort(key=lambda i: i[0])

    ans = []
    ans.append(x[0])

    for cur in x[1:]:
        last = ans[-1]

        if cur[0] <= last[1]:
            new_end = max(last[1], cur[1])
            last[1] = new_end
        else:
            ans.append(cur)

    return ans


class InvalidFieldRangeValueError(Exception):
    pass


class ListRangeAction(argparse.Action):
    """Parses the comma separated range to list

    Args:
        argparse (_type_): Parse the comma separated range into the namespace option
    """

    def __init__(self, option_strings, dest, **kwargs) -> None:
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, _, namespace, values, option_string=None):
        ranges = []
        LOG.debug("Using the ListRangeAction for input values: [%s]", values)
        if values and isinstance(values, str):
            ranges = values.split(",")
            try:
                ranges = normalize_list_ranges(ranges)
            except InvalidFieldRangeValueError as e:
                raise argparse.ArgumentError(self, str(e))

        setattr(namespace, self.dest, ranges)


class CustomHelpFormatter(
    argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    pass


def getargs():
    parser = argparse.ArgumentParser(
        prog=PROG,
        usage="%(prog)s OPTION... [FILE]...",
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=CustomHelpFormatter,
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
        help="line delimiter is NUL, not newline(TODO)",
    )

    parser.add_argument(
        "--complement",
        action="store",
        help="Complement the set of selected bytes, character or fields(TODO)",
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
        default=[sys.stdin.buffer],
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

    if len(args.delimiter) > 1:
        parser.error("the delimiter must be a single character")

    if args.delimiter != DEFAULT_DELIM and any([args.bytes, args.characters]):
        parser.error(
            "an input delimiter may be specified only when operating on fields"
        )

    # By default the input delimiter is used for output_delimiter
    if not args.output_delimiter:
        args.output_delimiter = args.delimiter if args.fields else ""  # FIXME:

    # Options that are valid only in case of field
    if args.only_delimited and not args.fields:
        parser.error(
            "suppressing non-delimited lines make sense only when operating on fields"
        )

    return args


def setup_logging(args):
    LOG = logging.getLogger()
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    ch.setLevel(logging.WARN)
    LOG.addHandler(ch)
    logLevel = logging.WARN

    if args.verbose == 1:
        logLevel = logging.INFO
    elif args.verbose > 1:
        logLevel = logging.DEBUG
    LOG.setLevel(logLevel)
    LOG.info("Setup logger")


def main():
    logging.getLogger().setLevel(logging.WARN)
    args = getargs()
    setup_logging(args)

    LOG.info("Starting %s", PROG)
    run(args)


if __name__ == "__main__":
    main()
