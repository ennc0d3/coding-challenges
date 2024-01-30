// Remove unnecessary import statement

package cmd

import (
	"io"
	"os"
	"reflect"
	"strings"
	"testing"

	"github.com/enncod3/coding-challenges/cut/rangeutil"
)

type Range = rangeutil.Range

func TestProcessInput(t *testing.T) {
	tests := []struct {
		name            string
		files           []string
		delimiter       string
		outputDelimiter string
		dataType        string
		rangeList       string
		complement      bool
		zeroterminated  bool

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
			zeroterminated:  false,

			want: "f0\n0\n5\n10\n15\n20\n",
		},
		{
			name:            "failed to open files",
			files:           []string{"file2.txt", "file3.txt"},
			delimiter:       "|",
			outputDelimiter: "\t",
			dataType:        "field",
			rangeList:       "1-10",
			complement:      false,
			zeroterminated:  false,

			want: "Failed to open file: file2.txt\nFailed to open file: file3.txt\n",
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

			processInput(tt.files, tt.delimiter, tt.outputDelimiter, tt.dataType, tt.rangeList, tt.complement, tt.zeroterminated)

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

type processTestData struct {
	name            string
	input           string
	delimiter       string
	outputDelimiter string
	dataType        string
	rangeList       []Range
	complement      bool
	zeroterminated  bool
	want            string
}

func testProcessFunctionRunner(t *testing.T, tt processTestData) {
	input := strings.NewReader(tt.input)
	old := os.Stdout
	defer func() { os.Stdout = old }()

	r, w, _ := os.Pipe()
	os.Stdout = w

	if tt.complement {
		var err error
		tt.rangeList, err = rangeutil.ComplementRangeList(tt.rangeList, len(tt.input))
		if err != nil {
			t.Errorf("complementRangeList() error = %v", err)
			return
		}

	}
	process(input, tt.delimiter, tt.outputDelimiter, tt.dataType, tt.rangeList, tt.zeroterminated)

	w.Close()

	out, _ := io.ReadAll(r)

	if outStr := string(out); outStr != tt.want {
		t.Errorf("process() = [%v], want [%v]", outStr, tt.want)
		t.Errorf("Hex: process() = [% x], want [% x]", outStr, tt.want)
		t.Errorf("Quoted: process() = [%q], want [%q]", outStr, tt.want)

	}

}

func TestProcessOtherOptions(t *testing.T) {
	tests := []processTestData{
		{
			name:       "complement range list",
			input:      "123456\n",
			dataType:   "byte",
			rangeList:  []Range{{Start: 3, End: 3}, {Start: 4, End: 4}, {Start: 5, End: 5}, {Start: 2, End: 2}},
			complement: true,
			want:       "16\n",
		},

		// NUL is '\0' -> \000 in octal
		{
			name:           "process zero terminated data",
			input:          "ab\000cd\000",
			dataType:       "char",
			rangeList:      []Range{{Start: 1, End: 1}},
			zeroterminated: true,
			want:           "a\000c\000",
		},
		{
			name:           "process zero terminated data",
			input:          "ab\000cd",
			dataType:       "char",
			rangeList:      []Range{{Start: 1, End: 1}},
			zeroterminated: true,
			want:           "a\000c\000",
		},
		{
			name:           "process zero terminated data",
			input:          "a1:\000:",
			dataType:       "field",
			rangeList:      []Range{{Start: 1, End: int(^uint(0) >> 1)}},
			delimiter:      ":",
			zeroterminated: true,
			want:           "a1:\000:\000",
		},
		{
			name:           "process zero terminated muliple delimited data",
			input:          "a1:A1:YayOne\000b1:B1:BeOne\000",
			dataType:       "field",
			rangeList:      []Range{{Start: 1, End: 1}, {Start: 3, End: 3}},
			delimiter:      ":",
			zeroterminated: true,
			want:           "a1:YayOne\000b1:BeOne\000",
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
			testProcessFunctionRunner(t, tt)
		})
	}
}

func TestProcessFieldType(t *testing.T) {
	tests := []processTestData{
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
			input:           "Hello,World,How,Are,You,Today",
			delimiter:       ",",
			outputDelimiter: "|",
			dataType:        "field",
			rangeList:       []Range{{Start: 1, End: 2}, {Start: 4, End: 9999}},
			want:            "Hello|World|Are|You|Today\n",
		},
		{
			name:            "process field data type multiple ranges multiple lines",
			input:           "f1,f2,f3,f4,f5,f6\n1,2,3,4,5,6\na,b,c,d,e,f",
			delimiter:       ",",
			dataType:        "field",
			outputDelimiter: "|",
			rangeList:       []Range{{Start: 1, End: 2}, {Start: 5, End: 9999}},
			want:            "f1|f2|f5|f6\n1|2|5|6\na|b|e|f\n",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			testProcessFunctionRunner(t, tt)
		})
	}
}

