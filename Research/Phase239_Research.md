# Phase 239 研究暨設計定案：偏好交換格式（__UserDefMeta）與「自剪貼簿匯入配置資料」

> **文檔狀態**：研究暨設計定案。本文即本 phase 之交付物，不含實作。
> **用途**：本文為 **Phase 240**（Reqs 記錄）之設計依據；P240 為施工規格。**P240 之範圍界線：不涉及 TypeScript 網頁工具之開發**（該助手網頁暨 `ValueAdd/WebConfigAssistant/` 屬助手網頁 phase）。
> **資料來源**：`vChewing-macOS`（工作區 HEAD）、`vChewing-LibVanguard`、`vChewing-HomePage.io` 之**靜態閱讀**，＋ 三項**本機離線實測**（TypeScript 7.0.2 之 emit 行為、npm registry 可達性、工具鏈版本）。凡屬推論者皆已標註。
> **用詞**：本文稱 macOS 版輸入法為「唯音」、其 IME 進程為「IME 進程」；其偏好設定體系為「偏好」；`UserDef` 之成員稱「偏好鍵」。本功能稱 **Configuration Assistant**，中文全稱「**配置助手**」、簡稱「**助手**」（簡繁日通用）。

---

## 〇、摘要

### 0.1 目標與交付

**目標**：把唯音偏好設定的認知負荷，從 12 頁、118 條鍵收斂為一次性流程。作法是定義兩件規格：

1. **偏好交換格式**（§三）：一份扁平 JSON，加一枚單一根層中介辭典 `__UserDefMeta`（承載這套配置之總體目的與標題）。
2. **「自剪貼簿匯入配置資料」按鈕**（§四）：置於「偏好設定 → 一般設定」頁、「我姓ㄅ」按鈕之**下方**；以兩段式 `NSAlert` 列出「有哪些與當前設定不同的選項會被改」，讓使用者決定是否正式套用。

**交付**：① 本文（設計依據與施工落點）；② 供助手網頁 phase 之契約（§五）；③ 驗證要求（§六）。**P240 之施工範圍以本文 §〇 至 §七 為界。**

**三項決定性事實（實查）**：

1. **JSON 偏好匯入匯出機制已存在，且即為本格式所需之載荷處理途徑。** `UserDef.exportAsJSON()` / `UserDef.importFromJSON(_:)`（`Sources/Shared/UserDef/UserDef.swift:242／:258`）已提供：118 條偏好之逐鍵處置、6 條黑名單、逐型別值域驗證、逐筆成敗回報（`ImportResult`）。此事另有 GUI 入口（設定畫面「開發道場」頁）與 CLI 入口（`vChewing --dump-prefs-json` / `--import-prefs-json <path>`）。
   ⇒ 助手產出之 JSON，現行唯音**已經能吃**：使用者走「下載設定包 → 拖入設定畫面」即可完成整套流程。本 phase 之工作是**把最後一哩的摩擦磨掉**，並補上匯入後之推式副作用（§2.3、§4.4）。
2. **「我姓ㄅ」按鈕與其兩段式 `ActiveAlert` 是現成的形態典範**（§2.5）：資料來源換成剪貼簿、確認訊息改由差異清單動態生成，即可複用其整套確認 → 套用 → 結果之流程。
3. **官網「新手上路」與 FAQ 已是人類策展完成之知識庫**（§2.7）：`onboarding/README.md` 本身就是一份分支問卷，各篇更是逐條「偏好設定 → X 頁 → 選項 Y → 改成 Z」的現成處方。助手網頁 phase 應視為「把它可執行化」，題庫不必從零發明。

### 0.2 關鍵取捨

| 議題 | 結論 | 理由（詳見對應節） |
|---|---|---|
| 派送方式 | 於「偏好設定 → 一般設定」之「我姓ㄅ」按鈕**下方**新增按鈕「點此從剪貼簿匯入（由配置助手生成的）配置資料」；機理**照「我姓ㄅ」之兩段式 `ActiveAlert`** | §四。不新增 URL scheme、不新增跨行程通道、不改寫 `MainSputnik`；授權係由「使用者親手按下按鈕」結構性地保證 |
| 交換格式之中介資料 | 單一根層鍵 `__UserDefMeta`（辭典型別，成員值皆 String：`title`／`description`） | §三。可擴充、與偏好同域、摘除規則單純 |
| 既有 import 路徑之 `didSet` 缺口 | **一併修**：三條匯入入口（檔案／拖放／剪貼簿）共用同一段「套用＋和解」 | §2.3、§4.4。設定畫面之 JSON 匯入本就有此缺口 |
| 後設資料導出之落點 | 於 `vChewingSharedCLI` 新增 `dump-userdef-metadata` 動詞 | §5.4。該 CLI 為可改造對象（事主核定）；不動 manifest、不動 CI、不跨倉 |
| 助手產物之形態 | **單檔自足 HTML** | §5.3 |
| 題庫之來源 | 由官網 `onboarding/*` 與 `faq/*` 的既有處方**形式化**；標籤文字自 `Localizable.strings` 導出，不手抄 | §5.5、附錄 D |
| 助手是否隨 app 出貨 | 列為助手網頁 phase 之後續，本次不做 | §5.3 末 |

**※ 上表屬「本文立場、尚未經事主核定」者三列**——既有 import 路徑是否併修和解（第 3 列）、助手產物之形態（第 5 列）、助手是否隨 app 出貨（第 7 列）；三者俱見 §七。其餘四列為已核定之定案。

**★ 兩則不可退讓之約束**：① 助手**不得**代使用者決定未表態之項目——每題之預設選項一律「維持不變」（§5.5）；② 兩層可獨立交付，惟**助手網頁不得先於第 1 層上線**（§0.4）。

### 0.3 三則關鍵約束

1. **URL scheme 之可見性：不動註冊路徑即為已足。** `~/Library/Input Methods/` 並非 LaunchServices 之常規掃描位置（`/Applications`、`~/Applications`、`/System/Applications`），而 IME 僅透過 `TISRegisterInputSource`（`Packages/vChewing_IMKUtils/Sources/IMKUtils/TISInputSourceExtension.swift:52`，由 `vChewing install` 觸發）註冊自己。事主依個人經驗判斷「應該會被索引」⇒ 附錄 A 之存檔設計採「僅靠既有之 `TISRegisterInputSource`（零改動）」，註冊之不確定性以「**實作後之確認**」收尾，而非動工前之關卡。
2. **`open` 會另起一份執行檔，且該管線不走輸入法服務之啟動路徑。** 事主實測：唯音既有之其他 CLI 命令均不影響本體運作。⇒ 附錄 A 之存檔設計據此建立**雙實例架構**：Apple Event 之處理器須存在於第二實例內，且該實例須能在未取得 `IMKServer` 之情形下正常收工；跨行程之狀態與推式副作用另須處理。**本計畫之剪貼簿路線不受此約束**——套用者就是 IME 進程本身（§2.4、§4.4）。
3. **官網文章現階段不討論配置助手**——因該助手之頁面**可能會直接嵌入到官網**。⇒ 產物形態須以「**可被官網直接嵌入**」為前提（單檔自足 HTML，§5.3）；「於 `onboarding/README.md` 置頂入口」、「於 `manual/preferences.md` 補註」等推廣動作暫緩。

### 0.4 與助手網頁 phase 之次序約束

**兩層可獨立交付**：

```text
第 1 層（本 phase）：交換格式（§三）＋ 剪貼簿匯入按鈕（§四）＋ 既有 import 路徑之和解（§4.4）
                     零助手網頁依賴；可獨立落地、獨立驗證
第 2 層（助手網頁 phase）：ValueAdd/WebConfigAssistant/ 之建置、題庫與部署（§五、附錄 D）
                     其產物為一份 JSON 與一段引導文字；不依賴第 1 層之外的新機制
```

- **★ 次序約束：助手網頁不得先於第 1 層上線。** 助手之主出口〔複製配置資料〕需要第 1 層之按鈕，才有接收端（§5.2）。
- **P240 之範圍界線（事主明示）**：**不涉及 TypeScript 網頁工具之開發**——助手網頁暨 `ValueAdd/WebConfigAssistant/` 屬另一 phase。
- §五 之地位為**契約**：本 phase 不建置助手，但把助手網頁 phase 必須遵守之產出規則、出口、形態、防漂移機制與不可退讓之約束先定下來。

---

## 一、背景與需求

### 1.1 緣起

唯音接下來需要爭取其他媒體的宣傳，而在這之前得先改良 OOBE 體驗。其中一個長年被視為只能由官方網站「新手上路」之教學文章套裝承擔的職能，就是「幫使用者把偏好設定好」。

痛點不在選項不夠，而在選項太多而無從下手：唯音的偏好設定有 **12 頁、118 條鍵**（`UserDef`），官方文件自己承認「已經多到需要內建搜尋功能才找得到」（`onboarding_kimo.md:32`）。使用者真正的問題是「我不知道我該動哪幾個」。

⇒ 因此助手不是 FAQ 的另一種排版，而是**把 FAQ 的處方直接執行掉**：教學文章讀完還要自己去 12 個頁面裡找那 5 個開關；助手要直接幫使用者改好。

### 1.2 皮樂建言（事主轉述）

> ……設定非常的複雜。一個快速上手的設定引導畫面是可以做的。例如：要用戶先勾選幾個基本項目，然後再下一步勾選其他選項。你 100 個選項是給 IQ 140 以上的人在理解的，但是用戶群體 IQ 平均是 100。這就是我常常遇到的問題。

皮樂的建言有三層，缺一不可：

1. **問題不在選項不夠，而在選項太多而無從下手。** OOBE 的痛點是「我不知道我該動哪幾個」。
2. **解法是「分期付款」的認知負荷管理**：一次只問一組相關問題，前一題的答案決定後一題的出題範圍（分支問卷）。這正是 Windows 95/2000 安裝程式與「新增硬體助手」的形態。
3. **產物必須是「可用的偏好設定」，不是「一份說明」。** 助手要直接幫使用者改好，而不是請使用者自行去 12 個頁面裡找。

### 1.3 需求原文照錄

> 唯音接下來也得想辦法爭取到其他媒體的宣傳，但在這之前還得改良一下 OOBE 體驗。在此之前我一直以為這個職能只能藉由官方網站新上路的教學文章套裝來完成。然而，vChewing 1.x 極早期開發階段參與開發的皮樂（Hiraku）給出了一個非常重要的思路：設計一套 Configuration Assistant 以分支問卷的形式來輔助使用者們完成自己的偏好設定體系。

### 1.4 職能定位：助手 vs 官網教學文章

| | 現行 onboarding 文章套裝 | 配置助手 |
|---|---|---|
| 載體 | 靜態 Markdown 網頁（zh-Hant 單語） | 互動網頁（分支問卷） |
| 輸出 | 使用者腦中的「等等要去哪一頁改哪一項」 | 一份 JSON 配置包（可直接匯入） |
| 覆蓋率 | 只有 8 種「其他輸入法背景」的入口 | 可涵蓋任意組合（背景 × 打字習慣 × 偏好細節） |
| 維護 | 唯音改版即需手改文章（且已有版本漂移註記，如「僅 v4.4.1」） | 與 `UserDef` 後設資料對齊，可用工具檢查漂移 |
| 語言 | 僅繁中 | 可四語系（複用 app 既有 `.strings`） |

**助手不取代 onboarding 文章，而是「文章的執行檔」。** 文章仍須存在——它是助手選項的權威解釋來源，也是助手答不出來的長尾問題的歸宿；助手的每一頁都應附「深入說明 →」連到對應文章。此設計使兩者互為校驗，而非重複。

---

## 二、既有資產盤點（實查）

### 2.1 偏好體系

- **`UserDef`**：`Packages/vChewing_OSNeutral_LibVanguard/Sources/Shared/UserDef/UserDef.swift:9`，`public enum UserDef: String, CaseIterable, Identifiable, Sendable`。**118 條 case**（`case kName = "RawStorageKey"`，rawValue 即 `UserDefaults` 鍵）。另有 6 條以 `_` 起頭者（`_DebugMode`、`_FailureFlag_POMObservation` 等）——**`_` 前綴並非保留字，`_DebugMode` 是合法且可交換的偏好鍵**。
- **`DataType`**（`UserDef.swift:143`）：六種載荷，**每種自帶其預設值**（＝預設值之單一真源）：`.string` / `.bool` / `.integer` / `.double` / `.arrayOfStrings` / `.dictionary([String: Bool])`。其中 `.double` 未被任何 case 使用（值域為空的相容殘留）。
- **`MetaData`**（`UserDef.swift:178`）：`shortTitle` / `prompt` / `inlinePrompt` / `popupPrompt` / `description` / `minimumOS` / `options: [Int: String]?` / `toolTip`。全部為 `"i18n:UserDef.kXxx.shortTitle"` 形式之鍵名，於執行期由 `.i18n` 解析。**`options` 正是「單選題之選項標籤」的現成來源**（例：`kKeyboardParser4Zhuyin` 之 11 種排列、`kCandidateStateJKHLBehavior` 之三態）——助手的單選題不必自造標籤。
- **`@AppProperty`**：`Packages/vChewing_OSNeutral_LibVanguard/Deps/VanguardSwiftExtension/Sources/SwiftExtension/SwiftFoundationImpl.swift:195`。**無快取**：`get` 每次直讀 `UserDefaults.current.object(forKey:)`。存於 `UserDefaults.standard`（生產環境），即沙盒容器內 `~/Library/Containers/org.atelierInmu.inputmethod.vChewing/Data/Library/Preferences/`。
- **`PrefMgr`**：`Sources/Shared/PrefMgr_Core.swift:9`，118 個 `@AppProperty` 屬性；13 條帶 `didSet` 副作用（見 §2.3）。`PrefMgr.shared` 於 `Packages/vChewing_Shared_DarwinImpl/Sources/Shared_DarwinImpl/PrefMgr_Singleton.swift:19` 建立並注入三個回呼。

### 2.2 ★ 現成之 JSON 匯入匯出

`Sources/Shared/UserDef/UserDef.swift`：

| 成員 | 行 | 行為 |
|---|---|---|
| `jsonExchangeBlacklist` | `:214` | 6 條**不參與交換**之鍵：`kUserDataFolderSpecified`、`kCassettePath`、`kAppleLanguages`、`kFailureFlagForPOMObservation`、`kMostRecentInputMode`、`kCandidateServiceMenuContents` |
| `exportAsJSON() -> Data?` | `:242` | 逐 `allCases` 輸出；跳過黑名單與**不在 `UserDefaults` 內者**；`.prettyPrinted` ＋（10.13+）`.sortedKeys`；**不得輸出任何以 `__` 起頭之鍵**（§3.3） |
| `importFromJSON(_:) -> ImportResult` | `:258` | **未知鍵 ⇒ 失敗**、黑名單鍵 ⇒ 失敗、其餘逐型別驗證後寫入 `UserDefaults` |
| `validateAndApply` | `:288` | 逐型別驗收；接受 JSON 數字 `0/1` 當 Bool、接受 `Double` 取整當 Int；值域外 ⇒ 失敗 |
| `validNumeralValueRange` | `:368` | 20 條鍵之值域（如 `kKeyboardParser4Pinyin: 100...105`、`kCandidateListTextSize: 12...196`） |

**格式**：一個扁平 JSON 物件，鍵＝`UserDef` rawValue，值為對應 JSON 型別。**無版本欄、無外層包裝、非 `Codable`**（純 `JSONSerialization`）。

**三處既有消費端**：

- 設定畫面「開發道場」頁（SwiftUI）：`Packages/vChewing_SettingsUI/Sources/SettingsUI/SettingsUI/VwrSettingsPaneDevZone.swift:39-97`；`fileExporter` / `fileImporter`；預設檔名 `vChewing_Preferences.json`。
- 同上（AppKit/Cocoa 備用介面）：`.../SettingsCocoa/VwrSettingsPaneCocoaDevZone.swift:124-205`；**已支援拖放匯入**（`:110-119`）。
- CLI：`Packages/vChewing_MainAssembly4Darwin/Sources/MainAssembly4Darwin/MainSputnik.swift:80-84`（`--dump-prefs-json`）、`:155-157`（`--import-prefs-json <path>`）。

**對本計畫之意義（兩點）**：

1. **接收端不必自造格式**：把 decode 後的 `Data` 交給 `UserDef.importFromJSON` 即可。黑名單、值域、逐筆錯誤訊息全部沿用——**這是既有的防線，且已寫好**。
2. **助手產物今天就能被消費**：助手只要輸出上述格式的 JSON，使用者拖入設定畫面（或走 CLI）即完成——此路徑本 phase 不動任何 IME 機制即可運作（§5.2）。

### 2.3 匯入後之推式副作用缺口（★ 施工必須處理）

**`UserDef.importFromJSON` 直接寫 `UserDefaults`，不經 `PrefMgr` 的 `@AppProperty` setter，故 13 條 `didSet` 副作用一概不觸發。** 而 IME 進程是**長駐**的（§2.4），因此這不是「反正重開就好」的問題。

13 條帶副作用之偏好（`PrefMgr_Core.swift:373-457`）：

| 鍵 | 副作用 |
|---|---|
| `userPhrasesDatabaseBypassed` | `didAskForSyncingLMPrefs?()` |
| `cns11643Enabled` / `symbolInputEnabled` / `cassetteEnabled` | 同上 |
| `suppressFactoryUnigramsOfKanaSyllables` / `useSCPCTypingMode` | 同上 |
| `phraseReplacementEnabled` / `associatedPhrasesEnabled` | 同上 |
| `candidateKeys` | 小寫化＋去重＋`candidateKeyValidator` 檢定（失敗則回預設） |
| `candidateListTextSize` / `popupCompositionBufferTextSize` | 自我夾限（12…196 / 18…40） |
| `readingNarrationCoverage` | `didAskForRefreshingSpeechSputnik?()` |
| `togglingAlphanumericalModeWithLShift` / `…RShift` | `didAskForSyncingShiftKeyDetectorPrefs?()` |

其中 `didAskForSyncingLMPrefs` 繫於 `SettingsUIHostWiring.swift:52-60`（重載片語置換／關聯詞語＋`LXMgr.syncLMPrefs()`）、`didAskForSyncingShiftKeyDetectorPrefs` 繫於 `:61-63`、`didAskForRefreshingSpeechSputnik` 繫於 `PrefMgr_Singleton.swift:19-27`。

**既有 import 路徑的收尾只有 `PrefMgr.shared.fixOddPreferencesCore()`**（`VwrSettingsPaneDevZone.swift:82`、`MainSputnik.swift:207`）。`fixOddPreferencesCore` 內以 `candidateKeys = candidateKeys` 之技巧強迫 `candidateKeys` 走一次驗證（`PrefMgr_Core.swift:463-464`），故**值域與正規化面已顧及**；但 `didAskForSyncingLMPrefs` 等**推式同步**未被觸發。

