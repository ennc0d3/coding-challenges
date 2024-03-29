#!/bin/bash
# shellcheck disable=SC2059

prog="cat"

tmpBaseDir="/tmp/__${prog}_test/"
outDir="${tmpBaseDir}/$$"

rm -rf "$tmpBaseDir" && mkdir -p $outDir

TestProg="../${prog}.py"
ActProg="cat"

runTests() {

    idx=0

    optTests=(
        # Simple cat
        "-n|testdata/test.txt"
        #
        "-b|testdata/test.txt"
        #
        "-sn|testdata/test.txt"
        #
        "-sb|testdata/test.txt"
        "-snb|testdata/test.txt"
        "-ET|testdata/test_specialchars.txt"
        "-s|testdata/test_specialchars.txt"

    )
    for test in "${optTests[@]}"; do
        echo "Test: $test"
        runTestLogic "$test"
    done
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
        args=$(echo "$opt" | cut -f1 -d"|")
        fileName="testdata/test.txt"
        if [[ "$opt" =~ .*\| ]]; then
            fileName=$(echo "$opt" | cut -f2 -d"|")
        fi

        echo "# ----------------------------"
        echo "# Test for [$TestProg ${args} ${fileName}]"
        echo "# ----------------------------"

        idx=$((idx + 1))
        cmd="$TestProg ${args} $fileName"
        actCmd="$ActProg ${args} $fileName"
        echo "Command: diff <($cmd) <($actCmd)"
        if diff <($cmd) <($actCmd); then
            echo "Command: $cmd and $actCmd are same: OK"
        else
            echo "Command: $cmd and $actCmd are different: FAIL"
        fi | tee -a "$outDir"/runtest.log
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
