# Phase 250 研究暨後續手術規劃：狂打模式（Furious Typing）之注音化

> **文檔狀態**：研究暨規劃定案。本文即本 phase 之交付物，**不含實作**。
> **用途**：本文為 **Phase 252 起**各施工 phase 之設計依據；各 phase 之施工規格由其在所在卷（Reqs 記錄）內自述，惟凡本文已定案者一律不得於施工中悄然改寫——需改者，於該 phase 之記錄內明寫「與 P250 §X 之出入及其理由」。
> **資料來源**：`vChewing-macOS`（工作區 HEAD）、`vChewing-LibVanguard`、`vChewing-DevLogs` 之**靜態閱讀**，＋ 四項**本機離線實測**（兩倉逐位元組盤點、`UserDef`／`PrefMgr` 全表面清點、狂拼執行期管線全追蹤、Tekkon 動態注音排列與其單元測試資料之量化）。凡屬推論者皆已標註。
> **用詞**：本文稱 macOS 版輸入法為「唯音」、其 IME 進程為「IME 進程」；`UserDef` 之成員稱「偏好鍵」。**狂打**（Furious Typing；ja「狂打ち」）為本模式之總稱，**狂拼**（ja「狂拼」）專指拼音側、**狂注**（ja「狂注」）專指注音側。詳見 §一。
>
> **修訂沿革**：
> - **v1（2026-09-26）**：初稿。曾裁定「注音狂打不開 copilot 窗」，並以「當前內容須為合法完整音節」為自動提交之前提。
> - **v2（2026-09-26，事主覆核後）**：事主指出「注音的狂打模式還是需要 copilot 視窗的，比如打「ㄍㄋㄋ」可以預覽到「幹你娘」」。經實查生產辭典，確認 v1 之設計有**功能缺口**：單聲母縮寫打法（ㄍㄋㄋ、ㄋㄋ…）在 v1 下**完全打不出來**（三顆聲母互搶同一個槽）。**故 §3.0、§3.2、§3.5、§4.2、§八.4、§九 #4／#5b／#5c、§十、§十一 皆已改版**；凡與 §3.0 衝突之文字一律作廢。**改版之淨效果**：自動提交之判準由四條件簡化為三條件、注音狂打接入 copilot 窗體系、`SyllableIndex` 之職責邊界收緊為「只答前綴一問」，並新增 `unfinishedReading` 之分流實作。
> - **v4（2026-09-26，事主核定手術節奏後之編號重組）**：事主指示「按照你認為合理的手術順序重組 phase 編號（Phase 251 開始的編號）」，並定調節奏「每完成一個 phase 之後都檢討 Phase 250 做出你認為的必要調整」。**重組要點**：① **插入新的 P251「術前驗證靶」**（零生產碼，先把可實測者實測掉）——理由：本文之全部斷言皆來自唯讀閱讀、未曾編譯或執行，而事主兩次覆核所抓到之錯**兩次都在「由程式碼結構推導、但未實測」那一類**；② 原 P253「FSM 核心」**拆為 P254（閘門收束，行為零變動）＋ P255（自動切音節）＋ P256（copilot 窗）**三個獨立 phase，使「零變動」那一半能單獨取得綠燈；③ 原 P251 之「439 vs 427 對稱性測試」**移入 P251 驗證靶**（先量再建）；④ 原 P254 之「熱鍵查證」**由未決清單移入 P251**（那是我本可在規劃階段就查掉的東西）。**全系列由六個 phase 擴為九個（251–259）**。新增 §8.0.1「phase 收尾之回檢本文程序」，把事主之節奏寫成可執行之三動作。
> - **v3（2026-09-26，事主修訂 v2 之舉例後）**：事主修訂為「比如打「ㄍㄋㄋ」可以預覽到「幹你娘」「狗男女」」，並追加一項**方針改變**：「那麼注音狂打模式還是屏蔽掉注音文吧。我敲「ㄍㄢˋ-ㄋㄧˇ-ㄋㄧㄤˊ」是能看到有「幹你娘」候選字的。拼音的話可能因為 cartesian product 溢出等原因，敲 gnn 看不到「幹你娘」但能看到「狗男女」。」經以本機生產辭典**逐鍵複查**（結果見 §3.0.1 之 v3 表），確認：① 單聲母縮寫（`ㄍ-ㄋ-ㄋ`）之詞條值**確為字串 `ㄍ`**，**不是**「狗男女」；②「狗男女」之真源是**完整讀音鍵** `ㄍㄡˇ-ㄋㄢˊ-ㄋㄩˇ`（權重 `-6.649`，即該鍵之**唯一且最高**候選），而**拼音之 `gnn` 正是靠 `PinyinTrie` 之前綴展開把 `gnn` 還原成 `ㄍㄡˇ-ㄋㄢˊ-ㄋㄩˇ` 才看得到它**；③「幹你娘」在原廠辭典內**零命中**，其真源為**逐字音節之語言模型組句**（`幹` `ㄍㄢˋ` −5.206／`你` `ㄋㄧˇ` −5.075／`娘` `ㄋㄧㄤˊ` −5.257，且 `ㄍㄢˋ` 起首之鍵有 72 條、`ㄍㄢˋ-ㄋ` 起首者 **0 條**）**或使用者自有詞庫**。**故 v3 之兩項改版**：（a）「注音文抑制」由「注音狂打**不**抑制」改為「**注音狂打亦抑制**」（見 §3.1 第 5 點、§7.4）；（b）§3.0.1 之資料查核全面重做、並新增「`ㄍ-ㄋ-ㄋ` 之類單符號鍵對狂打**並非必要**」之說明；（c）§7.4／§8.5 新增「抑制旗標之落點商榷」一項施工工作。

---

## 〇、摘要

### 0.1 目標與交付

**目標**：把唯音既有的「狂拼模式」（拼音連續組句）擴展為一個**同時涵蓋拼音與注音兩種打字方式**的「**狂打模式**」，並使其在使用者偏好層面**可分開開關**——注音側預設**停用**、拼音側維持預設**啟用**（＝既有使用者的行為零變動）。

**交付**：① 本文（設計依據與手術路線圖）；② 六個後續 phase 的界線與完成定義（§八）；③ 需事主知悉之自動裁定記錄（§九）。

**本 phase 不動任何生產碼。** 唯二的落點是本文與 `Reqs_0241-0250.md` 內的 Phase 250 記錄。

**四項決定性事實（實查）**：

1. **狂打之「拼音專利」只是一道五元合取閘門，不是管線結構。** `isFuriousTypingModeEffective`（`InputHandler_FuriousResegmentation.swift:63`）＝ `currentTypingMethod == .vChewingFactory` ∧ `!prefs.cassetteEnabled` ∧ `prefs.furiousTypingEnabled` ∧ `!prefs.useSCPCTypingMode` ∧ **`composer.isPinyinMode`**。該五元之中唯最後一項排除注音，而它同時被 12 處讀取點當作「狂拼有效」之定義（§二.1）。**注音化的核心工作量，不在「新寫一套注音管線」，而在「把這道閘門與其 12 個下游讀取點所隱含的『狂拼⇒拼音』假設逐一解耦」，並為注音補上一條等價的『自動切音節』機構**（§二.2）。
2. **注音側所需的資料結構，比拼音側小兩個數量級。** 拼音狂拼需要 `PinyinTrie`（每排列 498–571 節點）以支援「不完整 romaji 前綴 → 可能注音」之反向展開；注音鍵流本身即為注音符號，**不需要反向推導**。實測：`mapHanyuPinyin` 之 427 條注音詞幹，其**全部非空前綴**僅 **442 條**（427 完整 ＋ 15 嚴格前綴），UTF-8 共約 **3 KB**（§四.2）。故注音側所需者是一個**前綴集合**，而非 Trie；且其成本可忽略。
3. **單聲母／單韻母是辭典內之 first-class 讀音鍵，這是整個狂打功能之樞紐。** 實查生產辭典（`VanguardFactoryDict4Typing.txtMap`，206,266 條鍵）：**21 個聲母與 16 個單韻母／介母全部**是合法讀音鍵（各有一條「以自身為值」之詞條，如 `ㄍ → ㄍ`），另有 **85** 條「各段皆為單一注音符號」之多音節鍵（如 `ㄍ-ㄋ-ㄋ → ㄍ`、`ㄋ-ㄋ → ㄋㄟㄋㄟ`）。⇒ 自動提交單聲母在技術上完全可行；而**不做此事就等於縮寫打法在狂打模式下永遠打不出來**（三顆聲母互搶同一個槽位）。此即事主異議之技術根據（§3.0）。**惟須注意：那 85 條單符號鍵之值多為「回聲字串」，狂打之真正價值在於逐字組句與整鍵詞條**——「狗男女」來自完整讀音鍵 `ㄍㄡˇ-ㄋㄢˊ-ㄋㄩˇ`（−6.649），「幹你娘」則來自逐字語言模型組句（原廠辭典**無**該詞；§3.0.1 之 v3 表）。
4. **動態注音排列之「按鍵 ↔ 讀音」對照，引擎內不存在。** 反向（讀音 → 按鍵序列）**無任何 API**；正向（按鍵 → 讀音）是**逐鍵程序式解碼**且**依賴當前聲介韻槽狀態**（`handleETen26`／`handleHsu` 等五支 handler ＋ 共用的 `commonFixWhenHandlingDynamicArrangeInputs`），非純函式、亦非查表。唯一的全量對照在**測試資料**內：`Tests/TekkonTests/TestAssets_Tekkon/Tekkon_TestData.swift` 之 1485 行 × 5 排列 ＝ **7366 筆**已斷言之編碼（§五.1）。**故「把動態注音的讀音組合窮舉成 Trie」在技術上可行、但與現行程式碼是兩份各自維護的真相**——這是本 phase 對事主之存疑所給出的核心答覆（§五）。

### 0.2 關鍵取捨

| # | 議題 | 結論 | 依據 |
|---|---|---|---|
| 1 | 注音狂打是否沿用 `FuriousTypingSegmentor` 之 DP 重切分 | **不沿用**。注音鍵流之音節邊界由「槽位型別遞降」決定，非由語言模型猜測；且拼音重切分之全部前提是「相鄰音節可無分隔連寫」（`furiousTrail.joined()`），注音不成立 | §二.2、§三.4 |
| 2 | 注音狂打之「自動切音節」落點 | **Tekkon 提供結構判準、Handler 執行切分**（不在 Tekkon 內自動 chop） | §3.3 |
| 2b | **注音狂打是否開 copilot 窗** | **要開**（事主 v2 異議之直接結果）：縮寫／逐字打法**非開不可**——不開則該打法打不出，且「幹你娘」（逐字組句）與「狗男女」（整鍵詞條）一類候選永無露面之日 | §3.0、§3.5 |
| 3 | Tekkon 是否新增 Trie | **否**。新增一個 **442 條**之前綴索引（`Tekkon.SyllableIndex`），非 Trie；**不**收錄動態排列之按鍵序列 | §5.2、§5.3 |
| 4 | 動態鍵盤「下一步可敲哪些鍵」之 API | **本輪不實作**；逐鍵模擬派生（simulation-derived）列為**後續選項**，且**若實作則置於 `LibVanguard` 而非 Tekkon** | §5.4 |
| 5 | 偏好鍵之處理 | 既有 `FuriousTypingEnabled` **兩分為** `FuriousTypingEnabled4Pinyin`（承接舊值）與 `FuriousTypingEnabled4Zhuyin`（預設 `false`）；**Swift 端符號亦全量重新命名，不留別名** | §6.1、§6.2 |
| 6 | 資料遷移之落點 | 既有之 `PrefMgr.migrateDeprecatedSettings()`（`PrefMgr_Core.swift:516`）內新增一段，**逐字照** `UsingHotKeyHalfWidthASCII → UsingHotKeyHalfWidthPunctuation` 之成例 | §6.3 |
| 7 | 「注音文抑制」之歸屬 | **兩種狂打皆抑制**（v3，事主明示）。由「拼音狂打 且 拼音方式」改為依當前打字方式二選一之析取式；**且傾向把該旗標之賦值由 `LXFacade.syncPrefs()` 移到 Handler 側**（以 `typingMode` 為單一真源，避免熱鍵切換時之脫鉤）——留待 Phase 256 實查後定案 | §7.4 |
| 8 | Phase 切分 | **六個**後續 phase（251 起）。**251 先動 Tekkon**（事主明示），252 為偏好層、253 為 FSM 核心、254 為辭典層、255 為偏好介面與 i18n、256 為跨倉驗收 | §八 |
| 9 | 兩倉 byte-sync | 每一個後續 phase **同輪**鏡像 `Sources/`／`Tests/`／`Deps/`／六份 manifest／`makefile`，並以 `cmp`／`diff -rq` 之**實際輸出**為驗收證據 | §8.0、§10.3 |

**★ 三則不可退讓之約束**：① **注音狂打之出廠預設值為 `false`**——未表態之既有使用者，其拼音狂拼行為、乃至一切既有行為，一律零變動；② **本系列不動 `FuriousTypingSegmentor`、不動 Homa**——注音化是「新增一條與拼音並行的路徑」，不是「把拼音路徑改造成通用路徑」。凡遇「不如把拼音那套抽象化」之施工衝動，一律以本條擋下；真要抽象化，另立 phase；③ **單聲母／單韻母之縮寫打法必須可用**（§3.0）——自動提交之判準**不得**要求「當前內容已為完整音節」，且 `unfinishedReading` 於注音側必須回傳當前音節。此為本系列之**功能底線**，非加分項。

### 0.3 四則關鍵約束

1. **`UserDef.rawValue` 一經發佈即不可更名**（`UserDef.swift:9–10` 之明文紀律），而 `rawValue` 就是 `UserDefaults` 之鍵（`UserDef.swift:1427`）。故本系列之「重新命名」**必然**是一次**有損**的鍵遷移，必須配套 §六.3 之遷移碼；且 `UserDef.exportAsJSON()` 之輸出鍵亦即 `rawValue`，故**外部既有之配置包一旦含舊鍵，其匯入將以 `"Unknown key"` 失敗**（§六.4）。
2. **`migrateDeprecatedSettings()` 於每次 `InputSession.activateServer()` 執行**（`PrefMgr_Utilities.swift:8, 11–12`），且其內部直接使用 `UserDefaults.standard`（`PrefMgr_Core.swift:517`）而非 `UserDefaults.current`。新增之遷移段**必須自我守衛、冪等**——以「舊鍵存在與否」為閘，處理完即 `removeObject`。
3. **兩個 IME 行程之測試不得並行**：兩倉之 `swift test` 共用同一批**磁碟上**之具名 `UserDefaults` suite，併跑會產生游移之偽紅（`KnowledgeMemo4LLM.md:399`；P242 實錄）。本系列涉及偏好鍵之遷移，此紀律尤須遵守。
4. **`Tekkon` 靶不受 `defaultIsolation(MainActor.self)` 規範**（`Package.swift:92–94`；`Tekkon_PinyinTrie.swift:108–109` 有明文）。故 Tekkon 內任何新增之全域可變快取，**必須**照 `PinyinTrie.sharedCache` 之成例（`NSLock` ＋ `nonisolated(unsafe) private static var`）明示其同步責任。

---

## 一、術語定案：狂打／狂拼／狂注

### 1.1 事主之裁定

> 「從這個 Phase 起，Furious 作為 vChewing 輸入法的模式而言的中日翻譯由「狂拼」擴展到新的稱謂「狂打／狂打ち」。」
> 「從這個手術開始，Furious Typing 模式不再是拼音打字的專利。」

### 1.2 三層命名與其對位

| 層級 | zh-Hant | zh-Hans | ja | en | 說明 |
|---|---|---|---|---|---|
| **總稱**（模式本身） | 狂打模式 | 狂打模式 | **狂打ち**モード | Furious Typing | 涵蓋拼音與注音兩側 |
| **拼音側** | 狂拼模式 | 狂拼模式 | **狂拼**モード | Furious **Pinyin** Typing | 現行功能之既有稱謂，**不改** |
| **注音側** | 狂注模式 | 狂注模式 | **狂注**モード | Furious **Zhuyin** Typing | 本次新增 |

