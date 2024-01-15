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
    modeOpts=("-f" "-c" "-b")

    fieldOptsTestsCases=(
        # No matching delimiter, so print the line
        "-f 1,2"
        # No matching delimiter, so print the line, output-delimiter specified but should be ignored
        "-f 1,2 --output-delimiter=%"
        # Basic case
        "-f 1,2  -d,"
        # Basic case, with output-delimter
        "-f 1,2,4 -d%"
        # Overlapping field ranges
        "-f 1,2-4  -d,"
        # Overlapping range, with duplicate fields
        "-f 2-4,4,5 -d, --output-delimiter=|"
    )
    runTestLogic "${fieldOptsTestsCases[@]}"

    charOptsTestsCases=(
        # No matching delimiter, so print the line
        "-c 1,2"
        # No matching delimiter, so print the line, output-delimiter specified but should be ignored
        "-c 1,2 --output-delimiter=%"
        # Basic case
        "-c 1,2"
        # Basic case, with output-delimter
        "-c 1,2,4"
        # Overlapping field ranges
        "-c 1,2-4"
        # Overlapping range, with duplicate fields
        "-c 2-4,4,5 --output-delimiter=%"
    )
    runTestLogic "${charOptsTestsCases[@]}"

    if [[ $(grep -c "FAIL" $outDir/runtest.log) -gt 0 ]]; then
        echo "[ERROR]: One or more tests failed. see $outDir/runtest.log"
        exit 1
    else
        echo "All tests passed"
        exit 0
    fi
}

runTestLogic() {

    for opt in "$@"; do
        echo "OPT:[$opt]"
        for inputFile in testdata/*.csv; do
            echo "# ----------------------------"
            echo "# Test for [$TestProg ${opt} ${inputFile}]"
            echo "# ----------------------------"

            idx=$((idx + 1))
            cmd="$TestProg ${opt} $inputFile"
            actCmd="$ActProg ${opt} $inputFile"
            ($cmd >$outDir/$idx.act)
            ($actCmd >$outDir/$idx.exp)
            (
                if diff -w $outDir/"$idx".act $outDir/"$idx".exp; then
                    echo "$inputFile: OK"
                else
                    echo "$inputFile: FAIL"
                fi
            ) | tee -a $outDir/runtest.log
        done
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
