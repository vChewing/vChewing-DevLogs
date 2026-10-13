# Phase 303 研究（Task 2）：雙拼方案編輯器（Dualpin Schema Editor）

> 狀態：研究稿（2026-10-13；**本檔係 P303 Task 2 之術前調查**，用以界定其手術範圍）。文中之「本 Phase」一律指 **P303 之 Task 2**。
> 裁定：事主業於 2026-10-13 17:04 逐項回覆（見 §0.1），本稿隨之定案；§1.2、§3.1、§3.3、§3.5、§3.7、§3.8 與 §4 皆已按裁定改寫。
> 施工時點：**2026-10-13 18:01**（事主指定）——於該時點之前，本稿為凍結之術前調查，不動任何原始碼。
> 施工結果（2026-10-13）：完工，`vChewing-macOS` `f5d80765`（P303 之單一提交；本 Task 之 13 檔／＋2,631 併入其中，合計 32 檔／＋3,707／−42）；`Shared_DarwinImplTests` 15／15（新增 5）、`SettingsUITests` 27／27（新增 8）；5.10 側兩架構皆 `Build complete!`。實際落地與本稿之差異凡五處：①附錄 B 之字串清單落地為四語系各 38 鍵（另補 `Status.{Saved,SaveFailed,Exported,ExportDumped,ExportFailed}` 五者；38 之末者為事主驗收後新增之 `Validation.Details`）；②序列化之 `$schema` 在草稿未自帶時補官網之 canonical URL；③5.10 側另生兩處可用性勘誤（`NSStackView` 之 arranged 系列係 10.11+、`NSTextField.placeholderString` 係 10.10+）；④事主目視驗收後就地重寫兩版界面之版面（鍵位格逐音節一行、指派列補標籤、校驗摘要與可組碼數分行、「進階」改顯式按鈕且明細入寬度填滿容器之 group box）；嗣後事主自行精修 SwiftUI 版之排版（區塊分隔線、控制項貼右、標籤欄依容器比例、鍵位格居中、指派區改 Grid 附「音節／按鍵」標頭），並逐項移植至 AppKit 版（另修 action row 貼左成疊；嗣後再修範本彈出鈕貼右與鍵位格真正居中——後者不倚賴 `NSStackView` 之 `.equalSpacing` 等分餘寬，改以兩側等寬空白視圖夾定），官網說明頁之截圖亦同步重生；⑤官網另立 `manual/dualpinSchemaEditor.md` 一篇專述編輯器、並自 `manual/preferences.md`〈頁面 9：鍵盤設定〉提點（`vChewing-Homepage.io` `5ce2eec`，3 檔／＋123；`techdocs/Dualpin_Schema.md` 依裁定不述編輯器）。記載見 `Reqs4LLM/Archive_P301-P400/Reqs_0301-0310.md` 之 P303 篇（Task 2）。
> **Amendment（2026-10-14，事主 m06762／m06779／m07059）**：10.9 實機之三項回報皆已就地修正並 fixup 併回同一提交（32 檔／＋3,707／−42，`f5d80765`；其上三筆提交之 hash 隨之更動——P304 `8ddaef69`、P305 `b485d9fb`、P306 `5464fcdf`）。①**匯入徑原係無條件 `NSOpenPanel()`**：10.9 上於輸入法自身呼叫它會令自身與客體應用無限停止響應（事主只能斷電重啟；實測與 `i18n:InfoMessage.TechnicalReasonNSOpenPanel` 所述一致），今比照 DevZone 之 JSON 匯入慣例——`guard #available(macOS 10.13, *)` 否則 `SettingsPanesCocoa.warnAboutComDlg32Inavailability()`，並改以 `NSFileDragRetrieverButton` 讓同一顆鈕可拽入 `.json`（10.12 與更早之唯一匯入途徑）。②**三顆動作鈕原係裸 `NSButton()`**：10.9 上未顯式宣告 `bezelStyle` 者呈方角（Windows 2000 式），今以 DSL 之 `NSButton(verbatim:target:action:)` 建構（該建構子顯式 `bezelStyle = .rounded`）。③**「校驗明細」之展開盒恆坍縮成一條線**：`boxed(title:)` 於**建立**盒時即以 `fittingSize` 定下高度下限，彼時明細尚未填入 ⇒ 之後填入者撐不開；今廢該盒與「進階」鈕，改以 `NSAlert` ＋ `beginSheetModal(at:)`，明細置於可捲動唯讀 `NSTextView`（440×210）之 accessory view；其內容寬另自 `NSScrollView.contentSize` 扣除捲動條寬度（overlay 捲動條不佔 `contentSize`，浮動時壓住右緣；而文字視圖一旦可橫向捲動，左緣即被裁），今只准縱向捲動、令文字換行——事主 m07059 之截圖。驗證：`make debugLegacy`（Swift 5.10／`x86_64-apple-macosx10.9`）`Done.`、雙 app 皆出；`make lintFormatUncommitted` 零殘留；提交 hook 掃 889 檔 `CRITICAL 0、WARN 0`。
> 前置：`Research/Phase301_Research_DualpinSupport.md`（引擎、schema 資料模型、E1–E9／W1–W8 之分級）、`Research/Phase303_Research_DualpinSettingsUI.md`（兩版設定界面之陳列與匯入）、`vChewing-macOS/AGENTS.md`／`CLAUDE.md`、`vChewing-LibVanguard/AGENTS.md`、官網倉之 `techdocs/Dualpin_Schema.md`（格式標準）。
> 產權界線：本 Phase 之產物**一律落於 `vChewing-macOS`**（界面、助手後設資料、四語系文案、測試）；**不得觸及** `Packages/vChewing_OSNeutral_LibVanguard`（`vChewing-LibVanguard` 之逐位元組鏡像）——凡涉校驗語義、schema 之資料模型與其編碼者，皆屬 P302 之工作面，本 Phase 只**消費**其公開面（唯一例外見附錄 A：若事主准許，序列化輔助擬落於 `Shared_DarwinImpl` 之既有 `DualpinSchemaStore`，該檔在 LibVanguard 側無鏡像）。