**⇒ 規格要求**：全部匯入路徑（檔案／拖放／剪貼簿）於匯入後執行一次**「匯入後之和解」（reconciliation）**：

1. `PrefMgr.shared.fixOddPreferencesCore()`（既有）；
2. **逐一對 13 條帶副作用之鍵做自我賦值**（`prefs.x = prefs.x`），以觸發 `didSet`——此為最小且顯式的做法，不必為 `PrefMgr` 新增「以 `UserDef` 泛型寫值」的 118 臂 switch；
3. `UserDefaults.current.synchronize()`（CLI 路徑已有此步，`:208`；常駐行程雖有 cfprefsd 代理，但顯式同步無害且便於測試）；
4. 推式狀態中另有 `inputHandler.assembler.maxSegLength`（於 `initInputHandler()` 重推，`InputSession.swift:229,234`）：**不即時刷新**，於下一次輸入源重啟（`performServerActivation`）時生效。此點須寫入使用者可見之說明；「於和解中主動重推」須先確認 `SessionHost` 能否自 IME 進程取得當前 handler 實例（列為 §六 之實測項）。

**未實測之行為細節**：修改 `candidateListTextSize` 後候選窗何時重繪——依 `CandidatePool4AppKit` 之設計（`CandidatePool4AppKit.swift:135-139` 之註記），字級為**即時讀取**，惟 cell 的 `textDimension` 為建池快照，`candidateListTextSize` 又不在 `CandidateDisplayConfig` 之失效條件內（`CtlCandidateGSI4AppKit.swift:167-190`），故**高度即時、寬度恐需一次建池**。純外觀、無需處理，列為實機觀察項（§六）。

### 2.4 設定視窗與 IME 同進程

- 入口：`Sources/vChewingIME_macOS/Modules/main.swift:10-14` → `MainSputnik4IME.asyncInit().runNSApp(isLegacyDistro: false)`。
- `MainSputnik4IME.init()`（`MainSputnik.swift:12-34`）：兩次 `wireUp()` → `handleVarArgs()`（可能 `exit`）→ `handleIMKConnection()`（失敗則 `exit(1)`）。
- `runNSApp()`（`MainSputnik.swift:57-65`）：設 `NSApplication.shared.delegate = AppDelegate.shared` → 建主選單 → `NSApplicationMain(...)`。
- **★ 同進程**：設定視窗（`CtlSettingsUI` / `CtlSettingsCocoa`）與 IME 同屬一個進程，以 `showPreferences()`（`InputSession_DarwinSurface.swift:100-118`）開啟，並以 `NSApp.popup()`（`OSFrameworkImpl/AppKitImpl/AppKitImpl_Misc.swift:486-498`，macOS 14+ 用 `activate()`、否則 `activate(ignoringOtherApps: true)`）強制拉到前景。**這正是「剪貼簿按鈕按下後能就地套用、就地觸發 13 條 `didSet`」之結構理由**（§4.4），也是 agent app 如何顯示視窗、取得焦點、彈 `NSAlert` 的既有典範。
- **長駐性**：`LSUIElement = true`、`NSSupportsSuddenTermination = false`、無「結束」選單項、`IMKServer` 由 `MainSputnik4IME.theServer` 持有、另有 60 s 週期計時器（`SecurityAgentHelper.swift:23-31`）與 `FolderMonitor`。唯一的自我終止路徑為私有記憶體 ≥ 1536 MB 兩次取樣（`AppDelegate.swift:230-267`）。由系統（`imklaunchagent`）於選用該輸入源時啟動，非登入項。
- **既有陷阱（非本計畫所引入，惟改動 CLI 動詞時須留意）**：`handleVarArgs()`（`MainSputnik.swift:69-127`）對**任何**未被辨識的 argv 皆回 `0`（case 1 之 `default: break` 後 `return 0`；case 2 之 `default: break` 後 `return 0`；`default: return 0`），而 `init` 隨即 `exit(varArgsResult)` ⇒ **多一顆不認識的命令列引數就會讓 IME 靜默 `exit(0)`**。今日之所以無事，是因系統正常啟動時不帶引數。

### 2.5「我姓ㄅ」之機理

「我姓ㄅ」是「逐字選字（ㄅ半）懶人包」之一鍵套用：按下按鈕 → 確認 alert → 逐項寫入 `PrefMgr.shared.*` → 結果 alert。這條流程即新按鈕所要複製之形態。

| 事實 | 位置 |
|---|---|
| **「我姓ㄅ」按鈕本體**——新按鈕即置於其**下方** | `Packages/vChewing_SettingsUI/…/SettingsUI/VwrSettingsPaneGeneral.swift:92`（`Button("i18n:Settings.ApplySCPCPreset.ButtonTitle")`，動作＝`activeAlert = .confirmApplyingSCPCBatchSettings`） |
| **其 `ActiveAlert` enum 與 alert 基建**（新按鈕照抄此形態） | `VwrSettingsPaneGeneral.swift:103-175`：`.alert(activeAlertTitle, isPresented:…)` ＋ `activeAlertButtons` ＋ `activeAlertMessage`；enum 三態＝`confirmApplyingSCPCBatchSettings`／`succeededInApplyingSCPCBatchSettings`／`fartWarning` |
| 其套用函式（逐項寫 `PrefMgr.shared.*`，之後設為「成功」態） | `VwrSettingsPaneGeneral.swift:182-214`（`applySCPCPreset()`） |
| **AppKit 之對位實作**（新按鈕亦須在此側行之） | `Packages/vChewing_SettingsUI/…/SettingsCocoa/VwrSettingsPaneCocoaGeneral.swift:137-184` |
| 開發道場之既有 JSON 匯入：`importPrefsFromJSONFile(at:)` 之邏輯可供共用 | `…/VwrSettingsPaneDevZone.swift:42-53`；`…/SettingsCocoa/VwrSettingsPaneCocoaDevZone.swift:185-205` |

⇒ **新按鈕即複製「我姓ㄅ」之形態**（同一套兩段式 alert：確認 → 套用 → 結果），差別只在：① 資料來源為剪貼簿；② **確認訊息係由差異清單動態生成**（非固定文案，§4.3）。

### 2.6 NSPasteboard 在本倉之先例

- **寫入方向已有先例**：服務設定頁之複製功能——`…/SettingsUI/VwrSettingsPaneServices.swift:260-261`、`…/SettingsCocoa/VwrSettingsPaneCocoaServices.swift:233-234`。
- **讀取方向**（本案所需）：`NSPasteboard.general.string(forType: .string)`。**讀取一般剪貼簿不需額外 entitlement**；仍列為實作後之確認（§六）。

### 2.7 官網 onboarding 與 FAQ：現成的人類策展知識庫

`vChewing-HomePage.io`（Jekyll，`remote_theme: vChewing/jekyll-theme-read-the-docs`，**無 `package.json`**；發佈於 `https://vchewing.github.io/`，原始碼倉 `vChewing/vChewing.github.io`）。

**（一）`onboarding/README.md` —— 已是分支問卷的骨架。** 其「我該從哪裡開始？」明言「不必從頭讀到尾。請直接找最接近您情況的那一段」，並分兩軸：

- *依您的打字習慣*：逐字選字（ㄅ半派）／注音組句／中英混打／CIN 表格／拼音輸入／簡體中文。
- *依您原本使用的輸入法*（官網 README 之標題原文）：行列三十／華碩／自然／漢音／奇摩／小麥注音／OpenVanilla／小鶴音形／拼音簡拼（共 9 篇 sub-article）。

**（二）各篇之「偏好處方」即助手的答案模板。** 抽樣（皆已與 `UserDef` 鍵對上，見附錄 D）：

| 來源 | 處方 | 對應偏好鍵 |
|---|---|---|
| `onboarding_msnewphonetic.md:18-29` | 選字游標改「詞語後方」、選字窗改「縱向佈局」、`始終自動展開多行選字窗` 保持關閉、調整選字鍵 | `kUseRearCursorMode`、`kUseHorizontalCandidateList`、`kAlwaysExpandCandidateWindow`、`kCandidateKeys` |
| `onboarding_msnewphonetic.md:42-47` | 開「啟用中英混合輸入回退」；需要時加開「英數閂滯狀態」；「依槽序鍵入判定讀音」維持開啟 | `kMixedAlphanumericalEnabled`、`kEnableLatchedAlnumStateInMixedAlnumMode`、`kMixedAlnumJudgeReadingsBySequentialRawKeyOrder` |
| `onboarding_msnewphonetic.md:51` | 不想看到右上飄窗 → 關掉提示 | `kShowNotificationsWhenTogglingCapsLock` / `…Eisu` / `…Shift` |
| `onboarding_array30.md:15-17`、`faq/basics.md:182-186` | 磁帶載入 `.cin2`、選字鍵改 `1234567890`、只勾「模擬逐字選字輸入」 | `kCassetteEnabled`（†路徑鍵在黑名單內，需使用者自行操作）、`kCandidateKeys`、`kUseSCPCTypingMode` |
| `onboarding_asus.md:22-26` | 開混打回退；必要時開「停用原廠假名音節資料」；聲調前置鍵入之取捨 | `kMixedAlphanumericalEnabled`、`kSuppressFactoryUnigramsOfKanaSyllables`、`kAcceptLeadingIntonations` |
| `onboarding_kimo.md:114-118`、`faq/basics.md:8-16,20-24` | 「我姓ㄅ」＝逐字選字懶人包；選字游標前／後之取捨；選字鍵自訂 | 見附錄 D.2 之 SCPC 群 |
| `onboarding_hanin.md:38` | 漢音符號表（`\`）需在偏好設定內手動啟用 | `kClassicHaninKeyboardSymbolModeShortcutEnabled` |
| `faq/basics.md:166-176` | 倚天 DOS 候選字排序（預設開）；「急速遺忘模式」；「停用原廠假名音節資料」 | `kEnforceETenDOSCandidateSequence`、`kReducePOMLifetimeToNoMoreThan12Hours`、`kSuppressFactoryUnigramsOfKanaSyllables` |
| `faq/basics.md:116-125` | 免打聲調僅限拼音模式；簡拼 →「狂拼模式」 | `kPinyinTypingEnabled`、`kFuriousTypingEnabled` |
| `manual/preferences.md` | 逐頁、逐選項之權威說明（465 行；**明示其原文 markdown 可供 AI 服務閱讀**） | 標籤與 `description` 之非程式權威來源 |
| `manual/toggles.md` | 中英／全半形／漢字轉換輪替等熱鍵一覽 | `kUsingHotKey*` 族 |
| `faq/troubleshooting.md` | 8 類症狀（Caps Lock 延遲、CMD+Z 失效、JetBrains/Rayon 小寫不動、Steam 看不到組字區、選字後字亂動……） | `kBypassNonAppleCapsLockHandling`、`kAlwaysUsePCBWithElectronBasedClients`、`kClientsIMKTextInputIncapable`、`kDisableSegmentedThickUnderlineInMarkingModeForManagedClients` |

**（三）既有文件已記載 JSON 交換。** `faq/basics.md:70-87` 完整說明了「開發道場」頁的 JSON 匯入／匯出與 `--dump-prefs` CLI——**即助手產物之下載路線已見於使用者文件**，助手之上線不會憑空長出一個沒人知道的檔案格式。

**（四）`manual/preferences.md` 已具備可機器處理的結構**：12 頁 × 子節標題（`### 游標與選字窗定位`、`### 混合輸入`、`### 聲調鍵`…），與助手的題組分頁可一一對位。**助手的題組分頁沿用這 12 頁之命名**，使用者回頭查文件時心智模型一致（§5.5）。

---

## 三、規格一：偏好交換格式（__UserDefMeta）

### 3.1 格式總覽

- **本體**：一個扁平 JSON 物件，鍵＝`UserDef` rawValue，值為對應 JSON 型別。**無版本欄、無外層包裝、非 `Codable`**（純 `JSONSerialization`）。
- **中介辭典**：單一根層鍵 **`__UserDefMeta`**（辭典型別，成員值皆 String）——承載「這套配置之總體目的與標題」，供確認 alert 顯示（§4.3）。
- **黑名單鍵不參與交換**：6 條（`jsonExchangeBlacklist`，§2.2）⇒ 可交換之鍵為 **112 條**。
- **型別**：strictly 依 `UserDef.dataType`——布林用 `true/false`、整數用 `123`、字串用 `"…"`、`arrayOfStrings` 用 `["…"]`、`dictionary` 用 `{"…": true}`。
- **值域**：由 `validNumeralValueRange` 於前端先驗（避免產出必然被 IME 拒絕的包）；**後端驗證仍為權威**，前端先驗不替代它。
- **版本資訊不入 JSON 本體**：schema 版本以 URL query（`v=1`）表示（附錄 A）。

```json
{
  "__UserDefMeta": {
    "title": "微軟新注音風格配置",
    "description": "這套配置會讓輸入法在行為方面盡量對齊微軟新注音 2003。"
  },
  "UseRearCursorMode": true,
  "UseHorizontalCandidateList": false,
  "CandidateKeys": "1234567890",
  "MixedAlphanumericalEnabled": true
}
```

**解析順序（IME 側）**：解碼 JSON → **無條件摘除根層所有以 `__` 起頭之鍵** → 取出 `__UserDefMeta`（若存在）→ 其餘內容交付逐鍵驗證（`importFromDictionary`）。

### 3.2 __UserDefMeta 之成員與顯示

事主定案原話（現行措辭）：

> App 拿到檔案之後，先摘出 `__UserDefMeta` 辭典格式，從裡面讀取 `description` `title` 這類內容（String）。然後，App 將那已經摘除過 `__UserDefMeta` 的內容交付那類似於 importFromJSON 那樣的邏輯來處理。你可將可複用的邏輯抽到單獨的專用 API 內。

**成員規格**（辭典之成員值皆為 String；**非 String 之成員逕行忽略、不使整包失敗**）：

| 成員 | 用途 | 顯示處 |
|---|---|---|
| `title` | 這套配置之短名（如「微軟新注音風格配置」） | `NSAlert` 之**標題** |
| `description` | **總體目的**（一句話，如「這套配置會讓輸入法在行為方面盡量對齊微軟新注音 2003。」） | `NSAlert` 訊息之**第一段**（其後接 `\n\n` 與被改條目清單，§4.3） |
| （其他成員） | **保留**：日後擴充（如 `author`、`createdAt`、`sourceURL` 等） | 現階段忽略（收於 `extras`） |
| 整個 `__UserDefMeta` 缺席 | **不視為錯誤** | alert 改以通用文案（`i18n:AssistantConfig.Meta.Unspecified`）代之 |

**★ 顯示之映射**：`title` → `NSAlert` 之**標題**；`description` → 訊息之**第一段**（總體目的），其後接 `\n\n` 與被改條目清單。

**字串之清洗**：`title`／`description` 皆**上限 512 字元**（超出即截斷並記一筆警告，**不**拒絕整包）、**須濾除控制字元（含 `\n`／`\r`）**——因其將被插入 alert 之單行段落。

### 3.3 命名紀律：rawValue 不得以 __ 開頭

事主明示：**「`UserDef.swift` 也得規定說 rawValue 不得以 ASCII 雙下劃線 `__` 開頭」**。此為本格式之硬性前提。

**理由**：摘除係**無條件**者（凡根層以 `__` 起頭之鍵一律先摘除、不問其形狀）——故若日後有人新增一枚以 `__` 開頭之**真偏好鍵**，它會被靜默摘除、**永遠無法匯入**；且 `exportAsJSON` 亦不得輸出之。其故障形態是「值就是存不進去」這種極難追查者——故須以紀律 ＋ 測試在**新增鍵的當下**就擋住，而非留待事後排查。

**為何取雙底線 `__`、不取單底線 `_`**：`UserDef` 之 118 條 rawValue 中**已有 2 條以單底線起頭之真偏好鍵**（`kIsDebugModeEnabled = "_DebugMode"`、`kFailureFlagForPOMObservation = "_FailureFlag_POMObservation"`），而**無一條以雙底線起頭**（`grep -c '= "__'` ＝ **0**，2026-09-24 實測）。故 `__` 為天然安全之保留命名空間。

**為何摘除必須無條件**：現行 `importFromJSON` 對未知鍵係**計入失敗**（`UserDef.swift:266-270`），故實作時須先摘除根層所有 `__` 起頭之鍵，才交付逐鍵驗證——如此，即使 `__UserDefMeta` 不是辭典（或成員值非 String），也**不會**落進逐鍵驗證而產生 `Unknown key` 失敗。

**落點（明文）**：`Sources/Shared/UserDef/UserDef.swift` 之 `enum UserDef` 之 doc comment（現無 doc comment）：

```swift
/// 偏好鍵之命名紀律：
/// - `rawValue` 即 `UserDefaults` 之鍵，一經發佈即不可更名。
/// - **不得以 ASCII 雙底線 `__` 開頭**：該前綴保留給偏好交換格式之
///   中介鍵（`__UserDefMeta`），而匯入端對根層所有 `__` 起頭之鍵
///   一律**無條件摘除**——故以 `__` 開頭之偏好鍵會永遠無法匯入。
///   （單底線 `_` 不在此限：`_DebugMode` 等即為既有的合法鍵。）
```

**落點（守衛）**：於既有之測試靶（`Tests/LibVanguardTests/`）新增一支檔案（建議 `UserDefNamingTests.swift`）：

```swift
@Test
func testNoRawValueStartsWithDoubleUnderscore() {
  for userDef in UserDef.allCases {
    #expect(
      !userDef.rawValue.hasPrefix("__"),
      "\(userDef) 之 rawValue 不得以 `__` 開頭（該前綴保留給交換格式之中介鍵）"
    )
  }
}
```

（該靶為 6.4+ 側獨有——5.10 側不宣告測試靶，故此守衛不影響 legacy 建置。）

**`vChewingSharedCLI` 之 `check-userdef-naming` 動詞構想不列入本計畫**：既有之單元測試已足夠，而多加一個 CLI 動詞屬額外維護面。

### 3.4 專用 API

落點：`Sources/Shared/UserDef/`，與既有之 JSON 交換同層。

