# Phase 217 施工規範（SOP）：把雙 toolchain 建置能力推及 `vChewing-macOS` 全倉

- 撰寫日期：2026-09-15。
- 狀態：**施工已完工（建置層面，2026-09-15 收工）**。本檔原為施工前規範；收工後**規範本體（§一～§十二）維持動工前原貌**（僅就實測結果補註），**實測紀錄集中於 §十三**（含 §13.4 之終點段與第三輪更正）。三倉之收工狀態、逐包 rc、兩支終點產物見 §十三；未竟事項見 §十四。
- 執行者：**Deepseek-v4-flash**——第一輪（Kimi Code harness，任務 A ＋ 任務 B 之 ⓪①②）與第二／三輪（DeepSeek 官方 harness，以下稱 **DSH**，終點段與收工）皆為該模型。事主 2026-09-15 指定。
- 事實基礎：`Research/Phase216_PostResearch.md`（LibVanguard 側已完成的手術：環境配對、版本擇定、語法矩陣、隔離方針、工具坑）、`Research/Phase215_PreResearch.md`（`Deps/VanguardSwiftExtension` 佈局之來歷與兩倉 byte-identity 的維持方式）、`Research/Phase216_PostResearch.md` §十四（單元測試結構之整肅）。**本檔凡涉機理者皆引自該等，不另立新說。**
- 適用對象：P217 施工者（AI agent 或事主本人）。
- 讀法：§一～§十二 為**規範本體**、§十三 為**施工進度**（快照，隨施工更新；規範與進度分離）、§十四 為**下一 phase 的待辦**；文末〈**事主裁定（2026-09-15，逐條）**〉為**裁決沿革之正本**。**本 SOP 已無待補細則**——原 13 個編號項中的 12 個有效問題已由事主逐條裁定（Q01～Q12），第 ④ 項連帶作廢，第 ⑬ 項依預設結案；**全文不再有任何待補標記**。**P217 已於 2026-09-15 收工**（兩支終點產物 `libInstallerAssembly4Darwin.a` 與 `libMainAssembly4Darwin.a` 已產出；5.10 側之 rc 分佈見 §十三）。**（2026-09-16 補註：原 19／19 之成立前提是「MainAssembly 之 5.10 manifest 不收 lexicon 依賴」；事主其後指示改回與 `Package.swift` 同構，該包遂復歸 rc≠0，**現值為 18／19**——見 §13.1 第 18 列與 §十四 N4。）**
- **本版沿革（2026-09-15，事主九條 P217 新規）**：本版即據該九條修訂。其中**兩條為取代性／修正性**（規則 4 取代本 SOP 初稿對 SwiftUI／`Observation` 的風險式處理；規則 5 取代並修正 availability 的處理方式；規則 9 取代 P216 時期之 A10），各處以「**事主 2026-09-15 新規，取代……**」註記，以保留判準的變遷。另有**兩項待補項因新規而定案移出**（用途＝compilability；CI 不納入 5.10 建置），並**遞補兩項新待補點**。
- **本版追加沿革（2026-09-15，事主追加 `#Preview` 規則）**：事主追加「**`#Preview` 也是 macro、需要用 compiler version 處理掉的**」。本版據以辦三件事——（a）把 `#Preview` **具名**寫進 §5.1(f) 與 §5.3 鐵律五，並補其機理與「整段包住」的範圍界定；（b）於 §5.4 新增**巨集（macro）普查**子表（`vChewing-macOS` 排除 `Deps/` 之實測，涵蓋巨集呼叫／巨集屬性／巨集宣告三類）；（c）於 §十二 新增 **R19**。**待補項維持 ①～⑫ 不變**——本輪普查未揭出須事主裁定之新問題（`#Preview` 的圈隔方式由既有的規則 4 與 §1.3 範圍條款即可導出，見 §5.4 之（五））。
- **本版追加沿革二（2026-09-15，事主追加兩條基礎設施規則）**：事主追加「**Unit Tests 不對 Swift 5.10 開放。每個 subpackage 要部署不同的 package.swift 版本、以及單獨的 makefile（便於測試 5.10 編譯）。**」本版據以——（a）把「Unit Tests 不對 5.10 開放」立為 **§5.3 鐵律六**並貫徹 §四／§十；（b）把 §三 的 manifest 要求**提升為逐 subpackage 通則**，附**逐套件施工 checklist 表**（§3.1）；（c）新增 **§2.4〈每個 subpackage 的 makefile 規範〉**（含可直接複製的模板）；（d）**重排 §九**：新增「**⓪ 基礎設施先鋪**」，排在改碼之前；（e）**遞補第⑬項待補點**（編號體系由 12 項增為 **13 項**，文末表與全文交叉指涉已同步）。此兩條把 P217 的前置工作由「改碼」擴大到「**逐套件鋪 manifest 與 makefile**」。
- **本版追加沿革三（2026-09-15，事主指定施工順序）**：事主給出 **18 項擊破序**（`SwiftyCapsLockToggler → … → MainAssembly4Darwin`，見 §9.3），並附「你可直接用這個順序加上你認為的合理修改」。本版據以**改寫 §九**：事主序列為 ① 擊破階段的**權威次序**；先前由依賴拓撲推導的那份順序**降格為 §9.4 的佐證**（不刪），並**逐條明列四處不一致**（含我自己先前 L1／L2 分層的一處錯誤，以及收斂段次序與新規 1 舉例次序之差異）。同時新增 §9.3 的**名稱對照表**（事主用名＝產品名 ↔ 目錄名＝SwiftPM identity）、§十 的**逐包驗收進度表**（按事主序可勾選）。**待補項數不變（仍為 13 項）**。
- **本版追加沿革四（2026-09-15，事主回覆三點）**：事主回覆三點，本版據以修訂——（a）**新增 §十三〈施工進度（快照，隨施工更新）〉**，作為**進度之唯一正本**，§十 原有的逐包進度表**併入該章**（§十 只留指向），並明寫「規範與進度分離」「指引檔不承載進度」；（b）**§2.4 的 makefile 定位改寫**：目的改為 **per-package 可建置性測試（compilation test）**、**不是單元測試**（與 §5.3 鐵律六交叉引用），規格強度降為「**模板即最小集，增刪依實際需求**」；（c）**裁定 `InstallerAssembly4Darwin` 可早收**——該項自第 17 位**前移至第 12 位**（與同深度的 `Shared_DarwinImpl`／`Uninstaller` 同組），**此調整令全序恢復與依賴深度一致的形態**（深度單調不減，原本唯一的一處「回跳」消失，逐段核對見 §9.4 之（一））；連帶更新 §9.1／§9.3／§9.4／§9.5／§9.6 與 §十三 之次序，並改寫 §9.4 之（二）為一則沿革。**待補項數不變（仍為 13 項）。**
- **本版追加沿革五（2026-09-15，事主逐條裁定全部細則）**：事主**逐條裁定〈待事主補的細則〉的全部問題**（Q01～Q12；Q04 因 Q01 連帶作廢；第 ⑬ 項未逐條裁定、依本 SOP 預設結案）。本版據以——（a）**原〈待事主補的細則〉清空**，改為〈**事主裁定（2026-09-15，逐條）**〉，內含**裁定表（13 列，原編號｜問什麼｜裁定｜依據／理由｜正文落點）**與前版編號沿革；（b）**正文原有的待補標記一律改寫為已定案的陳述，全文歸零**（唯一保留的兩項為**事實層**未解，另立專段、不用待補字樣）；（c）**新增 §十四〈下一 phase 的待辦〉**（承接 Q08 之 (b)：macOS 10.9 唯音輸入法／xcodeproj 側留待下一 phase）；（d）依 Q03／Q05／Q06／Q07／Q09／Q10／Q11／Q12 改寫 §2.3・§四・§5.5／§6.4／§6.2／§1.3・§9.6／§十二 R7／§十／§11.1／§7.2；（e）**新增 §十二 R21**（同一檔案不得被多個 actor 同時讀寫）。**本 SOP 已無待補細則**；P217 已於 2026-09-15 收工（見 §十三）。
- 數值快照：本檔所載行號、計數、清單皆為 2026-09-15 於 `vChewing-macOS` 工作區 clean 狀態下的實測（彼時 `git log` 頭為 `d0ff1138`／`df09641e`；**該倉的 hash 會隨每次 amend／rebase 漂移**，故本行僅作動工前的粗略對照，實作時請以訊息與主題指涉），**會隨施工漂移，僅作動工前的對照基準**。

---

## 一、目標與不變式

### 1.1 P217 要達成什麼

一句話：**`vChewing-macOS` 全倉在 Swift 5.10 toolchain 下可建置，且 Swift 6.2+ 側的行為一字不變。**

**施工方法：各個擊破（事主 2026-09-15 新規 1）。** 不採「先立骨架、後補細節」的由上而下，而是**從最小的 darwin dependency 入手，逐一修復 dual toolchain compilability**；最後再**按順序收斂**到 `InstallerAssembly`、`SettingsUI`、`CandidateWindow` 等元件，與**最終的 `MainAssembly`**。（本條取代本 SOP 初稿 §九 之鬆散「由葉到根」建議：方向不變，但「各個擊破 ＋ 明確終點 ＋ 明確收斂序」取代了原先只按依賴層分層的寫法。詳見 §九。）

**施工終點（事主 2026-09-15 新規 2）：`InstallerAssembly` 與 `MainAssembly`。** 理由：對 **libArcLite** 以及 **macOS 10.9 compatible Swift Runtime** 的摻入，**必須由 Xcode ＋ macOS 13.3- SDK 完成**；**Swift OpenSource Toolchain 無法完成這一點**，它在 P217 中的角色**僅止於「提前預編譯 static library `.a` 檔案供 Xcode 鏈接使用」**。故 5.10 側的「完成」以「**兩支 assembly 的 `.a` 可供 Xcode 鏈接**」為界，**不是**「OpenSource toolchain 自行產出可執行檔」。

「全倉」的具體範圍：

| 構件 | 現況（2026-09-15） | P217 要做的 |
|---|---|---|
| 巢狀 `Packages/vChewing_OSNeutral_LibVanguard/Deps/VanguardSwiftExtension/` | **已完成** | 不動（§5.3 禁則四） |
| `Packages/vChewing_OSNeutral_LibVanguard/` | **已完成** | 不動（除 byte-sync 鏡像之必要） |
| 其餘 18 個 `Packages/*` | 皆 6.2 單一 manifest | 補四份 manifest ＋ 語法遷移（各個擊破） |
| `vChewing_InstallerAssembly4Darwin`、`vChewing_MainAssembly4Darwin` | 皆 6.2 單一 manifest | **5.10 側的終點**（規則 2）；收斂序見 §九 |
| 根 `Package.swift`（`vChewing`／`vChewingInstaller` 兩支執行檔 ＋ `BundleApps` 插件） | 6.2 單一 manifest | **不在 5.10 側**（規則 2：OpenSource toolchain 之產出止於 `.a`，可執行檔由 Xcode 連結端產出） |
| `Sources/vChewingIME_macOS/Modules/main.swift`、`Sources/Installer_macOS/main.swift` | 收錄於根 manifest 之兩靶 | 同上（不進 5.10 側） |
| `Sources/vChewingDebuggable/`（2 檔，**僅** Xcode target，不在根 manifest） | — | **不納入 5.10 側**（事主裁定 Q01：目前不需要） |
| `vChewing.xcodeproj/project.pbxproj` | 三 scheme，`MACOSX_DEPLOYMENT_TARGET` 多為 12.0 | **先不動**（事主裁定 Q07） |
| `.github/workflows/` 三條 | 僅 6.2+ | **不做**（規則 8 定案：5.10 建置暫不列入 CI） |

**前哨已完成**：P216 的手術在 macOS 側的鏡像即 `Packages/vChewing_OSNeutral_LibVanguard/`（含其 `Deps/` 子套件），對應 macOS 倉現行 commit 訊息 `SwiftExtension // Swift 5.10 compilability.` 與 `LibVanguard // Swift 5.10 compilability.`（依 §八 第 7 條，此處**刻意不寫 hash**）。P217 是**由該點向外擴散**，不是重做。

**完成定義（逐步可驗收）**：對每個 in-scope package，能滿足「四份 manifest 就位」「`make build510-<pkg>` rc=0、0 error」「產物為 `.a`」「6.2 側不退化」四項，即該 package 收工。**全 phase 的完成＝`vChewing_InstallerAssembly4Darwin` 與 `vChewing_MainAssembly4Darwin` 兩支的 `.a` 皆可產出並供 Xcode 鏈接**（規則 2）＋ §十 驗收矩陣全綠。

**已定案（事主 2026-09-15 裁定 Q01）：`vChewingDebuggable` 不做 5.10 相容——目前不需要。** 事主原文：「這個 target 是用來測試 **memory footprint** 的。所有**不內建 Swift Runtime** 的 macOS 系統下的記憶體佔用**可能都會多出 200MB**、以供 Swift Runtime（包括各種 Swift AppKit Shim dylib）使用。**此乃已知狀況，不需要 `vChewingDebuggable` 再專門據此測試。**」故該靶**維持僅存在於 Xcode、不進 5.10 側**；其產物形態問題（原④）**因本裁定而連帶作廢**（非出貨靶既不在 5.10 側，即不存在 minOS／triple 的問題）。

**已定案（事主 2026-09-15 新規 2）：5.10 側的用途是 compilability，不是 runtime。** 產物止於供 Xcode 鏈接的 static `.a`；libArcLite 與 macOS 10.9 compatible Swift Runtime 的摻入由 Xcode ＋ macOS 13.3- SDK 負責，不在本 phase 的工具鏈職責內。**本條取代本 SOP 初稿之「5.10 側的用途：能建置抑或能跑在舊系統上」一問——該項已定案移出。**

### 1.2 三條硬不變式

| # | 不變式 | 依據 | 施工中的具體紅線 |
|---|---|---|---|
| **I1** | 每個行程內 `SwiftExtension` 恰一份 image | P215 §四（本 phase 唯一硬性不變式） | 不得新增任何「同套件 dynamic product」依賴；不得把 `SwiftExtension` 的型別副本抄進任何靶；`Deps/VanguardSwiftExtension` 的產品型別（Darwin `.dynamic`、非 Darwin `.static`）一字不動 |
| **I2** | 兩倉 byte-sync | P214 定讞；P216 §13.4 復原並維持 | `vChewing-LibVanguard/` ↔ `vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard/` 的 `Sources/`、`Deps/`、`Package.swift`、`Package@swift-5.10.swift`（及 6.0／6.1 兩份封堵檔）必須**逐位元組相同**；任一側的改動須**同輪鏡像**並以 `cmp`／`diff -rq` 驗收 |
| **I3** | 6.2 側全綠且項數不減 | P216 §一 | 每個 P217 commit 都必須維持 `swift build` ✅、`swift test` 全綠；**項數不得少於動工前基線**。項數若因靶拆分而位移，回報中須明列「N → M ＋ K」的守恆帳 |

**I1 為何是硬不變式的量化理由**（P215 §2.4／§2.5，施工時若有人提議「抄一份進去比較快」請回看本條）：`OSFrameworkImpl` 的 **public 簽名**上有 `@ArrayBuilder`、且對 `SwiftExtension` 的 `AppProperty` 宣告了 retroactive `DynamicProperty` conformance，而聚合體內的 `PrefMgr` 帶約 103 項 `@AppProperty`。同名兩份 image 即 ABI 危險型態；且 SwiftPM 對此**不報錯**，是靜默產出（探針 D／E 實測）。

### 1.3 什麼不算在範圍內；什麼或可直接繼承

- `vChewing-OSX-legacy` 一倉：**一行不動**（其 `project.pbxproj` 之 `SDKROOT = macosx13.3` 只是本 phase 選 SDK 的旁證，不是施工對象）。**但見下一條**。
- **【或然通道】可直接繼承自 Legacy Repo 者（事主 2026-09-15 新規 3，並經裁定 Q02 定其判準）**：部分模組**或可直接繼承自 Legacy Repo**（`vChewing-OSX-legacy`），以 **AppKitDSL 為首例**。
  - **判準（事主裁定 Q02）**：**Legacy 倉庫的本質是 vChewing-macOS 倉庫的「子集 ＋ Swift 5.10 Dialect」**；之所以說是「子集」，是因為**砍掉了 SwiftUI**。故——**「可繼承者」≒ 該模組在 legacy 的子集副本（即其非 SwiftUI 的部分）**。母倉的模組若整支都是 SwiftUI，則**無 legacy 對位物可繼承**，只能走 §5.1(f) 的 `#if compiler(>=6.2)` 圈隔。
  - **判定單位是模組、不是整包；仍須 case-by-case 逐一確認**（Q02 之裁定語即「case-by-case 逐一確認」）。每件的確認步驟：① 在 legacy 倉找出對位模組並比對其公開介面；② 確認其寫法在 5.10 側即可編（legacy 全倉無宣告層級 `@MainActor`，這正是 §6.1「那一刀」的來源）；③ 確認 6.2 側繼承後 `swift build`／`swift test` 不退化（I3）；④ **若該模組位於共享 `Sources/` 內，繼承即觸發 I2 的兩倉 byte-sync 鏡像**，不可只做單側。
  - 手法的位置見 §5.1(g)。**清單不預先列出**——依 Q02 之裁定，逐件於施工時確認並就地記錄。

- `vChewing-VanguardLexicon`（遠端）：**不處理（事主裁定 Q09）**。事主原文：「**已經與 Swift 5.10 相容。**現階段不用處理。**Swift 版本低於 5.10 的時候會自動報錯。**」　**（2026-09-16 補充：本裁定意謂「本 phase 不動該倉」；惟其後實測顯示該套件在 5.10 SwiftPM 之**依賴層**仍不可消費——其兩支 plugin 產品的 `CSQLite3` 靶帶 `.unsafeFlags(["-w"])`。故「改該倉」之事已另立為 §十四 **N4**，不與本裁定衝突：Q09 說的是本 phase 不處理，N4 記的是「下一 phase 若要讓 MainAssembly 於 5.10 側可建置，則必須由該倉出新版」。）**
  - **一併定案（Q07）：`vChewing.xcodeproj/project.pbxproj` 先不動。** 事主原文：「Legacy 倉庫的建置會引入『**舊版 Xcode 專用的 pbxproj**』。如果都讓一個 pbxproj 負責的話，**新版 Xcode 可能會自動摧毀掉舊版系統的 compilability**。」→ 故**不**在新舊 Xcode 之間共用同一份 pbxproj。
- `vChewing-Homebrew`／`vChewing-HomePage.io`／`vChewing-DevLogs`（除本規範之記錄本身）：不動。
- **P216 §十一的四項殘留之現行處置**：`Tekkon.sharedCache` → **不用處理（Q05，見 §6.4）**；兩個 5.10 warning（`InputSession.clientProxyObjectIdentifier`、`PrefMgr.didAskForSyncingLMPrefs`）→ 未動、僅列報；`Sources/LexiconAssembly/vChewingLXAssembly_Common.swift:72` 唯一那處 `#if compiler(>=6.2)` → 事主裁定保留；`withFileHandleQueue*` → **不用退役（Q06，見 §6.2）**；legacy 的 10.9 疑點 → 列為**事實層未解**（見文末〈事主裁定〉該段）。**其餘仍未動者，除事主另裁外不併辦。**
  - **P217 收工後回填（2026-09-15）**：`Phase216_PostResearch.md` §十一 已依本條之裁定**重新製表**——改用【已裁定保留】／【已結清】／【事實層未解】三種狀態標籤逐項標註（4／2／1），並補上各項在 P217 收工時之實測與落點。**該表自此不含任何「待事主裁定」項**；其中原第 4 項「`withFileHandleQueue*` 待退役」字樣，係**被本 phase 的 Q06 取代**者。
- 任何「順手整理」：本 phase 只做 5.10 可建置性。重構、改名、清死碼、調 config、升依賴版本，一律不做。

---

## 二、環境配對（三項缺一不可）

### 2.1 三項配對與各自的一行理由

| 項 | 值 | 為什麼（一行實測） |
|---|---|---|
| **工具鏈** | `LEGACY_TOOLCHAIN = $(HOME)/Library/Developer/Toolchains/swift-5.10.1-RELEASE.xctoolchain` | 只有 5.10 會挑到 `Package@swift-5.10.swift`（§三）；本機已存在此 toolchain |
| **SDK** | `LEGACY_SDK = /Applications/Xcode-15.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX13.3.sdk` | **SDK 錯＝312 個掩蓋式錯誤**：`module '_c_standard_library_obsolete' requires feature 'found_incompatible_headers__check_search_paths'`、`unknown argument: '-target-arch-variant'`、`could not build module 'Darwin'`——沒有一條指向真正的病灶；正解是 Xcode 15 的 MacOSX13.3.sdk |
| **scratch path** | 每個 package 一條：`.build/.legacy-<pkg>` | **共用＝兩份 manifest 的產物互踩**：5.10 的 SwiftPM 讀不懂新版 `.build/workspace-state.json`（v7），會警告 `unable to restore workspace state` 並**就地覆寫** |
| **部署目標** | `LEGACY_TRIPLE = x86_64-apple-macosx10.10` | **10.9 不存在**：`Data` 本身標為 macOS 10.10 起可用，`-target x86_64-apple-macosx10.9` 建不出東西（連 `@backDeployed` 同名 shim 都平替不了——`Data` 是型別、不是可比對的符號） |

**更陰的一層（務必記住）**：`swift package dump-package` 在 SDK 27 下**照樣成功**，因為 manifest 不 `import Foundation`。故「manifest 載得動」**不足以**證明該 SDK 可用；P216 曾據此誤判一次。

### 2.2 動工前的環境自檢

```bash
ls -d ~/Library/Developer/Toolchains/swift-5.10.1-RELEASE.xctoolchain
ls -d /Applications/Xcode-15.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX13.3.sdk
xcode-select -p     # 可為任意值：LEGACY_* 全走絕對路徑，不吃 xcode-select
```

本機 2026-09-15 實查：兩項皆在；`xcode-select -p` 為 `/Applications/Xcode.app/Contents/Developer`（Swift 6.4）。另裝有 `swift-6.3.3-RELEASE` 與 `swift-latest` 兩條 toolchain。

**環境認知（非本 phase 施工項）**：本倉的 build／CI 環境若為 **Intel Mac**，Xcode 上限為 **26.x**（6.3 系；macOS CI 現用的 Xcode 26.6 自帶 `swiftlang-6.3.3.1.3`），屆時 **Swift 6.4+ 須經 Open Source Toolchain 提供**；惟 **Xcode 允許指定系統預設的 Toolchain**，故此**不構成本 phase 的施工項**（僅作環境認知；其對封堵令的意涵見 P216 §13.6.9）。

### 2.3 Makefile 落點

在 `vChewing-macOS/Makefile`（現行 293 行）新增「Swift 5.10 側」一節，樣式照抄 `vChewing-LibVanguard/makefile` 第 4～38 行。**值一律 `?=`** 以便臨時覆蓋。

```make
# ---- Swift 5.10 側（x86_64、靜態產物）----
LEGACY_TOOLCHAIN ?= $(HOME)/Library/Developer/Toolchains/swift-5.10.1-RELEASE.xctoolchain
LEGACY_SDK ?= /Applications/Xcode-15.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX13.3.sdk
LEGACY_TRIPLE ?= x86_64-apple-macosx10.10

# 單一 package：make build510-vChewing_IMKUtils
build510-%:
	@export LC_ALL=C; \
	"$(LEGACY_TOOLCHAIN)/usr/bin/swift" build \
		--package-path "./Packages/$*" \
		--scratch-path ".build/.legacy-$*" \
		--triple "$(LEGACY_TRIPLE)" \
		--sdk "$(LEGACY_SDK)" \
		-Xswiftc -target -Xswiftc "$(LEGACY_TRIPLE)"

# 巢狀子套件在聚合體目錄之內（路徑帶斜線，故不能走上面的 `%`）：
# make build510-swiftExtension
build510-swiftExtension:
	@export LC_ALL=C; \
	"$(LEGACY_TOOLCHAIN)/usr/bin/swift" build \
		--package-path "./Packages/vChewing_OSNeutral_LibVanguard/Deps/VanguardSwiftExtension" \
		--scratch-path ".build/.legacy-swiftExtension" \
		--triple "$(LEGACY_TRIPLE)" \
		--sdk "$(LEGACY_SDK)" \
		-Xswiftc -target -Xswiftc "$(LEGACY_TRIPLE)"

clean510:
	@rm -rf .build/.legacy-*
```

兩個**不可省**的操作要點：

1. **`-Xswiftc -target -Xswiftc "$(LEGACY_TRIPLE)"` 絕不可省。** SwiftPM 5.10 會把 `--triple` 的**版本部分丟掉**、一律抬到自身地板（x86_64 為 `-target …-macosx10.13`）；宣告 `platforms: [.macOS(.v10_10)]` 也一樣被抬；`--triple` 單獨用無效；arm64 更被 linker 釘在 `minos 11.0`。**唯一有效的手段是 `-Xswiftc -target`（同一個 `-target` 後出現者勝）**——實測 `.o` 與最終二進位元組的建置版本確實是 10.10。
2. **scratch 逐 package 分離**，且 `spmClean` 要一併清 `.build/.legacy-*`。理由有二：① 5.10 SwiftPM 讀不懂 v7 版 `workspace-state.json`，共用即互踩；② 逐 package 一條使單點重建快、失敗可定位。**另**：巢狀子套件（`<package>/Deps/<sub>`）在直接對其建置時會生成獨立 `.build`，清掃邏輯須涵蓋（macOS 倉 `Makefile:39-46` 與 `Packages/Makefile:18-25` 已有先例，照抄即可）。

**已定案（事主 2026-09-15 裁定 Q03）：5.10 專用 manifest 的 `platforms` 一律填 `nil`；SwiftUI 的 availability 一律 macOS 14+。**

事主原文：「這樣才能**逼著 Xcode 15- 拿 macOS SDK 確認 10.9 API 合規性**。換言之就是對一般情況**故意不設 Availability 限制**。**SwiftUI 的 Availability 一律 macOS 14+**。」

落地三點：

1. **`platforms: nil` 是「故意不設限」，不是疏漏。** 用意是**把 10.9 的 API 合規性判定交給 Xcode 15 ＋ macOS SDK 端**裁決（本側產物是靜態 `.a`、不帶 load command，故編譯期不壓 minOS——§4.2 第 3 條）。
2. **非 SwiftUI 的 availability 點因此不逐一收斂。** 既然故意不設限制，就不必為「讓舊編譯目標過關」而在一般碼上加 availability 註記；遇真不可用者，仍走 §5.1(c) 或 §5.5 第 2 條的兩分支寫法。
3. **SwiftUI 一律以 macOS 14 為 availability 下限**，且**全體圈在 `#if compiler(>=6.2)` 之內**——與 §5.1(f)、§5.3 鐵律五同源；`#Preview` 亦然（§5.4 之（一））。故 `platforms: nil` 與「SwiftUI 不得裸露」兩者不矛盾：前者管**編譯期目標**，後者管**哪些碼進得了 5.10 側**。

