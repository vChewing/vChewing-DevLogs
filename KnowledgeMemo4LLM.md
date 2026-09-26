# vChewing & LibVanguard 工作區 - 格物致知專用文件

- 本文檔供 AI Agent 在每次開工前迅速了解專案全貌。
- **FeatureRequest（FR）目錄註記**：`vChewing-DevLogs/PendingFeatureReqs/` 存放 FeatureRequest 類 PreResearch 文件（現含 `PendingApproval/` 之 `FR608-PreResearch-v1a.md`／`-v1b.md`／`-v2.md`）。該目錄**僅在被要求處理時才處理**——除非事主明確指示，否則不得主動動工、不納入任何 Phase 排程、不預先分析其內容。
- **Reqs4LLM 分卷歸檔註記**：`vChewing-DevLogs/Reqs4LLM/` 之下，分卷以「至多 10 個 Phase」為單位。**現行卷一律現算、不以硬寫之檔名記載**：取 `Reqs4LLM/Archive_P*/` 之下、檔名匹配 `Reqs_0NN1-0NN0.md` 者之**標號最大**的一卷，其內 `^# Phase ` 標題數**未達 10** 者即為現行卷（含 0 個 Phase 之空卷）；若該末卷已滿 10 個 Phase、或經事主裁定結案，則現行卷為其後繼一卷（`Reqs_0(NN+1)1-0(NN+1)0.md`，尚未建立者於其所屬百位段目錄新建之）。現算之兩道手續：`ls -1 vChewing-DevLogs/Reqs4LLM/Archive_P*/Reqs_[0-9]*.md | sort | tail -1` 取末卷、`grep -c '^# Phase ' <末卷>` 數其 Phase 數。`vChewing-DevLogs/Reqs4LLM/Reqs_Other_Pending_Phases.md` 為不隨分卷歸檔的待定事項暫存。卷之所在目錄一律取「該卷首 Phase 所屬之百位段」：`Archive_P{百位段下界}-P{百位段上界}/`（如首 Phase 231 ⇒ `Archive_P201-P300/`；目錄不存在即新建）。故卷之落點與歸檔位置皆由卷名自身決定、無須回改本註記；既有三桶為 `Archive_P001-P100/`、`Archive_P101-P200/`、`Archive_P201-P300/`。**（archive 桶的「凍結」僅指該百位段的 100 個 Phase 已收齊；未滿 100 個 Phase 者只稱「已歸檔」、仍會續收後續結案的分卷——現下的 `Archive_P201-P300/` 即屬此態。）已滿或已結案的歸檔卷不再增改，新 Phase 之記錄一律寫入現行卷；惟對過往 Phase 之補記不在此限——無論該卷是否已歸檔，補記一律補進那個 Phase 自己的記錄內，不得佔用其他 Phase（含現行卷）的記錄空間。** 本文件群內所有路徑一律以**工作區根**為錨（`vChewing-DevLogs/…`、`vChewing-LibVanguard/…`、`vChewing-macOS/…` 等）。
- **授權註記**：本倉庫自身內容以 **LGPL-3.0-or-later** 授權，詳見 `COPYING` 與 `LICENSES/preferred/LGPL-3.0-or-later`。倉內**引用**的程式碼／資料仍依其來源授權、不受本倉庫授權影響（`vChewing-LibVanguard` LGPL-3.0-or-later〔附 Swift 靜態連結例外〕、`vChewing-macOS`／`vChewing-OSX-Legacy`（自 2026-09-13 起，**閉包以外之一切自研內容已換軌為 `MulanPSL-2.0`**，兩倉自此不再有 MIT-NTL；**以 `LibVanguard`（原 `OSNeutralAssembly`）為終末點之 8 個 SPM package 則為 LGPL-3.0-or-later**——`LibVanguard`／`LexiconAssembly`〔內含 `TrieKit`；`TrieKit` 係套件與 target 名，與本倉 `Sources/` 的 `LX_` 檔名前綴無關〕／`Homa`／`Shared`／`Tekkon`／`BrailleSputnik`／`BPMFVS`／`SwiftExtension`〔惟 `SwiftExtension` 為 `MulanPSL-2.0`〕；其遞移相依閉包以外者一律為 `MulanPSL-2.0`）、`vChewing-VanguardLexicon` `MulanPSL-2.0`、`vChewing-Homebrew` AGPL-3.0，另有 Megrez／ButKo BPMFVS／KeyKey／McBopomofo 等第三方片段）。清單見 `README.md`。
- 最後更新：2026-09-26 // 這一行只寫日期，不用贅述 DevReqHistory 裡面的那種記載格式。
- **狂打模式（Furious Typing）之注音化：規劃已定案（2026-09-26，Phase 250）**：規劃書為 `vChewing-DevLogs/Research/Phase250-ResearchAndNextSurgeryPlan.md`；後續施工自 **Phase 251** 起、共六個 phase（251 Tekkon → 252 偏好層 → 253 FSM 核心 → 254 辭典層 → 255 偏好介面與 i18n → 256 跨倉驗收）。**下列五則為後續施工必須遵守之事實，摘記於此以免重複踩坑**：① **術語三層**——總稱「狂打模式／狂打ちモード／Furious Typing」、拼音側「狂拼模式／狂拼モード／Furious Pinyin Typing」（既有稱謂**不改**）、注音側「**狂注**模式／狂注モード／Furious Zhuyin Typing」。② **`isFuriousTypingModeEffective` 之 12 處讀取點中，`InputHandler_CoreProtocol.swift:215` 之 `isPinyinFamilyTypingMode` 是鍵盤佈局翻譯之守衛，現恆等於 `isComposerUsingPinyin`；注音狂打**絕不可**把它放寬為「狂打有效」，否則注音之佈局翻譯被跳過、注音完全打不出字。③ **注音狂打不需要新的 typewriter**：`InputHandler_HandleComposition.swift:27–37` 已把 `.bopomofoKeyblock` 與拼音兩模式派給同一個 `BPMFFullMatchTypewriter`；且 `InputHandler_CoreProtocol.swift:611–617` 之 `inlineReadingPreview` 本即為注音準備了正確之讀音顯示路徑。④ **Tekkon 不承擔動態注音鍵盤之職能**：注音狂打所需者僅為「讀音前綴集合」——`mapHanyuPinyin` 之 427 條注音詞幹、其全部非空前綴僅 **442** 條、UTF-8 約 3 KB；**不建 Trie**（Trie 的獨門本事是「列舉下一步」，在沒有「動態鍵盤高亮／限制可敲鍵」這個消費者之前是空轉，且會把 `Tekkon_TestData.swift` 這份**錄影式**測試資料錯升為規格）。日後若真有消費者，正確路徑是「以既有 `Composer` 逐鍵模擬派生」且**置於 `LibVanguard`**。⑤ **偏好之兩分與遷移**：`FuriousTypingEnabled` → `FuriousTypingEnabled4Pinyin`（承接舊值、預設 `true`）＋ `FuriousTypingEnabled4Zhuyin`（**預設 `false`**）；遷移照 `PrefMgr.migrateDeprecatedSettings()` 內 `UsingHotKeyHalfWidthASCII → UsingHotKeyHalfWidthPunctuation` 之成例；**已知代價**——舊配置包（含 `"FuriousTypingEnabled"`）在新版會以 `"Unknown key"` 匯入失敗。
- **狂打模式之注音化：規劃已於同日改版（v2，2026-09-26，事主覆核後）**——事主原文：「我有個異議：竊以為注音的狂打模式還是需要 copilot 視窗的，比如打「ㄍㄋㄋ」可以預覽到「幹你娘」。」經實查生產辭典，v1 之設計有**功能缺口**：**單聲母縮寫打法（`ㄍㄋㄋ`、`ㄋㄋ`…）在 v1 下完全打不出來**（三顆聲母互搶同一個注音槽）。**v2 之三則要點（後續施工一律以此為準）**：① **注音狂打要開 copilot 窗**——`hasFuriousFrontPending` 對注音 ＝ `!composer.isEmpty`（與拼音之 `!romajiBuffer.isEmpty` 同構），並連帶須改 `unfinishedReading`（`InputSession_Delegates.swift:204–208`）為依 `typingMode` 分流、同步 `MockSession` 之對位實作；② **自動切音節之判準為三條件**（注拼槽非空／目標槽位 ≠ 聲調／目標槽位 ≤ 已填之最高槽位）**外加第四問**——「當前內容 ∪ 本鍵譯得之注音」**不**構成任何合法讀音之前綴（`SyllableIndex.isPrefix` 之否定）；**該第四問之否定即為提交之充分條件**，故 `ㄍ` 於敲下 `ㄋ` 時得被提交。**絕不可**把提交前提寫成「當前內容已為完整音節」；③ `SyllableIndex` 只答前綴一問（427 條詞幹 ＋ 15 條嚴格前綴 ＝ **442**），**不收** 37 個單符號讀音——**單符號之合法性是辭典之事實**：實查生產辭典，**21 個聲母與 16 個單韻母／介母全部**是合法讀音鍵（各有一條「以自身為值」之詞條），另有 **85** 條「各段皆為單一注音符號」之多音節鍵、**其中 `ㄍ-ㄋ-ㄋ` 之值即字串 `ㄍㄋㄋ`**；其上游正本 `vChewing-VanguardLexicon/.../data-zhuyinwen.txt` **全檔僅 8 行**，而 `幹你娘` 在整個生產辭典內**零命中**。故「打 `ㄍㄋㄋ` 會預覽到 `幹你娘`」在現行資料下**不成立**，會預覽到 `ㄍㄋㄋ` 本身；要顯示漢字須靠使用者辭典／POM，或於該上游倉補一條對照（另一倉、本系列不動）。
- **狂打模式之注音化：v3 方針（2026-09-26，事主修訂其 v2 舉例後；施工一律以此為準）**——事主原文：「修訂一下我剛才的說法：竊以為注音的狂打模式還是需要 copilot 視窗的，比如打「ㄍㄋㄋ」可以預覽到「幹你娘」「狗男女」。那麼注音狂打模式還是屏蔽掉注音文吧。我敲「ㄍㄢˋ-ㄋㄧˇ-ㄋㄧㄤˊ」是能看到有「幹你娘」候選字的。拼音的話可能因為 cartesian product 溢出等原因，敲 gnn 看不到「幹你娘」但能看到「狗男女」。」**實查之三則事實（生產辭典 `VanguardFactoryDict4Typing.txtMap`）**：① 單聲母（`ㄅ`…`ㄙ`，21 個）與單韻母／介母（16 個）**全部**是合法讀音鍵，其詞條為「以自身為值」之回聲（權重 `-8.863`）；另有 85 條「各段皆為單一注音符號」之多音節鍵（如 `ㄍ-ㄋ-ㄋ → ㄍ`）；② **「狗男女」之真源是完整讀音鍵 `ㄍㄡˇ-ㄋㄢˊ-ㄋㄩˇ`（−6.649）**，拼音之 `gnn` 靠 `PinyinTrie` 前綴展開才看得到它；③ **「幹你娘」在原廠辭典內零命中**，其真源是**逐字語言模型組句**（`ㄍㄢˋ` −5.206／`ㄋㄧˇ` −5.075／`ㄋㄧㄤˊ` −5.257 皆為強勢單字；`ㄍㄢˋ` 起首之鍵 72 條、`ㄍㄢˋ-ㄋ` 起首者 0 條），拼音側因笛卡爾積防禦（P155）而看不到。**v3 之兩項施工指令**：① **注音狂打亦須抑制注音文**（原 v2 為「僅拼音抑制」）——抑制對象即上游 `vChewing-VanguardLexicon/.../data-zhuyinwen.txt` 那 **8 行**（`EntryType.zhuyinwen`；值皆為注音符號字串）；② **`shouldSuppressFactoryZhuyinwenData` 之賦值落點須商榷**——`LXFacade.syncPrefs()` 只於每拍開頭被呼叫，而**純打字方式切換（熱鍵 `kUsingHotKeyPinyinZhuyinTypingSwitch`）是否改動 `prefs.pinyinTypingEnabled` 尚待實查**；若否，須改採 Handler 側之寫法（以 `typingMode` 為單一真源）。**Phase 254 之首要工作即此查證**。
- **狂打模式之注音化：手術編號已重組為九個 phase，並定調「每 phase 收尾回檢本文」之節奏（v4，2026-09-26，事主指示）**——事主原文：「那你按照你認為合理的手術順序重組 phase 編號（Phase 251 開始的編號）。之後的建議手術節奏是這樣：每完成一個 phase 之後都檢討 Phase 250 做出你認為的必要調整。」**九個 phase（251–259）之排序與依賴**：**251 術前驗證靶**（零生產碼；答四問：自動切音節判準對 1485×5 全部中途前綴是否不誤切、Dachen26 `qquu` 案、439 vs 427 逐條差集、熱鍵是否改動 `pinyinTypingEnabled`）→ **252 Tekkon API**（`SyllableIndex` ＋ `incomingPhoneType(forKey:)`，依 251 之結論）→ **253 偏好層**（兩分／更名／遷移）→ **254 FSM 閘門收束**（**行為零變動**，因新偏好預設 `false` 故 `zhuyinFuriousTyping` 不可達）→ **255 自動切音節**（★ 功能底線：必須打出「ㄍㄋㄋ」併入組字器）→ **256 copilot 窗與 `unfinishedReading` 分流** → **257 注音文抑制之落點定案**（依 251 之熱鍵答案）→ **258 偏好介面與 i18n** → **259 跨倉驗收**。**節奏之可執行化（規劃書 §8.0.1，每一 phase 收尾必做）**：① **對帳**（逐條核對規劃與實作之差異，凡推論被實測推翻者一律明列）→ ② **回寫本文**（修訂對應小節、並於規劃書〈修訂沿革〉追加 `vN（日期，Phase 2XX 完工回檢）`）→ ③ **重排後續**（若差異影響未動工之 phase，就地重編 §八含編號與全部交叉引用）。**紅線：不得只改「實作結果」而不動「設計依據」——留著一個已知錯誤的依據比沒有依據更危險。**
- AI Agent 得特別注意本文所提到的「Response Pattern」。
- **倉庫現狀（2026-09-17，vChewing **4.8.0** 發版）**：`vChewing-OSX-Legacy`（Aqua 紀念版）**已封存、不再更新**——legacy 發行版（支援自 macOS 10.9 起）之建置自此**唯由 `vChewing-macOS` 之 legacy targets 承擔**（`debugLegacy`／`releaseLegacy`／`archiveLegacy`／`cleanLegacy`，見 §10.5.2）。封存倉**仍保留為 10.9-compliant 的 API 寫法參照**（AppKit availability 有疑者照它），但**不再接收任何回寫／同步**；**該倉不在本工作區內**（`/Users/shikisuen/Repos/_vChewing/` 之下不存在，亦不得假設其存在）——故凡遇「legacy 側是否尚未 commit／是否需同步／兩倉或三倉之落點是否齊備」一類斷言，一律以「自 4.8.0 起 legacy 不再接收回寫，此類斷言僅為 4.8.0 以前之歷史事實」結案，**勿以「無法驗證」留白**；本文檔與 `DevReqsHistory.md` 中凡「三倉同步」「legacy 倉逐檔同構」一類記述，一律視為 4.8.0 以前之歷史事實。
- **命名沿革（2026-09-13，Phase 201~204 ＋ 同日第二輪 ＋ Phase 205）**：本文檔在此日期之前的所有條目，所出現的 `Typewriter`／`LangModelAssembly`／`LMAssembly`／`LMInstantiator`／`LMI`／`LMMgr`／`LookupHub`／`lmi`／`lookupHub`／`lm*`（小寫家族）／`LMPlainBPMF`／`LangModel`／`langModel`／`TestLM` 等名稱，係各該階段當時的實際名稱，**依歷史記載原則原樣保留、不予改寫**。更名結果：兩倉（`vChewing-macOS`／`vChewing-OSX-legacy`）的 `OSNeutralAssembly`／`LexiconAssembly`／`LXAssembly`／`LXFacade`／`LXMgr`／`LXQuerier`／`lxQuerier`／`lx*`，對應目錄亦已同步（`Packages/vChewing_OSNeutralAssembly`、`Packages/vChewing_LexiconAssembly`、`Shared/vChewingComponents/OSNeutralAssembly`、`Shared/vChewingComponents/LXAssembly`、`LangModelManager/` → `LXManager/`）；另 `Shared.InputMode.langModel` → `.lexicon`、`LangModelCache` → `LexiconCache`、`resetLangModelCache` → `resetLexiconCache`、`initUserLangModels()` → `initUserLexicons()`、`targetLangModels` → `targetLexicons`，測試靶的 `TestLM` 族 → `TestLX` 族（`mockLM` → `mockLX`、`strLMSampleData*` → `strLXSampleData*` 等）。**本倉**的 `Lexicon.LMPlainBPMF` → `Lexicon.LXPlainBPMF`（檔名 `LX_LXPlainBPMF.swift`）、`lmPlainBPMFData` → `lxPlainBPMFData`、`HomaTests_Basic.swift` 的測試局部變數 `langModel` → `lexicon`。本倉程式碼除此與 3 處文字引用外零改動。詳見 `vChewing-DevLogs/Reqs4LLM/Archive_P201-P300/Reqs_0201-0210.md`。
- **命名沿革（2026-09-14 第二輪，Phase 214）**：`OSNeutralAssembly` → `LibVanguard`（**套件名、module 名、target 名、測試靶名、其目錄名，以及 macOS 的套件目錄名**）。範圍含兩倉（`vChewing-LibVanguard` 與 `vChewing-macOS`）之 import／`@testable import`／`@_exported import`、註解與 doc comment、`UserDefaults` suite 名、macOS 11 個 consumer manifest 的 product 名（改 `Vanguard`）、`plugin.swift` 的 bundle 名排除集、CI 檔名與 job 名、`Makefile` 目標名、以及兩倉的 README／EVOLUTION_MEMO／AGENTS／CLAUDE／algorithm／copilot-instructions／DevLab 散文。**macOS 套件目錄亦一併正名**（事主同日補佈置）：`Packages/vChewing_OSNeutralAssembly` → `Packages/vChewing_OSNeutral_LibVanguard`，故 11 個 consumer manifest 的 `.package(path:)` 與 `.product(…, package: "vChewing_OSNeutral_LibVanguard")`（SwiftPM 對本地路徑相依之 identity 取自目錄名）、3 處 CI `--package-path`、`Makefile` 2 處、`project.pbxproj` 2 處與全部文件路徑同步；但該目錄**內部**的 `Sources/OSNeutralAssembly/`、`Tests/OSNeutralAssemblyTests/` 已改名為 `LibVanguard/`、`LibVanguardTests/`。兩倉 `Package.swift` 自此**逐位元組相同**（並改用 `@resultBuilder` 的 ArrayBuilder DSL），兩倉 `Sources/` 內容**全等**、`Tests/` 僅差本倉獨有的 2 個搶救測檔。另含一項檔名殘端：聚合靶的 umbrella 檔 `OSNeutralAssemblySPM.swift` → `LibVanguardSPM.swift`（兩倉）——檔名不入 manifest，byte-identity 檢查與編譯都不會發現它，須靠「殘留的 `OSNeutralAssembly*` 建置產物」反查。
- **刻意保留、勿於後續命名清剿中更動（事主 2026-09-13 裁定）**：`ButKo_BPMFVS` 這個 **SwiftPM 套件**已更名為 `vChewing_BPMFVS`（macOS `Packages/vChewing_BPMFVS`），但以下一律**不動**——① `ButKo_BPMFVS_Accessors.swift` 檔名（macOS `Sources/BPMFVS/` 與 legacy `Shared/3rdParty/` 各一份；事主明示故意保留，legacy `project.pbxproj` 有 4 處引用）；② legacy `vChewing/Resources/ButKoBPMFVS_Assets/` 目錄（內含 ButKo 上游資產 `phonic_table_Z.txt`／`LICENSE_BPMFVS.txt`，只放第三方資產故不隨套件改名）；③ 使用者可見的**功能名**「ButKo BPMFVS」——含 4 語系 `Localizable.strings` 的 `i18n:UserDef.kReflectBPMFVSInCompositionBuffer.*`／`i18n:UserDef.kSpecifyCmdOptCtrlEnterBehavior.option.4` 文案與官網 `ReleaseNotes.md`／`Downloads.md`／`manual/preferences.md`；④ Swift 端的 `CommitableMarkupType.bpmfvsAnnotationButKo` 與測試函式名 `test_IH103*_ButKoBPMFVS*`。另：`build_darwin_SPMTestsAndPackage.yml` 的 `packages=(...)` **刻意不收** `./Packages/vChewing_BPMFVS`（該 package 有 `Tests/BPMFVSTests`，實測 6/6 通過；事主對該套件另有後續打算）；該清單為**刻意維護之白名單**、非對 `Packages/*` 之全域掃描，故新套件（或既有套件之測試靶）不會自動被收——**2026-09-19 依事主指示補收 `./Packages/vChewing_CandidateWindow`**（Phase 231 之補記；該包有 `Tests/TDK4AppKitTests`，21 支全過）。

---

## 一、專案概述

**LibVanguard**（先鋒引擎）是 vChewing Project 下一代輸入法的引擎的核心套件庫，以 Swift Package 形式提供。專案採用 LGPL v3.0 授權（`SwiftExtension` 模組例外：自 2026-09-13 起採 `MulanPSL-2.0`，見 `LICENSES/preferred/MulanPSL-2.0` 與 `COPYING`），涵蓋從注音符號解析、辭典樹查詢、語言模型聚合、到組字引擎的完整輸入法管線（pipeline）。

- **Swift 工具版本**：**Swift 6.4+**（6.2／6.3 為封堵對象——各套件之 `Package@swift-6.2.swift`／`6.3.swift` 以 `#error` 明文拒絕該兩版，理由見 §10.5 末段）；另備 **Swift 5.10.1**（open-source toolchain）供 macOS 10.9 legacy 側建置——自 Phase 216 起本倉具雙 toolchain 建置能力、Phase 217 起**推及 `vChewing-macOS` 全倉**，建置行為隨 toolchain 版本而異（見 §十）。
- **最低平台支援**：現行側 macOS 12（**.macOS(.v12)**）——自 Phase 213 起承襲 `vChewing-macOS` 的 `LibVanguard` 設定（原為 macOS 15 / macCatalyst 18 / iOS 18 / visionOS 2，事主裁定現階段一律承襲 macOS 側）；**5.10（legacy）側之 manifest 刻意不宣告平台（`platforms: nil`）、部署目標為 `x86_64-apple-macosx10.9`**（PackageDescription 能宣告的 macOS 最低值只有 10.10，一宣告即被明文寫入產物，索性不宣告；地板由 makefile 之 `-Xswiftc -target` 與 legacy 連結端決定。早前記為「`Data` 標為 macOS 10.10 起、故 `10.9` 不存在」——該說已經重測推翻——詳見 §十）。
- **跨平台目標**：保持對 Linux 與 Windows 的可建置性（透過 `#if canImport(Darwin)` 條件編譯平台限制）。
- **出貨產物**：**（6.4+ 側）單一動態庫 `libVanguard.dylib`**（manifest 之 `package.name = "LibVanguard"` 而 product 名為 `Vanguard`）。**聚合靶與其測試靶自 2026-09-14 第二輪起亦更名**為 `LibVanguard` / `LibVanguardTests`（原 `OSNeutralAssembly` / `OSNeutralAssemblyTests`），故 `import LibVanguard`；其餘模組名（`Homa`、`TrieKit`、`LexiconAssembly` 等）不變。SwiftPM 的資源 bundle 名取**套件名**，故實為 `LibVanguard_*.bundle`。**兩倉（本倉與 `vChewing-macOS`）自此 `Package.swift` 逐位元組相同、`Sources/` 全等**。**（5.10 側，自 Phase 216 起）兩顆均為 static 之產物**：`libVanguard.a`（聚合體，14 MB）與 `libVanguardSwiftExtension.a`（子套件，540 KB）；`.a` 係純 `ar` 封存、不帶任何 load command，故 minOS 不進產物。
- **角色（事主 2026-09-14 定調）**：本倉現為**實驗田**；`vChewing-macOS` 仍消費自己的 `Packages/vChewing_OSNeutral_LibVanguard`，兩者自此是「逐位元組同源、各自獨立」的兩份副本。LibVanguard 對 macOS 的**向前建置能力**屬後續 phase（**自 Phase 216 起開始落地**：5.10／legacy 側之雙 toolchain 建置已可行，見 §10.5）。

> 該專案本身不應視為 vChewing 唯音輸入法的一部分，除非今後刻意有此安排。

---

## 二、專案架構

### 2.1 目錄結構

