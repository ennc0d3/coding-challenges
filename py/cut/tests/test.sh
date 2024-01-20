#!/bin/bash
# shellcheck disable=SC2059

prog="cut"

tmpBaseDir="/tmp/__${prog}_test/"
outDir="${tmpBaseDir}/$$"

rm -rf "$tmpBaseDir" && mkdir -p $outDir

TestProg="../${prog}.py"
ActProg="cut"

runTests() {

    idx=0

    fieldOptsTestsCases=(
        # No matching delimiter, so print the line
        "-f 1,2"
        # No matching delimiter, so print the line, output-delimiter specified but should be ignored
        "-f 1,2 --output-delimiter=%"
        # Basic case
        "-f 1,2  -d,"
        # Basic case, with output-delimter
        "-f 1,2,4 -d, --output-delimiter=%"
        # Overlapping field ranges
        "-f 1,2-4  -d,"
        # Overlapping range, with duplicate fields
        "-f 2-4,4,5 -d, --output-delimiter=%"
    )
    runTestLogic "${fieldOptsTestsCases[@]}"

    charOptsTestsCases=(
        # No matching delimiter, so print the line
        "-c 1,2|testdata/sample.txt|AB\nGH\nMN\nST\n\nYZ"

        # No matching delimiter, so print the line, output-delimiter specified but should be ignored
        "-c 1,2 --output-delimiter=%|testdata/sample.txt|A%B\nG%H\nM%N\nS%T\n\nY%Z"

        "-c 1,2-4|testdata/sample.txt|ABCD\nGHIJ\nMNOP\nSTUV\n\nYZ"
        # Overlapping range, with duplicate fields
        "-c 2-4,4,5 --output-delimiter=%|testdata/unicode.txt|ﺀ⇥⇝%ហ\n⤥ሪᙂ%ฉ"

    )
    runTestCharLogic "${charOptsTestsCases[@]}"

    bytesOptsTestsCases=(
        "-b 1-9|testdata/tamil.txt"
        # Fixme: When printing bytes which can't be decode to string, am using
        # replacement characters, ideally, I should just spit the raw bytes and leave
        # encoding to the terminal
        # "-b 1-7|testdata/unicode.txt"

    )
    runTestLogic "${bytesOptsTestsCases[@]}"

    if [[ $(grep -c "FAIL" $outDir/runtest.log) -gt 0 ]]; then
        echo "[ERROR]: One or more tests failed. see $outDir/runtest.log"
        exit 1
    else
        echo "All tests passed"
        exit 0
    fi
}

runTestLogic() {

    set -x

    for opt in "$@"; do
        echo "OPT:[$opt]"
        args=$(echo "$opt" | cut -f1 -d"|")
        fileName="testdata/fourchords.csv"
        if [[ "$opt" =~ ".*\|" ]]; then
            fileName=$(echo "$opt" | cut -f2 -d"|")
        fi

        echo "# ----------------------------"
        echo "# Test for [$TestProg ${args} ${fileName}]"
        echo "# ----------------------------"

        idx=$((idx + 1))
        cmd="$TestProg ${args} $fileName"
        actCmd="$ActProg ${args} $fileName"
        ($cmd >"$outDir"/"$idx".act)
        ($actCmd >"$outDir"/"$idx".exp)
        (
            if diff -w "$outDir"/"$idx".act "$outDir"/"$idx".exp; then
                echo "$fileName: OK"
            else
                echo "$fileName: FAIL"
            fi
        ) | tee -a "$outDir"/runtest.log
        echo "# ----------------------------"
    done

}

runTestCharLogic() {

    idx=0

    for opt in "$@"; do
        echo "OPT:[$opt]"
        args=$(echo "$opt" | cut -f1 -d"|")
        fileName=$(echo "$opt" | cut -f2 -d"|")
        expected=$(echo "$opt" | cut -f3 -d"|")
        echo "# ----------------------------"
        echo "# Test for [$TestProg ${args} ${fileName}]"
        echo "# ----------------------------"

        idx=$((idx + 1))
        cmd="$TestProg ${args} $fileName"
        ($cmd >"$outDir"/"$idx".act)
        (echo -e "$expected" >"$outDir"/"$idx".exp)
        (
            if diff -w "$outDir"/"$idx".act "$outDir"/"$idx".exp; then
                echo "$fileName: OK"
            else
                echo "$fileName: FAIL"
            fi
        ) | tee -a "$outDir"/runtest.log
        echo "# ----------------------------"
    done

}

parseArgs() {

    POSITIONAL=()
    while (($# > 0)); do
        case "${1}" in
        -v | --verbose)
            set +x
            shift
            ;;
        -p | --prog)
            numOfArgs=1
            if (($# < numOfArgs + 1)); then
                shift $#
            else
                TestProg=${2}
                echo "TestProg: ${1} with value: [${2}]"
                if [[ "${2}" == "" || ! -e "$TestProg" ]]; then
                    echo "Program name required: ../${prog}.py | ../${prog}"
                    exit 1
                fi
                shift $((numOfArgs + 1))

            fi
            ;;
        *)
            POSITIONAL+=("${1}")
            shift
            echo "Usage:
                  test.sh [-p|-prog <name>] [-v|--verbose]
                    "
            exit 1

            ;;
        esac
    done

    set -- "${POSITIONAL[@]}"

}

main() {
    parseArgs "$@"
    runTests
}

main "$@"
