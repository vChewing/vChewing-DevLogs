# Phase 215（前置研究）：把 `SwiftExtension` 自聚合體析出為獨立的動態載體

- 調查日期：2026-09-14。
- 狀態：**施工前研究**（本檔為本 phase 之研究交付物）。研究結論直接改寫了本 phase 的路線選擇：原定「在聚合體內新增一個 dynamic product、再由聚合體內部以 product 形式取用之」經實測**不可表達**，故改用本檔 §五 之**方案 1**（把 `SwiftExtension` 析出為獨立套件、由該套件出貨 dynamic product `VanguardSwiftExtension`）。
- 方法：以五支**隔離探針**（玩具套件，位於 `_MainWorkspace/tmp/p215Probe{A,C,D,E,G}`，**全程未動任何生產碼**）把 SwiftPM 的能力邊界釘死；再以唯讀盤點量測依賴網路與公開介面。
- 行號註記：本文 `檔案:行號` 為 2026-09-14 之快照（`vChewing-macOS` at `470d8558`，detached 4.7.4 狀態下的量測另註明）。

---

## 一、問題與來歷：這是 P210 併包所引入的 regression

### 1.1 現狀

`vChewingInstaller.app`（App-based installer）目前**自帶一份整條打字閉包**：

| 管線 | installer 的同捆內容 |
|---|---|
| Xcode | `Contents/Frameworks/Vanguard.framework` |
| makefile（`BundleApps` 插件） | `Contents/Frameworks/libVanguard.dylib`（6.8 MB，閉包全靜態併入） |

而 installer 的自身原始碼從整條閉包裡**只用到 `SwiftExtension` 一個模組**（實查：`AppKit/VwrAppInstaller4Cocoa.swift:7`、`InstallerShared.swift:7`、`SwiftUI/VwrAppInstaller4SwiftUI.swift:9` 三處 `import SwiftExtension`；實際取用符號僅 `String.i18n` 與 `Process.consoleLog`／`realHomeDir`／`isAppleSilicon` 等少數擴充）。

### 1.2 來歷：tag 4.7.4 時並非如此

於 detached `4.7.4`（`ccade0c7`）之 manifest 實查：

```
vChewing_InstallerAssembly4Darwin → IMKUtils + SwiftExtension + OSFrameworkImpl
vChewing_OSFrameworkImpl         → SwiftExtension（獨立套件 vChewing_SwiftExtension）
vChewing_IMKUtils                → SwiftExtension（同上）
```

**4.7.4 的 installer 完全沒有依賴聚合體**。是 P210〈追加檢證之四〉把 `vChewing_SwiftExtension` 這個獨立套件**併入**`vChewing_OSNeutralAssembly` 之後，上述三個消費端被迫把

```swift
.product(name: "SwiftExtension", package: "vChewing_SwiftExtension")
```

改寫為聚合體的產品名（P214 再定名為 `Vanguard`），installer 才自此背上整條閉包。**本 phase 的實質＝把 4.7.4 的形狀還原到併包後的佈局裡。**

---

## 二、依賴網路盤點

### 2.1 要斷的是三條邊，不是一條

installer 之所以摸到 `Vanguard`，有三條依賴邊，任一條不斷，`Vanguard` 都會遞移進入 installer 的 product 圖：

| # | 邊 | 現行宣告 |
|---|---|---|
| 1 | `vChewing_InstallerAssembly4Darwin` → `Vanguard` | `Packages/vChewing_InstallerAssembly4Darwin/Package.swift` |
| 2 | `vChewing_OSFrameworkImpl` → `Vanguard` | `Packages/vChewing_OSFrameworkImpl/Package.swift:29` |
| 3 | `vChewing_IMKUtils` → `Vanguard` | `Packages/vChewing_IMKUtils/Package.swift:43` |

### 2.2 三條邊純粹只為 `SwiftExtension` 而存在

實查兩個中介套件的 `Sources/`：