## 0. 起因與交辦

- 事主交辦（**逐字**，m02421）：「現在我請你做 P303-Task2 術前調查：利用我此前給你貼過的幾張 微軟拼音的 螢幕擷圖 思考一下 Dualpin Schema Editor 該怎麼設計。（一個寬度為 570px 的 NSView / SwiftUI View 鑲嵌在 「偏好設定 -> 鍵盤設定」的雙拼 Section 的底端。）」
- 事主此前交付之擷圖（2026-10-12，六張，業經複核）：**微軟拼音（Win11）內建之雙拼方案自訂畫面**，含「新增配置」對話框之各態（範本下拉展開、零子音模式下拉展開、零子音鍵下拉展開、音節下拉展開、按鍵下拉展開）；事主另附註「微軟拼音預設的方案都沒有這個特性」與「有關於微軟拼音原廠雙拼 schema『不支援 autochop』的證據」——**本設計因此不擬在編輯器內暴露 `autochopPolicy`**（見 §3.6）。
- 交辦之單一交付：**一個鑲嵌於「鍵盤設定 → 雙拼 Section」底端之方案編輯器**，寬度依該 Section 之可用寬。
- 本 phase 之 Task 1 遺留：Task 1 之交辦明白寫「雙拼方案的編輯器，現在暫時不急著實作，留待接下來其他 Phase 接手」——本 Phase 即其接手者。

### 0.1 事主裁定（2026-10-13）

- 事主（**逐字**）：「默認按照你的建議來。我給出的幾點要求：」
  1. 「實際 contentWidth 應根據容器大小來調整。」
  2. 「SettingsUI 與 SettingsCocoa 都得落實。」
  3. 「匯入匯出功能注意與超早期版本 macOS 的相容性（FileImporter / FileExporter 呼出即死）。」
  4. 「展開方式：始終展開。」
  5. 「允許另存內建副本。」
  6. 「善用 vChewingDebuggable target 生成 standalone app 專門測試 SettingsUI / SettingsCocoa。」
- 對本稿之效力：原 §5 之六項待裁定**全部結案**——渲染器範圍、範本清單、匯出、進階欄位皆照原建議；展開方式**由「就地展開、預設收合」改為「始終展開」**（上列要求 4）；並新增兩項原稿所無之要求：**匯入／匯出之超早期 macOS 相容性**（上列要求 3，已補入 §3.5）與**以 `vChewingDebuggable` 驗兩版界面之動線**（上列要求 6，已補入 §3.7／§3.8）。

## 1. 動工前盤點

### 1.1 落點：兩版渲染器皆須落

- SwiftUI 版：`Packages/vChewing_SettingsUI/Sources/SettingsUI/SettingsUI/VwrSettingsPaneKeyboard.swift`，`Form` 之**第三個 Section**（`:54-73`）——`Section(header: Text("i18n:Settings.SectionDualpinScheme".i18n))`，內含說明文字、`Button`（`i18n:Settings.DualpinScheme.Import`）、狀態文字 `dualpinSchemaStatusText`，並以 `.fileImporter` 接 `SettingsUIHost.shared.importDualpinSchema(_:)`。編輯器即接在該 `HStack` 之下。
- AppKit 版：`Packages/vChewing_SettingsUI/Sources/SettingsUI/SettingsCocoa/VwrSettingsPaneCocoaKeyboard.swift`（`:124-215`）——同一 Section 以 `NSStackView.buildSection(width:)` 疊出標籤、按鈕（`#selector(importDualpinSchema(_:))`）與狀態文字。編輯器即接在該區塊之末。
- 選用時機（實查）：`InputSession_DarwinSurface.showPreferences()`——`#if compiler(>=6.2)` 且 `#available(macOS 14, *)` 走 `CtlSettingsUI`（SwiftUI），否則走 `CtlSettingsCocoa`（AppKit，5.10 路徑亦然）。**兩版並存、並非其一為死碼**，故編輯器須兩版皆落（與 P303 之匯入區同一標準）。