**`LEGACY_TRIPLE` 仍維持 `x86_64-apple-macosx10.10`**（§2.1）：它是**編譯期 triple**，與 `platforms: nil` 各司其職——triple 決定「以哪個版本的 SDK API 為編譯基準」，`platforms: nil` 決定「manifest 不主動宣告平台下限」。
（**沿革**：本項初稿寫「須先以一支探針 package 實測再定案」、並把 `Observation`／`@Observable` 與 `SettingsUI` 的 `@available(macOS 14, *)` 併入同一風險敘述。**兩者皆已被取代**——前者由 Q03 直接定案；後者由規則 4 圈進 `#if compiler(>=6.2)`、其處置見上之第 3 點與 §5.5。）

### 2.4 每個 subpackage 的 makefile 規範（事主 2026-09-15 追加規則）

**規則原文**：「每個 subpackage 要部署不同的 package.swift 版本、以及**單獨的 makefile（便於測試 5.10 編譯）**。」
**事主 2026-09-15 補述（定調本節之規格強度）**：「與 makefile 有關的內容**根據實際需求來處理**，目前只是為了方便拿 Swift 5.10 做 **per-package compilation test**（**不是單元測試，而是測試可建置性**）。」

**存在理由 ＝ per-package 可建置性測試（compilation test）**，亦即**逐包驗收的最小單位**：有了逐包 makefile，任何人都能在**任一個 `Packages/<name>/` 目錄內**打一行 `make build510` 就把該套件的 5.10 **編譯**單獨跑起來——不必跑整倉、不必記長串旗標、也不必先讀懂 §2.3 的根層 Makefile。§九 的「各個擊破」正是靠這個入口才成立（見 §9.2）。

**【務必分清】可建置性驗證 ≠ 單元測試。** 兩者分屬工具鏈的兩側，**不可混淆**：

| | per-package 可建置性測試（compilation test） | 單元測試（unit test） |
|---|---|---|
| 目的 | 該套件**能否被編出來**（產出 `.a`） | 該套件**行為是否正確** |
| 在哪一側做 | **5.10 側**（`make build510`） | **僅 6.2 側**（`swift test`） |
| 依據 | 本節 | **§5.3 鐵律六**（Unit Tests 不對 Swift 5.10 開放）／§4.3 |
| 失敗的意義 | 該套件尚未完成 5.10 適配 | 功能有 regression |

故本節的 `build510` **不是**測試目標、也**不得**擴張為測試目標——它只回答「編不編得出來」。鐵律六限制了 5.10 側的**測試**，本節則界定了 5.10 側**唯一的驗證手段**；兩者互補而不衝突。

**規格強度：模板即最小集，增刪依該套件實際需求（事主 2026-09-15 定調）。**

- **最小集** ＝ 能跑起 `build510` 即可；`clean510` 視需要保留；**巢狀 `Deps/` 的變體目標只有聚合體需要**（見下）。
- **不為湊整而加目標**：模板裡沒有的目標，不要因為「看起來更完整」而加。
- **不強制任何測試類目標**（`test`／`test510`／`dockertest` 一律不出現在 5.10 側）。
- 若某套件的需求已由根層 `build510-%`（§2.3）完全滿足、毋須獨立入口，則依其實際需求省略——這正是「根據實際需求來處理」的落地；惟**逐包入口是 ⓪ 階段的常態交付**（§9.2）。

**這不是新發明，而是既有實例的推廣。** 本倉現況（2026-09-15 實查）：

| 位置 | 現狀 | 說明 |
|---|---|---|
| `Packages/vChewing_OSNeutral_LibVanguard/makefile` | **已存在且已生效**（122 行，git 已追蹤） | 內含 `LEGACY_*`、`build510`、`build510SwiftExtension`、`clean510`、`spmClean` 與 lint／format／test 一族；**與 `vChewing-LibVanguard/makefile` 逐位元組相同**（`cmp` 通過）——即 P216 在 LibVanguard 側所做者在 macOS 側的鏡像。**註**：它是**超集**（含 lint／format／test 族），非本節所稱之最小集；那些非 5.10 目標是該套件既有之物，**不在 P217 的增刪範圍內** |
| `Packages/vChewing_Hotenka/makefile` | 已存在（166 B，git 已追蹤） | 僅 `format`／`lint` 兩目標，**無** 5.10 側 → 須補最小集 |
| 其餘 17 個 `Packages/<name>/` | **無 makefile** | P217 要鋪的對象 |
| `Packages/Makefile` | 已存在 | 是**上層共用的** Makefile（`all`／`debug`／`release`／`clean`／`lint`／`format`／`lintFormat`），與逐套件者**不同層級**，不衝突 |

**模板（最小集；可直接複製到 `Packages/<name>/makefile`，增刪依該套件實際需求）**：

```make
# Pin LC_ALL so CJK collation stays identical regardless of the machine's locale settings.
.PHONY: build510 clean510

# ---- Swift 5.10 側（macOS 10.10 / x86_64，靜態產物）----
#
# 用途：於本套件目錄內 `make build510`，單獨驗證本套件的 5.10 編譯。
# 環境配對三項缺一不可，機理見：
#   vChewing-DevLogs/Research/Phase217_SOP.md §二（環境配對）與 §四（產物形態）。
LEGACY_TOOLCHAIN ?= $(HOME)/Library/Developer/Toolchains/swift-5.10.1-RELEASE.xctoolchain
LEGACY_SDK ?= /Applications/Xcode-15.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX13.3.sdk
LEGACY_TRIPLE ?= x86_64-apple-macosx10.10
# scratch path 逐套件獨立（各套件自己的 .build/.legacy）：共用會令兩份 manifest 的產物互踩。
LEGACY_SCRATCH ?= .build/.legacy

build510:
	@export LC_ALL=C; \
	echo "Building $(notdir $(CURDIR)) with Swift 5.10 for $(LEGACY_TRIPLE)…"; \
	"$(LEGACY_TOOLCHAIN)/usr/bin/swift" build \
		--package-path . \
		--scratch-path "$(LEGACY_SCRATCH)" \
		--triple "$(LEGACY_TRIPLE)" \
		--sdk "$(LEGACY_SDK)" \
		-Xswiftc -target -Xswiftc "$(LEGACY_TRIPLE)"

clean510:
	@rm -rf "$(LEGACY_SCRATCH)"
```

**若該套件有巢狀 `Deps/`（目前僅聚合體有）**，於同一份 makefile 再展開一個目標（照 LibVanguard 倉根與本倉聚合體既有實例）：

```make
LEGACY_SCRATCH_SWIFTEXTENSION ?= .build/.legacy-swiftExtension

# 巢狀子套件是**獨立的 package**、有自己的一組 `Package*.swift`，故版本擇定與聚合體各別進行；
# scratch 亦須再分一條，理由同 build510。
build510SwiftExtension:
	@export LC_ALL=C; \
	echo "Building Deps/VanguardSwiftExtension with Swift 5.10 for $(LEGACY_TRIPLE)…"; \
	"$(LEGACY_TOOLCHAIN)/usr/bin/swift" build \
		--package-path Deps/VanguardSwiftExtension \
		--scratch-path "$(LEGACY_SCRATCH_SWIFTEXTENSION)" \
		--triple "$(LEGACY_TRIPLE)" \
		--sdk "$(LEGACY_SDK)" \
		-Xswiftc -target -Xswiftc "$(LEGACY_TRIPLE)"
```

並把 `.PHONY` 與 `clean510` 一併擴充：

```make
.PHONY: build510 build510SwiftExtension clean510

clean510:
	@rm -rf "$(LEGACY_SCRATCH)" "$(LEGACY_SCRATCH_SWIFTEXTENSION)"
```

**四條不可省的技術要點（與「目標清單」無關，僅為技術必要性）**：

1. **scratch path 必須逐套件獨立**（各套件自己的 `.build/.legacy`）。理由與 §2.1 同：5.10 的 SwiftPM 讀不懂 v7 版 `workspace-state.json`，會就地覆寫；且巢狀子套件與其宿主共用同一 scratch 時，兩份 manifest 的產物會互相踩。
2. **`-Xswiftc -target -Xswiftc "$(LEGACY_TRIPLE)"` 不可省**——SwiftPM 5.10 會丟掉 `--triple` 的版本部分並抬到自身地板（10.13），只有 `-Xswiftc -target` 能真正壓到 10.10（§2.3 要點 1）。
3. **5.10 側不提供任何 test 目標**——貫徹「Unit Tests 不對 5.10 開放」（§5.3 鐵律六）。模板中的 `.PHONY` **不得**出現 `test510` 之類目標；若照抄聚合體那份已有 `test`／`test-debug`／`dockertest` 的 makefile，**那些是 6.2 側的目標，須原樣保留、不可挪用於 5.10**（亦**不得**因為看到它們而認為 5.10 側也該有對應物）。
4. **以 `--package-path .` 相對於該套件目錄運行**——與 §2.3 根層 `build510-%`（`--package-path ./Packages/$*`）形成兩個入口、同一套規則：根層一次跑一包，逐包 makefile 進到目錄就能跑。

> **要點 1～4 之外，沒有「必須包含」的目標清單。** 本節不對任何套件強制 `clean510` 或任何變體目標；模板即最小集，增刪依該套件實際需求（見上方「規格強度」）。

**命名與衝突**：檔名一律用**小寫 `makefile`**（與 `vChewing-LibVanguard/makefile`、本倉兩個既有實例一致）。**注意 macOS 的 APFS 預設不分大小寫**——同一目錄內不可同時存在 `makefile` 與 `Makefile`（會被視為同一檔）；本倉各 `Packages/<name>/` 目前皆無此衝突，但施工時不要為了「看起來一致」而把上層的 `Packages/Makefile` 也改名。

**與根層 Makefile 的關係**：§2.3 的根 `Makefile` 目標（`build510-%`／`build510-swiftExtension`／`clean510`）**保留**，供「一次掃多包」與 CI 式批次使用；§2.4 的逐包 makefile 供「單包深挖」。兩者旗標必須同源——**改一處就要改另一處**，否則會出現「根層過、逐包不過」的假象。

**定案（本 SOP 之預設結案；見文末〈事主裁定〉表末列）：聚合體的 `Packages/vChewing_OSNeutral_LibVanguard/makefile` 維持與 `vChewing-LibVanguard` 倉根的 `makefile` byte-identical，並視為 I2 的一部分。** 實測現況：**兩者已逐位元組相同**（各 122 行，`cmp` 通過；且本倉已 git 追蹤）。兩倉其餘（`Sources/`／`Deps/`／manifest）已由 I2 綁定 byte-sync（§1.2），這份 makefile 是唯一**尚未明文納入 I2、卻又已實質同源**的檔；本結案即把它明文納入——日後任一邊改動皆須同輪鏡像（§11.2）。**此項事主本輪未逐條裁定**，故標明為「依本 SOP 預設結案」，以免後人誤讀為事主裁定。

---

## 三、版本擇定與封堵

### 3.1 每個 subpackage 要哪四份 manifest（通則，非單一 package）

**規則原文（事主 2026-09-15 追加）**：「**每個 subpackage 要部署不同的 package.swift 版本**、以及單獨的 makefile（便於測試 5.10 編譯）。」

**通則**：本項**不是**針對某一個 package 的一次性作業，而是**對每一個 subpackage 的普遍要求**——凡 `Packages/` 下每一個目錄（各為一個獨立的 SwiftPM 套件），以及聚合體目錄內的巢狀 `Deps/` 子套件，**都必須各自部署一組四份 manifest**。理由直接來自 §3.2 的擇定規則：SwiftPM 的版本擇定**以「檔內宣告的 tools version」為準、逐套件各別進行**——少鋪一份，該套件在對應 toolchain 下就沒有正確的 manifest 可挑。

| 檔 | 檔內宣告 | 角色 |
|---|---|---|
| `Package.swift` | `// swift-tools-version: 6.2` | 6.2+ 側的現行 manifest，**本 phase 原則上不動**（除必要時補 5.10 側所需之設定） |
| `Package@swift-5.10.swift` | `// swift-tools-version: 5.10` | 5.10 側的對位版（§四） |
| `Package@swift-6.0.swift` | `// swift-tools-version: 6.0` | **封堵檔**：`import PackageDescription` ＋ `#error(…)` |
| `Package@swift-6.1.swift` | `// swift-tools-version: 6.1` | 同上 |

**逐套件施工 checklist（2026-09-15 實查，可直接當工單用）**：共 **19 個 subpackage**。`目錄名` 即 SwiftPM 本地路徑相依的 **package identity**（消費端以 `.product(name:package:)` 指涉時用的就是它，**不可逕自改名**）。

| # | 目錄名（＝ package identity） | 性質 | 巢狀 `Deps/` | 現行 `Package.swift` 的 testTarget | 5.10 manifest 待砍 | C／ObjC 靶（須原樣保留） | Darwin-only |
|---|---|---|---|---|---|---|---|
| 1 | `HangarRash_SwiftyCapsLockToggler` | 一般 | 無 | **0** | 無 | **有**（`CapsLockToggler`，C；`path: "Framework"`） | 否 |
| 2 | `Jad_BookmarkManager` | 一般 | 無 | 1 | 1 個 testTarget | 無 | **是**（AppKit） |
| 3 | `vChewing_CandidateWindow` | 一般 | 無 | 1 | 1 個 testTarget | 無 | **是**（AppKit／SwiftUI） |
| 4 | `vChewing_FolderMonitor` | 一般 | 無 | **0** | 無 | 無 | 否 |
| 5 | `vChewing_Hotenka` | 一般 | 無 | 1 | 1 個 testTarget | 無 | 否 |
| 6 | `vChewing_IMKUtils` | 一般 | 無 | **0** | 無 | **有**（`IMKSwiftModernHeaders`，C） | **是**（IMK） |
| 7 | `vChewing_InstallerAssembly4Darwin` | 一般 | 無 | 1 | 1 個 testTarget | 無 | **是** |
| 8 | `vChewing_MainAssembly4Darwin` | 一般（含 `resources` ＋ build plugin） | 無 | 1 | 1 個 testTarget | 無 | **是** |
| 9 | `vChewing_ModifierKeyHitChecker` | 一般 | 無 | **0** | 無 | 無 | 否 |
| 10 | `vChewing_NotifierUI` | 一般 | 無 | 1 | 1 個 testTarget | 無 | **是** |
| 11 | `vChewing_OSFrameworkImpl` | 一般 | 無 | 1 | 1 個 testTarget | **有**（`OSFrameworkImplViaObjC`） | **是** |
| 12 | **`vChewing_OSNeutral_LibVanguard`** | **聚合體** | **有**（`Deps/VanguardSwiftExtension`） | **9** | 9 個 testTarget ＋ 2 個測試素材靶（`LXAssemblyMaterials4Tests`／`HomaSharedTestComponents`）＋ 1 個 CLI 執行檔（`vChewingSharedCLI`）＋ 產品清單縮為單一 static | 無 | 否（跨平台：有 `Glibc`／`Musl`／`WinSDK` 分支） |
| 13 | `vChewing_OtherIMEDataReader` | 一般 | 無 | 1 | 1 個 testTarget | 無 | 否（CommonCrypto／SQLite，無 UI） |
| 14 | `vChewing_PopupCompositionBuffer` | 一般 | 無 | **0** | 無 | 無 | **是**（AppKit） |
| 15 | `vChewing_SettingsUI` | 一般 | 無 | 1 | 1 個 testTarget | 無 | **是** |
| 16 | `vChewing_Shared_DarwinImpl` | 一般 | 無 | 1 | 1 個 testTarget | 無 | **是** |
| 17 | `vChewing_TooltipUI` | 一般 | 無 | **0** | 無 | 無 | **是** |
| 18 | `vChewing_Uninstaller` | 一般 | 無 | **0** | 無 | 無 | **是** |
| 19 | `vChewing_UpdateSputnik` | 一般 | 無 | **0** | 無 | 無 | **是** |

**表註**：

- **19 個之中，11 個有 testTarget**（第 12 項的聚合體有 9 個，其餘 10 個各 1 個）；**8 個無**。凡有 testTarget 者，其 5.10 manifest 都要把 testTarget（及其 `Tests/` 依賴）**整段略去**——見 §四與 §5.3 鐵律六。
- **巢狀 `Deps/` 只有 1 個**（聚合體，內含 `VanguardSwiftExtension`）。**但它是獨立套件，故它自己也有一組四份 manifest**（P216 已完成），且需要自己的一條 scratch（§2.4）。
- **C／ObjC 靶有 3 個**（第 1、6、11 項）。這些是**生產靶、不是測試靶**，5.10 manifest 必須原樣保留（含其 `cSettings`／`path`／`publicHeadersPath`）。
- **Darwin-only ＝ 13 個**（判準：`Sources/` 依賴 Apple 專屬 SDK——AppKit／SwiftUI／IMK／Carbon／IOKit／CoreText／Metal／AVFoundation／QuartzCore／CoreGraphics／UserNotifications 等）。此列**僅供對照**：5.10 側一律在 macOS 上建置，故不影響施工順序；它影響的是「本套件能否在 Linux／WinNT 上建置」（與本 phase 的 CI 無關，見 §八 第 9 條）。
- **第五列的「待砍」僅指 5.10 manifest**；6.2 側的 `Package.swift` 一字不動（I3）。
- **另有根 manifest**（倉根的 `Package.swift`，兩支執行檔＋`BundleApps` 插件）——依規則 2 **不在 5.10 側**，故**不需要**三份版本檔（見 §1.1 與 §9.1 末段）。
- **本表與 §9.3 的關係**：本表是**按目錄名的字母序**（＝ `ls Packages/` 的順序），供「鋪 ⓪ 基礎設施」時逐項清點；**施工次序請用 §9.3 的事主指定序**（18 項，不含聚合體）與 §十 的進度表。兩張表的目錄名一致，可互相對照。**切勿把本表的字母序當成施工序。**

封堵檔的寫法（**兩版各寫一份，內容逐字相同、只差宣告值；19 個 subpackage 各一組**）：

```swift
// swift-tools-version: 6.1
import PackageDescription

#error("""
本套件於 Swift 6.0／6.1 toolchain 下不受支援：這兩個版本既不支援 libArcLite 混編、亦不支援 Approachable Concurrency。
請改用 Swift 5.10（見 Package@swift-5.10.swift）或 Swift 6.2 以上（見 Package.swift）。
""")
```

**為何要兩份**：比對基準是**檔內宣告的 tools version**，不是檔名——6.1 toolchain 只會挑到 6.1 那一檔，只寫 6.0 一份則 6.1 toolchain 有洞可鑽。`#error` 於 manifest 編譯期即中止，訊息乾淨可讀（實測輸出含自訂訊息 ＋ `invalid manifests at […]`）。副作用是本倉自此在 6.0／6.1 下**明文拒絕建置**，而非以殘缺設定產出看似成功的東西。

**【未來擴充】** **本封堵集預期由 6.0／6.1 擴及 6.2／6.3（見 §十四 N3），現行這三份版本檔（5.10／6.0／6.1）不是終態。** 理由：Swift 6.2／6.3 對「default-isolated 下游型別遵循 default-isolated 上游協定」會噴 `#ConformanceIsolation`、要求明文 `@MainActor`（§十二 R22）。屆時每個 package 要多鋪兩份封堵檔（`Package@swift-6.2.swift`／`Package@swift-6.3.swift`），**且 `Package.swift` 的宣告值須一併抬到 6.4**——否則 6.4 toolchain 會被 6.3 封堵檔攔下（實測：「同版時 `Package.swift` 勝出」只管同版，見 P216 §13.6.4，方案 A 不成立、方案 B 成立）。

### 3.2 擇定規則（實測釘死）

> **於 `Package*.swift` 全集中，取「檔內宣告的 tools version ≤ toolchain 版本」者之最高者；同版時 `Package.swift` 勝出；宣告值高於 toolchain 者單純落選、不報錯。**

三個要點各自有實測支撐：

1. **比對基準是檔內宣告、不是檔名。** 反證：`Package.swift` 宣告 `7.0`（高於 6.4 toolchain）時不會報錯，只是被略過。
2. **同版時 `Package.swift` 優先。** `Package.swift` 與 `Package@swift-6.1.swift` 同宣告 6.1 時，前者入選。
3. **`Package.swift` 是「以自身宣告值參賽的候選」，不是永遠的 fallback。** 本倉 `Package.swift` 宣告 6.2，故 6.3.3／6.4 toolchain 取它（6.2 ＞ 6.1），而非取 `Package@swift-6.1.swift`。

### 3.3 驗收

```bash
# 5.10 側應 dump 出 @swift-5.10 版（platforms 為空、產品 type 為 static）
"$(LEGACY_TOOLCHAIN)/usr/bin/swift" package --package-path ./Packages/<pkg> dump-package
# 6.3.3 側應 dump 出 Package.swift 版（6.2 ＞ 6.1）
"$HOME/Library/Developer/Toolchains/swift-6.3.3-RELEASE.xctoolchain/usr/bin/swift" package --package-path ./Packages/<pkg> dump-package
```

【方法限制】本機**無 6.0／6.1 toolchain**，故兩份封堵檔**無法以執行驗收**，只能做內容審查（確認檔內宣告值與 `#error` 皆正確）。回報時須明列此為「未實測」項。

---

## 四、產物形態

### 4.1 兩側對照

| 面向 | 6.2+ 側（**不動**） | 5.10 側（本 phase 新增） |
|---|---|---|
| 產品型別 | Darwin：`.dynamic`（`Vanguard` → `libVanguard.dylib`；`VanguardSwiftExtension` → `libVanguardSwiftExtension.dylib`）；非 Darwin（Linux／WinNT）：`.static` | **一律 `.static`**（連 `Deps/VanguardSwiftExtension` 亦已同步改 static） |
| `platforms` | `.macOS(.v12)` | **`nil`** |
| 測試靶 | 全數保留（11 個 subpackage 有，見 §3.1） | **全數不宣告**（**鐵律六**：Unit Tests 不對 5.10 開放，§4.3） |
| 測試供料靶 | `LXAssemblyMaterials4Tests`、`HomaSharedTestComponents` 皆出貨 | **不宣告**（test-only 素材靶亦在鐵律六之列） |
| 執行檔靶 | 保留 | **不宣告**（規則 2 之必然結果：本側產出止於 `.a`，可執行檔由 Xcode 連結端產出） |
| C／ObjC 靶 | 保留 | **保留**（3 個：`CapsLockToggler`／`IMKSwiftModernHeaders`／`OSFrameworkImplViaObjC`——生產靶，非測試靶，須連 `cSettings`／`path` 一併搬） |
| 語言模式 | `swiftLanguageModes: [.v6]`（實查全倉僅聚合體一份有） | `swiftLanguageVersions: [.v5]` |
| `defaultIsolation` | 逐靶掛（§六） | 無（5.10 無此 `SwiftSetting`） |
| DSL | 聚合體那套 `@resultBuilder` | 不需要（無條件編譯需求時，直接用陣列字面量） |

### 4.2 四條形態規則的理由

1. **5.10 側一律 static**：5.10 側的宿主是 macOS 10.10 級 legacy app，其 ARC 執行期由 libArcLite 提供，而 **dylib 必須在建置期就專門摻進該靜態庫**（不能像 app 那樣由宿主統一連結），故本側不產出任何動態庫。
2. **`platforms: nil`**：PackageDescription 能宣告的 macOS 最低值只有 **10.10**，一旦宣告即被**明文寫入產物的 `LC_BUILD_VERSION`**；本側索性不宣告，讓 SDK 之預設值說話。
3. **靜態 `.a` 不帶 load command**：`vtool -show-build libX.a` 直接以 `not mach-o` 拒收。故 minOS **不進產物**、只影響 availability 檢查——而這正是我們要的（讓 5.10 側的可用性判定與 legacy 宿主一致）。
   - **例外是執行檔**：唯有可執行檔會被壓上 `LC_BUILD_VERSION`／`LC_VERSION_MIN_MACOSX` 的 minOS（本側因工具鏈地板而必為 10.13 級）。LibVanguard 側即以「不收 `vChewingSharedCLI`」避開此問題。**P217 沿此辦理，且此事已由規則 2 升格為定局**（見下一條）；唯一可能的非出貨執行檔（`vChewingDebuggable`）**已由 Q01 裁定不納入 5.10 側**，故此例外在本 phase 不會發生。
4. **終點產物是「供 Xcode 鏈接的 `.a`」（事主 2026-09-15 新規 2）**：5.10 側的產物**不是**可執行檔，也**不是**可交付的 app。最終 binary 由 **Xcode ＋ macOS 13.3- SDK** 產出，並在該處完成 **libArcLite** 與 **macOS 10.9 compatible Swift Runtime** 的摻入；OpenSource toolchain 的職責到 `.a` 為止。此條同時解釋了為何本側不宣告任何執行檔靶（§4.1 表第七列）——**不是妥協，而是分工**。

### 4.3 Unit Tests 不對 Swift 5.10 開放（事主 2026-09-15 追加規則）

**規則原文**：「**Unit Tests 不對 Swift 5.10 開放。**」

**通則**：**5.10 側 manifest 一律不宣告任何 test target**——含 **test-only 的素材靶／資料靶**（本倉的 `LXAssemblyMaterials4Tests`／`HomaSharedTestComponents` 即是）。測試**只在 6.2 側跑**（`swift test`，§十）。此條**已於 P216 在 LibVanguard 側如此實作，本條即其一般化**：P216 的 `Package@swift-5.10.swift` 正是把 `Tests/` 全目錄、9 個 testTarget、2 個素材靶與 `vChewingSharedCLI` 一併排除（§3.1 checklist 第 12 列）。逐套件的「待砍」量見 §3.1 表（19 個之中 11 個有 testTarget）。

三個層次的理由：

1. **設施本身不在**：Swift Testing 等設施非 5.10 所及（`#expect`／`#require` 皆為巨集，本倉 74 檔／3096 處**全在 `Tests/`**——見 §5.4 之（一））。
2. **目的只是「可建置」**：5.10 側的產物是供 Xcode 鏈接的 `.a`（§4.2 第 4 條），測試不在此路徑上。
3. **靶分離**：testTarget 與其依賴會把 `Tests/` 拉進建置圖；不宣告即整段不編。

**連帶好處（可直接省下工作量）**：`Tests/` 目錄下現存的 6.x-only 語法因此**不必處理**——例如 `Packages/vChewing_OSNeutral_LibVanguard/Tests/LexiconAssemblyTests/_HomaTestShim.swift:9` 的 `nonisolated extension TestLX`（全倉非 `Deps/` 區域的 5 處標頭 `nonisolated` 之一）即屬此類，**不要動它**。

**與 §2.4 的呼應**：逐套件的 5.10 makefile **不得**提供任何 test 目標（`.PHONY` 中不許出現 `test510` 之類）——本節講 manifest、§2.4 講 makefile、§5.3 鐵律六講鐵律，三處同源。

**已作廢（原④，因 Q01 連帶作廢）**：原問題為「非出貨靶（`vChewingDebuggable`）若納入 5.10 側，其 minOS／triple 如何處置？」。Q01 已裁定該靶**不納入 5.10 側**，故其產物形態問題**不存在**——本節與 §4.2 第 3 條之例外條款在本 phase **不會被觸發**。**此項自此結案，不再是待辦。**

---

## 五、語法遷移的分層規則

### 5.1 依序嘗試（越前面越好）

**(a) 單一形態即可者優先。** 以下寫法兩代通吃，**能這樣寫就不要進 `#if`**：
- 成員級 `nonisolated`（`func`／`init`／`subscript`／**計算**屬性）
- `nonisolated let`（實例儲存、不可變）
- `nonisolated(unsafe) var`（**僅 class** 的儲存屬性需要）

