# [Write your own Cut Tool](https://codingchallenges.fyi/challenges/challenge-cut) - Python

The cut.py implements all the options the GNU cut provides, except for the treatment of character and bytes option which is
treated as the same in GNU cut, where this version supports character option with unicode support.

## Solution

Straightforward, nothing special except for the unicode support, the -c and -b are treated distinct.

The **argparse** module is used to implement the command options, the command handling and the associated handling of
range list is handled by modules under util package.

The code is structured under [cut](cut) and is using [Pipenv](https://pipenv.pypa.io/en/latest) as the package manager as I find it better than [Poetry](https://python-poetry.org/) due to the overhead in learning new package/dependency manager.

### Usage

```bash
usage: cut OPTION... [FILE]...

Print selected parts of lines from each FILE to standard output.

With no FILE, or when FILE is -, read standard input.

positional arguments:
  FILE                  The name of the input files (default:
                        [<_io.BufferedReader name='<stdin>'>])

options:
  -h, --help            show this help message and exit
  -b LIST, --bytes LIST
                        select only these bytes (default: None)
  -c LIST, --characters LIST
                        select only these characters (is same not same as
                        bytes option, it understands utf-8) (default: None)
  -f LIST, --fields LIST
                        Select only these fields; also print any line that
                        contains no delimiter character, unless the -s option
                        is specified (default: None)
  -d DELIMITER, --delimiter DELIMITER
                        Use DELIM instead of TAB for field delimiter (default:
                        )
  -s, --only-delimited  do not print lines not containing delimiters, Only
                        applicable in case of fields option (default: False)
  --output-delimiter OUTPUT_DELIMITER
                        use STRING as the output delimiter the default is to
                        use the input delimter (default: )
  -z, --zero-terminated
                        line delimiter is NUL, not newline (default: False)
  --complement          Complement the set of selected bytes, character or
                        fields (default: False)
  --version             output the version and exit
  -v, --verbose         Increase the verbosity (default: 0)

Use one, and only one of -b, -c or -f.  Each LIST is made up of one
range, or many ranges separated by commas.  Selected input is written
in the same order that it is read, and is written exactly once.
Each range is one of:

    N     N'th byte, character or field, counted from 1
    N-    from N'th byte, character or field, to end of line
    N-M   from N'th to M'th (included) byte, character or field
     -M   from first to M'th (included) byte, character or field```

### Example(s)
``` bash
# For Nul terminated string
echo "a1:A1:YayOne\x00" | ./cut.py -z -f1,3 -d':' --output-delimiter=%

# Input in the challenge,
 cat tests/testdata/sample.tsv | cut -f2,1
f0      f1
0       1
5       6
10      11
15      16
20      21
```

### Development

The main logic is parsing the command line arguments and handling the range, with complications due to the mix of additional options,
like --only-delimited, --output-delimiter, --complement, -z.

#### Unit tests

```bash
pytest -v
```

#### Function tests

The script [test.sh](tests/test.sh) runs the program against various options and compares the result with the
GNU cut for the [testdata](tests/testdata) mentioned in the challenge.

```bash
cd tests
./test.sh -p ../cut.py
```

The best way would have been to reuse the *coreutils* testcases

## Topics of interest

* [argparse](https://docs.python.org/3/library/argparse.html)
* [Unicode in 2023](https://tonsky.me/blog/unicode/)
* [Finding Code points](https://codepoints.net/search?q=)
* [codecs](https://docs.python.org/3/library/codecs.html)
* hd|hexdump|od|dd
* HexEditors - Bless, Ghex, xdd
* Understand Pytest discovery, Structuring of test
