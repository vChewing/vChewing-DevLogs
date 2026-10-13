# Phase 303 研究：雙拼之 macOS 側設定界面（方案陳列與匯入）

> 狀態：規劃稿（2026-10-12；**本檔係 P301（研究）之產物**——P301 除 `Phase301_Research_DualpinSupport.md` 外另產出本檔，用以**界定 P303 之手術範圍**；其登錄落於 **P301 之 Reqs 篇（追記）、`DevReqsHistory.md` 之 P301 列（追記）與 `KnowledgeMemo4LLM.md` §12.6（P301 之條）**，P303 自身不另立「規劃」任務、逕依本檔動工）。文中之「本 Phase」一律指 **P303**（下述手術之執行者）、「本檔」則屬 P301；一切改動皆為規劃、**不落任何原始碼**。
> 前置：`Research/Phase301_Research_DualpinSupport.md`（P301 之研究稿：`Arimitsu`／`DualpinParser`／`KeyboardParser` 之值域、schema 之身分與持久化、P302 之施工序）、`vChewing-LibVanguard/AGENTS.md`、`vChewing-macOS/AGENTS.md`／`CLAUDE.md`。
> 產權界線：本 Phase 之產物**一律落於 `vChewing-macOS` 倉**、且**不得觸及** `Packages/vChewing_OSNeutral_LibVanguard`（`vChewing-LibVanguard` 之 byte-sync 鏡像）。凡偏好鍵、`KeyboardParser` 之值域、schema 之資料模型，皆屬 P302 之工作面；本 Phase 只**消費**其公開面。

## 0. 起因

- 事主交辦（**逐字**）：「暫時規劃 P303 的內容：負責 vChewing-macOS 倉庫內的、LibVanguard 以外的內容。『唯音輸入法偏好設定->鍵盤設定->拼音輸入種類』這一欄目的下拉選單底部以 Divider 分隔出一個新段落，陳列出原廠所有雙拼方案＋使用者自訂的雙拼方案。然後，『唯音輸入法偏好設定->鍵盤設定->拼音輸入種類』的頁面底部新增一個 Section 允許使用者匯入雙拼資料。至於雙拼方案的編輯器，現在暫時不急著實作，留待接下來其他 Phase 接手。」
- 交辦之三事（本 Phase 之全部需求）：
  1. 「拼音輸入種類」之下拉選單**底部**以 **Divider** 分隔出**新段落**，陳列**原廠所有雙拼方案 ＋ 使用者自訂之雙拼方案**。
  2. 該**頁面底部**新增 **Section**，允許使用者**匯入雙拼資料**。
  3. **方案編輯器不做**（留待後續 Phase）。
- 三 Phase 之分工（本 Phase 之座標）：

| Phase | 倉／範圍 | 交付 |
| --- | --- | --- |
| P301 | `vChewing-DevLogs`（研究） | 研究稿 806 行：`DualpinParser` 之資料模型、校驗（E1–E9／W1–W8）、內建兩方案之碼表、打字機側接線、P302 施工序；**＋本檔**（P303 之規劃稿 439 行） |
| P302 | `vChewing-LibVanguard`（引擎側；含 Tekkon 之獨立先行 commit） | `Arimitsu` 直屬 SubTarget、`DualpinParser`、`DualpinTypewriter`、`TypingMode.DualPin`、**偏好鍵**、`KeyboardParser` 之雙拼值域 |
| **P303（本 Phase）** | **`vChewing-macOS`、`Packages/vChewing_OSNeutral_LibVanguard` 以外** | 兩版設定界面之**陳列**與**匯入**（本文第 3 節）、對 P302 之介面要求（附錄 A） |

- 依賴方向：**P303 消費 P302 之公開面**（`KeyboardParser` 之雙拼項、偏好鍵、`DualpinParser` 之純值 API）。故 P302 之 LibVanguard 面**凍結在先**、P303 動工在後；P303 之規劃稿因此必須把「需要 P302 供給什麼」寫死（附錄 A），以免兩個 Phase 各自演化出兩份真相。
- 用語沿用 P301：雙拼＝**Dualpin**；原廠方案＝**內建**（微軟雙拼〔預設〕、GB/T 34947-2017）；使用者自備者＝**自訂方案**；其唯一身分＝`rawID`（DNS 名，如 `dualPin.Microsoft`）。

## 1. 動工前盤點

### 1.1 「拼音輸入種類」下拉之實作（SwiftUI）

- 檔案：`Packages/vChewing_SettingsUI/Sources/SettingsUI/SettingsUI/UserDefRenderableImpl.swift`。
- 該欄即 `UserDef.kKeyboardParser4Pinyin` 之**專用渲染分支**——`extension UserDefRenderable<Int>` 之 `render()`（`:301-355`）內的 **`:311-330`**：

```swift
311:             case .integer where options.isEmpty && [.kKeyboardParser4Pinyin, .kKeyboardParser4Zhuyin]
312:               .contains(def): // 鐵恨注拼引擎的佈局模式選項（注音/拼音各自列示其值域）。
313:               Picker(
314:                 LocalizedStringKey(metaData.shortTitle ?? ""),
315:                 selection: binding
316:               ) {
317:                 ForEach(
318:                   KeyboardParser.allCases.filter { parser in
319:                     switch def {
320:                     case .kKeyboardParser4Zhuyin: return parser.rawValue < 100
321:                     case .kKeyboardParser4Pinyin: return parser.rawValue >= 100
322:                     default: return true
323:                     }
324:                   },
325:                   id: \.self
326:                 ) { item in
327:                   if [7, 100].contains(item.rawValue) { Divider() }
328:                   Text(item.localizedMenuName).tag(item.rawValue)
329:                 }
330:               }
```

- 三項關鍵性質：
  - **值域之篩選以 `rawValue >= 100` 為判準**（`:321`）⇒ 凡落於拼音值域之新 parser 案**自動**進入本下拉，無須改動此處之 predicate。
  - **分隔線係「前置」**（`:327`）：命中者先插 `Divider()` 再放 `Text`；`:328` 之 `.tag` 只掛在 `Text` 上 ⇒ **分隔線不可被選取**。既有兩條分隔線＝`rawValue == 7`（注音族之「大千 26」之前）與 `rawValue == 100`（拼音族之首項之前）。
  - `ForEach` 之元素型別為 `KeyboardParser`（`id: \.self`）；`.tag(item.rawValue)` 之型別與 `selection: binding`（`Binding<Int>`）逐字一致。
- 同檔另有「Picker 內放 `Divider()`」之先例 **`:243-256`**（`case (.string, .kBasicKeyboardLayout)`，以 `nil` 元素代表分隔線）⇒ 該寫法於本倉**已被反覆採用**，非新發明。

### 1.2 同欄之 Cocoa 對位

- 檔案：`Packages/vChewing_Shared_DarwinImpl/Sources/Shared_DarwinImpl/UserDefImpl/UserDefRenderableCocoa.swift`。
- 選項之組裝在 `init(def:)` 之 `checkDef:`（**`:44-55`**）：

```swift
44:     case .kKeyboardParser4Pinyin, .kKeyboardParser4Zhuyin:
45:       KeyboardParser.allCases.forEach { currentParser in
48:         case .kKeyboardParser4Zhuyin where currentParser.rawValue >= 100: return
49:         case .kKeyboardParser4Pinyin where currentParser.rawValue < 100: return
52:         if [7, 100].contains(currentParser.rawValue) { intOptions.append(nil) }
53:         intOptions.append((currentParser.rawValue, currentParser.localizedMenuName))
54:       }
55:       self.optionsLocalized = intOptions
```

- `optionsLocalized: [(Int, String)?]`（`:89`）之 **`nil` 元素即分隔線佔位**；實際建置於 `renderFunctionControl()`（**`:220-273`**）：Int 身分走 `btnPopup.bind(.selectedTag, to: NSUserDefaultsController.shared, withKeyPath: "values.\(def.rawValue)")`（`:246-252`），`nil` ⇒ `dropMenu.addItem(.separator())`（`:255`；另一處 `:236` 同法）。
- ⇒ 兩版 renderer **皆非** LibVanguard 鏡像內之檔案（一在 `vChewing_SettingsUI`、一在 `vChewing_Shared_DarwinImpl`）；**選單選項之組裝權在 macOS 側**。
- Cocoa 另有 String 身分之路（`:100` 之 `optionsLocalizedAsIdentifiables: [(String, String)?]` ＋ `bind(.selectedObject, …)`），惟本 Phase **不動**該支線（§3.1 之否決理由）。

### 1.3 選擇值之儲存與 binding 全鏈（關鍵：不經 `PrefMgr`）

