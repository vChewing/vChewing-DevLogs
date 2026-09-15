# Phase 216（術後報告）：LibVanguard 的雙 toolchain 建置能力（Swift 5.10 ／ Swift 6.4+）

- 撰寫日期：2026-09-15。**末次修訂：2026-09-15 深夜**（修掉本檔內部因多輪 rebase／追加而生的矛盾；見文末〈修訂紀錄〉）。
- 狀態：**術後記錄，P216 已完工。** 完工登記已於 2026-09-15 完成（`vChewing-DevLogs` 之 `942557d`（`P216.`）一筆，動 `DevReqsHistory.md`／`KnowledgeMemo4LLM.md`／`Reqs4LLM/Archive_P201-P300/Reqs_0211-0220.md`／本檔共 4 檔、+762/−7；該筆為現行 `HEAD` 之可達祖先）。
  - **早前版本此處曾寫「P216 尚未完工、事主接下來會親自在 `vChewing-macOS` 動刀」**——該狀態已於同日結清：macOS 側之對位工作已完成並推送，兩倉 byte-sync 已恢復（§13.4）。
- 範圍：`vChewing-LibVanguard` 一倉（**含其鏡像端 `vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard/`**——依事主 2026-09-15 劃定之分水嶺，LibVanguard 之修改一律屬 P216，含鏡射到 macOS 者）。P216 之外的 macOS 側改動（其餘 18 個 subpackage、倉根 `Sources/`、`Makefile`、`.github/workflows/` 之 toolchain pin）屬 P217，見 `Phase217_SOP.md`。
- 前置：本 phase **無獨立 PreResearch**；它直接建立在 P215（SwiftExtension 自聚合體析出為獨立動態載體）所定的 `Deps/` 佈局之上——該佈局的來龍去脈見 `vChewing-DevLogs/Research/Phase215_PreResearch.md`（含其〈落地狀態〉、〈追加〉、〈追加二〉、〈追加三〉）。P215 已結案，本檔與它無完工牽連。

---

## 一、commit 盤點（現行五筆）

時序即 `vChewing-LibVanguard` 現行 `git log` 的前五筆，**五筆皆為現行 `HEAD` 之可達祖先**。**原另有一筆 `FormatConfig // Add some guards.`，事主複核後整筆刪除**（理由見 §十 第 4 條；該筆連同其 `.swiftformat`／`.swiftlint.yml` 改動一併退場，兩份 config 回到 P216 之前的狀態）。下表 `git show` 之統計為**現行實測值**：

| # | commit | 訊息 | 範圍 |
|---|---|---|---|
| 1 | `a8d5fde` | `SPM // Starting working on Swift 5.10 compilability.` | 6 份版本擇定 manifest（兩個 package 各 3 份）＋ `makefile`：**8 檔、+318/−2** |
| 2 | `28d491f` | `SwiftExtension // Swift 5.10 compilability.` | `Sources/SwiftExtension/SwiftExtension.swift` ＋ `SwiftFoundationImpl.swift`：**2 檔、+375/−206** |
| 3 | `2a4466d` | `LibVanguard // Swift 5.10 compilability.` | 聚合體 23 檔：**+315/−299** |
| 4 | `45bb0ac` | `LibVanguard // Patch unit test issues.` | 單元測試結構之整肅：**16 檔、+490/−412**（內容見 §十四） |
| 5 | `6609f5b` | `SPM // Block Swift 6.2 and 6.3 toolchains.` | Swift 6.x 收斂為 **6.4+ only**：五個 `Package.swift` 抬版 ＋ 6.2／6.3 封堵檔 ＋ CI pin：**9 檔、+88/−5**（內容見 §13.6） |

> **⚠️ 一切 hash 記載都會隨 amend／rebase 失效——判準請以「訊息 ＋ 小節主題」為準。** 本檔初稿與其各輪追加曾逐次記錄當時的 hash（`189a76d5`／`6e5f19f2`／`a2160db8` → `0681e14`／`b757b2a`／`2bbce67` → `a4db83c`／`5b6e9c3`／`2bef551` → …），**這些舊值現皆不可達**（僅存於 reflog）。**本檔只保留上表之現行值。**

### 1. manifest 與建置腳本（`a8d5fde`）

- `Package@swift-5.10.swift`（聚合體 143 行、子套件 40 行）
- `Package@swift-6.0.swift` / `Package@swift-6.1.swift`（各 2 份，封堵檔，共 62 行）
- `makefile`：`LEGACY_*` 五個變數、`build510`、`build510SwiftExtension`、`clean510`，`spmClean` 一併清兩條 scratch，`.PHONY` 同步。

5.10 側 manifest 的四項刻意差異：**產物一律 static**（宿主是 macOS 10.9 的 legacy app，dylib 須提前專門摻 libArcLite）、**`platforms: nil`**（PackageDescription 能宣告的 macOS 最低值只有 10.10，一宣告即被明文寫入產物）、**不含任何測試靶**（單元測試只由 6.2+ 負責，連 `LXAssemblyMaterials4Tests`／`HomaSharedTestComponents` 兩靶一併不宣告）、**不收 `vChewingSharedCLI`**（一次性枴杖，且它是本側唯一會被壓上 minOS 的可執行檔）。另不使用 `.defaultIsolation(MainActor.self)` 等 6.x 才有的設定。因本側不需要任何 `#if`，故**未沿用 `Package.swift` 那套 `@resultBuilder` DSL**。

### 2.（**該 commit 已刪除**）格式化／靜態分析的防線

原有一筆 `FormatConfig` commit，內容為：

- `.swiftformat`：把「勿加 `modifierOrder`」「`--extensionacl` 必須維持 `on-declarations`」「`trailingCommas` 已除役」寫成不可動的三條。
- `.swiftlint.yml`：新增 `custom_rules.swift510_no_nonisolated_extension` 絆線，並把 `trailing_comma` 列入 `disabled_rules`。

**事主複核後整筆刪除**：本次手術無須動 config（理由見 §十 第 4 條），兩份 config 已回到 P216 之前的狀態。以上內容僅存檔供對照；其中兩道「尾逗號除役」屬多餘，另兩件（絆線與「三條不可動」註記）隨該 commit 一起退場。

### 3. SwiftExtension 子套件（`28d491f`）

- `SwiftExtension.swift`（16 個 extension 標頭的 `nonisolated` 下放到 37 個成員）
- `SwiftFoundationImpl.swift`（16 個 extension ＋ 5 個型別的同類下放、`asyncOnMain`／`mainSync` 的 compiler-flag 分隔、FileHandle 現代 API 的整組語法糖、`deinit` 的 `mainSync` 包裹）

### 4. 聚合體（`2a4466d`）

23 檔。三件大事：`nonisolated` 的清剿、`FileHandle` 舊 shim 的除役、`@MainActor` 自協定撤除；另外收斂了 `NSMutex`、把 dispatch 調度改為 `mainSync` 兜底、刪掉全倉的呼叫引數列尾逗號。

**驗收數字**（皆已複驗）：6.2 側 `swift build` ✅、`swift test` **535 項 0 失敗**（與本 phase 動工前同數）；5.10 側 `make build510SwiftExtension` ✅（`libVanguardSwiftExtension.a`，540 KB）、`make build510` **rc=0、0 error**（16.63s，`libVanguard.a` 14 MB）。

### 5. 封堵令（`6609f5b`）

Swift 6.x 收斂為 **6.4+ only**。**完整動機、實測與清單見 §13.6**（該節原為「待 Swift 6.4 問世後執行」之備忘，**已於 2026-09-15 執行完畢**）。此筆之 **LibVanguard 側**（兩倉之聚合體與子套件之封堵檔與 manifest 抬版）屬 P216；其**倉根 meta-manifest ＋ 三條 CI workflow 之 toolchain pin** 屬 P217。

---

## 二、SwiftPM 的版本擇定機制（實測釘死）

`Package@swift-X.Y.swift` 的擇定規則，官方文件語焉不詳，本輪以隔離探針釘死：

> **於 `Package*.swift` 全集中，取「檔內宣告的 tools version ≤ toolchain 版本」者之最高者；同版時 `Package.swift` 勝出；宣告值高於 toolchain 者單純落選、不報錯。**

三個要點各自有實測支撐：

1. **比對基準是檔內宣告、不是檔名。** 反證：`Package.swift` 宣告 `// swift-tools-version: 7.0`（高於 6.4 toolchain）時不會報錯，只是被略過。
2. **同版時 `Package.swift` 優先。** `Package.swift` 與 `Package@swift-6.1.swift` 同宣告 6.1 時，前者入選。
3. **`Package.swift` 是「以自身宣告值參賽的候選」，不是永遠的 fallback。** 這是本輪最容易誤判的一點：本倉 `Package.swift` 宣告 6.2，故 6.3.3／6.4 toolchain 取它（6.2 ＞ 6.1），而非取 `Package@swift-6.1.swift`。

**封堵檔的手法**：`Package@swift-6.0.swift` / `6.1` 兩份只寫 `import PackageDescription` ＋ `#error("""…""")`。`#error` 於 manifest 編譯期即中止，錯誤訊息乾淨可讀（實測輸出含自訂訊息 ＋ `invalid manifests at […]`）。之所以要為 6.0／6.1 各寫一份，正是因為比對基準是**檔內宣告的 tools version**——6.1 toolchain 只會挑到 6.1 那一檔。

