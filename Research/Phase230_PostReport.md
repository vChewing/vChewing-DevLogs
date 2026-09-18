# Phase 230 後置報告（PostReport）：LXCoreEX 五萬筆使用者片語承載力評估 ＋「純注音 key 早退」手術

- **評估對象**：`vChewing-LibVanguard` 之 `LXAssembly.LXCoreEX`（`Sources/LexiconAssembly/SubLMs/lxCoreEX.swift`）
  與其 key 正規化路徑（`Sources/LexiconAssembly/PinyinPhonaConverter.swift`）。
- **評估問題（事主原文）**：「請評估 LibVanguard 內 LXCoreEX 的設計是否能經受得起五萬筆使用者片語記錄的檢索、
  而不會給打字帶來遲鈍？（原廠 VanguardTextMapTrie 是至少三十萬筆記錄。）」
- **動刀裁定（事主原文）**：「如果發現是純注音字串的話（哪怕 delimiter 是 ascii minus symbol `-`），
  可略過 convertToPhonabets。」＋「LibVanguard 手術結束之後將內容同步到 vChewing-macOS。」
- **基準版本**：`vChewing-LibVanguard` git `d48486d`（2026-09-18）；手術前後皆同機同語料量測。
- **量測機／工具鏈**：Apple M4（Mac16,10），macOS 27.0（26A428），Swift 6.4.0-RELEASE，
  `swift test -c release`（`-O`、`-default-isolation MainActor`）。
- **量測靶**：`LXCoreEXScaleBench.swift`（臨時；跑畢已移出測試靶，存於
  `vChewing-LibVanguard/tmp/LXCoreEXScaleBench.swift`）。本報告之所有原始輸出見附錄。

---

## 〇、摘要

| 問題 | 結論 |
|---|---|
| 五萬筆的**檢索**會不會拖慢打字？ | **不會**。精確檢索 50k 實測 1.02 µs／次、p99 1.96 µs；300k 亦僅 1.55 µs。單鍵全鏈路（Homa 組字器 ＋ LXFacade）在完整匹配模式下，50k 庫與空庫之每鍵 p50 為 30.5 µs vs 29.4 µs——**無統計差異**。 |
| 五萬筆會不會拖慢打字？ | **會，但瓶頸不在檢索、在「載入／熱重載」**：`replaceData()` 於 50k 行實測 **11.4 秒**（300k 行 70.8 秒），而該路徑跑在 MainActor 上。 |
| 病灶？ | 91% 的載入時間花在 `String.convertToPhonabets()`：**每個 key 執行 432 次 `replacingOccurrences`**（實測 243.494 µs/key），且注音 key（含 `-`）恰好繞不過守衛。 |
| **手術後**？ | `replaceData()` 50k：11,420.1 ms → **207.8 ms**（55×）；300k：70,750.2 ms → **1,357.9 ms**（52×）；`convertToPhonabets()` 243.494 → **1.990 µs/key**（122×）。檢索端逐項同級（本手術只動建庫）。 |
| 與原廠 TextMapTrie 相比？ | **檢索同級、建庫原先是兩個數量級的差距**（同規模 50k：TextMapTrie 載入 20.6 ms／LXCoreEX 術前 11.4 s、術後 0.21 s）。TextMapTrie 之長處在 initials bucket 索引與 QueryBuffer 快取；LXCoreEX 之長處在無快取、尾端延遲極穩。 |

---

## 一、量測方法

### 1.1 語料模型

- **主語料（50k）**：50,000 行、45,006 個唯一 key（90% 新 key、10% 同 key 追加詞值）。
  音節取自倉內 `lxPlainBopomofo_RawData.swift` 之倚天中文系統注音表（**1,319 個合法音節**、37 個首字元），
  段數分佈 1 音節 2%／2 音節 40%／3 音節 30%／4 音節 15%／5 音節 8%／6 音節 5%。
  行格式為使用者片語檔之實際形制（`reverse: true`：`詞 讀音-讀音 權重`）。
  - `rawData` 2,455,049 bytes（2.34 MiB）、`keyData` 1,238,925 bytes（1.18 MiB）、
    `entries` 50,000×16 B＝800 KB ⇒ **LXCoreEX 自身淨佔 ≈4.5 MB**（RSS 增量實測 13.5–14.7 MB，
    含配置器零頭與暫存物）。
- **病理語料（50k）**：同上但**所有 key 皆以「ㄅㄚ」開頭**（42,034 唯一鍵）。
- **大語料（300k）**：300,000 行、284,617 唯一鍵、14.2 MB（95% 新 key）。

### 1.2 量測點