| # | 檔案:行號 | 事實 |
| --- | --- | --- |
| 1 | `.../SettingsUI/SettingsUI/UserDefRenderableImpl.swift:118-139` | `_UDAutoViewInt`：`@AppStorage(wrappedValue: def.intDefaultValue, def.rawValue) private var value: Int` |
| 2 | 同檔 `:132`（有 `onChange` 時為 `:130`） | `def.bind($value).render()` |
| 3 | `.../Shared_DarwinImpl/UserDefImpl/UserDefRenderable.swift:20-24,31,102-104` | `UserDefRenderable.binding: Binding<Value>` 之注入 |
| 4 | `.../Sources/Shared/UserDef/UserDef.swift:34-35` | `case kKeyboardParser4Pinyin = "KeyboardParser4Pinyin"`／`case kKeyboardParser4Zhuyin = "KeyboardParser4Zhuyin"` |

- ⇒ SwiftUI 側**直寫 `UserDefaults.current`**（鍵即 `rawValue` 字串），**不經** `PrefMgr`。
- `PrefMgr` 側以**同一批鍵**對位：`.../Sources/Shared/PrefMgr_Core.swift:92-96` 兩枚 `@AppProperty` 槽；`:375-386` 之 `public var keyboardParser: Int` 係**衍生相容存取器**（get 依 `pinyinTypingEnabled` 選槽；set 以 `newValue >= 100` ⇒ 寫拼音槽＋**開啟拼音**）；`:481-486` 以 `KeyboardParser(rawValue:) == nil` 把非法值矯回 `0`／`100`。
- 兩道既有守門之適用面：`UserDef.swift:564-569` 之 `validNumeralValueRange`（`.kKeyboardParser4Pinyin: 100...105`）**僅**於 JSON 匯入路徑（`validateIntRange`）生效；`:854-861` 該鍵之 metaData **不帶 `options`**（故落 §1.1 之專用分支）、`:204` 之 `MetaData.options: [Int: String]?` 係**靜態**對照（無法表達動態清單）。
- **設計含意**：本 Phase 之一切「選擇」皆應落在 `KeyboardParser4Pinyin` 這一枚 Int 上（詳 §3.1）；若另立 String 偏好以表示「選了哪個方案」，則**選中態與顯示態將分屬兩處**，兩版 renderer 皆須各自記得投影（此即 §3.1 否決替代方案之核心理由）。

### 1.4 鍵盤設定頁之兩版結構與落點

| 版本 | 檔案 | 結構（行號） | 新 Section 之落點 |
| --- | --- | --- | --- |
| SwiftUI | `.../SettingsUI/SettingsUI/VwrSettingsPaneKeyboard.swift`（106 行；全檔圈於 `#if compiler(>=6.2)` `:7`/`:106`） | `body: View` `:19-57`；`Form` `:20`；Section ① `:21-48`（QuickSetup 列 `:22-43`＋四個 `renderUI()` `:44-47`）；Section ② `:49-51`；`}.formStyled()` `:52` | **`:51` 之後、`:52` 之前** |
| Cocoa | `.../SettingsUI/SettingsCocoa/VwrSettingsPaneCocoaKeyboard.swift`（146 行） | `body: NSView?` `:27-117`；`NSStackView.build(.vertical, insets: .new(all: 14))` `:28`；區塊一（`.boxed()`）`:29-64`；區塊二標題 `:65-68`；區塊二（`.boxed()`）`:69-114`；尾端留白 `NSView().makeSimpleConstraint(.height, …)` `:115`；`@IBAction` `:119-135`；`#Preview` `:139-146` | **`:114` 之後、`:115` 之前** |
| 共同 | — | — | 新增之 Section 與既有區塊**同層**；Cocoa 之樣式為 `"i18n:…".i18n.makeNSLabel(fixWidth: contentWidth)` ＋ `NSStackView.buildSection(width: contentWidth) { … }?.boxed()` |

- 兩檔皆**不在** LibVanguard 鏡像內 ⇒ 屬本 Phase。

### 1.5 匯入之既有先例

- **SwiftUI `.fileImporter`**（4 處）：`VwrSettingsPaneClients.swift:58`、`VwrSettingsPaneDictionary.swift:89,164`、`VwrSettingsPaneCassette.swift:105-138`、`VwrSettingsPaneDevZone.swift:68`。最完整者為 Cassette（`:105-138`）：
  - `allowedContentTypes: [UTType(filenameExtension: "cin2")!, …]`、`allowsMultipleSelection: false`（`:107-112`）；
  - 成功：`SettingsUIHost.shared.resolveUserSpecifiedURL(selectedURL)` → `checkCassettePathValidity(url.path)` → 成功則 `loadCassetteData()` ＋ `BookmarkManager.shared.saveBookmark(for: url)` ＋ `importCassetteFileToCache(url)`（`:121-126`）；失敗則 `IMEApp.buzz()`（`:128`）；
  - 另見其 `.alert`（`:97-104`）與 `@State private var isShowingFileImporter`／`isShowingCassetteError`（`:143-146`）。
- **Cocoa `NSOpenPanel`**（5 處）：`VwrSettingsPaneCocoaDictionary.swift:236`（`beginSheetModal(at: CtlSettingsCocoa.shared?.window)`，`:250-257`）、同檔 `:342`、`VwrSettingsPaneCocoaCassette.swift:171`、`VwrSettingsPaneCocoaDevZone.swift:193`、`VwrSettingsPaneCocoaClients.swift:300`（`NSSavePanel` 見同 DevZone `:163`）。Cocoa 無 `.fileImporter`，其既有替代文案為 `i18n:InfoMessage.TechnicalReasonNSOpenPanel`（`VwrSettingsCocoaPanes.swift:59`）。
- **Cocoa 之「就地更新」先例**：`VwrSettingsPaneCocoaDictionary.swift:365`（`self?.pctUserDictionaryFolder.url = url`）——面板回呼後**直接改動受影響之控件**，而非重建整個 pane。本 Phase 之「匯入後刷新」即循此例（§3.3）。

### 1.6 宿主閉包（`SettingsUIHost`）與 wiring

- `Packages/vChewing_SettingsUI/Sources/SettingsUI/SettingsUIHost.swift`：`:36-76` 為閉包列；實例——`importCassetteFileToCache: (_ url: URL) -> ()`（`:44`）、`importYahooKeyKeyUserDictionary: (_ url: URL?) throws -> (totalFound: Int, importedCount: Int)`（`:46`）、`notify: (String) -> ()`（`:73`）。
- 實作之 wiring：`Packages/vChewing_MainAssembly4Darwin/Sources/MainAssembly4Darwin/SettingsUIHostWiring.swift:29`（`host.importCassetteFileToCache = { LXMgr.importCassetteFileToCache(from: $0) }`）、`:31-32`（`host.importYahooKeyKeyUserDictionary = { url in try LXMgr.importYahooKeyKeyUserDictionary(url: url) }`）。
- ⇒ 本 Phase 之匯入亦應為**一枚新閉包 ＋ 一處 wiring**（§3.5），其重活（讀檔、檢證、寫偏好）在 `MainAssembly4Darwin` 側完成；UI 只負責取檔、呈現結果。
- 套件依賴**已足**：`Packages/vChewing_SettingsUI/Package.swift:16-30` 與 `Packages/vChewing_Shared_DarwinImpl/Package.swift:16-26` 皆依 `.product(name: "Vanguard", package: "vChewing_OSNeutral_LibVanguard")`（SettingsUI 另依 `Jad_BookmarkManager`）⇒ `DualpinParser` 之公開 API 於 SettingsUI 內**直接可及**，無須另闢橋接。
- 測試目標：`Packages/vChewing_SettingsUI/Tests/SettingsUITests/`（現有 `CtlSettingsUITests.swift`：`:33-44` 測設定窗之開、關與 contentView 之釋放；另有 `AssistantContractTests.swift`、`PaneLayoutTests.swift`、`PrefsExchangeTests.swift`）。
- **外部寫入之推式副作用須自行補**（本 Phase 最易漏之機制）：`@AppProperty` 之 setter（`SwiftFoundationImpl.swift:234-260`）才會觸發之 `didSet`，於「直接寫 `UserDefaults`」時**一概不觸發**，而 IME 為長駐行程。故 `PrefMgr` 另供 `public func reconcileAfterExternalPrefsImport()`：`Packages/vChewing_Shared_DarwinImpl/Sources/Shared_DarwinImpl/PrefMgr_Utilities.swift:47-74`——①`fixOddPreferencesCore()`；②13 枚帶 `didSet` 之偏好逐一**自我賦值**；③`UserDefaults.current.synchronize()`；④註解明記另一項推式狀態 `inputHandler.assembler.maxSegLength` 須待下次啟用輸入源才生效。既有呼叫者：`PrefsExchange.swift:114-117`（`if !result.successes.isEmpty { PrefMgr.shared.reconcileAfterExternalPrefsImport() }`，`applyPrefsJSONFromData(_:)` 於 `:62-65`）。
- ⇒ 本 Phase 之匯入於寫偏好後**必須**呼叫之（或逕走 `PrefsExchange.applyPrefsJSONFromData(_:)` 之骨架）；若 P302 之新鍵自帶 `didSet`，尚須同步 `Packages/vChewing_Shared_DarwinImpl/Tests/Shared_DarwinImplTests/PrefMgrReconciliationTests.swift:36` 所記之鍵數（**附錄 A 之 A10**）。此檔在 macOS 側 package 內（非 LibVanguard 鏡像）⇒ 屬本 Phase 可動之範圍。

