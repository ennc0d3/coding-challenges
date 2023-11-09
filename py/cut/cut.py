#!/usr/bin/env python3


import argparse
import logging
import sys
import textwrap

LOG = logging.getLogger()

PROG = "cut"
VERSION = "0.0.1"
DESCRIPTION = """Print selected parts of lines from each FILE to standard output.

                 With no FILE, or when FILE is -, read standard input.
              """

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


"""TASKs

Rules:
    * Pomodoro and break
    * Measure time for the task
    * Use test and commit

Task list:
 - Implement the usage structure and mark the ones not implemented as TODO - DONE
 - Implement the base case for text file and field option(basic option, a comma separated list) - DONE
 - Re-think about the structure / Test
 - Implement the only-delimited option
 - Implement the range field options
 - Test the field options with the various ranges
 - Implement basic character option
 - Implement the character option with the ranges
 - Implement the byte option basic
 - Implement the complex byte option
 - Test on the binary data
 - Implement complementing range
 - Push


VSCODE: delete word in cursor?
"""


def run(args):
    process(args)


def process(args: argparse.Namespace):
    if args.fields:
        process_fields(args)


def process_fields(args):
    LOG.debug("Processing fields, args:%s", args.fields)
    for fileobj in args.infiles:
        # For each file, process data and print the fields

        data = fileobj.read().decode("utf-8")
        for line in data.splitlines():
            fields = line.split(args.delimiter)
            for rf in args.fields:
                if rf < len(fields):
                    print(
                        fields[rf],
                        end=args.output_delimiter,
                    )
            print()


# TODO: Probably move the validation part to the listAction action itself
def normalize_field_ranges(field_ranges):
    r = []
    for i in field_ranges:
        try:
            v = int(i)
            r.append(v)
        except ValueError as e:
            LOG.debug(e)
            raise InvalidFieldRangeValueError(f"cut: invalid field value '{i}'")
    return r


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
                ranges = normalize_field_ranges(ranges)
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
    logging.getLogger().setLevel(logging.DEBUG)
    args = getargs()
    setup_logging(args)
    LOG.info("Starting %s", PROG)
    run(args)


if __name__ == "__main__":
    main()