func TestProcessCharType(t *testing.T) {
	tests := []processTestData{

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
			name:            "multiple_sequence_emoj",
			input:           "🤦🏼‍♂️\n🤦🏼‍♂️\nくṞ㈢ޞយଦ",
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
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			testProcessFunctionRunner(t, tt)
		})
	}
}


func TestProcessByteType(t *testing.T) {
	tests := []processTestData{
		{
			name:            "multiple_sequence_emoj",
			input:           "🤦🏼‍♂️\n🤦🏼‍♂️\nくṞ㈢ޞយଦ",
			outputDelimiter: "%",
			rangeList:       []Range{{Start: 1, End: 4}},
			dataType:        "byte",
			want:            "🤦\n🤦\nく\xe1\n",
			//want: "🤦\n🤦\nく�\n", //TODO: Understand why it doesn't print replacement character instead of \xe1
		},
		{
			name:            "multiple_byte_utf8-string",
			input:           "கற்க கற்க\nHello,World",
			outputDelimiter: "%",
			rangeList:       []Range{{Start: 1, End: 12}, {Start: 14, End: 22}},
			dataType:        "byte",
			want:            "கற்க%கற்\nHello,World\n",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			testProcessFunctionRunner(t, tt)
		})
	}
}

func TestSplitOnNulTerminator(t *testing.T) {
	tests := []struct {
		name    string
		data    []byte
		atEOF   bool
		wantAdv int
		wantTok []byte
		wantErr error
	}{
		{
			name:    "empty data",
			data:    []byte{},
			atEOF:   false,
			wantAdv: 0,
			wantTok: nil,
			wantErr: nil,
		},
		{
			name:    "data with no NUL terminator",
			data:    []byte("Hello World!"),
			atEOF:   false,
			wantAdv: 0,
			wantTok: nil,
			wantErr: nil,
		},
		{
			name:    "data with NUL terminator",
			data:    []byte("a\000"),
			atEOF:   false,
			wantAdv: 2,
			wantTok: []byte("a"),
			wantErr: nil,
		},
		{
			name:    "data with multiple NUL terminators",
			data:    []byte("Hello\000World\000"),
			atEOF:   false,
			wantAdv: 6,
			wantTok: []byte("Hello"),
			wantErr: nil,
		},
		{
			name:    "data with multiple NUL terminators and atEOF",
			data:    []byte("a\000b\000"),
			atEOF:   true,
			wantAdv: 2,
			wantTok: []byte("a"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotAdv, gotTok, gotErr := splitOnNulTerminator(tt.data, tt.atEOF)
			if gotAdv != tt.wantAdv {
				t.Errorf("splitOnNulTerminator() advance = %v, want %v", gotAdv, tt.wantAdv)
			}
			if !reflect.DeepEqual(gotTok, tt.wantTok) {
				t.Errorf("splitOnNulTerminator() token = %v, want %v", gotTok, tt.wantTok)
			}
			if gotErr != tt.wantErr {
				t.Errorf("splitOnNulTerminator() error = %v, want %v", gotErr, tt.wantErr)
			}
		})
	}
}