**副產物**：6.0／6.1 是「災星」級 toolchain（既不支援 libArcLite 混編，亦不支援 Approachable Concurrency），本倉自此在該兩版下**明文拒絕建置**，而非以殘缺設定產出看似成功的東西。

---

## 三、toolchain × SDK 的硬配對（最容易浪費一整輪的坑）

**Swift 5.10.1 toolchain ＋ Xcode 27 的 MacOSX27.0.sdk ＝ 312 個錯誤，且全部是掩蓋式失敗**：

```
module '_c_standard_library_obsolete' requires feature 'found_incompatible_headers__check_search_paths'
unknown argument: '-target-arch-variant'
could not build module 'Darwin' / 'CoreFoundation' / 'Foundation'
```

沒有一條指向真正的病灶。**正解是 Xcode 15.4 的 MacOSX13.3.sdk**（亦即 legacy 專案自己在 `project.pbxproj` 裡寫的 `SDKROOT = macosx13.3`）。

**更陰的一層**：`swift package dump-package` 在 SDK 27 下**照樣成功**——因為 manifest 不 `import Foundation`。所以「manifest 載得動」**不足以**證明該 SDK 可用；本輪曾據此誤判一次。

---

## 四、部署目標：10.9 不存在、10.10 才是真底

**`Data` 本身標為 macOS 10.10 起可用。** 實測三種形態在同一 toolchain 下皆報 `'Data' is only available in macOS 10.10 or newer`：

- `func f() { let d = Data() }`（表達式位置）
- `func g() -> Data? { nil }`（簽名位置）
- **連 legacy 自己以 `@backDeployed(before: macOS 10.15)` 提供的同名 shim 形態也一樣**——`Data` 是型別、不是可比對的符號，平替不了。

故 `-target x86_64-apple-macosx10.9` 建不出東西；`10.10` 則 OK。附帶：legacy 的 `project.pbxproj` 寫的是 `MACOSX_DEPLOYMENT_TARGET = 10.9` ＋ `SDKROOT = macosx13.3`，與本實測**表面矛盾**，尚未追出 Xcode 實際送了什麼 triple（列為殘留疑點）。

**SwiftPM 會吞掉你想壓低的部署目標**，三種嘗試都失敗：

| 手段 | 實際結果 |
|---|---|
| `platforms: [.macOS(.v10_10)]` | 仍被抬到 toolchain 地板（x86_64 為 `-target …-macosx10.13`） |
| `--triple x86_64-apple-macosx10.9` | **版本部分被丟掉**，仍送 `-target …-macosx10.13` |
| arm64 | 被 linker 直接釘在 `minos 11.0`（arch 地板），任何宣告都無效 |

**唯一有效的辦法**：`-Xswiftc -target -Xswiftc x86_64-apple-macosx10.10`（同一個 `-target` 後出現者勝；實測 `.o` 與最終二進位元組的建置版本確實是 10.10）。

**為什麼可以只改編譯期**：本側產物一律是**靜態庫**，`.a` 是純 `ar` 封存、**不帶任何 load command**（`vtool -show-build libX.a` 直接以 `not mach-o` 拒收），故 minOS 不進產物、只影響 availability 檢查——而這正是我們要的（讓 5.10 側的可用性判定與 legacy app 一致）。10.9 的實際落地仍由 legacy Xcode 連結端決定。

---

**2026-09-16 更正（本節前半之「`Data` 說」不成立）**：以同一組 Swift 5.10.1 ＋ `MacOSX13.3.sdk` 重測，`let d = Data()` 於 `-target x86_64-apple-macosx10.9` 下**編譯並連結皆 rc=0**，產物 `vtool -show-build` 記為 `LC_VERSION_MIN_MACOSX version 10.9 / sdk 10.9`（`Data` 於該 SDK 之註記並非 10.10 起）。原實測極可能是在**未帶 `-sdk`** 的環境下跑的——那樣連 `import Foundation` 都不成立（`error: no such module 'Foundation'`），錯誤訊息容易被誤讀成可用性問題。

**10.9 的真正阻礙是 5 支 AppKit API（共 57 筆 availability 錯誤、涉 7 檔）**，全倉於 10.9 探針下實測：

| API | 筆數 | 落點 |
|---|---|---|
| `NSViewController.addChild` | 36 | `SettingsUI/SettingsCocoa/{VwrSettingsCocoaPanes,CtlSettingsCocoa}.swift` |
| `NSSearchField.sendsWholeSearchString`／`.sendsSearchStringImmediately`／`.placeholderString` | 5＋5＋5 | `CandidateWindow/TDK4AppKit/*`、`LibVanguard/Session/InputSession.swift`、`Shared/PrefMgr_Core.swift` |
| `NSColor.secondaryLabelColor` | 4 | `SettingsUI/SettingsCocoa/*` |

即 10.9 **並非不可能**，而是要以 `if #available(macOS 10.10, *)` 或等效改寫換來；做與不做屬取捨、非硬限制。現行 `10.10` 之選擇因此是「未付這筆成本」的結果，而非 SDK 所迫。


---

## 五、Swift 代際語法矩陣（兩套 toolchain 逐條實測）

**Swift 5.10 拒收、6.x 接受**（皆為 SE-0449 等新語法）：

| 寫法 | 5.10 的反應 |
|---|---|
| `nonisolated extension X { … }` | `'nonisolated' modifier cannot be applied to this declaration` |
| `nonisolated struct／enum／class` | 同上 |
| `nonisolated deinit` | SE-0371（Swift 6.1）語法，拒收 |
| **裸** `nonisolated var` 掛儲存屬性 | `'nonisolated' can not be applied to stored properties` |
| `@retroactive` 掛 conformance | `unknown attribute 'retroactive'`（並連帶把 `LocalizedError` 誤解析成 `any LocalizedError`） |
| `class X: @MainActor SomeProtocol` | SE-0434 隔離同構，5.10 報 `unknown attribute 'MainActor'` ＋ `inheritance from non-protocol, non-class type 'any …'` |
| 呼叫引數列尾逗號 | SE-0439（Swift 6.1），報 `unexpected ',' separator` |

**Swift 5.10 接受、且與 6.x 通吃**（本輪的「單一形態」工具箱）：

- 成員級 `nonisolated`（`func`／`init`／`subscript`／計算屬性）
- `nonisolated let`（實例儲存、不可變）
- `nonisolated(unsafe) var`（僅 **class** 的儲存屬性需要）
- `@MainActor` 掛型別／成員（但見 §七：會殺掉 ≤10.14 的相容性）

**兩個必須記住的否定結果**：

1. **`#if compiler(>=6.2)` 只夾住修飾符是無效的**。`#if compiler(>=6.2)` ／ `nonisolated` ／ `#endif` ／ `struct S {}` 這種寫法，5.10 之所以「通過」只是因為整個分支被編掉；6.x 會直接報 `cannot find 'nonisolated' in scope`。**只能整段宣告各寫一份。**
2. **struct 的儲存屬性不可標 `nonisolated`**：值型別的儲存屬性永不受 actor 隔離拘束，標了在 5.10 是 `'nonisolated' is redundant on struct's stored properties`、在 Swift 6 直接是**錯誤**。（此條為本輪一度誤導過的方向，記錄以免重蹈。）

**順帶**：把巢狀型別「拖出 namespace 到檔案層級」**不會解除其隔離**（實測：檔案層級型別在 `defaultIsolation` 下同樣受拘束），它只是形狀整理；本輪 `lxCassette.swift` 的 `CassettePatternToken`／`RevPrototype` 兩處即屬此類。

---

## 六、手法：把標頭上的修飾詞下放到成員

本輪的主力 codemod（腳本留於工作區 `tmp/p126pushdown.py`（extension 版）與 `tmp/p126pushdown_types.py`（型別版））：

> 把 `nonisolated extension X { … }`／`nonisolated class X { … }` 標頭上的 `nonisolated` 拿掉，改寫到**每個成員**之首；儲存屬性 `let` → `nonisolated let`、可變 `var` → `nonisolated(unsafe) var`；`deinit`／`case`／續行（`)`、`->`）／註解／`#if` 一律不動。

**無法下放、必須改用別的手段者**（本輪逐類遇到並處置）：

- **enum 帶 `case`**、**帶合成 conformance 的 struct**（`Hashable`／`Codable`／`CaseIterable`）→ 沒有成員可掛，只能整段 `#if compiler(>=6.2)` 分隔，或（若用途全在 MainActor 上）整條拿掉該修飾詞。
- **巢狀型別**（無法在自己身上掛 `nonisolated`）→ 拖出到檔案層級。
- **共享可變狀態**（`static var`／`class` 的可變儲存屬性）→ `nonisolated(unsafe)`。

**兩版寫法真的不同時**：`#if compiler(>=6.2)` 分隔整段宣告，<6.2 分支採 `vChewing-OSX-Legacy` 的寫法（本輪的最終結果是**全倉只剩 1 處**這種分隔，見 §十一）。

---

## 七、關鍵洞見：`defaultIsolation`、`@MainActor` 與協定