1. 建置／載入（`replaceData`）、`strData` 物化、RSS。
2. 精確檢索：5,000 個隨機存在鍵 ＋ 2,000 個不存在鍵。
3. 前綴檢索（`partialMatch` 路徑）：1 音節、1 首字元、2 音節、3 音節、無命中。
4. 多位置前綴掃描（狂拼）：以 **Tekkon.PinyinTrie 實際 chop 出來的 cells** ＋ 合成極端 cells。
5. **端到端打字**：真 `Homa.Assembler` ＋ `LXFacade.lxQuerier.grams(for:)`，逐音節 `insertKey` ＋ `assemble()`；
   同一組句子分別在「空庫」與「50k 庫」下各跑一次，差值即使用者片語庫之淨成本。
6. 同規模對照組：同一語料寫成 `VanguardTrie.Trie` → `serializeToTextMap` → `TextMapTrie(data:)`。

---

## 二、受測設計摘要（含複雜度）

LXCoreEX 之三件資料：`rawData: [UInt8]`（整檔位元組）、`keyData: [UInt8]`（所有唯一 key 之 UTF-8 串接）、
`entries: [CoreEXEntry]`（**逐行**索引、四枚 `UInt32`＝16 bytes、依 key 位元組序排序）；另有
`temporaryMap: [String: [Homa.Gram]]`（就地加詞）。

| 操作 | 演算法 | 複雜度 | 50k 實測（術前） |
|---|---|---|---|
| `unigramsFor(key:)` | 於 `entries` 二分搜尋 → 命中行逐行 `parseByteCells` ＋ `String(decoding:)` | O(log N·L ＋ 命中行數·L) | **1.02 µs** |
| `hasUnigramsFor(key:)` | 同上但只做二分搜尋 ＋ `temporaryMap` 字典查詢 | O(log N·L) | **0.37 µs** |
| `keys(matchingPrefix:)` | lower-bound 二分搜尋 → **線性前綴掃描**（逐鍵解碼、`Set` 去重） | O(log N ＋ M) | 0.06–0.81 ms（M＝136–1,966） |
| `unigramsFor(keyPrefix:)` | 上式 ＋ **每個命中 key 各自再二分搜尋一次** | O((M＋1)·log N) | 0.27–3.75 ms |
| `keys(matchingPrefixesByPosition:)` | 以首位置候選首字元定 lower-bound → **線性掃描 `[minInitial, maxInitial]` 位元組區間** | O(log N ＋ R)；**R＝區間內鍵數、與命中數無關** | 0.09–1.86 ms（R＝1,966–45,006） |
| `replaceData(bytes:)` | 逐行切格 → 逐 key `String` 解碼 → `convertToPhonabets()` → 字典聚合 → key 排序 → 建 blob／索引 | 實質 O(N·432·L) | **11.4 s（50k）** |
| `saveData()` | `rawData` ＋ `temporaryMap` 追加後整檔覆寫 | O(N) | 未量測 |

**設計要點**：① LXCoreEX **自身無任何查詢快取**（唯一快取在門面層 `LXFacade.unigramLRUCache`：上限 1,024 條、
指紋＝`config`＋`factoryGeneration`＋`pomGeneration`＋`gramSupplyHub.generation`，任一變動即全清）；
② `keys(matchingPrefixesByPosition:)` 之成本取決於**首字元候選之跨距**而非候選數；③ 精確路徑除命中行外不配置物件，故延遲極穩。

---

## 三、手術前的量測結果

### 3.1 建置／載入（主要風險）

| 語料 | 行數 | 唯一鍵 | `replaceData` | 每千行 | 精確檢索 mean |
|---|---|---|---|---|---|
| 2k | 2,000 | 1,792 | 462.7 ms | 231 ms | 0.93 µs |
| 5k | 5,000 | 4,482 | 2,244.9 ms | 449 ms | 1.11 µs |
| 10k | 10,000 | 8,960 | 2,805.5 ms | 281 ms | 0.93 µs |
| 20k | 20,000 | 17,931 | 4,484.3 ms | 224 ms | 2.35 µs |
| 50k | 50,000 | 44,958 | 12,737.7 ms | 255 ms | 1.25 µs |
| **300k** | 300,000 | 284,617 | **70,750.2 ms** | 236 ms | 1.55 µs |

### 3.2 精確檢索（熱路徑，無問題）