### 1.7 程序關係、沙箱與 bookmark

- **程序關係**：`Packages/vChewing_MainAssembly4Darwin` 同時被 `vChewing`（IME）與 `vChewingDebuggable` 兩個 app target 連結（`vChewing.xcodeproj/project.pbxproj:11,18,153,161,268,295,957-966`；app target 之 `productName` 見 `:270,297,319`）⇒ **設定窗於 IME 進程內呈現**（`CtlSettingsUI.show()` 之呼叫者為 `vChewingDebuggable/ContentView.swift:133` 與 `MainAssembly4Darwin/.../IMEMenuSputnik.swift:91`、`InputSession_DarwinSurface.swift:110`）。故設定界面所寫之 `UserDefaults` **即** IME 之所讀（同一進程、同一 bundle id），無跨進程同步問題。
- **沙箱**：`Sources/vChewingIME_macOS/Resources/vChewing.entitlements` **檔內**不含 `app-sandbox` 鍵，惟**應用程式確實是 sandboxed**——`Plugins/BundleApps/plugin.swift:308-331`（`assembleMainIMEApp`）於簽章前把「Xcode 建置設定所推導之三項 entitlement」疊加上去（`:313-317` `com.apple.security.app-sandbox: true`、`network.client: true`、`files.user-selected.read-write: true`；另 `:326-330` 於有內嵌 dylib 時補 `cs.disable-library-validation`），再交 `processEntitlements(source:bundleIdentifier:additionalEntitlements:)` 展開 `$(PRODUCT_BUNDLE_IDENTIFIER)`。發行路徑同：`BuildPKG.sh:158-193` 以 `sed` 展開 bundle id、`PlistBuddy` 補同一組三項後 `codesign`；其註解 `:171-176` 明言不補即「strips the app sandbox and breaks runtime behaviour」。⇒ **沙箱為實、`files.user-selected.read-write` 已具備**。`entitlements` 檔另有 `files.bookmarks.app-scope` 與 `temporary-exception.files.home-relative-path.read-write`（`…/Library/Preferences/$(PRODUCT_BUNDLE_IDENTIFIER).plist`、`…/Library/Mobile Documents/com~apple~CloudDocs/vChewing/`）。
- ⇒ 由此得**正面處置**：沙箱進程所選之 URL **携** security scope。SwiftUI 匯入端應比照 `VwrSettingsPaneDevZone.swift:75-81`（`guard url.startAccessingSecurityScopedResource() else { …AccessDenied }` ＋ `defer { url.stopAccessingSecurityScopedResource() }`）；惟 Cassette 之 `.fileImporter`（`VwrSettingsPaneCassette.swift:105-138`）與 Cocoa 之 `NSOpenPanel` 路徑（`VwrSettingsPaneCocoaDevZone.swift:208-227` 逕 `try? Data(contentsOf:)`）皆**未**做 start/stop ⇒ 兩者之先例不一致，本 Phase 以「UI 端 start/stop ＋ host 端 best-effort」為準（§3.4、§4.3）。
- 方案本體擬以**原文**存於偏好（P301 已定：`UserDefaults` 僅承載一筆 schema）⇒ 本 Phase **不**呼叫 `BookmarkManager.saveBookmark`（不必記住檔案位置以供日後重載；此即與 Cassette 之別）。

### 1.8 i18n 與後設資料之鏈路

- 文案本體：`Sources/vChewingIME_macOS/Resources/{en,ja,zh-Hans,zh-Hant}.lproj/Localizable.strings`（四份；鍵之形如 `"i18n:TypingMethod.HanyuPinyinNumeral"`，取樣見 `zh-Hant.lproj/Localizable.strings:132,336,344`）。
- 取值機制：`StringLiteralType.i18n` ＝ `NSLocalizedString(description, comment:)`（`Deps/VanguardSwiftExtension/Sources/SwiftExtension/SwiftFoundationImpl.swift:153-155`）——**無 bundle／table 參數** ⇒ 查表鍵即**含 `i18n:` 前綴之字面字串本身**，且一律自 `Bundle.main`（即 IME app）解析。
- ⇒ **鍵由引擎側宣告、文由 macOS 側供給**：P302 為新 parser 案寫 `localizedMenuName` 之鍵（如 `i18n:TypingMethod.DualpinMSPY`），P303 於四份 `.strings` 補上譯文。缺文則介面顯示鍵名本身（無崩潰），故兩個 Phase 之提交**互不阻塞編譯**。
- 後設資料：`ValueAdd/WebConfigAssistant/assets/userdef-metadata.json` 係 `vChewingSharedCLI dump-userdef-metadata` 之**導出物**（產生器 `Packages/vChewing_OSNeutral_LibVanguard/Sources/vChewingSharedCLI/VCSharedCLI_UserDefMetadata.swift`；`ValueAdd/WebConfigAssistant/Makefile:26-27,41,74`：`make metadata` 重新導出並逐位元組比對、`make metadata-update` 入庫、`make metadata-audit --strict` 稽核）⇒ P302 新增偏好鍵之後，macOS 側之此檔**必須**同步（否則 `make metadata` 比對失敗）。此為跨 Phase 之第一條硬鏈（§3.6）。
- **設定介面曝露面**（跨 Phase 之第二條硬鏈）：`ValueAdd/WebConfigAssistant/assets/settings-surface.json` 係 `tools/settings-surface.js` 之產物（`Makefile:89-93`：`make surface` 重寫入庫版、`make surface-check` 逐位元組比對、**`make audit` 內含 `surface-check`**）。該掃描器讀三處：①`SCAN_DIRS`＝`SettingsUI/SettingsUI` 與 `SettingsCocoa` 內之 `UserDef\.(k[A-Za-z0-9_]+)` 引用（現 112 鍵、掃 31 檔）；②`Packages/vChewing_OSNeutral_LibVanguard/Sources/Shared/Shared.swift` 之 `KeyboardParser` 宣告序（現 zhuyin 11 項／pinyin 6 項）；③**`UserDefRenderableImpl.swift` 之 `/if\s*\[([0-9,\s]+)\]\.contains\(item\.rawValue\)/`** 以取分隔線（`tools/settings-surface.js:78-86`；入庫現值 `dividerBefore: [7, 100]`）。⇒ §3.2 把 `[7, 100]` 改成 `[7, 100, 200]`，**同時**使此導出物漂移；P302（新增 parser 案）與 P303（改分隔線）**至少一方**須跑 `make surface` 並提交（§6.1、§6.2 之驗收）。檔首註記事主 2026-09-24 之立規：「只要不是 `SettingsUI`／`SettingsCocoa` 曝露給使用者的選項，就不要在配置助手裡面出現」，`tests/questions.test.js` 以「題庫 ⊆ 曝露面」守住。

### 1.9 現況空白（macOS 側之雙拼命中數）

- 全倉 `grep` `雙拼|双拼|Shuangpin|DoublePinyin|rawID` 僅 **1** 命中：`Packages/vChewing_OSNeutral_LibVanguard/Sources/LibVanguard/InputHandler/InputHandler_TypingMode.swift:15` 之註解（「雙拼…由磁帶承載」）。
- `KeyboardParser` 現有 17 案（注音 11：`0,1,4,5,8,6,7,3,2,9,10`；拼音 6：`100-105`）**無任何雙拼案**（`Packages/vChewing_OSNeutral_LibVanguard/Sources/Shared/Shared.swift:79-96`）。
- ⇒ 本 Phase 之界面改動**全為新增**，無既有雙拼 UI 可循；一切外觀與文案皆須新造。

## 2. 排除項

