# Phase 245 PostResearch：`WebConfigAssistant` 編譯鏈路之 Swift 重寫可行性

> **文檔狀態**：PostResearch（**可行性研究**，不含實作）。
> 用途為供事主裁定；**未經裁定前不得據以動工**。本文之全部建議皆已標明「實測」或「推論」。
>
> **委託**（2026-09-25，Phase 245 結案、Hiraku（皮樂）peer review 通過之後）：
> 「整個 `WebConfigAssistant` 的編譯框架目前用的是 npm 與 TypeScript。我想知道這個鏈路
> （`vChewing-macOS/ValueAdd/WebConfigAssistant/`）是否可以用 Swift 重寫。Swift Concurrency
> 這一層面可以直接用 Actor-based concurrency 且要求 Swift 5.10+（單元測試限 6.4+），這套 Swift
> 工具並不屬於輸入法程式建置的 dependency，只是在建置過後組裝 bundle 的時候運行一下以收錄
> 建置產物。」另有 P.S.：「如果沒辦法的話，用 .NET 10 重寫也行。」
>
> **本文之資料來源**：① 靜態閱讀現況碼（`vChewing-macOS` HEAD `2fe172ca` 之
> `ValueAdd/WebConfigAssistant/` 全部 17 檔 ＋ 其周邊：`Makefile`、`Scripts/vchewing-update.swift`、
> `Plugins/BundleApps/plugin.swift`、`Packages/vChewing_SettingsUI/Tests/SettingsUITests/AssistantContractTests.swift`、
> `vChewing.xcodeproj/project.pbxproj`）；② **十項離線實測**（§二；全部在本機跑過，指令與原始輸出見附錄 A）——Swift 側八項（§2.1-2.8）與 **.NET 側兩項**（§2.9-2.10）。
> 凡屬推論者皆已逐處標註「**推論**」。
>
> **修訂記錄（共三輪；第二輪內含兩次訂正）**：
> ① 2026-09-25 初稿。
> ② 同日第二輪——事主補示兩事：`dotnet` **並非未安裝**（實為 `/usr/local/share/dotnet/dotnet`，僅不在 `PATH`），
> 以及**依賴取得管道**才是關鍵（Apple 平台之 Swift 路線靠系統內建之 JavaScriptCore、零相依；但要在
> Windows／Linux 上搭建同一條管線，Swift 側就得引入 **GitHub 託管**之 SwiftPM 相依，而 GitHub 之套件下載
> 在 GFW 環境下經常受擾；**NuGet 不受擾**）。據此新增 §2.9／§2.10（.NET／Jint 之**實測**）、§7.5（跨平台
> 可攜性與依賴管道），並**改判** §零 之第 5 點、§7.4、§7.8、§八。初稿「.NET 因無 JS 引擎故不可行」之
> 結論**已被實測推翻**，文中如實記之。
> ⑤ 同日第五輪——事主問「dotnet 可能也有些過於肥大。你覺得用 golang 語言的話相比 swift 與 dotnet
> 而言怎樣呢？這些也算入這次的研究。」據此新增 **§7.6 戊：Go**（**實測**：goja 亦達 5／5 ＋ 78／78；
> `go mod vendor` 11 MB ⇒ 零網路；工具鏈 331 MB；**由 macOS 交叉編譯四平台已實測**），
> 並新增準據 ⑦（工具鏈與產物體積、跨平台建置之難易）、更新 §7.8 對照表（增戊欄與體積／速度列）、
> §零（加第 6 點）、§6.2、§八（三分支之取捨表）。**傾向**：就事主所提之兩項關切（取件風險、體積）而言，
> **戊案優於丙案**；惟 goja 為三者中最慢，且 Go 是本倉第三種語言。
>
> ⑥ 同日第六輪——事主指示「你再評估一下 Moonbit 語言」，並自行安裝了工具鏈。據此新增
> **§7.7 己：MoonBit**（**實測**：`justjavac/quickjs` 把 QuickJS 之預編譯靜態庫放進 mooncakes 套件內、
> 取件全程不碰 GitHub；fixture **5／5**、測試 **78／78**、約 1.0 s、產物 1.2 MB、工具鏈 291 MB）、
> 準據 ⑧（**語言與生態之成熟度**）、§7.9 對照表之己欄（並增「引擎之平台覆蓋」「成熟度」兩列）、
> §零 之第 7 點、§6.2 之 8、§八（取捨表增一列，並加「不建議現在採用、宜記為 1.0 後之首選」之傾向）。
> 附錄 H 收錄 MoonBit 側 PoC 全文。**並得一項對四案皆有價值之洞見**：該綁定無「註冊原生函式」之 API，
> 故改以「檔案內容物化 ＋ 間接 `eval`」之**無宿主回呼**設計達成同一目的——宿主門檻由三個函式降為兩個能力。
> 另：本研究隨手將 `~/.moon/bin` 併入 bash（`~/.bash_profile` ＋ `~/.bashrc`，帶守衛）與 nushell
> （`~/.config/nushell/env.nu`）；zsh 由安裝程式自理。
>
> ⑪ 同日第十一輪——事主提出收束：「你看目前已有的 build chain 是否可以脫離對 NODE 的依賴、
> 只要求 devenv 事先安裝 tsc？」**實測後判定該收束成立**，並新增 **§7.10 庚：最小改動案**——
> 關鍵發現是 **macOS 內建 `jsc`**（`JavaScriptCore.framework/…/Helpers/jsc`，具 `readFile`／
> `writeFile`／`load`／`print`／`quit` 等），以之為宿主跑**一字未改**之既有 78 支測試 ⇒
> **78／78、實時 0.138 s（比 node 之 0.219 s 更快）、零安裝**；配合 §7.4.2 管道 D 之原生 `tsc`，
> **整條鏈只要求 devenv 安裝 `tsc`**。本輪並量清剩餘工程（ESM `import` 18 處、`process.*` 31 處、
> `child_process` 1 處、`quit(n)` 不設 rc 之陷阱、argv 之替代機制）與界線（`jsc` 屬 OS 實作細節、
> 有 JXA 後備、此案為 macOS 專屬、建置器仍為 JS）。§八 隨之增列**第零步：先做庚案**。
>
> ⑩ 同日第十輪——事主問「TS7 除了 npm 以外有沒有獨立的 pkg／exe 安裝包？」。實測**四條管道**並新增
> **§7.4.2**：**GitHub Releases**（`microsoft/typescript-go` 之 `typescript/v7.0.2`，**21 個資產**、
> 每平台 8.2–9.6 MB，含 `win32-x64`／`arm64`）、**NuGet**（§7.4.1）、
> **npm registry 之 tarball 直取**（`registry.npmjs.org` 9,270,373 B／2.6 s；
> **`registry.npmmirror.com` 同檔、0.99 s、SHA-256 相同**；解壓 26 MB、`env -i` 下跑出 `Version 7.0.2`，
> 與 npm 安裝者逐位元組相同）。**結論：三條皆無 node**，且本專案之**首選為 npm registry 直取**
> （約 9 MB、可鏡像、< 1 s）；並記明此事**與語言無關**——Swift 驅動之建置器同樣可取用。
> 階段 1b 隨之改指首選管道。
>
> ⑨ 同日第九輪——事主問「Swift 還是得額外需要安裝 typescript 是吧」。查證後訂正本文兩處：
> ① **本機 `tsc` 之實情**——它是 npm 全域安裝之物，入口 `bin/tsc` 為 **`node` 啟動器**，
> 真正的原生編譯器在 `@typescript/typescript-<platform>/lib/tsc`（23 MB）；故**今日建置期本就在用 node**，
> 且 npm 曾被用來裝 TypeScript（先前「npm 只是轉呼 `make`」之印象已訂正）；
> ② **§7.4.1 之取用手法**——「挑 RID 之執行檔」**錯**：實測單獨執行會 panic（缺 `lib.d.ts`），
> 須解**整棵 `tools/` 樹**（162 MB）。並補上實測數字（57.3 MB、17.3 s、`env -i` 下可跑）。
> 據此把階段一拆明為 **1a（Swift 接手）／1b（改原生 `tsc` ⇒ node 徹底退場）**。
>
> ⑧ 同日第八輪——事主報知 Gitee 之 `mirrors_swiftwasm/JavaScriptKit` 鏡像「還比較新（不是最新）」。
> 查證後計兩事：① **鏡像實測**（淺克隆 4.9 s；`main` 落後上游約 5 日；最新標籤 `0.59.0` 與上游相同）
> ——故 §7.5 之緩解③ 由「可行手段」升格為「**已指名、已量測之實例**」，且其意義不限於該套件；
> ② **訂正事主原始關切中之一項前提**：JavaScriptKit **不是**嵌入式 JS 引擎之繫結，而是
> 「Swift/WASM 為客、JS 宿主為主」之互操作框架（其 `platforms` 僅 Apple、且遞移相依 GitHub 之
> `swift-syntax`）——用它反而**同時需要 SwiftWasm SDK 與一個 JS 宿主**，即本問題本身。
> 該路逕予關閉，並改列真正的候選 `jectivex/JXKit`（純 Swift 之 JSC 介面、明文支援 Linux）。
>
> ⑦ 同日第七輪——事主追問「也就是說現在的跨平台編譯最優解是 golang？」。據此於 §八 補一則附註，
> 把「**跨平台編譯**之最優解」與「**整體**最優解」明確分開：前者確為戊案（Go），
> 但附**兩項前提**（優勢建立於「JS 宿主為純 Go」之上；且只保證產得出、本研究未在真實
> Windows／Linux 實跑）與**一項反例**（己案引擎等級較高卻無交叉編譯；Go 在宿主品質上墊底），
> 並記明**目前管線只在 macOS 上跑，故乙案仍是最省事之解**。
>
> ④ 同日第四輪——事主追問「.NET 鏈路是否即可免除 TypeScript 之額外安裝」。此前該句在本文只是
> **未經實測**之推測，本輪驗掉：新增 §7.4.1，記明 `Microsoft.TypeScript.MSBuild` **7.0.1** 自 NuGet
> 取得後內含**六個原生 `tsc`、無 Node**，且以之編譯既有 `src/` **11／11 逐位元組相同**；
> 並記明此利得屬**管道**（nuget.org，純 HTTPS）而非語言，Swift 驅動之流程同樣可取用。
>
> ③ 同日第三輪——事主再指出 `vChewingSharedCLI` **本身即為跨平台**（LibVanguard 於非 macOS 系統下
> 僅要求 Swift 6.4+）。實查後**本文第二處錯誤判斷亦被推翻**：初稿所謂「`make metadata` 永遠不可能
> 跨平台」為假。已改寫 §7.5 之該段（附查核表），並據此**重定立場**：Windows／Linux 上之抉擇不是
> 「Swift 對 .NET」，而是「**Swift 之 JS 宿主該怎麼取**」。
>
> **與既有記錄之關係**：`vChewing-DevLogs/KnowledgeMemo4LLM.md` §A2.2 第 16 條之③已載明
> 「`vChewing-macOS/ValueAdd/` 是 Xcode 之 `PBXFileSystemSynchronizedRootGroup`、且實測 Release 產物不含其內容」；
> 本文 §2.7 在該結論上**追加一項新變數**（`.swift` 檔與 `.ts`／`.mjs` 之型別待遇不同），並未推翻該條。

---

## 零、結論摘要

**一句話**：這條鏈路**三分之二可以改用 Swift 重寫，且價值明確**；剩下那三分之一是
**TypeScript 前端本身**——Swift 無法取代它，但有一條經實測驗證、成本已知的**一次性脫離路徑**。
`.NET 10` 在此倉**不建議**，理由不是效能或語言能力，而是**JS 引擎**（§七）。

1. **npm**：**現況即已無用**——`dependencies` 與 `devDependencies` 皆空、倉內無 `node_modules/`，
   `package.json` 的 `scripts` 只是 `make` 的轉呼。可直接刪除，與本研究無關。
2. **Node（`node` ＋ 794 行 `.mjs` ＋ `node --test` 宿主）**：**可以完全移除**。
   實測：以 **250 行 Swift** 提供 CommonJS 與 `node:fs`／`path`／`vm`／`assert`／`test` 之替身，
   即可讓**一字未改**的既有 **78 支測試**（含 1,096 行之 DOM 冒煙測試）在 **JavaScriptCore** 內
   **78／78 全綠**（§2.2）；同一手段驅動助手之真實 `dist/core.js` 產生契約 fixture，
   **5／5 與入庫版逐位元組相同**（§2.1）。
3. **TypeScript（`tsc`）**：**Swift 不可取代**（那需要一整個 TS 前端）。但可**一次性脫離**：
   以 `tsc --removeComments false` 把 `src/*.ts` 降為**保留註解**的 `.js` 並入庫，其後 `tsc` 即退出鏈路。
   實測：該遷移候選之產物**跑完 78／78 測試、5／5 fixture 逐位元組相同**，代價是出貨產物
   **＋39,303 bytes（+11.3%）**，以及 `src/schema.ts` 那一層之**靜態型別檢查**（§2.8、§5.2）。
4. **Swift 側之要求全部可滿足**：`swift-tools-version: 5.10` 之基底 manifest ＋
   `Package@swift-6.4.swift` 追加測試靶——實測 5.10 toolchain 下 `swift test` 印
   **`error: no tests found`**、6.4 toolchain 下 swift-testing 正常執行；actor 與 task group 在 5.10 下
   編譯並**正確執行**（§2.3）。
5. **`.NET 10`（實測後改判；初稿之否定已被推翻）**：初稿誤判「本機未安裝 `dotnet`」——
   實情是 **`.NET` SDK 10.0.201 已在**（`/usr/local/share/dotnet/dotnet`，僅不在預設 `PATH`）。
   以 **NuGet** 取得之 **Jint**（純受控碼、無原生資產）**實測同樣跑出 5／5 fixture 逐位元組相同
   與 78／78 測試**（§2.9／§2.10），故「無法以真實產物驅動」之斷言為假。
   丙案與乙案之真正分野因此移到**兩處**：**引擎等級**（JSC 是瀏覽器級、Jint 是解譯器）
   與**依賴管道／跨平台**（乙案在 Apple 平台零相依，但出了 Apple 就靠 **GitHub 託管之 SwiftPM 相依**；
   丙案**一條 NuGet 管道通吃三平台**）。**建議改為條件式**（§八）：
   另（第四輪實測）：**TypeScript 本身亦可自 NuGet 取得**——`Microsoft.TypeScript.MSBuild` 7.0.1
   內含**六個原生 `tsc` 執行檔、無 Node**（TypeScript 7 已是 Go 原生版），以之編譯既有 `src/`
   **11／11 逐位元組相同**（§7.4.1）。故丙案在三平台上可做到「**不另裝 TypeScript、亦不裝 Node**」；
   惟該利得屬 **NuGet 這條管道**、非 .NET 獨有（`.nupkg` 即 zip，純 HTTPS 可取）。
   管線只在 macOS 上跑 ⇒ 乙案；需在 Windows／Linux 上跑，則**取決於該平台之 JS 宿主能否用
   `node` 或發行版 WebKitGTK 之 JSC**（能用 ⇒ 仍是乙案，因 `dump-userdef-metadata` 本即跨平台）；
   若 JS 宿主亦須避開 node 與 GitHub ⇒ 丙案（代價：**兩套**工具鏈）（§7.4／§7.5／§八）。

6. **`Go`（戊案；事主 2026-09-25 追加）**：實測可行，且**在事主所提之兩項關切上皆優於 .NET**——
   以純 Go 之 **goja** 同樣達到 **5／5 fixture ＋ 78／78 測試**（既有測試一字未改）；
   **`go mod vendor` 可把全部相依（11 MB）入庫 ⇒ 建置期零網路**（`GOPROXY` 本機已設為
   `goproxy.cn` 鏡像，即依賴管道亦在可鏡像之範圍內）；工具鏈 **331 MB**（.NET 為 3.0 GB）；
   且 **`GOOS`／`GOARCH` 已實測由 macOS 直接產出 Windows／Linux 之 amd64／arm64 執行檔**
   （各 12–13 MB、靜態、無執行期相依）。代價：**goja 為三種宿主中最慢**（1.78 s 對 0.76 s 對 0.31 s）、
   且**仍不能取代 Swift**（metadata 那一步），故與 .NET 同為「兩套工具鏈」（§7.6、§八）。

7. **`MoonBit`（己案；事主 2026-09-25 追加）**：**實測可行，且引擎等級為四案之次高**——
   mooncakes 上之 `justjavac/quickjs@0.1.5` **把 QuickJS 之預編譯靜態庫直接放進套件內**
   （macOS／Linux-x64／Windows-x64），取件**全程只碰 mooncakes.io（純 HTTPS、非 git）、不碰 GitHub**；
   以之載入助手真實 `core.js` ⇒ **5／5 fixture ＋ 78／78 測試**（約 1.0 s；產物 1.2 MB；
   工具鏈 291 MB）。**並附帶一項對四案皆有價值之洞見**：該綁定**無**「註冊原生函式」之 API，
   故本研究改以「檔案內容物化 ＋ 間接 `eval`」之**無宿主回呼**設計達成同一目的
   ——**宿主介面之門檻由三個函式降為兩個能力**（§7.7、附錄 H）。
   **代價**：語言 **pre-1.0**（v0.10.0、`moon` 0.1.x、關鍵套件單一作者）、**無交叉編譯**、
   綁定缺 arm64 Linux／Windows。**故其取捨屬準據⑧（成熟度），非可行性**（§6.2 之 8）。

8. **收束：本研究的首要建議其實最省——「庚案：不換語言，只換宿主」（§7.10）**。
   若目標只是「**擺脫 node、只要求 devenv 事先安裝 `tsc`**」（事主第十一輪之提案），
   則**不必改寫任何語言**：**macOS 內建了 `jsc`**（`JavaScriptCore.framework/Versions/A/Helpers/jsc`，
   具 `readFile`／`writeFile`／`load`／`print`／`quit`），以之為宿主跑**一字未改**之既有 78 支測試 ⇒
   **78／78、實時 0.138 s（比 node 之 0.219 s 更快）、零安裝**；再配合 §7.4.2 管道 D 之原生 `tsc`
   （約 9 MB 一次 HTTP GET），**整條鏈即只要求 `tsc`**。剩餘工程為約 40 行之 shim ＋ 五支工具之
   `import` 轉換 ＋ 一處 `plutil` 呼叫（§7.10 已逐項量清）。**四案（Swift／.NET／Go／MoonBit）
   仍適用於「要離開 JS」或「要跨平台」之場合，但皆非此目標之最廉價解。**

---

## 一、問題與現況盤點

### 1.1 現行鏈路（逐段列出外部行程）

`vChewing-macOS/ValueAdd/WebConfigAssistant/Makefile` 之 `audit` 為提交前總檢，其 8 個目標
對應 8 段工作，實際用到之外部行程只有四支（**實測**，見 §2.0）：

| `make` 目標 | 外部行程 | 產物／作用 |
|---|---|---|
| `typecheck` | `tsc --noEmit` | 型別檢查（無輸出） |
| `build` | `tsc` | `dist/js/<module>.js`（11 檔） |
| `bundle` | `node tools/build.mjs` | `dist/metadata.js`、`core.js`、`app.js`、`assistant.html`、`index.html` |
| `es5` | `node tools/es5guard.mjs` | ES5 語法守衛（目標環境含 macOS 10.9 之 Safari 7） |
| `test` | `node --test tests/*.test.js` | 78 支單元與冒煙測試 |
| `metadata` | `swift run … dump-userdef-metadata` | 自 `UserDef` 重導後設資料，與入庫版逐位元組比對 |
| `metadata-audit` | 同上 ＋ `--strict` | i18n 稽核 |
| `surface` / `surface-check` | `node tools/settings-surface.mjs` | 掃描 `SettingsUI`／`SettingsCocoa` 源碼，導出曝光面 107 鍵 |
| `version-check` | `node tools/target-version.mjs` | `version.txt` ↔ 倉根 `Release-Version.plist` |
| `fixtures` / `fixtures-check` | `node tools/fixtures.mjs` | 以助手核心邏輯生成／比對 5 份契約 fixture |
| `serve` | `python3 -m http.server` | 僅開發期預覽 |
| `deploy` | `cp` | 複製產物進官網倉 |

### 1.2 相依盤點（實測）

- **npm 是空的**：`package.json` 之 `dependencies`／`devDependencies` 皆為 `{}`，倉內無
  `node_modules/`、無 `package-lock.json`（`.gitignore` 亦已列）。三條 `scripts` 分別只是
  `make bundle`／`make test`／`make audit` 的轉呼。**npm 在今日之鏈路裡不承擔任何職能**；
  Makefile 首行「零 npm 相依：只用到 `tsc` 與 `node`」即其自述。
- **Node 只為本目錄而存在**：全倉（除 `.build/` 快取）無其他 `node`／`npm`／`.mjs` 引用；
  CI 之三條 workflow 皆不涉及 node。
- **`tsc` 是 npm 全域安裝之物，且其入口是 `node` 啟動器（第九輪訂正）**：實測
  `/usr/local/bin/tsc` → `/usr/local/lib/node_modules/typescript/bin/tsc`，內容為
  `#!/usr/bin/env node` ＋ `import "../lib/tsc.js"`；`lib/tsc.js` 僅 609 B，靠 `getExePath.js`
  定位**真正的原生編譯器**（`node_modules/@typescript/typescript-darwin-arm64/lib/tsc`，23 MB）。
  該套件之 `optionalDependencies` 列有 **20 個平台**之原生包、`engines` 為 `node >= 16.20.0`。
  **故「TypeScript 7 是 Go 原生版」為真，但 npm 之發行形態令 `tsc` 必須有 `node` 才能啟動**
  ——今日 `make build`／`make typecheck` **實際上是建置期就在用 node**，而非僅測試宿主；
  且該 TypeScript 是**曾經以 `npm i -g typescript@7` 安裝過**的（`npm ls -g` 可見 `typescript@7.0.2`）。
  這一點修正了本文先前「npm 只是 `make` 之轉呼」之印象——**`package.json` 確實零相依，
  但 npm 作為套件管理器曾被用來裝 TypeScript**。該版**已移除**
  `target: es5` 與 `module: none`（`error TS5108`／`TS6046`），此事已載於
  `vChewing-macOS/ValueAdd/WebConfigAssistant/README.md` §三，並直接導致現行兩項設計：
  ① 原始碼一律以 ES5 寫法撰寫（`var` ＋ `function` ＋ 字串相加）；
  ② 另設 `tools/es5guard.mjs` 掃描**建置產物**（而非原始碼），以同時抓出 `tsc` 自行注入之 ES6+ 語法。
- **`swift` 本來就在鏈路內**：`make metadata` 與 `make metadata-audit` 各跑一次
  `swift run --disable-sandbox -c release --package-path Packages/vChewing_OSNeutral_LibVanguard
  vChewingSharedCLI dump-userdef-metadata`。**這一條需要 6.4 toolchain**（該套件之
  `swift-tools-version: 6.4`；5.10 側 manifest 不收 `vChewingSharedCLI`）。
- **環境**（實測）：macOS 27.0（arm64）、Xcode 27.1（27A9269）、Swift 6.4
  （`swiftlang-6.4.0.34.1`）、Swift 5.10.1（toolchain 識別碼 `org.swift.5101202406041a`）、
  Node v22.20.0、TypeScript 7.0.2。**`.NET` SDK 10.0.201 存在**（`/usr/local/share/dotnet/dotnet`；另有 6.0.136／6.0.428／8.0.416，執行期 `Microsoft.NETCore.App` 10.0.5）——惟**不在預設 `PATH`**，故一般 shell 之 `dotnet --version` 回 `command not found`；本文初稿即因此誤判為未安裝，事主 2026-09-25 補示其路徑後已實測（§2.9／§2.10）。

