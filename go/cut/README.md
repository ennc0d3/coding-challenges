
# [Write your own cut Tool](https://codingchallenges.fyi/challenges/challenge-cut) - Golang

Interesting, GNU cut is still not implementing support for unicode, so the GNU cut options -c and -b behave the same, where in this
cut implementation we take care of unicode.

## Solution

Straightforward, nothing special except for the unicode support, the -c and -b are treated distinct.

The command line options are handled using [cobra]("github.com/spf13/cobra") after parsing the input options, appropriate action is
taken using the respective handlers(char or byte or field) and the processed output is printed on screen.

The tests are fair have good coverage to compare parity with the cut implemenation.

### Usage

```bash
A Go implementation of the GNU cut command.

Usage:
  cut [flags]

Flags:
  -b, --bytes string              select only these bytes
  -c, --characters string         select only these characters
  -n, --complement                complement the set of selected bytes, characters or fields
  -d, --delimiter string          use DELIM instead of TAB for field delimiter
  -f, --fields string             select only these fields
  -h, --help                      help for cut
  -s, --only-delimited            do not print lines not containing delimiters
      --output-delimiter string   use STRING as the output delimiter the default is to use the input delimiter
  -v, --verbose count             verbose output
  -z, --zero-terminated           line delimiter is NUL, not newline
```

### Example(s)

Checking the [input text](https://www.dropbox.com/s/hpbma5alue0du34/challenge-cut.zip?dl=0) mentioned in the [challenge step zero](https://codingchallenges.fyi/challenges/challenge-cut#step-zero)

```bash
./cc-cut -f2 tests/testdata/sample.tsv
f1
1
6
11
16
21

```

It is same as the output from cut, see

```bash
diff <(cut -f2 tests/testdata/sample.tsv) <(./cc-cut -f2 tests/testdata/sample.tsv)
```

A sample run for stdin,

```bash
echo "f1,f2,f3,f4\n1,2,3,4\na,b,c,d" | ./cc-cut -f1-2,3-4 -d, --output-delimiter=%
f1%f2%f3%f4
1%2%3%4
a%b%c%d

```

The output for the various options are same as that of the *cit* tool and it is verified using both Go tests and [*Functional tests*](tests/test.sh)

### Development

The parsing range and merging overlapping intervals is the major part and rest are quite straightforward,

#### Structure

```bash
cut
├── cmd
│   ├── root.go
│   └── root_test.go
├── go.mod
├── go.sum
├── main.go
├── README.md
└── tests
    ├── testdata -> ../../../py/cut/tests/testdata
    └── test.sh -> ../../../py/cut/tests/test.sh
```

#### Unit tests

```bash
    cd go/cut
    go test - v
```

#### Build

```bash
    cd go/cut
    go build -o cc-cut ./cmd
```

#### Function tests

The  [testdata](testdata) is used which to compare alignment with **cut** to run the test use [test.sh](tests/test.sh).

```bash
./test.sh -p ../cc-cut
```

### References

* For fun used zerolog for logging

### Issues/Todo

* Reuse the tests in coreutils, Example the [cut tests](https://github.com/coreutils/coreutils/blob/master/tests/cut/cut.pl)
* Limited emoj support,meaning the emoj that are joined are counted as multiple characters not as we humans see
