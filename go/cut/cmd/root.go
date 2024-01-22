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

	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
	"github.com/spf13/cobra"
)

type Range struct {
	Start int
	End   int
}

var rootCmd = &cobra.Command{
	Use:   "cut",
	Short: "cut is a utility that cuts out sections from each line of files",
	Long:  `A Go implementation of the GNU cut command.`,

	PreRunE: func(cmd *cobra.Command, args []string) error {
		bytes, _ := cmd.Flags().GetString("bytes")
		chars, _ := cmd.Flags().GetString("characters")
		fields, _ := cmd.Flags().GetString("fields")

		delimiter, _ := cmd.Flags().GetString("delimiter")
		outputDelimiter, _ := cmd.Flags().GetString("output-delimiter")

		log.Debug().Msgf("Delim: [%v]", delimiter)

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

		if bytes == "" && chars == "" && fields == "" {
			return errors.New("you must specify a list of bytes, characters or fields")
		}

		return nil
	},
	Run: func(cmd *cobra.Command, args []string) {

		switch {
		case verbosity == 1:
			zerolog.SetGlobalLevel(zerolog.InfoLevel)
		case verbosity > 2:
			zerolog.SetGlobalLevel(zerolog.DebugLevel)
		default:
			zerolog.SetGlobalLevel(zerolog.WarnLevel)
		}
		// Parse the range lists

		switch {
		case bytes != "":
			log.Debug().Msg("Bytes mode")
			bytesRanges, err := parseRangeList(bytes)
			log.Debug().Msgf("Bytes Ranges: [%v]", bytesRanges)
			if err != nil {
				fmt.Println("Error parsing bytes range list:", err)
				return
			}
			processInput(args, delimiter, outputDelimiter, "byte", bytesRanges)

		case characters != "":
			log.Debug().Msg("Characters mode")
			charactersRanges, err := parseRangeList(characters)
			log.Debug().Msgf("Characters Ranges: [%v] ", charactersRanges)
			if err != nil {
				fmt.Println("Error parsing characters range list:", err)
				return
			}
			processInput(args, delimiter, outputDelimiter, "char", charactersRanges)

		case fields != "":
			log.Debug().Msg("Fields mode")
			fieldsRanges, err := parseRangeList(fields)
			log.Debug().Msgf("Fields Ranges: [%v]", fieldsRanges)
			if err != nil {
				fmt.Println("Error parsing fields range list:", err)
				return
			}
			processInput(args, delimiter, outputDelimiter, "field", fieldsRanges)
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

func processInput(files []string, delimiter, outputDelimiter, dataType string, rangeList []Range) {
	if len(files) == 0 {
		// No files provided, read from stdin
		process(os.Stdin, delimiter, outputDelimiter, dataType, rangeList)
	} else {
		// Process each file
		for _, file := range files {
			f, err := os.Open(file)
			if err != nil {
				log.Error().Err(err).Msgf("Failed to open file: %s", file)
				continue
			}
			process(f, delimiter, outputDelimiter, dataType, rangeList)
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
			chars := line
			log.Debug().Msgf("Chars: [%s]", chars)
			for _, interval := range rangeList {
				if len(chars) > 0 {
					fmt.Printf("%s", chars[interval.Start-1:interval.End])
				}

			}
		case "byte":
			bytes := []byte(line)
			log.Debug().Msgf("bytes: [%v]", bytes)
			for _, interval := range rangeList {

				if len(bytes) > 0 {
					log.Debug().Msgf("Printing bytes:%v", bytes[interval.Start-1:interval.End])
					fmt.Printf("%s", bytes[interval.Start-1:interval.End])
				}
			}
		case "field":
			fields := strings.Split(line, delimiter)
			log.Debug().Msgf("fields: %v", fields)

			if len(fields) == 1 && onlyDelimited {
				continue
			}

			for _, interval := range rangeList {
				interval.End = min(interval.End, len(fields))
				if interval.Start > len(fields) {
					continue
				}
				log.Debug().Msgf("Printing fields:%v", fields[interval.Start-1:interval.End])
				for i, f := range fields[interval.Start-1 : interval.End] {
					if (i + interval.Start - 1) >= len(fields)-1 {
						fmt.Printf("%s", f)
					} else {
						fmt.Printf("%s%s", f, outputDelimiter)
					}
				}
			}
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

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}