```
vChewing-LibVanguard/
├── Package.swift                    # SPM 套件定義（package name: LibVanguard, 出貨 product: Vanguard）
├── makefile                         # lint / format / test / dockertest 指令
├── EVOLUTION_MEMO.md                # 各模組研發備忘錄
├── README.md                        # 專案說明（含〈What Is In This Repository〉）
├── COPYING / LICENSES/              # 授權（LGPL-3.0-or-later；SwiftExtension 與 ResourceLocator 例外為 MulanPSL-2.0）
├── .github/workflows/               # CI：test_ubuntu / test_winnt / test_darwin_LibVanguard.yml
├── Sources/
│   ├── LibVanguard/                 # 作業系統中立層：輸入控制器與狀態機（動態產品 Vanguard 之聚合靶）
│   ├── LexiconAssembly/             # 辭典聚合與洞察（LXFacade / LXQuerier / LXPerceptor）
│   ├── LXAssemblyMaterials4Tests/   # 測試專用辭典素材靶（獨立於出貨動態庫之外）
│   ├── Homa/                        # 護摩組字引擎
│   ├── TrieKit/                     # 辭典樹（RAM Trie + TextMap Trie）
│   ├── Tekkon/                      # 注拼引擎（聲韻並擊）
│   ├── BrailleSputnik/              # 盲文點字轉換
│   ├── BPMFVS/                      # 注音資產與存取器（ButKo BPMFVS）
│   ├── Shared/                      # 全體共用型別與常數
│   ├── SwiftExtension/              # Swift 語言擴展（MulanPSL-2.0）
│   ├── ResourceLocator/             # 執行期資源定位（MulanPSL-2.0）
│   └── vChewingSharedCLI/           # 跨模組共享命令列工具
└── Tests/
    ├── LibVanguardTests/
    ├── LexiconAssemblyTests/        # POM 測試族之大本營
    ├── HomaTests/ + HomaSharedTestComponents/
    ├── TrieKitTests/ / TekkonTests/ / BrailleSputnikTests/ / BPMFVSTests/
    ├── SharedTests/ / SwiftExtensionTests/ / ResourceLocatorTests/
    └── (本倉獨有) LexiconAssemblyTests/POMDecayWindowTests.swift
                 LexiconAssemblyTests/LXPlainBopomofoEtenDOSTests.swift
```

> **2026-09-14（Phase 213）之佈局變更**：本倉原有之 `Sources/LibVanguard/`、`Sources/_Modules/<模組>` 與
> `Tests/_Tests4Components/<模組>Tests`、`Tests/LibVanguardTests/` 已全數退場（73 檔），改為上表之
> **聚合式佈局**——即 `vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard` 的同源複製。該表所列 12 個
> `Sources/` 子目錄與 10 個測試靶與 macOS 側逐位元組一致，唯二差異為兩處硬編碼資源 bundle 名與本倉
> 獨有的 2 個測試檔。`TrieHub`／`FactoryTrieDBType`／`LexiconHub` 三個殘骸隨舊佈局一併退場。

> **本文件所屬的 `vChewing-DevLogs` 倉庫**：開發記錄已自 LibVanguard 獨立為工作區中的 `vChewing-DevLogs` 倉庫
> （原為 LibVanguard 的 `DevPlans/`，現供整個 vChewing 組織跨倉使用）：
>
> ```
> vChewing-DevLogs/
> ├── KnowledgeMemo4LLM.md               # 本文件
> ├── DevReqsHistory.md                  # 開發階段歷史
> ├── Reqs4LLM/                          # Phase 需求文件（分卷與現行卷之判定見 §12.2）
> ├── Research/                          # 各 Phase 研究報告
> └── PendingFeatureReqs/                # FeatureRequest 類 PreResearch
> ```

### 2.2 技術架構

模組依賴關係（上層依賴下層）：

```
Vanguard (動態產品 / libVanguard.dylib) — 出貨產品之 target 清單共 10 個
└── LibVanguard (聚合靶；唯一的出貨動態庫之根)
    ├── BPMFVS ── ResourceLocator ── SwiftExtension
    ├── BrailleSputnik ── Shared ── SwiftExtension
    ├── LexiconAssembly ── TrieKit ── SwiftExtension
    │                    ├── Homa
    │                    └── Shared
    ├── Homa
    ├── ResourceLocator
    ├── Shared
    ├── SwiftExtension
    └── Tekkon

（出貨產品清單另以逐 target 列出，故上圖之邊即 `Package.swift` 內 `dependencies:` 之實際內容。）
```

**出貨產品（Products）**：`Vanguard`（`.dynamic`，targets 為 `LibVanguard`／`Shared`／`SwiftExtension`／`ResourceLocator`／`LexiconAssembly`／`TrieKit`／`Homa`／`Tekkon`／`BrailleSputnik`／`BPMFVS`）；另有 `LXAssemblyMaterials4Tests` 與 `HomaSharedTestComponents` 兩個**測試素材靶**動態產品（刻意不進出貨庫），以及 `vChewingSharedCLI` executable。

> **2026-09-14（Phase 213）後之模組集合**：本倉已無「公開／內部模組」之分——12 個 `Sources/` 子目錄即 10 個出貨 target ＋ 2 個支援 target（`LXAssemblyMaterials4Tests`、`vChewingSharedCLI`），其中 **`LibVanguard` 同時是唯一聚合靶**（SwiftPM 拒絕讓同一 target 同時被動態與靜態產品取用，故整個閉包只能以單一動態庫出貨）。舊圖（`LibVanguard` 聚合 target ＋ `Sources/_Modules/*` 六模組）已全部退場。

> **已移除模組（2026-09-13，Phase 206）**：`SharedCore`（`KBEvent` / `KeyCode` / `KBEventProtocol`）與 `CandidateKit`（`CandidateCellData`）兩模組已自本倉切除，連同其空殼測試靶。`SharedCore` 內與 FCITX 有關的相容項已遷入 `vChewing-macOS` 與 `vChewing-OSX-Legacy` 兩倉、且於 Phase 206 改掛 MIT-NTL 標頭（惟該二檔皆落在 Phase 207 的授權閉包內，故其標頭已於同日隨閉包換軌回 LGPL-3.0-or-later）；`KBEvent` / `InputSignalProtocol` 在兩倉各有獨立副本，本倉移除不影響其運作。

---

## 三、核心資料模型

| 型別 | 模組 | 用途 |
|------|------|------|
| `Homa.Gram` | Homa | 元圖單位（Unigram/Bigram），承載讀音、字詞、機率、前驗詞 |
| `Homa.Node` | Homa | 組字節點，含元圖陣列、覆寫狀態、Bigram 快取 |
| `Homa.Segment` | Homa | 字詞幅節，`[Int: Node]` 字典（鍵為幅節長度） |
| `Homa.Assembler` | Homa | 組字核心處理器，持有遊標、段落、配置、動態規劃演算法 |
| `VanguardTrie.Trie.TNode` | TrieKit | Trie 節點，含 id / readingKey / children / entries |
| `VanguardTrie.Trie.Entry` | TrieKit | Trie 詞條，含 value / typeID / probability / previous |
| `Tekkon.Phonabet` | Tekkon | 單注音符號（Unicode Scalar + PhoneType） |
| `Tekkon.Composer` | Tekkon | 音節合成器，逐字元組合注音 |
| `VanguardTrie.TrieGram` | TrieKit | 元圖資料結構（`keyArray` / `value` / `probability` / `previous` / `anterior`）。原為 5 元 tuple，已改具名 struct。**Phase 213 前**的 LibVanguard `LexiconKit` 曾以 `public typealias HomaGram = VanguardTrie.TrieGram` 引用之，該模組已退場；macOS／LibVanguard 兩倉現以 `Homa.Gram` 為組字引擎的元圖型別，另有 `Homa.Gram.init(_ trieGram:)` 橋接。 |

---

## 四、核心組件詳解

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
- **`LXAssembly.LXPerceptor`**：使用者習慣洞察器（POM），基於 Ngram 的行為追蹤、時間衰減三次曲線。原 LibVanguard 側名為 `Perceptor`。其持久化層 `LXAssembly.PerceptionPersistor` 的鎖恆為**葉鎖**——取鎖期間不得呼叫任何回呼，因為 `LXPerceptor` 會在持自有鎖時呼叫該層的 `markKeyForUpsert(_:)`／`markKeyForRemoval(_:)`，兩者互相嵌套即成取鎖順序倒置的死鎖（2026-09-17 修正，回歸斷言見 `Tests/LexiconAssemblyTests/POMLockDisciplineTests.swift`）。
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

---

## 五、已實作功能清單

- **Homa Revolver soft revolve**：`Homa.Assembler.revolveCandidate` 具 `softRevolve: Bool = false`（先以 `isCandidateSafeToSoftRevolve` 過濾安全子集）；`current` 為目標候選在**原始候選列表**中的索引。SPACE 鍵啟動的輪替一律 `softRevolve: true`，其餘入口（Tab / ContextMenu / 方向鍵 / 方括號）維持 hard。
- **`UserDef.kPreferredRevolverForceLevel`**（integer, default 2, range 0...2）：0＝一律強輪替、1＝僅 SPACE 路徑弱輪替、2（預設）＝一律弱輪替。Typewriter 各 revolve 呼叫點依 `prefs.preferredRevolverForceLevel` 決定 `softRevolve`。
- **InputHandler 的 `rotation` 改名為 `revolution`**：`InputHandler_TriageInput.swift` 的 `triageByKeyCode` 內箭頭鍵分診臨時變數 `rotation` → `revolution`。既有 API 名（含 `revolveCandidate` / `revolveTypingMethod`）不受影響。
- **Installer app bundle 舊版清除**：安裝前 `killall vChewing` / `killall vChewingPhraseEditor`；以 `InputMethodConnectionName` 掃描 `~/Library/Input Methods` 與 `/Library/Input Methods` 的 `.app`；舊版改名 `vChewing-yyyy-MM-ddTHH-mm-ss.appTrashed` 後 trash，系統層級以 `osascript` 提權 `mv`。i18n key `i18n:Installer.AdminRenameFailureNotice`。
- **SwiftUI app installer alert refactor**：`VwrAppInstaller4SwiftUI.swift` 的多個 chained `.alert(...)` 改為單一 `.alert(item: $vm.config.alertItem)`；新增 `InstallerAlertItem` 與 `AlertType.makeAlertItem(paths:)`；Cocoa 端僅 `alertItem == nil` 時才轉換 `currentAlertContent`。

- 注音符號與拼音的雙向解析與轉換（Tekkon）
- 11 種注音排列 + 6 種拼音風格支援（Tekkon）
- RAM 常駐 Trie + TextMap Trie 兩模式辭典（TrieKit）
- Vanguard Pragma TextMap 格式讀寫（TrieKit / TrieIO）：三種 VALUES 行型別（`>typeID\tencodedCell` / `@probability\tchsCell\tchtCell` / 個體行），DEFAULT_PROB 壓縮，escaped pipe grouped cell，BEL 佔位空側；RevLookup 由主 `.txtMap` 自動生成；Typing TextMap `KEY_LINE_MAP` 直接儲存 raw phonabet key（format version `1.1`）
- TextMapTrie canonical specialized backend（TrieKit）：原始 Data 常駐 + 排序後 full-key index + binary search + prefix-range scan + eager reverse lookup + entry-group fast path；穩態記憶體約為全物化 Trie 的三分之一。
- **SQLite 與 Plist 支援已全面移除**：`VanguardTrie.SQLTrie`、`VanguardTrie.TrieSQLScriptGenerator`、`TrieHighFrequencyDecoder` 與本地 `CSQLite3` 套件全刪；`VanguardTrie.TrieHub` 不再持有 `sqlTrieMap` / `plistTrieMap`（`updateTrieFromSQLFile` / `updateTrieFromSQLScript` / `updateTrieFromPlistFile` 退場）；`TrieIO` 的 plist 出入徑與 `Trie` / `TNode` / `Entry` 的 `Codable` 皆移除。**序列化僅餘 TextMap 一途**；**判死的是 plist 檔案格式，不是 `VanguardTrie.Trie` 這個 RAM 型資料結構**；`TrieIO.validate(_:)` 的根節點假設為 `0`（設回 `1` 必誤報 `isValid: false`）。
- 兩倉的 factory dictionary runtime 維持 `factoryTrie: VanguardTrie.TextMapTrie?`，不回退下游 `FactoryTextMapLexicon`；`VanguardTrieProtocol.getEntryGroups(...)` 讓 existential query fast path 成立。
- `LMInstantiator.Config` 具 `partialMatchEnabled = false`（partial-match 總控）；`LMInstantiator.lookupHub` 為唯一 canonical public lookup surface。
- Phase 36 的完整敘事，以及 P5 wrapper retirement 的準入清單與 kickoff template，見 `vChewing-DevLogs/Research/Phase036_Research.md` appendix。
- `vChewing-LibVanguard` 的 `TrieHub` TextMap path 與兩倉的 `LMInstantiator_TextMapExtension` 均已移除 TextMap backend 的 phonabet encrypt/decrypt 假設；raw phonabet key 為唯一 canonical TextMap query surface。
- 以下 A~D 四項：
   - **Phase A**：`mergedAlternativeBucketUnigrams(for:)` 的原廠辭典查詢走 `factoryChoppedUnigramsFor()` / `factoryChoppedCoreUnigramsFor()`。**注意**：`makeTextMap` 輔助函式的 `VERSION` 為 `1.1`（否則 10+ 測試靜默失敗）。
  - **Phase B**：`TextMapTrie.getNodeIDsForKeyArray` 的 `keyInitials` 直接取 `$0.first?.description`（零鎖），不走 `getCachedFirstChar` 與 `internKey` 的雙重 NSLock。
  - **Phase C**：`QueryBuffer<T>` 以 `NSLock` 取代 `DispatchQueue.sync`（時間戳改用 `DispatchTime.now().uptimeNanoseconds`）。**注意**：`cleanupCheckInterval` 必須是 `static var`——Swift 不允許 generic type 內的 `static let` stored property。
   - **Phase D**：`Homa.Assembler.gramQueryCache` 的鍵自 `[[String]: [Homa.Gram]]` 改為 `GramQueryCacheKey`，`gramQueryCacheOrder` 同步為 `[GramQueryCacheKey]`，以插入順序實現 LRU 半量淘汰（汰最舊 50%）取代 `removeAll()`。**注意**：不可用裸 `Int` hash（碰撞誤命中）。
   - Phase B/C/D 已鏡像至 `vChewing-macOS`（`vChewing_LangModelAssembly/TrieKit/`、`vChewing_Homa/`）與 `vChewing-OSX-Legacy`（`Shared/vChewingComponents/LMAssembly/TrieKit/`、`Shared/vChewingComponents/Homa/`）。
- **`Homa.PossibleKey` 結構化枚舉**：`Config.keys` / `Assembler.keys` 為 `[PossibleKey]`（取代 `&` 字串編碼）；`unigramsFor` 具 LRU cache。**注意**：`insertTemporaryData` / `clearTemporaryData` / `injectTestData` 等資料變更入口皆須使該 cache 失效，否則 sub-LM 查詢返回過時結果。
- **就地加詞之即時生效鏈路（2026-09-17 定案）**：`SessionProtocol.performUserPhraseOperation` 之次序恆為「寫檔 → `insertTemporaryData` → `updateUnigramData()`」——熱重載（`assignNodes(.refreshExisting)`：清空組字器查詢快取、就地重查所有既有節點）看得見的只有已入庫的臨時資料，次序顛倒即無從立刻生效。`insertTemporaryData` 必須**全量**使 `LXFacade.unigramLRUCache` 失效（替代讀音路徑以 `ALT\t…` 定址、無法以 keyChain 枚舉）；`LXFacade.loadUserPhrasesData` 之非同步路徑不得在新資料就緒前清空既有資料（「舊資料已清空、新資料尚未讀入」之空窗期會讓熱重載把組字器重建成沒有使用者詞語的狀態），該清除延後至 `replaceData`（成功）／`readFileContentAsync` 之 `onFailure`（失敗）；且只清「本次將重新載入者」（`filterPath` 為 nil 時不動 `lxFiltered`）。
- **動態 `maxSegLength`**：`Homa.PossibleKey` 具 `count` 與 `isMultiple`；`assignNodes` 在 span 遍歷前檢查 `rangeOfPositions` 內是否有 `isMultiple` 的 key，有且 `maxSegLength > 4` 則縮為 4。無 `.multipleKeys` 者保持 `maxSegLength = 10`；有者每次插入查詢量封頂 780 次。
- **`LMCoreEX` 前綴部分匹配**：具輕量前綴索引 `sortedKeys: [String]`、`keys(matchingPrefix:)` 與 `unigramsFor(keyPrefix:)`；`LMInstantiator.unigramsFor(keyArray:)` 具 `partiallyMatch: Bool` 過載（預設 `false`）；`LookupHub.grams(for:)` 傳 `partiallyMatch: lmi.config.partialMatchEnabled`，使 `lmUserPhrases` 亦回前綴匹配。LRU 快取鍵含模式維度（`PM0`/`PM1`）。
- **`narrateTheComposer` 朗讀**：目標含 ASCII 字母時先試以 `Tekkon.cnvHanyuPinyinToPhona` 轉注音；組字路徑以 `actualKeys[cursor - 1]` 為朗讀對象。**陷阱**：`getPreviousRearSyllableSnapshot` 必須走 `receiveKey(fromPhonabet:)`——`actualKeys` 存注音，用 `receiveSequence(readingKey, isRomaji: true)` 重建會令拼音模式的後置聲調覆寫失效。
- **聲調覆寫提示之抑制偏好（2026-09-18，Phase 228）**：`kSuppressTooltipForIntonationKeyOverrideEvents`（`suppressTooltipForIntonationKeyOverrideEvents`；預設關）——啟用後，聲調鍵覆寫游標身後的漢字的音調時不再顯示「已覆寫游標身後的漢字的音調」內文提示。該提示之三行賦值（`tooltip`／`tooltipDuration`／`tooltipColorState`）收在 `BPMFFullMatchTypewriter.performRearIntonationOverrideIfNeeded` 之 `.success` 分支的偏好閘門內、**三行同進同退**（否則會留 `2` 秒之殘值）；覆寫行為、朗讀與 `session.switchState` 皆在閘門外、不受本偏好影響。同檔 `handleStandaloneIntonation` 之「獨立聲調鍵」提示（`IntonationMarkInstruction`）屬另一事件、不在本偏好管轄範圍。
- **混輸 Tooltip 之錨點（2026-09-18，Phase 229）**：中英混打模式下，內文 Tooltip 之錨點改以「未完成讀音後方之游標位置」為準（此前恆錨在組字區最前方＝客體量測座標 0 之矩形），與選字窗之錨定（`candidateWindowOriginInfo()` → `lineHeightRect()` → `clientLineHeightRect(forU16CursorPos:)`）同源。該位置須另存於 `IMEState`：`IMEStateData.cursorPosRightBehindTheUnfinishedReading`（Character 索引）＋唯讀 `u16CursorPosRightBehindTheUnfinishedReading`（UTF-16 對位）——**凡 `generateStateOfInputting()` 生成之輸入狀態一律賦值**：未完成讀音非空時取其插入處（`cursorSansReading`），為空時繼承當前輸入游標位置（`result.cursor`）；nil 僅見於非輸入狀態（標記／選字／關聯詞／符號表）。蓋因 `.ofInputting` 狀態之 `marker` 會被 `getMitigatedState(_:)` 拉平至 `cursor`（IMK 要求 selectionRange 之長度為 0），該位置於 Session 層無從回收。**用語**：護摩引擎以「與文字輸入方向相反的方向」為後方（Rear）——`isCursorAtAssemblerEdge(direction:)` 之中 `pos == 0` 為 `.rear`、`pos == length` 為 `.front`；故「未完成讀音後方」＝該讀音所占區段之起始側。消費端為 `SessionProtocol.showTooltip` 之 private `tooltipAnchorRect()`：輸入狀態一律改走 `lineHeightRect(atU16Pos:)`（未完成讀音為空者因而錨在輸入游標位置），非輸入狀態沿用既有錨定；客體量測無效（`CGRectNull`／原點為零）時退回既有錨定。**陷阱**：`updateVerticalTypingStatus()` 仍須先呼——縱排判定（`isVerticalTyping`）靠它，不可因換錨點而略過。**附註（2026-09-18 補記）**：面板定位須晚於客體之組字區更新——`switchState` 原先在 `updateCompositionBufferDisplay()` **之前**呼叫 `showTooltip`／`toggleCandidateUIVisibility`，導致量測當下客體仍持有上一狀態之組字區、本狀態之索引對其越界，`clientLineHeightRectForU16CursorPos:` 遂逐位遞減而退回前一個字元（症狀：Tooltip／選字窗定位恆落後一個字元）。現次序已改為「先更新組字區、後擺放面板」。經事主於真機覆驗，該症狀已解決（2026-09-18）。**相關不變量**：`clientMitigationLevel >= 2`（安全強化組字區／PCB 路徑）時 `getMitigatedState(_:)` 不拉平 `.ofInputting` 之 `marker`，故 `state.marker` 恆等於 `cursorPosRightBehindTheUnfinishedReading`、`markedRange` 即該未完成讀音所占區段；PCB（`vChewing_PopupCompositionBuffer` 之 `CompositionView.update(using:)`）以 `state.u16MarkedRange` 繪標記底色（故整段讀音成 marked range）、以 `state.u16Cursor` 擺閃爍游標（故游標在區段終點、非該欄位）。級別 < 2 時 `marker` 被拉平至 `cursor`、`markedRange` 為空（該欄位仍為讀音插入處）。
- **冗餘 `assemble()` 清理與 Homa `dropKey`**：`insertKey`、`dropKey`、`overrideCandidate`、`updateUnigramData` 等路徑已無冗餘 `assemble()`。`assembler.dropKey` 為 `do { try assignNodes() } catch { assemble() }`——不可只寫 `try? assignNodes()`，否則 `noNodesAssigned` 時 `assembledSentence` 停在刪鍵前狀態。
- **Homa revolver 首輪 pre-consolidation**：`revolveCandidate(...)` 具 `skipInitialConsolidation: Bool = false`；Typewriter 依 `homaCandidateCursorType` 與 `assembler.isCursorAtAssemblerEdge(direction:)` 決定是否跳過首輪鞏固——僅 `.placedFront` / `.placedRear` 且游標在對應 edge 時啟用。
- **MixedAlphanumericalTypewriter 前綴吸收**：修復八類缺陷（純注音超長吞噬、auto-split 偏向長後綴、Space 缺 fallback、ETenDOS 被 `hasUnigramsForFast` 過濾、auto-correct 干擾 suffix）。現行規則：動態碼長上限（Dachen26=6，其餘=4）、關 auto-correct、長後綴優先、Gated `hasNoDestructiveOverwrite`。
- **MixedAlphanumericalTypewriter camelCase 後綴防禦**：`buildAutoSplitCandidate` 具 `suffixHasUppercase` guard，拒絕後綴含大寫字母的候選（避免 `macOS ` 被拆成 `ma` + `OS`）。僅檢查 suffix（prefix 允許含大寫如 `Hello你好`）。**已知限制**：`iPhone ` 等中段大寫 + 單字母後綴仍可能誤拆。
- **MixedAlphanumericalTypewriter 聲調與 Shift ASCII 阻斷**：對 `BPMFFullMatchTypewriter` 委派點強制關閉 `isToneOverrideEnabled` 與 `isLeadingIntonationAccepted`；**Mixed mode 永遠不接受聲調前置鍵入**（相關偏好於 mixed mode 無效）。`isShiftASCII` 與 `shouldBlockPhoneticAbsorption`（digit + uppercase）閘門使 Shift 敲入的 ASCII 與純數字 / 大寫字母不被 Tekkon composer 吸收。
- **MixedAlphanumericalTypewriter 之讀音判定權威（2026-09-20，Phase 234）**：混打之「這串字是否為一個合理讀音」於兩處改委由 Tekkon 引擎層 `isSequentiallyTypedRawKeyOrder` 為權威——①**動態注音排列**（大千26／倚天26／許氏／星光／劉氏）改走該 API，故「鍵數 == 佔用槽數」之區域豁免（`maxSingleSyllableKeyCount` 之放寬 ＋ 兩道 `parser != .ofDachen26` 停用）已全數移除，該類排列之合法多寫編碼（大千26 `qquu`＝ㄅㄚ 為 4 鍵 2 槽）因而正確成字、不再整串滯留為 ASCII；②`shouldPreferASCIIWordPath` 新增第二項英文證據 `isNotSequentiallyTypedReading(_:)`（＝`!isSequentiallyTypedRawKeyOrder`，護欄為「長度 ≥ 2 且全為 `[A-Za-z]`」），故 `ls`／`ln`／`lc`／`mv` 這類「槽序上不可能這樣打」之短 token 於 Space 時遞交 ASCII（此前被收為單一音節：`ls`＝「峱」、`ln`＝「艘」、`lc`＝「蒿」、`mv`＝「須」）。原有之「非前進式槽消耗」計數式證據**保留**（`tod`／`film`／`hell` 等靠它），但收窄至**靜態排列**（`!parser.isDynamic && !parser.isPinyinMode`）——動態排列之合法編碼本即跨鍵改寫槽值、計數無意義。**（2026-09-21 補）本判定自 Phase 238 起收攏於偏好 `kMixedAlnumJudgeReadingsBySequentialRawKeyOrder`（預設啟用、無資料遷移；停用即回到本 phase 之前導 `d85b790` 之舊制，見下則）。**
  - **不可直接以引擎層判準替換「鍵數 == 佔用槽數」**：該 API 之條件五**明定放行「同鍵之重寫」與「同值之重寫」**（後者不留下可觀測之變化、且為動態排列所必需），然在混打語境下**冗餘鍵恰是「ASCII 前綴 ＋ 注音後綴」之分界證據**——`ai` ＋ `i6`（鍵序 `aii6`）即以此分界，若放行則整段被吞為單一讀音「模」。故**靜態排列維持鍵槽計數**（該式即「無冗餘鍵」、比引擎層判準略嚴），僅動態排列改委由該 API。**用語分野**：該 API 答「這是否為一個打得出來的讀音」，混打所問為「這是否為**這一整段**讀音（nothing else）」。