| 語料 | 操作 | n | mean | p50 | p95 | p99 | max |
|---|---|---|---|---|---|---|---|
| 50k | `unigramsFor(key:keyArray:)` | 5,000 | **1.020 µs** | 0.958 | 1.500 | 1.958 | 38.4 |
| 50k | `hasUnigramsFor(key:)`（存在） | 5,000 | **0.369 µs** | 0.375 | 0.500 | 0.583 | 0.96 |
| 50k | `hasUnigramsFor(key:)`（不存在） | 2,000 | 0.314 µs | 0.292 | 0.417 | 0.541 | 0.75 |
| 300k | `unigramsFor(key:keyArray:)` | 5,000 | **1.547 µs** | 1.417 | 2.292 | 4.375 | 96.5 |
| 300k | `hasUnigramsFor(key:)` | 5,000 | 0.541 µs | 0.500 | 0.833 | 1.000 | 2.08 |
| 病理 50k | `unigramsFor(key:keyArray:)` | 5,000 | 1.260 µs | 1.208 | 1.833 | 2.291 | 16.3 |

**判讀**：`O(log N)` 之實效極平——**六倍資料量只換來 1.5 倍單次延遲**。真機打字每鍵至多查
n(n+1)/2 個子串（6 音節＝21），且門面 LRU 吸收重複查詢；即使全數落空（21×1.5 µs ≈ 32 µs）
亦不及一幀（16 ms）之 0.2%。

### 3.3 前綴檢索（`partialMatch` 路徑）

50k 語料（45,006 鍵）：`ㄅㄠ`（136 鍵）0.060／0.270 ms；`ㄧ`（1,295 鍵）0.483／2.459 ms；
`ㄅ`（1,966 鍵）0.811／**3.747 ms**；2–3 音節前綴（各 1 鍵）0.001／0.003 ms；無命中 ≈0。
300k 語料（284,617 鍵）：`ㄅㄠ`（875 鍵）0.379／1.787 ms；`ㄧ`（8,101 鍵）3.138／15.603 ms；
`ㄅ`（12,324 鍵）5.708／**25.403 ms**。病理語料（42,034 鍵全在「ㄅㄚ」之下）：`ㄅ` 18.609／**95.159 ms**。

**判讀**：這是**唯一隨資料量線性劣化**的檢索路徑，成本 ≈ `M·log N`，且 `unigramsFor(keyPrefix:)`
比 `keys()` 貴 4–5 倍（每個命中鍵再二分搜尋一次）。注音打字之常態前綴為 2–4 音節（命中數個位數、< 10 µs），
但狂拼「只打首音節就查」會直接吃到這條線。

### 3.4 多位置前綴掃描（狂拼整詞簡拼）

50k：`ysxb`（掃 3,013 鍵）0.160／0.151 ms；`ys`（同）0.207／0.415 ms；`zhongguo`（2,172）0.090／0.094 ms；
`bpmf`（1,966）0.113／0.110 ms；合成 `[ㄅ ㄩ][ㄕ]`（掃**全庫 45,006** 鍵）1.861／**2.036 ms**；
合成 `[ㄅㄠ][ㄕ]`（1,966）0.086／0.093 ms。病理語料：`[ㄅㄆㄇㄈ]` 2.181／2.217 ms、
`[ㄅ ㄩ][ㄕ]` 3.062／**6.399 ms**（命中 1,869 鍵）。300k：`[ㄅ ㄩ][ㄕ]` 掃 284,617 鍵 ⇒ `keys()` **11.394 ms**。

### 3.5 端到端打字（真 Homa 組字器 ＋ LXFacade；每鍵 µs）

| 情境 | mean | p50 | p95 | p99 | max |
|---|---|---|---|---|---|
| 空庫，完整匹配（60 句輪替） | 33.3 | 29.4 | 72.9 | 134.4 | 236.1 |
| **50k 庫，完整匹配（60 句輪替）** | 33.7 | **30.5** | 63.7 | 113.8 | 254.4 |
| 空庫，`partialMatch`（60 句輪替） | 36.3 | 29.5 | 81.7 | 185.3 | 440.0 |
| **50k 庫，`partialMatch`（60 句輪替）** | **546.2** | 211.2 | 868.7 | **10,369.6** | **18,956.9** |
| 50k 庫，完整匹配（warm，同句連打） | 60.1 | **20.0** | 31.2 | 57.2 | **9,951.3**※ |

※ 該 9.95 ms 為整段量測之**單一**離群樣本（首次觸及 2.4 MB 位元組陣列之冷頁面觸發）：p50 與空庫同級，
其餘 239 鍵皆在 57 µs 以內。

### 3.6 同規模對照：`VanguardTrie.TextMapTrie`（同一 50k 語料）

| 指標 | LXCoreEX | TextMapTrie |
|---|---|---|
| 建庫／載入 | 11,420 ms | **20.6 ms** |
| 精確查詢（5,000 個互異鍵、逐鍵首查） | **1.02 µs** | 33.4 µs（p50 9.2／p99 153.7／max 709.5） |
| 精確查詢（同 200 鍵重複 25 輪＝打字實態） | **1.13 µs**（p99 2.9） | 1.39 µs（QueryBuffer 命中；p50 0.17／**p99 47.9／max 470.4**） |
| 前綴查詢（超集語義：1,295／1,966 鍵） | 0.48／0.81 ms（`keys()`）、2.46／3.75 ms（含 gram） | 冷 3.03／4.41 ms、**熱 0.0065／0.0099 ms** |