- `vChewing_OSFrameworkImpl/Sources/OSFrameworkImpl/OSFrameworkImpl.swift:5` 為 `@_exported import SwiftExtension`；另 `AppKitImpl/{NSView,NSWindowController,NSWindowPositioner}.swift` 各一行 `import SwiftExtension`。
- `vChewing_IMKUtils/Sources/IMKUtils/IMKHelper.swift:6` 為 `import SwiftExtension`。
- 對 `Vanguard`／`Homa`／`Tekkon`／`Shared`／`LXAssembly`／`TrieKit`／`BrailleSputnik`／`BPMFVS`／`ResourceLocator` 的 `import`：**兩套件皆零命中**（連 `import Vanguard` 本身亦零命中——它們是經由 `.product` 宣告取得該模組的，原始碼從未指名它）。

### 2.3 `SwiftExtension` 之實際 API 使用面（唯讀掃描）

| API | `OSFrameworkImpl` | `IMKUtils` | `InstallerAssembly4Darwin` |
|---|---|---|---|
| `ArrayBuilder`（`@resultBuilder enum`，型別） | **7** | — | — |
| `AppProperty`（property wrapper，型別，含外部 conformance） | 4 | — | — |
| `NSMutex`（型別） | 5 | — | — |
| `Process.consoleLog` | 4 | 7 | 6 |
| `String.i18n`／`.i18n(loc:)` | 8 | 2 | **50** |
| `Process.isAppleSilicon` | 3 | — | — |
| `Process.totalMemoryGiB` | 1 | — | — |
| `CGRect.zeroValue` | 1 | — | — |
| `LatinKeyboardMappings`（型別） | — | 1 | — |

（`NSApplication.isAppleSilicon` 一項經追查**不屬** `SwiftExtension`：它宣告於 `OSFrameworkImpl/AppKitImpl/AppKitImpl_Misc.swift:464`，內部才去叫 `SwiftExtension` 的 `Process.isAppleSilicon`。）

**結論**：使用面已涵蓋 `SwiftExtension` 的核心型別與主要擴充，故「窄載體」不可能比「整個 `SwiftExtension` target」更窄；但它相對整條打字閉包（`Homa`／`Tekkon`／`LexiconAssembly`／`Shared`／`BPMFVS`／`ResourceLocator`／`TrieKit`）仍是極小的一片。

### 2.4 `OSFrameworkImpl` 是 installer 的 AppKit DSL 來源，而該 DSL 踩在 `SwiftExtension` 的型別上

`AppKit/VwrAppInstaller4Cocoa.swift:10`、`SwiftUI/VwrAppInstaller4SwiftUI.swift:12` 皆 `import OSFrameworkImpl`；取用其 DSL（`buildSection`／`stack`／`makeSimpleConstraint`／`makeNSLabel`／`boxed`／`pinEdges`／`NSFileDragRetrieverButton`／`NSLabelView`／`UILayoutOrientation` 等）。**故 installer 無法擺脫 `OSFrameworkImpl`**，而 `OSFrameworkImpl` 的公開介面上有 `SwiftExtension` 的型別：

| 事實 | 位置 |
|---|---|
| `@ArrayBuilder` **出現在 public 簽名** | `Sources/OSFrameworkImpl/AppKitImpl/AppKitImpl_NSView.swift:609`：`public init?(title: String, @ArrayBuilder<NSView?> views: () -> [NSView?])`；另 6 處同款 |
| **retroactive conformance**：對 `SwiftExtension` 的 `AppProperty` 由 `OSFrameworkImpl` 這邊宣告 | `Sources/OSFrameworkImpl/SwiftUIImpl.swift:171` `extension AppProperty: @retroactive DynamicProperty {}` |
| `NSMutex<…>` | `AppKitImpl_NSView.swift:771`、`AppKitImpl_Misc.swift:87/131/510`、`SecureEventInputSputnik.swift:136` |

### 2.5 「兩份 image」之風險量化

聚合體自身（將被併入 `libVanguard.dylib`）使用：`@AppProperty` **115 處**（`Sources/Shared/PrefMgr_Core.swift` 一檔即 103 項偏好屬性）、`NSMutex` **22 處**、`ArrayBuilder` 4 處。

反面量測（使「異名副本」在編譯期可行的原因）：聚合體的 **public 面並未暴露**這三個型別——`public` 面上提及 `AppProperty`／`ArrayBuilder` 者**僅有它們自己的宣告**，提及 `NSMutex` 者 0 處。