- **中英混打模式之「英數閂滯狀態」（2026-09-20，Phase 235）**：`UserDef.kEnableLatchedAlnumStateInMixedAlnumMode`（`rawValue: "EnableLatchedAlnumStateInMixedAlnumMode"`，`.bool(false)`，**預設關閉**）；偏好名稱 `PrefMgr.enableLatchedAlnumStateInMixedAlnumMode`**兩開關前提（首要不變式）**：本功能之所有新行為一律以「閂滯開關 ON」且「`kMixedAlphanumericalEnabled` ON」為前提，兩者未同時成立時行為必須與 Phase 235 之前完全一致**語意**：中英混打模式一旦判定某段英數內容「不可能是一個依槽序鍵入的讀音」（上鎖點＝`isNotSequentiallyTypedReading == true`，「覆寫修正」之優先級低於英文判定），即將該段即刻遞交並**上鎖為閂滯於英打**；其後每一顆可列印 ASCII（`0x20...0x7E`）皆即刻遞交，直到解除**狀態承載**：`MixedAlnumConfig`（`public struct: Sendable, Equatable`；**現與 `MixedAlphanumericalTypewriter` 同檔**——`Sources/LibVanguard/Typewriter/Typewriter_MixedAlphanumerical.swift` 內以 `// MARK: - MixedAlnumConfig` 起頭；原獨立檔 `Sources/LibVanguard/InputHandler/InputHandler_MixedAlnumConfig.swift` 已刪除，兩倉一致）——`buffer: String` ＋ `isLatchedToAlnum: Bool`；`InputHandlerProtocol` 以 `mixedAlnumConfig` 持有，`mixedAlphanumericalBuffer` 為其 protocol extension 薄存取器（比照 `Homa.Assembler.config`）**兩個復位粒度（施工必記）**：`resetContent()` 僅清緩衝（在 `clearComposerAndCalligrapher()` 路徑上、亦即每次遞交都會經過）、`resetAll()` 連閂滯旗標一併清且**唯一呼叫點＝`releaseLatchedAlnumState(announce:)`**（收斂後不再是死碼），`clearComposerAndCalligrapher()` 只呼前者——**`InputHandler.clear()` 本身不得解除閂滯**，因其為 `switchState(.ofCommitting)` 之必經之路，而閂滯於英打時每鍵皆會遞交（否則第一顆鍵即自我解除）**落點**：①閂滯分支置於 `Typewriter_MixedAlphanumerical.handle(_:)` **最前端**（在波浪符號鍵、Shift+Space、Space、中文標點查詢之前）——以 `resolveVisibleInputText(_:)` 解析可見文字、單一可列印 ASCII 即即刻遞交，否則回 `nil` 交還既有流程；故 `matchesCJKPunctuation` 之 `return nil` 陷阱由構造上消除，並另於其計算式加 `!isLatchedToAlnum` 作防重構；②`InputHandler_TriageInput` 之 Space 分支前提已由 `!mixedAlphanumericalBuffer.isEmpty` 放寬為 `… || mixedAlnumConfig.isLatchedToAlnum`（否則閂滯態下 Space 會繞道至一般組字送字邏輯）；③**四個解除鍵皆置於各函式之 `.ofInputting` 護欄之前**（閂滯態之 state 恆為 `.ofEmpty`）：Enter **不攔截**（回 `false`，否則終端機情境喫不到換行）、BkSp／Delete／Esc **攔截**、Option+BkSp **不攔截**；④**靜默解除（`announce: false`，完全不發提示）**：兩個直接發出點＝`resetInputHandler()`（函式開頭）與 `performServerActivation()`（後者不呼前者，故須獨立實作）；**凡經 `resetInputHandler()` 而入者皆靜默**——繁簡輸入模式切換（`InputSession.inputMode` 之 `didSet`）、`inputControllerWillClose()`、`commitComposition()`、`performServerDeactivation()`（以 `commitExisting: false`）、`isASCIIMode` 之 setter（Shift／CapsLock／JIS 英數鍵皆經此；其三條切換路徑皆經同一 setter）、`handleEvent(nil)`（macOS Emoji 面板，以 `forceComposerCleanup: true`）、CapsLock 切換分支（`shiftEisuToggleOffTogetherWithCapsLock` 情境）**提示載體（不走 `state`）**：進入與解除之提示一律由 StatusUI 負責——`SessionCoreProtocol.showStatusHint(_ text: String, duration: Double)`（`extension SessionCoreProtocol` 之**預設實作**、**非 protocol requirement** ⇒ 既有 conformer 未動；作法逐項照抄 `performServerActivation()` 之打字模式提示：`ui?.statusUI` → `statusUI.sync(accent:locale:)` → `updateVerticalTypingStatus()` 行高矩形左上角頂點 → PCB 顯示時 `max(...)` 上抬 → `heightDelta = height + 4.0` → `direction: .horizontal` → `asyncOnMain(bypassAsync: UserDefaults.pendingUnitTests)`，closure 不捕獲 self）發出點：`commitLatchedAlnum`（上鎖，i18n `i18n:StateOfInputting.Tooltip.MixedAlnumLatchedStateEntered`）與 `releaseLatchedAlnumState(announce: true)`（解除，`…MixedAlnumLatchedStateReleased`），時長各 **1.5 秒****不觸碰 `state`** ⇒ 解除後不會留下任何組字內容、亦不產生 `.ofInputting`以 state 承載之 tooltip 舊法已廢（其空狀態變體會令狀態恆為 `.ofInputting`，致使解除後之 BkSp／Delete／Esc 仍被各函式之 `.ofInputting` 護欄攔截；且任何依賴 state 之提示皆會被緊接的按鍵事件之 `switchState` 換掉，連續打字時不可見）會發提示之解除僅四個呼叫點：`handleEnter`／`handleBackSpace`（含 Option+BkSp）／`handleDelete`／`handleEsc`，皆置於各函式 `.ofInputting` 護欄之前**已知取捨（勿誤認為缺陷）**：閂滯一旦上鎖，其後之中文讀音鍵亦會作 ASCII 遞交（`test_IH447` 已固化此後果）；**波浪符號鍵**在閂滯態下若產生可列印 ASCII 即作 ASCII 遞交、不再呼出符號選單（**已裁定**：與 `isASCIIMode` 之行為一致）**小鍵盤**：閂滯於英打時，NumPad 之字元鍵逕以半形 ASCII 即刻遞交、**不受 `numPadCharInputBehavior` 影響**（Wave 8 裁定）**測試**：`test_IH442`～`test_IH448`（7 支／11 案例；`IH443` 為兩開關四態之首要不變式、`IH447` 固化上鎖之已知後果）需求研究全文見 `vChewing-DevLogs/Research/Phase234_PostResearch.md`**現狀（2026-09-20 定稿）**：已 commit——`vChewing-LibVanguard` `427cfba`（12 檔、＋530／−5）／`vChewing-macOS` `e27fc6e2`（18 檔、＋568／−5；`d47d7bb7`→`441186a8`→`73d57a1e`→`e27fc6e2`——末者為 2026-09-20 rebase 拆分後之現行值，見其後〈L10n 再訂正〉與〈rebase 拆分〉），兩倉同訊息 `Typewriter // MixedAlnum: +Latched alnum state.`；兩倉 `swift test -c release --no-parallel --disable-sandbox` 各 **567 支、0 失敗**，兩倉 `make lintFormatUncommitted` `rc=0` 且逐檔雜湊零變動，鏡像 `Sources/` 與 `Tests/` 逐檔 md5 同值；commit 訊息經一次 amend 定稿（移除「A release shows an inline tooltip.」之宣稱，改述兩次狀態轉換皆經 `SessionCoreProtocol.showStatusHint`）四語系 `…description` 於 commit 後改排為**單行條列**（值內以單一 `\n` 分隔、行首 `- ` 羅列 5 個條目，共 6 行；**勿改為實體換行**；2026-09-20 再訂正——分組換行改單、末句去重）；該 4 檔 `.strings` 已隨 `vChewing-macOS` 之 amend 入庫（`441186a8`）、官網倉之對應說明已入庫（現行 `35d9ece`；沿革 `ee9954a` → `3a35d8b`）、本文件群之文書亦已入庫於 `vChewing-DevLogs`（`P234 - P235.` 一筆，含本次訂正）**未驗／已知未做**：真機目視未做（1.5 秒提示在連續打字下是否確實可見）；`IH446` 無「靜默解除不發 StatusUI」之直接斷言；`showStatusHint` 刻意未複製先例之 `state.tooltip` 旗標 ⇒ latch 提示為**一次性**（面板被關閉後不會重發） **用詞（2026-09-20 定案）**：`Latch`／「閂滯」（zh-Hans「闩滞」、ja「ラッチ」）；本功能之舊稱 `Sticky`／「黏滯」已於 commit 前全面換除、倉內零殘留（UserDef 鍵名與 `rawValue`、`PrefMgr` 屬性、`MixedAlnumConfig` 之欄位、i18n 鍵、四語系文案、測試名與 Swift 註解皆然）；識別字為 `UserDef.kEnableLatchedAlnumStateInMixedAlnumMode`、`PrefMgr.enableLatchedAlnumStateInMixedAlnumMode`、`MixedAlnumConfig.isLatchedToAlnum`、`releaseLatchedAlnumState(announce:)`、`SessionCoreProtocol.showStatusHint(_:duration:)`、i18n `StateOfInputting.Tooltip.MixedAlnumLatchedStateEntered`／`StateOfInputting.Tooltip.MixedAlnumLatchedStateReleased`；四語系文案之對應詞為「啟用中英混打模式的英數閂滯狀態」／「启用中英混打模式的英数闩滞状态」／「中英混在モードで英数のラッチ状態を有効化」／`Enable latched alphanumerical state in mixed alphanumerical mode`。**換稱（2026-09-20 定稿後）**：識別字之 `EnglishAlnum` 一律換稱為 `Alnum`（見前列〈換稱後續〉之對照）；`UserDef` 鍵名與 `rawValue`、i18n 鍵、四語系文案皆不含該詞、未受影響，故**無資料遷移**。**定稿後續（2026-09-20）**：四語系 `.strings` 之該把 `description` 已改排為 `\n` 條列（5 條目），並經 amend 併入 `vChewing-macOS`（現行 `e27fc6e2`，沿革見下）；官網倉 `vChewing-HomePage.io` 之 `manual/preferences.md` 亦已補該選項並併入 `35d9ece`（沿革 `ee9954a` → `3a35d8b`）。**換稱後續（2026-09-20，commit 之後）**：含 `EnglishAlnum` 之識別字全面換稱為 `Alnum`（`isLatchedToAlnum`／`commitLatchedAlnum`／`handleLatchedAlnumInput`），兩倉 feature commit 隨之 amend（`0cb3f14`→`427cfba`、`d47d7bb7`→`441186a8`），訊息與計數未變。**CI（2026-09-20，推送後）**：`vChewing-LibVanguard` 之四條 workflow（linux／WinNT／macOS-SwiftOpenSource／macOS-Xcode）於 SHA `427cfba` 全綠——run `35492768006`／`35492768019`／`35492768083`／`35492768008`；同日前一次推送之 `0cb3f14` 亦四條全綠。`vChewing-macOS` 之 `441186a8` 亦已推送且其 CI 綠（`debug-macOS-SPMTestsAndPackage`，run `35493468473`；該倉其餘 CI 與 LibVanguard 之範圍雷同、事主明示只看此條）。**L10n 再訂正（2026-09-20）**：該 `description` 之 `\n\n` 全改為 `\n`、並刪去與首句重複之末句（四語系同）——解譯後 6 行（1 句 ＋ 5 條目）、`\n` 轉義 12 → 5、值仍單行；該筆 macOS commit 隨之由 `441186a8` amend 為 `73d57a1e`、再經事主之 rebase 拆分定為 **`e27fc6e2`**。**rebase 拆分（2026-09-20）**：該筆已拆為兩顆——`df55d281`（`L10n // Term fixes & sorting the files.`，8 檔 ＋12／−12）內含**與本 phase 無關**之 `kShowModeDescriptionOnActivatingServer.description`／`.shortTitle` 措辭修正（內文提示→浮動提示、正名 0.7 秒）、`i18n:Installer.OldVersionStillInUse` 措辭與 `.strings` 排序；P235 本體則為 `e27fc6e2`（18 檔 ＋568／−5）。兩顆皆已推（`origin/main`＝`e27fc6e2`）；rebase 後之三條 CI（linux／WinNT／debug-macOS-SPMTestsAndPackage）雖自動再觸發，惟 `e27fc6e2` 與已驗之 `441186a8` 之樹差僅四語系 `.strings` 各一行、且測試靶（`Packages/vChewing_OSNeutral_LibVanguard`）零讀取 `.strings`／`lproj`——文案變更在 CI 上不可觀測，故不留未驗項，綠燈由 `441186a8` 承繼。

  - **未接線處**：`buildAutoSplitCandidate` 仍用自帶之 `enforceCSVTOrdering = true` ＋ `receiveKey` 回 false 即作廢（語意與該 API 條件三同向）；改採後者會**額外**禁掉跨鍵覆寫之尾段（`dcl` 之類）並把 `var shadow = self` 之複製成本帶進逐後綴迴圈，故刻意未動。`isLeadingToneBlocked` 亦保留：其另涵蓋「聲調前置**後又被更正**」（如 `3su4`）之情形，屬混打之**政策**而非結構檢定，不可逕以條件三取代。
  - **仍未解**：全 parser-covered 之短英文 token（`tod`／`film`／`hell`／`rm`）與合法注音串本質同形之**平手**（`rm`＋Space 仍得「居」；使用者仍可以 Enter 強制遞交英文）；「覆寫修正」與「英文鍵入」在按鍵層同形（`dcl`＋Space 仍被當英文遞交）。此二者為需求層固有、非本層所能及。
