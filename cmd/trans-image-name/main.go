package main

import (
	"fmt"
	"io/fs"
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"

	"gitee.com/ls-2018/sync/utils"
)

func isDir(path string) bool {
	info, err := os.Stat(path)
	if err != nil {
		return false // 不存在或无权限
	}
	return info.IsDir()
}

func isFile(path string) bool {
	info, err := os.Stat(path)
	if err != nil {
		return false
	}
	return info.Mode().IsRegular()
}

func replaceImages(fileData string, filepath string) {
	var res []string
	var reverseList []string
	for _, item := range strings.Split(fileData, "\n---\n") {
		_t, rm := utils.ReplaceImage(item)
		for _, v := range rm {
			reverseList = append(reverseList, v)
		}
		res = append(res, _t)
	}
	if filepath == "" {
		if len(strings.Split(fileData, "\n")) == 1 {
			if len(reverseList) > 0 {
				fmt.Println(reverseList[0])
			} else {
				fmt.Println("unknow map info")
			}
		} else if len(res) > 0 {
			fmt.Println(strings.Join(res, "\n---\n"))
		} else {
			fmt.Println(res[0])
		}
	} else {
		if len(res) > 0 {
			ioutil.WriteFile(filepath, []byte(strings.Join(res, "\n---\n")), 0644)
		} else {
			ioutil.WriteFile(filepath, []byte(res[0]), 0644)
		}
	}
}

func main() {
	utils.PrepareTransImageName()
	target := os.Args[1]
	if isDir(target) {
		filepath.WalkDir(target, func(path string, d fs.DirEntry, err error) error {
			if !(strings.HasSuffix(path, ".yaml") || strings.HasSuffix(path, ".yml")) {
				return nil
			}
			if !isFile(path) {
				return nil
			}

			fileData, err := os.ReadFile(path)
			if err != nil {
				return nil
			}
			replaceImages(string(fileData), path)
			return nil
		})
	} else if isFile(target) {
		fileData, err := os.ReadFile(target)
		if err != nil {
			return
		}
		replaceImages(string(fileData), target)
	} else {
		replaceImages("image: "+target, "")
	}
}