**(b) 把標頭上的修飾詞下放到成員。** 主力 codemod，規則為：

> 把 `nonisolated extension X { … }`／`nonisolated class X { … }` 標頭上的 `nonisolated` 拿掉，改寫到**每個成員**之首；儲存屬性 `let` → `nonisolated let`、可變 `var` → `nonisolated(unsafe) var`；`deinit`／`case`／續行（`)`、`->`）／註解／`#if` 一律不動。

P216 的 codemod 腳本留在工作區：`_MainWorkspace/tmp/p126pushdown.py`（extension 版）、`tmp/p126pushdown_types.py`（型別版）。**新一輪使用前必須先在單檔上驗，不可直接對全倉跑**（理由見 §八）。

**(c) 真的下放不了者，整段宣告以 `#if compiler(>=6.2)` 分隔**，<6.2 分支採 `vChewing-OSX-legacy` 的寫法。適用對象：
- **enum 帶 `case`**、**帶合成 conformance 的 struct**（`Hashable`／`Codable`／`CaseIterable`）——沒有成員可掛
- **巢狀型別**（無法在自己身上掛 `nonisolated`）

三個必須記住的否定結果：
1. **`#if compiler(>=6.2)` 只夾住修飾符是無效的**。`#if` ／ `nonisolated` ／ `#endif` ／ `struct S {}` 這種寫法，5.10 之所以「通過」只是因為整個分支被編掉；**6.x 會直接報 `cannot find 'nonisolated' in scope`**。只能**整段宣告各寫一份**。
2. **struct 的儲存屬性不可標 `nonisolated`**：值型別的儲存屬性永不受 actor 隔離拘束；標了在 5.10 是 `'nonisolated' is redundant on struct's stored properties`、在 Swift 6 直接是**錯誤**。
3. **把巢狀型別「拖出 namespace 到檔案層級」不會解除其隔離**（實測：檔案層級型別在 `defaultIsolation` 下同樣受拘束），它只是形狀整理。

**(d) 長 body 的型別／長 symbol 的實作，可依實際情況移進 `extension`（事主 2026-09-15 新規 6）。** 用途有兩層：① 形狀整理；② **縮小 `#if compiler(>=6.2)` 兩分支的複製面積**——因為 (c) 的分隔必須「整段宣告各寫一份」，把**實作**（長 body、長 symbol）挪進 `extension` 之後，兩分支就只剩「宣告殼」需要各寫一次，重複量大幅下降。此手法與 (b) 的下放互補：先 (b) 下放修飾詞，再 (d) 把 body 挪出去。

**(e) 提煉共用的 `fileprivate protocol`，讓兩版共用業務邏輯（P216 時期手法，2026-09-15 補記入本規範）。** 事主於 P216 曾提示：「若嫌重複內容太多，可提煉共用的 `fileprivate protocol`，讓兩版藉由 protocol 共用業務邏輯」。與 (d) 並列使用：`extension` 負責搬走 body、`fileprivate protocol` 負責讓兩分支共用同一份實作，兩者合起來可把 (c) 的重複降到最低。

**(f) SwiftUI 之任何內容，一律以 inline compiler condition 僅限 6.2+（事主 2026-09-15 新規 4）。** 範圍包含 **SwiftUI 本體與一切與之相關的 Swift macro**——**明確含 `#Preview`**（事主 2026-09-15 追加規則：「`#Preview` 也是 macro、需要用 compiler version 處理掉的」）**與 `@Observable`**（及其所屬的 `Observation` 模組；本倉 `PEReloadEventObserver.swift`、`SettingsUIViewModel.swift` 兩處即為現成實例）。寫法一律為整段包進 `#if compiler(>=6.2)`（…`#endif`），<6.2 分支**不提供**任何替代實作。
　**`#Preview` 之機理（為何非圈不可）**：`#Preview` 是 **SwiftUI 的巨集**，其展開結果**需要 macOS 14 級的 preview 執行期**，且展開本身**需要 Xcode 的 `PreviewsMacros` 外掛**——在 5.10 側（OpenSource toolchain、部署目標 10.10、SDK 13.3）**必失敗**。它特別容易漏，因為它常躲在 preview-only 碼裡、看起來「不影響出貨」；**本倉實測有 17 處、分布於 17 個檔**（§5.4 之（一））。
　**圈隔範圍：整段包住。** 含 `#Preview` **其內宣告的 preview 專用型別**（helper view、閉包內型別、preview 專用的輔助宣告）在內，**不可只包修飾詞**——理由即 §5.1 的否定結果 1：只夾住修飾符的寫法在 6.2 側會直接報錯。遇既有 `#if DEBUG` 守衛者（本倉僅 2 檔），**在既有守衛之內再加一層**，不得拆掉既有守衛。
　**沿革**：本條**取代**本 SOP 初稿僅把 `Observation`／`@Observable` 當作「風險點」提及的寫法——那不是待補事項，而是**已經定案的硬性規則**。`#Preview` 之具名係 2026-09-15 事主追加規則所補（原條文之「相關 Swift macro」已可涵蓋，但**必須具名**——不具名則施工者極易把它當成「不影響出貨」而漏掉）。同一精神另立為 §5.3 鐵律五。**另注（Q03）**：SwiftUI 的 availability 一律 macOS 14+，與本條之圈隔互為表裡。

**(g) 可直接繼承自 Legacy Repo 者，優先繼承（事主 2026-09-15 新規 3：「AppKitDSL 或可直接繼承自 Legacy Repo」；判準經裁定 Q02 定案）。** 遇到 (a)～(f) 皆難纏的模組（尤以 AppKit 相關者），先自問「legacy 倉怎麼寫的」——**legacy 的寫法本身就是 5.10 側相容寫法的現成答案**（§6.1「那一刀」正是照抄 legacy 形狀而得）。**判準（Q02）：legacy 倉＝本倉的「子集 ＋ Swift 5.10 Dialect」，其子集性來自「砍掉了 SwiftUI」——故「可繼承者」≒ 該模組在 legacy 的子集副本（非 SwiftUI 部分）。** 逐件 case-by-case 確認；判定步驟與紅線見 §1.3，**清單不預先列出、於施工時逐件記錄**。

**(h) 呼叫引數列尾逗號：當且僅當 5.10 報錯時，依 case-by-case 原則修復（事主 2026-09-15 新規 9）。** 不再一律刪除——**沿革：本條取代 P216 時期之 A10「尾逗號一律刪掉」**。理由已在 P216 §十 第 4 條釐清：**沒有任何一支工具會把呼叫引數列尾逗號加回來**（`swiftlint --fix` 與 `swiftformat` 單獨跑都不動它），故刪與不刪都**不需要**動 `.swiftformat`／`.swiftlint.yml`；既然如此，就沒有理由為了一個只在 5.10 觸發的語法去改動大量 6.2 側既有碼。遇 5.10 報 `unexpected ',' separator` 時才就該處修，其餘原樣。

**一個必須記住的否定結果（承 (c)～(h)）**：`#if compiler(>=6.2)` 的分隔**只適用於「整段宣告／整段碼」**；任何「只夾住修飾符」或「只夾住半個運算式」的寫法都是無效的（見上方否定結果 1）。

### 5.2 代際語法矩陣（摘要）

**5.10 拒收、6.x 接受**：

| 寫法 | 5.10 的反應 |
|---|---|
| `nonisolated extension X { … }` | `'nonisolated' modifier cannot be applied to this declaration` |
| `nonisolated struct／enum／class` | 同上 |
| `nonisolated deinit` | SE-0371（Swift 6.1）語法，拒收 |
| **裸** `nonisolated var` 掛儲存屬性 | `'nonisolated' can not be applied to stored properties` |
| `@retroactive` 掛 conformance | `unknown attribute 'retroactive'`（並連帶把 `LocalizedError` 誤解析成 `any LocalizedError`） |
| `class X: @MainActor SomeProtocol` | SE-0434 隔離同構；報 `unknown attribute 'MainActor'` ＋ `inheritance from non-protocol, non-class type 'any …'` |
| 呼叫引數列尾逗號 | SE-0439（Swift 6.1），報 `unexpected ',' separator`——**唯此一項採 case-by-case，不一律修（規則 9，見 §5.1(h)）** |

**5.10 接受、且與 6.x 通吃**：成員級 `nonisolated`（`func`／`init`／`subscript`／計算屬性）、`nonisolated let`（實例儲存、不可變）、`nonisolated(unsafe) var`（僅 class 儲存屬性需要）、`@MainActor` 掛型別／成員（**但見 §5.3 禁則一**）、`#if compiler(>=6.2)` 分隔**整段宣告**。

註：`@backDeployed` 本身**不是**代際問題（SE-0386，Swift 5.9 起即有）——§七 的退休理由是跨模組 overload ambiguity，不是 5.10 拒收。

註（2026-09-15 新增）：本表所列「拒收」項中，**唯一不採「一律修掉」策略的是尾逗號**（規則 9，見 §5.1(h)）；其餘各項皆須實際處置。另，SwiftUI 相關內容——**含 `#Preview` 這類巨集**——**不在本表內**：那不是代際語法差異，而是**專案策略**：一律以 `#if compiler(>=6.2)` 圈起（規則 4 ＋ 2026-09-15 事主追加之 `#Preview` 規則，見 §5.1(f) 與 §5.3 鐵律五；實測數字見 §5.4 之（一））。

### 5.3 六條鐵律（禁止事項）

1. **不得為消錯而新增 `@MainActor`。** `MainActor` 屬 Swift Concurrency，需 macOS 10.15 起的執行期；新增即**殺死對 macOS 10.14 為止所有系統的相容性**（P216 §七 事主明令）。P216 結束時 `Sources/` 僅存 1 處 `@MainActor`，且位於 `#if compiler(>=6.2)` 分支內。
2. **不得刪功能。** 遇無法兩全者，改寫、不刪除；真無解則列為殘留並回報。
3. **不得放寬 `swiftLanguageVersions`。** 5.10 側固定 `[.v5]`。
4. **不得動已定讞的 `Deps/VanguardSwiftExtension`**（含其四份 manifest 與 `Sources/`）——它是 I2 的錨點；動它即同時打破兩倉 byte-sync。
5. **不得讓 SwiftUI 之任何內容裸露於 5.10 可編的路徑上（事主 2026-09-15 新規 4）。** 範圍含 SwiftUI 本體與一切相關 Swift macro——**明確含 `#Preview`**（事主 2026-09-15 追加規則；機理與範圍界定見 §5.1(f)）**與 `@Observable`**。一律以 inline compiler condition 圈進 `#if compiler(>=6.2)`，<6.2 分支**不提供替代實作**；`#Preview` 所在處須**整段包住**（含其內宣告的 preview 專用型別）。**操作上的意涵**：5.10 側根本不會編到這些碼，故「`Observation` 等 macOS 14 期模組是否隨 MacOSX13.3.sdk 提供」、「`PreviewsMacros` 外掛是否可得」**皆不構成 P217 的技術風險**——這正是本條的價值所在。
6. **Unit Tests 不對 Swift 5.10 開放（事主 2026-09-15 追加規則）。** 5.10 側 manifest **不得宣告任何 test target**，亦**不得宣告 test-only 的素材靶／資料靶**；逐套件的 5.10 makefile **不得提供 test 目標**。測試只在 6.2 側跑。此條之一般化依據與逐套件的「待砍」量見 §4.3 與 §3.1；**它同時是 §九「⓪ 基礎設施先鋪」能成立的前提**——若 5.10 側還要兼顧測試，逐包驗證的最小單位就不存在了。**注意區分（事主 2026-09-15 補述）**：§2.4 的逐包 makefile 所提供的 `make build510` 是**可建置性驗證（compilation test），不是單元測試**——前者在 5.10 側做、後者只在 6.2 側做，兩者互補而不衝突。

### 5.4 本倉現況普查（2026-09-15，動工前；**不含 `Deps/`**，該處已於 P216 處置完畢）

```bash
cd /Users/shikisuen/Repos/_vChewing/_MainWorkspace/vChewing-macOS
grep -rn --include=*.swift -E '^[[:space:]]*nonisolated[[:space:]]+(extension|class|struct|enum|actor)' Sources Packages | grep -v '/Deps/'
grep -rn --include=*.swift -E 'nonisolated[[:space:]]+deinit' Sources Packages
grep -rn --include=*.swift '@retroactive' Sources Packages | grep -v '/Deps/'
grep -rn --include=*.swift -E ':[[:space:]]*@MainActor[[:space:]]' Sources Packages | grep -v '/Deps/'
```

| 形態 | 命中 | 位置 | 處置 |
|---|---|---|---|
| `nonisolated extension` | 2（＋1 在 Tests） | `Packages/Jad_BookmarkManager/Sources/BookmarkManager/BookmarkManager.swift:308`（`NSKeyedUnarchiver`）、`Packages/vChewing_MainAssembly4Darwin/.../LXManager/UserPhraseImpl.swift:11`（`FileHandle`，見 §七） | (b) 下放至成員；FileHandle 那處直接隨 §七 整組退場 |
| `nonisolated enum` 帶 `case` / `nonisolated struct` 帶合成 conformance | 2 | `Packages/vChewing_OSFrameworkImpl/.../AppKitImpl/AppKitImpl_Misc.swift:119`（`enum MeasurementPath: Hashable, Sendable`）、`:121`（`struct CacheKey: Hashable, Sendable`） | (c) 整段 `#if compiler(>=6.2)` 分隔 |
| `nonisolated deinit` | 2 | `Packages/vChewing_SettingsUI/.../SettingsUI/CtlSettingsUI.swift:15`、`.../SettingsCocoa/CtlSettingsCocoa.swift:43` | 樸素寫法 ＋ `mainSync`（§六） |
| `@retroactive` | 6 | `Tekkon_Phonabets.swift:243`、`UserDefRenderable.swift:86`、`NSEventImpl_Shared.swift:10`、`OSFrameworkImpl/SwiftUIImpl.swift:167`、`InputSession_DarwinSurface.swift:16`、`LXMgr_KimoDataParser.swift:9` | 5.10 拒收 → 逐處改寫或 `#if` |
| `: @MainActor <Protocol>` | 3（均非真協定同構） | `Tests/LibVanguardTests/.../MockedInputHandlerAndStates.swift:17,84`（Tests，5.10 側不編）、`Sources/LexiconAssembly/vChewingLXAssembly_Common.swift:76`（**參數位置的 `@MainActor` autoclosure 標註**，即 P216 §十一 第 3 項唯一保留處） | 僅 Tests 兩處可略；實際「協定同構」隱患已於 P216 清空 |

**普查之已知漏收（2026-09-15，① 之實測發現；規則本體不變，僅此補記）**：上表所列用的正則要求 `nonisolated` **緊接** `extension|class|struct|enum|actor`，故**被其他修飾詞隔開者一律漏收**——實例即 `Packages/vChewing_OSFrameworkImpl/Sources/OSFrameworkImpl/SecureEventInputSputnik.swift:110` 的 `nonisolated public struct ActivationFlags: OptionSet, Sendable`（被 `public` 隔開），該處**不在上表所列的 2 處之內**，係 ① 以編譯器診斷實測發現（已依 §5.1(c) 收掉）。**下一次普查若要收緊，於正則的 `nonisolated` 與型別關鍵字之間容許修飾詞即可**；本 phase 不動規則本體。

**判讀**：P216 已把最重的一刀（`@MainActor` 自協定撤除，1771 筆錯誤一併歸零）在共享的 `Sources/` 上做完，故 macOS-only 的 `Packages/*` 這一側**剩下的量很小**（標頭 `nonisolated` 5 處、`nonisolated deinit` 2 處、`@retroactive` 6 處）。真正的成本在**manifest 三件套 × 18 個 package**、**§七 的 FileHandle 遷移**、以及**規則 4 的 SwiftUI 圈隔**，不在隔離語法。

**SwiftUI／`Observation` 的普查（2026-09-15）**——這些**全屬 §5.1(f)／§5.3 鐵律五**之範圍，即：**一律以 `#if compiler(>=6.2)` 圈起**：

```bash
grep -rln --include=*.swift 'import SwiftUI' Sources Packages | grep -v '/Deps/'
grep -rn  --include=*.swift 'import Observation\|@Observable' Sources Packages | grep -v '/Deps/'
```

| 形態 | 命中 | 分布 |
|---|---|---|
| `import SwiftUI` | **30 檔** | `vChewing_SettingsUI` 18、`vChewing_CandidateWindow` 4、`vChewing_InstallerAssembly4Darwin` 3、`vChewing_OSFrameworkImpl` 2、`Sources/vChewingDebuggable` 2、`vChewing_Shared_DarwinImpl` 1 |
| `@Observable` | **3 處** | `Sources/vChewingDebuggable/ContentView.swift:88`、`Shared_DarwinImpl/PEReloadEventObserver.swift:12`、`SettingsUI/SettingsUIViewModel.swift:12` |

**注意**：`vChewing_SettingsUI` 與 `vChewing_CandidateWindow` 兩者皆在規則 1 的**收斂序**上，且恰好是 SwiftUI 佔比最高的兩個元件——故規則 4 的圈隔工作量**集中在收斂階段**，不是均勻分布的。`vChewing_OSFrameworkImpl` 一檔之內混有 SwiftUI（`SwiftUIImpl.swift`）與 AppKit（`AppKitImpl_*`）者，須**逐檔判斷界線**，不可整檔包 `#if`（§5.1(f) 的範圍限定於 SwiftUI 之內容，AppKit 內容照常可編）。

#### 5.4.1 巨集（macro）普查（2026-09-15，排除 `Deps/`；全倉 349 個 Swift 檔）

**複製用命令**：

```bash
cd /Users/shikisuen/Repos/_vChewing/_MainWorkspace/vChewing-macOS
L=$(grep -rl '' --include=*.swift Sources Packages | grep -v '/Deps/')
# 先取全體 `#` token 再分類（可看出有無漏網之巨集）
grep -rhoE '#[A-Za-z_][A-Za-z0-9_]*' $L | sort | uniq -c | sort -rn
for s in '#Preview' '#Previewable' '#Predicate' '#Playground' '#expect' '#require'; do
  echo "$s: $(grep -rhoE "${s}\b" $L | wc -l) 命中 / $(grep -rlE "${s}\b" $L | wc -l) 檔"
done
for a in '@Observable' '@Bindable' '@Model' '@Entry' '@Previewable' '@Query'; do
  echo "$a: $(grep -rhoE "${a}\b" $L | wc -l) 命中 / $(grep -rlE "${a}\b" $L | wc -l) 檔"
done
grep -rn --include=*.swift -E '#externalMacro|@freestanding|@attached|MacroImplementation|CompilerPlugin' Sources Packages | grep -v '/Deps/'
```

**（一）巨集呼叫（freestanding macro，`#` 起首）**

| 巨集 | 命中 | 檔數 | 處置 |
|---|---|---|---|
| **`#Preview`** | **17** | **17** | **須圈隔**（§5.1(f)／§5.3 鐵律五）；落點分布見（四） |
| `#Previewable` | **0** | **0** | — |
| `#Predicate` | **0** | **0** | — |
| `#Playground` | **0** | **0** | — |
| `#expect` | 3096 | 74 | Swift Testing 巨集；**74 檔全在 `Tests/`**（實查：非 `Tests/` 者 **0** 檔）→ 5.10 側不編，無須處理 |
| `#require` | 45 | 13 | 同上（全在 `Tests/`） |
| `#_sourceLocation` | 1 | 1 | 同上（`HotenkaTests/HotenkaTestSupport.swift:36`） |
| `#bundle` | 1 | 1 | Foundation 巨集；位於 `Sources/LXAssemblyMaterials4Tests/TestData.swift:29`——**測試材料靶**，5.10 manifest 不宣告該靶，無須處理 |
| 其他 `#` token | — | — | **皆非巨集**：`#available`(130)／`#if`(76)／`#endif`(71)／`#selector`(77)／`#unavailable`(32)／`#else`(29)／`#elseif`(9)／`#error`(5)／`#line`(2)／`#function`(2)／`#filePath`(1)／`#dsohandle`(1) 為**語言內建指令**；`#PRAGMA`(69／7 檔) 與 `#D41J0U8U`(1)、`#import`(2) 為**假陽性**——前者是 `Tests/` 內字串常值與註解中的詞庫檔格式標記（`#PRAGMA:VANGUARD_HOMA_LEXICON_*`），後兩者是字串內的密碼遮蔽字樣與註解引述之 ObjC 標頭 |

**（二）巨集屬性（attached macro）**

| 屬性 | 命中 | 檔數 | 落點 |
|---|---|---|---|
| `@Observable` | **3** | **3** | `Sources/vChewingDebuggable/ContentView.swift:88`、`Shared_DarwinImpl/PEReloadEventObserver.swift:12`、`SettingsUI/SettingsUIViewModel.swift:12` |
| `@Bindable` | **3** | **1** | `SettingsUI/SettingsUI/VwrSettingsUI.swift:18,72,178` |
| `@Model` | **0** | **0** | —（SwiftData 巨集，本倉未用） |
| `@Entry` | **0** | **0** | — |
| `@Previewable` | **0** | **0** | — |
| `@Query` | **0** | **0** | — |

**對照組（非巨集，但同屬 §5.1(f) 圈隔範圍）**：`@State` 51、`@AppStorage` 14、`@Environment` 6、`@Binding` 5、`@StateObject` 1。這些是 **property wrapper（型別）而非巨集**——不需個別圈隔，隨其所在的 SwiftUI 檔一併處理即可。列出僅為免施工者誤把它們當成巨集來算工作量。

**（三）巨集宣告**

| 宣告 | 命中 | 說明 |
|---|---|---|
| `#externalMacro` | **0** | 本倉**無自製巨集** |
| `@freestanding` | **0** | 同上 |
| `@attached` | **0** | 同上 |
| `MacroImplementation` | **0** | 同上 |
| `CompilerPlugin` | **0** | 同上；`Plugins/BundleApps/plugin.swift` 是 **CommandPlugin（命令插件）**，與巨集無涉 |

**（四）巨集落點與收斂序的對應**

| 巨集 | 命中 | 落點 package（檔數） | 階段 |
|---|---|---|---|
| `#Preview` | 13 | `vChewing_SettingsUI`（`SettingsCocoa/VwrSettingsPaneCocoa*` 12 ＋ `SettingsCocoa/VwrSettingsCocoaPanes.swift` 1） | **收斂**（第 2 位） |
| `#Preview` | 2 | `vChewing_CandidateWindow`（`TDK4AppKit/_GSI4AppKit_Previews.swift`、`TDK4AppKit/_TDK4AppKit_Previews.swift`） | **收斂**（第 3 位） |
| `#Preview` | 1 | `vChewing_InstallerAssembly4Darwin`（`AppKit/VwrAppInstaller4Cocoa.swift:645`） | **收斂**（第 1 位） |
| `#Preview` | 1 | `Sources/vChewingDebuggable/ContentView.swift:472` | **非出貨靶；不納入 5.10 側**（Q01）——故**不需圈隔**，列此僅為數字完整 |
| `@Observable` | 1 | `vChewing_Shared_DarwinImpl`（`PEReloadEventObserver.swift:12`） | **擊破**（L2） |
| `@Observable` | 1 | `vChewing_SettingsUI`（`SettingsUIViewModel.swift:12`） | **收斂** |
| `@Bindable` | 3（1 檔） | `vChewing_SettingsUI`（`VwrSettingsUI.swift`） | **收斂** |

**結論**：巨集圈隔**幾乎全數落在收斂階段**——17 處 `#Preview` 之中有 **16 處**位於收斂序的三個元件（`SettingsUI` 13、`CandidateWindow` 2、`InstallerAssembly4Darwin` 1），僅 **1 處**在非出貨靶；`@Observable`／`@Bindable` 亦集中於 `SettingsUI`。擊破階段唯一觸及者是 `Shared_DarwinImpl` 的 **1 處** `@Observable`。故**巨集圈隔不是均勻分布的工作，而是收斂階段的主要工作量來源之一**（見 §十二 R19）。

**（五）兩個必須記住的細節**

1. **`@available(macOS 14.0, *)` 擋不住巨集展開。** 實例：`Packages/vChewing_SettingsUI/Sources/SettingsUI/SettingsCocoa/VwrSettingsCocoaPanes.swift:95-98` 正是 `@available(macOS 14.0, *)` 緊接 `#Preview(traits: .fixedLayout(width: 600, height: 768)) { SettingsPreview() }`——在 5.10 側**仍會失敗**，因為 `@available` 是可用性標註、而巨集必須在**編譯期展開**。此與 §5.5 的 availability 政策不衝突：規則 5 管「可用即用」，圈隔管「編譯期能否展開」，兩者層次不同。
2. **既有 `#if DEBUG` 守衛者，在既有守衛之內再加一層，不得拆掉既有守衛。** 實查：17 檔中僅 `vChewing_CandidateWindow` 的兩個 `_*_Previews.swift` 有 `#if DEBUG`（`_TDK4AppKit_Previews.swift:9` 至 `:166` 包住整檔）；其餘 **15 檔並無 DEBUG 守衛**（**既有現象、非本 phase 造成**）。**本 phase 不改動 DEBUG 語義**——那是範圍外的清理（§1.3：「重構、改名、清死碼一律不做」），且會改變 6.2 側 release 產物的內容（與 I3「6.2 側行為一字不變」相牴觸）。**只加 `#if compiler(>=6.2)`，不動 `#if DEBUG`。**

### 5.5 availability 與 `#unavailable` 政策（事主 2026-09-15 新規 5）

**本節取代本 SOP 初稿對 availability 的零散處理方式**（初稿只在 §2.3 與 §4.2 的 minOS 敘述裡順帶提及，未成政策；後經**規則 5** 與**裁定 Q03** 先後定案）。今後一律照本節辦理：

1. **`@available(macOS 14, *)` 這類 API 可優先使用，與 `if #unavailable` 無關。** 即：不必為了「讓舊編譯目標過關」而迴避高版本 API；凡 API 本身可用即用之，再以 `@available` 標註。
2. **若仍需 `#unavailable`，一律採 `if #unavailable() {} else {}` 的完整兩分支寫法。** 理由（事主原話）：為防止後者在某些場合可能出現編譯錯誤。**不得**使用不完整的單分支形式。
3. 遇「該 API 在目標版本根本不可用」時，走 §5.1(c) 的 `#if compiler(>=6.2)` 或本節的第 2 條兩分支；**不得**以刪功能迴避（§5.3 鐵律二）。

**沿革（本條修正 P216 提示的適用範圍）**：P216 原始提示中有「最低版本沒必要這麼低時的 deprecated 警告用 `if #unavailable` 處理」一語。**本條修正的正是它**——P216 實測顯示該類問題的**真實形態是 availability 錯誤，而非 deprecation 警告**，三個實例皆有紀錄：

| 實例 | 真實形態 | 出處 |
|---|---|---|
| `@MainActor` | 需 macOS **10.15** 起的執行期（屬 Swift Concurrency） | §5.3 鐵律一之源 |
| `Data` | 型別本身標為 macOS **10.10** 起可用 | §二 部署目標之源 |
| `read(upToCount:)` | 需 macOS **10.15.4** 起 | §七 FileHandle 糖之源 |

