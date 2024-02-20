package main

import (
	"os"
	"time"

	"github.com/ennc0d3/coding-challenges/cat/cmd"
	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
)

func main() {

	writer := zerolog.ConsoleWriter{Out: os.Stderr, TimeFormat: time.RFC3339}
	log.Logger = log.Output(writer)
	zerolog.SetGlobalLevel(zerolog.WarnLevel)

	cmd.Execute()
}
