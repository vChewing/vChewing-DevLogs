# Phase 233 術後調查報告：`isSequentiallyTypedRawKeyOrder` 對 MixedAlnum 的可用性評估

> 評估日期：2026-09-20。範圍：`vChewing-LibVanguard`（Tekkon ＋ Typewriter 兩層）。
> 背景：Phase 233 依需求於 Tekkon 新增讀音序列檢證 API `isSequentiallyTypedRawKeyOrder(_:suffixOnly:)`，
> 該 Phase 的規格自陳其最終用途為「對 `vChewing-LibVanguard` 的 MixedAlnum 打字模式的體驗改良工作產生一些輔助效益」。
> 該 API 至今**尚無任何呼叫端、亦未 commit**。本文即為此評估該 API「是否接得起來、接起來之後改善得了什麼」的術後沉澱。
> **本文不含任何執行期實測**：全部判斷來自靜態閱讀——P233 規格與實作（`Sources/Tekkon/Tekkon_SyllableComposer.swift`）、
> MixedAlnum 現行實作（`Sources/LibVanguard/Typewriter/Typewriter_MixedAlphanumerical.swift`，866 行）、
> 以及既有測項清單（`Tests/LibVanguardTests/InputHandlerTests_Cases4.swift` 等）。

---

## 一、結論速覽

| 問題 | 判斷 |
|---|---|
| 能不能接？ | **能**，且屬「收斂重複邏輯」型的手術。 |
| 有沒有效？ | **有，但效力僅限於「必要條件過濾」這一層。** |
| 最確定的收益在哪？ | **條件五（不得覆寫修正）**——現行以「鍵數 == 佔用槽數」這個長度代理量近似，該代理量在**動態排列（尤其大千26）下已知會誤判**；P233 的條件三刻意以「最終值首度出現之鍵序」為準，正是為不誤殺動態排列的合法編碼而設計。 |
| 解不解得了頭號痛點？ | **解不了。**「全 parser-covered 短英文 token 持續鍵入時仍可能 zhuyin-first」是兩個**都合法**的讀法之間的**平手**；P233 是**合法性**判定器，對平手一律回 true。 |
| 最大風險？ | **API 的複製成本**——`isSequentiallyTypedRawKeyOrder` 內部 `var shadow = self` ＋ `clear()` ＋ 全串重播，而 `bestAutoSplitCandidate` 已明言「重用單一 trial composer 以減少 struct 複製與 heap 分配」。直接塞進該迴圈會把刻意省下的成本加回來。 |
| 建議路線？ | 三階：①先換掉已知壞掉的長度代理量；②再收斂 `shouldPreferASCIIWordPath` 與 `isLeadingToneBlocked`；③**不要**期待它解決短英文 token。 |

---

## 二、P233 交付物的性質

### 2.1 它是一個「必要性判定器」，不是分類器

`isSequentiallyTypedRawKeyOrder` 的語意是「這串字**是否為**按正確順序打出來的一個 plausible 讀音」。
因此它的兩個回傳值不對稱：

- 回 **false** ⇒ 有資訊量。「這串**不可能**是一個讀音」——可以直接判死。
- 回 **true** ⇒ 資訊量低。「這串**可能**是一個讀音」——但**不排除**它同時也是英文。

這個不對稱是整份評估的樞軸。MixedAlnum 的難點從來不是「這串能不能當讀音」，而是
「這串**同時**能當讀音、又能當英文時該選誰」。

### 2.2 五條件的資訊量分佈

