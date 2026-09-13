# Phase 199（可行性研究）：SPM 模組階層的動態庫化（dll 化）可行度調查

- 調查日期：2026-09-12。
- 狀態：**本 phase 即為研究 phase**。事主 2026-09-13 定性：Phase 199 單獨作為**可行性研究**用 phase（暫不施工）；**具體需要施術時，事主會另下 phase 編號**。本檔即本 phase 的交付物。調查始於 P198（MainAssembly 餘下單元測試歸類）完工後應事主指示進行，後經事主改列為獨立的 P199 研究 phase（檔名 `Phase199_Research_DLLifyTheSPMHierachy.md`）。本檔不動任何生產碼、不改任何 `Package.swift`；所有結論皆來自唯讀盤點與六個一次性 scratch 實驗（見 §五、§9.2、§9.3）。
- **落地狀態（2026-09-13，Phase 210 更新——本研究的終極目標已達成）**：`OSNeutralAssembly` 現在**可以被編譯成一個 dylib**（新增 `type: .dynamic` 的 `OSNeutralAssemblyDylib` product，其 7 個依賴 package 全部靜態併入該庫，且**不含** `MainAssembly4Darwin`／`IMKSwift`）。原報告列為「未驗」的 §八 E4／E5 已由該 phase 結案；而 §一.2「資源查找不會因 dylib 化而壞」只說對了一半——**dylib 一旦脫離任何 bundle，`Bundle.module` 是直接 `fatalError` 而非回 `nil`**，故該閉包的資源查找已全域改走 nullable 的 `ResourceLocator`。**惟本 phase 只做到「能編出 dylib」，未觸及出貨路徑**：`Contents/Frameworks` 嵌入、rpath、由內而外簽章、公證（即 §六 第 1、2 條阻塞級風險）與 §四 的工具鏈缺口**一律未動**。新增內容見〈Phase 210 更新〉一節。**（2026-09-13，Phase 210 追加檢證之五更正）**：此「未觸及出貨路徑」於併包後已被推翻——`make debug`／`make release` 皆同捆裸 `libOSNeutralAssembly.dylib`，Xcode 三個 scheme 皆自動以 `OSNeutralAssembly.framework` 形態嵌入；出貨路徑已部分落地，殘項見 §八 E8。
- 行號註記：本文所有 `檔案:行號` 皆為 2026-09-12 調查當日之快照；後續 phase（含 Phase 201~205 的命名換軌與 Phase 210）的改動可能使其位移，引用前請以內容比對為準。
- 委託要旨：評估把 `vChewing-macOS` 的 SPM 模組階層當中「可動態化者」由現行的全靜態連結改為動態庫（dylib），以緩解與檔案體積有關的難題；已知 `MainAssembly4Darwin` 不可動態化、且必須 static-link `IMKSwift`（輸入法必須讓系統能從執行檔直接讀到 `IMKInputSessionController`）。
- 主要疑慮：對「Xcode-based compilation」與「Swift-package-based compilation」兩條路徑的影響。
- **前置任務狀態（2026-09-13 更新）**：事主定性「**Phase 201~205 的命名換軌**」為本研究目標的**前置任務之一**，該工作已於 2026-09-13 完成——`Typewriter` 模組 → `OSNeutralAssembly`、`LangModelAssembly` 模組 → `LexiconAssembly`、`LMAssembly` 命名空間與其成員 → `LXAssembly.*`、`LMInstantiator`／`LMI` → `LXFacade`、`LMMgr` → `LXMgr`、小寫 `lm*` → `lx*`、`LangModel`／`langModel` → `Lexicon`／`lexicon`、測試靶 `TestLM` 族 → `TestLX` 族，本地套件 `ButKo_BPMFVS` → `vChewing_BPMFVS`。**本檔內的模組名、套件路徑、CI 檔名與符號名已於同日同步至新制**（量測數據、實驗結論與風險判斷一字未動）；`vChewing-DevLogs/Reqs4LLM/Archive_P001-P100/Reqs_0011-0020.md` 等歷史分卷與 `DevReqsHistory` 的 Phase 199 列則依開發史原則保留舊名，對照見 `KnowledgeMemo4LLM.md` 的〈命名沿革〉。
- 方法：先用子代理並行盤點 Xcode 專案設定、SwiftPM 建置與 bundle 組裝管線、以及執行時（IMK／簽章／資源查找）約束；再以 scratch 實驗把子代理「無法靜態判定」的兩個關鍵未知（dyld rpath、dylib 內的 `Bundle`/`Bundle.module` 解析）實測釘死。

---

## 一、結論速覽

1. **現況是「全靜態」**：兩條建置路徑（SwiftPM + `BundleApps` 插件 + `Makefile` 的出貨路徑；以及 `vChewing.xcodeproj` 的 Xcode 路徑）都把每個套件編成 relocatable `.o` 直接併入執行檔。`Build/Products/Release/` 有 36 個 `.o`、`LinkFileList` 34 行全是 `.o`，全機**零** `.a`／`.dylib`／`.tbd`；`otool -L` 對兩個 app 皆只列出系統庫與 `/usr/lib/swift/*`。
2. **資源查找不會因 dylib 化而壞**（本調查最大的未知，已實測排除）：把 SwiftPM 的 `.dynamic` 產物放進 `Fake.app/Contents/Frameworks/`、資源 bundle 放進 `Contents/Resources/` 後，dylib 內部的 `Bundle(for:)` 仍解析到**該 .app 本體**、`Bundle(for:).resourceURL` 仍是 `Contents/Resources`，`Bundle.module` 亦成功讀到 `ExpLibPkg_ExpLib.bundle`。原因：SPM 自動生成的 `resource_bundle_accessor.swift` 依序嘗試 `Bundle.main.resourceURL` → `Bundle(for: BundleFinder.self).resourceURL` → `Bundle.main.bundleURL`，而這三個候選在此佈局下都指向 `Contents/Resources`。**現行把 bundle 放 `Contents/Resources` 的作法可以原樣沿用。**
3. **真正的硬阻塞是簽章，不是連結**：現行 `make release`／`make debug` 以 **ad-hoc 簽章 + hardened runtime**（`codesign --sign - --options runtime`）出貨，且 entitlements 內**沒有** `com.apple.security.cs.disable-library-validation`。實測在此組合下 dyld 直接以
   `code signature … not valid for use in process: mapping process and mapped file (non-platform) have different Team IDs`
   拒絕載入自家 dylib。**這是 dll 化最先要解的問題**，且它同時決定了「本地開發路徑要不要放寬安全設定」與「分發路徑是否需要 Team ID 簽章」。
4. **第二大阻塞是工具鏈尚未接線**：`Plugins/BundleApps/plugin.swift:106-108` 以 `pathExtension == "bundle"` 硬編碼篩選，`assembleMainIMEApp` 從不建立 `Contents/Frameworks`、從不複製 `*.dylib`；`Makefile` 的 `lipo`（`:93-96`）、bundle 鏡像（`:73-78`、`:97-102`）、`vtool` 重蓋章（`:106-111`）三個迴圈也都只涵蓋 `vChewing` 與 `vChewingInstaller` 兩個執行檔與 `*.bundle`。
5. **rpath 兩條路徑不對稱**：SwiftPM 產出的執行檔實測只有 `/usr/lib/swift`、`@loader_path`、工具鏈路徑——**沒有** `@executable_path/../Frameworks`，故 dylib 放 `Contents/Frameworks` 會 `Library not loaded`（實測）；而 Xcode 三個 target 的 `LD_RUNPATH_SEARCH_PATHS` **早就**含 `@executable_path/../Frameworks`（`project.pbxproj:517-521, 557-561, 725-729, 791-795, 837-841, 878-882`），Xcode 端解析後甚至已帶 `DYLIB_INSTALL_NAME_BASE = @rpath`。
6. **體積效益的方向需要先確認，否則可能做白工**：對**單一** `.app` 消費者而言，dll 化通常使**總體積增加**——見 §3.5（**已修正**）：靜態連結真正的優勢比原先設想的窄。實測顯示 `-dead_strip` **只清各模組「非 exported」的死碼**，各 package 的 `public` 介面即使無人呼叫也**必然保留**（它是 dead-strip 的根）；而 **WMO 僅及於單一模組**，`-enable-cross-module-opt` 與 LTO 在本專案**皆未啟用**。會因 dylib 化而失去的是① weak/linkonce 符號的跨模組合併、② `__compact_unwind`／`__eh_frame`／型別中介資料等每映像一份的表在各庫重複列印、③ 各 dylib 對自身 exported 介面同樣無從 strip。現況 36 個 `.o` 合計 **34 MB**、連結後執行檔 **20.0 MB**，**但這 14 MB 的落差由哪些機制各貢獻多少，本調查未能量化**（`.o` 內的符號表／重定位／區域符號／對齊填充在最終連結時大幅縮編，佔比可能遠大於上述三項）。故**體積論據必須直接量測，不可由 `.o` 總和推論**；**建議後續 phase 先定義清楚「要省的是哪一種體積」**（`.app` 體積？PKG 體積？notarize／上傳耗時？還是「不想要一個巨大執行檔」的工程理由？），再決定是否動工。
7. **真正的紅利可能在別處**：模組化帶來的增量建置／連結時間縮短、資料模組（辭典）可獨立替換、Xcode 端各模組 `.swiftmodule` 快取重用、以及「同一個 dylib 被多個 consumer 共享」的場景。
8. **「只挑幾個模組動態化」做不到——SwiftPM 會直接拒絕**（見 §七方案 4）：`OSNeutralAssembly` 的依賴閉包（8 個 package）**完全落在** `MainAssembly4Darwin` 的閉包（25 個）之內，故任選子集都會讓同一個 static product 被 dylib 與 exe 各鏈一份，SwiftPM 以 `error: … This will result in duplication of library code.` 擋下（兩種拓撲實測皆然）。**最小自洽的動態集合 = `OSNeutralAssembly` 的整個閉包**：`OSNeutralAssembly, Tekkon, Homa, Shared, SwiftExtension, LexiconAssembly, BrailleSputnik, BPMFVS`；其餘 17 個 exe 專用套件可維持 static。規則：**動態集合必須對「同時被多個映像使用」封閉**。
9. **（2026-09-13 更新）除 §一.8 之外還有一條路：「一個 `.dynamic` product 罩住整個閉包」**。Phase 210 在 `vChewing_OSNeutralAssembly/Package.swift` 新增 `type: .dynamic` 的 `OSNeutralAssemblyDylib` product（target 與 static product 同為 `OSNeutralAssembly`），該 target 的 7 個依賴仍以 static 形式被**吸收進**這個 dylib。此拓撲下 SwiftPM **沒有**報 §一.8 的 duplication error——因為該 dylib 在整倉的建置圖內**沒有任何消費者**，應用端仍只消費 static 的 `OSNeutralAssembly` product。產物實測為 `Mach-O 64-bit dynamically linked shared library arm64`、`LC_ID_DYLIB` 為 `@rpath/libOSNeutralAssemblyDylib.dylib`、`otool -L` 只列 libiconv／Foundation／libSystem 與 Swift runtime。**此路徑與 §一.8 的「全閉包動態化」是兩件不同的事**：前者把整個閉包收進**一個**庫（適合「整包替換」與 §9.3 的 LGPL 聚合），後者讓閉包裡的每個 product 各自動態化（適合逐模組可替換）。兩者可並存，適用場景不同。
10. **（2026-09-13 更新）§一.2 的資源查找結論須補完——一般情形下 `Bundle.module` 是會炸的**：§五 B/D 證明的是「dylib 置於 `.app/Contents/Frameworks/`、資源 bundle 置於 `Contents/Resources/`」這**一種**佈局；Phase 210 補上了另一種——**dylib 脫離任何 bundle 時，SwiftPM 自動生成的 `Bundle.module` accessor 在找不到資源 bundle 時是直接 `fatalError`，不回 `nil`**。故該閉包內的資源查找已全面改走 nullable 的 `ResourceLocator`（查找序：手動指定 → `Bundle.main.resourceURL` → `Bundle(for:).resourceURL` → `Bundle.main.bundleURL` → 錨定型別所屬 bundle 之同層 → **`dladdr(#dsohandle)` 取得的編譯產物所在目錄與其 `Contents/Resources/`**），並於 `OSNeutralAssembly` 層面提供 `ResourceProvision` 供宿主手動指定。實測：純 CLI 宿主（`Bundle.main.bundleIdentifier` 為 `nil`）在「只有 dylib、旁邊沒有資源 bundle」的佈局下，查找回 `nil`、轉換原樣回退、退出碼 0、**不崩潰**。詳見〈Phase 210 更新〉。

