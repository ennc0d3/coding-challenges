package cmd

import (
	"bufio"
	"errors"
	"fmt"
	"io"
	"os"
	"sort"
	"strconv"
	"strings"
	"unicode/utf8"

	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
	"github.com/spf13/cobra"
)

type Range struct {
	Start int
	End   int
}

func checkOnlyOneSet(flags ...*string) error {
	var setFlag string
	for _, flag := range flags {
		if *flag != "" {
			if setFlag != "" {
				return errors.New("only one type of list may be specified")
			}
			setFlag = *flag
		}
	}
	if setFlag == "" {
		return errors.New("you must specify a list of bytes, characters or fields")
	}
	return nil
}

var rootCmd = &cobra.Command{
	Use:   "cut",
	Short: "cut is a utility that cuts out sections from each line of files",
	Long:  `A Go implementation of the GNU cut command.`,

	PreRunE: func(cmd *cobra.Command, args []string) error {
		bytes, _ := cmd.Flags().GetString("bytes")
		chars, _ := cmd.Flags().GetString("characters")
		fields, _ := cmd.Flags().GetString("fields")

		if err := checkOnlyOneSet(&bytes, &chars, &fields); err != nil {
			return err
		}

		delimiter, _ := cmd.Flags().GetString("delimiter")
		outputDelimiter, _ := cmd.Flags().GetString("output-delimiter")

		// Check that the delimiter is empty when operating on bytes or characters
		if (bytes != "" || chars != "") && delimiter != "" {
			return errors.New("an input delimiter may be specified only when operating on fields")
		}

		if delimiter == "" {
			log.Debug().Msg("No delimiter specified, using tab")
			delimiter = "\t"
			cmd.Flags().Set("delimiter", delimiter)
		}

		if outputDelimiter == "" && fields != "" {
			log.Debug().Msg("No output delimiter specified, using input delimiter")
			cmd.Flags().Set("output-delimiter", delimiter)
		}

		return nil
	},
	Run: func(cmd *cobra.Command, args []string) {

		switch {
		case verbosity == 1:
			zerolog.SetGlobalLevel(zerolog.InfoLevel)
		case verbosity >= 2:
			zerolog.SetGlobalLevel(zerolog.DebugLevel)
		default:
			zerolog.SetGlobalLevel(zerolog.WarnLevel)
		}

		switch {
		case bytes != "":
			log.Debug().Msg("Bytes mode")
			processInput(args, delimiter, outputDelimiter, "byte", bytes)

		case characters != "":
			log.Debug().Msg("Characters mode")
			processInput(args, delimiter, outputDelimiter, "char", characters)

		case fields != "":
			log.Debug().Msg("Fields mode")
			processInput(args, delimiter, outputDelimiter, "field", fields)
		}

	},
}

var (
	bytes           string
	characters      string
	delimiter       string
	fields          string
	complement      bool
	onlyDelimited   bool
	outputDelimiter string
	zeroTerminated  bool
	verbosity       int
)

func init() {
	rootCmd.PersistentFlags().StringVarP(&bytes, "bytes", "b", "", "select only these bytes")
	rootCmd.PersistentFlags().StringVarP(&characters, "characters", "c", "", "select only these characters")
	rootCmd.PersistentFlags().StringVarP(&delimiter, "delimiter", "d", "", "use DELIM instead of TAB for field delimiter")
	rootCmd.PersistentFlags().StringVarP(&fields, "fields", "f", "", "select only these fields")
	rootCmd.PersistentFlags().BoolVarP(&complement, "complement", "n", false, "complement the set of selected bytes, characters or fields")
	rootCmd.PersistentFlags().BoolVarP(&onlyDelimited, "only-delimited", "s", false, "do not print lines not containing delimiters")
	rootCmd.PersistentFlags().StringVar(&outputDelimiter, "output-delimiter", "", "use STRING as the output delimiter the default is to use the input delimiter")
	rootCmd.PersistentFlags().BoolVarP(&zeroTerminated, "zero-terminated", "z", false, "line delimiter is NUL, not newline")
	rootCmd.PersistentFlags().CountVarP(&verbosity, "verbose", "v", "verbose output")
}