三點結構性差異：① **載入**——TextMapTrie 全程 byte-level、不做逐 key 拼音轉換、並預建 initials buckets，
故 50k 僅 20.6 ms（術前之 LXCoreEX 慢 550×）；② **精確查詢**——LXCoreEX 反而更快（只解碼命中行；
TextMapTrie 要解析整個 node 之 entries），但 TextMapTrie 有 QueryBuffer 可攤還；③ **前綴查詢**——
TextMapTrie 有 `keyInitialsBuckets`（以各節首字元串接為鍵之排序桶），候選集只含與查詢首字元前綴相符者；
LXCoreEX 則按首字元切區間後線性掃描，且 `[ㄅ, ㄩ]` 這類 cells 會掃過整個跨距。

---

## 四、病灶定位與歸因

**20k 行語料之成本歸因（術前）**：

| 步驟 | 耗時 | 佔比 |
|---|---|---|
| `String.convertToPhonabets()`（432 次 `replacingOccurrences`／key） | 4,366.1 ms（**243.494 µs/key**） | **≈91%** |
| Tab→空格位元組 map（0.9 MB） | 14.2 ms | 0.3% |
| `parseByteLines` 行掃描（0.9 MB） | 0.4 ms | 0.01% |
| 其餘（逐 key 解碼、字典聚合、排序、建 blob） | ≈407 ms | ≈8.5% |
| **`replaceData` 總計** | **4,787.9 ms** | 100% |

**根因**：守衛 `if isEmpty || contains("_") || !isNotPureAlphanumerical { return }` 中，
`isNotPureAlphanumerical` 判「含非半形英數字元」；注音 key（含 `-`）**正好落入不早退的一側**，
於是每個 key 走滿 432 個 pattern 之 `replacingOccurrences`。

**為何要緊**：`loadUserPhrasesData()` 之同步（`open()`）與非同步（`readFileContentAsync` →
`withFileHandleQueueSync { replaceData }`）兩條路徑最終都在 **MainActor** 上執行 `replaceData`；
故五萬筆片語庫＝主執行緒凍結約 11 秒（就地加詞之熱重載同理）。成本隨行數線性（術前 224–449 ms／千行）。

---

## 五、手術內容

### 5.1 早退守衛（`PinyinPhonaConverter.swift`，＋17／−0）

```swift
if isEmpty || contains("_") || !isNotPureAlphanumerical { return }
// 純注音字串（含以半形減號 `-` 作分隔者）不含任何半形英數，而 432 個拼音 pattern 全部由半形英數
// 組成，故一個都命中不了——唯獨尾端的空格替換仍可能生效。除該情形外一律早退，
// 免得對每個 key 空跑 432 次 `replacingOccurrences`（實測：243.5 µs/key）。
guard containsHalfWidthAlphanumerical || (newToneOne != " " && contains(" ")) else { return }
```

- 新增 `fileprivate var containsHalfWidthAlphanumerical`（`unicodeScalars.contains`，無配置掃描）。
- **第一道守衛原樣保留**：純英數字串（`ba`、`shi4jie4`）在既有行為下**不轉換**；若逕以
  「含半形英數即放行」取代第一道，`ba` 會被轉成 `ㄅㄚ`——行為變更，非本案所求。
- **空格子句之必要性**：`newToneOne` 非 `" "` 且字串含空格時，純注音字串仍可能被改寫
  （`"ㄅㄚ ㄕ"` ＋ `newToneOne: "-"` → `"ㄅㄚ-ㄕ"`），故該情形不得早退。

**放行前提（已逐條查驗）**：432 個 pattern 之鍵**全部**為 `[0-9A-Za-z]+`（1 字元 9／2 字元 82／
3 字元 183／4 字元 127／5 字元 28／6 字元 3；無空字串、無 `_`、無空白、無減號）。
故字串若不含任何半形英數，任何 pattern 皆不可能命中；唯一可能的變動即尾端空格替換。

### 5.2 回歸測項（`LXCoreEXTests.swift`，＋43／−0）

`testConvertToPhonabetsFastPathParity`（7 條斷言）：純注音（`ㄅㄚ-ㄕ`）不變；拼音照舊轉
（`ba-shi`→`ㄅㄚ-ㄕ`、`shi4-jie4`→`ㄕˋ-ㄐㄧㄝˋ`）；純英數照舊不轉（`shi4jie4`、`ba`——含既有 quirk 之釘死）；
空格替換兩態；`_NumPad_1` 照舊早退。

