package sync

import (
	"encoding/json"
	"io/ioutil"
	"net/http"

	"k8s.io/kube-openapi/pkg/util/sets"
)

func GetImage() {
	random := "https://gitee.com/ls-2018/sync/raw/main/random-tasks.json"
	fix := "https://gitee.com/ls-2018/sync/raw/main/fixed-tasks.json"

	currentRandom := map[string][]string{}
	currentFix := map[string][]string{}
	remoteRandom := map[string][]string{}
	remoteFix := map[string][]string{}

	json.Unmarshal(RandomData, &currentRandom)
	json.Unmarshal(FixData, &currentFix)
	json.Unmarshal(Remote(random), &remoteRandom)
	json.Unmarshal(Remote(fix), &remoteFix)

	for k, tags := range remoteRandom {
		currentRandom[k] = sets.NewString(tags...).Union(sets.NewString(currentRandom[k]...)).List()
	}
	for k, tags := range remoteFix {
		currentFix[k] = sets.NewString(tags...).Union(sets.NewString(currentFix[k]...)).List()
	}

	marshal, _ := json.Marshal(currentRandom)
	RandomData = marshal
	marshal, _ = json.Marshal(currentFix)
	FixData = marshal
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
