#!/usr/bin/env python3


import argparse
import logging
import sys
import textwrap

LOG = logging.getLogger()

PROG = "cat"
DESCRIPTION = textwrap.dedent(
    """\
    Concatenate FILES(s) to standard output.

    With no FILE, or when FILE is -, read standard input.

    """
)

EXAMPLES = textwrap.dedent(
    """\
    Examples:
    cat f - g  Output f's contents, then standard input, then g's contents.
    cat        Copy standard input to standard output.
    """
)
__VERSION = "0.0.1"


def run(args):
    process(args)


def process(args):
    files = args.infiles
    lineno = 0
    blanks = 0
    for file in files:
        for line in file.readlines():

            if args.squeezeblank:
                if line.strip() == b"":  # type: ignore
                    blanks += 1
                    if blanks > 1:
                        continue

            if args.endofline:
                args.showends = True
                args.shownonprinting = True

            if args.tabs:
                args.showtabs = True
                args.shownonprinting = True

            if args.showall:
                args.showends = True
                args.showtabs = True
                args.shownonprinting = True

            if args.shownonprinting:
                line = line.replace(b"\r", b"^M")

            if args.showtabs:
                line = line.replace(b"\t", b"^I")

            if args.showends:
                line = line.replace(b"\n", b"$\n")
                line = line.replace(b"\r", b"$\r\n")

            if args.numbernonblank:
                if line.strip() == b"" or line.strip() == "$":  # type: ignore
                    print(line)
                else:
                    lineno += 1
                    print(f"{lineno} {str(line, 'utf-8')}")

            elif args.number:
                lineno += 1
                print(f"{lineno} {str(line, 'utf-8')}", end="")
            else:
                print(f"{str(line, 'utf-8')}", end="")


class CustomHelpFormatter(
    argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    pass


def getargs():

    parser = argparse.ArgumentParser(
        prog=PROG,
        usage="%(prog)s OPTION... [FILE]...",
        description=DESCRIPTION,
        epilog=EXAMPLES,
        formatter_class=CustomHelpFormatter,
    )
    parser.add_argument(
        "-A",
        "--show-all",
        default=False,
        action="store_true",
        dest="showall",
        help="equivalent to -vET",
    )
    parser.add_argument(
        "-b",
        "--number-nonblank",
        default=False,
        action="store_true",
        dest="numbernonblank",
        help="number nonempty output lines, overrides -n",
    )
    parser.add_argument(
        "-e",
        default=False,
        action="store_true",
        dest="endofline",
        help="equivalent to -vE",
    )
    parser.add_argument(
        "-E",
        "--show-ends",
        default=False,
        action="store_true",
        dest="showends",
        help="display $ at end of each line",
    )
    parser.add_argument(
        "-n",
        "--number",
        default=False,
        dest="number",
        action="store_true",
        help="number all output lines",
    )
    parser.add_argument(
        "-s",
        "--squeeze-blank",
        default=False,
        dest="squeezeblank",
        action="store_true",
        help="suppress repeated empty output lines",
    )
    parser.add_argument(
        "-t",
        default=False,
        action="store_true",
        dest="tabs",
        help="equivalent to -vT",
    )
    parser.add_argument(
        "-T",
        "--show-tabs",
        default=False,
        action="store_true",
        dest="showtabs",
        help="display TAB characters as ^I",
    )
    parser.add_argument(
        "-u",
        default=False,
        action="store_true",
        help="(ignored)",
        dest="ignore",
    )
    parser.add_argument(
        "-v",
        "--show-nonprinting",
        default=False,
        action="store_true",
        dest="shownonprinting",
        help="use ^ and M- notation, except for LFD and TAB",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s %(__VERSION)s",
        help="output the version and exit",
    )

    parser.add_argument(
        "infiles",
        nargs="*",
        metavar="FILE",
        type=argparse.FileType("rb"),
        default=[sys.stdin.buffer],
        help="The name of the input files, when not specified, reads from stdin.",
    )

    # Debug options
    parser.add_argument(
        "-V",
        default=0,
        dest="verbose",
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
    for h in LOG.handlers:
        h.setLevel(logLevel)
    LOG.info("Setup logger")


def main():
    args = getargs()
    setup_logging(args)
    LOG.info("Starting %S", PROG)
    run(args)


if __name__ == "__main__":
    main()