| 條件 | 內容 | 在 MixedAlnum 語境下的作用 |
|---|---|---|
| ① | 每字元須為該排列之合法按鍵且被引擎接受 | **強過濾**。直接排除「含非注音鍵」的字串。 |
| ② | 重播後須 `isPronounceable` | **強過濾**。排除「鍵都合法但組不出音」。 |
| ③ | 最終仍填著之各槽，其最終值首度出現之鍵序須隨 聲→介→韻→調 單調不減 | **中過濾**。排除亂序輸入（先韻後聲等）。 |
| ④ | 曾鍵入聲調者，最終不得失落該聲調 | **中過濾**。排除「聲調被後續鍵吃掉」。 |
| ⑤ | 靜態注音排列且非 `suffixOnly` 時，不得以另一鍵改寫既有非空槽值 | **弱過濾，但正是平手問題的核心訊號**。 |

條件五的適用範圍經 P233 實測界定為「靜態注音排列」：動態排列之合法編碼本即由引擎跨鍵改寫槽值
（倚天26 之 `ge`＝ㄐㄧ：鍵 `g` 先寫ㄓ、鍵 `e` 再觸發糾正為ㄐ），拼音排列亦本就逐鍵清除重建，
故 `enforcesNoOverwriteCorrection = !suffixOnly && !parser.isDynamic && !parser.isPinyin`。

---

## 三、為什麼對 MixedAlnum 仍然值得做

### 3.1 現行程式碼正在手工模擬同一組條件——而且分成七處各寫一份

`Typewriter_MixedAlphanumerical.swift` 內可逐一對上 P233 的五條件，但每一條都是**不同的、彼此不一致的近似**：

| P233 條件 | 現行近似 | 落點 |
|---|---|---|
| ① | `handler.composer.inputValidityCheck(charStr:)` ＋ `receiveKey` 之回傳值 | `buildAutoSplitCandidate`、主流程多處 |
| ② | `trialComposer.isPronounceable` | `bufferIsSingleSyllablePhonetic`、`buildAutoSplitCandidate`、主流程 |
| ③ | `trialComposer.enforceCSVTOrdering = true` ＋ `receiveKey(fromScalar:)` 回 false 即整個候選作廢 | `buildAutoSplitCandidate` |
| ④ | `trialComposer.hasIntonation() \|\| suffixEndsWithSpace`；另立 `isLeadingToneBlocked` | 主流程、`buildAutoSplitCandidate` |
| ⑤ | `hasNoDestructiveOverwrite = fullInput.count == occupiedSlotCount`（**長度代理量**） | 主流程至少兩處 |
| （⑤ 的另一個近似） | `shouldPreferASCIIWordPath`：數「非前進式槽消耗」（`afterOccupied <= beforeOccupied`）達 `minimumOverwriteCount` 次 | 獨立啟發式 |

**同一個概念七處各一份，正是回歸風險的來源。** 把這一層收斂成單一權威 API 是明確的正收益，
而且與 P233 規格所述之最終用途完全吻合。

### 3.2 最可兌現的一項：條件五的長度代理量在動態排列下是壞的

現行以「**鍵數 == 佔用槽數**」當作「無破壞性覆寫」的代理量：

```swift
let hasNoDestructiveOverwrite = fullInput.count == occupiedSlotCount
```

這個等式**預設「一鍵一槽」**。但動態排列的合法編碼本來就是一鍵多寫：
大千26 之 `qquu`＝ㄅㄚ 是 **4 鍵、2 槽**（首擊 `q`→ㄆ、次擊 `q`→ㄅ），
`fullInput.count == occupiedSlotCount` 直接不成立，於是合法輸入被誤判為「破壞性覆寫」。

程式碼裡留有兩處痕跡，可見此事已被察覺，但只能以區域豁免處理：

1. `private var maxSingleSyllableKeyCount` 之中：`case .ofDachen26: 6 // 這是酷音大千26鍵的顯著缺點`
2. Space 分支之中：`guard handler.composer.parser != .ofDachen26 else { return false }`
   ——直接把該檢查對大千26 整條停用

P233 的條件三**正是為此設計**：它不看「逐寫皆單調」（那會誤殺 `qquu`），
而看「**最終值首度出現之鍵序**」；同鍵之重寫不留可觀測痕跡、不影響判定。
其文件明載此為「實測所得之界定、非權宜放寬」，並以五個動態排列、共 7337 筆語料於 `suffixOnly: true`
模式逐筆檢證零誤殺。