```swift
extension UserDef {
  /// 中介辭典（`__UserDefMeta`）之內容。未知成員收於 `extras`，俾便日後擴充。
  public struct ExchangeMeta: Sendable {
    public var title: String?
    public var description: String?
    public var extras: [String: String] = [:]
  }

  /// 自交換格式之根物件摘出 `__UserDefMeta`，回傳「中介辭典」與「已摘除之其餘內容」。
  /// 摘除之判準為「鍵以 `__` 起頭」，故形狀異常者亦不會落進逐鍵驗證。
  public static func destructureExchange(
    _ root: [String: Any]
  ) -> (meta: ExchangeMeta?, payload: [String: Any])

  /// 自既有之扁平字典逐鍵驗證並寫入——**由現行 `importFromJSON` 之迴圈原封不動抽出**。
  public static func importFromDictionary(_ dict: [String: Any]) -> ImportResult

  /// **既有 API：簽名與語意不變**（解碼後逕交 `importFromDictionary`）。
  public static func importFromJSON(_ data: Data) -> ImportResult

  /// 交換格式之完整入口：解碼 → 摘除 `__UserDefMeta` → 逐鍵驗證。
  public static func importFromExchangeJSON(_ data: Data)
    -> (meta: ExchangeMeta?, result: ImportResult)

  /// 差異計算（規格見 §3.5）：僅回傳「會被實際寫入且值與當前不同」之鍵。
  public static func diffAgainstCurrent(
    _ dict: [String: Any]
  ) -> (changed: [UserDef], result: ImportResult)
}
```

**為何要抽出**：① 三條消費路徑（檔案匯入、拖放、剪貼簿）與既有之 CLI 共用同一段驗證；② `importFromJSON` 之既有呼叫端**一字不改**（設定畫面「開發道場」頁與 `MainSputnik.swift` 均不動）；③ 差異計算與套用共用同一次驗證結果，避免「先驗一次、再驗一次」之兩套邏輯漂移。交換格式之路徑即「解碼 → 摘除 `__UserDefMeta` → 交**同一個** `importFromDictionary`」。

### 3.5 差異判定

**規則**：不得以「JSON 內有出現該鍵」為準，須以「**該鍵會被實際寫入、且寫入後之值與當前值不同**」為準。即：

1. 先過既有的黑名單與逐型別值域驗證（`validNumeralValueRange` 等）；
2. 再與 `UserDefaults.current.object(forKey:)` 之當前值比較，且**兩側須先對齊到同一表示法**（布林／整數／`[String]`／`[String: Bool]`），否則會出現「明明一樣卻列為不同」之**偽陽性**。

**本設計最容易做錯之處即此偽陽性陷阱**：JSON 數字 `0/1` 與 Swift `Bool`、`Double` 與 `Int`、`NSArray` 與 `[String]` 在比較前若不歸一，alert 會列出根本不會改變的項目，使用者對清單的信任隨即瓦解。

**介面**：抽出 `UserDef.diffAgainstCurrent(_:) -> ([UserDef], UserDef.ImportResult)`——同時回傳「將變更之鍵」與「逐筆驗證結果」，供 alert 與結果訊息共用（§3.4）。

**測試必須覆蓋三類**：

1. **同值不算差異**（含跨表示法之同值：`1` 對 `true`、`24` 對 `24.0`）；
2. **值域外不算差異**（驗證失敗之鍵不得進 alert 清單）；
3. **黑名單不算差異**（黑名單鍵永不出現在清單中）。

---

## 四、規格二：「自剪貼簿匯入配置資料」按鈕

### 4.1 落點

事主定案原話：

> 或者先不用管開發道場了：
>
> 在「偏好設定 -> 一般設定」「我姓ㄅ」按鈕下方新增按鈕「點此從剪貼簿匯入（由配置助手生成的）配置資料」，運作機理與「我姓ㄅ」差不多：用 NSAlert 知會使用者「有哪些與當前設定不同的選項會被改」，讓使用者決定是否正式套用。
>
> 注意：這個交換格式裡面除了剛才提到的 json 代碼以外，還需要一個欄位來顯示這個交換格式所導入的配置的總體目的是什麼（比如說「這套配置會讓輸入法在行為方面盡量對齊XXX」）。NSAlert 在顯示 descriptions 時，先顯示總體目的，然後 `\n\n` 接續一個清單、顯示被改過的 UserDef 條目的標題。

**三項要點**：① 按鈕之落點為**「一般設定」頁、「我姓ㄅ」按鈕之下方**；② 機理**照「我姓ㄅ」之兩段式 alert**（§2.5、§4.2）；③ 交換格式**含「總體目的」欄位**（權威規格見 §3.2）。

| 事實 | 位置 |
|---|---|
| 「我姓ㄅ」按鈕本體——新按鈕即置於其**下方** | `Packages/vChewing_SettingsUI/…/SettingsUI/VwrSettingsPaneGeneral.swift:92` |
| 其 `ActiveAlert` enum 與 alert 基建（新按鈕照抄此形態） | `VwrSettingsPaneGeneral.swift:103-175` |
| 其套用函式（逐項寫 `PrefMgr.shared.*`） | `VwrSettingsPaneGeneral.swift:182-214` |
| AppKit 之對位實作（新按鈕亦須在此側行之） | `VwrSettingsPaneCocoaGeneral.swift:137-184` |
| `NSPasteboard` 先例 | §2.6 |
| 設定視窗與 IME 同進程 | §2.4 |
| 開發道場之既有 JSON 匯入，其 `importPrefsFromJSONFile(at:)` 之邏輯可供共用 | `…/VwrSettingsPaneDevZone.swift:42-53`；`…/SettingsCocoa/VwrSettingsPaneCocoaDevZone.swift:185-205` |

⇒ 新按鈕複製「我姓ㄅ」之形態（同一套兩段式 alert：確認 → 套用 → 結果），差別只在：① 資料來源為剪貼簿；② **確認訊息係由差異清單動態生成**（非固定文案）。

**兩介面共用同一段邏輯**：SwiftUI（`VwrSettingsPaneGeneral`，緊接「我姓ㄅ」之下）與 AppKit（`VwrSettingsPaneCocoaGeneral`）皆須新增此按鈕，且**與既有之檔案／拖放匯入共用同一段套用邏輯**——抽出 `applyPrefsJSONFromData(_:) -> UserDef.ImportResult`（供檔案、拖放、剪貼簿三條路徑共用），此亦順帶修好 §2.3 之缺口。

### 4.2 運作機理與五態 alert

```text
使用者按下「點此從剪貼簿匯入（由配置助手生成的）配置資料」
  → 讀 NSPasteboard.general.string(forType: .string)
  → 空 ⇒ .clipboardEmpty
  → 非 JSON、或無任何可辨識之鍵 ⇒ .failedToParse
  → 解析成功 ⇒ 與當前值逐鍵 diff（僅計「會被實際寫入且值有變」者）
        → 無差異 ⇒ .noDifferences（alert：「此配置與您當前設定無異」）
        → 有差異 ⇒ .confirmApplying
              ├─ alert 訊息：總體目的 → `\n\n` → 被改之 UserDef 條目標題清單
              ├─ 「套用」⇒ 寫入 ＋ §4.4 之和解 ⇒ .succeeded
              └─ 「取消」⇒ 靜默返回（不寫入任何東西）
```

**五態 alert**（比照 `ActiveAlert` 之 enum 寫法擴充）：`confirmApplying`／`succeeded`／`noDifferences`／`failedToParse`／`clipboardEmpty`（後兩者可合併、以訊息字串區別）。

**確認之顯示**：標題取自 `__UserDefMeta.title`（缺則用通用文案 `i18n:AssistantConfig.Meta.Unspecified`）；內文第一段為 `description`（總體目的），其後為**逐項之可讀摘要**（用 `UserDef.metaData.shortTitle` 之本地化字串）。按鈕為「套用」／「取消」。

**照既有慣例實作**：`setActivationPolicy(.accessory)` ＋ `activate(ignoringOtherApps: true)`、`runModal()`、`NSApp.popup()`（§2.4）、**已有 modal 則不重開**（`LXMgr_Core.swift:448`）、`UserDefaults.pendingUnitTests` 短路（以便測試）。既有範例：`MainSputnik.swift:233-248`（`NSAlert` ＋「授權／取消」＋ `runModal()`）、`AppDelegate.swift:184-196`（破壞性按鈕 ＋ macOS 11+ `hasDestructiveAction`）。

**取消即完全不寫入**——這是本設計的安全閥：**任何未經使用者於本機主動授權的變更，都不可能靜默發生**；授權係由「使用者親手按下按鈕」結構性地保證。

### 4.3 確認訊息之組版

事主明示之組版，三步依序：

1. **先顯示總體目的**——即 `__UserDefMeta.description`（§3.2）；
2. 然後 `\n\n`；
3. 接續一個清單，逐行顯示**被改過的 `UserDef` 條目之標題**——即 `UserDef.metaData.shortTitle` 之本地化字串（`.i18n`）。

alert 之**標題**取自 `__UserDefMeta.title`；整個 `__UserDefMeta` 缺席時，標題改用通用文案 `i18n:AssistantConfig.Meta.Unspecified`。

### 4.4 匯入後之和解

**跨介面之套用函式**：`applyPrefsJSONFromData(_:) -> UserDef.ImportResult`——三條路徑（檔案、拖放、剪貼簿）共用（§4.1）。

**和解函式**：於 `UserDef.importFromJSON`／`importFromDictionary` 之後呼叫（落點：`Shared_DarwinImpl`，與 `PrefMgr_Utilities.swift` 同層，俾使設定畫面之既有 import 一併受益）：

```swift
extension PrefMgr {
  /// 於「外部來源直接寫入 UserDefaults」之後，把推式副作用補上。
  /// `UserDef.importFromJSON` 不經 `@AppProperty`，故 13 條 didSet 不會觸發。
  public func reconcileAfterExternalPrefsImport() { … }
}
```

**內容依 §2.3 之規格**：① `fixOddPreferencesCore()`（值域與正規化）；② 逐一對 13 條帶副作用之鍵自我賦值（觸發 `didSet` 之推式同步）；③ `UserDefaults.current.synchronize()`；④ `inputHandler.assembler.maxSegLength` **非即時**——於下一次輸入源重啟時生效，此點須寫入使用者可見之說明（是否於和解中主動重推，列為 §六 之實測項）。

**本按鈕之套用者即 IME 進程本身**（§2.4），故 13 條 `didSet` 之推式副作用**就地即刻觸發**，無須任何跨行程機制。

**結果之呈現**：設定頁既有之逐筆成敗清單（含每筆失敗原因）可直接沿用；`ImportResult` 之語意不變（未知鍵／黑名單鍵計入失敗，其餘照常套用）。

### 4.5 新增 i18n

- **五態 alert 之標題／訊息／按鈕文案 × 4 語系**（`Sources/vChewingIME_macOS/Resources/{zh-Hant,zh-Hans,en,ja}.lproj/Localizable.strings`），並依既有慣例以 `LocalizableFileSorter` 維持排序。
- **`__UserDefMeta` 缺席或 `title` 缺漏時之通用文案**：`i18n:AssistantConfig.Meta.Unspecified` × 4 語系。

---

## 五、助手之契約（供助手網頁 phase）

> 本節全部內容**不在 P240 之施工範圍內**（§0.4）；其地位為**契約**：助手網頁 phase 必須遵守之產出規則、出口、形態、防漂移機制與不可退讓之約束。題庫草案見附錄 D。

### 5.1 配置包之產出規則

1. **稀疏**：只輸出使用者**明確表態**之鍵（未答＝不動＝不輸出）。
2. **型別**：strictly 依 `UserDef.dataType`（§3.1）。
3. **值域**：由後設資料之 `validNumeralValueRange` 於**前端先驗**，但**不得因此略去後端驗證**——後端才是權威。
4. **格式**：鍵序依 `allCases` 之宣告序（與 `exportAsJSON()` 之 `.sortedKeys` 不同；此處刻意選宣告序，因助手有 `allCases` 之知識、且宣告序對人閱讀更友善）。**兩種輸出版本**：① 下載檔用之 pretty-print；② 剪貼簿用者同上（pretty-print 較利於必要時目視檢查）。深層連結用之 minified percent-encoded 版本見附錄 A。
5. **必須含**：**`__UserDefMeta` 辭典**（至少含 `description` ＝總體目的；建議連 `title`）——見 §3.2。
6. **不得含**：黑名單鍵（助手根本不該出這幾題——`kUserDataFolderSpecified`／`kCassettePath` 需使用者於 GUI 親自選路徑、`kAppleLanguages` 由系統設定決定，其餘為暫態）；**`__` 起頭之其他鍵**——根層之中介鍵**只准** `__UserDefMeta` 一枚（§3.3）。
7. **「回到出廠預設」之可行性**：`UserDef` 之預設值即 `DataType` 載荷，且 `AppProperty.init` 會在原鍵缺失時種下預設值。故「回復預設」**無須新增任何 IME 機制**：助手只要輸出該鍵之 `defaultValue` 即可。**唯一的語意落差**：少數鍵之預設值經 `fixOddPreferencesCore()` 之夾限或正規化（如 `kCandidateKeys` 之去重）——故「回復預設」對這些鍵之結果以 IME 側之正規化後值為準，助手應在摘要頁註明。**不新增「移除鍵」語意**——`exportAsJSON` 之語意是「值」，憑空多出「刪除」語意會使格式與 CLI 行為一起複雜化。

### 5.2 出口

- 〔**複製配置資料**〕→ 剪貼簿（`NSPasteboard.general.setString(_:forType: .string)`）。**此為現階段之主出口**：使用者再至「偏好設定 → 一般設定」按「點此從剪貼簿匯入（由配置助手生成的）配置資料」（§四）。
- 〔**下載配置檔案**〕→ `vChewing_Preferences.json`（檔名與既有 `fileExporter` 一致）＋ 使用指示。此路線走既有之拖放／檔案匯入或 CLI，無須本計畫之新機制（§2.2）。
- **助手最終頁之三步指示**：〔複製設定包〕→「開啟 唯音偏好設定 → 一般設定」→「按『點此從剪貼簿匯入…』」。**導引一律以文字說明為之**：助手**不得**以任何深層連結或 URL scheme 代開設定視窗。
- （若日後啟用附錄 A 之路線）第三出口〔直接套用〕→ `vchewing://prefs/apply?data=…&nonce=…&v=1`；兩條套用路徑不應同時提供，以免使用者被弄混。

### 5.3 助手之形態

**本文之設計立場：產物採單檔自足之 HTML**（`dist/assistant.html`，可雙擊開啟）——多檔 ESM 為備選（附錄 B.3），本項尚待事主核定（§七 第 4 項）。理由：

1. **沒有 ESM／CORS 陷阱**——`file://` 下載入外部 ES module 會被瀏覽器拒絕；單檔產物解鎖三個部署情境：上架網站、隨 app bundle 出貨（`NSWorkspace` 開 `file://`）、離線轉交。
2. **主站（Jekyll／GitHub Pages）不會執行 npm**，故必須提交「已建置的產物」；單檔讓這件事變得乾淨（一個檔案，而非一坨 `assets/`）。
3. **可被官網直接嵌入**（§0.3 之約束 3）：官網只需處理一個檔案（放進 Jekyll 之任一目錄，或作為一個頁面之 body），不必處理 `assets/` 目錄樹、不必讓 Jekyll 執行 npm。
4. 本機預覽不需要起 HTTP 伺服器（雙擊即可）。

**技術選型**：

- **語言**：TypeScript（本機已具備）。
- **框架**：**不用**。整個助手是「一組步驟 × 一組表單控制項 ＋ 一個純函式的『答案 → JSON』轉換」；引入框架會帶來 version churn 與建置複雜度，而收益為零。
- **打包**：**`esbuild`（唯一 devDependency）**，以 `--bundle --format=iife` 產出**單一 JS**，再內聯進一份 HTML 模板（含 CSS）。
- **不使用**：`Vite`／`Webpack`／`Parcel`（對本規模過重）、任何 UI 框架（無收益）、`_sass` 之 Jekyll 資產（與主站主題耦合，反使助手不能獨立測試）。
- **本機實測環境**：Node `v22.20.0`、npm `11.15.0`（registry `https://registry.npmjs.org/` 可達：`npm view esbuild version` → `0.28.2`）、TypeScript **`7.0.2`**（全域 `typescript` 套件，即 Go 原生版；`tsc` 之 emit 能力正常——`enum` 降級、`#private`、泛型箭頭函式、`satisfies`、ESM 輸出皆如期產出）。
- **⚠ TS 7 之遷移變更（實測發現）**：若 `tsconfig.json` 未顯式指定 `rootDir`，`tsc` 會報 **TS5011**（"The common source directory of 'tsconfig.json' is './src'. The 'rootDir' setting must be explicitly set to this or another path"），並將產物佈局改為 `dist/src/…`。⇒ 本專案的 `tsconfig.json` **必須**顯式寫 `rootDir`。

**目錄結構**（`vChewing-macOS/ValueAdd/WebConfigAssistant/`）：

```text
ValueAdd/WebConfigAssistant/
├── Makefile                     ← 本目錄專用；不動主倉 Makefile
├── README.md                    ← 建置／預覽／部署／後設資料再生成（zh-Hant）
├── package.json                 ← devDeps：typescript、esbuild；scripts 全由 Makefile 驅動
├── tsconfig.json
├── .gitignore                   ← node_modules/、dist/、*.local
├── index.html                   ← 模板（含 {{STYLE}} / {{SCRIPT}} 佔位）
├── src/
│   ├── main.ts                  ← 掛載、讀 URL（lang／step）、鍵盤導覽
│   ├── shell.ts                 ← Win2000 風之外框：左側步驟列、底部按鈕、進度
│   ├── widgets.ts               ← 單選／複選／下拉／數字／開關（回傳 UserDef 相容值）
│   ├── steps/
│   │   ├── step00-welcome.ts
│   │   ├── step01-background.ts    ← 「您用哪一款輸入法」——分支樞紐
│   │   ├── …
│   │   └── step99-summary.ts
│   ├── preset.ts                ← 答案 → 稀疏 JSON（純函式，核心可測件）
│   ├── deeplink.ts              ← 設定包 → vchewing:// URL（純函式；附錄 A 之路線）
│   ├── schema.ts                ← 讀後設資料、提供逐鍵值域與型別檢查
│   └── i18n/
│       ├── index.ts             ← 語言偵測（URL > navigator.language > zh-Hant）
│       └── {zh-Hant,zh-Hans,en,ja}.ts   ← 由後設資料生成，見 §5.4
├── assets/
│   ├── userdef-metadata.json    ← 由 UserDef 導出（提交入庫；漂移由 make 檢查）
│   └── assistant.css
├── tests/
│   ├── preset.test.ts
│   ├── deeplink.test.ts
│   └── fixtures/*.json          ← 供 Swift 側契約測試共用之範例設定包
└── tools/
    └── inline.mjs               ← 把 bundle ＋ css 塞進 index.html（單檔產物）
```

