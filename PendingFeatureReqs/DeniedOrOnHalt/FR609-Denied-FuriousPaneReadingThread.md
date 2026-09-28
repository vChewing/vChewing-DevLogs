# FR609（FeatureRequest）：狂打模式之讀音線顯示於 copilot 窗頂部 pane —— 已否決（暫緩）與其調查記錄

> **文檔狀態**：**已否決（暫緩；現階段不施工）**。事主裁定（2026-09-29）：**報酬率太低**。
> **複審條件**：今後若有**足夠數量之使用者**提出**同質** complaint／FR，屆時再檢討是否實作。
> **本文件之性質**：非實作藍圖。此處留存者係該 FR 之討論結論與技術發現，供未來複審者免於重做研究；§七 之施工範圍僅為「若複審通過」之起點建議。
> **編號沿例**：FR 之編號對應 PullReq 編號（`FR608-PreResearch-v1a.md` 即由 `PullReq608` 逆推）；FR609 之編號由事主指定。
> **檔案命名**：`<FR 編號>-<處置>-<主旨>.md`。FR608 系列之檔名帶的是「文檔種類」（`PreResearch-v1a` 等），本檔帶的是「處置」＋「主旨」——目錄已表處置、而檔名多帶主旨便於人眼掃目錄。

---

## 一、FR 原文與其後續修正

**原文（事主轉述）**：

> 「狂打模式下的 reading 顯示得顯示成整個 Furious Buffer 內容的「被拆分後」的形態、且處於離游標最近的那個 unfinished segment 以外的 Segments 用下劃線標注。」

**討論中之修正（事主逐項裁定）**：

1. **落點**：不用內文組字區，用 **copilot 窗頂部 pane**。
2. **標記方式**：不用下劃線，改用**分隔符**（事主提案「`→`」）。
3. 併問：此 FR 是否亦適用於**拼音狂打**（助手答：不宜，見 §六）。

---

## 二、現行可見性盤點（FR 之觀察成立）

| 表面 | 狂打時顯示什麼 | 來源 |
|---|---|---|
| 內文組字區 | copilot 組句之**中文**（主段）＋前方預覽（**亦為中文**） | `InputHandler_HandleStates.swift:547-548`、`:564` |
| copilot 窗頂部 pane | **只有**未固化素材（`✍️ `＋當前字母流／音節） | `InputSession_Delegates.swift:207` ⇐ `InputHandler_FuriousResegmentation.swift:100-114` |
| Tooltip | 僅候選窗為空時顯示 `composer.romajiBuffer` | `InputHandler_HandleStates.swift:657-661` |

⇒ 「已自動切分／已入組字器之讀音，於狂打時無處以讀音形態示人」為真 ⇒ **FR 指出的缺口確實存在**。

---

## 三、為何落點只能是 copilot 窗頂部 pane（內文組字區之三條硬傷）

1. **mark 狀態直接複製 `displayTextSegments`**（`InputHandler_HandleStates.swift:930-936`、`:960-966`），而 `userPhraseKVPair.value` 取 `rawDisplayedText[markedRange]`（`IMEStateProtocolAndData.swift:385-389`）⇒ 分隔符會落進詞值（就地加詞／詞語選字）。
2. **marking 之 cursor／marker 由組字器節長推得**（同檔之 `convertCursorForDisplay`）⇒ 顯示多出字元即游標漂移。
3. **狂打之遞交走 `assembledMainValues + preview`**（`:731-734`）⇒ 分隔符不會隨遞交出去；若把主段由中文改為讀音，則或遞交讀音、或所見≠所遞交——後者正是 P262–P266 一系所修掉的那類 bug。

pane 全無此顧慮：資料源係 `String?`（`CtlCandidateProtocol.swift:38`）、由 `CandidatePool4AppKit` 自繪（`:1495`），不經 IMK、不進 `displayedText`、不涉遞交與游標算術。**唯一代價係窗寬**：`totalAccuSize.width = max(totalAccuSize.width, pane 寬 + originDelta * 2)`（`:1182`）；pane 之字級為 `max(ceil(unifiedSize * 0.7), 11)`（`:1499`）。

---

## 四、下劃線語法（原案）棄用之理由

- **IMK 綁死該維度**：組字區要顯示游標則**所有下劃線之粗細必須相等**，且 `.ofInputting` 之 selectionRange 長度必須為 0；`InputSession_HandleStates.swift:67-77` 之 mitigation 整段即為粗細一致而設（QQNT 等客體連 `.thick` 都吃不下）。
- **macOS 14 起**，同粗細之相鄰下劃線會**合成一線段** ⇒ 想以下劃線畫出之邊界，正是系統會抹掉者。
- **一頻道二義**：「下劃線＝未遞交」係該頻道既有且最強之語義，再借它表示「已拆分」即衝突。
- **分段資訊其實已在**：`IMEStateParsed.AttrStrULStyle.pack` 早已逐段累加 `NSMarkedClauseSegment`（`:44-53`）；IME 側唯一能動的只有下劃線那一維——而那一維正是平台綁死的。

---

## 五、分隔符之比較（供複審者）

