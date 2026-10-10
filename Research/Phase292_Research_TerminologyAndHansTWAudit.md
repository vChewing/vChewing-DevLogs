# Phase 292 研究實錄：「空格」術語更動（空白鍵／空白字元）與 zh-Hans-TW 體例稽核

> 本檔為 Phase 292 之長篇推導、逐處清單與量測，依備忘錄 §12.7.2 自 Reqs 卷抽出（`Research/` 不計入 Phase 篇預算）。
> 卷內之 Phase 篇僅留取捨、證據與界線，並指向本檔。
>
> 狀態：完工（2026-10-09／2026-10-10）｜各倉最終形＝`vChewing-macOS` `373ccd81`＋`540fc1b3`／`vChewing-LibVanguard` `6b0188b`／`vChewing-HomePage.io` `1b5816f`（事主重製，母 `040b280`）／`Tekkon` `ef40f0d`／`TekkonCC` `a80b8e4`／`TekkonNT` `8187ae4`／本卷 `Reqs_0291-0300.md`（母 `5fbf45e`）。

## 1. 緣起（事主逐字，依時序）

1. 主交辦：「**你先閱讀 devlogs 的 knowledgememo，然後開 Phase 292 處理這個任務：術語更動：將所有「keyboard key」意義的「空格鍵」改稱「空白鍵」、將所有「text char」意義的「空格」改稱「空白字元」。處理範圍：整個 vChewing-macOS 倉庫與 LibVanguard 倉庫、還有 homepage 倉庫。要處理的語言範圍：both zh-Hant and zh-Hans (zh-Hans 使用簡化字)。P.S.: `/Users/shikisuen/Repos/_vChewing/_DedicatedComponentRepos/TekkonWorkspace/Tekkon` 的 `05359eb` 可作為參考。**」
2. 「**Tekkon 倉有錯誤的話也請修了。而且那邊 Tekkon 是三個倉庫（Swift & C# & C++）。LibVanguard 是正本。**」
3. 「**「BackSpace 後按空白字元」應該是「BackSpace 後按空白鍵」才對吧。**」與「**有發現這類錯誤的話，哪怕是 tekkon workspace 的既有錯誤，也請修正。**」
4. 「**P292 所有內容均使用 monocommit。我已經處理了一部分倉庫了，你處理剩下的倉庫（devlogs 等）**」
5. 「**追加任务（用新的commit）：检查 vChewing-macOS 仓库的简体中文化是否仍有其他有违 `zh-Hans-TW` 体例的地方，比如「半角」等。**」
6. 收束：「**DevLogs 修一下，这也是 P292。**」與「**（Homepage 那边 assistant 的修改被我撤了。回头等 v4.8.8 发版了再更新。**」

## 2. 判準之演進

- **初版**（逐字沿用參考稿 Tekkon 倉 `05359eb`（`Terms // Fix the zh-Hant calling of "SPACE" char / key.`，6 檔 ＋19／−19））：指「按鍵」者→`空白鍵`；指「字元／字元寬度／分隔用之空白」者→`空白字元`。該稿把「空格鍵」與鍵義之「空格」**一併**改為「空白鍵」。其 14 處落點（供比對）：`Tekkon_SyllableComposer.swift:444`、`TekkonTests_Pinyin.swift:377,397`（鍵義）；`README.md:128`、`Tekkon_SyllableComposer.swift:95,96`、`Tekkon_Utilities.swift:48`、`TekkonTests_Basic.swift:102`、`TekkonTests_Pinyin.swift:32,81,201,250,298,348,378`、`TekkonTests_PhonabetAutoChopPredicate.swift:78,137,195,260`（字元義）。
- **補完（提交後複核所發現）**：參考稿只涵蓋「bare『空格』恰為字元義」之諸例，未暴露動作義之分歧。今補為：**bare「空格」之動作義（按／敲／摁／雙擊／用…確認／固化）者→「空白鍵」**。觸發點＝抽查官網 `manual/preferences.md` 之 diff，見新增行 `| 行為設定 | switch.2 | 按鍵行為（空白字元、Tab、Shift、Caps Lock 等）…`——該處與 Tab／Shift／Caps Lock 並列為按鍵名，屬鍵義，卻被首輪機械讀法判為字元義。
- **再修（事主指示後）**：句中該詞若為**施動者或動作之對象**（按、敲、雙擊、寫入…者、讀音完成）→`空白鍵`；若為**被寫入／被分隔／被插入之值**，或**寬度、佔位**（陰平佔位）→`空白字元`。此判準與倉內先於本案之原文相符：`zh-Hant.lproj/Localizable.strings:465`「於按下空白鍵時以 `qquu ` 遞交」、`:467`「空白鍵則用於確認該讀音」、`Typewriter_MixedAlphanumerical.swift:35`「空白鍵之語意為『固化該讀音』」。
- **字元義之守恆清單**：分隔符（bigram、權重）、插入之字元、字元寬度、ASCII／NBSP、行首行尾剝除、縮排、陰平佔位、`ReleaseNotes.md:554` 之 Discord 例。