**推論**：「同名同具名型別的兩份 image」在 IME 行程內即為 `AppProperty` 之 retroactive `DynamicProperty` conformance 與 `@ArrayBuilder` 公開簽名所指向的危險型態；而「異名副本」雖避開執行期描述子衝突，卻使兩份型別互不相容、且**無任何機制約束兩份不漂移**（見 §四 路線乙）。

---

## 三、SwiftPM 的能力邊界（五支探針，實測）

| 探針 | 測什麼 | 實測結果 |
|---|---|---|
| **A** | target 依賴**同套件**之 product | ❌ `.product(name: "LeafDyn", package: "P215Probe")` → `error: unknown package 'P215Probe' in dependencies of target 'Mid'; valid packages are:`（清單為**空**）；省略 `package:` → `error: 'product(name:package:)' is unavailable: the 'package' argument is mandatory as of tools version 5.2`。**同套件 product 依賴不存在此語法。** |
| **C** | target 僅屬 dynamic product；同套件 exe 以 target 名依賴它 | ❌ exe **未**連結 `libLeafDyn.dylib`（`otool -L` 無該條），且 `leafValue` 在 exe 為**已定義**符號（`nm -gU` 計數 1）→ 靜態併入 |
| **D** | 同一 target 同時列入兩個 dynamic product | ❌ `libWide.dylib` 仍**靜態內含** `leafValue`（defined=1）；`libLeafDyn.dylib` 亦產出，兩顆各一份，且 **SwiftPM 不報錯**（靜默重複） |
| **E** | **＝原定形態**：target 只列入 `LeafDyn`，`Wide` 以 target 名依賴它 | ❌ 同 D：`libWide.dylib` 靜態內含（defined=1）、未連結 `libLeafDyn.dylib` |
| **G** | **跨套件** dynamic product | ✅ `libWide.dylib` 之 `otool -L` 出現 `@rpath/libLeafDyn.dylib`，`leafValue` 在 libWide 為**未定義**（undefined=1）→ 真動態相倚 |

**判決**：SwiftPM 之「產品的動態／靜態」只對**跨套件**的消費者生效；**同套件內**，屬於 dynamic product 的 target 對同套件消費者一律靜態併入。原定形態（聚合體內部以 product 形式取 `SwiftExtension`）**不可表達**，且失敗方式不是報錯、而是**靜默產出兩份 image**——正是本 phase 唯一硬性不變式所禁。

---

## 四、候選路線與淘汰理由

**不變式（硬）**：*每個行程內 `SwiftExtension` 的具名型別恰好一份 image。*

| 路線 | 內容 | 判定 |
|---|---|---|
| **甲** | 只在聚合體內新增窄產品，聚合體內部不動 | ❌ 探針 D／E：`libVanguard.dylib` 仍靜態內含，兩份 image |
| **乙（內化／抄副碼）** | 讓三消費端把所用到的 `SwiftExtension` API 副本抄進自身靶，與聚合體完全脫鉤 | ❌（可做但不採）：因 `OSFrameworkImpl` 用到 `ArrayBuilder`（public 簽名）／`AppProperty`（含 conformance）／`NSMutex`，複製量實質＝**整個 `SwiftExtension`（3 檔 1104 行）**；同名副本＝與甲同一種病且更無保護（與 `Vanguard` 無關、無編譯期與 SwiftPM 層級約束），異名副本＝型別不相容＋永久漂移債。且 P207／P208 才將本模組獨立為 MulanPSL-2.0（理由為「通用工具、應能與其他專案混用」），抄進 AppKit DSL 套件即作廢該獨立性 |
| **丙／丁（原定）** | 聚合體內新增 dynamic product `VanguardSwiftExtension`，其內部靶以同套件 product 形式取用之 | ❌ 探針 A／D／E：**語法不存在**、且靜默兩份 image |
| **方案 1（採用）** | `SwiftExtension` **析出為獨立套件**，由該套件出貨 dynamic product `VanguardSwiftExtension`；聚合體與全部消費端以**跨套件** product 取用之 | ✅ 探針 G 已驗證：真動態相倚、單一 image、零副本 |

