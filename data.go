package sync

import _ "embed"

var RandomData []byte

var FixData []byte

//go:embed cmd/trans-image-name/main.go
var Process1 []byte

//go:embed cmd/trans-image-name-reverse/main.go
var Process2 []byte