## 3. 初版作業法與盤點

- 盤點：`tmp/p292_survey.py`（Python `os.walk`，跳 `.git`／`.build`／`build`／`Build`／`node_modules`／`.tmp`／`DerivedData`／`.swiftpm` 與二進位副檔名）掃三倉，輸出每條含「空格」之 `(倉, 相對路徑, 行號, 整行)`；三倉共 **702 行**。
  - `vChewing-LibVanguard` 27 檔（`InputHandler_TriageInput.swift` 28、`InputHandlerTests_FuriousZhuyin.swift` 44、`InputHandlerTests_FuriousPinyin.swift` 25…）。
  - `vChewing-macOS`：`zh-Hant.lproj/Localizable.strings` 21、`zh-Hans.lproj/Localizable.strings` 22、`shortcuts.html` 5＋5、`shortcuts-src/` 5＋5＋1、`template-*.txt` 各 2、`PhonaSet.swift` 6、助手 `src/i18n.ts` 2 與 `assets/userdef-metadata.json` 33、`Makefile` 1（縮排義）。
  - `vChewing-HomePage.io` 23 檔 253 次（`ReleaseNotes.md` 45、`manual/arranges.md` 11、`manual/preferences.md` 11、`onboarding/onboarding_pinyinsimp.md` 11…）。
- 分類器 `tmp/p292_classify.py`（規則式：右鄰`鍵`⇒KEY、右鄰`字元`⇒CHAR、±24 字窗之證據詞）**已棄用**：全體統計 `REVIEW 385／CHAR 218／KEY 611／OOS 2`，385 處落「需人工」，且同句共現會誤判（例：`（一個半形空格）、Tab` 因同句有「按」而被判成鍵義）⇒ 改為「逐處人工裁定 ＋ 整檔同構替換」。
- **複核絞網＝雙向反查**：以「字元義前綴 ＋ `空白鍵`」與「`空白字元` ＋ 鍵義詞」各掃一遍，本案共抓出 18 檔（＝9 檔 ×2 倉）誤判並修正。**教訓：`／` 是弱證據**——`ASCII 空格／Tab／NBSP／全形空格` 是並列之**字元**清單，而 `聲調鍵／空格鍵` 是並列之**鍵**清單，兩者形同而義異。

## 4. 追加修正（判準補完後之清單，除末項外皆 `空白字元`→`空白鍵`）

- `vChewing-LibVanguard`：`Sources/LibVanguard/InputHandler/InputHandler_FuriousResegmentation.swift:815`（auto-chop／空白鍵固化插入）、`Sources/LibVanguard/Session/InputSession_HandleEvent.swift:129`（系統之雙擊空白鍵全形句號替換）、`Tests/LibVanguardTests/InputHandlerTests_FuriousZhuyin.swift:39`（未按空白鍵）與 `:1512`（再按空白鍵）。
- `vChewing-macOS`：上列四處之同源閉包副本；`.strings` 無須更動（追加複核確認 619 鍵中已無鍵義誤判；`kFuriousTypingEnabled4Zhuyin.description` 之「空白鍵在此模式下仍是陰平鍵」維持為「空白鍵」）。
- `vChewing-HomePage.io`：`manual/preferences.md` 8 處（「按鍵行為（空白鍵、Tab、Shift、Caps Lock 等）」、「空白鍵確認高亮候選字」×3、SCPC 列之「按空白鍵確認高亮候選字」與「用空白鍵選字」、「對齊個人的空白鍵/翻頁習慣」、「空白鍵在此模式下仍是陰平鍵」）、`ReleaseNotes.md:181,204`、`onboarding/onboarding_pinyinsimp.md:23,58(×2),73`。
- 三倉再提交：`vChewing-macOS` `043670b4`、`vChewing-LibVanguard` `3e57378`、`vChewing-HomePage.io` `f062727`（三倉 9 檔、＋19／−19；其後皆經 monocommit 取代）。

