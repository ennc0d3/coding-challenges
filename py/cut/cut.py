#!/usr/bin/env python3


import argparse
import logging

from cmdparser import cutcmd

LOG = logging.getLogger()


def process(args: argparse.Namespace):

    content_type = "str"
    line_separator = "\n"

    if args.bytes:
        content_type = "bytes"
        line_separator = b"\n"

    if args.zero_terminated:
        line_separator = b"\x00" if args.bytes else "\x00"

    for fileobj in args.infiles:

        data = get_content(fileobj, content_type)
        lines = data.split(sep=line_separator)  # type: ignore
        if lines[-1] == b"" or lines[-1] == "":
            lines = lines[:-1]

        for line in lines:
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
                            fields[start - 1 : end], encoding="utf-8", errors="replace"  # type: ignore
                        ),
                        sep="",
                        end=delim,
                    )

            print_line(line_separator, line)


def get_content(fileobj, content_type: str = "bytes"):
    data = fileobj.read()
    assert isinstance(data, bytes)
    if content_type == "str":
        data = data.decode("utf-8")
    return data


def print_line(line_separator, line):
    if isinstance(line, bytes):
        print(end=str(line_separator, encoding="utf-8"))
    else:
        print(end=line_separator)


def setup_logging(args, LOG: logging.Logger):
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
    ch.setLevel(logLevel)
    LOG.info("Setup logger")


def main():
    args = cutcmd.getargs()
    global LOG
    setup_logging(args, LOG)
    process(args)


if __name__ == "__main__":
    main()