⇒ **這是可以直接兌現的改善**：把兩個區域豁免換成一個有定義的判準。

### 3.3 覆寫修正的判準化

現行對「按錯再按對」的處理，只有 `shouldPreferASCIIWordPath` 這種與 `minimumOverwriteCount`
掛鉤的**計數式**啟發（預設 2，Space 路徑傳 1）。P233 把它變成有定義的判定：
「以**另一鍵**改寫既有非空槽值」；且明確排除兩種無害情形——同鍵之重寫（`qquu`）與同值之重寫（`ll`）。
P233 的實測例把界線畫得很清楚：大千 `dcl`／`qn`／`cl34` 預設假、`suffixOnly: true` 真；
`cl`／`ll` 兩者皆真。

---

## 四、它解不了的部分（必須先講清楚，以免期待落空）

### 4.1 頭號痛點是「平手」，不是「非法」

MixedAlnum 的已知限制是：**全 parser-covered 短英文 token 持續鍵入時仍可能 zhuyin-first**。
`tod`、`film`、`hell` 這類字串的特性是——每個字母都是該排列下的合法注音鍵、且按序打出來
**確實可以**是一個 plausible 讀音。P233 對它們會回 **true**，因為它們**真的是**合法的按序輸入。

要把 true 翻成「所以是中文」，還需要**另一種決策訊號**：

- 詞庫命中與機率（現行已用：`hasGrams`／`bestProbability`）
- 大小寫（現行已用：`suffixHasUppercase`、`shouldBlockPhoneticAbsorption`）
- 或一份**封閉的英文白名單**

P233 本身**刻意不碰**這一層：其裁定 (b) 明示「合理」之權威維持引擎層 `isPronounceable`，
未採靜態讀音表 `allPossibleReadings`。這是正確的邊界劃分，但也意味著
**接上 P233 之後，平手問題一格都沒有前進**。

### 4.2 業界對照：微軟新注音的行為

台灣市場長青的微軟新注音，其自有的中英混打**並不做「全域最優切分搜尋」**。它的路線是：

- 以一組與輸入法同生共死的**輸入鍵集合**界定「哪些鍵算中文輸入」；
  集合**補集之外**的鍵，一律就是英數段的自然邊界（不需要一份「終止鍵清單」）。
- 只有極少數特例走硬性規則（例如網址／電郵開頭那一類固定字串）。
- 另有一份**極小的封閉字表**處理「整串恰為已知英文詞」的情形。

換言之，微軟把「中文／英文」的判定壓在**與語言無關的字元類邊界**上，
只在少數特例才動用詞表；而 vChewing 的 auto-split 是在**每次按鍵**列舉所有後綴長度
（`for suffixLength in 1 ... maxSuffixLength`）逐個建 composer 再比序。
兩者是兩種取捨：微軟的守備範圍窄但成本極低且行為可預測；vChewing 的覆蓋面廣但啟發式堆疊深。

這個對照不是要主張改弦更張，而是要指出：**「不做搜尋」在業界是被驗證可行的一條路**。
若日後真要處理平手問題，往「封閉資源界定邊界」的方向走，成本會比再加一層啟發式低得多。

---

## 五、接線前的三個實務顧慮

### 5.1 複製成本（我認為這是最容易被忽略的一項）

`isSequentiallyTypedRawKeyOrder` 的實作是：

```swift
var shadow = self
shadow.clear()
shadow.enforceCSVTOrdering = false
// …逐 scalar 重播，並以 [[String: Int]] × 4 ＋ previousValues ＋ lastWritingKeyBySlot 記帳…
```

而 `bestAutoSplitCandidate` 之中有一行明寫的設計約束：

```swift
// 重用單一 trial composer 以減少 struct 複製與 heap 分配。
var sharedComposer = handler.composer
```

