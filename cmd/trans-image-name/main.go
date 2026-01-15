package main

import (
	"crypto/md5"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io/fs"
	"io/ioutil"
	"math/big"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	. "gitee.com/ls-2018/sync"
	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
	"sigs.k8s.io/yaml"
)

const base = "ccr.ccs.tencentyun.com/acejilam"

var innerRepo = []string{
	"nmlabk1dsz", "0s6fw8l7rt", "k8acwb59jt", "asb7ey0ckh", "cx0iujr1hd", "dmk7blvfhi", "m3qz8cr26i",
	"tcin8k239o", "c3xyhfajvl", "sqf3lrtm5d", "8friq1os9v", "kl46e0x7v2", "t0cakez7u1", "ut53ombafd",
	"er8c2l0ft4", "m6hnixklv8", "o0hy7f1l5q", "pfs9xyuk8b", "utj5z6cykp", "432aqtoflr", "pxsuq87he9",
	"t6yhnpcv7q", "7jstwmakc9", "q2dkfymnh7", "y1ef7ck6dr", "cz7bpuhdlk", "3mck6e20t9", "8k34l57a6c",
	"wr0mfuk9d4", "lh764rgbdj", "xfv94yiwgz", "l6jewm94pt", "o95xz0mar1", "kaemyf84i6", "7r5c2vef4i",
	"yq20ipejmw", "8hjuzgko01", "1nf85ctuov", "pdrwk3f9on", "63rgv1d2fz", "an9ydoeqsx", "vi2tmfekdy",
	"op06w8m4dq", "ruvpqdj23h", "w92zmkustx", "iszv5e2crb", "u54f81rnay", "2c7e859ina", "hpimk8va1l",
	"9vfu30gqos", "y6vrbhjx3m", "m8iyzvlj0t", "i5mp02dgju", "lneogt429q", "g3am4cdkli", "hnwopya265",
	"eg72vzc0fs", "v4qel8dg23", "b2h9zqputi", "hq28x7jgaz", "vw51banxem", "zblwujy5oa", "m40eudxnyz",
	"rax76uclqj", "1hf6imyk4b", "9edyokl1xz", "urb3vy0qn1", "h7ab0vx6yt", "6r0vqga49c", "abo3cl4jef",
	"agd469misz", "ij8gmonk7t", "tjfpbmewh5", "vdi3etfs5y", "dveb417qg8", "mxvpwiljub", "jtwaylcz97",
	"3usd7z9y2x", "h7ufbplxrk", "mrqwp7yu6a", "wfdlsk63yb", "m9ujrlae28", "ve34muab2x", "ozu9sw6pgl",
	"w75yub6mip", "oz5i4du0wp", "k9sjui3vgb", "lzyrndm3qf", "eav12mkc9o", "6bao24gj01", "23mo0bl87g",
	"95zbwqlysf", "3uvkbcgmrf", "xgfrjcd4h5", "hy9opcvd5m", "0y1tg9wj7e", "urhmniw452", "nvgm6x8t71",
	"ag4sl3r8ot", "qylw5i4623",
}

func init() {
	for i, item := range innerRepo {
		innerRepo[i] = "ib-" + item
	}
}

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
	return transImages
}

func transImageName() map[string]string {
	transImages := transRandomImageName()
	for k, v := range transFixImageName() {
		transImages[k] = v
	}
	return transImages
}

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

func handleImage(_line string) (int, int, bool) {
	line := strings.Trim(_line, " \n")

	if strings.HasPrefix(line, "image: ") {
		return strings.Index(_line, "image: "), len("image: "), true
	}
	if strings.HasPrefix(line, "- image: ") {
		return strings.Index(_line, "- image: "), len("- image: "), true
	}

	return -1, 0, false
}

func replaceImage(data string) (string, map[string]string) {
	imageMap := make(map[string]string)
	imageReverseMap := make(map[string]string)

	var finTexts []string

	for _, line := range strings.Split(data, "\n") {
		index, indexLength, handle := handleImage(line)
		if !handle || index < 0 {
			finTexts = append(finTexts, line)
			continue
		}
		newLine := strings.Trim(strings.Split(strings.Trim(line, " \n"), "#")[0], " \n")
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

func replaceImages(fileData string, filepath string) {
	var res []string
	var reverseList []string
	for _, item := range strings.Split(fileData, "\n---\n") {
		_t, rm := replaceImage(item)
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
	os.Setenv("SkipUpgradeCheck", "true")
	if NeedUpgrade() {
		cmd := exec.Command("bash", "-c", "go install -v gitee.com/ls-2018/sync/cmd/...@latest")
		cmd.Env = append(os.Environ(),
			"GOPRIVATE=gitee.com",
			"GONOSUMDB=gitee.com",
			"GONOPROXY=gitee.com",
		)
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr

		if err := cmd.Run(); err != nil {
			fmt.Println("err:", err)
		}

		cmd = exec.Command("trans-image-name", os.Args[1])
		out, err := cmd.Output()
		if err != nil {
			panic(err)
		}
		fmt.Println(string(out))
		os.Exit(0)
	}

	repoMap = transImageName()
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