即：那些不是「最低版本訂得太低所以吃到 deprecated 警告」，而是「事件本身在該版本**根本不可用**」。故對策是 `@available` ＋ 完整兩分支 `#unavailable`，**不是壓警告**。

**與 §4.2 的關係**：本政策只規範「原始碼端如何標註 availability」；產物端的 minOS 仍由 §4.2 決定（`platforms: nil` ＋ `-Xswiftc -target` ＋ 靜態 `.a` 不帶 load command）。兩者**互不替代**。

---

## 六、隔離與調度方針

### 6.1 兩側的隔離落差

- **6.2 側**：`defaultIsolation(MainActor.self)` 出現於**全部 21 份 manifest**（根 1 ＋ `Packages/*` 19 ＋ 巢狀子套件 1），但**逐靶掛**——聚合體內有**四個**靶**刻意不在名單上**（實查其 `swiftSettings` 為空）：**`ResourceLocator`、`TrieKit`、`Tekkon`、`Homa`**。其中 **`Tekkon` 與 `Homa` 即事主裁定 Q05 所稱者**——「已經相容，都在 P216 解決了；這兩個 target 的建置**沒有被釘死在 MainActor 上**」，故其 `nonisolated(unsafe)` 合法且與 legacy 同步（§6.4）。實務含義：**其餘全體回 MainActor**。
- **5.10 側**：無此 `SwiftSetting`（tools 6.2 起才有）。此落差曾以 **1771 筆錯誤**（1052 ＋ 719）的形式爆發，看似硬仗，實則**只有兩個根因，一刀可解**。
- **那一刀**：把 `@MainActor` 自協定撤除，改採 legacy 的寫法（事主原話：「Legacy 怎麼寫，你就怎麼寫；你把 `@MainActor` 從 Protocol 撤掉」）。P216 實查 legacy 倉本來就沒有宣告層級的 `@MainActor`，**只改 3 行**即令 1052 ＋ 719 一併歸零。
- **機理**：協定一旦不再是 `@MainActor`，5.10 側整個層就是**全體一致的 nonisolated**，主客體之間的隔離落差消失；而 6.2 側因 `defaultIsolation`，協定拿掉顯式標註後**仍然是 MainActor**、語義不變。**這是唯一的「單一形態、零取捨」大手術**，P217 若再遇同型錯誤，先找協定同構，不要逐成員補標註。

### 6.2 調度方針

事主原話：

> non-MainActor 只用於調度，任務都還是在 MainActor 上跑。如果需要在指定的 DispatchQueue 內運行的東西的話，那麼輪到這個 Queue 執行 closure 的時候、就將裡面的內容用 `mainSync` 包裹。

**一個必踩的互鎖陷阱**：`queue.sync { mainSync { … } }` **必定死鎖**——呼叫方全在 MainActor，main 卡在 `queue.sync`，而佇列執行緒的 `mainSync` 又等 main。故必須寫成「已在主執行緒就直接跑，否則才 `queue.sync { mainSync { … } }`」：

```swift
func withFileHandleQueueSync<T>(_ body: () throws -> T) rethrows -> T {
  if Thread.isMainThread { return try body() }          // 快徑：避免自鎖
  return try queue.sync { try mainSync { try body() } }
}
```

`Thread.isMainThread` 快徑是**全倉唯一未能照字面貫徹之處，已獲事主核可**。

**當 `mainSync` 可能造成死鎖時，酌情改用 `asyncOnMain`（事主 2026-09-15 新規 7）。** 兩者的差別在「等不等」：`mainSync` 是**同步等待** main 執行完再返回；`asyncOnMain` 則**把工作排進 main 佇列、不等待**。凡「呼叫鏈已在 main 上、或可能以任何路徑回到 main」之處，`mainSync` 都有自鎖風險（與上方 `queue.sync { mainSync { … } }` 同一病根）。判準依序自問：

1. 此處**必須**拿到結果才能繼續？（只有「是」才需要 `mainSync`）
2. 呼叫方是否可能已經在 main？（若是 → 必須有 `Thread.isMainThread` 快徑，或改 `asyncOnMain`）
3. 若拿不到結果也能繼續（fire-and-forget，或後續動作可改以回呼／狀態通知銜接）→ **直接用 `asyncOnMain`**，不要用 `mainSync` 硬等。

**兩個不能忘的邊界**：① **`deinit` 內不可用 `asyncOnMain`**（其為 async，而 `deinit` 不可逃逸），故 §6.3 仍以 `mainSync` 為唯一手段；② 本條與 §七 的 `withFileHandleQueueSync` 是**同一組問題的兩種解法**——§七 走「呼叫方快徑」（已在 main 就直接跑），本條走「不等待」，兩者可並用。

#### 6.2.1 Queue 的角色與三條並發紀律（事主裁定 Q06）

**`withFileHandleQueue*` 不用退役（Q06）**，但其角色與寫法自此明文化。事主原文：

> 這個 Queue **只管任務觸發時機**，實際的 lambda expression 內的任務執行仍舊**套一圈 MainActor `mainSync`**（**需要以 `mainSync {}` 觸發、而非 `{ @MainActor in }` 等不相容寫法**）。**POM 相關的 Queue 同理。**然而，你得注意，**不能讓同一個檔案被多個 Actor 同時讀寫**。

**紀律 A｜Queue 只管「觸發時機」。** 佇列的存在意義**不是**「把工作搬到別的執行緒跑」，而是**決定何時啟動**；**任務本體一律回到 MainActor 執行**。故一個正確的形狀是「main → 序列佇列（僅決定時機）→ `mainSync` → main」，其中間那一跳**不承擔並發**。（P216 曾把此層描述為「三跳繞路、臨界區已被 MainActor 天然序列化」——**該描述仍成立**，但處置由「建議退役」改為「**保留，並把角色釘死為時機控制**」。）

**紀律 B｜一律以 `mainSync {}` 觸發，禁用不相容寫法。** 實際的 lambda expression 內的任務執行，**必須**以 **`mainSync {}`** 包裹；**不得**改用 `{ @MainActor in … }`（或同類的隔離標註）——那在 5.10 側不相容（見 §5.2 矩陣：`@MainActor` 在型別／成員以外的位置一律有代際風險）。**POM 相關的 Queue 同理**——同一規則適用於全部 dispatch 佇列，不是單一 API 的特例。

**紀律 C｜同一檔案（同一資源）不得被多個 Actor 同時讀寫。** 這是最容易被「反正都回到 MainActor 了」這個印象蓋掉的一條：**佇列的序列性只保證「同一佇列上的任務不並行」，不保證「同一檔案不被兩個 actor 同時碰」**。凡同一路徑／同一 handle 可能同時被 MainActor 與某個非 MainActor 上下文觸及者，必須**收斂到單一 actor**（本 phase 即收斂到 MainActor）或有明確的互斥；**不得**以「都在一個 Queue 上」推論其安全。**此條約束整個 §六**，並見 §十二 R21。

**與 §6.3 的關係**：`deinit` 仍只能用 `mainSync`（不可 `asyncOnMain`，見上）；此與紀律 B 一致——`mainSync {}` 是本 phase 唯一的跨 actor 觸發形式。

### 6.3 `deinit`

`nonisolated deinit` 是 SE-0371／Swift 6.1 語法、**5.10 拒收**。一律**樸素寫法 ＋ 把內容用 `mainSync` 裹上**。本倉兩處（§5.4 表格）即照此辦。

**`deinit` 是規則 7 的例外**（見 §6.2 邊界①）：其為同步上下文、不可 `await`，故不能改用 `asyncOnMain`。若在其中遇上死鎖風險，處置方式是**把工作移出 `deinit`**（例如改由明確的 teardown 方法在生命週期早期執行），**不是**改調度原語。

### 6.4 `NSMutex` 的退場條件

既然全體回到 MainActor，`NSMutex` 保護的共享狀態即可改回普通 stored property。**但有四個例外**：**`ResourceLocator`、`TrieKit`、`Tekkon`、`Homa`** **不在** `defaultIsolation` 名單上（實查其 `swiftSettings` 為空，與 §6.1 一致），故 `NSMutex` 這個型別本身仍須能從 nonisolated 情境使用——其定義留在 `Deps/VanguardSwiftExtension`，以 `#if compiler(>=6.2)`／<6.2 兩分支分隔。**P217 不得為「清乾淨」而把它拆掉。**

**已定案（事主裁定 Q05）：`Tekkon.sharedCache` 不用處理，且 `Tekkon`／`Homa` 兩靶不在 `defaultIsolation` 的施行範圍內。**

事主原文：「**Tekkon 與 Homa 都不用處理**，因為已經相容，**都在 P216 解決了**。這兩個 target 的建置**沒有被釘死在 MainActor 上**，且 Legacy 倉庫的寫法目前也是 `nonisolated(unsafe) private static var sharedCache: [Int: PinyinTrie] = [:]`。」

三點落地：

1. **`Tekkon` 與 `Homa` 兩靶不納入 default isolation 的施行範圍**——該兩靶在 **P216 已達成雙 toolchain 相容**（P216 全倉最終只剩 1 處 `#if compiler(>=6.2)`，且不涉及它們的隔離）。故其 `nonisolated(unsafe)` **非但可留、且與 legacy 同步**（legacy 寫法逐字相同）。
2. **`Packages/vChewing_OSNeutral_LibVanguard/Sources/Tekkon/Tekkon_PinyinTrie.swift:110` 的 `nonisolated(unsafe) private static var sharedCache` 維持原樣**，P217 不動它——既不搬進 Sendable 盒、也不為它改 manifest。（本條與 §6.1 所載「`TrieKit`／`Tekkon` 兩靶不在 `defaultIsolation` 名單」**一致**：正因不在名單，才需要且允許 `nonisolated(unsafe)`。）
3. **注意其在共享 `Sources/` 內**：若日後真要動它，仍觸發 I2 的兩倉鏡像——但本 phase 已定為不動。

**已定案（事主裁定 Q06）：`withFileHandleQueue*` 不用退役**，並樹立三條紀律（**詳見 §6.2**，該處為本裁定之正本）：Queue 只管**觸發時機**、內容一律以 `mainSync {}` 觸發（**禁用 `{ @MainActor in }` 等不相容寫法**）、**POM 相關 Queue 同理**、以及**同一檔案不得被多個 Actor 同時讀寫**。

---

## 七、共用設施的貫徹：FileHandle 語法糖

### 7.1 病與藥

**病**：`@backDeployed(before: macOS 10.15)` **同名重宣告**是昏招。它在本模組內重複宣告 Foundation 的同名 API，令**跨模組呼叫點落入 overload ambiguity 而無法編譯**。本倉的 `SwiftExtension` 因此長期把整段 shim 註解掉，而 `LexiconAssembly` 又另有一組作用中的同類 shim——兩模組各宣告一次 `FileHandle.seek(toOffset:)`，正是同一個病的兩種表現。

**藥（P216 事主定讞的形態）**：整組「**現代名 ＋ old-macOS fallback**」的語法糖，落於 `Deps/VanguardSwiftExtension/Sources/SwiftExtension/SwiftFoundationImpl.swift` 的〈FileHandle Backports〉一節（< 10.15／10.15.4 走舊名、≥ 走現代名）：

| 糖（新名） | 舊名 fallback | 備註 |
|---|---|---|
| `read(upTo count: Int) throws -> Data?` | `readData(ofLength:)` | 空 → `nil` |
| `seek(to offset: UInt64) throws` | `seek(toFileOffset:)` | |
| `readToEndOfFile() throws -> Data?` | `readDataToEndOfFile()` | 空 → `nil` |
| `seekToEOF() throws -> UInt64` | `seekToEndOfFile()` | |
| `writeData(_ data: Data) throws` | `write(_:)` | |
| `closeTheFile() throws` | `closeFile()` | |

**糖名刻意與 Foundation 的現代名不同**（`readToEndOfFile` 而非 `readToEnd`、`closeTheFile` 而非 `close`）——這正是為了不與 Foundation 同名、從根上避開 overload ambiguity。

### 7.2 本倉現況與施工法（2026-09-15 實查，不含 `Deps/`）

**兩份同名 shim 仍在**：

| 位置 | 內容 | 宣告數 |
|---|---|---|
| `Packages/vChewing_MainAssembly4Darwin/Sources/MainAssembly4Darwin/LXManager/UserPhraseImpl.swift:11-44` | `nonisolated extension FileHandle`，內含 6 個 `@backDeployed`：`close()`／`seek(toOffset:)`／`seekToEnd()`／`readToEnd()`／`read(upToCount:)`／`write(contentsOf:)` | 6 |
| `Packages/vChewing_OSFrameworkImpl/Sources/OSFrameworkImpl/AppKitImpl/AppKitImpl_Misc.swift:16-22` | `extension FileHandle`，內含 1 個 `@backDeployed`：`readToEnd()` | 1 |

**兩份重複宣告同一個符號（`readToEnd()`）**——即 §7.1 那個病的實例。呼叫點（現代名）共 **20 處**：`UserPhraseImpl.swift` 12、`LXMgr_KimoDataParser.swift` 7、`AppKitImpl_Misc.swift:371` 1。糖名呼叫點現存 **8 處**，全在共享的 `LexiconAssembly`（`lxPerceptionPersistor.swift` 4、`LXConsolidator.swift` 4）。

兩個宿主 package **皆已可取得該糖**：`vChewing_OSFrameworkImpl` 直依賴 `../vChewing_OSNeutral_LibVanguard/Deps/VanguardSwiftExtension`；`vChewing_MainAssembly4Darwin` 經遞移（實查其 manifest 未直接宣告該 product，但 P215 §六 之「跨套件模組可見性含遞移依賴」已在該包身上成立——`AppKitImpl_Misc.swift:12` 的 `import SwiftExtension` 即為證據）。**若遷移途中出現「找不到符號」，才補顯式依賴；先不預補。**

**施工法**：把上述 20 個呼叫點改走糖名，再**整組移除**兩份 shim。改動集中在 3 個檔。

**驗收**：

```bash
grep -rn --include=*.swift '@backDeployed' Sources Packages | grep -v '/Deps/'   # 應為 0 命中
```

**已定案（事主裁定 Q12）：兩份 `@backDeployed` FileHandle shim 退役。** 事主原文：「**退役。**相關的語法糖**已經被我寫在 `VanguardSwiftExtension`** 了，直接用。」

故施工法明確：**把上述 20 個呼叫點改走既有語法糖（§7.1 之六組新名），再整組移除兩份 shim**——**不另寫新糖、不另立 shim**，一律用 `Deps/VanguardSwiftExtension/Sources/SwiftExtension/SwiftFoundationImpl.swift`〈FileHandle Backports〉一節已定讞的那一組（`readToEndOfFile()`／`seekToEOF()`／`closeTheFile()`／`writeData(_:)` 等）。改動集中在 3 個檔（兩份 shim ＋ 其呼叫點）。

---

## 八、工具紀律

1. **交差前只跑 `make lintFormatUncommitted`**（或逐檔處理）。該目標已存在於 macOS 倉 `Makefile:232-241`，只處理 `git diff --name-only HEAD` 的未提交 Swift 檔。
2. **嚴禁對全倉跑 auto-fix**：`make lintFormat`／`make lint`（後者＝`swiftlint lint --fix --autocorrect` 對 `git ls-files` 之全量）。**P216 曾誤跑一次，一舉改動 84 個無關檔案**（已全數 `git checkout --` 還原）。
3. **判準是整條 pipeline 的淨結果，不是任何單一工具的中間態。** `make lintFormat` ＝ `swiftlint --fix` 之後 `swiftformat`；哪怕 SwiftLint 整出超出預期的修改，也會被 SwiftFormat 斧正回去。P216 §十 第 4 條的誤判正是拿「單獨執行兩支工具」的結果推論而來——**單獨執行所見的是「SwiftLint 後、SwiftFormat 前」的中間態，不等於 pipeline 的淨行為**。
4. **本 phase 不動 `.swiftformat`／`.swiftlint.yml`。** P216 事主裁定：本次手術無須修改 config。特別注意 macOS 倉 `--extensionacl on-declarations`（`.swiftformat:83`）**正是**「把修飾詞自 extension 下放給成員」的方向，與 §5.1(b) 一致；**不得**改成 `on-extension`（那正是產生 `nonisolated extension` 的路徑）。SwiftFormat 0.55.2 本身**沒有任何 isolation／actor 規則**，故現行設定即無此風險。
5. **若日後真要加絆線**（如 `swift510_no_nonisolated_extension`）：**不可用 `match_kinds`**（實測 swiftlint 0.61.0：加了 `match_kinds: [keyword, identifier, typeidentifier]` 的 `custom_rules` **完全不觸發**、匹配被靜默丟棄），改用**行首錨定** `'(?m)^[ \t]*nonisolated[ \t]+extension[ \t]'`；且要知道 `swiftlint lint --fix` 模式下**不報**自訂規則（同一份檔案集 read-only 抓 19 筆、`--fix` 模式 0 筆）。此為另立一筆的事，不在 P217 內。
6. **`void_return`（SwiftLint，要 `-> Void`）與 `--voidtype tuple`（SwiftFormat，要 `-> ()`）長年互相打架**；`make lintFormatUncommitted` 的淨結果由後者勝出。**不要為此改 config。**
7. **一切 hash 記載都會隨 amend 失效。** 文書（含本檔）一律以「**訊息 ＋ 主題**」指涉 commit，hash 只當線索——P216 的三筆 commit 已因事主兩輪 amend 換過兩次 hash。
8. **改 manifest／產品型別後必須清建置快取再驗**：`make spmClean`（另加 `make clean510`）。否則增量建置會以殘留 `.o`／`.swiftmodule` 產出 `Undefined symbols` 之**假失敗**——P215 實際踩到過。
9. **macOS 倉對 Swift 5.10 的建置，暫不列入 CI（事主 2026-09-15 新規 8，定案）。** 現行三條 workflow（`build_darwin_SPMTestsAndPackage.yml`、`test_ubuntu_LibVanguard.yml`、`test_winnt_LibVanguard.yml`）**一律不動**；`.github/workflows/` 不在 P217 的改動範圍內。5.10 側的驗收一律在**本地**依 §十 執行，並在回報中附實際輸出。
   - **沿革**：本條由新規 8 定案（取代初稿之「CI 是否納入 5.10」一問，該問曾列「本地 only／新增獨立 job／只驗 manifest」三選項）。**其後經裁定 Q08 分流**：**CI 仍不納入**（本條不變），但**「5.10 編譯是否納入 `Packages/Makefile` 的既有目標鏈」已定為「Swift Package 側＝納入本 phase」**（§2.4）——**CI 不納入 ≠ Makefile 不納入**，兩者層級不同，不可混為一談。

---

## 九、施工順序：事主指定序（權威）

### 9.1 總覽（三階段；⓪ 先於 ①）

> **新規 1**：macOS 的施工方法原則上採取**各個擊破**之方式——從最小的 darwin dependency 入手逐一修復 dual toolchain compilability；最後再按順序收斂到 `InstallerAssembly`、`SettingsUI`、`CandidateWindow` 等元件、與最終的 `MainAssembly`。
> **新規 2**：Swift 5.10 的 compilability **施工終點是 `InstallerAssembly` 與 `MainAssembly`**（理由見 §一：libArcLite 與 macOS 10.9 compatible Swift Runtime 的摻入須由 Xcode ＋ macOS 13.3- SDK 完成）。
> **基礎設施規則**：**Unit Tests 不對 Swift 5.10 開放；每個 subpackage 要部署不同的 package.swift 版本、以及單獨的 makefile（便於測試 5.10 編譯）。**
> **事主 2026-09-15 指定序**（原話，全文見 §9.3）：`SwiftyCapsLockToggler → BookmarkManager → FolderMonitor → Hotenka → IMKUtils → ModifierKeyHitChecker → OtherIMEDataReader → UpdateSputnik → OSFrameworkImpl → Shared_DarwinImpl → Uninstaller → PopupCompositionBuffer → NotifierUI → TooltipUI → CandidateWindow → SettingsUI → InstallerAssembly4Darwin → MainAssembly4Darwin`。
> **事主 2026-09-15 同日追裁**：「`InstallerAssembly4Darwin` **可早收**，你調整順序即可」——故本規範將該項**自第 17 位前移至第 12 位**（與同深度的 `Shared_DarwinImpl`／`Uninstaller` 同組收掉），**調整後次序見 §9.3 之表**；此舉令全序**恢復深度單調**（§9.4 之（一）（二））。

| 階段 | 內容 | 完成判定 |
|---|---|---|
| **⓪ 基礎設施先鋪（先於 ①）** | **逐套件鋪 manifest（每個 subpackage 各 3 份：`@swift-5.10` ＋ 兩份封堵檔）＋ makefile（每個 subpackage 各 1 份）**，一次鋪完 19 組 | 19 個 subpackage 各可在自己目錄內 `make build510` 跑起來（此時**尚允許失敗**——失敗清單正是 ① 的工單）；6.2 側不退化 |
| **① 擊破（＝事主指定序，經早收調整）** | **按 §9.3 之 18 項次序逐一**修復 dual toolchain compilability——一次只收一個 package，用 ⓪ 備好的 `make build510` 逐包驗、逐項勾（§十三 之進度表） | 該套件 `make build510` rc=0、0 error；6.2 側不退化 |
| **② 收斂（＝該序的尾段）** | **§9.3 的第 16～18 位**：`CandidateWindow` → `SettingsUI` → **`MainAssembly`**（末位即終點）。`InstallerAssembly` 已於第 12 位**提前收掉**，故本段只剩 `MainAssembly` 一支 assembly | 兩支 assembly 的 `.a` 皆可產出並供 Xcode 鏈接（＝§一 的全 phase 完成定義）；`InstallerAssembly` 於 ① 階段達標、`MainAssembly` 於 ② 階段達標 |

**沿革**：本節與 §9.3 於 2026-09-15 因**事主指定序**改寫，**取代**本 SOP 先前「由葉到根」與「L1／L2 分層推導」所得的順序。原本那份**依賴拓撲分析不刪**，降格為 §9.4 的**佐證**；凡與事主序不一致者，於 §9.4 **逐條明列**（含我自己先前分析的一處錯誤）。同日晚些，事主再裁定 `InstallerAssembly4Darwin` **可早收**，本規範遂將其前移——**此調整的淨效果是：原本 §9.4 之（二）所記的唯一「回跳」消失，全序恢復與依賴深度一致**（逐步核對見 §9.4 之（一））。

**不在 5.10 側者**（規則 2 之直接後果，勿誤收）：根 manifest（`vChewing`／`vChewingInstaller` 兩支執行檔）、`Plugins/BundleApps`、`Sources/vChewingIME_macOS` 與 `Sources/Installer_macOS` 的 `main.swift`、`.github/workflows`。**這些不是「稍後再做」，而是分工上不屬於 OpenSource toolchain 的工作**——可執行檔與 bundle 由 Xcode 連結端產出。故**⓪ 只鋪 19 個 subpackage，根 manifest 不鋪三份版本檔**（它不需要 5.10 側的對位版）。

### 9.2 ⓪ 基礎設施先鋪（先於 ①）

**為何必須是第 0 步（而不是邊做邊鋪）**：

1. **它是「各個擊破」得以成立的前提。** 規則 1 要求「一次只收一個 package」——但若沒有逐包的 makefile，想驗一個 package 就得跑整倉或手打一長串旗標；那樣「逐包」在操作上不可行，規則 1 會退化成「一次一堆」。**有了逐包入口，逐包驗收才是一行指令。**
2. **它把「環境配對」的三項一次性釘死。** 模板裡的 `LEGACY_TOOLCHAIN`／`LEGACY_SDK`／`LEGACY_TRIPLE` 是全倉共用的一組值（§2.1）；逐包 makefile 讓每一個 package 的驗證都走同一組配對，不會出現「某包用錯 SDK 而產生 312 個掩蓋式錯誤」這種只在單點發作的事故。
3. **它把「版本擇定」的資訊前移。** 三份版本檔一鋪好，`swift package dump-package` 就能立刻告訴你**每個 toolchain 各挑了哪一份**（§3.3）；若等改碼後才鋪，manifest 的問題會與編譯錯誤混在一起，難以歸因。
4. **它讓失敗本身變成資訊。** 跑一輪 19 份 `make build510`、把失敗清單記下來，即得到**① 的完整工單**——哪些包只差 manifest、哪些包真有語法問題，一目了然（§9.6 第 0 點）。

**產出物（逐套件各一份，共 19 組；巢狀子套件已於 P216 完成）**：

| 產出 | 數量 | 規格出處 |
|---|---|---|
| `Package@swift-5.10.swift` | 19 | §3.1（含 §四 的產物形態要求：`.static`／`platforms: nil`／無測試靶） |
| `Package@swift-6.0.swift`（封堵檔） | 19 | §3.1 |
| `Package@swift-6.1.swift`（封堵檔） | 19 | §3.1 |
| `makefile`（逐套件） | 19（其中 2 個既存、1 個已含 5.10 側） | §2.4 |

**⓪ 與 ① 的關係（一條規則，不兩說）**：**先一次鋪完 19 組 ⓪，再跑一輪取得工單，最後才按事主序逐包改碼。** 具體三步：

1. **一次鋪完** 19 個 subpackage ×（3 份版本檔 ＋ 1 份 makefile）——**不與改碼交錯**；
2. **對 19 個各跑一次** `make build510`，記下失敗清單（＝ ① 的工單）；
3. **按 §9.3 的事主序**，逐包修到 rc=0（每完成一項即在 **§十三** 的進度表更新該列）。

**「邊修邊補 manifest」不予採用**——理由是一條可檢驗的原則：三份版本檔與 makefile 是**同一組機械模板**（§3.1／§2.4），一次鋪完的邊際成本遠低於分次；而分次會讓「這一包的失敗是 manifest 問題、還是語法問題」在同一輪輸出裡混在一起，**那正是 ⓪ 要消滅的東西**（§十二 R20）。

### 9.3 ① 擊破序：事主 2026-09-15 指定（權威）

**事主原話**：「你可直接用這個順序加上你認為的合理修改。」——本表即照此辦理，**並已納入事主同日追裁「`InstallerAssembly4Darwin` 可早收」之調整**（該項自第 17 位前移至第 12 位；原話次序的沿革見 §9.1 與 §9.4 之（二））。