### 1.3 程式碼規模與歸屬（實測之行數與位元組）

| 歸屬 | 內容 | 行數 | 位元組 |
|---|---|---|---|
| 助手本體（`src/*.ts`） | `globals` 12、`model` 129、`i18n` 745、`schema` 318、`questions` 691、`starter` 146、`preset` 128、`widgets` 419、`shell` 192、`exits` 89、`main` 823 | **3,692** | 185,379 |
| 建置工具（`tools/*.mjs`） | `build` 245、`es5guard` 172、`fixtures` 161、`settings-surface` 140、`target-version` 76 | **794** | — |
| 測試（`tests/`） | `dom-smoke` 1,096、`questions` 653、`preset` 179、`metadata` 147、`i18n` 108、`dom-shim` 216、`core-loader` 50 | **2,449** | — |
| 資產（入庫之防漂移物資） | `assets/userdef-metadata.json` 232,766 B、`assets/settings-surface.json` 6,627 B、`assets/assistant.css` 630 行 | — | 239,393 |
| 產物（`dist/`，不入庫） | `js/*.js` 148,148 B、`metadata.js` 187,836 B、`core.js` 284,639 B、`app.js` 335,995 B、`assistant.html` 349,299 B、`index.html` 813 B | — | — |

**關鍵比例**：`assistant.html` 之 349,299 B 中，**181.7 KiB 是內嵌之後設資料**
（`tools/build.mjs` 之 `projectMetadata()` 已把 `prompt`／`toolTip` 一類欄位投影掉），
助手自身之 JS 只有約 145 KiB。**故「產物大小」在本議題中不是敏感量**——這點在 §5.2
評估「保留註解」時會用到。

### 1.4 兩項既有事實（直接影響本研究之範圍）

**① 助手今日不隨發行版出貨。** `Scripts/vchewing-update.swift` 之註解明言
「配置助手側之 `version.txt`（其所在目錄缺席時略過——**該助手不隨發行版出貨**）」；
實測 `Build/Products/Release/vChewing.app/Contents/Resources/` 之清單亦無 `assistant.html`。
助手今日之出口是官網（`make deploy` → `vChewing-HomePage.io/assistant/`）。
故委託中「在組裝 bundle 的時候運行一下以**收錄建置產物**」是一項**新能力**，
而非既有行為之重寫；§4.5 給出動詞設計，其是否接線屬 §6.2 之待裁定事項。

**② 「助手 ↔ 唯音」之契約已有 Swift 側守門人。**
`Packages/vChewing_SettingsUI/Tests/SettingsUITests/AssistantContractTests.swift` 以
`UserDef.destructureExchange(_:)`／`diffAgainstCurrent(_:)` 驗證 5 份 fixture「唯音一概收得下」，
且**只做純查詢、不寫 `UserDefaults`**。此測試與助手之**產物**耦合、與助手之**工具鏈**無關
——故本研究之任何階段都不應、也不會動它（§5 之驗收條件即以此為前提）。

---

## 二、實測（十項）

以下十項全部在本機跑過。逐條指令與原始輸出見**附錄 A**；Swift 側兩支 PoC 之完整原始碼見**附錄 B**
（`NodeHost.swift` 250 行）、**.NET 側兩支之完整原始碼見附錄 F**。為使本節可獨立閱讀，
各項均附「此項證明了什麼」。**§2.9／§2.10 係事主 2026-09-25 補示後所增**，其結論推翻了本文初稿對
`.NET 10` 之判斷。

### 2.0 基線（現況之實測值）

- `make audit`（暖機）：**rc=0，實時 2.882 s**。
- `node --test tests/*.test.js`：**78 支／78 通過**，node 自報 `duration_ms 192.03`，實時 0.219 s。
- `node tools/fixtures.mjs --check`：5 份 `same`，實時 0.047 s。
- `make metadata`（暖機）：實時 1.506 s，其中 SwiftPM 自報 `Build complete! (0.24秒)`
  ——**最大之單一外部成本是那兩次 `swift run`，而非 node**。

### 2.1 實驗一：以 JSC 承載助手之真實 `dist/core.js`，重現五份 fixture

**手段**：一支 147 行 Swift 程式，`import JavaScriptCore`，把 `dist/core.js`（284,639 B）
`evaluateScript(_:withSourceURL:)` 進 `JSContext`，再以 JS 驅動函式照
`tools/fixtures.mjs` 之五個情境（含 `starter: true` 之封閉全集情境）產生配置包。

**結果**：

```
core.js 載入 JSC 完畢：2.8 ms
  msnewphonetic-scpc.json：位元組相同（95 項，4207 位元組）
  kimo-zhuyin.json：位元組相同（92 項，4049 位元組）
  pinyin-newbie.json：位元組相同（92 項，4025 位元組）
  minimal-sparse.json：位元組相同（1 項，225 位元組）
  starter-macoszhuyin.json：位元組相同（16 項，866 位元組）
五份 fixture 中，位元組相同者：5/5
```

**證明了什麼**：助手之核心（`dist/core.js`，無 DOM 之純邏輯）**不含任何宿主 API**
（`src/*.ts` 內 `console.`／`require(`／`globalThis`／`process.` 之出現次數皆為 **0**），
故換引擎零成本；`JSValue` ↔ Swift 之橋接（含 `NSDictionary`／`[String: Any]` 之自動轉換）
足以承載 fixture 產生器之全部需求。載入 284 KB 之 JS 只需 **2.8 ms**。

### 2.2 實驗二：以 Swift 提供 Node 替身，跑完**一字未改**之既有 78 支測試

**手段**：`NodeHost.swift`（250 行）實作一個最小之 CommonJS 載入器與 Node 內建模組替身：

- 相對路徑 `require` → 讀檔、包進 `(function (exports, require, module, __filename, __dirname) {…})`、
  `evaluateScript` 後取 `module.exports`（含快取）；
- `node:fs` 之 `readFileSync`／`existsSync`、`node:vm` 之 `runInThisContext` → 由 Swift 以區塊實作
  （`runInThisContext` 在 JSC 即為「於同一 context 內求值」，語意天然對位）；
- `node:assert` 之 `ok`／`strictEqual`／`notStrictEqual`／`deepStrictEqual` 與 `node:test` 之
  `test(name, fn)` → 以 80 行 JS 前導碼實作（實測：測試檔只用到這 4 個斷言函式與 1 個 `test()`，
  `node:test` API 之使用共 86 處、`assert.*` 共 537 處，別無其他）；
- 測試之執行與結果彙整由 Swift 驅動（`JSValue.call(withArguments: [])` ＋ `exceptionHandler` 捕捉）。

**結果**（既有測試檔**零修改**）：

```
模組載入：9.3 ms
測試：78 支，通過 78，失敗 0
```

以 `swiftc -O` 編成執行檔後連跑三次：**78／78**，實時 **0.30／0.30／0.31 s**
（node 基線 0.219 s；**慢約 0.09 s，可忽略**）。

**證明了什麼**：`node --test`、`node:assert`、`node:vm`、`tests/core-loader.js` 之作用，
以及「以全域物件承載產物、每次重載即重置狀態」這一整套機制（`dom-smoke.test.js` 之
`bootApp()` 依賴它）**都可以用 JavaScriptCore ＋ 一支 Swift 宿主原樣承接**。
1,096 行之 DOM 冒煙測試（含 DOM 替身 216 行）不需改寫一個字——這是本研究**成本最低、
回報最高**的一項發現。

### 2.3 實驗三：雙 manifest（5.10 基底 ＋ 6.4 測試靶）之實測行為

委託要求「Swift 5.10+（單元測試限 6.4+）」。本倉既有佈局是「基底 6.4 ＋ 5.10 封堵鏈」，
而委託要的是**反向**：基底須 5.10、測試靶只准 6.4+。實測以三檔小套件驗證：

- `Package.swift`（`swift-tools-version: 5.10`，只宣告執行檔靶）
- `Package@swift-6.4.swift`（`swift-tools-version: 6.4`，追加 `.testTarget`）

| 呼叫 | 結果（實測） |
|---|---|
| 6.4 toolchain `swift test` | swift-testing 執行 1 支測試並通過 |
| 6.4 toolchain `swift build` | 成功 |
| **5.10 toolchain** `swift package dump-package` | `toolsVersion: 5.10.0`、`targets: ['vca-builder']` ⇒ **選中的是基底 `Package.swift`，測試靶不存在** |
| **5.10 toolchain** `swift build` | 成功 |
| **5.10 toolchain** `swift run` | `actor total = 36` ⇒ **actor ＋ `withTaskGroup` 在 5.10 下確實可執行** |
| **5.10 toolchain** `swift test` | `error: no tests found; create a target in the 'Tests' directory` ⇒ **測試結構性地被擋在 6.4 之外** |

> **一則方法學附註（值得記下）**：`TOOLCHAINS=swift-5.10.1-RELEASE` 這種寫法**無效**，
> `xcrun swift --version` 仍回報 6.4；必須用 toolchain 之 **bundle identifier**
> （`TOOLCHAINS=org.swift.5101202406041a`，由
> `/Library/Developer/Toolchains/swift-5.10.1-RELEASE.xctoolchain/Info.plist` 之
> `CFBundleIdentifier` 取得）。本文第一輪實測曾因此得到**假陽性**（誤以為 5.10 也跑得動測試靶），
> 覆核後推翻。此坑與 `Phase217_SOP.md` 之 toolchain 擇定同源，建議一併記入該檔。

**證明了什麼**：委託之兩項要求**不需任何約定或 CI 紀律即可結構性成立**——
5.10 用基底 manifest（無測試靶）、6.4 用 `Package@swift-6.4.swift`（有測試靶）；
而 `actor` 不因降到 5.10 而失效。**5.10 之要求本身也有正當理由**：見 §4.7。

### 2.4 實驗四：`"use strict"` 之所在位置是**行為載重**的

`tools/build.mjs` 之串接順序是「`metadata.js` 之程式碼 → `CORE_ORDER` → `APP_ORDER`」，
而 `metadata.js` 之首行是一句 `//` 註解、接著是 `var VCA_METADATA = …`。
`tsc` 為每個模組產出之 `"use strict";` 因此**落在第 8 行**：

```
1: // 本檔為建置產物（由 assets/userdef-metadata.json 與 assets/settings-surface.json 投影而成），請勿手改。
2: var VCA_METADATA = {…};
…
8: "use strict";
```

`"use strict"` 只在**指令前導區**（directive prologue）有效，故**出貨產物並非嚴格模式**。
實測（於同一份 script 內附加未宣告之賦值）：

```
實際產物（原樣）          ：未拋錯 ⇒ sloppy mode
"use strict" 提到檔首時  ：拋錯 ⇒ ReferenceError: Can't find variable: __vcaStrictProbe
```

**證明了什麼**：重寫之串接器**必須逐位元組保留現行順序**。若某位實作者「順手」把
`"use strict";` 提到檔首（看起來像是無害的整理），產物之語意即改變：未宣告之賦值、
`arguments.callee`、八進位字面量、`with` 等行為全部翻轉。建議一併以一條測試固化
「產物**不得**為嚴格模式」——這是本研究提出之**唯一新增守衛**。

### 2.5 實驗五：JavaScript 之 `\w` ≠ ICU 之 `\w`

`tools/es5guard.mjs` 之 30 條規則（13 條語法 ＋ 13 條標準庫 API ＋ 4 條模組系統殘留）與其詞法處理全為 JS 正則。若改以
`NSRegularExpression`（ICU）重寫同一組樣式，語意會漂移。實測 `(^|[^\w$.])let\s`：

```
JS  : 唯音let x ⇒ true    .let x ⇒ false   let x ⇒ true
ICU : 唯音let x ⇒ false   .let x ⇒ false   let x ⇒ true
```

**證明了什麼**：**JS 之 `\w` 是 ASCII-only，ICU 之 `\w` 是 Unicode 感知**。同一條規則在
含 CJK 之文本上給出相反答案。凡「把 JS 正則照抄成 ICU 正則」之改寫，都必須逐條處理
`\w`／`\W`／`\s`／`\b` 之語意差（改寫為 `[A-Za-z0-9_]` 等顯式字元類）——這是**安靜的**
行為變更，不會有任何編譯器警告。

### 2.6 實驗六：ES5 守衛之實態（含一項**已排除**之疑慮）

初判以為 `tools/es5guard.mjs` 之規則是「對整份產物做原始正則掃描」，因而會被字串內容誤判
（產物內含大量 CJK 文案，而 CJK 字串內完全可能出現 `` ` `` 或 `=>`）。**實讀推翻此疑慮**：
`es5guard.mjs:62` 之 `stripLiterals()` 是一支 **58 行（`es5guard.mjs:62-119`）之詞法掃描器**，會先把字串／樣板／
註解／正則字面量之內容替換為空白（保留換行以維持行號），之後才跑規則。實測：

```
含字串之樣本（字串內有 let、`、=>）：違規 0 筆（0 ＝ 未誤判）
真含箭頭函式之樣本                ：違規 1 筆
```

**證明了什麼**：該守衛**已經**是「字串感知」的，設計良好；因此**移植它才是本研究中最需要小心的一環**
——要移植的不是 30 條正則，而是那支 58 行詞法掃描器（其中還包含「斜線是除法還是正則字面量」
之啟發式判斷，該判斷本身又用到 `\w`／`\s`，見 §2.5）。此為 §3.3 之直接依據。

### 2.7 實驗七：Xcode 同步根群組之成員集（既有結論之覆核與追加）

`vChewing.xcodeproj/project.pbxproj:143` 之 `ValueAdd` 是 `PBXFileSystemSynchronizedRootGroup`，
其例外集（`5B9184C22F3B0244006B48E8`）只列了 5 個 `RawImages/*` 檔，`target` 為 `vChewing`。
實測 Xcode 自己之專案模型（PIF，`Build/Intermediates.noindex/XCBuildData/PIFCache/project/PROJECT@*`）
**確實列舉了助手之檔案**，且型別為 `sourcecode.typescript`：

```
/groupTree/children/2/children/2/children/0/children/0/path => assistant.css
/groupTree/children/2/children/2/children/2/children/6/path => questions.ts
/groupTree/children/2/children/2/children/5/children/0/path => build.mjs
```

全倉之同步根群組共 **5 個**：`Plugins`、`vChewingIME_macOS`、`ValueAdd`、`Installer_macOS`、
`vChewingDebuggable`。`Scripts/` 與 `Tools/` **皆不在**專案內（`grep -c "path = Scripts;"` 為 0）。

**既有結論**（`KnowledgeMemo4LLM.md` §A2.2 第 16 條③，已實測）：Release 產物**不含**其內容，
故不影響出貨。**本文追加**：`.ts`／`.mjs`／`.json` 對 Xcode 是「無編譯器之型別／資源」，
故今日只是被列舉與索引；但 **`.swift` 是一級原始碼型別**——在 `ValueAdd/` 內新增 `.swift` 檔
**會被納入 `vChewing` 靶之成員集並參與編譯**（**推論**：依同步根群組之成員規則與
`RawImages/*.pxd` 之所以需要例外集之事實反推；**未以一次 Xcode 建置實測**，見 §6.1 之 R2）。
**故本研究建議之套件落點必須先處理此事**（§4.6）。

### 2.8 實驗八：一次性 TS→JS 遷移候選之驗證

**手段**：`tsc --project tsconfig.json --outDir <tmp> --removeComments false`，即令 `tsc`
**保留註解**地把 `src/*.ts` 降為 `.js`（型別抹除、`namespace` 降為 IIFE）。此即 §5.2 之遷移候選。

**結果**：

| 量 | 現行（`removeComments: true`） | 遷移候選（`false`） | 差 |
|---|---|---|---|
| 11 個模組之 JS 總量 | 148,148 B | 187,474 B | ＋39,326 B（＋26.5%） |
| `app.js`（含後設資料） | 335,995 B | 375,321 B | ＋39,326 B |
| `assistant.html` | 349,299 B | **388,602 B** | **＋39,303 B（＋11.3%）** |

遷移候選之**產物**（由該 `.js` 串接而成）經三項獨立驗證：

1. 五份 fixture 逐位元組比對：**5／5 位元組相同**（以 §2.1 之 JSC 手段重跑）；
2. §2.2 之 Swift 宿主跑**完整 78 支測試**：**78／78 通過**；
3. §2.6 之 ES5 守衛：**OK**（該守衛之 `stripLiterals` 正確吃掉多出來的 39 KB 註解）。

**證明了什麼**：TypeScript **可以一次性退出鏈路**，且退出之代價是**已知且已量測**的
（型別檢查 ＋ 39 KB）。遷移本身不是「重寫 3,692 行」——`tsc` 產出之 `.js` 與原 `.ts`
**逐語句對應、註解原位保留**（附錄 A 附有 `questions.js` 之開頭 20 行以資對照），
故其審閱負擔落在「產物等價」之機器驗證，而非逐行重讀。

### 2.9 實驗九：.NET／Jint 載入真實 `core.js`，重現五份 fixture

**動機（事主 2026-09-25 補示，本文初稿漏看之事）**：① `dotnet` **並非未安裝**——實為
`/usr/local/share/dotnet/dotnet`（SDK **10.0.201**、執行期 **10.0.5**），只是不在預設 `PATH`；
② **JS 引擎之取得管道才是關鍵**：Apple 平台上 Swift 路線靠**系統內建**之 JavaScriptCore（零相依），
但一旦要在 **Windows／Linux** 上搭建同一條管線，Swift 側就得引入 **GitHub 託管**之 SwiftPM 相依
（`swiftwasm/JavaScriptKit` 一類；事主指其現要求 Swift 6.3+），而 GitHub 之套件下載在 GFW 環境下
**經常受擾**；**NuGet 則不受擾**。

**手段**：`dotnet new console --framework net10.0` ＋ `dotnet add package Jint`（**NuGet 管道**；
實測還原 **5.08 s**、取得 **Jint 4.16.3**）。C# 讀入 `dist/core.js`（284,639 B）後 `engine.Execute`，
續以與 `tools/fixtures.mjs` 同源之驅動（附錄 F）產生五個情境。

**結果**：

```
core.js 載入 Jint 完畢：66.3 ms
引擎：Jint（純受控碼 JS 解譯器，非瀏覽器級引擎）
  msnewphonetic-scpc.json：位元組相同（95 項，4207 位元組）
  kimo-zhuyin.json：位元組相同（92 項，4049 位元組）
  pinyin-newbie.json：位元組相同（92 項，4025 位元組）
  minimal-sparse.json：位元組相同（1 項，225 位元組）
  starter-macoszhuyin.json：位元組相同（16 項，866 位元組）
五份 fixture 中，位元組相同者：5/5
```

### 2.10 實驗十：.NET／Jint 跑完**一字未改**之 78 支測試

**手段**：一支 **156 行 C#** ＋ `prelude.js`（Node 內建替身，構造與 §2.2 之 Swift 版同構），
宿主 API 只落到三個 C# 函式：`__readFile`／`__fileExists`／`__evalExpr`（後者即
`engine.Evaluate`，對位 `vm.runInThisContext` 之「於同一全域求值」）。

**結果**（既有測試檔**零修改**）：

```
模組載入：63.5 ms
測試：78 支，通過 78，失敗 0
```

`dotnet run` 含編譯之總實時 **5.180 s**；純執行 **0.759 s**。

**證明了什麼（本文初稿之判斷已被推翻，如實記之）**：初稿斷言 .NET「**無內建 JS 引擎**」故
**無法**以真實產物驅動 fixture 與測試，並據此整體否定丙案。**該斷言為假**——Jint 自 NuGet 取得、
純受控碼、無原生資產，**同時**通過 5／5 fixture 逐位元組比對與 78／78 測試。
故丙案在準據②（真實產物驅動）上與乙案**同級**；差異移至**引擎等級**與**依賴管道／跨平台**
兩項（§7.4／§7.5）。

**仍應記明之差異**：Jint **不是**瀏覽器級引擎，其 ECMAScript 覆蓋度隨版本演進且不構成規格。
就**現行**語料（ES5 風格之產物 ＋ 使用 `const`／`let`／箭頭函式／解構之測試）實測無差異；
但長期而言，「在 Jint 上綠燈」之保證強度弱於「在 JavaScriptCore 上綠燈」——尤其**偽陰性**
（Jint 容忍而瀏覽器不容忍之寫法）不會被任何測試抓到。此為丙案之實質代價，非致命傷。

---

## 三、逐段裁定

### 3.1 對照表

| 現行元件 | 規模 | Swift 可否取代 | 依據／手段 |
|---|---|---|---|
| `npm`（`package.json`） | 18 行 | ✅ **且現況即已無用** | 零相依；`scripts` 僅轉呼 `make`（§1.2） |
| `tools/build.mjs`：串接 ＋ 來源完整性守衛 | 245 行 | ✅ **全然** | 純檔案 I/O ＋ 字串運算；`assertOrderCoversSources()` 對位為 `Sources/` 之目錄列舉 |
| `tools/build.mjs`：後設資料投影（`projectMetadata`） | 同上 | ✅ **全然** | `JSONSerialization` 之 `[String: Any]` 重組；**鍵序須保序**（JS 物件插入序 ⇒ Swift 需顯式有序容器，見 §4.1 註） |
| `tools/build.mjs`：HTML 組裝（`index.html` 模板 ＋ `{{…}}` 替換） | 同上 | ✅ **全然** | |
| `tools/build.mjs`：`dist/index.html` 跳轉頁 | 同上 | ✅ **全然** | |
| `tools/es5guard.mjs` | 172 行 | ⚠️ **驅動可 Swift、規則宜留 JS** | 詞法掃描器之語意敏感（§2.5／§2.6） |
| `tools/fixtures.mjs` | 161 行 | ✅（其 JS 邏輯於 JSC 內原樣執行） | 實測 5／5 逐位元組相同（§2.1） |
| `tools/settings-surface.mjs` | 140 行 | ✅ **全然** | 逐行掃描 ＋ 簡單樣式；其樣式只涉及 ASCII，無 `\w` 陷阱 |
| `tools/target-version.mjs` | 76 行 | ✅ **全然** | 文字解析 ＋ `PropertyListSerialization` 讀 `.plist`（**優於**今日之以 `plutil` 或字串比對） |
| `tests/*.test.js` ＋ `core-loader.js` ＋ `dom-shim.js` | 2,449 行 | ✅ **內容原樣，只換宿主** | 實測 78／78（§2.2） |
| `node --test`（測試宿主） | — | ✅ **全然** | 同上 |
| `make metadata`／`metadata-audit` 之 `swift run` | — | ✅ **並可合併為一次** | actor 獨占（§4.3） |
| `tsc`（型別檢查 ＋ 編譯） | — | ❌ **不可** | 需 TypeScript 前端；三條出路見 §3.2 |
| `make serve`（`python3 -m http.server`） | — | ✅（可選） | 或逕保留 `python3`（與本研究無關） |
| `make deploy`（`cp`） | — | ✅ **全然** | |

### 3.2 TypeScript 前端：唯一不可取代者，與三條出路

Swift 無法編譯 TypeScript。要在 Swift 內做到，等於在 Swift 內重寫一個 TS 前端
（詞法／語法／語意分析 ＋ 型別抹除 ＋ `namespace` 降級 ＋ 註解剝除）——那不是「重寫編譯框架」，
而是「重寫 TypeScript」，**明確超出可行性研究的合理範圍**。三條出路：