### 1.2 寬度：570 係「中文／日文 UI 之實得內容寬」，不得寫死

- `SettingsPanesCocoa.windowWidth = 634 + (英文 UI ? 80 : 0)`；`contentWidth = windowWidth - 65` ⇒ **中文／日文 UI ＝ 569**、**英文 UI ＝ 649**；`innerContentWidth = contentWidth - 37` ⇒ 532／612。
- 故「570px」實即 `contentWidth`（569）之約數。編輯器**一律取容器實得寬**（SwiftUI 側不設 `frame(width:)` 之硬值、AppKit 側以 `contentWidth` 傳入），英文 UI 下不得留白或溢出。
- 參照：`CtlSettingsUI.formWidth = 614`（SwiftUI `Form` 之最小寬）、`contentMaxHeight = 650`。編輯器**始終展開**（事主裁定第 4 條），故其高度須與既有三節併存而不逼出縱向捲動之突兀跳動——高度預算與收斂手段見 §4 風險 2。

### 1.3 既有之「面板內編輯器」先例

- `Packages/vChewing_SettingsUI/Sources/SettingsUI/PhraseEditor/PhraseEditorUI.swift`（427 行，`VwrPhraseEditorUI`）＋ `PhraseEditorDelegate.swift`（31 行）：**SwiftUI 專屬**（整檔圈於 `#if compiler(>=6.2)`、`@available(macOS 14, *)`），以 delegate 與宿主（`SettingsUIHost.phraseEditorDelegateProvider`）通訊，**無 AppKit 對位**。
- 可借道者：delegate 注入之形（不由套件直接摸宿主型別）、`fileChangeIndicator` 之類的觀察機制。不可照搬者：其「無 AppKit 對位」——雙拼 Section 係兩版皆有之區塊，編輯器不得只在 SwiftUI 側存在。

### 1.4 資料面（本 Phase 只消費）

- 模型：`Arimitsu.DualpinParser`（`Packages/vChewing_OSNeutral_LibVanguard/Sources/LibVanguard/Arimitsu/DualpinParser.swift`）——`rawID`／`rawTitle`／`localizedTitle`／`initials: [String: Character]`（23 鍵）／`finals: [String: Character]`（35–36 鍵）／`nullOnset`／`keyInterception`／`autochopPolicy`／`overrides`／`aliases`／`acknowledgedUnreachable`；`alphabet` 係**推導值**（`derivedAlphabet`）、不可寫。
- 三種零聲母政策（`NullOnsetPolicy`）：`.fixedKey(Character)`／`.finalInitial`／`.finalInitialOrVerbatimDigraph`——**與微軟拼音之三選項一一對應**（見 §2）。
- 校驗：`DualpinParser.validate(inventory:conflictingRawIDs:)` → `DualpinValidationReport`（`errors`／`warnings`／`isUsable`）。分級：**E1**（碼含 alphabet 外之鍵）／**E2**（碼長非 2）／**E3**（無碼且未宣告，DIPE 除外）／**E4**（alphabet 含聲調鍵或不可列印字元）／**E5**（別名與既有碼相撞）／**E6**（`keyInterception` 之鍵不在 alphabet）／**E7**（`rawTitle` 空）／**E8**（`overrides` 之碼長非 2）／**E9**（`rawID` 空、非反向域名、或與現存方案相衝）；**W1**（已宣告之不可達詞幹）／**W2**（重碼）／**W3**（用到主機保留鍵而未列 `keyInterception`）／**W4**（ü 之 v 化正規化）／**W5**（兩表有鍵未被任何碼用到）／**W7**（`autochopPolicy` 非 `disabled`）／**W8**（`localizedTitle` 缺 `en`）。
- 匯入門檻：`Shared_DarwinImpl.DualpinSchemaStore.importSchema(from:)`——`isUsable` 為假即拒收並回傳 `[DualpinImportIssue]`（錯誤碼＋引擎說明）。編輯器之「儲存」須與同一門檻對齊。
- 儲存面之現狀：`DualpinParser.encode(to:)`（`:271-291`）以宣告序輸出，**不含 `$schema`**；官網七份 JSON 之首行 `$schema` 係先前以外部腳本注入。編輯器若原樣 `JSONEncoder().encode(parser)` 會**丟掉 `$schema`**——此為必須補上之一格（附錄 A）。
- 偏好鍵：`UserDef.kDualpinSchemaJSON`（JSON 原文，整份取代、不另存檔案）、`kKeyboardParser4Dualpin`、`kDualpinEnabledForPinyinTyping`；匯入後另呼 `reconcileAfterExternalPrefsImport()`。編輯器之「儲存」應走同一組 setter 與同一收尾。

