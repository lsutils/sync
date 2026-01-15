package main

import (
	"fmt"

	"gitee.com/ls-2018/sync/utils"
)

func main() {
	//var lines []string
	//
	//if len(os.Args) > 1 {
	//	lines = os.Args[1:]
	//} else {
	//	data, _ := io.ReadAll(os.Stdin)
	//	lines = strings.Split(string(data), "\n")
	//}
	lines := []string{"ccr.ccs.tencentyun.com/acejilam/ib-0y1tg9wj7e:dba37485fee3d4d76d5d82609cc9bccb-latest"}
	fmt.Println(utils.ReverseImage(lines))
}