- **方案編輯器**（事主逐字：「現在暫時不急著實作，留待接下來其他 Phase 接手」）——本 Phase 不含「新增自訂方案之欄位」、「改鍵位」、「多筆方案之管理」。
- **LibVanguard 鏡像內之一切**（`Packages/vChewing_OSNeutral_LibVanguard`）：偏好鍵之註冊（`UserDef`／`PrefMgr`／`PrefMgrProtocol` 五處）、`KeyboardParser` 之新案、`DualpinParser` 之資料模型與校驗、打字機與分派——**皆屬 P302**。
- `vChewing-LibVanguard` 與其兩份 manifest（`Package.swift`、`Package@swift-5.10.swift`）、`Tests/LibVanguardTests/Arimitsu/`——P302。
- 磁帶（Cassette）模式之既有語意與其界面；SCPC；真並擊方案。
- `ValueAdd/WebConfigAssistant` 之**編輯器**（P301 已定「不急」）；惟其**兩份導出物**（`userdef-metadata.json`、`settings-surface.json`）之同步屬本 Phase（§1.8、§3.6）。
- 鏡照（`vChewing-macOS` 之 LibVanguard 鏡像、`TekkonWorkspace` 之三倉）——依 P268 之職責邊界，不由本 session 兼任。

## 3. 設計

### 3.1 方案之陳列＝`KeyboardParser` 值域之擴張（對 P302 之介面要求）

- **建議（本稿之立場）**：於拼音值域（`>= 100`）增列**每個方案一枚 case**：

| `KeyboardParser` 案 | `rawValue` | 顯示（`localizedMenuName` 之鍵，由 P302 宣告、P303 供文） | 語意 |
| --- | --- | --- | --- |
| `ofDualpinMSPY` | **200** | `i18n:TypingMethod.DualpinMSPY`（微軟雙拼） | 內建預設（P301 §3.8） |
| `ofDualpinGBT17` | **201** | `i18n:TypingMethod.DualpinGBT17`（GB/T 34947-2017 雙拼） | 第二內建（P301 §3.6） |
| `ofDualpinUserSupplied` | **202** | `i18n:TypingMethod.DualpinUserSupplied`（自訂雙拼方案） | 自備 schema（P301 §3.3 之 E9／持久化） |

- 理由（逐條）：
  1. **無須自訂 binding**：`Picker` 之 `selection` 直取 parser 之 `rawValue`；`@AppStorage` 所寫之槽即「選了哪個方案」，**選中態與顯示態同源**（§1.3）。
  2. **值域判準自動吸納**：`:321` 之 `parser.rawValue >= 100` 與 `KeyboardParser.isPinyin` 皆以 100 為界 ⇒ 新案**無須改 predicate** 即入拼音下拉；`PrefMgr_Core.swift:481-486` 之矯正邏輯亦自動涵蓋（`rawValue` 有效）。
  3. **與既有架構同構**：`KeyboardParser` 本即「一枚案＝一種輸入法方案」（既有 6 拼音 ＋ 11 注音），雙拼不過是「兩鍵定長之拼音變體」而**非**另一層模式；`MandarinParser` 於雙拼下恆為 `.ofHanyuPinyin`（P301 架構定調③）⇒ 值域上之鄰接亦反映引擎側之實情。
  4. **Cocoa 側零新機制**：Int 身分之 `bind(.selectedTag, …)` 已然可用（§1.2）。
  5. **持久化零新增語意**：原廠僅存「選了哪一枚」；自訂方案另存 JSON 原文（P301 已定之單筆策略）——UI 側不必知曉兩者之別。
- **否決之替代方案**（記其理由，免日後重議）：單一 `.ofDualpin` 模式項 ＋ 另一枚 String 偏好（存 `rawID`）＋「自訂 `Binding<Int>` 投影」。
  - 理由①：SwiftUI 可行而 Cocoa 不可行——Cocoa 之 popup 直接 `bind(.selectedTag, …)` 至 `NSUserDefaultsController`（`UserDefRenderableCocoa.swift:246-252`），**無投影之處**，須改寫 Cocoa renderer 之 binding（成本高、風險高）。
  - 理由②：投影使「選中態」（Int）與「顯示態」（String）分屬兩處，兩版 renderer 都得各自記得投影，易生不一致。
  - 理由③：字串身分之路本已存在（`:100` 之 `optionsLocalizedAsIdentifiables`），惟其用途為「以物件為身分之 popup」，與本欄之 Int 語意不符。
- **附帶要求（防兩份真相）**：`KeyboardParser` 須曝一枚**純值**存取器（如 `public var dualpinSchemaRawID: String?`），回 `"dualPin.Microsoft"`／`"dualPin.GBT17"`／`nil`（自訂案之 `rawID` 來自使用者資料）。⇒ macOS 側**永不硬編 `rawID` 字串**，內建方案之「案」與「schema 身分」之對應只存在一處（P302）。
- **後果（誠實記之）**：新增一枚原廠雙拼方案 ⇒ 須改 P302 之 `Shared.swift`（enum ＋ `localizedMenuName`）＋ P303 之四份 `.strings`。此與既有 6 拼音案之處理完全相同；本 Phase 接受此代價（不為一枚未定之未來方案預造泛用機制）。

### 3.2 段落與分隔線（兩版 renderer 之最小改動）

- SwiftUI（`UserDefRenderableImpl.swift:327`）：`if [7, 100].contains(item.rawValue) { Divider() }` → `if [7, 100, 200].contains(item.rawValue) { Divider() }`。
- Cocoa（`UserDefRenderableCocoa.swift:52`）：`if [7, 100].contains(currentParser.rawValue) { intOptions.append(nil) }` → 同增 `200`。
- 之所以「加一枚數值」即得「底部新段落」：分隔線為**前置**（§1.1）⇒ `200` 命中即於**第一枚雙拼案之前**插入分隔線，其後 201／202 依 `allCases` 之宣告序陳列（**故 P302 之宣告序必須為 200, 201, 202 連續**——此為附錄 A 之一條）。
- `ForEach` 之元素型別**不變**（仍為 `KeyboardParser`），`.tag` 仍為 Int ⇒ 不動 §1.1 之任何型別；此即 §3.1 建議之主要紅利。
- 新段落之**內容**（建議）：

```
漢語拼音+數字標調
國音二式+數字標調
耶魯拼音+數字標調
合羅拼音+數字標調
通用拼音+數字標調
韋氏拼音+數字標調
──────────────────────  ← 既有（rawValue 100 之前置分隔線）
微軟雙拼                    ← 200（新段落之首）
GB/T 34947-2017 雙拼        ← 201
自訂雙拼方案                ← 202（其標題另見 §3.3）
```

（注音側不受影響：`:320` 之 `rawValue < 100` 篩選已排除新案。）

### 3.3 自訂項之標題與其刷新

- `KeyboardParser.localizedMenuName`（`Sources/Shared/Shared.swift:100-123`）為**引擎側**之純函式，不可能知曉使用者自訂方案之標題 ⇒ `ofDualpinUserSupplied` 之 `localizedMenuName` 只作**通用退回文**（「自訂雙拼方案」）。
- **兩版 renderer 對該案覆寫標題**：
  - 有自訂方案時：顯示其 `localizedTitle`（P301 之五級 fallback，經 `title(forLocaleTag:)`）——**建議**顯示為「自訂：<標題>」或逕為「<標題>」（待裁定 §5.2）。
  - 無自訂方案時：退回通用鍵，或綴以「（尚未匯入）」。
- 資料來源必須是 **P302 之純值存取器**（如 `PrefMgr.shared.dualpinUserSchemaTitle(forLocaleTag:) -> String?` ＋ `dualpinUserSchemaRawID -> String?`），**不得**令 macOS 側自行解 JSON：①JSON 之解碼與校驗屬 `DualpinParser` 之職權；②`Locale` 等 Foundation 型別只應存在於 macOS 側，而**字串標籤**（如 `Locale.current.identifier`）由 macOS 側產生後傳入（P301 之 m00420 裁定）。此為附錄 A 之一條。
- **刷新之時機與機制**（兩版不同，此為本設計最易漏處）：
  - SwiftUI：標題之來源為 `UserDefaults` ⇒ 以 `@AppStorage(UserDef.kDualpinUserSchemaJSON.rawValue)` 令該行**可觀察**即自動重繪（置於一枚小型 `@ViewBuilder` 子視圖，僅該案使用之，免使所有 Int 類 UserDef 都多一次觀察）。
  - Cocoa：popup 之 `NSMenuItem` 只在 pane 載入時建置一次 ⇒ 匯入成功後**就地改動該項之 `title`**（循 `VwrSettingsPaneCocoaDictionary.swift:365` 之先例），**不**重建整個 pane。
