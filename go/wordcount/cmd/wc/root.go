package wc

import (
	"fmt"
	"os"

	"github.com/ennc0d3/coding-challenges/wordcount/util"
	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "wc",
	Short: "print newline, word, and byte counts for each file",
	Long: `Print newline, word, and byte counts for each FILE, and a total line if
more than one FILE is specified.`,
	Args: cobra.ArbitraryArgs,
	Run: func(cmd *cobra.Command, args []string) {

		fileNames := args
		if len(args) < 1 {
			fileNames = []string{os.Stdin.Name()}
		}
		stats := util.ProcessFiles(fileNames)

		opts := util.PrintOptions{
			Lines: LineFlag,
			Words: WordFlag,
			Bytes: ByteFlag,
			Chars: CharFlag}
		util.PrintStats(stats, opts)
	},
}

var Verbose bool
var ByteFlag bool
var CharFlag bool
var Version bool
var LineFlag bool
var WordFlag bool

func init() {

	rootCmd.PersistentFlags().BoolVarP(&Verbose, "verbose", "v", false, "verbose output")
	rootCmd.PersistentFlags().BoolVarP(&Version, "version", "V", false, "version output")

	rootCmd.Flags().BoolVarP(&ByteFlag, "bytes", "c", false, "bytes count output")
	rootCmd.Flags().BoolVarP(&CharFlag, "chars", "m", false, "char count output")
	rootCmd.Flags().BoolVarP(&LineFlag, "lines", "l", false, "line count output")
	rootCmd.Flags().BoolVarP(&WordFlag, "words", "w", false, "word count output")

}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}