**驗證三件**：① **差分壓力測試**——模擬器比對新舊守衛，字母表
`{ㄅ, ㄕ, ㄚ, ㄧ, -, 空格, _, a, b, z, 1, é, 日, 😀}` 之長度 1–4 全組合（抽樣 60,000）× `newToneOne ∈ {"", " ", "-"}`
＝ **124,110 例、0 筆不一致**；② **紅綠雙驗**——錯版守衛（丟掉空格子句）使該測**恰紅 1 筆**
（`spacedBopomofo`），恢復後全綠；③ 全靶測試見下節。

---

## 六、手術後的量測結果

### 6.1 前後對照（同一合成語料、同 seed、Release、Apple M4）

| 量測項 | 手術前 | 手術後 | 倍率 |
|---|---|---|---|
| `replaceData` 50k 行 | 11,420.1 ms | **207.8 ms** | 55× |
| `replaceData` 50k 行（病理語料） | 12,292.6 ms | **220.4 ms** | 56× |
| `replaceData` 300k 行 | 70,750.2 ms | **1,357.9 ms** | 52× |
| `replaceData` 20k 行（歸因組） | 4,787.9 ms | **74.0 ms** | 65× |
| └ `convertToPhonabets()` | 4,366.1 ms（243.494 µs/key） | **35.7 ms（1.990 µs/key）** | 122× |
| └ 其餘（解析／排序／建 blob） | ≈420 ms | ≈38 ms | — |
| 建庫規模曲線（每千行） | 224–449 ms | **3.6–4.6 ms** | ≈60× |
| 50k 建庫速率 | 4,378 行/s | **240,583 行/s** | 55× |
| 精確檢索 `unigramsFor(key:)` 50k | 1.020 µs | 1.030 µs | 同級 |
| `hasUnigramsFor(key:)` 50k | 0.369 µs | 0.369 µs | 同級 |
| 前綴 `ㄧ`／`ㄅ`（50k） | 0.483／0.811 ms、2.459／3.747 ms | 0.489／0.812 ms、2.476／3.781 ms | 同級 |
| 狂拼寬 cells（掃 45,006 鍵） | 1.861／2.036 ms | 1.922／2.063 ms | 同級 |
| 病理：前綴 `ㄅ`（42,034 鍵） | 18.609／95.159 ms | 18.588／94.113 ms | 同級 |
| 端到端打字 PM=0（60 句輪替） | 33.668 µs（p50 30.542） | 34.255 µs（p50 31.333） | 同級 |
| 端到端打字 PM=1（60 句輪替） | 546.196 µs（p99 10,369.6） | 404.774 µs（p99 8,006.5） | 雜訊級※ |

※ 本手術未動任何檢索路徑；PM=1 之兩次差異屬同句集合下之執行期雜訊（其 p99 仍為毫秒級）。

### 6.2 手術後之規模曲線

| 行數 | 唯一鍵 | `replaceData` | 每千行 | 精確檢索 mean |
|---|---|---|---|---|
| 2,000 | 1,792 | 9.2 ms | 4.58 ms | 0.954 µs |
| 5,000 | 4,482 | 22.2 ms | 4.44 ms | 0.963 µs |
| 10,000 | 8,960 | 36.3 ms | 3.63 ms | 0.956 µs |
| 20,000 | 17,931 | 74.9 ms | 3.74 ms | 1.003 µs |
| 50,000 | 44,958 | 194.8 ms | 3.90 ms | 1.170 µs |
| 300,000 | 284,617 | 1,357.9 ms | 4.53 ms | 1.412 µs |

### 6.3 驗證（2026-09-18，本機實測）

- **全靶（Release）**：`vChewing-LibVanguard` 之 `swift test -c release --no-parallel --disable-sandbox`
  ⇒ **9 靶 550 支全過**（18／37／7／6／212／**199**／61／3／7；`LexiconAssemblyTests` 由 198→199＝新測項）、
  零 `failed`、零 `error:`；`vChewing-macOS` 之巢狀套件同一命令 ⇒ **9 靶 550 支全過**（同九個數字）。
- **格式管線**：兩倉 `make lintFormatUncommitted` 皆 `rc=0`；兩倉受改兩檔 md5 逐一同值
  （`PinyinPhonaConverter.swift` `82e9e42766596db350925b48ac5dfe07`、
  `LXCoreEXTests.swift` `824b1de70866f525c16755a8dbc3c57d`）、連跑兩次 md5 逐次不變；
  格式化後複跑 `LXCoreEXTests` 14 支全過。
- **兩倉對位**：`vChewing-LibVanguard` 為正本、`vChewing-macOS` 之巢狀副本逐位元組同步（各 2 檔、＋60／−0）。

