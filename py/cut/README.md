# [Write your own Cut Tool](https://codingchallenges.fyi/challenges/challenge-cut) - Python

I used the opporunity, to read slightly in depth about [argparse](https://docs.python.org/3/howto/argparse.html) and used it to mimic the [cut](https://linux.die.net/man/1/cut) options. This a very good but a long [tutorial](https://realpython.com/command-line-interfaces-python-argparse/) on argparse.

## Solution

The code is structured under [cut](cut) and is using [Pipenv](https://pipenv.pypa.io/en/latest) as the package manager as I find it better than [Poetry](https://python-poetry.org/) due to the overhead in learning new package/dependency manager.

### Usage

### Example(s)

### Development

#### Unit tests

#### Function tests

## Topics of interest

* [codecs](https://docs.python.org/3/library/codecs.html)
* [argparse](https://docs.python.org/3/library/argparse.html)
* io.StringIO, io.bytesIO
* f-strings, format specification
* [Finding Code points](https://codepoints.net/search?q=)
* [Unicode in 2023](https://tonsky.me/blog/unicode/)
* hd|hexdump|od|dd
* HexEditors - Bless, Ghex, xdd
* endiness
* Copying multi sequence emoj with zwj (always expands?)
* Understand Pytest discovery, Structure of tests
* The selected field ranges are print in the order they read not in the order they gave, which is not good for cut
