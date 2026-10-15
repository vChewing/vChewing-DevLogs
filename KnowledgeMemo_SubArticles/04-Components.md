<!-- 本檔為 vChewing-DevLogs/KnowledgeMemo4LLM.md 之分卷；索引：../KnowledgeMemo4LLM.md
     開工前請先讀索引，再依〈三、任務→必讀分卷〉取用本檔。 -->

# 四、核心組件詳解

### 4.1 Tekkon — 注拼引擎

負責注音符號與拼音的解析、輸入法鍵盤映射。

- **`Tekkon.Composer`**：音節合成器，接收按鍵輸入並組合出完整的注音音節。
- **`Tekkon.MandarinParser`**：支援 11 種注音排列（大千、ETen、許氏、IBM、星光等）與 6 種拼音風格（漢語拼音、耶魯、韋氏等）。
- **`Tekkon.PinyinTrie`**：簡化版拼音辨析 Trie，用於狂拼輸入的 `chop()` 拆解。
- **轉換 API**：`cnvPhonaToHanyuPinyin`、`cnvHanyuPinyinToPhona` 等注音⇄拼音雙向轉換。
- **`Tekkon.Composer.isSequentiallyTypedRawKeyOrder(_:suffixOnly:)`（讀音序列檢證；2026-09-19 新增、同日依事主三項裁定改版）**：檢證任一 `some StringProtocol`「是否是按照正確順序打出來了一個 plausible 的注音／拼音讀音」——以當前注音排列逐字元重播進**一份影子注拼槽**（`shadow`；不動自身、亦不倚賴呼叫端之 `enforceCSVTOrdering`），並觀察 聲／介／韻／調 四槽之填值歷程。**五條件**：①每字元皆為該排列之合法按鍵、且於重播時被引擎接受；②重播結束後 `isPronounceable`；③最終仍填著之各槽，其「**最終值首度出現之鍵序**」須隨 聲→介→韻→調 單調不減；④重播期間若曾鍵入聲調，最終不得失落該聲調；⑤**於靜態注音排列、且非 `suffixOnly` 時，不得以另一鍵改寫既有之槽值**（即不接受「按錯再按對」之覆寫修正）。**條件五之適用範圍經實測界定為「靜態注音排列」**（一鍵一注音者）：動態注音排列之合法編碼本即由引擎跨鍵改寫槽值（倚天26 之 `ge`＝ㄐㄧ：鍵 `g` 先寫ㄓ、鍵 `e` 再觸發糾正為ㄐ），拼音排列之組音區亦本就逐鍵清除重建——該二類情形下「以另一鍵覆寫修正」無以定義，故條件五對動態排列與拼音排列皆不生效（實測所得、非權宜）。**`suffixOnly: Bool = false` 參數（事主裁定三）**：以**另一鍵**改寫既有槽值之「覆寫修正」（大千 `dcl`，原案本判合格）**改判為預設不合格**，並以本參數放寬之——傳 `true` 時放寬條件五，供「只檢定尾段（後綴）」之呼叫端使用：`dcl`／`qn`／`cl34` 於預設模式判**假**、`suffixOnly: true` 判**真**。**「同鍵之重寫」（大千26 之 `qquu`：首擊 `q`→ㄆ、次擊 `q`→ㄅ）與「同值之重寫」（`ll`）皆不在禁制之列**：前者係動態排列自身編碼所必需，後者不留下可觀測之變化。**條件三為何只看「最終值之首度出現鍵序」**：動態注音排列之合法編碼本即要求同一槽先後寫入不同值，「逐寫皆單調」之嚴版會誤殺此類合法輸入（同鍵之重寫亦然）。**行為例（皆已實測）**：大千 `cl`⇒真、`ll`⇒真、`lc`／`us`／`3u`／`44`⇒兩種模式皆假；大千26 `qquu`／`uuu`／`mm`⇒兩種模式皆真；倚天26 `ge`⇒兩種模式皆真；拼音 `su3`／`suan`⇒真、`3su`／`sh`／`S`⇒假。**以測試素材全表逐筆檢證（零誤殺；於 `suffixOnly: true` 模式檢證）**：Dachen26 1469／ETen26 1466／Hsu 1466／Starlight 1468／AlvinLiu 1468（計 7337 筆）——動態排列之合法編碼含引擎自身之跨鍵糾正，故全表之斷言於放寬條件五之模式下進行。**與 Lexicon 之權責界線（重要）**：本 API 僅做**引擎層之結構檢定**（「打得出來的合理讀音」）；該讀音是否真實存在於辭典，屬 **Lexicon（TrieKit／`LXAssembly` 一族）之權責**、不在檢定範圍。權威判準為引擎層 `isPronounceable`（故大千 `vi`＝ㄒㄛ 判合格；此為事主裁定二之結果、維持不變），**非**靜態讀音表 `allPossibleReadings`。**何以未採「Unicode 排序訣竅」**：Unicode 之介母 ㄧ／ㄨ／ㄩ 為 U+3127–3129、排在全部韻母（U+311A–U+3126）之後，按該訣竅會把「ㄨㄚ」「ㄧㄠ」這種正常之介＋韻序列判為倒序；本 API 改以引擎槽序為權威。**同構版本**：C++ `isSequentiallyTypedRawKeyOrder(const std::string& input, bool suffixOnly = false)`（`TekkonWorkspace/TekkonCC`）、C# `IsSequentiallyTypedRawKeyOrder(string input, bool suffixOnly = false)`（`TekkonWorkspace/TekkonNT`）；三語言各新增 6 支測項。**API 名稱（事主裁定一）**：原案 `isSequentiallyTypedReasonableReading` 經裁定更名為 `isSequentiallyTypedRawKeyOrder`；原提議之 `isSequentiallyTypedKeyCluster` 未採。**現狀**：已有呼叫端——Phase 234 已將本 API 接為 MixedAlnum 之讀音判定權威（動態排列之「整段是否為單一讀音」＋ 純英文字母緩衝之亂序證據），詳見 §五「MixedAlphanumericalTypewriter 之讀音判定權威」一則。