---

## 七、判讀

**撐得住的部分（已是主力路徑）**：完整匹配打字每鍵 20–120 µs（含真組字引擎），五萬筆片語庫之淨增量
< 5 µs；`hasUnigramsForFast`（Homa 每鍵可用性檢查）0.37–0.55 µs／鍵；建庫手術後每千行 ≈4 ms。

**仍撐不住／仍有風險者（依嚴重度）**：

1. **`partialMatch`（狂拼）下之長文／換句輸入**：每鍵 p99 ≈ 8–10 ms、max ≈ 10–19 ms（50k）。
   同句連打時被門面 LRU 吸收（p50 ≈ 84 µs）——**這是偶發掉幀，非持續遲鈍**。
   其根因（前綴掃描 `O(M·log N)`）本質是**檢索**，非本 phase 所動。
2. **病態資料分佈**：片語高度集中於同一首音節時，單次前綴查詢 18.6 ms（`keys()`）／94–95 ms（含 gram）（50k）。
3. **300k 規模**：`unigramsFor(keyPrefix: "ㄅ")` 25.4 ms、寬 cells 掃描 11.4 ms——檢索開始進入「有感」區。
4. **殘餘建庫成本**：`convertToPhonabets()` 術後仍佔 20k 建庫之 48%（35.7／74.0 ms），來源是既有之
   `isNotPureAlphanumerical`（`map`＋`filter` 兩層中介陣列、每 key 一次配置）。**本 phase 未動**
   （守衛再怎麼早退，都要先跑過這道既有守衛），詳見下節。

**關鍵不變式**：實際打字延遲幾乎**不隨片語庫筆數變化**（主力路徑為 `O(log N)`）；
唯一隨筆數線性成長的是（a）建庫——已由本 phase 移除主要常數、（b）前綴／狂拼掃描——未動。

---

## 八、建議（本 phase 已完成 R1；餘者未動）

- **R1（已完成）**：純注音 key 略過 `convertToPhonabets()`。實測 50k 建庫 11.4 s → 0.21 s。
- **R1b（可選，未動）**：將 `isNotPureAlphanumerical` 改為無配置掃描（現為 `map`＋`filter`），
  並把兩道守衛次序對調——可再省該 48% 之大半（估 50k 再省 ≈35 ms）。屬既有熱點，非本案所求。
- **R2（未動）**：`unigramsFor(keyPrefix:)` 之 M 次二分搜尋改為「一次 lower-bound ＋ 連續掃描」
  （命中鍵在 `entries` 內本就連續）；可省 M 次比較與 M 次 `String` 解碼（2.46 ms → 估 0.5 ms 級）。
- **R3（未動）**：`keys(matchingPrefixesByPosition:)` 由「首字元跨距掃描」改為「候選首音節區間之聯集」，
  或建「首音節 → entries 區間」索引（`TextMapTrie.keyInitialsBuckets` 之輕量版）：
  50k 省 ≈1.8 ms／次、300k 省 ≈11 ms／次。
- **R4（未動）**：檢索快取。LXCoreEX 無快取、全靠門面 LRU（1,024 條、POM 一變全清）；
  若 `partialMatch` 成為常態，可於 LXCoreEX 內加小型快取。
- **R5（未動）**：載入路徑之長期方案——比照 TextMapTrie 全面 byte-level（key 只做位元組切片、
  排序於位元組上進行、輸出時才解碼）。

---

## 九、未驗事項與量測侷限

1. **語料為合成**：音節分佈取自倉內倚天注音表（等機率抽樣 ＋ 段數分佈），**非真實五萬筆片語庫**；
   若真實庫更集中於少數首音節，§3.3／§3.4 之數字會往病理欄靠攏。
2. **機器單一**：全部數據來自 Apple M4。舊機（該檔註解自承「2010–2013 舊 Mac 讀取異常緩慢」）
   與 Intel Mac 未量測；Linux／WinNT CI 未跑。
3. **未在真實 IME 行程內量測**：本報告為 LibVanguard 內部 CPU 時間，不含 IMK 宿主、選字窗繪製、
   POM 背景落盤、App Nap 等開銷；GUI 體感未驗。
4. **未驗原廠辭典筆數**：本地無 `.txtMap` 產物可查（僅 995 筆之測試樣本），
   「原廠至少三十萬筆」一項沿用提問方之前提、未獨立核實。
5. **未量測**：`saveData()` 落盤、片語編輯器 UI 路徑、POM 變更觸發門面 LRU 全清之影響鏈、
   `temporaryMap` 大量就地加詞情境。