- **尚未匯入時是否陳列 202**：
  - 建議**一律陳列**（理由：①清單形狀靜態 ⇒ Cocoa 側無須為「有無自訂方案」重建選單；②可發現性——使用者得由選單得知「此處可自備方案」）。
  - 惟「選中 202 而尚無 schema」時，引擎側之**生效閘**（P301 §3.5：schema 可用 ∧ …）會使之**不生效**（落入既有拼音路徑）⇒ 介面須以文案明示（「尚未匯入」），不得靜默。
  - 另一選項（條件陳列）之代價：Cocoa 側須於匯入後重建選單；SwiftUI 側須使清單可觀察。列為待裁定（§5.2）。

### 3.4 匯入 Section（兩版）

- **共同內容**（建議）：
  - Section 標題：`i18n:Settings.SectionDualpinScheme`（「雙拼輸入方案」）。
  - 說明文（一至二行）：雙拼方案之 JSON 匯入、匯入即**覆蓋**既有自訂方案、原廠方案無須匯入。
  - 匯入鈕：`i18n:Settings.DualpinScheme.Import`（「匯入方案（JSON）…」）。
  - 狀態列：`i18n:Settings.DualpinScheme.Status.None`（尚未匯入）／`…Status.Imported`（已匯入：%@）。
  - 失敗提示：`i18n:Settings.DualpinScheme.ImportFailure.Title` ＋ 由**錯誤碼**映射之說明（§3.4 之末）。
- **SwiftUI**（`VwrSettingsPaneKeyboard.swift`）：
  - 於 `:51` 之後、`:52` 之前新增 `Section(header: …) { … }`，內含說明 `Text(...).settingsDescription()`、`Button`、狀態 `Text`。
  - `@State private var isShowingDualpinImporter = false`、`@State private var dualpinImportFailure: String?`；`.fileImporter(isPresented:allowedContentTypes:[.json], allowsMultipleSelection:false) { … }`；`.alert(...)`（比照 `VwrSettingsPaneCassette.swift:97-138`）。
  - 成功：`SettingsUIHost.shared.importDualpinSchema(url)` → 依 outcome 更新狀態；失敗：`IMEApp.buzz()`（`IMEApp_DarwinImpl.swift:69`）＋ 設 `dualpinImportFailure`。
  - 註：`:52` 之 `.formStyled()`／`:53-56` 之 `.frame(...)`／`.alert` 之鏈皆掛在 `Form` 之外層，新增之 `Section` **不得**插到 `.formStyled()` 之後。
- **Cocoa**（`VwrSettingsPaneCocoaKeyboard.swift`）：
  - 於 `:114` 之後、`:115` 之前追加一組 `NSStackView.buildSection(width: contentWidth) { … }?.boxed()`（標題以 `makeNSLabel(fixWidth:)`），內含說明標籤、`NSButton`（`target`／`action` 指向該 pane 之新 `@IBAction`）、狀態標籤（**持有其參考**以便匯入後就地更新）。
  - `@IBAction func importDualpinSchemeAction(_ sender: NSButton)`：比照 `VwrSettingsPaneCocoaDictionary.swift:225-260` 建 `NSOpenPanel`（`allowedFileTypes`／`allowedContentTypes` 依 macOS 版本分流）、`beginSheetModal(at: CtlSettingsCocoa.shared?.window)`，成功取 `url` 後呼叫 `SettingsUIHost.shared.importDualpinSchema(url)`，依 outcome 更新狀態標籤／彈 `NSAlert`／`IMEApp.buzz()`。
  - UI 預設 AppKit（`vChewing-macOS/AGENTS.md`）⇒ Cocoa 版**不得**改用 SwiftUI；且新 AppKit API 須守 macOS 10.9 地板（`allowedContentTypes` 須 `#unavailable(macOS 11)` 分流，見同檔 `:244-249`）。
- **成功後之自動選用**：建議匯入成功即 `PrefMgr.shared.keyboardParser = KeyboardParser.ofDualpinUserSupplied.rawValue`（經**衍生存取器**，其 setter 會一併 `pinyinTypingEnabled = true`）。理由：匯入而無感是壞 UX。**須明示之副作用**：此舉會把輸入法切至**拼音模式**（若原為注音）。列為待裁定（§5.2）。
- **檔案之讀取**：由 host 閉包（MainAssembly 側）執行——`Data(contentsOf:)`／`String(contentsOf:encoding:)`，UTF-8；sandbox 為實（§1.7）⇒ security scope 於 **host 端**以 best-effort 處理（「記下是否曾啟動、只在曾啟動時停止」，循 `LXMgr_KimoDataParser.swift:85` 之寫法），**UI 端**（SwiftUI）則循 `VwrSettingsPaneDevZone.swift:75-81` 做 `guard startAccessingSecurityScopedResource()` ＋ `defer { …stop… }`；兩者皆冪等。Cocoa 之 `NSOpenPanel` 路徑受 `files.user-selected.read-write` 保障（既有先例 `VwrSettingsPaneCocoaDevZone.swift:208-227` 未做 start/stop 亦能讀，本 Phase 不盲從、以 host 端 best-effort 為準）。
- **寫偏好後之推式和解**（必做）：寫入自訂 schema 之偏好鍵後（以及設定 `keyboardParser` 之後），須呼叫 `PrefMgr.shared.reconcileAfterExternalPrefsImport()`——否則長駐 IME 行程不觸發帶 `didSet` 之偏好的推式同步（§1.6）；若 P302 之新鍵自帶 `didSet`，該函式之自我賦值清單與 `PrefMgrReconciliationTests.swift:36` 之鍵數亦須同步（A10）。
- **失敗之呈現**：P302 之校驗碼（P301 §3.3 之 **E1–E9**；W1–W8 為警告、不阻匯入）→ P303 以一張「碼 → 文案鍵」之對照表供文（附錄 B）。⇒ macOS 側**只做映射**，不含任何檢證邏輯；檢證之單一真相留在 `DualpinParser`。

### 3.5 宿主閉包之簽名與 wiring

- `SettingsUIHost.swift` 新增（置於 `:44-46` 之同群）：

```swift
public var importDualpinSchema: (_ url: URL) -> DualpinImportOutcome = { _ in .failure(.unreadable) }
```

- 結果型別（**macOS 側**宣告，如 `SettingsUI/SettingsUI/DualpinImportOutcome.swift`）：

```swift
public enum DualpinImportOutcome {
  case success(rawID: String, title: String)
  case failure(DualpinFailure)   // DualpinFailure ＝ 包住 P302 之校驗碼之純值型別
}
```

  - 之所以**不**直用 `throws`＋tuple（如 `importYahooKeyKeyUserDictionary`）：本匯入之失敗須携**可辨識之檢證碼**以映射文案；`throws` 會使 UI 端拿到 `Error` 而須再行分派。若 P302 之錯誤型別不可用（如其携 Foundation 型別），P303 則以一枚本地 enum **鏡射**其碼（附錄 A 明列此要求：碼須為**可窮舉比對之純值**）。
- `SettingsUIHostWiring.swift` 新增一處（置於 `:29-32` 之同群）：讀檔 → `DualpinParser` 之解碼／校驗入口 → 成功則寫偏好（自訂 JSON 原文；必要時設 `keyboardParser`）→ 回報 outcome。所有副作用（寫偏好、通知）皆在此，UI 不觸及 `PrefMgr`。
- **生效時機**：`PrefMgr` 之 `@AppProperty` 每次讀取皆走 `UserDefaults`（`SwiftFoundationImpl.swift:234-260`）⇒ 偏好變更**即時**為引擎所見；惟**直接寫 `UserDefaults`** 不觸發 `didSet` 之推式副作用 ⇒ 須再呼叫 `PrefMgr.shared.reconcileAfterExternalPrefsImport()`（§1.6、§3.4）。而 P302 若於 `Arimitsu` 內**快取**已解碼之 schema，則須另供一枚「重載」入口（附錄 A 之 A7）——本 Phase 之匯入流程**必須**能主動觸發之，否則使用者匯入後須重啟 IME 方能生效。

### 3.6 文案與後設資料

- 新 i18n 鍵（四語系）：見附錄 B。全部落於 `Sources/vChewingIME_macOS/Resources/{en,ja,zh-Hans,zh-Hant}.lproj/Localizable.strings`（**四份皆須補**；缺一則該語系顯示鍵名）。
- `ValueAdd/WebConfigAssistant/assets/userdef-metadata.json`：待 P302 落定偏好鍵後執行 `make metadata-update`（其導出物之內容由 `vChewingSharedCLI` 生成，**不得手改**）；`make metadata` 之逐位元組比對即本 Phase 之一條驗收。
- `ValueAdd/WebConfigAssistant/assets/settings-surface.json`：因 §3.2 之分隔線改動（併 P302 之 parser 新案）而漂移 ⇒ 執行 `make surface` 並提交；`make surface-check`（`make audit` 之一環）即驗收（§1.8）。
- 既有 UI 之文案風格參照：`i18n:UserDef.kCassettePath.description`（`VwrSettingsPaneCassette.swift:68`）之 `Text(...).settingsDescription()` 慣例。

