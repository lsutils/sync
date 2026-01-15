package sync

import (
	"io/ioutil"
	"net/http"
	"os"
	"reflect"
)

func NeedUpgrade() bool {
	random := "https://gitee.com/ls-2018/sync/raw/main/random-tasks.json"
	fix := "https://gitee.com/ls-2018/sync/raw/main/fixed-tasks.json"

	p1 := "https://gitee.com/ls-2018/sync/raw/main/cmd/trans-image-name/main.go"
	p2 := "https://gitee.com/ls-2018/sync/raw/main/cmd/trans-image-name-reverse/main.go"

	RandomData = Remote(random)
	FixData = Remote(fix)

	if os.Getenv("SkipUpgradeCheck") == "true" {
		return false
	}

	if reflect.DeepEqual(Remote(p1), Process1) && reflect.DeepEqual(Remote(p2), Process2) {
		return false
	}
	return true
}

func Remote(url string) []byte {
	resp, err := http.Get(url)
	if err != nil {
		return nil
	}
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil
	}
	return body
}