6. **量測配置**：`swift test -c release`（`-O`）；Debug（`-Onone`）絕對值會顯著更差，不可外推。
7. **單一 seed**：`mean` 受離群樣本影響大，**請以 p50／p95 為準**；病理語料為刻意構造之上界，非現實分佈。
8. **未 commit**：本 phase 之變更待事主 finalize。

---

## 附錄 A：量測原始輸出（手術前）

50k ＋ 病理語料（節錄；完整見 `tmp/LXCoreEXScaleBench.swift` 之輸出）：

```
=== [0] corpus ===
lines=50000 uniqueKeys=45006 utf8Bytes=2455049 keyBytes=1238925
=== [1] build (replaceData) ===
replaceData: 11420.1 ms (lines/s: 4378)
lx.count=45006 isLoaded=true
RSS delta: 14.7 MB (46.7 -> 61.5)
=== [2] exact-key retrieval [50k] ===
unigramsFor(key:keyArray:) existing:   n=5000 mean=1.020µs p50=0.958 p95=1.500 p99=1.958 max=38.417
hasUnigramsFor(key:)      existing:   n=5000 mean=0.369µs p50=0.375 p95=0.500 p99=0.583 max=0.958
hasUnigramsFor(key:)      absent:     n=2000 mean=0.314µs p50=0.292 p95=0.417 p99=0.541 max=0.750
=== [3] prefix (partial-match) retrieval [50k] ===
ㄅㄠ matches=136 keys()=0.060 ms unigramsFor(keyPrefix:)=0.270 ms grams=155
ㄧ    matches=1295 keys()=0.483 ms unigramsFor(keyPrefix:)=2.459 ms grams=1446
ㄅ    matches=1966 keys()=0.811 ms unigramsFor(keyPrefix:)=3.747 ms grams=2185
=== [4] multi-position prefix scan (狂拼) [50k] ===
ysxb inRangeKeys=3013 matches=0  keys()=0.160 ms unigramsFor()=0.151 ms
ys   inRangeKeys=3013 matches=139 keys()=0.207 ms unigramsFor()=0.415 ms
wide [ㄅ ㄩ][ㄕ] inRangeKeys=45006 matches=110 keys()=1.861 ms unigramsFor()=2.036 ms
=== [6] end-to-end typing, DB: 50k corpus ===
PM=0 mixed(60 sentences x 6 keys): n=360 mean=33.668µs p50=30.542 p95=63.709 p99=113.833 max=254.417
PM=1 mixed(60 sentences x 6 keys): n=360 mean=546.196µs p50=211.166 p95=868.667 p99=10369.584 max=18956.875
=== [6] end-to-end typing, DB: empty DB ===
PM=0 mixed(60 sentences x 6 keys): n=360 mean=33.283µs p50=29.375 p95=72.916 p99=134.417 max=236.125
PM=1 mixed(60 sentences x 6 keys): n=360 mean=36.295µs p50=29.542 p95=81.709 p99=185.333 max=440.042
=== [5] pathological corpus (all keys start with ㄅㄚ) ===
lines=50000 uniqueKeys=42034 build=12292.6 ms
prefix ㄅ matches=42034 keys()=18.609 ms unigramsFor(keyPrefix:)=95.159 ms grams=50000

=== [7] 建庫規模曲線（術前）===
2000  lines build=462.7 ms  (231.37 ms/1k)
5000  lines build=2244.9 ms (448.97 ms/1k)
10000 lines build=2805.5 ms (280.55 ms/1k)
20000 lines build=4484.3 ms (224.21 ms/1k)
50000 lines build=12737.7 ms (254.75 ms/1k)
=== [8] 建庫成本歸因（20k 行）===
convertToPhonabets() × 17931 keys: 4366.1 ms (243.494 µs/key)
parseByteLines() over 0.9 MB: 0.4 ms
tab→space byte map: 14.2 ms
replaceData() total: 4787.9 ms (of which key conversion ≈ 91%)

=== [11] 300k 行語料 ===
lines=300000 uniqueKeys=284617 utf8=14.2 MB build=70750.2 ms
unigramsFor  n=5000 mean=1.547µs p50=1.417 p95=2.292 p99=4.375 max=96.500
prefix ㄧ: matches=8101  keys()=3.138 ms  unigramsFor=15.603 ms
prefix ㄅ: matches=12324 keys()=5.708 ms  unigramsFor=25.403 ms
multi-prefix wide [ㄅ ㄩ][ㄕ]: inRange=284617 keys()=11.394 ms

=== [9] TextMapTrie（同一 50k 語料）===
Trie insert 45006 keys: 80.8 ms; serialize: 62.0 ms; txtMap size: 2.16 MB
TextMapTrie init: 20.6 ms; RSS delta: 7.6 MB
getNodes(exact, 5,000 互異鍵): mean=33.420µs p50=9.208 p95=109.459 p99=153.709 max=709.542
=== [10] 熱查詢對照 ===
LXCoreEX unigramsFor (repeat 25x, no cache):        mean=1.128µs p50=0.917 p95=2.083 p99=2.916 max=78.125
TextMapTrie getNodes (repeat 25x, QueryBuffer warm): mean=1.386µs p50=0.167 p95=0.583 p99=47.875 max=470.416
TextMapTrie superset-prefix ㄅ: matchedNodes=1966 cold=4.407 ms warm=0.0099 ms
```