**方案 1 與 4.7.4 的關係**：4.7.4 的 `Packages/vChewing_SwiftExtension` 出貨的是**static** product `SwiftExtension`；方案 1 只改一處——該產品改為 **dynamic**（否則 `libVanguard.dylib` 會靜態內含、exe 側亦靜態內含，回到兩份 image 且可能觸發 `duplication of library code`）。

---

## 五、定案形態（方案 1）

### 5.1 Darwin

- 新套件 `Packages/vChewing_SwiftExtension/`：target `SwiftExtension`（3 檔來源）＋ testTarget `SwiftExtensionTests`；出貨 `.library(name: "VanguardSwiftExtension", type: .dynamic, targets: ["SwiftExtension"])`。
- 聚合體：`Sources/SwiftExtension/` 與 `Tests/SwiftExtensionTests/` 移出；`Vanguard` 產品的 target 清單移除 `"SwiftExtension"`；5 個內部靶（`ResourceLocator`／`TrieKit`／`Shared`／`LexiconAssembly`／`LibVanguard`）改 `.product(name: "VanguardSwiftExtension", package: "vChewing_SwiftExtension")`。
- 三消費端（§2.1 之三條邊）改依賴 `VanguardSwiftExtension`。
- 結果：`libVanguard.dylib` 以 `LC_LOAD_DYLIB` 相倚 `libVanguardSwiftExtension.dylib`（非內嵌）；installer 只帶後者一顆；IME 帶兩顆但 `SwiftExtension` 恰一份 image。

### 5.2 非 Darwin（事主裁定）

> macOS 版自帶兩個 dylib 已經是不可避的事實。你可以用條件編譯的方式讓 SwiftExtension 在 macOS 以外的系統下變成 static。

故新套件之產品型別以 `#if canImport(Darwin)` 分流：**Darwin ＝ `.dynamic`；其餘 ＝ `.static`**。非 Darwin 之下聚合體照舊靜態內嵌 `SwiftExtension`，既有的單一 `Vanguard` dylib 形態**一字不變**（LibVanguard 倉之 ubuntu／winnt CI 必須維持原狀）。

### 5.3 兩倉同步之已知困難

P214 裁定兩倉 `Package.swift` **逐位元組相同**（`vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard/` 與 `vChewing-LibVanguard/`）。惟本方案使聚合體多出一條**本地路徑相依**：

- macOS：聚合體位於 `Packages/vChewing_OSNeutral_LibVanguard/`，新套件位於 `Packages/vChewing_SwiftExtension/` → 相對路徑 `../vChewing_SwiftExtension`
- LibVanguard：聚合體位於**倉根**，新套件無處可作其兄弟目錄 → 路徑必然不同

**故兩倉 manifest 之逐位元組相同性在本 phase 之後不再成立，差異將恰好落在那**一行** `.package(path:)`。此為已知且紀錄在案的偏離**（新套件自身的內容仍可維持兩倉相同）。此事於施工時確認並記錄於手術記錄。

---

## 六、爆炸半徑與未決事項

- **直接 `import SwiftExtension` 的套件（macOS 倉，實查 10 個）**：`vChewing_CandidateWindow`／`vChewing_FolderMonitor`／`vChewing_IMKUtils`／`vChewing_InstallerAssembly4Darwin`／`vChewing_MainAssembly4Darwin`／`vChewing_NotifierUI`／`vChewing_OSFrameworkImpl`／`vChewing_SettingsUI`／`vChewing_Shared_DarwinImpl`／`vChewing_UpdateSputnik`（另聚合體自身 19 檔）。其中 `vChewing_CandidateWindow` 與 `vChewing_NotifierUI` **並未**宣告 `Vanguard` 產品依賴卻能 `import SwiftExtension`——即 SwiftPM 之跨套件模組可見性含遞移依賴。故析出後它們是否仍需顯式補上依賴，**須以建置實測判定**，不可只憑靜態推論。
- **未決**：`vChewing.xcodeproj/project.pbxproj` 是否需為新本機套件補 `XCLocalSwiftPackageReference`（P210 之經驗：`-derivedDataPath` 不導產物、產物落倉庫自身 `Build/Products/`；且 Xcode 之 SPM 解析可能經由根 `Package.swift` 的圖達成，未必需要專案層級宣告）。
- **未決**：CI 清單（`build_darwin_SPMTestsAndPackage.yml` 之 `packages=(…)` 與兩條 `--package-path`）是否需隨新套件調整；LibVanguard 倉之三條 CI 亦然。