## 5. Tekkon 三倉之複核

- 範圍：`_DedicatedComponentRepos/TekkonWorkspace/` 之 `Tekkon`（Swift，`05359eb`）／`TekkonCC`（C++，`6035a73`）／`TekkonNT`（C#，`86df487`）。三倉「空格」計數皆 0；`空白鍵`（鍵義）與`空白字元`（字元義）逐處檢視皆合判準、無誤判；無簡體「键」滲漏。例：`Tekkon_SyllableComposer.swift:95,96,444`、`Tekkon_Utilities.swift:48`；`TekkonCC/Sources/Tekkon/include/Tekkon.hh:1499,1786,1959,1960,2368`（字元義）與 `:2427`（鍵義）；`TekkonNT/Tekkon/Composer.cs:84,85,586`（字元義）與 `:667`（鍵義）。bare「空白」（whitespace）非本案對象。
- **修正一（測試名與敘述不符）**：`TekkonTests_SyllableIndex.swift:69-70` 原作 `@Test("嚴格前綴恰為 15 條，且其全表逐條斷言")`／`func strictPrefixesAreExactlyTheFifteen()`，惟函式體內之註解自陳「上述 16 條」、斷言之嚴格前綴陣列實為 16 條（`ㄅ ㄆ ㄇ ㄈ ㄈㄧ ㄉ ㄊ ㄋ ㄌ ㄍ ㄎ ㄎㄧ ㄏ ㄐ ㄑ ㄒ`），且 C++（`TekkonCCTests_SyllableIndex.mm:150`、`GTests/TekkonTests_SyllableIndex.cc:151`）與 C#（`TekkonTests_SyllableIndex.cs:110`）皆作 Sixteen ⇒ 改為 16／`strictPrefixesAreExactlyTheSixteen()`（案號 `fe3ca75`）。
- **修正二（註解數字陳舊）**：同檔 `:152` 之「空字串：全部 427 條」改為 426——其下一行斷言即 `#expect(index.completions(of: "").count == 426)`，C++／C# 對位皆作 426。來歷：該檔於 `25a5018`「Tekkon // Drop the single-letter entry "q" from mapHanyuPinyin.」一次寫入時即並存 427 與 426（刪去單字母條目「q」後未同步之殘留）。此數字在三處 Swift 副本同錯，故 `vChewing-LibVanguard`（正本，`64e9b0a`）與 `vChewing-macOS` 閉包（`1d2d90e6`）一併更正以維持逐位元組同源。
- **史記更正**：`Tekkon` 倉 `fe3ca75` 其後已非 `main` 之祖先（物件仍在庫中）；`main` 為 `8c275e3`（與 `05359eb` 同訊息，16／426 兩處修正已含於其中，`git log -S'嚴格前綴恰為 16 條'` 即指向之），最終經事主整併為 `ef40f0d`。
- 驗證：`swift test --disable-sandbox`（Tekkon 倉）57 支／9 套、0 失敗；`vChewing-LibVanguard` 同數；`diff -rq --exclude=.DS_Store` 三處 Swift 副本之 `Sources/Tekkon` 與 `Tests/TekkonTests` 全等。

## 6. 術語再修（3 類 11 檔）