### 4.2 TrieKit — 辭典樹

支援對讀音的多音字首字元檢索配對，分兩種實現：

- **`VanguardTrie.Trie`**（記憶體型）：全 RAM 常駐、無 QueryBuffer。序列化入口僅 **Vanguard Pragma TextMap 格式**一途（見下方說明）；不支援 Plist 序列化。
- **`VanguardTrie.TextMapTrie`**（TextMap 專用型）：Phase 35 定案後，已不再只是「惰性解析版 Trie」，而是 canonical specialized backend。其核心結構為 raw `Data` 常駐、排序後 full-key index、binary search exact lookup、lexicographic prefix-range scan、eager reverse lookup table、bounded parsed-entry cache，以及 partial-match 用的 `keyInitialsIDMap` prefilter。這讓它既維持低穩態記憶體占用，又能在 exact / longer-segment / revlookup 熱路徑上避免舊有通用 node materialization 成本。（Phase 11 曾嘗試 DFD 模式以 `pread()` 取代常駐 Data，但實機測試記憶體反飆升 20~30 MB 而作廢；詳見 Reqs4LLM/Archive_P001-P100/Reqs_0011-0020.md。）Phase 38 起，Typing TextMap 的 `KEY_LINE_MAP` canonical key 已改為 raw phonabet；TextMap caller layer 不得再對該 backend 做額外 encrypt/decrypt。
- **`VanguardTrieProtocol`**：統一查詢介面。核心 surface 為 `getNode(...)`、`getNodes(...)`、`getEntryGroups(...)`；高階 query API（`hasGrams` / `queryGrams` / `queryAssociatedPhrasesAsGrams`）已改以 entry groups 為主要抽象，使 `any VanguardTrieProtocol` existential 仍能命中 TextMapTrie specialized backend。
- **特殊功能**：部分比對（不完全讀音）、多音切割（分隔器 `&` 用於拼音→TrieKit 的多候選搜尋）。
- **三倉全等（Phase 200 收尾；Phase 213 後路徑更新）**：TrieKit 現於 `vChewing-LibVanguard`（`Sources/TrieKit/`）、`vChewing-macOS`（`Packages/vChewing_OSNeutral_LibVanguard/Sources/TrieKit/`）、`vChewing-OSX-legacy`（`Shared/vChewingComponents/LXAssembly/TrieKit/`）逐位元組一致，LibVanguard 的 `TrieKitTests/` 亦與 macOS 相同。兩處**不可清除**的工具鏈限制必須保留：① `TrieProtocol.swift` 的排序比較是手寫 unrolled 條件分支而**非** 5 元 tuple 的 `>`——後者在 legacy 的 Xcode-15／Swift-5 下 type-check 超時（語義已逐元核對等價，含 `seq` 交叉比較怪癖）；② `TK_QueryBuffer.swift` 的 `import SwiftExtension` 包在 `#if canImport(SwiftExtension)` 內，因 legacy 無該模組（其 `NSMutex` 與本檔同模組）。**另：TrieKit 的 5 元 tuple 已改為具名 struct `VanguardTrie.TrieGram`**（欄位名 `keyArray` / `value` / `probability` / `previous` / `anterior` 與原 tuple 標籤逐一相同，故成員存取點無需改動）；`TrieIO.parseValueLine` 改回傳 `[Trie.Entry]`（該 tuple 形狀與 `Entry` 逐欄相同，不需新型別）；`queryGrams` / `queryAssociatedPhrasesAsGrams` 回傳 `[VanguardTrie.TrieGram]`；LexiconKit 以 `public typealias HomaGram = VanguardTrie.TrieGram` 引用。`queryAssociatedPhrasesAsGrams` 內部那個帶 `seq` 的 6 元 tuple 與手寫 comparator 維持原樣。