---

## 七、附錄：探針原始位置

| 探針 | 路徑 | 用途 |
|---|---|---|
| A | `_MainWorkspace/tmp/p215ProbeA/` | 同套件 product 依賴之語法存在性 |
| C | `_MainWorkspace/tmp/p215ProbeC/` | dynamic product 之成員被同套件 exe 依賴時之連結行為 |
| D | `_MainWorkspace/tmp/p215ProbeD/` | 同一 target 列入兩個 dynamic product 之行為 |
| E | `_MainWorkspace/tmp/p215ProbeE/` | 原定形態（target 只列入窄產品）之行為 |
| G | `_MainWorkspace/tmp/p215ProbeG/` | 跨套件 dynamic product 之動態相倚證明 |

全部探針皆為獨立玩具套件，與生產圖無關；**本 phase 動工前之生產碼零改動**。

---

## 落地狀態（2026-09-14，Phase 215 施工後補記）

本檔 §五 之方案 1 **已於同日落地並全量驗證**（macOS 與 LibVanguard 兩倉）。與本文預測相符者：

- 新套件落點：macOS `Packages/vChewing_VanguardSwiftExtension/`；LibVanguard 於倉根同名目錄。
- 兩倉之**聚合體 manifest 之差異恰為一行** `.package(path:)`（§5.3 之預測成立）。
- 探針 G 之結論直接成立：`libVanguard.dylib` 以 `LC_LOAD_DYLIB` 相倚 `libVanguardSwiftExtension.dylib`，兩顆之**已定義符號交集為 0**——`SwiftExtension` 每行程恰一份 image（§四 之不變式）。
- §6 之兩項「未決」皆已結案：**Xcode 無需 pbxproj 變更**（經由根套件圖自行解析新本機套件，`vChewingInstaller` 與 `vChewing` 兩 scheme 皆 rc=0）；**CI 清單無需調整**（見下「與預測不同者」）。

**與本文預測不同者（施工後更正）**：

1. **§6 之模組可見性推論需修正**：本文稱「8 個消費端是否需顯式補依賴，須以建置實測判定」。實測結果為**無需補**——SwiftPM 之跨套件模組可見性含遞移依賴，全倉根建置一次通過（12.59 秒），故實際改動的 manifest 只有 3 個（三條邊）＋ 聚合體自身。
2. **module 名一併更名**：事主於施工中指示「`SwiftExtension` 就得更名為 `VanguardSwiftExtension`」，故不只產品名、連**靶名與模組名**亦更名（`import VanguardSwiftExtension`），源碼檔 `SwiftExtension.swift` → `VanguardSwiftExtension.swift`。這是本文 §五 未載之追加要求。
3. **`buildTargetDependencies` 的 result builder 陷阱**：該 builder 在其他元素為字串字面量時，會把 `.product` 的隱式基底推成 `String`（`error: value of type 'String' has no member 'product'`）；**必須顯式寫 `Target.Dependency.product(…)`**。本文未預見。
4. **非 Darwin 之 `.static` 分流以頂層 `#if` 表達**（而非聚合體那套 ArrayBuilder DSL）——SwiftPM 不容 `#if` 寫進陣列字面量，但**可以**用頂層變數繞過，比為此在第二個 manifest 複製整套 DSL 精簡。

**量化結果**：installer 自身同捆由整條閉包（6.8 MB 級）降為**一顆 383 KB**；`vChewing.app` 為兩顆（6.59 MB ＋ 383 KB）。測試總數守恆：macOS 聚合體 539 → 529（整靶 10 項移出）、新套件 10；LibVanguard 545 → 535 ＋ 10。

**殘留**：`vChewing-OSX-legacy` 依範圍未動，其 TrieKit 副本仍寫 `canImport(SwiftExtension)`（該守衛在該倉恆為 false），使 P200 之「三倉 TrieKit 七檔 sha256 全等」在此一項上失效——列為跨倉同步債。

## 追加（同日）：模組更名之回退