5.10 側沒有 `defaultIsolation(MainActor.self)`（該 SwiftSetting 是 tools 6.2 起才有），而 6.2 側六個靶（BPMFVS／Shared／BrailleSputnik／LexiconAssembly／LibVanguard／vChewingSharedCLI）都有。這個落差曾以 **1771 筆錯誤**的形式爆發（1052 ＋ 719），看起來像一場硬仗；實則只有**兩個根因**，且一刀可解。

**量測過程**（以 scratch 副本逐層中和）：

| 層 | 中和掉的東西 | 剩餘錯誤 |
|---|---|---|
| L1 | `UserDef` 的兩處（尾逗號、`.sortedKeys`） | 1 筆（`withFileHandleQueueSync` 的 completion 呼叫） |
| L2 | 上開 1 筆 | 進到 `Sources/LibVanguard/`，**1052 筆**，根因是 `class InputHandler: @MainActor InputHandlerProtocol` 與 `class InputSession: @MainActor SessionProtocol` ——其餘 ~1032 筆全是級聯 |
| L3 | 把那 2 處改成不帶 `@MainActor` 的同構 | **719 筆**（372 屬性／185 方法／135 屬性寫入／22 autoclosure／3 init），仍全在 `Sources/LibVanguard/` |

**正解**（事主裁定「Legacy 怎麼寫，你就怎麼寫；你把 `@MainActor` 從 Protocol 撤掉」）：實查 legacy，`InputHandlerProtocol`／`SessionProtocol`／`SessionCoreProtocol` 及 `Sources/Shared/Protocols/` 六檔**本來就沒有 `@MainActor`**，legacy 全倉亦無任何宣告層級的 `@MainActor`。照抄該形狀，**只改 3 行**：

- `InputHandler_CoreProtocol.swift`：協定宣告撤掉 `@MainActor`
- `InputHandler.swift`：`: @MainActor InputHandlerProtocol` → `: InputHandlerProtocol`
- `InputSession.swift`：`: @MainActor SessionProtocol, Sendable` → `: SessionProtocol, Sendable`

結果：**L2 ＋ L3 一併歸零**，`make build510` rc=0。機理：5.10 側沒有 `defaultIsolation`，協定一旦不再是 `@MainActor`，整個 `LibVanguard` 層就是**全體一致的 nonisolated**，主客體之間的隔離落差消失；而 6.2 側因 `defaultIsolation` 的關係，協定拿掉顯式標註後**仍然是 MainActor**、語義不變。**這是本輪唯一的「單一形態、零取捨」大手術。**

**硬約束（事主明令）**：**不得**為消錯而在型別／成員上**新增** `@MainActor`——那等於殺死對 macOS 10.14 為止所有系統的相容性（`MainActor` 屬 Swift Concurrency，需 10.15 起的執行期）。本輪結束時 `Sources/` 僅存 1 處 `@MainActor`，且位於 `#if compiler(>=6.2)` 分支內。

---

## 八、dispatch 調度與 `deinit`

方針（事主原話）：「non-MainActor 只用於調度，任務都還是在 MainActor 上跑。如果需要在指定的 DispatchQueue 內運行的東西的話，那麼輪到這個 Queue 執行 closure 的時候、就將裡面的內容用 `mainSync` 包裹。」

**一個必踩的互鎖陷阱**：`queue.sync { mainSync { … } }` **必定死鎖**——呼叫方全在 MainActor，main 卡在 `queue.sync`，而佇列執行緒的 `mainSync` 又等 main。故 `withFileHandleQueueSync` 必須寫成「已在主執行緒就直接跑，否則才 `queue.sync { mainSync { … } }`」（`Thread.isMainThread` 快徑）。此為全倉唯一未能照字面貫徹之處，已獲事主核可。

**`deinit`**：`nonisolated deinit` 是 SE-0371／Swift 6.1 語法、5.10 拒收；一律樸素寫法 ＋ 把內容用 `mainSync` 裹上（`InputSession.deinit`、`Debouncer.deinit`）。

**`NSMutex` 的退場**：既然全體回到 MainActor，`NSMutex` 保護的共享狀態改回普通 stored property 即可（`InputSession.sessionAddrByControllerAddr`、`LXFacade` 的 `factoryGeneration`／`pomGeneration`／`factoryTrie`／`lxPerceptor`）。**唯二例外**：`TrieKit` 與 `ResourceLocator` **不在** `defaultIsolation` 名單上，故 `NSMutex` 這個型別本身仍須能從 nonisolated 情境使用（其定義留在 SwiftExtension，以 `#if compiler(>=6.2)`／<6.2 兩分支分隔）。

---

## 九、FileHandle 現代 API 的平替（事主定讞的形態）

**死刑判決：`@backDeployed(before: macOS 10.15)` 同名重宣告是昏招。** 它在本模組內重複宣告 Foundation 的同名 API，令跨模組呼叫點（如 `LXConsolidator.checkPragma`）落入 overload ambiguity 而無法編譯。本倉的 `SwiftExtension` 因此長期把整段 shim 註解掉，而 `LexiconAssembly` 又另有一組作用中的同類 shim——兩模組各宣告一次 `FileHandle.seek(toOffset:)`，正是同一個病的兩種表現。

**定讞形態：整組「現代名 ＋ old-macOS fallback」的語法糖**（`Deps/…/SwiftFoundationImpl.swift` 的〈FileHandle Backports〉一節；< 10.15／10.15.4 走舊名、≥ 走現代名）：

| 糖 | 舊名 fallback |
|---|---|
| `read(upTo count: Int) throws -> Data?` | `readData(ofLength:)`（空→nil） |
| `seek(to offset: UInt64) throws` | `seek(toFileOffset:)` |
| `readToEndOfFile() throws -> Data?` | `readDataToEndOfFile()`（空→nil） |
| `seekToEOF() throws -> UInt64` | `seekToEndOfFile()` |
| `writeData(_ data: Data) throws` | `write(_:)` |
| `closeTheFile() throws` | `closeFile()` |

聚合體側 9 個呼叫點改走糖（`LXConsolidator` 5、`lxPerceptionPersistor` 4），`LXConsolidator` 自帶的 33 行舊 shim 整組移除。

---

## 十、工具鏈的坑（SwiftLint／SwiftFormat／make）

1. **`match_kinds` 會讓 `custom_rules` 靜默失效。** 實測 swiftlint 0.61.0：加了 `match_kinds: [keyword, identifier, typeidentifier]` 的規則**完全不觸發**（匹配被靜默丟棄）。改用**行首錨定** `'(?m)^[ \t]*nonisolated[ \t]+extension[ \t]'` 即達到目的：真宣告會抓、註解裡提到則不會誤報。
2. **`swiftlint lint --fix` 模式下不報自訂規則。** 同一份檔案集：read-only 模式抓 19 筆、`make lint`（`--fix --autocorrect`）**0 筆、rc=0**。故絆線目前只在非 fix 呼叫下生效。（read-only 模式下僅有警告時 exit code 為 2。）
3. **`make lint` 是對全倉的 auto-fix。** 本輪誤跑一次，一舉改動 **84 個無關檔案**（已全數 `git checkout --` 還原）。**紀律：交差前只用 `make lintFormatUncommitted`，或逐檔處理。**
4. **【2026-09-15 更正】尾逗號的「兩工具互相打架」之說不成立。** 本報告初稿曾斷言 SwiftLint 的 `trailing_comma` 與 SwiftFormat 的 `trailingCommas` 方向相反、互相打架（並據此主張兩者都要除役）。事主複核後指出該結論有誤，實測複驗如下：
   - **整條 pipeline**：在已 commit 的樹上跑 `make lintFormat`（＝`swiftlint --fix` 後 `swiftformat`），**淨差異為零**——該樹是此 pipeline 的不動點，不會冒出有問題的內容。
   - **隔離測試**：對含多行呼叫引數列的樣本檔，`swiftlint --fix` **單獨跑不動它**、`swiftformat` 單獨跑也不動它（唯一變動是 `markTypes`／`organizeDeclarations` 補的 `// MARK:` 段）。
   - 故：**沒有任何一支工具會把呼叫引數列尾逗號加回來**；`disabled_rules: [trailing_comma]` 與自 `--rules` 移除 `trailingCommas` 這兩道「除役」**並非必要**。當初之所以誤判，是拿**單獨執行**兩支工具的結果推論，而單獨執行所見的是「SwiftLint 後、SwiftFormat 前」的中間態，不等於 pipeline 的淨行為。
   - 教訓（一般化）：**推論工具行為時必須以整條 pipeline 的淨結果為準**；單獨執行的中間態不可作為依據。（`UserDef.swift` 那處違反 5.10 的呼叫引數列尾逗號係**手寫**而來，非工具所加；刪除它是對的，但不需要靠改工具設定來維持。）
   - 該道「除役」原先與其它 guards 同裝在一個 `FormatConfig` commit 裡。**事主複核後已將該 commit 整筆刪除**，`.swiftformat` 與 `.swiftlint.yml` 回到 P216 之前的狀態（即：`trailing_comma` 復為預設啟用、`trailingCommas` 復返 `--rules` 白名單、`swift510_no_nonisolated_extension` 絆線不再存在）——理由是根本無須動 config（見下）。
   - **事主補記（結論與原則）**：**本次手術無須修改 SwiftLint 與 SwiftFormat 的 Config。** 原因：這條格式管線謀求的是兩者**順序運行之後的最終結果**——哪怕 SwiftLint 整出了超出預期的修改，也會被 SwiftFormat 斧正回去。故判準永遠是「`make lintFormat` 跑完之後樹上有什麼」，而非任何單一工具、任何中間態。