### 1.5 不可借道之現成機制

1. **不得自建第二套校驗**——錯誤碼、嚴重度、說明文字一律由 `Arimitsu` 供給，界面只轉述（P303 已立此界）。
2. **不得裸寫 `UserDefaults`**——一律走 `PrefMgr` 之 setter（推式副作用與 `@AppProperty` 之觀測皆賴此）。
3. **不得讓 SwiftUI 裸露於 5.10 可編路徑**——`#if compiler(>=6.2)` 圈好，AppKit 側不得 `import SwiftUI`。
4. **不得改引擎之 `encode(to:)` 之行為**（屬 P302 之工作面）；序列化之補強只能加在消費側（附錄 A）。
5. **不得在 `vChewing_SettingsUI` 之外新增偏好鍵**以支撐編輯器自身之狀態（暫存草稿留於記憶體；跨視窗持久化不是本 Phase 之需求）。

## 2. 微軟拼音（Win11）編輯器之逐圖對照

| 擷圖 | 內容 | 可沿用 | 不宜照搬 |
| --- | --- | --- | --- |
| ① 新增配置（初始態） | 名稱（上限 32 字元）／範本（（無））／零子音模式（固定式零子音）／零子音（O）／按鍵自訂（音節 `-` → 按鍵 `-`）／預覽之三列鍵位格（每格上格留白、下格為該鍵字母）／註記「請確定所有的音節均對應有效按鍵」／`新增`、`取消` | 整題架構：**身分（名稱）→ 來源（範本）→ 零聲母（模式＋鍵）→ 按鍵自訂 → 鍵位預覽 → 動作** | 「下格＝該鍵字母」之初始值係微軟之佔位，於唯音會直接撞 E1（`q` 等非合法尾綴），故初始態**必須**自範本或空白表推得 |
| ② 範本下拉 | （無）／智慧型 ABC／自然代碼 | 「自內建方案拷貝一份再改」之動線 | 微軟之範本清單以自家內建為限；唯音應納入**內建兩案 ＋ 目前自訂 ＋ 七份已發表者**（後者即官網 `valueadd/dualpin-schema-files/`，見 §3.3） |
| ③ 零子音模式下拉 | 固定式零子音／母音第一個字元的按鍵／母音第一個字元的按鍵（2 個字元的母音是完整拼音） | **逐項對位唯音之 `NullOnsetPolicy` 三態**（文案可直接沿用此義） | — |
| ④ 零子音鍵下拉 | （無）／`;`／A／E／I／O／U／V | 「零聲母鍵係**一枚**鍵、且可由下拉擇之」 | 其選項**只列母音鍵**；唯音之 `.fixedKey` 應允許字母表內任一鍵（GB/T 用 `a`、微軟用 `o`），並即時報 W5／E1 |
| ⑤ 音節下拉 | `-`／`ch`／`sh`／`zh`／`ai`／`an`／`ang`／`ao`／`ei`／`en`／`eng`／`er`／`ia`…… | 「音節（聲母＋韻母）為一**封閉清單**、逐項擇鍵」 | 微軟將聲母與韻母併成**一條扁平清單**——唯音之 schema 本就分 `initials`／`finals` 兩表，宜分組呈現（§3.3） |
| ⑥ 按鍵下拉＋A 格 | 音節 `ch` → 按鍵清單（A／E／I／O／U／V）；預覽之 **A 格上格顯示 `ch`、下格顯示 `a`** | **一鍵兩槽**之視覺：上格＝該鍵所領之聲母、下格＝所領之尾綴（唯音之 `initials`／`finals` 可同鍵，如四通之 `a`＝`zh` ＋ `a`） | 其按鍵清單僅六鍵；唯音應就字母表（含 `;`）擇鍵，並在已被佔用之鍵上標示衝突 |

- ⑥ 之「一鍵兩槽」是**最重要之一格**：它讓「未滿碼／同鍵異類」之風險可視化。唯音之四通（27 鍵、`ing` 落 `;`）、拼音加加（26 鍵）等皆能在此格中一眼讀出。
- 微軟之註記「請確定所有的音節均對應有效按鍵」＝**把校驗丟給使用者**；唯音之引擎已有完整 E／W 分級，故本設計以**即時校驗報告**取代該註記（§3.4），這是相對微軟之主要增益。