它之所以要重用，是因為每次按鍵要跑最多 `maxSuffixLength`（4–6）輪候選。
**直接在最內圈呼叫 P233，等於把刻意省下的複製成本加回來**（且 P233 內含四張
`[String: Int]` 與兩個定長陣列，屬 per-call 配置）。

⇒ **建議**：先為 Tekkon 補一個 `inout` 重用變體（或令呼叫端傳入一個已 `clear()` 的 shadow composer），
再於 auto-split 迴圈內使用。這是**接線的前置工作**，不是接線後的最佳化。

### 5.2 這不是等價替換，而是行為變更

P233 **刻意關閉** `enforceCSVTOrdering` 並自行觀測槽序；現行 `buildAutoSplitCandidate`
則是**開啟**它、靠 `receiveKey` 回 false 來擋。兩者對某些字串的判定**會不同**——
P233 的條件三較寬（只在「最終值」上要求單調）、條件五較嚴（額外禁止跨鍵覆寫）。

⇒ 這是一次**行為變更**，必須以既有測項逐案比對，不能當純重構提交。

### 5.3 `suffixOnly` 的選擇要逐一決定，不能全站統一

這是本次評估中**最需要留神**的一點：

- `bestAutoSplitCandidate` 所評估的是「**獨立的**後綴」（`String(fullInput.suffix(suffixLength))`）。
  既然是獨立評估，語意上應取 **`suffixOnly: false`**，以**保留**條件五——
  而條件五恰恰是 `tod`／`film` 這類判別最需要的那條。
- `suffixOnly: true` 會**關掉**條件五，適合的是「整串＝ASCII 前綴 ＋ 尾段讀音」的**整段**判定語境。

若在此處弄反，等於在**最需要條件五的地方**把它關掉——那不是「改善無效」，而是**倒退**。

---

## 六、建議的推進順序

**第一階（低風險、高確定性）— 換掉已知壞掉的長度代理量**

只動「已經知道代理量是壞的」的地方，優先序：

1. `hasNoDestructiveOverwrite`（主流程至少兩處）
2. 連帶移除 `case .ofDachen26: 6` 與 `guard handler.composer.parser != .ofDachen26 else { return false }`
   兩個區域豁免

護欄：`test_IH405_MixedAutoSplitASCIIAndPhoneticSuffix`、
`test_IH408_MixedAutoSplitBoundaryCases`、`test_IH409_MixedSpaceFinalizeAutoSplit`、
`test_IH410_MixedLeadingIntonationAlwaysBlockedRegardlessOfPref`，
以及 `test_IH402`／`IH403`／`IH404`／`IH406`／`IH411`～`IH414`／`IH435`／`IH436` 等既有 MixedAlnum 測項。

**第二階（中風險）— 收斂計數式啟發**

把 `shouldPreferASCIIWordPath` 的「非前進式槽消耗計數」換成 P233 條件五，
並把 `isLeadingToneBlocked` 併入條件三／四。此階的風險在於
`minimumOverwriteCount` 這個旋鈕（預設 2、Space 路徑 1）承載了不少既有行為
（`tod`／`film` 的保護、`aiq`／`aijo6` 的放行），必須逐案回歸。

**第三階（不建議做）— 期待 P233 解決短英文 token 的 zhuyin-first**

那是平手問題，需要**分類訊號**而非更好的過濾器。若真要推進，見 §4.2 的方向。

---

## 七、殘餘風險與已知限度

1. **本文無實測。**「複製成本」一項是**推論**（依實作與註解），非量測。建議第一階動工前先做一次
   微基準（同一按鍵序列、在 auto-split 決策點量 CPU time／配置次數），再決定是否需要 §5.1 的 `inout` 變體。
2. **P233 前置未完成。** 該 Phase 五處落點皆未 commit，且 API 無任何呼叫端。
   「接線」的前提是 P233 先落地。
