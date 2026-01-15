package utils

import (
	"crypto/md5"
	"encoding/hex"
	"strings"

	. "gitee.com/ls-2018/sync"
)

func ReverseImage(lines []string) string {
	var linesBak []string

	for _, line := range lines {
		linesBak = append(linesBak, line)
	}

	res := ""

	for _, line := range lines {

		if strings.Trim(line, TrimChars) == "" {
			continue
		}
		line = strings.Trim(line, TrimChars)

		if !strings.Contains(line, "acejilam/ib-") {
			res += line + "\n"
			continue
		}

		ss := strings.Split(line, ":")
		mda := strings.Split(ss[len(ss)-1], "-")[0]

		for oldImage, newImage := range randomImageMap {
			_ = newImage
			imageRepoBytes := md5.Sum([]byte(oldImage))
			imageRepoMd5 := hex.EncodeToString(imageRepoBytes[:])
			if imageRepoMd5 == mda {

				newLine := oldImage + ":" + strings.Join(strings.Split(ss[len(ss)-1], "-")[1:], "-")
				newLine = strings.Trim(newLine, TrimChars)
				res += newLine + "\n"
			}

		}

	}
	return strings.Trim(res, TrimChars)
}