| 位次 | 事主用名（＝產品名） | 目錄名（＝ SwiftPM identity） | 依賴深度 | testTarget | 巢狀 `Deps/` | 備註 |
|---|---|---|---|---|---|---|
| 1 | `SwiftyCapsLockToggler` | `HangarRash_SwiftyCapsLockToggler` | 1 | 0 | 無 | 帶 C 靶；**擊破起點、首支探針**（§9.6） |
| 2 | `BookmarkManager` | `Jad_BookmarkManager` | 1 | 1 | 無 | 下游有 `SettingsUI`（第 17 位） |
| 3 | `FolderMonitor` | `vChewing_FolderMonitor` | 1 | 0 | 無 | |
| 4 | `Hotenka` | `vChewing_Hotenka` | 1 | 1 | 無 | 無任何本地依賴 |
| 5 | `IMKUtils` | `vChewing_IMKUtils` | 1 | 0 | 無 | 帶 C 靶；**四支下游**（10／12／17） |
| 6 | `ModifierKeyHitChecker` | `vChewing_ModifierKeyHitChecker` | 1 | 0 | 無 | |
| 7 | `OtherIMEDataReader` | `vChewing_OtherIMEDataReader` | 1 | 1 | 無 | 無任何本地依賴 |
| 8 | `UpdateSputnik` | `vChewing_UpdateSputnik` | 1 | 0 | 無 | |
| 9 | `OSFrameworkImpl` | `vChewing_OSFrameworkImpl` | 1 | 1 | 無 | 帶 ObjC 靶；**四支下游**（10／11／12／17） |
| 10 | `Shared_DarwinImpl` | `vChewing_Shared_DarwinImpl` | 2 | 1 | 無 | 四支下游（13～16） |
| 11 | `Uninstaller` | `vChewing_Uninstaller` | 2 | 0 | 無 | |
| **12** | **`InstallerAssembly4Darwin`** | **`vChewing_InstallerAssembly4Darwin`** | **2** | 1 | 無 | **← 事主追裁「可早收」，自第 17 位前移至此**（原話次序為第 17 位）；與同深度的 10／11 同組收掉；此舉令全序**恢復深度單調**（§9.4 之（一）） |
| 13 | `PopupCompositionBuffer` | `vChewing_PopupCompositionBuffer` | 3 | 0 | 無 | |
| 14 | `NotifierUI` | `vChewing_NotifierUI` | 3 | 1 | 無 | |
| 15 | `TooltipUI` | `vChewing_TooltipUI` | 3 | 0 | 無 | |
| 16 | `CandidateWindow` | `vChewing_CandidateWindow` | 3 | 1 | 無 | **② 收斂段起點** |
| 17 | `SettingsUI` | `vChewing_SettingsUI` | 3 | 1 | 無 | **② 收斂段**；SwiftUI 與巨集最密集處（§5.4） |
| 18 | `MainAssembly4Darwin` | `vChewing_MainAssembly4Darwin` | 4 | 1 | 無 | **終點**；唯一吃遠端 `vChewing-VanguardLexicon` 者（§十二 R7） |

**名稱對照的兩個要點**（施工時最容易踩）：

1. **事主用名 ＝ 該套件的產品名／模組名。** 實查 19 個 manifest，18 個產品名與事主用名**逐一對應**（第 12 個 `vChewing_OSNeutral_LibVanguard` 的產品名是 `Vanguard`，但它不在清單內）。
2. **SwiftPM 的本地相依 identity 是目錄名**（§3.1）——故：`make build510-<目錄名>`（§2.3 的根層目標）用**目錄名**；`.product(name:package:)` 則是**產品名 ＋ 目錄名**兩者並用。**本倉已有兩個目錄名與產品名不同者**：`HangarRash_SwiftyCapsLockToggler` → `SwiftyCapsLockToggler`、`Jad_BookmarkManager` → `BookmarkManager`——這正是清單第 1、2 項。**不可混用。**

**清單未涵蓋的那一個目錄**：`vChewing_OSNeutral_LibVanguard`（聚合體）。**核對結果：採納原判斷，不列為擊破標的。** 理由：它是 P216 的成果，即本規範的**基線與參考實作**（§1.1「前哨已完成」），也是 19 個之中的深度 0；其巢狀子套件 `Deps/VanguardSwiftExtension` 亦然（§5.3 鐵則四禁動）。數目核對：**清單 18 項 ＋ 聚合體 1 個 ＝ 19 個目錄**，吻合。

### 9.4 依賴拓撲佐證，與不一致處的完整清單

**（一）佐證：事主序是一份合法的拓撲序。** 以各 manifest 的 `.package(path:)` 實查、並**修正深度算法**後（見下方「不一致之二」），18 項的依賴深度如下——**每一項的依賴都排在自己的前面，無一例外**：

| 深度 | 套件 | 在事主序中的位次 |
|---|---|---|
| **0** | `vChewing_OSNeutral_LibVanguard`（聚合體）、`Deps/VanguardSwiftExtension` | —（**已完成**，P216 鏡像） |
| **1**（9 個） | `HangarRash_SwiftyCapsLockToggler`、`Jad_BookmarkManager`、`vChewing_FolderMonitor`、`vChewing_Hotenka`、`vChewing_IMKUtils`、`vChewing_ModifierKeyHitChecker`、`vChewing_OtherIMEDataReader`、`vChewing_UpdateSputnik`、`vChewing_OSFrameworkImpl` | **1～9（恰好就是前九位）** |
| **2**（3 個） | `vChewing_Shared_DarwinImpl`、`vChewing_Uninstaller`、`vChewing_InstallerAssembly4Darwin` | **10、11、12** |
| **3**（5 個） | `vChewing_PopupCompositionBuffer`、`vChewing_NotifierUI`、`vChewing_TooltipUI`、`vChewing_CandidateWindow`、`vChewing_SettingsUI` | 13、14、15、16、17 |
| **4**（1 個） | `vChewing_MainAssembly4Darwin` | 18 |

**深度單調性核對（早收調整後，逐段）**：第 1～9 位全為深度 1；第 10～12 位全為深度 2；第 13～17 位全為深度 3；第 18 位為深度 4。**序列的深度單調不減（non-decreasing），且每一項的依賴皆在其前方——即「合法拓撲序 ＋ 深度單調」兩者同時成立，調整前的那一處「回跳」已消失。**

**逐條依賴邊（調整後位次）**：`Shared_DarwinImpl`(10) → `OSFrameworkImpl`(9)／`IMKUtils`(5)／聚合體；`Uninstaller`(11) → `OSFrameworkImpl`(9)；`InstallerAssembly4Darwin`(**12**) → `IMKUtils`(5)／`OSFrameworkImpl`(9)／巢狀子套件（已定讞）；`PopupCompositionBuffer`(13)／`NotifierUI`(14)／`TooltipUI`(15)／`CandidateWindow`(16) → `Shared_DarwinImpl`(10)；`SettingsUI`(17) → `Shared_DarwinImpl`(10)／`OSFrameworkImpl`(9)／`IMKUtils`(5)／`Jad_BookmarkManager`(2)；`MainAssembly4Darwin`(18) → 其餘全員。**全數指向前方。**

**（二）不一致之一（已由事主 2026-09-15 裁定消解）：`InstallerAssembly4Darwin` 的押後。** 事主原指定序把它放在第 **17** 位（五個深度 3 的套件之後），而它的依賴深度是 **2**（只依賴第 5 位 `IMKUtils` 與第 9 位 `OSFrameworkImpl`）——**本可緊接第 11 位 `Uninstaller` 之後收掉**。**本 SOP 當時的處置是「仍照事主序」**（理由：它屬新規 1「收斂到 …… 等元件」之列，提前收掉會讓「終點兩支 assembly」的性質模糊），並記為全序中唯一不服從深度單調者。**事主隨後裁定「可早收」**，遂移至第 **12** 位——**至此不再有回跳，深度單調恢復**（見上（一）之核對）。此項**不再是「不一致」**，改記為一則沿革：事主原序的押後是為了收斂語義的可讀性，早收是為了深度一致性；兩者皆可，事主選了後者。

**（三）不一致之二：本 SOP 先前 §9.2 的 L1／L2 分層有誤（我自己的錯，已修正）。** 舊表把五個「只依賴聚合體」的套件（`HangarRash_SwiftyCapsLockToggler`／`Jad_BookmarkManager`／`vChewing_FolderMonitor`／`vChewing_ModifierKeyHitChecker`／`vChewing_UpdateSputnik`）放進 **L2**，把「無任何本地依賴」與「僅依賴巢狀子套件」的四個放進 **L1**。**但聚合體與巢狀子套件是深度 0 且已完成**——依賴它們**不增加深度**。故那五個的真實深度是 **1**，與 `Hotenka` 等同等。**修正後，事主序的第 1～9 位恰好就是九個深度 1 的套件**，兩者完全吻合；舊表的 L1／L2 之分純屬我自己把「有無依賴」與「深度」混為一談。

**（四）不一致之三：舊 §9.2 的「先掃 L1／L2、再由事主序收 L3／L4」與事主序不相容，且其中一處事實有誤。** 舊文寫「`InstallerAssembly` 雖在收斂序之首，其依賴層為 L3」——**實為深度 2**（修正見上一條）；又舊文主張「擊破階段先把 L1／L2 掃平」——而事主序在深度 1 之後**直接進 depth 2/3 的順序推進**，並非「分層掃平」。**該段已刪，不再並存兩套順序。**

**（五）不一致之四：收斂段的次序與新規 1 的舉例次序不同。** 新規 1 寫「收斂到 `InstallerAssembly`、`SettingsUI`、`CandidateWindow`」，而本序（經早收調整後）的收斂段是 **`CandidateWindow`(16) → `SettingsUI`(17) → `MainAssembly`(18)**——`InstallerAssembly` 已於第 **12** 位收掉，**不在收斂段內**。**以本序為準**：新規 1 那串以「等元件」收尾、屬舉例，且寫在「早收」裁定之前；指定序逐項具名、18 項與目錄一一對應（§9.3）。**共同點是都以 `MainAssembly` 收尾**；**差異點是 `InstallerAssembly` 由收斂段移入擊破段**——這一點正是早收裁定的直接後果。

**（六）同深度內的相對次序（無衝突，僅記錄）**：深度 2 內為 `Shared_DarwinImpl`(10)／`Uninstaller`(11)／`InstallerAssembly4Darwin`(12)——**三者互不依賴**，任意序皆可（早收裁定正好把第三個補進這一組）；深度 3 內前四位（13～16）同為 `Shared_DarwinImpl` 的下游、彼此互不依賴，任意；`SettingsUI`(17) 雖亦為深度 3，卻額外依賴 `Jad_BookmarkManager`(2)（**全清單唯一一條橫跨十餘位次的依賴邊**，方向正確）。

**（七）每步都要能單獨驗收**：在**該套件目錄內** `make build510`（§2.4）或於倉根 `make build510-<目錄名>`（§2.3）rc=0 ＋ 6.2 側 `swift build`／`swift test` 不退化 ＋ byte-sync 未破（I2 只在動到共享 `Sources/`／`Deps/` 時受影響，故 ① 階段大部分步驟不觸發）。**「單獨驗收」之所以做得到，全靠 §9.2 的 ⓪ 先把逐包入口鋪好。** 勾選用進度表見 **§十三**（唯一正本）。

### 9.5 ② 收斂階段

即 §9.3 的第 **16～18** 位：`CandidateWindow` → `SettingsUI` → `MainAssembly4Darwin`。**`InstallerAssembly4Darwin` 已於第 12 位提前收掉**（事主 2026-09-15 裁定），故本段**只剩 `MainAssembly` 一支 assembly**——規則 2 所稱的「兩支 assembly」中，前者在 ① 階段達標、後者在 ② 階段達標，**兩者皆是終點產物，只是收的時間不同**。

**這一段是工作量與風險的集中處**，兩條已知理由：

- **巨集與 SwiftUI 圈隔集中在這裡**：17 處 `#Preview` 有 16 處落在此段的兩個元件（`CandidateWindow` 2、`SettingsUI` 13）與已早收的 `InstallerAssembly4Darwin`（1）（§5.4 之（四）／§十二 R19）。
- **遠端依賴與 build plugin 只在終點**：`MainAssembly4Darwin` 是唯一吃 `vChewing-VanguardLexicon` 者（§十二 R7），其 5.10 行為未實測。

**排程時請為此段單獨預留工時**——① 階段的九個深度 1 套件都很輕（多數是 manifest 與零星語法），一到 ② 階段成本陡增。

### 9.6 先做什麼可以得到最大資訊量（依序）

0. **【⓪，資訊量最大】把 19 個 subpackage 的三份版本檔 ＋ makefile 一次鋪完，19 個各跑一次 `make build510`，把失敗清單記下來。** 同時產出三樣東西——**（a）① 的完整工單**（哪幾包只差 manifest、哪幾包真有語法問題）；**（b）環境配對的驗證**（SDK／triple／scratch 三項是否如 §2.1 所述生效）；**（c）逐包驗收的入口**。成本是機械性的（19 × 4 檔，且模板已備於 §2.4 與 §3.1），收益卻是整條擊破路線的地圖。**先做這個，再動任何一行碼。**
1. **首項即第 1 位的 `HangarRash_SwiftyCapsLockToggler`（1 檔 ＋ 1 個 C 靶）**：把「三份版本檔 ＋ makefile ＋ 5.10 建置」跑通一次，得到本倉的樣板。**在 ① 之中，這一步的資訊量最大**——它同時驗證 SDK 配對、版本擇定、scratch 隔離、static 產物四件事，且順帶驗到 C 靶的搬運，成本卻只有一個檔。（**與事主序一致**：它本就是第 1 位。）
2. **第 9 位的 `OSFrameworkImpl` 是 ① 階段的重點**：它是**最多套件的上游**（`Shared_DarwinImpl`／`Uninstaller`／`InstallerAssembly`／`SettingsUI` 都吃它），手上有 `@backDeployed` shim（§七）與兩個**無法下放的巢狀 `nonisolated` 型別**（§5.4），正好把 §5.1(c) 與 §七 的打樣做完。**位次 9 剛好落在九個深度 1 套件的末位，是個天然的檢查點**——到此為止，深度 1 應全綠。
   - **接著的第 10～12 位是深度 2 的三連**（`Shared_DarwinImpl` → `Uninstaller` → **`InstallerAssembly4Darwin`**）；其中 **`InstallerAssembly4Darwin`（第 12 位）是事主裁定「可早收」者**，收掉它即**達成規則 2 的第一支終點產物**（另一支 `MainAssembly` 在第 18 位）。**這是一個適合對外報進度的里程碑。**
3. **`MainAssembly4Darwin` 的 `UserPhraseImpl.swift` 單檔試點**：它是最大的 shim（6 個宣告、12 個呼叫點），單檔可獨立驗，且不牽動其他 package。可在 ① 階段的空檔先做此單檔（不觸發該包的整體驗收）。
4. **最後才碰 ② 的終點**：`MainAssembly` 的遠端依賴與兩個 build plugin 未實測（§十二 R7）。**不要在資訊量最少的時候先碰它。**（**補記，2026-09-15**：該項已於二輪複驗收工；R7 之三層懸案結清、該包 5.10 側 rc=0。實測紀錄見 **§13.4**。）

**已定案（事主裁定 Q07）：`vChewing.xcodeproj/project.pbxproj` 先不動。** 現況：三 scheme（`vChewing`／`vChewingDebuggable`／`vChewingInstaller`），`MACOSX_DEPLOYMENT_TARGET` 多為 12.0（`Sources/vChewingDebuggable` 為 15.6），`XCLocalSwiftPackageReference` 僅一筆（指向 `Packages/vChewing_OtherIMEDataReader`）。

事主原文：「Legacy 倉庫的建置會引入『**舊版 Xcode 專用的 pbxproj**』。如果都讓一個 pbxproj 負責的話，**新版 Xcode 可能會自動摧毀掉舊版系統的 compilability**。」

故本 phase 的處置是：**不動 pbxproj、不把新舊 Xcode 的建置擠進同一份**；P215 的經驗（「Xcode 無需 pbxproj 變更，經由根套件圖自行解析本機套件」）在本 phase 仍然有效。**Xcode 端的 `.a` 鏈接與 libArcLite／Swift Runtime 摻入**屬 app 側工程，**留待下一 phase**（§十四）。

**已定案（事主裁定 Q08，分流）**：**5.10 編譯之納入與否，分兩層處理。**

| 層 | 裁定 | 落點 |
|---|---|---|
| **(a) Swift Package 側** | **納入本 phase**——把逐包 `build510`（§2.4 的最小集）掛進 `Packages/Makefile` 的既有目標鏈 | §2.4、本節 |
| **(b) macOS 10.9 唯音輸入法（app／xcodeproj 側）** | **留待下一 phase** | **§十四** |

事主原文：「如果只是 **Swift Package** 的話，請處理；如果是指對 **macOS 10.9 的唯音輸入法**的話，此乃**待決事項**。這得需要我部署好 **macOS 10.9 專用的 xcodeproj** 才行。**留待下一個 phase 處理。**」

故 `Packages/Makefile` 現行的七個目標（`all`／`debug`／`release`／`clean`／`lint`／`format`／`lintFormat`，皆指向 `vChewing_MainAssembly4Darwin`）**應增列 5.10 側的目標**（例如 `build510-*` 一族，指入各 subpackage 的 `makefile` 或直接跑根 `Makefile` 的對應目標）；**而 app 側的 xcodeproj 建置，本 phase 不碰。**

**已定案（事主裁定 Q09）：`vChewing-VanguardLexicon` 不處理。** 事主原文：「**已經與 Swift 5.10 相容。**現階段不用處理。**Swift 版本低於 5.10 的時候會自動報錯。**」　**（2026-09-16 補充：本裁定意謂「本 phase 不動該倉」；惟其後實測顯示該套件在 5.10 SwiftPM 之**依賴層**仍不可消費——其兩支 plugin 產品的 `CSQLite3` 靶帶 `.unsafeFlags(["-w"])`。故「改該倉」之事已另立為 §十四 **N4**，不與本裁定衝突：Q09 說的是本 phase 不處理，N4 記的是「下一 phase 若要讓 MainAssembly 於 5.10 側可建置，則必須由該倉出新版」。）**

它同時是 `MainAssembly4Darwin`（**事主序第 18 位、② 之終點**）的遠端依賴與兩個 build plugin 的來源，故**該包在 5.10 側可建置的兩個已知前提已齊**：lexicon 本體相容（Q09）＋ 套件圖不需變更（§1.1）。**原列為「未實測」的那兩層，已於二輪複驗結清**（見 §13.4 第一點）：兩支 build plugin **5.10 SwiftPM 硬拒**（產品含 `CSQLite3` 靶帶 `.unsafeFlags(["-w"])`；非根套件的 unsafe flags 一律不准），故 **5.10 manifest 不收該遠端依賴與兩支 plugin**、`Package.resolved` 之相容性問題連帶無關——該包於 5.10 側自此**已達 rc=0 並產出 `libMainAssembly4Darwin.a`（26 MB）**。**§十二 R7 之三層懸案至此全部結清**（該條已改註）。**（2026-09-16 更新：該「不收」之取捨已依事主指示**翻轉**為與 `Package.swift` 同構——該 manifest 現收該遠端依賴與兩支 plugin，故該包於 5.10 側復歸 rc≠0（全倉 18／19）。正解須由 lexicon 倉出新版，見 §十四 N4。）**

---

## 十、驗收矩陣

**通則**：每一步動工**前後各量一次基線**（6.2 側建置 rc、各 package 測試項數、byte-sync 檢查值）；回報時必須**同框對照**（「動工前 → 動工後」），不得只給後值。

| 項目 | 命令 | 門檻 |
|---|---|---|
| 6.2 根建置 | `swift build` | rc=0 |
| 6.2 根測試 | `swift test` | 全綠；項數 ≥ 基線 |
| 6.2 聚合體測試 | `swift test --no-parallel --package-path ./Packages/vChewing_OSNeutral_LibVanguard` | 全綠；項數 ≥ 基線 |
| 6.2 各 package 測試 | `for p in Packages/*/; do [ -d "$p/Tests" ] && swift test --no-parallel --package-path "$p"; done` | 全綠；項數 ≥ 基線。**測試僅 6.2 側**（鐵律六：Unit Tests 不對 5.10 開放，§4.3）——5.10 側**沒有**任何測試項目，也不應有任何測試目標 |
| **第 0 步（⓪ 基礎設施，§9.2）** | 對 19 個 subpackage 各跑 `(cd Packages/<name> && make build510)`；並 `ls Packages/*/Package@swift-*.swift` 應見 19×5 份（5.10／6.0／6.1／6.2／6.3；6.4 由 `Package.swift` 本身承擔） | 19 個入口皆能啟動；**此時允許編譯失敗**（失敗清單即 ① 的工單），但**不得**有「找不到 manifest／make 目標不存在」之失敗 |
| 5.10 單 package | `cd Packages/<name> && make build510`（逐包入口，§2.4）或於倉根 `make build510-<目錄名>`（§2.3） | rc=0、**0 error**；產物為 `.a` |
| 5.10 子套件 | `make build510-swiftExtension`（或聚合體目錄內 `make build510SwiftExtension`） | rc=0（P216 已達，本 phase 只需不破） |
| **5.10 側終點** | `make build510-vChewing_InstallerAssembly4Darwin` ＋ `make build510-vChewing_MainAssembly4Darwin`（倉根或逐包 `make` 入口皆可；**收工時實測 `make build510-all` 為 19／19 rc=0、無須任何額外旗標**（惟見下註），見 §13.4 第四點） | rc=0、**0 error**；兩份 `.a` 產出並供 Xcode 鏈接（**規則 2 之全 phase 完成定義**）。**2026-09-15 已達成**：`libInstallerAssembly4Darwin.a`（3.2 MB）＋ `libMainAssembly4Darwin.a`（26 MB），兩者 `file` → `current ar archive`、`vtool` → `not mach-o` |
| 產物形態 | `file .build/.legacy-<pkg>/…/libVanguard.a`、`vtool -show-build` | 靜態封存；`vtool` 應以 `not mach-o` 拒收 |
| byte-sync（I2） | 見下方命令清單第 4 段 | `cmp` 無輸出、`diff -rq` 零差異 |
| 殘留語法 | 見下方命令清單第 5 段 | 標頭 `nonisolated` 5 處清零、`nonisolated deinit` 2 處清零、`@backDeployed`（非 `Deps/`）清零、`@retroactive` 6 處清零 |
| SwiftUI／巨集圈隔（規則 4＋`#Preview` 追加） | 見下方命令清單第 5b 段；以 `grep -rln 'import SwiftUI'`（30 檔）與 `grep -rnE '#Preview\b'`（17 處）後**逐檔**核對 `#if compiler(>=6.2)` 邊界 | 5.10 側建置**不出現任何 SwiftUI／`Observation`／`#Preview` 相關錯誤**；17 處 `#Preview` 全數圈隔（`SettingsUI` 13、`CandidateWindow` 2、`InstallerAssembly4Darwin` 1、`vChewingDebuggable` 1） |
| 交差前 | `make lintFormatUncommitted` ＋ `git status --short` | 無非預期檔案變動 |

**已定案（事主裁定 Q10）：不設測試項數門檻。** 事主原文：「單元測試**僅在 Swift 6.2+ 的情況下啟用**，你這次手術應該**不用處理其行文**。除非**手術後單元測試盤點時發現錯誤需要調整**。」

故本 phase 對測試的處置是：

- **不設「不得少於基線」之硬門檻**，亦不需為項數位移做守恆算式；
- **手術後做一次盤點**（§十 上表「6.2 根測試」「6.2 聚合體測試」「6.2 各 package 測試」三列照跑），**僅在盤點發現錯誤時才處理**；
- Q10 與**鐵律六**（Unit Tests 不對 5.10 開放，§4.3）互補：前者說「6.2 側不必逐項對帳」，後者說「5.10 側根本沒有測試」。

### 逐包驗收進度表

**已移出本節。** 逐包進度表（19 個套件的到位狀態與 rc）自 2026-09-15 起**集中於 §十三〈施工進度〉**，該處為**唯一正本**——同一份易變資料不該散在多處。本節僅保留**驗收矩陣**（上表，即「怎麼驗、門檻是什麼」）與下方命令清單（「用什麼指令」）；**兩者的產出（各包跑到哪了）一律記在 §十三**。

- 施工次序之權威 ＝ **§9.3**（事主指定序，含「`InstallerAssembly4Darwin` 可早收」之調整）。
- 進度之唯一正本 ＝ **§十三〈施工進度（快照，隨施工更新）〉**。
- 指引檔（`AGENTS.md`／`CLAUDE.md`／`.github/copilot-instructions.md`）**不承載進度**，只指向 §十三（見 §13.3）。

### 可直接複製的命令清單

```bash
BASE=/Users/shikisuen/Repos/_vChewing/_MainWorkspace
MAC=$BASE/vChewing-macOS
LV=$BASE/vChewing-LibVanguard
LT=$HOME/Library/Developer/Toolchains/swift-5.10.1-RELEASE.xctoolchain
SDK=/Applications/Xcode-15.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX13.3.sdk
TRIPLE=x86_64-apple-macosx10.10

# ── 1. 前置檢查
ls -d "$LT" "$SDK"
cd "$MAC" && git status --short

# ── 2. 6.2 側基線（動工前後各一次）
cd "$MAC"
swift build
swift test 2>&1 | tail -5
for p in "$MAC"/Packages/*/; do
  [ -d "$p/Tests" ] || continue
  echo "== $p"
  swift test --no-parallel --package-path "$p" 2>&1 | tail -3
done

# ── 3. 5.10 側（單一 package）
#   3a) 逐包入口（§2.4，在各套件目錄內）——擊破階段的主力用法
cd "$MAC/Packages/vChewing_IMKUtils" && make build510 && cd "$MAC"
#   3b) 或於倉根一次跑一包（§2.3）
cd "$MAC"
make build510-vChewing_IMKUtils          # 例
#   3c) 或不用 make（旗標同源）：
"$LT/usr/bin/swift" build \
  --package-path ./Packages/vChewing_IMKUtils \
  --scratch-path .build/.legacy-vChewing_IMKUtils \
  --triple "$TRIPLE" --sdk "$SDK" \
  -Xswiftc -target -Xswiftc "$TRIPLE"

# ── 3d. 第 0 步自檢：19 個 subpackage 的 manifest 與 makefile 是否鋪齊
cd "$MAC"
ls Packages/*/Package@swift-5.10.swift | wc -l   # 應為 19
ls Packages/*/Package@swift-6.0.swift  | wc -l   # 應為 19
ls Packages/*/Package@swift-6.1.swift  | wc -l   # 應為 19
ls Packages/*/makefile                 | wc -l   # 應為 19（2 個既存）
# 逐一啟動（此時允許編譯失敗；只要求「入口存在」）
for p in "$MAC"/Packages/*/; do
  [ -f "$p/makefile" ] || { echo "MISSING makefile: $p"; continue; }
  echo "== $p"; (cd "$p" && make build510) 2>&1 | tail -3
done

# ── 3e. 5.10 側終點（規則 2：全 phase 完成定義）
cd "$MAC"
make build510-vChewing_InstallerAssembly4Darwin
make build510-vChewing_MainAssembly4Darwin
# 兩者 rc=0、0 error，且 .a 供 Xcode 鏈接——OpenSource toolchain 的職責到此為止

# ── 4. byte-sync（I2）
cmp "$LV/Package.swift"                      "$MAC/Packages/vChewing_OSNeutral_LibVanguard/Package.swift"
cmp "$LV/Package@swift-5.10.swift"           "$MAC/Packages/vChewing_OSNeutral_LibVanguard/Package@swift-5.10.swift"
diff -rq "$LV/Sources"  "$MAC/Packages/vChewing_OSNeutral_LibVanguard/Sources"
diff -rq "$LV/Deps"     "$MAC/Packages/vChewing_OSNeutral_LibVanguard/Deps" --exclude Build

# ── 5. 殘留語法掃描（見 §5.4／§七）
cd "$MAC"
grep -rn --include=*.swift -E '^[[:space:]]*nonisolated[[:space:]]+(extension|class|struct|enum|actor)' Sources Packages | grep -v '/Deps/'
grep -rn --include=*.swift -E 'nonisolated[[:space:]]+deinit' Sources Packages
grep -rn --include=*.swift '@retroactive' Sources Packages | grep -v '/Deps/'
grep -rn --include=*.swift '@backDeployed' Sources Packages | grep -v '/Deps/'

# ── 5b. SwiftUI／巨集圈隔普查（規則 4 ＋ `#Preview` 追加；見 §5.4）
L=$(grep -rl '' --include=*.swift Sources Packages | grep -v '/Deps/')
grep -rln --include=*.swift 'import SwiftUI' Sources Packages | grep -v '/Deps/'   # 30 檔
grep -rn  --include=*.swift 'import Observation\|@Observable' Sources Packages | grep -v '/Deps/'
grep -rnE '#Preview\b' --include=*.swift Sources Packages | grep -v '/Deps/'      # 17 處
for s in '#Preview' '#Previewable' '#Predicate' '#Playground' '#expect' '#require'; do
  echo "$s: $(grep -rhoE "${s}\b" $L | wc -l) 命中 / $(grep -rlE "${s}\b" $L | wc -l) 檔"