3. **本次未讀 `BPMFFullMatchTypewriter` 與 `InputHandler` 的分診路徑。**
   MixedAlnum 有相當比例的鍵是轉交給 `BPMFFullMatchTypewriter` 處理的
   （`onLexiconMatchFailure` 回退、`bufferIsSingleSyllablePhonetic` 分支等），
   改動 `hasNoDestructiveOverwrite` 是否外溢到那些路徑，本文只做了局部評估。
4. **`suffixOnly` 的語意選擇（§5.3）若判斷有誤，整項收益為負。** 建議在第一階實作時，
   以「同一批測資在兩種 `suffixOnly` 設定下的差異」先產出一張對照表，再決定。

---

## 八、附錄：P233 條件 ↔ 現行近似碼對照（供手術時逐項打勾）

| # | P233 條件 | 現行近似碼（皆在 `Typewriter_MixedAlphanumerical.swift`） | 建議處置 |
|---|---|---|---|
| ① | 合法按鍵且被引擎接受 | `inputValidityCheck(charStr:)`＋`receiveKey` 回傳值 | 保留，可交由 P233 統一 |
| ② | 須可發音 | `trialComposer.isPronounceable` | 保留，可交由 P233 統一 |
| ③ | 最終值首度出現之鍵序單調 | `enforceCSVTOrdering = true` ＋ `receiveKey` 失敗即丟 | **替換**（語意較嚴，須逐案比對） |
| ④ | 聲調不得失落 | `hasIntonation() \|\| suffixEndsWithSpace`；`isLeadingToneBlocked` | **併入** |
| ⑤ | 不得跨鍵覆寫修正 | `hasNoDestructiveOverwrite`（長度代理量）；`shouldPreferASCIIWordPath`（計數式） | **替換（第一階）／收斂（第二階）** |
| — | `suffixOnly` | 無對應概念（`requiresWordLikePrefix` 為另一回事） | **新增決策**，逐呼叫端指定 |

---

*本文為評估性術後報告，不含程式碼變更、不含實測數據。所引之既有測項名稱與檔案路徑皆為現況；
若該等檔案於後續 Phase 更動，請以 HEAD 為準。*

---

## 追記（2026-09-20，Phase 234 施術後之覆核）

本報告之建議已有相當部分付諸實作（見 `vChewing-DevLogs/Reqs4LLM/Archive_P201-P300/Reqs_0231-0240.md` 之 Phase 234）。
以下為本次**實測**對本報告各項判斷之覆核結果——**推翻者一項、成立者若干、未涉者一項**，記於此以免日後誤引。

### 被推翻者：§8「以 P233 條件五**替換**長度代理量」在靜態排列下不成立

本報告 §8 之附錄表將條件五 ↔ `hasNoDestructiveOverwrite` 之處置記為「替換（第一階）」，§3.1 亦以「收斂成單一權威」為正面論述。
**實作後 `test_IH400_MixedAlnumKanjiInputTest_Izanami`（前綴 `ai`）當場紅 4 筆**，症狀為 `ai` 前綴未被遞交、整段 `ㄇㄛˊ` 被吞為單一讀音「模」。

根因在於**兩個問題並不等價**：

- `isSequentiallyTypedRawKeyOrder` 答的是「這串字**是否為**一個打得出來的讀音」——其條件五**明定放行**「同鍵之重寫」與「**同值之重寫**」（後者不留下可觀測之變化，且為動態排列所必需）。
- 混打所要問的是「這是否為**這一整段**讀音（nothing else）」。而在混打語境下，**冗餘鍵恰恰是「ASCII 前綴 ＋ 注音後綴」之分界證據**：使用者鍵入 `aii6`（`ai` ＋ `i6`）而非 `ai6`，正是為了劃出該邊界；若放行同值重寫，切分即消失。