| 方案 | 邊界可見度 | 每邊界之寬 | 語義負擔 | 字面風險 |
|---|---|---|---|---|
| NBSP `\u{A0}` | 低 | 窄（隨字面） | 無（既有慣例：`IMEStateParsed.swift:292` 之讀音串） | 無 |
| **EM SPACE `\u{2003}`（助手建議）** | 中高 | 與字級同寬 | 無 | 極低（空白類，無字形） |
| `→`（事主提案） | 高 | 常為全形（EAW=Ambiguous） | 有：本 app 之使用者可見文案中，`→` 主要作**方向鍵**字形（設定說明之「←/→」）；`i18n:Common.ReplaceTo` 之箭頭**僅 ja 值有**（`単語 →`；zh-Hant 為「置換 為」、zh-Hans 為「置换 为」），故不構成本語系之先例 | 需回退面孔：`phraseFontEmphasized` 未必有 U+2192，而 pane 之規格係「與 page indicator 同款」（P184） |

助手之預設選擇為 `\u{2003}`。**寬度一欄係推定**（pane 之字面與字級皆影響實際寬度，須實機量測）；此事項於裁定「不施工」時**尚未定案**——單一常數，複審時再定即可。

---

## 六、拼音側為何不宜（若複審，此為範圍界線）

1. **該物不存在**：拼音原文只活在 `furiousTrail`（`InputHandler_FuriousTypingConfig.swift:40-41`），而 trail 係**窗非史**——任何顯式干涉與不完整前綴／α 固化皆令其失效，**19 處呼叫端**（選字、就地選字、輪替、聲調覆寫、游標移動、溢出遞交；另 3 處自癒：`InputHandler_FuriousResegmentation.swift:571`／`:584`／`:589`）。失效後組字器只剩**注音鍵**，原文不可復原 ⇒ 欲顯示「整個 buffer 之拆分」須先新增一份跨固化存續之敲鍵史（狀態層工程）。
2. **該「拆分」會被否定**：`enumerateFuriousResegmentationCandidates()` 以 `furiousTrail.joined()` 重新枚舉**同音節數**之切分（`:594-608`），再 drop 舊鍵、插新鍵（`:627-637`；入口 `resegmentFuriousTrailIfNeeded`，於每次 auto-chop 之後執行：`Typewriter_BPMFFullMatch.swift:297`）⇒ `fang|an` 會被改寫為 `fan|gan`（兩者互不為前綴）。`buildFuriousCoSegmentedOffers()` 更把 trail 與注拼槽**併成單一字母流**重切（`:665-666`）⇒ 連「上一段／尾段」之邊界本身亦在談判中。
3. **會污染唯一可信之核對管道**：pane 之職責係 P184 移交過來之「敲鍵可見性接棒」——今日顯示未拆分原文（忠實），正是拿來核對「我敲了什麼」者；改顯示切分＝在照妖鏡上畫引擎之猜測，且 trail 失效時 pane 會在使用者眼前**由拆分視圖忽然退回原文**。
4. **報酬率**：拼音側之收益係「看到一個會被改寫的切分」，成本係新增狀態＋其生命週期紀律（標準級以上）。

**注音側恰好相反（可證之性質差異，非偏好）**：一鍵一音節單位 ⇒ 敲鍵序列**本身即已切分**，`assembler.keys` 即真值；P266 之交棒係**前綴保留**（`:261-264` 斷言 `zip(cellKeys, wordPair.keyArray).allSatisfy { $1.hasPrefix($0) }`）⇒ 顯示只會由「ㄎ」長成「ㄎㄜ」、**不會被否定**（單調）。忠實且單調之讀數方配得上 pane 之職責。

---

## 七、若複審通過：建議之施工範圍（僅供省去重做研究）

- **限定注音側**；拼音側維持現行 `composer.romajiBuffer`。
- 資料＝`assembler.keys`（引擎實有之鍵：單注音格，或 P266 交棒後之完整音節）＋注拼槽之當前讀音；**尾段不加分隔符**（貼於末端，接手原下劃線想提供之辨識功能）。
- 落點：`InputHandlerProtocol` 新增一顯示用 computed property，`Session.unfinishedReading` 一行改為取它（`InputSession_Delegates.swift:207`）；**選字窗側零程式改動**。
- **上界**：尾端至多 4 格（比照 `maxZhuyinAbbreviationCells`），過長時前端截斷；否則窗寬隨輸入長度成長。
- 測項落點：`TDK4AppKitTests.swift:759`（nil ⇒ pane 隱藏）、`:772`（pane ⇒ 候選整體下移、窗寬納入）之鄰居——內容含分隔符、上界與截斷、寬高。
- 不動 `committableDisplayText`、不動 IMK attribute 策略。

---

## 八、裁定

- **2026-09-29（事主）**：**先不施工**；理由＝**報酬率太低**。
- **複審條件**：今後若有**足夠數量之使用者**提出**同質** complaint／FR，屆時再檢討是否實作。
- 本文件係該裁定之唯一記錄；裁定時**未動任何程式碼**（`vChewing-LibVanguard` 與 `vChewing-macOS` 皆零改動）。