5. **`--extensionacl` 是 `nonisolated extension` 風險的閘門**：`on-declarations`（本倉現行）方向是**把修飾詞自 extension 下放給成員**，與我們要的一致；改成 `on-extension` 則會把成員共有的修飾詞**抬到 extension 標頭**——那正是產生 `nonisolated extension` 的路徑。SwiftFormat 0.55.2 本身**沒有任何 isolation／actor 規則**（`--rules` 又是白名單），故本倉現行設定本身即無此風險；原設計的「絆線」已隨前述 `FormatConfig` commit 一併退場，若日後想再要那道保險，得另立一筆。
6. **`void_return`（SwiftLint，要 `-> Void`）與 `--voidtype tuple`（SwiftFormat，要 `-> ()`）亦互相打架**，本倉長年如此；`make lintFormatUncommitted` 的淨結果由後者勝出。

---

## 十一、殘留與未決

**口徑（2026-09-15，P217 收工後回填）**：本表是本檔的**殘留清單**，狀態標籤只有三種——

- **【已裁定保留】**：事主已裁定「維持現狀、不處理」，**不是待辦**；留檔是為了記住裁定與其代價。
- **【已結清】**：該殘留所描述的狀態**已消失**（後續工作已解）。
- **【事實層未解】**：**非**待裁定事項，而是施工時撞上的觀測疑點；不阻塞任何工作，留作觀測。

**收工時的判定：七項之中，已裁定保留 4 項、已結清 2 項、事實層未解 1 項——沒有任何一項是「待事主裁定」。**

| # | 項目 | 狀態 | 現況、代價與落點 |
|---|---|---|---|
| 1 | `Sources/Tekkon/Tekkon_PinyinTrie.swift:110` 的 `nonisolated(unsafe) private static var sharedCache` | **【已裁定保留】** | **不用處理（事主 Q05）**：`Tekkon` 與 `Homa` 兩靶**不在 `defaultIsolation` 名單**（P217 §6.1 實查其 `swiftSettings` 為空），其 `nonisolated(unsafe)` 非但可留、**且與 legacy 倉逐字相同**。原列的兩條路（納入 manifest／搬進 Sendable 盒）皆屬重構，**不做**。落點：P217 §6.4 |
| 2 | 5.10 側 2 個 warning：`InputSession.clientProxyObjectIdentifier`、`PrefMgr.didAskForSyncingLMPrefs`（`Sendable` 一致性 ＋ 可變 stored property） | **【已裁定保留（僅列報）】** | **P217 收工時仍會出現**（實測）。消音只能靠 `nonisolated(unsafe)`（會反過來拆掉 6.2 側隔離）或補 `@MainActor`（違反本檔 §七 之硬約束），**故維持列報**。**驗收門檻是「0 error」，warning 不在門檻內**（P217 §10）。落點：P217 §1.3 之現行處置行 |
| 3 | 全倉僅存 1 處 `#if compiler(>=6.2)`：`Sources/LexiconAssembly/vChewingLXAssembly_Common.swift:72` 的 `readFileContentAsync`（兩分支僅差 `completion` 的 `@MainActor`） | **【已裁定保留】** | **事主裁定保留**：拿掉它會迫使 5 個呼叫端各自寫 `#if` 差分，成本更高。P217 收工時**仍為 5.10 側全倉唯一一處**。落點：P217 §1.3 之現行處置行 |
| 4 | `withFileHandleQueue*` 一組 GCD 佇列 | **【已裁定保留】**（**原判「待退役」已被取代**） | **事主 Q06 裁定：`不用退役`**。角色自此定死為「**只管任務觸發時機**」——佇列**不承擔並發**，任務本體一律以 `mainSync {}` 回到 MainActor（**禁用 `{ @MainActor in … }` 等不相容寫法**），並受「**同一檔案不得被多個 actor 同時讀寫**」之約束。**`withFileHandleQueueAsync` 仍為 0 呼叫端之死 API**（P217 實查：全工作區僅剩其自身宣告），惟事主既已裁定不退役，**本檔不再將它列為待辦**。落點：P217 §6.2.1（三條紀律） |
| 5 | legacy `project.pbxproj` 的 `MACOSX_DEPLOYMENT_TARGET = 10.9` 與本檔 §四 的 `Data` 實測相牴觸 | **【事實層未解】** | **疑點未解，但不阻塞施工**：P217 之 Q03 已把該 phase 的處置定為「`platforms: nil`、故意不設 Availability 限制、交由 Xcode 15 ＋ macOS SDK 端裁決 10.9 合規性」，且 Q07 明令**不動 pbxproj**。此事**屬下一 phase**（P217 §十四 之 N1／N2：10.9 專用 xcodeproj 之部署、新舊 pbxproj 分家）。落點：P217 §1.3 文末〈事實層的開放問題〉 |
| 6 | 本倉 `Sources/` 自此與 `vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard/Sources/` 不再逐位元組相同（P214 所定的性質） | **【已結清】** | 事主當時即裁定「**遲早還會同源，但不是現在**」。**P217 收斂段期間已同源**：收工時實測 `Sources/`／`Tests/`／`Deps/`／六份版本 manifest／`makefile` **兩倉零差異**（`diff -rq` 與 `cmp`；僅未追蹤之 `.DS_Store` 之類不同）。落點：P217 §11.2（I2）與 §13.4 |
| 7 | 本輪 `Sources/` 未動、而 `vChewing-macOS` 側尚有對位工作（含上述第 1／4／6 項的連帶） | **【已結清】** | **P216 已完工登記**（「不標完工」是**當時**的狀態），後續由 **P217** 接手並收工：`vChewing-macOS` 側 19 個目錄在 5.10 側全數 rc=0、兩支終點產物（`libInstallerAssembly4Darwin.a`／`libMainAssembly4Darwin.a`）已產出。落點：P217 §十三 |

**與 P217 的關係（一句話）**：第 1／4 項的裁定出自 **P217 的事主 Q05／Q06**；第 5 項則被 P217 明確**移出該 phase**（N1／N2）。故本檔 §十一**不再有「待事主裁定」項**——P217 自身的殘留清單另見 `Phase217_SOP.md` §十二（R1～R23）與 §十四。

---

## 十二、可重現的指令集

```bash
# 6.2 側（現行 macOS 12+）
swift build && swift test                 # 應 535 項 0 失敗

# 5.10 側（macOS 10.10 legacy 靜態庫）
make build510SwiftExtension               # 只建置巢狀子套件（SwiftExtension 模組本身）
make build510                             # 聚合體：libVanguard.a
make clean510                             # 清兩條 scratch

# 環境配對（makefile 內 LEGACY_*，可用 ?= 覆蓋）
#   LEGACY_TOOLCHAIN = ~/Library/Developer/Toolchains/swift-5.10.1-RELEASE.xctoolchain
#   LEGACY_SDK       = /Applications/Xcode-15.app/…/MacOSX13.3.sdk
#   LEGACY_TRIPLE    = x86_64-apple-macosx10.10
#   scratch          = .build/.legacy（聚合體）、.build/.legacy-swiftExtension（子套件）
```

三項配對缺一不可，理由見 §三／§四：SDK 錯則得到 312 個掩蓋式錯誤；部署目標錯則 `Data` 直接不可用；scratch 共用則兩份 manifest 的產物互相踩（5.10 的 SwiftPM 讀不懂 v7 版 `workspace-state.json`，會警告並就地覆寫）。

---

## 十三、追加（2026-09-15）：後續各輪 amend、macOS 側的鏡像、與封堵令

> **本節之沿革**：初稿寫於「三筆 commit 時期」，標題原帶「**待整理**」；其後 13.2～13.5 各輪追加陸續結清，13.6 之封堵令亦已執行完畢。**本節現已無待整理項**（結清紀錄見各小節之【結清】標記與 §13.4）。

### 13.1 hash 沿革（**歷史紀錄，現值見 §一**）

`vChewing-LibVanguard` 的 commit 在本 phase 期間歷經**多輪** amend／rebase。下表為完整沿革，供追溯之用——**表中「現行」欄所記之值亦已全部失效**：

| 訊息 | 初稿 | 第二輪 | 第三輪（亦已失效） |
|---|---|---|---|
| `SPM // Starting working on Swift 5.10 compilability.` | `189a76d5` | `0681e14` | `a4db83c` |
| `SwiftExtension // Swift 5.10 compilability.` | `6e5f19f2` | `b757b2a` | `5b6e9c3` |
| `LibVanguard // Swift 5.10 compilability.` | `a2160db8` | `2bbce67` | `2bef551` |

**現行值一律以 §一 之表為準**（`a8d5fde`／`28d491f`／`2a4466d`／`45bb0ac`／`6609f5b`）。**含本檔在內的一切 hash 記載都會隨 amend 失效——判準請以「訊息 ＋ 小節主題」為準，hash 只當線索。**

### 13.2 amend 引入的內容（由 macOS 側可見差異推知）【**已結清**】