1. 「（「BackSpace 後按空白字元」之輪替／重組錯亂由此而來）」→`空白鍵`（3 檔，三處 Swift 副本）：`Tekkon/Tests/TekkonTests/TekkonTests_Pinyin.swift:378`、`vChewing-LibVanguard/Tests/TekkonTests/TekkonTests_Pinyin.swift:378`、`vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard/Tests/TekkonTests/TekkonTests_Pinyin.swift:378`。**此條推翻先前的「刻意未動」**（原為求與參考稿逐位元組一致而保留 `空白字元`）。
2. 「於當前狀態下寫入聲調槽者（聲調鍵／空白字元）由既有管線固化，不屬本案。」→`空白鍵`（6 檔）：`Tekkon/Tests/TekkonTests/TekkonTests_PhonabetAutoChopPredicate.swift:260`、`TekkonCC/Tests/TekkonCCTests/TekkonCCTests_PhonabetAutoChopPredicate.mm:441`、`TekkonCC/GTests/TekkonTests_PhonabetAutoChopPredicate.cc:426`、`TekkonNT/Tekkon.Tests/TekkonTests_PhonabetAutoChopPredicate.cs:226`、`vChewing-LibVanguard/Tests/TekkonTests/TekkonTests_PhonabetAutoChopPredicate.swift:260`、`vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard/Tests/TekkonTests/TekkonTests_PhonabetAutoChopPredicate.swift:260`（句中「者」為施動者，且與「聲調鍵」並列）。
3. 「SCPC 下之逐音節選字不受影響：讀音完成（聲調鍵／空白字元）時仍走」→`空白鍵`（2 檔）：`vChewing-LibVanguard/Sources/LibVanguard/Typewriter/Typewriter_BPMFFullMatch.swift:237` 與 macOS 閉包之同源副本。
- 提交：`Tekkon` `062d262`／`TekkonCC` `b758ec7`／`TekkonNT` `39f2031`／`vChewing-LibVanguard` `c6504cc`／`vChewing-macOS` `54b04c88`（其後皆經 monocommit 取代）。
- **反查方法（供後續同類案件複用）**：`grep -rnE '鍵(／|、|與|或)空白字元'`、`grep -rnE '[（(][^）)]*鍵[^）)]*空白字元'`、`grep -rnE '(按|敲|雙擊|摁)空白字元'`、`grep -rnE '鍵.{0,30}空白字元'`。**注意：CJK 字元寫進 `[...]` 於本機 grep 不生效（回 0 筆），須改用 `-E` 之交替 `(a|b)`。**
- 再確認之未動：`InputHandler_TriageInput.swift:161`「不帶 Shift 的空白鍵恆插入半形空白字元」（鍵與字元並存，兩者皆合判準）；`TekkonTests_PhonabetAutoChopPredicate.swift:78,137,195`（字元義；C++ `…mm:158,222,358`／`…cc:150,214,342` 與 C# `…cs:148,290,342` 對位一致）；`Tekkon.hh:1583,1625`／`Shared.cs:154,175`（泛稱「空白」＝whitespace）。
- 測試：`Tekkon` 57／9；`vChewing-LibVanguard` 682 支／66 套、0 失敗；`TekkonCC` ObjC++ XCTest 60 支 0 失敗、GTests 66／10（`cmake -S . -B Build -G Ninja -DFETCHCONTENT_FULLY_DISCONNECTED=ON`）；`TekkonNT` 未執行（本機無 `dotnet`；其改動為單行註解）。

## 7. 整併（monocommit）

- 事主整併之六倉：`vChewing-macOS` `373ccd81`（45 檔）、`vChewing-LibVanguard` `6b0188b`（28 檔）、`vChewing-HomePage.io` `aa14ec7`（25 檔；其後重製為 `040b280`／squash 為 `1b5816f`）、`Tekkon` `ef40f0d`（7 檔）、`TekkonCC` `a80b8e4`（11 檔）、`TekkonNT` `8187ae4`（7 檔）。抽查確認各 monocommit 皆已含本案全部落點（含三處 Swift 副本之「BackSpace 後按空白鍵」、`Typewriter_BPMFFullMatch.swift:237` 之「讀音完成（聲調鍵／空白鍵）」、`Tekkon` 之 16／426 更正）。
- 本卷：原四筆 P292 commit（`dc979a9`／`32028de`／`e262a3b`／`f772746`）以 `git reset --soft 5fbf45e` 整併為單一 commit，樹內容與整併前逐位元組相同（`git diff` 為空）。其後追加稽核與事主後續處置再整併一次（母 `5fbf45e`）。
- **教訓**：`git reset --soft` 不動索引——重整併前必先 `git add`（曾因此產出漏掉編輯之 `e1de409`，已修正為 `e44acf2`）。
- 效力：卷內各節所記之逐階段 hash 皆已由各倉 monocommit 取代，不再存在於各倉 `main` 之歷史。`vChewing-VanguardLexicon`／`vChewing-Homebrew` 未涉本案，無須整併。

