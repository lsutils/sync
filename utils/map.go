package utils

import (
	"crypto/md5"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"math/big"
	"os"
	"strings"

	. "gitee.com/ls-2018/sync"
	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
	"sigs.k8s.io/yaml"
)

var repoMap = make(map[string]string)
var randomImageMap = make(map[string]string)
var fixedImageMap = make(map[string]string)

func transRandomImageName() map[string]string { // old repo name -> new repo name
	if len(randomImageMap) != 0 {
		return randomImageMap
	}

	syncs := make(map[string][]string)
	transImages := make(map[string]string)
	if os.Getenv("RandomImagePath") != "" {
		data, err := os.ReadFile(os.Getenv("RandomImagePath"))
		if err != nil {
			panic(err)
		}
		json.Unmarshal(data, &syncs)
	} else {
		json.Unmarshal(RandomData, &syncs)
	}

	for image, tags := range syncs {
		_ = tags
		imageRepoBytes := md5.Sum([]byte(image))
		imageRepo := hex.EncodeToString(imageRepoBytes[:])
		bigInt := new(big.Int).SetBytes(imageRepoBytes[:])

		index := new(big.Int).Mod(
			bigInt,
			big.NewInt(int64(len(innerRepo))),
		).Int64()
		innerBucket := innerRepo[index]

		transImages[image] = fmt.Sprintf("%s/%s:%s-", base, innerBucket, imageRepo)
	}
	randomImageMap = transImages
	return transImages
}

func transFixImageName() map[string]string {
	if len(fixedImageMap) != 0 {
		return fixedImageMap
	}

	syncs := make(map[string][]string)
	transImages := make(map[string]string)
	if os.Getenv("FixImagePath") != "" {
		data, err := os.ReadFile(os.Getenv("FixImagePath"))
		if err != nil {
			panic(err)
		}
		json.Unmarshal(data, &syncs)
	} else {
		json.Unmarshal(FixData, &syncs)
	}

	for repo, tags := range syncs {
		_ = tags
		ss := strings.Split(repo, "/")
		name := ss[len(ss)-1]
		transImages[repo] = fmt.Sprintf("%s/%s", base, name)
	}
	fixedImageMap = transImages
	return transImages
}

func PrepareTransImageName() map[string]string {
	transImages := transRandomImageName()
	for k, v := range transFixImageName() {
		transImages[k] = v
	}
	repoMap = transImages
	return transImages
}

func handleImage(_line string) (int, int, bool) {
	line := strings.Trim(_line, TrimChars)

	if strings.HasPrefix(line, "image: ") {
		return strings.Index(_line, "image: "), len("image: "), true
	}
	if strings.HasPrefix(line, "- image: ") {
		return strings.Index(_line, "- image: "), len("- image: "), true
	}

	return -1, 0, false
}

func ReplaceImage(data string) (string, map[string]string) {
	imageMap := make(map[string]string)
	imageReverseMap := make(map[string]string)

	var finTexts []string

	for _, line := range strings.Split(data, "\n") {
		index, indexLength, handle := handleImage(line)
		if !handle || index < 0 {
			finTexts = append(finTexts, line)
			continue
		}

		newLine := strings.Trim(strings.Split(strings.Trim(line, TrimChars), "#")[0], TrimChars)
		rawNewLine := newLine

		if len(strings.Split(line[index:], "/")) == 1 {
			length := len(strings.Split(newLine, " "))
			last := strings.Split(newLine, " ")[length-1]
			newLine = strings.ReplaceAll(newLine, last, "docker.io/library/"+last)
		}

		if len(strings.Split(line[index:], "/")) == 2 {
			length := len(strings.Split(newLine, " "))
			last := strings.Split(newLine, " ")[length-1]
			newLine = strings.ReplaceAll(newLine, last, "docker.io/"+last)
		}
		for k, v := range repoMap {
			if strings.Contains(newLine, k+":") {
				newLine = strings.ReplaceAll(newLine, k+":", v)
				imageMap[newLine[indexLength:]] = rawNewLine[indexLength:]
				imageReverseMap[rawNewLine[indexLength:]] = newLine[indexLength:]

			} else if strings.Contains(newLine, k) {
				newLine = strings.ReplaceAll(newLine, k, v+"latest")
				imageMap[newLine[indexLength:]] = rawNewLine[indexLength:]
				imageReverseMap[rawNewLine[indexLength:]] = newLine[indexLength:]
			}
		}

		if rawNewLine != newLine {
			finTexts = append(finTexts, line[:index]+newLine)
		} else {
			finTexts = append(finTexts, line)
		}
	}

	d := unstructured.Unstructured{}
	yaml.Unmarshal([]byte(strings.Join(finTexts, "\n")), &d)
	anons := d.GetAnnotations()
	if anons == nil {
		anons = map[string]string{}
	}
	marshal, _ := json.MarshalIndent(imageMap, "", "  ")
	if len(imageMap) > 0 {
		anons["image-replace"] = string(marshal)
	}
	d.SetAnnotations(anons)
	marshal, _ = yaml.Marshal(d.Object)
	return string(marshal), imageReverseMap
}
