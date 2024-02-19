# [Write your own cat Tool](https://codingchallenges.fyi/challenges/challenge-cat) - Python



## Solution

The code is structured under [cat]() and is using [Pipenv](https://pipenv.pypa.io/en/latest) as the package manager as I find it better than [Poetry](https://python-poetry.org/) due to the overhead in learning new package/dependency manager.

### Usage

### Example(s)

### Development

#### Unit tests

#### Function tests

### Issues & Todos
The option --show-nonprinting is tricky, The manual states this, 
> Display control characters except for LFD and TAB using ‘^’
notation and precede characters that have the high bit set with
‘M-’. 
This is not properly implemented in the current logic

## References
[cat -v, show-nonprinting](https://stackoverflow.com/questions/44694331/what-is-the-m-notation-and-where-is-it-documented)

### Topics of interest