> **【結清，2026-09-15】** 本節原標「待事主確認」。實查結果：本節所記之三檔**皆已入庫**（macOS 側 `SwiftFoundationImpl.swift` → `89af456f`、`Shared.swift` → `d920059e`、`VwrSettingsPaneDevZone.swift` → `d033e90c`），且本倉對位之 `SwiftFoundationImpl.swift`（`28d491f`）與 `Shared.swift`（`2a4466d`）與之**逐位元組相同**（§13.4 之 I2 複驗）。以下為當時的調查原文，保留作沿革。

事主指示「詳見 `vChewing-macOS` 的 uncommitted changes 以及其最近兩三個 commit」；實查該倉如下。

**新增的兩筆 commit**（同一套手術在 macOS 側的鏡像，範圍與 LibVanguard 側逐一對應）：

- `52200afb SwiftExtension // Swift 5.10 compilability.`：5 檔 +405/−193（子套件的 3 份 manifest ＋ `SwiftExtension.swift` ＋ `SwiftFoundationImpl.swift`）
- `ddb217f6 LibVanguard // Swift 5.10 compilability.`：聚合體側（3 份 manifest ＋ 23 檔 `Sources/`）

**未 commit 的 3 個檔**（macOS 目前編譯正常）：

1. `Packages/vChewing_OSNeutral_LibVanguard/Deps/VanguardSwiftExtension/Sources/SwiftExtension/SwiftFoundationImpl.swift`（+49 級）：
   - `HSBA` 改為 `#if compiler(>=6.2)` 分隔——6.2 分支保留型別級 `nonisolated public struct HSBA: Sendable`，<6.2 分支為樸素 `public struct HSBA: Sendable`，兩分支 body 逐字相同（儲存屬性皆不標）。**這正是「struct 的儲存屬性不可標 `nonisolated`」的正解**（見 §五），也是 §十一 未決事項的落地。
   - `CandidateKey` 與其巢狀 `ValidationError` 採同一手法（6.2 分支 `nonisolated public enum`，<6.2 分支樸素）。
2. `Packages/vChewing_OSNeutral_LibVanguard/Sources/Shared/Shared.swift`（+61 級）：同類的 compiler-flag 分隔。
3. `Packages/vChewing_SettingsUI/Sources/SettingsUI/SettingsUI/VwrSettingsPaneDevZone.swift`（8 行）：把 `UserDef.exportAsJSON()` 與 `FileWrapper(regularFileWithContents:)` 那段**包進 `mainSync { … }`**——因為 `UserDef` 在 5.10 側的處置之後已屬 MainActor（同 §八 的調度方針）。

### 13.3 待整理（事主稍後自行處理 macOS 倉）【**已全部結清**】

> **【結清，2026-09-15】** 下列四項皆已完成：前三項見 §13.4（macOS 側整理完畢、byte-sync 恢復）；第四項（本倉是否同步 `HSBA`／`CandidateKey`／`Shared.swift` 之分隔手法）亦已達成——兩倉 `Sources/`／`Deps/` 現為零差異。以下為當時原文。

- macOS 側上述 3 個未 commit 檔的整理與 commit。
- macOS 側的 `Sources/` 與本倉自此的同源性關係（§十一 第 6 項）。
- 本倉若要同步 13.2 所列的 `HSBA`／`CandidateKey`／`Shared.swift` 的分隔手法，需確認與 macOS 側逐字一致（目前**未做**，本檔僅記錄）。
- 本節內容為**據 macOS 側差異反推**，未逐行核對本倉 amend 後的實際內容。

### 13.4 macOS 側整理完畢、byte-sync 已恢復（2026-09-15，實測）

事主已將 macOS 倉的對位修改整理並推送。複驗如下：

- **macOS 倉**：工作區 clean、與遠端同步（即已推送）。當時所記之兩筆對位 hash 為 `eeba341d`（`SwiftExtension // Swift 5.10 compilability.`）與 `121ef1a3`（`LibVanguard // Swift 5.10 compilability.`）、其前為 `4125707e`（`LibVanguard // Sync licenses from the dedicated repo.`）——**該組 hash 其後續經 rebase 而失效**（見 §13.5）；**現行對位見 §一 與本檔末之〈現行 hash 對照〉**。

- **byte-sync 實測**（`vChewing-LibVanguard` ↔ `vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard/`）：
  - `Sources/`：`diff -rq` **零差異**
  - `Deps/`：`diff -rq` **零差異**（僅 `Build/Products/` 下的 framework 符號連結造成 `Directory loop detected` 噪音，非內容差異）
  - `Package.swift`：`cmp` **逐位元組相同**
  - `Package@swift-5.10.swift`：`cmp` **逐位元組相同**
  - **（末次修訂補測）** `Tests/` 與 6.0／6.1／6.2／6.3 四份版本 manifest ＋ `makefile`：亦**零差異**

- **連帶效果**：§十一 第 6 項（「`Sources/` 自此不再逐位元組相同」）**已消解**——P214 所定的兩倉同源性在本 phase 結束時**恢復並維持**。§13.3 的待整理清單亦全部結清。

- 仍未動作者：本檔 §十一 第 1～5 項（Tekkon 的 `sharedCache`、2 個 5.10 warning、唯一那處 `#if`、`withFileHandleQueue*` 的退役時機、legacy 的 10.9 疑點）。**其中 §十一 第 2 項之 2 個 warning 與第 3 項之單一 `#if`，已於 §13.6.5 之封堵令執行後成為「既有狀態、事主已裁定保留」**。
- 本 phase 的正式完工登記**已於同日完成**（`vChewing-DevLogs` 之 `942557d`（`P216.`）；見檔頭之狀態行）。

### 13.5 追加（同日稍後）：事主自寫的 `savePOMData` actor 修補，已 rebase 進早期記錄

§13.2 所記「未 commit 的 3 個檔」之外，事主另有一筆自寫修補，且**未留在當下、已 rebase 進 macOS 倉的早期記錄**：

- **`a5384aeb LXMgr // Call \`savePOMData\` on MainActor.`**（2026-09-15 13:45:53，1 檔 +5/−1）：

  ```diff
  -          targetLexicons.forEach { $0.savePOMData() }
  +          asyncOnMain {
  +            targetLexicons.forEach {
  +              $0.savePOMData()
  +            }
  +          }
  ```

  病灶：`savePOMData` 會在**錯誤的 actor** 上被呼叫；改以 `asyncOnMain` 兜上，與本 phase §六／§八 的調度方針一致。

- 該筆現位於 macOS 倉歷史的較早處，而非 HEAD 附近。**這正是「hash 記載會隨 amend／rebase 失效」的又一實例**：§13.4 所記的 macOS 兩筆 hash 於此輪 rebase 後再度失效——當時記為 `d0ff1138`（`SwiftExtension // Swift 5.10 compilability.`）與 `df09641e`（`LibVanguard // Swift 5.10 compilability.`），licenses 那筆為 `35922297`。**該組值其後亦失效**；**現行對位見 §一 與本檔末之〈現行 hash 對照〉**。

### 13.6 Swift 6.2／6.3 的 conformance-isolation 問題與封堵令（**已於 2026-09-15 執行完畢**）

> **【執行狀態，2026-09-15 深夜補記】** 本節原標「備忘（待 Swift 6.4 正式問世後執行）」。**Swift 6.4.0 已於 2026-09-14 正式發佈**，封堵令遂於 **2026-09-15 執行完畢**（採 §13.6.4 之**方案 B**）：五個 `Package.swift` 抬到 6.4 ＋ 兩倉各鋪 6.2／6.3 封堵檔 ＋ 三系統 CI 之 toolchain pin 抬到 ≥6.4。**故本節以下之 13.6.1～13.6.4 為「動機與實測」的歷史紀錄、13.6.5～13.6.9 為執行與其後之核對**；13.6.6 之清單即實際落地的清單。**執行者為前一輪 harness（Kimi Code CLI，模型 DeepSeek-v4-flash）**。歸屬：LibVanguard 側屬 P216、倉根 meta-manifest ＋ 三條 CI pin 屬 P217（見 §13.6.5 之註記與 `Reqs_0211-0220.md` 之〈P216／P217 之分水嶺〉）。

**本節為事主 2026-09-15 交辦之備忘。**下列 §13.6.3／§13.6.4 的實測**一律在 `/tmp` 副本上做、未動任何倉**（副本：`/tmp/p216/Base`、`Repro633`、`Repro633Fix`、`VariantA`、`VariantB`、`SubA`、`SubB`）；本檔以外的文書改動只有 `Phase217_SOP.md`（見 §13.6.7）。

#### 13.6.1 事主原話（權威）

**目標**：

> 過幾天等 Swift 6.4 正式問世之後將 Swift 6.2 與 6.3 加入封堵清單、Swift 6.x 的工具鏈僅支援 Swift 6.4+。

**原因**：

> default isolation at MainActor 的倉庫裡面寫的 protocol 都自帶 MainActor。但 Swift 6.2 與 6.3 在一個已經 default isolation at MainActor 的下游倉庫內讓某個 class 遵循這種 protocol 的時候會被要求明文寫 `@MainActor`。錯誤報告如下（三個系統的 CI 全趴窩，都是 Swift 6.3 的）：

**性價比結論**：

> 眼下解決這個 CI 錯誤的話需要付出空前的成本、可能會導致對 Swift 5.10 的相容工作徹底失敗。所以只能放棄。

**測試授權**：「你可以用本機的 Swift 6.3.3 Open Source Toolchain 對著 LibVanguard 倉庫測試。」