## 3. 設計（提案）

### 3.1 版面（由上而下，**始終展開**，全部落在容器實得寬之內）

1. **定位**：編輯器**始終展開**（事主裁定第 4 條），直接落於雙拼 Section 之底端——說明文字與匯入列之下；**不設**展開／收合動作，亦不另開 sheet 或獨立視窗。
2. **身分**：名稱（`rawTitle`，上限 32 字元）＋ `rawID`（預設 `dualPin.User.<slug>`；可編輯、即時驗 E9 與反向域名形）。四語系標題（`localizedTitle`）置於「進階」內。
3. **來源**：範本下拉（（無）／內建兩案／目前自訂方案）；擇定後**即覆寫**兩表與零聲母政策（覆寫前確認）。內建兩案之擇定即**另存內建副本**（事主裁定第 5 條）——自動改發 `dualPin.User.<slug>` 之新 `rawID`，內建本體不受影響。
4. **零聲母**：模式下拉（三態，文案對位擷圖③）＋（`.fixedKey` 時）零聲母鍵下拉。
5. **鍵位預覽格**：三列（`QWERTYUIOP`／`ASDFGHJKL;`／`ZXCVBNM`），每格上格＝聲母、下格＝尾綴；空格以淺色 `—` 表示；未被任何碼用到之鍵加註 `W5` 樣式；用到主機保留鍵者加註 `W3` 樣式。
6. **按鍵自訂**：`音節 [下拉] → 按鍵 [下拉]`（對位擷圖⑤⑥）。音節清單**分兩組**：聲母（`initials` 之 23 項，含 `zh`／`ch`／`sh`）與尾綴（`finals` 之 35–36 項，含 `er`／`ai`／`ang`…）；按鍵清單為字母表（26 字母＋`;`）並標示該鍵已被誰佔用。設值後即時重繪鍵位格。
7. **校驗報告**：一行摘要（`可匯入`／`N 項錯誤`）＋可展開之清單（E 在前、W 在後，逐條列 `碼 說明`）。錯誤存在時，儲存鈕停用。
8. **動作列**：`儲存`（寫回偏好）／`匯出方案檔…`（匯出 JSON）／`還原`（回滾至本次載入時之草稿）。始終展開，故無「關閉」；亦無「新增」——未匯入時即以空白草稿起步（§3.3）。

### 3.2 草稿模型（提案）

- 新檔 `Packages/vChewing_SettingsUI/Sources/SettingsUI/DualpinEditor/DualpinSchemaDraft.swift`（**5.10 可編**，純 Foundation＋`Arimitsu`）：
  - `struct DualpinSchemaDraft`：`var rawID/rawTitle/localizedTitle/initials/finals/nullOnset/keyInterception/autochopPolicy/overrides/aliases/acknowledgedUnreachable`（與 `DualpinParser` 同形）＋ `func makeParser() -> DualpinParser`＋ `mutating func applyTemplate(_:)`＋ `func assign(syllable: String, to key: Character)`（自動判定該音節屬 `initials` 或 `finals`；同鍵之他類別不受影響）。
  - `func validate(conflictingRawIDs:) -> DualpinValidationReport`：轉呼引擎，**不自行判級**。
  - 兩表之「音節清單」由引擎之**公開常量**推得（`initials`／`finals` 之鍵即清單；新增方案時以內建兩案之鍵之聯集為底），避免界面自帶一份 426 詞幹之副本。
- 檢視層：SwiftUI `VwrDualpinSchemaEditor`（`#if compiler(>=6.2)`、`@available(macOS 14, *)`）與 AppKit `VwrDualpinSchemaEditorCocoa`（`NSStackView`／`NSPopUpButton`／`NSTextField`，沿用 `vChewing_OSFrameworkImpl` 之 Result Builder DSL），兩者共用上開草稿模型。

### 3.3 範本與初始態

- 空白（（無））：以內建兩案之鍵之聯集為兩表之骨架、`nullOnset = .fixedKey("o")`，並即時顯示 E3／W5 之體檢結果（引導使用者自範本起步）。
- 內建兩案（微軟雙拼、GB/T 34947-2017）：`DualpinParser.mspy`／`.gbt17` 直接拷貝；**注意 `rawID` 必須改名**（否則 E9），故「自內建起步」時自動生成 `dualPin.User.<slug>`。
- 已發表之七份：**不**內嵌進 App（徒增體積與漂移）；「範本」清單只列**內建兩案 ＋ 目前自訂**（照 §5 原建議定案），其餘經由既有之「匯入」動線取得後再編輯（匯入即成為「目前自訂」）。
- 「目前自訂」為範本時＝**複製一份另存新名**，原方案在儲存前不受影響。

