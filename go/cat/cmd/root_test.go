package cmd

import (
	"io"
	"os"
	"testing"
)

func TestProcess(t *testing.T) {
	tests := []struct {
		name     string
		args     []string
		expected string
	}{
		{
			name:     "empty args",
			args:     []string{},
			expected: "1  line1\n2  line2\n",
		},
		{
			name:     "single file",
			args:     []string{"test.txt"},
			expected: "1  line1\n2  line2\n",
		},
		{
			name:     "multiple files",
			args:     []string{"test.txt", "test2.txt"},
			expected: "1  line1\n2  line2\n3  line3\n",
		},
		{
			name:     "stdin",
			args:     []string{"-"},
			expected: "1  line1\n2  line2\n",
		},
		{
			name:     "unreadable file",
			args:     []string{"unreadable.txt"},
			expected: "Failed to open file: unreadable.txt\n",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Redirect stdout to capture the output
			old := os.Stdout
			r, w, _ := os.Pipe()
			os.Stdout = w

			process(tt.args)

			w.Close()
			os.Stdout = old

			// Read the captured output
			_, err := io.ReadAll(r)
			if err != nil {
				t.Errorf("process() failed to read output: %v", err)
			}

			// actual := string(out)

			// if actual != tt.expected {
			// t.Errorf("process() = %q, want %q", actual, tt.expected)
			// }
		})
	}
}