#### 13.6.2 CI 錯誤原文（照引，含行號）

```text
/Users/runner/work/vChewing-LibVanguard/vChewing-LibVanguard/Sources/LibVanguard/Session/InputSession.swift:9:20: error: conformance of 'InputSession' to protocol 'SessionCoreProtocol' crosses into main actor-isolated code and can cause data races [#ConformanceIsolation]
  7 | // MARK: - InputSession
  8 |
  9 | public final class InputSession: SessionProtocol, Sendable {
    |                    |- error: conformance of 'InputSession' to protocol 'SessionCoreProtocol' crosses into main actor-isolated code and can cause data races [#ConformanceIsolation]
    |                    |- note: isolate this conformance to the main actor with '@MainActor'
    |                    `- note: conformance depends on main actor-isolated conformance of 'InputSession' to protocol 'CtlCandidateDelegate'
 10 |   // MARK: Lifecycle
 11 |
```

#### 13.6.3 本輪實測之一：重現與中招清單（6.3.3）

**環境配對（本輪新踩到的坑，與 §三 同類，記下以免重蹈）**：本機 6.3.3 開源 toolchain 的預設 target 是 `arm64-apple-macosx28.0`；**若直接配 Xcode 27 的 `MacOSX27.0.sdk`，會得到 739 個錯誤、其中 592 個是 `unknown argument: '-target-arch-variant'`**，其餘全是 Foundation 未建成而生的級聯（`cannot find type 'UUID'／'Data'／'URL' in scope` 等）——**沒有一條指向真正病灶**。病灶在 SDK 27 的 `.swiftinterface`：其 `swift-module-flags` 帶了只有 6.4 編譯器才認得的 `-target-arch-variant arm64e.x1`（例：`MacOSX27.0.sdk/usr/lib/swift/NaturalLanguage.swiftmodule/arm64e-apple-macos.swiftinterface`）。**正解是 macOS 26.x 的 SDK**——本輪用本機 CommandLineTools 的 `/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk`；這也正是 6.3 系 toolchain 的年代配對（本倉 macOS CI 現釘的 `xcode-version: "26.6"` 即屬該代）。

```bash
# 重現（在 /tmp 副本內；scratch 亦在 /tmp，不動倉內 .build）
SDKROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk \
  ~/Library/Developer/Toolchains/swift-6.3.3-RELEASE.xctoolchain/usr/bin/swift \
  build --build-tests --scratch-path /tmp/p216/scratch633-full
```

| 項目 | 實測結果 |
|---|---|
| `swift build --build-tests` | **rc=1**；主診斷 **5 段**（1 段出自 `Emitting module LibVanguard`、另 4 段出自檔案編譯階段——同一個 conformance 被重報），含 `error:` 的行**合計 11** |
| `swift test --no-parallel`（CI 的實際指令） | **rc=1**，同一失敗點、同一診斷 |
| **中招清單** | ① `InputSession`（`Sources/LibVanguard/Session/InputSession.swift:9:20`，其 conformance 對 `SessionCoreProtocol` 報錯；note 鏈的第一條指向 `CtlCandidateDelegate`）——**首輪只露這一個**；② `InputHandler`（`Sources/LibVanguard/InputHandler/InputHandler.swift:10:34`，conformance 對 `InputHandlerProtocol`）——**把①依編譯器指示補上 `@MainActor` 之後才會露出來**（其 note 鏈為 `conformance depends on main actor-isolated conformance of 'InputSession' to protocol 'SessionCoreProtocol'`）。①②皆補上後，**全倉（含全部測試靶）rc=0、0 error**。⇒ **中招者恰為這兩個 conformance，再無第三個** |
| 未中招者 | 其餘模組與靶**皆未報同類診斷**：`Shared`／`LexiconAssembly`／`BrailleSputnik`／`BPMFVS`／`Tekkon`／`Homa`／`ResourceLocator`／`TrieKit`／`LXAssemblyMaterials4Tests`／`HomaSharedTestComponents` 在 LibVanguard 之前就已編完（其中不依賴 LibVanguard 的六個測試靶另以 `--target` 逐一驗過，rc=0）；`vChewingSharedCLI` 與依賴 LibVanguard 的三個測試靶則在「②之修補版」的全倉 rc=0 建置中一併編過 |
| 子套件 `Deps/VanguardSwiftExtension` | 單獨 `swift build --build-tests` **rc=0、0 診斷**（子套件**不中招**） |
| 6.4 對照（預設 toolchain） | `swift build --build-tests` **rc=0、0 error、0 warning**（`Build complete!`）；`swift test --no-parallel` **rc=0、9 套件 535 項全綠**（與 §一 所記「動工前同數」一致） |
| 5.10 對「編譯器建議的修法」的反應 | `final class C: @MainActor P {}` → `unknown attribute 'MainActor'` ＋ `inheritance from non-protocol, non-class type 'any P'`（同 §五）。**編譯器要的那兩行是 6.2+ 專屬語法，5.10 側不可能同形** |

**未實測項與疑點（本輪據實記載）**：

- **Swift 6.2 一側未在本機實測**：本機只有 5.10.1／6.3.3 兩套開源 toolchain（另加 Xcode 27 的 6.4 開發版），**沒有 6.2**，故「6.2 也中同一招」一事**未經本機 toolchain 驗證**。事主的封堵清單同時涵蓋 6.2，本檔照引其原話；6.3 一側已如上實測。⇒ **同日稍後已由 CI 日誌補足**（§13.6.8 第 3 列）。
- **疑點（CI 的實際 toolchain 版本）**：本倉 WinNT workflow 現釘 `swift-version: swift-6.2-release`，與「三個系統的 CI 全趴窩，都是 Swift 6.3 的」在字面上不一致（macOS＝`xcode-version: "26.6"`、Linux＝`SwiftyLab/setup-swift@latest`，這兩者才是 6.3 系）。⇒ **已結清**：WinNT 該 job 確實跑 `swift-6.2-RELEASE`，**且 6.2 也中同一招**（§13.6.8）。

**與 §七 的關係**：6.3 索取 `@MainActor` 的兩個位置，**正是 §七 所記那 3 行手術中被撤掉的位置**（`InputSession` 與 `InputHandler` 的 conformance）。本輪試過的兩條回頭路各自撞牆：**加回去**（conformance 隔離到 MainActor）是 6.2+ 專屬語法、5.10 拒收（上表末列）；**改在型別上新增 `@MainActor`** 則違反 §七 的硬約束（會殺死 ≤10.14 相容性）。⇒ 在「同一份 `Sources/` 要同時服務 5.10 與 6.x」且「不得新增 `@MainActor`」的雙重前提下，**本輪未找到兩側通吃的第三種寫法**——這正是 §13.6.1 所稱「空前成本」的實質（並非不願修，而是那條路與 5.10 相容互斥）。

#### 13.6.4 本輪實測之二：封堵方案 A／B

規則前提（§二 已釘死）：**於 `Package*.swift` 全集中，取「檔內宣告的 tools version ≤ toolchain 版本」者之最高者；同版時 `Package.swift` 勝出。**

**方案 A（`Package.swift` 維持 6.2，另加 `Package@swift-6.2.swift` 與 `Package@swift-6.3.swift` 兩份 `#error` 封堵檔）⇒ ❌ 不成立。**

| 腿 | 結果 |
|---|---|
| 6.3.3 | **被攔下 ✔**：SwiftPM 取 `Package@swift-6.3.swift`（其 manifest 編譯命令含 `"-package-description-version", "6.3.0", "…/Package@swift-6.3.swift"`），`#error` 於 manifest 編譯期中止，rc=1 |
| **6.4（承重點）** | **也被攔下 ✘**：入選者仍是**同一份 `Package@swift-6.3.swift`**（6.3 ≤ 6.4，且 6.3 ＞ 6.2），`Package.swift` 根本沒被載入 |

**機理（本輪最要緊的一條）**：**「同版時 `Package.swift` 勝出」只管同版**。一旦存在宣告值更高的封堵檔（6.3），它對 6.4 toolchain 而言就是「不高於自己的最高者」，**穩贏 `Package.swift` 的 6.2**。⇒ 以「在 6.2／6.3 上加封堵檔、其餘不動」的直覺做法，**會把 6.4 一起封死**（含現行的 C1 線：Xcode 27 預設 toolchain 將無法建置本倉）。

**方案 B（`Package.swift` 的宣告值提到 6.4 ＋ 6.2／6.3 兩份封堵檔）⇒ ✅ 成立。**

| 腿 | 結果 |
|---|---|
| 6.3.3 | **被攔下 ✔**（取 `Package@swift-6.3.swift`） |
| 6.4 | **取 `Package.swift` ✔**（`swift package dump-package -v` 只編譯 `Package.swift`）；`swift build --build-tests` **rc=0、`Build complete!`（26.90 秒）** |
| 子套件同構同驗 | A 形 → 6.4 **被攔 ✘**；B 形 → 6.4 **rc=0、`Build complete!`（5.74 秒）** ✔ |

**B 的代價（須記明）**：