#### TextMap 格式概要

`VanguardTrieIO` 提供 `parseTextMap` / `serializeToTextMap` / `loadFromTextMap` / `loadFromTextMapLazy`。`parseValueLine` 為共用的 VALUES 行解析方法，供全物化與惰性兩條路徑共用；RevLookup 由 MainTextMap 自動生成，不再讀取 external `.revlookup`。

TextMap 現行為單一 `.txtMap`（三段式 PRAGMA：HEADER / VALUES / KEY_LINE_MAP）。RevLookup 不再有獨立 sidecar，而是由 runtime 依 MainTextMap 自動構建。VALUES 行有三種型別：

- **型別 A 合併行** `>typeID\tencodedCell`：具有 DEFAULT_PROB 的 typeID 條目按讀音合併為單行，grouped cell 使用 escaped pipe 編碼。
- **型別 B CHS/CHT 機率分組行** `@probability\tchsCell\tchtCell`：僅限 `TYPE=TYPING`。`@` 前綴用來消除與一般三欄個體行的歧義，grouped cell 同樣使用 escaped pipe 編碼，BEL (`\u{7}`) 佔位空側。
- **型別 C 個體行** `value\tprobability\ttypeID[\tprevious]`：不具備 DEFAULT_PROB 或需要 Bigram `previous` 的條目。

完整格式規格引用：`vChewing-DevLogs/Reqs4LLM/Archive_P001-P100/Reqs_0000-0010.md` Phase 02 格式規格段落。

### 4.3 Homa — 護摩組字引擎

Megrez 的繼任者，實現漢字組句動態規劃演算法。

- **Bigram 支援**：Gram 承載真實讀音；Bigram 描述僅以前驗字詞為準（不糾結前驗讀音）。
- **節點覆寫**：`OverrideType.withTopGramScore`（頂分覆寫）與 `.withSpecified`（明確指定）。
- **候選字輪替與鞏固**：內建 `Homa_CandidateAPIs_Revolver`（輪替）與 `Homa_ConsolidatorAPIs`（上下文鞏固）。
- **路徑搜尋**：`PathFinder` 以動態規劃 + Unigram/Bigram 結合評分產生最佳組句。
- 取消了舊版 `LangModelProtocol` 協定，改用回調函式 `gramQuerier`。`gramAvailabilityChecker` 已於 Phase 44 移除（`insertKeys()` 直接使用 `queryGrams()` 檢查可用性，無需獨立回調）。
- **Phase 05 熱路徑最佳化**：`Assembler` 具備跨連續 `insertKey()` 的 bounded gram query cache；`queryGrams(using:cache:)` 以結構化 comparator / hash 去除原本字串插值排序與去重成本。

### 4.4 LexiconAssembly — 辭典聚合與洞察中樞（macOS／LibVanguard 兩倉同源）

整合多種辭典來源，向上層提供統一查詢介面。**本節原名 `LexiconKit`，其對位物自 Phase 213 起於 `vChewing-LibVanguard` 亦已更名為 `LexiconAssembly`（原 `Sources/_Modules/LexiconKit/` 整目錄退場）。`vChewing-macOS` 側早於 Phase 202 更名、Phase 210 併入 `Packages/vChewing_OSNeutral_LibVanguard`。**