### 3.4 校驗回饋之分級

- **E 級（阻擋儲存）**：逐條列出，錯誤碼沿用引擎（`E3 詞幹「eh」無法得碼，且未列於 acknowledgedUnreachable。` 之類）。其中 E3 之提示另註「`eh` 屬 DIPE，不列 E3，亦不得列入 `acknowledgedUnreachable`」以導正誤解。
- **W 級（不阻擋、可摺疊）**：W2 重碼逐條列出（此係合法、僅供檢視）；W5 未用鍵在鍵位格上直接標示；W3 保留鍵另提示「如需用到，請於進階內列入 `keyInterception`」；W7 於編輯器內僅以唯讀方式顯示 `autochopPolicy = disabled`。
- 摘要行另示「得碼 425／426（`eh` 屬 DIPE）」——與官網格式標準之敘述同源。

### 3.5 儲存、匯出與身分

- 儲存：`isUsable` 為真方准寫入；寫入序列化後之 JSON 原文至 `PrefMgr.shared.dualpinSchemaJSON`，並（與 `importSchema` 同一收尾）令 `keyboardParser4Dualpin = .ofDualpinCustom`、`dualpinEnabledForPinyinTyping = true`、`reconcileAfterExternalPrefsImport()`。
- 匯出：寫出同一份原文（檔名建議 `<rawTitle>.dualpin.json`）；匯出為**新增能力**（微軟無此項，唯音有格式標準，宜供流通）。
- **檔案對話框之相容性細則**（事主裁定第 3 條；此係唯音既有之全域約定，非本編輯器獨有）：
  - **macOS 10.13 之前（10.9–10.12）一律不開 `NSOpenPanel`／`NSSavePanel`**：舊系統之 ComDlg32 不可用，呼出面板會**死掉整個桌面**。既有範式（照抄即可，見 `VwrSettingsPaneCocoaDevZone.swift`）：匯出於 `#available(macOS 10.13, *)` 為假時改走 `exportPrefsAsJSONToFileDump(_:)`，把 JSON 傾印至 `~/Library/Application Support/fileDump/`（該私有方法起於 `:233`，註解逐字：「macOS 10.12 與更早版本（ComDlg32 不可用）的匯出替代方案。」「此段一律不使用 NSOpenPanel / NSSavePanel。」）；匯入於同條件下改彈 `SettingsPanesCocoa.warnAboutComDlg32Inavailability()`（`VwrSettingsCocoaPanes.swift:57-62`：title＝`i18n:ClientManager.DragTargetInstruction`、message＝`i18n:InfoMessage.TechnicalReasonNSOpenPanel`，經 `callAlert`）。
  - **編輯器比照辦理**（決議：與既有之匯出／匯入同款，不另立新制）：匯出在 `< 10.13` 走同一 `fileDump` 替代，並於狀態列示明所寫入之檔案路徑；匯入在 `< 10.13` 彈同款警告、不開面板。**`< 10.13` 之面板呼叫一律禁止**（不得因「編輯器係新功能」而破例）。
  - **10.13 及以上仍分兩層內容型別**：`if #unavailable(macOS 11) { panel.allowedFileTypes = ["json"] } else { panel.allowedContentTypes = [.json] }`（既有實例：`VwrSettingsPaneCocoaKeyboard.swift:166-177`、`VwrSettingsPaneCocoaDictionary.swift:236-247`、`VwrSettingsPaneCocoaCassette.swift:171-182`、`VwrSettingsPaneCocoaClients.swift:300-307`、`VwrSettingsPaneCocoaDevZone.swift:163-169`）；凡 macOS 10.10 以上始有之 AppKit API（如 `.secondaryLabelColor`）一律 `#available` 守衛，10.9 退回 `.gray` 之類。
  - 面板一律以 `beginSheetModal` 掛於設定視窗（不用 `runModal`，以免在 IMK 情境下搶焦點）；回呼中才讀 `url`。
  - **5.10（macOS 10.9）路徑不得出現 SwiftUI 之 `.fileImporter`／`.fileExporter`**——該二修飾符只存在於 macOS 14+ 之 SwiftUI 面，而本倉之 SwiftUI 面整檔圈於 `#if compiler(>=6.2)`；編輯器之 AppKit 版一律以 `NSOpenPanel`／`NSSavePanel` 為之。SwiftUI 版（macOS 14+）得用該二修飾符，惟其回呼與 AppKit 版**共用同一支** `SettingsUIHost` 動作（匯入）與同一支序列化（匯出），避免兩份真相。
  - 同款機制亦見於使用者辭典目錄之指定與磁帶檔案之指定（`VwrSettingsPaneCocoaDictionary.swift`、`VwrSettingsPaneCocoaCassette.swift`）——本條為全設定界面之共同約定，編輯器不得例外。