func parseRangeList(rangeList string) ([]Range, error) {
	ranges := strings.Split(rangeList, ",")
	parsedRanges := make([]Range, 0, len(ranges))

	for _, r := range ranges {

		if !strings.Contains(r, "-") {
			value, err := strconv.Atoi(r)
			if err != nil {
				return nil, err
			}
			parsedRanges = append(parsedRanges, Range{Start: value, End: value})

		} else {
			bounds := strings.Split(r, "-")

			if len(bounds) == 2 && (bounds[0] == "" && bounds[1] == "") {
				return nil, fmt.Errorf("invalid range with no endpoint: %s", r)
			}

			var start, end int
			var err error

			if bounds[0] != "" {
				start, err = strconv.Atoi(bounds[0])
				if err != nil {
					return nil, err
				}
			} else {
				start = 1
			}

			if len(bounds) > 1 && bounds[1] != "" {
				end, err = strconv.Atoi(bounds[1])
				if err != nil {
					return nil, err
				}
			} else {
				end = int(^uint(0) >> 1) // Maximum int value
			}

			parsedRanges = append(parsedRanges, Range{Start: start, End: end})
		}

	}

	// Sort the ranges by start value
	sort.Slice(parsedRanges, func(i, j int) bool {
		return parsedRanges[i].Start < parsedRanges[j].Start
	})

	// Merge overlapping ranges
	mergedRanges := make([]Range, 0, len(parsedRanges))
	currentRange := parsedRanges[0]

	for _, r := range parsedRanges[1:] {
		if r.Start <= currentRange.End {
			// If the current range overlaps with the next one, merge them
			if r.End > currentRange.End {
				currentRange.End = r.End
			}
		} else {
			// If the current range does not overlap with the next one, add it to the list and move on to the next one
			mergedRanges = append(mergedRanges, currentRange)
			currentRange = r
		}
	}

	// Add the last range
	mergedRanges = append(mergedRanges, currentRange)

	return mergedRanges, nil
}

func processInput(files []string, delimiter, outputDelimiter, dataType string, rangeList string) {

	fieldsRanges, err := parseRangeList(rangeList)
	log.Debug().Msgf("Fields Ranges: [%v]", fieldsRanges)
	if err != nil {
		log.Fatal().Err(err).Msg("Error parsing fields range list")
	}

	if len(files) == 0 {
		process(os.Stdin, delimiter, outputDelimiter, dataType, fieldsRanges)
	} else {
		for _, file := range files {
			f, err := os.Open(file)
			if err != nil {
				log.Error().Err(err).Msg("Failed to open file")
				fmt.Printf("Failed to open file: %s\n", file) /*  */
				continue
			}
			process(f, delimiter, outputDelimiter, dataType, fieldsRanges)
			f.Close()
		}
	}
}

func process(input io.Reader, delimiter, outputDelimiter, dataType string, rangeList []Range) {

	log.Debug().Msgf("Processing input dataType: [%s] with delimiter [%s], rangeList: [%v] and output delimiter [%s]", dataType, delimiter, rangeList, outputDelimiter)
	scanner := bufio.NewScanner(input)
	for scanner.Scan() {
		line := scanner.Text()

		switch dataType {
		case "char":
			handleCharType(line, rangeList, outputDelimiter)

		case "byte":
			handleByteType(line, rangeList, outputDelimiter)
		case "field":
			handleFieldType(line, delimiter, outputDelimiter, rangeList)
		default:
			fmt.Println("Invalid data type. Must be 'char', 'byte', or 'field'.")
			return
		}
		fmt.Println()
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, "reading input:", err)
	}
}

func handleFieldType(line string, delimiter string, outputDelimiter string, rangeList []Range) {
	fields := strings.Split(line, delimiter)
	log.Debug().Msgf("field mode, fields: %v, outputDelimiter:[%s]", fields, outputDelimiter)

	if len(fields) == 1 && onlyDelimited {
		return
	}
	line_fields := make([]string, 0)
	for _, interval := range rangeList {
		if interval.Start > len(fields) {
			continue
		}
		interval.End = min(interval.End, len(fields))

		selected_fields := fields[interval.Start-1 : interval.End]
		line_fields = append(line_fields, selected_fields...)

		log.Debug().Msgf("Printing fields:%v, len of fields: %d, all_fields: %v", selected_fields, len(selected_fields), line_fields)

	}
	fmt.Printf("%s", strings.Join(line_fields, outputDelimiter))
}

func handleByteType(line string, rangeList []Range, outputDelimiter string) {
	bytes := []byte(line)
	log.Debug().Msgf("byte mode: bytes: [%v]", bytes)
	for i, interval := range rangeList {

		if interval.Start > len(bytes) {
			continue
		}

		interval.End = min(interval.End, len(bytes))
		log.Debug().Msgf("Printing bytes:%s, i: %d, interval(%d:%d), output-delimiter: [%s]",
			bytes[interval.Start-1:interval.End], i, interval.Start, interval.End, outputDelimiter)
		if i > 0 && i < len(rangeList) {
			fmt.Printf("%s", outputDelimiter)
		}
		fmt.Printf("%s", string(bytes[interval.Start-1:interval.End]))

	}
}

func handleCharType(line string, rangeList []Range, outputDelimiter string) {

	log.Debug().Msg("char mode")
	runeCount := utf8.RuneCountInString(line)
	runeValues := []rune(line)

	for i, interval := range rangeList {

		if interval.Start > runeCount {
			continue
		}

		interval.End = min(interval.End, runeCount)
		log.Debug().Msgf("Printing chars:%s, i: %d, interval(%d:%d), output-delimiter: [%s]",
			line[interval.Start-1:interval.End], i, interval.Start, interval.End, outputDelimiter)
		if i > 0 && i < len(rangeList) {
			fmt.Printf("%s", outputDelimiter)
		}
		fmt.Printf("%s", string(runeValues[interval.Start-1:interval.End]))
	}
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}
