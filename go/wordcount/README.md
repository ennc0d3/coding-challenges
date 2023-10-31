# [Write your own WC](https://codingchallenges.fyi/challenges/challenge-wc) - Golang

Though, I might have used a million times, when implementing it I had a chance to sidestep and understand UTF8 encodings, multi-byte characters, encoding of emoj with zero with joiners, the unix definition of a [POSIX text file](https://en.wikipedia.org/wiki/Text_file#Unix_text_files)

The solution is nothing fancy, very simple and haven't invested time to make it efficient, but as I move forward with the another exercises I might take up them (Why not benchmark, etc for fun)

## Solution

The code is structured under [wordcount](wordcount) and implementation is straightforward due Golang

##

### Usage

```bash
 ./wc --help
Print newline, word, and byte counts for each FILE, and a total line if
more than one FILE is specified.

Usage:
  wc [flags]

Flags:
  -c, --bytes     bytes count output
  -m, --chars     char count output
  -h, --help      help for wc
  -l, --lines     line count output
  -v, --verbose   verbose output
  -V, --version   version output
  -w, --words     word count output
```

### Example(s)

Checking the [input text](https://www.gutenberg.org/cache/epub/132/pg132.txt) mentioned in the [challenge step zero](https://codingchallenges.fyi/challenges/challenge-wc#step-zero)

The output from *wc (GNU Coreutils) 8.32* on Ubuntu with (LC_NAME=sv_SE.UTF-8)

```bash
wc tests/testdata/test.txt
7145  58164 342147 tests/testdata/test.txt

```

The output from [*wc.py*](./wc) for the same test.txt,

```bash
./wc tests/testdata/test.txt
 7145  58164 342147 tests/testdata/test.txt
```

A sample run for stdin,

```bash
echo -n "TwoLines\n\n" | ./wc
 2      1       10      /dev/stdin
```

The output for the various options are same as that of the *wc* tool and it is verified using both Go tests and [*Functional tests*](tests/test.sh)

### Development

The module is called [wordcount](go.mod) and it uses *cobra* package for command line parsing, the logic is implemented in the package named [util](util)

#### Build

```bash
go build -o ./wc .
```

#### Unit tests

To run the tests,

```bash
go test -v ./...
```

Checkout the specific [util](util) package to see the various inputs it uses.

#### Function tests

The  [testdata](testdata) is used which to compare alignment with **wc** to run the test use [test.sh](tests/test.sh).
