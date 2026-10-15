<!-- 本檔為 vChewing-DevLogs/KnowledgeMemo4LLM.md 之分卷；索引：../KnowledgeMemo4LLM.md
     開工前請先讀索引，再依〈三、任務→必讀分卷〉取用本檔。 -->

# 十、建置與開發（下）：雙 toolchain 之逐包入口與終點推進

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

> 5.10 側之 manifest（`Package@swift-5.10.swift`——Phase 216 先在聚合體與子套件各鋪一份，**Phase 217 起 `vChewing-macOS` 之 19 個 subpackage 各一份**）刻意**不宣告測試目標**、**不收 `vChewingSharedCLI`**、**`platforms: nil`**，產物一律 static；`Package@swift-6.0.swift`／`6.1.swift`（自 Phase 217 起另含 **`6.2.swift`／`6.3.swift`**）為 `#error` 封堵檔（令各該版 toolchain 明文拒絕建置）。擇定規則與其餘坑見 `vChewing-DevLogs/Research/Phase216_PostResearch.md` 與 `Phase217_SOP.md`。

#### 10.5.1 Phase 217：`vChewing-macOS` 全倉（19 個目錄）的逐包入口

**每個 subpackage 都自成一個可單獨驗證的單位**——各自六份 manifest（`Package.swift`@6.4 ＋ `Package@swift-5.10／6.0／6.1／6.2／6.3`）與**各一份 `makefile`**：

| 入口 | 用途 |
|---|---|
| `cd Packages/<name> && make build510` | **單包深挖**（產物落該包自己的 `.build/.legacy`；`make clean510` 清之） |
| `cd Packages && make build510-all` | **全倉批次**：逐包跑、個別失敗不中斷、逐包列 ✓／✗（`make clean510-all` 清全部分支） |
| `make build510-<目錄名>`（倉根 `Makefile`） | 同上的單包快捷；`make build510-swiftExtension` 走巢狀子套件 |

**性質**：這是**可建置性驗證（compilation test）**，**不是單元測試**——5.10 側的 manifest 與 makefile **刻意不含任何測試目標**；測試一律在 6.4 側跑（§10.3）。

**5.10 側的原始碼層原則（P217 貫徹）**：SwiftUI 之任何內容——**含 `#Preview` 這類巨集**——一律整段圈進 `#if compiler(>=6.2)`；`nonisolated` 自 extension／型別標頭**下放到成員**；availability 用 `if #unavailable() {} else {}` 兩分支；`nonisolated deinit` 改樸素 `deinit`（內容以 `mainSync` 裹上）；`@Sendable` 閉包內不得碰 MainActor 成員（legacy 形狀為 `DispatchQueue.main.async { @MainActor in … }`）；**不得為消錯新增 `@MainActor`**（會殺死 ≤ macOS 10.14 的執行期相容性）。

**終點與驗收**：兩支終點產物 **`libInstallerAssembly4Darwin.a`（3.2 MB）** 與 **`libMainAssembly4Darwin.a`（26 MB）**（`file` → `current ar archive`、`vtool` → `not mach-o`，即不帶任何 load command、minOS 不進產物）；`make build510-all` 於 2026-09-15 達 **19／19 rc=0、0 error**，6.4 側 `swift build` rc=0＋**535 項測試 0 失敗**。

**現值一項例外（2026-09-16）**：`vChewing_MainAssembly4Darwin` 之 5.10 manifest 依事主指示**改回與 `Package.swift` 同構**（收遠端 `vChewing-VanguardLexicon` 依賴與兩支 build plugin），故**該包於 5.10 側復歸 rc≠0、全倉 18／19**——5.10 SwiftPM 對非根套件的 `unsafeFlags` 一律硬拒（該 lexicon 的 `CSQLite3` 目標帶 `.unsafeFlags(["-w"])`），`--disable-sandbox` 無效、改本地 `.package(path:)` 則撞 macOS 10.15 平台下限；**正解在 lexicon 倉**（見 `Phase217_SOP.md` §十四 **N4**）。

**本項已由 P218 接管（2026-09-16）**：lexicon 之 deploy 工具真正用上 Swift Concurrency（故其 manifest 須宣告 macOS 10.15），與本側 5.10 之 10.13 地板相衝；現行作法是 5.10 manifest 不再收該依賴與兩支 plugin（`make build510-all` 因而復歸 19／19 rc=0），「另尋資料注入他法」移入 P218——原因、實測與後續見 P218 之紀錄。（此補註同時取代上方「現值一項例外」所述之狀態。）