- **狂拼模式之執行期狀態收斂為 `FuriousTypingConfig`（2026-09-20，Phase 236；純結構重構、零行為變動）**：比照 P235 之 `MixedAlnumConfig`，將原散在 `InputHandler` 上的三條狂拼狀態（`trail`／`highlightOverride`／`coSegmentedOffers`）收斂為單一值型別（`public struct: Sendable, Equatable`；`==` 逐欄手寫——`CandidateInState` 為 tuple 別名、無從合成），**塞在** `Sources/LibVanguard/Typewriter/Typewriter_BPMFFullMatch.swift` **檔首**（`// MARK: - FuriousTypingConfig`，緊接 `// MARK: - BPMFFullMatchTypewriter` 之前）；`InputHandlerProtocol` 改持單一 `furiousConfig`，三條舊名降為 protocol extension 之薄存取器（比照 `mixedAlphanumericalBuffer`）⇒ 呼叫端未動；`trail` 之唯一清除出口＝`invalidateFuriousTrail()` → `resetTrail()`；`FuriousCoSegmentedOffer` 補 `Sendable, Equatable`。驗證：`swift test -c release --no-parallel --disable-sandbox` **567 支、0 失敗**（lint/format 後複跑同）；鏡像五檔逐位元組一致。兩倉 commit `0dc086b`／`7ed7df35`（同訊息 `Typewriter // FuriousTyping: +State config.`）。**同日追加修正（事主裁定）**：原設計僅 `trail` 隨 `clear()` 失效，而 `highlightOverride`／`coSegmentedOffers` 會殘留——已明立兩粒度 `resetTrail()`／`resetAll()`，`clear()` 改呼 `resetAll()`；新增 `test_IH449`（紅綠雙驗：暫 revert 即紅）；測試 567 → **568 支、0 失敗**。兩倉該筆隨之 amend 為 `1768a15`／`a3263ba7`（各 6 檔、＋131／−13）並經事主推送（現 `origin/main` 即此二筆；LibVanguard 側四條 CI 全綠）。**v4.8.3 之程式變動至此全部定讞**。
- **中英混打讀音判定之偏好開關（2026-09-21，Phase 238）**：`UserDef.kMixedAlnumJudgeReadingsBySequentialRawKeyOrder`（`rawValue: "MixedAlnumJudgeReadingsBySequentialRawKeyOrder"`，`.bool(true)`、**預設啟用**）、`PrefMgr.mixedAlnumJudgeReadingsBySequentialRawKeyOrder`。**語意**：啟用＝ Phase 234 之判定（動態排列委由 Tekkon `isSequentiallyTypedRawKeyOrder`、`shouldPreferASCIIWordPath` 之亂序證據生效）；**停用＝回到 Phase 234 之前導 `d85b790` 之舊制**（動態排列退回「鍵數 == 佔用槽數」、大千26 重現整條豁免、兩字母亂序 token 重新被吸收為讀音）——已以 `d85b790` 之 worktree 探針逐案對照證實。**落點**：`Typewriter_MixedAlphanumerical.swift` 之單一共閘 `judgeReadingsBySequentialRawKeyOrder`，三處設閘（`bufferIsSingleSyllablePhonetic`／`fullInputIsSingleReading`／`shouldPreferASCIIWordPath`）；設定介面兩側皆置於 `kMixedAlphanumericalEnabled` **正下方**（兩側面板皆不作 UI 層之連動停用——非法態由程式端合取吸收；SwiftUI 側初版曾作、已於 2026-09-21 經事主裁定撤除〔含 P235 時代為閂滯列所加者與為此之 `@AppStorage` 私有屬性〕；兩列之次序為母開關 → 本選項 → 閂滯選項）。**範圍之界線（重要）**：本開關**不及於閂滯**——P235 之上鎖點以引擎層槽序檢定為定義，停用本開關不改變閂滯之行為（`test_IH453` 固化）。**無資料遷移**（預設值＝現行行為，既有使用者之行為零變動）。測試 `test_IH450`～`IH453`（4 支／7 案例）；兩倉 `swift test -c release --no-parallel --disable-sandbox` 各 **572 支、0 失敗**（術前 568）。**現狀（2026-09-21）**：兩倉已由事主 commit（`acdad14`／`607932ac`，同訊息〈`Typewriter // +`kMixedAlnumJudgeReadingsBySeqRawKeyOrder`.`〉——首行之 `Seq` 僅係長度簡寫，程式碼與 i18n 鍵名仍為全稱 `…Sequential…`；兩者並已推送——兩倉合計七條 CI 全數 success；同日並立「同環境之 CI 以本機代跑」之新制，本 phase 已試行 macOS 靶之同組命令於本機（7 包全 rc=0、全程約 4 分鐘））；官網倉 `manual/preferences.md` 已補記本選項一列（並修正該表兩處相對指涉；已入庫 `5c9b8a4`）；5.10 legacy 側建置已由事主實測通過。**commit 後之末句措辭修訂**：四語系 `description` 之末句改以「維持聲韻並擊等不需嚴格依按鍵序敲注音之特性」為由建議停用（ja／en 同步改譯；官網倉對位列之末句與「滿足的需求」欄一併改寫）——該四語系 `.strings` 之修訂已隨 macOS 側 amend 入 `607932ac`；官網倉 `manual/preferences.md` 亦已入庫 `5c9b8a4`。
- **`LMInstantiator` TextMap path 收斂到 `VanguardTrie.Trie.EntryType`**：`CoreColumn` 已自兩倉的 factory lookup surface 退場；`factoryUnigramsFor` / `factoryChoppedUnigramsFor` / `hasFactoryCoreUnigramsFor` 等一律以 `entryType:` 傳參。**注意**：`suppressFactoryUnigramsOfKanaSyllables` 須也覆蓋 `queryGrams(...)` 的 `makeFactoryUnigrams(queriedGrams:...)`。
- **Typewriter 層中英文混輸 `MixedAlphanumericalTypewriter`**（`TypewriterProtocol` 實作；由 `mixedAlphanumericalEnabled` 控制，**預設關閉**；與 cassette/pinyin 互斥）：`composer` + `mixedAlphanumericalBuffer` 雙軌。auto-split 即時算最優 ASCII/Phonetic 邊界；Space finalize 具 `onLexiconMatchFailure` fallback。**已知限制**：全 parser-covered 短英文 token 持續鍵入時仍可能 zhuyin-first。
- **混輸緩衝區之 Option+BkSp 整段作廢**：`handleBackSpace` 之混輸分支對「恰為 Option」之 BkSp 採 `removeAll()` 一次清空 `mixedAlphanumericalBuffer`（尚待辨識的英文緩衝區），其餘維持刪末字元；清空後注拼槽由 `syncComposerWithMixedAlphanumericalBuffer()` 同清，組字區既有中文不受波及。判準 `commonKeyModifierFlags == .option` 與同函式 codePoint／romanNumerals 兩支一致。
- **nonKanji（假名、鴨蛋零等）原廠辭典查詢**：`theDataMISC` 查詢原受 `keyChain.hasPrefix("_")` 限制，普通讀音 key 下的 `nonKanji`（typeID 8）條目永遠不會被返回；現以 `CoreColumn.theDataNonKanji`（textMapTypeIDs = [8]）在 `unigramsFor` / `hasUnigramsForFast` 為所有普通讀音 key 啟用該路徑，並保留 `_` 開頭 key 的 MISC 行為。
- **`suppressFactoryUnigramsOfKanaSyllables` 偏好旗標**：可停用原廠假名音節輸出（以詞值的 kana script 判定濾除，保留 `〇` 等非假名 nonKanji）。另：mixed mode 下除 `input.isSymbolMenuPhysicalKey` 外，主鍵盤數字 / 字母 / 符號鍵只要 Alt 被摁著就以 keyCode + `LatinKeyboardMappings` 還原 raw ASCII。
- 完整 Lexicon partial-match 熱路徑最佳化（Phase 05）：Assembler 跨插入查詢快取、Trie split cache 重用、node.id 去重、SQL prepared statement reuse
- `vChewing-macOS/Packages/vChewing_LangModelAssembly` 以 `vanguardTextMap` 取代 legacy SQLite。**現行規則**：runtime 與測試路徑都不接受 external `.revlookup` payload；反查只索引 single-segment `@` 分組行內的 ideographic characters，並無條件納入全部 CNS 條目；輸出會將 ASCII phonabet key 還原為注音。
- 不完全讀音部分比對與多音切割查詢（TrieKit）
- Unigram + Bigram 動態規劃組句（Homa）
- 節點覆寫、候選字輪替、上下文鞏固（Homa）
- Homa rare-case candidate revolver / consolidator：`CandidatePairWeighted.weight` 退回語言模型 metadata 身分，不可當成 `.withSpecified` explicit override score；`revolveCandidate()` 對 non-explicit 且 target span 改變的首輪情形有條件式 consolidation。
- 多來源辭典聚合（`LexiconAssembly`；Phase 213 前於本倉名為 `LexiconKit`）
- 使用者習慣 Ngram 洞察與時間衰減（`LexiconAssembly.LXPerceptor`；Phase 213 前於本倉名為 `LexiconKit.Perceptor`）
- 1947 與 2018 盲文標準轉換（BrailleSputnik）
- **原廠 VanguardTextMap 非同步載入**：`connectFactoryDictionary` 依 `asyncLoadingUserData` 拆分同步 / 非同步雙路徑；生產環境走 `VanguardTrie.TextMapTrie` 初始化路徑，避免載入時 1-2 秒 UI 凍結。
- **factory dictionary completion-driven 載入狀態**：`connectFactoryDictionary` 以 completion callback 回報最終載入結果；`LMMgr.connectCoreDB()` 先發 Started 通知、再於 completion 成功時發 Complete 通知（消除 async 路徑的「提前宣告完成」謊報）；Legacy 端以 main-queue + `@MainActor` 發通知。
- **拼音免聲調長句效能（TrieKit / LMInstantiator）**：`TextMapTrie` 具 chopped lookup specialized fast path（避免 protocol default 的笛卡爾積全展開）；`LMInstantiator.mergedAlternativeBucketUnigrams(for:)` 先索引原廠候選再做 deferred filter removal。
- **拼音免聲調長句效能精修**：`TextMapTrie` chopped path 的 ASCII initials / prefix/equality 走 UTF-8 bytes（遇非 ASCII 自動 fallback string path）；Tekkon `PinyinTrie` 具 parser-keyed shared cache，`pinyinAutoChopResult` 走 shared trie。
- **`QueryBuffer` NSMutex 清理 + `LMInstantiator` 單輪 memo**：`QueryBuffer` 每個 mutable property 各自以 `NSMutex` 保護。`LMInstantiator.mergedAlternativeBucketUnigrams` 具單輪 scope memo（`FactoryLookupMemoKey`）與 `joinedKey` cache。
- **`hasUnigramsForFast` 與非原廠迴路**：`LMInstantiator.hasUnigramsForFast(keyArray:)` 跳過濾除表、語彙置換、InputToken 展開、DateTime、倚天排序等後處理。`LookupHub.hasGrams(for:)` 與 `Typewriter_BPMFFullMatch` 亦走 fast path；`mergedAlternativeBucketUnigrams` 迴路前有 `Set<String>` 批量預篩選，非原廠迴路自 O(M^N) 降為 O(1) 或 O(K)。
- ~~下游 FactoryTextMapLexicon DFD 硬碟直讀（Phase 11，已作廢）~~：實機測試記憶體飆升 20~30 MB，全數撤銷。失敗根因：pread() 碎片化 heap allocation + 物化讀音鍵字串陣列開銷 + Data(contentsOf:) 隱性 mmap purgeable 優勢被低估。
- **LMCassette（CIN2 磁帶模組）連續記憶體最佳化**：`charDefMap`、`charDefWildcardMap`、`symbolDefMap`、`reverseLookupMap` 四個大型 Dictionary 改為 `CassetteSortedMap`（contiguous Data + byte-range index + binary search）；`octagramMap` / `octagramDividedMap` 改為 `CassetteOctagramMap` / `CassetteOctagramDividedMap`。
- **LMCassette 索引壓縮與 wildcard map 去重**：offset / count 欄位由 `Int` 改 `UInt32`；移除 `CassetteByteRange`；刪除 `charDefWildcardMap` 與 `buildWildcard(from:wildcard:)`；wildcard 查詢改對 `charDefMap` 做前綴掃描，經 `wildcardValuesFor(key:wildcard:)` / `containsWildcardMatch(key:wildcard:)` 即時產生。
- **LMCassette CIN v2.7 花牌鍵與任意單字元鍵分化**：新增 `%anysinglecharkey` 解析（**僅首次生效**、與 `%wildcardkey` 碰撞時後來者被忽略）。`patternValuesFor(key:wildcard:anySingleChar:)` / `containsPatternMatch(key:wildcard:anySingleChar:)` 為通用 pattern matcher（anySingleChar 恰好 1 字元）。`processCassetteQuickSelection` 具 functional-key bypass，使 `Shift+?` 在 `?` 為當前磁帶 functional key 時讓位給組筆錄入。`LMInstantiator` 具 `cassetteAnySingleCharKey`。**注意**：前提是磁帶已把 `?` 定義為 `%anysinglecharkey` / `%wildcardkey` 且未被同名資料鍵失效化。
- **LMCassette 反查索引零複製化**：廢除 `reverseLookupMap: CassetteSortedMap`，改為 `CassetteReverseIndex`（`revChars` = 去重後唯一反查字詞 bytes、`revEntries` 16B、`revCodeRefs` 指向 charDef/symbolDef 合併 namespace 的 entry 索引），查詢時依 refs 自來源 map 的既有 `rawData` 按需物化碼字串。**注意**：同字詞多碼順序自非穩定 sort 的未定義順序改為確定性（charDef 先、各依碼 bytes 序）。
- **`LMCoreEX` / `LMReplacements` / `LMAssociates` 索引壓縮**：三模組的 Dictionary + `strData: String` 改為 `rawData: [UInt8]` + sorted UInt32 byte-offset entries + binary search；`strData` 對外維持 `String` computed 唯讀屬性。`RangeParserAPI` 新增 `[UInt8]` byte 級 helper。LMReplacements 保留「同 key 最後一行覆蓋」；LMAssociates 保留 `#` cell 提早停止與雙鍵查詢；LMCoreEX 保留 tab 正規化與第三欄權重。
- **磁帶模式花牌鍵三明治組合**：`Typewriter_Cassette` 已無「組筆區非空時敲花牌鍵立即組字」條件——花牌鍵與任意單字元鍵一律僅作普通筆畫錄入，組字時機與一般筆畫一致（滿筆長自動組字、或空白/Enter 強制組字）；`shouldFormLongestCassetteKey` 無花牌鍵豁免（`zzzx*` 類無更長可能時仍自動組字，`y*` 因 `y**` 仍有匹配而保留錄入空間）。**行為變更**：敲 `y*` 後需按空白/Enter 組字。
- **Homa Assembler 查詢結果去重與元圖位置唯一性**：`queryGrams` 以 keyArray 為鍵的快取會把同一批 `[Homa.Gram]`（含相同 FIUUID）分發給不同節點，使 `generateKeyForPerception` 以 `lastIndex(id ==)` 定位 head 時誤判。現行設計：快取為純模板角色，`assignNodes` 新建節點與 `syncingGrams` 兩條路徑一律以 `Gram.withNewIdentity()` 物化節點專屬副本。
- **LMAssembly 共用 parser / cell tokenizer**：`RangeParserAPI.parse()` 對單一 ASCII separator 走 `String.UTF8View` byte scan、非 ASCII 者走 `Character` fallback。**注意**：單元測試 `UserDefaults` reset 順序不當會造成 stale `cassetteEnabled`、令 associated phrase 測試誤報。
- **InputHandler 倚天 DOS 候選補缺字**：`generateArrayOfCandidates()` 尾段具 `segregateCandidatesForETenDOS(from:)` 與 `supplementalETenSingleKanjiCandidates(reading:existingSingleSegments:)`：`prefs.enforceETenDOSCandidateSequence` 開啟時維持既有單字重排，關閉時把缺席的 ideographic 單漢字以 `-9.5` 權重追加到尾端。**注意**：`segregateCandidatesForETenDOS` 須防禦空 `keyArray` 候選。
- **ButKo BPMFVS 特殊遞交**：本地 package `ButKo_BPMFVS` 具 `phonic_table_Z.txt` parser 與 `convertToBPMFVS(smashedPairs:)`，以 ButKo 的讀音順序決定 IVS slot（首讀音維持原字、次讀音起附加 `U+E01E0 + slot`）；查表前須把 raw key 的後置輕聲（如 `ㄉㄜ˙`）正規化成前置輕聲。`UserDef.kReflectBPMFVSInCompositionBuffer` 令組字區 / 候選預覽只在 `CommitableMarkupType.bpmfvsAnnotationButKo = 4` 且開關啟用時投影成 BPMFVS。
- **`vChewing-VanguardLexicon` C-based 新酷音辭典純 Swift 生成器**：`chewingCBasedCHS` / `chewingCBasedCHT` 由 `ChewingCBasedDatabaseGenerator` 直接生成 `dictionary.dat` 與 `index_tree.dat`（不依賴 precompiled 版本）。**注意**：單字 `char-misc-nonkanji` 類的負詞頻行直接忽略；root node key 採 16-bit truncation 以對齊原版 C 行為。
- **`vChewing-VanguardLexicon` HealthCheck duplicate 偵查**：`Collector.healthCheckPerMode()` 直接重讀 raw source assets（含 `char-kanji-core` / `char-misc-bpmf` / 當前語系所有 `phrases-*`），以與 ingest 相同的 normalization 重建 occurrence；只要 `phrase + reading` 相同即視為 duplication，彙總後寫入 `healthCheckException([String])` 再拋出失敗。
- **`vChewing-VanguardLexicon` Rust 版新酷音辭典純 Swift 生成器**：`chewingRustCHS` / `chewingRustCHT` 由 `ChewingRustDatabaseGenerator` 自 `tsi.src` / `word.src` 生成 libchewing-rust 可讀的 `tsi.dat` / `word.dat`。**注意**：單字負詞頻（如 `ば -1 ㄅㄚ`）忽略、多字負詞頻拒絕。
- **BPMFVS commit 洩漏修復與詞庫 Unicode 污染稽核**：`committableDisplayText(...)` 為兩倉的統一 raw commit source——各提交路徑全部收斂到不含 BPMFVS 投影的原始字串；唯一產出 BPMFVS 的路徑是刻意的 `commissionByCtrlOptionCommandEnter`。`InputSession_HandleStates.swift` 的 `.ofEmpty` auto-commit 分支須以 `if let inputHandler` 條件綁定，不用 `?? previous.displayedText` fallback。
- **BPMFVS marking state 使用者詞語污染修復**：`IMEStateData` 具 `rawDisplayTextSegments: [String]?` 作 raw/display 雙軌——`displayTextSegments` 供渲染、`rawDisplayTextSegments` 儲存未投影原始字串；`userPhraseKVPair` 改從 `rawDisplayedText` 截取標記範圍；candidate preview 須同步更新兩個欄位。
- **Hotenka 繁簡轉換引擎 v2.0.0**：兩倉自 SQLite 後端（v1.3.1）升級至 StringMap 後端（v2.0.0）：`HotenkaChineseConverter` 無 `CSQLite3Lib` 依賴、新增 `HotenkaStringMap.swift`；`convdict.sqlite` 換為 `convdict.stringmap`；`init(sqliteDir:)` 換為 `init(stringMapPath:)` throwing initializer。
- **CNS11643 全字庫讀音過濾 UX**：`kFilterNonCNSReadingsForCHTInput` 對單一讀音（`keyArray.count == 1`）的不合規 Unigram 以 `-9.5` 權重 demote（建新 `Megrez.Unigram`，`score` 為 `let`），**多讀音詞組仍維持濾除**；否則啟用該選項時「播」（CNS 僅收 ㄅㄛˋ）等常用漢字會在 ㄅㄛ 讀音下消失。
- **`BookmarkManager` 熱點快取**：`LMMgr.dataFolderPath(isDefaultFolder: false)` / `cassettePath()` 每次無條件 `BookmarkManager.shared.loadBookmarks()`——在 iCloud Drive 路徑下成為 restore 熱點；`Jad_BookmarkManager` 與 legacy copy 具 bookmark store signature 快取（bookmark 檔未變且 access 尚在時直接返回）。
- **沙盒卸除 Fallback UX**：兩倉收緊 sandbox 後不再以 NSOpenPanel 取得 `~/Library/Input Methods/` 授權自刪，改由 `AppDelegate.selfUninstall()` 顯示指引 NSAlert，並以 Finder 揭示使用者詞語資料夾、App Support 父資料夾與 runtime `Bundle.main.bundleURL`。
- **iCloud Drive 磁帶書籤持久化失敗 workaround**：iCloud Drive 管理的 `~/Documents`、`~/Desktop` 等目錄中的 CIN2 磁帶 security-scoped bookmark 無法跨 reboot 持久化。`LMMgr` 具「Import to AppSupport cache」：選取 CIN2 檔案時同步複製到 `~/Library/Application Support/vChewing/Cassettes/`；`cassettePath()` 在 bookmark 還原失敗時 fallback 至快取副本；`resetCassettePath()` 清理快取檔（不誤刪使用者指定在 `Cassettes/` 的來源檔）；UI 入口須在 `saveBookmark` 後呼叫 `importCassetteFileToCache`。
- **磁帶最長可能碼自動組字、overflow trap、滿碼刪退與 Shift+Backspace 析構**：`Typewriter_Cassette.handle(...)` 不於 append 之前判定 `isStrokesFull` / longest-possible key，而拆成「既有滿碼 overflow」與「append 後 auto-combine」兩段；quick-set refresh 移到 combine 判定之後（否則未改動 calligrapher 的刪鍵會被 `renderQuickSetsIfNeeded(...)` 誤吞）。第 5 碼只回報 `2268DD51`，不漏到 `A9BFF20E` blocked-data trap。
- **Perception Override / Megrez 演進落地**：Megrez `Compositor` 具 Assembler 級 `perceptor` 注入，`3_KeyValuePaired.swift` 以 `perceptionHandler ?? perceptor` dual-dispatch 送出 `PerceptionIntel`；`LMPerceptionOverride` 的 `kDecayThreshold` 為 `-13.0`，WAL / JSON snapshot / CRC32 compaction 抽離至 `PerceptionPersistor`。
- **Homa transplant / LXPerceptor 對齊**：三倉（`vChewing-macOS`、`vChewing-LibVanguard`、`vChewing-OSX-Legacy`）完成 Megrez → Homa、`LMPerceptionOverride` → `LXPerceptor` canonical rename，並修補 `CandidatePair` 權重語義與同分標點保序；LibVanguard 側補 `LX_Perceptor.reducedLifetime` parity。
- **`LMCoreEX` tab→space 正規化**：`LMCoreEX.replaceData()` 最前端有一行 `let rawStrData = rawStrData.replacingOccurrences(of: "\t", with: " ")`。**理由**：`parseCells(in: splitee: " ")` 只認 ASCII space，而 `LMConsolidator.consolidate()` 在 pragma header 完好時會 early-return，故 `open()` 與 `readFileContentAsync` 都不做 tab→space 正規化。
- **候選字排序與原廠辭典重載 LRU cache 失效**：`LMInstantiator.unigramsFor()` 在 consolidate 後須補 `sort { $0.probability > $1.probability }`；`Homa.Assembler.fetchCandidates()` 排序須含第三級鍵 `$0.weight` / `$1.weight`。`static var factoryGeneration` 於 `factoryTrie` setter 遞增，`unigramsFor()` 的 LRU fingerprint 為 `config.hashValue ^ factoryGeneration`。
- **IME 之 varargs CLI 偏好 JSON 交換入口 `--dump-prefs-json` 與 `--import-prefs-json`**（落點 `MainSputnik.swift` 之 `MainSputnik4IME`：`dumpPrefsAsJSON` / `applyPrefsJSON(_:)`）：`--dump-prefs-json` 把可交換偏好以**純 JSON** 印至標準輸出；`--import-prefs-json <path>` 自 JSON 檔匯入，匯入後做**和解**（`PrefMgr.shared.reconcileAfterExternalPrefsImport()`——即 `fixOddPreferencesCore()` ＋ 13 條帶 `didSet` 之鍵自我賦值 ＋ `synchronize()`；**2026-09-24 前為僅 `fixOddPreferencesCore()`**）（機制係既有之 `UserDef.exportAsJSON()` / `importFromJSON(_:)`，含 `jsonExchangeBlacklist`）。**沙盒**：container 外 JSON 直讀必被拒，故與 `--import-kimo` 同款先試直讀、失敗則取 security-scoped 授權。
- **偏好交換格式（`__UserDefMeta`）與「自剪貼簿匯入配置資料」**（2026-09-24，Phase 240 落地）：`UserDef` 具交換格式之專用 API——`jsonExchangeReservedKeyPrefix`（`"__"`）／`jsonExchangeMetaKey`（`"__UserDefMeta"`）／`ExchangeMeta`（`title`／`description`／`extras`／`warnings`）／`destructureExchange(_:)`（**無條件摘除**根層所有 `__` 起頭之鍵；缺席 ⇒ `meta == nil`；形狀異常不使整包失敗）／`importFromDictionary(_:)`（逐鍵驗證之真源，`importFromJSON` 為其薄殼）／`importFromExchangeJSON(_:)`／`diffAgainstCurrent(_:)`（**純查詢**；以「會被實際寫入且與當前值不同」為判準，並以檔內 private 之 `NormalizedValue` 為單一比較表示法——根除 `1`↔`true`、`2024`↔`2024.0` 一類偽陽性）。**命名紀律**：`rawValue` 不得以 ASCII 雙底線 `__` 開頭（單底線 `_` 不在此限），已明文寫入 `enum` doc comment 並以 `SharedTests/UserDefExchangeTests.swift` 守住。**匯入後之和解**：`PrefMgr.reconcileAfterExternalPrefsImport()`（落點 `Packages/vChewing_Shared_DarwinImpl/…/PrefMgr_Utilities.swift`）＝`fixOddPreferencesCore()` ＋ 13 條帶 `didSet` 之鍵自我賦值（`candidateKeys` 由前者涵蓋）＋ `synchronize()`；**四條匯入路徑**（設定畫面「開發道場」之檔案匯入與拖放、「一般設定」頁之剪貼簿匯入、CLI `--import-prefs-json`）皆經 `PrefsExchange`（`Packages/vChewing_SettingsUI/Sources/SettingsUI/PrefsExchange.swift`；**只用 Foundation**，故可測且可於 5.10 側編譯）之 `applyPrefsJSONFromData`／`applyPayload` 收尾；剪貼簿按鈕之機理照「我姓ㄅ」之兩段式 alert（確認→套用→結果），**取消即完全不寫入**。**註**：`inputHandler.assembler.maxSegLength` 非即時（於下一次輸入源啟用時重推）；相關記述另見 §附錄二 A2.2 第 16 項。
- **配置助手（Configuration Assistant；2026-09-24，Phase 241 落地）**——助手之自稱一律為「**唯音輸入法配置助手**」（zh-Hans「唯音输入法配置助手」／en「vChewing Configuration Assistant」／ja「唯音入力アプリ配置助手」）：產品名取 app l10n 之全稱 `i18n:Common.VChewing`（zh-Hant「唯音輸入法」、ja「唯音入力アプリ」；bundle 之 `CFBundleName` 反而是簡稱「唯音」）＋「配置助手」：落點 `vChewing-macOS/ValueAdd/WebConfigAssistant/`（**建置產物之忽略為雙保險**：該目錄之巢狀 `.gitignore` 列 `node_modules/`／`dist/`／`tmp/`／`*.tsbuildinfo`，倉根 `.gitignore` 另立**路徑限定**之 `ValueAdd/WebConfigAssistant/dist/` 與 `…/tmp/` 作後備——**不得改採全域 `dist/`**，會誤傷日後刻意入庫者；`assets/*.json` 與 `tests/fixtures/*.json` 係**刻意入庫**之防漂移物資，不在忽略之列。2026-09-25 定案，原委見 Phase 241 補記）——**TypeScript、零 npm 相依**（`dependencies` 與 `devDependencies` 皆空；只用本機既有之 `tsc` 與 `node`），產物為**單檔自足之 HTML**（`dist/assistant.html`，約 306 KB：CSS／JS／後設資料皆已內聯；`dist/` 受 `.gitignore`）。**為何零相依**：本機之 TypeScript 7.x（Go 原生版）**已移除 `target: es5` 與 `module: none`**（`TS5108`／`TS6046`），故改以「原始碼一律 ES5 寫法 ＋ `target: es2015` 編譯 ＋ `lib: ["ES5","DOM"]`（誤用 ES6+ 標準庫 API 即編譯期報錯）＋ 產物之 ES5 守衛（`tools/es5guard.mjs`）」為紀律；打包器因此不必要。**防漂移**：`vChewingSharedCLI` 新動詞 **`dump-userdef-metadata`**（兩倉逐位元組同源）導出 118 條鍵之型別／值域／預設值／四語系標籤至 `assets/userdef-metadata.json`（`make metadata` 會重新導出並 `cmp`，有差即失敗；`make metadata-audit` 為 `--strict` 之 i18n 稽核；後設資料之現行規模為 232,766 bytes）；`--extra-label-prefix` 另收錄注音／拼音排列之 17 條既有 i18n 名稱（`i18n:KeyboardLayout.*`／`i18n:TypingMethod.*`）。**適配之輸入法版本**存於該目錄之 `version.txt`（`version=`／`build=`），由建置注入並於首頁以 `.vca-version`（與推薦值、維持不變之註記共用 `#114514`／11px 之小字規則）顯示；`make version-check` 與倉根 `Release-Version.plist`（本倉版本之 SSOT）逐值比對、已納入 `make audit`。**改版無須手動同步該 txt**：本倉版本之唯一寫入咽喉點是倉根 `BuildVersionSpecifier.swift`（由 `Scripts/vchewing-update.swift` 之發版流程以 `/usr/bin/swift` 呼叫；**倉根 `Makefile` 並無 `gitRelease` 目標**），該腳本現已一併改寫該 txt，且 `vchewing-update.swift` 之 `versionStampIsLanded()` 亦驗收之（未寫入即 exit 6 中止）。**產物規模**：`dist/assistant.html` 338,793 bytes（325.6 KiB；內嵌後設資料字面值 186,061 bytes）。**契約測試**：`Packages/vChewing_SettingsUI/Tests/SettingsUITests/AssistantContractTests.swift` 讀 `tests/fixtures/*.json`（由助手自身之核心邏輯生成）並斷言唯音一概收得下——**fixture 以 `#filePath` 錨定，故無須改動任何 manifest**；該測試只做純查詢（`destructureExchange` ＋ `diffAgainstCurrent`），不寫入 `UserDefaults`。**介面**：Windows 2000／ME 風格（桌面 `#3B6EA5`、窗體 `#C0C0C0`、`Tahoma, "Helvetica Neue", sans-serif`、黑色文字、`outset`／`inset`／`groove` 之 3D 邊框、`::-webkit-scrollbar` 捲軸、自繪之單選／核取）；窗體為**定尺寸**對話框：內容區為固定 `height: 490px`（**非** `max-height`——短頁面會令窗體變矮、底部按鈕逐頁位移，連續點擊者須追逐按鈕；過長者於區內捲動；視口不高與窄螢幕由媒體查詢給較短之固定高度），小字說明（`.vca-rec`／`.vca-opt-note`）之配色為 `#114514`（**不得以 `opacity` 代之**——黑字壓 `#C0C0C0` 時 0.9 之 alpha 幾乎無可見差異，且會把指定色沖淡）。左側 168 px 白色水印區由上而下為大字圖示、該頁標題、**該頁之職能說明**（`left.<stepId>`；**該第三行原放助手全稱、與標題帶重複**，事主 2026-09-25 指出後改為職能說明，如起始配置頁作「可先套用，亦可略過」——長度以顯示寬度 ≤ 34 格約束之）。標題帶右側為「第 n 步，共 N 步」＋分段方塊（兩者相隔 10 px；**無關閉鈕**——取消由底部按鈕承擔）；該右側區為 `display: inline-table` ＋兩個 `table-cell` 格位（方塊格位 `line-height` 恰等於方塊總高）——**垂直置中一律用格位、不得用 `inline-block` ＋ `vertical-align: middle`**（後者按「基線 ＋ 半 x-height」對位，疊加後會把方塊推低數 px）。**分支問卷、二路線（Phase 245 起）**：**快速（預設，四頁）**＝歡迎 → 背景（**來源 ＋ 打字方式兩個分支樞紐同頁**）→ **起始配置** → 摘要；**逐項（十三頁）**＝同上再＋九頁逐項問題。頁數**即時可變**（核取項「只套用起始配置」決定 `buildSteps(profile, osVersion, expressOnly)` 是否收錄逐項頁面；標題帶之「第 N 步，共 M 步」與分段方塊隨之由十三格變四格），底列另有**「跳到摘要 ＞」**（只在「距摘要尚有兩頁以上」時露面；按「上一步」會**原路折返**至跳轉前所在之頁）。**起始配置**（`src/starter.ts` 之 `starterFor()`）＝該 profile 之現成配置，內容即推薦值表（`recommendationFor`）之**全集**——**不另立第二份策展表**（故逐題頁面標示之「推薦值」與起始配置所寫入者恆同值；套用後在逐題頁面看到的就是同一組已選中之值，可逐項改回「維持不變」、取消套用則整組撤回）；**出廠預設值不在其中**（那是逐頁核取項之事）、**使用者親自表態者不受覆蓋**、**換 profile 即重算**。來源題含 **macOS 內建注音（10.6 Snow Leopard 起）** 一項，其接待說明與推薦值取自官網該篇 onboarding；來源 → 文章之對位見 `DOC_PATH_BY_ORIGIN`，來源 → 接待語見 `NOTE_KEY_BY_ORIGIN`（起始配置頁之「深入說明 →」亦指該文章）。**每個單選題之預設選項一律「維持不變」**、「以推薦值（或出廠預設值）補齊」為逐頁明示之核取項。**推薦值之策展紀律（Phase 245 明文化）**：以 origin 粗粒度落值時，**三類刻意不收**——①**值等於出廠預設者**（寫入等於無操作，且「以出廠預設值補齊」是逐頁核取項之事）；②**條件過窄者**（如 asus 一文之 `kAcceptLeadingIntonations = false` 僅 v4.4.1 有效、OpenVanilla 一文之 `kUseSCPCTypingMode = true` 原文限定「**嘸蝦米的老用戶**」——以來源粗粒度落值會波及同源之其他使用者，與文章原意互斥）；③**助手碰不到者**（不在設定介面曝露面內者，如 `kAssociatedPhrasesEnabled`；或需使用者自備檔案路徑／TIS 識別碼者，如 `kCassettePath`／`kBasicKeyboardLayout`）。**無依據者寧可照實明示「沒有需要先套用的項目」**——如小麥注音、OpenVanilla 兩來源之 origin 級起始配置為空，此為據實之結果（其內容仍會由 `typing` 分支供出），非未竟事項。**事主 2026-09-25 之四項策展裁定（優先於文章之暗示級處方）**：① **中英混打回退（`kMixedAlphanumericalEnabled`）只按華碩**，其餘來源不按來源預設啟用（原依奇摩／自然／《新手上路》所加者撤除）；② 「打字方式」之兩支注音路線**雙向表態**——`zhuyinmix`（注音組句＋中英混打）⇒ `true`、純 `zhuyin` ⇒ **刻意 `false`**（此為「值等於出廠預設者不收」之經核定例外）；③ **左右 Shift 切換英數之兩鍵**對微軟新注音／奇摩／自然／華碩／狂拼流拼音**刻意釘住為啟用**（非文章處方）；④ **來源標籤之統括命名**——`origin.opt.pinyin` 作「狂拼流漢語拼音輸入法（微軟拼音／微信輸入法／搜狗拼音／昇陽拼音／智能狂拼／紫光拼音／Rime）」（en／ja 用指定外文名 WeType／SunPinyin／ChineseStar／Microsoft Pinyin），並另立 `ORIGIN_SHORT_NAME_KEY`（`origin.short.pinyin`）供內文與配置名之短名。**層級優先序**：`effectiveRecommended()` 為「`typing` 級 ＞ `origin` 級」，故華碩＋純注音組句 ⇒ 停用混打。**起始配置之封閉性（事主 2026-09-25 第二輪指示：同一台電腦上多人來回切換配置時不得互相干擾）**：唯音之匯入是「只寫入包內出現的鍵」，故稀疏之配置必互相殘留——極端例為行列三十（磁帶派）之 `CassetteEnabled = true`（**為真即停用注音輸入**）殘留給下一位注音使用者。故起始配置一律**封閉於一組固定的鍵全集**（`starterUniverse()`；＝任何一組配置都可能指名之鍵的聯集，現代系統 **16** 鍵、舊系統 14 鍵）：全集內有推薦值者寫入該值（**指名**，`namedKeys`）、無者寫入**唯音之出廠預設值**（**回歸**，`resetKeys`）⇒ 任兩組配置之鍵集逐項相等，後套用者必然完整覆蓋先套用者；全集之外之偏好（選字窗字級、熱鍵、通知……）一概不碰。UI 將預覽分兩段並於摘要頁加一行 `summary.starterScope`。**兩段皆為逐項核取清單**（事主 2026-09-25：「要是變成一個 checkbox 清單讓使用者自己勾選就好了（預設是全勾選）」＋「『本組指名的項目』也弄成 checklist 吧」）：狀態分存於 `state.starterNamedOff`／`state.starterResetOff`（**皆存取消者**、預設空＝全選），可逐項取消（該鍵即不予更動），兩段各有一條緊貼標題之「全部取消勾選／全部勾選」連結；說明隨取消項數改口。**該頁之取捨項預設為「套用這組起始配置」**（事主：「使用者叫出這個配置畫面就是為了想切換配置的」）——`starterOn` 初始為真、`boot()` 先跑 `syncStarter()`；故即令一題未答，配置包亦非空（全集皆回歸出廠預設），要稀疏者須主動改選「不套用」。**題庫外之鍵**（`PRESET_ONLY_KEYS`；事主：「ㄅ半模式請自動啟用關聯詞語」）：`kAssociatedPhrasesEnabled` **不入題庫**（嚴守 2026-09-24 之曝露面規）而僅由起始配置指名——逐字選字派 ⇒ `true`、餘者回歸 `false`；其顯示名取別名鍵 `kUsingHotKeyAssociates`（「關聯詞語模式」）。全集遂為 **17 鍵**（舊系統 15）。**preset 之冗餘檢討（事主 2026-09-25）**：preset **不得**指定 `kCandidateWindowShowOnlyOneLine`（僅以單行/單列來陳列候選字）——該鍵為全域排版偏好（為老花眼之大字號顯示而設），而ㄅ半之單行已由 `kEnforceSingleLineCandidateWindowLayout4SCPC` 保證；該鍵遂退出鍵全集（全集 16 鍵）。**看似相近而實不互涵者**：`kUseHorizontalCandidateList`（佈局方向）vs `kEnforceSingleLineCandidateWindowLayout4SCPC`（行數）；`kAlsoConfirmAssociatedCandidatesByEnter` vs `kAssociatedPhrasesEnabled`（前者以後者為前提）；`kCassetteEnabled`（字根）vs `kUseSCPCTypingMode`（注音）各管各的模式。**選字鍵（`kCandidateKeys`）之逐來源定值**（事主裁定）：微軟新注音／小麥注音／奇摩／OpenVanilla／自然／華碩／ㄅ半 ⇒ `123456789`；CIN（所有字根類，來源或打字方式為之皆然）⇒ `1234567890`；macOS 內建注音／漢音／狂拼流／其餘 ⇒ `123456`（＝回退值）。**產物**另有 `dist/index.html`（`<meta http-equiv="refresh">` 跳轉至 `assistant.html`），故整個 `dist/` 目錄丟上網即可用；`make deploy` 複製兩檔。**取捨**：回歸段會把未指名之鍵主動寫回出廠預設（多數人為無操作，曾手動改過者則為主動改回；預覽與摘要兩處全列）。**已知界線**：app 內手動設定且不在全集內者不在此列（如 app「我姓ㄅ」連帶之 `kAssociatedPhrasesEnabled`——不在曝露面內、助手不得過問）。**題庫之界線（事主 2026-09-24 立規）**：**凡未出現於 `SettingsUI/`（SwiftUI）或 `SettingsCocoa/`（AppKit）之選項，助手一律不問**——該集合由 `tools/settings-surface.mjs` 掃描那兩個目錄之源碼生成（`assets/settings-surface.json`，現為 107 鍵），並以測試之「題庫 ⊆ 曝露面」不變式守住；設定介面增刪曝露項時跑 `make surface` 即可跟上（現行題庫 100 鍵／102 題）。**注音／拼音排列之選項**（順序、標籤、分組）一律取用自 app 源碼抽出之曝光面（`assets/settings-surface.json` 之 `keyboardParsers`，經建置注入 `VCA_SURFACE`；`tools/settings-surface.mjs` 解析 `KeyboardParser` 之宣告序與其 `localizedMenuName`，故順序為 0,1,4,5,8,6,7,3,2,9,10、並於 7 之前插分隔線——與設定介面一致）。**值之顯示**一律走「題目自身之選項標籤」（`labelForValue`）——`kKeyboardParser4Zhuyin`／`4Pinyin` 之標籤不在 `metaData.options` 內（由 `KeyboardParser.localizedMenuName` 供出、經 `--extra-label-prefix` 導出），逕用 `formatValue` 只會印出裸數字（`100`）。**「深入說明 →」**預設指向官網絕對位址 `https://vchewing.github.io/`（`DOC_BASE` 可覆寫；相對路徑在 `file://` 之下必為死鏈），文章路徑取官網各篇之實際 `permalink`。**建置與測試**：於該目錄跑 `make audit`（型別檢查 ＋ ES5 守衛 ＋ 76 支 `node --test` ＋ 後設資料防漂移 ＋ i18n 稽核 ＋ 曝露面防漂移 ＋ fixture 防漂移）、`make bundle`。**未竟**：真機（macOS 10.9 ＋ Safari 7）之實測與目視待 Phase 242 或更後續；官網嵌入與推廣依 P239 §0.3 之約束 3 暫緩。詳見 `vChewing-DevLogs/Reqs4LLM/Archive_P201-P300/Reqs_0241-0250.md` 之 Phase 241。

