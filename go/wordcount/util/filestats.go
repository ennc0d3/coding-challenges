package util

import (
	"fmt"
	"os"
	"strings"
	"unicode/utf8"
)

type FileStat map[string]int
type FileStats map[string]FileStat

func ProcessFiles(fileNames []string) FileStats {

	stats := FileStats{}

	// Process the file content
	for _, fileName := range fileNames {

		data, err := os.ReadFile(fileName)
		if err != nil {
			return nil
		}
		bytesLen := len(data)
		charLen := utf8.RuneCount(data)

		lineLen := len(strings.Split(string(data), "\n")) - 1
		wordsLen := len(strings.Fields(string(data)))

		stat := FileStat{
			"bytes": bytesLen,
			"chars": charLen,
			"lines": lineLen,
			"words": wordsLen,
		}

		stats[fileName] = stat

	}

	if len(stats) > 1 {
		totals := FileStat{}
		for _, filestats := range stats {
			totals["lines"] += filestats["lines"]
			totals["words"] += filestats["words"]
			totals["bytes"] += filestats["bytes"]
		}
		stats["totals"] = totals
	}
	return stats

}

type PrintOptions struct {
	Lines bool
	Words bool
	Bytes bool
	Chars bool
}

// TODO: Refactor this for repetition
func PrintStats(stats FileStats, printOptions PrintOptions) {

	if !printOptions.Lines && !printOptions.Words && !printOptions.Bytes && !printOptions.Chars {
		for fileName, stats := range stats {
			fmt.Printf(" %d\t%d\t%d\t%s\n", stats["lines"], stats["words"], stats["bytes"], fileName)
		}
		return

	}

	if printOptions.Bytes {
		for fileName, stats := range stats {
			fmt.Printf(" %d\t%s\n", stats["bytes"], fileName)
		}
	} else if printOptions.Words {
		for fileName, stats := range stats {
			fmt.Printf(" %d\t%s\n", stats["words"], fileName)
		}
	} else if printOptions.Chars {
		for fileName, stats := range stats {
			fmt.Printf(" %d\t%s\n", stats["chars"], fileName)
		}
	} else if printOptions.Lines {
		for fileName, stats := range stats {
			fmt.Printf(" %d\t%s\n", stats["lines"], fileName)
		}
	}

}