| 出路 | 內容 | 代價 | 實測依據 |
|---|---|---|---|
| **甲：留住 `tsc`** | Swift 工具把 `tsc` 當外部行程呼叫（同時做型別檢查與編譯） | `tsc` 仍是鏈路相依（但 npm／node 可去）；型別檢查保全 | §2.2、§2.3 |
| **乙：一次脫離** | 以 `tsc --removeComments false` 一次性把 `src/*.ts` 降為 `.js` 並入庫，其後 `tsc` 退出 | ＋39,303 B 之產物；**失去 `schema` 層之靜態型別檢查**；`TypeScript` 可退為自願之 lint（`tsc --checkJs --noEmit`） | §2.8（78／78、5／5、守衛 OK） |
| **丙：維持現狀** | 不動 | 保留 node ＋ tsc ＋ npm（現況） | §2.0 |

**本研究之建議**：**甲為必經之路、乙為可選之第二步**（§5、§8）。理由：
① 甲已完全解除委託所指之痛（npm 直接刪、node 直接去），且**可逆**；
② 乙之真正代價不是工具鏈而是**型別安全**——`src/schema.ts`（318 行）負責 118 條偏好鍵之
`coerceValue`／`validateValue`，是整個助手最需要靜態型別的地方；
③ 乙在甲之上只是「少呼叫一支行程」，先做甲再觀察，決策品質更高。

### 3.3 兩項「性質保守」之裁定

**① ES5 規則之落點**：建議**規則與詞法掃描器留在 JS，於 JSC 內執行**（Swift 只負責檔案 I/O、
結果彙整與 exit code）。理由即 §2.5／§2.6：那 58 行掃描器與 30 條規則之語意就是 JavaScript 本身，
在 JSC 內執行是**逐位元組對位**的零風險移植。若事主希望連這 230 行 JS 也進 Swift，則
**必須**附一條**差分測試**：以 JSC 跑原版、以 Swift 跑新版，對同一批樣本（含現行產物、
含刻意構造之邊界樣本）斷言兩者判決一致。此為可接受之次選，但成本明顯較高。

> **一項必須向事主言明之事**：「用 Swift 重寫此鏈路」**不會**讓倉內再無 JavaScript。
> 它消除的是 **Node／npm／tsc 這三個「建置相依」**；留下來的 JS 是
> ①**受測物**（助手產物本身，本來就是 JS）與 ②**規則定義**（ES5 規則、既有測試）。
> 兩者皆由**系統內建之 JavaScriptCore** 執行，不需安裝任何東西。此為本研究之邊界。

**② 產物大小**：若走乙案並保留註解，`assistant.html` 由 349,299 B 增至 388,602 B（＋11.3%）。
該產物過半之內容本來就是內嵌之後設資料（181.7 KiB／349,299 B），且它以 `file://` 或官網單頁之形態交付，
39 KB 之增量在實務上無感。**但**若事主在意，替代手段是「於串接時剝除註解」——
該剝除器**仍須詞法感知**（否則 `//` 會出現在字串裡），故其成本與 §3.3① 同源。
**本研究不建議**為此先造剝除器；先接受 39 KB，日後有實需再議。

---

## 四、目標架構

### 4.1 套件佈局

```
vChewing-macOS/ValueAdd/WebConfigAssistant/
├── Builder/                             ← 新增：SwiftPM 套件（零相依）
│   ├── Package.swift                    ← swift-tools-version: 5.10（只有執行檔靶）
│   ├── Package@swift-6.4.swift          ← 追加 BuilderTests（swift-testing）
│   ├── Sources/VCABuilder/
│   │   ├── main.swift                   ← 動詞分派（§4.2）
│   │   ├── Paths.swift                  ← 一切路徑之單一來源（以套件根為錨）
│   │   ├── BundleAssembler.swift        ← CORE_ORDER／APP_ORDER 串接 ＋ 來源完整性守衛
│   │   ├── MetadataProjection.swift     ← projectMetadata() 之對位
│   │   ├── HtmlAssembly.swift           ← index.html 模板替換 ＋ dist/index.html
│   │   ├── ES5Guard.swift               ← 驅動 JSC 執行 tools/es5-rules.js
│   │   ├── JSFixtureDriver.swift        ← 以 JSC 產生／比對 5 份 fixture
│   │   ├── SettingsSurface.swift        ← 掃描 SettingsUI／SettingsCocoa ＋ KeyboardParser
│   │   ├── TargetVersion.swift          ← version.txt ↔ Release-Version.plist
│   │   ├── MetadataDump.swift           ← actor：唯一之 swift run 呼叫（§4.3）
│   │   ├── JavaScriptHost.swift         ← CommonJS／Node 替身（§2.2 之 PoC 正規化）
│   │   └── TestHarness.swift            ← 以 JavaScriptHost 跑 tests/*.test.js
│   ├── Tests/BuilderTests/              ← swift-testing（6.4+ 專屬）
│   └── tools/
│       └── es5-rules.js                 ← 自 es5guard.mjs 抽出之 stripLiterals ＋ 30 條規則
├── src/ · tests/ · assets/ · index.html · version.txt · Makefile   ← 不變
└── tools/                               ← 階段一之後僅餘 es5-rules.js；階段二之後全空
```

**兩項設計註記**：

- **鍵序**：`projectMetadata()` 之輸出會被 `JSON.stringify` 序列化為 JS 字面量，而 JS 物件之
  鍵序即插入序；`dist/metadata.js` 亦因此有固定之鍵序。Swift 之 `[String: Any]` **不保序**，
  故投影層須以**顯式有序結構**（例如 `[(key: String, value: JSONValue)]` 或自帶序號之
  `enum JSONValue`）承載，並自備序列化器。這是本架構中唯一需要手寫序列化之處；
  否則 `dist/metadata.js` 之鍵序會變——**不影響執行期語意，但會讓「產物逐位元組相同」之驗收條件失效**
  （§5.1 之驗收條件正需要它）。
- **零相依**：套件不引入**任何** SwiftPM 相依（`dependencies: []`）。故無網路、無解析、
  無 `Package.resolved`，且**不受**「Xcode 無法用另裝之 OpenSource toolchain 解析套件」
  （`AGENTS.md` §2）之影響。

### 4.2 動詞（CLI）

動詞刻意**一一對位現行 `make` 目標**，`Makefile` 只餘薄包裝——**人機介面不變**（`make audit` 照舊），
此為遷移期最重要之性質：任何一步出錯都能立刻與現況對照。

| 動詞 | 對位之 `make` 目標 | 要點 |
|---|---|---|
| `build` | `bundle` | 產出 `dist/*` 五件 |
| `typecheck` | `typecheck` | **僅階段一**（呼叫 `tsc --noEmit`） |
| `es5` | `es5` | 於 JSC 內跑 `tools/es5-rules.js` |
| `test` | `test` | JS 套件於 JSC 內跑（§4.4） |
| `audit` | `audit` | 上列全部 ＋ 下列全部（§4.3 之並行） |
| `metadata` ／ `metadata-update` ／ `metadata-audit` | 同名 | 經 `MetadataDump` actor |
| `surface` ／ `surface-check` | 同名 | |
| `version-check` | 同名 | |
| `fixtures` ／ `fixtures-check` | 同名 | |
| `collect --into <path>` | **（新）** | 收錄產物進 bundle（§4.5） |
| `serve` | `serve` | 可選；或保留 `python3` |

### 4.3 Actor 與結構化並行之落點

**① `MetadataDump`（actor）——唯一之 `swift run` 呼叫。**
今日 `make audit` 跑**兩次** `swift run`（`metadata` 與 `metadata-audit`），各自付一次
SwiftPM 之規劃與鎖；而 SwiftPM 之 `.build` **有建置鎖**，兩支行程併發時會互相等待或直接失敗
（**推論**：依 SwiftPM 之既有行為；本研究未實測併發 `swift run`，見 §6.1 之 R3）。
故設計為：**一個 actor 持有那唯一的一次 dump**，`metadata` 用之、`metadata-audit` 亦用之
（`--strict` 改為對同一份 dump 做稽核，或在同一次呼叫內帶上 `--strict`）。
此舉同時解決「重複呼叫」與「併發不安全」兩個問題。**實測之收益上限**：
`make audit` 暖機實時 2.882 s，其中 `swift run` 為最大項（`make metadata` 單獨為 1.506 s）。

**② `withThrowingTaskGroup`——受測物之並行。**
5 份 fixture 情境、5 支測試檔彼此獨立，各配**自己的 `JSVirtualMachine`**
（`JSContext` 綁定於建立它的執行緒；跨執行緒共用不安全）。
swift-testing 預設即並行執行測試，故此設計與之天然契合。

**③ `async let`——把便宜的事塞進貴的事之陰影裡。**
`audit` 之骨架：

```swift
let dumper = MetadataDump(cliPackage: paths.cliPackage)   // actor
async let assembly  = BundleAssembler.build(paths)         // 產物
async let dump      = dumper.dump()                        // ← 最貴（swift run）
async let es5       = ES5Guard.check(paths)                // JSC，ms 級
async let surface   = SettingsSurface.scan(paths)          // ms 級
async let version   = TargetVersion.check(paths)           // ms 級
async let fixtures  = JSFixtureDriver.compareAll(paths)    // JSC，ms 級
```

**必須言明之節制**：②③ 之收益**不是吞吐量**——那些驗證各自都在 100 ms 以下
（實測：`fixtures --check` 0.047 s、整支 JSC 測試宿主 0.31 s）。
真正的收益是**把 ms 級之工作藏進 s 級之工作之陰影裡**，使 `audit` 之實時趨近於
那一次 `swift run`。若只是為了「用上 actor」而把 0.05 s 的工作拆成八份，那是負收益。
本文之立場：**actor 之用，在於「獨占一件不可併發之事」與「宿主隔離」，不在於加速**。

**④ `Sendable` 之硬約束**：`JSContext`／`JSValue` **不是** `Sendable`。
故 actor 與 task 之邊界**只准傳 `String`／`Data`／`[String: String]` 一類值型別**，
JS 物件不得跨越 await 邊界。此為編譯器可強制之約束（Swift 6 之並行檢查會直接報錯），
亦是本架構能安全使用 actor 的原因。

### 4.4 測試宿主之分層

| 層 | 內容 | 宿主 |
|---|---|---|
| **JS 層（既有，2,449 行，零修改）** | `tests/*.test.js` ＋ `dom-shim.js` ＋ `core-loader.js` | `JavaScriptHost`（CommonJS ＋ node 內建替身） |
| **Swift 層（新增，薄）** | ① 動詞之整合測試（`build` 後產物之存在與大小、`collect` 之落點）；② **產物不變式**之測試（含 §2.4 之「不得為嚴格模式」）；③ `MetadataProjection` 之鍵序；④ `TargetVersion` 之解析；⑤ `SettingsSurface` 之掃描結果；⑥ **差分測試**（若走 §3.3① 之次選） | swift-testing（6.4+） |

**分工原則**：**JS 之契約由 JS 測、Swift 之職責由 Swift 測**。既有 78 支測試測的是助手的
行為與 DOM 結構，它們的宿主換了、**判準一字不動**，故「測試通過」在階段一之意義與今日完全相同。
Swift 層只補「Node 宿主本身之正確性」與「工具新職責」——**不重複 JS 層已覆蓋之語意**。

### 4.5 產物之收錄（`collect`）

今日助手不進 bundle（§1.4①）。若事主決定讓它進，則：

```
vca-builder collect --into Build/Products/Release/vChewing.app/Contents/Resources/WebConfigAssistant/
```

之位元組內容與 `dist/` 同源，並由 `make release`（或其後置步驟）呼叫。
**須事主裁定之事**：① 是否收錄；② 落點（`Contents/Resources/WebConfigAssistant/` 之形態）；
③ 是否需 `Info.plist`／四語系顯示名（**今日無此需求，本研究不代為設計**）；
④ 舊版 macOS 之 legacy bundle（`BundleAppsLegacy`）是否一併收錄
——**注意**：`BundleAppsLegacy` 之組裝發生在 **5.10 toolchain 為 active developer directory** 之時，
故若要走這條路，本工具**必須能在 5.10 下建置並執行**：§2.3 之雙 manifest 佈局正是為此。

### 4.6 與 Xcode／SwiftPM 之隔離

依 §2.7，在 `ValueAdd/` 內新增 `.swift` 檔會落入 `vChewing` 靶之成員集。三個選項：

| 選項 | 作法 | 評價 |
|---|---|---|
| **甲（建議）** | 套件置 `ValueAdd/WebConfigAssistant/Builder/`，並於 `vChewing.xcodeproj/project.pbxproj` 之 `ValueAdd` 同步根群組例外集追加 `WebConfigAssistant/Builder`（以及 `node_modules`，若階段一前仍存在） | 與受建之物同址（`tools/` 之既有佈局即如此）；例外集**正是為此而存在**（`RawImages/*.pxd` 五項即先例）；代價是動一次 `pbxproj` |
| 乙 | 套件置於專案外之新頂層目錄（例如 `vChewing-macOS/Builder/WebConfigAssistant/`） | 完全不動 `pbxproj`；代價是工具與受建物分家 |
| 丙 | 套件置 `Scripts/`（實測**不在**專案內） | 與既有之「倉級工具腳本」同址；但 `Scripts/README.md` 之職能敘述為版本／子模組維護，語意上略遠 |

**本研究建議甲**，並以「一次 Xcode 建置」驗證例外集確已生效（§6.1 R2）。

### 4.7 建置器自身之建置與呼叫

```make
VCA_DIR    := $(CURDIR)/ValueAdd/WebConfigAssistant
VCA_TOOL   := $(VCA_DIR)/Builder/.build/.tool/release/vca-builder

$(VCA_TOOL): $(wildcard $(VCA_DIR)/Builder/Sources/VCABuilder/*.swift)
	cd $(VCA_DIR)/Builder && swift build -c release --scratch-path .build/.tool
```

**兩項要點**：

- **scratch path 須按 toolchain 分開**（`.build/.tool` 對 6.4、另一條對 5.10）。
  實測：同一個 `.build` 內換 toolchain 會反覆出現 `[Planning deferred tasks]` 之重複規劃。
  此坑在本倉已有先例——legacy 側用 `.build/.legacy-root`。
- **5.10 之要求有其實質理由**，不只是「與倉規一致」：legacy bundle 之組裝
  （`BundleAppsLegacy`）發生在 5.10 為 active toolchain 之時（§4.5），若屆時要收錄助手，
  工具就必須能在 5.10 下建置並執行。故委託之「Swift 5.10+（測試限 6.4+）」是**恰好正確**之規格，
  §2.3 已實測其成立。

---

## 五、遷移計畫

### 5.1 階段一：Node 退場（`tsc` 暫留）

**做什麼**：建立 `Builder/` 套件，實作 §3.1 表中所有標「✅」之段落；`Makefile` 改為呼叫
`vca-builder`；刪 `package.json`；`tools/*.mjs` 除 `es5-rules.js`（由 `es5guard.mjs` 抽出）外全刪。
`tsc` 仍在（`typecheck` 與 `build` 動詞），**npm 與 node 完全消失**。

**驗收條件（全部可機器判定）**：

1. `dist/metadata.js`、`dist/core.js`、`dist/app.js`、`dist/assistant.html`、`dist/index.html`
   與遷移前之產物**逐位元組相同**（`VCA_BUILD_STAMP` 與 `產出時間` 兩處之時戳須先正規化）。
2. `assets/userdef-metadata.json`、`assets/settings-surface.json`、`tests/fixtures/*.json` 逐位元組**未變**。
3. `make audit` rc=0；78 支測試全綠；輸出行數與內容與遷移前等價。
4. `git grep -n "node\b"` 於 `ValueAdd/WebConfigAssistant/` 下**零命中**（除文件敘述）。
5. Xcode 之一次建置（§4.6 甲）仍成功，且 `vChewing` 靶之成員集**不含** `Builder/`。

**一項必須言明之限定（第九輪補）**：階段一移除了「**node 作為建置器**」，但**若仍沿用 npm 版之
`tsc`，則 node 仍以 `tsc` 之啟動器身分留在建置期**（§1.2 之實測）。故「node 完全退場」實為**兩步**：

- **階段 1a**：Swift 工具接手 Node 之全部職責（本節所述）——node 退為 `tsc` 之啟動器。
- **階段 1b**：改用**不需 node 之原生 `tsc`** ⇒ **node 自此徹底退出建置期**。三條來源（§7.4.2，
  皆已實測）：**首選** npm registry 之平台 tarball 直取（**約 9 MB**／中國鏡像 < 1 s／解壓 26 MB）；
  需多平台一次備齊則用 NuGet（六 RID、57 MB）；要求官方 release 出處則用 GitHub Releases。
  （此步與階段二獨立：做了 1b 就再也不需要 npm／node；做了階段二則連 `tsc` 都不需要。）

**回退**：刪 `Builder/`、`git checkout -- Makefile tools/ package.json` 即可回到現況。
本階段**不動 `src/` 一個字元**，故風險受控。

**工作量之估計**：§2.2 之 PoC 已證明宿主層約 **250 行 Swift**；其餘段落多為檔案 I/O
（`build.mjs` 245 行、`fixtures` 161、`surface` 140、`target-version` 76 之對位），
加上 §4.4 之 Swift 層測試。**本文不給人日之估計**（本工作區之估計慣例從缺），
僅指出：**風險最高的宿主層已是實測過的原型**。

### 5.2 階段二：TypeScript 退場（可選）

**做什麼**：執行 §2.8 之一次性遷移——`tsc --removeComments false` 產出之 11 檔 `.js`
**逐檔入庫取代 `src/*.ts`**；其後刪 `tsconfig.json`、刪 `typecheck` 動詞、刪 `tsc` 相依；
`BundleAssembler` 之輸入由「`dist/js/` 之 `tsc` 產物」改為「`src/*.js` 本身」。
`TypeScript` 可保留為**自願之 lint**（`tsc --allowJs --checkJs --noEmit`），但**不入 `audit`**。

**驗收條件**：

1. 遷移提交中之 11 檔 `.js`，與**被刪除之** 11 檔 `.ts` 之 `tsc` 輸出**逐位元組相同**
   （即：入庫者恆等於機器產物，而非人手重寫——此為本階段之核心不變式）。
2. 五份 fixture 逐位元組相同（實測：**5／5**）。
3. 78 支測試全綠（實測：**78／78**）。
4. ES5 守衛 OK（實測：**OK**，含多出來的 39 KB 註解）。
5. `assistant.html` 之增量恰為 ＋39,303 B（± 時戳）；**真機（macOS 10.9 ＋ Safari 7）之日視複核**
   仍需事主執行（本工作區無法代勞）。

**須事主明示接受之代價**：`src/schema.ts` 那一層之靜態型別檢查消失。緩解手段有二
（可併用）：① 既有 78 支測試與 Swift 側之契約測試已是強力防漂移；
② 需要時把 `tsc --checkJs` 當 lint 跑（但那就把 `tsc` 請回來了，只是不擋建置）。
**本研究不替事主決定此事**（§6.2 之 1）。

### 5.3 階段三：收錄進 bundle（可選、且待裁定）

依 §4.5 實作 `collect` 動詞並接線至 `make release`（以及需要時之 `bundleLegacy`）。
驗收：`make release` rc=0 且 `.app` 內可見該產物；`BundleApps` 之既有行為零變更。
**此階段與前兩階段完全獨立**——即使前兩階段都不做，`collect` 亦可單獨以今日之鏈路實作。

### 5.4 每階段之可逆性

| 階段 | 可逆性 | 回退成本 |
|---|---|---|
| 一 | **完全可逆** | 刪目錄 ＋ `git checkout` 三處；`src/` 未動 |
| 二 | **語意上不可逆、技術上可逆** | 技術上 `git revert` 即回 `.ts`；但「型別檢查」之回歸需重新建立紀律 |
| 三 | **完全可逆** | 移出 `Makefile` 之兩行 |

---

## 六、風險與未決

### 6.1 風險表

| # | 風險 | 級別 | 依據 | 緩解／驗證 |
|---|---|---|---|---|
| R1 | **TypeScript 前端不可由 Swift 取代** | —（事實） | §3.2 | 甲／乙／丙三路；建議甲為必經、乙另議 |
| R2 | `ValueAdd/` 同步根群組會把新 `.swift` 納入 `vChewing` 靶 | 中 | **推論**（§2.7） | 例外集（§4.6 甲）＋**一次 Xcode 建置實測**；未驗前不動 `pbxproj` 之外的最終決定 |
| R3 | 兩次 `swift run` 併發時 SwiftPM 之建置鎖 | 中 | **推論**（§4.3①） | actor 獨占 ＋ 合併為一次 dump；**未實測併發行為** |
| R4 | `"use strict"` 之位置為行為載重 | **高（若誤改）** | **實測**（§2.4） | 串接器保留現行順序；**新增一條測試**固化「產物不得為嚴格模式」 |
| R5 | ES5 規則若以 ICU 正則重寫，`\w`／`\s` 語意漂移 | **高（若誤改）** | **實測**（§2.5） | 規則與掃描器留 JS、於 JSC 內執行；若必移植則附差分測試（§3.3①） |
| R6 | `JSValue`／`JSContext` 非 `Sendable` | 低（設計約束） | 語言規則 | actor／task 邊界只傳值型別；由編譯器強制 |
| R7 | 5.10 與 6.4 共用 `.build` 造成反覆重規劃 | 低 | 實測（`[Planning deferred tasks]`） | 分開之 `--scratch-path`（§4.7） |
| R8 | 遷移期之「產物逐位元組相同」難以達成（鍵序、時戳、換行） | 中 | §4.1 註 | 顯式有序序列化；驗收前先正規化時戳；`newLine: lf` 已在 `tsconfig` |
| R9 | 一次性遷移之審閱負擔（185 KB 之產物） | 中 | §2.8 | 以「入庫者恆等於機器產物」之不變式驗收，而非逐行閱讀 |
| R10 | 階段二之後若不滿，需重建型別紀律 | 中 | §5.4 | 決策點獨立於階段一；可先長期觀察階段一 |
| R11 | `serve` 動詞（若自製 HTTP 伺服器）引入新程式碼 | 低 | — | 逕保留 `python3`；`serve` 與 `audit` 無關 |
| R12 | 真機（macOS 10.9 ＋ Safari 7）複核無法在本工作區完成 | 低 | 既有未驗項 | 產物不變即可保證相容性；階段二之 ＋39 KB 不改變語法層 |

### 6.2 待事主裁定之事項

1. **是否走階段二（去 TypeScript）**——代價是 `schema` 層之靜態型別（§5.2）。
2. **若走階段二，是否接受出貨產物 ＋39,303 B（＋11.3%）而保留註解**（§3.3②）。
3. **助手是否隨 `vChewing.app` 出貨**；`collect` 動詞之落點與形態（§4.5）。
4. **套件之落點**：甲（`ValueAdd/` 內 ＋ 動 `pbxproj` 例外集）／乙（專案外）／丙（`Scripts/`）（§4.6）。
5. **ES5 規則是否接受「留 JS、於 JSC 內執行」**（§3.3①）；若不接受，是否接受差分測試之成本。
6. **`vChewing-DevLogs/Tools/` 之兩支 Python（`check_integrity.py`／`safepatch.py`）是否一併 Swift 化**
   ——**本研究建議「否」**：那兩支之全部價值在於**與 Swift 建置鏈路無關之獨立性**
   （它們是 2026-09-25 那次截斷事故之後設立的**外部**絆線）；把它們綁進同一條工具鏈，
   等於讓安全網與被保護之物共用同一個故障模式。
7. **此管線是否需在 Windows／Linux（或非 Apple 之 CI）上搭建**——此為**階段一實作語言之前提**；
   若需，則更細的一問是：**該平台上之 JS 宿主可否用 `node` 或發行版 WebKitGTK 之 JSC**？
   可用 ⇒ 仍選乙案（Swift 一套工具鏈足矣，因 `dump-userdef-metadata` 本即跨平台）；
   不可用（連 JS 宿主亦須避開 node 與 GitHub）⇒ 選**丙案（.NET 10）或戊案（Go）**：
   若兼重**工具鏈體積**與**離線可建置性** ⇒ 戊案（Go）；若重**與 .NET 生態之親和** ⇒ 丙案。
   兩者皆為兩套工具鏈。詳見 §7.5、§7.6、§八。