**Swift 6.2／6.3 之封堵（Phase 216 起、Phase 217 補齊）**：五個位置各鋪兩份 `#error` 封堵檔（兩倉 12 組 manifest 逐位元組相同），`Package.swift` 之 tools version 抬到 **6.4**，三系統 CI 之 toolchain pin 同批抬到 ≥6.4。**封堵訊息之正本模板**見 `Phase217_SOP.md` §十二 R22 末段（46 份封堵檔同構）。**測試紀律**：`swift test --no-parallel`（CLI 層）與 `@Suite(…, .serialized)`（型別層）**缺一不可**，且單元測試下 `LXFacade.asyncLoadingUserData` 恆為 `false`——見同 SOP §十二 R23。

#### 10.5.2 雙 toolchain 之終點推進（Phase 218 起）

5.10 側自此**真的產出可交付的執行檔**：倉根 `Package@swift-5.10.swift` 出 `vChewing` 與 `vChewingInstallerLegacy`。

- **libArcLite**：以 `-Xlinker -force_load -Xlinker ./LegacyZone/ARCLite/libarclite_macosx.a` 摻入（`-L` ＋ `-larclite_macosx` 實測為虛——`ld` 逕以 SDK 版 libobjc 之匯出滿足符號、**不抽任何成員**；swift driver 亦不認裸 `-force_load`）。**只有 x86_64 支線**摻它（arm64 自 macOS 11 起 ARC 執行期即在 libobjc 內），故該 flag 依 triple 下在倉根 `makefile`。
- **執行期（兩段式 rpath）**：載入記錄保持 `@rpath/libswift*.dylib`，由 `BundleAppsLegacy` 把 Xcode 內 `usr/lib/swift-5.0|5.5/macosx` 之 back-deployment 副本放進 `<build-dir>/Frameworks/` 並追加 `@loader_path/Frameworks`——現行 macOS 之 `/usr/lib/swift/*` 由 dyld shared cache 供貨、故系統執行期勝出，10.9–10.13 才落到內嵌副本。**勿**改用 `install_name_tool -change` 逕指內嵌副本：那會令現行系統也載入 10.9 版本而 abort。該 plugin 另以 `pruneForeignRPATHs(of:)` 清掉建置機 toolchain 的絕對 `LC_RPATH`（`…/swift-5.10.1-RELEASE.xctoolchain/…`），只留 `/usr/lib/swift`、`@loader_path*`、`@executable_path/../Frameworks`。
- **入口與環境**：`make debugLegacy`／`releaseLegacy`／`archiveLegacy`／`cleanLegacy`（scratch `.build/.legacy-root`）；`releaseLegacy` 另建 arm64 slice 並逐支 `lipo` 成 universal（`x86_64-apple-macosx10.9` ＋ `arm64-apple-macosx11.0`）。`DEVELOPER_DIR` **必須 pin 一個「預設 macOS SDK ≤ 14.x」的 Xcode（Xcode 15 即可，任何 ≤ 15.4 者等價）**——這是 `swift build` 一併編譯的 build plugin `BundleAppsLegacy` 之 SDK 來源（`--sdk`／`SDKROOT`／`-Xswiftc -sdk` 三者對它**皆無效**，實測 plugin 之 `commandLine` 記的仍是 active dev dir 的預設 SDK）；CLT 不能當 dev dir（無 `Platforms/`），自製 dev dir 會被 `xcode-select` 判 malformed。C／ObjC 目標另須 `-Xcc -target -Xcc x86_64-apple-macosx10.9`（`-Xcc -mmacosx-version-min` 會被 SwiftPM 自己那條 `-target …10.13` 壓住；clang 讓後出現的 `-target` 勝）。`LEGACY_SDK` 綁 **CLT 那份** `/Library/Developer/CommandLineTools/SDKs/MacOSX13.3.sdk`（Xcode 15 內的同名目錄只是指過去的 symlink；該 SDK **非現行 CLT 所附**——現行 CLT 已把它改成移除包，換機須自行自 macOS 13.3 之 CLT／Xcode 14.3 備妥）。
- **`archiveLegacy`（2026-09-17 補）**：前置 `releaseLegacy`，再令 plugin 以 `--archive` 組出 `Build/Products/vChewingInstallerLegacy-<stamp>hrs.xcarchive`（內含安裝程式（IME 棲於其 `Contents/Resources/`）與兩支執行檔之 dSYM，外加 `Info.plist` 之 `ArchiveVersion`／`ApplicationProperties`），並搬進 `~/Library/Developer/Xcode/Archives/<date>/` 供 Xcode Organizer 手動以 Developer ID 簽名與公證；archive 之所以不直接寫進那裡，是因為 command plugin 之寫入權止於套件目錄。
- **10.9 專屬陷阱**：① **絕不可把 Optional block 交給 libdispatch**——`setEventHandler(handler: nil)` 會被本路徑內建的 Swift 5.0 Dispatch shim 原樣轉成 `dispatch_source_set_event_handler(source, NULL)`，而 10.9 的 libdispatch 對此直接 BUG（SIGILL）；一律改傳 `{}`（現代 libdispatch 容忍 NULL，故 6.4 側從未顯露）。② 辭典資產**自動建置**：`lexiconLegacy` 是 `bundleLegacy` 之前置、跑 `LegacyZone/LexiconBuildTrigger`；其 config 變數是 `LEXICON_CONFIG`（預設 `release`）、**刻意不叫 `LEGACY_CONFIG`**（後者指 app 的 config 且會隨 sub-make 外洩，實測會把詞典建置拖回 debug）。③ `CGRect.seniorTheBeast` 這類跨模組常數一律是各消費檔**檔尾的 `fileprivate` 常數**、不放 `SwiftExtension`（Swift 5.10 `-O` 對跨模組 `CGRect` 常數會 SIL verifier 崩潰）；`vChewing-OSX-legacy` 逐檔同構。
- **concurrency**：整個 5.10 閉包**零 concurrency 引用**（每 slice 20／20 archive 乾淨、兩支執行檔無 `swift_task_*` 未定符號），`@rpath/libswift_Concurrency.dylib` 不再是任何載入記錄；`BundleAppsLegacy` 仍整批備齊該副本，屬未被引用的死重（事主 2026-09-16 裁定不用管）。
- **lexicon 無法被 5.10 側消費**：其 deploy 工具真正用上 Swift Concurrency（需 macOS 10.15），故 `MainAssembly4Darwin` 之 5.10 manifest 不收它——資料改由 `LegacyZone/LexiconBuildTrigger` 這一 throwaway 套件出帶外產出，再由 plugin 注入安裝程式之 `MainAssembly4Darwin_MainAssembly4Darwin.bundle`（`Bundle.currentSPM` 解析的即該 bundle）。
- **legacy 安裝程式的在地化名稱**：與主線共用同一份 `<lproj>`，故 Finder 顯示名原與主線相同；解法是 `LSHasLocalizedDisplayName`（兩側 plist 本已帶）＋ `LegacyZone/InstallerLocalizations/<lproj>/InfoPlist.strings` 的不同 `CFBundleName`，由 plugin 於複製 lproj 後 **merge**（非取代——`CFEULAContent` 必須存續）；IME 側對位者為 `LegacyZone/IMELocalizations/…`（把 `NSHumanReadableCopyright` 改寫為 `Aqua Special Build. …`，供 About 面板顯示）。落點刻意選在 `LegacyZone/`：`Sources/Installer_macOS/` 在 `vChewing.xcodeproj` 裡是同步根群組，把帶 `.lproj` 的新目錄放其下會被掃進**現代**安裝程式的資源 phase。`project.pbxproj` 事主明示**不動**。
- **現況（2026-09-17）**：10.9 真機之輸入法本體運作正常；安裝程式在 10.9 按「安裝」數秒即崩之缺陷已修（見上①）、**修後之 10.9 複驗尚未回報**；10.10／11.x 真機仍未驗。legacy 產物之總記憶體佔用實測**降至 macOS 15 Sequoia／Intel Mac 之水位**（開著偏好設定視窗亦僅 80 餘 MB），機理未查。**本路徑自此為 legacy 發行版之唯一建置來源**——`vChewing-OSX-Legacy` 已於 vChewing **4.8.0** 封存（僅存為 10.9 寫法之參照、不再回寫）。
