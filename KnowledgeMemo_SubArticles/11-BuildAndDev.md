<!-- 本檔為 vChewing-DevLogs/KnowledgeMemo4LLM.md 之分卷；索引：../KnowledgeMemo4LLM.md
     開工前請先讀索引，再依〈三、任務→必讀分卷〉取用本檔。 -->

# 十、建置與開發（上）：建置要求、指令、測試指令與程式碼格式化

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
swift build   # 6.4+ 側（macOS、debug）
make iOS      # iOS 27 側（release、arm64 device）：產物 libVanguard.dylib、platform IOS／minos 27.0
```

> **`make iOS`（P289 起）**：只出 `Vanguard` 一個產品（另兩者為測試素材目標，release 建不出——見 §12.6）。SDK／triple／產品／scratch／旗標皆為變數：模擬器為 `make iOS IOS_SDK=iphonesimulator IOS_TRIPLE=arm64-apple-ios27.0-simulator IOS_SCRATCH=.build/.ios-sim`；本機 harness 內另須補 `IOS_FLAGS=--disable-sandbox`（同 §10.5 之舊例，該旗標不寫死於 makefile）。`clean-iOS` 清其 scratch。

### 10.3 測試指令

```bash
make test          # Release 模式測試
make test-debug    # Debug 模式測試
make dockertest    # Docker 容器測試（Linux）
```

> **SwiftPM 之測試一律附 `--no-parallel`——這是必需條件、非偏好（事主 2026-09-24 再次明示）**：本倉各目標之測試共用 `UserDefaults` 等行程內靜態狀態，並行執行即互相搶奪其 I/O 與狀態（macOS 倉 `Makefile` 之 `test:` 目標註解、以及各套件 `makefile` 皆已記明）。另依 §12.6：本工作區之 SwiftPM 執行一律附 `--disable-sandbox`（SwiftPM 之內層 sandbox 與 harness 之 sandbox 不疊加）。

> **兩顆 `swift test` 不得同時跑——`--no-parallel` 只治「同一行程內之各目標」，不治「兩個行程共用同一批 `UserDefaults` 網域」（2026-09-25 實錄；事主指出此誤兩個月內已不止一次）**：`UserDefaults.unitTests` 之**預設值即 `UserDefaults(suiteName: "UnitTests")`**（`Deps/VanguardSwiftExtension/Sources/SwiftExtension/SwiftFoundationImpl.swift:186-188`），而各測試 suite 之 `init` 又把它改指向各自的具名 suite（如 `org.atelierInmu.vChewing.LibVanguard.SessionTests`）；**具名 suite 係落在磁碟上的 plist（`~/Library/Preferences/*.plist`）、跨行程共用**，且 `UserDefaults.current` 於 `pendingUnitTests` 為真時即取用之（同檔 `:179-181`）。故同時跑兩顆 `swift test`（典型：`vChewing-LibVanguard` 與 `vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard` 各一顆）時，兩個行程會互搶同一批偏好檔。**受害表象**：`LibVanguardTests` 中「先 `UserDef.resetAll()`、再斷言打字結果」之 session／candidate／狂拼測項成群失敗（`state.candidates.isEmpty`、`displayedText` 不符、`hasComposition` 為假…），且**每次失敗的測項都不同、單獨重跑即全綠**。**判別法**：凡見此類成群且跨次游移之失敗，**先停掉其它一切測試、單獨重跑該倉**；單獨跑綠即屬偽陽性，不得據以改碼或改資料。**紀律**：同一時間只跑一顆 `swift test`（不與另一倉、不與 Docker、不與「以本機代跑之 CI 目標」並行）；`--no-parallel` 與本條**互不替代、缺一不可**。**何以須記入本文檔**：同款記載原僅見於 `DevReqsHistory.md` 之 Phase 241 條末（「工具層教訓：兩倉之 SwiftPM 測試不可並行跑…其中一邊之總數僅報到 354」）——歷史檔不是開工前會讀的地方，故未能阻止重犯（2026-09-25 又犯一次）。相關之同源陷阱（單一行程內 reset 順序不當造成 stale `cassetteEnabled`）另見附錄二〈LMAssembly 共用 parser / cell tokenizer〉條末之註記。

- **★ LibVanguard 測試之分類與編號新制（2026-10-06，P286；事主指示）**：`Tests/LibVanguardTests/` 之 `InputHandlerTests`／`SessionTests` 一律用 `test_<Suite>_<Category>_<NNN>_<Summary>`（`Suite`＝`IH`／`SS`），且**分類即檔案**——`InputHandlerTests_<Category>.swift`（10 類）／`SessionTests_<Category>.swift`（8 類），`Cases1..5` 之卷制已廢。`@Test` 顯示名一律英文、格式 `[<Suite>-<Category>-<NNN>] <sentence>`。舊 `test_IH###` 與裸 `testNNN` 一律作廢（**歷史文書保留舊稱**）；全量對照表見 `vChewing-DevLogs/Research/Phase286_TestTaxonomyAndNumbering.md`。

> **配置助手之建置與測試（2026-09-24，Phase 241 起）**：於 `vChewing-macOS/ValueAdd/WebConfigAssistant/` 內跑——`make audit`（提交前總檢：`tsc --noEmit` ＋ ES5 守衛 ＋ 測試宿主 `--tests`（**96 支**；數目隨 phase 增長，此為 P303 期之現值）＋ `make metadata`（後設資料防漂移）＋ `make metadata-audit`（`--strict` i18n 稽核）＋ `make fixtures-check`（契約 fixture 防漂移））、`make bundle`（產出單檔 `dist/assistant.html`）、`make metadata-update`（Swift 側 `UserDef` 有變時，重新導出後設資料並入庫）、`make deploy`（複製產物進官網倉；`DOC_BASE`／`DEPLOY_SUBDIR` 可覆寫）。**零 npm 相依**——不需 `npm install`、`node_modules/` 自始不存在。**註**：`node --test` 之引數須為**檔案 glob**（`tests/*.test.js`）；Node 22 之下傳目錄（`tests/`）會以「找不到模組」失敗。

### 10.4 程式碼格式化

```bash
make lintFormatUncommitted  # 交差／commit 前慣用：僅對 tracked 且未 commit 的 Swift 檔依序執行 lint＋format
make lintFormat             # 全倉：SwiftLint 自動修正（先）＋ SwiftFormat（後）
make lint                   # 僅 SwiftLint 自動修正
make format                 # 僅 SwiftFormat（縮排 2 空格）
```

> 交差前「一次性運行」 `make lintFormatUncommitted` 即可（先 lint 後 format 的順序已內建）。注意 lint+format 可能將 `count == 0` 轉為 `.isEmpty`，需確認對應型別確有此屬性，否則改用 `.count * 1 == 0`。
