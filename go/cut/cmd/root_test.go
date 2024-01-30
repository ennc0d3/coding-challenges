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
			gotRanges, err := complementRangeList(tt.rangeList, tt.max)
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

func TestProcessInput(t *testing.T) {
	tests := []struct {
		name            string
		files           []string
		delimiter       string
		outputDelimiter string
		dataType        string
		rangeList       string
		complement      bool

		want string
	}{
		{
			name:            "single file provided",
			files:           []string{"../tests/testdata/sample.tsv"},
			delimiter:       "\t",
			outputDelimiter: ",",
			dataType:        "field",
			rangeList:       "1",
			complement:      false,
			want:            "f0\n0\n5\n10\n15\n20\n",
		},
		{
			name:            "failed to open files",
			files:           []string{"file2.txt", "file3.txt"},
			delimiter:       "|",
			outputDelimiter: "\t",
			dataType:        "field",
			rangeList:       "1-10",
			complement:      false,
			want:            "Failed to open file: file2.txt\nFailed to open file: file3.txt\n",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Keep backup of the real stdout
			old := os.Stdout
			defer func() { os.Stdout = old }()

			// Create new pipe
			r, w, _ := os.Pipe()
			os.Stdout = w

			processInput(tt.files, tt.delimiter, tt.outputDelimiter, tt.dataType, tt.rangeList, tt.complement)

			w.Close()

			// Read everything from reader (stdout)
			out, _ := io.ReadAll(r)

			if outStr := string(out); outStr != tt.want {
				t.Errorf("process() = [%v], want [%v]", outStr, tt.want)
				t.Errorf("Hex: process() = [% x], want [% x]", outStr, tt.want)
				t.Errorf("Quoted: process() = [%q], want [%q]", outStr, tt.want)
			}

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
		complement      bool
		want            string
	}{
		{
			name:            "process char data type",
			input:           "Hello,World",
			outputDelimiter: "|",
			dataType:        "char",
			rangeList:       []Range{{Start: 1, End: 5}},
			complement:      false,
			want:            "Hello\n",
		},
		{
			name:            "process char data type",
			input:           "Hello,World",
			outputDelimiter: "|",
			dataType:        "char",
			rangeList:       []Range{{Start: 1, End: 1}, {Start: 2, End: 5}},
			complement:      false,
			want:            "H|ello\n",
		},
		{
			name:            "process char data type multline",
			input:           "Hello,World\nHow Are You",
			outputDelimiter: "|",
			dataType:        "char",
			rangeList:       []Range{{Start: 1, End: 5}},
			complement:      false,
			want:            "Hello\nHow A\n",
		},
		// grapheme cluster are not supported
		{
			name:            "process unicode string type multiline",
			input:           "Ծﺀ⇥⇝ហី꒺\n\nநிற்க அதற்குத்",
			outputDelimiter: "%",
			dataType:        "char",
			rangeList:       []Range{{Start: 1, End: 3}, {Start: 5, End: 7}},
			complement:      false,
			want:            "Ծﺀ⇥%ហី꒺\n\nநிற%க அ\n",
		},
		{
			name:            "process byte data type",
			input:           "Hello,World",
			outputDelimiter: "|",
			dataType:        "byte",
			rangeList:       []Range{{Start: 1, End: 5}},
			complement:      false,
			want:            "Hello\n",
		},
		{
			name:  "multiple_sequence_emoj",
			input: "🤦🏼‍♂️\n🤦🏼‍♂️\nくṞ㈢ޞយଦ",

			outputDelimiter: "%",
			rangeList:       []Range{{Start: 1, End: 4}},
			dataType:        "byte",
			complement:      false,
			want:            "🤦\n🤦\nく\xe1\n",
			//want: "🤦\n🤦\nく�\n", //TODO: Understand why it doesn't print replacement character instead of \xe1
		},
		{
			name:            "multiple_byte_utf8-string",
			input:           "கற்க கற்க\nHello,World",
			outputDelimiter: "%",
			rangeList:       []Range{{Start: 1, End: 12}, {Start: 14, End: 22}},
			dataType:        "byte",
			complement:      false,
			want:            "கற்க%கற்\nHello,World\n",
		},
		{
			name:            "process field data type",
			input:           "Hello,World",
			delimiter:       ",",
			outputDelimiter: "|",
			dataType:        "field",
			rangeList:       []Range{{Start: 1, End: 2}},
			complement:      false,
			want:            "Hello|World\n",
		},
		{
			name:            "process field data type multiple ranges",
			input:           "Hello,World,How,Are,You,Today",
			delimiter:       ",",
			outputDelimiter: "|",
			dataType:        "field",
			rangeList:       []Range{{Start: 1, End: 2}, {Start: 4, End: 9999}},
			complement:      false,
			want:            "Hello|World|Are|You|Today\n",
		},
		{
			name:            "process field data type multiple ranges multiple lines",
			input:           "f1,f2,f3,f4,f5,f6\n1,2,3,4,5,6\na,b,c,d,e,f",
			delimiter:       ",",
			outputDelimiter: "|",
			dataType:        "field",
			rangeList:       []Range{{Start: 1, End: 2}, {Start: 5, End: 9999}},
			complement:      false,
			want:            "f1|f2|f5|f6\n1|2|5|6\na|b|e|f\n",
		},
		{
			name:       "complement range list",
			input:      "123456\n",
			dataType:   "byte",
			rangeList:  []Range{{Start: 3, End: 3}, {Start: 4, End: 4}, {Start: 5, End: 5}, {Start: 2, End: 2}},
			complement: true,
			want:       "16\n",
		},

		{
			name:            "process invalid data type",
			input:           "Hello,World",
			delimiter:       ",",
			outputDelimiter: "|",
			dataType:        "invalid",
			rangeList:       []Range{{Start: 1, End: 2}},
			complement:      false,
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
			if tt.complement {
				var err error
				tt.rangeList, err = complementRangeList(tt.rangeList, len(tt.input))
				if err != nil {
					t.Errorf("complementRangeList() error = %v", err)
					return
				}

			}
			process(input, tt.delimiter, tt.outputDelimiter, tt.dataType, tt.rangeList)

			// Close writer
			w.Close()

			// Read everything from reader (stdout)
			out, _ := io.ReadAll(r)

			if outStr := string(out); outStr != tt.want {
				t.Errorf("process() = [%v], want [%v]", outStr, tt.want)
				t.Errorf("Hex: process() = [% x], want [% x]", outStr, tt.want)
				t.Errorf("Quoted: process() = [%q], want [%q]", outStr, tt.want)

			}

		})
	}
}
