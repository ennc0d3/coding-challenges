""" Test for cut."""

import argparse
import io
import string
import textwrap

import cut
import pytest


class TestProcessData:
    @pytest.mark.parametrize(
        "test_input, test_expected",
        [
            pytest.param(
                textwrap.dedent(
                    """\
                        f0 f1 f2
                        1 2 3
                    """
                ),
                {
                    0: ["f0 f1 f2"],
                    1: ["1 2 3"],
                },
                id="simple_case",
            ),
        ],
    )
    def test_process_text_data(self, test_input, test_expected):
        fps = [io.StringIO(test_input)]
        o = cut.process(
            argparse.Namespace(
                infiles=fps,
                only_delimited=False,
                bytes=False,
                characters=False,
                delimiter=string.whitespace,
                fields=True,
            ),
            fps,
        )
        assert o == test_expected

    @pytest.mark.parametrize(
        "test_input, test_expected",
        [
            pytest.param(
                textwrap.dedent(
                    """\
                    くṞ㈢ޞយଦᎮ
                    こんにちは
                    """
                ),
                {
                    0: ["く", "Ṟ", "㈢", "ޞ", "យ", "ଦ", "Ꭾ"],
                    1: ["こ", "ん", "に", "ち", "は"],
                },
                id="utf8-stiring",
            ),
        ],
    )
    def test_process_character_data(self, test_input, test_expected):
        fps = [io.StringIO(test_input)]
        o = cut.process(
            argparse.Namespace(
                infiles=fps,
                only_delimited=False,
                bytes=False,
                characters=True,
                delimiter=string.whitespace,
                fields=False,
            ),
            fps,
        )
        assert o == test_expected

    @pytest.mark.parametrize(
        "test_input, test_expected",
        [
            pytest.param(
                textwrap.dedent(
                    """\
                    🤦🏼‍♂️
                    くṞ㈢ޞយଦᎮ
                    """
                ),
                {
                    0: "🤦🏼‍♂️",
                    1: "くṞ㈢ޞយଦᎮ",
                },
                id="multiple_sequence_emoj",
            ),
            pytest.param(
                "கற்க",
                {0: "கற்க"},
                id="multiple_byte_utf8-string",
            ),
        ],
    )
    def test_process_bytes_data(self, test_input, test_expected):
        fps = [io.StringIO(test_input)]
        o = cut.process(
            argparse.Namespace(
                infiles=fps,
                only_delimited=False,
                bytes=True,
                characters=False,
                delimiter=string.whitespace,
                fields=False,
            ),
            fps,
        )
        assert o == test_expected