**「狂注」之定名理由**：事主只釘死了總稱與既有之「狂拼」，注音側之簡稱未指定。取「狂注」是為了與「狂拼」**同構**（`狂` ＋ 一個單字動詞，且該動詞是本輸入法之第一等術語：注音／拼音），並使四語系在句中皆為兩字／兩拍，便於 `shortTitle` 之排版。ja 之「狂注」不成詞，但與「狂拼」同屬生造語，且 `狂` 字頭已由事主釘死；不採「狂打ち注音」一類長形，因其在 `shortTitle` 內會與總稱撞名。

**「狂打ち」之字形**：照事主原文用**漢字 ＋ 平假名送假名**（`狂打ち`），不寫成全漢字「狂打」——後者在日文內易被讀作「きょうだ」，失其動詞性。

### 1.3 落點：四語系字串與 `TypingMode`

`TypingMode` 之 `rawValue` 直接構成 i18n 鍵（`InputHandler_TypingMode.swift:27–29`：`"i18n:TypingMode.i18nKey4InlineModeHint.\(rawValue)"`）。故新增 `.zhuyinFuriousTyping` 即自動要求一條新鍵 `i18n:TypingMode.i18nKey4InlineModeHint.zhuyinFuriousTyping`（現有 `.pinyinFuriousTyping` 之四語系值為：zh-Hant／zh-Hans「狂拼模式」、ja「狂拼モード」、en「Furious Typing」——**該值建議同步改為「狂拼模式」語義不動、但 en 改「Furious Pinyin Typing」以與注音側對稱**；此為 §九 之自動裁定事項之一）。

**既有 i18n 之清單**（皆在 `Sources/vChewingIME_macOS/Resources/{en,ja,zh-Hans,zh-Hant}.lproj/Localizable.strings` 之 444–445 行與 349 行；`Base.lproj` **無** `Localizable.strings`）：

| 鍵 | 現值（zh-Hant） | 處置 |
|---|---|---|
| `i18n:UserDef.kFuriousTypingEnabled.shortTitle` | 啟用狂拼模式（連續拼音打字） | 隨 case 更名；文案改「啟用狂拼模式（連續拼音打字）」**不變**（其語義本即拼音） |
| `i18n:UserDef.kFuriousTypingEnabled.description` | （長文，見 §六.1） | 隨 case 更名；**內容不動** |
| `i18n:TypingMode.i18nKey4InlineModeHint.pinyinFuriousTyping` | 狂拼模式 | 值**不動**（zh 側）；en 建議改 `Furious Pinyin Typing` |
| `i18n:TypingMode.i18nKey4InlineModeHint.zhuyinFuriousTyping` | — | **新增**：狂注模式／狂注模式／狂注モード／Furious Zhuyin Typing |
| `i18n:UserDef.kFuriousTypingEnabled4Zhuyin.shortTitle` | — | **新增**：啟用狂注模式（連續注音打字）／啟用狂注模式（连续注音打字）／狂注モードを有効化（連続注音入力）／Enable Furious Zhuyin Typing (continuous bopomofo) |
| `i18n:UserDef.kFuriousTypingEnabled4Zhuyin.description` | — | **新增**：zh-Hant 草案見 §七.5 |

zh-Hans 一律照 **zh-Hans-TW** 紀律（僅簡化字形、詞彙沿用臺灣用法）。

---

## 二、現況盤點（實查）

### 2.1 閘門與其讀取點

| 名稱 | 落點 | 內容 |
|---|---|---|
| `TypingMode` | `InputHandler_TypingMode.swift:14–30` | `.cassette`／`.bopomofoKeyblock`／`.pinyinKeyblock`／`.pinyinFuriousTyping` |
| `typingMode` | 同檔 `:38–44` | `if prefs.cassetteEnabled { return .cassette }`；`if prefs.furiousTypingEnabled, !prefs.useSCPCTypingMode, composer.isPinyinMode { return .pinyinFuriousTyping }`；`return composer.isPinyinMode ? .pinyinKeyblock : .bopomofoKeyblock` |
| `isFuriousTypingModeEffective` | `InputHandler_FuriousResegmentation.swift:63–65` | `currentTypingMethod == .vChewingFactory && typingMode == .pinyinFuriousTyping` |
| `hasFuriousFrontPending` | 同檔 `:68–70` | `isFuriousTypingModeEffective && !composer.romajiBuffer.isEmpty` |

`isFuriousTypingModeEffective` 之**讀取點共 12 處**（實查）：
`Typewriter_BPMFFullMatch.swift:269`（`allowsExtendedRomajiBuffer`）、`:321`（trail 記錄）；`InputHandler_CoreProtocol.swift:215`（`isPinyinFamilyTypingMode`）、`:873`（POM matchMode）、`:885`（POM 自動套用抑制）；`InputHandler_HandleCandidate.swift:281`（`furiousShift`）；`InputHandler_FuriousResegmentation.swift:69, 166, 352, 441`；`InputHandler_HandleStates.swift:43`（`furiousFrontContext`）、`:119`（`furiousAbbreviatedCells`）；`Session/InputSession_Delegates.swift:352`。

`hasFuriousFrontPending` 之**讀取點共 6 處**：
`Typewriter_BPMFFullMatch.swift:122`（Shift＋選字鍵路由）、`:136`（Enter 固化）；`InputHandler_TriageInput.swift:35`（固化後之空格消費）、`:49`（Tab）；`InputHandler_HandleStates.swift:271`（`confirmFuriousFrontCandidate` 之守衛）、`:813`（標點前固化）；`Session/SessionCoreProtocol.swift:198`（`isFuriousCopilotCandidateWindowVisible`）。

`typingMode` 之讀取點共 3 處：`InputHandler_HandleComposition.swift:27`（typewriter 分派）、`InputHandler_FuriousResegmentation.swift:64`、`Session/SessionProtocol.swift:337`（內文模式提示之 i18n 鍵）。

**關鍵觀察**：`InputHandler_HandleComposition.swift:27–37` 之 `switch typingMode` **已把 `.bopomofoKeyblock` 與 `.pinyinFuriousTyping, .pinyinKeyblock` 一併派給同一個 `BPMFFullMatchTypewriter`**。故注音狂打**不需要新的 typewriter**，只需要該 typewriter 內部的狂打分支認得注音。

### 2.2 拼音狂拼與注音狂打之根本差異

| 面向 | 拼音狂拼（現況） | 注音狂打（本案） |
|---|---|---|
| 注拼槽之內在 | `romajiBuffer`（**無分隔之字母流**，可橫跨多音節）＋ 聲介韻調四槽 | **僅**聲介韻調四槽；鍵流本身即帶分隔（聲介韻調之槽位型別是天然邊界），**不需要** extended buffer |
| 音節邊界之判定 | 未知。以 `PinyinTrie.chop` 貪婪最長匹配 ＋ LM 引導之 DP 重切分修正 | **已知**。新鍵之目標槽位若早於或等於已填之最高槽位，則當前音節已了結 |
| 「不完整讀音」之表示 | `romajiBuffer`（如 `bian` 打了一半之 `bia`） | 四槽之部分填充（如只有聲母 `ㄅ`）——`composer.isEmpty == false` 即「有未完成讀音」 |
| 前綴合法性 | `PinyinTrie.search(romaji)` 前綴展開 | `Tekkon.SyllableIndex.isPrefix(_:)` |
| 重切分之必要性 | **必要**（greedy chop 會切錯，如 `fangan` → `fang\|an` 而使用者要 `fan\|gan`） | **不必要**（邊界為結構所決定）；且「相鄰音節無分隔連寫」之前提不成立 |
| 簡拼（`ysxb` → 整詞） | 有（α 路徑：`abbreviatedWordCandidates(keysChopped:)`） | **無**（注音不打簡拼；注音符號本身已是音節之最小成分） |
| 注音文抑制 | 啟用 | **啟用**（v3，事主明示；與拼音同，見 §7.4） |

**故注音狂打是拼音狂拼之「退化情形」**：少掉 segmentor、少掉 trail、少掉簡拼、少掉 extended buffer，換來一條新的「自動切音節」判準。這正是「新增並行路徑」而非「抽象化既有路徑」在工程上更省的理由（§0.2 ★②）。

### 2.3 `FuriousTypingConfig` 與注音之關係

`FuriousTypingConfig`（`Typewriter_BPMFFullMatch.swift:21–74`）之三欄——`trail`（拼音字母 blob 序列）、`highlightOverride`、`coSegmentedOffers`——**皆為拼音專屬**。注音狂打**不寫入 trail、不建立 offers**；`furiousHighlightOverride`／`coSegmentedOffers` 於注音側**無生產者**（前者由 copilot 窗之高亮驅動、後者為拼音之聯合重切產物）——**注音狂打不寫入對方**，故：

- `furiousConfig` 這一項**協定要求**（`InputHandler_CoreProtocol.swift:50`）**不動**（避免打破 `InputHandler`／`MockInputHandler` 兩個 conformer）；
- 注音狂打**不呼叫** `invalidateFuriousTrail()`／`popFuriousTrail(_:)`（呼叫亦無害，因其只動拼音狀態）；
- 需要動的是 `hasFuriousFrontPending` 與 `unfinishedReading`（見 §3.5）；註音側之 highlight 與 co-segmented 路徑自然不被觸發（無生產者）。

### 2.4 既有資產之可複用度（逐段）

| 段 | 落點 | 注音可否複用 |
|---|---|---|
| `BPMFFullMatchTypewriter.handle` 之選字鍵路由、Enter 固化、Backspace | `Typewriter_BPMFFullMatch.swift:106–144` | **可**（皆以 `hasFuriousFrontPending` 為閘，閘一放寬即通） |
| `consumeReadingInputIfNeeded` 之「先送注拼槽」骨架 | 同檔 `:240–283` | **可**（注音分支已在 `receiveKey(fromScalar:)` 內） |
| `performPinyinAutoChopIfNeeded` | 同檔 `:285–350` | **不可**（拼音專屬）；注音另立一支 |
| `composeReadingIfReady` ＋ `readingKeyForQuery` | 同檔 `:352` 起 | **可**（與拼音無關；`phonabetKeyForQuery` 本即注音） |
| `furiousFrontContext`／`buildFuriousFrontCandidates` 之 Homa 段 | `InputHandler_HandleStates.swift:39–101, 154–253` | **部分可**（候選評分、POM、交叉邊界詞皆與音節表示無關）；其**輸入**（`romaji` → `zhuyinReadings`）**不可** |
| `applyFuriousFrontCandidate`／`previewFuriousHighlightedCandidate` | `InputHandler_FuriousResegmentation.swift:192–341` | **可**（純 Homa 鍵桶操作） |
| `enumerateFuriousResegmentationCandidates`／`resegmentFuriousTrailIfNeeded` | 同檔 `:351–431, 549–573` | **不可**（trail 為拼音字母） |
| `unfinishedReading`（copilot 窗頂部） | `InputSession_Delegates.swift:204–208` | **需改**（改讀 `composer` 之當前音節） |
| 註音文抑制 | `LXFacade.swift:334` | **需改**（見 §7.4） |

---

## 三、注音狂打之規格

### 3.0 ★ 注音狂打之原始需求：**單聲母狂打**（事主 2026-09-26 之異議）

> 事主原文：「竊以為注音的狂打模式還是需要 copilot 視窗的，比如打「ㄍㄋㄋ」可以預覽到「幹你娘」。」

此異議推翻本文初稿之兩項設計（初稿曾主張「不開 copilot 窗」並以「音節須為合法完整讀音」為自動提交之前提）。其原因不只是「少了預覽」，而是**單聲母狂打根本打不出來**：

| 步驟 | 初稿之行為 | 後果 |
|---|---|---|
| 敲 `ㄍ` | 注拼槽＝`ㄍ`；因非完整讀音故不提交 | — |
| 敲 `ㄋ` | `S_new(1) <= S_max(1)`，但 `ㄍ` 非**完整**讀音 ⇒ 不切、逕行覆寫 | **`ㄍ` 消失**，注拼槽＝`ㄋ` |
| 敲 `ㄋ` | 同上 | 注拼槽＝`ㄋ`（第二顆） |

即：初稿之設計會讓「ㄍㄋㄋ」在狂打模式下**永遠打不出來**——三顆聲母互搶同一個槽，最終只剩一顆。而這正是網路注音文最典型之打法。

**故本節（含 §3.2 之判準與 §3.5 之 copilot 窗）已然改版；凡與本節衝突之初稿文字一律作廢。**

#### 3.0.1 決定性證據：原廠辭典之實況（**v3 全面複查**）

實查 `VanguardFactoryDict4Typing.txtMap`（生產辭典，206,266 條鍵；取自 `Build/…/vChewing.app` 之既有產物）：

| # | 事實 | 值 |
|---|---|---|
| 1 | **21 個注音聲母全部**都是合法讀音鍵（`ㄅ`…`ㄙ`） | 21／21；其詞條為「以自身為值」之單條目，權重一律 `-8.863`（如 `ㄅ → ㄅ`、`ㄍ → ㄍ`、`ㄋ → ㄋ`） |
| 2 | 16 個單獨韻母／介母亦全部是合法讀音鍵（`ㄚ`…`ㄩ`） | 16／16，同形 |
| 3 | 「各段皆為單一注音符號」之多音節鍵 | **85** 條（`ㄋ-ㄋ`、`ㄓ-ㄓ`、`ㄔ-ㄔ`、`ㄕ-ㄕ`、`ㄓ-ㄨ`…） |
| 4 | **`ㄍ-ㄋ-ㄋ` 之詞條值** | **字串 `ㄍ`**（權重 `-8.863`）——**不是**「狗男女」、亦不是「幹你娘」 |
| 5 | **「狗男女」之真源** | 完整讀音鍵 **`ㄍㄡˇ-ㄋㄢˊ-ㄋㄩˇ`**（權重 `-6.649`，**該鍵之唯一條目**）；`ㄍㄡˇ-ㄋㄢˊ-ㄋㄩ`／`ㄍㄡ-ㄋㄢ-ㄋㄩ` 皆**不存在** |
| 6 | **「幹你娘」於原廠辭典內** | **零命中**（全檔 450,484 行；`幹你`／`你娘` 亦皆 0）。其逐字單音節為：`幹`＝`ㄍㄢˋ`（−5.206）、`你`＝`ㄋㄧˇ`（−5.075）、`娘`＝`ㄋㄧㄤˊ`（−5.257） |
| 7 | `ㄍㄢˋ` 起首之鍵共 **72** 條（`ㄍㄢˋ-ㄅㄢˋ`、`ㄍㄢˋ-ㄇㄚˊ`…），但 `ㄍㄢˋ-ㄋ` 起首者 **0 條** | ⇒ 該三字**只能**由語言模型逐字組句，或由使用者自有詞庫提供 |

**上游正本**：`vChewing-VanguardLexicon` 之 `Sources/LibVanguardChewingData/Resources/components/common/data-zhuyinwen.txt`，**全檔 8 行**：

```
ㄅㄧㄤ   ㄅㄧㄤ    -9.6
ㄅㄧㄤˋ  ㄅㄧㄤˋ   -9.6
ㄉㄨㄤ   ㄉㄨㄤ    -9.6
ㄋㄟ     ㄋㄟ      -9.6
ㄋㄟㄋㄟ  ㄋ-ㄋ     -9.6
ㄋㄟㄋㄟ  ㄋㄟ-ㄋㄟ  -9.6
ㄎㄧㄤ   ㄎㄧㄤ    -9.6
ㄍㄋㄋ   ㄍ-ㄋ-ㄋ   -9.6
```

該檔之型別標記為 `EntryType.zhuyinwen`（`10 << 0`；其詞條之值**皆為注音符號字串**），**即 §7.4 那個抑制旗標所過濾之對象**——這 8 行就是「注音文」的全部。

**三項結論**：

1. **單聲母音節在辭典內是 first-class**：`assembler.insertKey("ㄍ")` 本即會成功，故自動提交單聲母在技術上可行（v1 之缺口因此純屬設計判斷之誤，非資料限制）。
2. **但單符號多音節鍵（`ㄍ-ㄋ-ㄋ`）對狂打並非必要**：其值只是回聲字串 `ㄍ`。狂打之所以需要 `ㄍ|ㄋ|ㄋ` 三鍵，理由是**逐字組句**（候選來自語言模型）與**不吞鍵**（v1 之病灶），與那 85 條單符號鍵無關。**故 §4.2 之 `SyllableIndex` 不收單符號之裁定不變**。
3. **「狗男女」與「幹你娘」各有其真源、且互不相同**：