done
for a in '@Observable' '@Bindable' '@Model' '@Entry' '@Previewable' '@Query'; do
  echo "$a: $(grep -rhoE "${a}\b" $L | wc -l) 命中 / $(grep -rlE "${a}\b" $L | wc -l) 檔"
done
grep -rn --include=*.swift -E '#externalMacro|@freestanding|@attached' Sources Packages | grep -v '/Deps/'  # 應為 0

# ── 6. 版本擇定探針
"$LT/usr/bin/swift" package --package-path ./Packages/<pkg> dump-package | head -20
"$HOME/Library/Developer/Toolchains/swift-6.3.3-RELEASE.xctoolchain/usr/bin/swift" \
  package --package-path ./Packages/<pkg> dump-package | head -20

# ── 7. 交差前
cd "$MAC" && make lintFormatUncommitted && git status --short
```

---

## 十一、交付與回報格式

### 11.1 commit 顆粒度

一個「可單獨驗收」的單位一筆 commit，與 P216 的三筆同構：

| # | 訊息 | 範圍 |
|---|---|---|
| 1 | `SPM // Starting working on Swift 5.10 compilability.` | manifest 三件套（×N）＋ `Makefile` 的 `LEGACY_*`／`build510-%`／`clean510`／`spmClean` |
| 2 | `SwiftExtension // Swift 5.10 compilability.` | **本倉已存在，勿重做** |
| 3 | `LibVanguard // Swift 5.10 compilability.` | **本倉已存在，勿重做** |
| 4+ | 往外擴散者，**建議以 package 為單位**：`OSFrameworkImpl // Swift 5.10 compilability.`、`MainAssembly4Darwin // Swift 5.10 compilability.`…；同批同質的小 package 可合併為 `SPM // Swift 5.10 compilability for leaf packages.` | 各 package 的 `Sources/` 改動 |

訊息慣例照本倉既有形式（`vChewing-macOS/AGENTS.md` §7：`ModuleName // SubModuleName: Change.`；實例：`SettingsUI // Defer some tasks to MainActor.`、`LibVanguard // Dylibify VanguardSwiftExtension.`）。**不寫 hash。**

**已定案（事主裁定 Q11）：先不要切分 commit；施工者可自由。** 事主原文：「**先不要切分 Commit。**或者你**按照你的想法切分也行**，反正最後我可能都得統一處理。」

故本節的顆粒度建議**僅為參考、不是規則**：上表的三筆（`SPM // …`／`SwiftExtension // …`／`LibVanguard // …`）與「往外擴散者以 package 為單位」的建議仍然可用，但**不強制**；事主最終會統一處理。**唯一不變的是訊息慣例與「不寫 hash」**（見上）。

### 11.2 兩倉鏡像

凡動到 `Packages/vChewing_OSNeutral_LibVanguard/**`（含其 `Deps/`）或 `vChewing-LibVanguard/**` 者，**另一倉必須同輪落一筆同訊息 commit**，並在回報中附 `cmp`／`diff -rq` 的**實際輸出**（非「已檢查」）。I2 的破壞多半不是發生在改動當下，而是發生在「只改一側、想說等等再同步」的那一段空窗。

**已納入 I2 的邊界（依 Q⑬ 之預設結案）**：聚合體的 `makefile` **已與 `vChewing-LibVanguard/makefile` 逐位元組相同**，自本版起**明文納入 I2 的適用範圍**（I2 原列 `Sources/`／`Deps/`／manifest，今擴及此檔）。故本節的鏡像要求**涵蓋該檔**——`cmp` 清單須加一行：

```bash
cmp "$LV/makefile" "$MAC/Packages/vChewing_OSNeutral_LibVanguard/makefile"
```

### 11.3 回報必含欄位（缺一不可）

1. 本輪動到的檔案清單（依 package 分組，附 `+/−` 行數）
2. 每筆 commit 的**訊息 ＋ 主題**（不寫 hash）
3. **6.2 側**：`swift build` rc；各 package 測試項數（**動工前基線 → 動工後**同框對照）
4. **5.10 側**：每個 package 的建置 rc、error 數、耗時、產物名與大小；**含終點兩支 assembly（`InstallerAssembly`／`MainAssembly`）的 `.a`**（規則 2 之完成定義）
5. **byte-sync**：`cmp`／`diff -rq` 的實際輸出
6. **殘留清單**：尚未處理的檔與原因（**不得靜默略過**）
7. **未驗證項**：明列「未實測」與「無法實測」兩類（如 §三 的兩份封堵檔、§十二 R7 的遠端依賴）
8. **SwiftUI／巨集圈隔進度**（規則 4 ＋ `#Preview` 追加）：已圈／未圈的**檔數與清單**（基線見 §5.4 普查：30 檔 `import SwiftUI`、3 處 `@Observable`、3 處 `@Bindable`、**17 處 `#Preview`／17 檔**）；`#Preview` 部分須逐檔列出「已圈／待圈」，並註明是否位於既有 `#if DEBUG` 之內
9. **基礎設施（⓪）與逐包進度盤點**：19 個 subpackage 各自的 `Package@swift-5.10.swift`／`@swift-6.0`／`@swift-6.1` 與 `makefile` 的**有無清單**（附 `ls Packages/*/Package@swift-*.swift | wc -l` 之實測值＝19／19／19 與 `ls Packages/*/makefile | wc -l`＝19），以及**第 ⓪ 步跑出來的第一輪失敗清單**（即 ① 的工單）。**本項須以 §十三 之進度表「更新前後對照」的形式回報**（§13.3 第 1 條）——進度只記在 §十三 那張表，回報時附對照即可，**不要另開一份進度表**

---

## 十二、風險清單與已知坑

摘自 Phase216 §三／§四／§五／§十，挑「施工時最容易重蹈」者，每條一行：

1. **R1｜SDK 錯＝312 個掩蓋式錯誤**：5.10 toolchain ＋ Xcode 27 的 MacOSX27.0.sdk 會炸在 `_c_standard_library_obsolete`／`-target-arch-variant`／`could not build module 'Darwin'`——**沒有一條指向真正病灶**；正解是 MacOSX13.3.sdk。
2. **R2｜manifest 載得動 ≠ SDK 可用**：`swift package dump-package` 在 SDK 27 下照樣成功（manifest 不 `import Foundation`）。P216 曾據此誤判一次。
3. **R3｜scratch 共用＝互踩**：5.10 的 SwiftPM 讀不懂 v7 版 `workspace-state.json`，會警告 `unable to restore workspace state` 並就地覆寫。
4. **R4｜部署目標會被 SwiftPM 吞掉**：`platforms: [.macOS(.v10_10)]` 與 `--triple` 都被抬到工具鏈地板（x86_64 為 10.13）；arm64 更被 linker 釘在 `minos 11.0`。**唯一有效的是 `-Xswiftc -target`。**
5. **R5｜`#if compiler(>=6.2)` 只夾修飾符＝無效**：5.10 之所以「通過」只是整個分支被編掉；6.x 會報 `cannot find 'nonisolated' in scope`。**只能整段宣告各寫一份。**
6. **R6｜struct 的儲存屬性不可標 `nonisolated`**：5.10 是 `'nonisolated' is redundant on struct's stored properties`，Swift 6 直接是**錯誤**。此條曾誤導過 P216 的方向。
7. **R7｜遠端依賴與 build plugin 在 5.10 側未實測 ——【已結清：5.10 SwiftPM 不可消費（2026-09-15 二輪複驗）；取捨於 2026-09-16 翻轉】**：**三層之最終狀態**——（i）lexicon 本體相容：**已由事主裁定 Q09 確定**；（ii）`Package.resolved`（`"version": 3` ＋ `originHash`）：**因該依賴自 5.10 側退場而自動無關**；（iii）兩支 build plugin（`TextTemplateAssetInjectorPlugin`／`VanguardTextMapPlugin`）：**5.10 SwiftPM 硬拒**——其產品所含 `CSQLite3` 靶帶 `.unsafeFlags(["-w"])`，而非根套件的 unsafe flags 一律不准；`--disable-sandbox` 無效、乾淨解析仍復現、5.10 亦無允許之開關（**故 ③ 段一度記載的「沙箱假象」為誤判，已於 §13.4 更正**）。**處置沿革**：2026-09-15 之取捨為「5.10 manifest 不收該遠端依賴與兩支 plugin」，該包遂達 **rc=0、0 error** 並產出 `libMainAssembly4Darwin.a`（26 MB）；**2026-09-16 事主指示改回與 `Package.swift` 同構**（收該依賴與兩支 plugin），該包於 5.10 側因此**復歸 rc≠0**（全倉 18／19）。6.4 側之 `Package.swift` 兩時期皆原樣保留（新世代 SwiftPM 允准 plugin 靶的 unsafe flags）。**正解在 lexicon 倉**（移除 `CSQLite3` 之 `.unsafeFlags(["-w"])` 並使其 plugin 產品的平台宣告不低於本側）——見 §十四 **N4**。機理與完整紀錄見 **§13.4**。
8. **R8｜`make lint` 是全倉 auto-fix**：P216 誤跑一次，**改動 84 個無關檔案**。交差前只用 `make lintFormatUncommitted`。
9. **R9｜單獨跑一支工具的中間態不可作判準**：判準永遠是 `make lintFormat` 跑完之後樹上有什麼。
10. **R10｜`match_kinds` 讓 `custom_rules` 靜默失效**：swiftlint 0.61.0 下完全不觸發；且 `--fix` 模式下自訂規則不報。要寫絆線一律用**行首錨定**。
11. **R11｜`--extensionacl on-extension` 會製造 `nonisolated extension`**：本倉現行為 `on-declarations`（正確方向），**不得改動**。
12. **R12｜hash 隨 amend 失效**：一切文書以「訊息 ＋ 主題」指涉；P216 的三筆 commit 已換過兩輪 hash。
13. **R13｜改 manifest／產品型別後不清快取＝假失敗**：殘留 `.o`／`.swiftmodule` 會產出 `Undefined symbols`（P215 實際踩到）。
14. **R14｜`queue.sync { mainSync { … } }` 必定死鎖**：須以 `Thread.isMainThread` 快徑繞開。
15. **R15｜為消錯而新增 `@MainActor`＝殺死 ≤10.14 相容性**：P216 事主明令禁止，P217 沿用。
16. **R16｜同套件 dynamic product 靜默產出兩份 image**：SwiftPM 對此**不報錯**（探針 D／E），只能靠 I1 的紅線在人工層面守。
17. **R17｜SwiftUI 內容漏圈 `#if compiler(>=6.2)`（規則 4）**：全倉 30 檔 `import SwiftUI`（§5.4 普查）分布於 6 個元件，其中 `SettingsUI`（18 檔）與 `CandidateWindow`（4 檔）恰在收斂序上——漏圈的代價是 5.10 側一次噴出大量錯誤，而非單檔失敗。判準見 §5.1(f) 與 §5.3 鐵律五；**其中的巨集部分另見 R19**（兩者同源、但操作要點不同：R17 講「有哪些檔」，R19 講「漏掉時的具體陷阱」）。
18. **R18｜`mainSync` 在「呼叫方可能已在 main」時自鎖（規則 7）**：與 R14 同源而形態不同——R14 是 `queue.sync { mainSync { … } }` 的**必死鎖**，本條是 `mainSync` **單獨使用**的潛在自鎖。處置見 §6.2（改用 `asyncOnMain`）；**`deinit` 內不適用**（§6.3）。
19. **R19｜巨集圈隔是收斂階段的主要工作量來源之一（事主 2026-09-15 追加 `#Preview` 規則）**：全倉 **17 處 `#Preview`／17 檔**（§5.4 之（一）），其中 **16 處落在收斂序的三個元件**——`InstallerAssembly4Darwin` 1、`SettingsUI` 13、`CandidateWindow` 2——僅 1 處在非出貨靶；`@Observable`（3 處）與 `@Bindable`（3 處／1 檔）亦集中於 `SettingsUI`。**故這不是均勻分布的工作**：擊破階段幾乎不會遇到（唯一例外是 `Shared_DarwinImpl` 的 1 處 `@Observable`），收斂階段則會一次遇上全部。「各個擊破」在擊破階段的每個 package 上都很輕，但一到收斂階段成本陡增——**排程時須為收斂階段預留這塊**。**三個易錯點**：① 別把 `#Preview` 當「不影響出貨」而漏掉（它藏在 preview-only 碼裡）；② `@available(macOS 14, *)` 擋不住巨集展開（`VwrSettingsCocoaPanes.swift:95-98` 即為實例）；③ 只包修飾詞無效，必須**整段包住**（含 preview 專用型別）。
20. **R20｜跳過第 0 步就動碼＝把「各個擊破」弄丟（事主 2026-09-15 兩條基礎設施規則）**：若未先鋪逐套件 manifest 與 makefile 便開始改碼，驗證就只能靠整倉建置，於是「一次一包」在操作上不可行、退化成「一次一堆」；且 manifest 層的失敗（版本擇定錯、`platforms` 沒填 `nil`、測試靶沒砍）會與語法錯誤混在同一次輸出裡，**難以歸因**。**第 0 步的全部價值就在把這兩類失敗分開**（§9.2／§9.6 第 0 點）。**兩個相關易錯點**：① 逐套件的 `.build/.legacy` 若沒各自獨立，19 個 package 會互踩（＝R3 的放大版）；② 照抄聚合體那份既有 makefile 時，別把它的 `test`／`test-debug`／`dockertest` 目標也當成 5.10 側的目標——那些是 6.2 側的（鐵律六）。
21. **R21｜同一檔案被多個 actor 同時讀寫（事主裁定 Q06 之第三條紀律）**：**佇列的序列性只保證「同一佇列上的任務不並行」，不保證「同一檔案不被兩個 actor 同時碰」**——這是全 §六 最容易被「反正都回到 MainActor 了」這個印象蓋掉的一條。凡同一路徑／同一 handle 可能同時被 MainActor 與某個非 MainActor 上下文觸及者，**必須收斂到單一 actor**（本 phase 即收斂到 MainActor）或有明確互斥；**不得**以「都在一個 Queue 上」推論其安全。**易錯場景**：`withFileHandleQueueSync` 的呼叫端在 MainActor、而閉包內又去碰「已由 MainActor 持有的同一 handle」——此時若任一側改走 `asyncOnMain` 或另開佇列，即可能同時讀寫。**另兩條配套紀律見 §6.2.1**（Queue 只管觸發時機；一律以 `mainSync {}` 觸發、禁用 `{ @MainActor in }`）。
22. **R22｜Swift 6.2／6.3 對「default-isolated 下游型別遵循 default-isolated 上游協定」要求明文 `@MainActor`（`#ConformanceIsolation`）**：本倉（以及整個 6.2 側）是 default-isolation（MainActor）的，故凡 class 遵循「由 default-isolated 模組宣告、或經該處協定繼承而來的協定」者，在 6.2／6.3 下會是**硬錯**：`conformance of 'X' to protocol 'P' crosses into main actor-isolated code and can cause data races`，note 要求 `isolate this conformance to the main actor with '@MainActor'`。**本 phase 不處理**（P217 是 5.10 側的相容手術，此病只在 6.2／6.3 的 6.x 側發作；且編譯器要的那種 conformance 隔離語法 5.10 拒收、在型別上新增 `@MainActor` 又違反 P216 §七 的硬約束）。**緩解手段＝「Swift 6.x ⇒ 6.4+ only」的封堵清單**：6.2／6.3 各加一份 `#error` 封堵檔，`Package.swift` 宣告值一併抬到 6.4（**方案 B**；方案 A——只加封堵檔、不動 `Package.swift`——實測會把 6.4 一起封死，**不可採**）。詳見 **P216 §13.6**（含 6.3.3 實測：中招者恰為 `InputSession` 與 `InputHandler` 兩個 conformance；子套件不中招）與 §十四 N3。**易錯點**：① 這條與 R15 方向相反、極易混淆——R15 禁的是「為消錯而在型別／成員上**新增** `@MainActor`」（殺死 ≤10.14 相容性），本條講的是 6.2／6.3 反過來**索要**同一個東西；兩者無解的交集就是「棄 6.2／6.3」這個結論。② 封堵令生效前，**三系統 CI 必須先抬到 6.4**，否則 CI 會比使用者更早趴（P216 §13.6.4 代價第 2 條）。

    **封堵檔 `#error` 訊息之正本模板（2026-09-16 一致化後；全倉 46 份共用）**——只有 `{scope}` 與末行隨位置變動：

    ```swift
    #error(
      """
      {scope} 不支援 Swift 6.2 / 6.3 toolchain：Swift 6.x 僅支援 6.4+。
      6.2／6.3 對「default-isolated 下游型別遵循 default-isolated 協定」會強制索求明文 @MainActor
      （#ConformanceIsolation），故本依賴閉包在該兩版下不存在可用的產物形態。
      理由與實測見 vChewing-DevLogs/Research/Phase216_PostResearch.md §13.6。
      {exit}
      """
    )
    ```

    `{scope}`＝該處套件／聚合體名（`LibVanguard`／`VanguardSwiftExtension`／各 subpackage 產品名／倉根之 `vChewingIME`）；`{exit}` 有兩種：常態為「請改用 Swift 5.10（Package@swift-5.10.swift）或 Swift 6.4 以上（Package.swift）。」，**倉根 meta-manifest**（無 5.10 對位檔）為「請改用 Swift 6.4 以上（Package.swift）。」。**新增封堵檔時照抄此模板，勿另創措辭**；兩倉之鏡像配對（聚合體與 `Deps/`）須維持逐位元組相同。
23. **R23｜單元測試的三條紀律（事主 2026-09-15 明令；本輪就地落實）**：
    - **(a) 一律 `swift test --no-parallel`。** 本倉的測試共用大量**行程內靜態狀態**（`LXFacade` 的 `factoryTrie`／`lxCassette`、`PrefMgr.shared`、`SessionHost.shared` 等），並行執行即互相踩踏。**落實處**：逐包 `makefile` 的 `test`／`test-debug`／`dockertest` 本來就帶此旗標（未動）；**倉根 `Makefile` 的 `test` 目標原本缺**，本輪補上（兩個 `swift test` 呼叫各加 `--no-parallel`，並註明理由）；**兩倉 CI 共 6 條 workflow 亦早已帶此旗標**（本倉 `test_darwin/ubuntu/winnt_LibVanguard.yml`；macOS 倉 `build_darwin_SPMTestsAndPackage.yml`／`test_ubuntu_LibVanguard.yml`／`test_winnt_LibVanguard.yml`）。**至此所有入口皆帶此旗標。**
      **⚠️ 判讀陷阱（本輪親歷）**：`--no-parallel` **只保證「同一時間只有一個測試函式在跑」，不保證「同步執行到完」**——非同步測試仍會在 `await` 的暫停點交錯。故「日誌顯示測試逐一進場」**不等於**「測試彼此無干擾」；本輪曾據此一度誤判為「已無並行」。
    - **(b) 所有測試 suite 一律標 `.serialized`（事主 2026-09-15 明令）。** **落實範圍與方式**：
      - **`Tests/LibVanguardTests/`**：新增唯一根 suite **`LibVanguardTestsRoot`**（`LibVanguardTests_Root.swift`，標 `.serialized`），並把原先四個游離的頂層 suite（`InputHandlerTests`／`FuriousTypingSegmentorTests`／`ResourceProvisionTests`／`RomanNumeralTests`）**全部改寫成 `extension LibVanguardTestsRoot { … }` 巢狀宣告**；其餘各 `Cases*.swift` 之 `extension InputHandlerTests` 隨之改為 `extension LibVanguardTestsRoot.InputHandlerTests`。如此整靶落入**同一 serialized 子樹**，型別層即保證不並行。
      - **`Tests/BrailleSputnikTests/`**：該靶唯一 suite 補上 `.serialized`（原缺）。
      - 其餘靶（`LexiconAssemblyTests`／`TekkonTests`／`TrieKitTests`／`HomaTests`／`BPMFVSTests`／`SharedTests`／`ResourceLocatorTests`）經普查**原即全數帶 `.serialized`**，未動。
      **新增測試時**：新 suite 一律寫成 `extension LibVanguardTestsRoot { … }` 並在其內宣告 `@Suite(…, .serialized)`，**不得新增游離於根之外、或未標 `.serialized` 的頂層 suite**。
    - **(c) `LXFacade.asyncLoadingUserData` 在單元測試下必須為 `false`（事主 2026-09-15 定案）——凡涉及 userdata 載入的測試一律走同步載入。** 測試要的是**確定性**：資料須在斷言之前**載入完畢**，不得留下「等等才會落定」的非同步尾巴。故生產碼把該開關與測試模式綁定——`resetSharedResources()` 與 `applyEnvironmentDefaults()` 皆寫 `= !UserDefaults.pendingUnitTests`（**單元測試 ⇒ `false`**）；測試側於需要時自行 `= false` 並以 `defer` 還原原值。**本輪補齊的最後一處**：`test_IH400_MixedAlnumKanjiInputTest_Izanami`（`InputHandlerTests_Cases4.swift`）——它是唯一跑遍整個注音表、大量觸及 userdata 卻**未**壓同步的測試，其餘九支磁帶測試（`Cases1`）皆有壓。該處即前述「時過時不過」抖動的來源：補上之後，**兩倉各連跑 5 次 `--no-parallel` 全綠（535 項、0 issue）**。
      **⚠️ 本條曾有過一次方向性誤判，留檔以示警戒（2026-09-15 當晚）**：本 SOP 一度把此條寫成「恆為 `true`、測試亦不例外」，並據以改動生產碼與測試（撤除 `restoreAsyncLoadingStrategy`、改以 `await LXATestsData.waitUntil(...)` 等待非同步載入）。**該方向已由事主推翻並全部還原**（兩倉該七檔回到 `false` 語義、逐位元組同步）。**教訓**：測試的載入策略屬**產品決策**，不是施工者可自行推論的技術細節——「測試未覆蓋非同步路徑」確是事實，但**權衡的結果是選確定性**；施工者不得以該事實為由逕自翻轉語義。同類事項一律先問。
      **⚠️ 另記一則方法論教訓**：`.serialized` 與 `--no-parallel` **層級不同、缺一不可**——前者是**型別層**（保證該子樹不並行），後者是**CLI 層**（保證同一時間只有一個測試函式）。本輪實測：即使 `LibVanguardTestsRoot` 已就位，**故意不加 `--no-parallel` 仍會抖動**（`6 suites` 並行模式下 `test_IH400`／`test_IH105` 仍偶發失敗）。故**兩者都要**：結構是保險，旗標是開關。

---

## 十三、施工進度（快照，隨施工更新）

**本表為快照、隨施工更新；規範與進度分離。** §一～§十二 是**規範**（除非事主裁定變更，否則不隨施工改動）；本章是**進度**（每次施工後更新即可，**不需要**重新審閱規範，也不該讓進度的變動去動到規範的條文）。

**本章為進度之唯一正本。** §十 原有的〈逐包驗收進度表〉已於 2026-09-15 **併入本章**（§十 只留指向）——**不留兩份進度表**：§十 載「怎麼驗、門檻是什麼、用什麼指令」，本章載「各包跑到哪了」。

**指引檔不承載進度。** `vChewing-macOS/AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md` **均不記載施工進度**，只在該處**指向本章**——理由是同一份易變資料不該散在三處（改了這裡、忘了那裡，就是四份不一致的開始）。

### 13.1 逐包狀態（按 §9.3 之事主指定序；含「`InstallerAssembly4Darwin` 可早收」之調整）

**用法**：⓪ 階段一次鋪完 19 組後，把「版本 manifest」「`makefile`」兩欄改為「已就位」；跑完第一輪 `make build510` 後，把 rc 記入「首輪 rc」欄（即 ① 的工單）；接著按位次逐包修，修好即更新「目前 rc」欄。**位次即施工次序，不可跳位**（§9.4 已證明全部依賴皆指向前方）。

> **⓪ 已完成（2026-09-15）**：19 個 subpackage 的版本 manifest 與逐包 `makefile` 已全數就位；首輪 `make build510-all`（於 `Packages/`）已跑畢——**耗時 30m12s、`make` rc=2；8 包 rc=0、11 包 rc≠0**。下表即該輪結果，rc≠0 者即 ① 的工單。
>
> **本輪實鋪的是「六份」而非 §3.1 原表單的「三份」**：除 `Package@swift-5.10.swift` 與 6.0／6.1 兩份封堵檔外，**另鋪 `Package@swift-6.2.swift`／`Package@swift-6.3.swift` 兩份封堵檔**（隨「Swift 6.x 僅支援 6.4+」之裁定；見 §3.1 末段〈未來擴充〉與 §十四 N3），並把該 18 包的 `Package.swift` 宣告值**一併由 6.2 抬到 6.4**——不抬則 6.4 toolchain 會被 6.3 封堵檔攔下（即 N3 之「方案 B」）。**兩側實測**：6.3.3 toolchain 建置該 18 包任一 → 封堵檔生效（`error: … 不支援 Swift 6.2 / 6.3 toolchain`）；6.4 toolchain → 取 `Package.swift`、rc=0；5.10 toolchain 之 `dump-package` → `platforms` 為空（`nil`）、產品型別為 `static`。
>
> **6.2／6.4 側複驗（本輪）**：倉根 `swift build` **rc=0**（Build complete，54.80s）——涵蓋全部 19 個 subpackage。`swift test --no-parallel` 抽驗：**聚合體 rc=0、9 個測試靶共 535 項全綠**；`vChewing_Hotenka` 8 項、`vChewing_OtherIMEDataReader` 6 項、`vChewing_OSFrameworkImpl` 3 項皆綠；`Jad_BookmarkManager` 之測試靶為**既存連結失敗**（見該列備註，已實測非本輪所致）。逐列結果見下表「6.2 側不退化」欄。