## 8. zh-Hans-TW 體例稽核（追加交辦）

### 8.1 方法

- 以 Swift 之 `CFStringTransform(output, nil, "Hant-Hans" as CFString, false)` ＋ `Scripts/Markdown2HTML/derive-zh-Hans.swift` 之同一組 11 個 `glyphOverrides`（鍵→键、冊→册、熱→热、彙→汇、體→体、網→网、臺→台、灣→湾、倉→仓、蝨→虱、螢→荧）把 **zh-Hant 對位檔轉為簡體**，再與 zh-Hans 實值逐鍵／逐行比對：凡「轉換結果 ≠ 實值」即為偏離。此法同時抓出大陸詞彙、繁體殘留與改寫式意譯；單憑「大陸詞彙表」掃描既會漏（「字號」於 zh-Hant 亦作「字號」）、亦會誤（日文之「半角」「字号」為日語正字）。
- 工具置於 `tmp/`（未入版控）：`hans_diff.swift`（逐鍵）／`hans_diff2.swift`（片段）／`hans_diff3.swift`（±26 字上下文）／`pair_diff.swift`（任意檔對逐行）／`t2s.swift`（整檔轉換，供 Python `difflib` 用）；套用器 `tmp/p292h_fix.py`（以鍵為範圍／以行號為範圍就地替換並逐處 `assert` 命中）。
- 稽核對象＝`git ls-files` 篩出之全部 zh-Hans／`-CHS` 檔：輸入法與安裝程式之 `Localizable.strings`／`InfoPlist.strings`、`shortcuts-src/shortcuts.zh-Hans.md` 與四語系 HTML 產物、`README-CHS.md`、`LICENSE-CHS.txt`、`LegacyZone/**/zh-Hans.lproj/InfoPlist.strings`、`ValueAdd/PKGInstallerAssets/pkgText*`、助手 `src/i18n.ts` 與 `assets/userdef-metadata.json`。RTF 另經 `textutil -convert txt` 轉純文字後比對；助手後設資料另抽 287 組雙語欄位同法比對。
- **注意**：Python 掃描函式定義後必須實際呼叫——曾因漏寫 `walk(d)` 而誤報「詞彙可疑 0 處」（假陰性）。

### 8.2 判準與四類修正

判準：凡 zh-Hans 與「zh-Hant 之字元簡化」不符者**一律對齊 zh-Hant**；僅兩類例外——① 刻意之語境改寫（見 8.4）；② 法定授權文本（見 8.4）。

1. **大陸詞彙改用臺灣用語**：`服务菜单`→`服务选单`；`数据`→`资料`（3 鍵）；`模块`→`模组`；`支持的汉字`→`支援的汉字`（2 處）、`仅限于万国码`→`仅限万国码`；`默认为关闭`→`预设为关闭`（2 處）；`可打印`→`可列印`；`半角`→`半形`；`字符`→`字元`（2 處）；`如需使用`→`若要使用`；`建议直接联系`→`建议直接洽询`；安裝程式之 `该软件`→`该软体`、`请注销`→`请登出`、`再运行一次安装程式`→`再执行一次安装程式`。
2. **繁體殘留改正**：`目前為止`→`目前为止`、`一併`→`一并`、`回歸`→`回归`（助手 3 鍵）；安裝程式 `i18n:Installer.ReadyToUse` 之後半句整串故作繁體（「若是在當前使用者帳戶內首次安裝的話，請重新登入。」）；`README-CHS.md` 首列 `[繁體中文]`→`[繁体中文]` 與 L24 整行（擁有／啓用／就會／承襲／體驗）。
3. **標點體例**：西式引號改臺灣引號——`“Documents”`／`“Desktop”`→`「Documents」`／`「Desktop」`（4 處，含助手）、`pkgTextWarning-CHS.txt` 之 `“手动”`→`「手动」`。
4. **與 zh-Hant 逐字對齊（「只做字元簡化」之要求）**：助手 23 鍵中之其餘（`项目`→`选项` 14 處、`哪些项目`→`哪些问题` 2 處、`当前`→`目前`、`未答的项目`→`未答之项目`、`等）的合法编码`→`等）之合法编码`、`更细致的调整`→`更细致地调整`、`字号`→`字级`）；輸入法側 `若当前前后半径`→`若目前前后半径`、`显示当前使用的打字模式`→`显示目前使用的打字模式`、`将当前注音排列`→`将目前注音排列`、`该回退之 ASCII 缓冲即`→`…缓冲区即`；`README-CHS.md` 之 `内部文件时间戳`→`内部档案时间戳`、`发布`→`发行`、`这样一来`→`如此一来`、`本体之建置相依`→`本体的建置相依`。

