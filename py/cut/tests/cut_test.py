""" Test for cut."""

import argparse
import io
import logging
import string
import textwrap

import cut
import pytest

logging.getLogger().setLevel(logging.DEBUG)


@pytest.mark.parametrize(
    "input_intervals, expected_out",
    [
        pytest.param([[1, 2]], [[1, 2]]),
        pytest.param([[2, 3], [3, 5]], [[2, 5]]),
        pytest.param(
            [[1, 2], [3, 6], [8, 8], [11, 13]],
            [[1, 2], [3, 6], [8, 8], [11, 13]],
        ),
        pytest.param([[1, 2], [2, 2], [2, 4], [4, 8]], [[1, 8]]),
        pytest.param(
            [[1, 2], [4, 6], [3, 4], [8, 8], [11, 13]],
            [[1, 2], [3, 6], [8, 8], [11, 13]],
            id="merging_overlapping_intervals_changes_order",
        ),
    ],
)
def test_merge_overlapping_intervals(input_intervals, expected_out):
    ans = cut.merge_overlapping_intervals(input_intervals)
    assert ans == expected_out


class TestNormalizeListRange:
    @pytest.mark.parametrize(
        "test_input,test_expected",
        [
            pytest.param(
                ["1", "1"],
                [[1, 1]],
                id="simple_single_entry_normalize",
            ),
            pytest.param(
                ["1", "4", "2"],
                [[1, 1], [2, 2], [4, 4]],
                id="simple_normalize",
            ),
            pytest.param(
                ["1-2", "3-4"],
                [[1, 2], [3, 4]],
                id="non_merging_simple_interval",
            ),
            pytest.param(
                ["1-3", "3-4"],
                [[1, 4]],
                id="merging_simple_interval",
            ),
            pytest.param(
                ["1-2", "4-6", "3-4", "8", "11-13"],
                [[1, 2], [3, 6], [8, 8], [11, 13]],
                id="merging_mixed_interval",
            ),
        ],
    )
    def test_normalize_list_range(self, test_input, test_expected):
        output = cut.normalize_list_ranges(test_input)
        assert output == test_expected

    @pytest.mark.parametrize(
        "test_input, test_exception",
        [
            pytest.param(
                ["1", "1.2"],
                cut.InvalidFieldRangeValueError,
            ),
            pytest.param(
                ["1", "0x0A"],
                cut.InvalidFieldRangeValueError,
            ),
        ],
    )
    def test_normalize_list_range_exceptions(self, test_input, test_exception):
        with pytest.raises(test_exception):
            cut.normalize_list_ranges(test_input)


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
                textwrap.dedent(
                    """\
                        f0 f1 f2
                        1 2 3
                    """
                ),
                id="simple_case",
            ),
        ],
    )
    def test_process_text_data(self, test_input, test_expected, capfd):
        fps = [io.StringIO(test_input)]
        cut.process(
            argparse.Namespace(
                infiles=fps,
                only_delimited=False,
                bytes=False,
                characters=False,
                delimiter=string.whitespace,
                output_delimiter=None,
                fields=[[1, 1]],
            ),
        )
        out, err = capfd.readouterr()

        assert out == test_expected

    @pytest.mark.parametrize(
        "test_input, test_expected",
        [
            pytest.param(
                textwrap.dedent(
                    """\
                    くṞ㈢ޞយଦᎮ
                    こんにちは
                    கற்க
                    """
                ),
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
    def test_process_character_data(self, test_input, test_expected, capfd):
        fps = [io.StringIO(test_input)]
        cut.process(
            argparse.Namespace(
                infiles=fps,
                only_delimited=False,
                bytes=False,
                characters=[[1, 1], [2, 2]],
                delimiter=None,
                output_delimiter="%",
                fields=None,
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
                characters=False,
                delimiter=string.whitespace,
                output_delimiter="%",
                fields=False,
            ),
        )

        out, err = capfd.readouterr()

        assert out == test_expected