> **① 已完成（2026-09-15，任務 B）**：由 ⓪ 的 **6 處診斷（4 檔）** 入手，逐包重跑 `make build510-all` 追蹤消長，最終 **16 包 rc=0、3 包 rc≠0**（`make` 仍回 rc=2 係因末三包未收）。**6 處的處置全數落在既有的三種格**：§5.1(b)（標頭 `nonisolated` 下放至成員）1 處、§5.1(c)（`#if compiler(>=6.2)` 兩分支、<6.2 採 legacy 寫法）3 處、§5.5 第 2 條（`if #unavailable() {} else {}` 兩分支）2 處。
>
> **「其餘皆為上游連帶」經實測修正**：上游（`OSFrameworkImpl`、`Jad_BookmarkManager`）轉綠後，13～15 位**才顯出其自身診斷**（首輪之所以只見到上游者，係依賴圖先編上游、封包早停）。故 ① 的實際工作量 = 6 處原始工單 ＋ 下列「轉綠後才顯出者」，後者亦一併依同三種格收掉：
>
> | 包（位次） | 轉綠後顯出之自身診斷 | 處置 |
> |---|---|---|
> | `Shared_DarwinImpl`（10） | `PEReloadEventObserver.swift` 之 `@Observable`／`ObservationIgnored`；`UserDefImpl/UserDefRenderable.swift` 之 `UserDefRenderable`／`Binding` availability | 兩檔依 §5.1(f)／鐵律五圈進 `#if compiler(>=6.2)` |
> | `InstallerAssembly4Darwin`（12） | `#Preview` 1 處；`SwiftUI/` 兩檔之 `MeshGradient`／`GraphicsContext`；`MainSputnik4Installer.swift:18` 之 `async` 需 10.15 | SwiftUI 兩檔整檔圈隔、`#Preview` 圈隔、`asyncInit()` 標 `@available(macOS 10.15, *)`、`runNSApp` 內之 SwiftUI 分支圈隔；另補 `import IMKUtils`（§7.2 之例） |
> | `PopupCompositionBuffer`（13） | `hide()`（`nonisolated`）經非隔離 `mainSync` 閉包呼叫 MainActor 成員 | §5.1(c)，<6.2 分支採 legacy 寫法 |
> | `TooltipUI`（15） | 同型病（`setColor(state:)`） | 同上 |
>
> **未收者恰為 §9.3 的第 16～18 位**：16 `CandidateWindow`、17 `SettingsUI` 屬 **② 收斂段**；18 `MainAssembly4Darwin` 為**待事主裁定**之項。**① 段（第 1～15 位）自此全綠**——含規則 2 的第一支終點產物 `libInstallerAssembly4Darwin.a`（產物經 `file`／`vtool` 驗為 static `ar` archive、`vtool` 以 `not mach-o` 拒收）。
>
> **6.2／6.4 側複驗（① 完成時）**：倉根 `swift build` **rc=0**；聚合體 `swift test --no-parallel` **rc=0、9 個測試靶共 535 項、0 失敗**（與 ⓪ 之 535 項**一致，項數不減**）。
>
> **② 收斂段之前段已完成（2026-09-15，任務 B 之 ②）**：§9.3 第 **16～17** 位收掉——`vChewing_CandidateWindow`、`vChewing_SettingsUI` 皆達 `make build510` **rc=0、0 error**（產物 `libCandidateWindow.a`／`libSettingsUI.a`，經 `file` 驗為 `current ar archive`）。修後重跑 `make build510-all` 之 rc 分佈：**19 個目錄中 18 個 ✓**（含聚合體），**唯一失敗者即第 18 位 `vChewing_MainAssembly4Darwin`**（`rc=2`，失敗於依賴圖層：遠端 lexicon 兩支 build plugin 產品之 `CSQLite3` 靶，`contains unsafe build flags`——**與本輪無關、依工單未動**）。即 **18 個擊破項中 17 項 rc=0，② 段自此只剩終點 `MainAssembly4Darwin`**。
>
> **本輪手法全數落在既有格內**（未新增任何手法）：`#Preview` 逐處圈隔（本輪 15 處：`SettingsUI` 13＋`CandidateWindow` 2；全倉 17 處至此僅餘非出貨靶 `vChewingDebuggable` 1 處未圈——依 Q01 不需圈）與 SwiftUI 之整檔／整段圈隔（§5.1(f)＋鐵律五：`SettingsUI` 17 檔整檔、`CandidateWindow` 2 段）；`if #unavailable() {} else {}` 完整兩分支（§5.5 第 2 條：`performDrag(with:)` 1 處、`localizedStandardContains` 1 處，後者 10.10 分支採 legacy 同款 `range(of:options:)`，§5.1(g)）；`nonisolated deinit` → 樸素 `deinit`（§6.3：`CtlSettingsUI`／`CtlSettingsCocoa` 各 1 處）；`#if DEBUG` 之內再加一層 `#if compiler(>=6.2)`（§5.4 之（五）第 2 點：`CandidateWindow` 兩個 preview 檔，既有守衛未動）。**未新增任何 `@MainActor`**（鐵律一）；**未動 manifest／CI／`.swiftformat`／`.swiftlint.yml`／`Deps/`／倉根 `Sources/`**；16 個已就位包的原始碼一字未動（交差前的 `make lintFormatUncommitted` 對全樹之淨變動為**零**，見下行）。
>
> **6.2／6.4 側複驗（② 完成時）**：倉根 `swift build` **rc=0**（Swift 6.4）；聚合體 `swift test --no-parallel` **rc=0、9 個測試靶共 535 項、0 失敗**（與 ① 之 535 項**一致，項數不減**）；兩包自身 6.4 側 `swift test` 皆 **rc=0**（`CandidateWindow` 20 項、`SettingsUI` 1 項）。**交差前 `make lintFormatUncommitted`**：淨結果與執行前**逐位元組相同**（`git diff HEAD | shasum` 兩次同值），即 SwiftLint 的 `void_return`／`trailing_comma` 修正全數由 SwiftFormat 斧正回原狀（§八 第 3、6 條）。

| 位次 | 目錄名（＝ identity） | 版本 manifest<br>（`Package.swift`@6.4 ＋ 5.10／6.0／6.1／6.2／6.3，共六份） | `makefile` | 首輪 `make build510` rc | 目前 rc | 6.2 側不退化 | 備註 |
|---|---|---|---|---|---|---|---|
| 1 | `HangarRash_SwiftyCapsLockToggler` | **已就位**（六份） | **已就位**（`build510`／`clean510`） | **rc=0** | **rc=0** | ✅（根 `swift build` 涵蓋） | 帶 C 靶（`CapsLockToggler` 原樣保留）；**首支探針**（§9.6）——**只鋪 manifest 即通** |
| 2 | `Jad_BookmarkManager` | **已就位**（六份） | **已就位** | rc=2 | **rc=0**（① 已收） | ⚠️ 見備註（**既存**、非本輪所致） | 首輪診斷：`Sources/BookmarkManager/BookmarkManager.swift:308`（`nonisolated extension`）——**已依 §5.1(b) 下放至成員**（該 extension 的 4 個 `static func` 各標 `nonisolated`；extension 標頭之 `nonisolated` 撤除）。**6.4 側 `swift test` 之測試靶連結失敗為既存問題**（**不修、僅列報**）：`Undefined symbols … SwiftExtension.mainSync`（測試靶只宣告 `Vanguard` 產品、未宣告 `VanguardSwiftExtension`）；**已實測 HEAD 之 6.2 manifest 亦然**（rc=1、同符號），故非 manifest 鋪設所致；CI 對 rc=1 另有「視為無測試而略過」之分支，故未顯影 |
| 3 | `vChewing_FolderMonitor` | **已就位**（六份） | **已就位** | **rc=0** | **rc=0** | ✅（根 `swift build` 涵蓋） | **只鋪 manifest 即通** |
| 4 | `vChewing_Hotenka` | **已就位**（六份） | **已就位**（**既存 `format`／`lint` 保留未動**，其 `.PHONY` 擴充後追加 5.10 段） | **rc=0** | **rc=0** | ✅（根 `swift test` 亦綠） | **只鋪 manifest 即通** |
| 5 | `vChewing_IMKUtils` | **已就位**（六份） | **已就位** | **rc=0** | **rc=0** | ✅（根 `swift build` 涵蓋） | 帶 C 靶（`IMKSwiftModernHeaders` 原樣保留）；**只鋪 manifest 即通** |
| 6 | `vChewing_ModifierKeyHitChecker` | **已就位**（六份） | **已就位** | **rc=0** | **rc=0** | ✅（根 `swift build` 涵蓋） | **只鋪 manifest 即通** |
| 7 | `vChewing_OtherIMEDataReader` | **已就位**（六份） | **已就位** | **rc=0** | **rc=0** | ✅（根 `swift test` 亦綠） | **只鋪 manifest 即通**（此包 6.2 側本即無 `platforms`，5.10 manifest 明列 `nil`） |
| 8 | `vChewing_UpdateSputnik` | **已就位**（六份） | **已就位** | **rc=0** | **rc=0** | ✅（根 `swift build` 涵蓋） | **只鋪 manifest 即通** |
| 9 | `vChewing_OSFrameworkImpl` | **已就位**（六份） | **已就位** | rc=2 | **rc=0**（① 已收，0 error／0 warning） | ✅（根 `swift test` 亦綠） | 帶 ObjC 靶（`OSFrameworkImplViaObjC` 原樣保留）；**深度 1 檢查點**（§9.6）。首輪六處診斷有**四處落在本包**，**已全數收掉**：`AppKitImpl_Misc.swift:119`（`enum MeasurementPath`）／`:121`（`struct CacheKey`）與 `SecureEventInputSputnik.swift:110`（`struct ActivationFlags`）皆 `nonisolated` 掛巢狀型別 → 依 §5.1(c) 以 `#if compiler(>=6.2)` 整段分隔、<6.2 分支採 legacy 寫法（Misc 兩者共用同一組 member，僅兩個型別宣告各寫一份）；`AppKitImpl_NSView.swift:538`／`:547` 為 availability（`archivedData(withRootObject:requiringSecureCoding:)`／`unarchivedObject(ofClass:from:)` 需 macOS 10.13）→ 依 §5.5 第 2 條以 `if #unavailable(macOS 10.13) {} else {}` 兩分支寫法，<10.13 分支用舊名（`archivedData(withRootObject:)`／`unarchiveObject(with:)`，即 legacy 對位寫法）。**註**：`SecureEventInputSputnik.swift:110` **不在 §5.4 普查所列的 2 處之內**（該普查之正則要求 `nonisolated` 緊接 `extension\|class\|struct\|enum\|actor`，被 `public` 隔開者漏收）——屬**新增實測發現**，已回報事主，並已於 §5.4 補記 |
| 10 | `vChewing_Shared_DarwinImpl` | **已就位**（六份） | **已就位** | rc=2 | **rc=0**（① 已收） | ✅（根 `swift build` 涵蓋） | 四支下游（13～16）。首輪診斷在**上游**（`OSFrameworkImpl/…/AppKitImpl_NSView.swift:538`），上游修好後**顯出自身兩檔**並已收掉：`PEReloadEventObserver.swift`（`@Observable`／`ObservationIgnored`，§5.1(f) 圈進 `#if compiler(>=6.2)`）與 `UserDefImpl/UserDefRenderable.swift`（SwiftUI 專屬、legacy 無對位物，同法圈隔）。**連帶**：13～16 位之下游即隨之轉綠；`SettingsUI` 之 `PerEditor` 端仍引用前者，屬 ② 段圈隔範圍（見第 17 列） |
| 11 | `vChewing_Uninstaller` | **已就位**（六份） | **已就位** | rc=2 | **rc=0**（① 已收） | ✅（根 `swift build` 涵蓋） | 首輪診斷在**上游**（`OSFrameworkImpl/…/AppKitImpl_Misc.swift:119`）；上游收掉即綠，本包原始碼未動 |
| **12** | **`vChewing_InstallerAssembly4Darwin`** | **已就位**（六份） | **已就位** | rc=2 | **rc=0**（① 已收；**產出 `libInstallerAssembly4Darwin.a`**） | ✅（根 `swift build` 涵蓋） | **← 事主裁定「可早收」，自原第 17 位前移**；**收掉此包即達成規則 2 的第一支終點產物**（§9.5）。上游收掉後顯出自身四處，已全數收掉：`SwiftUI/` 兩檔（`InstallerApp4SwiftUI`／`VwrAppInstaller4SwiftUI`）依 §5.1(f) 整檔圈進 `#if compiler(>=6.2)`；`VwrAppInstaller4Cocoa.swift:645` 之 `#Preview` 依同一規則圈隔（`@available(macOS 14.0, *)` 擋不住巨集展開）；`MainSputnik4Installer.swift:18` 之 `asyncInit()` 標 `@available(macOS 10.15, *)`（concurrency 執行期下限，§5.5 第 1 條），其 `runNSApp` 內的 SwiftUI 分支一併圈隔（5.10 側一律走 AppKit 版，與 legacy 安裝程式一致）；另補 `InstallerShared.swift` 之 `import IMKUtils`（顯式依賴，依 §7.2「出現找不到符號才補」之例） |
| 13 | `vChewing_PopupCompositionBuffer` | **已就位**（六份） | **已就位** | rc=2 | **rc=0**（① 已收） | ✅（根 `swift build` 涵蓋） | 首輪診斷在**上游**（`OSFrameworkImpl/…/AppKitImpl_Misc.swift:119`）；上游收掉後顯出自身一處：`PopupCompositionBuffer.swift:192` 之 `hide()`——`nonisolated` 的它經非隔離 `mainSync` 閉包呼叫 MainActor 成員 `prepareForHide()`。依 §5.1(c) 以 `#if compiler(>=6.2)` 分隔，<6.2 分支採 legacy 寫法（`hide()` 不標 `nonisolated`、直接於 body 內呼叫） |
| 14 | `vChewing_NotifierUI` | **已就位**（六份） | **已就位** | rc=2 | **rc=0**（① 已收） | ✅（根 `swift build` 涵蓋） | 首輪診斷在**上游**（`OSFrameworkImpl/…/AppKitImpl_NSView.swift:538`）；其自身**零原始碼診斷**——第 10 位 `Shared_DarwinImpl` 收掉即綠 |
| 15 | `vChewing_TooltipUI` | **已就位**（六份） | **已就位** | rc=2 | **rc=0**（① 已收） | ✅（根 `swift build` 涵蓋） | 首輪診斷在**上游**（`OSFrameworkImpl/…/AppKitImpl_Misc.swift:119`）；上游收掉後顯出自身一處：`TooltipUI.swift:179` 之 `hide()`（同第 13 列之病與藥：MainActor 成員 `setColor(state:)`） |
| 16 | `vChewing_CandidateWindow` | **已就位**（六份） | **已就位** | rc=2 | **rc=0**（② 已收；**產出 `libCandidateWindow.a`**） | ✅（根 `swift build` 涵蓋；本包 6.4 側 `swift test` **rc=0、20 項**） | **② 收斂段起點**；`#Preview` 2 處。首輪兩條診斷已收：`TDK4AppKit/_GSI4AppKit_Previews.swift`／`_TDK4AppKit_Previews.swift` 之 `no macro named 'Preview'` → 依 §5.4 之（五）第 2 點**在既有 `#if DEBUG` 之內再加一層 `#if compiler(>=6.2)`**（既有守衛一字未動，preview 整段含其內宣告一併包住）；`VwrCandidateGSI4AppKit.swift:563` 之 `performDrag(with:)`（需 macOS 10.11）→ 依 §5.5 第 2 條**完整兩分支**（`if #unavailable(macOS 10.11) {} else {}`；10.10 分支留空、不另立替代實作，`vChewing-OSX-Legacy` 於該處為單分支 `#available` 寫法）。**另依 §5.1(f)／鐵律五補圈兩處**：`VwrCandidateGSI4AppKit.swift`／`VwrCandidateTDK4AppKit.swift` 檔尾〈Debug Module Using Swift UI〉段（`import SwiftUI` ＋ `NSViewRepresentable` 包裝；其唯一引用者即前述兩個 preview 檔），**同檔其餘 AppKit 內容一字未動** |
| 17 | `vChewing_SettingsUI` | **已就位**（六份） | **已就位** | rc=2 | **rc=0**（② 已收；**產出 `libSettingsUI.a`**） | ✅（根 `swift build` 涵蓋；本包 6.4 側 `swift test` **rc=0、1 項**） | **② 收斂段**；SwiftUI 18 檔／`#Preview` 13 處／`@Observable`＋`@Bindable`／`nonisolated deinit` 2 處。**收法**：17 個純 SwiftUI 檔（`SettingsUI/` 全 15 檔＋`PhraseEditor/PhraseEditorUI.swift`＋`SettingsCocoa/PrefUITabs.swift` 之 `suiView` 乙員以外者另計）**整檔**圈進 `#if compiler(>=6.2)`（§5.1(f)＋鐵律五）；`PhraseEditorUI.swift:218` 之 `PEReloadEventObserver` 引用（第 10 位圈隔之連帶）**隨該檔整檔圈隔而解，未在 SettingsUI 側硬造符號**；`SettingsCocoa/PrefUITabs.swift` 僅圈 `suiView`（回傳 `some View` 且逐一引用 6.2+ 面板），其餘成員（`cocoaTag`／`i18nTitle`／`icon`）為 AppKit 側所用、兩代皆須可編；`SettingsCocoa/` 13 檔之 `#Preview` 逐處圈隔；`CtlSettingsCocoa.swift` 之 `nonisolated deinit`（:43）改樸素 `deinit`（§6.3；不觸及 MainActor 狀態故免 `mainSync`），同檔 `localizedStandardContains`（:255，需 macOS 10.11）依 §5.5 第 2 條寫完整兩分支、10.10 分支採 legacy 同款 `range(of:options:)`（§5.1(g)）。**5.10 側所留者**＝`SettingsCocoa` 整組 AppKit 設定介面（與 legacy 倉庫之 SettingsCocoa 對位）＋`SettingsUIHost`／`PhraseEditorDelegate`／`_ModuleReexport`；SwiftUI 側之型別（`CtlSettingsUI`／`VwrSettingsUI`／`SettingsUIViewModel`／各 `VwrSettingsPane*`／`VwrPhraseEditorUI`）於 5.10 側不存在（§5.1(f)：<6.2 不提供替代實作），其下游連帶落於第 18 位 |
| 18 | `vChewing_MainAssembly4Darwin` | **已就位**（六份） | **已就位** | rc=2 | **rc≠0**（2026-09-16 事主指示「改回與 `Package.swift` 同構」後復發，失敗於依賴圖層；此前的 rc=0 與 `libMainAssembly4Darwin.a`（26 MB）係以「5.10 側不收該依賴」為前提者） | ✅（根 `swift build` rc=0；根 manifest 無 test target，本包之測試靶屬 `MainAssembly4DarwinTests`，見 §13.4 之盤點） | **終點**。**依賴圖層：5.10 側之取捨歷經一次翻轉（現行狀態＝收該依賴，故本包 5.10 側不可建置）**。（i）2026-09-15 二輪複驗確認：該兩支 plugin 產品各含 `CSQLite3` 靶，而該靶帶 `.unsafeFlags(["-w"])`，**5.10 SwiftPM 對非根套件的 unsafe flags 一律硬拒**；`--disable-sandbox` 無效、乾淨解析仍復現、亦無允許之開關——故非沙箱假象；當時的處置是「5.10 manifest 不收該依賴與兩支 plugin」，本包遂達 rc=0。（ii）**2026-09-16 事主指示改回**：該 manifest 現與 `Package.swift` 同構（遠端依賴 ＋ 兩支 plugin 原樣保留），**本包在 5.10 側因此回到 rc≠0**（再次止於 `contains unsafe build flags`）。**兩條替代路均已實測**：(a) `--disable-sandbox` 無效；(b) 改 `.package(path:)` 指向本地 lexicon 檢出者可過該關卡（SwiftPM 對本地路徑相依免檢），但隨即撞上平台下限衝突——plugin 產品要求 macOS 10.15，而本側 `platforms` 為 `nil`（取其地板 10.13）。**故唯一的正解在 lexicon 倉自身**：移除該 `.unsafeFlags(["-w"])`（並使其 plugin 產品的平台宣告不低於本側）後出新版；已登記為 §十四 **N4**。6.4 側不受影響（新世代 SwiftPM 允准 plugin 靶的 unsafe flags；根 `swift build` 實測 rc=0）。**原始碼層診斷 10 條、涉 6 檔，已全數收掉**：`UserPhraseImpl.swift:11` 之標頭 `nonisolated extension` → §5.1(b) 下放至 6 個成員；`MainSputnik.swift:12` 之 `wireUp()` 兩個非隔離呼叫 → 於 init 內套 `mainSync {}`（§6.2，非 `{ @MainActor in }`）；同檔 `asyncInit()` → `@available(macOS 10.15, *)`（與 `MainSputnik4Installer` 同款）；`IMEMenuSputnik.swift:87` 與 `InputSession_DarwinSurface.swift:106` 之 `CtlSettingsUI` 引用 → 依 §5.1(f)／鐵律五以 `#if compiler(>=6.2)` 圈隔，5.10 側一律走 `CtlSettingsCocoa`（與 `vChewing-OSX-Legacy` 的同名實作一致）；`LXMgr_Core.swift:99`／`:450` 之 MainActor 呼叫 → 依 legacy 形狀改走 `DispatchQueue.main.async { @MainActor in … }`（5.10 側 `mainSync` 之閉包不帶隔離，故不可用）；`SettingsUI/SettingsUIHost.swift` 之顯式 `@MainActor` → **撤除**（legacy 同名檔本即無此標註；6.2 側改由 `defaultIsolation` 提供同一隔離，語義不變。**必要性已實測**：復原該標註即令 `MainSputnik.swift:20` 報 `call to main actor-isolated static method 'wireUp()'`） |

> **本列之「目前 rc」已由 P218 接管（2026-09-16）**：P218 起該包之 5.10 manifest 不再收 lexicon 依賴與兩支 plugin，`make build510-all` 復歸 19／19 rc=0；機理（lexicon 真正用上 Swift Concurrency，其 10.15 下限與本側 10.13 地板相衝）見 P218 之紀錄。

### 13.2 已就位者（P216 成果；不列為擊破標的）

| 目錄／子套件 | 六份版本 manifest | `makefile` | 首輪 rc | 目前 rc | 說明 |
|---|---|---|---|---|---|
| `vChewing_OSNeutral_LibVanguard`（聚合體，深度 0） | **已就位**（六份，P216 ＋ 任務 A） | **已就位**（122 行；與 `vChewing-LibVanguard/makefile` 逐位元組相同——已明文納入 I2，見 §11.2） | **rc=0**（P216 已達；本輪 `build510-all` 複驗亦 rc=0） | **rc=0** | **本規範之參考實作**；6.2 側基線記為 529 項——本輪 6.4 側 `swift test --no-parallel` 複驗：**9 個測試靶、535 項全綠（rc=0）** |
| `Deps/VanguardSwiftExtension`（巢狀子套件，深度 0） | **已就位**（六份） | **已就位**（`build510SwiftExtension` 於聚合體 `makefile` 內） | **rc=0**（P216 已達） | **rc=0** | 已定讞，§5.3 鐵則四禁動（本輪未動；兩倉 `cmp` 逐位元組相同） |

**不列於 §13.1 的理由**：兩者皆是 P216 的成果、即本規範的**基線與參考實作**，不列為擊破標的（§9.3 末段）。數目核對：**§13.1 的 18 項 ＋ §13.2 的聚合體 1 個 ＝ 19 個目錄**，吻合。

### 13.3 更新規則（三條）

1. **誰更新、何時更新**：**每次施工後由施工者就地更新本章**（即時更新，不必等到 phase 結束）；每筆 commit 的回報須附本章相關列的**更新前後對照**（§11.3 欄位 9 已列為必含項）。
2. **更新什麼**：只更新 §13.1 的狀態欄（版本 manifest／`makefile`／首輪 rc／目前 rc／6.2 側不退化）與備註；**不動 §一～§十二 的條文**。若施工中發現規範本身有誤，**另立條目或回報事主**，不在本章就地改規範。
3. **指引檔只指向、不承載**：`AGENTS.md`／`CLAUDE.md`／`.github/copilot-instructions.md` 至多寫一行「施工進度見 `vChewing-DevLogs/Research/Phase217_SOP.md` §十三」，**不得複製本章的表格或數字**——同一份易變資料散在多處，必然走鐘。

### 13.4 ③ 終點段已完成（2026-09-15，第二輪 harness；本節為該輪之實測紀錄）

> **⚠️ 本節〈一〉已於第三輪（同日）更正**：③ 段原判「`contains unsafe build flags` 係沙箱假象、`--disable-sandbox` 可解」**不成立**——見〈一〉現行文字（該兩支 plugin 之產品**在 5.10 SwiftPM 下確不可收**；`--disable-sandbox` 無效、乾淨解析仍復現）。〈二〉〈三〉〈五〉隨之校正。**另：〈一〉所載之「5.10 manifest 不收該依賴」之取捨，已於 2026-09-16 依事主指示翻轉為「與 `Package.swift` 同構」**——該包於 5.10 側因此復歸 rc≠0（18／19）。**其餘結論（兩支終點產物、6.4 側不退化、I2 不破）不受影響。**

> **一句話**：**§十三 的 19 個目錄自此全數 rc=0**（2026-09-16 之翻轉使第 18 位復歸 rc≠0，見下註）；規則 2 的**兩支終點產物皆已產出**，P217 的完成定義（§1.1 末段）在**建置層面**達成。

**一、首輪「第 18 位卡在依賴圖層」經二輪複驗確認成立——③ 段原判「環境假象」已推翻。** 首輪（及 ② 段複驗時）所見的

```
error: 'vchewing_mainassembly4darwin': the target 'CSQLite3' in product 'TextTemplateAssetInjectorPlugin' contains unsafe build flags
error: 'vchewing_mainassembly4darwin': the target 'CSQLite3' in product 'VanguardTextMapPlugin' contains unsafe build flags
```

**確係 SwiftPM 對 `CSQLite3` 之 `unsafeFlags(["-w"])` 的實質拒絕**：該靶屬遠端 `vChewing-VanguardLexicon`，而兩支 plugin 產品皆含它，5.10 SwiftPM 對**非根套件**的 unsafe flags 一律硬拒。三條獨立實測：① `--disable-sandbox` **無效**；② 清空 `.build/.legacy` 後之**乾淨解析**（強制重新 fetch ＋ 重新計算版本）**仍復現**同樣兩行；③ `swift build --help` 實查——5.10 **沒有**任何「允許依賴 unsafe flags」的開關。**處置**：5.10 manifest **不收**該遠端依賴與兩支 plugin（依 §5.1(g)「legacy 為現成答案」之原則自決；**已隨 P217 收工入庫**——事主如不認可此取捨，改回該依賴即令本包 5.10 側不可建置）——本側是**可建置性**驗證、產物為不帶資源的靜態 `.a`；而真正要出 macOS 10.9 app 的 legacy 倉庫本即自帶 `DictionaryData/`、不經此二 plugin 取得辭典，`Sources/` 亦不 import 該套件任何模組（實查 import 全集：SwiftExtension／AppKit／Foundation／Carbon／Darwin／IMKUtils／LibVanguard／ResourceLocator／UniformTypeIdentifiers／Shared／Shared_DarwinImpl）。**6.4 側不受影響**：新世代 SwiftPM 允准 plugin 靶的 unsafe flags，`Package.swift` 原樣保留該依賴與兩支 plugin（根 `swift build` 實測 rc=0）。**§十二 R7 之 (b) 至此結清為「5.10 側不可收」**；其 (ii)（`Package.resolved` v3 ＋ `originHash` 之相容性）因該依賴自 5.10 側退場而**自動無關**。