| 候選 | 真源 | 為何拼音之 `gnn` 看得到／看不到 |
|---|---|---|
| **狗男女** | **完整讀音鍵** `ㄍㄡˇ-ㄋㄢˊ-ㄋㄩˇ`（−6.649） | 拼音側之 `gnn` 經 `PinyinTrie` 之前綴展開，可得 `ㄍㄡˇ`／`ㄋㄢˊ`／`ㄋㄩˇ` 等一眾注音桶，恰含該鍵 ⇒ **看得到** |
| **幹你娘** | **逐字語言模型組句**（`ㄍㄢˋ`＋`ㄋㄧˇ`＋`ㄋㄧㄤˊ`）**或**使用者自有詞庫 | 拼音側同樣可得該三桶，但依 P155 之量化，拼寫之笛卡爾積會觸發 Homa 之 `maxSegLength` 半徑偵測與防禦 ⇒ **繁雜度壓過收益、看不到**。**故事主所見之對比（`gnn` 見「狗男女」而不見「幹你娘」）正是此二源之差異** |

**⇒ 對事主之例之誠實答覆（v3）**：在**完整讀音**之輸入下（`ㄍㄢˋ-ㄋㄧˇ-ㄋㄧㄤˊ`、`ㄍㄡˇ-ㄋㄢˊ-ㄋㄩˇ`），注音狂打之 copilot 窗**會**預覽到「幹你娘」與「狗男女」——前者靠**逐字組句**、後者靠**整鍵詞條**，而**兩者都不需要注音文那 8 行**。在**單聲母縮寫**（`ㄍㄋㄋ`）之輸入下，則只會得到回聲字串 `ㄍ`（且該字串將因 §7.4 之抑制而不再出現）——**這正是事主 v3 追加「注音狂打也屏蔽注音文」之合理性所在：屏蔽掉回聲字串，留下的才是使用者要的詞。**

#### 3.0.2 自動提交之**充分**條件（比必要條件更強、且與拼音一致）

既然單聲母本即為合法音節，則「自動提交」**不必**等到結構上確定為新音節——只要「當前串已不可能再延伸成更長之讀音」即可提交。此與拼音狂拼之 greedy 語義同源（拼音之 `pinyinAutoChopResult` 亦是在「延伸後不再是單一可唸讀音」時才 chop）。

上表之三步遂變為：

| 步驟 | 新行為 |
|---|---|
| 敲 `ㄍ` | 注拼槽＝`ㄍ` |
| 敲 `ㄋ` | `ㄍㄋ` **非**任一讀音之前綴 ⇒ **提交 `ㄍ`**、注拼槽重設為 `ㄋ` |
| 敲 `ㄋ` | `ㄋㄋ` **非**任一讀音之前綴 ⇒ **提交 `ㄋ`**、注拼槽＝`ㄋ`（第二顆） |
| （paused） | 組字器三鍵皆在；copilot 窗以 `ㄍ-ㄋ-ㄋ` 查得詞條 ⇒ 預覽 `ㄍㄋㄋ` |
| 空格／Enter | 固化第三顆並遞交 |

**「不必等到結構上確定」是本改版之關鍵**：條件 ③（目標槽位不升）只是「新音節開始」之**必要**條件，用來避免在**同一**音節內誤提交（如 `ㄅㄧ` ＋ `ㄢ`）；真正之**充分**條件是條件 ④ 之否定（不再可能是任何讀音之前綴）。

### 3.1 使用者可見之行為

1. 使用者以任一注音排列連續鍵入，**不需逐音節敲聲調、亦不需按空格確認**。
2. 每當當前注拼槽內容連同本拍按鍵**已不可能再延伸成任何合法讀音**時，當前內容自動寫入組字器（＝「自動切音節」）；**單聲母亦照此提交**（§3.0）。
3. 聲調鍵之語義**完全不動**：敲聲調即照既有行為確認該音節（含後置聲調覆寫）。狂打只免除「不敲聲調也要能前進」這一件事。
4. 空格／Tab／Enter／標點之語義**沿用拼音狂拼**（固化當前讀音並停留於組字狀態；標點前先固化）。
5. **不進行重切分**；**建立 copilot 未完成讀音窗**（見 §3.5）；**觸發注音文抑制**（v3：與拼音同；見 §7.4）。
6. 逐字選字模式（SCPC）下狂打**不生效**（沿用既有 `!prefs.useSCPCTypingMode` 條件）。

### 3.2 自動切音節之判準（本案之核心規格）

設當前注拼槽已填之最高槽位為 `S_max`（以 `PhoneType.rawValue` 排序：聲 1 ＜ 介 2 ＜ 韻 3 ＜ 調 4），本拍按鍵譯得之注音為 `K`、其目標槽位為 `S_new`。

**判準（三條件，施工以此為準）**：

```
切音節 ⇔ ① 注拼槽非空
        ② 本鍵之目標槽位 S_new ≠ .intonation（後置聲調屬當前音節）
        ③ S_new <= S_max
        ④ 且 `SyllableIndex.isPrefix(當前內容 ∪ {K})` 為**假**
           （「∪」＝以 K 寫入其目標槽後之假想內容）
→ 成立時：以 phonabetKeyForQuery(pronounceableOnly: true) 取出當前內容、寫入組字器、
          清空注拼槽，然後才把本鍵送入。不成立時：照既有行為把本鍵送入注拼槽。
```

**逐條理由**：

| # | 條件 | 為何需要 |
|---|---|---|
| ① | 注拼槽非空 | 空槽無可提交 |
| ② | 非聲調 | 聲調是**同一**音節之延續（後置聲調），提交它會把該音節拆成兩半 |
| ③ | `S_new <= S_max` | 「新音節開始」之**必要**條件。缺它則同一音節內之每一次追加都會被誤判（如 `ㄅ` ＋ `ㄧ` 時 `S_new(2) > S_max(1)` 故不切，正確） |
| ④ | 延伸後非任何讀音之前綴 | 「新音節開始」之**充分**條件，亦為單聲母狂打之解藥（§3.0.2）。同時是**動態排列逐槽覆寫**之解藥（見下） |

**三則對照實例（施工者以此自查）**：

| 輸入 | `S_new` vs `S_max` | ④ 之判定 | 結果 |
|---|---|---|---|
| `ㄍ` ＋ `ㄋ` | 1 ≤ 1 ⇒ 進入 ④ | `ㄍㄋ` 非任一讀音之前綴（假） | **切** ⇒ 提交 `ㄍ`，新音節 `ㄋ` |
| `ㄅㄧ` ＋ `ㄢ` | 3 ＞ 2 ⇒ 直接不切 | — | **不切** ⇒ 續接為 `ㄅㄧㄢ`（使用者確係此意者，此為唯一能打出 `ㄅㄧㄢ` 之選擇） |
| 大千26 `qquu`（＝`ㄅㄚ`）：首擊 `q` 後敲第二個 `q` | 1 ≤ 1 ⇒ 進入 ④ | 假想內容為 `ㄆ` 被覆寫為 `ㄅ`，即 `ㄅ`；`ㄅ` **是**合法讀音之前綴（真） | **不切** ⇒ 逕行覆寫（正確：該排列之合法編碼本即逐槽覆寫） |

**已知之代價（可接受、已記錄）**：`ㄅ` ＋ `ㄋ` 之一類「兩顆聲母連打」必然產生 `ㄅ|ㄋ` 兩個單聲母音節。若使用者真正想打的是 `ㄅㄧㄢ` 而誤敲了 `ㄋ`，他得自行退格——此與拼音狂拼之 greedy 行為同等對待，非本案新增之缺陷。

> **規格留白（須於 Phase 255 實測定案）**：條件 ④ 之假想內容應以值語義之副本試算（`var probe = composer; probe.receiveKey(...)`；`Composer` 是 `@frozen struct`，複製成本極低），**不得**直接改動 `composer` 後再回退。施工者若發現更廉價之做法（如直接在 `translate(key:)` 之結果上判定），得就地採用並於該 phase 記錄理由。

### 3.3 為何 Tekkon 不自動 chop

`Composer` 是 `@frozen public struct`，且 `/` 之語義（`pinyinAutoChopResult` 僅回傳「預測」，實際 chop 由 handler 執行）已是本倉之既有分工。**注音沿用同一分工**：Tekkon 提供**判準所需之素材**（當前槽內容、目標槽位、前綴合法性），Handler 執行切分與寫入。

**紅線**：`Tekkon` **不得**新增任何知曉「狂打」概念之 API，亦不得在 `receiveKey` 內做任何自動提交。Tekkon 是無狀態偏好、無會話概念之音節組裝器，此邊界一破即為不可維護（§5.5）。

### 3.4 為何不沿用 `FuriousTypingSegmentor`

`FuriousTypingSegmentor` 之 DP 以「字母流之位置切分」為搜尋空間，其輸入是 `furiousTrail.joined()`（`InputHandler_FuriousResegmentation.swift:378`）——**無分隔之連寫字串**。注音鍵流**不具此性質**：每一鍵已由排列與槽位型別唯一決定其歸屬，故「切分」不是搜尋問題而是判定問題。

若硬要沿用，須先構造一個「注音鍵流之無分隔字串」——但該字串在注音內**根本不存在**（排列對若干鍵是一對多、且依賴槽狀態），構造它的成本高於直接判定。**故不沿用，且不動 segmentor 一行**（§0.2 ★②）。

### 3.5 copilot 窗與 `unfinishedReading` 之處理（**已依事主異議改版**）

> 初稿曾主張「注音狂打不需要 copilot 窗，因使用者打出的注音符號本身即為讀音」——**該主張已被事主之「ㄍㄋㄋ」一例推翻**（§3.0）。注音狂打**需要** copilot 窗，且其必要性有三層：① **縮寫／逐字打法**（ㄍㄋㄋ、ㄋㄋ、ㄓㄓ…）之讀音序列由多個單符號音節組成，只有 copilot 窗能把它們拼起來顯示；② **完整讀音之逐字組句**（`ㄍㄢˋ-ㄋㄧˇ-ㄋㄧㄤˊ` → 「幹你娘」）與**整鍵詞條**（`ㄍㄡˇ-ㄋㄢˊ-ㄋㄩˇ` → 「狗男女」）皆須候選窗才可見——**此二者為事主所舉之正例**（§3.0.1 之 v3 表）；③ 拼音側既有之 copilot 機制（交叉邊界詞、POM 前置、就地選字）本身即是狂打模式之核心價值，注音沒有理由自外。

**故本案之決定**：**為注音狂打開啟 copilot 窗**。作法是把 `hasFuriousFrontPending` 對注音之語義訂為 **`!composer.isEmpty`**——與拼音之 `!composer.romajiBuffer.isEmpty` 同構（皆為「注拼槽內尚有未固化之讀音素材」）。

```swift
public var hasFuriousFrontPending: Bool {
  switch typingMode {
  case .pinyinFuriousTyping: return !composer.romajiBuffer.isEmpty
  case .zhuyinFuriousTyping: return !composer.isEmpty
  default: return false
  }
}
```

**連帶效果（須逐一驗證，見 §八 Phase 255 之驗收）**：

| 項 | 處置 |
|---|---|
| `isFuriousCopilotCandidateWindowVisible`（`SessionCoreProtocol.swift:196–199`） | **不需改**——其定義已是 `state.type == .ofInputting && state.isCandidateContainer && hasFuriousFrontPending`，閘一改即通 |
| 其餘 5 個 `hasFuriousFrontPending` 讀取點（`Typewriter_BPMFFullMatch.swift:122`（Shift＋選字鍵就地選字）、`:136`（Enter 固化）；`InputHandler_TriageInput.swift:35`（固化後之空格消費）、`:49`（Tab）；`InputHandler_HandleStates.swift:271`（就地確認）、`:813`（標點前固化）） | **皆為所欲**：注音狂打悉數沿用，無一需改 |
| `unfinishedReading`（`InputSession_Delegates.swift:204–208`） | **須改**：其現行實作取 `inputHandler?.composer.romajiBuffer`（拼音專屬），注音下恆空。改為依 `typingMode` 分流——拼音回 `romajiBuffer`，注音回 `composer.getComposition(isHanyuPinyin: false)`（當前未完成音節之注音原字串）。**此即 copilot 窗頂部 pane 之資料源**，亦是縮寫打法逐鍵可見之保證 |
| `CtlCandidateProtocol.unfinishedReading`（`:38`）之協定形狀 | **不動**（本來就是 `String?`） |
| `MockSession.unfinishedReading`（`Tests/…/MockedInputHandlerAndStates.swift:127–135`） | **須同步改**（其註解已自陳「與生產端 `InputSession_Delegates` 對應」）；測試須釘住注音下之回傳值 |
| tooltip 回顯（`HandleStates.swift:466–469`：`result.tooltip = composer.romajiBuffer`） | **不動**。該行有 `furiousContext != nil \|\| (furiousContext == nil && furiousAbbreviatedCells != nil)` 之前提，注音不滿足（`furiousAbbreviatedCells` 是拼音簡拼；且注音之讀音已在組字區讀音欄）⇒ 自然不觸發 |
| 組字區讀音欄（`readingForDisplay` → `inlineReadingPreview`） | **不動**。`InputHandler_CoreProtocol.swift:613` 之 `guard !prefs.cassetteEnabled, !composer.isPinyinMode` 本即為注音準備了正確路徑 |

> **與初稿之淨差異**：`hasFuriousFrontPending` 由「注音恆 `false`」改為「注音 ＝ `!composer.isEmpty`」，並因此多出兩項實作（`unfinishedReading` 之分流、mock 之同步）與一項新測試。**代價小、收益是整個單聲母狂打能力**。

---

## 四、Tekkon 側之 API 設計

### 4.1 為何需要新 API

`Composer` 現有之公開表面（實查，`Tekkon_SyllableComposer.swift`）足以回答「當前槽內容是什麼」（`value`／`getComposition()`）、「可不可以唸」（`isPronounceable`）、「可否查詢」（`phonabetKeyForQuery`），**但不足以回答**：

- 「`ㄅㄧ` 是否為某合法讀音之前綴？」（§3.2 條件 ④；**此為單聲母狂打之唯一判準**——`ㄍㄋ` 非前綴 ⇒ 提交 `ㄍ`，見 §3.0.2）
- 「`ㄅㄧ` 本身是否已是完整讀音？」
- 「以 `ㄅㄧ` 開頭之合法讀音有哪些？」（供前綴之後綴展開。**注音狂打之 copilot 窗已定案要開**（§3.5），但**不**由此列舉驅動——驅動它的是組字器之既有跨鍵詞查詢（如 `ㄍ-ㄋ-ㄋ`），故本項仍非本輪之必需）

且既有之 `MandarinParser.allPossibleReadings`（`Tekkon_Phonabets.swift:85–103`）**不可**用於此：其對注音排列回傳 **2562** 條字串，是「427 讀音詞幹 × 6 種聲調後綴」之乘積，**每條皆帶聲調後綴**，故對「`ㄅㄧ` 是否為前綴」之 `hasPrefix` 判定會產生大量偽陽性（`ㄅㄧㄢˊ` 以 `ㄅㄧ` 開頭，但 `ㄅㄧˊ` 亦然，而使用者敲的是無調之 `ㄅㄧ`）。**且該集合之唯一呼叫者是 `PinyinTrie` 之建構子**（`Tekkon_PinyinTrie.swift:24`）——為注音排列建 `PinyinTrie` 是無意義的（其 trie 恆為空，`mapZhuyinPinyin == nil`）。

### 4.2 資料規模（實測）

以 `Tekkon.mapHanyuPinyin`（`Tekkon_Constants.swift:249`，**427** 條）之 value 為注音詞幹，逐一展開其全部非空前綴：

| 量 | 值 |
|---|---|
| 拼音條目數 | 427 |
| 相異注音詞幹數 | **427** |
| 相異非空前綴數 | **442** |
| 其中「本身即完整讀音」 | **427** |
| 其中「嚴格前綴（不完整但合法）」 | **15** |
| 全部前綴字串之 UTF-8 位元組數 | 約 **3,069** |
| 詞幹長度分佈 | 1 字：24；2 字：227；3 字：176 |
| 最長詞幹 | 3 個注音符號（如 `ㄔㄨㄤ`、`ㄐㄩㄥ`） |