8. **能否接受 pre-1.0 之語言（MoonBit／己案）**——技術面已實測可行（QuickJS 為真引擎、
   取件走純 HTTPS 之 mooncakes.io、產物 1.2 MB、宿主門檻最低），風險集中在**成熟度**：
   語言 v0.10.0、`moon` 0.1.x、關鍵套件由單一作者維護、且**無交叉編譯**。
   若接受 ⇒ 己案可與乙案並列考量（其引擎等級僅次於乙案之系統 JSC）；若不接受 ⇒ §八之三分支不變。

---

## 七、替代方案

### 7.1 評估準據

本研究以**六項**準據比較四個方案：① **能去除哪些建置相依**；② **能以真實產物驅動 fixture 與測試與否**
（此為本專案防漂移之根本手段）；③ **工具鏈經濟**（是否引入新工具鏈、是否與既有之
`vChewing-macOS` 建置流程相容、是否能離線）；④ **與「Swift 5.10+／測試 6.4+」規格之契合**；
⑤ **實驗證據之有無**；⑥ **依賴取得管道與跨平台可行性**——此管線能否在 **Windows／Linux** 上搭建，
以及其相依走 **GitHub（SwiftPM）**／**NuGet**／**GOPROXY** 之何者。**⑥ 為第二輪新增**（事主 2026-09-25 明示：
GitHub 之 SwiftPM 相依下載經常受 GFW 干擾，NuGet 則否）；⑦ **工具鏈與產物之體積、以及跨平台建置之難易**
——**⑦ 為第五輪新增**（事主 2026-09-25：「dotnet 可能也有些過於肥大」）；
⑧ **語言與生態之成熟度**（是否 pre-1.0、關鍵相依之維護面、破壞性變更之風險）——**⑧ 為第六輪新增**
（為 MoonBit 而設）。三者之權重皆由事主裁定。

### 7.2 甲：維持現狀（Node ＋ TypeScript）

| 準據 | 評估 |
|---|---|
| ① 去除相依 | 不去除（node ＋ tsc ＋ 一個已無用之 npm） |
| ② 真實產物驅動 | ✅（`node:vm`） |
| ③ 工具鏈經濟 | 本目錄自成一格；node 只為此目錄而存在 |
| ④ 5.10 規格 | 不適用 |
| ⑤ 證據 | 現況本身 |

**評價**：零風險、零收益。委託之動機（此鏈路與倉之其餘部分異質）**成立且具體**：
全倉只為這一個子目錄需要 node。

### 7.3 乙：Swift（本文件之主案）

| 準據 | 評估 |
|---|---|
| ① 去除相依 | **npm 全去、node 全去**；`tsc` 於階段一暫留、階段二可去 |
| ② 真實產物驅動 | ✅✅ **實測 5／5 與 78／78**，且宿主引擎與交付目標同源（皆為 WebKit 之 JSC） |
| ③ 工具鏈經濟 | **零新工具鏈**——`swift` 本就在鏈路內；零 SwiftPM 相依；可離線；與 legacy 5.10 路徑相容 |
| ④ 5.10 規格 | ✅ **實測成立**（§2.3）；actor 於 5.10 下實測可執行 |
| ⑤ 證據 | **八項實測**，含兩支可重現之 PoC |

### 7.4 丙：.NET 10（P.S. 之評估；**實測後改判**）

> **前提之訂正（2026-09-25，事主補示）**：本文初稿誤判「本機未安裝 `dotnet`」。實情為
> **`/usr/local/share/dotnet/dotnet` 存在**（SDK **10.0.201**，另有 6.0.136／6.0.428／8.0.416；
> 執行期 `Microsoft.NETCore.App` **10.0.5**），只是**不在預設 `PATH`** 內——故初稿之
> `dotnet --version → command not found` 為真，而由它推出之「未實測」與「無 JS 引擎故不可行」
> **兩項結論皆假**。本節已按 §2.9／§2.10 之實測重寫，初稿之錯誤判斷保留於 §零 之修訂記錄中備查。

| 準據 | 評估（**實測**） |
|---|---|
| ① 去除相依 | ✅ 可去 npm／node（同乙）。**且 TypeScript 本身亦可自 NuGet 取得、不必另裝**——見 §7.4.1（**實測**） |
| ② 真實產物驅動 | ✅ **實測 5／5 fixture 逐位元組相同 ＋ 78／78 測試**——以 `Jint` **4.16.3**（NuGet；純受控碼、無原生資產）載入真實 `dist/core.js`，並以 156 行 C# ＋ 一支 JS 前導碼跑完既有一字未改之測試套件。**惟**引擎為解譯器而非瀏覽器級（§2.10 末） |
| ③ 工具鏈經濟 | ⚠️ 引入本倉唯一之 .NET 相依。**但**：本機 `dotnet` 已在、且其相依走 **NuGet**（不必碰 GitHub） |
| ④ 跨平台 | ✅ 建置器本身：同一份 C# 於三平台皆可。**但**整條管線仍**需要 Swift 6.4**——`dump-userdef-metadata` 是 SwiftPM 執行檔（見 §7.5 之查核表）。故丙案在非 Apple 平台上實為 **Swift ＋ .NET 兩套工具鏈** |
| ⑤ 依賴管道 | ✅ **NuGet 一條**（事主：不受 GFW 擾） |
| ⑥ 引擎等級 | ⚠️ Jint 非瀏覽器級；若在意，可改 `ClearScript`（`Microsoft.ClearScript.V8*`，**亦為 NuGet**，含各 RID 之原生 V8 資產）——本研究**未實測**該路徑 |
| ⑦ 5.10 規格 | 不適用（該規格是 Swift 側的） |
| ⑧ 證據 | **兩項實測**（§2.9／§2.10）＋ 兩支可重現之 PoC（附錄 F） |

#### 7.4.1 TypeScript 之取件：實測（事主 2026-09-25 之追問）

**問題**（事主原文）：「換言之，目前 .NET 鏈路就是可以免除對 typescript 的額外安裝需求，是吧？」
——本文此前只把 `Microsoft.TypeScript.MSBuild` 寫成一句**未經實測**的推測，本小節將其驗掉。

**實測**（2026-09-25）：

| 查核項 | 結果 |
|---|---|
| 取件 | `dotnet add package Microsoft.TypeScript.MSBuild` → **7.0.1**（**NuGet**；restore **5.66 s**） |
| 套件內容 | `tools/runtimes/` 之下為 **六個原生 `tsc` 執行檔**（`darwin-arm64`／`darwin-x64`／`linux-arm64`／`linux-x64`／`win32-arm64`／`win32-x64`），各 **26–28 MB**；套件總計 **217 MB** |
| **有無 Node** | **沒有**。`tools/` 內無 `tsc.js`、無 `node`；`build/` 只有 `.props`／`.targets`／`.xaml`，其註解自述「executes a custom executable specified in the `TscExe` property」——即直接跑原生執行檔。**TypeScript 7 已是 Go 原生版（`tsgo`）**，故 Node 在此步徹底消失 |
| 版本 | NuGet 之該執行檔自報 **`Version 7.1.0-dev.20260817.1`**；本機全域安裝者為 **7.0.2**——**兩者不同版** |
| **輸出等價性** | 以 NuGet 之該執行檔、用助手**既有之 `tsconfig.json`** 編譯助手**既有之 `src/`** ⇒ **11 檔全部與現行 `dist/js/*.js` 逐位元組相同**（`exits`／`globals`／`i18n`／`main`／`model`／`preset`／`questions`／`schema`／`shell`／`starter`／`widgets`） |

#### 7.4.2 TypeScript 7 之獨立取得管道（第十輪實測；事主問「TS7 除了 npm 以外有沒有獨立的 pkg／exe 安裝包？」）

**答案：有四條，其中三條不需 npm。** 全部實測：

| 管道 | 取得物 | 實測 |
|---|---|---|
| **A. npm 命令**（今日所用） | `typescript@7.0.2`（30 MB） | 其 `bin/tsc` 為 **`node` 啟動器** ⇒ **需 node**（§1.2） |
| **B. GitHub Releases** | `microsoft/typescript-go` 之 tag **`typescript/v7.0.2`**（2026-07-08，**非 prerelease**）：**21 個資產** = 20 個平台之 `.tgz`（**8.2–9.6 MB**）＋ `typescript.tgz`（0.3 MB） | 涵蓋 `darwin-arm64`／`darwin-x64`／`linux-{x64,arm64,arm,loong64,mips64el,ppc64,riscv64,s390x}`／**`win32-{x64,arm64}`**／`freebsd`／`netbsd`／`openbsd`／`sunos`／`aix`。**GitHub 託管**（可循 §7.5 之鏡像手法） |
| **C. NuGet** | `Microsoft.TypeScript.MSBuild` 7.0.1 之 `.nupkg` | **HTTP 200、57,283,265 B、17.3 s**；解**整棵 `tools/` 樹** ⇒ **162 MB**（**一次得六個 RID**）；`env -i` 下可跑（§7.4.1） |
| **D. npm registry 之 tarball 直取**（**不經 npm 命令**） | `@typescript/typescript-<rid>` 之 `.tgz` | `registry.npmjs.org` ⇒ **9,270,373 B、2.6 s**；**`registry.npmmirror.com`（中國鏡像）⇒ 同 9,270,373 B、0.99 s，SHA-256 完全相同**；解壓 **26 MB**、含 `lib/tsc` ＋ 全套 `lib.*.d.ts`；`env -i PATH=/usr/bin:/bin` 下跑出 **`Version 7.0.2`**，且該 `lib/tsc` 與 npm 安裝者**逐位元組相同**（`a82f7313…`） |

**對本專案之最佳解：管道 D。** 一次 HTTP GET（**約 9 MB**；中國鏡像 **< 1 s**）、解壓 26 MB，即得
一顆原生 `tsc` ＋ 其 `lib.*.d.ts` 全套——**不需 node、不需 npm、不需 dotnet**，且該管道**可鏡像**
（npmmirror 與 npmjs 逐位元組相同，已驗）。若需**一次備齊多平台**則用 C（六 RID 一份 57 MB）；
若要求**官方 release 出處**則用 B。**三條皆無 node。**

**結論**：**是**——.NET 鏈路可免除對 TypeScript 之額外安裝需求，且**連 Node 亦免除**；
而**此事與語言無關**：管道 B／C／D 皆只是「一顆二進位 ＋ 其資料檔」，
**Swift 驅動之建置器同樣可取用**（§7.4.1 之訂正）。
惟須附三項限定：

1. **去除的是「安裝」，不是「TypeScript」**。階段一仍以 TypeScript 編譯；要**徹底**不要 TypeScript，
   得走階段二（§5.2，一次性 `--removeComments false` 遷移）——那時本小節所論即無關。
2. **管道本身不綁語言**。`.nupkg` 就是一個 zip，可用**純 HTTPS GET** 自 nuget.org 取回
   （即事主所指之**不受 GFW 擾**的管道）。故**乙案（Swift）同樣吃得到這個好處**——
   只是 SwiftPM 不會替你 `restore`，得自己下載、解壓、挑 RID 之執行檔（多約 30 行）。
   換言之：此事是「**NuGet 這條管道**」的優勢，不是「.NET 這個語言」的優勢。
   **（第九輪訂正與補測）** 先前的措辭「自己下載、解壓、**挑 RID 之執行檔**」**不正確**：
   實測只解出 `darwin-arm64/tsc` 一支再執行，會 **panic**——
   `bundled: …/lib.d.ts does not exist; this executable may be misplaced`。
   該執行檔**不是自足之物**，必須與同目錄之 `lib.*.d.ts` 成套。**正確做法與實測數字**：

   | 步 | 實測 |
   |---|---|
   | 純 HTTPS GET `.nupkg` | `https://www.nuget.org/api/v2/package/Microsoft.TypeScript.MSBuild/7.0.1` ⇒ **HTTP 200、57,283,265 bytes、17.3 s** |
   | 解壓 | 須解**整棵 `tools/` 樹** ⇒ **162 MB**（六個 RID 各約 27 MB，內含 `tsc` 與整套 `lib.*.d.ts`） |
   | 執行 | `env -i PATH=/usr/bin:/bin <樹>/tools/runtimes/darwin-arm64/tsc --version` ⇒ **`Version 7.1.0-dev.20260817.1`**（**無 dotnet、無 npm、無 node**） |
3. **本小節只解了 TypeScript 這一步**。**Node 之去留仍取決於 JS 宿主**（fixture 與測試，
   §7.5）——那是另一個元件。故 .NET 鏈路之完整面貌是：**TypeScript 自 NuGet（無 Node）＋
   JS 宿主自 NuGet（Jint，無 Node）⇒ 三平台上 Node 徹底消失、且只碰一條取件管道**；
   而乙案在 macOS 上零相依，在 Windows／Linux 上則需在「node／GitHub 之 JavaScriptKit／
   發行版 WebKitGTK／vendoring」四者中擇一。

**丙案之真正優勢（初稿漏看；第三輪再收窄）**：**跨平台與依賴管道其實是同一件事**。
乙案在 Apple 平台上零相依（`import JavaScriptCore` 一行就有瀏覽器級引擎），但出了 Apple，
其 **JS 宿主**一環得另尋出路（§7.5）；丙案則把該環節換成 **NuGet 取件**。
**惟第三輪查明**：`dump-userdef-metadata` 本身即為跨平台之 SwiftPM 執行檔、且取件不碰 GitHub，
故丙案**並不能取代 Swift**——它在非 Apple 平台上節省的只是「JS 宿主之取件管道」，
代價則是多養一套工具鏈。

**丙案之真正代價（初稿誇大，訂正後仍存在）**：① **引擎等級**——Jint 之 ECMAScript 覆蓋度
隨版本演進、不構成規格，故「綠燈」之語意強度弱於 JSC，尤其**偽陰性**（Jint 容忍而瀏覽器不容忍
之寫法）不會被任何測試抓到；② **第二套工具鏈**——本倉其餘部分皆是 Swift／Xcode。

**若仍選乙案而需跨平台**：SwiftPM 之相依並非只能走 GitHub，見 §7.5 之四項緩解。

### 7.5 JS 宿主之跨平台可攜性與依賴取得管道（事主 2026-09-25 之關切）

本節處理「把同一條管線搬到 Windows／Linux」時，**JS 宿主**這一環該怎麼辦。此事之所以是關鍵，
是因為本管線之防漂移手段（5 份 fixture 與 78 支測試）**全部**建立在「能在真實 JS 引擎裡跑真實產物」
之上；**宿主換不了，整條管線就換不了**。

**兩案之宿主地圖**：

| 平台 | 乙案（Swift）之 JS 宿主 | 丙案（.NET）之 JS 宿主 |
|---|---|---|
| macOS | **系統框架 `JavaScriptCore`**（零相依、瀏覽器級、與 Safari 同源） | Jint（NuGet） |
| Linux | ① **`jectivex/JXKit`**——「pure Swift interface to JavaScriptCore for iOS, macOS, tvOS, and **Linux**」；其 README 明言 Linux 上走 **WebKit GTK JavaScriptCore**（GitHub 託管 ⇒ **可走 Gitee 鏡像**）② 自寫 *system library target* 指向 **WebKitGTK 之 JSC**（發行版套件 `libjavascriptcoregtk-4.0／4.1`，**無遠端相依**）③ 該環節改呼 `node` | Jint（NuGet） |
| Windows | ① **`jectivex/JXKit`**——其 `Package.swift` 確有 `.when(platforms: [.windows])` 之連結設定（`JavaScriptCore`／`WTF`／`CoreFoundation`／`ASL`／`Kernel32`），**惟未實測** ② 該環節改呼 `node`（JSC 無發行版套件） | Jint（NuGet） |

**事主之關切成立且具體**：乙案在非 Apple 平台上，**唯一「開箱」之路是 GitHub 託管之 SwiftPM 相依**
（WebKitGTK 那條雖無遠端相依，但要自寫 modulemap 與連結設定，且 **Windows 無對應物**）。
SwiftPM 之取件走 **git over HTTPS**，與 NuGet 之 CDN 取件不是同一回事。

**若選乙案，四項可行之緩解**（皆為既有機制，非新發明）：

1. **改走發行版套件（只解 Linux）**：以 SwiftPM 之 *system library target*（`module.modulemap`
   ＋ `pkgConfig: "javascriptcoregtk-4.1"`）直接鏈結發行版之 JSC，**零遠端相依**。
   代價：Windows **無**對應物；且需自行維護 modulemap。
2. **內嵌（vendoring）**：把該 SwiftPM 相依之原始碼整份入庫，或以其為 `path:` 本地相依
   ——建置期**零網路**。代價：入庫體積與授權遵循（須先查該套件之授權條款）。
3. **git 鏡像（2026-09-25 已取得指名之實例，見下開「鏡像實測」）**：
   `git config --global url."https://gitee.com/…".insteadOf "https://github.com/…"`。
   SwiftPM 走 git，故此設定對它有效。代價：鏡像之同步頻率不可控。
4. **SwiftPM 之套件註冊表**（SwiftPM 6 支援以 registry 取代 SCM）或 **`binaryTarget` ＋
   artifact bundle**：把取件點改到自控之主機。

**第二輪之第二項訂正（事主指出；本節初稿此處亦錯，已實查推翻）**：初稿曾斷言
「**`make metadata` 永遠不可能跨平台**」——**該判斷為假**。實查（2026-09-25）：

| 查核項 | 結果 |
|---|---|
| `vChewingSharedCLI` 之宣告 | `Packages/vChewing_OSNeutral_LibVanguard/Package.swift:63` 之 `Product.executable`，**無條件宣告** |
| 其四支源碼（`VCSharedCLI_*.swift`，共 888 行）之 import | 只有 `Foundation` 與 `Shared`；`#if`／`canImport`／`Darwin`／`AppKit` 之出現次數**皆為 0** |
| 該 manifest 之 `platforms:` | 只在 `#if canImport(Darwin)` **之內**宣告 `SupportedPlatform.macOS(.v12)`；**非 Darwin 平台上為 `nil`（不設限）**——刻意之跨平台設計 |
| CI | `test_ubuntu_LibVanguard.yml`（`ubuntu-latest`）與 `test_winnt_LibVanguard.yml`（`windows-latest`）皆以 Swift **6.4** 對該套件跑 `swift test` |
| 該閉包之遠端套件相依 | **12 份 manifest（含巢狀子套件 `Deps/VanguardSwiftExtension`）之 `.package(url:)` 總數為 0**——僅一條本地 `path:` 相依 |

**故「跨平台」之範圍是全部八件事（含 `metadata`），而 GitHub 暴露面只剩一個元件**：
`dump-userdef-metadata` 可跨平台、且取件時**完全不碰 GitHub**；整條管線裡**唯一**需要 GitHub
取件的環節，只有非 Apple 平台上的 **JS 宿主繫結**。此事大幅收窄了事主所慮之範圍，
且使問題精確地落在**單一元件**上——這正是本節之所以關鍵。

**唯一之工具鏈限制（非平台限制）**：5.10 側 manifest **刻意不收** `vChewingSharedCLI`
（其註解自述該靶「是早年用來輔助提取 `UserDef` localization key 的一次性枴杖，非出貨路徑」，
且它是 5.10 側唯一之執行檔、會被壓上 10.13 之 minOS）。故該 CLI **只在 6.4 側存在**；
而 CI 在 Windows／Linux 上所用者正是 6.4。

**Windows／Linux 之 JS 宿主選項（乙案之下；此即本節之核心）**：

| 選項 | 取件管道 | 平台 | 代價 |
|---|---|---|---|
| 該環節改呼 `node` | nodejs.org（中國有鏡像）——**不碰 GitHub** | 三平台 | node 未除盡（僅非 Apple 平台） |
| WebKitGTK 之 JSC（system library target） | 發行版套件（apt／dnf）——**不碰 GitHub** | **僅 Linux** | 自維護 modulemap；**Windows 無對應物** |
| `JavaScriptKit`／`JavaScriptKit/JavaScriptCore` | **GitHub（SwiftPM）** | 三平台 | **即事主所慮之取件風險** |
| vendoring／artifact bundle（自控主機） | 自控主機——**不碰 GitHub** | 三平台 | 入庫體積／授權／自建發佈流程 |

**附註（第四輪新增）**：`§7.4.1` 已實測 TypeScript 可自 NuGet 取得（原生執行檔、無 Node、輸出逐位元組相同）。
此事之要點是**管道**而非語言——`.nupkg` 即 zip、可純 HTTPS 取回，故 Swift 驅動之建置器同樣吃得到，
只是少了自動 `restore`。故此後論及「NuGet 之利」時，應記明它**不是 .NET 獨有**。

**鏡像實測（2026-09-25，事主報知；已查證）**：事主指 `https://gitee.com/mirrors_swiftwasm/JavaScriptKit`
為**尚新（非最新）**之鏡像。實測：

| 查核項 | 結果 |
|---|---|
| 鏡像可達性 | `git ls-remote` 成功；**淺克隆 4.9 s**；`refs/heads/main` ＝ `ebc501f`（合併提交，**2026-09-11**） |
| 與上游之差距 | 上游 `main` 之 tip 為 `53e8cc1`（**2026-09-16**）⇒ **落後約 5 日**（`api.github.com` 自本機可達，故得直接比對） |
| 標籤 | 鏡像之最新標籤為 **`0.59.0`**，與上游之最新標籤**相同** ⇒ **依語意化版本釘版取用時，鏡像不缺** |
| 意義 | 此事把本節之緩解 ③ 由「一個可行之手段」升格為「**已指名、已量測之實例**」；且其意義**不限於 JavaScriptKit**——凡 GitHub 託管之 SwiftPM 相依，皆可用同一手法改道。 |

**一項必須訂正之前提（事主 2026-09-25 之原始關切中，此點不成立）**：事主原以為非 Apple 平台須「換用
`swiftwasm/JavaScriptKit`」。**實查後不成立**——JavaScriptKit **不是**「嵌入式 JS 引擎之繫結」，
而是**反方向**的東西：

| 證據 | 內容 |
|---|---|
| 其 README 首句 | 「Swift framework to interact with JavaScript **through WebAssembly**」；「…from Swift code **when compiled to WebAssembly**」 |
| 其 `Package.swift` 之 `platforms` | **只有 Apple 平台**（`.macOS(.v13)`／`.iOS(.v13)`／`.tvOS(.v13)`／`.watchOS(.v6)`／`.macCatalyst(.v13)`）；`.wasi` 僅出現於 `linkerSettings` |
| 其架構 | target `JavaScriptKit` 依賴 `_CJavaScriptKit` ＋ `BridgeJSMacros`，並帶一份 **JS 側執行期資源**（`Runtime/`）⇒ 係「Swift/WASM 為客、JS 宿主為主」 |
| 其遞移相依 | `.package(url: "https://github.com/swiftlang/swift-syntax", …)`——**又一個 GitHub 相依**，且 swift-syntax 之建置成本不低 |

**故 JavaScriptKit 之路不僅無助於本問題，反而更差**：用它就得同時具備
**① SwiftWasm SDK（另一套工具鏈）** 與 **② 一個 JS 宿主（Node／Deno／瀏覽器）**——
而「需要 JS 宿主」正是本研究要解決的問題本身。**此路逕予關閉，記此以免後人重蹈。**