**二、第 18 位的原始碼層診斷共 10 條、涉 6 檔，處置如下**（全數落在既有格內，未新增 `@MainActor`、未動 `project.pbxproj`／CI／格式化設定）：

| 檔 | 診斷 | 處置（依 SOP 條文） |
|---|---|---|
| `LXManager/UserPhraseImpl.swift:11` | `'nonisolated' modifier cannot be applied to this declaration`（標頭 `nonisolated extension FileHandle`） | **§5.1(b) 下放至成員**：標頭之 `nonisolated` 撤除、6 個 `@backDeployed` 成員各標 `nonisolated` |
| `MainSputnik.swift:12` | `call to main actor-isolated static method 'wireUp()' in a synchronous nonisolated context`（`SettingsUIHost`／`SessionHost` 各一） | **§6.2 調度寫法**：於 `init` 內套一圈 `mainSync { … }`（本型別依設計必在主執行緒；**非** `{ @MainActor in }`） |
| `MainSputnik.swift:30` | `concurrency is only available in macOS 10.15.0 or newer`（`asyncInit()`） | `@available(macOS 10.15, *)`——**與 `InstallerAssembly4Darwin` 之 `MainSputnik4Installer.asyncInit()` 同款處置** |
| `SessionController/IMEMenuSputnik.swift:87` | `cannot find 'CtlSettingsUI' in scope` | **§5.1(f)／鐵律五**：設定選單項整段包進 `#if compiler(>=6.2)`；5.10 分支祇留 AppKit 版一項 |
| `SessionController/InputSession_DarwinSurface.swift:106` | 同上 | 同上；5.10 分支直接 `CtlSettingsCocoa.show()`＋`NSApp.popup()`，**與 `vChewing-OSX-Legacy` 的同名實作逐字一致** |
| `LXManager/LXMgr_Core.swift:99`、`:450` | `call to main actor-isolated … in a synchronous nonisolated context`（`Notifier.notify`／`NSApp.popup`） | 依 legacy 形狀改走 `DispatchQueue.main.async { @MainActor in … }`——5.10 側 `mainSync` 之閉包不帶隔離，故該側不可用 |
| `vChewing_SettingsUI/Sources/SettingsUI/SettingsUIHost.swift:15` | （**間接**：其顯式 `@MainActor` 令上一列之 `wireUp()` 成為硬錯誤——`mainSync` 之閉包在 5.10 側不帶隔離） | **撤除該顯式 `@MainActor`**：legacy 同名檔本即無此標註（其檔內註記明言「legacy 為 Swift 5 語言模式、無預設 MainActor 隔離，故不標註」），6.2 側改由 `defaultIsolation` 提供**同一隔離**、語義不變（§6.1「那一刀」之同一手法）。**必要性已實測**：復原該標註即令 `MainSputnik.swift:20` 報 `call to main actor-isolated static method 'wireUp()'`、rc≠0 |

改動規模：**7 檔、+123／−54 行**（含 `Package.swift` 之 6.2→6.4 抬版乙行；不含新鋪之六份 manifest 與 `makefile`）。

**三、本輪實測（同框對照）**

| 項目 | 動工前（首輪） | 本輪（③ 之後） |
|---|---|---|
| `make build510-all` 之 rc 分佈（**二輪複驗：直接以 `make build510-all` 跑，未加任何額外旗標**） | 19 目中 18 目 rc=0 | **19 目中 19 目 rc=0、0 error**（`_MainWorkspace/tmp/p217-verify-510.sh` 之 `--disable-sandbox` 變體亦同為 19／19）　**⚠️ 該 19／19 以「MainAssembly 之 5.10 manifest 不收 lexicon 依賴」為前提；2026-09-16 事主指示改回同構後，該包復歸 rc≠0（18／19）——見 §13.1 第 18 列與 §十四 N4** |
| 規則 2 終點產物 | `libInstallerAssembly4Darwin.a`（3.2 MB） | **＋ `libMainAssembly4Darwin.a`（26 MB）**；兩者皆 `file` → `current ar archive`、`vtool` → `not mach-o`（靜態封存、不帶 load command） |
| 6.4 側倉根 `swift build` | rc=0 | **rc=0**（Build complete 5.10 秒） |
| 6.4 側聚合體 `swift test --no-parallel` | 535 項 0 失敗 | **535 項 0 失敗**（9 個測試靶，逐靶 18／37／7／6／203／193／61／3／7） |
| I2 byte-sync | 全項 `cmp` 通過 | **全項 `cmp` 通過**（六份 manifest ×2 位置 ＋ 聚合體 `makefile` ＋ `Sources`／`Deps` `diff -rq` 零差異） |
| `make lintFormatUncommitted` | **未跑** | **已跑**：SwiftLint ＋ SwiftFormat 連跑之**淨結果為零變動**（`git diff --shortstat` 於該管線前後皆為同一組數字——② 段當時 68 檔／+4028−3663、③ 段之後 74 檔／+4150−3716；兩輪皆零變動，即產物本即符合該管線格式，管線具冪等性） |

> **✅ 一項既存測試不穩定——已修復（2026-09-15 深夜，`45bb0ac LibVanguard // Patch unit test issues.`，16 檔、+490/−412）**：本節原先列報「聚合體 6.4 側 `swift test --no-parallel` 之 `test_IH400_MixedAlnumKanjiInputTest_Izanami(_:_:)` 間歇失敗（四次連跑之 issue 數 4／3／0／0）」——根因為**測試彼此踩踏行程內全域狀態**（`LXFacade.factoryTrie`／`lxCassette`、`PrefMgr.shared`、`SessionHost.shared`）＋該測試是全靶唯一「跑遍整張注音表卻未把 `asyncLoadingUserData` 壓成 `false`」者。**修法與驗收見 §十二 R23 之 (b)(c) 與 `Phase216_PostResearch.md` §十四**：`LibVanguardTests` 收進單一 `.serialized` 根 suite、該測試補上同步載入、`HomaTests` 之堆積哨兵改為多次取樣；**兩倉各以 `swift test --no-parallel` 連跑 5 次全綠（535 項、0 issue）**。**故本節上述「以兩次連跑皆綠為準」之臨時判準不再需要**；`--no-parallel` 與 `.serialized` 兩道防線仍**缺一不可**（理由見 R23 末段）。**與 P217 之 5.10 手術無關**之判斷不變（中招者位於聚合體、6.4 側）。

**四、環境註記（下一輪務必先讀；此為工具層，非規範變更）**

1. **`make build510`／`make build510-all` 現已恢復為可用入口**（③ 段時期的「19 包假性 rc=2」已隨 5.10 manifest 不再收 lexicon plugin 而消失；本輪**實測 `make build510-all` 得 19／19 rc=0、零 error**；**2026-09-16 改回同構後為 18／19**）。該現象的**唯一**成因是 MainAssembly 的 plugin 依賴（見本節第一點）；其餘 18 包在任何時期皆不受影響。逐包 `makefile` **自始至終未改**。
2. **6.4 側之 `swift test` 於本 harness 下須 `--disable-sandbox`**（事主 2026-09-15 明示此為正解，勿以提權繞過）；`swift build` 則否。SwiftPM 另會對 `~/Library/org.swift.swiftpm` 與 `~/Library/Caches/org.swift.swiftpm` 報不可寫警告——以 `--cache-path`／`--config-path`／`--security-path` 指入工作區即可消音。逐包走訪腳本留存於 `_MainWorkspace/tmp/p217-verify-510.sh`（**工作區暫存物，不進任何倉庫**）。
3. **PATH 上的 `swift` 仍為 6.3.3**（非 6.4）：驗 6.4 側務必明寫 `~/Library/Developer/Toolchains/swift-6.4.0-RELEASE.xctoolchain/usr/bin/swift`，否則被自家封堵檔攔死。

**五、收工狀態與未竟文書項（2026-09-15 收工時之實測；2026-09-16 追加與 rebase 後之複測見末行）**

| 倉 | HEAD | 變動 |
|---|---|---|
| `vChewing-macOS` | `3ecbe770`（`MainAssembly // Swift 5.10 compilability.`） | 收工時 **clean**；2026-09-16 之追加 43 項（42 份封堵檔 ＋ `Packages/vChewing_MainAssembly4Darwin/Package@swift-5.10.swift`）**已隨該倉 rebase 入庫——現值 clean**（已複驗：該 manifest 之 lexicon 相依與兩支 plugin、以及 42 份封堵檔皆在 `HEAD` 之樹內） |
| `vChewing-LibVanguard` | `45bb0ac`（`LibVanguard // Patch unit test issues.`） | 收工時 **clean**；2026-09-16 之追加 4 項（聚合體與 `Deps/VanguardSwiftExtension` 之封堵檔各 2 份）**已隨 rebase 入庫——現值 clean** |
| `vChewing-DevLogs` | `4429504`（`P217.`） | **clean**（`Research/Phase216_PostResearch.md`／`Research/Phase217_SOP.md`／`Reqs4LLM/Archive_P201-P300/Reqs_0211-0220.md` 三者已入庫） |

**任務 B 之「不得 commit」政策已隨收工解除**：兩碼倉的全部改動均已入庫：19 個 subpackage 各**六份 manifest**（`Package.swift` 宣 6.4 ＋ 5.10／6.0／6.1／6.2／6.3 五份對位與封堵檔）、各**一份逐包 `makefile`**（17 份為新鋪，`vChewing_Hotenka` 與聚合體兩份係既有檔追加 5.10 段），外加 18 個 subpackage 之 `Sources/` 圈隔與「下放 `nonisolated`」改動、以及**封堵令之 10 份新檔**（5 個位置 × `Package@swift-6.2`／`6.3` 各一）。`AGENTS.md`／`CLAUDE.md`／`.github/copilot-instructions.md` 之 tools-version／CI 版本／manifest 份數**已補正**（6.2→6.4、Xcode 26.6→27.0、三份→六份 manifest；並補記 MainAssembly 之 5.10 manifest 之 lexicon 取捨——該取捨已於 2026-09-16 翻轉，見下）——此係事主「這幾個檔案都得檢查調整」之明確指示，非順手整理。

**封堵檔訊息措辭一致化（2026-09-16 已辦）**：全倉 **46 份**封堵檔（`Package@swift-6.2/6.3` × 23 個位置：兩倉之聚合體、兩者之 `Deps/VanguardSwiftExtension`、`vChewing-macOS` 之 18 個 subpackage 與倉根 meta-manifest）的 `#error` 訊息自此**同構**：第 1 行僅換上該處之 scope 名、第 2～4 行逐字相同，第 5 行只有「倉根 meta-manifest 無 5.10 對位」者省去 5.10 一語。**模板見 §十二 R22 末段**；實測（6.3.3 toolchain）：任一位置皆於 manifest 編譯期以新訊息攔下。**兩倉之鏡像配對仍逐位元組相同**（`cmp` 實查）。

**`vChewing_MainAssembly4Darwin` 之 5.10 manifest 改回與 `Package.swift` 同構（2026-09-16，事主指示）**：該 manifest 現收遠端 lexicon 依賴（`exact: "4.7.4"`）與兩支 build plugin，與 `Package.swift` 對位；**代價是該包於 5.10 側復歸 rc≠0**（失敗於依賴圖層之 `contains unsafe build flags`），故全倉 `make build510-all` 之現值為 **18／19**（其餘 18 個目錄不受影響；6.4 側 `swift build` 實測 rc=0）。**正解在 lexicon 倉**：移除其 `CSQLite3` 靶的 `.unsafeFlags(["-w"])`（並使兩支 plugin 產品的平台宣告不低於本側之 `nil` 地板）後出新版——已登記為 §十四 **N4**。該 manifest 檔頭第 5 條已就地載明此事與兩條已實測之替代路（`--disable-sandbox` 無效；`.package(path:)` 可過 unsafe flags、但撞 10.15 平台下限）。

**hash 複測（2026-09-16，事主三倉各自 rebase 之後）**：本檔與 `Phase216_PostResearch.md`、`Reqs_0211-0220.md` 中所引之「現行」hash 已全數複測更新（`vChewing-LibVanguard`：`45bb0ac`／`6609f5b`；`vChewing-macOS`：`3ecbe770`／`cad648e3`／`588d1b8e`／`48ff88ef`；`vChewing-DevLogs`：`4429504`／`942557d`）。三倉於該次複測時皆 **clean**。依 §十二 R12，hash 仍會隨下一次 amend／rebase 失效——**判準一律以「訊息 ＋ 小節主題」為準**。

---

## 十四、下一 phase 的待辦（P217 不處理）

**本章承接事主裁定 Q08 之 (b)。** Q08 把「5.10 編譯是否納入既有目標鏈」分流為兩層：**Swift Package 側＝本 phase 處理**（§2.4）；**macOS 10.9 唯音輸入法（app／xcodeproj 側）＝留待下一 phase**。以下即後者，於 P217 內**不處理**，僅登記以免散失。（**N3 為例外**：它不是 Q08(b) 的後續，來源是 P216 §13.6 的備忘；因同屬「P217 不做、下一 phase 才動」而一併登記於此。）

| # | 待辦 | 為什麼現在不能做（事主原文） | 前置條件 | 指向 |
|---|---|---|---|---|
| **N1** | **讓 5.10 側的產物鏈進「macOS 10.9 唯音輸入法」的 app 建置**（含 `vChewing.xcodeproj` 端把兩支 assembly 的 `.a` 鏈進最終 binary、並在該處完成 libArcLite 與 macOS 10.9 compatible Swift Runtime 的摻入） | 「如果是指對 **macOS 10.9 的唯音輸入法**的話，此乃**待決事項**。**這得需要我部署好 macOS 10.9 專用的 xcodeproj 才行。留待下一個 phase 處理。**」 | **事主先部署「macOS 10.9 專用的 xcodeproj」** | §1.1（終點）、§4.2 第 4 條（`.a` 之用途）、§9.6（⑦⑧ 兩處已定案之背景） |
| **N2** | **舊版 Xcode 專用 pbxproj 的建立與維護**（與新 Xcode 分開） | 同 Q07：「Legacy 倉庫的建置會引入『舊版 Xcode 專用的 pbxproj』。如果都讓一個 pbxproj 負責的話，新版 Xcode 可能會自動摧毀掉舊版系統的 compilability。」 | 同 N1（需先有 10.9 專用專案） | §1.3、§9.6（Q07 處） |
| **N3** | **已完成（2026-09-15）**——原待辦：**待 Swift 6.4 正式問世後**，把 **Swift 6.2／6.3 加入封堵清單**（**兩倉同步**），使 Swift 6.x 的工具鏈僅支援 **6.4+**。落地：五個 `Package.swift`（兩倉之聚合體、聚合體之 `Deps/VanguardSwiftExtension`、`vChewing-macOS` 倉根 meta-manifest）之宣告值抬到 6.4 ＋ 各鋪兩份封堵檔；三系統 CI 的 toolchain pin 同批抬到 ≥6.4（本機驗收：6.3.3 被攔、6.4.0 之 535 項測試全綠）。commit：`vChewing-LibVanguard` = `6609f5b`、`vChewing-macOS` = `588d1b8e`。**歸屬（2026-09-15 事主劃定分水嶺後定案）**：本筆於 macOS 側之**倉根 meta-manifest ＋ 三條 CI workflow**（toolchain pin 抬至 ≥6.4）屬 **P217**——記於 `Reqs4LLM/Archive_P201-P300/Reqs_0211-0220.md` 之〈P216／P217 之分水嶺〉；其**LibVanguard 側**（封堵檔與 manifest 抬版）則與 `6609f5b` 同屬 **P216**、記於同卷 P216 之〈跨倉同步〉對照表。**同一筆 commit 橫跨兩 phase 時，按檔案所屬分記、不整筆重複登記。** | 「過幾天等 Swift 6.4 正式問世之後將 Swift 6.2 與 6.3 加入封堵清單、Swift 6.x 的工具鏈僅支援 Swift 6.4+。」（理由：6.2／6.3 對本倉的兩個 conformance 噴 `#ConformanceIsolation`、要求明文 `@MainActor`——**三系統 CI 已逐條核對，Swift 6.2 亦然**，見 P216 §13.6.8） | **Swift 6.4 正式問世**（已滿足：`swift-6.4.0-RELEASE` 於 2026-09-14 發佈）；且須與**三系統 CI 的 toolchain 換版同一批落地**（否則封堵令會先把 CI 擋死）（已同批落地）；另須確認建置環境可指定 Open Source Toolchain（Intel Mac 側的 Xcode 上限為 26.x，見 §2.2 環境認知與 P216 §13.6.9） | **P216 §13.6**（實測、方案 B、屆時要動的清單）、§三（封堵檔的未來擴充）、§十二 R22 |
| **N4** | **讓 `vChewing-VanguardLexicon` 出一個「5.10 可消費」的版本**——移除 `CSQLite3` 靶的 `.unsafeFlags(["-w"])`（或改用非 unsafe 的等效設定），並確認兩支 plugin 產品（`TextTemplateAssetInjectorPlugin`／`VanguardTextMapPlugin`）的平台宣告不低於 5.10 側之 `nil` 地板（10.13）。辦妥之後，`vChewing_MainAssembly4Darwin` 之 5.10 manifest 即可與 `Package.swift` 同構而仍可建置（該 manifest 目前已同構、故該包 5.10 側 rc≠0） | 「**已經與 Swift 5.10 相容。**現階段不用處理。」（事主 2026-09-15 之 Q09）——惟 2026-09-16 之實測顯示其在 **SwiftPM 依賴層**仍不相容；改動該倉屬**另一倉庫之發版作業**，非本 workspace 之建置手術所能代勞 | `vChewing-VanguardLexicon` 出新版（並把 `exact:` pin 抬到該版） | 本 SOP §十二 R7、§13.1 第 18 列、§13.4 第一點 |

> **N4 已由 P218 取代（2026-09-16）**：lexicon 之 deploy 工具真正用上 Swift Concurrency（其 manifest 須宣告 macOS 10.15），本側 5.10 既不可能收它、亦無法靠降其地板或抬本側地板解套；「另尋資料注入他法」移入 P218。

**P217 的邊界（提醒）**：本 phase 的完成定義**到「兩支 assembly 的 `.a` 可供 Xcode 鏈接」為止**（§一），**不含**把 `.a` 真的鏈成可執行的輸入法、也不含 10.9 的實機執行。N1／N2 正是那條邊界之外的第一段路。

**§十四 與 §十三 的關係**：§十三 記「P217 內、逐包的進度」；§十四 記「P217 之外、下一 phase 的交接」。**兩者都隨時間更新，但都不屬於 §一～§十二 的規範本體。**

---

## 事主裁定（2026-09-15，逐條）

**本節為裁決沿革之正本。** P217 開工前所列的 13 個編號項，其中 **12 個有效問題已由事主於 2026-09-15 逐條裁定**（Q01～Q12）；第 ④ 項因 Q01 的答覆而**連帶作廢**（其前提「若 ① 納入」已不成立）；第 ⑬ 項事主本輪未逐條裁定，**依本 SOP 之暫定預設結案**（見表末註）。**本 SOP 已無待補細則**；P217 已於 2026-09-15 收工（見 §十三）。

### 裁定表（13 列：Q01～Q12 ＋ ⑬之預設結案）

| 原編號 | 問什麼 | 裁定 | 依據／理由（事主原文） | 正文落點 |
|---|---|---|---|---|
| **Q01（①）** | `vChewingDebuggable` 是否做 5.10 相容？ | **目前不需要。** | 「這個 target 是用來測試 memory footprint 的。所有不內建 Swift Runtime 的 macOS 系統下的記憶體佔用可能都會多出 200MB、以供 Swift Runtime（包括各種 Swift AppKit Shim dylib）使用。此乃已知狀況，不需要 `vChewingDebuggable` 再專門據此測試。」 | §1.1 表、§1.3 |
| **Q02（②）** | Legacy 繼承清單（哪些模組可繼承） | **case-by-case 逐一確認。** | 「Legacy 倉庫的本質是 vChewing-macOS 倉庫的**子集 ＋ Swift 5.10 Dialect**。之所以說是『子集』，是因為**砍掉了 SwiftUI**。」 | §1.3、§5.1(g) |
| **Q03（③）** | 最低 macOS 版本的最終取捨（`platforms` 填什麼） | **5.10 專用 manifest 的 `platforms` 一律填 `nil`**；SwiftUI 一律 macOS 14+。 | 「這樣才能逼著 Xcode 15- 拿 macOS SDK 確認 **10.9 API 合規性**。換言之就是對一般情況**故意不設 Availability 限制**。**SwiftUI 的 Availability 一律 macOS 14+**。」 | §2.3、§四、§5.5 |
| **Q04（④）** | 非出貨靶的產物形態（minOS／triple） | **作廢。** 因 ① 不納入，**非出貨靶不存在於 5.10 側**，本項失其前提。 | 同 Q01 | 已自 §4.3 移除；原處改記「本項已作廢」 |
| **Q05（⑤）** | `Tekkon.sharedCache` 是否併辦？ | **不用處理。** | 「**Tekkon 與 Homa 都不用處理**，因為已經相容，**都在 P216 解決了**。這兩個 target 的建置**沒有被釘死在 MainActor 上**，且 Legacy 倉庫的寫法目前也是 `nonisolated(unsafe) private static var sharedCache: [Int: PinyinTrie] = [:]`。」 | §6.4（＋§5.4 對齊） |
| **Q06（⑥）** | `withFileHandleQueue` 是否退役？ | **不用退役。** 並立三條規則。 | 「這個 Queue **只管任務觸發時機**，實際的 lambda expression 內的任務執行仍舊**套一圈 MainActor `mainSync`**（**需要以 `mainSync {}` 觸發、而非 `{ @MainActor in }` 等不相容寫法**）。**POM 相關的 Queue 同理。**然而，你得注意，**不能讓同一個檔案被多個 Actor 同時讀寫**。」 | §6.2、§6.4、§十二 R21 |
| **Q07（⑦）** | `project.pbxproj` 是否要動？ | **先不動。** | 「Legacy 倉庫的建置會引入『**舊版 Xcode 專用的 pbxproj**』。如果都讓一個 pbxproj 負責的話，**新版 Xcode 可能會自動摧毀掉舊版系統的 compilability**。」 | §1.3、§9.6 |
| **Q08（⑧）** | 5.10 編譯是否納入 `Packages/Makefile` 既有目標鏈？ | **分流**：(a) **Swift Package 側＝納入本 phase**；(b) **macOS 10.9 唯音輸入法（app／xcodeproj 側）＝留待下一 phase。** | 「如果只是 **Swift Package** 的話，請處理；如果是指對 **macOS 10.9 的唯音輸入法**的話，此乃**待決事項**。這得需要我部署好 **macOS 10.9 專用的 xcodeproj** 才行。**留待下一個 phase 處理。**」 | §2.4、§九、§十一、**§十四** |
| **Q09（⑨）** | `vChewing-VanguardLexicon` 是否同批處理？ | **不處理。** | 「**已經與 Swift 5.10 相容。**現階段不用處理。**Swift 版本低於 5.10 的時候會自動報錯。**」 | §1.3；§十二 R7 改註（見下）；**2026-09-16 之實測補充見 §十四 N4**（該套件於 5.10 SwiftPM 之依賴層不可消費一事，另立待辦） |
| **Q10（⑩）** | 測試項數門檻（逐包不減／總帳守恆） | **不設門檻。** | 「單元測試**僅在 Swift 6.2+ 的情況下啟用**，你這次手術應該**不用處理其行文**。除非**手術後單元測試盤點時發現錯誤需要調整**。」 | §十 |
| **Q11（⑪）** | commit 切分粒度偏好 | **先不要切分**（可自由）。 | 「**先不要切分 Commit。**或者你**按照你的想法切分也行**，反正最後我可能都得統一處理。」 | §11.1 |
| **Q12（⑫）** | 兩份 `@backDeployed` FileHandle shim 是否退役 | **退役。** | 「**退役。**相關的語法糖**已經被我寫在 `VanguardSwiftExtension`** 了，直接用。」 | §7.2 |
| **（⑬）** | 聚合體 `makefile` 是否與 `vChewing-LibVanguard/makefile` byte-identical？ | **依本 SOP 暫定預設結案：維持 byte-identical，並視為 I2 的一部分。**（事主本輪未逐條裁定；此項非「待補」，而是本規範自訂之預設，施工時依此辦理） | 實測兩者**已逐位元組相同**（122 行，`cmp` 通過；本倉已 git 追蹤）；兩倉其餘已 byte-sync，多這一檔邊際成本低、且可防兩側 `LEGACY_*` 漂移 | §2.4、§11.2 |

**表末註**：**本 SOP 已無待補細則**；P217 已於 2026-09-15 收工（見 §十三）。全文不再出現待補標記——原正文各處的待補標記已一律改寫為**已定案的陳述**。仍以「未解」形式保留者，收工時**只剩一項事實層問題**（legacy 之 10.9 疑點；另一項 `Package.resolved` 已因 5.10 側不再收該依賴而消滅）——它不是待裁定事項，只是施工時可能撞上的觀測疑點。

### 前版編號沿革（保留供追溯）

| 舊編號 | 處置 |
|---|---|
| ① | 收斂重寫（出貨執行檔由規則 2 排除；現只問非出貨靶）→ 本輪由 Q01 裁定 |
| ②（新規 2 之前的舊②） | 定案移出（5.10 側用途＝compilability，新規 2） |
| ②（規則 3 衍生者） | 原列「Legacy 繼承清單」→ 本輪由 Q02 裁定為 case-by-case |
| ③、④ | ③ 由 Q03 裁定；④ 因 Q01 連帶作廢 |
| ⑤、⑥、⑦ | 分別由 Q05、Q06、Q07 裁定 |
| ⑧（規則 8 衍生者） | 由 Q08 裁定為分流（Package 側納入、app 側留待下一 phase）；**原「CI 不納入」之定案仍有效**（§八 第 9 條） |
| ⑨、⑩、⑪、⑫ | 分別由 Q09、Q10、Q11、Q12 裁定 |
| ⑬（兩條基礎設施規則衍生） | 未經事主逐條裁定；**依預設結案**（見上表末列） |
| （更早已移出者） | 原②「5.10 側用途」＝新規 2 定案；原⑧「CI 不納入」＝新規 8 定案。兩者皆見 §八 與 §1.1 |

### 事實層的開放問題（非裁定事項，施工時可能撞上）

- ~~**`Package.resolved` 的版本相容性**~~（**已消滅，2026-09-15 收工時結清**）：5.10 側的 manifest 既已**不收**該遠端 lexicon 依賴（理由見 §十二 R7 與 §13.4 第一點），5.10 SwiftPM 對該檔即**無所解析**——`Package.resolved` 本就為 repo-wide `.gitignore` 所略，其「`"version": 3` ＋ `originHash` 能否被 5.10 讀懂」之問題**自此不存在**。（Q09 所確立者——lexicon 本體與 5.10 相容——不受影響，惟 5.10 側已不使用它。）
- **legacy `project.pbxproj` 的 `MACOSX_DEPLOYMENT_TARGET = 10.9` 與 `Data` 實測相牴觸**（P216 §十一 第 5 項）：**疑點未解**。惟 Q03 已把本 phase 的處置定為「`platforms: nil`、故意不設 Availability 限制、交由 Xcode 15 ＋ macOS SDK 端裁決 10.9 合規性」，故此疑點**不阻塞施工**，留作觀測。