故 Phase 234 之實際處置為**分工**而非替換：**靜態排列維持「鍵數 == 佔用槽數」**（該式即「無冗餘鍵」，比引擎層判準略嚴），**動態排列**方委由 `isSequentiallyTypedRawKeyOrder`。
本報告 §3.2／§8 所未見者，正是「同鍵／同值重寫」這一格對混打語境的正面價值。

### 成立者

- **§3.2（條件五之長度代理量在動態排列下是壞的）**：完全成立。實測大千26 `qquu` ＋ Space 術前遞交 `qquu `、術後正確成字「八」；`qquud`／`uuu`／`mm` 同理。兩處區域豁免（`maxSingleSyllableKeyCount` 之放寬、兩道 `parser != .ofDachen26`）已全數移除。
- **§4.1（平手問題解不了）**：成立且未動。`rm` ＋ Space 仍得「居」；`tod`／`film`／`hell` 等仍靠原有之計數式證據。
- **§8 之「條件三 ↔ `enforceCSVTOrdering`」一項**：本 phase **未動** `buildAutoSplitCandidate`。該處原有之 CSVT 檢定語意上與條件三同向，改採 P233 將**額外**禁掉跨鍵覆寫之尾段（`dcl` 之類），且屬 §5.1 所指之熱點——依最小變更原則保留現狀。
- **§8 之「`isLeadingToneBlocked` 併入條件三／四」一項**：本 phase **未採**。該檢查另涵蓋「聲調前置**後又被更正**」（如 `3su4`）之情形；此為混打之**政策**（`MixedAlphanumericalTypewriter` 明載「Mixed mode 永遠不接受聲調前置鍵入」）而非單純之結構檢定，不可逕以條件三取代。§5.3 之 `suffixOnly` 選擇問題因未涉該處而暫未兌現。

### 未涉者：§5.1 之複製成本

本報告 §5.1 將「為 Tekkon 補 `inout` 重用變體」列為接線之前置工作。Phase 234 **未動** `bestAutoSplitCandidate`（§5.1 所指之唯一熱點），故未需該變體；實際新增之引擎層呼叫皆為**每次按鍵 O(1) 次**。
**實測**：`IH400`（Izanami 全注音表語料）於 release 組態之八案例耗時——術前 49.0 秒、術後三次重跑 48.0～51.4 秒（**區間重疊**）⇒ 無可測之效能影響。
若日後真要接線 `buildAutoSplitCandidate`（其逐後綴迴圈至多 4～6 輪、每次按鍵可達 4～5 回），§5.1 之 `inout` 變體仍應視為前置工作。

### 本報告未預見者：P233 作為「亂序」之英文證據

本報告將 P233 之價值主要定位在「**必要條件過濾**」（§2.1／§3），未料到其對「**亂序鍵入**」之判定本身即可直接充作**英文意圖之證據**：`ls`／`ln`／`lc`／`mv` 這類在槽序上不可能這樣打出來的短 token，於 Space 確認時應留在 ASCII 路徑（此前 `ls` 被收為單一音節而輸出「峱」）。
更關鍵的是：該證據之護欄為「全為 ASCII 英文字母且**長度 ≥ 2**」，因而得以覆蓋原有計數式啟發之 `count >= 3` 護欄所不及的**兩字母 token**——而 shell 使用者最常用的英數 token 恰多為兩字母（`ls`／`ln`／`cd`／`rm`／`mv`／`cp`）。
此為本報告 §3.1「七處各寫一份」之盤點中所未列出的**第八項**用途。

### 對本報告結論之淨影響

- §一「結論速覽」之「最確定的收益在哪」一列應改為：**動態排列之區域豁免**（而非「條件五之長度代理量」，後者僅在動態排列下為真）。
- §六「建議的推進順序」之第一階**部分成立**：換掉代理量之有效範圍僅限動態排列。
- §七「殘餘風險」之第 1 項（複製成本為推論、非量測）**已閉合**：量測結果為無可測影響（原因見上）。
