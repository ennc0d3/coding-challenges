""" Test for cut."""

import logging

import cut
import pytest

logging.getLogger().setLevel(logging.DEBUG)


class TestNormalizeFieldRange:
    @pytest.mark.parametrize(
        "test_input,test_expected",
        [
            pytest.param(
                ["1", "4", "2"],
                [(1,1), (2,2), (4,4)],
                id="simple_normalize",
            ),
        ],
    )
    def test_normalize_field_range(self, test_input, test_expected):
        output = cut.normalize_field_ranges(test_input)
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
    def test_normalize_field_range_exceptions(self, test_input, test_exception):
        with pytest.raises(test_exception):
            cut.normalize_field_ranges(test_input)


#class TestProcessFieldOption:
        #   @pytest.mark.parametrize(
        #"test_input, test_expected",
            #[
            #pytest.param(
            #    ["1", "0x0A"],
            #    cut.InvalidFieldRangeValueError
        #),
    #],
    #)
        #def test_normalize_field_range_exceptions(self, test_input, test_exception):
            #with pytest.raises(test_exception):
#cut.normalize_field_ranges(test_input)