---

## 二、現況實測

### 2.1 兩條建置路徑，出貨路徑是 SwiftPM + 插件

- **出貨路徑**（`Makefile:54-142`）：`universal-build` → 逐架構 `swift build -c release --arch arm64|x86_64`（`:62`、`:81`）→ `lipo -create` 合併兩個執行檔（`:93-96`）→ `vtool -set-build-version` 重蓋章（`:106-111`）→ `swift package bundle-apps`（`:114-142`）由 `Plugins/BundleApps/plugin.swift` 組 `.app`、`Info.plist`、`actool`/`tiffutil` 圖示、lproj、SPM 資源 bundle，最後 ad-hoc 簽章。
- **Xcode 路徑**：`vChewing.xcodeproj` 有 3 個 `com.apple.product-type.application` target——`vChewing`、`vChewingDebuggable`、`vChewingInstaller`（`project.pbxproj:376-380`），三者都只以 SPM product 形式依賴本地套件（`XCFrameworks` 階段各只有一筆 SPM product，`:154-179`）。從 `Build/Intermediates.noindex/XCBuildData/…/build-request.json` 可知它**確實會被實際建置**（最後一次 Release 建置 2026-09-10 13:02、73 個 target），`Makefile:239-244` 亦保留 `xcodebuild` 目標，但註解與現行流程把它視為 legacy／開發輔助。

### 2.2 全靜態的證據

- `Build/Products/Release/*.o`：36 個 universal relocatable object（每個都是 `[x86_64][arm64]`）。
- `Build/Intermediates.noindex/vChewing.build/Release/vChewing.build/Objects-normal/arm64/vChewing.LinkFileList`：34 行，**全部**是 `.o` 絕對路徑，零 `.a`、零 `.dylib`、零 `.tbd`。
- `Build/Products/Release/vChewing.app/Contents/`：`_CodeSignature`、`Info.plist`、`MacOS`、`PkgInfo`、`Resources`——**沒有 `Frameworks/`**。
- `otool -L Build/Products/Release/vChewing.app/Contents/MacOS/vChewing`：只有系統 framework／`/usr/lib/*`／`/usr/lib/swift/*`，**零** `@rpath/…` 條目。
- 26 個 `Packages/*/Package.swift` 的 `Product.library(...)` **無一**宣告 `type: .static` 或 `.dynamic`（全為預設），故 SwiftPM 對 executable consumer 採靜態連結。

### 2.3 體積現況（本次實測）

| 項目 | 大小 |
|---|---|
| `vChewing.app` 總計 | **39 MB** |
| └ `Contents/MacOS/vChewing`（universal fat） | 19.8 MB（`du` 計 19 MB；Xcode 路徑產物 18.9 MB） |
| └ `Contents/Resources`（辭典／`*.bundle`／圖示／lproj／授權） | 20 MB |
| `vChewingInstaller.app` 總計 | **42 MB**（其 `Contents/Resources/vChewing.app` 內嵌**整份** IME app，`plugin.swift:363-367`） |
| └ `vChewingInstaller` 執行檔本體（SwiftPM 路徑） | **僅 2.6 MB**——安裝器 app 的體積幾乎全來自被內嵌的 IME app |
| `vChewing` 執行檔本體（SwiftPM 出貨路徑，`.build/universal-release/`） | **20.0 MB** |
| 同目錄內容 | 只有 `vChewing`、`vChewingInstaller` 兩個執行檔 ＋ 4 個 `*.bundle`（`BPMFVS_BPMFVS`、`MainAssembly4Darwin_MainAssembly4Darwin`、`VanguardLexicon_LibVanguardChewingData`、`VanguardLexicon_VanguardTrieKit`）——**零 `.dylib`**，即插件 `--build-dir` 的輸入今日不含任何動態庫 |
| 36 個模組 `.o` 合計 | **34 MB**（連結後執行檔 19.8～20 MB；落差機制見 §3.5——**勿**逕稱其為 dead-strip／WMO／去重） |
| 套件 `.build` | 2.3 GB（與分發無關，僅影響本機／CI 快取） |

> 註（量測出處）：`Build/Products/Release/` 同時混有 Xcode 路徑與插件路徑的殘留產物，故上表以該目錄讀到的 `.app` 總量（39／42 MB）與執行檔大小（19.8 MB）僅供量級參考；已用 SwiftPM 出貨路徑的 `.build/universal-release/vChewing`（**20.0 MB**）交叉驗證，兩者一致。後續 phase 若要正式引用體積數字，應以一次乾淨的 `make release` 為準（見 §八 E2）。


模組 `.o` 體積排行（前 12，universal，含 debug/精簡符號前的原樣）：

| 模組 | `.o` | 備註 |
|---|---|---|
| `SettingsUI` | 7.1 MB | 最大單一貢獻者；僅設定窗需要 |
| `LibVanguardChewingData` | 3.5 MB | **來自遠端套件**（`vChewing-VanguardLexicon`） |
| `OSNeutralAssembly` | 3.1 MB | 跨平台（Linux/Windows CI 亦建） |
| `LexiconAssembly` | 2.8 MB | |
| `CSQLite3` | 2.2 MB | C 目標 |
| `Shared` | 2.1 MB | |
| `MainAssembly4Darwin` | 1.5 MB | **必須維持靜態** |
| `TrieKit` | 1.5 MB | |
| `InstallerAssembly4Darwin` | 1.3 MB | 僅安裝器 |
| `Homa` | 1.2 MB | |
| `OSFrameworkImpl` | 1.1 MB | |
| `TDK4AppKit` | 1.0 MB | 候選窗 |

其餘（`Tekkon` 0.8、`Shared_DarwinImpl` 0.8、`KeyKeyUserDBKit` 0.7、`SwiftExtension` 0.5、`VanguardTrieKit` 0.5、`NotifierUI`/`Hotenka`/`TooltipUI` 各 0.3、`PopupCompositionBuffer`/`IMKUtils`/`IMKSwift`/`BrailleSputnik` 各 0.2、`BookmarkManager`/`BPMFVS`/`FolderMonitor`/`OtherIMEDataReader`/`UpdateSputnik` 各 0.1～0.2、`Uninstaller`/`IMKSwift.o`/`CandidateWindow`/`CapsLockToggler` ≈0）。

### 2.4 `MainAssembly4Darwin`＋`IMKSwift` 必須靜態的實際落點

- 契約寫在 `Sources/vChewingIME_macOS/Resources/Info.plist:102-111`：`InputMethodServerControllerClass`、`InputMethodServerDataSourceClass`、`InputMethodServerDelegateClass`、`InputMethodSessionController` 皆具名為 `IMKInputSessionController`（另有 `…PreferencesWindowControllerClass`）。IMK 是以 **ObjC 類名**在宿主位址空間內實例化，故該類別必須存在於**執行檔映像**中。
- 對應實作在 `Packages/vChewing_IMKUtils/Sources/IMKSwiftModernHeaders/IMKSwift.m:55`（`@implementation IMKInputSessionController`）；`nm -gU .build/universal-release/vChewing` 可證 `_OBJC_CLASS_$_IMKInputSessionController` **定義於執行檔映像**。
- 技術附註：dyld 會把已載入映像的 ObjC/Swift 類別一併註冊，故「類別存在於 dylib」在理論上也能被 `NSClassFromString` 找到；但這條路徑把 IMK 的可載入性綁在「dylib 必須先被載入」之上——而 IME 主執行檔的啟動順序、以及系統載入 IME 的時機，都不宜再押這一注。**維持 static 是低成本換取確定性的選擇**，本調查支持維持。

---

## 三、SwiftPM 側：`type: .dynamic` 的真實語義（實測）

### 3.1 同套件 vs 跨套件：兩種截然不同的結果（重要）

以 scratch 實驗（§五）實測：

| 拓撲 | 結果 |
|---|---|
| **同一個 package 內**：`executableTarget` 依賴宣告為 `type: .dynamic` 的 library product | SwiftPM **仍把該目標的 `.o` 直接靜態連結進執行檔**——`nm -gU` 顯示 `_$s6ExpLib6reportSSyF` 是執行檔內**已定義**（`T`）符號；`otool -L` 完全不見 `libExpLib.dylib`。dylib 本身仍會被建出（供外部 consumer），但這條路徑沒用到它。 |
| **跨 package**：`ExpAppPkg` 以 `.package(path: "../ExpLibPkg")` 依賴後者 | 如預期產生動態相依：`otool -L ExpTool` → `@rpath/libExpLib.dylib`；產物落在 `.build/<arch>/release/libExpLib.dylib` 與 Nexus 路徑 `.build/out/Products/Release/libExpLib.dylib`（Swift 6.4 佈局）。 |

**對本專案的直接含義**：

- 本專案正是「跨 package」拓撲（root `Package.swift` 以 `.package(path: "./Packages/…")` 依賴各套件），所以 `.dynamic` 會真的生效。
- 但**同一個 package 之內**的子目標（例如 `MainAssembly4Darwin` 內部的多個 target、`OSNeutralAssembly` 內部的 `OSNeutralAssembly` 與其子目標）**不會**因為 `.dynamic` 而變成動態——若想把「某套件內部的子模組」拆成動態，必須先把它拆成獨立 package（成本與影響面完全不同，見 §七方案 3）。
- 反之，`MainAssembly4Darwin` 這個 package 內部即使有什麼可動態化的東西，也不受 `.dynamic` 影響（因為 consumer 在同 package 內或在另一個 package 取用它的 product……後者才是關鍵：**只要 MainAssembly4Darwin 這個 *product* 保持自動／靜態即可**，其內部無需特別處理）。

