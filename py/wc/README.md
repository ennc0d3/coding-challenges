# [Write your own WC](https://codingchallenges.fyi/challenges/challenge-wc) - Python

Though, I might have used a million times, when implementing it I had a chance to sidestep and understand UTF8 encodings, multi-byte characters, encoding of emoj with zero with joiners,the unix definition of a [POSIX text file](https://en.wikipedia.org/wiki/Text_file#Unix_text_files)

## Solution

The code is structured under [wordcount](wordcount) and is using [Pipenv](https://pipenv.pypa.io/en/latest) as the package manager as I find it better than [Poetry](https://python-poetry.org/) due to the overhead in learning new package/dependency manager.

### Usage

```bash
./wc.py --help
usage: wc.py [-h] [-m] [-c] [-l] [-w] [-L] [--version] [-v] [infiles ...]

A program to count words (wc)

positional arguments:
  infiles               The name of the input files

options:
  -h, --help            show this help message and exit
  -m, --chars           Count the characters
  -c, --bytes           Count the bytes
  -l, --lines           Count the lines
  -w, --word            Count the words
  -L, --max-line-length
                        print the maximum display width
  --version             output the version and exit
  -v, --verbose         Increase the verbosity
```

### Example(s)

Checking the [input text](https://www.gutenberg.org/cache/epub/132/pg132.txt) mentioned in the [challenge step zero](https://codingchallenges.fyi/challenges/challenge-wc#step-zero)

The output from *wc (GNU Coreutils) 8.32* on Ubuntu with (LC_NAME=sv_SE.UTF-8)

```bash
wc tests/testdata/test.txt
7145  58164 342147 tests/testdata/test.txt
```

The output from [*wc.py*](wc.py) for the same test.txt,

```bash
./wc.py tests/testdata/test.txt
 7145  58164 342147 tests/testdata/test.txt
```

The output for the various options are same as that of the *wc* tool and it is verified using both [Unit test *(Pytests)*](tests/wc_test.py) and [*functional tests*](tests/test.sh)

A sample run for stdin,

```bash
echo -n "TwoLines\n\n" | ./wc.py
 2  1 10 <stdin>
```

### Development

Only an single module [wc.py](./wc.py), and it uses *argparse* module for handling arguments, process the file content and outputs depending on the input arguments. The output function attempts to align with *wc*'s structure but that is just me trying to play with the f'string format.

#### Unit tests

To run the tests, ensure the pipenv shell is activated, as we have *pytest* dependency.

```bash
pytest -vv
```

Checkout the [testcases](tests/wc_test.py) and see the various inputs it uses.

#### Function tests

To verify more inputs [testdata](testdata) is used which to compare alignment with **wc** result by running [test.sh](tests/test.sh).
