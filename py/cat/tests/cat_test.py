"""Test for cat"""

import io

import pytest


class TestCatBasic:
    @pytest.mark.parametrize(
        "test_input, test_expected",
        [
            pytest.param(
                io.StringIO("a\nb\nc\nd\ne\nf\n"),
                "a\nb\nc\nd\ne\nf\n",
                id="cat_basic_1",
            ),
        ],
    )
    def test_cat_basic(self, test_input, test_expected):
        assert True  # TODO