**★ 不跨倉之建置約束**：**WebConfigAssistant 之建置與執行不得依賴 `vChewing-macOS` 以外之任何倉。** 故本目錄之 Makefile **一律只用倉內既有資源**——後設資料導出走 `vChewing-macOS` **自己那份** `Packages/vChewing_OSNeutral_LibVanguard`（該套件之 manifest 只相依其內之 `Deps/VanguardSwiftExtension` 巢狀套件，故 `swift run --package-path …` 全離線自足、不觸網、不觸及倉外），**不以上溯至工作區根、更不引用 `vChewing-LibVanguard`**。（惟該 CLI 之原始碼係**同源雙份**：實作該動詞時**須同步 `vChewing-LibVanguard` 之正本、並逐檔 `cmp` 驗證逐位元組相同**——見 §5.4.5。此為**原始碼同步之義務**，**不是**本目錄之建置相依。）

**與兩套既有建置系統之關係（已實查，兩者皆不受影響）**：

- **SPM**：`Package.swift` 之 `vChewing` 目標為 `path: "./Sources/vChewingIME_macOS"`，**不含 `ValueAdd`** ⇒ 助手目錄內任何檔案都不會被 SPM 看見。
- **Xcode**：`ValueAdd` 是 `PBXFileSystemSynchronizedRootGroup`（`vChewing.xcodeproj/project.pbxproj:143`），故 Xcode 會**自動列舉**其內容。實測 Release 產物內**無** `ValueAdd/PKGInstallerAssets`／`RawImages` ⇒ 既有內容不落入 app bundle。
- **⚠ 但**：`node_modules/` 動輒數萬個檔案，被 Xcode 列舉會拖慢索引。**作法**：於 `project.pbxproj` 之該同步群組的 `PBXFileSystemSynchronizedBuildFileExceptionSet` 內為 `WebConfigAssistant` 增列例外（形制照既有之 `RawImages/*` 條目），或至少於實作後開 Xcode 確認索引未失控。**此事列為實作驗收項之一**（§六）。

**觀感與可用性（Windows 2000 安裝程式風格）**：

- 版面：左側 164 px 白色區塊放「本步驟之大圖示／大字」＋ 一條深藍漸層標題帶；右側內容區；右下角按鈕列「`< 上一步`｜`下一步 >`｜`取消`」，末頁改「`完成`」。
- 色彩：經典灰 `#D4D0C8` 底色、標題帶 `#0A246A` → `#A6CAF0` 漸層、內凹分組框（`border: 2px groove`）、按鈕用 outset 斜角（左上白／右下深灰）。字型 `Tahoma, "MS Sans Serif", system-ui, sans-serif`。
- 進度：右上角「步驟 3 / 10」＋一排分段方塊（非百分比條）。
- **★ 必須保留的現代可用性**（復古不可凌駕無障礙）：① 對比度 ≥ 4.5:1；② 可見焦點環；③ 全鍵盤可操作（Tab／方向鍵選單選、Alt+← 上一步、Enter 下一步）；④ `prefers-reduced-motion` 時停用動畫；⑤ `role="radiogroup"` / `<fieldset><legend>` 之語意標記。
- 每頁之「深入說明 →」連回官網對應文章錨點（§1.4）。

**i18n**：

- 助手自身之**介面文字**（步驟標題、按鈕、說明句）為手寫之四語系表，置於 `src/i18n/*.ts`。
- **偏好選項之標籤與說明**則由 §5.4 之導出檔供給（自動、四語系）。
- 語言決定序：URL `?lang=` ＞ `navigator.language` ＞ `zh-Hant`。四語系沿用專案既有之 `zh-Hant` / `zh-Hans` / `en` / `ja`（注意 `-CHS` 之風格規則：**簡體只簡化字形、保留台灣用語**——`支援` 不寫成 `支持`、`記憶體` 不寫成 `内存`）。
- 切換語言**不得**重置答案狀態。

**部署**：

- **產物 = `dist/assistant.html`（單檔自足）**（§0.3 之約束 3）。
- **首選之嵌入形態**：置於官網倉之 `<某目錄>/index.html`（例如 `assistant/`），則網址即 `<主站>/assistant/`。**若事主決定納入官網之導覽／側欄**，該檔可能需要 front-matter 或改寫為 Jekyll 頁面——**此屬官網側之決定**；本目錄只負責產出「內容單一、不與站台主題耦合」的 HTML。
- **上架**：`make deploy` 複製為 `vChewing-HomePage.io/<DEPLOY_SUBDIR>/index.html`（`DEPLOY_SUBDIR` 預設 `assistant`，可覆寫），於官網倉提交。Jekyll **不執行 npm**，故「提交已建置產物」是 GitHub Pages 下之唯一路線；檔首應加一行 HTML 註解表明其為**生成物**及其生成指令。
- **推廣動作暫緩**（§0.3 之約束 3）：「於 `onboarding/README.md` 置頂一顆『▶ 開啟配置助手』」與「於 `manual/preferences.md` 之介面概觀補一句」皆不做。
- **助手 → 文章之單向連結**：保留（§1.4 之「深入說明 →」）；以**相對路徑**書寫，以備「助手與官網同網域」與「助手獨立部署」兩種情形。
- **隨 app 出貨（選配）**：把 `assistant.html` 放進 app bundle，以 `NSWorkspace` 開 `file://` ⇒ 全離線可用。此路線正交於第 1 層，且能覆蓋「無網路」與「不想開瀏覽器連外」的場合。**列為助手網頁 phase 之後續**（§七），勿一次塞入。

### 5.4 防漂移

**問題**：助手必須知道 118 條鍵之**名稱、型別、值域、預設值、可讀標籤**。手抄必然漂移。

**落點：`vChewingSharedCLI`**（該 CLI 為可改造對象）⇒ 於該 CLI 新增 `dump-userdef-metadata` 動詞。以下為據此而定之規格。

#### 5.4.1 動詞介面

```sh
swift run vChewingSharedCLI dump-userdef-metadata [<locale>=<path-to-.strings>]... [--strict]
```

- 形式沿用該 CLI 既有之**位置引數**風格（其餘動詞皆為 `paths: [String]`），僅以 `locale=path` 載明語系。例：
  ```sh
  swift run vChewingSharedCLI dump-userdef-metadata \
      zh-Hant=<…>/zh-Hant.lproj/Localizable.strings \
      zh-Hans=<…>/zh-Hans.lproj/Localizable.strings \
      en=<…>/en.lproj/Localizable.strings \
      ja=<…>/ja.lproj/Localizable.strings > assets/userdef-metadata.json
  ```
- **不給任何 `locale=path` 時，仍輸出完整之程式面後設資料（無標籤）**——使該動詞在沒有 `.strings` 的環境下依然可用、且便於測試。
- **`stdout` 必須是純 JSON**（俾使 `> file.json` 直接可用）。一切進度、警告、缺鍵報告走 **`stderr`**。此點與該 CLI 其餘動詞「進度印 stdout」之慣例**刻意不同**，須在用法說明內載明。
- **退出碼**（該 CLI 現行無退出碼紀律，本動詞為新設、不影響既有行為）：`0` 成功；`1` 引數不合法／`.strings` 讀不到；加 `--strict` 時，任一 case 之 `isMetadataPendingManualUpdate` 為真、或任一語系缺任一鍵，即回 `1`（使 CI 得以把「i18n 未補齊」變成紅燈）。

#### 5.4.2 輸出 schema

```json
{
  "schemaVersion": 1,
  "generator": "vChewingSharedCLI dump-userdef-metadata",
  "locales": ["zh-Hant", "zh-Hans", "en", "ja"],
  "count": 118,
  "entries": [
    {
      "key": "kUseRearCursorMode",
      "rawValue": "UseRearCursorMode",
      "type": "bool",
      "default": false,
      "range": null,
      "minimumOS": 10.9,
      "exchangeBlacklisted": false,
      "metadataPending": false,
      "options": [
        { "value": 0, "label": "將游標置於詞語前方 // macOS 內建注音風格" },
        { "value": 1, "label": "將游標置於詞語後方 // Windows 微軟新注音風格" }
      ],
      "labels": {
        "zh-Hant": { "shortTitle": "選字游標:", "description": "請選擇用以觸發選字的游標相對位置。" },
        "zh-Hans": { "…": "…" }, "en": { "…": "…" }, "ja": { "…": "…" }
      }
    },
    {
      "key": "kCandidateListTextSize",
      "rawValue": "CandidateListTextSize",
      "type": "integer",
      "default": 24,
      "range": [12, 196],
      "minimumOS": 10.9,
      "exchangeBlacklisted": false,
      "metadataPending": false,
      "options": null,
      "labels": { "…": { "…": "…" } }
    }
  ],
  "missingI18nKeys": [
    { "locale": "ja", "key": "i18n:UserDef.kXxx.description" }
  ]
}
```

- `type` 取 `DataType` 之四種名稱（`bool`／`integer`／`double`／`string`／`arrayOfStrings`／`dictionary`——以既有之 `defaultsCommandTypeName` 為基礎對位）。
- `range` 即 `validNumeralValueRange`，非數值鍵為 `null`。
- `minimumOS` 取自 `MetaData.minimumOS`（**助手須據此決定是否出題**——`manual/preferences.md` 已載明舊版 AppKit 介面會隱藏需要較新系統的選項）。
- `metadataPending` 即該 case 之 `isMetadataPendingManualUpdate`（供 `--strict` 與人工稽核用）。
- `missingI18nKeys` 為**額外收益**：一份「四語系 `.strings` 對 `UserDef` 標籤之覆蓋率報告」。本倉目前沒有任何工具在做這件事——`generate-missing-strings` 只針對 `.strings` 之間互相對位，不驗與 `UserDef` 之對位。此報告可直接當 i18n 稽核用。
- **決定性與冪等**：`entries` 依 `allCases` 之**宣告序**（穩定、可 diff）；`JSONSerialization` 之 `[.prettyPrinted, .sortedKeys]`（物件內鍵序穩定；陣列序不受影響）；`missingI18nKeys` 先按 `locale` 再按 `key` 排序。輸出可寫入後直接與入庫版 `cmp`。輸出前須 `JSONSerialization.isValidJSONObject` 斷言（與既有 `exportAsJSON` 同款自保）。

#### 5.4.3 施工前提（已實查）

| # | 事實 | 後果 |
|---|---|---|
| 1 | `vChewingSharedCLI` 之三個原始檔在兩倉**逐位元組相同**（`cmp` 實測）：`VCSharedCLI_main.swift`（374 行）、`VCSharedCLI_UserDefImpl.swift`（89 行）、`VCSharedCLI_NonUserDefI18nMap.swift`（22 行） | **建置與執行一律只走倉內那份**（`vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard`）——**不跨倉**。**惟原始碼係同源雙份，施工時必須同步正本**（程序見 §5.4.5），現階段**維持兩份逐位元組一致** |
| 2 | `Product.executable(name: "vChewingSharedCLI")` 於 `Package.swift:63-68`；`Target.executableTarget` 於 `:186-194`（`dependencies: ["Shared"]`、`.defaultIsolation(MainActor.self)`）。**兩倉皆已宣告** | **新增動詞無須改任何 manifest** |
| 3 | 兩倉之 `Package@swift-5.10.swift` 皆明示**不收 `vChewingSharedCLI`**（理由：它是該側唯一可執行檔，會被壓上 10.13 之 minOS，與 10.9 地板牴觸） | **5.10 側亦無須改動** |
| 4 | `.github/` 內對 `vChewingSharedCLI` 之命中數為 **0** | **CI 無涉** |
| 5 | `import Shared` 即足以取得一切所需：`UserDef.allCases`、`dataType`／`DataType`（`defaultValue`、`defaultsCommandTypeName`）、`metaData`／`MetaData`（`shortTitle`／`prompt`／`inlinePrompt`／`popupPrompt`／`description`／`options`／`minimumOS`／`toolTip`）、`validNumeralValueRange`、`jsonExchangeBlacklist` | 不必動 `Shared`（**零 API 新增**） |
| 6 | i18n 鍵之命名規範**已被編碼**在 `VCSharedCLI_UserDefImpl.swift`：`i18n:UserDef.<caseName>.<label>`、`i18n:UserDef.<caseName>.option.<idx>`（以 `Mirror` 走訪 `MetaData`，新增欄位自動涵蓋） | 標籤鍵可**生成**、不必手抄 |
| 7 | **實測統計（HEAD）**：118 cases／118 `dataType` arms／118 `metaData` arms（其中 **7** 條回 `nil`）；`metaData` 內之可讀字串**全部**已是 `i18n:` 形式（bare literal 計 **0**、`i18n:` literal 計 257） | `isMetadataPendingManualUpdate` 目前對所有 case 皆 false ⇒ 嚴格模式今日不會誤報 |
| 8 | 四語系 `.strings` 為 **old-style plist**（`plutil -lint` → OK），鍵即 `i18n:UserDef.*`（實例：`i18n:UserDef.kUseRearCursorMode.option.1` = 「將游標置於詞語後方 // Windows 微軟新注音風格」、`i18n:UserDef.kCandidateListTextSize.shortTitle` = 「選字窗字號:」） | 可用 `NSDictionary(contentsOfFile:)` 直接查鍵，**不必自寫 `.strings` 解析器** |

#### 5.4.4 效益

1. 標籤與說明**直接複用 app 自己已翻譯好的字串** ⇒ 助手之四語系 i18n **自動生成**，無須另做一份翻譯，且**永不與 app 措辭分歧**。
2. `options` 即各單選題之選項標籤來源（含值與標籤之對應，故助手不必知道任何魔術數字）。
3. `make metadata` 可將「Swift 側已改、助手未跟上」變成**可偵測的失敗**（重新導出後與入庫版 diff）。
4. `range`／`type`／`default` 使助手之前端先驗有單一真源。
5. `missingI18nKeys` 順帶補上一個本倉缺的 i18n 稽核能力。

#### 5.4.5 施工程序（含正本同步）

> **現階段維持兩份一致**（事主指示）；「如何處置此重複」另行裁定。故下列同步步驟**屬必經**。

1. **改正本**：於 `vChewing-LibVanguard/Sources/vChewingSharedCLI/` 新增該動詞（新檔 ＋ `VCSharedCLI_main.swift` 之三行改動：`switch` 分支、`printUsage()` 一行、`case` 之實作入口）。
2. **自證**：於正本 `swift run -c release vChewingSharedCLI dump-userdef-metadata …`，確認輸出合於 §5.4.2 之 schema，並含 §六 所述之冪等（連跑兩次 `cmp` 相同）。
3. **同步鏡像**：把**同三檔**複製進 `vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard/Sources/vChewingSharedCLI/`（兩目錄檔名一一對應，可直接覆蓋）。
4. **逐檔驗證逐位元組相同**（形制照本工作區既有作法）：
   ```sh
   A=vChewing-LibVanguard/Sources/vChewingSharedCLI
   B=vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard/Sources/vChewingSharedCLI
   for f in VCSharedCLI_main.swift VCSharedCLI_UserDefImpl.swift VCSharedCLI_NonUserDefI18nMap.swift; do
     cmp -s "$A/$f" "$B/$f" && echo "same  $f" || echo "DIFF  $f"
   done
   ```
   三行皆須 `same`；並將三檔之 md5 記入 Phase 239 之記錄（比照本工作區多數 phase 之記載方式）。
5. **產物**：於 `ValueAdd/WebConfigAssistant/` 跑 `make metadata` 產出 `assets/userdef-metadata.json` 並提交；`make metadata-audit` 應綠。
6. **等效性抽驗（可選、人工，不屬 assistant 之 Makefile）**：同一份 `.strings` 之下，正本那份 CLI 之輸出應與鏡像那份**逐位元組相同**（`cmp`）——此為「同源雙份仍等效」之直接證據。

#### 5.4.6 Makefile 與測試之接線

`make metadata` 即上述命令，改為「導出至暫存檔 → 與 `assets/userdef-metadata.json` `diff` → 有差即 `exit 1`」，並讓 `build`／`audit` 依賴之（助手之產物契約因此不可能與 Swift 側脫節）。測試見 §六。

**實作成本估算**：一支新檔（約 150–250 行 Swift，含 `--strict` 與缺鍵報告）＋ `VCSharedCLI_main.swift` 之 3 行（`case` 分支、`printUsage()` 一行、`switch` 之動詞）＋ 兩倉原始碼之逐位元組鏡像（**原始碼同步層面；本目錄之建置只走倉內那份 `Packages/vChewing_OSNeutral_LibVanguard`**）＋ assistant 側一個 Makefile 目標。**不動任何 Swift 生產路徑、不動 manifest、不動 CI、不跨倉。**