**事主裁定**：本 phase §五 原案只要求「新套件出貨一個對外的 library `VanguardSwiftExtension`」；施工中途事主追加「`SwiftExtension` 就得更名為 `VanguardSwiftExtension`」，〈落地狀態〉亦隨之記載。其後事主複核裁定**回退該更名**：模組維持 `SwiftExtension`，**僅產品名**為 `VanguardSwiftExtension`。

**技術要點**：SwiftPM 不要求產品名與模組名相同——`Product.library(name: "VanguardSwiftExtension", targets: ["SwiftExtension"])` 即為本套件之現行宣告。

**連帶效益（回退反而消掉兩項成本）**：
1. 三個消費端 manifest 的 `package:`（＝目錄名 identity）與 `product:` 字串本與模組名無關，故**一字未動**。
2. `TK_QueryBuffer.swift` 的守衛還原為 `canImport(SwiftExtension)`，**三倉 TrieKit 七檔 sha256 全等隨之復原**（實測三檔皆 `1d53eb83c2521564…`）——本檔〈落地狀態〉原列為跨倉同步債者自行消解。

**回退之代價**：套件目錄名與 manifest `name:` 仍為 `vChewing_VanguardSwiftExtension`／`VanguardSwiftExtension`，與其內的模組 `SwiftExtension` 不同名（identity 取自目錄名，故消費端宣告不受影響）；此組態已於該套件 manifest 與 README 註明。

**回退後之複驗（2026-09-14）**：兩倉 `swift build` ✅（清快取後 macOS 47.73 秒／LibVanguard 8.02 秒）、macOS 聚合體 529＋新套件 10＋安裝器 5、LibVanguard 聚合體 535＋新套件 10 全綠；`make debug`／`make release` 同捆實查（`vChewing.app` 兩顆、`vChewingInstaller.app` 僅 `libVanguardSwiftExtension.dylib` 一顆、皆 universal、皆驗章通過）；installer 實跑存活 ✅；兩倉 `make lintFormat` 後重建 ✅。**施工教訓**：更名後必須**清建置快取**（macOS 用 `make spmClean`；LibVanguard 無該目標、須自行清 `.build`），否則增量建置會以殘留 `.o`／`.swiftmodule` 產出 `Undefined symbols` 之假失敗（本次實際踩到）。

## 追加二：`Deps/` 佈局——§5.3「兩倉 manifest 必然分歧」之推論被推翻

本檔 §5.3 曾斷言：因兩倉聚合體分別位於 `Packages/` 與倉根，「本地路徑相依」使兩倉 manifest 之逐位元組相同性**必然失效**，差異至少一行。**事主提出之佈局推翻了此推論**：

> 我把你剛才的工作臨時 commit 到 wip head 了。然後我做了一些改動。你看合理嗎？
> 竊以為這可以解決與 vChewing-LibVanguard 倉庫的 byte-identical 需求。

**正解**：子套件**置於聚合體目錄之內**（`<聚合體>/Deps/VanguardSwiftExtension/`），而非作其兄弟。如此，`.package(path:)` 之相對路徑**以聚合體自身目錄為錨**，兩倉皆為 `Deps/VanguardSwiftExtension`——**同字串，manifest 逐位元組相同**。§5.3 之所以誤判，是預設了「子套件必須是 `Packages/` 層的兄弟目錄」這一未經檢驗的前提。

**附帶結論（新知識）**：SwiftPM **接受巢狀子套件**（某 package 之目錄內含另一 package），實測兩倉皆可建置、可測試、可出貨；各消費端以 `.package(path: "../vChewing_OSNeutral_LibVanguard/Deps/VanguardSwiftExtension")` 指入，`package:` 取子套件之目錄名 identity。**故本 phase 之「已知偏離」項全數消滅**：兩倉 `Package.swift` 復原為逐位元組相同，`Sources/` 與子套件內容亦全等。

**落地後複驗**：macOS 聚合體 529＋子套件 10＋安裝器 5、LibVanguard 聚合體 535＋子套件 10 全綠；`make debug`／`make release` 同捆實查與 installer 實跑皆通過；兩倉 lintFormat 後重建＋重測通過；`cmp` 兩倉聚合體 manifest 相同。
