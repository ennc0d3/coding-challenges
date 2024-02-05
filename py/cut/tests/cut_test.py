""" Test for cut."""

import argparse
import io
import logging
import string
import textwrap
from typing import List

import cut
import pytest

logging.getLogger().setLevel(logging.DEBUG)


class CutArgs:
    def __init__(
        self,
        infiles,
        field_range=None,
        bytes_range=None,
        char_range=None,
        delimiter=None,
        output_delimiter=None,
        complement=False,
        zero_terminated=False,
        only_delimited=False,
    ):
        self.infiles = infiles
        self.only_delimited = only_delimited
        self.bytes = bytes_range
        self.characters = char_range
        self.delimiter = delimiter
        self.fields = field_range
        self.output_delimiter = output_delimiter
        self.zero_terminated = zero_terminated
        self.complement = complement

    def to_namespace(self):
        return argparse.Namespace(
            infiles=self.infiles,
            only_delimited=self.only_delimited,
            bytes=self.bytes,
            characters=self.characters,
            delimiter=self.delimiter,
            fields=self.fields,
            output_delimiter=self.output_delimiter,
            zero_terminated=self.zero_terminated,
            complement=self.complement,
        )


class TestProcessData:

    @pytest.mark.parametrize(
        "test_input, test_expected",
        [
            pytest.param(
                CutArgs(
                    [
                        io.BytesIO(
                            bytes(
                                textwrap.dedent(
                                    """\
                                         f0 f1 f2
                                         1 2 3
                                         """
                                ),
                                encoding="utf-8",
                            )
                        )
                    ],
                    field_range=[[1, 1]],
                    delimiter=string.whitespace,
                ),
                textwrap.dedent(
                    """\
                    f0 f1 f2
                    1 2 3
                    """
                ),
                id="simple_case",
            ),
            pytest.param(
                CutArgs(
                    [io.BytesIO(bytes("a1:\0:", encoding="utf-8"))],
                    delimiter=":",
                    field_range=[[1, 100]],
                    zero_terminated=True,
                    output_delimiter=":",
                ),
                "a1:\0:\0",
                id="simple_case_zero_terminated_with_delimiter",
            ),
            pytest.param(
                CutArgs(
                    [
                        io.BytesIO(
                            bytes("a1:A1:YayOne\0b1:B1:BeOne\0", encoding="utf-8")
                        )
                    ],
                    field_range=[[1, 1], [3, 3]],
                    delimiter=":",
                    output_delimiter=":",
                    zero_terminated=True,
                ),
                "a1:YayOne\0b1:BeOne\0",
                id="simple_case_zero_terminated_with_multiple_fields",
            ),
            pytest.param(
                CutArgs(
                    [io.BytesIO(bytes("ab\0cd\0", encoding="utf-8"))],
                    char_range=[[1, 1]],
                    delimiter=":",
                    zero_terminated=True,
                ),
                "a\0c\0",
                id="nullterminated_char_range",
            ),
        ],
    )
    def test_process_text_data(self, test_input, test_expected, capfd):
        cut.process(
            test_input.to_namespace(),
        )
        out, err = capfd.readouterr()

        assert out == test_expected

    @pytest.mark.parametrize(
        "test_input, test_range, test_expected",
        [
            pytest.param(
                textwrap.dedent(
                    """\
                    くṞ㈢ޞយଦᎮ
                    こんにちは
                    கற்க
                    """
                ),
                [[1, 1], [2, 2]],
                textwrap.dedent(
                    """\
                    く%Ṟ
                    こ%ん
                    க%ற
                    """
                ),
                id="utf8-string",
            ),
        ],
    )
    def test_process_character_data(
        self, test_input, test_range: List[List], test_expected, capfd
    ):
        fps = [io.BytesIO(bytes(test_input, encoding="utf-8"))]
        cut.process(
            argparse.Namespace(
                infiles=fps,
                only_delimited=False,
                bytes=False,
                characters=test_range,
                delimiter=None,
                output_delimiter="%",
                fields=None,
                zero_terminated=False,
            ),
        )
        out, err = capfd.readouterr()

        assert out == test_expected

    @pytest.mark.parametrize(
        "test_input, test_range, test_expected",
        [
            ("ab\0cd\0", [[1, 1]], "a\0c\0"),
            ("ab\0cd", [[1, 1]], "a\0c\0"),
        ],
    )
    def test_process_zeroterminated_character_data(
        self, test_input, test_range: List[List], test_expected, capfd
    ):
        fps = [io.BytesIO(bytes(test_input, encoding="utf-8"))]

        cut.process(
            argparse.Namespace(
                infiles=fps,
                only_delimited=False,
                bytes=False,
                characters=test_range,
                delimiter=None,
                output_delimiter="%",
                fields=None,
                zero_terminated=True,
            ),
        )
        out, err = capfd.readouterr()

        assert out == test_expected

    @pytest.mark.parametrize(
        "test_input, test_byte_range, test_expected",
        [
            pytest.param(
                textwrap.dedent(
                    """\
                    🤦🏼‍♂️
                    🤦🏼‍♂️
                    くṞ㈢ޞយଦ
                    """
                ),
                [[1, 4]],
                textwrap.dedent(
                    """\
                    🤦
                    🤦
                    く�
                    """
                ),
                id="multiple_sequence_emoj",
            ),
            pytest.param(
                "கற்க கற்க",
                [[1, 12], [14, 22]],
                "கற்க%கற்\n",
                id="multiple_byte_utf8-string",
            ),
        ],
    )
    def test_process_bytes_data(
        self, test_input, test_byte_range, test_expected, capfd
    ):
        fps = [io.BytesIO(bytes(test_input, encoding="utf-8"))]

        cut.process(
            argparse.Namespace(
                infiles=fps,
                only_delimited=False,
                bytes=test_byte_range,
                characters=None,
                delimiter=string.whitespace,
                output_delimiter="%",
                fields=None,
                zero_terminated=False,
            ),
        )

        out, err = capfd.readouterr()

        assert out == test_expected


# @pytest.mark.parametrize(
#     "test_input, data_type, range_list, delimiter, zero_terminated, test_expected",
#     [
#         ("ab\0cd\0", "char", [[1, 1]], None, True, "a\0c\0"),
#         ("ab\0cd", "char", [[1, 1]], None, True, "a\0c\0"),

#     ],
# )
# def test_process_zero_terminated_data(
#     test_input, data_type, range_list, delimiter, zero_terminated, test_expected, capfd
# ):
#     fps = [io.BytesIO(bytes(test_input, encoding="utf-8"))]

#     cut.process(
#         argparse.Namespace(
#             infiles=fps,
#             only_delimited=False,
#             bytes=False,
#             characters=data_type == "char",
#             delimiter=delimiter or string.whitespace,
#             output_delimiter="\0",
#             fields=
#             zero_terminated=zero_terminated,
#             range_list=range_list,
#         ),
#     )

#     out, err = capfd.readouterr()

#     assert out == test_expected