```make
# ValueAdd/WebConfigAssistant/Makefile
# 本目錄專用。主倉 Makefile 不受影響、亦不呼叫本檔。

NPM            ?= npm
NPX            ?= npx
PYTHON         ?= python3
HOMEPAGE_REPO  ?= ../../../vChewing-HomePage.io
DEPLOY_SUBDIR  ?= assistant
PORT           ?= 8787
CLI_PKG        ?= ../../Packages/vChewing_OSNeutral_LibVanguard
STRINGS_DIR    ?= ../../Sources/vChewingIME_macOS/Resources
METADATA       := assets/userdef-metadata.json
METADATA_TMP   := dist/userdef-metadata.json

.PHONY: help init build bundle inline watch serve preview test lint metadata metadata-audit audit deploy clean

help:            ## 列出可用目標
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

init:            ## 安裝開發相依（首次）
	$(NPM) install

build:           ## 型別檢查 + 編譯至 dist/
	$(NPX) tsc --project tsconfig.json

lint:            ## 只做型別檢查、不輸出
	$(NPX) tsc --project tsconfig.json --noEmit

watch:           ## 增量編譯
	$(NPX) tsc --project tsconfig.json --watch

bundle: build     ## 打包成單一 IIFE（esbuild）
	$(NPX) esbuild dist/main.js --bundle --format=iife --target=es2020 --minify \
	        --outfile=dist/assistant.js

inline: bundle    ## 產出單檔自足助手：dist/assistant.html（可直接雙擊）
	node tools/inline.mjs

serve:            ## 本機預覽（僅開發期需要；產物本身可雙擊開啟）
	cd dist && $(PYTHON) -m http.server $(PORT)

test: build       ## 單元測試（node:test，零額外相依）
	node --test dist/tests/

metadata:         ## 自 UserDef 重新導出後設資料，並驗證與入庫版一致（防漂移）
	@mkdir -p dist
	swift run -c release --package-path $(CLI_PKG) vChewingSharedCLI dump-userdef-metadata \
	    "zh-Hant=$(abspath $(STRINGS_DIR))/zh-Hant.lproj/Localizable.strings" \
	    "zh-Hans=$(abspath $(STRINGS_DIR))/zh-Hans.lproj/Localizable.strings" \
	    "en=$(abspath $(STRINGS_DIR))/en.lproj/Localizable.strings" \
	    "ja=$(abspath $(STRINGS_DIR))/ja.lproj/Localizable.strings" \
	    > "$(abspath $(METADATA_TMP))"
	cmp -s "$(METADATA_TMP)" "$(METADATA)" || { \
	    echo "後設資料已漂移。請以 dist/userdef-metadata.json 覆蓋 assets/userdef-metadata.json。"; exit 1; }

metadata-audit:   ## 上述導出之嚴格模式：任一 i18n 鍵缺漏即失敗（i18n 稽核）
	@mkdir -p dist
	swift run -c release --package-path $(CLI_PKG) vChewingSharedCLI dump-userdef-metadata \
	    "zh-Hant=$(abspath $(STRINGS_DIR))/zh-Hant.lproj/Localizable.strings" \
	    "zh-Hans=$(abspath $(STRINGS_DIR))/zh-Hans.lproj/Localizable.strings" \
	    "en=$(abspath $(STRINGS_DIR))/en.lproj/Localizable.strings" \
	    "ja=$(abspath $(STRINGS_DIR))/ja.lproj/Localizable.strings" \
	    --strict > /dev/null

audit: lint test metadata  ## 提交前總檢

deploy: inline    ## 複製產物進官網倉
	@test -d "$(HOMEPAGE_REPO)" || { echo "找不到官網倉：$(HOMEPAGE_REPO)"; exit 1; }
	mkdir -p "$(HOMEPAGE_REPO)/$(DEPLOY_SUBDIR)"
	cp dist/assistant.html "$(HOMEPAGE_REPO)/$(DEPLOY_SUBDIR)/index.html"
	@echo "已部署。請於官網倉提交 $(DEPLOY_SUBDIR)/index.html"

clean:
	@echo "手動清理：請將 node_modules/ 與 dist/ 移入 tmp/_filesToTrash"
```

> **`clean` 之註記**：本工作區之自動化規則禁絕 `rm -rf`（須移入 `tmp/_filesToTrash`）。故 `clean` 目標**不執行刪除**，只印提示——以免自動化流程被權限確認中斷。此為對本工作區既有紀律之遵循，非疏漏。

**相對路徑之核對**：`vChewing-macOS/ValueAdd/WebConfigAssistant` → `..`＝`ValueAdd`、`../..`＝`vChewing-macOS` ⇒ 官網倉為 `../../../vChewing-HomePage.io`、**CLI 所在之套件為 `../../Packages/vChewing_OSNeutral_LibVanguard`**、四語系 `.strings` 為 `../../Sources/vChewingIME_macOS/Resources`。✅

### 5.5 題庫與不可退讓之約束

**題庫不新造，而是把既有文件之分支與處方形式化**（§2.7）。草案見附錄 D。

**每一頁題組之結構**（三層，供不同深度之使用者）：

1. **一句話的處境**（給所有人）：「您用哪一款輸入法？」
2. **幾個單選／多選**（給所有人）：選項標籤取自 `UserDef.metaData.options`／`shortTitle`，**不自造**。
3. **可折疊的「為什麼問這個」**（給進階者）：一段說明 ＋ **「深入說明 →」連回對應的 `onboarding/*.md` 或 `manual/preferences.md` 錨點**。

**題組分頁之對位**：`manual/preferences.md` 之 12 頁 × 子節標題，與助手之題組分頁**一一對位**；助手的題組分頁沿用這 12 頁之命名，使用者回頭查文件時心智模型一致（§2.7）。

**分支規則**：僅少數幾處真正的分支（例如「您主要用注音」⇒ 跳過拼音題組；「逐字選字派」⇒ SCPC 題組取代組句題組；「來自行列／倉頡」⇒ 顯示磁帶相關題組）。其餘以「未作答＝不動」處理，避免問卷爆炸。

**★ 不可退讓之約束**：**每個單選題之預設選項一律為「維持不變（推薦）」，該題即不輸出任何鍵。** 助手**不得**在使用者未表態處代為決定，否則「跑一次助手」會變成一次非自願的大範圍覆寫。若使用者勾選「以推薦值補齊未答之項目」，則以 `UserDef.dataType.defaultValue` 填充該題組所涉之鍵（**明示且逐組**，非全域）。

**助手之「推薦值」之定位**：每頁註明「這些是可選的起點，不是必須」。

**契約測試之目標**：建議以「每個 `onboarding_*.md` 對應一份 fixture」為目標——既測助手、又把既有文章之處方**固化成可執行規格**（§六）。

**助手之題庫標籤與 i18n**：標籤與說明由 §5.4 之導出檔供給（四語系、自動）；助手自身介面文字為手寫四語系表；語言決定序與 `-CHS` 風格規則見 §5.3。

---

## 六、驗證要求

### 6.1 Swift 側單元測試

| 項 | 驗證內容 |
|---|---|
| `UserDefNamingTests` | 全數 rawValue 皆不以 `__` 開頭（§3.3） |
| `diffAgainstCurrent(_:)` | 三類：同值不算差異（含跨表示法同值）／值域外不算差異／黑名單不算差異（§3.5） |
| `destructureExchange(_:)` | 根層以 `__` 起頭之鍵**無條件摘除**；`__UserDefMeta` 形狀異常（非辭典、成員非 String）時不使整包失敗（§3.2、§3.3） |
| `importFromDictionary(_:)` | 與既有 `importFromJSON` 語意一致；未知鍵／黑名單鍵 ⇒ 逐筆失敗（沿用 `ImportResult`） |
| `importFromExchangeJSON(_:)` | 解碼 → 摘除 → 逐鍵驗證；回傳 `(meta, result)` |
| `exportAsJSON()` | 不得輸出任何以 `__` 起頭之鍵（§3.3） |
| `title`／`description` 之清洗 | 512 字元上限（超出截斷並記警告、不拒絕整包）＋控制字元（含 `\n`／`\r`）濾除（§3.2） |
| `reconcileAfterExternalPrefsImport()` | 對 13 條 `didSet` 之**觸發斷言**（§2.3、§4.4） |
| 按鈕流程 | 五態 `ActiveAlert` 之流程（確認／成功／無差異／解析失敗／剪貼簿空）；以 `UserDefaults.pendingUnitTests` 短路（§4.2） |

### 6.2 契約測試與後設資料稽核

- **契約測試（最強手段；承 §5.3 之不跨倉約束）**：把 `tests/fixtures/*.json` 複製進 **`vChewing-macOS` 內**某個測試靶之資源，斷言 **`UserDef.importFromJSON(fixture)` 之 `failures.isEmpty`**。如此，**助手一旦產出 IME 不收的包、Swift 側測試即紅**。
  該靶應選 **macOS 倉獨有**者（例如既有之 `Packages/vChewing_SettingsUI` 之測試靶——其為 macOS 專屬，且已相依 `LibVanguard` 故可直接呼 `UserDef.importFromJSON`），**而非** `vChewing_OSNeutral_LibVanguard` 之測試靶：後者與 `vChewing-LibVanguard` 維持逐位元組鏡像，為它增設測試資源會連帶改動兩倉 manifest，與 §5.4.3 第 2 條「無須改 manifest」之益處相衝。**無論選何者，此測試只在 `vChewing-macOS` 之內**（落點之裁定見 §七）。
- **助手側之純函式單元測試**（`node --test`，零額外相依）：`preset.ts`（答案物件 → JSON 之逐案例：稀疏性、型別、值域、預設值填充、黑名單鍵永不出現）；`schema.ts`（後設資料之覆蓋率——**118 條鍵是否皆在 metadata 內**）；`deeplink.ts` 之測試見附錄 A。
- **`make metadata`**：Swift 側後設資料與入庫版之 diff 檢查（漂移偵測）。
- **`make metadata-audit`**：上述導出之 `--strict` 模式——任一語系缺任一 `UserDef` 標籤鍵即失敗。**此為本倉目前不存在之 i18n 稽核能力**：既有之 `generate-missing-strings` 只做 `.strings` 之間之互相對位，**不驗與 `UserDef` 之對位**。
- **`dump-userdef-metadata` 自身之驗證**（實作該動詞時應一併附上）：① **冪等**——同一輸入連跑兩次，輸出逐位元組相同；② 不給任何 `locale=path` 時仍輸出合法 JSON、且 `entries.count == 118`；③ 給一份刻意缺鍵之臨時 `.strings` 時 `missingI18nKeys` 非空、且 `--strict` 回 `1`；④ `entries[].key` 之集合恆等於 `UserDef.allCases` 之集合；⑤ **不變式**：任一帶 `range` 之 entry，其 `default` 必落在 `range` 之內（此即「後設資料所稱之預設值，必為 `importFromJSON` 之 `validateAndApply` 所接受者」之最低保證）。
  **載體**：上述 ①–⑤ **可以不必新增 Swift 測試靶**——於 WebConfigAssistant 之 `Makefile` 以 shell ＋ `python3` 對導出檔做檢查即可（跑兩次 `cmp`、`python3 -c` 斷言 `count`／鍵集／`range` 包含 `default`）。此可保住 §5.4.3 第 2 條「**新增動詞無須改任何 manifest**」之性質；若改採一等公民的 Swift 測試靶，則須為該 executable 靶新增一個測試靶，**那會同時改動兩倉之 `Package.swift` 與 5.10 manifest（後者須再添一條不收錄之說明）**，成本與本動詞本體同量級。**本文建議走 shell 路線**（理由：該動詞之產物本身即資料、資料之驗證用比對最直接；且 CLI 靶自來無測試靶、維持一致）。載體之裁定見 §七。

### 6.3 實機實測項

| # | 問題 | 方法 | 影響 |
|---|---|---|---|
| 1 | 讀取一般剪貼簿是否需要額外 entitlement？ | 以實作版實測 | §2.6、§4.2 |
| 2 | 修改 `candidateListTextSize` 後，候選窗寬度是否需一次建池才跟隨？ | 實機觀察 | §2.3 末（純外觀） |
| 3 | IME 進程能否自 `SessionHost` 取得當前 `InputHandler`，以於和解中即時重推 `maxSegLength`？ | 讀 `SessionHost` 之既有閉包表 | §2.3 第 4 點、§4.4 |
| 4 | Xcode 之 `ValueAdd` 同步群組遇 `node_modules/` 之索引影響 | 加例外集前後開 Xcode 對照 | §5.3（實作驗收項） |

### 6.4 風險與緩解

| # | 風險 | 等級 | 緩解 |
|---|---|---|---|
| 1 | 匯入後 `didSet` 不觸發導致「看起來沒生效」 | 中 | §4.4 之和解（三條匯入入口共用）；並一併修既有 import 路徑 |
| 2 | 助手與 `UserDef` 漂移（新增偏好、改值域、改標籤） | 中 | §5.4 之導出 ＋ `make metadata` ＋ §6.2 之契約測試 |
| 3 | 助手與官網文件雙軌漂移 | 中 | 助手單向連回文章（§1.4）；「於 `manual/preferences.md` 逐選項加註」暫緩（§0.3 之約束 3） |
| 4 | 復古樣式犧牲無障礙 | 中 | §5.3 之五條硬性可用性要求；Windows 2000 風格僅止於**外觀**，不繼承其互動缺陷（如無鍵盤導覽） |
| 5 | 單檔產物入庫使 diff 難讀 | 低 | 檔首生成註解；來源（`src/`）始終為真源；`dist/` 進 `.gitignore`（僅部署副本入官網倉） |
| 6 | 助手之「推薦值」被當成「唯音的官方立場」 | 低 | 每頁註明「這些是可選的起點，不是必須」；預設選項一律「維持不變」（§5.5） |

---

## 七、未決事項

以下四項尚未經事主核定。**四項皆不阻塞 P240 動工。**

1. **既有之檔案／拖放匯入路徑是否一併補和解**（§2.3、§4.4）：本文建議**一併修**——既然要抽出共用之 `applyPrefsJSONFromData(_:)`，順帶即完成；且該缺口今天就在（設定畫面「開發道場」頁之匯入與 CLI 之 `--import-prefs-json` 皆受影響）。
2. **`dump-userdef-metadata` 之歸屬**（§5.4）：其**落點**已定（於 `vChewingSharedCLI` 新增該動詞，事主 2026-09-24 核定「`vChewingSharedCLI` 是可改造對象」）；惟**應歸本 phase 抑或助手網頁 phase** 未定。本文建議**歸助手網頁 phase**——在助手存在之前它沒有消費者。若與本 phase 同批，則需連帶選定其輸出 schema 之凍結時點。
3. **助手之入口**（§1.4、§5.3）：使用者如何得知有「配置助手」？（官網推廣已依約束 3 暫緩。）本文建議**本次不做**、記為後續；若要，最小成本為輸入法選單加一項開網頁（**不引入 URL scheme**）。
4. **助手產物之形態**（§5.3）：單檔自足 HTML（本文立場）或多檔 ESM（附錄 B.3）。此項屬助手網頁 phase、不阻塞 P240，惟其結果會影響 §5.3 之目錄結構與 `Makefile`。

**另**：助手是否隨 app bundle 出貨（§5.3 末）——本文建議列為助手網頁 phase 之後續、本次不做。

---

## 附錄 A：未採用之方案——vChewing:// web scheme（存檔）

> **存檔說明**：本附錄完整保存 `vChewing://` 深層連結派送之設計。其獨有價值為「一鍵完成」與「可分享連結給他人」（未來自動化亦然）；若日後要復活此路線，本文各節之規格即為施工依據，惟須先確認 §0.3 之約束 1、2。**本設計不屬 P240 之施工範圍。**

### A.1 註冊

**唯一落點**：`Sources/vChewingIME_macOS/Resources/Info.plist`。該檔是**實體檔、非模板**，兩條建置路徑皆讀它——SPM 路徑經 `Plugins/BundleApps/plugin.swift:207-224` 之純字串替換（`$(…)`）後重新序列化；legacy 路徑 `Plugins/BundleAppsLegacy/plugin.swift:486-499` 讀同一檔。**新增一個字面 `CFBundleURLTypes` 陣列無須改動任何 substitution／additionalKeys。**

```xml
<key>CFBundleURLTypes</key>
<array>
  <dict>
    <key>CFBundleURLName</key>
    <string>org.atelierInmu.inputmethod.vChewing.prefs</string>
    <key>CFBundleTypeRole</key>
    <string>Viewer</string>
    <key>CFBundleURLSchemes</key>
    <array>
      <string>vchewing</string>
    </array>
  </dict>
</array>
```

**註冊之可見性**：採「僅靠既有之 `TISRegisterInputSource`（零改動）」；備援為於 `vChewing install` 之路徑補 `LSRegisterURL`（`Plugins/BundleApps/plugin.swift`），保底路線見 A.12。

**現況（實查，2026-09-24）**：

| 項目 | 結論 |
|---|---|
| IME `Info.plist` 之 `CFBundleURLTypes` | **不存在**（`Sources/vChewingIME_macOS/Resources/Info.plist`；實測 `Build/Products/Release/vChewing.app/Contents/Info.plist` 亦無） |
| 全工作區之 `CFBundleURLSchemes` | **只有一處**：`Sources/vChewingDebuggable/Resources/Info.plist:25-35`，scheme `vchewingdbg`；由該 App 以 SwiftUI `.onOpenURL` 處理（`vChewingDebuggableApp.swift:7-21` → `ContentView.swift:175-195`）。該 App 為 **Xcode-only、不隨發行版出貨**（`BuildPKG.sh` 從不複製它）⇒ **本附錄之 scheme 是全新增的攻擊面，防濫用須從零設計**（A.8） |
| `NSAppleEventManager` / `kAEGetURL` / `application(_:open:)` | **全工作區含 git 歷史零命中** |
| `LSRegisterURL` | **零命中** |
| 既有的「URL 驅動行為」 | `CandidateTextService`（`Sources/Shared/CandidateTextService.swift:38-59`）之 `@URL:`／`@WEB:` 候選字服務——**刻意只允許 `http`/`https`**，`file`/`mailto`/`data`/`javascript` 一律拒絕；此為「URL 之輸入須白名單」之既有先例 |

### A.2 派送與雙實例架構

事主原話：

> S2 的話，IME 會另外執行一份，但屆時的管線不走輸入法服務啟動的管線。我此前測試過唯音輸入法的其他 CLI 命令，均不影響唯音輸入法本體的運作。

⇒ **`open 'vchewing://…'` 會令系統另起一份 `vChewing` 執行檔**（而非把 Apple Event 轉送給已在執行的那份），且該第二份之管線**不走輸入法服務（IMKServer）之啟動路徑**。其後果有四：① Apple Event 之處理器必須存在於**第二實例**內，且該實例必須能在**未取得 IMKServer** 之情形下正常收工——而 `MainSputnik4IME.init()` 於 `handleIMKConnection()` 失敗時逕 `exit(1)`（`MainSputnik.swift:27-32`），**該處必須改**；② **跨行程之狀態共享不能只放記憶體**（in-memory nonce store 不成立）；③ 推式副作用（§2.3 之 13 條 `didSet`）**不可能**由第二實例觸發，需一則**跨行程訊號**（A.5）；④ 反之，**唯讀之即時刷新不受影響**：`@AppProperty` 之 getter 每次直讀 `UserDefaults`（§2.1），故第二實例寫入之值，正職 IME 於下一次讀取即見——**此跨行程可見性須實測確認**（A.11 之 S11）。

| | Case A：AE 抵達**既有** IME 行程 | Case B：另起**第二實例** |
|---|---|---|
| 判準 | `handleIMKConnection()` 成功（本行程即正職 IME） | `handleIMKConnection()` 失敗（該 Mach 名已被佔） |
| 現行行為 | 正常 | `exit(1)`（`MainSputnik.swift:27-32`）——URL 永無機會處理 |
| 規格要求 | 安裝 AE 處理器 → 就地處理 | 改為進入「URL 命令模式」，**不** `exit` |
| 角色 | 正職 IME，順帶處理深層連結 | **只**處理深層連結；**絕不**登錄為輸入源、**絕不**服務客體 |
| 收尾 | 不退出（續任正職） | 處理完畢即退出 |