- **`LXAssembly.LXFacade`**：辭典查詢門面（Phase 201~204 由 `LMInstantiator`／`LMI` 更名而來）。原 LibVanguard 的 `VanguardTrie.TrieHub`（Trie 資料庫中樞，唯一資料來源為 Vanguard Pragma TextMap 的 `updateTrieFromTextMapFile`）**已於 Phase 213 隨舊佈局退場**，其角色由 `LXFacade` ＋下述來源抽象承接。唯一公開查詢面為 `LXAssembly.LXQuerier`（Phase 201~204 之 API 壓縮）。
- **`LXAssembly.LXPerceptor`**：使用者習慣洞察器（POM），基於 Ngram 的行為追蹤、時間衰減三次曲線。原 LibVanguard 側名為 `Perceptor`。其持久化層 `LXAssembly.PerceptionPersistor` 的鎖恆為**葉鎖**——取鎖期間不得呼叫任何回呼，因為 `LXPerceptor` 會在持自有鎖時呼叫該層的 `markKeyForUpsert(_:)`／`markKeyForRemoval(_:)`，兩者互相嵌套即成取鎖順序倒置的死鎖（2026-09-17 修正，回歸斷言見 `Tests/LexiconAssemblyTests/POMLockDisciplineTests.swift`）。其檢索自 2026-10-14（P305）走三組 head 索引（`headReadingIndex`／`toneStrippedHeadReadingIndex`／`headReadingSegmentIndex`，桶為 `[String]`、最近使用者在前）＋ `parsedKeyCache`，故 `perceptionsFor`／`getToneInsensitiveSuggestion`／`alternateKeys` 之成本與記憶總量脫鉤；索引係**超集**，判準仍在各查詢自身。**不變量**：`mutLRUMap.count <= mutCapacity` 且與 `mutLRUKeySeqList` 同構——由 `enforceCapacity()` 於「快照載入／日誌重播／逐筆記憶」三處維持（此前日誌重播只寫映射、不寫序列，故容量上限形同虛設、記憶逐啟動膨脹）。其日誌重播自 2026-10-14（P306）改以**有序變化流** `[PerceptionPersistor.JournalChange]`（`.clear`／`.upsert(pair)`／`.remove(key:)`）交付呼叫端，`replayApplicator` 之簽名為 `([JournalChange]) -> ()`（原 `inout [String: KeyPerceptionPair]` ＋ `inout Bool mutated` 已廢）；移除與清空故得表達。
- **`LXAssembly.LXPlainBopomofo`**：倚天中文 DOS 注音表（Phase 201~204 由 `Lexicon.LMPlainBPMF` 更名）。
- **`LXAssembly.LexiconGramSupplierProtocol`**：統一所有辭典來源的元圖供應協定。
- **`LXAssembly.LXGramSupplyHub`／`LXFactoryGramSupplier`**：多來源中樞與「把原廠辭典包成可掛載來源」的轉接器（Phase 212 落地，兩倉同源）。另有合流 API（`LXAssembly.GramConcatFlags`／`concatGramQueryResults`／`concatGramAvailabilityCheckResults`／`makeGramIdentityHash`）。宿主或測試可經 `LXFacade.mountGramSupplier(_:)`（或 `lxQuerier` 的同名方法）掛載任意來源，其元圖會併入 `unigramsFor` 的一般查詢結果、並被 `hasUnigramsForFast` 承認。**兩倉於此完全同源**（`vChewing-macOS` 為正本、`vChewing-OSX-legacy` 為減去模組 import 與 `nonisolated` 的同構副本；legacy 不承擔單元測試）；LibVanguard 自 Phase 213 起為 macOS 的逐位元組複製，故 Phase 212 所記之「四項刻意差異（命名空間／元圖型別／`makeGramIdentityHash` 之可見性／`Homa.Gram.init(_ trieGram:)` 橋接）」**已不再存在**。
- 不負責去重複化（交由 Homa 引擎處理）。

### 4.5 BrailleSputnik — 盲文點字

- 支援 1947 與 2018 兩種盲文標準。
- 核心 API：`convertToBraille(smashedPairs:, extraInsertion:) -> String`。
- 內含聲介韻調完整映射表與標點符號映射。

### 4.6 SwiftExtension — Swift 語言擴展（出貨產品名 `VanguardSwiftExtension`）

- Bool / Double / String / Array / Set 等型別的便利運算符與擴展。
- `LatinKeyboardMappings`：拉丁字母鍵盤映射表。
- `SwiftFoundationImpl`：Foundation 相容實現（跨平台）。
- **打包形態（2026-09-14）**：已自聚合體析出為獨立套件，置於**聚合體目錄之內**（macOS `Packages/vChewing_OSNeutral_LibVanguard/Deps/VanguardSwiftExtension/`、LibVanguard `Deps/VanguardSwiftExtension/`——如此 `.package(path:)` 兩倉同字串、聚合體 manifest 得以逐位元組相同），由該套件出貨 dynamic product `VanguardSwiftExtension`（Darwin 為 dynamic、其餘平台為 static）——**模組名仍為 `SwiftExtension`，故全倉一律 `import SwiftExtension`**（SwiftPM 不要求產品名與模組名相同）。聚合體之 `libVanguard.dylib` 對它是**動態相倚**而非靜態內嵌，故每個行程內本模組恰一份 image；App-based installer 亦僅同捆這一顆（383 KB）。授權為 MulanPSL-2.0（見該套件 `LICENSE`）。