**15 條嚴格前綴之全表**：`ㄅ ㄆ ㄇ ㄈ ㄈㄧ ㄉ ㄊ ㄋ ㄌ ㄍ ㄎ ㄎㄧ ㄏ ㄐ ㄒ`。
（皆為聲母；`ㄈㄧ`／`ㄎㄧ` 之所以成為嚴格前綴，是因 `ㄈㄧㄠ`／`ㄎㄧㄡ`／`ㄎㄧㄤ` 這幾個音節無對應之完整詞幹。**此 15 條即「打了半截之注音」之全部可能**。）

> **註**：實測另有一條交叉證據——動態排列測試資料內之相異無調詞幹為 **439** 條（`TestAssets_Tekkon/Tekkon_TestData.swift` 之 1485 行）。439 ＞ 427 之差（12 條）係該表納入若干「無獨立完整詞幹、僅以聲母形出現」之音節（如 `ㄔ`、`ㄕ`、`ㄗ`…之單獨形式）所致。**施工者於 Phase 252 須以二者之對稱差集為準，決定 `SyllableIndex` 之建構來源**：本文主張**以 `mapHanyuPinyin` 之 value 為唯一來源**（因其為引擎既有之正本、且 `allPossibleReadings` 亦以它為正本），並**另立一則測試**斷言「動態排列測試資料內之全部無調詞幹皆為 `SyllableIndex` 之成員或其前綴」——如此則二者之落差被**釘成可觀測之事實**，而非隱形漂移。

**單符號讀音之處置（★ 依 §3.0 之新證據修訂）**：`SyllableIndex` 之**語意定義為「多數派之漢語音節」**（427 條詞幹 ＋ 15 條嚴格前綴 ＝ **442**），故 `isComplete("ㄍ") == false`（`ㄍ` 非獨立音節，僅是 `ㄍㄚ` 一族之嚴格前綴）。**但原廠辭典確實收錄 21 個單聲母與 16 個單韻母之讀音鍵**（§3.0.1 實查），且 `ㄍ` 恰在 15 條嚴格前綴之列 ⇒ `isPrefix("ㄍ") == true`、`isPrefix("ㄋ") == true`。

**故 `SyllableIndex` 之用途界定為**：只服務 §3.2 條件 ④ 那**一問**——「此串是否還可能延伸成合法讀音」。**它不負責「此串在辭典內有無詞條」**，那由 `assembler` 之查詢鏈（`currentLM.lxQuerier.hasGrams(for:)`）回答，兩者職責分明、互不替代。

**兩項由此而來的施工紅線**：

| # | 紅線 | 理由 |
|---|---|---|
| 1 | **不得**把 `SyllableIndex.isComplete(_:)` 當作「可否提交」之依據 | 否則單聲母狂打全滅（§3.0 之初稿錯誤即源於此）。「可否提交」之依據是 §3.2 之三條件 ＋ 第四問（**其第四問對單符號前綴為假** ⇒ 得提交） |
| 2 | **禁止**為了涵蓋單符號而把 37 個單符號硬塞進 `SyllableIndex.allReadings` | 那會使 `isComplete("ㄍ")` 為真，進而讓 §3.2 條件 ④ 對 `ㄍ` 之外推失真；且會使「427」這個可稽核數字失去意義。單符號之合法性是**辭典之事實**，不是**音節表之事實** |

### 4.3 建議之 API 形狀

**新增型別**：`Tekkon.SyllableIndex`（`public struct`，`Sendable`），置於**新檔** `Sources/Tekkon/Tekkon_SyllableIndex.swift`。

```swift
extension Tekkon {
  /// 注音／拼音音節之唯讀前綴索引。
  ///
  /// 由 `Tekkon.mapHanyuPinyin` 之 427 條注音詞幹派生（含其全部非空前綴，共 442 條）。
  /// **僅為查詢結構，不含任何排列、會話或偏好狀態**——排列相關之判定一律留在 `Composer`。
  public struct SyllableIndex: Sendable {
    public static func shared(for parser: MandarinParser) -> SyllableIndex

    /// 該字串是否為某合法讀音之完整形式。
    public func isComplete(_ reading: String) -> Bool
    /// 該字串是否為某合法讀音之非空前綴（含其本身即完整者）。
    public func isPrefix(_ reading: String) -> Bool
    /// 以該字串為前綴之全部完整讀音（升冪，內容穩定）。
    public func completions(of prefix: String) -> [String]

    /// 全部完整讀音（427 條；升冪）。供測試與防漂移比對。
    public static var allReadings: [String] { get }
  }
}
```

**設計要點**：

| # | 要點 | 理由 |
|---|---|---|
| 1 | **無狀態、與排列無關** | 427 條詞幹對**所有**排列相同（注音是排列中立之表記）。以 `parser` 為參數是為了**保留未來之擴充位**（若某排列真有專屬讀音集，屆時不必改簽名）；實作上所有排列共用同一份索引。 |
| 2 | **`completions(of:)` 為升冪、內容穩定** | 沿用 `PinyinTrie.zhuyinReadings` 之既有紀律（`:291`：`Array(Set(expanded)).sorted()`），以保證測試可斷言。 |
| 3 | **共用作法照 `PinyinTrie.shared(parser:)`** | 同一模式：`NSLock` ＋ `nonisolated(unsafe) private static var` 快取（`Tekkon_PinyinTrie.swift:83–110`），並提供 `clearSharedCache()` 供測試。**不新增第二種快取範式。** |
| 4 | **索引本體用 `Set<String>`，不用 Trie** | 442 條字串、查詢只有「成員資格」與「前綴列舉」兩種；`Set` 之 O(1) 成員查詢勝過 Trie 之逐字元走訪，且無自訂資料結構之維護成本。`completions(of:)` 以 `allReadings.filter { $0.hasPrefix(prefix) }` 實作（427 條線性掃描，**非熱路徑**——只在前綴不完整時才需列舉）。 |
| 5 | **不觸碰 `PinyinTrie`、不觸碰 `Composer`** | 純新增檔；`Tekkon_SyllableComposer.swift` 於 Phase 252 **零改動**（唯一例外見 §4.4）。 |

### 4.4 `Composer` 側唯一需新增者：一個唯讀探針

§3.2 之最終判準需要「本鍵譯得之目標槽位」。`Composer.translate(key:)` 是 `internal mutating`（`:601`），且會**就地修改槽位**（`handleETen26` 等會呼叫 `receiveKey(fromPhonabet:)` 與 `fixValue`），故不可由 `LibVanguard` 直接呼叫。

**建議新增**（`Composer` 之 `public` 擴充，純唯讀）：

```swift
extension Tekkon.Composer {
  /// 本鍵若被接收，將寫入之槽位型別；`nil` 表該鍵非本排列之可用鍵。
  ///
  /// 以值語義之副本試跑 `receiveKey` 後比對前後槽位得出，**不改動自身**。
  public func incomingPhoneType(forKey key: String) -> Tekkon.PhoneType?
}
```

實作即以 `var probe = self; probe.receiveKey(fromString: key)` 後比對四槽之變化（`PhoneType` 已是現成之枚舉，`Composer` 是 `@frozen struct`，複製成本極低）。

**替代方案（施工者可擇一，須於 Phase 252 記錄理由）**：不新增探針，改由 Handler 直接以值語義副本試跑整個候選流程。**本文不主張此案**，因它把 Tekkon 內之槽位語義洩漏到 Handler 內。

### 4.5 明確**不**做者（本輪）

| # | 不做 | 理由 |
|---|---|---|
| 1 | 動態注音排列之「讀音 → 按鍵序列」反向表 | 引擎內不存在；唯一真相在測試資料內。建成正式表即等於**把測試資料升格為規格**，而該資料是**既有行為之錄影**、非規格（§五.1、§五.2） |
| 2 | 動態注音排列之「當前可敲哪些鍵」查詢 | 需要「正向 key → phonabet」之**純函式**化，而 `handleETen26`／`handleHsu` 等**不是純函式**（它們依賴並改寫整個槽狀態、且有 `receiveKey` 之副作用）。真要提供，唯一不失真之方式是**逐鍵模擬**（§五.4） |
| 3 | 把 `translate(key:)` 拆成「純翻譯」與「副作用」兩段 | 表面上很誘人（可望一次解決 #2），但五支 handler 之語意**本即**與槽狀態交纏（此為動態排列之定義），硬拆會在 handler 內製造出「半套狀態」之新概念。風險與收益不成比例 |
| 4 | 把 442 條前綴索引升格為 Trie | 見 §五.3 |

---

## 五、事主存疑之答覆：動態注音「窮舉成 Trie」是否值得

### 5.1 現況事實（實查）

| 事實 | 數據 | 出處 |
|---|---|---|
| 動態注音排列之數目 | 5（`.ofDachen26`／`.ofETen26`／`.ofHsu`／`.ofStarlight`／`.ofAlvinLiu`） | `Tekkon_Phonabets.swift:51–71` |
| 讀音 ↔ 按鍵對照之**引擎內** API | **不存在**（正向為程序式解碼；反向無） | `Tekkon_SyllableComposer.swift:601–629`；`grep` 全倉零命中的反向表 |
| 逐鍵解碼之熱路徑 | `translate(key:)` 於**每次注音按鍵**執行；`inputValidityCheck(charStr:)` 至少每鍵一次 | `:246`；`Typewriter_BPMFFullMatch.swift:251` |
| 唯一之全量對照 | 測試資料 `TestAssets_Tekkon/Tekkon_TestData.swift`：**1485** 行 × 5 排列；扣除 59 個 `` `NULL `` 單元後**已斷言 7366 筆** | 該檔 `:5–1492`；`TekkonTests_Arrangements.swift:218–246` |
| 該表之相異無調詞幹 | **439** | 本文實測 |
| 該表之（情境無關之）相異按鍵序列 | **5888** 條、19658 字元、**6072** 相異前綴 | 本文實測 |
| 若為單一排列之按鍵序列建 Trie，節點數 | Dachen26 **1620**、ETen26 **1551**、Hsu **1557**、Starlight **1550**、AlvinLiu **1553** | 本文實測 |
| 該表是否為規格 | **否**。其為既有行為之錄影；且**59 個 `` `NULL `` 單元**明文承認「某些讀音在某些排列下打不出來」 | `TekkonTests_Arrangements.swift:107` |

### 5.2 為何「窮舉成 Trie」之正面價值有限

**① 需要的問題只有兩個，而它們不需要 Trie。** 注音狂打實際要問的只有「這串注音符號是不是某讀音之前綴」（§3.2 條件 ④）與「它本身是否已完整」。前者以 `Set<String>` 之成員查詢即可 O(1) 回答；後者亦然。**Trie 的獨門本事是「列舉下一步」**——而在 §4.5 #2 未實作之前，無人要問這個問題。

**② 真正的那個 Trie 不可能是靜態的。** 若真要做「當前可敲哪些鍵」，其真相來源是**五支依賴槽狀態之 handler**，不是五份 key→phonabet 的靜態表（後者明文「未包含全部的映射內容」）。要以靜態 Trie 覆蓋，唯一的辦法是**逐鍵模擬既有 `Composer` 走遍所有路徑**——這在技術上完全可行（見 §5.4），但它產出的是**實作之導出物**，而非一份可獨立審閱之規格。

**③ 於是維護成本是雙份。** 一旦該 Trie 成為正式資產，任何 `handleETen26`／`handleHsu`／`commonFixWhenHandlingDynamicArrangeInputs` 之修改都**必須**連帶重新生成並複驗該 Trie；而「生成器忘了跑」是本倉屢見之失效模式（`assets/userdef-metadata.json` 與 `assets/settings-surface.json` 皆為同型之生成物，皆須靠 Makefile 之 `cmp` 擋漂移）。**在沒有任何消費者之前，先引入一個需要漂移守衛之生成物，是純負債。**

**④ 而它會把「測試資料」錯升為「規格」。** `Tekkon_TestData.swift` 是**錄影**：它記錄的是「某日之實作在這 1485 個讀音上給出什麼按鍵序列」。若把它 tokenize 成 Trie 並讓生產碼查詢之，則該錄影內**任何既有瑕疵**都會被固化為規格，且日後修 handler 反而會「弄壞規格」。此與本倉「測試不得反向定義生產行為」之精神相悖。

### 5.3 那麼，取代方案是什麼

| 需求 | 本案之答覆 | 成本 |
|---|---|---|
| 「打了半截之注音是否可能成音」 | `SyllableIndex.isPrefix(_:)`（442 條） | 約 3 KB 字串 ＋ 一個 `Set` |
| 「它是否已完整」 | `SyllableIndex.isComplete(_:)` | 同上 |
| 「以它開頭之讀音有哪些」 | `SyllableIndex.completions(of:)`（線性掃描 427 條，非熱路徑） | 同上 |
| 「動態排列下，下一步可敲哪些鍵」 | **本輪不做**；若日後要做，採 §5.4 | — |
| 「現行 5 個排列之 7366 筆編碼是否仍正確」 | **既有測試已足**（`testDynamicKeyLayouts` ＋ `testDynamicLayoutsCorpus`）。本案**不動**它，僅另加一則**對稱性斷言**（§4.2 註） | 一則測試 |

### 5.4 若日後真要做「動態鍵盤之可敲鍵集」：建議路徑（本輪不實作）

**原則**：**由既有 `Composer` 模擬派生（simulation-derived）**，而非另立對照表；**且置於 `LibVanguard` 而非 Tekkon**。

```
演算法（草案）：
  輸入：當前 Composer 狀態 c、排列 p
  輸出：[(key, resultingPhoneType)] 之集合
  步驟：
    1. for key in p 之全部可敲鍵（≈ 40–45 個；由既有 11 份鍵盤表之鍵集聯集得出）：
    2.   var probe = c; guard probe.receiveKey(fromString: key) else { continue }
    3.   若 probe 之槽內容通過「合法性」檢查（SyllableIndex.isPrefix）則收錄
    4. 去重、排序
```

**為何置於 `LibVanguard`**：此查詢之消費者必然是 UI／FSM（動態鍵盤顯示、狂打之合法性提示），而 `Tekkon` 之既有紀律是「不知曉會話與偏好」。且此函式只用到 `Composer` 之 public 介面（`receiveKey` 之 `@discardableResult Bool` ＋ 四槽 ＋ `getComposition()`），不需 Tekkon 讓步任何邊界。

**量化**：每鍵一次複製 ＋ 一次 `receiveKey`；單次查詢 ≈ 40 次此等操作。若此查詢只在「鍵盤佈局重繪」時呼叫（而非每鍵），成本完全可忽略。**故「是否值得」之判準不是算力，而是「有沒有消費者」**——目前沒有。

### 5.5 一句話結論（供事主覆核）

> **不必為動態注音建 Trie。** 狂打所需者是一個 442 條之前綴集合（約 3 KB、零維護）；Trie 的獨門本事（列舉下一步）在沒有「動態鍵盤高亮／限制可敲鍵」這個消費者之前是空轉，而它一旦成為正式資產，就會把一份**錄影式測試資料**升格為**規格**，並替 `handleETen26` 一類高度情境相依之程式碼添上第二份必須同步的真相。**故 Tekkon 不承擔此職能**；日後若真有消費者，正確的做法是「以既有 `Composer` 模擬派生」而非「建表」，且該派生程式碼應落在 `LibVanguard`。

---

## 六、偏好層之設計

### 6.1 `UserDef` 之變更

**現況**（`UserDef.swift`）：

| 項 | 值 |
|---|---|
| case | `kFuriousTypingEnabled`（`:62`） |
| rawValue | `"FuriousTypingEnabled"` |
| `dataType` | `.bool(true)`（`:670`） |
| `metaData` | `:971–974`，引用 `i18n:UserDef.kFuriousTypingEnabled.{shortTitle,description}` |

**目標**：

| 項 | `…4Pinyin` | `…4Zhuyin` |
|---|---|---|
| case | `kFuriousTypingEnabled4Pinyin` | `kFuriousTypingEnabled4Zhuyin` |
| rawValue | `"FuriousTypingEnabled4Pinyin"` | `"FuriousTypingEnabled4Zhuyin"` |
| `dataType` | `.bool(true)`（**承接既有預設**） | `.bool(false)`（**新功能、預設停用**） |
| `metaData` | 沿用既有兩條 i18n 鍵（隨 case 更名） | 新增兩條 i18n 鍵 |
| 交換格式 | 不在黑名單內（可匯出匯入） | 同左 |