**Case B 之「URL 命令模式」**：① `handleIMKConnection()` 回 `nil` 時不再 `exit(1)`，改標記 `isURLCommandMode = true` 並續行至 `NSApplicationMain`；② 於 `applicationWillFinishLaunching` 安裝同一套 AE 處理器；③ 處理該 URL（成功或失敗）→ 收尾（A.5 之和解訊號、A.7 之回饋）→ `NSApp.terminate`；④ **不**呼叫 `TISRegisterInputSource`、**不**建立 `IMKServer`、**不**註冊任何與正職 IME 同名之全域資源；⑤ **逾時自盡**：進入本模式後 30 s 內未收到任何命令即退出（避免異常情境留下無所事事之常駐行程）；⑥ `handleVarArgs()` 之語意不變，惟其「未辨識之 argv 亦回 `0` ⇒ `exit(0)`」之陷阱（§2.4 末）與本模式之交會須留意（A.11 之 S3）。

**AE 處理器之安裝（兩 Case 共用）**——於 `AppDelegate.applicationWillFinishLaunching`（`AppDelegate.swift:92`）之最前段：

```swift
NSAppleEventManager.shared().setEventHandler(
  self,
  andSelector: #selector(Self.handleGetURLEvent(_:withReplyEvent:)),
  forEventClass: AEEventClass(kInternetEventClass),
  andEventID: AEEventID(kAEGetURL)
)
```

**為何不用 `application(_:open:)`**：本檔同時服務 **legacy 發行版（部署地板 macOS 10.9）**——`Sources/vChewingIME_macOS` 為兩條路徑共用之原始碼，而 `application(_:open:)` 之 `[URL]` 多載需 10.13+。`NSAppleEventManager` ＋ `kAEGetURL` 自 10.9 起即存在，**單一碼路同時滿足兩側**，且不必為 delegate 方法加 `#available` 包裝。**時序**：`applicationWillFinishLaunching` 於 `finishLaunching` 內、首個事件出列之前執行，足以接住啟動前即已抵達之 Apple Event。**回覆事件**：`kAEGetURL` 之標準範式帶 `withReplyEvent`，處理後應回覆一則 Apple Event，以便 `open(1)` 之呼叫端得知成功／失敗（實作時照 Apple 官方範例為之；其對 LaunchServices 與各瀏覽器之必要性未在本 phase 斷言）。**多載與去重**：`setEventHandler` 於同一 (class, id) 對上為**取代**語意，AppKit 之內建處理器在此被取代，無衝突。

**何以仍保留 Case A**：① 成本近零——兩 Case 共用**同一個** AE 處理器與**同一個**處理函式，僅收尾方式不同；② 若日後系統行為改變（或使用者經 `open -a` 等路徑觸發），Case A 仍須正確；③ 「同一處理函式」正是兩條碼路不致各自漂移之保證。

### A.3 URL 語法（完整）

```text
scheme   vchewing
host     prefs
verbs    apply | revert | ping(dev)

apply   data=<percent-encoded minified JSON>  必要
        v=<int>                              選配（預設 1）
        nonce=<32 hex>                       選配；缺失 ⇒ 需 NSAlert 確認
revert  nonce=<32 hex>                       必要

範例（示意，載荷經截斷）：
vchewing://prefs/apply?v=1&data=%7B%22UseRearCursorMode%22%3Atrue%7D&nonce=9f2c…
```

- host ＝ `prefs`，path ＝ 動詞。**刻意限制為單一動詞族**（見 A.8 第 5 層）。
- `data`：**minified JSON** 經 percent-encoding；若改用 `URLComponents`，其對 `?` 之後的解析自然處理百分號編碼。
- `v`：schema 版本（整數）。**JSON 本體不得含版本鍵。**
- 全部鍵名為 `UserDef` rawValue，**不新增任何別名**——助手與 IME 之間以 `UserDef.swift` 為唯一契約。

**解析與拒絕規則（逐條）**：① scheme ≠ `vchewing` ⇒ 不處理（理論上不會送達）；② host ≠ `prefs` ⇒ 拒絕 ＋ 飄窗（「不支援的指令」）；③ path 非 `apply`／`revert`／`ping` ⇒ 拒絕 ＋ 飄窗；④ `data` 缺失或無法 percent-decode ⇒ 拒絕 ＋ 飄窗；⑤ decoded JSON 非 `[String: Any]` ⇒ 拒絕（`importFromJSON` 亦會回 `Invalid JSON format`，此處先擋以免白跑）；⑥ encoded `data` > 128 KiB ⇒ 拒絕（不 decode）；decoded > 64 KiB ⇒ 拒絕；⑦ 未知鍵／黑名單鍵／值域外 ⇒ 逐筆計入失敗（**非**整體拒絕），照既有 `ImportResult` 語意；⑧ 成功與失敗筆數皆為 0 ⇒ 視為無操作、**不發飄窗**；⑨ `ping` ⇒ 以飄窗回報版本與 scheme 版本（**僅供 spike；文檔不公開**）。

### A.4 傳輸編碼與長度

助手之產物**天然稀疏**——只輸出使用者答過的題，典型 15–30 鍵。估算：118 鍵之完整包 minified 約 5 KB、percent-encoding 後約 5.5 KB；稀疏包（25 鍵）minified 約 0.5–0.8 KB、encoded 後 < 1.5 KB ⇒ **無須壓縮即可滿足常見情境**。

1. 解碼後 JSON 之上限 **64 KiB**；encoded 之 `data` 參數上限 **128 KiB**。超限 ⇒ 拒絕並以飄窗回報（不靜默）。
2. **v1 不引入 deflate**。若日後確有超長包之需求，再以 `z=1`（deflate ＋ base64url）擴充——`Compression` 框架為 macOS 10.11+，legacy（10.9）側需另走 libz，故**此擴充會破 10.9 相容性**，須先裁定 legacy 是否支援深層連結。
3. **另有一條不在 v1 範圍之路線**：`vchewing://prefs/apply?url=https://…/preset.json` 由 IME 自行抓取（IME 已有 `network.client` entitlement）。可運送任意長度之包、適合「分享設定」場合，但引入**遠端內容**與**網路時序**兩個新變數，且遠端內容之風險需另行評估。**建議目前不做。**

### A.5 匯入後的和解（含跨行程訊號）

（一）**和解函式本身**：深層連結路徑在 `UserDef.importFromJSON` 之後呼叫 `reconcileAfterExternalPrefsImport()`（規格同 §4.4；落點建議 `Shared_DarwinImpl`，與 `PrefMgr_Utilities.swift` 同層）。

（二）**跨行程訊號**（因雙實例架構而必需）——Case B 之第二實例套用完偏好即退出，故 13 條 `didSet` 之推式副作用**只能由正職 IME 行程補做**。作法沿用本倉既有之 IPC 慣例（`DistributedNotificationCenter`；先例：`SecureEventInputSputnik.swift:176-247` 觀察螢幕鎖定、`CandidatePool4AppKit.swift:410-420` 觀察外觀變更）：

| 項目 | 規格 |
|---|---|
| 通知名 | `org.atelierInmu.inputmethod.vChewing.prefsImported`（暫定） |
| 發出者 | 第二實例（Case B），於套用成功之後 |
| 觀察者 | 正職 IME 行程（於啟動時註冊） |
| `userInfo` | 僅摘要（成功／失敗筆數、載荷雜湊之前 8 位）；**不放載荷本身**——觀察者不需要它，且可縮小事務與外洩面 |
| 觀察者動作 | `reconcileAfterExternalPrefsImport()` ＋ 發 A.7 之飄窗 |
| 無 IME 在跑時 | 無人接收；亦無妨——`@AppProperty` 之 getter 為即時讀取，下一次啟動 IME 自然取得新值 |
| 安全性 | 該通知名任何行程皆可發（與本倉既有之二則同）；但其唯一效果為「叫 IME 重讀偏好並跳一則提示」，**無破壞性**，故不另設防護 |

（三）**飄窗之歸屬**：Case A 由該行程自發飄窗（`Notifier` 即其常駐視窗）；**Case B 之第二實例不得自發飄窗**——它處理完即 `terminate`，而飄窗會隨行程消失，故須經上述通知請正職 IME 代發。**Case B 且無正職 IME 在跑**（冷啟情境）時無人可發，僅在「確有變更」時由第二實例彈一則簡短 `NSAlert`（模態、可停留至使用者確認），否則靜默退出。

### A.6 有序化（事主明示之要求）

事主原話：**「讓這些行為有序運行（而非在被 spam call 這種 web scheme 的時候同時做無用功）」**。

**設計**：新增 `@MainActor final class PrefsDeepLinkBroker`（落點建議 `Packages/vChewing_MainAssembly4Darwin/Sources/MainAssembly4Darwin/DeepLink/`）。全部狀態在主執行緒，與 `Notifier`（`@MainActor`）、`UserDefaults`、`PrefMgr`、`NSAlert` 之執行緒要求天然一致；**不需要** actor／佇列／鎖。

```text
idle ──enqueue(req)──▶ applying(req)
                         │
                         ├─ enqueue(req2) ──▶ pending = req2（覆寫；supersededCount += 1）
                         │
                         └─ 完成 ──▶ 若有 pending：等 minInterval（0.3s）後 ▶ applying(pending)
                                    否則 ▶ idle
```

| 護欄 | 規格 | 目的 |
|---|---|---|
| **單槽待辦（latest-wins 合併）** | 同時最多 1 筆「正在套用」＋ 1 筆「待辦」。新的請求覆寫待辦槽。**合併只作用於尚未開始者，永不重排已開始者** ⇒ 已受理之請求仍嚴格 FIFO | 斬斷「N 筆同時做無用功」 |
| **最小間隔** | 兩次套用之間 ≥ 0.3 s | 讓主執行緒喘息、避免飄窗洗版 |
| **相同載荷去重** | 對正規化後之 JSON 取雜湊；與**最近一次**已套用者相同且間隔 < 3 s ⇒ 丟棄並記數 | 網頁重複觸發、使用者連點 |
| **速率上限** | 10 s 內受理 > 8 筆 ⇒ 丟棄該批次其餘並以**一則**飄窗回報「過於頻繁，已忽略 N 筆」 | 敵意行程之風暴防護 |

**解析失敗之處置**：URL 無法解析、非 `prefs` host、`data` 缺失、超限、JSON 無效——**一律即時以飄窗回報，不進佇列**。僅「已通過解析與驗證者」才進佇列，故佇列本身不可能被垃圾撐爆。

**可測試性**：`Broker` 之核心（狀態機、去重、速率、合併計數）應為**純函式可測**：注入「時鐘」與「套用器」兩個閉包，即可在單元測試內以假時間驅動全部四道護欄，不必真的開視窗。此與本倉既有之測試風格一致（`UserDefaults.pendingUnitTests` 短路、注入式回呼）。

### A.7 飄窗（Notifier）與回饋

**套件**：`Packages/vChewing_NotifierUI`（`NotifierUI.swift` / `NotifierViewModel.swift`），以 `MainActor` 為預設隔離。**唯一入口**：`Notifier.notify(message: String)`（`NotifierUI.swift:70-72`）。**位置**：螢幕右上、可見區頂端下方約 100 pt、右緣內縮 20 pt（`NotifierViewModel.swift:152-161`，並有測試釘住 `NotifierViewModelTests.swift:60-62`）。**外觀**：無邊框透明 `NSWindow`（`level = max(CGShieldingWindowLevel(), kCGPopUpMenuWindowLevel)`、`.canJoinAllSpaces`、`.stationary`、`ignoresMouseEvents = true`），卡片為 `NSVisualEffectView`（`.underWindowBackground`）＋ 標題／副標雙行文字（17 pt bold ＋ 15 pt secondary）。**限制**：① 最多 3 張卡（`maxCardCount`）；② 同訊息 0.3 s 內去重（`dedupWindow`）；③ 顯示 1.3 s（`displayLifetime`）；④ **空字串（去換行後）直接丟棄**；⑤ `ignoresMouseEvents = true` ⇒ **不可能有按鈕或可點擊動作**，故「還原」必須走選單／設定畫面。**訊息慣例**：`"i18n:標題鍵".i18n + "\n" + "i18n:副標鍵".i18n`（既有呼叫點遍及 `IMEMenuSputnik.swift` 各熱鍵切換、`LXMgr_Core.swift:91-102`、`InputSession_HandleEvent.swift:52-56`）。**可達性**：`MainAssembly4Darwin` 以 `@_exported import NotifierUI`（`_ModuleReexport.swift:15`）轉出。

| 情境 | 標題（第 1 行） | 副標（第 2 行） |
|---|---|---|
| 成功 | `i18n:PrefsDeepLink.Notice` =「配置助手」 | `i18n:PrefsDeepLink.Applied:%d%d` =「已套用 %d 項、略過 %d 項」 |
| 部分失敗 | 同上 | 同上（略過 > 0 時，並於設定畫面之既有錯誤清單介面提供逐筆原因） |
| 全部失敗 | 「配置助手」 | `i18n:PrefsDeepLink.Rejected:%@` =「設定包未被接受：%@」 |
| 逾時／過頻 | 「配置助手」 | `i18n:PrefsDeepLink.Throttled:%d` =「請求過於頻繁，已忽略 %d 筆」 |
| 已回退 | 「配置助手」 | `i18n:PrefsDeepLink.Reverted` =「已還原上次套用的變更」 |
| 需確認（無 nonce） | — | 走 `NSAlert`，不發飄窗 |

**新增 i18n 鍵 × 4 語系**（`Sources/vChewingIME_macOS/Resources/{zh-Hant,zh-Hans,en,ja}.lproj/Localizable.strings`），並依既有慣例以 `LocalizableFileSorter` 維持排序。**發話者之區別**：上表之「成功／部分失敗／全部失敗／逾時·過頻／已回退」諸列，皆以「**由正職 IME 發出**」為前提（Case B 須經 A.5 之分散式通知請正職 IME 代發）；「需確認（無 nonce）」與「Case B 且無 IME 在跑」兩種情境，由**收訊之行程**以 `NSAlert` 直接面對使用者。**驗收準則**：訊息**永不為空**；兩行格式；**不得**設計成需要點擊的提示。

### A.8 防濫用（六層）

**威脅模型**：任一本地行程、任一網頁（含惡意廣告 iframe）、任一被誘導之使用者點擊，皆可 `open 'vchewing://prefs/apply?data=…'`。可造成的傷害**被沙盒與既有黑名單限縮**於「可交換的 112 條偏好」之內——不能指定檔案路徑（`kUserDataFolderSpecified`／`kCassettePath` 在黑名單）、不能改介面語言（`kAppleLanguages` 在黑名單）、不能載入辭典或執行外部指令。但仍可：把注音排列換掉、關掉安全相關提示、打開偵錯模式、把候選字字級改成 196、開啟浮動組字窗……即**騷擾級至中度的可用性破壞**，且可**持久**。

- **第 1 層（沿用，已存在）**：`UserDef` 之黑名單 ＋ 逐型別值域驗證 ＋ 未知鍵一律拒絕 ＋ 64 KiB 上限。**這是「設定包能表達什麼」的硬邊界**，已寫好、勿重造。
- **第 2 層（新增）：一次性 nonce 交握**。IME 端於**使用者主動發起**（選單「配置助手……」或設定畫面按鈕）時產生 128-bit 隨機 nonce，TTL 10 分鐘、**單次使用**（用後即焚；同 session 可再生成）；以 `NSWorkspace.shared.open` 開啟 `<主站>/assistant/#nonce=<hex>`，**置於 fragment 而非 query**（fragment 不會被送到伺服器，故不進主站之存取日誌）；助手於最終步驟把 nonce 原樣轉回 URL。**帶有效 nonce ⇒ 直接套用**；**無效或無 nonce ⇒ 退到第 3 層**。
  **★ 存放（記憶體不跨行程）**：nonce 由正職 IME 產生，而 URL 由另一行程（Case B）收到，故須改用**兩行程皆可讀取之儲存**——建議落於 `UserDefaults` 之一枚專用鍵（該鍵須列入 `jsonExchangeBlacklist`，以免被偏好 JSON 之匯入匯出帶走；兩行程之 bundle ID 相同，故 `UserDefaults.standard` 即同域）；另一路線為落於 IME 容器／App Support 內之一枚 `0600` 權限檔案（代價：須自行處理原子寫入與清理）。
  **效力之誠實界定**：nonce 一旦落於偏好或檔案，**同使用者之其他行程即可讀取**（沙盒容器與偏好域對同使用者皆為可讀）。故它自「行程內之秘密」降格為「**短時效、單次使用之會話憑證**」——仍足以阻擋盲呼與網頁順手牽羊（攻擊者須先讀到它，且受 10 分鐘窗與一次使用之限），**但不是密碼學意義上的 secret**。此點必須寫進程式註解與本段，不得含糊。**不要**提供「今後不再詢問」之永久豁免——那會把第 3 層一次性地廢掉；**受信任的路徑就是那顆按鈕本身**，而它是逐 session 生效的。
- **第 3 層（新增）：無 nonce 者一律經 `NSAlert` 確認**。顯示：標題「配置助手要求變更偏好設定」、內文「本設定包將變更 **N** 項設定」、**逐項之可讀摘要**（用 `UserDef.metaData.shortTitle` 與新舊值之標籤），按鈕「套用」／「取消」。照既有慣例：`setActivationPolicy(.accessory)` ＋ `activate(ignoringOtherApps: true)`、`runModal()`、`NSApp.popup()`、**已有 modal 則不重開**（`LXMgr_Core.swift:448`）、`UserDefaults.pendingUnitTests` 短路（以便測試）。⇒ **任何未經使用者於本機主動授權的變更，都不可能靜默發生。** 在「另起第二實例」之世界裡，該實例本身即可自擁一個 `NSApplication` 迴圈與模態視窗，故確認成本並未增加。
- **第 4 層（新增）：可還原**。**套用者通常是第二實例，而它套用完即退出** ⇒ 任何形式的「還原」都必須有跨行程之儲存（「僅在記憶體留存快照」不成立；選單項「還原上次套用」若要能還原第二實例所套用者，快照亦須在共用儲存內）。二選一：**甲（建議）**——快照落於 `UserDefaults` 之一枚專用鍵（同樣列入黑名單），單筆覆寫式，並明訂清除時機（「回退一次即清」及「IME 啟動時若發現已逾時〔建議 24 h〕則清」）；**乙**——放棄此層，改以使用者既有之 JSON 匯出備份作為還原手段（設定畫面「開發道場」頁已有匯出），並於助手之摘要頁提示「套用前請先匯出一份備份」。本文傾向甲：第 3 層仍是主要防線，而「一鍵可逆」是它被社交工程繞過時的補強；成本僅一枚偏好鍵。**無論甲或乙，皆不得於飄窗上加按鈕**（A.7 之限制⑤）。
- **第 5 層（紀律）：scheme 不得擴權**。動詞族**永久限定**為 `prefs/*`；**明確拒絕**未來把 `lexicon/import`、`dict/import`、`open-folder`、`shell` 等加進 scheme——`MainSputnik.swift` 的 CLI 已示範「一個命令通道能承載多少能力」，而 URL scheme 的觸發門檻比 CLI **低得多**（可由網頁觸發）。不新增任何 entitlements；**特別不得**加入 Apple Events 相關 entitlement（接收 `kAEGetURL` 不需要；加入只會擴大外送能力）。每次受理／拒絕皆以 `vCLog` 留痕（含來源與結果，**不含完整載荷**）。
- **第 6 層（選配，建議列為「不做」）**：以 Apple Event 之 `keySenderPIDAttr` / `keySenderAuditTokenAttr` ＋ `SecCodeCopyGuestWithAttributes` 驗證呼叫端簽章。**不建議實作**：URL 之送出者對「網頁點擊」而言是**瀏覽器**、對「終端機」而言是 shell／`open`，白名單在此毫無意義；而它會引入一個**本倉零先例**、且需長期維護的安全程式碼面。若日後確有需求，其正當用途是**日誌欄位**而非准入判斷。

