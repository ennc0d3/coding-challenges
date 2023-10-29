package util

import (
	"io/fs"
	"os"
	"testing"

	"github.com/google/go-cmp/cmp"
)

func TestProcessFile(t *testing.T) {
	testcases := map[string]struct {
		inputFileData string
		expFileStat   FileStat
	}{
		"AsciiWord": {
			"One",
			FileStat{"words": 1, "lines": 0, "bytes": 3, "chars": 3},
		},
		"SingleSpaceNoLF": {
			" ",
			FileStat{"words": 0, "lines": 0, "bytes": 1, "chars": 1},
		},
		"WindowsStyleJustCRLF": {
			"\r\n",
			FileStat{"words": 0, "lines": 1, "bytes": 2, "chars": 2},
		},
		"UnixStyleJustLF": {
			"\n",
			FileStat{"words": 0, "lines": 1, "bytes": 1, "chars": 1},
		},
		"EmptyFile": {
			"",
			FileStat{"words": 0, "lines": 0, "bytes": 0, "chars": 0},
		},
		"EmojFacePalmZWJ": {
			"🤦🏼‍♂️",
			FileStat{"words": 1, "lines": 0, "bytes": 17, "chars": 5},
		},
		"UnicodeSentenceTamilTirukurral": {
			"ஒழுக்கம் விழுப்பந் தரலான் ஒழுக்கம்\n" +
				"உயிரினும் ஓம்பப் படும்\n",
			FileStat{
				"chars": 58,
				"bytes": 160,
				"words": 7,
				"lines": 2,
			},
		},
		"UnicodeCrazyWeirdoWord": {
			"ẇ͓̞͒͟͡ǫ̠̠̉̏͠͡ͅr̬̺͚̍͛̔͒͢d̠͎̗̳͇͆̋̊͂͐",
			FileStat{
				"chars": 34,
				"bytes": 67,
				"words": 1,
				"lines": 0,
			},
		},
		"TwoLines": {
			"TwoLines\n\n",
			FileStat{
				"chars": 10,
				"bytes": 10,
				"words": 1,
				"lines": 2,
			},
		},
		"MultilineNoLFInLastLine": {
			`Gutenberg™
Gustavberg`,
			FileStat{
				"lines": 1,
				"words": 2,
				"bytes": 23,
				"chars": 21,
			},
		},
	}

	tmpDir, err := os.MkdirTemp("/tmp/", "wc-go*")
	if err != nil {
		t.Fatalf("Unable to create temporary directory, err: %s", err)
	}
	for name, tc := range testcases {

		t.Run(name, func(t *testing.T) {

			fp, err := os.CreateTemp(tmpDir, "*.txt")
			if err != nil {
				t.Fatalf("Unable to create tempfile err: %s", err)
			}
			if err := os.WriteFile(fp.Name(), []byte(tc.inputFileData), fs.FileMode(os.O_WRONLY)); err != nil {
				t.Fatalf("Unable to write %s, err: %s", fp.Name(), err)
			}
			// Actual test
			got := ProcessFiles([]string{fp.Name()})
			if d := cmp.Diff(tc.expFileStat, got[fp.Name()]); d != "" {
				t.Errorf("FileStat Differs (-want vs +got): %s\n", d)
			}
		})
	}

}