**命名理由**：rawValue 之 `4` 後綴為本倉既有之**分流慣例**（`KeyboardParser4Pinyin`／`KeyboardParser4Zhuyin`，`UserDef.swift:34–35`）。用同一慣例可讓「同族兩鍵」在 `Localizable.strings` 之全域排序內相鄰（實測：`…Enabled4Pinyin`／`…Enabled4Zhuyin` 排於 `…Enabled` 之後、`kHalfWidthPunctuationEnabled` 之前），亦讓 `dump-userdef-metadata` 之輸出可肉眼歸族。

**case 宣告之位置**：`UserDef.swift:62` 改為兩行（`4Pinyin` 在前、`4Zhuyin` 在後）。該 case 區塊（`:18–141`）**非**字母序，故無需重排。

### 6.2 Swift 端符號：全量更名，不留別名

`prefs.furiousTypingEnabled` 現有 **141** 處測試引用 ＋ **5** 處生產引用（`Sources/`）＋ **2** 處 `PrefMgrProtocol`／`PrefMgr_Core` 宣告；另 `SettingsUI` 2 處、`LXFacade` 1 處。

**決定：全量更名為 `furiousTypingEnabled4Pinyin`，並新增 `furiousTypingEnabled4Zhuyin`；不留 `furiousTypingEnabled` 之別名。**

| 方案 | 優 | 劣 | 裁定 |
|---|---|---|---|
| 留別名（`var furiousTypingEnabled: Bool { get { furiousTypingEnabled4Pinyin } … }`） | 改動小（約 150 處免動） | 一個 `rawValue` 是 `…4Pinyin` 之偏好卻名為 `furiousTypingEnabled`——正是本案要消滅之 disambiguation 債；且日後必有人以為它是「總開關」而寫出 `if furiousTypingEnabled` 之錯誤 | **否** |
| 全量更名 | 名實相符；`grep furiousTypingEnabled` 之結果即為完整清單 | 一次機械式大改（約 150 處，其中 141 處為測試） | **採** |

**測試之機械式更名須注意**：`InputHandlerTests_Cases1.swift` 之 137 處皆為 `testHandler.prefs.furiousTypingEnabled = …` 之**同型賦值**，故以逐字取代 `prefs.furiousTypingEnabled` → `prefs.furiousTypingEnabled4Pinyin` 即可；CJK 緊鄰變數之陷阱不適用（此處為 ASCII），但**仍須以 `git diff --stat` 覆核改動數與預期相符**。**建議落點**：Phase 253 內一次完成，並於該 phase 之驗收內跑滿 `swift test`（兩倉各自、不並行）。

### 6.3 資料遷移

**落點**：`PrefMgr_Core.swift` 之 `migrateDeprecatedSettings()`（`:516`）之**末段**（緊接既有之 `UsingHotKeyHalfWidthASCII` 段之後）。**逐字照**該段之成例（`:573–578`）：

```swift
// 遷移舊設定：狂拼 pref 更名並兩分（"FuriousTypingEnabled" → "FuriousTypingEnabled4Pinyin" ＋ 新增 "FuriousTypingEnabled4Zhuyin"）。
// 舊 key 之用戶設定值搬移至拼音側；注音側維持其出廠預設（false）——該側在舊版並不存在，無值可承。
if defaults.object(forKey: "FuriousTypingEnabled") != nil {
  furiousTypingEnabled4Pinyin = defaults.bool(forKey: "FuriousTypingEnabled")
  defaults.removeObject(forKey: "FuriousTypingEnabled")
}
```

**設計要點**：

| # | 要點 | 理由 |
|---|---|---|
| 1 | **只讀 `object(forKey:) != nil` 為閘** | 舊鍵存在即處理、處理完即刪；故冪等（§0.3 約束 2）。第二次執行時舊鍵已不存在，直接略過 |
| 2 | **不寫入注音側** | 注音側在舊版不存在，任何「推測之值」都是捏造。其 `.bool(false)` 之出廠預設由 `@AppProperty` 之 self-register 機制處理（`SwiftFoundationImpl.swift:199–205`） |
| 3 | **以 `defaults.bool(forKey:)` 讀值** | 照既有段之寫法；`bool(forKey:)` 對非布林之型別會回傳 `false`，但因 `object(forKey:) != nil` 已先確認存在，且該鍵在舊版恆為布林（`dataType` 為 `.bool`），故無風險 |
| 4 | **經 `PrefMgr` 之型別化屬性寫入**（`furiousTypingEnabled4Pinyin = …`）而非 `defaults.set(_:forKey:)` | 照既有段之成例；且能觸發 `@AppProperty` 之 setter（本鍵無 `didSet`，但一致性更重要） |
| 5 | **遷移碼使用 `UserDefaults.standard`** | 該函式既有之首行即 `let defaults = UserDefaults.standard`（`:517`），故與測試 suite 脫鉤。**此為既有行為，本案不改變**——但須於 Phase 253 之驗收內，以「直接對 `UserDefaults.standard` 佈置舊鍵、再呼叫 `fixOddPreferencesCore()`」之**獨立測試**驗證遷移（不可依賴測試 suite） |

**附帶之風險與緩解**：

| 風險 | 影響 | 緩解 |
|---|---|---|
| 使用者從未改過該鍵（＝從未於兩處寫入過 `FuriousTypingEnabled`） | **無值可遷**（`object(forKey:) == nil`），新鍵由 `@AppProperty` 註冊為 `true` | 無事。**此為絕大多數使用者之情形**——因 `@AppProperty` 之 init 會把預設值寫入，故實際上幾乎所有使用者**都**有該鍵。此時遷移即為「把 `true` 搬過去」，結果相同 |
| 使用者曾關掉狂拼（值為 `false`） | 遷移後拼音側為 `false`，行為不變 | 正確 |
| 使用者之系統上同時跑著舊版與新版之 IME | 舊版會把新鍵視為未知鍵（不影響 IME 運作，僅 `UserDef` 匯出時少一項） | 已知、可接受 |
| **匯入外部舊配置包** | 含 `"FuriousTypingEnabled"` 之配置包將以 `"Unknown key"` **整包失敗** | 見 §6.4 |

### 6.4 交換格式之破壞性（本系列之**已知代價**，須讓事主知悉）

`UserDef.exportAsJSON()`／`importFromDictionary(_:)` 以 `rawValue` 為鍵（`UserDef.swift:271, 285`），而**未知鍵會被拒**（`:285–288`：`reason: "Unknown key"`）。

**故**：任何在本次更名前由助手（或使用者手改）產生、含 `"FuriousTypingEnabled"` 之配置包，**在新版上會匯入失敗**。

**三種處置（本文主張第三種）**：

| 案 | 內容 | 評價 |
|---|---|---|
| 甲 | 不動，任其失敗 | 代價明確但使用者體驗差；且失敗訊息為 `Unknown key`，使用者無從得知「跑一次新版就好了」 |
| 乙 | 於 `importFromDictionary` 內加一張「舊鍵 → 新鍵」之別名表 | **違反本倉對「LLM 式向後相容 shim」之既有紀律**（`migrateDeprecatedSettings` 之模式是「一次性搬移」，不是常駐別名）；且會讓交換格式之鍵空間永久帶著歷史債 |
| **丙** | **於 `migrateDeprecatedSettings()` 內「先遷移、後匯入」**——因匯入路徑必然先經 `reconcileAfterExternalPrefsImport()` → `fixOddPreferencesCore()`，而遷移段會把**磁碟上**之舊鍵搬走。但**配置包檔案內**之舊鍵仍在 ⇒ 丙案**不足以解決** | **不足** |

**故最終裁定**：**採甲案**，並於 Phase 257 之 i18n 內**加強 `Unknown key` 之可讀性**（將失敗訊息改為可指出「此鍵可能在較新／較舊之版本中不存在」）——**此為本文之自動裁定，列於 §九**。理由是：本專案之配置助手（P240–P249）才剛上線，其產物尚未大規模流通；而犧牲交換格式之簡潔以換取一次性之相容，是長期的負債。

**若事主不同意**：替代方案是「在 `importFromDictionary` 之最前端加一段**一次性的鍵重寫**（僅當偵測到舊鍵時），並於 rewrite 後照常走既有驗證路徑」。此案之改動面僅一處、且與乙案之差別是「一次性重寫」而非「常駐別名」。**留待 Phase 253 施工時依事主之覆核決定。**

### 6.5 `PrefMgrProtocol` 之變更

`:93` 之 `var furiousTypingEnabled: Bool { get set }` 改為兩行：

```swift
var furiousTypingEnabled4Pinyin: Bool { get set }
var furiousTypingEnabled4Zhuyin: Bool { get set }
```

該協定為 124 行「一屬性一行」之平鋪結構（`:5` 起，無 `@MainActor` 屬性、`MainActor` 由 `Package.swift:117–118` 之 `.defaultIsolation(MainActor.self)` 供給），故新增一行無任何結構性影響。**實作者只有 `PrefMgr` 一個**（`PrefMgr_Core.swift:9`），故無需改動任何 mock。

---

## 七、語意層之設計

### 7.1 `typingMode` 之新形狀

```swift
public enum TypingMode: String, Equatable {
  case cassette
  case bopomofoKeyblock
  case pinyinKeyblock
  case pinyinFuriousTyping   // 狂拼
  case zhuyinFuriousTyping   // 狂注（新增）

  public var i18nKey4InlineModeHint: String {
    "i18n:TypingMode.i18nKey4InlineModeHint.\(rawValue)"
  }
}

extension InputHandlerProtocol {
  public var typingMode: TypingMode {
    if prefs.cassetteEnabled { return .cassette }
    let isFurious = composer.isPinyinMode
      ? prefs.furiousTypingEnabled4Pinyin
      : prefs.furiousTypingEnabled4Zhuyin
    if isFurious, !prefs.useSCPCTypingMode {
      return composer.isPinyinMode ? .pinyinFuriousTyping : .zhuyinFuriousTyping
    }
    return composer.isPinyinMode ? .pinyinKeyblock : .bopomofoKeyblock
  }
}
```

**既有行為之等價性**：拼音側之條件由 `prefs.furiousTypingEnabled` 變為 `prefs.furiousTypingEnabled4Pinyin`，而經 §6.3 之遷移後二者同值 ⇒ **既有使用者之 `typingMode` 逐值不變**。此為 Phase 255 之首要回歸斷言（既有 67 支狂拼測試即是）。

### 7.2 `isFuriousTypingModeEffective` 與 `hasFuriousFrontPending`

```swift
extension InputHandlerProtocol {
  public var isFuriousTypingModeEffective: Bool {
    currentTypingMethod == .vChewingFactory
      && (typingMode == .pinyinFuriousTyping || typingMode == .zhuyinFuriousTyping)
  }
  public var isPinyinFuriousTypingModeEffective: Bool {
    isFuriousTypingModeEffective && typingMode == .pinyinFuriousTyping
  }
  public var hasFuriousFrontPending: Bool {
    switch typingMode {
    case .pinyinFuriousTyping: return !composer.romajiBuffer.isEmpty
    case .zhuyinFuriousTyping: return !composer.isEmpty   // §3.5：注音之未完成讀音即其槽內容
    default: return false
    }
  }
}
```

**新增 `isPinyinFuriousTypingModeEffective` 之必要性**：既有 12 個讀取點之中，至少三者**必須**保持拼音專屬——

| 讀取點 | 為何必須拼音專屬 |
|---|---|
| `Typewriter_BPMFFullMatch.swift:269`（`allowsExtendedRomajiBuffer = …`） | 該旗子只對 `romajiBuffer` 有意義；注音側若設為 `true` 則 `romajiBuffer`（恆空）無影響，但語意上不該設 |
| `Typewriter_BPMFFullMatch.swift:321`（trail 記錄） | trail 是拼音字母 blob |
| `InputHandler_CoreProtocol.swift:215`（`isPinyinFamilyTypingMode`） | 該旗子之語意就是「拼音系」（`:209–213` 之註解已明言）。**注音狂打不是拼音系** ⇒ 鍵盤佈局翻譯**必須**照常執行（注音要美規鍵盤翻譯！） |

**紅線**：`isPinyinFamilyTypingMode` 之語意**不得**因本案而放寬。若在 Phase 255 之施工中發現 `isFuriousTypingModeEffective` 之某讀取點對注音也該為真，**逐點改用 `isFuriousTypingModeEffective`**，而非把 `isPinyinFamilyTypingMode` 改成 `isFuriousTypingModeEffective`。

**`hasFuriousFrontPending` 於注音側之語意變更之漣漪（須逐點複驗）**：初稿訂為 `false`、現訂為 `!composer.isEmpty`（§3.5）。此一改動使注音狂打**進入** copilot 窗體系，故 Phase 255 須逐點確認那 6 個讀取點在注音下皆為所欲——特別是 `InputHandler_TriageInput.swift:35` 之「固化後消費空格」與 `:49` 之 Tab：二者在注音下會先固化當前音節再續行，正是狂打所欲；而 `Typewriter_BPMFFullMatch.swift:122` 之 Shift＋選字鍵就地選字，於注音下亦應成立（該窗顯示的是組字器之候選）。

### 7.3 自動切音節之落點

**新增**（`Typewriter_BPMFFullMatch.swift` 內，與 `performPinyinAutoChopIfNeeded` 並列）：

```swift
/// 注音狂打：本鍵是否應先把當前音節固化進組字器。
/// - Returns: 已固化則 `true`；不應固化則 `nil`（呼叫方照常把按鍵送入注拼槽）。
private func performZhuyinAutoChopIfNeeded(
  inputText: String,
  prefs: some PrefMgrProtocol,
  session: Session
) -> Bool?
```

呼叫點：`consumeReadingInputIfNeeded` 內 `receiveKey` 之**正前方**，與 `performPinyinAutoChopIfNeeded` 同一位置（`Typewriter_BPMFFullMatch.swift:255–269`），以 `switch handler.typingMode` 分流。

**固化之實際動作**：以 `phonabetKeyForQuery(pronounceableOnly: true)` 取當前讀音鍵 → `assembler.insertKey(...)`（照 `composeReadingIfReady` 之既有寫法，`:407`）→ `composer.clear()` → 續行本鍵之接收。**不觸碰 trail、不做重切分。**

**POM 自動套用之處置**：拼音側之 `performPinyinAutoChopIfNeeded` 於每次自動 chop 後會呼叫 `handler.retrievePOMSuggestions(apply: true)`（`:334`），使感知覆寫／n-gram 記憶能立即回饋。注音側**建議一併照做**（同一語意：每次自動提交後重取 POM 建議），但**須列為 Phase 255 之實測項**——若發現它與呼叫 `composeReadingIfReady` 之既有 POM 路徑重複，則以不重複者為準。

**`phonabetKeyForQuery(pronounceableOnly:)` 之參數**：注音側應傳 `true`（`isPronounceable` ＝ 聲／介／韻任一非空），**不可**傳 `false`——後者對空槽亦可能回傳非空字串（其判定為 `!readingKey.isEmpty`，而 `ㄍ` 本身即非空）。此點於 Phase 255 須以測試釘住（`IH160` 一類）。

### 7.4 注音文抑制：**兩種狂打皆抑制**（v3 改版；事主明示）

**事主原文（v3）**：「那麼注音狂打模式還是屏蔽掉注音文吧。我敲「ㄍㄢˋ-ㄋㄧˇ-ㄋㄧㄤˊ」是能看到有「幹你娘」候選字的。」

**現況**：`LXFacade.swift:334`：`config.shouldSuppressFactoryZhuyinwenData = prefs.furiousTypingEnabled && prefs.pinyinTypingEnabled`。

**目標**：**拼音狂打與注音狂打皆抑制**。因 `LXFacade` 拿不到 `composer`（它不知曉當前打字方式），故以偏好之**析取**近似：

```swift
// 兩種狂打皆抑制注音文（v3）：
// 拼音側：狂拼開關已開 且 當前在拼音方式
// 注音側：狂注開關已開 且 當前在注音方式（＝ !pinyinTypingEnabled）
let inPinyinMode = prefs.pinyinTypingEnabled
config.shouldSuppressFactoryZhuyinwenData =
  inPinyinMode
    ? prefs.furiousTypingEnabled4Pinyin
    : prefs.furiousTypingEnabled4Zhuyin
```