- **功能鍵（F1－F20）與未遞交組字內容之守護**（2026-09-25，Phase 243 落地）：`KeyCode.isFunctionKey`（F1－F20；**以硬體鍵碼判定**、不受基礎鍵盤佈局影響）＋ `InputSignalProtocol.isFunctionKey`（協定擴充預設實作，故 macOS 側之 `NSEvent` 免費取得同一語意）。**兩層守護缺一不可**：① `InputSession_HandleEvent.swift` 之 `handleKeyDown` 內、2026-07-07（`8125fabf`）新增之 Fn 快篩（`fnKeyCheck`）對**任何**帶 `.function` 旗標且不在其「無辜鍵碼」清單（翻頁／Home／End／方向鍵／刪退鍵）內者一律 `return false`——而 F1－F20 之按鍵事件**恆帶** `.function`（另帶 `.numericPad`，此即 `isNonLaptopFunctionKey` 之由來），故功能鍵在該快篩之下**從未進入 `triageInput`**，`InputHandler_TriageInput` 自 2022-12-17（`9fbc9a64`）即存在之終末處理（`A9BFF20E`，「避免 F1-F12 按鍵干擾組字區」）**整個被架空**；故該快篩須對功能鍵讓步：`if keyCode.isFunctionKey, hasUncommittedContent { break fnKeyCheck }`，`hasUncommittedContent` ＝ `state.hasComposition || !(inputHandler?.isComposerOrCalligrapherEmpty ?? true)`（**與終末處理同一判準**，勿另立第二套）。② `triageInput` 之 `.ofEmpty, .ofInputting` 分支須對功能鍵**就地攔截且不得靜默**：`vCLog("Blocked function key: …")` ＋ `errorCallback?("F1F20BEE")` 之後 `return true`——**用碼與終末處理之泛用碼 `A9BFF20E` 有別**，日誌前綴亦異（`Blocked function key:` vs `Blocked data:`），故兩者有兩重可辨識性。**何以不得靜默（事主 2026-09-25 裁定）**：靜默吃掉按鍵，使用者無從分辨「輸入法刻意攔截」與「功能鍵故障」——**「不出聲」不是「安靜的好設計」、而是可觀察性的缺失**。`errorCallback` 之終點與終末處理相同（`InputSession.callError(_:)` → `vCLog` ＋ `buzzer?()` → `SessionHost.shared.buzz()` → `IMEApp.buzz()`）。**各狀態之實測處置（逐態壓送 F5）**：`.ofEmpty`（無未遞交內容）放行且不出聲；`.ofInputting` 與 `.ofMarking`（後者經 `handleMarkingState` 未攔後轉 `.ofInputting` 再分診）皆回 `F1F20BEE`；`.ofCandidates` 屬**另一途**、本即由 `handleCandidate` 尾端之泛用碼 `172A0F81` 出聲（非功能鍵專用、未動）；`.ofAssociates` 經轉 `.ofEmpty` 後放行。**故「靜默」之缺口僅 `.ofInputting`／`.ofMarking` 此一分支**——凡日後新增「就地吃掉按鍵」之分支，同一紀律適用：**要嘛放行、要嘛出聲**。**放行即病灶**：`handleEvent` 回 false 者，IMK 會將該 NSEvent 原樣交給客體，客體以該鍵自身的字元改寫組字區之標記範圍 ⇒ **未遞交的讀音消失、且該鍵自身之字元被寫進文件**（vChewing-macOS Issue #617：`su3` + F5 得到控制字元而非「你」）。**範圍之界線**：例外僅及於 `keyCode.isFunctionKey`——`Fn` + 字母之系統熱鍵（如表情符號選擇器 `Fn+E`）帶 `.function` 但不屬功能鍵，**照舊放行**（不撤 2026-07-07 之政策，`test519` 固化）；**未遞交內容為空時功能鍵亦照舊放行給系統**（`test518` 固化）。測項落點 `Tests/LibVanguardTests/SessionTests_Cases5.swift` 之 `test516`～`test519`（516／517 為判別性、518／519 為不變量護欄），fixture 落點 `TestComponents/KBEventFixturesForTests.swift` 之 `functionKeyEvent(_:)`／`f5Event`／`fnEWithLetterEvent`。詳見 `vChewing-DevLogs/Reqs4LLM/Archive_P201-P300/Reqs_0241-0250.md` Phase 243。

- **中英混打之空白鍵與「空格鍵對內文組字區的行為」偏好**（2026-09-25，Phase 244 落地）：`Typewriter_MixedAlphanumerical.swift` 之 Space 分支自 Phase 244 起讀該偏好——**值 0（插入空格）且混打緩衝非空**時，空白鍵與 Shift+Space 同義（遞交 `committableDisplayText` ＋ 整段緩衝 ＋ 一個半形空格、一次遞交）；前提式為 `input.isShiftHeld || (!handler.mixedAlphanumericalBuffer.isEmpty && handler.prefs.spaceKeyBehaviorAgainstICB == 0)`。**「緩衝非空」為必要條件**：`handleComposition(input:)`（`InputHandler_HandleComposition.swift:31-32`）對**每一顆**可列印鍵皆呼叫 `MixedAlphanumericalTypewriter.handle(_:)`（空白鍵亦然），故若只以偏好值為閘，**純中文組字**之空白鍵會被本分支接走、改動既有之組字區送字路徑（實測：`su3` ＋ 空白於值 0 下之遞交由兩筆併為一筆）。**值 1／2 刻意不動（可驗之範圍界線）**：`apple` ＋ 空白 與 `ello` ＋ ㄕ（大千 `g`）＋ 空白在引擎眼中**同構**（同為純字母 5 字元緩衝、`shouldPreferASCIIWordPath` 同為真、同有詞庫命中之單鍵尾綴），故 2026-05-04（`743d7817`）所加之 **`count >= 5` auto-split 逃生門**不可刪亦不可收緊——刪之或收緊之必令 `test_IH400`（Izanami）於純字母鍵序之讀音上轉紅，而該逃生門之實際適用面**僅限純字母緩衝**（`shouldPreferASCIIWordPath` 之初閘即 `^[A-Za-z]+$`，含數字／符號之混輸本即不經此路）。凡日後欲再動該逃生門者，須先解此同構平手（或引入英文 lexicon），否則即以上述測試為代價。**診斷入口**：混打路徑之按鍵並非只經 `InputHandler_TriageInput` 之 `.kSpace` 分支——`handleComposition` 才是每鍵之第一站。

---

## 附錄一、開發階段歷史

因該章節過於龐大，故挪至 `vChewing-DevLogs/DevReqsHistory.md` 單獨管理。

---

## 附錄二、已知問題與注意事項

### A2.1 當前已知問題

1. `TrieJoinedTestSuite/testTrieJoinedAssemblyingUsingPartialMatchAndChops`（Phase 213 前於本倉名為 `LXTests4TrieHub/testTrieHubAssemblyingUsingPartialMatchAndChops`）若暫時使用完整 Lexicon 測資，會因語料語義與 Tiny Sample 不同而出現 sentence expectation failure；目前應將 benchmark 視為有效信號、將 assertion mismatch 視為已知暫時狀態。
2. **CI（linux／WinNT）測試行程硬崩（`Illegal instruction`／`c000001d`）——`mainSync` 對主佇列之遞迴 `sync`（2026-09-16 查明；已修於 P219）**：自 **`95a609c`**（2026-09-15，該筆把 CI 之 Swift 版自 `latest`＝當時的 6.3.3 抬到 **6.4**）起，兩條 workflow 之 `swift test --no-parallel` 每次都在同一處崩潰、且恰為兩個測試靶各一次（`LibVanguardTests`／`LexiconAssemblyTests`）。**堆疊**（WinNT 版有符號）：`InputSession.deinit` → `String.mainSync` → `DispatchQueue.main.sync` → `__DISPATCH_WAIT_FOR_QUEUE__` → libdispatch 之 client crash（`src/queue.c:1646`「`dispatch_sync called on queue already owned by current thread`」；Darwin 編成 SIGTRAP、Linux／WinNT 編成 ud2＝SIGILL）；另一條為 `LXAssociates.saveData()` → `withFileHandleQueueSync` 內之 `mainSync`。**機理**：`mainSync` 以 `Thread.isMainThread` 判斷「是否已在主執行緒」——在 Linux／WinNT 上主佇列之工作是由 dispatch worker 執行（該執行緒 `Thread.isMainThread` 為假、卻已持有主佇列之 drain 鎖），於是走 `DispatchQueue.main.sync` 慢路徑而遞迴 `sync`。**macOS 不受影響**（主佇列跑在主執行緒、走就地執行之快速路徑；本機同款 `test202_InputHandler_EscapeBehaviorVariants` 綠燈）。**同期 macOS 那條 CI 之紅燈與此無關**：`setup-xcode` 找不到 Xcode 27.0（runner 映像只到 26.6）。**已落地之修法（P219，2026-09-16；兩倉 byte-sync）**：① `mainSync`（`SwiftExtension/SwiftFoundationImpl.swift`）改以「註冊在 `DispatchQueue.main` 上之 `DispatchSpecificKey`」判斷是否已在主佇列（`getSpecific` 問的是「當前正在執行的佇列」、非執行緒身分，故兩平台通用）——命中則就地執行；② `withFileHandleQueueSync`（`LexiconAssembly/vChewingLXAssembly_Common.swift`）同法加掛 `fileHandleQueueKey` 之判斷。**兩項 6.2+ 側之實作約束**：該判斷函式須標 `nonisolated`（否則自身即成為 MainActor 隔離、反而無法自 `nonisolated` 的 `mainSync` 呼叫），且該 `DispatchSpecificKey` 與其註冊動作須收進**函式內之區域型別**——置於檔案層級會被 `-default-isolation MainActor` 收歸 MainActor，`nonisolated(unsafe)` 雖可編過、但 6.4 會對它誤發「對 Sendable 常數為多餘」之診斷（照該診斷移除即編不過）。**本機驗收**：6.4 側 **535 項 0 失敗**、5.10 側（兩倉）與 macOS 側皆 `Build complete!`；`vChewing-OSX-legacy` 之同構同步（`mainSync` 改走新增之 `isOnMainQueue()`、`withFileHandleQueueSync` 之檔案本已符合、僅補 doc comment）經 `make debug-core` `** BUILD SUCCEEDED **`。**未驗**：Linux／WinNT 之止崩須推一次 CI 方能確認。**仍未辦**：③ `InputSession.deinit`（本體僅一行 log）與 `Debouncer.deinit`（僅動 lock 保護之狀態）不再 hop 至主佇列——此僅為先前提議、未採納為 P219 之範圍。

   **第二輪（2026-09-16，CI 複驗後）**：上述修法只解了一半——`InputSession.deinit` 那條已止（linux／WinNT 之 `LibVanguardTests` 各 **60 項全綠**），惟 `LexiconAssemblyTests.testSaveDataRoundTrip` 仍崩、兩平台各一次。**真因**（WinNT 符號化堆疊：`testSaveDataRoundTrip` → `LXAssociates.saveData()` → `withFileHandleQueueSync` → `closure #1` → `mainSync` → `DispatchQueue.main.sync` → `_dispatch_sync_f_slow` → `__DISPATCH_WAIT_FOR_QUEUE__`）：`fileHandleQueue.sync` 於未受競爭時**就地在呼叫端執行**（libdispatch 之 `_dispatch_sync_f_fast`），而該呼叫端（`@MainActor` 之測試本體）**正在主佇列上**；於是內層 `mainSync` 眼中「當前正在執行的佇列」已被壓成 `fileHandleQueue`——`Thread.isMainThread` 為假、`DispatchQueue.getSpecific(key: mainQueueSpecificKey)` 亦為 `nil`（**它問的是當前佇列**），兩者皆不命中，遂對主佇列 `sync`，而主佇列之 drain 鎖正由本執行緒持有。**教訓（通用）**：`getSpecific` 這一招問得出「當前佇列是否為主佇列」，卻**問不出「本執行緒是否代持著主佇列」**；凡「先 `Q.sync` 進某佇列、再於其內 `mainSync` 回主佇列」之寫法，都必須在**進入 `Q.sync` 之前**擋掉在主佇列上的呼叫方——補在內層無效。**修法**：① `isOnMainQueue()` 由 `private` 改 `public nonisolated func`；② `withFileHandleQueueSync` 之第一關由在 corelibs 上形同虛設的 `if Thread.isMainThread` 換成 `if isOnMainQueue() { return try execute() }`（macOS 側行為不變）。`withFileHandleQueueAsync`／`readFileContentAsync` 走 async、block 必落別的 worker，無此互鎖，不動。`vChewing-OSX-legacy` 之 `withFileHandleQueueSync` 不 hop `mainSync`、亦無此互鎖，只對齊 `isOnMainQueue()` 之存取級別並在 doc 註明「本倉不應加掛那一關」。**本機驗收**：LibVanguard 6.4 側 **535 項 0 失敗**；三倉建置與格式管線皆過。**未驗**：本機無法複現（Darwin 上主佇列恆在主執行緒），故止崩只能靠 CI 判準——第二輪推上去後（run `35087157715`＝linux／`35087157691`＝WinNT，同 SHA `2b5b360a`）**兩平台全綠、`Program crashed` 計 0 次**（9 靶共 534 項；此前必崩之 `LexiconAssemblyTests` 為 193 項 30 套全綠）。**本項自此結清。** 附帶之同批改動：`TekkonTests` 之 `"[Tekkon] StringProcessingPerformance"` 門檻自 0.1 放寬至 0.2（`vChewing-LibVanguard` `caeaccc`／`vChewing-macOS` `3d7938a6`）——實測散佈：本機 0.016s／linux runner 0.034s／WinNT runner **0.1035 → 0.0560 s**（同一 runner 兩輪相差 1.85×），故 0.2 對最慢觀測值僅約 1.9× 餘裕、與 runner 自身抖動同量級；再遇 flake 宜升至 0.3。

### A2.2 開發注意事項