> **存檔註記**：以「僅存於記憶體」為前提之 nonce 與還原快照設計不成立（跨行程）；若日後改為同行程派送，記憶體形態即恢復可行。

### A.9 邊界情況

| 情境 | 期望行為 | 備註 |
|---|---|---|
| IME 未執行時點擊 `vchewing://` | LaunchServices **另啟一份**（Case B）⇒ 該份進入「URL 命令模式」、處理完即退出 | 冷啟時 `applicationWillFinishLaunching` 內之辭典／磁帶載入為非同步——惟 Case B 不建 `IMKServer`、亦不需 `LXMgr` 就緒，故反較單純；**和解／回饋步驟仍須容忍兩者尚未就緒** |
| IME 已執行 | **仍會另起第二實例** ⇒ 由該第二實例套用，並經跨行程通知請正職 IME 補做推式副作用與發飄窗 | `IMKServer` 之全域 Mach 名衝突正是 Case B 之判準（`MainSputnik.swift:27-32`，**該處須改**） |
| 第二實例逾時（30 s 內無命令送達） | 逕行退出 | A.2 第 5 點；避免異常情境留下無所事事之常駐行程 |
| 同載荷連續兩次 | 第二次被去重丟棄 | A.6 |
| 載荷含未知鍵 | 該鍵計入失敗，其餘照常套用，飄窗回報「略過 N 項」 | 既有 `ImportResult` 語意 |
| 載荷含黑名單鍵 | 同上（reason = `Blacklisted key`） | 既有 |
| 載荷為 `{}` | 成功 0、失敗 0 ⇒ 視為無操作，**不發飄窗**（避免空訊息被 Notifier 丟棄而產生「按了沒反應」） | 須顯式處理，不可依賴 Notifier 之空字串過濾 |
| legacy 發行版（macOS 10.9） | 同碼路；`Compression`／deflate 路線排除，`application(_:open:)` 不使用 | A.2 |
| 使用者手動編輯 URL | 等同任意來源 ⇒ 若含 nonce 則直接套用、否則確認 | 合理 |

### A.10 落點清單

| 檔案 | 動作 |
|---|---|
| `Sources/vChewingIME_macOS/Resources/Info.plist` | 新增 `CFBundleURLTypes` |
| `Packages/vChewing_MainAssembly4Darwin/…/MainSputnik.swift` | `handleIMKConnection()` 失敗時**不再 `exit(1)`**，改標記並進入「URL 命令模式」，含 30 s 逾時自盡 |
| `Packages/vChewing_MainAssembly4Darwin/…/AppDelegate.swift` | 安裝 AE 處理器；新增 `handleGetURLEvent`；URL 命令模式之收尾（處理畢即 `terminate`） |
| `…/MainAssembly4Darwin/DeepLink/PrefsDeepLinkHandler.swift` | 新增（**兩 Case 共用之單一處理函式**；解析、驗證、套用、收尾） |
| `…/MainAssembly4Darwin/DeepLink/PrefsDeepLinkBroker.swift` | 新增（狀態機、去重、速率、日誌） |
| `…/MainAssembly4Darwin/DeepLink/PrefsDeepLinkTokenStore.swift` | 新增（**共用儲存**之 nonce：`UserDefaults` 專用鍵〔列黑名單〕或 `0600` 檔案 ＋ TTL ＋ 單次使用） |
| `…/MainAssembly4Darwin/DeepLink/PrefsImportedRelay.swift` | 新增：發／收跨行程 `DistributedNotificationCenter` 通知（A.5 第（二）點） |
| `Packages/vChewing_Shared_DarwinImpl/…/PrefMgr_Utilities.swift` | 新增 `reconcileAfterExternalPrefsImport()` |
| `Packages/vChewing_Shared_DarwinImpl/…/PrefMgr_Singleton.swift` | 若 A.8 第 4 層採甲案：新增還原快照之讀寫（`UserDefaults` 專用鍵） |
| `Packages/vChewing_MainAssembly4Darwin/…/IMEMenuSputnik.swift` | 新增「配置助手……」與「還原上次套用」兩項 |
| `Packages/vChewing_SettingsUI/…/SettingsUIHostWiring.swift` | 接線「以助手開啟」之主機動作（`openAssistant`） |
| `Sources/vChewingIME_macOS/Resources/*.lproj/Localizable.strings` | 新增 A.7 之 i18n 鍵 × 4 |
| `Plugins/BundleApps/plugin.swift`（**僅在 A.11 之 S1 確認發現未被索引、啟用備援時**） | 於 `vChewing install` 之路徑補 `LSRegisterURL` |

**測試**：`Broker` 之純邏輯單元測試（假時鐘）＋ `PrefsDeepLinkURL` 之解析／拒絕案例表 ＋ `reconcileAfterExternalPrefsImport()` 對 13 條 `didSet` 之觸發斷言。**助手側**：`deeplink.ts` 之 JSON → URL 正確性測試（percent-encoding、nonce 轉送、長度上限觸發）。

### A.11 待驗證項與風險（本附錄之專屬項）

| # | 問題 | 方法 |
|---|---|---|
| **S1** | `~/Library/Input Methods/` 之 IME bundle，其新宣告之 `CFBundleURLTypes` 是否被 LaunchServices 索引（本文按「會被索引」處理） | 實作後之**確認**：於本機建置版之 `Info.plist` 加 scheme，`TISRegisterInputSource` 後以 `lsregister -dump \| grep -i vchewing` 查；再 `open 'vchewing://prefs/ping'`。未索引 ⇒ 啟用 A.1 之備援或 A.12 之保底路線 |
| **S2** | `open` 會另起第二實例，且該實例之管線不走輸入法服務之啟動路徑；既有之其他 CLI 動詞均不影響正職 IME | 實作後之**確認**：`ps aux \| grep vChewing` 前後對照；觀察第二實例之 argv／`-psn`，及其 `IMKServer` 建立失敗後之去向 |
| **S3** | URL 冷啟時，LaunchServices 是否傳入會觸發 `handleVarArgs` 之 `exit(0)` 的 argv？ | 於 `handleVarArgs` 入口暫時 `print(CommandLine.arguments)` 後冷啟 |
| **S4** | `open` 與 Safari／Chrome／Firefox 對 `vchewing://` 之長度上限與手勢要求（是否需使用者點擊） | 以 1 KB／8 KB／64 KB 之 encoded 載荷實測（檢驗 64 KiB 上限是否過寬） |
| **S5** | 沙盒下接收 `kAEGetURL` 是否需要額外 entitlement？（`LSRegisterURL` 於沙盒下對自身 bundle 是否可用——**僅在 S1 之備援被啟用時才需要**） | 實測 |
| **S6** | 無 nonce 之 `NSAlert` 於 agent app（`LSUIElement`）下能否取得焦點並正確 `runModal()`？ | 照 `MainSputnik.swift:229-231` 之既有作法實測；**Case B 須一併測** |
| **S8** | `Notifier` 能否正確前置顯示——**Case A**（於 AE 回呼內呼叫）與 **Case B**（於分散式通知之回呼內、由正職 IME 發出）各測一次 | 實測 |
| **S11** | **第二實例寫入 `UserDefaults` 後，正職 IME 行程是否於下一次讀取即見新值？** | 第二實例以 CLI 寫一枚易觀察之鍵（如 `kCandidateListTextSize`），於正職 IME 內觀察其 `PrefMgr` 之讀值。**此為「唯讀即時刷新」之根本假設**；若不成立，則跨行程通知須改為「觸發**重新載入**」而非僅「補做推式副作用」 |
| **S12** | Case B 之第二實例：`NSApplicationMain` 於「未能取得 `IMKServer`」之情形下能否正常跑起事件迴圈並收到 AE？逾時自盡是否可靠？ | 實作後冷啟／熱啟各測一次 |
| **S13** | `DistributedNotificationCenter` 之觀察者於**正職 IME** 內是否確實收到**第二實例**所發之通知（沙盒下之跨行程分散式通知）？ | 實測 |

| # | 風險 | 等級 | 緩解 |
|---|---|---|---|
| R1 | IME 之 scheme 未被 LaunchServices 索引 ⇒ 派送假設不成立 | **低** | 保底路線仍在（A.12）；僅在 S1 發現未被索引時才啟用 |
| R2 | 深層連結成為新的攻擊面 | 中 | A.8 六層；其中「一律可見（飄窗）＋ 一鍵可逆（還原）」是骨幹 |
| R9 | **第二實例架構之旁效**：異常情境下留下無所事事之常駐行程；或該實例意外取得／佔用正職 IME 之資源 | 中 | A.2：不建 `IMKServer`、不登錄輸入源、**30 s 逾時自盡**；所有收工路徑（含錯誤路徑）皆須 `terminate` |
| R10 | **跨行程可見性之假設不成立**（S11）⇒ 使用者見「套用了卻沒反應」 | 中 | 先實測 S11；若不成立，則 A.5 之通知須承載「**重新載入**」語意，並以「下次輸入源重啟即生效」為保底語意 |

### A.12 保底路線（若 S1 為否）

URL 僅作「設定包之識別（指紋）」，實際傳輸改由 ① 官網頁面下載 `.json`、② 使用者拖入設定畫面（既有功能）或 ③ 以 `--import-prefs-json` 交給 CLI 完成。此路線**不需要任何 IME 改動**。

### A.13 助手側之對應出口

若啟用本附錄之路線，助手另加〔**直接套用**〕出口 → `vchewing://prefs/apply?data=…&nonce=…&v=1`，並以 minified percent-encoded 版本輸出（§5.1 第 4 點）；IME 側入口為選單「配置助手……」（帶 nonce 開啟）。**兩條套用路徑不應同時提供**，以免使用者被弄混。

### A.14 沙盒、簽章與 IPC（實查）

**（一）沙盒與簽章**

- **IME 受沙盒管轄**：`com.apple.security.app-sandbox` 為 `true`，但**不在** `Sources/vChewingIME_macOS/Resources/vChewing.entitlements` 內——它由三條路徑於簽章時注入：`Plugins/BundleApps/plugin.swift:309-313`、`Plugins/BundleAppsLegacy/plugin.swift:585-587`、`BuildPKG.sh:181-186`（後者附有明示警語：改用別組 entitlements 重簽會剝掉沙盒、破壞執行期行為）。
- **本機 ad-hoc 簽章另帶** `com.apple.security.cs.disable-library-validation`（僅在嵌入 dylib 時注入，且僅開發路徑；發行路徑以真 Team ID 重簽，無此放寬）。
- **發行簽章**：Developer ID，Team `WEY3MS268C`（`BuildPKG.sh:52-55`），hardened runtime ＋ 公證（`:334-341`）。

**（二）既有 IPC 面與呼叫端身分**

| 面 | 現況 |
|---|---|
| ① `IMKServer` | 全域 Mach 名 `org.atelierInmu.inputmethod.vChewing_Connection`（由 `mach-register.global-name` entitlement 白名單） |
| ② 對系統 `DistributedNotification` | **單向觀察**（螢幕鎖定、外觀變更）——不得作為信任邊界 |
| ③ 出向 `URLSession` | 僅更新檢查 |
| 其他 | **無 XPC、無 `CFMessagePort`、無 Distributed Objects、無 socket** |
| 呼叫端身分 | 既有的訊號只有一處：`SessionProtocol.swift:245-249` 讀 IMK 提供之 `clientProxy?.clientBundleIdentifier()`，用於行為微調與 `com.apple.SecurityAgent` 辨識——**非密碼學驗證** |
| 未認證命令面 | `MainSputnik.swift:69-164` 的 CLI（`--import-prefs-json`、`--import-kimo`、`--import-standalone-factory-lexicon`、`install`、`uninstall`）——**任何能 `exec` 該執行檔的行程皆可觸及**。沙盒限制的是它「能讀寫什麼」，不是「誰可以叫它」 |

> 上述三項是 A.8 之威脅模型與「第 3 層＝主要防線」判斷之事實基礎：本附錄所新增的 inbound 通道（URL scheme）之觸發門檻，比既有之 CLI 命令面更低（可由網頁觸發）。

---

## 附錄 B：已作廢之草案（存檔）

> **存檔說明**：本附錄保存經裁定停用、且已被取代之草案，供日後追溯與可能的復活。以下內容**不施工**。

### B.1 交換格式之 `$purpose` 單一字串方案

`__UserDefMeta` 辭典格式定案前之草案：以**一枚扁平字串鍵**承載「這套配置之總體目的」。事主原話：

> `$purpose` 這個乾脆改名為 `__UserDefMeta` 辭典格式好了，這個欄位宜直接用 NSJSONSerialization 解讀為一個 NSDictionary。

**作廢之範圍與理由**：上述單一扁平字串鍵與其姊妹構想 `$purposeID`（**封閉集之識別碼 ＋ IME 端本地化**）**俱作廢**。理由：① 單一扁平鍵無處安放「短名」與「總體目的」兩種語意，而 alert 之標題與訊息第一段各需其一（§3.2）；② 辭典格式之可擴充性已涵蓋日後同類需求——例如日後若要 IME 端本地化，再加一枚辭典成員即可，不必為此另設識別碼之封閉集；③ 扁平鍵散落於根層，與偏好鍵共用命名空間，遲早與真偏好鍵混淆。

### B.2 按鈕落點之開發道場草案

「自剪貼簿匯入配置資料」按鈕之落點**最初定於設定畫面「開發道場」頁**，其後改定為「偏好設定 → 一般設定」頁、「我姓ㄅ」按鈕之下方（§4.1）。作廢之理由：匯入配置是**面向全體使用者**的 OOBE 收尾動作，而開發道場是面向進階／診斷用途的頁面，兩者之客群不同。

### B.3 助手產物之多檔 ESM 甲案

零打包器路線：多檔 ESM ＋ `import "./x.js"` ＋ `moduleResolution: node16`，靠 `<script type="module">` 載入。**放棄原因**：`file://` 打不開（瀏覽器拒絕）、部署時要複製整個 `assets/` 樹、且失去「隨 app 出貨」之可能；代價是一個 `http.server` 依賴（僅開發期）。**保留之價值**：完全不引入 `esbuild` 相依。若日後決定不引入任何打包器，此案仍可行——代價如上（§5.3）。

### B.4 後設資料導出之獨立腳本備選

於 `vChewingSharedCLI` 新增 `dump-userdef-metadata` 動詞定案前之備選：另寫一支獨立 Swift 腳本導出後設資料。**作廢之理由**：需自行維護一支可執行靶，且與 CLI 動詞重複。（定案之規格見 §5.4。）

### B.5 隨派送方式定案而失效之待裁定項（一句話記載）

原列為「待事主裁定」之四項——**防濫用路線**（含「nonce 之存放位置」與「還原快照之存廢」兩支子項）、**scheme 之正名**（`vchewing` 小寫與 `vChewing://` 寫法之取捨）、**`~/Library/Input Methods/` 之註冊路線**、**legacy（macOS 10.9）是否支援深層連結**——其對象均屬 `vChewing://` web scheme；該派送方式定案為剪貼簿路線之後，四者連同其子項一併失效（設計保存於附錄 A，若日後復活則須重新裁定）。

---

## 附錄 C：證據索引（file:line）

**偏好體系與 JSON 交換**
- `Packages/vChewing_OSNeutral_LibVanguard/Sources/Shared/UserDef/UserDef.swift:9`（enum）、`:143`（DataType）、`:178`（MetaData）、`:214`（黑名單）、`:227`（`resetAll`）、`:242`（`exportAsJSON`）、`:258`（`importFromJSON`）、`:266-270`（未知鍵之失敗處置）、`:288`（`validateAndApply`）、`:368`（值域）
- `.../Sources/Shared/PrefMgr_Core.swift:9`（PrefMgr）、`:12-22`（注入回呼）、`:373-457`（13 條 didSet）、`:463-464`（`candidateKeys` 自我賦值之正規化）
- `.../Deps/VanguardSwiftExtension/Sources/SwiftExtension/SwiftFoundationImpl.swift:179`（`UserDefaults.current`）、`:195`（`@AppProperty`）
- `Packages/vChewing_SettingsUI/Sources/SettingsUI/SettingsUI/VwrSettingsPaneDevZone.swift:39-97`、`:42-53`、`:81-82`
- `Packages/vChewing_SettingsUI/Sources/SettingsUI/SettingsCocoa/VwrSettingsPaneCocoaDevZone.swift:110-205`、`:185-205`
- `Packages/vChewing_MainAssembly4Darwin/Sources/MainAssembly4Darwin/MainSputnik.swift:80-84`、`:155-157`、`:185-218`、`:204-218`
- `Packages/vChewing_MainAssembly4Darwin/.../SettingsUIHostWiring.swift:50`、`:52-63`
- `Packages/vChewing_Shared_DarwinImpl/Sources/Shared_DarwinImpl/PrefMgr_Singleton.swift:19-27`

**設定畫面、剪貼簿與按鈕落點**
- `Packages/vChewing_SettingsUI/.../SettingsUI/VwrSettingsPaneGeneral.swift:92`、`:103-175`、`:182-214`
- `Packages/vChewing_SettingsUI/.../SettingsCocoa/VwrSettingsPaneCocoaGeneral.swift:137-184`
- `Packages/vChewing_SettingsUI/.../SettingsUI/VwrSettingsPaneServices.swift:260-261`、`.../SettingsCocoa/VwrSettingsPaneCocoaServices.swift:233-234`（`NSPasteboard` 寫入先例）
- `Packages/vChewing_OSFrameworkImpl/.../AppKitImpl/AppKitImpl_Misc.swift:486-498`（`NSApp.popup()`）
- `Packages/vChewing_MainAssembly4Darwin/.../SessionController/InputSession_DarwinSurface.swift:100-118`（`showPreferences`）、`:150-160`、`:200-213`
- `Packages/vChewing_Shared_DarwinImpl/Sources/Shared_DarwinImpl/SwiftExtension/InputSession.swift:229,234`（`maxSegLength` 之重推）
- `Packages/vChewing_MainAssembly4Darwin/.../LXMgr_Core.swift:445-482`（「已有 modal 則不重開」之守衛，`:448`）