**理由**：① 事主明示；② 抑制之對象是 §3.0.1 那 8 行**以注音符號字串為值**之詞條（如 `ㄍ-ㄋ-ㄋ → ㄍ`）——它們在**兩種**狂打模式下都是雜訊：拼音側因使用者不會想在拼音連續輸入時看到注音字串；注音側則因使用者要的是「狗男女」「幹你娘」一類**真詞**，而非回聲字串。**兩側之訴求一致**。

**★★ 落點之商榷（施工者必讀）**：`syncPrefs()` 只於 `InputHandler_TriageInput.swift:14` 之**每拍開頭**被呼叫，而**純打字方式切換**（熱鍵 `kUsingHotKeyPinyinZhuyinTypingSwitch`）是否會改變 `prefs.pinyinTypingEnabled`，須於 Phase 256 之施工中**逐路徑實查**：

| 情形 | `pinyinTypingEnabled` 是否改變 | 意義 |
|---|---|---|
| 使用者在設定介面改「拼音／注音打字模式」 | **會**（`PrefMgr_Core.swift:359–369` 之 `keyboardParser` setter） | 上述析取式正確 |
| 使用者按熱鍵切換（`SessionProtocol`／`InputSession_HandleEvent` 之 TIS 路徑） | **未必** | 此時 `syncPrefs()` 之輸入與實際打字方式**脫鉤** ⇒ 本式失準 |

**若發生脫鉤**，則**正解是把該旗標之賦值從 `syncPrefs()` 移到 Handler 側**——即在 `InputHandler` 每一拍（`triageInput` 之開頭，與 `syncPrefs()` 同址）依 `typingMode`／`composer.isPinyinMode` **這一手上之真值**重設：

```swift
// 落點建議（Phase 256 施工時定案）：
// 於 InputHandlerProtocol 內提供
var shouldSuppressFactoryZhuyinwenData: Bool {
  switch typingMode {
  case .pinyinFuriousTyping: return true
  case .zhuyinFuriousTyping: return true
  default: return false
  }
}
// 並在 triage 之開頭（syncPrefs() 之旁）把結果推入 currentLM 之 config。
```

**本文之傾向**：**採 Handler 側之寫法**（單一真源 ＝ `typingMode`，與 §7.1 同源），且**須以測試釘住熱鍵切換之情形**；`LXFacade.syncPrefs()` 內那一行則改為**不再推導該旗標**（或保留為 fallback 但由 Handler 覆寫）。**此為 v3 新增之施工項，列為 Phase 256 之首要工作。**

**已知之界線（沿用）**：`syncPrefs()` 於每次 `triageInput` 之開頭重算，故非熱鍵之變更會即時跟上。**前述脫鉤之查證結果須寫入 Phase 256 之記錄。**

### 7.5 `UserDef.kFuriousTypingEnabled4Zhuyin.description` 之草案（zh-Hant）

> 本開關是為了方便需要連續注音打字的使用者，亦為日後於 iOS 等觸控裝置上使用螢幕注音鍵盤之場合預作準備。僅對注音輸入（任一注音排列）生效，且與拼音側之「狂拼模式」各自獨立開關；對磁帶、逐字選字（SCPC）、內碼、漢音鍵盤符號與羅馬數字等輸入方法不適用。啟用後，連續鍵入注音符號即可組句，無需逐音節敲聲調或空格鍵確認：每當當前音節已經打完、而下一鍵屬於新音節時，該音節會自動寫入組字器。與狂拼模式不同，本模式不會刻意過濾掉注音文，亦不會以語言模型試算未完成的讀音。

（zh-Hans 照 zh-Hans-TW；en／ja 對位文案於 Phase 257 定稿。）

**文案之關鍵一句（v2 新增）**：上稿之「無需逐音節敲聲調或空格鍵確認」須在 Phase 257 之定稿內**明示單聲母可用**——例如續寫「只敲聲母亦可（如 `ㄍㄋㄋ`、`ㄋㄋ`），未完成的讀音會由選字窗即時預覽」。理由：此為本模式最不易被使用者自行發現之能力（§3.0），而它正是注音使用者最想要的那一項。

---

## 八、後續手術之 Phase 切分

### 8.0 全系列之共同紀律（每一 phase 皆適用）

| # | 紀律 | 出處 |
|---|---|---|
| 1 | **兩倉 byte-sync**：凡動 `vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard/**`（含 `Deps/`）或 `vChewing-LibVanguard/**`，**另一倉必須同輪鏡像**，範圍含 `Sources/`、`Tests/`、`Deps/`、`Package.swift`、`Package@swift-5.10.swift`、`Package@swift-6.0…6.3.swift`、`makefile`；並在回報中附 `cmp`／`diff -rq` 之**實際輸出** | `Phase217_SOP.md:56`（I2）、`:1043`（§11.2）、`:1045`（`makefile` 納入 I2） |
| 2 | 鏡像於 `make lintFormatUncommitted` **之後**複驗（SwiftLint `--fix` ＋ SwiftFormat 會改檔） | P242／P243／P244 之成例 |
| 3 | **同一時間只跑一顆 `swift test`**（兩倉不得並行） | `KnowledgeMemo4LLM.md:399` |
| 4 | SwiftPM 一律附 `--disable-sandbox`；測試一律 `--no-parallel` | `KnowledgeMemo4LLM.md:397` |
| 5 | Commit 標題照 `ModuleName // SubModuleName: Change.`，描述末行 `(Phase XXX - Task YYY)` | `KnowledgeMemo4LLM.md` §12.6 |
| 6 | 文書三件套：本卷之 phase 記錄、`DevReqsHistory.md` 一行、`KnowledgeMemo4LLM.md` 之更新 | §12.2 |
| 7 | **CI 之 macOS 側一律以本機代跑**（同環境豁免）；Linux／Windows 仍以 CI 為唯一途徑 | `KnowledgeMemo4LLM.md` §12.6 |
| **8** | **★ 每完成一個 phase，即回頭檢討本文並作必要之調整**（事主 2026-09-26 定調之節奏）——作法見 §8.0.1 | 事主指示 |

#### 8.0.1 phase 收尾之「回檢本文」程序（事主定調之節奏）

**每一 phase 完工時，除該 phase 自身之文書三件套外，尚須在**該 phase 之記錄內**完成下列三事**：

| # | 動作 | 內容 |
|---|---|---|
| 1 | **對帳** | 逐條核對本文對該 phase 之規劃與實作結果之差異。**凡本文之推論被實測推翻者，一律明列**（例：「§3.2 條件 ④ 於 Dachen26 之 X 情形失準，實測結果為…」） |
| 2 | **回寫本文** | 依差異修訂本文之**對應小節**（非只改 §八），並於文首〈修訂沿革〉追加一行 `vN（日期，Phase 2XX 完工回檢）`，扼述改了哪幾節、為什麼 |
| 3 | **重排後續** | 若差異足以影響**尚未動工**之 phase 的範圍、依賴或完成定義，則**就地重編 §八**（含編號；重編時須同步更新本文其餘小節之交叉引用、以及三件套內之引用） |

**紅線**：第 2 步不得只改「實作結果」而不動「設計依據」——本文是後續 phase 之設計依據，**留著一個已知錯誤的依據比沒有依據更危險**。

**既有之成例**：本 phase（250）自身之 v1→v2→v3 三次改版即此程序之最早演練（事主兩次覆核所促）。

### 8.1 依賴圖（重組後）

```
P251（術前驗證靶：自動切音節判準 ＋ 熱鍵推入路徑）   ← 事主明示「251 先動 Tekkon」
   │  零生產碼；產出「四個未知之答案」
   ▼
P252（Tekkon API：SyllableIndex ＋ incomingPhoneType）
   │  依賴 P251 之結論（尤其 Dachen26 覆寫案）
   ▼
P253（偏好層：兩分 ＋ 更名 ＋ 遷移）        ← 與 P251／P252 無交集，理論上可並行；
   │                                          但本系列一律循序、不得並行測試（§8.0 紀律 3）
   ▼
P254（FSM 閘門收束；行為零變動）            ← 依賴 P253（兩個偏好鍵）
   │
   ▼
P255（自動切音節；★ 功能底線：ㄍㄋㄋ 可打）  ← 依賴 P252 ＋ P254
   │
   ▼
P256（copilot 窗與 unfinishedReading 分流）  ← 依賴 P255
   │
   ▼
P257（注音文抑制之落點定案）                ← 依賴 P251 之熱鍵答案 ＋ P253 ＋ P254
   │
   ▼
P258（偏好介面 ＋ i18n ＋ 助手後設資料）    ← 依賴 P253（偏好名）＋ P256（TypingMode case）
   │
   ▼
P259（跨倉驗收 ＋ Swift 5.10 可建置性 ＋ 文書）← 依賴 P252–P258 全部
```

**九個 phase（251–259）。**

**重組之三項理由**：

| # | 變更 | 理由 |
|---|---|---|
| 1 | **插入新的 P251「術前驗證靶」** | 本文之全部斷言都來自唯讀閱讀，**未曾編譯或執行**。而事主兩次覆核所抓到之錯，**兩次都在「我從程式碼結構推導、但沒有實測」之那一類**（v1 之 copilot 窗判斷、v2 之辭典值誤讀）。故在動任何生產碼之前，先花一個 phase 把**可實測者實測掉** |
| 2 | **原 P253 之「FSM 核心」拆為 P254（閘門收束）＋ P255（自動切音節）＋ P256（copilot 窗）** | 原規劃已建議「分兩半施工」，惟仍列為同一 phase 之內部紀律。**改為三個獨立 phase**，使「行為零變動」那一半（P254）能單獨取得綠燈與單獨之回檢，風險不再與行為改動混在同一筆 commit |
| 3 | **原 P251（Tekkon）之「對稱性測試」移入 P251** | 439 vs 427 之落差是**實測問題**、非 API 問題。留在 API phase 會讓「先量再建」變成「邊建邊量」 |

### 8.2 Phase 251 — 術前驗證靶（★ 全新）

| 項 | 內容 |
|---|---|
| **目標** | **不動任何生產碼**，以測試靶回答四個未知，產出一份「驗證報告」小節（寫入本 phase 之 Reqs 記錄） |
| **落點** | 新增 `Tests/TekkonTests/TekkonTests_AutoChopPredicate.swift`（或同義檔名）；必要時於 `Tests/LibVanguardTests/` 新增一則查證用之測試；**零生產碼改動** |
| **依賴** | 無。**本 phase 不動 `Sources/` 一字**，故與 byte-sync 無關（但 `Tests/` 仍受 I2 覆蓋，須鏡像） |
| **未知一（主項）：自動切音節判準** | 取 `Tests/TekkonTests/TestAssets_Tekkon/Tekkon_TestData.swift` 之 1485 行 × 5 排列，對**每一筆合法編碼**之**每一個中途前綴**，以「值語義之 `Composer` 副本」模擬 §3.2 之三條件 ＋ 第四問，斷言：**中途不得誤切**、且**該編碼之音節邊界與判準給出之切點一致**。**本項若失敗 ⇒ §3.2 之判準須重寫，P252 之 API 形狀亦可能連帶改變** |
| **未知二：Dachen26 之 `qquu` 逐槽覆寫案** | 單獨一則測試，逐步斷言 `qquu` 之四拍中，第二拍**不得**被判為新音節（此為第四問承重最重之處） |
| **未知三：439 vs 427** | 以 Python 或 Swift 列出 `Tekkon_TestData` 之 439 條無調詞幹與 `mapHanyuPinyin` 之 427 條之**對稱差集**，將差異**逐條列出**；並斷言「439 條全部為 427 條之成員或其前綴」（或據實推翻此斷言） |
| **未知四：熱鍵推入路徑** | 追查「純打字方式切換（熱鍵 `kUsingHotKeyPinyinZhuyinTypingSwitch`）是否改動 `prefs.pinyinTypingEnabled`／`keyboardParser`」——起點：`SessionProtocol` 之 TIS 路徑、`InputSession_HandleEvent`、`InputHandler_TriageInput:14`、`InputHandler_CoreProtocol.currentKeyboardParserType:565`。**產出：一句可引用的結論 ＋ 其 `path:line` 依據** |
| **完成定義** | ① 四項未知各有明確結論（**允許結論為「判準失敗」**——那正是本 phase 之價值）；② 既有 43 支 Tekkon 測試＋全部 LibVanguard 測試**逐支照舊通過**（本 phase 只新增測試，不得使任何既有測試轉紅）；③ 兩倉 `Tests/` byte-sync 之輸出；④ **於 Reqs 記錄內寫出「驗證報告」小節**，供 P252 起直接引用 |
| **不動** | `Sources/` 之任何檔案、任何偏好、任何 i18n、任何 manifest |
| **風險** | 低（零生產碼）。**唯一之風險是「本 phase 得出顛覆性結論而需重編 §八」——那正是 §8.0.1 之回檢程序所為而設** |

### 8.3 Phase 252 — Tekkon API：注音前綴索引

| 項 | 內容 |
|---|---|
| **目標** | 交付 `Tekkon.SyllableIndex` 與 `Composer.incomingPhoneType(forKey:)`；**零行為變動** |
| **落點** | 新增 `Sources/Tekkon/Tekkon_SyllableIndex.swift`；`Sources/Tekkon/Tekkon_SyllableComposer.swift`（僅新增一個 `public` 擴充，不動既有碼）；新增 `Tests/TekkonTests/TekkonTests_SyllableIndex.swift` |
| **依賴** | **P251 之結論**——尤其未知一：若判準在 P251 被證偽，本 phase 之 API 形狀須先依新判準重訂 |
| **完成定義** | ① `SyllableIndex.allReadings.count == 427`；② `allReadings` 之全部非空前綴集合 ＝ 442 條；③ `isComplete`／`isPrefix`／`completions` 之行為測試（含 15 條嚴格前綴之全表斷言）；④ `incomingPhoneType(forKey:)` 覆蓋 **Dachen26 `qquu`** 案（P251 未知二之固化物）；⑤ 既有 43 支 Tekkon 測試**逐支照舊通過**（項數不得少於動工前）；⑥ 兩倉 byte-sync 之 `cmp`／`diff -rq` 輸出 |
| **SyllableIndex 之職責邊界** | 只答前綴一問（**不收** 37 個單符號讀音）；單符號之合法性是**辭典之事實**、非音節表之事實（§4.2 之兩條紅線） |
| **不動** | `PinyinTrie`、`Composer` 之既有成員、`MandarinParser`、任何鍵盤表、任何偏好、任何 i18n |
| **風險** | 低。已由 P251 先量後建，故本 phase 之設計已無重大未知 |

### 8.4 Phase 253 — 偏好層：兩分、更名、遷移

| 項 | 內容 |
|---|---|
| **目標** | `kFuriousTypingEnabled` → `kFuriousTypingEnabled4Pinyin` ＋ `kFuriousTypingEnabled4Zhuyin`（後者預設 `false`）；Swift 符號全量更名；`migrateDeprecatedSettings()` 內新增遷移段；**零行為變動**（§7.1 之等價性） |
| **落點** | `Sources/Shared/UserDef/UserDef.swift`（case／`dataType`／`metaData`）；`Sources/Shared/PrefMgr_Core.swift`（`@AppProperty` ×2、遷移段）；`Sources/Shared/Protocols/PrefMgrProtocol.swift`；`Sources/LexiconAssembly/LXFacade.swift:334`（僅改屬性名以維持可編譯，語意變動留待 P257）；`Sources/LibVanguard/**` 之 5 處引用；`Tests/LibVanguardTests/InputHandlerTests_Cases1.swift`（137 處）、`SessionTests_Cases5.swift`（4 處）；新增遷移測試（見下） |
| **依賴** | 無（P251／P252 未落地亦可——三者之落點互不相交） |
| **遷移測試之落點** | 建議置於 `Tests/SharedTests/`（新增一檔）。**關鍵**：因 `migrateDeprecatedSettings()` 用 `UserDefaults.standard`，測試須直接對 `.standard` 佈置／清理，**不可**依賴 `UserDefaults.unitTests` suite。測試須涵蓋：① 舊鍵為 `true` → 新拼音鍵為 `true`、舊鍵消失；② 舊鍵為 `false` → 新拼音鍵為 `false`；③ 舊鍵不存在 → 不動任何鍵；④ **冪等**：連跑兩次結果相同；⑤ 注音鍵於三種情形下皆為出廠預設 `false`；⑥ 遷移**不**影響既有之五段舊遷移 |
| **完成定義** | ① 兩倉 `swift test` 各自單獨跑、**項數不得少於動工前基線**（動工前實測：兩倉各 **592 支**——以動工當日之實測為準）；② 新增遷移測試 6 項全過；③ `UserDef.allCases.count` 由 **118 → 119**（此數字另有兩處會斷言：助手之 `tests/metadata.test.js:26` 與 `VCSharedCLI_UserDefMetadata.swift:119` 之 `assert`——**後者為 source 側 assert，會自動跟上；前者須於 P258 一併改**，故本 phase 之完成定義內**不含**助手側綠燈，僅要求「Swift 側綠燈 ＋ 助手側之漂移為**已知且已記錄**」）；④ 兩倉 byte-sync 之輸出 |
| **風險** | 中。141 處測試之機械式更名；遷移碼之冪等性與 `UserDefaults.standard` 之測試隔離。**緩解**：更名以單一 `sed` 式取代 ＋ `git diff --stat` 覆核；遷移測試獨立檔、獨立 suite |