落點：輸入法 `Sources/vChewingIME_macOS/Resources/zh-Hans.lproj/Localizable.strings` 15 鍵；安裝程式 `Sources/Installer_macOS/Resources/zh-Hans.lproj/Localizable.strings` 3 鍵；助手 `ValueAdd/WebConfigAssistant/src/i18n.ts` zh-Hans 區塊（144 鍵）之 23 鍵；助手後設資料（`make metadata-update` 重生）12 欄；`README-CHS.md` 5 行；`ValueAdd/PKGInstallerAssets/pkgTextWarning-CHS.txt` 1 行 ⇒ 6 檔、＋59／−59，提交 `vChewing-macOS` `540fc1b3`。

### 8.3 驗證

| 項目 | 結果 |
|---|---|
| 輸入法 `Localizable.strings`（619 鍵，鍵集與 zh-Hant 全同） | 僅餘 1 鍵之差＝`kFilterFactoryKanjisOfNonCurrentInputMode.description` 之繁體／簡體語境互換（刻意） |
| 安裝程式 `Localizable.strings`（39 鍵） | 0 差異 |
| 助手 `i18n.ts`（zh-Hant／zh-Hans 各 144 鍵） | 0 差異 |
| 助手後設資料（287 組雙語欄位） | 僅餘同一處語境互換 |
| `README-CHS.md`（對 zh-Hant 逐行） | 僅餘首列語言列、L16「拼音/注音」語序（皆刻意）與 5 處「本仓」→「本仓库」（臺灣詞彙，無害） |
| `swift LocalizableFileSorter.swift`（自倉根）連跑兩次 | 兩支 `.strings` 之 sha256 不變 ⇒ 鍵序與鍵數未動、冪等 |
| `make metadata-update` | 重生 `assets/userdef-metadata.json`：`count` 與 `entries` 皆 119（與 `tests/metadata.test.js:28` 之斷言相符） |
| `make audit` | `typecheck`／`es5`／`test`（88 支、0 失敗）／`metadata`（無漂移）／`metadata-audit`／`surface-check`（108 鍵、無漂移）／`version-check`（4.8.7 (4870)）／`fixtures-check`（五份 fixture 皆 same）全過 |
| pre-commit `check_integrity.py` | CRITICAL 0、WARN 0（869 份受版控檔案） |

### 8.4 例外與界線