1. **6.2 側 manifest 就此不存在**：本方案等於落定「Swift 6.x 僅支援 6.4+」。5.10 側完全不受影響（`Package@swift-5.10.swift` 一字不動）。
2. **三系統 CI 都要同時換 toolchain，否則封堵令一落地 CI 立刻全趴**：本倉 macOS workflow 現釘 `xcode-version: "26.6"`（＝Swift 6.3.3）、WinNT workflow 釘 `swift-version: swift-6.2-release`、Linux 走 `SwiftyLab/setup-swift@latest`（版本浮動）。**封堵令與 CI 換版必須同一批落地**——這正是「須待 Swift 6.4 正式問世」的實質理由（屆時才有可釘的正式版 Xcode／`swift-6.4-release`）。
3. **消費端**：`vChewing-macOS` 以本地路徑相依聚合體與子套件（manifest 屬 byte-sync 範圍，實測 4 份 md5 全同），故其 CI 亦須 ≥ 6.4。

#### 13.6.5 執行條件與執行結果

**執行條件（動工前原記）**：

- **須待 Swift 6.4 正式問世。** 動工前本倉 `Package.swift` 宣告 6.2、本機預設 toolchain 為 `Apple Swift version 6.4` 之**開發版**，時機未到。
- 動工時採**方案 B**。

**執行結果（2026-09-15，已完成）**：五個 `Package.swift`（兩倉之聚合體、聚合體之 `Deps/VanguardSwiftExtension`、`vChewing-macOS` 倉根 meta-manifest）之宣告值已抬到 6.4，並在上述各處各鋪 `Package@swift-6.2.swift`／`Package@swift-6.3.swift` 兩份封堵檔；三系統 CI 的 toolchain pin 已同批抬到 ≥6.4。本機驗收：6.3.3 被 `Package@swift-6.3.swift` 的 `#error` 攔下（rc=1）、6.4.0 側 `swift build` rc=0 且 `swift test --no-parallel` **535 項 0 失敗**。
  - **現行 commit 對位**：`vChewing-LibVanguard` = `6609f5b`（`SPM // Block Swift 6.2 and 6.3 toolchains.`）、`vChewing-macOS` = `588d1b8e`（`Repo // Block Swift 6.2 and 6.3 toolchains.`）。（本項執行當時所記之 hash `95a609c`／`d88a423c` 已經 rebase 而不可達；見 §一 之註記。）
  - **歸屬（依事主 2026-09-15 劃定之分水嶺）**：本項於 **LibVanguard 側**（兩倉之聚合體與子套件之封堵檔與 manifest 抬版）屬 **P216**；其**倉根 meta-manifest ＋ 三條 CI workflow 之 toolchain pin**（CI 安全閘門：不作此改則 CI 會被自家封堵檔擋死）屬 **P217**。分記之正本見 `Reqs4LLM/Archive_P201-P300/Reqs_0211-0220.md` 之〈P216／P217 之分水嶺〉。
  - **執行後之複驗（2026-09-15 深夜）**：現行封堵檔確實攔下 6.3.3（實測報 `SettingsUI 不支援 Swift 6.2 / 6.3 toolchain：Swift 6.x 僅支援 6.4+`）；6.4 側倉根 `swift build` rc=0、聚合體 `swift test --no-parallel` 535 項 0 失敗；兩倉之六份 manifest 逐位元組相同。

#### 13.6.6 要動的清單（兩倉同步；manifest 屬兩倉 byte-sync 範圍）【**已按此清單落地**】

| 倉／套件 | 檔案 | 動作 |
|---|---|---|
| `vChewing-LibVanguard`（聚合體，根） | `Package.swift` | 宣告值 `6.2` → **`6.4`** |
| 同上 | `Package@swift-6.2.swift`、`Package@swift-6.3.swift` | **新增**（`import PackageDescription` ＋ `#error(…)` 封堵檔，寫法照 `Package@swift-6.0.swift`） |
| `vChewing-LibVanguard/Deps/VanguardSwiftExtension`（獨立 package） | `Package.swift` ＋ 同上兩份 | 同上（子套件有自己的一組 manifest，須各自鋪） |
| `vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard` 及其 `Deps/VanguardSwiftExtension` | 同上 6 檔 | **逐位元組同步**（I2 範圍） |
| CI workflows | `vChewing-LibVanguard/.github/workflows/{test_darwin,test_winnt,test_ubuntu}_LibVanguard.yml`；`vChewing-macOS/.github/workflows/{build_darwin_SPMTestsAndPackage,test_winnt_LibVanguard,test_ubuntu_LibVanguard}.yml` | toolchain 抬到 6.4 **正式版**（Xcode 27.x ／ `swift-6.4-release` ／ setup-swift 釘選版本） |

**不動**：`Package@swift-6.0.swift`、`Package@swift-6.1.swift`（原封堵檔續留）、`Package@swift-5.10.swift`、`makefile`、`Sources/`（本次不動任何原始碼）。

#### 13.6.7 連帶改動

- `vChewing-DevLogs/Research/Phase217_SOP.md`：§二（環境配對補「Intel Mac 的 Xcode 天花板」環境認知一句）、§三（封堵檔一節補未來擴充之提示）、§十二（新增 R22）、§十四（新增 N3）。改動內容見該檔。

#### 13.6.8 三條 CI 失敗的逐條核對（2026-09-15，`gh` 抓取）

以 `gh` CLI（本機 v2.100.0，已認證）抓取事主交付的三條 job 日誌逐條核對。**三者同為一次 push 所觸發**：`2bef551 LibVanguard // Swift 5.10 compilability.`（2026-09-15 12:54:57 +0800，即 §13.1 表列的第三筆），三條 run 的 `headSha` 皆為 `2bef551d43b6e9d81d2616b41b2cf1cd0a0ec1e7`、`startedAt` 皆為 `2026-09-15T05:46:19Z`。

| # | 系統（job｜runner｜workflow） | 實際工具鏈 | 失敗指令 | 主診斷（`error:` 行） | 步驟 rc | 連結 |
|---|---|---|---|---|---|---|
| 1 | **Linux**｜`test-linux-LibVanguard`｜`ubuntu-latest`｜`unit-test-LibVanguard-linux` | **Swift 6.3.3**（`swift-6.3.3-RELEASE`；`/opt/hostedtoolcache/swift-6.3.3-RELEASE-ubuntu2404/6.3.3/x86_64/`；經 `SwiftyLab/setup-swift@latest`） | `swift --version && swift test --no-parallel` | `/home/runner/work/…/Sources/LibVanguard/Session/InputSession.swift:9:20: conformance of 'InputSession' to protocol 'SessionCoreProtocol' crosses into main actor-isolated code and can cause data races [#ConformanceIsolation]`（**10 段重報**） | **1** | https://github.com/vChewing/vChewing-LibVanguard/actions/runs/34934096396/job/104268203553 |
| 2 | **macOS**｜`test-macOS-LibVanguard`｜`macos-26`｜`unit-test-LibVanguard-macOS` | **Apple Swift 6.3.3**（`swiftlang-6.3.3.1.3 clang-2100.1.1.101`）；Xcode 由 `maxim-lobanov/setup-xcode@v1.7.0` 切到 **26.6.0（17F113）** | 同上 | `/Users/runner/work/…/Sources/LibVanguard/Session/InputSession.swift:9:20: …`（**13 段重報**） | **1** | https://github.com/vChewing/vChewing-LibVanguard/actions/runs/34934096352/job/104268203072 |
| 3 | **WinNT**｜`test-winnt-LibVanguard`｜`windows-latest`｜`unit-test-LibVanguard-WinNT` | **Swift 6.2**（`swift-6.2-RELEASE`；`compnerd/gha-setup-swift`） | `swift --version` ＋ `swift test --no-parallel` | `D:\a\vChewing-LibVanguard\vChewing-LibVanguard\Sources\LibVanguard\Session\InputSession.swift:9:20: …`（**10 段重報**） | **1** | https://github.com/vChewing/vChewing-LibVanguard/actions/runs/34934096340/job/104268203258 |

**判定：三條為同一病灶（✅）。** 三者皆止於同一個 conformance、同一個座標 `:9:20`、同一串 note 鏈（`isolate this conformance to the main actor with '@MainActor'` ＋ `conformance depends on main actor-isolated conformance of 'InputSession' to protocol 'CtlCandidateDelegate'`），且**三條日誌都沒有出現 `InputHandler`**（與 §13.6.3 本機所見的「①先露、②被遮蔽」一致）；三條的失敗步驟 exit code 均為 **1**，日誌尾端均收在 `error: fatalError`。**沒有任何一條是別的病。**

（重報段數 10／13／10 之別，只是各平台 SwiftPM 對同一個 conformance 的重複回報次數、以及 `swift test` 會多編測試靶所致；主體仍是一個 conformance。以 Linux 為例：`error:` 行共 22 ＝ 10 段 ×2 ＋ `emit-module` 1 ＋ `fatalError` 1。）

**與 §13.6.3 疑點的對帳（結清，並局部修正原判）**：

- §13.6.3 原記的疑點——「WinNT 釘 `swift-6.2-release`，與事主所說『三個系統都是 6.3』字面不一致」——**以日誌為準：WinNT 該 job 跑的確實是 `swift-6.2-RELEASE`**，事主原話在這一點上不精確（另兩條確為 6.3.3）。
- 但**病灶逐字相同**。⇒ **「Swift 6.2 也中同一招」由此取得 CI 級證據**（不再只是事主轉述）：把 6.2 與 6.3 一併納入封堵清單是對的；反之若只封 6.3、放 6.2 過，WinNT 會繼續紅。
- 附帶確認：**macOS CI 的 Xcode 26.6 自帶的就是 Swift 6.3.3**（`swiftlang-6.3.3.1.3`），與本機 6.3.3 開源 toolchain 同版；Linux 的 `SwiftyLab/setup-swift@latest` 當日解析到 **6.3.3**。
- 仍未由本機 toolchain 驗證者：**6.2 的本機重現**（本機無 6.2 toolchain）。此項以 CI 日誌替代，**不再列為疑點**。