### 8.5 Phase 254 — FSM 閘門收束（**行為零變動**）

| 項 | 內容 |
|---|---|
| **目標** | 把「狂打有效」之閘門與其 12 個讀取點，由「狂拼⇒拼音」之隱式假設解耦；新增 `TypingMode.zhuyinFuriousTyping` 之**型別與分派**，但**不使其可達**（新偏好預設 `false`） |
| **落點** | `InputHandler_TypingMode.swift`（新 case ＋ `typingMode` 新形狀）；`InputHandler_FuriousResegmentation.swift`（`isFuriousTypingModeEffective` 放寬 ＋ 新增 `isPinyinFuriousTypingModeEffective`）；`InputHandler_HandleComposition.swift`（`:27–37` 分派）；`Typewriter_BPMFFullMatch.swift` 之三處閘門逐點收束；`InputHandler_HandleStates.swift`（`:43`／`:119`）；`Session/InputSession_Delegates.swift:352` |
| **依賴** | P253（兩個偏好鍵） |
| **完成定義** | ① **既有 67 支狂拼測試逐支照舊通過**（此為「零變動」之主證）；② 新增閘門層測試（`typingMode` 五值之真值表；`isPinyinFamilyTypingMode` 於注音排列下**仍為假**）；③ 測試項數不得少於動工前基線；④ 兩倉 byte-sync 之輸出 |
| **紅線** | `InputHandler_CoreProtocol.swift:215` 之 `isPinyinFamilyTypingMode` **不得**放寬——它是鍵盤佈局翻譯之守衛，一破即注音完全打不出字（§7.2、§10.5 風險 1） |
| **為何獨立成 phase** | 因新偏好預設 `false`，`zhuyinFuriousTyping` **永不出現** ⇒ 本 phase 可**證明**其行為變動為零。把這一半單獨取得綠燈，後續 P255／P256 之行為改動才有乾淨之基準線可比對 |

### 8.6 Phase 255 — 自動切音節（★ 功能底線）

| 項 | 內容 |
|---|---|
| **目標** | 注音狂打下，當前音節於「不可能再延伸」時自動提交——**含單聲母** |
| **落點** | `Typewriter_BPMFFullMatch.swift`（新 `performZhuyinAutoChopIfNeeded`，與 `performPinyinAutoChopIfNeeded` 並列；呼叫點在 `receiveKey` 之正前方）；`Tests/LibVanguardTests/InputHandlerTests_Cases1.swift`（或新增檔）加入新測試 |
| **依賴** | P252（`SyllableIndex`）＋ P254（閘門） |
| **功能底線** | **必須能打出「ㄍㄋㄋ」並在組字器取得 `ㄍ`／`ㄋ`／`ㄋ` 三鍵**（§3.0、§0.2 ★③）。此為本 phase 之唯一不可退讓之驗收項；`IH155` 即其固化物 |
| **建議之新測試** | **IH155 縮寫打法**（逐鍵斷言三鍵入組字器、且**不得**因互搶同槽而只剩一顆）；IH156 「`ㄅㄧ` ＋ `ㄢ` ＝ `ㄅㄧㄢ`」之不被誤切（§3.2 條件 ③）；IH157 動態排列之覆寫不被誤切（`qquu` 之 Dachen26 案）；IH158 聲調鍵語義不變（含後置聲調覆寫）；IH159 SCPC 下注音狂打不生效；IH162 注音狂打之空格／Tab／Enter／標點語義；IH163 注音狂打**不**寫入 `furiousTrail`；IH164 注音狂打關閉時之行為與今日完全一致 |
| **完成定義** | ① 上列測試全過；② 既有 67 支狂拼測試照舊；③ 兩倉 byte-sync 之輸出 |
| **風險** | 中。切點判準已由 P251 實測過；本 phase 之新增風險在「呼叫點之位置」與「與既有 `composeReadingIfReady` 之交互」 |
| **實測項（留待事主）** | `ㄍㄢˋ-ㄋㄧˇ-ㄋㄧㄤˊ` → 「幹你娘」（逐字組句）、`ㄍㄡˇ-ㄋㄢˊ-ㄋㄩˇ` → 「狗男女」（整鍵詞條） |

### 8.7 Phase 256 — copilot 窗與 `unfinishedReading` 分流

| 項 | 內容 |
|---|---|
| **目標** | 為注音狂打接入 copilot 未完成讀音窗；`unfinishedReading` 依 `typingMode` 分流 |
| **落點** | `InputHandler_FuriousResegmentation.swift`（`hasFuriousFrontPending` 之注音分支 ＝ `!composer.isEmpty`）；`Session/InputSession_Delegates.swift:204–208`（`unfinishedReading` 分流）；`Tests/LibVanguardTests/TestComponents/MockedInputHandlerAndStates.swift:127–135`（mock 同步） |
| **依賴** | P255 |
| **完成定義** | ① 注音狂打且有未完成音節時 `isFuriousCopilotCandidateWindowVisible` 為真（IH161）；② 注音狂打時 `unfinishedReading` 回傳當前音節之注音字串、空槽時為 `nil`（IH160）；③ 其餘 5 個 `hasFuriousFrontPending` 讀取點於注音下皆為所欲（§3.5 之表，逐點驗）；④ 既有拼音狂拼之 `hasFuriousFrontPending` 語意不變（IH165，回歸護欄）；⑤ 兩倉 byte-sync 之輸出 |
| **風險** | 中。`hasFuriousFrontPending` 之語意變更會波及其 6 個讀取點；mock 與生產須同步，否則測試與生產行為分岔 |
| **為何與 P255 分開** | P255 交付「讀音進得了組字器」，P256 交付「讀音看得見」。二者之失效模式完全不同、可獨立歸因；合併會使診斷變難 |

### 8.8 Phase 257 — 注音文抑制之落點定案

| 項 | 內容 |
|---|---|
| **目標** | `shouldSuppressFactoryZhuyinwenData` 改為**兩種狂打皆抑制、兩種非狂打皆不抑制**；並依 **P251 未知四** 之答案決定旗標之落點 |
| **落點** | `Sources/LexiconAssembly/LXFacade.swift:334` 與 `:73–74` 之 doc comment；**若 P251 判定熱鍵不改動 `pinyinTypingEnabled`，則另需** `InputHandler_TriageInput.swift`／`InputHandler_CoreProtocol.swift` 之推入端（以 `typingMode` 為單一真源）；`Tests/LexiconAssemblyTests/LXFacade_FuriousZhuyinwenTests.swift` |
| **依賴** | **P251（未知四之答案）** ＋ P253（新偏好名）＋ P254（`typingMode` 之新值） |
| **完成定義** | ① 既有 2 支測試照舊通過；② 新增斷言：**四態**（拼音狂打／注音狂打／拼音非狂打／注音非狂打）；③ 若採 Handler 側，另加一則熱鍵切換之測試；④ 兩倉 byte-sync 之輸出 |
| **風險** | **低於原規劃**——因熱鍵那一題已於 P251 查清，本 phase 不再背著未知動工 |
| **注意** | 該測試族以 `instance.setOptions { $0.shouldSuppressFactoryZhuyinwenData = true }` **直接驅動 config**（`LXFacade_FuriousZhuyinwenTests.swift:45`），**不經偏好** ⇒ 新測試必須改走 `syncPrefs()`（或 Handler 之推入路徑），否則它驗不到本案之改動 |

### 8.9 Phase 258 — 偏好介面、i18n 與助手後設資料

| 項 | 內容 |
|---|---|
| **目標** | 兩顆開關在使用者可及之處現身；四語系文案齊備；防漂移產物重生 |
| **落點** | `Packages/vChewing_SettingsUI/Sources/SettingsUI/SettingsUI/VwrSettingsPaneBehavior.swift:104–106`（SwiftUI）；`…/SettingsCocoa/VwrSettingsPaneCocoaBehavior.swift:209–214`（AppKit 對位）；`Sources/vChewingIME_macOS/Resources/{en,ja,zh-Hans,zh-Hant}.lproj/Localizable.strings`（＋4 條 × 4 語系：兩條 `…4Zhuyin` 之新鍵、一條 `…4Pinyin` 之改名、一條 `TypingMode…zhuyinFuriousTyping` 之新鍵）；`ValueAdd/WebConfigAssistant/src/questions.ts:521`（手寫之種子鍵清單）；`ValueAdd/WebConfigAssistant/tests/metadata.test.js:26`（`count` 118 → 119）；`ValueAdd/WebConfigAssistant/assets/{userdef-metadata.json, settings-surface.json}`（重生）；`ValueAdd/WebConfigAssistant/tests/fixtures/{kimo-zhuyin,msnewphonetic-scpc,pinyin-newbie}.json`（重生） |
| **依賴** | P253（偏好名）＋ P256（新 `TypingMode` case 之 i18n 鍵） |
| **完成定義** | ① 助手 `make audit` 全綠（含 `metadata`／`metadata-audit`／`surface-check`／`fixtures-check` 四道防漂移）；② `Localizable.strings` 之四語系鍵集一致、且經 `LocalizableFileSorter.swift` 排序後逐位元組穩定；③ `SUI/Tests/SettingsUITests/AssistantContractTests.swift` 之 4 支契約測試全綠（**此即 §6.4 之舊配置包問題在測試上之現形處**）；④ 兩倉 byte-sync 之輸出（`Sources/` 之改動僅 `Shared/` 之 i18n 鍵字串，須鏡像） |
| **兩顆開關之排版（建議）** | SwiftUI 側：**同一 `Section` 內兩列**（`4Pinyin` 在上、`4Zhuyin` 在下），**不**做 UI 層之連動停用——因二者是**並行**選項、非從屬關係。AppKit 側：照 `NSStackView.buildSection` 之既有形制，兩列同一 section（`VwrSettingsPaneCocoaBehavior.swift:85–90` 之既有說明已交代為何不做連動停用） |
| **文案之關鍵一句** | 注音側之 `description` 須**明示單聲母可用**（§7.5）；且須寫明**注音文會被過濾**（P257 之行為） |
| **風險** | 中。四語系文案之語體（zh-Hans-TW）與 ja 之「狂打ち／狂拼／狂注」定譯；防漂移產物之重生順序（**須照 `Makefile` 之依賴鏈：`metadata-update` → `surface` → `fixtures`**） |

### 8.10 Phase 259 — 跨倉驗收與可建置性

| 項 | 內容 |
|---|---|
| **目標** | 全系列之收尾：跨倉逐位元組總驗、Swift 5.10 側之可建置性、文書三件套 |
| **落點** | 無生產碼改動（除本 phase 自身發現之缺漏）；`vChewing-DevLogs` 三件套；`vChewing-macOS/AGENTS.md` 若有過時敘述則一併修 |
| **依賴** | P252–P258 全部 |
| **完成定義** | ① 兩倉 `Sources/`／`Tests/`／`Deps/`／六份 manifest／`makefile` 之 `cmp`／`diff -rq`／`shasum` 逐項輸出，且**零差異**（僅 `.DS_Store`）；② 兩倉 `swift test` 各自單獨跑、全綠、項數與動工前基線之**同框對照**；③ `make build510`（逐套件）與可及之 legacy 路徑之可建置性（**注意**：`Tekkon` 之 5.10 側為 static archive，新增檔須自動納入；`Package@swift-5.10.swift` 之 `Tekkon` 靶若列舉檔案則須同步——**實查：本倉 manifest 以目錄為單位、不逐檔列舉**，故無需改 manifest）；④ 助手 `make audit` 全綠；⑤ 文書：本卷之各 phase 記錄（252–259 各自寫入其所屬卷，251 亦然）、`DevReqsHistory.md` 逐 phase 一行、`KnowledgeMemo4LLM.md` 之更新；⑥ 若 P255／P256 之行為於實機上有未及之情形，於本 phase 記錄為「已知界線」而非強行修補 |

**卷之歸屬**：`Reqs_0241-0250.md` 於本 phase（250）之後即達 10 個 Phase（241–250）之滿卷條件 ⇒ **Phase 252 起寫入後繼之新卷**。依〈Reqs4LLM 分卷歸檔註記〉之現算紀律，新卷為 `Reqs_0251-0260.md`，其落點目錄仍為 `Archive_P201-P300/`（該百位段未滿 100 個 Phase，故仍續收）。

---

## 九、自動裁定記錄（事主已授權「先自動落實最優解」）

> 事主原文：「你在規劃完畢之後如有需要我親自裁示的事情的話，你可以先自動落實你的最優解。我信任你對唯音輸入法這個產品的全局理解能力。」

| # | 事項 | 本文之裁定 | 若事主不同意之替代 |
|---|---|---|---|
| 1 | 注音側之簡稱 | **「狂注」**（ja「狂注」） | 改「狂打注音」一類；惟 `shortTitle` 會與總稱撞名 |
| 2 | ja 之「狂打ち」字形 | 漢字＋送假名（`狂打ち`） | 全漢字「狂打」 |
| 3 | en 之 `TypingMode` 提示值 | `Furious Pinyin Typing`（原為 `Furious Typing`，因總稱讓位） | 保留 `Furious Typing` |
| 4 | ~~注音狂打是否開 copilot 未完成讀音窗~~ | **【已作廢——事主 2026-09-26 之異議】** 初稿裁定「不開」係基於「注音不需要猜測」之判斷，而該判斷漏掉了**單聲母縮寫打法**（§3.0）。**現行裁定：要開**；`hasFuriousFrontPending` 對注音 ＝ `!composer.isEmpty`（§3.5） | —（已改版，無替代案） |
| 5 | 動態鍵盤可敲鍵集 | **本輪不做**；日後若做，以模擬派生且置於 `LibVanguard`（§5.4） | 逕行實作於 Tekkon 內 |
| 5b | `SyllableIndex` 是否收錄 37 個單符號讀音 | **不收**。其語意為「多數派漢語音節」（427 ＋ 15 嚴格前綴 ＝ 442）；單符號之合法性是**辭典之事實**、由 `assembler` 之查詢鏈回答（§4.2 之兩條施工紅線） | 併入 `allReadings` 成 479 條；惟此舉會使「427」失去可稽核性、且令條件 ④ 之外推失真 |
| 5c | 單聲母狂打之提交是否需先問辭典 | **不問**。§3.2 之判準純由結構 ＋ `SyllableIndex` 決定；提交後若辭典無詞條，`composeReadingIfReady` 之既有錯誤路徑自會處置（`B49C0979`） | 提交前先 `hasGrams` 探測；惟該查詢在熱路徑上，且會使「注音不收簡拼」之界線模糊 |
| 6 | 舊配置包之相容 | **不**加別名，採甲案（§6.4）；改為加強 `Unknown key` 之訊息 | 於匯入端加一次性鍵重寫 |
| 7 | 兩顆開關之排版 | 同一 Section 之兩列、不做連動停用（§8.6） | 各一 Section |
| 7b | 注音文抑制之旗標落點 | 傾向**由 `LXFacade.syncPrefs()` 移到 Handler 側**（以 `typingMode` 為單一真源）；**但此依 §7.4 之熱鍵查證結果而定**——若實查確認熱鍵切換會改動 `pinyinTypingEnabled`，則留在 `syncPrefs()` 即可 | 維持 `syncPrefs()` 之析取式（近似法） |
| 8 | 遷移失敗之處置 | **不**回滾、**不**補償；舊鍵處理完即刪 | — |
| 9 | 新 `UserDef` case 之插入位置 | `:62` 原位改兩行（`4Pinyin` 先、`4Zhuyin` 後） | 併入 `KeyboardParser4*` 一族 |