### 3.2 SwiftPM 產出的 rpath（實測）

`.dynamic` 拓撲下 SwiftPM 產出的執行檔 `LC_RPATH` 只有三條：

```
path /usr/lib/swift
path @loader_path
path /Applications/Xcode.app/.../usr/lib/swift-6.2/macosx
```

**沒有** `@executable_path/../Frameworks`。故把 dylib 放進 `Contents/Frameworks` 後必須另外補 rpath（`install_name_tool -add_rpath`、`-Xlinker -rpath`，或在插件/`Makefile` 內處理）。dyld 的實際搜尋失敗清單（實測）可供除錯對照：它會依序試 `/usr/lib/swift`、`Contents/MacOS/`、工具鏈路徑、`/usr/local/lib`、`/usr/lib`，最後才報 `Library not loaded`。

### 3.3 `.dynamic` 對跨平台建置的意義

`Packages/vChewing_OSNeutralAssembly` 同時活在 Ubuntu／Windows CI（`.github/workflows/test_ubuntu_OSNeutralAssembly.yml`、`test_winnt_OSNeutralAssembly.yml`，兩者皆 `swift test --no-parallel`）。`.dynamic` 在 Linux 是 `.so`、Windows 是 `.dll`，語義與 macOS 不同（無 hardened runtime、無 library validation、rpath 換成 `DT_RUNPATH`／DLL 搜尋路徑）。**若在共用套件上宣告 `.dynamic`，等於連跨平台建置與其 CI 一起改動**，須一併驗證（尤其 Windows 的 `.dll` 需與 `.exe` 同目錄或加入 `PATH`）。

### 3.4 遠端套件不可改

全倉僅**一個**遠端套件相依：`vChewing-VanguardLexicon`（`Packages/vChewing_MainAssembly4Darwin/Package.swift:34`，提供 `TextTemplateAssetInjectorPlugin`、`VanguardTextMapPlugin` 兩個 build plugin 與 `LibVanguardChewingData` 模組）。該模組是**第二大**貢獻者（3.5 MB）卻**無法**由本地改成 `.dynamic`——除非 fork／patch 上游，或改成 vendor 進本地 `Packages/`。同理，`vChewing_BPMFVS`、`HangarRash_SwiftyCapsLockToggler`、`Jad_BookmarkManager` 等雖為**本地路徑**套件（在 `Packages/` 內）故可改，但它們是外部上游碼，改動會製造與上游的鏡像落差（本專案一向在意鏡像逐字節一致）。

### 3.5 跨模組優化的真實邊界（實測；本節修正 §2.3 的推論）

§2.3 原本把「36 個 `.o` 合計 34 MB → 執行檔 20 MB」的落差逕稱作「全模組 dead-strip ＋ 去重 ＋ WMO 的成果」。**該推論不成立**，逐一實測後的真實規則是：

| 機制 | 是否跨 package 生效 | 實測結果 |
|---|---|---|
| dead-strip | **只清各模組「非 exported」的死碼** | 跨 package 靜態連結下，一個從未被呼叫的 `public func` **存活**（最終映像 3 個符號）；同檔從未被呼叫的 `internal`／`private func` **被清除**（0 個） |
| WMO | **不跨模組**（whole-module ＝ 單一 Swift 模組） | SwiftPM release 計畫出現 `-whole-module-optimization`（6 次）；Xcode 為專案層 `SWIFT_COMPILATION_MODE = wholemodule` |
| 跨模組最佳化（`-enable-cross-module-opt`） | **未啟用** | SwiftPM release 計畫中零出現 |
| LTO | **未啟用** | Xcode 專案 `LLVM_LTO` **零命中**；SwiftPM 計畫無 `-lto` |
| 去重（weak/linkonce 符號合併） | **跨 package 生效**（單一最終連結內） | 最終映像中泛型特化只剩**一份**且已被在地化（`t`）；`.o` 內原為 external（`T`） |
| ICF（相同但相異的機器碼摺疊） | 不支援 | Apple 連結器不提供 |

由此可下的三條結論：

1. **「其他 package 的 exported API 沒被用到就會被 strip」不成立**：每個模組的 `public` 介面是 dead-strip 的根，靜態連結下**必然被保留**。真實 IME 執行檔的交叉驗證亦同——8683 個 external 符號中，實際被使用的模組（`NotifierUI` 134、`UpdateSputnik` 52、`CandidateWindow` 32）保留其匯出，而未被 IME 連結的 `InstallerAssembly4Darwin` 為 0。
2. **跨模組的 IR 級最佳化在本專案完全不存在**：既無 LTO、亦無 `-enable-cross-module-opt`，故跨邊界只剩 `@inlinable`／`@_alwaysEmitIntoClient`／`@frozen` 這類由語言層帶來的效果。
3. **34 MB → 20 MB 的成分未被量化**：`.o` 內含的符號表、重定位、區域符號、`__compact_unwind`／`__eh_frame`、對齊填充等，在最終連結時會大幅縮編——**這部分的佔比可能遠大於上述三項機制**。因此**任何以「靜態連結省了多少」為前提的 dll 化論證，都必須先做 §八 E2 的直接量測**，不得由 `.o` 總和推論。

實驗重現：`_MainWorkspace/tmp/p199strip/`（三個 package：`LibPkg` 靜態庫 ＋ `LibBPkg` 中介庫 ＋ `AppPkg` 執行檔，庫中含從未被呼叫的 `public`／`internal`／`private` 函式與泛型特化）。判讀符號的指令範例：

```bash
nm -g <product>.o | grep -c neverCalled     # 產物 .o：public 函式是否被發出
nm    <exe>       | grep -c neverCalled     # 最終映像：3 → 未被 strip
nm    <exe>       | grep -c internalNeverCalled   # 0 → 已被 strip
swift build -c release -v | grep -oE "\-dead_strip|\-whole-module-optimization|\-enable-cross-module-opt|\-lto[a-z=]*" | sort | uniq -c
```

---

## 四、下游工具鏈盤點：dll 化要動哪些地方

### 4.1 `Plugins/BundleApps/plugin.swift`（出貨路徑的核心缺口）

- `:106-108`（現為 `:102-104`）以 `filter { $0.pathExtension == "bundle" }` 掃描「執行檔同層」的資源——**這是最大的結構性缺口**：任何非 `*.bundle` 的東西（即 dylib）對組裝器完全不可見。**（2026-09-13 實測確認，Phase 210 追加檢證）**：把一個真正的 `libOSNeutralAssemblyDylib.dylib`（`Mach-O 64-bit dynamically linked shared library arm64`）塞進插件輸入目錄後重跑 `bundle-apps`，退出碼 0、日誌對 `dylib` 0 命中、`.app` 內仍 0 個 dylib、無 `Contents/Frameworks`、執行檔 0 條 `@rpath`——即此篩選確實會把 dylib 擋在門外。
- `assembleMainIMEApp`（`:165-297`）只建立 `Contents/`＋`MacOS`＋`Resources`（`:176-182`），**從不建立 `Contents/Frameworks`**，只 `copyItem` 執行檔（`:185`）與 `*.bundle`（`:276-280`）。
- 簽章是單發 `codesign --sign - --entitlements … --options runtime --force --deep <app>`（`:588-597`），**無**逐一二進位「由內而外」簽章步驟；`--deep` 對嵌套第三方的 `--options runtime` 傳遞與公證皆不可靠。
- `Info.plist` 生成（`:502-526`）與 `dSYM` 產生（`:425-434`，對**已拷貝的** universal 執行檔跑 `dsymutil`）都只針對兩個 app。

### 4.2 `Makefile`

- `:93-96` `lipo` 只合併 `vChewing`、`vChewingInstaller`；dylib 需**逐架構各自** `lipo`（否則臂架 dylib 缺失）。
- `:73-78`、`:97-102` 只鏡像 `*.bundle` 到 `.build/universal-release`（Swift 6.4 的 Nexus 佈局讓 bundle 只落在 `.build/out/Products/Release`）；`.dylib` 從未被納入，故 `--build-dir .build/universal-release` 的插件將看不到它們。
- `:106-111` `vtool` 重蓋章迴圈字面寫死 `for bin in vChewing vChewingInstaller;`。

### 4.3 `vChewing.xcodeproj`

