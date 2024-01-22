// Remove unnecessary import statement

package cmd

import (
	"io"
	"os"
	"reflect"
	"strings"
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
			got, err := parseRangeList(tt.input)
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
func TestProcessInput(t *testing.T) {
	tests := []struct {
		name            string
		files           []string
		delimiter       string
		outputDelimiter string
		dataType        string
		rangeList       []Range
	}{
		{
			name:            "no files provided",
			files:           []string{},
			delimiter:       ",",
			outputDelimiter: "|",
			dataType:        "string",
			rangeList:       []Range{{Start: 1, End: 3}},
		},
		{
			name:            "single file provided",
			files:           []string{"file1.txt"},
			delimiter:       "\t",
			outputDelimiter: ",",
			dataType:        "int",
			rangeList:       []Range{{Start: 1, End: 5}},
		},
		{
			name:            "multiple files provided",
			files:           []string{"file1.txt", "file2.txt", "file3.txt"},
			delimiter:       "|",
			outputDelimiter: "\t",
			dataType:        "float",
			rangeList:       []Range{{Start: 1, End: 10}},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			processInput(tt.files, tt.delimiter, tt.outputDelimiter, tt.dataType, tt.rangeList)
			// Add assertions here to verify the expected behavior
		})
	}
}

func TestProcess(t *testing.T) {
	tests := []struct {
		name            string
		input           string
		delimiter       string
		outputDelimiter string
		dataType        string
		rangeList       []Range
		want            string
	}{
		{
			name:            "process char data type",
			input:           "Hello,World",
			outputDelimiter: "|",
			dataType:        "char",
			rangeList:       []Range{{Start: 1, End: 5}},
			want:            "Hello\n",
		},
		{
			name:            "process byte data type",
			input:           "Hello,World",
			outputDelimiter: "|",
			dataType:        "byte",
			rangeList:       []Range{{Start: 1, End: 5}},
			want:            "Hello\n",
		},
		{
			name:            "process field data type",
			input:           "Hello,World",
			delimiter:       ",",
			outputDelimiter: "|",
			dataType:        "field",
			rangeList:       []Range{{Start: 1, End: 2}},
			want:            "Hello|World\n",
		},
		{
			name:            "process field data type multiple ranges",
			input:           "Hello,World,How,Are,You",
			delimiter:       ",",
			outputDelimiter: "|",
			dataType:        "field",
			rangeList:       []Range{{Start: 1, End: 2}, {Start: 4, End: 9999}},
			want:            "Hello|World|Are|You\n",
		},
		{
			name:            "process invalid data type",
			input:           "Hello,World",
			delimiter:       ",",
			outputDelimiter: "|",
			dataType:        "invalid",
			rangeList:       []Range{{Start: 1, End: 2}},
			want:            "Invalid data type. Must be 'char', 'byte', or 'field'.\n",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			input := strings.NewReader(tt.input)
			// Keep backup of the real stdout
			old := os.Stdout
			defer func() { os.Stdout = old }()

			// Create new pipe
			r, w, _ := os.Pipe()
			os.Stdout = w

			// Call function that writes to stdout
			process(input, tt.delimiter, tt.outputDelimiter, tt.dataType, tt.rangeList)

			// Close writer
			w.Close()

			// Read everything from reader (stdout)
			out, _ := io.ReadAll(r)

			if outStr := string(out); outStr != tt.want {
				t.Errorf("process() = [%v], want [%v]", outStr, tt.want)
			}

		})
	}
}
