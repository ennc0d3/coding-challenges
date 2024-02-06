import pytest

from util.rangeparser import (
    InvalidFieldRangeValueError,
    complement_ranges,
    merge_overlapping_intervals,
    normalize_list_ranges,
)


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
    ans = merge_overlapping_intervals(input_intervals)
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
        output = normalize_list_ranges(test_input)
        assert output == test_expected

    @pytest.mark.parametrize(
        "test_input, test_exception",
        [
            pytest.param(
                ["1", "1.2"],
                InvalidFieldRangeValueError,
            ),
            pytest.param(
                ["1", "0x0A"],
                InvalidFieldRangeValueError,
            ),
        ],
    )
    def test_normalize_list_range_exceptions(self, test_input, test_exception):
        with pytest.raises(test_exception):
            normalize_list_ranges(test_input)


def test_complement_ranges():
    max_value = 1 << 16
    assert complement_ranges([[1, 5], [10, 15]]) == [[6, 9], [16, max_value]]
    assert complement_ranges([[3, 7], [12, 18]]) == [[1, 2], [8, 11], [19, max_value]]
    assert complement_ranges([[1, 1]]) == [[2, max_value]]
    assert complement_ranges([[2, 3], [5, 6], [8, 8], [11, 13]]) == [
        [1, 1],
        [4, 4],
        [7, 7],
        [9, 10],
        [14, max_value],
    ]
    assert complement_ranges([]) == []
