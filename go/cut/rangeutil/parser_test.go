package rangeutil

import (
	"reflect"
	"testing"
)

func TestParseRangeList(t *testing.T) {
	tests := []struct {
		name    string
		input   string
		want    []Range
		wantErr bool
	}{
		{
			name:  "single range",
			input: "1-3",
			want:  []Range{{Start: 1, End: 3}},
		},
		{
			name:  "multiple ranges",
			input: "1-3,5-7",
			want:  []Range{{Start: 1, End: 3}, {Start: 5, End: 7}},
		},
		{
			name:  "overlapping ranges",
			input: "1-3,2-4",
			want:  []Range{{Start: 1, End: 4}},
		},
		{
			name:  "overlapping ranges with same start",
			input: "1-3,1-4",
			want:  []Range{{Start: 1, End: 4}},
		},
		{
			name:  "interval without start",
			input: "-3",
			want:  []Range{{Start: 1, End: 3}},
		},
		{
			name:  "interval without end",
			input: "1-",
			want:  []Range{{Start: 1, End: int(^uint(0) >> 1)}},
		},
		{
			name:    "interval without start and end",
			input:   "-",
			wantErr: true,
		},

		{
			name:    "invalid range",
			input:   "1-a",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := ParseRangeList(tt.input)
			if (err != nil) != tt.wantErr {
				t.Errorf("parseRangeList() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("parseRangeList() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestComplementRangeList(t *testing.T) {
	tests := []struct {
		name       string
		rangeList  []Range
		max        int
		wantRanges []Range
		wantErr    error
	}{
		{
			name:       "Test 1",
			rangeList:  []Range{{Start: 1, End: 3}, {Start: 5, End: 7}},
			max:        10,
			wantRanges: []Range{{Start: 4, End: 4}, {Start: 8, End: 10}},
			wantErr:    nil,
		},
		{
			name:       "Test 2",
			rangeList:  []Range{{Start: 1, End: 1}, {3, 3}, {Start: 5, End: 100}},
			max:        100,
			wantRanges: []Range{{2, 2}, {Start: 4, End: 4}},
			wantErr:    nil,
		},
		{
			name:       "Test 3",
			rangeList:  []Range{{Start: 1, End: 10}},
			max:        10,
			wantRanges: []Range{},
			wantErr:    nil,
		},
		{
			name:       "Range with less than max",
			rangeList:  []Range{{Start: 2, End: 9}},
			max:        10,
			wantRanges: []Range{{1, 1}, {10, 10}},
			wantErr:    nil,
		},
		{
			name:       "Range without end",
			rangeList:  []Range{{Start: 2, End: int(^uint(0) >> 1)}},
			max:        int(uint(^uint(0) >> 1)),
			wantRanges: []Range{{1, 1}},
			wantErr:    nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotRanges, err := ComplementRangeList(tt.rangeList, tt.max)
			if err != tt.wantErr {
				t.Errorf("complementRangeList() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(gotRanges, tt.wantRanges) {
				t.Errorf("complementRangeList() = %v, want %v", gotRanges, tt.wantRanges)
			}
		})
	}
}
