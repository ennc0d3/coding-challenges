
# [Write your own cat Tool](https://codingchallenges.fyi/challenges/challenge-cat) - Golang

A simple implementaiton

## Solution

### Usage

```bash
A Go implementation of the GNU cat command.

Usage:
```

### Example(s)

Checking the with the examples mentioned in the [challenge](https://codingchallenges.fyi/challenges/challenge-cat)

```bash
head -n1 test.txt | ./cat -

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

#### Structure

```bash

```

#### Unit tests

```bash
    cd go/cat
    go test - v
```

#### Build

```bash
    cd go/cat
    go build -o cc-cat ./cmd
```

#### Function tests

The  [testdata](testdata) is used which to compare alignment with **cut** to run the test use [test.sh](tests/test.sh).

```bash
./test.sh -p ../cc-cat
```

### References

### Issues/Todo

There are same as the ones in the py-cat implementation, [see](../../py/cat/README.md#issues--todos)
