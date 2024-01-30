package rangeutil

import (
	"fmt"
	"sort"
	"strconv"
	"strings"
)

type Range struct {
	Start int
	End   int
}

func ParseRangeList(rangeList string) ([]Range, error) {
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

func ComplementRangeList(rangeList []Range, max int) ([]Range, error) {
	// Sort the range list
	sort.Slice(rangeList, func(i, j int) bool {
		return rangeList[i].Start < rangeList[j].Start
	})

	complementRanges := make([]Range, 0, len(rangeList))
	current := 1

	for _, r := range rangeList {
		if r.Start > current {
			complementRanges = append(complementRanges, Range{Start: current, End: r.Start - 1})
		}
		if r.End < max {
			if r.End+1 > current {
				current = r.End + 1
			}
			if r == rangeList[len(rangeList)-1] {
				complementRanges = append(complementRanges, Range{Start: current, End: max})
			}
		}
	}

	return complementRanges, nil
}
