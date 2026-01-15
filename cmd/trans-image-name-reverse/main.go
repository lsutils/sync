package main

import (
	"crypto/md5"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"math/big"
	"os"
	"strings"

	. "gitee.com/ls-2018/sync"
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

var randomImageMap = make(map[string]string)

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

func main() {
	transRandomImageName()

	var lines []string
	var linesBak []string

	if len(os.Args) > 1 {
		lines = os.Args[1:]
	} else {
		data, _ := io.ReadAll(os.Stdin)
		lines = strings.Split(string(data), "\n")
	}

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
	fmt.Println(res)

}