- 序列化（附錄 A）：新增 `DualpinSchemaStore.serialize(_ parser: DualpinParser) -> String?`——`$schema` 置首、其後依 `DualpinParser.CodingKeys` 之宣告序、`initials`／`finals` 之鍵排序、2 空格縮排、結尾換行；並保證 `$schema` 於解碼—再編碼之往返中不丟失。

### 3.6 不暴露之欄位與往返保真

- **不暴露**：`autochopPolicy`（事主之證據：微軟原廠方案亦不支援；唯音本版僅實作 `disabled`，他形載 W7）、`overrides`、`aliases`、`acknowledgedUnreachable`、`keyInterception`（前三者置於「進階」內以唯讀原文檢視；`keyInterception` 得以複選清單編輯，惟預設收合）。
- **往返保真**：草稿須原樣攜帶未被界面觸及之欄位（含 `$schema`）；儲存時不得因界面未顯示而刪除之。此點須以測試釘死（§3.8）。
- `normalizationApplied` 屬載入期之旗標，不入 JSON、亦不於界面呈現。

### 3.7 落點檔案清單（提案）

| 檔案 | 內容 |
| --- | --- |
| `SettingsUI/DualpinEditor/DualpinSchemaDraft.swift`（新） | 草稿模型、範本套用、驗證轉呼、音節清單推導 |
| `SettingsUI/SettingsUI/DualpinSchemaEditorUI.swift`（新，`#if compiler(>=6.2)`） | SwiftUI 版編輯器 |
| `SettingsUI/SettingsCocoa/DualpinSchemaEditorCocoa.swift`（新） | AppKit 版編輯器 |
| `SettingsUI/SettingsUI/VwrSettingsPaneKeyboard.swift` | 第三 Section 之末端接入（SwiftUI） |
| `SettingsUI/SettingsCocoa/VwrSettingsPaneCocoaKeyboard.swift` | 同上（AppKit） |
| `Shared_DarwinImpl/Dualpin/DualpinSchemaStore.swift` | `serialize(_:)`／`save(_:)`（附錄 A） |
| `Sources/vChewingIME_macOS/Resources/{en,ja,zh-Hans,zh-Hant}.lproj/Localizable.strings` | 新字串（附錄 B） |
| `Packages/vChewing_SettingsUI/Tests/SettingsUITests/`、`Shared_DarwinImplTests/` | 測試（§3.8） |

- **驗收動線**（事主裁定第 6 條）：以 `vChewingDebuggable`（Xcode scheme，`ENABLE_HARDENED_RUNTIME = NO`）建 standalone app 專測兩版設定界面——SwiftUI 版與 AppKit 版各開一輪，含匯入、另存內建副本、匯出、還原與校驗報告；不須安裝 IME 即可驗。

### 3.8 測試

- `Shared_DarwinImplTests`：`serialize` 之往返（含 `$schema` 之首行、鍵序、縮排）與 `save` 後之偏好鍵狀態；`isUsable` 為假時**不得**寫入。
- `SettingsUITests`：範本套用後兩表之鍵集合＝範本之鍵集合；`assign(syllable:to:)` 之同鍵兩槽互不干擾；E/W 之呈現級別（以 `ValidationReport` 造樁，不重跑引擎）。
- 迴歸：以一組已知草稿（四通、拼音加加之鍵位）走完「範本 → 改一鍵 → 驗證 → 匯出 → 重讀」，斷言與官網已發表之 JSON 逐欄相同。
- 相容性：AppKit 版之檔案對話框分支須能以靜態核對確認——10.13 之前之分支內**不得**出現任何面板 API 呼叫（僅 `fileDump` 傾印與警告），10.13–10.15 走 `allowedFileTypes`、11 以上走 `allowedContentTypes`。
- 界面驗收（人工，經 `vChewingDebuggable`）：兩版各驗「範本套用後鍵位格即時重繪」「E 級存在時儲存鈕停用」「英文 UI（649）與中文 UI（569）皆不擠壓」「10.9／10.12 路徑**完全不開面板**：匯出落 `~/Library/Application Support/fileDump/`、匯入彈 `warnAboutComDlg32Inavailability()` 之警告」。四語系文案須齊備（附錄 B）。

## 4. 風險與界線