**故非 Apple 平台上「真正的 Swift 側 JS 宿主」候選是**：`jectivex/JXKit`（純 Swift 之 JSC 介面，
明文支援 Linux；Windows 有連結設定但未實測；`swift-tools-version:5.6` 相當寬鬆；授權 **LGPL-3.0**；
GitHub 託管 ⇒ 可循上開鏡像手法）、發行版 WebKitGTK 之 JSC（自寫 modulemap）、或 `node`。
**三者在 Windows 上皆未實測**（附錄 E）。

**立場（經第二輪兩次訂正後之定論）**：由於 `dump-userdef-metadata` **本身即需 Swift 6.4**
（且其取件不碰 GitHub），故 Windows／Linux 上之真正抉擇**不是**「Swift 對 .NET」，
而是「**Swift 之 JS 宿主該怎麼取**」。丙案（.NET）在此情境下是**第二套工具鏈**
（Swift 仍是必需），其收益僅止於「把 JS 宿主之取件自 GitHub 換成 NuGet」。故：

- 若願在非 Apple 平台以 `node` 或發行版 JSC 承擔 JS 宿主 ⇒ **乙案即可，且不多一套工具鏈**；
- 若堅持非 Apple 平台上之 JS 宿主亦不得依賴 node 與 GitHub ⇒ **丙案**
  （代價：Swift ＋ .NET **兩套**工具鏈）；
- 若「跨平台」根本不是需求 ⇒ **乙案**（Apple 平台上零相依、零新工具鏈）。

三者皆是可接受之工程取捨，取決於該管線是否真需在 Windows／Linux 上搭建（§6.2 之 7）。

### 7.6 戊：Go（事主 2026-09-25 追加之評估；**實測**）

**事由**（事主原文）：「dotnet 可能也有些過於肥大了。你覺得用 golang 語言的話相比 swift 與 dotnet
而言怎樣呢？這些也算入這次的研究。」

**為何值得一評**：Go 在準據⑥（依賴管道）上有**結構性**優勢、在準據⑦（體積）上遠勝丙案，
且其 JS 宿主可用**純 Go** 實作（無 cgo、無原生資產）。環境（**實測**）：**Go 1.24.3 已在**本機
（`/usr/local/go/bin/go`，同樣不在預設 `PATH`——與 `dotnet` 同一形態），且 **`GOPROXY` 已設為
`https://goproxy.cn,direct`**（中國之 Qiniu 鏡像）。

**實測（手法與 §2.9／§2.10 相同；原始碼見附錄 G）**：

| 查核項 | 結果 |
|---|---|
| JS 宿主 | `github.com/dop251/goja`——**純 Go** 之 ECMAScript 實作，**無 cgo、無原生資產** |
| 取件 | `go get github.com/dop251/goja@latest` ⇒ **9.76 s**；連同 4 個遞移相依（`dlclark/regexp2`、`go-sourcemap/sourcemap`、`google/pprof`、`golang.org/x/text`） |
| 真實產物驅動（fixture） | **5／5 逐位元組相同**；`core.js` 載入 goja **6.1 ms**（三者中最快） |
| 真實產物驅動（78 支測試） | **78／78**（既有測試與 DOM 替身**一字未改**；約 80 行 Go ＋ **與 .NET 版同一支** `prelude.js`） |
| 執行實時（已編譯） | **1.78 s**——三者中最慢（Swift＋JSC 0.31 s、.NET＋Jint 0.76 s） |
| 工具鏈體積 | **Go SDK 331 MB**（對照：**`.NET` 3.0 GB**、Swift toolchains 9.0 GB、Xcode 3.6 GB） |
| 產物體積 | 自足之**靜態**執行檔 **13 MB**（對照：Swift PoC 87 KB；.NET 需執行期或 self-contained） |
| **交叉編譯** | **由 macOS 直接產出四平台執行檔**：`windows/amd64` 13 MB、`windows/arm64` 12 MB、`linux/amd64` 13 MB、`linux/arm64` 13 MB（PE／ELF 皆經 `file` 確認）——**不需 Windows／Linux 機器、不需額外 SDK** |
| **內嵌相依** | `go mod vendor` ⇒ **11 MB**（`dop251/goja` 1.5 MB、`dlclark/regexp2` 760 KB、`golang.org/x/text` 8.6 MB、`google/pprof` 160 KB…）——入庫後**建置期零網路** |
| 工具鏈地板 | `go.mod` 記 `go 1.25.0`（goja 最新版要求；高於本機 1.24.3——Go 會經 **proxy** 取用所需 toolchain，即該步亦在可鏡像之管道內） |

**戊案之三項獨有優勢（皆已實測）**：

1. **依賴管道最可控**：`GOPROXY` 是**環境變數**、可指向任何鏡像（本機已是 `goproxy.cn`），
   且 `go mod vendor` 能把**全部**相依（11 MB）入庫 ⇒ **建置期零網路、連鏡像都不必信**。
   此為三案中最徹底之答案——不是「換一條可靠的 CDN」，而是「**可以完全不要 CDN**」。
2. **一機產出四平台**：`GOOS`／`GOARCH` 交叉編譯，產出靜態執行檔、無執行期相依。
   乙案需各平台之 JSC 繫結；丙案之 self-contained 發佈動輒數十 MB 且需下載 runtime pack。
3. **工具鏈最輕**：331 MB（丙案 3.0 GB 之約九分之一），執行檔 13 MB ＋ vendor 11 MB。

**戊案之三項代價（如實記之）**：

1. **仍不能取代 Swift**：`dump-userdef-metadata` 是 SwiftPM 執行檔（§7.5 查核表），
   故 Go 在非 Apple 平台上同樣是 **Swift ＋ Go 兩套工具鏈**——此點與丙案同構。
2. **引擎等級**：goja 是**解譯器**，非瀏覽器級；與 Jint 同類之顧慮（偽陰性不會被抓到），
   且**實測為三者中最慢**（1.78 s 對 0.76 s 對 0.31 s）。對建置工具而言可忽略，但不應略去不記。
3. **第三種語言**：本倉現有 Swift ＋ Python（`vChewing-DevLogs/Tools/`）。引入 Go 或 .NET 皆是
   「再加一種」；Go 較輕，但仍是一個新語言與新的 CI 設定。

**戊案與丙案之直接對照**：

| | 丙 .NET 10 | 戊 Go |
|---|---|---|
| JS 宿主 | Jint（**NuGet**，28 MB） | goja（**GOPROXY**，1.5 MB） |
| 可否完全離線建置 | ⚠️ 可以本地資料夾為套件來源，但**無 `vendor/` 那樣之一等公民慣例** | ✅ **`go mod vendor` 11 MB 入庫即零網路** |
| 工具鏈體積 | **3.0 GB** | **331 MB** |
| 交叉編譯 | `dotnet publish -r`（需 runtime pack，產物數十 MB） | ✅ **`GOOS`／`GOARCH`，四平台皆已實測** |
| 78 支測試實時 | 0.76 s | 1.78 s |
| 仍需 Swift（metadata） | ✅ 是 | ✅ 是 |

**小結**：若首要顧慮是**依賴取件之可靠性**與**工具鏈體積**，**戊案（Go）優於丙案（.NET）**；
若顧慮的是**與既有生態之親和**與**引擎等級**，乙案（Swift）仍勝。Go 之定位是
「**為跨平台而生的最小方案**」——它用「多一個小工具鏈」換來「依賴可完全內嵌、四平台一機產出」。

### 7.7 己：MoonBit（事主 2026-09-25 追加之評估；**實測**）

**事由**（事主原文）：「你再評估一下 Moonbit 語言。」事主並自行安裝了工具鏈
（`moon 0.1.20260920`，`~/.moon` 共 **291 MB**；本研究隨之將 `~/.moon/bin` 併入 bash／zsh／nushell 之 env）。

**為何它不是「又一個 .NET」**：MoonBit 在準據⑥上有**與另三案皆不同**之結構——其套件註冊表
**mooncakes.io 是 HTTP 服務、不是 git**，且本機可達（HTTP 200、1.68 s）。更關鍵的是：mooncakes 上
有一個**真綁定** `justjavac/quickjs@0.1.5`，它把 **QuickJS 之預編譯靜態庫直接放進套件內**
（`lib/macos-universal/libquickjs.a` 2.2 MB、`lib/linux-x64/libquickjs.a` 1.3 MB、
`lib/windows-x64/quickjs.lib` 2.3 MB；QuickJS 2025-09-13）。**故取件全程只碰 mooncakes.io／
download.mooncakes.io，不碰 GitHub。**

**實測**：

| 查核項 | 結果 |
|---|---|
| 工具鏈 | `moon 0.1.20260920`；`~/.moon` **291 MB**（bin 164 MB ＋ lib 126 MB） |
| 取件 | `moon add justjavac/quickjs` ⇒ **18 s**；帶入 `justjavac/ffi@0.2.4` 與 `moonbitlang/x`；落於專案內 `.mooncakes/`（**7.6 MB**） |
| 註冊表 | `~/.moon/registry`（22 MB）**無 `.git` 目錄**；下載端點為 `https://download.mooncakes.io/symbols.zip` ⇒ **純 HTTPS，非 git、非 GitHub** |
| JS 引擎 | **QuickJS**（Fabrice Bellard 之**真引擎**，ES2020 級）——四案之中**引擎等級最高**者 |
| 真實產物驅動（fixture） | **5／5 逐位元組相同** |
| 真實產物驅動（78 支測試） | **78／78**（既有測試與 DOM 替身**一字未改**） |
| 執行實時（已編譯） | **0.95–1.28 s**（四案：Swift＋JSC 0.31、.NET＋Jint 0.76、**MoonBit＋QuickJS 約 1.0**、Go＋goja 1.78） |
| 產物 | **1.2 MB** 原生執行檔（release） |
| 交叉編譯 | ❌ **無**。`moon build --target` 選的是**後端**（`wasm`／`wasm-gc`／`js`／`native`／`llvm`），**不是 OS／arch**——無 `GOOS`／`GOARCH` 之對位；native 產物只給宿主平台 |

**一項必須記下之綁定限制，與一項因此而得之洞見**：`justjavac/quickjs` 之公開面只有
`Runtime`／`Context`（`eval`、`parse_json`、`json_stringify`、`new_*`、`to_*`）／
`Value`（`get_property`、`set_property` 等），**沒有**「把原生函式註冊進 JS」之 API。
故 Swift／.NET／Go 三案所用之「宿主提供 `__readFile`／`__evalExpr`」寫法在本案**不可行**。

**本研究因此改用並實證了一個門檻更低之設計**（附錄 H）：宿主只做兩件事——① 以 `new_string`
＋ `set_property` 把檔案內容**物化**為一個 JS 物件（連字串轉義都不必）；② 把前導碼 eval 進去。
其後之模組載入與測試執行**全在 JS 內**完成——「於同一全域求值」以**間接 eval**
（`(0, eval)(code)`）實現（依規格即全域求值，與 node 之 `vm.runInThisContext` 對位）。
**代價**：`path.join` 必須自行正規化 `.` 與 `..`——前三案的宿主把路徑交給**作業系統**解析，
故簡化版不顯問題；本案之檔案在**記憶體 map** 內、無 OS 可代勞。此為本輪唯一真正的語意陷阱
（初次執行即因此 2 支紅燈，修正後 78／78）。**收穫**：凡能「eval 字串 ＋ 設定物件屬性」之宿主
皆可驅動本替身——**宿主介面之門檻由「三個函式」降為「兩個能力」**。此事對四案皆有價值，
不限於 MoonBit。

**己案之五項代價（如實記之）**：

1. **語言為 pre-1.0**：`moon` 自報 `0.1.20260920`，語言版本 v0.10.0（2026-06；官方另有 1.0 roadmap），
   mooncakes 上之套件亦多在 `0.1.x`。對一支要活十年的建置工具而言，**破壞性變更之風險是實質的**。
2. **native 產物無交叉編譯**：欲得 Windows 版工具，須在 Windows 上建置（或自備交叉 C 工具鏈）。
3. **`.mooncakes/` 預設不入庫**（範本 `.gitignore` 即列之）⇒「入庫即零網路」雖可行（7.6 MB）
   但**非其慣例**——此點與 Go 之 `vendor/` 恰好相反。
4. **QuickJS 綁定之平台覆蓋不全**：`lib/` 只有 `macos-universal`、`linux-x64`、`windows-x64`
   ——**無 linux-arm64、無 windows-arm64**。
5. **生態極小**：本案所賴之關鍵套件（`justjavac/quickjs`、`justjavac/ffi`）由單一作者維護。

**己案之定位**：**「引擎等級最高、取件管道亦乾淨，但語言本身最年輕」**。技術面（QuickJS ＋
純 HTTPS 取件 ＋ 1.2 MB 產物 ＋ 最低之宿主門檻）是四案之外最有趣的一個；
其風險則集中在**成熟度**（準據⑧）而非工程可行性——該準據之權重由事主裁定（§6.2 之 8）。

### 7.8 丁：純 JS 化（去 TypeScript、保留 Node）

即 §5.2 之階段二**單獨**執行（不動宿主）。可去 `tsc`，但 node 仍在。
**評價**：與委託之方向部分相符，但把最貴的一半（Node 宿主之 794 行 ＋ 測試宿主）留著，
且不解決「node 只為此目錄而存在」之異質性。**乙案嚴格優於丁案**。

### 7.9 對照表

| | 甲 維持現狀 | **乙 Swift** | 丙 .NET 10 | **戊 Go** | **己 MoonBit** | 丁 純 JS 化 |
|---|---|---|---|---|---|---|
| npm | 留 | **去** | 去 | 去 | 去 | 留 |
| node | 留 | **去** | 去 | 去 | 去 | 留 |
| `tsc` | 留 | 階段一留／階段二去 | **實測：自 NuGet 取得原生 `tsc`（無 Node），11/11 逐位元組相同**（§7.4.1） | 同丙 | 同丙 | **去** |
| 真實產物驅動（②） | ✅ | **✅ 實測 5／5＋78／78** | **✅ 實測 5／5＋78／78** | **✅ 實測 5／5＋78／78** | **✅ 實測 5／5＋78／78** | ✅ |
| JS 引擎等級 | node（V8） | **瀏覽器級（系統 JSC）** | 解譯器（Jint；或 ClearScript/V8） | 解譯器（goja） | **真引擎（QuickJS）** | node（V8） |
| 78 支測試實時（已編譯） | 0.22 s | **0.31 s** | 0.76 s | 1.78 s | 約 1.0 s | 0.22 s |
| 依賴取得管道（⑥） | —（node 自帶） | Apple **零相依**；非 Apple ⇒ **GitHub（SwiftPM）** | **NuGet** | **GOPROXY**（本機已設 `goproxy.cn`）＋ `vendor` 可離線 | **mooncakes.io（純 HTTPS、非 git）**；引擎為套件內附之預編譯庫 | — |
| 工具鏈體積（⑦） | 無（node 自帶） | **無新工具鏈** | **＋3.0 GB** | **＋331 MB**（vendor 11 MB） | **＋291 MB**（`.mooncakes` 7.6 MB，預設不入庫） | 無 |
| 跨平台建置（⑦） | ✅ | ⚠️ JS 宿主需擇一（**JXKit**／發行版 WebKitGTK 之 JSC／`node`）——**JavaScriptKit 已排除**（§7.5）；三者於 Windows 皆未實測 | `dotnet publish -r`，需 runtime pack | **✅ 一機交叉編譯四平台（實測）** | ❌ **無交叉編譯**（`--target` 選後端非 OS） | ✅ |
| 引擎之平台覆蓋 | — | 系統 JSC | 純受控碼 | 純 Go | ⚠️ 綁定只有 macos-universal／linux-x64／win-x64（**無 arm64 Linux／Windows**） | — |
| **成熟度（⑧）** | 成熟 | **成熟（Swift 6.4）** | 成熟 | 成熟（1.24+） | ⚠️ **pre-1.0**（語言 v0.10.0、`moon` 0.1.x、關鍵套件單一作者） | — |
| 仍需 Swift 供 metadata | — | ✅（本即 Swift，**一套工具鏈**） | ✅（**兩套**） | ✅（**兩套**） | ✅（**兩套**） | — |
| 5.10 相容 | — | **✅ 實測** | — | — | — | — |
| 實驗證據 | — | **八項** | **兩項** | **兩項** | **兩項** | 部分（§2.8） |
| **建議** | — | **管線留在 macOS 時採用** | **跨平台且重生態親和時** | **跨平台且重取件／體積時** | **取決於能否接受 pre-1.0**（§6.2 之 8） | 不採用（併入乙之階段二） |

### 7.10 庚：最小改動案——**不換語言，只換宿主**（第十一輪實測；事主之收束提案）

> **本節與前三節不在同一軸上**：§7.1–§7.9 比較的是「**用哪個語言重寫建置器**」；
> 本節是「**建置器仍用 JavaScript，但把 `node` 換掉**」。二者不互斥——庚案可先做，日後再議是否改寫。

**事主之提案**（原文）：「你看目前已有的 build chain 是否可以脫離對 NODE 的依賴、
只要求 devenv 事先安裝 tsc？」

**答案：可以，且本研究已實測。** 關鍵在於**macOS 內建了一個 JS shell**：

```
/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc
```

實測其 shell 提供 `readFile`／`writeFile`／`load`／`print`／`printErr`／`debug`／`quit`／
`checkSyntax`／`$262`——**足夠取代 `node:fs`／`node:path`／`node:vm`／`node:test` 之全部所需**。

**實測（決定性）**：以 jsc 為宿主、跑**一字未改**之既有 78 支測試（測試與 DOM 替身皆未動）：

```
模組載入：5 ms
測試：78 支，通過 78，失敗 0
real 0m0.138s
```

**0.138 s——比 node 之 0.219 s 更快**，且**零安裝**（在 OS 內）。四案之宿主實時因此重排為：
**jsc 0.138 s ＜ node 0.219 s ＜ JSC＋Swift 0.31 s ＜ Jint 0.76 s ＜ QuickJS 約 1.0 s ＜ goja 1.78 s。**

**故庚案之全貌**：`node` → macOS 內建之 `jsc`（或後備 `osascript -l JavaScript`）；
`tsc` → 原生 `tsc`（§7.4.2 之管道 D：一次約 9 MB 之 HTTP GET，免 node／npm／dotnet）。
**結果：整條鏈只要求 devenv 事先安裝 `tsc`**，`node` 與 `npm` 双双退場。

**剩餘工程（已逐項量清，皆為機械性）**：

| 項 | 現況 | 庚案之處理 |
|---|---|---|
| 五支 `tools/*.mjs` 之 ESM `import` | `import fs from 'node:fs'` 等 18 處 | **jsc 不支援 ESM `import`**（實測：`SyntaxError: import call expects one or two arguments`）⇒ 改為 `load()` 之全域或 shim |
| `process.stdout.write`（19 處） | node 之無換行輸出 | jsc 之 `print` **恆帶換行** ⇒ shim 內做行緩衝，或逐行輸出 |
| `process.argv`（7 處） | 3 個 `--check` 旗標 ＋ 1 個 `--doc-base=` | **jsc 之全域 `arguments` 不存在**（實測 `ReferenceError`；傳給 jsc 之額外引數會被當成**待載入之檔案**）⇒ 改由 Makefile 生成一小段 `_args.js` 供 `load()`，或以環境變數（惟純 jsc 無 `process.env`） |
| `process.exit`（5 處） | 失敗即非零 rc | **實測：`quit(3)` 之 rc 仍為 0**；須改以**未捕捉之例外**收場（實測 rc＝3） |
| `node:child_process`（1 處／2 呼叫） | `execFileSync('plutil', …)` 讀 `Release-Version.plist` | jsc 無子行程能力 ⇒ 於 JS 內解析該 plist 之 XML，或把該值由 Makefile 傳入 |
| shim 本體 | — | 約 40 行 JS（`readFile`／`writeFile`／`path.join`／`indirect eval`／`process` 墊片） |

**庚案之代價與界線（如實記之）**：

1. **`jsc` 是 OS 之實作細節，非對外承諾之 CLI**——它位於 `JavaScriptCore.framework/…/Helpers/`，
   Apple 可隨時搬移或移除（**未驗**其在最舊支援之 dev macOS 上是否同樣存在；本機為 macOS 27）。
   **後備**：`osascript -l JavaScript`（JXA，**有文件、穩定**）——本研究已驗其**讀檔能力**
   （`$.NSString.stringWithContentsOfFileEncodingError` 讀 `version.txt` 成功），
   但**未**在 JXA 上跑過那 78 支測試（附錄 E）。
2. **此案為 macOS 專屬**。jsc 不是跨平台之物；若日後需在 Windows／Linux 上建此管線，
   §7.5 之分析與其餘四案仍然適用。
3. **建置器仍是 JS（794 行）**：不會獲得型別檢查，也不會縮小那批工具之體積。
   庚案解的是「**node 依賴**」，不是「工具鏈異質」。
4. **與階段一之關係**：庚案**不擋**階段一。若日後想要型別化之建置器（Swift／Go／.NET），
   庚案所做之 shim 與宿主抽象正是那一步之工作底稿；反之若庚案夠用，階段一即無必要。

**定位**：**庚案是「只要求 devenv 安裝 `tsc`」這個目標之最廉價解**——不動語言、不動 78 支測試、
不動 `src/`，只換兩樣外部物：宿主與 `tsc` 之來源。事主之收束**成立**。

---

## 八、建議

**第零步（第十一輪新增，且為本研究之首要建議）：先做庚案（§7.10）。**
若目標只是「擺脫 node、只要求 devenv 裝 `tsc`」，則**不必改寫任何語言**：把宿主換成
**macOS 內建之 `jsc`**（實測 78／78、**0.138 s**、零安裝）、把 `tsc` 換成**原生 `tsc`**
（§7.4.2 管道 D，約 9 MB 一次 HTTP GET），即達成——剩餘工程是約 40 行之 shim ＋ 五支工具之
`import` 轉換 ＋ 一處 `plutil` 呼叫。**庚案成本最低、且不擋後續任何一步**：
若日後仍想要型別化之建置器或跨平台，再循下列分支即可。

**第一步（若庚案不足，或需在 Windows／Linux 上搭建）**：先裁定此管線是否需在
Windows／Linux 上搭建；若是，其 JS 宿主如何取件。**
此事決定階段一之實作語言，且**沒有技術上的唯一正解**（§7.5）：

- **若否（管線只在 macOS 上跑）⇒ 乙案（Swift）**。理由：零新工具鏈、零 SwiftPM 相依、
  引擎為瀏覽器級（與 Safari 同源）、且與 legacy 5.10 路徑天然相容。
- **若是，且願以 `node` 或發行版 WebKitGTK 之 JSC 承擔非 Apple 平台之 JS 宿主 ⇒ 仍選乙案**。
  理由：`dump-userdef-metadata` 本即跨平台且取件不碰 GitHub，故 **Swift 一套工具鏈足矣**
  （`node` 之取件走 nodejs.org／鏡像、WebKitGTK 走發行版套件，皆非 GitHub）。
- **若是，且非 Apple 平台上之 JS 宿主亦不得依賴 `node` 與 GitHub ⇒ 丙案（.NET 10）或戊案（Go）**。
  兩者皆已實測足以驅動現行語料（5／5 ＋ 78／78），且**兩者都仍是兩套工具鏈**
  （`dump-userdef-metadata` 是 SwiftPM 執行檔，Swift 省不掉）。二者之取捨：

  | 若首要顧慮是… | 選 | 依據 |
  |---|---|---|
  | **依賴取件之可靠性**與**工具鏈體積** | **戊案（Go）** | `go mod vendor` 讓 11 MB 相依入庫後**建置期零網路**（連鏡像都不必信）；工具鏈 **331 MB**（丙案 3.0 GB）；**一機交叉編譯四平台**（皆已實測） |
  | **與既有生態之親和**（微軟技術棧、NuGet 套件豐富度） | 丙案（.NET） | `dotnet` 已在本機；但工具鏈 3.0 GB、且 JS 宿主仍需一套 |
  | **願承擔 pre-1.0 之風險，換取最高之引擎等級與最低之宿主門檻** | **己案（MoonBit）** | 引擎為 **QuickJS**（真引擎，四案中僅次於乙案之系統 JSC）；取件走**純 HTTPS 之 mooncakes.io**（非 git、非 GitHub）；產物 1.2 MB；且其綁定逼出了「無宿主回呼」之設計（§7.7）。**代價：語言 pre-1.0、無交叉編譯、綁定缺 arm64** |