## 附錄 B：量測原始輸出（手術後）

```
=== [0] corpus ===
lines=50000 uniqueKeys=45006 utf8Bytes=2455049 keyBytes=1238925
=== [1] build (replaceData) ===
replaceData: 207.8 ms (lines/s: 240583)
RSS delta: 13.5 MB (46.8 -> 60.3)
=== [2] exact-key retrieval [50k] ===
unigramsFor(key:keyArray:) existing:   n=5000 mean=1.030µs p50=0.958 p95=1.500 p99=1.917 max=32.667
hasUnigramsFor(key:)      existing:   n=5000 mean=0.369µs p50=0.375 p95=0.500 p99=0.583 max=5.750
=== [3] prefix (partial-match) retrieval [50k] ===
ㄅㄠ matches=136  keys()=0.063 ms unigramsFor(keyPrefix:)=0.294 ms
ㄧ   matches=1295 keys()=0.489 ms unigramsFor(keyPrefix:)=2.476 ms
ㄅ   matches=1966 keys()=0.812 ms unigramsFor(keyPrefix:)=3.781 ms
=== [4] multi-position prefix scan (狂拼) [50k] ===
wide [ㄅ ㄩ][ㄕ] inRangeKeys=45006 matches=110 keys()=1.922 ms unigramsFor()=2.063 ms
=== [6] end-to-end typing, DB: 50k corpus ===
PM=0 mixed(60 sentences x 6 keys): n=360 mean=34.255µs p50=31.333 p95=65.708 p99=122.417 max=259.334
PM=1 mixed(60 sentences x 6 keys): n=360 mean=404.774µs p50=203.625 p95=729.000 p99=8006.500 max=10461.292
=== [5] pathological corpus ===
lines=50000 uniqueKeys=42034 build=220.4 ms
prefix ㄅ matches=42034 keys()=18.588 ms unigramsFor(keyPrefix:)=94.113 ms grams=50000

=== [7] 建庫規模曲線（術後）===
2000  lines build=9.2 ms   (4.58 ms/1k)
5000  lines build=22.2 ms  (4.44 ms/1k)
10000 lines build=36.3 ms  (3.63 ms/1k)
20000 lines build=74.9 ms  (3.74 ms/1k)
50000 lines build=194.8 ms (3.90 ms/1k)
=== [8] 建庫成本歸因（20k 行）===
convertToPhonabets() × 17931 keys: 35.7 ms (1.990 µs/key)
parseByteLines() over 0.9 MB: 0.4 ms
tab→space byte map: 13.8 ms
replaceData() total: 74.0 ms (of which key conversion ≈ 48%)

=== [11] 300k 行語料 ===
lines=300000 uniqueKeys=284617 utf8=14.2 MB build=1357.9 ms
unigramsFor n=5000 mean=1.412µs p50=1.334 p95=2.042 p99=2.541 max=26.000
```

## 附錄 C：重現方式

```sh
# 1) 把量測靶放回測試靶
cp vChewing-LibVanguard/tmp/LXCoreEXScaleBench.swift \
   vChewing-LibVanguard/Tests/LexiconAssemblyTests/

# 2) 逐項執行（-c release 必備；--disable-sandbox 為本機環境所需）
cd vChewing-LibVanguard
swift test -c release --disable-sandbox --filter 'benchAll'                   # 50k ＋ 病理語料
swift test -c release --disable-sandbox --filter 'benchScalingAndAttribution' # 規模曲線 ＋ 歸因
swift test -c release --disable-sandbox --filter 'benchTextMapTrieReference'  # TextMapTrie 對照
swift test -c release --disable-sandbox --filter 'benchWarmRepeatComparison'  # 熱查詢對照
swift test -c release --disable-sandbox --filter 'benchThreeHundredK'         # 300k（約 70 秒）

# 3) 跑畢移出（300k 一項即需 70 秒，不宜留在 CI）
rm vChewing-LibVanguard/Tests/LexiconAssemblyTests/LXCoreEXScaleBench.swift
```

量測靶輸出之完整報告存於 `/tmp/lxcoreex_scale_report.txt`（每次執行覆寫）。
