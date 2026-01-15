package sync

import _ "embed"

//go:embed random-tasks.json
var RandomData []byte

//go:embed fixed-tasks.json
var FixData []byte

var TrimChars = " \n\r\t"