**本研究之傾向（供事主參考，非代為裁定）**：就事主於第二輪與第五輪所提之兩項關切
（**依賴取件之 GFW 風險** 與 **工具鏈肥大**）而言，**戊案（Go）在兩項上皆優於丙案**：
前者是「可以完全不要 CDN」，後者是 331 MB 對 3.0 GB。丙案之真正長處是與 .NET 生態之親和，
而本案（一支建置工具）用不到那個長處。

**關於己案（MoonBit）之傾向**：其**工程可行性已無疑問**（實測 5／5 ＋ 78／78，且引擎最真、
取件最乾淨、產物最小、宿主門檻最低）；唯一的問題是**成熟度**——本倉是一支要長期維護的輸入法，
其建置工具卻押在一個語言版本仍為 v0.10.0、關鍵套件由單一作者維護、且**無法交叉編譯**之上。
**本研究不建議現在採用**，但建議**記為日後重估之首選**：若 MoonBit 於 1.0 後仍保持此一取件結構與
QuickJS 綁定之維護，則它會是四案中最省事的一個。**此一條目應由事主裁定**（§6.2 之 8）。惟須記明戊案之代價：**goja 是三者中最慢的宿主**
（1.78 s 對 0.76 s 對 0.31 s），且 Go 對本倉而言是第三種語言。

**第二步（兩案共通，無論選誰）**：實作「階段一」——由新工具接手全部既有職責，**移除 npm 與 node**，
`src/` 一個字元不動，`Makefile` 只餘薄包裝（`make audit` 照舊）。驗收是產物**逐位元組相同**、
完全可逆（§5.1）。此步之收益與語言無關，且已有兩個語言的實測原型（§2.2 之 250 行 Swift、
§2.10 之 156 行 C#）。

**第三步（可選、待裁定）**：階段二（去 TypeScript）。技術已驗（§2.8：78／78、5／5、守衛 OK），
真正的取捨是「`schema` 層之靜態型別 vs 少一支外部行程」，而後者在階段一之後已不再痛。

**其餘四項不隨語言選擇而變**：

4. **ES5 規則與既有測試留在 JS，由所選宿主之引擎執行。** 向事主言明：本改寫消除的是
   **建置相依**（npm／node／tsc），不是倉內的 JavaScript；助手產物本身是 JS，
   而受測物與規則定義都不該為了「語言純度」而被重寫。
5. **`vChewing-DevLogs/Tools/` 之兩支 Python 不併入本工具。** 安全網必須獨立於被保護之物
   （§6.2 之 6）。
6. **助手是否隨 `vChewing.app` 出貨**是獨立決策（§4.5），與本案無關。
7. **本文之全部結論以附錄 A 之十項實測為憑**；凡未實測者（Xcode 成員集之 `.swift` 待遇、
   併發 `swift run`、真機 Safari 7、以及 §7.4 之 `ClearScript` 路徑）皆已列入 §6.1 與附錄 E，
   並標明為推論或未驗。

**附註：「跨平台編譯」單獨看時之最優解（2026-09-25，事主追問「也就是說現在的跨平台編譯最優解
是 golang？」）**——此問須與「整體最優」分開回答，否則會被讀成前者蘊含後者：

- **單就跨平台編譯而言，最優解確是戊案（Go）**，且已實測：同一台 macOS 上 `GOOS`／`GOARCH`
  產出 `windows/amd64`、`windows/arm64`、`linux/amd64`、`linux/arm64` 四個**靜態**執行檔
  （各 12–13 MB；`file` 確認 PE32+／ELF），**不需額外 SDK、不需 runtime pack**。
- **但有兩個前提**：① 該優勢**建立於「JS 宿主為純 Go」之上**——goja 無 cgo，故交叉編譯乾淨；
  一旦改用需 cgo 之宿主（例如以 cgo 鏈結發行版之 WebKitGTK JSC），**交叉編譯即失效**。
  ② 交叉編譯只保證**產得出**，不保證**跑得對**：本研究**未在真實 Windows／Linux 上執行過**那些產物
  （附錄 E 之 7①）。
- **一個不可忽略之反例**：己案（MoonBit ＋ QuickJS）之**引擎等級明顯較高**（真引擎對受控碼解譯器），
  卻**完全沒有交叉編譯**；丙案（.NET）可行 `publish -r` 但要 runtime pack 且產物大一截。
  換言之，**Go 在「跨平台編譯」這一項稱冠的同一個設計裡，正好在「JS 宿主品質」這一項墊底**
  （goja 為四案中最慢，1.78 s 對 0.31／0.76／約 1.0 s）。四案之中**沒有任何一案在所有準據上皆勝**。
- **故不可由此推得「整體最優解是 Go」**：若該管線實際上只在 macOS 上跑——而**目前正是如此**
  （官網倉無 CI，見 §1.4）——則乙案（Swift）仍是最省事之解：**零新工具鏈、單一工具鏈、
  且引擎為瀏覽器級**。Go 之稱冠只在「**確需在 Windows／Linux 上產出或驗證**」這個前提成立時才相關。

**一項對初稿之明確訂正**：初稿曾以「.NET 無內建 JS 引擎」為由整體否定丙案。該結論**錯誤**，
已由 §2.9／§2.10 推翻；兩案之取捨自此完全落在**依賴管道／跨平台**與**引擎等級**兩項上，
而非「可行與否」。

## 附錄 A：實測環境與逐條指令

**環境**：macOS 27.0（Build 26A428，arm64）／Xcode 27.1（27A9269）／Swift 6.4
（`swiftlang-6.4.0.34.1 clang-2100.3.34.1`）／Swift 5.10.1（`org.swift.5101202406041a`）／
Node v22.20.0／TypeScript 7.0.2／**.NET SDK 10.0.201**（`/usr/local/share/dotnet/dotnet`；
另裝 6.0.136／6.0.428／8.0.416；執行期 `Microsoft.NETCore.App` 10.0.5；**不在預設 `PATH`**，
故以下 .NET 指令皆先 `export PATH="/usr/local/share/dotnet:$PATH"`）。
受測之 `vChewing-macOS` HEAD 為 `2fe172ca`。

**工作目錄**（scratch，未入庫）：`tmp/poc-jsc/`、`tmp/manifest-probe/`、`tmp/stage2-probe/`、
`tmp/dotnet-probe/`。

```bash
# 基線
cd vChewing-macOS/ValueAdd/WebConfigAssistant
make audit                       # rc=0，real 2.882s
node --test tests/*.test.js      # 1..78 / # pass 78 / # fail 0；duration_ms 192.03
node tools/fixtures.mjs --check  # 5 份 same；real 0.047s
make metadata                    # real 1.506s；SwiftPM: Build complete! (0.24秒)

# 實驗一＋二：Swift 宿主（附錄 B）
swift  tmp/poc-jsc/PoC.swift      vChewing-macOS/ValueAdd/WebConfigAssistant   # → 5/5 位元組相同
swiftc -O tmp/poc-jsc/NodeHost.swift -o tmp/poc-jsc/nodehost
tmp/poc-jsc/nodehost vChewing-macOS/ValueAdd/WebConfigAssistant \
  tests/questions.test.js tests/i18n.test.js tests/preset.test.js \
  tests/metadata.test.js tests/dom-smoke.test.js                              # → 78 支／通過 78；real 0.31s

# 實驗三：雙 manifest
cd tmp/manifest-probe
swift test                                                     # 6.4：swift-testing 1 支通過
TOOLCHAINS=org.swift.5101202406041a xcrun swift package dump-package   # toolsVersion 5.10.0、targets [vca-builder]
TOOLCHAINS=org.swift.5101202406041a xcrun swift run --scratch-path .b510   # actor total = 36
TOOLCHAINS=org.swift.5101202406041a xcrun swift test --scratch-path .b510  # error: no tests found

# 實驗四：嚴格模式
swift tmp/poc-jsc/strict2.swift vChewing-macOS/ValueAdd/WebConfigAssistant/dist/core.js

# 實驗五：\w 語意
node -e 'console.log(/(^|[^\w$.])let\s/.test("唯音let x"))'     # true（JS：\w 為 ASCII-only）

# 實驗六：守衛之詞法感知
node -e 'import("./tools/es5guard.mjs").then(m => console.log(m.scan(sample).length))'   # 0（含字串者）、1（真箭頭函式）

# 實驗七：Xcode 專案模型
grep -oE "[A-F0-9]{24} /\* [A-Za-z0-9_.]+ \*/ = \{isa = PBXFileSystemSynchronizedRootGroup" \
  vChewing-macOS/vChewing.xcodeproj/project.pbxproj      # Plugins / vChewingIME_macOS / ValueAdd / Installer_macOS / vChewingDebuggable
python3 -c '…PIF…'   # groupTree 內確有 assistant.css / questions.ts / build.mjs（sourcecode.typescript）

# 實驗九／十：.NET 側（NuGet 管道）
export PATH="/usr/local/share/dotnet:$PATH"
dotnet --list-sdks                                     # 10.0.201（另有 6.0／8.0）
cd tmp/dotnet-probe/JintProbe && dotnet add package Jint        # restore 5.08s → Jint 4.16.3
dotnet run -- <WebConfigAssistant 之絕對路徑>                     # → core.js 載入 Jint：66.3 ms；fixture 5/5 位元組相同
cd ../NodeHostProbe && dotnet run -- <同上> \
  tests/questions.test.js tests/i18n.test.js tests/preset.test.js \
  tests/metadata.test.js tests/dom-smoke.test.js                 # → 78 支／通過 78；real 0.759s（純執行）

# 第四輪：TypeScript 自 NuGet（量測「免除額外安裝」之宣稱）
export PATH="/usr/local/share/dotnet:$PATH"
cd tmp/ts-nuget-probe
dotnet add package Microsoft.TypeScript.MSBuild      # restore 5.66s → 7.0.1；套件 217 MB、六個原生 tsc（各 26–28 MB）
TSC=~/.nuget/packages/microsoft.typescript.msbuild/7.0.1/tools/runtimes/darwin-arm64/tsc
"$TSC" --version                                      # → Version 7.1.0-dev.20260817.1（本機全域者為 7.0.2）
(cd <WebConfigAssistant> && "$TSC" --project tsconfig.json --outDir <out>)
for f in <WebConfigAssistant>/dist/js/*.js; do cmp -s "$f" "<out>/$(basename $f)" && echo "same $(basename $f)"; done
                                                     # → 11 檔全部 same（逐位元組相同）

# 第五輪：Go（量測體積、交叉編譯與依賴內嵌）
export PATH="/usr/local/go/bin:$PATH"
go version                                    # → go1.24.3 darwin/arm64（/usr/local/go/bin/go，不在預設 PATH）
go env GOPROXY                                # → https://goproxy.cn,direct（中國鏡像；此為環境變數，可任意指定）
go get github.com/dop251/goja@latest          # 9.76s；連同 4 個遞移相依
go run ./fixprobe  <WebConfigAssistant> ./driver.js      # → core.js 載入 goja 6.1 ms；fixture 5/5 位元組相同
go run ./hostprobe <WebConfigAssistant> ./prelude.js \
  tests/questions.test.js tests/i18n.test.js tests/preset.test.js \
  tests/metadata.test.js tests/dom-smoke.test.js          # → 78 支／通過 78
go build -o bin/hostprobe ./hostprobe && ls -lh bin/hostprobe   # → 13 MB 靜態執行檔
for t in windows/amd64 windows/arm64 linux/amd64 linux/arm64; do \
  GOOS=${t%/*} GOARCH=${t#*/} go build -o bin/hostprobe-$os-$arch ./hostprobe; done
                                              # → 12–13 MB；file 確認 PE32+／ELF
go mod vendor && du -sh vendor                # → 11 MB；此後建置期零網路

# 第六輪：MoonBit（事主自行安裝：curl -fsSL https://cli.moonbitlang.com/install/unix.sh | bash）
#   本研究並將 ~/.moon/bin 併入 bash（~/.bash_profile ＋ ~/.bashrc，帶守衛）、
#   nushell（~/.config/nushell/env.nu）；zsh 由安裝程式自理（~/.zshrc:118）。
export PATH="$HOME/.moon/bin:$PATH"
moon version                                          # → moon 0.1.20260920；~/.moon 共 291 MB
cd tmp/moon-probe && moon new . --user vca --name moonprobe   # （實作時於上層先建）
moon add justjavac/quickjs                            # 18s；帶入 justjavac/ffi、moonbitlang/x
moon add moonbitlang/x                                # 需在 module 層宣告，否則子套件不得 import
moon build --target native                            # 產物 1.2 MB
_build/native/release/build/cmd/main/main.exe         # → fixture 5/5；測試 78 支／通過 78（約 1.0s）
go env 2>/dev/null; cat ~/.moon/registry/.registry-update-state.json   # 端點為 download.mooncakes.io（純 HTTPS，非 git）

# 實驗八：一次性遷移候選
tsc --project tsconfig.json --outDir tmp/stage2-probe/js --removeComments false
# → 187,474 B（vs 148,148 B）；串接後 assistant.html 388,602 B（vs 349,299 B，＋39,303 B）
# → fixture 5/5 位元組相同；78/78 測試通過；es5guard OK
```

**遷移候選之可讀性佐證**（`--removeComments false` 產出之 `questions.js` 開頭 20 行）：