- **法定文本不動**：`LICENSE-CHS.txt` 與 `Sources/{vChewingIME_macOS,Installer_macOS}/Resources/zh-Hans.lproj/InfoPlist.strings` 之 `CFEULAContent` 係木蘭 PSL v2 之**官方簡體譯本**（「您／软件／复制／分发／许可证／约束」），與臺灣譯本（「台端／本軟體／重製／散布／授權條款」）相差 70 行；改之等同改寫法定文本。
- **文件內容落差僅報告不補**：`README-CHS.md` 較 `README.md` 少一句「（`make archiveLegacy` 另出 `.xcarchive`，供 Xcode 手动签名公证）」；另 5 處「本仓」於簡體版作「本仓库」（臺灣詞彙，無害）。`README-CHS.md` 之「用戶」1 處與 `pkgTextWarning-CHS.txt` 之「用户」1 處皆 mirror zh-Hant 之「用戶」⇒ 可接受。
- **官網助手產物未更新**：`vChewing-HomePage.io/assistant/assistant.html` 內嵌之助手產物尚未更新（經事主撤回至 P292 前之版本：殘留「空格」64／「半角」12／「字符」2／「默认」2／「打印」1／`数据`2／「模块」1／「字号」7／「项目」38 等）；重生須自 macOS 倉 `ValueAdd/WebConfigAssistant/` 跑 `make deploy` 並於官網倉另開提交。
- `tmp/` 下之稽核工具未入版控。`en.lproj`／`ja.lproj` 全部不在本案（日文之「半角」「字号」為日語正字；英文本即以 Space／half-width 表述）。
- 業經核對無偏離者：`ValueAdd/PKGInstallerAssets/pkgTextSuccessful-CHS.rtf`、`shortcuts-src/shortcuts.zh-Hans.md` 與四語系 `shortcuts.html`、`LegacyZone/**/zh-Hans.lproj/*`、`template-*.txt`、`Packages/**`（無 zh-Hans 資源）。

## 9. 事主之後續處置（2026-10-10）

- **官網倉**：事主將本 Phase 之 commit 重製為 `040b280`（`Terms // 空格鍵 -> 空白鍵; 空格 -> 空白字元.`，23 檔；其後再 squash 為 `1b5816f`，含 P294 之官網文書）：① 撤回 `assistant/assistant.html` 與 `assistant/index.html` 兩檔之改動；② 術語公告自 `## 4.8.7` 段移入新增之 `## 4.8.8 (Proposed)` 段（文字逐字同）。
- **本卷**：追加稽核原以 `# Phase 293` 獨立成篇，經事主指示「DevLogs 修一下，这也是 P292。」後改列為本 Phase 之一節。本卷 P292 之紀錄整併為單一 commit（母 `5fbf45e`）；原已推送之 `e44acf2`（P292 主體）與臨時之 `a8b0023`（P293 篇）由是取代 ⇒ 推送該倉需 force（`git push` 為事主專權）。
- **house style 收束**（同日，事主指示）：本 Phase 之卷內篇原為 20,178 chars／19 小節（逾大型預算 2.52×），依 `Tools/housestyle_audit.py` 之量尺改寫——長篇推導與逐處清單移入本檔，卷內篇回歸 §12.7.4 之六節骨架，並將 P292 登錄為「大型」型態（`LARGE_PHASES`）。

## 10. 產製鏈與版本號

- 官網 `manual/shortcuts.md`（繁體權威原文）→ `Scripts/Markdown2HTML/sync-from-homepage.swift` → `derive-zh-Hans.swift` → `generate-shortcuts.swift` → 四語系 `Resources/<lproj>/shortcuts.html`。`Makefile`：`SHORTCUTS_GENERATOR ?= ./Scripts/Markdown2HTML/generate-shortcuts.swift`、`SHORTCUTS_HOMEPAGE ?= ../../../vChewing-HomePage.io`；`make shortcuts` 讀官網倉、`make shortcutsCheck` 驗產物為最新（官網倉不在則退回本倉之同步副本）。
- 助手：`ValueAdd/WebConfigAssistant/` 之 `make metadata-update`（重導出 `assets/userdef-metadata.json`）→ `make bundle`（`dist/`）→ `make deploy`（複製 `dist/assistant.html`／`dist/index.html` 進官網倉 `assistant/`，不自動提交）。
- 副標之版本號由 4.8.6 併同更新為 4.8.7；新補之發行日誌公告（4.8.7 段，後移入 4.8.8 (Proposed)）刻意引述舊稱（「空格鍵」「空格」），故全倉掃描仍命中該 4 處——此為引文、非殘留。
- 全倉殘留掃描（本案完成後）：`vChewing-LibVanguard` 0 處；`vChewing-macOS` 2 處（`Makefile` 之縮排義、`tmp/new-ja.txt` 暫存產物）；`vChewing-HomePage.io` 6 處（1.4.7b 段縮排義 2、新補公告引述舊稱 4）。
