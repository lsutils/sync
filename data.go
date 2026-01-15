package sync

import _ "embed"

//go:embed random-tasks.json
var RandomData []byte

//go:embed fixed-tasks.json
var FixData []byte

//go:embed cmd/trans-image-name/main.go
var Process1 []byte

//go:embed cmd/trans-image-name-reverse/main.go
var Process2 []byte

var TrimChars = " \n\r\t"
