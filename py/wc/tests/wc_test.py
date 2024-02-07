import logging
import tempfile
import textwrap

import pytest
import wc

BASE_DIR = None

# Aliases
TP = pytest.param

LOG = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def basetmp(tmp_path_factory):
    global BASE_DIR
    BASE_DIR = tmp_path_factory.mktemp("__wc_test")


def create_testfile(data):
    with tempfile.NamedTemporaryFile(
        dir=BASE_DIR, prefix="input-", suffix=".txt", delete=False
    ) as f:
        f.write(bytes(data, encoding="utf8"))
        return f.name


@pytest.mark.parametrize(
    "test_input,test_expected",
    [
        TP(
            "One",
            {
                "chars": 3,
                "bytes": 3,
                "words": 1,
                "lines": 0,
            },
            id="single_word_nolf",
        ),
        TP(
            " ",
            {
                "chars": 1,
                "bytes": 1,
                "words": 0,
                "lines": 0,
            },
            id="single_space_nolf",
        ),
        TP(
            "\r\n",
            {
                "chars": 2,
                "bytes": 2,
                "words": 0,
                "lines": 1,
            },
            id="crlf_counts_two_chars",
        ),
        TP(
            "\n",
            {
                "chars": 1,
                "bytes": 1,
                "words": 0,
                "lines": 1,
            },
            id="lf_counts_one_char",
        ),
        TP(
            "Gutenberg™",
            {
                "chars": 10,
                "bytes": 12,
                "words": 1,
                "lines": 0,
            },
            id="unicode_word",
        ),
        TP(
            "",
            {
                "chars": 0,
                "words": 0,
                "bytes": 0,
                "lines": 0,
            },
            id="empty_file",
        ),
        TP(
            "🤦🏼‍♂️",
            {
                "chars": 5,
                "bytes": 17,
                "words": 1,
                "lines": 0,
            },
            id="emoj_facepalm_zwj",
        ),
        TP(
            textwrap.dedent(
                """\
            ஒழுக்கம் விழுப்பந் தரலான் ஒழுக்கம்
            உயிரினும் ஓம்பப் படும்
            """
            ),
            {
                "chars": 58,
                "bytes": 160,
                "words": 7,
                "lines": 2,
            },
            id="unicode_sentence_tamil_tirukurral",
        ),
        TP(
            "ẇ͓̞͒͟͡ǫ̠̠̉̏͠͡ͅr̬̺͚̍͛̔͒͢d̠͎̗̳͇͆̋̊͂͐",
            {
                "chars": 34,
                "bytes": 67,
                "words": 1,
                "lines": 0,
            },
            id="unicode_crazy_weird_word",
        ),
        TP(
            "\r\n",
            {
                "chars": 2,
                "bytes": 2,
                "words": 0,
                "lines": 1,
            },
            id="single_line_only_crlf",
        ),
        TP(
            "TwoLines\n\n",
            {
                "chars": 10,
                "bytes": 10,
                "words": 1,
                "lines": 2,
            },
            id="two_lines_mutliple_lf",
        ),
        TP(
            textwrap.dedent(
                """\
                Gutenberg™
                Gustavberg"""
            ),
            {
                "chars": 21,
                "bytes": 23,
                "words": 2,
                "lines": 1,
            },
            id="multiple_lines_no_lf_in_last_line",
        ),
    ],
)
def test_process_filedata(test_input, test_expected):
    filename = create_testfile(test_input)
    with open(filename, "rb") as fileobj:
        result = wc.process_filedata([fileobj])
        assert result[filename] == test_expected