**IME 進程與生命週期**
- `Sources/vChewingIME_macOS/Modules/main.swift:10-14`
- `Packages/vChewing_MainAssembly4Darwin/.../MainSputnik.swift:12-34`（init）、`:57-65`（runNSApp）、`:69-127`（handleVarArgs）、`:229-231`、`:233-248`（確認對話框典範）、`:390-398`（IMKServer）
- `Packages/vChewing_MainAssembly4Darwin/.../AppDelegate.swift:30-34`、`:92`（willFinishLaunching）、`:162`（willTerminate）、`:184-196`（破壞性按鈕）、`:230-267`（自盡）
- `Sources/vChewingIME_macOS/Resources/Info.plist`（`LSUIElement`、`InputMethodConnectionName`）
- `Sources/vChewingIME_macOS/Modules/SecurityAgentHelper.swift:23-31`（60 s 週期計時器）

**飄窗（附錄 A 之用）**
- `Packages/vChewing_NotifierUI/Sources/NotifierUI/NotifierUI.swift:27`、`:31-59`、`:70-72`、`:266-329`
- `Packages/vChewing_NotifierUI/Sources/NotifierUI/NotifierViewModel.swift:61-83`、`:152-161`
- `Packages/vChewing_NotifierUI/Tests/NotifierUITests/NotifierViewModelTests.swift:60-62`
- `Packages/vChewing_MainAssembly4Darwin/.../SessionHostWiring.swift:37-38`、`:49`；`_ModuleReexport.swift:15`
- `Packages/vChewing_OSNeutral_LibVanguard/Sources/Shared/CandidatePool4AppKit.swift:135-139`、`:410-420`
- `Packages/vChewing_OSFrameworkImpl/.../CtlCandidateGSI4AppKit.swift:167-190`
- `Packages/vChewing_MainAssembly4Darwin/.../SecureEventInputSputnik.swift:176-247`

**安全、簽章與 IPC**
- `Sources/vChewingIME_macOS/Resources/vChewing.entitlements`
- `Plugins/BundleApps/plugin.swift:207-224`、`:309-321`、`:549-576`；`Plugins/BundleAppsLegacy/plugin.swift:486-499`、`:585-587`
- `BuildPKG.sh:52-55`、`:145-154`、`:181-186`、`:189-193`、`:334-341`
- `Packages/vChewing_OSNeutral_LibVanguard/Sources/Shared/CandidateTextService.swift:38-59`（URL 白名單先例）
- `Packages/vChewing_IMKUtils/Sources/IMKUtils/TISInputSourceExtension.swift:52`

**配置助手之知識來源（官網）**
- `onboarding/README.md`（分支骨架）
- `onboarding/onboarding_msnewphonetic.md:16-53`
- `onboarding/onboarding_array30.md:13-17`
- `onboarding/onboarding_asus.md:19-26`
- `onboarding/onboarding_kimo.md:99-128`、`:177`
- `onboarding/onboarding_hanin.md:38`
- `faq/basics.md:8-24`、`:70-87`、`:100-125`、`:166-186`
- `faq/troubleshooting.md`（8 類症狀）
- `manual/preferences.md`（12 頁逐項參考，465 行）
- `manual/toggles.md`（熱鍵一覽）

**本機實測**
- `node --version` → `v22.20.0`；`npm --version` → `11.15.0`
- `tsc --version` → `Version 7.0.2`（全域 `typescript`）
- `npm view esbuild version` → `0.28.2`（registry 可達）
- `tsc --project tsconfig.json`（ES2022／ESM／`rootDir` 顯式）→ emit 正常（enum 降級、`#private`、泛型箭頭函式）
- 同上但**省略 `rootDir`** → `error TS5011`，產物佈局變為 `dist/src/…`
- `grep -c '= "__'`（`UserDef.swift`）→ `0`

---

## 附錄 D：題庫草案（供助手網頁 phase）

> 鍵名為 `UserDef` 之 **case 名**（`k` 前綴）。★ ＝ 該題之答案對應既有文件處方（§2.7）。
> 本附錄為**草案**，最終題庫與推薦值須經事主裁定；**每題之預設選項一律為「維持不變」**（§5.5）。

**步驟草案（與 `manual/preferences.md` 之 12 頁分頁對位）**：

| # | 步驟 | 內容 | 分支 |
|---|---|---|---|
| 0 | 歡迎 | 一頁說明「這一趟會問您 8 組問題、約 3 分鐘；隨時可上一步；最後會給您一份設定包」。此頁先問**介面語言**（僅影響助手自身） | |
| 1 | **您用哪一款輸入法？** | 微軟新注音／雅虎奇摩／小麥注音／OpenVanilla／漢音／自然／華碩／行列三十／拼音（搜狗、紫光…）／全新使用者 | ⟂ **分支樞紐** |
| 2 | 您主要用哪種打字方式？ | 注音組句／逐字選字（ㄅ半）／漢語拼音／CIN 字根（行列、倉頡、嘸蝦米…）／其他 | ⟂ 決定後續是否出現拼音、SCPC、磁帶題組 |
| 3 | 打字節奏 | 聲韻並擊之取捨、免打聲調（拼音）、聲調鍵行為、Shift 相關鍵行為、Cmd+Opt+Ctrl+Enter 行為 | |
| 4 | 選字窗 | 字級、字型、橫向／縱向、單行與自動展開、選字鍵、顯示讀音／碼位、選字後游標位置 | |
| 5 | 中英混打 | 是否開混打回退；是否閂滯；槽序判定；左右 Shift 切換中英 | |
| 6 | 標點、數字與符號 | 半形標點、縱向標點硬化、羅馬數字、貨幣數字、符號輸入、數字小鍵盤 | |
| 7 | 辭典與智慧功能 | 康熙／JIS 轉換、全字庫 CNS、關聯詞語、片語置換、假名音節、倚天 DOS 排序、漸退記憶（急速遺忘）、狂拼 | |
| 8 | 通知與系統整合 | 飄窗提示（CapsLock／Eisu／Shift）、自動檢查更新、朗讀、音效、自動重載資料 | |
| 9 | 進階（可整頁跳過） | 安全強化組字區、Electron 客體、SecureEventInput 稽核、Debug 模式、熱鍵開關組、磁帶細節 | |
| 10 | 摘要與產生 | 差異預覽（逐鍵「目前 → 將改為」）＋ 出口（§5.2） | |

### D.1 步驟 1「您用哪一款輸入法？」（分支樞紐，本身不輸出任何鍵）

| 選項 | 觸發之題組 | 既有文件 |
|---|---|---|
| 微軟新注音 | D.4 ★、D.5 ★ | `onboarding_msnewphonetic.md` |
| 雅虎奇摩輸入法 | D.2、D.4、D.7 ★ | `onboarding_kimo.md`、`faq/basics.md:20-35` |
| 小麥注音 / OpenVanilla | D.2、D.4、D.7、D.10 | `onboarding_mcbpmf.md`、`onboarding_ov.md` |
| 漢音輸入法 | D.6 ★、D.9 ★ | `onboarding_hanin.md:38` |
| 自然輸入法 | D.4、D.5 | `onboarding_goingime.md` |
| 華碩／ASUS | D.5 ★、D.7 ★ | `onboarding_asus.md:22-26` |
| 行列三十 / 倉頡 / 嘸蝦米 | D.2（SCPC）、D.9（磁帶） | `onboarding_array30.md`、`faq/basics.md:182-186` |
| 搜狗／紫光／昇陽拼音 | D.2（拼音）、D.5（狂拼 ★） | `onboarding_pinyinsimp.md`、`faq/basics.md:116-125` |
| 全新使用者 | 不觸發 | — |

### D.2 步驟 2「主要打字方式」

| 選項 | 鍵 |
|---|---|
| 注音組句 | `kKeyboardParser4Zhuyin`、`kPinyinTypingEnabled = false` |
| 逐字選字（ㄅ半）★ | `kUseSCPCTypingMode = true`、`kUseSpaceToCommitHighlightedCandidate4SCPC`、`kCandidateKeys`、`kUseHorizontalCandidateList = false`、`kEnforceSingleLineCandidateWindowLayout4SCPC`、`kAssociatedPhrasesEnabled` |
| 漢語拼音 | `kPinyinTypingEnabled = true`、`kKeyboardParser4Pinyin` |
| 通用／國音二式／耶魯／韋氏 | `kKeyboardParser4Pinyin`（100…105） |
| CIN 字根 | `kCassetteEnabled`（**路徑鍵為黑名單，須使用者自行載入**） |

### D.3 步驟 3「打字節奏」

| 題 | 鍵 |
|---|---|
| 是否允許聲調前置 | `kAcceptLeadingIntonations` ★ |
| 聲調鍵之行為 | `kSpecifyIntonationKeyBehavior`（0…2）、`kSuppressTooltipForIntonationKeyOverrideEvents` |
| Shift+BkSp | `kSpecifyShiftBackSpaceKeyBehavior`（0…2） |
| Shift+Tab | `kSpecifyShiftTabKeyBehavior` |
| Shift+Space（選字窗／空組字區） | `kSpecifyShiftSpaceKeyBehavior4CandidateWindow`、`kSpecifyShiftSpaceKeyBehavior4EmptyState` |
| Cmd+Opt+Ctrl+Enter | `kSpecifyCmdOptCtrlEnterBehavior`（0…6） |
| 自動糾正讀音組合 | `kAutoCorrectReadingCombination` |
| Esc 清理 | `kEscToCleanInputBuffer` |

### D.4 步驟 4「選字窗」

| 題 | 鍵 |
|---|---|
| 字級 ★ | `kCandidateListTextSize`（12…196） |
| 字型 | `kCandidateTextFontName` |
| 橫向／縱向 ★ | `kUseHorizontalCandidateList` |
| 單行 | `kCandidateWindowShowOnlyOneLine` |
| 始終展開多行 ★ | `kAlwaysExpandCandidateWindow` |
| 選字鍵 ★ | `kCandidateKeys` |
| 游標置於詞語前／後方 ★ | `kUseRearCursorMode` |
| 顯示讀音／Unicode 碼位 | `kShowReverseLookupInCandidateUI`、`kShowCodePointInCandidateUI` |
| 選字後游標位置 | `kCursorPlacementAfterSelectingCandidate`（0…2） |
| 選字窗定位 | `kUseDynamicCandidateWindowOrigin` |
| 動畫 | `kEnableCandidateWindowAnimation` |

### D.5 步驟 5「中英混打」

| 題 | 鍵 |
|---|---|
| 啟用中英混合輸入回退 ★ | `kMixedAlphanumericalEnabled` |
| 英數閂滯狀態 ★ | `kEnableLatchedAlnumStateInMixedAlnumMode` |
| 依槽序鍵入判定讀音 ★ | `kMixedAlnumJudgeReadingsBySequentialRawKeyOrder` |
| 左／右 Shift 切換中英 | `kTogglingAlphanumericalModeWithLShift`、`…RShift` |
| 大寫字母鍵行為 | `kUpperCaseLetterKeyBehavior`（0…4） |
| 狂拼模式 ★ | `kFuriousTypingEnabled` |
| 共用英數模式狀態 | `kShareAlphanumericalModeStatusAcrossClients` |

### D.6 步驟 6「標點、數字與符號」

| 題 | 鍵 |
|---|---|
| 半形標點模式 | `kHalfWidthPunctuationEnabled` |
| 縱向標點硬化 | `kHardenVerticalPunctuations` |
| 大寫漢字數字格式 | `kRomanNumeralOutputFormat`（0…3） |
| 貨幣數字 | `kCurrencyNumeralsEnabled` |
| 符號輸入 | `kSymbolInputEnabled`、`kReplaceSymbolMenuNodeWithUserSuppliedData` |
| 數字小鍵盤 | `kNumPadCharInputBehavior`（0…2） |
| 漢音符號表熱鍵 ★ | `kClassicHaninKeyboardSymbolModeShortcutEnabled` |

### D.7 步驟 7「辭典與智慧功能」

| 題 | 鍵 |
|---|---|
| 康熙／JIS 轉換 | `kKanjiConversionPreferences`（0…2） |
| 全字庫 CNS | `kCNS11643Enabled`、`kFilterNonCNSReadingsForCHTInput` |
| 關聯詞語 | `kAssociatedPhrasesEnabled`、`kAlsoConfirmAssociatedCandidatesByEnter` |
| 片語置換 | `kPhraseReplacementEnabled` |
| 假名音節 ★ | `kSuppressFactoryUnigramsOfKanaSyllables` |
| 倚天 DOS 候選字排序 ★ | `kEnforceETenDOSCandidateSequence` |
| 急速遺忘模式 ★ | `kReducePOMLifetimeToNoMoreThan12Hours` |
| 允許單漢字升權 | `kAllowRescoringSingleKanjiCandidates` |
| 固定候選順序 | `kUseFixedCandidateOrderOnSelection` |
| 組字區 BPMFVS | `kReflectBPMFVSInCompositionBuffer` |

### D.8 步驟 8「通知與系統整合」

| 題 | 鍵 |
|---|---|
| 飄窗提示（CapsLock／Eisu／Shift）★ | `kShowNotificationsWhenTogglingCapsLock`、`…Eisu`、`…Shift` |
| 飄窗配色 | `kSpecifiedNotifyUIColorScheme`（0…2） |
| 自動檢查更新 | `kCheckUpdateAutomatically` |
| 朗讀 | `kReadingNarrationCoverage`（0…2）、`kCandidateNarrationToggleType` |
| 音效 | `kBeepSoundPreference`（0…2）、`kShouldNotFartInLieuOfBeep` |
| 自動重載資料 | `kShouldAutoReloadUserDataFiles`、`kPhraseEditorAutoReloadExternalModifications` |
| 切換輸入源時顯示模式說明 | `kShowModeDescriptionOnActivatingServer` |
| 客體調適（Electron／Steam 等）★ | `kAlwaysUsePCBWithElectronBasedClients`、`kClientsIMKTextInputIncapable`、`kDisableSegmentedThickUnderlineInMarkingModeForManagedClients` |

### D.9 步驟 9「進階（可整頁跳過）」

| 題 | 鍵 |
|---|---|
| 安全強化組字區 | `kSecurityHardenedCompositionBuffer` |
| SecureEventInput 稽核 | `kCheckAbusersOfSecureEventInputAPI` |
| Caps Lock 相關 | `kBypassNonAppleCapsLockHandling`、`kShiftEisuToggleOffTogetherWithCapsLock` |
| Electron 客體 | `kAlwaysUsePCBWithElectronBasedClients` |
| Debug 模式 | `kIsDebugModeEnabled` |
| 磁帶細節 | `kForceCassetteChineseConversion`（0…2）、`kAutoCompositeWithLongestPossibleCassetteKey` |
| 最大候選長度 | `kMaxCandidateLength` |
| 熱鍵開關組 | `kUsingHotKeySCPC`／`…Associates`／`…CNS`／`…KanjiConversionMode`／`…PinyinZhuyinTypingSwitch`／`…HalfWidthPunctuation`／`…CurrencyNumerals`／`…Cassette`／`…RevLookup`／`…InputMode`（共 10） |
| 其他 | `kUseShiftQuestionToCallServiceMenu`、`kConsolidateContextOnCandidateSelection`、`kKeepReadingUponCompositionError`、`kTrimUnfinishedReadingsOnCommit`、`kPreferredRevolverForceLevel`、`kCandidateStateJKHLBehavior`、`kFetchSuggestionsFromPerceptionOverrideModel`、`kFilterFactoryKanjisOfNonCurrentInputMode`、`kAlwaysShowTooltipTextsHorizontally`、`kShowTranslatedStrokesInCompositionBuffer`、`kShowHanyuPinyinInCompositionBuffer`、`kInlineDumpPinyinInLieuOfZhuyin`、`kReducePOMLifetimeToNoMoreThan12Hours` |

### D.10 助手**不應**觸及之鍵（與理由）

| 鍵 | 理由 |
|---|---|
| `kUserDataFolderSpecified` | 黑名單；需使用者於 GUI 親自選路徑（沙盒授權） |
| `kCassettePath` | 同上 |
| `kAppleLanguages` | 黑名單；由系統設定管轄 |
| `kFailureFlagForPOMObservation` | 黑名單；暫態旗標 |
| `kMostRecentInputMode` | 黑名單；暫態 |
| `kCandidateServiceMenuContents` | 黑名單；結構複雜且與客體相關 |
| `kDeltaOfCalendarYears` | 與系統日期之偏移；非使用者偏好 |
| `kRespectClientAccentColor`、`kMinCellWidthForHorizontalMatrix` | 屬視覺微調，價值低於認知成本；且後者為實驗性 |

---

## 附錄 E：定案沿革（一段）

本 phase 由事主於 2026-09-24 逐輪裁定收束為下列定案：**派送方式**定為「偏好設定 → 一般設定」頁、「我姓ㄅ」按鈕下方之剪貼簿匯入按鈕，機理照「我姓ㄅ」之兩段式 `ActiveAlert`（先前曾評估 `vChewing://` web scheme 之深層連結派送，其完整設計保存於附錄 A）；**功能名稱**定為 Configuration Assistant，中文全稱「配置助手」、簡稱「助手」，更名之理由為其舊英文名稱之兩岸歧義過重，連帶更名者為 `ValueAdd/WebConfigAssistant/`、部署子目錄與產物 `assistant/`／`assistant.html`、相關程式識別字 `openAssistant`；**交換格式之中介資料**定為單一根層辭典 `__UserDefMeta`，其早期之扁平字串草案保存於附錄 B.1；**按鈕落點**自設定畫面「開發道場」頁改定為「一般設定」頁，其草案保存於附錄 B.2；**後設資料導出之落點**定為於 `vChewingSharedCLI` 新增 `dump-userdef-metadata` 動詞，獨立腳本之備選保存於附錄 B.4；**助手產物之形態**定為單檔自足 HTML，多檔 ESM 之甲案保存於附錄 B.3；原屬 web scheme 之四項待裁定事項（防濫用路線、scheme 之正名、註冊路線、legacy 是否支援深層連結）隨派送方式定案而失效，記載於附錄 B.5；**P240 之範圍界線**則界定為不涉及 TypeScript 網頁工具之開發，助手網頁暨 `ValueAdd/WebConfigAssistant/` 屬另一 phase。
