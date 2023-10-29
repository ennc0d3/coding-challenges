#!/usr/bin/env python3


import argparse
import collections
import io
import logging
import re
import sys
from io import IOBase

LOG = logging.getLogger()


def run(args):
    files = args.infiles
    result = process_filedata(files)
    output_result(args, result)


def process_filedata(fileobjs: list[IOBase]) -> dict[str, dict]:
    result = collections.defaultdict(dict)

    for fp in fileobjs:
        raw_content = fp.read()
        name = getattr(fp, "name", "unknown")
        fp.close()
        # Count the characters
        if isinstance(fp, io.TextIOBase):
            utf_content = raw_content
        else:
            utf_content = raw_content.decode("utf8")
        result[name]["chars"] = len(utf_content)
        # Count the bytes
        result[name]["bytes"] = len(raw_content)
        # Count the words
        result[name]["words"] = len(utf_content.split())
        all_lines = utf_content.splitlines(keepends=True)
        # For wc compatibility, only if the line ends with LF|CRLF|CR we can count it
        # as line, so a check to ensure that
        count = len(all_lines)
        if count and not re.search(r"\r?\n|\r", all_lines[-1]):
            count -= 1
        result[name]["lines"] = count
    return result


def get_max_widths(result) -> dict[str, int]:
    w = collections.defaultdict(int)
    for filename, data in result.items():
        if len(filename) > w["filename"]:
            w["filename"] = len(filename)
        for key, value in data.items():
            width = len(str(value))
            if width > w[key]:
                w[key] = width
    return w


def output_result(args, result):
    if len(args.infiles) > 1:
        update_totals(result)
    width = get_max_widths(result)

    for filename, data in result.items():
        LOG.debug("File: %s, data: %s", filename, data)
        if args.charcount:
            print(f"{data['chars']} {filename}")
        elif args.bytecount:
            print(f"{data['bytes']} {filename}")
        elif args.linecount:
            print(f"{data['lines']} {filename}")
        elif args.wordcount:
            print(f"{data['words']} {filename}")
        else:
            print(
                f" {data['lines']:>{width['lines']}}  {data['words']:>{width['words']}} {data['bytes']:>{width['bytes']}} {filename:<}",
            )


def update_totals(result):
    total = collections.defaultdict(int)
    for data in result.values():
        for k, v in data.items():
            total[k] += v
    result["total"] = total


def getargs():
    parser = argparse.ArgumentParser(description="A program to count words (wc)")
    parser.add_argument(
        "-m",
        "--chars",
        default=False,
        action="store_true",
        dest="charcount",
        help="Count the characters",
    )
    parser.add_argument(
        "-c",
        "--bytes",
        default=False,
        action="store_true",
        dest="bytecount",
        help="Count the bytes",
    )
    parser.add_argument(
        "-l",
        "--lines",
        default=False,
        action="store_true",
        dest="linecount",
        help="Count the lines",
    )
    parser.add_argument(
        "-w",
        "--word",
        default=False,
        action="store_true",
        dest="wordcount",
        help="Count the words",
    )
    parser.add_argument(
        "-L",
        "--max-line-length",
        default=False,
        action="store_true",
        dest="maxlinelength",
        help="print the maximum display width",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="wc 0.0.1",
        help="output the version and exit",
    )

    parser.add_argument(
        "infiles",
        nargs="*",
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
    LOG.info("Starting wc")
    run(args)


if __name__ == "__main__":
    main()