1. 始終保持對 Linux 與 Windows 的可建置性（透過 `#if canImport(Darwin)` 處理平台差異）。
2. TrieKit 不計畫直接支援 Regex Fuzzy Match；不完全讀音檢索需先經 Tekkon 的 `chop()` 拆解。
3. Homa 引擎取消了舊版 `LangModelProtocol` 協定，改用回調函式。
4. `LexiconAssembly` 不負責查詢結果的去重複化，該工作由 Homa 引擎完成。（Phase 213 前於本倉名為 `LexiconKit`。）
5. 下游 `vChewing_LangModelAssembly` 目前的預設 factory lookup 已由 `FactoryCoreLookupStrategy.configuredLookup` 表達；當 `partialMatchEnabled` 開啟時，這條預設路徑可走 partial-match path。`FactoryCoreLookupStrategy.strictSuperset` 則是獨立的 strict-superset strategy，不得將兩者混為一談。另在 plain BPMF / 倚天 DOS 與 cassette quick-result facade 上，`SupplementalLookupStrategy` 已明確區分 `.configuredLookup` / `.exactMatch` / `.partialMatch`；其中 `configuredLookup` 保留各 backend default，不等於強制 exact，也不等於強制 partial。Phase 36 結束後，repo 內唯一 canonical public lookup surface 已是 `LMInstantiator.lookupHub`；舊 `query*` / `cassetteQuickSetsFor` wrappers 已自 current tree 移除。若未來再做類似 breaking cleanup，請直接以 `Phase036_Research.md` appendix 內的 P5 gate 與 kickoff template 為範本。
6. **Phase 46 後 `&` 字串編碼已從 Homa ↔ LMInstantiator 介面移除**。`Homa.Assembler` 現以 `[PossibleKey]` 儲存每個位置的可能讀音，並在 `assignNodes` 內部以笛卡爾積展開為精確 `[String]` 陣列後呼叫 `gramQuerier`。Typewriter 不再產生 `&` 字串；TrieKit `keysChopped:` 仍保留內部 `&` 處理供自身 partial-match 路徑使用，但 Homa 傳遞至 `LMInstantiator` 的皆為精確陣列。
6. 下游測試 fixture 的 typeID 必須與 VanguardLexicon 建置器的實際 typeID 分配一致（Phase 09 教訓：`_punctuation_list` 等 `_` 前綴 key 在 production 為 typeID=4，fixture 誤標為 5/6 導致漏洞）。
7. 不要再把 Phase 35 理解成「回退到下游 `FactoryTextMapLexicon`」。那條路徑只屬中間驗證；最終 source of truth 是 canonical `VanguardTrie.TextMapTrie` 與 `VanguardTrieProtocol.getEntryGroups(...)`。
8. **`SwiftExtension` 符號之鏈接前提（2026-09-17，Phase 225 實錄）**：`SwiftExtension` 已析出為獨立 dynamic 產品 `VanguardSwiftExtension`，而 `libVanguard.dylib` 對它只有 `LC_LOAD_DYLIB`（**非 `LC_REEXPORT_DYLIB`**），且 SwiftPM 6.4 起之預設引擎（`swiftbuild`）**不代 dynamic 產品傳導其動態依賴**（舊 llbuild 引擎會代傳，故 6.3 世代不顯此坑）。故凡直接使用 SwiftExtension 符號之**靶**——**含只靠 `@_exported import SwiftExtension` 轉出、自身沒寫 import 者**——其 manifest 必須自行宣告 `.product(name: "VanguardSwiftExtension", package: "VanguardSwiftExtension")`（套件依賴之 `path:` 指 `../vChewing_OSNeutral_LibVanguard/Deps/VanguardSwiftExtension`），或至少鏈一個「已宣告它」的**靜態**產品（`IMKUtils`／`OSFrameworkImpl`／`InstallerAssembly4Darwin` 三家即已如此；靜態產品會把自身動態依賴往下帶）。只鏈 `Vanguard` 這一 dynamic 產品不足——`Jad_BookmarkManager` 即因此在 macOS CI 之 test 靶 link 期報 `Undefined symbols: SwiftExtension.mainSync…`（`mainSync` 於 `deinit` 內被呼叫）。另註：5.10 側之 `VanguardSwiftExtension` 是 `.static`，無此缺口。**本倉盤點（2026-09-17）**：全倉使用 SwiftExtension 符號者 15 家，屬「裸露形狀」（只鏈 dynamic 的 `Vanguard`、自身未宣告）者為 `Jad_BookmarkManager`／`vChewing_FolderMonitor`／`vChewing_UpdateSputnik` 三家——皆已補齊（6.4 ＋ 5.10 兩側各一檔）；其餘八家（`SettingsUI`／`MainAssembly4Darwin`／`Shared_DarwinImpl`／`CandidateWindow`／`NotifierUI`／`PopupCompositionBuffer`／`TooltipUI`／`Uninstaller`）係經**靜態**產品鏈獲得（`CandidateWindow` 為兩層：`Shared_DarwinImpl`→`IMKUtils`），惟這層安全性寫在**鄰居**的 manifest 內、不在自己的 manifest 內——改動上游依賴（尤其移除某家的產品宣告）前須重查此鏈。
9. **就地加詞／濾除之即時生效紀律（2026-09-17，Phase 226 實錄）**：寫檔後的就地生效唯一靠 `LXFacade.insertTemporaryData`；其後必須緊接 `InputHandler.updateUnigramData()`（順序顛倒即無效——熱重載（`.refreshExisting`）查不到尚未入庫的臨時資料）。凡新增查詢快取路徑，該路徑之快取鍵必須能被 `insertTemporaryData` 失效（現行作法是全量 `unigramLRUCache.removeAll`，因替代讀音路徑以 `ALT\t…` 定址、無法以 keyChain 枚舉）；凡在非同步重載前清空資料來源，必須確認該清除不會被「就地熱重載」撞上（現行作法：同步路徑照舊即清，非同步路徑延後至 `replaceData`／`onFailure`，且只清本次將重新載入者）。
10. **選字窗（`CandidateWindow`／`TDK4AppKit`）之範本 cell 定影陷阱（2026-09-19，Phase 231 實錄）**：`CandidatePool4AppKit` 的兩個**行程級靜態範本 cell**（`shitCell`／`blankCell`）之 `textDimension` 係 `CandidateCellData4AppKit.init` 依當時 `candidateListTextSize` 算好**存進 struct** 者，而 `updateMetrics` 只寫 `visualDimension`、不回寫 `textDimension`，故該值一經初次存取即在行程內定影。**凡須隨字級浮動之幾何量，一律即時讀 `CandidateCellData4AppKit.unifiedTextHeight`／`unifiedCharDimension`（或 `unifiedSize`），不得自範本 cell 取值**——GSI 捲動模式之視口高度即因 `lineStep` 自 `shitCell.textDimension.height` 取快照，而出現「橫向排版、縱向展頁時的最大高度不隨字級遞增」（字級 16 → 40 之實測：`unifiedTextHeight` 19.0 → 48.0 已更新，但 `lineStep` 23.0 → 23.0 未動、`pageCandidateSize.height` 92.0 → 92.0 未動，而真實版面已是 42.0／行、208.0／頁；`maxScrollOffset` 連帶失真為 220.0 而非 104.0）。**何以只在 GSI 之橫向排版顯病**：TDK（非捲動）之高度取自 `metrics.fittingSize`（實測幾何相加）、縱向排版之捲動視口量的是各列實測寬高，兩者必隨字級浮動；唯獨橫向捲動視口以 `lineStep × maxLinesPerPage` 這個**合成值**表達（「視口恆為整頁高、末頁不縮水」之設計意圖本身正確）。已修於 Phase 231（`lineStep` 之真源改為即時讀取）。**同源未修（2026-09-19 經事主澄清，已與兩項刻意設計分離；處置待裁）**：範本 cell（💩）之 `textDimension.width` 同屬「初次初始化即定影」之物，故**字級調小**時，由它導出的最小寬度（`minimumCellDimension.width`；單行橫排另含 `cellWidth(_:)` 之 `minAccepted`）不會跟著縮、甚至會蓋過刻意地板。**先排除兩項刻意設計**：① 單欄（vertical、單行）於字級 12 時之視窗寬約 76 係**故意**（`cellWidth` 之 `min = max(unifiedSize * 6, ceil(cell.size * 5.6))` ＝ 72，加 `originDelta * 2` 之 4 ＝ 76；實測 12／16／24 ⇒ 76.0／100.0／148.0 逐級等比，**隨字級即時浮動、非定影物**）；② 範本 cell 用 💩 且其字形比全形空白大，係 macOS 對 emoji glyph 之既有渲染行為（**不進入寬度算式**：範本之 `textDimension.width` 走的是與任何單字 cell 相同之 `ceil(unifiedCharDimension * 1.4)` 公式）。**隔離量測（唯一變因＝樣板何時定影；現行字級固定；完整表見 Phase 231 記錄之〈附註〉）**：現行字級 16 之橫排單行 ⇒ 樣板於 16 定影時 cell 寬 42.0、於 40 定影時 **76.0**、於 196 定影時 **297.0**；直排 4 列 ⇒ 56.0／**76.0**／**297.0**；直排單欄 ⇒ 96.0／96.0（被刻意地板遮蔽）／**297.0**。即**同一偏好下僅換定影時之字級即可數倍之差**（297 ＝ 字級 196 時 💩 樣板之 `ceil(206 * 1.4) + 8`）；**字級調大時此地板永不生效**（故日常看不出，僅「同一行程內把字級調小」方顯）。**事主 2026-09-19**：vertical layout（橫向展頁）於日常使用看不出毛病——與量測相符。
11. **Swift Testing 之 `#expect` 對混型別運算元誤報失敗（2026-09-19，Phase 231 實錄）**：`#expect` 面對運算元型別不一致的比較（如左 `CGFloat`、右 `Double`）會**報失敗而實為相等**。本機實測：`let cgValue: CGFloat = 52`、`let doubleValue: Double = 52` ⇒ 直接比較 `cgValue == doubleValue` 為 `true`，但 `#expect(cgValue == doubleValue, …)` 報 `Expectation failed`（兩側印出之值同為 52.0）；寫成 `#expect(cgValue == CGFloat(doubleValue), …)` 即通過。故測項內凡浮點比較，務必先把兩側對齊到同一型別。
12. **GSI 捲動模式之幾何紀律（2026-09-19，Phase 232 實錄）**：`VwrCandidateGSI4AppKit` 之捲動模式自有一套幾何（`fittingSize` 之捲動分支、`clipOrigin`、`drawOffsetX/Y`、`scrollerTrackRect`、`drawBottomFields(topY:)`、`findCell` 之命中點與視埠矩形），與非捲動模式所走之 `CandidatePool4AppKit.updateMetrics()`（`metrics`／`topPaneShift`）**互不相干**——捲動模式之 cell 幾何來自 `computeCandidateOnlySize()`（自 `(0,0)` 起排），故 `updateMetrics()` 之「全體 cell 下移」副作用**不會**在捲動模式發生。凡新增「固定在視埠上、不隨捲動移動」之內容（頂部 pane、未來之其他徽章），一律得四件並做：①在 `fittingSize` 為其留位（高 ＋shift、寬納入其寬）；②把候選區之六處幾何以同一位移下移；③在 `findCell` 之命中點與視埠矩形（含 cell 之 view 座標推算）同步扣除該位移——否則點選會偏移；④把該位移計入 clip path 之快取鍵（只比尺寸会在 pane 出現／消失時取到過期路徑）。**已修於 Phase 232**（頂部 pane——此前該 pane 於捲動模式下既不繪製、亦未留位）。
13. **選字鍵標籤之顯示區域為正方形（2026-09-19，Phase 232 定調）**：`CandidateCellData4AppKit.keyLabelBoxSide` ＝ 標籤自身之行高（`ceil(ascender + abs(descender) + leading)`），即標籤之顯示區域為「邊長＝行高」之正方形；`phraseDrawXOffset` 即該邊長（候選字詞自正方形右緣起排）、`headerDrawXOffset` 令標籤於盒內水平居中。**不得**回復為「橫向留白＝標籤字寬」（`ceil(0.6 × 字級)`）之舊制——那會令該區域成窄高形（約 1 : 1.95），且字級越大越明顯。cell 寬度另有「標籤盒 ＋ 候選字詞 ＋ 2 × padding」之硬約束（極大字級下舊算式本就容不下兩者——字級 196 時術前即超格約 10 點）。**標籤於其區域內之居中須為「墨跡光學居中」**：偏移 = `區域邊長 / 2 − CTLineGetBoundsWithOptions(line, .useGlyphPathBounds).midX`、**不得取整**（`ceil` 恆向上取整會令標籤偏 center-trailing，實測左右留白差可達 2.0 點）；**不得**改用 `[.useGlyphPathBounds, .useOpticalBounds]`（該組合回傳 advance 盒而非墨跡盒）。該正方形之設計讀法（**事主 2026-09-19 裁定**）：**顯示區域變寬至標籤行高**——標籤字級不動、候選字詞右移約 0.1 × 字級；**不得**改為「縮小標籤字級以求其盒成正方形」之另一讀法。**尾端內距與補償（2026-09-21，Phase 237 定調；2026-09-21 經事主實機目視定版）**：標籤右緣（連帶緊隨其右緣起排的候選字詞）右移之量 `keyLabelBoxSide − fontSizeKey`，**須由該格之總寬度一併吸收**（`updateMetrics` 內 `cellDimension.width += keyLabelBoxSide - fontSizeKey`）；且 cell 寬之硬約束須含**尾端**內距——`max(cellDimension.width, keyAndPhraseWidth + 6 * padding)`（＝**前端** 2 × padding ＋ 標籤盒 ＋ 候選字詞 ＋**尾端** 4 × padding ＝ 8 點）。**該約束之舊版只有前端那一份 2 × padding**，故標籤盒一變寬，被吃掉的便是尾端內距：實測（單行橫排、非 matrix）二字以上之候選字詞於字級 ≥ 40 時尾端內距**恰為 0.00 點**、單字候選亦逐級短少 2～21 點；**尾端內距之額度經事主實機目視比較定案**——先試 4 × padding 之約束（尾端 2 × padding）判為不足，今制為 6 × padding（尾端 4 × padding）；**不得**退回只含前端之舊式。**用語定調（事主 2026-09-21）**：`trailing inner padding` 一律作「**尾端內距**」（不寫「尾隨內距」）、其對稱者作「**前端內距**」。**凡改動標籤之顯示區域、`keyLabelBoxSide` 之取值或 `phraseDrawXOffset` 者，皆須同步檢查此二項。****相鄰未修（已量測、未動）**：橫排多行（matrix）路徑之 cell 寬由 `cellWidthMultiplied` 覆寫 ⇒ 不經該硬約束、亦不吃補償（實測中文候選之尾端內距 4.16～59.58 點，惟拉丁候選於字級 12 僅 0.92 點）；**事主 2026-09-21 目測裁定「沒什麼故障，先不動了」**——該路徑暫不處置，勿自行改造。
14. **單元測試中判讀離屏點陣圖之紀律（2026-09-19，Phase 232 實錄）**：**不得**直接讀 `NSBitmapImageRep.bitmapData` 之原始位元組並假設其通道序為 R,G,B——通道序隨環境（系統外觀、繪圖驅動）而異，會令墨跡偵測在 CI 上整列誤判（`testGSIScrollModeShowsTopPane` 即因此在 CI 上「首個有墨跡之列」兩側皆得 0、本機卻正常）。一律改用 `colorAt(x:y:)`（與通道序無關；值須除以 alpha 還原非預乘），且**底色須取「整張圖取樣後最常見之亮度」（眾數）**、不得賭單一像素；深淺色外觀皆須成立。本倉範式見 `TDK4AppKitTests.swift` 檔尾之 `OffscreenInkScan`。
15. **選字窗之外觀可覆寫（2026-09-19，Phase 232 之三）**：選字窗之外觀以 `TDK4AppKit.CandidateAppearance`（`Int` 原始值：`auto = 0`／`light = 1`／`dark = -1`）表示，**寄存於 `CandidatePool4AppKit.candidateAppearance`**（預設 `.auto`）；控制器另有 `appearanceOverride` 代理之。**jailed**：不經偏好設定、無設定介面，`CandidateAppearance.current` 僅模組內可見。兩條不變式：① `.auto` 於 **macOS 10.13 及以前一律解析為淺色**（深色模式係 10.14 引進）；② **系統外觀變更時須自動更新**——池註冊 `DistributedNotificationCenter` 之 `AppleInterfaceThemeChangedNotification`，收到即清「依外觀而異」之屬性字串快取（文字色／底色已烤進字串；不清即沿用舊外觀）。凡新增「依明暗解析之色」者，一律問 `CandidateAppearance.isDarkModeResolved`／`thePool.isDarkModeResolved`，**不得**各自去問 `NSApplication.isDarkMode`（否則覆寫失效）；凡新增長壽快取之色，須以明暗狀態為鍵（見 GSI 之高亮行底色）。**事主 2026-09-19 裁定**：所有選字窗之外觀只可能雷同，故模組層之 `current`（供 cell 靜態色用之共用解析通道）係設計如此，非缺陷。
16. **偏好「外部匯入」之推式副作用缺口，暨 IME 之 argv 陷阱（2026-09-24，Phase 239 研究實錄）**：① **`UserDef.importFromJSON(_:)`（`Sources/Shared/UserDef/UserDef.swift:258`）直接對 `UserDefaults.current.set(…)` 寫值、不經 `PrefMgr` 之 `@AppProperty` setter**，故 13 條帶 `didSet` 副作用之偏好一概**不觸發**（`didAskForSyncingLMPrefs` 之 8 個消費鍵：`userPhrasesDatabaseBypassed`／`cns11643Enabled`／`symbolInputEnabled`／`cassetteEnabled`／`suppressFactoryUnigramsOfKanaSyllables`／`useSCPCTypingMode`／`phraseReplacementEnabled`／`associatedPhrasesEnabled`；`didAskForRefreshingSpeechSputnik` 之 `readingNarrationCoverage`；`didAskForSyncingShiftKeyDetectorPrefs` 之兩條 Shift 鍵；另有 `candidateKeys` 之小寫化／去重／檢定，與 `candidateListTextSize`／`popupCompositionBufferTextSize` 之夾限）。既有兩條 import 路徑（設定畫面「開發道場」頁、CLI `--import-prefs-json`）之收尾皆只有 `PrefMgr.shared.fixOddPreferencesCore()`——**值域與 `candidateKeys` 之正規化已顧及、推式同步未顧及**。凡於 **IME 進程存活期間**由外部寫入偏好者（未來的 `vChewing://` 深層連結、或任何程式化寫入），一律須於其後補一次「和解」：`fixOddPreferencesCore()` ＋ **逐一對 13 條帶副作用之鍵自我賦值**（`prefs.x = prefs.x`）以觸發 `didSet` ＋ `UserDefaults.current.synchronize()`。須留意 `inputHandler.assembler.maxSegLength` 屬 `initInputHandler()` 重推者（`InputSession.swift:229,234`），非即時。② **`MainSputnik.handleVarArgs()`（`Packages/vChewing_MainAssembly4Darwin/Sources/MainAssembly4Darwin/MainSputnik.swift:69-127`）對任何未被辨識之 argv 皆回 `0`**（case 1 與 case 2 之 `default:` 之後皆 `return 0`，外層 `default: return 0`），而 `MainSputnik4IME.init()` 隨即 `exit(varArgsResult)`（`:24-26`）⇒ **多一顆不認識的命令列引數即令 IME 靜默 `exit(0)`**。今日無事係因系統正常啟動不帶引數；**凡新增依賴「行程能存活至 `applicationWillFinishLaunching`」之功能（如 URL scheme 之冷啟派送），須先確認該路徑之 argv**。③ 網頁／助手資產若置於 `vChewing-macOS/ValueAdd/`：該目錄是 Xcode 之 `PBXFileSystemSynchronizedRootGroup`（`vChewing.xcodeproj/project.pbxproj:143`）⇒ Xcode 會**自動列舉**其內容（實測 Release 產物內不含其內容，故不影響出貨；惟 `node_modules/` 動輒數萬檔會拖慢索引，宜於該同步群組之例外集內排除之）。**（2026-09-25 追加，見 `Research/Phase245-PostResearch.md` §2.7）**該群組之成員規則對 **`.swift`** 檔比對 `.ts`／`.mjs` 嚴重：`.ts`／`.mjs`／`.json` 對 Xcode 是「無編譯器之型別」，今日只被列舉與索引；而 **`.swift` 是一級原始碼型別**，故在 `ValueAdd/` 之下新增任何 `.swift` 檔**推論**會被納入 `vChewing` 靶之成員集並參與編譯（`RawImages/*.pxd` 之所以列於例外集即此機制之反證；**未以一次 Xcode 建置實測**）。實測補強：Xcode 之專案模型（`Build/Intermediates.noindex/XCBuildData/PIFCache/project/PROJECT@*`）確有列舉助手之檔案（型別 `sourcecode.typescript`）；全倉之同步根群組恰 **5 個**（`Plugins`／`vChewingIME_macOS`／`ValueAdd`／`Installer_macOS`／`vChewingDebuggable`），而 **`Scripts/` 與 `Tools/` 皆不在專案內**——故「把新工具放專案外」是可行之替代落點。SPM 側不受影響（`vChewing` 靶之 `path` 為 `./Sources/vChewingIME_macOS`）。④ **偏好 JSON 交換格式之保留前綴為 `__`（雙底線；不得用單底線 `_`）**：`UserDef` 之 118 條 rawValue 中**已有 2 條以單底線起頭之真偏好鍵**（`kIsDebugModeEnabled = "_DebugMode"`、`kFailureFlagForPOMObservation = "_FailureFlag_POMObservation"`），而**無一條以雙底線起頭**（`grep -c '= "__'` ＝ 0）。故日後為交換格式增設之根層中介鍵一律取 `__` 前綴——現行定案者為 **`__UserDefMeta`**（辭典型別，成員值皆 String：`title`／`description` 等）；實作時須令 **`__` 起頭之根層鍵一律無條件摘除**（故形狀異常者亦不落進逐鍵驗證而報 `Unknown key`），且 `exportAsJSON` 不輸出之。**連帶之命名紀律（事主 2026-09-24 明示；須明文寫入 `UserDef.swift` 之 `enum` doc comment、並以單元測試守住）：`UserDef` 之 rawValue 不得以 ASCII 雙底線 `__` 開頭**——否則該鍵會被上述之無條件摘除吞掉、**永遠無法匯入**（單底線 `_` 不在此限）。⑤ **術語（事主 2026-09-24 裁定）**：「Configuration Wizard／設定精靈」一詞**停用**（「Wizard」之兩岸歧義太重），改稱 **Configuration Assistant／配置助手**（簡稱「**助手**」，簡繁日通用——ja 亦作「助手」）；`ValueAdd/` 下之目錄亦隨之為 `WebConfigAssistant/`。同批裁定另有「偏好設定 → 一般設定」頁「我姓ㄅ」按鈕下方之「自剪貼簿匯入配置資料」按鈕（機理照「我姓ㄅ」之 `ActiveAlert` 兩段式），詳見 `vChewing-DevLogs/Research/Phase239_Research.md`。

   **（2026-09-24，Phase 240 已落地）**：上列 ① 之缺口已補——`PrefMgr.reconcileAfterExternalPrefsImport()` 落於 `Packages/vChewing_Shared_DarwinImpl/Sources/Shared_DarwinImpl/PrefMgr_Utilities.swift`，**四條匯入路徑**（設定畫面之檔案匯入／拖放、一般設定頁之剪貼簿匯入、CLI `--import-prefs-json`）皆已改走它（GUI 三路徑經 `PrefsExchange.applyPrefsJSONFromData`／`applyPayload`）；④ 之命名紀律已明文寫入 `UserDef.swift` 之 `enum` doc comment 並以 `Tests/SharedTests/UserDefExchangeTests.swift` 守住，且 `__UserDefMeta` 之解析／無條件摘除／差異計算（`diffAgainstCurrent`）皆已實作。**仍未動**：② 之 argv 陷阱（`handleVarArgs` 對未辨識引數回 `0` ⇒ IME 靜默 `exit(0)`）與 ③ 之 `ValueAdd/` 同步群組索引影響。**（2026-09-24，Phase 241 補記）**：`ValueAdd/WebConfigAssistant/` 已建立——③ 之憂慮（`node_modules/` 拖慢 Xcode 同步群組索引）**因該目錄採零 npm 相依而不成立**（`node_modules/` 自始不存在）。

17. **三則與「偏好值域」「macOS 版本」「格式管線」有關之陷阱（2026-09-24，Phase 241 施工實錄 ＋ 同日修畢）**：① **`UserDef.metaData.options` 必須落在 `validNumeralValueRange` 之內**——實測曾有三條鍵不然：`kSpecifiedNotifyUIColorScheme`（選項含 -1「淺色模式」，值域曾為 `0...2`）、`kForceCassetteChineseConversion`（選項含 3）、`kNumPadCharInputBehavior`（選項 0…5）。而 `validateAndApply` 對整數一律以該值域把關 ⇒ **連 app 自己匯出的偏好包都會被拒**（使用者於介面內選了那些選項、匯出後再匯入即失敗），且 `fixOddPreferencesCore()` 會把這些值靜默夾掉。**該缺陷已於 2026-09-24 修畢**：三條鍵之值域放寬為 `-1...1`／`0...3`／`0...5`（與其 `options` 一致），並以兩倉 `Tests/SharedTests/UserDefExchangeTests.swift` 之 `testEveryDeclaredOptionIsAcceptedByValidator`（通用不變式「選項 ⊆ 值域」）與 `testFormerlyMismatchedRanges`（絆線）守住。**凡日後新增選項者，值域須同步放寬**——否則該不變式測試即紅。② **macOS 版本不可用浮點比較**：`10.9` 在數值上等於 10.90、**大於** `10.15`——以 `Double` 比較會把 Catalina 判得比 Mavericks 還舊（助手初版即因此把 macOS 10.15 之使用者之幾乎所有選項誤判為「需要較新系統」而略過）。一律改用整數版本碼 `major × 100 + minor`，而後設資料之浮點 `minimumOS`（如 `10.15`）須**依其字面值之字串**拆位轉碼（`String(10.9)` ⇒ `"10.9"` ⇒ minor 9；若以 `(v - floor(v)) * 100` 取之則 10.9 得 90）。③ **`make lintFormatUncommitted` 只涵蓋「已追蹤且已修改」之 Swift 檔**（其清單取自 `git diff --name-only HEAD`）——**新建（untracked）之檔案不在內**，須另行顯式跑 swiftlint／swiftformat，並於其後複跑建置與測試。**另附兩條同批之教訓**：(a) CLI 既有之 `UserDef.isMetadataPendingManualUpdate` 曾對上列三條鍵**誤報**（其判準原為「鍵名是否恰等於 `i18n:UserDef.<case>.<field>`」）；已於 2026-09-24 修訂為「**凡以 `i18n:` 起頭者即為已遷移**」＋「值即標籤之數字不算欠譯」，`i18nKeyConvMap` 同步收斂（原會為數字標籤憑空生出 i18n 條目、汙染 `generate-missing-strings`），`dump-userdef-metadata` 之輸出自此不再有 `benignPendingMetadataKeys` 一欄。(c) **凡動 `SettingsUI`／`SettingsCocoa` 之曝露項者，須重跑 `make surface`**（`vChewing-macOS/ValueAdd/WebConfigAssistant/`）——助手之題庫以「設定介面曝露面」為界（事主 2026-09-24 立規：不是設定介面曝露給使用者的選項，就不該在助手裡出現），該面係以 `tools/settings-surface.mjs` 掃描那兩個目錄之源碼生成；未重跑即 `make audit` 之 `surface-check` 轉紅。另：助手之「深入說明 →」一律連官網絕對位址（`DOC_BASE`，預設 `https://vchewing.github.io/`）＋官網各篇之實際 `permalink`——**相對路徑在 `file://` 之下必為死鏈**。(b) **兩倉之 SwiftPM 測試不可並行跑**——本 phase 實測：並行時兩邊各出現大量**假紅**（`LibVanguardTests` 之 InputHandler 系列斷言失敗、其中一邊之測試總數僅報到 354），改為**逐一順跑**即兩邊皆 582／0、0 筆 `recorded an issue`。