- 三個 app target **都沒有** `Embed Frameworks` 階段的 `PBXCopyFilesBuildPhase`（`dstSubfolderSpec = 10`）；唯一存在的 copy-files 階段是 `Embed Foundation Extensions`（`dstSubfolderSpec = 13`）且 `files = ()` 空集合（`project.pbxproj:33-43`）。
- 專案層 `DEAD_CODE_STRIPPING = YES`（`:598`、`:647` 等處）、`SWIFT_COMPILATION_MODE = wholemodule`（`:665`）、`COPY_PHASE_STRIP = NO`。專案**完全沒有** `MACH_O_TYPE`／`OTHER_LDFLAGS`／`BUILD_LIBRARY_FOR_DISTRIBUTION`／`DYLIB_*` 等設定（`OTHER_LDFLAGS = " -liconv"` 是套件圖帶進來的，來自 `Packages/vChewing_OSNeutralAssembly/Package.swift:42`、`:60` 的 `.linkedLibrary("iconv", .when(platforms: [.macOS]))`）。
- 實測解析後設定已含 `DYLIB_INSTALL_NAME_BASE = @rpath`、`LD_RUNPATH_SEARCH_PATHS_YES = @loader_path/../Frameworks`（Xcode 預設即在位），且三 target 的 `LD_RUNPATH_SEARCH_PATHS` 早已包含 `@executable_path/../Frameworks`。
- Xcode 是否會**自動**把本地 SPM 的 `.dynamic` product 嵌入 `.app/Frameworks` 並補簽，本調查**未實測**（需改 `Package.swift` 後跑 Xcode 建置，超出唯讀範圍）；文獻僅能佐證「Xcode 依套件宣告決定靜態／動態，實務上多為靜態」[Emerge Tools: Make Your iOS App Smaller with Dynamic Frameworks](https://www.emergetools.com/blog/posts/make-your-ios-app-smaller-with-dynamic-frameworks)。**列為後續 phase 的第一號待驗實驗（§八 E1）。**

### 4.4 簽章與公證

- 三條簽章路徑全都開 hardened runtime：`plugin.swift:588-597`（ad-hoc、`--options runtime --force --deep`）、`BuildPKG.sh:189-193`（Developer ID、`--force --deep --sign "${TEAM_ID}" --options runtime --timestamp`）、Xcode（`ENABLE_HARDENED_RUNTIME = YES` 於 `project.pbxproj:693, 765, 823, 870`；`CODE_SIGN_IDENTITY = "-"` 於 `:685, 757, 817, 864`）。
- Entitlements 只有兩份，且**都沒有** `com.apple.security.cs.disable-library-validation`：`Sources/vChewingIME_macOS/Resources/vChewing.entitlements`（app-scope bookmarks、KeyKey DB 讀取、`~/Library` 讀寫例外、mach-register global name、shared-preference 等；`app-sandbox`/`network.client`/`files.user-selected.read-write` 由簽章時注入）與 `Sources/Installer_macOS/Resources/vChewingInstaller.entitlements`（空字典）。
- 實測現行已建好的 `Build/Products/Release/vChewing.app` 簽章為 `flags=0x10002(adhoc,runtime)`、`TeamIdentifier=not set`（與 §五 B/C/D 實驗的條件一致）。

---

## 五、四個一次性實驗（scratch，不影響工作樹）

實驗位於 `_MainWorkspace/tmp/p199exp/`（同一 package 拓撲）與 `_MainWorkspace/tmp/p199exp2/`（跨 package 拓撲）。皆為最小可重現案例：一個含資源的 library target ＋ 一個 executable + 以 `type: .dynamic` 宣告 product ＋ 手工組出的 `Fake.app`。指令與結論：

| # | 條件 | 指令要點 | 觀察 |
|---|---|---|---|
| A | dylib 放 `Contents/Frameworks`、資源 bundle 放 `Contents/Resources`、**不補 rpath** | `cp` 執行檔／dylib／bundle 進 Fake.app → 直接執行 | ❌ `dyld: Library not loaded: @rpath/libExpLib.dylib`；搜尋清單證明 `Contents/Frameworks` **不在** rpath 內 |
| B | 同上 ＋ `install_name_tool -add_rpath @executable_path/../Frameworks`，ad-hoc 簽章（**無** `--options runtime`） | 補 rpath → `codesign --force --sign -` → 執行 | ✅ 可執行；`Bundle(for:).bundleURL` = `Fake.app`、`.resourceURL` = `Fake.app/Contents/Resources`、`Bundle.module` = `Contents/Resources/ExpLibPkg_ExpLib.bundle`、資源讀取成功 |
| C | 同 B 但簽章改為 **hardened runtime**（`--options runtime`，即現行出貨條件） | `codesign --force --options runtime --sign -` → 執行 | ❌ `Library not loaded`；關鍵訊息：`code signature … not valid for use in process: mapping process and mapped file (non-platform) have different Team IDs` |
| D | 同 C ＋ entitlements 加 `com.apple.security.cs.disable-library-validation = true` | `codesign --force --options runtime --sign - --entitlements <該 plist>` → 執行 | ✅ 全部斷言恢復正常，資源讀取成功 |

**由 A–D 可下的結論**：

1. rpath 是**必要**條件（A→B）。
2. hardened runtime + ad-hoc 是**充分**的拒絕條件（B→C），與 dylib 是否自家簽的無關——ad-hoc 沒有 Team ID 可比對。
3. `disable-library-validation` 是可行解（D），代價是削弱該 app 的程式庫載入防線；對本地／未公證的開發路徑無害，但**公證路徑要不要帶它須另行定調**（帶了會被檢視、不帶則必須走真 Team ID 簽章）。
4. 資源查找（SPM `Bundle.module` 與 `Bundle.currentSPM` 的候選集）在 dylib 化後**不需要改**——B 與 D 都證明 `Contents/Resources` 依然被正確解析。這也印證了 `Packages/vChewing_MainAssembly4Darwin/Sources/MainAssembly4Darwin/LXManager/BundleAccessor.swift:35-44` 既有的候選清單（其中第二項註解正是 "Framework embedding"）與 SwiftPM 自動生成的 accessor（候選序：`Bundle.main.resourceURL` → `Bundle(for:).resourceURL` → `Bundle.main.bundleURL`）都已經為這個情境預留了路徑。
   - **（2026-09-13 補正，Phase 210）**：本條的適用範圍僅止於「dylib 仍在某個 `.app` 內」。**脫離 bundle 的情形會踩到 `Bundle.module` 的 `fatalError`**（該 accessor 找不到資源 bundle 時不是回 `nil`）。該候選清單已抽為獨立 target `ResourceLocator`（`vChewing_SwiftExtension` 套件），`Bundle.currentSPM` 改為 `Bundle?`，SwiftPM 自動生成的 accessor 自此不再被 `OSNeutralAssembly` 閉包使用。見〈Phase 210 更新〉。

---

## 六、風險清單（依嚴重度）

> **（2026-09-13 更新）** 第 1、2 條是**出貨路徑**的阻塞，第 5 條（Xcode 自動嵌入）亦屬出貨路徑——Phase 210 證明了「能編出 dylib」但**未觸及出貨路徑**，故這三條**全部照舊未決**。第 4 條（體積）仍未量測（§八 E2 未做）。第 6 條（跨平台連帶）因新增的 `.dynamic` product 只存在於 `vChewing_OSNeutralAssembly` 套件內，**該套件的 Ubuntu／Windows CI 會連帶產出 `.so`／`.dll`**（實機未驗）。
>
> **（同日追加檢證）** 第 1、2 條的「現況」已實測釘死：Xcode 的三個 scheme（`vChewing`／`vChewingDebuggable`／`vChewingInstaller`）與 `make debug`／`make release` 五條路徑**全部不會產出、也不會同捆任何 dylib**（五者的 `.app` 皆 0 個 `.dylib`、無 `Contents/Frameworks`、執行檔 0 條 `@rpath`）。即：**新增的 dylib product 對現行出貨完全惰性**——第 2 條要「動」的時候，起點是零，不是「已經有東西漏出去」。第 5 條（Xcode 會不會自動嵌入 `.dynamic` product）在本專案**不適用**：沒有任何 target 宣告它為依賴。
>
> **（2026-09-13，Phase 210 追加檢證之五：上述「五條路徑皆不產出、不同捆」已被後續推翻——該記述在併包前為真）** 併包後事實已變：`make debug`／`make release` 皆同捆裸 `libOSNeutralAssembly.dylib`；Xcode 三個 scheme 皆以 `OSNeutralAssembly.framework` 形態自動嵌入（`Contents/Frameworks/`、並自帶 `@executable_path/../Frameworks` rpath）。第 5 條至此有答案：**Xcode 會自動嵌入**，「Xcode 直接建置不會同捆」的假設是錯的。惟自動嵌入在 ad-hoc ＋ hardened runtime 下令 app 啟動即死（退出碼 134、`different Team IDs`），成因經對照組實驗定位為 library validation，解法為 Xcode 內建設定 `RUNTIME_EXCEPTION_DISABLE_LIBRARY_VALIDATION`（見 §9.3 路線 (e)）。第 1、2 條至此**均不再是純阻塞**：同捆與 rpath 已落地，本地 ad-hoc 的簽章放寬亦已解（發佈路徑仍走同一 Team ID）。
>
> **（同日追加：第 1 條的阻塞已從 `Fake.app` 升級為真 app 實測）** 把 `Tekkon` 暫翻為 `.dynamic`、經升級後的 `BundleApps`（見 §八 E8）同捆進 `Contents/Frameworks` 並補上 rpath 之後，以**改掉 bundle ID 的 app 副本**實跑得：

```
dyld: Library not loaded: @rpath/libTekkon.dylib
  Referenced from: …/Probe.app/Contents/MacOS/vChewing
  Reason: tried: … '/…/Probe.app/Contents/Frameworks/libTekkon.dylib'
          (code signature … not valid for use in process:
           mapping process and mapped file (non-platform) have different Team IDs)
  退出碼 134
```

> 注意該路徑在搜尋清單中**不是 "no such file"**——dyld 精準找到了我方同捆的檔案，唯一異議是 library validation。即：**同捆、rpath 與由內而外簽章皆正確，卡點純粹是簽章政策**（`disable-library-validation` 或全體 Team ID 簽章，＝§八 E3）。

1. **簽章／載入（阻塞級）**：ad-hoc + hardened runtime 下 dylib 無法載入（實測 C）。必須二選一：加 `disable-library-validation`，或確保所有嵌套二進位都帶同一 Team ID 且由內而外正確簽章。後者與現行 `--deep` 單發簽章不相容（`--deep` 已被 Apple 視為不可靠）。
2. **組裝管線未接（阻塞級）**：`BundleApps` 不建 `Contents/Frameworks`、不複製 dylib、不補 rpath（硬編碼 `pathExtension == "bundle"`）。`Makefile` 的三個迴圈也都只涵蓋兩個 exe。
3. **公證／notarize**：nested dylib 需逐一 `--timestamp` 簽章；`--deep` 會被 notary 服務挑出來。另 `dSYM`（`:425-434`）目前只對兩個 app 產生，dylib 需各自 `dsymutil` 才能保住可除錯性。
4. **體積可能反向成長**（見 §一.6 與 §3.5）：單一 app 消費者時，dylib 化會失去「weak/linkonce 符號的跨模組合併」與「每映像一份的 unwind／metadata 表」，且各 dylib 對自身 exported 介面同樣無從 strip——**但實測顯示這些機制的量級遠小於原先設想**（各 package 的 `public` 介面在靜態連結下本來就必然保留；WMO 本來就不跨模組；LTO 與跨模組最佳化本來就沒開）。**這一項必須在後續 phase 動工前以 E2 直接量測**，不可由 `.o` 總和推論。
5. **Xcode 端行為未驗**：三個 app target 無 `Embed Frameworks` 階段。Xcode 會不會自動嵌入本地 SPM 的 `.dynamic` product、會不會自動補簽、`vChewingDebuggable`（`ENABLE_HARDENED_RUNTIME = NO`）是否因此行為不同——**未實測**（§八 E1）。
6. **跨平台連帶**：`OSNeutralAssembly`（及其他共用套件）在 Ubuntu／Windows CI 也會建；`.dynamic` 會改動那裡的連結形態與測試執行方式（`.so`／`.dll` 的搜尋路徑）。
7. **遠端套件不可控**：`vChewing-VanguardLexicon` 的 `LibVanguardChewingData`（3.5 MB）無法本地改成 `.dynamic`；外部上游套件（`vChewing_BPMFVS` 等）即使在本倉 `Packages/` 內，改動也會製造鏡像落差。
8. **ObjC 類別可見性／類別名衝突**：dylib 化後 ObjC 類別仍會被 dyld 註冊，理論上不影響 `Info.plist` 的類名查找；但把「必須在執行檔映像內」的假設放寬，等於把 IME 的可載入性押在載入順序上——**建議不對 `MainAssembly4Darwin`／`IMKSwift` 動刀**（與委託前提一致）。
9. **`make debug` 的脆弱假設**：插件以 `builtArtifacts.first(where: { $0.kind == .executable })` 推導 bundle 來源目錄（`plugin.swift:87-92`）；dylib 出現後該目錄推導仍成立，但「第一個 executable」這個假設本來就鬆（同目錄還有 plugin 工具與 `VCDataBuilder`）。
10. **測試靶連帶**：`swift test` 在多數套件裡已是消費者；`.dynamic` 會讓測試 bundle 需要 rpath／搜尋路徑（SwiftPM 會自行處理，但 `--no-parallel` 的 CI 迴圈與 `Makefile:240-241` 的 `swift test` 需要複驗）。

---

## 七、候選設計（供本 phase 結論與後續施術 phase 取用）

### 方案 1（保守／推薦先做）：只動態化「大而獨立、且消費者單一」的模組，且先把簽章與管線打通

- 對象候選：`SettingsUI`（7.1 MB）、`OSNeutralAssembly`（3.1 MB）、`LexiconAssembly`（2.8 MB）、`Homa`（1.2 MB）、`TrieKit`/`VanguardTrieKit`、`Tekkon`、`Hotenka`、`BrailleSputnik`、`OSFrameworkImpl`、`Shared`/`SwiftExtension` 等（依 §二.3 排序取捨）。
- 維持靜態：`MainAssembly4Darwin`、`IMKSwift`／`IMKSwiftModernHeaders`、`IMKUtils`（三者與 IMK 入口契約同命），以及遠端 `LibVanguardChewingData`。
- 必要配套：`BundleApps` 複製 `Contents/Frameworks` ＋ 補 `@executable_path/../Frameworks` rpath ＋ 逐一二進位由內而外簽章；`Makefile` 對 dylib 逐架構 `lipo` 與 Nexus 鏡像；Xcode 端加 `Embed Frameworks`（或驗證其自動嵌入）。
- 先決條件：**完成 §八 的 E1–E3**，尤其 E2（量測 dll 化後的實際總體積）。

### 方案 2（全面）：除 `MainAssembly4Darwin`＋`IMKSwift` 外全部 `.dynamic`

- 效益最大化（模組邊界最乾淨），但 §六 的每一條風險都同時被放大，且 §一.6 的體積反效果最明顯（34 MB 的 `.o` 會被切成 30+ 個各自帶著未用碼的 dylib）。
- 除非目標其實是「模組化／可替換性」而非體積，否則不建議。

### 方案 3（替代／先確認動機）：不 dll 化，改用其他體積槓桿

若真正的痛點是 `.app`／PKG 體積，值得先量測這些方向（成本通常遠低於重做連結模型）：

- `Contents/Resources` 佔 IME app 的 **20 MB／39 MB**（§二.3）——辭典資料（`*.bundle` 內的 TextMap／SQLite／Plist）才是最大單一項，且與程式碼體積無關。先確認是否可用「共用辭典資料」「按需下載」「壓縮」處理。
- `vChewingInstaller.app` 內嵌**整份** `vChewing.app`（42 MB 中有 39 MB 是它）——分發總量的最大槓桿其實在這裡，而非模組連結方式。
- `strip`／`-Osize`／`DEAD_CODE_STRIPPING` 已開（`project.pbxproj:598`），故程式碼側能擠的不多；`dSYM` 已與 `.app` 分離（`--archive` 才產生）。

**建議**：先以 §八 的實驗回答「要省的是哪一種體積」與「Xcode 端會不會自動嵌入」。若答案指向「模組化／建置時間」→ 走方案 1；若指向「分發體積」→ 走方案 3（先動資源與安裝器內嵌）。

### 方案 4（委託人提案：只動 `Tekkon`／`Homa`／`OSNeutralAssembly`）——**SwiftPM 直接拒絕**，附最小可行集合

提案形狀：只把 `Tekkon`、`Homa`、`OSNeutralAssembly` 三者改為 `.dynamic`，其餘維持 static；`OSNeutralAssembly` 以 `@_exported` 重匯出其 static 依賴的公開 API，讓 `MainAssembly` 無需再自行宣告那些套件。

**① 重匯出這半已經做了**：`Packages/vChewing_OSNeutralAssembly/Sources/OSNeutralAssembly/OSNeutralAssemblySPM.swift` 現行即對 `BPMFVS`／`BrailleSputnik`／`Homa`／`LexiconAssembly`／`Shared`／`SwiftExtension`／`Tekkon` 全數 `@_exported`（另含平台 libc）。故此半無需施工。

**② 動態集合這半會被 SwiftPM 以 error 擋下（實測）**：

```
error: Swift package product 'SharedLib-product' is linked as a static library by 'AppMain-product'
       and 'DylibLib-product'. This will result in duplication of library code.
```

兩種拓撲皆然：① exe **直接**宣告該 static product；② exe 只經由**中介靜態套件**（模擬 `MainAssembly4Darwin` 的角色）間接取得它——實測同樣報同一則 error。重現於 `_MainWorkspace/tmp/p199split/`。

**③ 為什麼必然觸發（閉包數學，實測）**：`OSNeutralAssembly` 的依賴閉包共 8 個 package，且**完全被 `MainAssembly4Darwin` 的閉包（25 個）涵蓋**——兩者交集就是那 8 個全數：

```
OSNeutralAssembly 閉包 : BPMFVS, BrailleSputnik, Homa, LexiconAssembly, Shared, SwiftExtension, Tekkon, OSNeutralAssembly
兩者交集                  : 上述 8 個（＝OSNeutralAssembly 閉包全體）
只在 OSNeutralAssembly 內、exe 不需要者：0 個
```

也就是說：**沒有任何一個模組可以「只待在 dylib 裡」而同時不被 exe 靜態連結**。「只把 OSNeutralAssembly 動態化」不存在合法的靜態／動態切法。

**④ 最小可行集合**：把「動態集合」取為 `OSNeutralAssembly` 的**整個閉包**即自洽：

| 動態化（8） | 維持 static（17 ＋ `MainAssembly4Darwin` 本體） |
|---|---|
| `OSNeutralAssembly`, `Tekkon`, `Homa`, `Shared`, `SwiftExtension`, `LexiconAssembly`, `BrailleSputnik`, `BPMFVS`（`.o` 合計約 10.8 MB） | `BookmarkManager`, `CandidateWindow`, `FolderMonitor`, `Hotenka`, `IMKUtils`, `ModifierKeyHitChecker`, `NotifierUI`, `OSFrameworkImpl`, `OtherIMEDataReader`, `PopupCompositionBuffer`, `SettingsUI`, `Shared_DarwinImpl`, `SwiftyCapsLockToggler`, `TooltipUI`, `Uninstaller`, `UpdateSputnik`（＋`MainAssembly4Darwin`）—這些只被 exe 一個映像使用，不會重複 |

一般化規則：**「動態集合」必須對「同時被多個映像使用」封閉**；最小動態集合 = 共享模組的依賴閉包。上表左欄正是「`OSNeutralAssembly` 的閉包」，而非任選的 3 個模組。

**⑤ 狀態分裂（singleton split）是 SwiftPM 該守衛在保護的正確性面**：若某模組同時存在於 dylib 與 exe 兩個映像，其 `static var`／singleton 會有**兩份獨立實例**，跨映像讀寫互不可見——`PrefMgr.shared`、`SessionHost.shared`、`LXAssembly` 的靜態快取（`factoryTrie`／`associatesLazyLoader`）皆屬此類。方案 4 的原形正是這種佈局。（本項為**機制推理**：SwiftPM 已使該佈局無法建置，故未能實測；如需把推理變成事實，可以 `swiftc -emit-library` 手工造一個 dylib ＋ 另將同一份 `.o` 靜態併入 exe，即可觀察兩個 `shared` 實例。）

**⑥ 對 `Homa`／`Tekkon` 的特別註記**：兩者本身各僅 1.2 MB／0.8 MB 且皆為**無狀態純算法**模組（`vChewing_Homa` 的 `dependencies: []`、`vChewing_Tekkon` 的 `dependencies: []`，皆為葉節點）。把它們單獨動態化**沒有收益**；它們之所以必須進入動態集合，純粹是因為 exe 也要用它們、而 SwiftPM 不允許同一 static product 被兩個映像各鏈一份。**想「少動幾個模組」是做不到的——要嘛 0 個，要嘛就是這 8 個。**

---

## 八、待驗事項（可直接執行的實驗清單）

> 以下為後續工作所需的驗證項。哪些屬於本 phase 的研究範圍、哪些留待施術 phase，依事主對 P199 的範圍界定為準；本檔僅將其整理成可執行清單。

- **E1（Xcode 自動嵌入？）**：把**一個**無關緊要的本地套件（建議 `vChewing_FolderMonitor`）暫時改成 `type: .dynamic`，跑 `xcodebuild -project vChewing.xcodeproj -scheme vChewing -configuration Debug build`，檢查 `vChewing.app/Contents/Frameworks/` 是否自動出現 dylib、是否被自動簽章、`otool -L` 是否出現 `@rpath/…`。做完**立刻還原**。
- **E2（體積量化）**：同樣以上述單套件動態化為探針，量測 `Contents/MacOS/vChewing` 的 `lipo -info`／`size -m` 前後差異與 `.app` 總量差異；據此推算「全動態」與「方案 1 子集」的體積帳。**並應一併拆解「靜態連結時 34 MB `.o` → 20 MB 映像」的成分**（逐 section 比較 `.o` 總和與最終映像；符號表／重定位／區域符號／`__compact_unwind`／`__eh_frame` 各佔多少），因為 §3.5 已證明該落差**不能**歸因於跨模組 dead-strip／WMO。
- **E3（簽章路線定調）**：對 `Fake.app` 式樣本驗證兩條路：① ad-hoc ＋ `disable-library-validation`（本地／開發）；② `codesign --sign <TeamID> --options runtime --timestamp` 逐一二進位由內而外（分發／公證）。確認哪條要進 `plugin.swift` 與 `BuildPKG.sh`，並確認 §五 C 的 "different Team IDs" 是否在真 Team ID 下消失。
- **E4（`.dynamic` 與 SwiftPM 測試靶）**：把 `OSNeutralAssembly` 暫時 `.dynamic`（或新開一個 scratch 套件），確認 `swift test`、`--no-parallel`、以及 Ubuntu／Windows CI 的對應行為（`.so`／`.dll` 搜尋路徑）。**（2026-09-13 結案，Phase 210）**：不需「暫時」——`vChewing_OSNeutralAssembly` 已永久新增 `.dynamic` product。實測該套件的 `swift build`／`swift test` 同時產出 `libOSNeutralAssembly.a` 與 `libOSNeutralAssemblyDylib.dylib` 且 `swift test` 203 項全綠；根層 `swift build`（應用端）**不會**連帶建置該 dylib（建置日誌命中 0），故零常規建置成本。**Ubuntu／Windows CI（`.so`／`.dll`）仍未驗**（本機無 Docker）。
- **E5（資源候選序守門）**：確認 `Makefile` 對 SwiftPM 自動生成 `resource_bundle_accessor.swift` 的補丁（把 `Bundle.main.resourceURL` 提到最前）在 dylib 化後是否仍需要／是否仍生效；以 §五 B/D 的 `Fake.app` 樣本重跑即可。**（2026-09-13 結案，Phase 210）**：**該補丁在 `Makefile` 內已不存在**——全文只剩 `Plugins/BundleApps/plugin.swift` 一段描述它的過時註解（已於 Phase 210 更正）。且 `OSNeutralAssembly` 閉包自此**不再使用 SwiftPM 自動生成的 accessor**：`Bundle.module` 全面改走 `ResourceLocator`（nullable、可手動指定）。實測：dylib 脫離任何 bundle 而資源 bundle 不在側時，查找回 `nil`、轉換原樣回退、**不崩潰**（改前必 `fatalError`）。詳見〈Phase 210 更新〉。
- **E6（ObjC 類別可見性，可選）**：以 scratch dylib 放置一個 `@objc` 類別，由 `NSClassFromString` 從主執行檔查找，驗證 dyld 註冊行為——用來決定 `IMKUtils`／`IMKSwift` 是否**絕對**必須靜態（目前建議仍是維持靜態，此實驗只為把假設變成事實）。
- **E7（目標清單與動機）**：與事主確認「要省的是哪一種體積」（`.app`／PKG／上傳與公證耗時／不想要單一巨大執行檔），以及可接受的安全面取捨（是否容忍 `disable-library-validation`）。**（2026-09-13 部分回答）**：Phase 210 的動機並非體積，而是「先確認 `OSNeutralAssembly` 能被編譯成 dylib」這一件事本身（事主明示「遲早會被編譯成 dylib」）。體積一項仍未量測。
- **E8（出貨路徑；併包前「仍未開工」，2026-09-13 Phase 210 追加檢證之五已部分落地）**：把該 dylib 放進 `Contents/Frameworks`、補 `@executable_path/../Frameworks` rpath、逐一二進位由內而外簽章、notarize、`Makefile` 的逐架構 `lipo` 與 Nexus 鏡像、`plugin.swift` 的 `pathExtension == "bundle"` 硬編碼篩選——即 **§四 全節與 §六 第 1、2 條**。Phase 210 **一律未動**；`vChewing-OSX-legacy` 亦僅同步原始碼（該倉不建 dylib）。**（2026-09-13 追加檢證：現況已實測釘死）** 五條既有建置路徑（Xcode 的 `vChewing`／`vChewingDebuggable`／`vChewingInstaller` 三 scheme ＋ `make debug` ＋ `make release`）皆**不產出、亦不同捆** dylib（`.app` 內 0 個 `.dylib`、無 `Contents/Frameworks`、執行檔 0 條 `@rpath`）；另以正向探針（把真正的 `libOSNeutralAssemblyDylib.dylib` 塞進插件輸入目錄後重跑 `bundle-apps`）確認 §四.1 的 `pathExtension == "bundle"` 篩選確實會擋掉 dylib。**故此路線的起點是零**：E8 要做的每一件事都還是原封不動的未開工，不存在「部分漏出去」的中間態。**（2026-09-13，Phase 210 追加檢證之五更正：此段為併包前為真的記述）** 併包後 `make debug`／`make release` 已同捆裸 `libOSNeutralAssembly.dylib`、Xcode 三 scheme 亦自動嵌入 framework 形態，見下一條。
- **（同日第二輪，2026-09-13：E8 的管線已備、觸發未拉）** 事主指示「把 `OSNeutralAssemblyDylib` 變成 app target 的依賴」以落實 E8。實測結果：
  - **照字面做不可行**：於根 `Package.swift` 加一行 `.product(name: "OSNeutralAssemblyDylib", …)` 後 `swift build` 報 `error: Swift package product 'Shared-product' is linked as a static library by 'vChewing-product' and 'OSNeutralAssemblyDylib-product'. This will result in duplication of library code.`（另列 `BrailleSputnik`／`BPMFVS`／`LexiconAssembly`／`Homa`／`SwiftExtension`／`Tekkon`／`ResourceLocator`）。product 級依賴圖量測：exe 側與 dylib 側的**交集恰為整個閉包**，「由閉包外消費閉包內」的邊共 **15 條**、來自 11 個 exe 側產品（`Shared` 被 5 個消費、`SwiftExtension` 被 6 個）。→ **§一.8 的「最小自洽動態集合＝整個閉包」於 P210 之後依然成立**（成員 8 → 9，新增 `ResourceLocator`）。
  - **已就位並實測者**（`Plugins/BundleApps/plugin.swift`）：掃描同時辨識 `*.dylib`；**只同捆執行檔實際連結者**（`otool -L` 取 `@rpath/*.dylib` 之名再回建置目錄取件，找不到即報錯）；建立 `Contents/Frameworks/`；以 `install_name_tool -add_rpath @executable_path/../Frameworks` 補 rpath（須在簽章前）；`codesign` 改**由內而外**並移除 `--deep`（Apple 已不建議以 `--deep` 簽章）。`Makefile` 的 `universal-build` 亦增列 dylib 的逐架構蒐集、`lipo` 合併與 Nexus 鏡像。以暫翻 `Tekkon` 為 `.dynamic` 作探針實測：真連結 → 同捆＋rpath＋三層簽章全過；未連結（含建置目錄殘留者）→ **不進 app**。
  - **仍未開工**：把閉包 9 個 library product 改為 `.dynamic`、Xcode 三 scheme 的 `Embed Frameworks`、`BuildPKG.sh` 的嵌套 Team ID 簽章、以及 §六 第 1 條的簽章政策（`disable-library-validation`）：後者已於本輪以真 app 量測確認其必要性（見 §六）。另須留意６個套件同時活在 Ubuntu／Windows CI，`.dynamic` 會改變其 `.so`／`.dll` 連結形態（本機無 Docker、無法驗證）。
- **（2026-09-13，Phase 210 追加檢證之五：E8 部分落地，且前述「不產出、不同捆」已被推翻）** 併包之後事實已變——`make debug`／`make release` 皆同捆裸 `libOSNeutralAssembly.dylib`，Xcode 三個 scheme 皆自動以 `OSNeutralAssembly.framework` 形態嵌入（`Contents/Frameworks/`，Xcode 自帶 `@executable_path/../Frameworks` rpath），**無須手寫 `Embed Frameworks` 階段**。**E1 至此有答案：Xcode「會」自動嵌入**，「Xcode 直接建置不會同捆」的舊假設是錯的。管線面：`assembleMainIMEApp`／`assembleInstallerApp` 現共用 `embedLinkedDylibs(of:into:availableDylibs:)`（只複製執行檔 `@rpath/` 依賴清單內實際連結者、建 `Contents/Frameworks/`、`install_name_tool -add_rpath @executable_path/../Frameworks`、找不到即 `throw PluginError`）。
  - **自動嵌入伴隨的啟動回歸（已修）**：ad-hoc ＋ hardened runtime 下 app 一啟動即 `Library not loaded`、`different Team IDs`、退出碼 134；以副本重簽的對照組實驗定位為 library validation（關掉 hardened runtime、或加 `disable-library-validation`，皆放行）。解法採 Xcode 內建設定 `RUNTIME_EXCEPTION_DISABLE_LIBRARY_VALIDATION = YES;`（`vChewing`／`vChewingInstaller` 兩 target × Debug／Release 共四處，`plutil -lint` OK）；該鍵由 Xcode 於簽章時注入、**不寫進** `Sources/vChewingIME_macOS/Resources/vChewing.entitlements`，故 `BuildPKG.sh` 以該原始檔重簽的發佈件仍嚴格、無須改動。`vChewingDebuggable` 因 `ENABLE_HARDENED_RUNTIME = NO` 不需此鍵。三 scheme 皆 `** BUILD SUCCEEDED **`、皆嵌 framework、皆 6 秒實跑存活、`codesign --verify --deep --strict` 皆 satisfies。
  - **追加修掉的真 bug**：`make` 路徑的安裝器 app 因 `assembleInstallerApp` 未同捆 dylib／補 rpath 而一直無法啟動（退出碼 134、`dyld: Library not loaded: @rpath/libOSNeutralAssembly.dylib`、`Contents/` 無 `Frameworks/`）——Xcode 路徑靠自動嵌入才僥倖正常，`make` 路徑一直是壞的。現與主 app 共用同捆邏輯，簽章改走 `processEntitlements(source:bundleIdentifier:additionalEntitlements:)` 並以 `nestedCode:` 由內而外。修後 `make debug`／`make release` 退出碼 0、安裝器帶 dylib 與 rpath、universal（`lipo -archs` = `x86_64 arm64`）、6 秒實跑存活、主 app 無回歸。
  - **仍未做的殘項**：① `BuildPKG.sh` 對嵌套二進位仍以 `--deep` 單發簽章（未改為逐層由內而外；本機無 Developer ID 憑證可驗）；② Linux／Windows CI 未驗（本機無 Docker）；③ §六 第 4 條體積仍未量測（§八 E2 未做）。

---

## 九、LGPL 導向的追加研究（2026-09-12）

委託人補充真實目的：**把「跨平台組件」整體收進一個 dylib、以 LGPLv3 發佈**（而非為了體積）。此目的與 §一–§八 的體積討論是**兩件事**，重新盤點如下。

> 範圍註記（2026-09-13）：以下 §9.3 的路線 (b) 涉及 `vChewing-LibVanguard` 倉；事主已指示該倉**現階段僅為實驗場**、正式捲入前尚有需清理之事項，故相關建議**僅止於技術可行性層面**，不構成施工排程建議。

### 9.1 真正的 LGPL 集合只有兩個模組（macOS 倉）

| 模組（macOS 倉） | 標頭授權 |
|---|---|
| `vChewing_Tekkon` | **LGPL-3.0-or-later** |
| `vChewing_Homa` | **LGPL-3.0-or-later** |
| `vChewing_OSNeutralAssembly`／`vChewing_Shared`／`vChewing_SwiftExtension`／`vChewing_LexiconAssembly`／`vChewing_BrailleSputnik`／`vChewing_BPMFVS` | MIT-NTL |

**`vChewing_BPMFVS` 的「程式」部分經事主確認為 vChewing 嫡系（僅其資料來源非嫡系）**——此點只影響出處標註，不影響授權歸屬（標頭即 vChewing ＋ MIT-NTL）與結構可行性。

（表中模組名已於 2026-09-13 同步至 Phase 201~205 的新制；**標頭授權本身不因更名而變**，故「真正的 LGPL 集合只有 `vChewing_Tekkon` 與 `vChewing_Homa` 兩個」這項結論不受影響。）

**但上游 LibVanguard 的同一批模組全部標 `LGPL-3.0-or-later`**（`Tekkon`／`Homa`／`BrailleSputnik`／`TrieKit`／`LexiconKit`，實測逐檔標頭；原列於此的 `SharedCore`／`CandidateKit` 已於 2026-09-13（Phase 206）自 LibVanguard 移除——`SharedCore` 內與 FCITX 有關的相容項已遷入 macOS 與 legacy 兩倉並改掛 MIT-NTL 標頭），其 `LICENSES/preferred/LGPL-3.0-or-later` ＋ `LICENSES/exceptions/CUSTOM_LGPLv3_EXCEPTION.md` 亦在。**兩倉的標頭不一致**（最明顯是 `BrailleSputnik`：上游 LGPL、macOS 側 MIT-NTL）。這決定了「LGPL dylib」到底要收哪幾個模組，**需事主先定調**。

### 9.2 「只把 LGPL 那兩個做成 dylib」是可行且乾淨的（實測）

先前 §七方案 4 撞牆的原因是「動態 product 會把它的 **static** 依賴吸收進 dylib，而 exe 又靜態連結同一批」。而 `Tekkon`／`Homa` **兩者的 `dependencies` 都是 `[]`（零依賴）**，故：

- 兩者做成 `.dynamic` 後**各自都是自足 dylib**，沒有任何東西被吸收 → **吸收／重複衝突完全不存在**；
- **靜態 product 可以依賴動態 product**（實測：SwiftPM 建置成功，無前述 error）；
- 且 **LGPL 符號完全不再出現在執行檔**：`nm` 對 exe 數 `baseHello` ＝ **0**、dylib ＝ 1，exe 的動態依賴僅 `@rpath/libDynBase.dylib`，執行正常。這正是 LGPL 合規要的形態（程式碼只存在於可替換的庫內）。

也就是說：**LGPL 合規這件事，只需把 2 個 product 改成 `.dynamic`，原始碼零改動，消費者自動改為動態連結。**（重現：`_MainWorkspace/tmp/p199lgpl/`，靜態中介庫 → 動態庫的三層拓撲。）

### 9.3 「一個 dylib」：同一 package 內可，跨 package 不行（含實測與出路）

SwiftPM 的模型是「**一個動態 product ＝ 一個 dylib**」，且 product 只能涵蓋**同一個 package** 內的 target。macOS 倉把 Tekkon／Homa 等放在各自的 package → 只能得到**多個** dylib。

**但在同一個 package 之內，一個動態 product 可以涵蓋多個 target，且確實只產出一個 dylib（實測）**：以 `AggPkg`（同 package 內 `ModA`／`ModB` 兩 target，`ModB` 依賴 `ModA`）宣告 `.library(name: "AggCore", type: .dynamic, targets: ["ModA", "ModB"])`，結果：

```
產出的 dylib：只有 libAggCore.dylib（無 libModA／libModB）
dylib 內符號：_$s4ModA6aHelloSSyF ✓   _$s4ModB6bHelloSSyF ✓
執行檔動態依賴：@rpath/libAggCore.dylib（僅此一條）
靜態副本：aHello in exe = 0、in dylib = 1     ← 程式碼只存在於 dylib（正是 LGPL 聚合要的形態）
.swiftmodule：ModA 與 ModB 皆照常產出 → 消費者仍可 import ModA／import ModB（模組身分不變）
執行：a a-b ✓
```

（重現：`_MainWorkspace/tmp/p199agg/`。）

因此「把 OSNeutralAssembly 與其所有 deps 聚合成**一個** dylib」技術上成立，前提是那些模組必須**同屬一個 package**（同 package 內多 target ＋ 單一 `.dynamic` product）。三條出路：

- **(a) 併包**：把相關模組的 source 收進同一個 package，保留 target／module 名 → 單一 dylib；消費者**原始碼的 `import` 完全不變**，只需改 `Package.swift` 的相依行。代價：動到多倉鏡像結構（LibVanguard 與 legacy 各自的副本）。
- **(b) 改在 LibVanguard 做（形式上最省事，但見下方保留）**：`vChewing-LibVanguard` 的**同一個 package 內已含** `Tekkon`／`Homa`／`BrailleSputnik`／`TrieKit`／`LexiconKit` 全部 target（`Sources/_Modules/*`；`SharedCore`／`CandidateKit` 原亦在此列，已於 2026-09-13（Phase 206）移除），且已有 `LibVanguard` 傘狀 product。新增／改一個 `.dynamic` product 納入所要的 target，即**一行**可得單一 dylib；macOS 倉與 legacy 倉改成消費它即可。
  - **保留事項（事主 2026-09-13 指示）**：**LibVanguard 目前充其量只是實驗場**；在正式把整個倉捲入此變動之前，**尚有若干事項需先清理**（清單未定，事主將另行琢磨）。故本路線**暫不列入建議施工順序**，僅記錄其技術可行性；正式動工前應先由事主定案「LibVanguard 是否／何時成為此聚合的正式落點」。
- **(c) SwiftPM 之外的整合建置**（自寫腳本把多包 source 編進一個 dylib）：可行，但放棄 SwiftPM 的模組衛生與增量建置，不建議。
- **(d) 2026-09-13 新增（Phase 210 實證）：不動任何套件結構，在既有 package 上另立一個 `.dynamic` product，讓它把整個閉包「吸」進去。** 見〈Phase 210 更新〉§五——`OSNeutralAssemblyDylib` 的 target 只有 `OSNeutralAssembly` 一個，但它那 7 個跨 package 的依賴以 static 形式被吸收進同一個 dylib。此路線**不改任何既有 product 的型別、不動任何套件結構**，也不必把 source 併包；且因為應用端仍只消費 static product，SwiftPM 不會報 §一.8 的 duplication error。**限制**：被吸入的模組在同一個行程內**不能同時**又被 exe 靜態連結（§一.8 的老規則），故它適合「給另一個消費者以一個庫整體取用」（例如以 LGPL 形態整包發佈），不適合「叫應用端改吃這個 dylib」。（**2026-09-13，Phase 210 追加檢證之五**：併包後此 product 已更名為 `OSNeutralAssembly`、成為唯一出貨動態庫，產物為 `libOSNeutralAssembly.dylib`；Xcode 側以 `OSNeutralAssembly.framework` 形態自動嵌入。見 §八 E8。）
- **(e) 2026-09-13 新增（Phase 210 追加檢證之五）：本地 ad-hoc 路徑的簽章放寬，改用 Xcode 內建設定而非改授權原始檔。** 在 `vChewing.xcodeproj/project.pbxproj` 的 `vChewing`／`vChewingInstaller` 兩 target × Debug／Release 四個 `XCBuildConfiguration` 各插入 `RUNTIME_EXCEPTION_DISABLE_LIBRARY_VALIDATION = YES;`（`plutil -lint` OK）；Xcode 於簽章時自動注入 `com.apple.security.cs.disable-library-validation`，實跑由退出碼 134 轉為存活。**此鍵不寫進** `Sources/vChewingIME_macOS/Resources/vChewing.entitlements`，故 `BuildPKG.sh` 以該原始檔重簽的發佈件天然不帶放寬——正好落實「本地放寬、發佈嚴格」的雙軌政策，`BuildPKG.sh` 無須改動。`vChewingDebuggable` 因 `ENABLE_HARDENED_RUNTIME = NO`、不需此鍵。此設定名可在 `Xcode.app/Contents/SharedFrameworks/SwiftBuild.framework/…/SWBCore` 內與字串 `com.apple.security.cs.disable-library-validation` 相鄰處查得。

**聚合後要注意的兩件事**：

1. **被聚合的模組不宜再以「各自獨立的 static product」被其他映像消費**，否則又回到「同一靜態 product 被兩處各鏈一份」的舊問題。要嘛聚合 dylib 成為唯一消費途徑，要嘛那些 per-module product 也一併改為 `.dynamic`。
2. **授權聚合效果**：vChewing 自有這些模組的著作權（`OSNeutralAssembly`／`Shared`／`SwiftExtension`／`LexiconAssembly`／`BrailleSputnik`／`BPMFVS` 標頭為 MIT-NTL；`Tekkon`／`Homa` 為 LGPL-3.0-or-later），故**有權如此聚合**——MIT-NTL 屬寬鬆授權（MIT 明示允許 sublicense／合併，僅需保留原 notice 與 NTL 商標條款）。惟把 MIT-NTL 與 LGPL 併入**同一個庫**後，該庫整體以 LGPL 形態發佈：MIT-NTL 那部分的授權不會被「收回」（下游仍可依 MIT 取用），但取得該 dylib 者同時獲得 LGPL 賦予的權利。此為事主的政策選擇，非法規障礙（本文作者非法律專業，最終以事主／法務判斷為準）。

### 9.4 唯一真正的矛盾：hardened runtime vs LGPL 的「可替換性」

LGPLv3 §4 走「共享庫機制」路線的前提是使用者**能替換**該庫。而現行出貨為 ad-hoc ＋ `--options runtime` ＋ entitlements 無 `com.apple.security.cs.disable-library-validation`：使用者自行重編的 dylib 會被 library validation 以 *different Team IDs* 拒絕（§五 C 實測）；加了該 entitlement 即可載入（§五 D 實測）。故這是一條**需要與發佈／法務政策一起定調**的取捨：

- 加 `disable-library-validation`：符合「可替換」精神，代價是放寬該 app 的程式庫載入防線（業界為 LGPL／外掛而加此 entitlement 者所在多有）；
- 不加：使用者仍可替換，但必須**連整個 app 一起重新簽章**才能載入。

其餘工程面（`Contents/Frameworks`、rpath、逐一由內而外簽章、notarize、跨平台 CI）與 §四／§六 同，惟此路徑的施工範圍縮到 **1–2 個 dylib**。**（2026-09-13，Phase 210 追加檢證之五）** 本地 ad-hoc 一路的放寬已改由 Xcode 內建設定 `RUNTIME_EXCEPTION_DISABLE_LIBRARY_VALIDATION` 於簽章時自動注入（見 §9.3 路線 (e)）；因該鍵不寫進授權原始檔，`BuildPKG.sh` 的發佈件仍不帶放寬，故本節的取捨**原樣未決**——只是本地開發與發佈的分界變得更乾淨。

---

## 〈2026-09-13 更新〉Phase 210：終極目標已達成——`OSNeutralAssembly` 可編譯為 dylib

> 本節為 P199 調查之後的落地結果。它**不改動**本檔既有的量測數據、實驗結論與風險判斷，只回答一件事：在 §一.8 那個「要嘛 0 個、要嘛 8 個」的僵局之外，有沒有別的形狀？

### 一、閉包盤點：真正需要動的只有一份檔案資源

動工前先做了一次閉包實查：`OSNeutralAssembly` 及其 7 個依賴 package 在執行期**只讀取一份檔案資源**——`BPMFVS` 的 `phonic_table_Z.txt`；其餘 package（`BrailleSputnik`／`Homa`／`LexiconAssembly`／`Shared`／`SwiftExtension`／`Tekkon`）對 `Bundle` 一無引用。故「去 `Bundle.module` 化」的落點僅三處，而非地毯式清剿。

### 二、`ResourceLocator`：nullable 化的資源查找

新增獨立 target `ResourceLocator`（置於 `vChewing_SwiftExtension` 套件內，兩倉各一份鏡像；legacy 側無 `import SwiftExtension` 一行之差——`NSMutex` 與其同模組）。查找序：

1. 手動指定（`specifyResourceBundleURL(_:forBundleNamed:)`／`resourceRootURL`）
2. `Bundle.main.resourceURL`（`.app/Contents/Resources/`）
3. `Bundle(for: anchor).resourceURL`（framework、測試 bundle）
4. `Bundle.main.bundleURL`
5. 錨定型別所屬 bundle 之同層目錄（`swift test` 的兄弟佈局）
6. **編譯產物所在目錄**：以 `dladdr(#dsohandle)` 取得當前 image 路徑，再取其上層與其 `Contents/Resources/`

第 6 項是新補的關鍵——§五 的四個實驗（A–D）全都把 dylib 放進 `.app` 內，故都沒有覆蓋「動態庫與資源 bundle 同層、而宿主在別處」這一種**無法從宿主推得**的佈局。全部落空時回 `nil`，**絕不 `fatalError`**。

### 三、三處改動

| 落點 | 改前 | 改後 |
|---|---|---|
| `BPMFVS.getBPMFVSDataURL()` | `Bundle.module.url(…)`（找不到即 `fatalError`） | `dataURLOverride ?? ResourceLocator.url(…)` |
| `Bundle.currentSPM`（`MainAssembly4Darwin`） | `static let … : Bundle`，`fatalError` | `static var … : Bundle?`；**成功才快取、失敗不快取** |
| `InputHandler_HandleStates` 的 locale 取值 | `Bundle.main.preferredLocalizations[0]`（無保護 subscript） | `.first ?? "en"` |

`BPMFVS` 另增 `dataURLOverride`／`specifyDataURL(_:)`／`isDataTableLoaded`；`cachedLookupTable` 由 `let` 改 `var`，故指定後即時重載，載入失敗時所有 `convert` 一律原樣回傳輸入值。兩倉生產碼自此 `Bundle.module` 零殘留（僅餘 legacy `DictionaryData/`〔pinned submodule、建置期工具〕與 `LexiconAssembly/Sources/LXAssemblyMaterials4Tests/TestData.swift`〔測試材料靶、不在執行期閉包內〕）。

### 四、OSNeutralAssembly 層級的資源指定介面

新增 `ResourceProvision`：`specifyResourceRoot(_:)`／`specifyResourceBundle(_:forBundleNamed:)`／`specifyBPMFVSTable(_:)`／`clearAllSpecifications()`／`availabilityReport() -> [String: Bool]`（回報資源**是否已成功載入**，而非「路徑是否存在」——後者會在指定壞路徑時誤報 `true`）。`ResourceLocator` 另以 `@_exported import` 併入 `OSNeutralAssemblySPM.swift`，故其 API 亦在本套件層面可見。

### 五、dylib 產物

`Packages/vChewing_OSNeutralAssembly/Package.swift` 於既有 static product 之外新增：

```swift
.library(name: "OSNeutralAssemblyDylib", type: .dynamic, targets: ["OSNeutralAssembly"])
```

實測產物：`libOSNeutralAssemblyDylib.dylib`（`Mach-O 64-bit dynamically linked shared library arm64`）、`LC_ID_DYLIB` 為 `@rpath/libOSNeutralAssemblyDylib.dylib`、`otool -L` 只列 libiconv／Foundation／libSystem 與 Swift runtime——**無任何 bundle 假設**。整組閉包（`BPMFVS`／`BrailleSputnik`／`Homa`／`LexiconAssembly`／`Shared`／`SwiftExtension`／`Tekkon`）已靜態併入該庫，且 `BPMFVS_BPMFVS.bundle` 就躺在同一目錄，正是查找序第 6 項所覆蓋的佈局。

**它與 §一.8 僵局的關係（重要）**：本作法**不推翻 §一.8**。應用端的消費途徑完全沒變——`MainAssembly4Darwin` 仍只消費 static 的 `OSNeutralAssembly` product，全倉 `swift build` 甚至不會連帶建置這個 dylib（實測建置日誌命中 0），常規建置成本為零。這個 dylib 是給**另一個消費者**用的獨立產物：以**一個可替換的庫**整體取用該閉包（§9.3 的 LGPL 聚合正是這種需求）。因此 SwiftPM 在此拓撲下未報 duplication error——因為該 dylib 在整倉的建置圖內無人消費。**未驗的邊界**：若日後真的讓應用端同時消費此 dylib 與閉包內任一 static product，§一.8 的 error 是否回來，本 phase 未測（依 SwiftPM 該守衛的語義，屆時應採「要嘛全動態、要嘛照舊全靜態」的老規則）。

### 六、端到端實測（三種佈局）

以 `swiftc` 另編一支**純 CLI 宿主**（`Bundle.main.bundleIdentifier` 為 `nil`，非 `.app`、非 `.xctest`）連結該 dylib：

| 佈局 | 結果 |
|---|---|
| dylib 與資源 bundle 同層、宿主在別處 | ✅ 命中（路徑落在 dylib 所在目錄下的 `BPMFVS_BPMFVS.bundle/Contents/Resources/phonic_table_Z.txt`） |
| 只有 dylib、旁邊沒有資源 bundle | ✅ `availabilityReport` 為 `false`、`bpmfvsDataURL` 為 `nil`、轉換原樣回退、**退出碼 0 不崩潰**（改前必 `fatalError`） |
| 補回資源 bundle 後重跑 | ✅ 命中 |

三種佈局中，宿主手動指定不可讀資料表 → `availabilityReport` 立即轉 `false` 且轉換退避、`clearAllSpecifications()` 後立刻回復，全程無崩潰。

### 七、本 phase 仍未動者（＝本研究仍未結案的部分）

- **出貨路徑全未動**：`Contents/Frameworks` 嵌入、`@executable_path/../Frameworks` rpath、由內而外簽章、notarize、`Makefile` 的 `lipo`／Nexus 鏡像／`vtool` 三個迴圈、`plugin.swift` 的 `pathExtension == "bundle"` 硬編碼篩選（＝**§四 全節、§六 第 1、2 條、§八 E8**）。**（2026-09-13，Phase 210 追加檢證之五：此條已部分推翻——併包後 `make debug`／`make release` 皆同捆裸 `libOSNeutralAssembly.dylib`，Xcode 三 scheme 皆自動嵌入 framework 形態；殘項見 §八 E8。）**
- **體積未量測**（§八 E2）。
- **Xcode 端是否自動嵌入仍未驗**（§八 E1）。**（2026-09-13，Phase 210 追加檢證之五：已驗，見 §八 E8——Xcode **會**自動以 `OSNeutralAssembly.framework` 形態嵌入；但 ad-hoc ＋ hardened runtime 下 app 啟動即死（134），已用內建設定 `RUNTIME_EXCEPTION_DISABLE_LIBRARY_VALIDATION` 修好。）**
- **Linux／Windows CI 未驗**：新增的 `.dynamic` product 會讓 `vChewing_OSNeutralAssembly` 套件的 Ubuntu／Windows 建置一併產出 `.so`／`.dll`（＝§六 第 6 條）；本機無 Docker，未實跑。
- **`MainAssembly4Darwin`／`IMKSwift` 維持靜態**（與委託前提一致，未動）。
- **`vChewing-OSX-legacy` 僅同步原始碼**（該倉為純 XcodeProj，不建 dylib）。

完整施工與驗證記錄見 `vChewing-DevLogs/Reqs4LLM/Archive_P201-P300/Reqs_0201-0210.md` 的 Phase 210。

---

## 十、附錄：關鍵檔案位置索引

| 主題 | 位置 |
|---|---|
| 出貨建置管線 | `vChewing-macOS/Makefile:54-142`（`universal-build`／`release`／`archive`／`debug`／`pkg`） |
| bundle 組裝插件 | `vChewing-macOS/Plugins/BundleApps/plugin.swift`（`:106-108` 資源篩選、`:165-297` IME app、`:303-371` 安裝器 app、`:502-526` Info.plist、`:588-597` 簽章） |
| Xcode 專案 | `vChewing-macOS/vChewing.xcodeproj/project.pbxproj`（`:376-380` targets、`:33-43` copy-files phase、`:154-179` frameworks phase、`:517-521/557-561/725-729/791-795/837-841/878-882` rpath、`:693/765/823/870` hardened runtime） |
| IME 契約 | `vChewing-macOS/Sources/vChewingIME_macOS/Resources/Info.plist:102-111` |
| Entitlements | `Sources/vChewingIME_macOS/Resources/vChewing.entitlements`、`Sources/Installer_macOS/Resources/vChewingInstaller.entitlements` |
| PKG／公證簽章 | `vChewing-macOS/BuildPKG.sh:178-195`、`DevLab/NotarizationCommands.md`(txt) |
| 資源查找 | `Packages/vChewing_SwiftExtension/Sources/ResourceLocator/ResourceLocator.swift`（`ResourceLocator`；2026-09-13 Phase 210 起為該閉包資源查找的唯一入口，legacy 鏡像在 `Shared/Extensions/ResourceLocator.swift`）；`Bundle.currentSPM` 現為 `Packages/vChewing_MainAssembly4Darwin/Sources/MainAssembly4Darwin/LXManager/BundleAccessor.swift` 內對它的 nullable 包裝（原候選清單即抽為此 target）；SwiftPM 自動生成 accessor 位於 `.build/out/Intermediates.noindex/<Target>.build/<Config>/<Target>-t.build/DerivedSources/resource_bundle_accessor.swift`（該閉包已不再使用）；OSNeutralAssembly 層級的指定介面為 `Packages/vChewing_OSNeutralAssembly/Sources/OSNeutralAssembly/ResourceProvision.swift` |
| 本地套件清單 | `vChewing-macOS/Packages/*/Package.swift`（26 個；`Product.library(...)` 除 `vChewing_OSNeutralAssembly` 自 2026-09-13（Phase 210）起多一個 `type: .dynamic` 的 `OSNeutralAssemblyDylib` 之外，**全為預設型別**） |
| 遠端套件 | `Packages/vChewing_MainAssembly4Darwin/Package.swift:34`（`vChewing-VanguardLexicon` @4.7.4；含 `LibVanguardChewingData`） |
| CI 測試清單 | `.github/workflows/build_darwin_SPMTestsAndPackage.yml:49-87`（顯式套件列舉）、`test_ubuntu_OSNeutralAssembly.yml`、`test_winnt_OSNeutralAssembly.yml` |
| LibVanguard 側 | `vChewing-LibVanguard/Package.swift`（4 個 `Product.library`，亦全為預設型別；2026-09-13（Phase 206）前為 6 個）；`Sources/_Modules/{Tekkon,Homa,TrieKit,LexiconKit,SwiftExtension,BrailleSputnik}`（`SharedCore`／`CandidateKit` 已於同日移除） |
| 本調查的 scratch 實驗（LGPL 追加） | `_MainWorkspace/tmp/p199lgpl/`（靜態中介庫 → 動態庫：驗證「靜態可依賴動態」與 LGPL 符號不入 exe，見 §9.2） |
| 本調查的 scratch 實驗（單一 dylib 聚合） | `_MainWorkspace/tmp/p199agg/`（同 package 內兩 target ＋ 單一 `.dynamic` product → 只產出一個 dylib、模組身分保留、exe 零靜態副本，見 §9.3） |
| 本調查的 scratch 實驗 | `_MainWorkspace/tmp/p199exp/`（同 package 拓撲）、`_MainWorkspace/tmp/p199exp2/`（跨 package 拓撲，含 `Fake.app`）、`_MainWorkspace/tmp/p199strip/`（跨 package 靜態連結的 dead-strip／去重／WMO 判讀，見 §3.5）、`_MainWorkspace/tmp/p199split/`（SwiftPM 對「同一 static product 被 exe 與 dylib 各鏈一份」的拒絕，見 §七方案 4） |
| Phase 210 的端到端驗證（dylib 宿主） | `_MainWorkspace/tmp/p210_dylib_hostcheck.sh`（可重跑）與其輸出目錄 `_MainWorkspace/tmp/p210_scratch/`：以 `swiftc` 編出一支純 CLI 宿主連結 `libOSNeutralAssemblyDylib.dylib`，分三種佈局實測（dylib＋資源 bundle 同層／僅 dylib／補回 bundle），並驗證手動指定與 `availabilityReport` 的退避行為，見〈Phase 210 更新〉§六 |