### 3.7 方案編輯器（本 Phase 不做）

- 書面界定「本 Phase 所做之匯入」之語意：**以檔案內容整份取代**既有之自訂方案（單筆；P301 之單筆持久化）。故：
  - 編輯器、欄位級錯誤定位之可視化、「多筆自訂方案之管理」皆**不**在本 Phase。
  - 「移除自訂方案」是否納入本 Phase ⇒ 待裁定（§5.2）。若不納入，使用者仍可匯入另一份或以手動方式清空偏好鍵（記為界線，§5.1）。

## 4. 實證（本 Phase 所跑之查證）

### 4.1 唯讀勘查清單

- 全部查證皆為**唯讀**（`grep`／`sed`／`read`）；未修改任何檔案、未建置、未執行任何 macOS app。
- 已勘查之檔案（皆在 `vChewing-macOS` 倉）：§1.1–§1.8 各處所引之檔；另含 `Packages/vChewing_SettingsUI/Tests/SettingsUITests/{CtlSettingsUITests,AssistantContractTests,PaneLayoutTests,PrefsExchangeTests}.swift`、`Sources/vChewingIME_macOS/Resources/vChewing.entitlements`、`vChewing.xcodeproj/project.pbxproj`（target 連結關係）、`Plugins/BundleApps/plugin.swift`（entitlement 之建置期注入）、`BuildPKG.sh`（發行簽章）、`Packages/vChewing_SettingsUI/Sources/SettingsUI/PrefsExchange.swift`、`Packages/vChewing_Shared_DarwinImpl/Sources/Shared_DarwinImpl/PrefMgr_Utilities.swift`（推式和解）、`Packages/Jad_BookmarkManager/Sources/BookmarkManager/BookmarkManager.swift`、`ValueAdd/WebConfigAssistant/{Makefile,tools/settings-surface.js,assets/{userdef-metadata.json,settings-surface.json}}`、`Packages/vChewing_SettingsUI/Sources/SettingsUI/{SettingsUI/VwrSettingsPaneDevZone.swift,SettingsCocoa/VwrSettingsPaneCocoaDevZone.swift,SettingsUI/VwrSettingsPaneCassette.swift,SettingsCocoa/VwrSettingsPaneCocoaCassette.swift}`（匯入先例）。
- 引擎側（`Packages/vChewing_OSNeutral_LibVanguard`）僅作**值域與鍵名之核對**（`Shared.swift:79-123`、`UserDef.swift:34-35,204,564-569,668-669,854-861`、`PrefMgr_Core.swift:92-96,375-386,481-486`、`PrefMgrProtocol.swift:25-27`）——其正本在 `vChewing-LibVanguard`（P302 之工作面）。

### 4.2 SwiftUI `Picker` 之能力邊界（實查結論）

| 問題 | 結論 | 依據 |
| --- | --- | --- |
| `Picker` 內可否放 `Divider()`？ | **可**，本倉已有兩處 | `UserDefRenderableImpl.swift:327`、`:243-256` |
| 分隔線可否被選中？ | **不可**（`.tag` 只掛在 `Text` 上） | 同檔 `:327-328` |
| 可否混入「非 `KeyboardParser`」之動態項？ | 須換 `ForEach` 之統一元素型別（現為 `KeyboardParser`） | 同檔 `:317-326` |
| 可否對某項下 `String` tag？ | **不可**（tag 與 `Binding<Int>` 型別須逐字一致；否則該項不成候選、選中態不顯示） | 同檔 `:315,328` 與 `_UDAutoViewInt` `:118-139` |
| `selection` 之值不在 tag 集合時？ | 顯示為**無選中** | SwiftUI 之一般語意（**未實機驗證**，見 §4.4） |
| 有無 String 選項之先例？ | 有（`kBasicKeyboardLayout` 等） | 同檔 `:233-256` |

### 4.3 踩坑（逐條）

1. **`PrefMgr.keyboardParser` 不寫入即不翻模式**：SwiftUI 側之 `@AppStorage` 直寫 `KeyboardParser4Pinyin` 槽，**不**動 `pinyinTypingEnabled`；而 `PrefMgr.shared.keyboardParser` 之 getter 依該旗標選槽（`PrefMgr_Core.swift:375-386`）⇒ 若介面「只寫槽」，則引擎所見之方案可能仍為注音槽之值。**本 Phase 之處置**：凡由介面主動**切換方案**者（如匯入後自動選用），一律經 `PrefMgr.shared.keyboardParser` 之 setter（衍生存取器），不直寫槽。
2. **`validNumeralValueRange` 之值域（`100...105`）與新案（200–202）之張力**：該範圍僅於 JSON 匯入路徑生效（`UserDef.swift:564-569`、`validateIntRange`）⇒ 若使用者以 JSON 匯入偏好且携 `keyboardParser = 200`，將被 `validateIntRange` 擋下。**本 Phase 之處置**：列為對 P302 之一條要求（值域須隨新案擴張），並於 §5.1 記為界線（本 Phase 不修該檔）。
3. **security-scope 之兩派先例**：IME 為**沙箱**進程（§1.7：entitlement 由 `plugin.swift`／`BuildPKG.sh` 於建置期注入），故 `VwrSettingsPaneDevZone.swift:76` 之 `guard url.startAccessingSecurityScopedResource()` 於本倉**不是**恆假；惟 Cassette 之 `.fileImporter`（`VwrSettingsPaneCassette.swift:105-138`）與 Cocoa 之 `NSOpenPanel` 路徑（`VwrSettingsPaneCocoaDevZone.swift:208-227`）皆**未**做 start/stop。本 Phase 之準則：UI 端做 start/stop、host 端再以 best-effort 包一層（兩者冪等），**不得**因某一先例缺失而省略（§1.7、§3.4）。
4. **`Cocoa` 之子控件須自持參考**：Cocoa pane 非宣告式，狀態標籤與自訂項之 `NSMenuItem` 於匯入後須**就地更新** ⇒ 建置時即須持有其參考（`pctUserDictionaryFolder` 之先例，`VwrSettingsPaneCocoaDictionary.swift:365`）。
5. **`.formStyled()` 之位置**：SwiftUI 之新 `Section` 須落於 `Form` 之 closure 內（`:51` 與 `:52` 之間）；插到 `.formStyled()` 之後雖可編譯卻不成 `Form` 之 section（外觀失序）。
6. **「以字串偏好承載整包 JSON」為本倉首例**：現有 123 枚 `UserDef` 中，`.string` 型者皆為路徑／字型名／按鍵串（`kCassettePath`、`kCandidateTextFontName`、`kCandidateKeys` 等）；結構化者僅 `.arrayOfStrings`（`kCandidateServiceMenuContents`）與 `.dictionary`（`kClientsIMKTextInputIncapable`）兩型，且此二者**皆在匯出／匯入黑名單內**（`UserDef.swift:248-255`）。⇒ A4 之鍵於值域、匯出、配置助手之呈現（textarea？）三處皆屬新境，須與 P302 議定其 `exchangeBlacklisted` 歸屬（A11、§5.2）。
7. **兩條導出物之漂移**：本 Phase 之改動會同時觸動兩個入庫產物——`assets/userdef-metadata.json`（因 P302 新增偏好鍵）與 `assets/settings-surface.json`（因 §3.2 之分隔線與 P302 之 parser 新案）；`make audit` 內含 `metadata`／`metadata-audit`／`surface-check` ⇒ 未同步即總檢紅（§1.8、§3.6）。

### 4.4 未實機驗證之事項（明示）

- `Picker` 內 `Divider()` 於 macOS 之**實際外觀**（本倉既有寫法，惟本 Phase 未截圖核對）。
- Cocoa `NSMenu` 之 `.separator()` 於 `NSPopUpButton` 內之外觀（同上）。
- `startAccessingSecurityScopedResource()` 於沙箱 IME 進程內對 `.fileImporter` URL 之回值是否為真（§1.7 已證沙箱為實，故合理預期為真，惟本 Phase 未實機驗證）。
- `selection` 值不在 tag 集合時之顯示（讀自 SwiftUI 一般語意）。
- 以上四項皆列為 P303 動工時之**首輪驗證項**（§6.2）。

## 5. 已知界線與待裁定

### 5.1 界線