---
19. **配置助手之建置鏈已免除 node 與 npm（2026-09-25，Phase 246 落地）**：整條鏈之外部相依**只剩 `tsc`**。**宿主**改用 macOS 內建之 **JXA**（`osascript -l JavaScript`）——`tools/host/` 四檔：`run.js`（入口；`osascript -l JavaScript tools/host/run.js <工具.js> [引數…] | --tests`）、`node.js`（node API 墊片）、`loader.js`（CommonJS 載入器）、`tests.js`（測試宿主）。**五支工具由 `tools/*.mjs` 改為 `tools/*.js` 並改用 CommonJS**（邏輯未變；`import.meta.url` → `__filename`、入口守衛 → `require.main === module`）；**五支測試檔與 DOM 替身一字未改**；`package.json` 已刪。**何以不用更快之 `jsc`**（`JavaScriptCore.framework/Versions/A/Helpers/jsc`；實測既有 78 支測試 0.138 s）：它缺三樣本鏈需要之物——**無目錄列舉**（`readFile` 對目錄直接拋錯）、**無子行程能力**（讀 `.plist` 用）、**無 argv**（傳入之引數會被當成待載入之檔案）。**`tsc` 必須是原生版**：npm 版之 `bin/tsc` 是 `#!/usr/bin/env node` 之啟動器（真正之原生檔在 `@typescript/typescript-<平台>/lib/tsc`）⇒ 用之等於仍依賴 node。故新增 **`make check-tsc`**（以「執行檔是否以 `#!` 起頭」判別，並為 `typecheck`／`build` 之前置），取得方式三條皆不需 node／npm（**推薦**：`registry.npmmirror.com` 之 `@typescript/typescript-<rid>` tarball，約 9 MB，與 npmjs 逐位元組相同）。**兩處非忠實之代償**（記於 `tools/host/node.js` 檔首）：`vm` 之 context 隔離以「全域求值後回填 `VCA`／`VCA_METADATA`」代償；`execFileSync('plutil', …)` 改以 `NSDictionary` 直讀。**驗收**：`make audit` rc=0（暖機 **3.98 s**；node 期 2.882 s）、**於 PATH 完全無 node 時 rc=0**、產物 **7／7 逐位元組相同**、五支工具輸出全同、78／78 測試（0.43 s）。**施工中四個坑**（皆首跑即現）：① `process`／`Buffer` 須裝上 `globalThis`（node 之此二者為全域）；② flush 若經由已被覆蓋之全域 `console` 會**自我吞噬**（跑完無輸出亦無錯）⇒ 須先留宿主原生之 log；③ `path.relative` 須完整實作，否則 `settings-surface.js` 對倉根以外之路徑求相對值會**假漂移**；④ 五支工具之入口守衛**形制不一**（僅 `es5guard` 用多行 `invokedPath`），須逐支改。研究全文見 `vChewing-DevLogs/Research/Phase245-PostResearch.md` §7.10／§7.10.1。**追加（同日）：助手之產物會收錄進輸入法之 main bundle**——`ValueAdd/WebConfigAssistant/tools/embed-into-bundle.sh <vChewing.app 路徑>` 為三條建置路徑共用之腳本，落點 `Contents/Resources/assistant/assistant.html`（**收錄範圍經事主 2026-09-25 補示收斂為「只 `assistant.html`」**——單檔自足、CSS 與 JS 皆已內聯，故 `dist/index.html` 不收）。**唯一的閘是「`tsc` 是否在 PATH」**：未偵測到即印警告、`rc=0`；編譯失敗亦警告續行——**絕不中斷輸入法之建置**。三處呼叫點：`BundleApps/plugin.swift` 與 `BundleAppsLegacy/plugin.swift` 各自新增之 `embedAssistant`（皆於 `assembleMainIMEApp` 之 **`codesign` 之前**；故 `make debug`／`release`／`archive` 與 `debugLegacy`／`releaseLegacy`／`archiveLegacy`／`bundleLegacy` 皆涵蓋），以及 `vChewing.xcodeproj` 之 `vChewing` 靶上新增的 `PBXShellScriptBuildPhase`（`5B2A55E72F4C0001006B48E8`）。**何以在 plugin 內而非 Makefile 之後補做**：`--archive` 會在同一趟 plugin 內完成組裝與封存，事後補做會漏掉 `.xcarchive`；且簽章會封印資源，故必須在簽章之前。實測：`make debug` rc=0、`codesign --verify --strict` 仍有效、兩檔與 `dist/` 逐位元組相同；legacy 側同上。**已知障礙與其真因**：本機之 `xcodebuild … -scheme vChewing` 因 package plugin 驗證失敗而 rc=65（**在任何 build phase 之前**；已以暫撤改動重跑實證為既有問題）。**真因**（自 Xcode 之 `xcactivitylog` 取出）：`Plugin "VanguardTextMapPlugin" … was disabled because it has changed (previous fingerprint was …)`——**Xcode 之套件 plugin 信任機制**在套件更新、指紋改變後停用該二 plugin，須在 **GUI 中一次性重新信任**；命令列無從核准。**兩個已排除之假線索**：① `~/Library/Developer/Toolchains/` 之重複 toolchain symlink（暫移後警告消失但失敗相同）；② `defaults write com.apple.dt.Xcode IDESkipPackagePluginFingerprintValidating -bool YES`（實測無效、已復原）。故 Xcode 端到端未驗。**另一項施工所得**：`BundleAppsLegacy` 之 `run(_:arguments:)` 與現代側不同——它把子行程輸出收進 Pipe 再回傳，故呼叫端**必須自行印出**，否則腳本之警告會被吞掉。
20. **工具層之截斷防護（2026-09-25，Phase 245 施工事故之後增設）**：**事故**——以手寫 Python 就地改檔時，一行無心的 `io.open(path, "w")`（`"w"` 於**開檔當下**即截斷、其後未寫入）把 `ValueAdd/WebConfigAssistant/src/questions.ts`（600 餘行）清成 0 bytes；同一輪內發生**兩次**（第一次以 `git checkout` 救回、第二次由 `make typecheck` 之成堆「Cannot find name …」抓到）。**危險在於靜默**：截斷當下毫無徵兆，要等下一個讀它的工具才引爆；若該檔其時無任何工具在讀，就可能一路帶進 commit。**防護（`vChewing-DevLogs/Tools/`，工作區根部有同名 symlink）**：① **`check_integrity.py`（絆線）**——以 `git ls-tree -r -l HEAD` 一次取齊各 blob 之大小，與工作區逐檔比對：`HEAD` > 0 而工作區為 0 bytes ⇒ **CRITICAL**（exit 1）、較 `HEAD` 縮小逾 70% 且逾 200 bytes ⇒ **WARN**、已刪除者僅列出；一次掃 1400 餘檔在彈指之間。**已裝為六個倉之 `.git/hooks/pre-commit`**（`--install-hooks`；`SKIP_INTEGRITY=1 git commit …` 可略過），故任何一次 commit 之前都會先驗。② **`safepatch.py`（安全改檔）**——`patch_file()`／`write_text()`：先讀全文、在記憶體裡替換、確認合理，才以「同目錄臨時檔 ＋ `os.replace`」（原子）換上；三道守衛為「錨點須恰出現 `count` 次」「結果不得為空」「不得較原文縮小逾 75%（除明示 `--allow-shrink`）」，任一不通過即**不寫入、原檔分毫未動**。兩支皆有 `--self-test`（紅綠雙驗：完好檔綠、截斷檔 CRITICAL、大幅縮減 WARN、刪除僅列出；正常替換綠、三道守衛各自拒寫且原檔不動）。**AI agent 之紀律**：就地改檔一律走 `safepatch.py`，不要手寫 `open(..., "w")`——`"w"` 是「我要寫」與「現在就清空」之合體，語意與意圖分離正是事故之源；一整輪 patch 之後跑一次 `python3 check_integrity.py`。


## 九、關鍵檔案速查

| 檔案路徑 | 說明 |
|----------|------|
| `Package.swift` | SPM 套件定義（package name `LibVanguard`、出貨 product `Vanguard`） |
| `makefile` | `make lint` / `make format` / `make lintFormat` / `make lintFormatUncommitted` / `make test` / `make dockertest` |
| `EVOLUTION_MEMO.md` | 各模組研發備忘錄（人工維護） |
| `.github/workflows/test_{ubuntu,winnt,darwin}_LibVanguard.yml` | CI（Phase 213 新增；倉根直接 `swift test --no-parallel`） |
| `Sources/Homa/Homa_MainComponents/Homa_Assembler.swift` | 組字核心引擎（Phase 05：跨插入 gram query cache / 熱路徑去 allocation） |
| `Sources/Homa/Homa_MainComponents/Homa_PathFinder.swift` | 動態規劃路徑搜尋 |
| `Sources/Tekkon/Tekkon_SyllableComposer.swift` | 音節合成引擎 |
| `Sources/TrieKit/VanguardTrie_Core.swift` | Trie 核心資料結構 |
| `Sources/TrieKit/TrieProtocol.swift` | Trie 共用查詢邏輯（Phase 35：`getEntryGroups(...)` / existential fast path） |
| `Sources/TrieKit/TrieTextMap_Core.swift` | TextMapTrie canonical specialized backend（Phase 35） |
| `Sources/TrieKit/VanguardTrieIO.swift` | Trie IO（Vanguard Pragma TextMap 序列化/反序列化 + 結構驗證） |
| `Sources/TrieKit/TK_QueryBuffer.swift` | 7 秒動態清理查詢快取 |
| `Sources/LexiconAssembly/LXFacade.swift` | 辭典查詢門面（原 `LMInstantiator`／`LMI`） |
| `Sources/LexiconAssembly/LX_GramConcatAPI.swift` | 元圖查詢結果聚合（構造化排序 / 具型雜湊） |
| `Sources/LexiconAssembly/LXGramSupplyHub.swift` | 多來源元圖供應中樞（Phase 212） |
| `Sources/LexiconAssembly/SubLMs/LXPerceptor.swift` | 使用者習慣洞察器（POM；原 `Perceptor`） |
| `Sources/LibVanguard/` | 作業系統中立層（輸入控制器與狀態機；原 `OSNeutralAssembly`） |
| `Tests/LexiconAssemblyTests/` | POM 測試族之大本營（含本倉獨有之 `POMDecayWindowTests.swift`／`LXPlainBopomofoEtenDOSTests.swift`） |
| `vChewing-macOS/ValueAdd/WebConfigAssistant/` | 配置助手（Phase 241；**Phase 246 起免除 node／npm**）：TypeScript ＋ JXA 宿主、外部相依只有 `tsc`（**須原生版**）、單檔自足 HTML；入內跑 `make audit`／`make bundle`；建置與部署細節見該目錄之 `README.md` |
| `Sources/vChewingSharedCLI/VCSharedCLI_UserDefMetadata.swift` | `dump-userdef-metadata` 動詞（Phase 241）：導出 118 條 `UserDef` 之後設資料與四語系標籤，供助手防漂移；`--strict` 為 i18n 稽核 |

---

## 十、建置與開發

### 10.1 建置要求

- **Swift 6.4+ 是硬性下限**。取得方式二選一：**Xcode 27+**（需 macOS 26.6 以上）；或 **Xcode 26.x**（Intel Mac 能用的最後一代）＋ 另裝 **Swift 6.4+ open-source toolchain**。請用正式發行版 Xcode、最小子版本號越高越好（RC 版另做相容性測試）。
  - **Xcode 無法用另裝的 open-source toolchain 來解讀 Swift Package**（套件解析固定用自己內建那條）⇒ Intel Mac（Xcode ≤ 26.x、內建 Swift < 6.4）**已不能以 Xcode 建置本倉**，只能走 SwiftPM CLI（`make spmDebug`／`make release` 一類）＋ 6.4+ toolchain；Apple silicon 不受影響。
  - **6.2／6.3 是封堵對象**：各套件皆備 `Package@swift-6.2.swift`／`6.3.swift` 兩份 `#error` 封堵檔，該兩版 toolchain 會被明文拒絕——那兩版會對「default-isolation 之下游遵循上游協定」強制索求明文 `@MainActor`（`#ConformanceIsolation`），本倉閉包在該兩版下**無可用的產物形態**（另見 `Phase216_PostResearch.md` §13.6）。
  - **另裝 toolchain 時 SDK 世代要對**：Xcode 27 自帶的 macOS 27 SDK 內含「只用得了 6.4 以上編譯器」的 `.swiftinterface`，不可拿 6.2／6.3 系 toolchain 去配它。
  - **想在 macOS 27 之前的系統上以 6.4+ 編譯**（例如末代 Intel MacBook Pro 13-inch）：讓當前 shell 用上 6.4+ toolchain **是使用者自己的責任**。Swiftly 是可行路徑，但其 shell 環境配置繁瑣、且會把原本裝在系統根目錄的 FOSS toolchain 全部改裝進 user-space（macOS 26 上可用）；最高只能跑到 macOS 15 者，Swiftly 可能裝不進 user-space，只能以管理員權限手動安裝官方 `.dmg`／`.pkg` 到系統根目錄，並自行按需改 `makefile`。
  - **本倉不提供 `build640` 這類「鎖定 Swift 版本號」的建置入口**——Swift 每發一版就得回頭把所有 `makefile` 修一遍；建置入口一律以「當前 shell 的 `swift`」為準。
- 出貨 runtime 目標 **macOS 12+**（`platforms: [.macOS(.v12)]`；5.10 legacy 側為 `x86_64-apple-macosx10.9` 之靜態 `.a`，其 toolchain／SDK／部署目標之三方配對見 §10.5）
- **預設建置引擎自 Swift 6.4 起翻轉為 `swiftbuild`（Swift Build）**：產物佈局自 `.build/<triple>/<config>` 變為 `.build/out/{Products,Intermediates.noindex}/…`（`--build-system native` 可退回舊 llbuild 引擎，但已標 deprecated）。**兩個實務後果**：① 凡寫死舊佈局路徑之腳本／plugin 皆須復查；② 新引擎**不為 dynamic 產品傳導其動態依賴**（舊引擎會代傳）——見附錄二 A2.2 第 8 條。

### 10.2 建置指令

```bash
swift build
```

### 10.3 測試指令

```bash
make test          # Release 模式測試
make test-debug    # Debug 模式測試
make dockertest    # Docker 容器測試（Linux）
```

> **SwiftPM 之測試一律附 `--no-parallel`——這是必需條件、非偏好（事主 2026-09-24 再次明示）**：本倉各靶之測試共用 `UserDefaults` 等行程內靜態狀態，並行執行即互相搶奪其 I/O 與狀態（macOS 倉 `Makefile` 之 `test:` 目標註解、以及各套件 `makefile` 皆已記明）。另依 §12.6：本工作區之 SwiftPM 執行一律附 `--disable-sandbox`（SwiftPM 之內層 sandbox 與 harness 之 sandbox 不疊加）。

> **兩顆 `swift test` 不得同時跑——`--no-parallel` 只治「同一行程內之各靶」，不治「兩個行程共用同一批 `UserDefaults` 網域」（2026-09-25 實錄；事主指出此誤兩個月內已不止一次）**：`UserDefaults.unitTests` 之**預設值即 `UserDefaults(suiteName: "UnitTests")`**（`Deps/VanguardSwiftExtension/Sources/SwiftExtension/SwiftFoundationImpl.swift:186-188`），而各測試 suite 之 `init` 又把它改指向各自的具名 suite（如 `org.atelierInmu.vChewing.LibVanguard.SessionTests`）；**具名 suite 係落在磁碟上的 plist（`~/Library/Preferences/*.plist`）、跨行程共用**，且 `UserDefaults.current` 於 `pendingUnitTests` 為真時即取用之（同檔 `:179-181`）。故同時跑兩顆 `swift test`（典型：`vChewing-LibVanguard` 與 `vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard` 各一顆）時，兩個行程會互搶同一批偏好檔。**受害表象**：`LibVanguardTests` 中「先 `UserDef.resetAll()`、再斷言打字結果」之 session／candidate／狂拼測項成群失敗（`state.candidates.isEmpty`、`displayedText` 不符、`hasComposition` 為假…），且**每次失敗的測項都不同、單獨重跑即全綠**。**判別法**：凡見此類成群且跨次游移之失敗，**先停掉其它一切測試、單獨重跑該倉**；單獨跑綠即屬偽陽性，不得據以改碼或改資料。**紀律**：同一時間只跑一顆 `swift test`（不與另一倉、不與 Docker、不與「以本機代跑之 CI 靶」並行）；`--no-parallel` 與本條**互不替代、缺一不可**。**何以須記入本文檔**：同款記載原僅見於 `DevReqsHistory.md` 之 Phase 241 條末（「工具層教訓：兩倉之 SwiftPM 測試不可並行跑…其中一邊之總數僅報到 354」）——歷史檔不是開工前會讀的地方，故未能阻止重犯（2026-09-25 又犯一次）。相關之同源陷阱（單一行程內 reset 順序不當造成 stale `cassetteEnabled`）另見附錄二〈LMAssembly 共用 parser / cell tokenizer〉條末之註記。

> **配置助手之建置與測試（2026-09-24，Phase 241 起）**：於 `vChewing-macOS/ValueAdd/WebConfigAssistant/` 內跑——`make audit`（提交前總檢：`tsc --noEmit` ＋ ES5 守衛 ＋ 測試宿主 `--tests`（**78 支**；數目隨 phase 增長，此為 Phase 246 之現值）＋ `make metadata`（後設資料防漂移）＋ `make metadata-audit`（`--strict` i18n 稽核）＋ `make fixtures-check`（契約 fixture 防漂移））、`make bundle`（產出單檔 `dist/assistant.html`）、`make metadata-update`（Swift 側 `UserDef` 有變時，重新導出後設資料並入庫）、`make deploy`（複製產物進官網倉；`DOC_BASE`／`DEPLOY_SUBDIR` 可覆寫）。**零 npm 相依**——不需 `npm install`、`node_modules/` 自始不存在。**註**：`node --test` 之引數須為**檔案 glob**（`tests/*.test.js`）；Node 22 之下傳目錄（`tests/`）會以「找不到模組」失敗。

### 10.4 程式碼格式化

```bash
make lintFormatUncommitted  # 交差／commit 前慣用：僅對 tracked 且未 commit 的 Swift 檔依序執行 lint＋format
make lintFormat             # 全倉：SwiftLint 自動修正（先）＋ SwiftFormat（後）
make lint                   # 僅 SwiftLint 自動修正
make format                 # 僅 SwiftFormat（縮排 2 空格）
```

> 交差前「一次性運行」 `make lintFormatUncommitted` 即可（先 lint 後 format 的順序已內建）。注意 lint+format 可能將 `count == 0` 轉為 `.isEmpty`，需確認對應型別確有此屬性，否則改用 `.count * 1 == 0`。

### 10.5 雙 toolchain 建置（Swift 5.10 legacy 側；Phase 216 起、**Phase 217 擴及全倉**）

本倉**同一份 `Sources/`** 同時具備兩套建置能力：6.4+ 側即 §10.2／§10.3 之 `swift build`／`make test`（產物 `libVanguard.dylib`）；5.10 側供 macOS 10.9 之 legacy 靜態庫，走下列目標（產物 `libVanguard.a`／`libVanguardSwiftExtension.a`）：

```bash
make build510               # 聚合體：libVanguard.a（14 MB）
make build510SwiftExtension # 只建置巢狀子套件（SwiftExtension 模組本身）：libVanguardSwiftExtension.a（540 KB）
make clean510               # 清兩條 scratch
```

**三項環境配對缺一不可**（`makefile` 內之 `LEGACY_*`，可用 `?=` 覆蓋）：

| 項 | 值 |
|---|---|
| toolchain | open-source `swift-5.10.1-RELEASE` toolchain（`LEGACY_TOOLCHAIN`） |
| SDK | Xcode 15 的 `MacOSX13.3.sdk`（`LEGACY_SDK`） |
| 部署目標 | `x86_64-apple-macosx10.9`（`LEGACY_TRIPLE`）；另 scratch 分兩條：`.build/.legacy`（聚合體）與 `.build/.legacy-swiftExtension`（子套件） |

**兩個硬事實**：

1. **Xcode 27 的 SDK 對 5.10 不可用**——`MacOSX27.0.sdk` 配 5.10.1 toolchain 會得到 312 個掩蓋式錯誤（`unknown argument: '-target-arch-variant'`、`could not build module 'Darwin'`），且 `swift package dump-package` 在該 SDK 下**照樣成功**——故「manifest 載得動」不足以證明該 SDK 可用。
2. **部署目標之有效手段**——SwiftPM 會吞掉你想壓低的部署目標（`--triple` 之版本段被丟掉、`platforms:` 亦被抬到 toolchain 地板），唯一有效之手段是 `-Xswiftc -target -Xswiftc x86_64-apple-macosx10.9`。早前之「`10.9` 不可用、因 `Data` 標為 macOS 10.10 起」一說已經重測推翻（2026-09-16），見 §十。

> 5.10 側之 manifest（`Package@swift-5.10.swift`——Phase 216 先在聚合體與子套件各鋪一份，**Phase 217 起 `vChewing-macOS` 之 19 個 subpackage 各一份**）刻意**不宣告測試靶**、**不收 `vChewingSharedCLI`**、**`platforms: nil`**，產物一律 static；`Package@swift-6.0.swift`／`6.1.swift`（自 Phase 217 起另含 **`6.2.swift`／`6.3.swift`**）為 `#error` 封堵檔（令各該版 toolchain 明文拒絕建置）。擇定規則與其餘坑見 `vChewing-DevLogs/Research/Phase216_PostResearch.md` 與 `Phase217_SOP.md`。

#### 10.5.1 Phase 217：`vChewing-macOS` 全倉（19 個目錄）的逐包入口

**每個 subpackage 都自成一個可單獨驗證的單位**——各自六份 manifest（`Package.swift`@6.4 ＋ `Package@swift-5.10／6.0／6.1／6.2／6.3`）與**各一份 `makefile`**：

| 入口 | 用途 |
|---|---|
| `cd Packages/<name> && make build510` | **單包深挖**（產物落該包自己的 `.build/.legacy`；`make clean510` 清之） |
| `cd Packages && make build510-all` | **全倉批次**：逐包跑、個別失敗不中斷、逐包列 ✓／✗（`make clean510-all` 清全部分支） |
| `make build510-<目錄名>`（倉根 `Makefile`） | 同上的單包快捷；`make build510-swiftExtension` 走巢狀子套件 |

**性質**：這是**可建置性驗證（compilation test）**，**不是單元測試**——5.10 側的 manifest 與 makefile **刻意不含任何測試靶／測試目標**；測試一律在 6.4 側跑（§10.3）。

**5.10 側的原始碼層原則（P217 貫徹）**：SwiftUI 之任何內容——**含 `#Preview` 這類巨集**——一律整段圈進 `#if compiler(>=6.2)`；`nonisolated` 自 extension／型別標頭**下放到成員**；availability 用 `if #unavailable() {} else {}` 兩分支；`nonisolated deinit` 改樸素 `deinit`（內容以 `mainSync` 裹上）；`@Sendable` 閉包內不得碰 MainActor 成員（legacy 形狀為 `DispatchQueue.main.async { @MainActor in … }`）；**不得為消錯新增 `@MainActor`**（會殺死 ≤ macOS 10.14 的執行期相容性）。

**終點與驗收**：兩支終點產物 **`libInstallerAssembly4Darwin.a`（3.2 MB）** 與 **`libMainAssembly4Darwin.a`（26 MB）**（`file` → `current ar archive`、`vtool` → `not mach-o`，即不帶任何 load command、minOS 不進產物）；`make build510-all` 於 2026-09-15 達 **19／19 rc=0、0 error**，6.4 側 `swift build` rc=0＋**535 項測試 0 失敗**。

**現值一項例外（2026-09-16）**：`vChewing_MainAssembly4Darwin` 之 5.10 manifest 依事主指示**改回與 `Package.swift` 同構**（收遠端 `vChewing-VanguardLexicon` 依賴與兩支 build plugin），故**該包於 5.10 側復歸 rc≠0、全倉 18／19**——5.10 SwiftPM 對非根套件的 `unsafeFlags` 一律硬拒（該 lexicon 的 `CSQLite3` 靶帶 `.unsafeFlags(["-w"])`），`--disable-sandbox` 無效、改本地 `.package(path:)` 則撞 macOS 10.15 平台下限；**正解在 lexicon 倉**（見 `Phase217_SOP.md` §十四 **N4**）。