```js
"use strict";
// 唯音輸入法配置助手 // 題庫（分支問卷）。
//
// 設計立場：題庫**不新造**，而是把官網既有的策展知識（`onboarding/*.md`、`manual/preferences.md`）
// 可執行化。每一題的標題與說明一律取自 app 自己的 `.strings`（經後設資料導出）；
// 本檔只負責「分頁、排序、分支、推薦值」。
//
// 兩條不可退讓之約束：
//   ① 每個單選題之預設選項一律為「維持不變」——未表態者不輸出任何鍵。
//   ② 助手不得產出後端會拒收的值（故選項一律與 `validNumeralValueRange` 取交集）。
var VCA;
(function (VCA) {
    /// 版本碼之下限（macOS 10.9 ⇒ 1009）。見 schema.ts 之 `osVersionCode`。
    var MINIMUM_OS_FLOOR = 1009;
    …
```

型別抹除、`namespace` 降為 IIFE、**註解原位保留**（含 `///`），與原 `.ts` 逐語句對應。

---

## 附錄 B：PoC 原始碼（Swift 之 Node 替身）

**性質宣告**：以下為**一次性 PoC**，非生產碼——其用意是**量測可行性**，故刻意不做錯誤處理之
完備、不支援未用到之 Node API、`path.join` 之正規化亦只做到測試所需之程度。
實驗過程中修掉兩處橋接缺陷（`path.join` 之可變參數橋接、模組載入失敗之靜默吞掉），
**此二處本身即是「移植成本」之實測樣本**。正式實作須補：`Data` 層之 I/O、UTF-8 邊界、
錯誤訊息之可讀性、以及 §4.4 之 Swift 層測試。

```swift
// (c) 2026 and onwards The vChewing Project (MulanPSL-2.0 License).
// ====================
// This code is released under the SPDX-License-Identifier: `MulanPSL-2.0`.
//
// 一次性 PoC（可行性研究用之量測原型），非生產碼。原檔：tmp/poc-jsc/NodeHost.swift。
// PoC #2: a Swift-hosted CommonJS + Node-builtin shim, so that the *existing,
// unmodified* `tests/*.test.js` suite runs inside JavaScriptCore.
//
// Usage: swift NodeHost.swift /path/to/ValueAdd/WebConfigAssistant tests/questions.test.js ...

import Foundation
import JavaScriptCore

// MARK: - Assertion / test-harness prelude (evaluated once, in JS)

let prelude = """
var __tests = [];
var __modules = {};
function __AssertionError(message, operatorName) {
  var err = new Error(message);
  err.name = 'AssertionError';
  err.code = 'ERR_ASSERTION';
  err.operator = operatorName;
  return err;
}
function __deepEqual(a, b) {
  if (a === b) return true;
  if (typeof a !== typeof b) return false;
  if (a === null || b === null) return false;
  if (typeof a !== 'object') return false;
  var aArray = Object.prototype.toString.call(a) === '[object Array]';
  var bArray = Object.prototype.toString.call(b) === '[object Array]';
  if (aArray !== bArray) return false;
  if (aArray) {
    if (a.length !== b.length) return false;
    for (var i = 0; i < a.length; i++) { if (!__deepEqual(a[i], b[i])) return false; }
    return true;
  }
  var keysA = Object.keys(a), keysB = Object.keys(b);
  if (keysA.length !== keysB.length) return false;
  for (var j = 0; j < keysA.length; j++) {
    var key = keysA[j];
    if (!Object.prototype.hasOwnProperty.call(b, key)) return false;
    if (!__deepEqual(a[key], b[key])) return false;
  }
  return true;
}
function __assert(ok, message, operatorName) {
  if (!ok) throw __AssertionError(message || ('assertion failed: ' + operatorName), operatorName);
}
var __pathModule = {
  join: function () {
    var parts = [];
    for (var i = 0; i < arguments.length; i++) {
      var part = String(arguments[i]);
      if (part === '') continue;
      parts.push(part);
    }
    var out = '';
    for (var j = 0; j < parts.length; j++) {
      var piece = parts[j];
      if (out === '') { out = piece; continue; }
      var lastChar = out.charAt(out.length - 1);
      var firstChar = piece.charAt(0);
      if (lastChar === '/' && firstChar === '/') { out = out + piece.slice(1); continue; }
      if (lastChar === '/' || firstChar === '/') { out = out + piece; continue; }
      out = out + '/' + piece;
    }
    return out;
  },
};
var __assertModule = {
  ok: function (value, message) { __assert(!!value, message, 'ok'); },
  strictEqual: function (actual, expected, message) {
    __assert(actual === expected, message || ('strictEqual: ' + String(actual) + ' !== ' + String(expected)), 'strictEqual');
  },
  notStrictEqual: function (actual, expected, message) {
    __assert(actual !== expected, message || ('notStrictEqual: ' + String(actual) + ' === ' + String(expected)), 'notStrictEqual');
  },
  deepStrictEqual: function (actual, expected, message) {
    __assert(__deepEqual(actual, expected),
      message || ('deepStrictEqual failed'), 'deepStrictEqual');
  },
  equal: function (actual, expected, message) { __assertModule.strictEqual(actual, expected, message); },
  throws: function (fn, message) {
    var threw = false;
    try { fn(); } catch (e) { threw = true; }
    __assert(threw, message || 'throws: 未拋出', 'throws');
  },
};
var __testModule = function test(name, fn) { __tests.push({ name: name, fn: fn }); };
__testModule.test = __testModule;
__testModule.describe = function (name, fn) { fn(); };
__testModule.it = __testModule;
"""

// MARK: - Node host

final class NodeHost {
  let ctx: JSContext
  let root: URL
  var cache: [String: JSValue] = [:]
  var lastException: String = ""
  var currentTest: String = ""

  init(root: URL, coreSourceOverride: String? = nil) {
    self.root = root
    let vm = JSVirtualMachine()!
    self.ctx = JSContext(virtualMachine: vm)!
    ctx.exceptionHandler = { [weak self] _, exception in
      self?.lastException = exception?.toString() ?? "?"
    }
    ctx.evaluateScript(prelude, withSourceURL: URL(fileURLWithPath: "prelude.js"))
    installBuiltins()
  }

  func fail(_ message: String) -> Never {
    FileHandle.standardError.write(Data((message + "\n").utf8))
    exit(2)
  }

  // MARK: Native builtins

  private func installBuiltins() {
    let fs: @convention(block) (String, JSValue?) -> JSValue = { [unowned self] path, encoding in
      let url = URL(fileURLWithPath: path)
      guard let text = try? String(contentsOf: url, encoding: .utf8) else {
        return JSValue(undefinedIn: self.ctx)
      }
      return JSValue(object: text, in: self.ctx)
    }
    let fsExists: @convention(block) (String) -> Bool = { path in
      FileManager.default.fileExists(atPath: path)
    }
    let vmRun: @convention(block) (String, JSValue?) -> JSValue = { [unowned self] code, options in
      let filename = options?.objectForKeyedSubscript("filename")?.toString()
      return self.ctx.evaluateScript(code, withSourceURL: URL(fileURLWithPath: filename ?? "eval.js"))
    }

    let global = ctx.globalObject!
    let fsModule = JSValue(newObjectIn: ctx)!
    fsModule.setObject(unsafeBitCast(fs, to: AnyObject.self), forKeyedSubscript: "readFileSync" as NSString)
    fsModule.setObject(unsafeBitCast(fsExists, to: AnyObject.self), forKeyedSubscript: "existsSync" as NSString)

    let pathModule = ctx.objectForKeyedSubscript("__pathModule")!

    let vmModule = JSValue(newObjectIn: ctx)!
    vmModule.setObject(unsafeBitCast(vmRun, to: AnyObject.self), forKeyedSubscript: "runInThisContext" as NSString)

    let assertModule = ctx.objectForKeyedSubscript("__assertModule")!
    let testModule = ctx.objectForKeyedSubscript("__testModule")!

    for (name, module) in [
      ("node:fs", fsModule), ("fs", fsModule),
      ("node:path", pathModule), ("path", pathModule),
      ("node:vm", vmModule), ("vm", vmModule),
      ("node:assert", assertModule), ("assert", assertModule),
      ("node:test", testModule), ("test", testModule),
    ] {
      ctx.setObject(module, forKeyedSubscript: "__builtin:" + name as NSString)
    }
    _ = global
  }

  /// CommonJS `require`, implemented in Swift; `fromDir` is the requiring module's directory.
  func requireNative(fromDir: String, id: String) -> JSValue {
    if let builtin = ctx.objectForKeyedSubscript("__builtin:" + id), !builtin.isUndefined {
      return builtin
    }
    guard id.hasPrefix(".") || id.hasPrefix("/") else {
      fail("未知之模組：" + id)
    }
    var candidate = URL(fileURLWithPath: fromDir).appending(path: id)
    if candidate.pathExtension.isEmpty { candidate.appendPathExtension("js") }
    return loadModule(at: candidate)
  }

  func loadModule(at url: URL) -> JSValue {
    let key = url.standardizedFileURL.path
    if let cached = cache[key] { return cached }
    guard let source = try? String(contentsOf: url, encoding: .utf8) else {
      fail("找不到模組：\(key)")
    }
    let dir = url.deletingLastPathComponent().path
    let wrapperSource = """
    (function (exports, require, module, __filename, __dirname) {
    \(source)
    })
    """
    guard let wrapper = ctx.evaluateScript(
      wrapperSource, withSourceURL: url
    ) else { fail("模組無法包裝：\(key)") }

    let module = JSValue(newObjectIn: ctx)!
    let exports = JSValue(newObjectIn: ctx)!
    module.setObject(exports, forKeyedSubscript: "exports" as NSString)
    cache[key] = exports

    let require: @convention(block) (String) -> JSValue = { [unowned self] id in
      self.requireNative(fromDir: dir, id: id)
    }
    lastException = ""
    _ = wrapper.call(withArguments: [
      exports, unsafeBitCast(require, to: AnyObject.self), module, key, dir,
    ])
    if !lastException.isEmpty {
      FileHandle.standardError.write(Data("模組載入失敗 \(key)：\(lastException)\n".utf8))
    }
    if let final = module.objectForKeyedSubscript("exports"), final.isObject {
      cache[key] = final
      return final
    }
    return exports
  }

  // MARK: Test driving

  func runAllTests() -> (passed: Int, failures: [String]) {
    guard let tests = ctx.objectForKeyedSubscript("__tests"), tests.isArray else {
      return (0, ["__tests 不是陣列"])
    }
    let count = Int(tests.forProperty("length")!.toInt32())
    var passed = 0
    var failures: [String] = []
    for index in 0..<count {
      let entry = tests.atIndex(index)!
      let name = entry.objectForKeyedSubscript("name")!.toString()!
      let fn = entry.objectForKeyedSubscript("fn")!
      lastException = ""
      _ = fn.call(withArguments: [])
      if lastException.isEmpty {
        passed += 1
      } else {
        failures.append("\(name)：\(lastException)")
      }
    }
    return (passed, failures)
  }
}

// MARK: - main

let root = URL(fileURLWithPath: CommandLine.arguments[1])
let files = Array(CommandLine.arguments.dropFirst(2))
let clock = Date()
let host = NodeHost(root: root)
for file in files {
  _ = host.loadModule(at: root.appending(path: file))
}
let loadMs = Date().timeIntervalSince(clock) * 1000
let result = host.runAllTests()
print(String(format: "模組載入：%.1f ms", loadMs))
print("測試：\(result.passed + result.failures.count) 支，通過 \(result.passed)，失敗 \(result.failures.count)")
for failure in result.failures.prefix(12) { print("  ✗ \(failure)") }
exit(result.failures.isEmpty ? 0 : 1)
```

**實驗一之驅動**（`PoC.swift`，147 行，全文從略）之核心：把 `dist/core.js` 求值進 `JSContext`，
再以一段 JS 函式照 `tools/fixtures.mjs` 之五個情境產生配置包，與 `tests/fixtures/*.json`
逐位元組比對；情境之 `profile`／`manualAnswers`／`fillAllPages`／`starter` 逐項照抄
`tools/fixtures.mjs` 之 `SCENARIOS`，確保「同一份輸入」。

---

## 附錄 C：逐檔對照（現行 → 建議）

> **本表以乙案（Swift）之落點為例**。丙案（.NET）與戊案（Go）所欲承接之**職責完全相同**
> （串接、投影、HTML 組裝、ES5 守衛、fixture 驅動、曝光面掃描、版本比對、JS 測試宿主、
> metadata dump 之獨占），差別只在語言與檔名（`.csproj`／`go.mod`）。故不重複三份表——
> **附錄 B、F、G 之三支 PoC 已分別示範了同一批職責在三個語言下的骨架**。

| 現行 | 建議 | 備註 |
|---|---|---|
| `tools/build.mjs` | `Sources/VCABuilder/{BundleAssembler,MetadataProjection,HtmlAssembly}.swift` | `CORE_ORDER`／`APP_ORDER` 與 `assertOrderCoversSources()` 原樣對位 |
| `tools/es5guard.mjs` | `Sources/VCABuilder/ES5Guard.swift` ＋ `tools/es5-rules.js` | **規則與 `stripLiterals` 留 JS**（§3.3①） |
| `tools/fixtures.mjs` | `Sources/VCABuilder/JSFixtureDriver.swift` | 情境表照抄；產生與比對之邏輯於 JSC 內執行 |
| `tools/settings-surface.mjs` | `Sources/VCABuilder/SettingsSurface.swift` | `KeyboardParser` 之逐行掃描與分隔線正則原樣對位 |
| `tools/target-version.mjs` | `Sources/VCABuilder/TargetVersion.swift` | `.plist` 改用 `PropertyListSerialization` |
| `tests/core-loader.js` | `Sources/VCABuilder/JavaScriptHost.swift` | `vm.runInThisContext` ⇒ 同一 context 之 `evaluateScript` |
| `tests/dom-shim.js` | **原樣保留** | 216 行 JS，一字不改 |
| `tests/*.test.js` | **原樣保留** | 2,183 行 JS，一字不改 |
| — | `Sources/VCABuilder/TestHarness.swift` | 新增（§4.4） |
| — | `Sources/VCABuilder/MetadataDump.swift` | 新增（actor，§4.3①） |
| — | `Sources/VCABuilder/main.swift`·`Paths.swift` | 新增 |
| `package.json` | **刪除** | npm 無職能（§1.2） |
| `tsconfig.json` | 階段一保留；階段二刪除 | §5.2 |
| `src/*.ts` | 階段一不動；階段二換為 `tsc` 產出之 `src/*.js` | §5.2 不變式：「入庫者恆等於機器產物」 |

## 附錄 D：`make` 目標對照

| `make` 目標 | 階段一之後 | 階段二之後 |
|---|---|---|
| `help` | 不變 | 不變 |
| `typecheck` | `vca-builder typecheck`（內部呼 `tsc --noEmit`） | **刪除** |
| `build` | `vca-builder build`（內部呼 `tsc`） | `vca-builder build`（無 `tsc`） |
| `bundle` | `vca-builder build` | 同左 |
| `es5` | `vca-builder es5` | 同左 |
| `test` | `vca-builder test`（JSC 宿主） | 同左 |
| `metadata` / `metadata-update` / `metadata-audit` | `vca-builder metadata …`（actor；dump 一次） | 同左 |
| `surface` / `surface-check` | `vca-builder surface …` | 同左 |
| `version-check` | `vca-builder version-check` | 同左 |
| `fixtures` / `fixtures-check` | `vca-builder fixtures …` | 同左 |
| `audit` | `vca-builder audit`（8 段併行，§4.3③） | 同左（少一段） |
| `serve` | 不變（`python3`） | 不變 |
| `deploy` | `vca-builder` 或 `cp` | 同左 |
| `clean` | 提示文字更新（`.build/` 與 `Builder/.build/`） | 同左 |
| —（新） | `collect --into …` | 同左 |

## 附錄 E：本文未驗之事項

1. **`ValueAdd/` 同步根群組對新 `.swift` 檔之實際待遇**（§2.7、R2）——需一次 Xcode 建置。
   已實測者僅止於「PIF 內確有列舉助手之檔案」與「既有備忘錄載明 Release 產物不含其內容」。
2. **兩次 `swift run` 併發之實際行為**（R3）——本文明確以 actor 迴避，未實測其失敗形態。
3. **真機 macOS 10.9 ＋ Safari 7 之複核**（R12）——本工作區無法代勞；
   階段一之產物不變、階段二之產物僅多註解，故語法層風險不變。
4. ~~**`.NET 10` 之任何一項**——`dotnet` 未安裝，全部為文獻性評估。~~ **（第二輪已補實測）**
   §2.9／§2.10 已量測 .NET 側之 fixture 與測試；**仍未驗者**為：① `ClearScript`（V8，NuGet）
   路徑之可行性與體積；② Jint 對**未來** ES2015+ 寫法之覆蓋度邊界（現行語料已全綠，但邊界未探）；
   ③ ~~`Microsoft.TypeScript.MSBuild` 於 net10.0 之現況~~ **（第四輪已補實測，見 §7.4.1）**——
   **仍未驗者**：該套件之 **MSBuild 自動編譯整合**（本研究只呼叫了它帶下來的 `tsc` 執行檔，
   未以 `dotnet build` 走 `TypeScriptCompile` 項目）；以及「**Swift 驅動之流程自行自 nuget.org
   下載 .nupkg、解壓、挑 RID**」這條變體（未實作，僅指出其可行）。
5. **`tsc --checkJs` 對階段二之 `.js` 是否真能提供可用之型別檢查**——未試；
   此為階段二之緩解手段，若事主要走階段二，**宜先花少量時間驗此點**。
6. **5.10 toolchain 下建置完整 `Builder/` 套件**——實測用的是三檔小套件（§2.3），
   非本建議之完整套件；`JavaScriptCore` 之連結（`.linkedFramework`）在 5.10 下之表現未驗。
7. **戊案（Go）之未驗項**：① **交叉編譯之產物未在真實 Windows／Linux 上執行過**
   ——本研究只以 `file` 確認其為 PE32+／ELF，未實跑（本機無該兩平台）；
   ② **goja 之 ES 覆蓋度邊界未探**（現行語料全綠，但邊界未測，與 Jint 同類之顧慮）；
   ③ `go.mod` 記 `go 1.25.0` 而本機為 **1.24.3**——Go 之自動 toolchain 取用**在受限網路下**
   是否順暢未驗（本機之 `goproxy.cn` 通暢）；
   ④ Go 案之 CI／Makefile 接線未實作。
8. **己案（MoonBit）之未驗項**：① **native 產物未在 Windows／Linux 實跑**（本機只有 macOS；
   且該案**無交叉編譯**，故無法如戊案那樣一機產出他平台產物來檢視）；
   ② `lib/linux-x64`、`lib/windows-x64` 之 QuickJS 靜態庫**未經連結實測**（本機只驗了 `macos-universal`）；
   ③ MoonBit 之 **1.0 roadmap 之時程**未查（本研究只確認現行版本為 v0.10.0／`moon` 0.1.x）；
   ④ 己案之 CI／Makefile 接線未實作；
   ⑤ 本研究為 MoonBit 所加之 **bash／nushell env 區塊未經 nushell 實跑驗證**
   （本機無 `nu` 執行檔；`~/.config/nushell/env.nu` 之語法依現行 nushell 慣例書寫）。
9. **乙案之非 Apple JS 宿主（第八輪新增之未驗項）**：① `jectivex/JXKit` **未實測**——本研究只查其
   描述、`Package.swift` 之平台設定與 README 之 Linux 說明，**未以之建置或執行任何東西**
   （本機為 macOS，且該套件之 Linux 路徑需 WebKitGTK 之 JSC）；② **Windows 上之 JSC 來源未驗**
   （JXKit 之 `.when(platforms: [.windows])` 連結設定指向何處、是否可得，皆未查）；
   ③ JXKit 之**維護活躍度**（最近提交 2026-01-24）與其 **LGPL-3.0** 授權對本工作區之適用性未評估
   （惟該工具不隨發行版出貨，與 IME 之授權閉包無涉）；④ Gitee 鏡像之**更新頻率**未驗
   （本研究只確認「取用當時落後約 5 日、標籤不缺」）。
10. **庚案（第十一輪）之未驗項**：① **`jsc` 在較舊之 dev macOS 上是否同樣存在**未驗
   （本機為 macOS 27；該檔位於 `JavaScriptCore.framework/Versions/A/Helpers/`，
   屬 OS 之實作細節而非對外承諾之 CLI）；② **JXA（`osascript -l JavaScript`）未跑過那 78 支測試**
   ——本研究只驗其讀檔能力；③ **五支工具本身尚未在 `jsc` 下實跑**（本輪只跑通了「測試宿主」這一半，
   即 `tests/*.test.js` ＋ `dom-shim.js` ＋ `core-loader.js`）；④ `quit(n)` 不設 rc 之替代做法
   （以未捕捉例外收場，實測 rc＝3）**未在真流程中接線**。
11. **`make audit` 在階段一之後之實時**——本文只給「現況 2.882 s」與「應趨近於一次 `swift run`」
   之推論，未實作故未實測。


---

## 附錄 F：.NET 側 PoC 原始碼（Jint 之 Node 替身）

**性質宣告**：與附錄 B 同——**一次性 PoC**，用意是**量測可行性**，非生產碼。
四支檔案皆在 `tmp/dotnet-probe/`（未入庫）。與 Swift 版（附錄 B）逐項同構：
`csproj` 即「manifest」、`prelude.js` 即「Node 內建替身」、`Program.cs` 即「宿主」。
實測過程中修掉之缺陷：① `Jint` 之 `Engine.Invoke` 對 `Func<string, JsValue>` 之封送不直觀 ⇒
改以「於同一引擎內求值一小段 JS 呼叫」為唯一跨界方式（`engine.SetValue` ＋ `engine.Execute`）；
② 測試檔之原始碼含大量 CJK 與引號 ⇒ 以 `__sourceText` 傳值取代字串內嵌，免跳脫問題。

### F.1 `NodeHostProbe/NodeHostProbe.csproj`（即 .NET 側之「manifest」）

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <AssemblyName>NodeHostProbe</AssemblyName>
    <RootNamespace>NodeHostProbe</RootNamespace>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Jint" Version="4.16.3" />
  </ItemGroup>
</Project>
```

### F.2 `NodeHostProbe/Program.cs`（宿主；產出 §2.10 之 78／78）

```csharp
// (c) 2026 and onwards The vChewing Project (MulanPSL-2.0 License).
// ====================
// This code is released under the SPDX-License-Identifier: `MulanPSL-2.0`.
// Phase 245 PostResearch 附錄 F 之 .NET/Jint 分支實測：
// 以 Jint 執行**一字未改**之既有 tests/*.test.js（含 DOM 冒煙測試）。
//
// 用法：dotnet run -- <WebConfigAssistant 之絕對路徑> <相對於該路徑之測試檔>...

using System.Text.Json;
using Jint;
using Jint.Native;

var root = args.Length > 0 ? args[0] : ".";
var testFiles = args.Skip(1).ToArray();

var engine = new Engine(options => options
  .LimitRecursion(512)
  .MaxStatements(0));

// 三個宿主 API：檔案讀取、存在性、於同一全域求值。
engine.SetValue("__readFile", new Func<string, string?>(path =>
  File.Exists(path) ? File.ReadAllText(path) : null));
engine.SetValue("__fileExists", new Func<string, bool>(path => File.Exists(path)));
engine.SetValue("__evalExpr", new Func<string, string, JsValue>((
  code, _) => engine.Evaluate(code)));

var preludePath = Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "prelude.js");
if (!File.Exists(preludePath))
  preludePath = Path.Combine(root, "..", "..", "..", "tmp", "dotnet-probe", "NodeHostProbe", "prelude.js");
engine.Execute(File.ReadAllText(preludePath));

static string Q(string text) => JsonSerializer.Serialize(text);

var clock = System.Diagnostics.Stopwatch.StartNew();
foreach (var file in testFiles)
{
  var full = Path.Combine(root, file);
  var dir = (Path.GetDirectoryName(full) ?? ".").Replace('\\', '/');
  engine.SetValue("__sourceText", File.ReadAllText(full));
  try
  {
    engine.Execute($"__loadModuleSource({Q(dir)}, {Q(full)}, __sourceText);");
  }
  catch (Exception ex)
  {
    Console.Error.WriteLine($"模組載入失敗 {Path.GetFileName(full)}：{ex.GetType().Name}: {ex.Message.Split('\n')[0]}");
  }
}
Console.WriteLine($"模組載入：{clock.Elapsed.TotalMilliseconds:F1} ms");

var total = (int)engine.Evaluate("__tests.length").AsNumber();
var passed = 0;
var failures = new List<string>();
for (var index = 0; index < total; index++)
{
  var name = engine.Evaluate($"__tests[{index}].name").AsString();
  try
  {
    engine.Execute($"__tests[{index}].fn();");
    passed++;
  }
  catch (Exception ex)
  {
    failures.Add($"{name}：{ex.Message.Split('\n')[0]}");
  }
}
Console.WriteLine($"測試：{total} 支，通過 {passed}，失敗 {failures.Count}");
foreach (var failure in failures.Take(12)) Console.WriteLine($"  ✗ {failure}");
return failures.Count == 0 ? 0 : 1;
```

### F.3 `NodeHostProbe/prelude.js`（Node 內建替身；對位附錄 B 之前導碼）

```javascript
// Phase 245 PostResearch 附錄 F 之 .NET/Jint 分支實測：Jint 專用之 CommonJS ＋ Node 內建替身。
// 與 Swift 版（NodeHost.swift）同構，只在兩個宿主 API 上落到 C#：
//   __readFile(path) / __fileExists(path) / __evalExpr(code)
var __tests = [];
var __modules = {};

function __basename(p) { var i = p.lastIndexOf('/'); return i < 0 ? p : p.slice(i + 1); }
function __dirname(p) { var i = p.lastIndexOf('/'); return i <= 0 ? '/' : p.slice(0, i); }
function __pathJoin(dir, rel) {
  var base = rel.charAt(0) === '/' ? '' : dir;
  var parts = (base + '/' + rel).split('/');
  var out = [];
  for (var i = 0; i < parts.length; i++) {
    var piece = parts[i];
    if (piece === '' || piece === '.') continue;
    if (piece === '..') { out.pop(); continue; }
    out.push(piece);
  }
  return '/' + out.join('/');
}

function __deepEqual(a, b) {
  if (a === b) return true;
  if (typeof a !== typeof b) return false;
  if (a === null || b === null) return false;
  if (typeof a !== 'object') return false;
  var aArray = Object.prototype.toString.call(a) === '[object Array]';
  var bArray = Object.prototype.toString.call(b) === '[object Array]';
  if (aArray !== bArray) return false;
  if (aArray) {
    if (a.length !== b.length) return false;
    for (var i = 0; i < a.length; i++) { if (!__deepEqual(a[i], b[i])) return false; }
    return true;
  }
  var keysA = Object.keys(a), keysB = Object.keys(b);
  if (keysA.length !== keysB.length) return false;
  for (var j = 0; j < keysA.length; j++) {
    var key = keysA[j];
    if (!Object.prototype.hasOwnProperty.call(b, key)) return false;
    if (!__deepEqual(a[key], b[key])) return false;
  }
  return true;
}
function __assert(ok, message, operatorName) {
  if (!ok) throw new Error((message || ('assertion failed: ' + operatorName)) + ' [' + operatorName + ']');
}

var __assertModule = {
  ok: function (value, message) { __assert(!!value, message, 'ok'); },
  strictEqual: function (actual, expected, message) {
    __assert(actual === expected, message || ('strictEqual: ' + String(actual) + ' !== ' + String(expected)), 'strictEqual');
  },
  notStrictEqual: function (actual, expected, message) {
    __assert(actual !== expected, message || ('notStrictEqual: ' + String(actual) + ' === ' + String(expected)), 'notStrictEqual');
  },
  deepStrictEqual: function (actual, expected, message) {
    __assert(__deepEqual(actual, expected), message || 'deepStrictEqual failed', 'deepStrictEqual');
  },
  equal: function (actual, expected, message) { __assertModule.strictEqual(actual, expected, message); },
  throws: function (fn, message) {
    var threw = false;
    try { fn(); } catch (e) { threw = true; }
    __assert(threw, message || 'throws: 未拋出', 'throws');
  },
};

var __testModule = function test(name, fn) { __tests.push({ name: name, fn: fn }); };
__testModule.test = __testModule;
__testModule.describe = function (name, fn) { fn(); };
__testModule.it = __testModule;

var __builtin = {
  'node:fs': {
    readFileSync: function (path) { var t = __readFile(path); if (t === null) throw new Error('ENOENT: ' + path); return t; },
    existsSync: function (path) { return __fileExists(path); },
  },
  'node:path': { join: function () {
    var out = '';
    for (var i = 0; i < arguments.length; i++) {
      var piece = String(arguments[i]);
      if (piece === '') continue;
      if (out === '') { out = piece; continue; }
      var last = out.charAt(out.length - 1), first = piece.charAt(0);
      if (last === '/' && first === '/') { out = out + piece.slice(1); continue; }
      if (last === '/' || first === '/') { out = out + piece; continue; }
      out = out + '/' + piece;
    }
    return out;
  } },
  'node:vm': { runInThisContext: function (code, options) {
    __evalExpr(code, (options && options.filename) || 'eval.js');
    return undefined;
  } },
  'node:assert': __assertModule,
  'node:test': __testModule,
};
__builtin['fs'] = __builtin['node:fs'];
__builtin['path'] = __builtin['node:path'];
__builtin['vm'] = __builtin['node:vm'];
__builtin['assert'] = __builtin['node:assert'];
__builtin['test'] = __builtin['node:test'];

function __require(dir, id) {
  if (Object.prototype.hasOwnProperty.call(__builtin, id)) return __builtin[id];
  if (id.charAt(0) !== '.' && id.charAt(0) !== '/') throw new Error('未知之模組：' + id);
  var resolved = __pathJoin(dir, id);
  if (!/\.js$/.test(resolved)) resolved = resolved + '.js';
  if (Object.prototype.hasOwnProperty.call(__modules, resolved)) return __modules[resolved].exports;
  var source = __readFile(resolved);
  if (source === null) throw new Error('找不到模組：' + resolved);
  var module = { exports: {} };
  __modules[resolved] = module;
  var moduleDir = __dirname(resolved);
  var wrapper = __evalExpr(
    '(function (exports, require, module, __filename, __dirname) {\n' + source + '\n})',
    resolved
  );
  var localRequire = function (childId) { return __require(moduleDir, childId); };
  wrapper(module.exports, localRequire, module, resolved, moduleDir);
  return module.exports;
}

// 由 C# 呼叫：把一份測試檔當模組載入（source 以 __sourceText 傳入，免跳脫問題）。
function __loadModuleSource(dir, fullPath, source) {
  var module = { exports: {} };
  __modules[fullPath] = module;
  var wrapper = __evalExpr(
    '(function (exports, require, module, __filename, __dirname) {\n' + source + '\n})',
    fullPath
  );
  var localRequire = function (id) { return __require(dir, id); };
  wrapper(module.exports, localRequire, module, fullPath, dir);
  return module.exports;
}
```

### F.4 `JintProbe/Program.cs`（fixture 探針；產出 §2.9 之 5／5）

驅動情境之 JS 為 `tmp/dotnet-probe/driver.js`（82 行），其五個情境之 `name`／`title`／
`description`／`profile`／`manualAnswers`／`fillAllPages`／`starter` 逐項照抄
`tools/fixtures.mjs` 之 `SCENARIOS`——與附錄 B 之 `PoC.swift` 同源，故此處不重複列出。

```csharp
// (c) 2026 and onwards The vChewing Project (MulanPSL-2.0 License).
// ====================
// This code is released under the SPDX-License-Identifier: `MulanPSL-2.0`.
// Phase 245 PostResearch 之 .NET／Jint 分支實測：以 Jint 載入助手之真實 dist/core.js，
// 重現五份契約 fixture 並與入庫版逐位元組比對。
//
// 用法：dotnet run -- <WebConfigAssistant 之絕對路徑>

using System.Text.Json;
using Jint;

var root = args.Length > 0 ? args[0] : ".";
var corePath = Path.Combine(root, "dist", "core.js");
var driverPath = Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "driver.js");
if (!File.Exists(driverPath)) driverPath = Path.Combine(root, "..", "..", "..", "tmp", "dotnet-probe", "driver.js");

var coreSource = File.ReadAllText(corePath);
var driverSource = File.ReadAllText(driverPath);

var engine = new Engine(options => options.LimitRecursion(256));

var loadClock = System.Diagnostics.Stopwatch.StartNew();
engine.Execute(coreSource);
loadClock.Stop();
Console.WriteLine($"core.js 載入 Jint 完畢：{loadClock.Elapsed.TotalMilliseconds:F1} ms");
Console.WriteLine("引擎：Jint（純受控碼 JS 解譯器，非瀏覽器級引擎）");

string json;
try
{
  json = engine.Evaluate(driverSource).AsString();
}
catch (Exception ex)
{
  Console.Error.WriteLine($"Jint 求值失敗：{ex.GetType().Name}: {ex.Message}");
  return 2;
}

using var document = JsonDocument.Parse(json);
var identical = 0;
var total = 0;
foreach (var item in document.RootElement.EnumerateArray())
{
  total++;
  var name = item.GetProperty("name").GetString()!;
  var produced = item.GetProperty("json").GetString()!;
  var committed = File.ReadAllText(Path.Combine(root, "tests", "fixtures", name + ".json"));
  var parsed = JsonDocument.Parse(produced);
  var count = parsed.RootElement.EnumerateObject().Count() - 1;
  var same = produced == committed;
  if (same) identical++;
  Console.WriteLine($"  {name}.json：{(same ? "位元組相同" : "**相異**")}（{count} 項，{System.Text.Encoding.UTF8.GetByteCount(produced)} 位元組）");
}
Console.WriteLine($"五份 fixture 中，位元組相同者：{identical}/{total}");
return identical == total ? 0 : 1;
```


---

## 附錄 G：Go 側 PoC 原始碼（goja 之 Node 替身）

**性質宣告**：與附錄 B／F 同——**一次性 PoC**，用意是**量測可行性**，非生產碼。
三支檔案皆在 `tmp/go-probe/`（未入庫）。**關鍵一點**：`hostprobe` **原樣重用**了附錄 F 之
`prelude.js`（Node 內建替身）與 `driver.js`（fixture 情境驅動），故 Go 側只需提供三個宿主 API
（`__readFile`／`__fileExists`／`__evalExpr`）——**同一份 JS 前導碼在 Swift（附錄 B）、
.NET（附錄 F）、Go（附錄 G）三案中一字未改地共用**，此即「宿主可換、受測物不動」之實證。

### G.1 `go.mod`（量測當時）

```text
module vca-go-probe

go 1.25.0

require (
	github.com/dlclark/regexp2/v2 v2.5.2 // indirect
	github.com/dop251/goja v0.0.0-20260917113740-793a2a65c13b // indirect
	github.com/go-sourcemap/sourcemap v2.1.3+incompatible // indirect
	github.com/google/pprof v0.0.0-20230207041349-798e818bf904 // indirect
	golang.org/x/text v0.3.8 // indirect
)
```

### G.2 `fixprobe/main.go`（fixture 探針；產出 §7.6 之 5／5）

```go
// (c) 2026 and onwards The vChewing Project (MulanPSL-2.0 License).
// ====================
// This code is released under the SPDX-License-Identifier: `MulanPSL-2.0`.
// Phase 245 PostResearch 附錄 G 之 Go/goja 分支實測（一）：以 goja 載入助手之真實 dist/core.js，
// 重現五份契約 fixture 並與入庫版逐位元組比對。
//
// 用法：go run ./fixprobe <WebConfigAssistant 之絕對路徑> <driver.js 之路徑>

package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/dop251/goja"
)

type produced struct {
	Name string `json:"name"`
	JSON string `json:"json"`
}

func main() {
	root := os.Args[1]
	driverPath := os.Args[2]

	coreSource, err := os.ReadFile(filepath.Join(root, "dist", "core.js"))
	if err != nil {
		fmt.Fprintln(os.Stderr, "讀取 core.js 失敗：", err)
		os.Exit(2)
	}
	driverSource, err := os.ReadFile(driverPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, "讀取 driver.js 失敗：", err)
		os.Exit(2)
	}

	vm := goja.New()

	start := time.Now()
	if _, err := vm.RunScript("core.js", string(coreSource)); err != nil {
		fmt.Fprintln(os.Stderr, "core.js 求值失敗：", err)
		os.Exit(2)
	}
	fmt.Printf("core.js 載入 goja 完畢：%.1f ms\n", float64(time.Since(start).Microseconds())/1000.0)
	fmt.Println("引擎：goja（純 Go 之 ECMAScript 實作，非瀏覽器級引擎）")

	value, err := vm.RunScript("driver.js", string(driverSource))
	if err != nil {
		fmt.Fprintln(os.Stderr, "driver 求值失敗：", err)
		os.Exit(2)
	}

	var items []produced
	if err := json.Unmarshal([]byte(value.String()), &items); err != nil {
		fmt.Fprintln(os.Stderr, "driver 之輸出非合法 JSON：", err)
		os.Exit(2)
	}

	identical := 0
	for _, item := range items {
		committed, err := os.ReadFile(filepath.Join(root, "tests", "fixtures", item.Name+".json"))
		if err != nil {
			fmt.Fprintln(os.Stderr, "讀取入庫 fixture 失敗：", err)
			os.Exit(2)
		}
		var parsed map[string]any
		_ = json.Unmarshal([]byte(item.JSON), &parsed)
		verdict := "**相異**"
		if item.JSON == string(committed) {
			verdict = "位元組相同"
			identical++
		}
		fmt.Printf("  %s.json：%s（%d 項，%d 位元組）\n",
			item.Name, verdict, len(parsed)-1, len(item.JSON))
	}
	fmt.Printf("五份 fixture 中，位元組相同者：%d/%d\n", identical, len(items))
	if identical != len(items) {
		os.Exit(1)
	}
}
```

### G.3 `hostprobe/main.go`（宿主；產出 §7.6 之 78／78）

```go
// (c) 2026 and onwards The vChewing Project (MulanPSL-2.0 License).
// ====================
// This code is released under the SPDX-License-Identifier: `MulanPSL-2.0`.
// Phase 245 PostResearch 附錄 G 之 Go/goja 分支實測（二）：
// 以 goja 執行**一字未改**之既有 tests/*.test.js（含 DOM 冒煙測試）。
// 以 .NET 版之 prelude.js 原樣重用——故本檔只需提供三個宿主 API。
//
// 用法：go run ./hostprobe <WebConfigAssistant 之絕對路徑> <prelude.js 之路徑> <相對於該路徑之測試檔>...

package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/dop251/goja"
)

func main() {
	root := os.Args[1]
	preludePath := os.Args[2]
	testFiles := os.Args[3:]

	vm := goja.New()

	// 三個宿主 API：檔案讀取、存在性、於同一全域求值。
	_ = vm.Set("__readFile", func(call goja.FunctionCall) goja.Value {
		path := call.Argument(0).String()
		data, err := os.ReadFile(path)
		if err != nil {
			return goja.Null()
		}
		return vm.ToValue(string(data))
	})
	_ = vm.Set("__fileExists", func(call goja.FunctionCall) goja.Value {
		_, err := os.Stat(call.Argument(0).String())
		return vm.ToValue(err == nil)
	})
	_ = vm.Set("__evalExpr", func(call goja.FunctionCall) goja.Value {
		value, err := vm.RunScript(call.Argument(1).String(), call.Argument(0).String())
		if err != nil {
			panic(vm.ToValue(err.Error()))
		}
		return value
	})

	prelude, err := os.ReadFile(preludePath)
	if err != nil {
		fmt.Fprintln(os.Stderr, "讀取 prelude.js 失敗：", err)
		os.Exit(2)
	}
	if _, err := vm.RunScript("prelude.js", string(prelude)); err != nil {
		fmt.Fprintln(os.Stderr, "前導碼求值失敗：", err)
		os.Exit(2)
	}

	clock := time.Now()
	for _, file := range testFiles {
		full := filepath.Join(root, file)
		source, err := os.ReadFile(full)
		if err != nil {
			fmt.Fprintln(os.Stderr, "讀取測試檔失敗：", err)
			os.Exit(2)
		}
		dir := filepath.ToSlash(filepath.Dir(full))
		_ = vm.Set("__sourceText", string(source))
		call := fmt.Sprintf("__loadModuleSource(%s, %s, __sourceText);", quote(dir), quote(full))
		if _, err := vm.RunScript(filepath.Base(full), call); err != nil {
			fmt.Fprintf(os.Stderr, "模組載入失敗 %s：%v\n", filepath.Base(full), err)
		}
	}
	fmt.Printf("模組載入：%.1f ms\n", float64(time.Since(clock).Microseconds())/1000.0)

	lengthValue, err := vm.RunString("__tests.length")
	if err != nil {
		fmt.Fprintln(os.Stderr, "讀取 __tests.length 失敗：", err)
		os.Exit(2)
	}
	total := int(lengthValue.ToInteger())
	passed := 0
	var failures []string
	for index := 0; index < total; index++ {
		nameValue, _ := vm.RunString(fmt.Sprintf("__tests[%d].name", index))
		name := nameValue.String()
		if _, err := vm.RunString(fmt.Sprintf("__tests[%d].fn();", index)); err != nil {
			message := err.Error()
			if cut := strings.IndexByte(message, '\n'); cut >= 0 {
				message = message[:cut]
			}
			failures = append(failures, fmt.Sprintf("%s：%s", name, message))
			continue
		}
		passed++
	}
	fmt.Printf("測試：%d 支，通過 %d，失敗 %d\n", total, passed, len(failures))
	for index, failure := range failures {
		if index >= 12 {
			break
		}
		fmt.Printf("  ✗ %s\n", failure)
	}
	if len(failures) != 0 {
		os.Exit(1)
	}
}

// quote 以 Go 之 %q 產生 JS 字串字面量（與 .NET 版之 JsonSerializer.Serialize 對位）。
func quote(text string) string {
	return fmt.Sprintf("%q", text)
}
```


---

## 附錄 H：MoonBit 側 PoC 原始碼（QuickJS 之 Node 替身）

**性質宣告**：與附錄 B／F／G 同——**一次性 PoC**，用意是**量測可行性**，非生產碼。
兩支檔案在 `tmp/moon-probe/`（未入庫；`moon new` 所生之其餘範本檔從略）。

**關鍵差異（與前三案）**：本案之宿主**不提供任何 JS 可呼叫之原生函式**（綁定無此 API），
故 `tests-pure.js` **完全不呼叫宿主**——檔案內容由 MoonBit 以 `new_string` ＋ `set_property`
**物化**為 `__fileMap`，而「於同一全域求值」以**間接 `eval`**（`(0, eval)(code)`）在純 JS 內完成。
宿主與受測物之間因此只剩**兩個能力**：eval 字串、設定物件屬性。

### H.1 `moon.mod`（相依宣告）

```text
name = "vca/moonprobe"

version = "0.1.0"

import {
  "justjavac/quickjs@0.1.5",
  "moonbitlang/x@0.5.5",
}
```

### H.2 `cmd/main/moon.pkg`

```text
import {
  "justjavac/quickjs",
  "moonbitlang/x/fs",
}

supported_targets = "+native"

pkgtype(kind: "executable")
```

### H.3 `cmd/main/main.mbt`（宿主；產出 §7.7 之 5／5 與 78／78）

```moonbit
// (c) 2026 and onwards The vChewing Project (MulanPSL-2.0 License).
// ====================
// This code is released under the SPDX-License-Identifier: `MulanPSL-2.0`.
///|
/// Phase 245 PostResearch 附錄 H 之 MoonBit 分支實測（二）：
/// 以 **無宿主回呼** 之設計，跑完**一字未改**之既有 78 支測試。
///
/// 宿主只做兩件事：① 把檔案內容以 `new_string` ＋ `set_property` 物化為 JS 物件；
/// ② 把前導碼 `tests-pure.js` eval 進去。其後之模組載入與測試執行全在 JS 內完成
/// （模組載入以 `__loadTestFile(path)` 觸發，測試逐支以 `__tests[i].fn()` 觸發）。

fn main {
  let root = "/Users/shikisuen/Repos/_vChewing/_MainWorkspace/vChewing-macOS/ValueAdd/WebConfigAssistant"
  let here = "/Users/shikisuen/Repos/_vChewing/_MainWorkspace/tmp/moon-probe"

  let files : Array[String] = [
    root + "/dist/core.js",
    root + "/dist/app.js",
    root + "/assets/userdef-metadata.json",
    root + "/tests/core-loader.js",
    root + "/tests/dom-shim.js",
    root + "/assets/assistant.css",
    root + "/assets/settings-surface.json",
    root + "/dist/index.html",
    root + "/version.txt",
  ]
  let test_files : Array[String] = [
    root + "/tests/questions.test.js",
    root + "/tests/i18n.test.js",
    root + "/tests/preset.test.js",
    root + "/tests/metadata.test.js",
    root + "/tests/dom-smoke.test.js",
  ]

  let runtime = @quickjs.Runtime::new()
  defer runtime.destroy()
  let context = runtime.new_context()
  defer context.destroy()

  // ① 物化檔案（不經字串轉義：以 new_string 直接造 JS 字串）
  let map = context.new_object()
  for path in files {
    let content = try! @fs.read_file_to_string(path)
    let _ = map.set_property(context, path, context.new_string(content))
  }
  for path in test_files {
    let content = try! @fs.read_file_to_string(path)
    let _ = map.set_property(context, path, context.new_string(content))
  }
  let global = context.global_object()
  let _ = global.set_property(context, "__fileMap", map)

  // ② 前導碼
  let prelude_path = here + "/tests-pure.js"
  let prelude = try! @fs.read_file_to_string(prelude_path)
  let loaded = context.eval(prelude)
  if loaded.is_exception() {
    println("前導碼失敗：\{context.exception_message()}")
    loaded.destroy()
    return
  }
  loaded.destroy()

  // ③ 載入五支測試檔
  for path in test_files {
    let result = context.eval("__loadTestFile(\"" + path + "\")")
    if result.is_exception() {
      println("模組載入失敗 \{path}：\{context.exception_message()}")
    }
    result.destroy()
  }

  // ④ 逐支執行
  let total_value = context.eval("__tests.length")
  let total = context.to_int32(total_value)
  total_value.destroy()
  let mut passed = 0
  let failures : Array[String] = []
  for index = 0; index < total; index = index + 1 {
    let name_value = context.eval("__tests[" + index.to_string() + "].name")
    let name = context.to_string_lossy(name_value)
    name_value.destroy()
    let outcome = context.eval("__tests[" + index.to_string() + "].fn();")
    if outcome.is_exception() {
      let message = context.exception_message()
      outcome.destroy()
      failures.push(name + "：" + message)
    } else {
      outcome.destroy()
      passed = passed + 1
    }
  }
  println("測試：\{total} 支，通過 \{passed}，失敗 \{failures.length()}")
  for failure in failures {
    println("  ✗ \{failure}")
  }
}
```

### H.4 `tests-pure.js`（**無宿主回呼**之 Node 替身；產出 §7.7 之 78／78）

```javascript
// Phase 245 PostResearch 附錄 H 之 MoonBit 分支實測：**無宿主回呼**之 Node 替身。
//
// 何以需要此變體：MoonBit 之 `justjavac/quickjs` 綁定只提供 eval／parse_json／
// new_*／to_*／get_property／set_property，**沒有**把原生函式註冊進 JS 的 API。
// 故 Swift／.NET／Go 三案所用的「宿主提供 __readFile／__evalExpr」寫法在此不可行。
//
// 替代設計（本檔即其實證）：把宿主之兩項能力降到最低——
//   ① 檔案內容由宿主以 new_string ＋ set_property 預先物化為一個 JS 物件（無字串轉義問題）；
//   ② 「於同一全域求值」以**間接 eval**（`(0, eval)(code)`）在純 JS 內完成。
// 如此一來，凡能 eval 字串並設定物件屬性之宿主皆可驅動本替身——不限於本引擎。

var __fileMap = globalThis.__fileMap || {};

function __has(object, key) { return Object.prototype.hasOwnProperty.call(object, key); }
function __readFile(path) { return __has(__fileMap, path) ? __fileMap[path] : null; }
function __fileExists(path) { return __has(__fileMap, path); }
// 間接 eval：依規格即「於全域範疇求值」，與 node 之 vm.runInThisContext 對位。
function __evalExpr(code, name) { return (0, eval)(code); }

function __dirnameOf(path) {
  var index = path.lastIndexOf('/');
  return index <= 0 ? '/' : path.slice(0, index);
}
function __pathJoin(dir, rel) {
  var base = rel.charAt(0) === '/' ? '' : dir;
  var parts = (base + '/' + rel).split('/');
  var out = [];
  for (var i = 0; i < parts.length; i++) {
    var piece = parts[i];
    if (piece === '' || piece === '.') continue;
    if (piece === '..') { out.pop(); continue; }
    out.push(piece);
  }
  return '/' + out.join('/');
}

function __deepEqual(a, b) {
  if (a === b) return true;
  if (typeof a !== typeof b) return false;
  if (a === null || b === null) return false;
  if (typeof a !== 'object') return false;
  var aArray = Object.prototype.toString.call(a) === '[object Array]';
  var bArray = Object.prototype.toString.call(b) === '[object Array]';
  if (aArray !== bArray) return false;
  if (aArray) {
    if (a.length !== b.length) return false;
    for (var i = 0; i < a.length; i++) { if (!__deepEqual(a[i], b[i])) return false; }
    return true;
  }
  var keysA = Object.keys(a), keysB = Object.keys(b);
  if (keysA.length !== keysB.length) return false;
  for (var j = 0; j < keysA.length; j++) {
    var key = keysA[j];
    if (!__has(b, key)) return false;
    if (!__deepEqual(a[key], b[key])) return false;
  }
  return true;
}
function __assert(ok, message, operatorName) {
  if (!ok) throw new Error((message || ('assertion failed: ' + operatorName)) + ' [' + operatorName + ']');
}

// 注意：node 之 path.join **會正規化** `.` 與 `..`。四案之中，Swift／.NET／Go 三案的
// 宿主把路徑交給**作業系統**去解析，故先前之簡化版（只串接）不顯問題；本案之檔案在
// 記憶體內之 map 中、無 OS 可代勞，故必須自行正規化——此為「宿主換成記憶體 map」時
// 唯一真正的語意陷阱，如實記之。
var __pathModule = {
  join: function () {
    var pieces = [];
    for (var i = 0; i < arguments.length; i++) {
      var piece = String(arguments[i]);
      if (piece === '') continue;
      pieces.push(piece);
    }
    var joined = pieces.join('/');
    var absolute = joined.charAt(0) === '/';
    var segments = joined.split('/');
    var out = [];
    for (var j = 0; j < segments.length; j++) {
      var segment = segments[j];
      if (segment === '' || segment === '.') continue;
      if (segment === '..') { if (out.length > 0) out.pop(); continue; }
      out.push(segment);
    }
    return (absolute ? '/' : '') + out.join('/');
  },
};
var __assertModule = {
  ok: function (value, message) { __assert(!!value, message, 'ok'); },
  strictEqual: function (actual, expected, message) {
    __assert(actual === expected, message || ('strictEqual: ' + String(actual) + ' !== ' + String(expected)), 'strictEqual');
  },
  notStrictEqual: function (actual, expected, message) {
    __assert(actual !== expected, message || ('notStrictEqual: ' + String(actual) + ' === ' + String(expected)), 'notStrictEqual');
  },
  deepStrictEqual: function (actual, expected, message) {
    __assert(__deepEqual(actual, expected), message || 'deepStrictEqual failed', 'deepStrictEqual');
  },
  equal: function (actual, expected, message) { __assertModule.strictEqual(actual, expected, message); },
  throws: function (fn, message) {
    var threw = false;
    try { fn(); } catch (e) { threw = true; }
    __assert(threw, message || 'throws: 未拋出', 'throws');
  },
};
var __tests = [];
var __testModule = function test(name, fn) { __tests.push({ name: name, fn: fn }); };
__testModule.test = __testModule;
__testModule.describe = function (name, fn) { fn(); };
__testModule.it = __testModule;

var __builtin = {
  'node:fs': {
    readFileSync: function (path) {
      var text = __readFile(path);
      if (text === null) throw new Error('ENOENT: ' + path);
      return text;
    },
    existsSync: function (path) { return __fileExists(path); },
  },
  'node:path': __pathModule,
  'node:vm': { runInThisContext: function (code, options) { __evalExpr(code, (options && options.filename) || 'eval.js'); return undefined; } },
  'node:assert': __assertModule,
  'node:test': __testModule,
};
__builtin['fs'] = __builtin['node:fs'];
__builtin['path'] = __builtin['node:path'];
__builtin['vm'] = __builtin['node:vm'];
__builtin['assert'] = __builtin['node:assert'];
__builtin['test'] = __builtin['node:test'];

var __modules = {};
function __require(dir, id) {
  if (__has(__builtin, id)) return __builtin[id];
  if (id.charAt(0) !== '.' && id.charAt(0) !== '/') throw new Error('未知之模組：' + id);
  var resolved = __pathJoin(dir, id);
  if (!/\.js$/.test(resolved)) resolved = resolved + '.js';
  if (__has(__modules, resolved)) return __modules[resolved].exports;
  var source = __readFile(resolved);
  if (source === null) throw new Error('找不到模組：' + resolved);
  var module = { exports: {} };
  __modules[resolved] = module;
  var moduleDir = __dirnameOf(resolved);
  var wrapper = __evalExpr(
    '(function (exports, require, module, __filename, __dirname) {\n' + source + '\n})',
    resolved
  );
  var localRequire = function (childId) { return __require(moduleDir, childId); };
  wrapper(module.exports, localRequire, module, resolved, moduleDir);
  return module.exports;
}

/// 載入一份測試檔（內容已在 __fileMap 內，故只需路徑）。
function __loadTestFile(fullPath) {
  var dir = __dirnameOf(fullPath);
  var source = __readFile(fullPath);
  if (source === null) throw new Error('找不到測試檔：' + fullPath);
  var module = { exports: {} };
  __modules[fullPath] = module;
  var wrapper = __evalExpr(
    '(function (exports, require, module, __filename, __dirname) {\n' + source + '\n})',
    fullPath
  );
  var localRequire = function (childId) { return __require(dir, childId); };
  wrapper(module.exports, localRequire, module, fullPath, dir);
  return module.exports;
}
```


---

## 附錄 I：庚案之 PoC（macOS 內建 `jsc` 為宿主）

**性質宣告**：與附錄 B／F／G／H 同——**一次性 PoC**，量測可行性用。檔案在 `tmp/jsc-probe/`（未入庫）。

**作法**：把附錄 H 之 `tests-pure.js`（**無宿主回呼**之 Node 替身）**原樣重用**，僅換掉檔首六行——
把「宿主物化之 `__fileMap`」換成 **jsc 內建之 `readFile`**：

```javascript
// jsc 版：直接以 macOS 內建 JavaScriptCore shell 之 readFile／writeFile 供檔，
// 故連「宿主物化檔案」這一步都不必——本檔即為完整宿主。
function __has(object, key) { return Object.prototype.hasOwnProperty.call(object, key); }
function __readFile(path) { try { return readFile(path); } catch (e) { return null; } }
function __fileExists(path) { try { readFile(path); return true; } catch (e) { return false; } }
```

其後接上附錄 H 之其餘部分，再加上一段驅動：

```javascript
var testFiles = [
  "<WebConfigAssistant>/tests/questions.test.js",
  "<WebConfigAssistant>/tests/i18n.test.js",
  "<WebConfigAssistant>/tests/preset.test.js",
  "<WebConfigAssistant>/tests/metadata.test.js",
  "<WebConfigAssistant>/tests/dom-smoke.test.js",
];
for (var i = 0; i < testFiles.length; i++) {
  try { __loadTestFile(testFiles[i]); }
  catch (e) { print("模組載入失敗 " + testFiles[i] + "：" + e); }
}

var passed = 0, failures = [];
for (var k = 0; k < __tests.length; k++) {
  try { __tests[k].fn(); passed++; }
  catch (e) { failures.push(__tests[k].name + "：" + String(e).split("\n")[0]); }
}
print("測試：" + __tests.length + " 支，通過 " + passed + "，失敗 " + failures.length);
```

**執行**：

```bash
JSC=/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc
"$JSC" tmp/jsc-probe/run.js
# → 模組載入：5 ms
#   測試：78 支，通過 78，失敗 0
#   real 0m0.138s
```

**此事之意義**：附錄 H 為 MoonBit 而發明之「無宿主回呼」設計（宿主只提供 eval 與屬性設定），
在此**直接適用於 macOS 內建之 shell**——**同一份 JS 前導碼，四個宿主（Swift／.NET／Go／MoonBit）、
一個系統 shell（jsc），受測物皆一字未改**。宿主介面之抽象因此收斂到極簡。