- 本 Phase **不得**修改 `Packages/vChewing_OSNeutral_LibVanguard` 之任何檔（P302 之工作面；該處為 `vChewing-LibVanguard` 之 byte-sync 鏡像）。凡本稿列為「對 P302 之要求」者（附錄 A），皆須由 P302 落地。
- 本 Phase 不含方案編輯器；「自訂方案」於本 Phase 之語意為**單筆、整份取代**。
- 「移除自訂方案」若最終不納入，則使用者清空該偏好之途徑為手動（記為已知不便）。
- 本 Phase 之介面改動於**舊系統**（Cocoa 路徑）與**新系統**（SwiftUI 路徑）皆須可編：SwiftUI 之新 `Section` 隨 `VwrSettingsPaneKeyboard.swift` 整檔圈於 `#if compiler(>=6.2)` 之內，無額外處理；Cocoa 之新 `@IBAction` 與 `NSOpenPanel` 須守 macOS 10.9／11 之 API 分流。
- 本 Phase 不涉 `vChewingDebuggable` 之專屬界面（其設定窗與 IME 共用 `CtlSettingsUI`，故自動受益）。

### 5.2 待事主裁定

1. **匯入檔之副檔名／型別**：僅 `.json`（`UTType.json`）抑或另立自訂型別（如 `dualpin`）？前者零成本、後者利於檔案辨識但須於 `Info.plist` 註冊。
2. **匯入成功後是否自動切換至該方案**（並因而開啟拼音模式）？抑或僅提示「已匯入，請於上方選單選用」？
3. **尚未匯入時，自訂項（202）是否陳列於下拉**？（建議：陳列，惟綴以「尚未匯入」。）
4. **「移除自訂方案」是否納入本 Phase**？
5. **匯入檔之大小上限**（擋下誤選之大型檔）；建議 1 MiB（現行內建 JSON 原文之量級為數百行）。
6. **自訂項之標題形**：「自訂：<標題>」抑或逕為「<標題>」？
7. **P303 動工之時點**：是否即於 P302 之 LibVanguard 面凍結後動工（本稿之假設），抑或先做界面之骨架（以假資料驅動）？
8. **自訂 schema 偏好鍵之 `exchangeBlacklisted` 歸屬**：應隨「偏好 JSON」之匯出／匯入流通（如多數偏好），抑或列黑名單（如 `kCassettePath`、`kUserDataFolderSpecified`）？（§4.3-6；字串承載整包 JSON 為本倉首例。）
9. **兩份導出物之重生成責任**：`assets/userdef-metadata.json`（P302 觸發）與 `assets/settings-surface.json`（P302 之 parser 新案與本 Phase 之分隔線皆觸發）由哪一方執行 `make metadata-update`／`make surface` 並提交？（§1.8、§4.3-7。）

### 5.3 未動

- `UserDef`／`PrefMgr`／`PrefMgrProtocol`（偏好鍵之註冊）——P302。
- `KeyboardParser` 之 enum 本體（值域之擴張）——P302。
- `DualpinParser` 之資料模型、校驗、內建兩方案——P302（P301 §3.2–§3.8）。
- 打字機、分派、生效閘、狂打對接——P302（P301 §3.5、§6）。
- `ValueAdd/WebConfigAssistant` 之編輯器；`Info.plist` 之型別註冊（除裁定 1 另行交辦）。
- 鏡照工作。

## 6. 後續（P303 手術範圍）

### 6.1 落點

| 落點 | 檔 | 規模（估） |
| --- | --- | --- |
| 下拉之新段落（SwiftUI） | `Packages/vChewing_SettingsUI/Sources/SettingsUI/SettingsUI/UserDefRenderableImpl.swift:311-330`（分隔線 `:327`；自訂項之標題覆寫） | 數行＋一枚小視圖 |
| 下拉之新段落（Cocoa） | `Packages/vChewing_Shared_DarwinImpl/Sources/Shared_DarwinImpl/UserDefImpl/UserDefRenderableCocoa.swift:44-55`（分隔線）；`:220-273`（標題覆寫） | 數行 |
| 匯入 Section（SwiftUI） | `.../SettingsUI/SettingsUI/VwrSettingsPaneKeyboard.swift`（`:51` 與 `:52` 之間；＋`@State`、`.fileImporter`、`.alert`） | 約 60–90 行 |
| 匯入 Section（Cocoa） | `.../SettingsUI/SettingsCocoa/VwrSettingsPaneCocoaKeyboard.swift`（`:114` 與 `:115` 之間；＋`@IBAction`、`NSOpenPanel`、狀態標籤） | 約 60–90 行 |
| 結果型別 | `.../SettingsUI/SettingsUI/DualpinImportOutcome.swift`（新） | 約 20–40 行 |
| 宿主閉包 | `.../SettingsUI/SettingsUIHost.swift`（`:44-46` 之同群） | 1–2 行 |
| wiring | `Packages/vChewing_MainAssembly4Darwin/Sources/MainAssembly4Darwin/SettingsUIHostWiring.swift`（`:29-32` 之同群） | 約 20–40 行 |
| 文案（四語系） | `Sources/vChewingIME_macOS/Resources/{en,ja,zh-Hans,zh-Hant}.lproj/Localizable.strings` | 每份 ＋10～15 鍵（附錄 B） |
| 後設資料之導出物 | `ValueAdd/WebConfigAssistant/assets/userdef-metadata.json`（`make metadata-update`） | 依 P302 之新增鍵數 |
| 曝露面之導出物 | `ValueAdd/WebConfigAssistant/assets/settings-surface.json`（`make surface`） | 依 P302 之 parser 新案與本 Phase 之分隔線改動 |
| 推式和解（條件性） | `Packages/vChewing_Shared_DarwinImpl/Sources/Shared_DarwinImpl/PrefMgr_Utilities.swift:47-74`（若 P302 之新鍵自帶 `didSet`，納入自我賦值清單）＋ `Packages/vChewing_Shared_DarwinImpl/Tests/Shared_DarwinImplTests/PrefMgrReconciliationTests.swift:36`（鍵數） | 數行 |
| 測試 | `Packages/vChewing_SettingsUI/Tests/SettingsUITests/`（新增一檔：outcome ↔ 文案之映射、匯入路徑之冒煙測試） | 約 80–150 行 |
| 文書 | 現行 Reqs 卷（P303 篇）、`DevReqsHistory.md`（一列）、`KnowledgeMemo4LLM.md` §12.6（一條）、`Tools/housestyle_audit.py`（登錄 P303） | — |

### 6.2 驗證計畫

1. **分隔線與陳列**：`KeyboardParser` 增列 200–202 後，拼音下拉之**末段**恰為三枚雙拼項、其前恰有一條分隔線；注音下拉**不含**之（值域判準之回歸）；Cocoa 之 popup 同構（以 `optionsLocalized` 之內容斷言：`nil` 之位置與 `200` 之前）。
2. **標題之四態**：①無自訂方案 ⇒ 通用鍵（或「尚未匯入」）；②有自訂且語系命中 ⇒ 其 `localizedTitle`；③有自訂而語系未命中 ⇒ 五級 fallback 之結果（P301 §6.2 之 4b 同一套例）；④標題變更（重新匯入）⇒ 兩版介面皆即時更新（SwiftUI 自動、Cocoa 就地改 `title`）。
3. **匯入之正路**：以內建兩方案之 JSON 原文（P301 §3.1：內建即使用者格式之範例）為測資，匯入後 ①偏好鍵之內容＝檔案原文；②狀態列示其 `rawID` 與標題；③（若裁定自動選用）`PrefMgr.shared.keyboardParser` ＝ 202；④引擎側（以 `Arimitsu` 之公開 API）能解出同一份 schema。
4. **匯入之反路**：E1–E9 各造一份反例檔，確認 ①介面彈出對應文案（非鍵名）；②`IMEApp.buzz()` 被觸發；③偏好**不變**（不得半途寫入）。
5. **邊界**：①空檔、②非 UTF-8、③非 JSON、④超大小上限、⑤取消面板（`case .failure`）——皆不留副作用、不崩潰。
6. **W1–W8**：携警告之 schema 得匯入，且介面（或日誌）明示其不支援之項（P301：`autochopPolicy` 非 `.disabled` ⇒ W7、不拒收、**不得靜默降級**）。
7. **程序與偏好**：於 IME 進程內匯入後，**同一進程**之引擎側立即可見新 schema（無跨進程問題，§1.7）；若 P302 有快取，則重載入口確有被呼叫。另：寫偏好後確有 `PrefMgr.shared.reconcileAfterExternalPrefsImport()` 之呼叫（或走 `PrefsExchange.applyPrefsJSONFromData(_:)`），且（若 P302 之新鍵帶 `didSet`）`PrefMgrReconciliationTests` 所記鍵數與該清單同步、測試綠（§1.6、§3.4）。
8. **建置**：①`vChewing_SettingsUI` 之 SwiftUI 路徑（macOS 14+／compiler 6.2+）；②Cocoa 路徑（legacy tools 5.10 之可編性——`make build510`）；③`make metadata` 之逐位元組比對；④**`make surface`／`make surface-check` 之無漂移**（分隔線含 200、拼音排列含三枚新案）；⑤既有測試不退化（`SettingsUITests` 之設定窗開／關）。
9. **不越界**：`git status` 確認 `Packages/vChewing_OSNeutral_LibVanguard` 之檔案**零改動**（本 Phase 之硬界線，§5.1）。