**本項已由 P218 接管（2026-09-16）**：lexicon 之 deploy 工具真正用上 Swift Concurrency（故其 manifest 須宣告 macOS 10.15），與本側 5.10 之 10.13 地板相衝；現行作法是 5.10 manifest 不再收該依賴與兩支 plugin（`make build510-all` 因而復歸 19／19 rc=0），「另尋資料注入他法」移入 P218——原因、實測與後續見 P218 之紀錄。（此補註同時取代上方「現值一項例外」所述之狀態。）

**Swift 6.2／6.3 之封堵（Phase 216 起、Phase 217 補齊）**：五個位置各鋪兩份 `#error` 封堵檔（兩倉 12 組 manifest 逐位元組相同），`Package.swift` 之 tools version 抬到 **6.4**，三系統 CI 之 toolchain pin 同批抬到 ≥6.4。**封堵訊息之正本模板**見 `Phase217_SOP.md` §十二 R22 末段（46 份封堵檔同構）。**測試紀律**：`swift test --no-parallel`（CLI 層）與 `@Suite(…, .serialized)`（型別層）**缺一不可**，且單元測試下 `LXFacade.asyncLoadingUserData` 恆為 `false`——見同 SOP §十二 R23。

#### 10.5.2 雙 toolchain 之終點推進（Phase 218 起）

5.10 側自此**真的產出可交付的執行檔**：倉根 `Package@swift-5.10.swift` 出 `vChewing` 與 `vChewingInstallerLegacy`。

- **libArcLite**：以 `-Xlinker -force_load -Xlinker ./LegacyZone/ARCLite/libarclite_macosx.a` 摻入（`-L` ＋ `-larclite_macosx` 實測為虛——`ld` 逕以 SDK 版 libobjc 之匯出滿足符號、**不抽任何成員**；swift driver 亦不認裸 `-force_load`）。**只有 x86_64 支線**摻它（arm64 自 macOS 11 起 ARC 執行期即在 libobjc 內），故該 flag 依 triple 下在倉根 `makefile`。
- **執行期（兩段式 rpath）**：載入記錄保持 `@rpath/libswift*.dylib`，由 `BundleAppsLegacy` 把 Xcode 內 `usr/lib/swift-5.0|5.5/macosx` 之 back-deployment 副本放進 `<build-dir>/Frameworks/` 並追加 `@loader_path/Frameworks`——現行 macOS 之 `/usr/lib/swift/*` 由 dyld shared cache 供貨、故系統執行期勝出，10.9–10.13 才落到內嵌副本。**勿**改用 `install_name_tool -change` 逕指內嵌副本：那會令現行系統也載入 10.9 版本而 abort。該 plugin 另以 `pruneForeignRPATHs(of:)` 清掉建置機 toolchain 的絕對 `LC_RPATH`（`…/swift-5.10.1-RELEASE.xctoolchain/…`），只留 `/usr/lib/swift`、`@loader_path*`、`@executable_path/../Frameworks`。
- **入口與環境**：`make debugLegacy`／`releaseLegacy`／`archiveLegacy`／`cleanLegacy`（scratch `.build/.legacy-root`）；`releaseLegacy` 另建 arm64 slice 並逐支 `lipo` 成 universal（`x86_64-apple-macosx10.9` ＋ `arm64-apple-macosx11.0`）。`DEVELOPER_DIR` **必須 pin 一個「預設 macOS SDK ≤ 14.x」的 Xcode（Xcode 15 即可，任何 ≤ 15.4 者等價）**——這是 `swift build` 一併編譯的 build plugin `BundleAppsLegacy` 之 SDK 來源（`--sdk`／`SDKROOT`／`-Xswiftc -sdk` 三者對它**皆無效**，實測 plugin 之 `commandLine` 記的仍是 active dev dir 的預設 SDK）；CLT 不能當 dev dir（無 `Platforms/`），自製 dev dir 會被 `xcode-select` 判 malformed。C／ObjC 靶另須 `-Xcc -target -Xcc x86_64-apple-macosx10.9`（`-Xcc -mmacosx-version-min` 會被 SwiftPM 自己那條 `-target …10.13` 壓住；clang 讓後出現的 `-target` 勝）。`LEGACY_SDK` 綁 **CLT 那份** `/Library/Developer/CommandLineTools/SDKs/MacOSX13.3.sdk`（Xcode 15 內的同名目錄只是指過去的 symlink；該 SDK **非現行 CLT 所附**——現行 CLT 已把它改成移除包，換機須自行自 macOS 13.3 之 CLT／Xcode 14.3 備妥）。
- **`archiveLegacy`（2026-09-17 補）**：前置 `releaseLegacy`，再令 plugin 以 `--archive` 組出 `Build/Products/vChewingInstallerLegacy-<stamp>hrs.xcarchive`（內含安裝程式（IME 棲於其 `Contents/Resources/`）與兩支執行檔之 dSYM，外加 `Info.plist` 之 `ArchiveVersion`／`ApplicationProperties`），並搬進 `~/Library/Developer/Xcode/Archives/<date>/` 供 Xcode Organizer 手動以 Developer ID 簽名與公證；archive 之所以不直接寫進那裡，是因為 command plugin 之寫入權止於套件目錄。
- **10.9 專屬陷阱**：① **絕不可把 Optional block 交給 libdispatch**——`setEventHandler(handler: nil)` 會被本路徑內建的 Swift 5.0 Dispatch shim 原樣轉成 `dispatch_source_set_event_handler(source, NULL)`，而 10.9 的 libdispatch 對此直接 BUG（SIGILL）；一律改傳 `{}`（現代 libdispatch 容忍 NULL，故 6.4 側從未顯露）。② 辭典資產**自動建置**：`lexiconLegacy` 是 `bundleLegacy` 之前置、跑 `LegacyZone/LexiconBuildTrigger`；其 config 變數是 `LEXICON_CONFIG`（預設 `release`）、**刻意不叫 `LEGACY_CONFIG`**（後者指 app 的 config 且會隨 sub-make 外洩，實測會把詞典建置拖回 debug）。③ `CGRect.seniorTheBeast` 這類跨模組常數一律是各消費檔**檔尾的 `fileprivate` 常數**、不放 `SwiftExtension`（Swift 5.10 `-O` 對跨模組 `CGRect` 常數會 SIL verifier 崩潰）；`vChewing-OSX-legacy` 逐檔同構。
- **concurrency**：整個 5.10 閉包**零 concurrency 引用**（每 slice 20／20 archive 乾淨、兩支執行檔無 `swift_task_*` 未定符號），`@rpath/libswift_Concurrency.dylib` 不再是任何載入記錄；`BundleAppsLegacy` 仍整批備齊該副本，屬未被引用的死重（事主 2026-09-16 裁定不用管）。
- **lexicon 無法被 5.10 側消費**：其 deploy 工具真正用上 Swift Concurrency（需 macOS 10.15），故 `MainAssembly4Darwin` 之 5.10 manifest 不收它——資料改由 `LegacyZone/LexiconBuildTrigger` 這一 throwaway 套件出帶外產出，再由 plugin 注入安裝程式之 `MainAssembly4Darwin_MainAssembly4Darwin.bundle`（`Bundle.currentSPM` 解析的即該 bundle）。
- **legacy 安裝程式的在地化名稱**：與主線共用同一份 `<lproj>`，故 Finder 顯示名原與主線相同；解法是 `LSHasLocalizedDisplayName`（兩側 plist 本已帶）＋ `LegacyZone/InstallerLocalizations/<lproj>/InfoPlist.strings` 的不同 `CFBundleName`，由 plugin 於複製 lproj 後 **merge**（非取代——`CFEULAContent` 必須存續）；IME 側對位者為 `LegacyZone/IMELocalizations/…`（把 `NSHumanReadableCopyright` 改寫為 `Aqua Special Build. …`，供 About 面板顯示）。落點刻意選在 `LegacyZone/`：`Sources/Installer_macOS/` 在 `vChewing.xcodeproj` 裡是同步根群組，把帶 `.lproj` 的新目錄放其下會被掃進**現代**安裝程式的資源 phase。`project.pbxproj` 事主明示**不動**。
- **現況（2026-09-17）**：10.9 真機之輸入法本體運作正常；安裝程式在 10.9 按「安裝」數秒即崩之缺陷已修（見上①）、**修後之 10.9 複驗尚未回報**；10.10／11.x 真機仍未驗。legacy 產物之總記憶體佔用實測**降至 macOS 15 Sequoia／Intel Mac 之水位**（開著偏好設定視窗亦僅 80 餘 MB），機理未查。**本路徑自此為 legacy 發行版之唯一建置來源**——`vChewing-OSX-Legacy` 已於 vChewing **4.8.0** 封存（僅存為 10.9 寫法之參照、不再回寫）。

## 十一、參考資料

- 詳見 `vChewing-DevLogs` 目錄的其餘 Markdown 檔案。
- `vChewing-LibVanguard/EVOLUTION_MEMO.md` 記錄了各模組的原始設計備忘錄。

---

> ⚠️ **注意**: 本文檔為 LLM 用的「格物致知」文件——只承載**現況**與**施工注意事項**。**最後更新：2026-09-25。**
>
> **沿革不再寫入本文檔（2026-09-17 修訂）**：逐 Phase 的施工記述一律見 `vChewing-DevLogs/DevReqsHistory.md`（逐 Phase 一行摘要）與 `vChewing-DevLogs/Reqs4LLM/Archive_P{…}/Reqs_0NN1-0NN0.md`（規格與實作全文）。先前於此逐 Phase 累積的長篇「最後更新」記述（Phase 201~223）已移除——那些內容本即 `DevReqsHistory.md` 各列的複寫，需要舊敘述時請看本檔的 git 歷史。此後本文檔只增刪「現況」與「施工注意事項」兩類內容。


---

## 十二、AI Agent 反應模式（Response Pattern）

> 本節供 AI Agent 參考，當用戶提出新的 Phase 開發任務時，應遵循以下標準流程。

### 12.1 工作流程（Workflow）

當用戶提出新的 Phase 需求時，按以下順序執行：

```
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: 讀取相關檔案                                           │
│  - 讀取用戶指定的 Phase 描述                                    │
│  - 讀取需要修改的原始碼檔案                                     │
│  - 確認現有實作與新需求的關聯                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: 程式碼實作                                             │
│  - 根據需求實作功能                                             │
│  - 遵循專案現有程式碼風格（Swift 6, @MainActor, 層級結構）      │
│  - 複用既有組件和工具函數                                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: 編譯驗證                                               │
│  - swift build（於 vChewing-LibVanguard/）                      │
│  - 確保無錯誤、無警告                                           │
│  - 如有錯誤立即修復                                             │
│  - 然後用 Xcode build 觸發 localized strings key 生成           │
│  - 完成 localization 之後再次重試編譯                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: 文件同步（並行執行）                                   │
│  ├─ vChewing-DevLogs/Reqs4LLM: Phase 規格與實作備忘錄           │
│  ├─ vChewing-DevLogs/DevReqsHistory.md: 追加 Phase 歷史摘要     │
│  ├─ vChewing-DevLogs/KnowledgeMemo4LLM.md: 更新標記與近期摘要   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 5: 彙總報告                                               │
│  - 列出所有變更的檔案                                           │
│  - 說明核心實作邏輯                                             │
│  - 確認編譯狀態                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 12.2 文件更新規則

| 檔案 | 更新時機 | 內容格式 |
|------|---------|----------|
| **vChewing-DevLogs/Reqs4LLM/Archive_P{首 Phase 所屬百位段}/Reqs_0NN1-0NN0.md**（現行卷；檔名現算，判定式見文首〈Reqs4LLM 分卷歸檔註記〉） | 每個 Phase 必須 | `# Phase XX` 標題 + `Assignee:` 行（**Model ＋ Harness** 兩者兼備，見 §12.6）＋ 規格說明 + `## Phase XX 實作結果` 小節（歸檔卷不再增改；惟對過往 Phase 之補記一律補進該 Phase 自己的記錄內——無論該卷是否已歸檔，回填規則見 §12.5） |
| **vChewing-DevLogs/DevReqsHistory.md** | 每個 Phase 必須 | 追加一行 `\| Phase XX \| 簡短描述 \|` |
| **KnowledgeMemo4LLM.md** | 每個 Phase 必須 | 更新 `最後更新` 標記，並按需要補上近期 phase 摘要或修正過時指引 |
| **UserGuide (4語言)** | 影響使用者操作時 | 在對應章節添加功能說明（鍵盤熱鍵、滑鼠操作等） |

### 12.3 程式碼實作原則

1. **最小變更原則**：只做必要的修改，不改動無關程式碼
2. **風格一致性**：
   - **勿在 Swift 原始碼正文內提及 Phase 編號**（各 Phase 規格之既有要求；原「使用 `// Phase XX:` 註解標記新代碼」之指引與此相牴觸，已於 Phase 210 更正）
   - 遵循現有命名慣例（如 `handleXxx`, `onXxx`）
   - 保持縮排和空行風格
3. **平台相容性**：
   - (今後會按需求補充)
4. **狀態管理**：
   - (今後會按需求補充)

### 12.4 常見任務類型

| 任務類型 | 典型檔案 | 注意事項 |
|----------|----------|----------|

### 12.5 回報格式範本

> 注意**各個 Phase 檔案內部的標題層級**：一級標題（`#`）僅保留給 `# Phase NNN`；`--------------------` 大分隔線亦僅保留於 Phase 之間。

```markdown
## 變更總結

### 程式碼變更

**檔案名稱.swift**:
- 變更項目 1
- 變更項目 2

### 文件更新

| 檔案 | 更新內容 | 注意事項 |
|------|---------|---------|
| vChewing-DevLogs/Reqs4LLM/Archive_P{首 Phase 所屬百位段}/Reqs_0NN1-0NN0.md（現行卷；檔名現算） | 新增 Phase XX 規格與實作備忘錄 | 一律寫入**現行卷**；**歸檔卷**（已滿 10 個 Phase、或經事主裁定結案者）不再增改。分卷以「十年前綴 `0NN1`–`0NN0`」為界、每卷至多 10 個 Phase（如 `Reqs_0201-0210.md` 收 Phase 201~210）；**同一區間內的新 Phase 續寫同一卷，不另立新卷**。該區間寫滿或結案後始自立為一卷，並置於 `Archive_P{首 Phase 所屬百位段}/`（歸檔桶與「卷是否已滿」無關：現行卷雖置於 `Archive_P…/` 之內仍屬現行卷）。**對過往 Phase 之補記不寫入現行卷**：無論該 Phase 所屬之卷是否已歸檔，補記一律逕補進**那個 Phase 自己的記錄內**，不得佔用其他 Phase 的記錄空間。 |
| vChewing-DevLogs/KnowledgeMemo4LLM.md | 根據專案實際情況更新內容（如適用） | 參考既往記錄的文書風格。 |
| vChewing-DevLogs/DevReqsHistory.md | 新增 Phase XX 到開發階段歷史 | 參考既往記錄的文書風格。 |

### 編譯狀態

✅ 編譯通過 / ❌ 有錯誤（說明）
```

### 12.6 工作細節附註

- 交差前注意與 L10n 有關的內容是否全部補齊。
- **zh-Hans 之語體一律為「zh-Hans-TW」（臺灣華語、簡體字形）、非大陸普通話（事主 2026-09-24 明示）**：凡新增／修訂 zh-Hans 文案者，須先沿用本倉 zh-Hant 之對應用語、再轉為簡體字形，**不得**逕採大陸慣用語。實查之對照（本倉 zh-Hant → 本倉 zh-Hans；括號內為**不得**採用者）：**剪貼簿 → 剪贴簿**（剪贴板）、**匯入 → 汇入**（导入）、**套用 → 套用**（動詞；`应用` 於本倉只作名詞「客體應用」即 app）、**設定 → 设定**（设置）、**資料 → 资料**（数据）、**視窗 → 视窗**（窗口）、**選單 → 选单**（菜单）、**軟體 → 软体**（软件）、**標幟 → 标帜**（标识）、**拷貝 → 拷贝**（复制）、**無法讀取 → 无法读取**（“无法”與“读取”兩岸同形、可用）。四語系 `.strings` 為**全域排序**（`LocalizableFileSorter.swift`），任何增刪皆須以「複本跑排序器後逐位元組比對」複驗。
- **ja：凡指「可交換之配置檔（exchangeable configuration profile／配置包）」此一義之 `configuration` 時，一律作「配置」、**不得**作「構成」**（事主 2026-09-24 明示，並界定此為該詞在此義下之定譯）——「構成」於本倉只作「系統構成部品」一類之**他義**（實查：`aboutWindow.DISCLAIMER_TEXT`、`InfoMessage.EndOfIMKCandidatesExplanation`），**非此義者不在此限、不必強改**。ja 之既有慣例（實查）：`読み込(む)` 優先於 `インポート`（16 : 1）、`環境設定`＝preferences、`適用`＝apply、`クリップボード`＝clipboard。
- **`i18n:Settings.ImportConfigFromClipboard`**（事主 2026-09-24 命名；舊為 `…ImportFromClipboard`）＝「自剪貼簿匯入配置資料」按鈕之五態 alert 文案群（11 條）＋ `i18n:AssistantConfig.Meta.{Unspecified, NoDescription}` 2 條；其 Swift 端落點為 `Packages/vChewing_SettingsUI/Sources/SettingsUI/PrefsExchange.swift`（`Preparation.alertTitle`／`alertMessage`）。
- 如果要使用 tmp 目錄的話，請使用**所在倉庫根目錄**的 `tmp/` 或 `.tmp/`（例如 `vChewing-LibVanguard/tmp/`、`vChewing-DevLogs/tmp/`）、而非系統的 `/tmp/`。使用 `/tmp/` 這種 out-of-workspace 的路徑會迫使事主每次都得手動設定存取權限，非常麻煩。
- **CI 之豁免：同環境者以本機代跑之（事主 2026-09-21 定調）**：任何 CI 工作流程，**凡其執行環境與當前開發環境相同者，一律以當前環境（本機）代跑之**——**不等待 GitHub 之排隊與運行**（macOS runner 在 GitHub 上之排隊時間過長，事主明示此制）。作法：以該 workflow 之**同組命令**於本機實跑（SwiftPM 之測試一律附 `--disable-sandbox`，見上），並以本機之實跑結果為驗證證據；該等 workflow 之遠端結果其後若轉綠，得補記為追認、非必需。**環境不同者不得豁免**：本工作區之當前環境為 macOS，故 `unit-test-LibVanguard-linux`／`unit-test-LibVanguard-WinNT` 兩條仍以 CI 為唯一驗證途徑，不得以本機結果冒充之。文書之 CI 欄照此記：豁免者記「同環境、以本機代跑」及其命令與結果，未豁免者方須記 run ID。
- **腳本內的全形字元陷阱（2026-09-13 實錄）**：本工作區的 shell 常以 `LC_ALL=C` 執行，此時 bash 會把緊接在全形字元（如 `（`）之前的高位元組**一併視為變數名的一部分**——`log "…：$scheme（Debug）…"` 會以 `scheme\xef…: 未綁定的變數` 失敗（在 `set -u` 下直接中止腳本，且若已把 stderr 重導就完全看不出原因）。**凡變數緊鄰 CJK／全形字元者，一律寫成 `${var}`。** 同源的坑：Python `re` 的 `\b` 視中日韓字元為 word character，故 `\bTypewriter\b` 不會命中 `Typewriter的`（見 `DevReqsHistory.md` Phase 201 的〈方法學教訓〉）；腳本化取代 CJK 文本時請改用 `(?<![A-Za-z0-9_])`／`(?![A-Za-z0-9_])` 這類斷言。
- **跨平台 manifest 的 `platforms:` 陷阱（2026-09-14 實錄）**：`Package(platforms:)` 之參數型別是 **`[SupportedPlatform]?`**，故 **`platforms: []` 會讓 SwiftPM 報 `supported platforms can't be empty`**（Linux／Windows CI 當場炸），正解是 **`platforms: nil`**（＝不宣告平台限制）。要條件編譯分流者，須把變數宣告為 **optional**：`#if canImport(Darwin) let p: [SupportedPlatform]? = [.macOS(.v12)] #else let p: [SupportedPlatform]? = nil #endif`。**此誤在本機（Darwin）永遠測不出來**——務必以「把 `canImport(Darwin)` 反轉為假」的 scratch 套件預驗（見 `_MainWorkspace/tmp/p215LinuxSim` 之做法），或直接等 CI。
- 如果事主丟給您 Xcode Instruments Profile 檔案的話，可能會是二進位檔案，請先嘗試用 `xctrace export` 解讀成 XML 再分析。
- 每次交差之前「一次性運行」 `make lintFormatUncommitted` 這一條命令。如果事主明確要你對某些工作單獨 commit 的話，每次 commit 之前也請運行 `make lintFormatUncommitted`。該命令僅對 tracked 且未 commit 的 Swift 檔案下動作，且依序執行 SwiftLint 自動修正與 SwiftFormat（先 lint 後 format 的順序已內建）。但注意在運行之後也請 build 一次，因為這些自動修正對 `count == 0` 的範式會頑固地轉換成 `.isEmpty` 而不會檢查相關 type 是否有 `isEmpty` 這個 read-only property。發現這種情況的話，可以用 `.count * 1 == 0` 取代之。commit 的 title 格式是 `ModuleName // WhatHasBeenFixed`、且在 commit 的 description 的末尾單獨一行寫明 `(Phase XXX - Task YYY)`。Commit Titles 始終以 ASCII Period `.` 結尾，除非是疑問句時才使用 `?` 結尾。
- 給 ChatGPT、Codex、Raptor 的特殊指令：Do not intentionally stop with tasks incompleted to ask me whether you do the next step I already told you. Just do it. I have backups, hence no worry. // Claude、Kimi、GLM、QwenCoder 從來不用問這些問題，就能把這些事情全部做好。唯獨 ChatGPT、Codex、Raptor 不這樣，就很奇怪很令人窩火。
- **Phase 文書之用語與署名（事主 2026-09-18 定調）**：① Phase 檔頭之 `Assignee:` 行**必須同時寫明 Model 與 Harness**——形如 `Deepseek-v4-flash（Codewhale harness）。`；只寫「（harness）」而未冠 harness 之名、或把 harness 之名填進 model 位者（如 `Codewhale（harness）`），皆屬誤標。② 文書提及 GitHub issue 之發起人時：**非 ShikiSuen 者一律稱「工單樓主」**；「事主」一詞**專指 ShikiSuen 本人**（含其於 issue 串／討論區內之發言在內）。

---

- **設定面板之兩側命名與「Section」之形制（2026-09-25，Phase 247／248 實查）**：事主口語之 **「SessionUI」／「SessionCocoa」**即本倉 `vChewing_SettingsUI` 套件內之 **SwiftUI 面板**（`Sources/SettingsUI/SettingsUI/VwrSettingsPane*.swift`）與 **AppKit 面板**（`Sources/SettingsUI/SettingsCocoa/VwrSettingsPaneCocoa*.swift`）；全倉並無 `SessionCocoa` 一字，phase 文書見此用語時應據此對位。同一個「Section」在兩側形制不同：SwiftUI 側是 `Section { … }`（語言構造）；AppKit 側是 `NSStackView.buildSection(width:) { … }?.boxed()`（`vChewing_OSFrameworkImpl` 之工廠函式 ＋ 外框，`withDividers: false` 即令同段各列之間不留分隔線）。**分段即兩側唯一之視覺分群手段**——本二面板之各段皆無標題（原始碼內之 `// MARK: (header: Text("…"))` 是**註解**、非實作），故一個 `Section` 就是使用者在畫面上看到的一個帶框方塊。
- **`make lintFormatUncommitted` 只涵蓋「tracked 且未 commit」之 Swift 檔（2026-09-25，Phase 247 實錄）**：**新建而尚未 `git add` 之檔不在其列**（其以 `git diff --name-only HEAD` 取檔）；故新增檔案後須先 `git add` 再跑，或對該檔單獨跑 `swiftlint lint --fix --autocorrect --config .swiftlint.yml <檔>` ＋ `swiftformat --swiftversion 5.5 --indent 2 <檔>`，否則新檔會漏格式化。實錄：P247 之新檔 `AssistantLauncher.swift` 即因此漏跑，事後補跑（僅移除一個多餘之 `// MARK: Public`）、並以 `--amend` 就地補入同一筆尚未推送之 commit。

> ⚠️ **注意**: 本文檔需要定期更新以反映最新程式碼狀態。如有發現過期內容，請及時修正。
