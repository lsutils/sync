
package main

import (
	"crypto/md5"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"
)

const base = "ccr.ccs.tencentyun.com/acejilam"

var innerRepo = []string{
	"ib-nmlabk1dsz", "ib-0s6fw8l7rt", "ib-k8acwb59jt", "ib-asb7ey0ckh", "ib-cx0iujr1hd", "ib-dmk7blvfhi", "ib-m3qz8cr26i",
	"ib-tcin8k239o", "ib-c3xyhfajvl", "ib-sqf3lrtm5d", "ib-8friq1os9v", "ib-kl46e0x7v2", "ib-t0cakez7u1", "ib-ut53ombafd",
	"ib-er8c2l0ft4", "ib-m6hnixklv8", "ib-o0hy7f1l5q", "ib-pfs9xyuk8b", "ib-utj5z6cykp", "ib-432aqtoflr", "ib-pxsuq87he9",
	"ib-t6yhnpcv7q", "ib-7jstwmakc9", "ib-q2dkfymnh7", "ib-y1ef7ck6dr", "ib-cz7bpuhdlk", "ib-3mck6e20t9", "ib-8k34l57a6c",
	"ib-wr0mfuk9d4", "ib-lh764rgbdj", "ib-xfv94yiwgz", "ib-l6jewm94pt", "ib-o95xz0mar1", "ib-kaemyf84i6", "ib-7r5c2vef4i",
	"ib-yq20ipejmw", "ib-8hjuzgko01", "ib-1nf85ctuov", "ib-pdrwk3f9on", "ib-63rgv1d2fz", "ib-an9ydoeqsx", "ib-vi2tmfekdy",
	"ib-op06w8m4dq", "ib-ruvpqdj23h", "ib-w92zmkustx", "ib-iszv5e2crb", "ib-u54f81rnay", "ib-2c7e859ina", "ib-hpimk8va1l",
	"ib-9vfu30gqos", "ib-y6vrbhjx3m", "ib-m8iyzvlj0t", "ib-i5mp02dgju", "ib-lneogt429q", "ib-g3am4cdkli", "ib-hnwopya265",
	"ib-eg72vzc0fs", "ib-v4qel8dg23", "ib-b2h9zqputi", "ib-hq28x7jgaz", "ib-vw51banxem", "ib-zblwujy5oa", "ib-m40eudxnyz",
	"ib-rax76uclqj", "ib-1hf6imyk4b", "ib-9edyokl1xz", "ib-urb3vy0qn1", "ib-h7ab0vx6yt", "ib-6r0vqga49c", "ib-abo3cl4jef",
	"ib-agd469misz", "ib-ij8gmonk7t", "ib-tjfpbmewh5", "ib-vdi3etfs5y", "ib-dveb417qg8", "ib-mxvpwiljub", "ib-jtwaylcz97",
	"ib-3usd7z9y2x", "ib-h7ufbplxrk", "ib-mrqwp7yu6a", "ib-wfdlsk63yb", "ib-m9ujrlae28", "ib-ve34muab2x", "ib-ozu9sw6pgl",
	"ib-w75yub6mip", "ib-oz5i4du0wp", "ib-k9sjui3vgb", "ib-lzyrndm3qf", "ib-eav12mkc9o", "ib-6bao24gj01", "ib-23mo0bl87g",
	"ib-95zbwqlysf", "ib-3uvkbcgmrf", "ib-xgfrjcd4h5", "ib-hy9opcvd5m", "ib-0y1tg9wj7e", "ib-urhmniw452", "ib-nvgm6x8t71",
	"ib-ag4sl3r8ot", "ib-qylw5i4623"
}

var randomImageMap map[string]string

func transRandomImageName(path string) map[string]string {
	if randomImageMap != nil {
		return randomImageMap
	}

	if path == "" {
		path = filepath.Join(getExecutableDir(), "random-tasks.json")
	}

	fileContent, err := ioutil.ReadFile(path)
	if err != nil {
		fmt.Printf("Failed to read random-tasks.json: %v", err)
		os.Exit(1)
	}

	var syncs map[string][]string
	if err := json.Unmarshal(fileContent, &syncs); err != nil {
		fmt.Printf("Failed to parse random-tasks.json: %v", err)
		os.Exit(1)
	}

	raws := make(map[string][]string)
	for image, tags := range syncs {
		raws[image] = []string{image}
	}

	transImages := make(map[string]string)
	for newName, oldImages := range raws {
		oldImage := oldImages[0]
		md5Bytes := md5.Sum([]byte(newName))
		imageRepo := hex.EncodeToString(md5.Sum([]byte(oldImage)))
		innerBucket := innerRepo[int(toBigEndianUint64(md5Bytes[:]))%len(innerRepo)]
		transImages[oldImage] = fmt.Sprintf("%s/%s:%s-", base, innerBucket, imageRepo)
	}

	randomImageMap = transImages
	return transImages
}

func getExecutableDir() string {
	ex, err := os.Executable()
	if err != nil {
		panic(err)
	}
	return filepath.Dir(ex)
}

func toBigEndianUint64(b []byte) uint64 {
	var n uint64
	for i := 0; i < len(b); i++ {
		if i < 8 {
			n = (n << 8) | uint64(b[i])
		} else {
			break
		}
	}
	return n
}

func main() {
	_a := transRandomImageName("")
	
	var lines []string
	
	if len(os.Args) > 1 {
		lines = os.Args[1:]
	} else {
		content, err := ioutil.ReadAll(os.Stdin)
		if err != nil {
			fmt.Printf("Failed to read from stdin: %v", err)
			os.Exit(1)
		}
		lines = strings.Split(string(content), "\n")
	}
	
	res := ""
	for _, line := range lines {
		if strings.TrimSpace(line) == "" {
			continue
		}
		line = strings.TrimSpace(line)
		
		if !strings.Contains(line, "acejilam/ib-") {
			res += line + "\n"
			continue
		}
		
		parts := strings.Split(line, ":")
		if len(parts) < 2 {
			res += line + "\n"
			continue
		}
		
		tagPart := parts[len(parts)-1]
		mdaParts := strings.Split(tagPart, "-")
		if len(mdaParts) < 2 {
			res += line + "\n"
			continue
		}
		mda := mdaParts[0]
		
		found := false
		for oldImage := range _a {
			imageRepoMd5 := hex.EncodeToString(md5.Sum([]byte(oldImage)))
			if imageRepoMd5 == mda {
				newLine := oldImage + ":" + strings.Join(mdaParts[1:], "-")
				res += strings.TrimSpace(newLine) + "\n"
				found = true
				break
			}
		}
		
		if !found {
			res += line + "\n"
		}
	}
	
	fmt.Print(res)
}