### 6.3 資料流

```
使用者於「鍵盤設定 → 拼音輸入種類」選取 200／201／202
  └─ Picker（binding: Binding<Int>）／Cocoa btnPopup(.selectedTag)
       └─ 直寫 UserDefaults 之 "KeyboardParser4Pinyin"
            └─（引擎側，P302）PrefMgr.keyboardParser → TypingMode.DualPin ＋ DualpinParser
                 （202 ⇒ 取自訂 schema 之 JSON 原文；200／201 ⇒ 取內建）

使用者於「雙拼輸入方案」Section 按「匯入方案（JSON）…」
  ├─ SwiftUI: .fileImporter([.json]) ／ Cocoa: NSOpenPanel(beginSheetModal)
  │    └─ SettingsUIHost.shared.importDualpinSchema(url)
  │         └─（MainAssembly4Darwin 之 wiring）
  │              ├─ 讀檔（UTF-8；host 端 best-effort security scope；UI 端 start/stop）
  │              ├─ DualpinParser 之解碼／校驗（426 條詞幹；E1–E9／W1–W8）
  │              ├─ 成功 ⇒ 寫偏好（自訂 JSON 原文）＋（若裁定）keyboardParser = 202
  │              │        ＋ `PrefMgr.shared.reconcileAfterExternalPrefsImport()`
  │              │        ＋（若 P302 有快取）觸發重載
  │              └─ 回報 DualpinImportOutcome
  ├─ .success ⇒ 更新狀態列（rawID＋標題）；Cocoa 另就地把 202 之 NSMenuItem 標題改掉
  └─ .failure ⇒ IMEApp.buzz() ＋ .alert／NSAlert（碼 → 四語系文案）
```

### 6.4 施工序（提交紀律）

- **手術範圍限於 `vChewing-macOS` 倉、且不含 `Packages/vChewing_OSNeutral_LibVanguard`**：該目錄為 `vChewing-LibVanguard` 之鏡像，其正本屬 P302；鏡照工作不由本 session 兼任（P301 §6.4 同紀律）。
- **提交標題格式**（`vChewing-macOS/AGENTS.md`）：`ModuleName // SubModuleName: Change.`。本 Phase 之建議：
  - `SettingsUI // UserDefRenderable: Add the Dualpin parser section.`
  - `MainAssembly4Darwin // SettingsUIHostWiring: Import Dualpin schema from JSON.`
  - `SettingsUI // Keyboard: Add the Dualpin scheme import section.`
- **依賴序**：P302 之 LibVanguard 面（`KeyboardParser` 之 200–202、偏好鍵、`DualpinParser` 之公開 API）**先行**；P303 於其後動工。若為並行，P303 之首批提交必得待 P302 落地方可編譯（不得以假案頂替後又改回）。
- **`git push` 屬事主**；本 session 之職責止於「正本乾淨、提交分離、並於交付報告指明待鏡照／待同步之事項（`userdef-metadata.json` 與 `settings-surface.json` 之導出、P302 之 Tekkon／LibVanguard 先行提交）」。
- **兩份導出物之提交歸屬**：`assets/userdef-metadata.json` 由 P302 之新增鍵觸發、`assets/settings-surface.json` 由 P302 之 parser 新案與本 Phase 之分隔線共同觸發 ⇒ 建議由**後落地者**跑 `make metadata-update`／`make surface` 並與其程式改動同批提交（避免中間態之 `make audit` 紅燈）；若分屬兩 Phase，則須於各自提交訊息明記「另一份待同步」。

## 7. 附錄

### 附錄 A：P303 對 P302 之介面要求（凍結稿）

| # | 要求 | 用途／理由 |
| --- | --- | --- |
| A1 | `KeyboardParser` 增列 `ofDualpinMSPY = 200`、`ofDualpinGBT17 = 201`、`ofDualpinUserSupplied = 202`，且**宣告序為 200→201→202 連續** | 下拉之新段落（分隔線為前置；§3.2） |
| A2 | 三案之 `localizedMenuName` 各回一枚 `i18n:TypingMethod.Dualpin*` 鍵 | 鍵由引擎宣告、文由 macOS 供給（§1.8） |
| A3 | 曝純值存取器 `dualpinSchemaRawID`（內建 ⇒ `"dualPin.Microsoft"`／`"dualPin.GBT17"`） | 免 macOS 側硬編 `rawID`（§3.1） |
| A4 | 偏好鍵：自訂 schema 之 JSON 原文（一枚 String 鍵）；內建之選擇由 A1 之 parser 值承載 | P301 之單筆持久化策略 |
| A5 | 曝純值存取器：自訂方案之 `rawID`／`localizedTitle(forLocaleTag:)`（無自訂時為 `nil`）；**不得**要求 macOS 側自行解 JSON | 下拉之標題覆寫（§3.3） |
| A6 | 匯入之檢證入口：輸入為 JSON 字串（或 `Data`），輸出為**可窮舉比對之純值**（成功 ⇒ `rawID`＋標題；失敗 ⇒ E1–E9 之碼，可携定位資訊） | 文案映射（§3.4）；`Error`／`NSError` 不合用 |
| A7 | 若 `Arimitsu` 快取已解碼之 schema，須供一枚「重載」入口 | 匯入後即時生效（§3.5） |
| A8 | `validNumeralValueRange`（`UserDef.swift:564-569`）之 `.kKeyboardParser4Pinyin` 值域須隨 A1 擴張（`…200...202`） | 免 JSON 匯入偏好時被 `validateIntRange` 擋下（§4.3） |
| A9 | 型別與檔案由 P302 定名；本 Phase 只引用其公開面（不得因 P303 之便而更動 P302 之命名） | 兩 Phase 之獨立性 |
| A10 | 若新偏好鍵帶 `didSet` 之推式副作用，須明示之，以便 P303 同步 `PrefMgr.reconcileAfterExternalPrefsImport()`（`Packages/vChewing_Shared_DarwinImpl/.../PrefMgr_Utilities.swift:47-74`）之自我賦值清單與 `PrefMgrReconciliationTests.swift:36` 之鍵數 | 長駐行程之推式同步（§1.6） |
| A11 | 新偏好鍵之 `exchangeBlacklisted` 歸屬（是否隨偏好 JSON 匯出／匯入）須明示；並留意「以 `.string` 承載整包 JSON」為本倉首例（值域、助手呈現、匯出三處皆新境） | 配置助手與匯出之語意（§4.3-6、§5.2-8） |

### 附錄 B：文案鍵清單（P303 供文；四語系各一份）

| 鍵 | zh-Hant（建議） | 用途 |
| --- | --- | --- |
| `i18n:TypingMethod.DualpinMSPY` | 微軟雙拼 | 下拉（P302 宣告） |
| `i18n:TypingMethod.DualpinGBT17` | GB/T 34947-2017 雙拼 | 下拉（P302 宣告） |
| `i18n:TypingMethod.DualpinUserSupplied` | 自訂雙拼方案 | 下拉之通用退回文（P302 宣告） |
| `i18n:Settings.SectionDualpinScheme` | 雙拼輸入方案 | 新 Section 之標題 |
| `i18n:Settings.DualpinScheme.Import` | 匯入方案（JSON）… | 匯入鈕 |
| `i18n:Settings.DualpinScheme.Status.None` | 尚未匯入自訂方案 | 狀態列 |
| `i18n:Settings.DualpinScheme.Status.Imported` | 已匯入：%@ | 狀態列（帶 `rawID`／標題） |
| `i18n:Settings.DualpinScheme.ImportFailure.Title` | 無法匯入雙拼方案 | 失敗提示之標題 |
| `i18n:DualpinSchema.Error.E1` … `E9` | （逐碼之說明；文由 P301 §3.3 之定義轉寫） | 失敗提示之正文 |
| `i18n:DualpinSchema.Warning.W1` … `W8` | （逐碼之說明） | 警告之呈現（不阻匯入） |
| `i18n:Message.ReadFailure` | （沿用既有鍵；若無則新造） | 讀檔失敗 |
