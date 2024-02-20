# [Write your own cat Tool](https://codingchallenges.fyi/challenges/challenge-cat) - Python

## Solution

The code is structured under [cat](./cat.py) and is using [Pipenv](https://pipenv.pypa.io/en/latest) as the package manager

### Usage

See,

```bash
cat.py --help
age: cat OPTION... [FILE]...

Concatenate FILES(s) to standard output.

With no FILE, or when FILE is -, read standard input.

positional arguments:
  FILE                  The name of the input files, when not specified, reads from stdin. (default: [<_io.BufferedReader name='<stdin>'>])

options:
  -h, --help            show this help message and exit
  -A, --show-all        equivalent to -vET (default: False)
  -b, --number-nonblank
                        number nonempty output lines, overrides -n (default: False)
  -e                    equivalent to -vE (default: False)
  -E, --show-ends       display $ at end of each line (default: False)
  -n, --number          number all output lines (default: False)
  -s, --squeeze-blank   suppress repeated empty output lines (default: False)
  -t                    equivalent to -vT (default: False)
  -T, --show-tabs       display TAB characters as ^I (default: False)
  -u                    (ignored) (default: False)
  -v, --show-nonprinting
                        use ^ and M- notation, except for LFD and TAB (default: False)
  --version             output the version and exit
  -V                    Increase the verbosity (default: 0)

Examples:
cat f - g  Output f's contents, then standard input, then g's contents.
cat        Copy standard input to standard output.
```

### Example(s)

```bash

cat -n tests/testdata/test.txt

```

### Development

The cat is in ./cat.py and super straightforward for the basic options

#### Unit tests

There is not any useful test, just a place holder for future options

```bash
pytest -v
```

#### Function tests

The directory contains the [testdata](tests/testdata) mentioned in the challenge.

```bash
cd tests
./test.sh -p
```

### Issues & Todos

* The option --show-nonprinting is tricky and not implemented, see open issue [#14](https://github.com/ennc0d3/coding-challenges/issues/14)
* The handling on printing line number is also different, GNU cat uses 6-20 as fieldwidth and may be '\t', not something that I think is important at the moment

## References

[cat -v, show-nonprinting](https://stackoverflow.com/questions/44694331/what-is-the-m-notation-and-where-is-it-documented)

### Topics of interest
