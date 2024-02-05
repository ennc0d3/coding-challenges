import argparse
import logging
import sys
import textwrap

from . import rangeparser

LOG = logging.getLogger(__name__)

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
        help="line delimiter is NUL, not newline",
    )

    parser.add_argument(
        "--complement",
        action="store_true",
        help="Complement the set of selected bytes, character or fields",
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

    if args.complement:
        for option in ["bytes", "characters", "fields"]:
            if getattr(args, option):
                setattr(
                    args, option, rangeparser.complement_ranges(getattr(args, option))
                )

    return args


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
                ranges = rangeparser.normalize_list_ranges(ranges)
            except rangeparser.InvalidFieldRangeValueError as e:
                raise argparse.ArgumentError(self, str(e))

        setattr(namespace, self.dest, ranges)


class CustomHelpFormatter(
    argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    pass
