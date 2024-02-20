package cmd

import (
	"bufio"
	"fmt"
	"os"
	"strings"

	"github.com/spf13/cobra"
)

const (
	VersionNumber = "0.0.1"
	Author        = "ennc0d3"
)

var (
	//Flags
	number                 bool
	numberNonBlank         bool
	squeezeBlank           bool
	showEnds               bool
	showTabs               bool
	showNonPrinting        bool
	showEndsAndNonPrinting bool
	showTabsAndNonPrinting bool
	showAll                bool

	// Debug options
	verbosity int
	version   bool

	rootCmd = &cobra.Command{
		Use:   "cat",
		Short: "Concatenate FILE(s) to standard output.",
		Long: `Concatenate FILE(s) to standard output.

		With no FILE, or when FILE is -, read standard input.`,
		Version: VersionNumber,
		PreRun: func(cmd *cobra.Command, args []string) {
			if numberNonBlank {
				number = false
			}
		},
		Run: func(cmd *cobra.Command, args []string) {
			// Run the command
			process(args)
		},
	}
)

func init() {
	rootCmd.PersistentFlags().BoolVarP(&number, "number", "n", false, "number all output lines")
	rootCmd.PersistentFlags().BoolVarP(&numberNonBlank, "number-nonblank", "b", false, "number nonempty output lines, overrides -n")
	rootCmd.PersistentFlags().BoolVarP(&squeezeBlank, "squeeze-blank", "s", false, "suppress repeated empty output lines")
	rootCmd.PersistentFlags().BoolVarP(&showEnds, "show-ends", "E", false, "display $ at end of each line")
	rootCmd.PersistentFlags().BoolVarP(&showTabs, "show-tabs", "T", false, "display TAB characters as ^I")
	rootCmd.PersistentFlags().BoolVarP(&showNonPrinting, "show-nonprinting", "v", false, "use ^ and M- notation, except for LFD and TAB")
	rootCmd.PersistentFlags().BoolVarP(&showEndsAndNonPrinting, "show-ends-and-nonprinting", "e", false, "display $, TAB, and ^C")
	rootCmd.PersistentFlags().BoolVarP(&showTabsAndNonPrinting, "show-tabs-and-nonprinting", "t", false, "display TAB characters as ^I and use ^ and M- notation, except for LFD and TAB")
	rootCmd.PersistentFlags().BoolVarP(&showAll, "show-all", "A", false, "equivalent to -vET")
	rootCmd.PersistentFlags().CountVarP(&verbosity, "verbose", "V", "verbose output")
	rootCmd.PersistentFlags().BoolVarP(&version, "version", "", false, "output version information and exit")

}

func process(args []string) {
	if len(args) == 0 {
		args = []string{"-"}
	}

	linenumber := 0
	blanks := 0
	for _, file := range args {
		if file == "-" {
			file = os.Stdin.Name()
		}
		f, err := os.Open(file)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			continue
		}

		scanner := bufio.NewScanner(f)
		for scanner.Scan() {
			linenumber++
			line := scanner.Text()

			if line == "" {
				blanks++
				if squeezeBlank && blanks > 1 {
					continue
				}
			} else {
				blanks = 0
			}

			// TODO: The linewidth behaviours is different from cat for linnumbers
			// that are greater than 6 digits. This is could be done like cat, but
			// the behaviour is not documented

			linewidth := len(fmt.Sprintf("%d", linenumber))
			if linewidth < 6 {
				linewidth = 6
			}

			if number {
				fmt.Printf("%*d\t", linewidth, linenumber)
			}

			if numberNonBlank {
				if line != "" {
					fmt.Printf("%*d\t", linewidth, linenumber)
				} else {
					continue
				}
			}

			if showEnds {
				line = line + "$"
			}

			if showTabs {
				line = strings.ReplaceAll(line, "\t", "^I")
			}

			if showNonPrinting || showEndsAndNonPrinting || showTabsAndNonPrinting {
				fmt.Fprintf(os.Stderr, "show-nonprinting not implemented")
			}

			fmt.Printf("%s\n", line)

		}

	}
}

func Execute() {
	// Run the command
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
