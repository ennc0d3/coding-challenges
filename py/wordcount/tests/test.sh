#!/bin/bash

outDir="/tmp/__wc_test_$$/"

rm -rf /tmp/__wc_test_*/ && mkdir -p $outDir

TestProg="../wc.py"
ActProg="wc"

runTests() {

    idx=0
    modeOpts=("-c" "-m" "-l" "-w")

    for modeOpt in "${modeOpts[@]}"; do
        echo "# ----------------------------"
        echo "# Test for $TestProg ${modeOpt}   "
        echo "# ----------------------------"
        for inputFile in testdata/*.txt; do
            idx=$((idx + 1))
            $TestProg "$modeOpt" "$inputFile" >$outDir/"$idx".act

            $ActProg "${modeOpt}" "$inputFile" >$outDir/"$idx".exp
            (
                echo "# $TestProg $modeOpt $inputFile"
                if diff -w $outDir/"$idx".act $outDir/"$idx".exp; then
                    echo "$inputFile: OK"
                else
                    echo "$inputFile: FAIL"
                fi
            ) | tee -a $outDir/runtest.log
        done
        echo "# ----------------------------"

    done

    if [[ $(grep -c "FAIL" $outDir/runtest.log) -gt 0 ]]; then
        echo "[ERROR]: One or more tests failed. see $outDir/runtest.log"
        exit 1
    else
        echo "All tests passed"
        exit 0
    fi
}

parseArgs() {

    POSITIONAL=()
    while (($# > 0)); do
        case "${1}" in
        -v | --verbose)
            set +x
            shift # shift once since flags have no values
            ;;
        -p | --prog)
            numOfArgs=1 # number of switch arguments
            if (($# < numOfArgs + 1)); then
                shift $#
            else
                TestProg=${2}
                echo "TestProg: ${1} with value: [${2}]"
                if [[ "${2}" == "" || ! -e "$TestProg" ]]; then
                    echo "Program name required: ../wc.py | ../wc"
                    exit 1
                fi
                shift $((numOfArgs + 1)) # shift 'numOfArgs + 1' to bypass switch and its value

            fi
            ;;
        *) # unknown flag/switch
            POSITIONAL+=("${1}")
            shift
            echo "Usage:
                  test.sh [-p|-prog <name>] [-v|--verbose]
                    "
            exit 1

            ;;
        esac
    done

    set -- "${POSITIONAL[@]}" # restore positional params

}

main() {
    parseArgs "$@"
    runTests
}

main "$@"