#### 13.6.9 Intel Mac 的 Xcode 天花板與「可指定系統預設 Toolchain」（事主原話）

**事主原話（2026-09-15）**：

> 這也對 macOS 倉庫的 Xcode 建置環境提出要求：**Intel Mac 最終可用 Xcode 版本是 Xcode 26.x，但可以安裝 Swift 6.4+ Open Source Toolchain。目前暫時不需要刻意做這個相容措施，因為 Xcode 允許指定系統預設的 Toolchain。**

三個要點：

1. **硬體側的天花板**：Intel Mac 的 Xcode 上限＝**Xcode 26.x**（即 6.3 系工具鏈，見 §13.6.8 第 2 列：Xcode 26.6 自帶 `swiftlang-6.3.3.1.3`）；要吃到 **Swift 6.4+**，只能靠 **Open Source Toolchain**（swift.org 的 `.xctoolchain`，即本機 `~/Library/Developer/Toolchains/swift-6.3.3-RELEASE.xctoolchain` 這種形態）。
2. **目前不刻意做此相容措施**：理由＝**Xcode 允許指定系統預設的 Toolchain**——建置端（含 CI）可讓 Xcode 走 Open Source Toolchain，不必遷就 Xcode 自帶的版本。故「Intel Mac ＋ Xcode 26.x」**不構成封堵令的破口**。
3. **與方案 B 的關係（此條是其關鍵前提）**：§13.6.4 的**方案 B**（`Package.swift` 提到 6.4 ＋ 6.2／6.3 各設封堵檔）在 **Apple 單側（CI／Intel Mac）之所以可行，正是靠上面這一條**——若不允許指定系統預設 Toolchain，則「Xcode 上限 26.x」的 Intel Mac 會**被自己的封堵令永遠擋在門外**（它的 Xcode 給不出 6.4）。（此條於動工前為「須先確認」；**封堵令已於 2026-09-15 落地並以 CI 實跑通過**，故該前提在本輪之 CI 環境已成立。）

**未實測項**：本輪未在 Intel Mac 上實跑（本機為 Apple Silicon），故上述三點皆按事主原話記錄；「Xcode 允許指定系統預設的 Toolchain」的**具體操作形態本輪未查核**（故不在此臆列旗標／設定名）。

---

## 十四、單元測試結構之整肅（`45bb0ac`，2026-09-15 深夜追加）

**來由**：本 phase 之手術把「載入使用者資料」的路徑改為非同步之後，測試出現**時過時不過**的抖動——同一測試在不同次執行間時紅時綠，失敗訊息皆屬「handler 狀態殘留」型（`Early commission is tearing …`／`Commissions missing prefix …`／`mixedAlphanumericalBuffer` 該有值卻是空字串／`narrateCallCount` 該 ≥1 卻是 0）。根因是**測試彼此踩踏行程內全域狀態**（`LXFacade` 的 `factoryTrie`／`lxCassette`、`PrefMgr.shared`、`SessionHost.shared`）。**16 檔、+490/−412**，三件事：

1. **`LibVanguardTests` 靶收進單一 serialized 根**：新增 `LibVanguardTests_Root.swift`（`@Suite("LibVanguardTestsRoot", .serialized)`），把原先四個游離的頂層 suite（`InputHandlerTests`／`FuriousTypingSegmentorTests`／`ResourceProvisionTests`／`RomanNumeralTests`）改寫成巢狀宣告，各 `Cases*.swift` 之 `extension InputHandlerTests` 隨之改為完整路徑。整靶自此落入**同一 serialized 子樹**。`BrailleSputnikTests` 靶原缺 `.serialized`，一併補上。
2. **`test_IH400_MixedAlnumKanjiInputTest_Izanami` 補上同步載入**：它是全靶唯一跑遍整張注音表、大量觸及 userdata 卻**未**把 `asyncLoadingUserData` 壓成 `false` 的測試（其餘九支磁帶測試皆有）。
3. **`HomaTests` 之堆積洩漏哨兵改為多次獨立取樣**：`RepeatedRecompositionAllocConvergence` 量的是**全域 malloc 保留區**，其基線受同靶先前測試影響，單次取樣必出現與洩漏無關的瞬態擴張（門檻 4 MB）。改為**獨立取樣至多三次、任一次通過即算通過**——真洩漏會讓每次都超標，故此法只濾噪音、**不放寬門檻**。

**兩道防線的層級（實測釘死，勿混用）**：

| 手段 | 層級 | 保證 |
|---|---|---|
| `swift test --no-parallel` | CLI | 「同一時間只有一個測試函式在跑」 |
| `@Suite(…, .serialized)` | 型別 | 「該 suite 子樹內絕不並行」 |

**缺一不可**：實測即使根 suite 已就位，**故意不加 `--no-parallel` 仍會抖**。故結構是保險、旗標是開關——兩倉所有測試入口皆已帶 `--no-parallel`（兩倉 CI 共 6 條 workflow、逐包 `makefile`、倉根 `Makefile`）。**驗證**：兩倉各以 `swift test --no-parallel` **連跑 5 次全綠**（535 項、0 issue）。

---

## 附錄：現行 hash 對照（末次修訂時之實測值）

> 本表為**本檔唯一之現行 hash 正本**；§一 之表與本表一致。**一切 hash 都會隨 amend 失效——判準請以「訊息 ＋ 小節主題」為準。**

| 訊息 | `vChewing-LibVanguard` | `vChewing-macOS`（鏡像／對位） |
|---|---|---|
| `LibVanguard // Dylibify VanguardSwiftExtension.` | `1424601` | `6fff46c1` |
| `SPM // Starting working on Swift 5.10 compilability.` | `a8d5fde` | 見 `48ff88ef` 之前置批次 |
| `SwiftExtension // Swift 5.10 compilability.` | `28d491f` | `89af456f` |
| `LibVanguard // Swift 5.10 compilability.` | `2a4466d` | `d920059e` |
| `LibVanguard // Patch unit test issues.` | `45bb0ac` | `cad648e3`（＝P216／P217 之分水嶺） |
| `SPM // Block Swift 6.2 and 6.3 toolchains.` | `6609f5b` | `588d1b8e`（其 macOS 自身側屬 P217） |

## 修訂紀錄

- **2026-09-15（末次修訂，事主授權）**：修掉本檔因多輪 rebase 與追加而生的內部矛盾——
  1. 檔頭狀態由「**P216 尚未完工**」改為「**已完工**」（完工登記已於同日完成；見 §13.4）。
  2. 標題之「Swift 6.2」改為「**Swift 6.4+**」（封堵令已落地，6.2／6.3 為封堵對象、非支援對象）。
  3. §一 由「三個 commit／rebase 前之統計」改為「**現行五筆／現行實測統計**」，並補上第 4、5 筆；刪去層層疊加的舊 hash 對照表，改為一句「舊值皆不可達」。
  4. §13.1 改為**純歷史沿革**（明示「現行」欄亦已失效），並指向 §一 與附錄。
  5. §13.2／§13.3 各加【已結清】標記（其所記之三檔皆已入庫、I2 已零差異）。
  6. §13.4 之兩筆 macOS hash 標明已失效；byte-sync 補測 `Tests/` 與四份版本 manifest ＋ `makefile`。
  7. §13.6 標題與導言改為「**已執行完畢**」；§13.6.5 由「執行條件」改為「執行條件與執行結果」；§13.6.6 標明「已按此清單落地」；§13.6.9 之「動工前須先確認」改為已成立。
  8. 新增 §十四（單元測試結構之整肅）與本附錄（現行 hash 對照）。
- **2026-09-15（P217 收工後之文書回填）**：**§十一 之口徑重整**——該表原以「殘留與未決」混列七項，看不出哪些已由事主裁定、哪些仍開著。今改用三種狀態標籤（**【已裁定保留】／【已結清】／【事實層未解】**），逐項回填 P217 收工時之實測與落點；**收工時判定：已裁定保留 4 項（第 1～4）、已結清 2 項（第 6、7）、事實層未解 1 項（第 5）——不再有任何「待事主裁定」項**。其中第 4 項之「待退役」係**被 P217 的事主 Q06 取代**（改為「不用退役」並定其三條紀律），第 5 項則被 P217 明列為**下一 phase** 之事（N1／N2）。
- **2026-09-16（三倉 rebase 後之 hash 複測）**：本檔所引之「現行」hash 全數複測更新——`vChewing-LibVanguard` 之第 4、5 筆改為 `45bb0ac`／`6609f5b`，`vChewing-macOS` 之對位改為 `cad648e3`／`588d1b8e`／`48ff88ef`，`vChewing-DevLogs` 之兩筆完工登記改為 `942557d`（`P216.`）／`4429504`（`P217.`）。**§一 之表與本附錄同步更新**；依 §十二 R12，判準仍以「訊息 ＋ 小節主題」為準。