---

## 十、驗證要求

### 10.1 Swift 側單元測試

| 層 | 測什麼 | 落在 |
|---|---|---|
| Tekkon | `SyllableIndex` 之三問 ＋ 442 條之集合斷言 ＋ 15 條嚴格前綴全表 ＋ 439 vs 427 之對稱性 | P252 |
| Shared | `migrateDeprecatedSettings()` 之六項（含冪等） | P253 |
| LibVanguard | 既有 67 支狂拼回歸 ＋ 新 IH155–IH164 | P255 |
| LexiconAssembly | 注音文抑制：**兩種狂打皆抑制、兩種非狂打皆不抑制**（四態）＋（若採 Handler 側）熱鍵切換 | P256 |
| SettingsUI | 助手 4 支契約測試 ＋ 既有 `PrefsExchange` 群 | P257 |

### 10.2 助手側（TypeScript）

`make audit` ＝ `typecheck` ＋ `es5` ＋ `test`（78 支）＋ `metadata` ＋ `metadata-audit` ＋ `surface-check` ＋ `version-check` ＋ `fixtures-check`。**本系列會動到其中五道**（鍵集變動 ⇒ `metadata`／`metadata-audit`／`surface-check`／`fixtures-check` 之輸入變動；`count` 斷言變動）。**重生順序須照 `Makefile` 之依賴：`metadata-update` → `surface` → `fixtures`。**

### 10.3 兩倉 byte-sync（每一 phase 之硬性驗收）

```bash
A=vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard
B=vChewing-LibVanguard
diff -rq -x '.build' -x 'Build' -x '.DS_Store' -x '.git' "$A/Sources" "$B/Sources"
diff -rq -x '.build' -x 'Build' -x '.DS_Store' -x '.git' "$A/Tests"   "$B/Tests"
diff -rq -x Build -x '.DS_Store' -x '.build' "$A/Deps" "$B/Deps"
for f in Package.swift Package@swift-5.10.swift Package@swift-6.0.swift \
         Package@swift-6.1.swift Package@swift-6.2.swift Package@swift-6.3.swift makefile; do
  cmp "$A/$f" "$B/$f"
done
```

**動工前基線（本 phase 實測，2026-09-26）**：`Sources/` 各 **125** 檔、`Tests/` 各 **76** 檔，`diff -rq` 與 `shasum -a 256` **零差異**；`Deps/` 各 12 檔零差異；七份固定檔之 SHA-256 兩兩相同。**唯一之差異是 `.DS_Store` 之類未追蹤噪聲。**

### 10.4 實機實測項（須事主）

| 項 | 為何須人眼 |
|---|---|
| **完整讀音之兩例**：`ㄍㄢˋ-ㄋㄧˇ-ㄋㄧㄤˊ` → 應見「幹你娘」（逐字組句）；`ㄍㄡˇ-ㄋㄢˊ-ㄋㄩˇ` → 應見「狗男女」（整鍵詞條）——★ 本案之首選實測項 | 需真人連續輸入；且須**與注音文抑制一併驗**（v3） |
| **縮寫打法**（`ㄍㄋㄋ`、`ㄋㄋ`、`ㄓㄓ`、`ㄔㄔ`…）之實際手感 | 需真人連續輸入。**注意**：v3 起注音文已被抑制，故縮寫打法之候選將**不再**含 `ㄍ`／`ㄋ` 一類回聲字串——**須確認剩下的候選仍有用**（此即 v3 方針之成敗所在） |
| 注音狂打之一般手感（自動切音節是否符合直覺、有無誤切） | 需真人連續輸入 |
| 注音狂打於**動態排列**（ETen26／Hsu／Starlight／AlvinLiu／Dachen26）下之表現 | 五種排列各有獨門特例 |
| 兩顆開關於設定介面之排版與文案 | 目視 |
| **預設值之實際效果**：既有使用者升級後，拼音狂拼行為應完全如舊；注音側應為關閉 | 需真機驗 |

### 10.5 風險與緩解（總表）

| # | 風險 | 等級 | 緩解 |
|---|---|---|---|
| 1 | `isFuriousTypingModeEffective` 之 12 個讀取點收束不完全，導致注音打字路徑被誤判為拼音系 ⇒ 鍵盤佈局翻譯被跳過 ⇒ 注音打不出字 | **高** | P255 分兩半施工（先閘門、後行為）；`isPinyinFamilyTypingMode` 列為紅線；IH156／IH157 為關鍵回歸 |
| 2 | 自動切音節於動態排列之覆寫語意下誤切 | 中 | §3.2 之三條件 ＋ 第四問（`SyllableIndex.isPrefix` 之否定）＋ IH157 |
| 2b | **單聲母狂打打不出來**（初稿之實際缺陷，事主已指出） | **高（已於本案解除）** | §3.2 條件 ④ 之 `isPrefix` 判準使 `ㄍ`／`ㄋ` 得被提交；`IH155` 為其固化物。**施工者不得以「當前內容須為完整音節」為提交前提** |
| 2c | 注音狂打接入 copilot 窗後，`unfinishedReading` 分流未同步 mock ⇒ 測試與生產行為分岔 | 中 | §3.5 之表已列明須同步 `MockSession.unfinishedReading`；`IH160` 之斷言須在**真** `InputSession` 與 **mock** 兩處皆成立 |
| 3 | 遷移碼不冪等 ⇒ 每次 `activateServer()` 都改寫偏好 | 中 | 以 `object(forKey:) != nil` 為閘 ＋ 處理完即 `removeObject` ＋ 連跑兩次之測試 |
| 4 | 141 處測試之機械式更名漏改或誤改 | 中 | 單一取代樣式 ＋ `git diff --stat` 覆核 ＋ 兩倉各跑滿測試 |
| 5 | 助手之防漂移四道未同步重生 | 中 | 照 `Makefile` 依賴鏈重生；`make audit` 全綠為 P257 之完成定義 |
| 6 | 兩倉 byte-sync 於 `make lintFormatUncommitted` 之後失守 | 中 | §8.0 紀律 1／2；每一 phase 附實際輸出 |
| 7 | 427 vs 439 之落差被誤當 bug 而擴大範圍 | 低 | P252 之對稱性測試將其釘為事實 |
| 8 | 舊配置包之 `Unknown key` 失敗 | 低 | §6.4 之已知代價 ＋ §九 #6 之裁定 |

---

## 十一、未決事項（留待事主或後續 phase）

| # | 事項 | 何時需要定案 |
|---|---|---|
| 1 | 舊配置包是否採「匯入端一次性鍵重寫」（§6.4 之替代案） | P253 施工中 |
| 2 | ~~注音狂打是否要開 copilot 未完成讀音窗~~ | **已定案：要開**（事主 2026-09-26 異議；§3.0、§3.5）。此項自未決清單移除 |
| 3 | 「動態鍵盤之可敲鍵集」是否有真實消費者（§5.4） | 無時程。**若 iOS 版之螢幕鍵盤要做「動態注音鍵盤高亮／限制」，此即其前置** |
| 4 | `kUsingHotKeyPinyinZhuyinTypingSwitch` 熱鍵切換時，兩顆狂打開關之互動是否需進一步細化 | P255 實測後 |
| 5 | iOS 移植之整體規劃（本案僅為其前置之一） | 另立 phase |
| 6 | **是否於 `vChewing-VanguardLexicon` 之 8 行注音文正本內補一條 `幹你娘` ↔ `ㄍ-ㄋ-ㄋ` 之對照** | 無時程。**該倉係另一倉、本系列不動之**；惟此為「讓事主之例如願顯示漢字」之最直接手段（§3.0.1）。若採，須同步重生辭典產物並於該倉另立 phase |
| 7 | 單聲母狂打之提交是否應加「辭典無詞條則不提交」之保護（§九 #5c 之替代案） | P255 實測後——若觀察到單聲母提交後常態落進 `B49C0979` 之錯誤路徑，則須回頭補此保護 |
| 8 | **「純打字方式切換（熱鍵）是否改變 `prefs.pinyinTypingEnabled`」**（§7.4） | **P256 之首要工作**——其答案決定抑制旗標之落點 |

---

## 附錄 A：本 phase（250）之實作結果

### A.1 落地

**改 4 檔**（皆為文書，**零生產碼**）：

| 檔 | 改動 |
|---|---|
| `vChewing-DevLogs/Research/Phase250-ResearchAndNextSurgeryPlan.md` | **新檔**（本文） |
| `vChewing-DevLogs/Reqs4LLM/Archive_P201-P300/Reqs_0241-0250.md` | 新增 `# Phase 250` 記錄（本文之摘要與其落點索引） |
| `vChewing-DevLogs/DevReqsHistory.md` | 追加 Phase 250 一列 |
| `vChewing-DevLogs/KnowledgeMemo4LLM.md` | `最後更新` 改 2026-09-26；文首新增「狂打模式之注音化：規劃已定案」一則，摘記五則後續施工必須遵守之事實 |

**同 phase 內之修訂（v2）**：上表四檔於同日經一次改版（事主對 copilot 窗之異議，見文首〈修訂沿革〉）。**未新增任何檔案、未新增任何生產碼**——改版完全落在同一批文書內。**唯一新增之生產碼路徑為規劃性質**（`unfinishedReading` 之分流），其實作仍屬 Phase 255。

**未動**：`vChewing-macOS` 之任何檔案、`vChewing-LibVanguard` 之任何檔案、助手之任何資產、任何 CI、任何 `Package*.swift`。

### A.2 研究方法

四路並行之唯讀盤點，各自以「`path:line` 為證、凡未實查者標 `unverified`」為紀律：

| 路 | 範圍 | 主要產出 |
|---|---|---|
| A | `UserDef`／`PrefMgr`／`PrefMgrProtocol` 之全表面 ＋ 全倉引用點 ＋ i18n ＋ SettingsUI ＋ 會壞之測試 | §六、§1.3 |
| B | 狂拼執行期管線（triage／auto-chop／segmentor／重切分／候選／顯示）＋ 27 條 romaji 專屬 vs 21 條音素中立之對照表 ＋ 66 支狂打相關測試 | §二、§3.4 |
| C | Tekkon 全模組（公開表面、音素模型、動態排列、`PinyinTrie`、43 支測試、熱路徑、快取）＋ 測試資料之量化 | §四、§五 |
| D | 兩倉 byte-sync 之範圍與現況、權威條文、歷史成例、遷移前例、CI 事實 | §8.0、§10.3 |

**方法學要點**：C 路與本文另以 Python 直接解析 `Tekkon_Constants.swift` 之 `mapHanyuPinyin` 字面與 `Tekkon_TestData.swift` 之測試表，獨立算出 §4.2 與 §5.1 之全部數字（427／442／15／3,069 bytes／1485／439／7366／5888／6072／各排列之 Trie 節點數）。**故 §五之結論建立在可複算之量化上，非印象。**

### A.3 本 phase 之關鍵查得（施工者勿重複踩）

1. **`InputHandler_HandleComposition.swift:27–37` 已把注音與拼音派給同一個 `BPMFFullMatchTypewriter`** ⇒ 注音狂打**不需要**新 typewriter。此為本案工作量估計之樞紐。
2. **`InputHandler_CoreProtocol.swift:611–617` 之 `inlineReadingPreview` 本即為注音準備了正確路徑**（`:613` 之 `guard !prefs.cassetteEnabled, !composer.isPinyinMode`）⇒ 注音狂打之讀音顯示**泰半免費**。
3. **`InputHandler_CoreProtocol.swift:215` 之 `isPinyinFamilyTypingMode` 恆等於 `isComposerUsingPinyin`**（其註解 `:209–213` 已自陳此點，並說明該命名是為了「避免鍵盤佈局翻譯等外部條件依賴『狂拼是否拼音』的隱式假設」）。**此事實使 P255 之風險具體化**：一旦 `isFuriousTypingModeEffective` 對注音為真，若施工者順手把 `:215` 改成它，注音之鍵盤佈局翻譯即被跳過。**此為本案點名之最大陷阱。**
4. **`FuriousTypingSegmentor` 之兩個生產建構點**（`InputHandler_FuriousResegmentation.swift:379–389`、`:452–462`）之注入閉包**逐字相同** ⇒ 若日後真要為注音做重切分（本案不做），那兩處即為落點。
5. **`migrateDeprecatedSettings()` 用 `UserDefaults.standard` 而 `@AppProperty` 用 `UserDefaults.current`**（僅測試時二者才分岔）⇒ 遷移碼之測試**必須**走 `.standard`，否則測不到。
6. **★ 生產辭典內，21 個聲母與 16 個單韻母／介母全部都是合法讀音鍵**（各一條「以自身為值」之詞條，權重 `-8.863`，如 `ㄍ → ㄍ`），另有 **85** 條「各段皆為單一注音符號」之多音節鍵（如 `ㄍ-ㄋ-ㄋ → ㄍ`、`ㄋ-ㄋ → ㄋㄟㄋㄟ`）——**其值皆為「回聲字串」**。上游正本 `vChewing-VanguardLexicon/…/data-zhuyinwen.txt` **全檔 8 行**（權重一律 `-9.6`；型別 `EntryType.zhuyinwen` ＝ §7.4 抑制旗標所過濾者）：`ㄅㄧㄤ`／`ㄅㄧㄤˋ`／`ㄉㄨㄤ`／`ㄋㄟ`／`ㄋㄟㄋㄟ`×2／`ㄎㄧㄤ`／`ㄍㄋㄋ`。**此為 P255「縮寫打法」之技術根據。**
7. **★ 事主所舉之兩個候選各有其真源、且互不相同**（v3 複查）：**「狗男女」**來自**完整讀音鍵** `ㄍㄡˇ-ㄋㄢˊ-ㄋㄩˇ`（權重 `-6.649`，該鍵之唯一條目）——而拼音之 `gnn` 正是靠 `PinyinTrie` 之前綴展開還原出該三桶才看得到它；**「幹你娘」**在原廠辭典內**零命中**，來自**逐字語言模型組句**（`ㄍㄢˋ` −5.206 ＋ `ㄋㄧˇ` −5.075 ＋ `ㄋㄧㄤˊ` −5.257；`ㄍㄢˋ` 起首之鍵有 72 條，而 `ㄍㄢˋ-ㄋ` 起首者 **0 條**）或使用者自有詞庫。**故事主所見之對比（拼音 `gnn` 見「狗男女」而不見「幹你娘」）即此二源之差異**（後者受 P155 所述之笛卡爾積防禦所抑）。**意涵：注音狂打之 copilot 窗之所以更強，正因它不必做那層前綴展開。**
8. **`hasFuriousFrontPending` 於注音側之語意，初稿訂為 `false` 是錯的**——它使注音狂打被排除在 copilot 窗體系之外，連帶使單聲母縮寫打法**完全不可用**（三顆聲母互搶同一個槽）。**本 phase 之規劃書已依事主異議改版**（§3.0、§3.5）；施工者若在任何處見到「注音不開 copilot 窗」之文字，一律以 §3.5 為準。
9. **`UserDef.allCases.count == 118` 這個數字被三處硬寫**：`VCSharedCLI_UserDefMetadata.swift:119` 之 `assert`（source 側，自動跟上）、助手 `tests/metadata.test.js:26` 之 `assert.strictEqual(metadata.count, 118)`（**須手改**）、以及助手之 `assets/userdef-metadata.json` 之 `count`（重生時自動跟上）。本案將使其成為 **119**。

### A.4 未驗／已知界線

| 項 | 說明 |
|---|---|
| 注音狂打之**實機手感** | 無法於本 phase 驗（無實作）。此為 P255 之後之事主驗收項 |
| 五種動態排列下之自動切音節是否全部正確 | 本文之判準（§3.2）係由程式碼結構推導，**未**逐排列窮舉驗證其正確性。P255 須以 IH157 一類測試覆蓋至少 Dachen26 與 ETen26（覆寫語意最強者） |
| 「`ㄅㄧ` ＋ `ㄢ`」之猜測是否符合使用者直覺 | 本文主張「不切、續接為 `ㄅㄧㄢ`」（§3.2）。此與拼音狂拼之 greedy 語義一致，但**注音使用者之直覺可能不同**。列為事主實測項 |
| `DevReqsHistory.md`／`KnowledgeMemo4LLM.md` 之更新 | **已執行**（即時補記，未延後） |
| 官網／`UserGuide` | 本案不動（功能尚未存在） |