1. **兩版渲染器之工作量**：編輯器之互動密度遠高於匯入區；AppKit 側無 SwiftUI 之宣告式便利，須以既有 Result Builder DSL 手組。此為本 Phase 之主要成本；**事主已裁定兩版皆落**（第 2 條），故無「只落一版」之退路。
2. **鍵位格之外觀與高度**：唯音無既有之「鍵位圖」視圖可借（實查 `SettingsUI`／`OSFrameworkImpl` 無此型別），須自繪；須在 569 與 649 兩寬下皆不出現擠壓。又編輯器**始終展開**（裁定第 4 條），高度控制只能靠**資訊密度**（鍵位格與按鍵自訂並排、校驗清單收於 DisclosureGroup）而非收合，故須與 `contentMaxHeight = 650` 併算。
3. **範圍蔓延**：一旦開放「自訂方案編輯」，勢必被期待能做「方案管理（多套並存、逐套命名）」。唯音現行模型**只存一套**（`UserDef.kDualpinSchemaJSON` 單筆）——本 Phase **不做**多套管理；若事主有意，應另立 Phase（涉及偏好鍵形狀之變更，屬 P302 工作面）。
4. **`rawID` 之可讀性**：自動生成之 `dualPin.User.<slug>` 對使用者不友善，惟其係方案之唯一身分（E9 之依據）；界面須說明其用途，並容許修改。
5. **與官網七份之關係**：編輯器**不**取代官網之發表（後者是已凍結之產物、附格式標準），僅為使用者自備方案之起點；兩者之 JSON 形狀須一致（§3.5）。

## 5. 裁定結果（2026-10-13）

| # | 待裁定之事 | 裁定 |
| --- | --- | --- |
| 1 | 渲染器範圍 | **兩版皆落**（`SettingsUI` 與 `SettingsCocoa`）；並加要求：`contentWidth` 依容器實得寬動態調整 |
| 2 | 範本清單 | 內建兩案 ＋ 目前自訂；**不**內嵌官網七份（其餘走匯入動線） |
| 3 | 匯出功能 | **納入**；匯入／匯出皆須顧及超早期 macOS 之相容性（SwiftUI 檔案對話框在舊系統呼出即死，見 §3.5） |
| 4 | 展開方式 | **始終展開**（原建議之「就地展開、預設收合」作廢） |
| 5 | 內建副本另存 | **允許**（內建本體不可覆寫；`rawID` 相衝即 E9） |
| 6 | 驗收動線 | 以 `vChewingDebuggable` 建 standalone app 專測兩版設定界面（§3.7、§3.8） |

- 其餘（`keyInterception` 開放編輯並預設收合、序列化落於 `Shared_DarwinImpl`、`autochopPolicy` 不暴露）皆照 §3 之原建議辦理。

## 附錄 A：對 `Shared_DarwinImpl` 之序列化要求

```swift
/// 將方案編為 JSON 原文（`$schema` 置首、鍵序依 `DualpinParser.CodingKeys` 之宣告序、2 空格縮排、結尾換行）。
/// 供編輯器之儲存與匯出使用；`DualpinParser.encode(to:)` 不含 `$schema`，故於此層補之。
public static func serialize(_ parser: DualpinParser) -> String?
/// 校驗通過後寫入偏好設定，並收取與 `importSchema` 同一組收尾
/// （`keyboardParser4Dualpin`、`dualpinEnabledForPinyinTyping`、`reconcileAfterExternalPrefsImport()`）。
public static func save(_ parser: DualpinParser) -> DualpinImportOutcome
```

- 兩者皆為 `vChewing-macOS` 側之加值，**不動 `Arimitsu`**；`vChewing-LibVanguard` 無此檔之鏡像，故不觸犯逐位元組同步之界。

## 附錄 B：i18n 新增字串（草案，四語系各一份）

- 區塊與動作：`Settings.DualpinEditor.SectionTitle`／`.Save`／`.Revert`／`.Export`／`.SaveAsBuiltinCopy`／`.Import`（始終展開，故無 `.Edit`／`.Create`／`.Close`）
- 身分：`.Name`／`.NamePlaceholder`／`.RawID`／`.RawIDHelp`
- 範本：`.Template`／`.Template.None`／`.Template.Builtin`／`.Template.Current`
- 零聲母：`.NullOnset.Mode`／`.NullOnset.FixedKey`／`.NullOnset.FinalInitial`／`.NullOnset.FinalInitialOrVerbatimDigraph`／`.NullOnset.Key`
- 按鍵自訂：`.Assignment.Syllable`／`.Assignment.Key`／`.Assignment.Initials`／`.Assignment.Finals`／`.Assignment.KeyTaken:%@`
- 鍵位格：`.Keyboard.Preview`／`.Keyboard.UnusedKey`／`.Keyboard.ReservedKey`
- 校驗：`.Validation.OK`／`.Validation.Errors:%d`／`.Validation.Summary:%@`／`.Validation.Advanced`／`.Validation.DIPENote`
- 草案落於動工時補齊四語系；`i18n:` 鍵名與本 phase 之 Task 1 同制。
