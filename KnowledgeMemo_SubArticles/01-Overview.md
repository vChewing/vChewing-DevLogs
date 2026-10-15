<!-- 本檔為 vChewing-DevLogs/KnowledgeMemo4LLM.md 之分卷；索引：../KnowledgeMemo4LLM.md
     開工前請先讀索引，再依〈三、任務→必讀分卷〉取用本檔。 -->

# 一、專案概述

**LibVanguard**（先鋒引擎）是 vChewing Project 下一代輸入法的引擎的核心套件庫，以 Swift Package 形式提供。專案採用 LGPL v3.0 授權（`SwiftExtension` 模組例外：自 2026-09-13 起採 `MulanPSL-2.0`，見 `LICENSES/preferred/MulanPSL-2.0` 與 `COPYING`），涵蓋從注音符號解析、辭典樹查詢、語言模型聚合、到組字引擎的完整輸入法管線（pipeline）。

- **Swift 工具版本**：**Swift 6.4+**（6.2／6.3 為封堵對象——各套件之 `Package@swift-6.2.swift`／`6.3.swift` 以 `#error` 明文拒絕該兩版，理由見 §10.5 末段）；另備 **Swift 5.10.1**（open-source toolchain）供 macOS 10.9 legacy 側建置——自 Phase 216 起本倉具雙 toolchain 建置能力、Phase 217 起**推及 `vChewing-macOS` 全倉**，建置行為隨 toolchain 版本而異（見 §十）。
- **最低平台支援**：現行側 macOS 12（**.macOS(.v12)**）——自 Phase 213 起承襲 `vChewing-macOS` 的 `LibVanguard` 設定（原為 macOS 15 / macCatalyst 18 / iOS 18 / visionOS 2，事主裁定現階段一律承襲 macOS 側；**iOS 側自 P289 起明文宣告 `.iOS(.v27)`**——支援帶 iOS 27+，免去 iOS 18 為止之 non-liquid-glass 鍵盤邊框相容勞力）；**5.10（legacy）側之 manifest 刻意不宣告平台（`platforms: nil`）、部署目標為 `x86_64-apple-macosx10.9`**（PackageDescription 能宣告的 macOS 最低值只有 10.10，一宣告即被明文寫入產物，索性不宣告；地板由 makefile 之 `-Xswiftc -target` 與 legacy 連結端決定。早前記為「`Data` 標為 macOS 10.10 起、故 `10.9` 不存在」——該說已經重測推翻——詳見 §十）。
- **跨平台目標**：保持對 Linux 與 Windows 的可建置性（透過 `#if canImport(Darwin)` 條件編譯平台限制）。
- **出貨產物**：**（6.4+ 側）單一動態庫 `libVanguard.dylib`**（manifest 之 `package.name = "LibVanguard"` 而 product 名為 `Vanguard`）。**聚合目標與其測試目標自 2026-09-14 第二輪起亦更名**為 `LibVanguard` / `LibVanguardTests`（原 `OSNeutralAssembly` / `OSNeutralAssemblyTests`），故 `import LibVanguard`；其餘模組名（`Homa`、`TrieKit`、`LexiconAssembly` 等）不變。SwiftPM 的資源 bundle 名取**套件名**，故實為 `LibVanguard_*.bundle`。**兩倉（本倉與 `vChewing-macOS`）自此 `Package.swift` 逐位元組相同、`Sources/` 全等**。**（5.10 側，自 Phase 216 起）兩顆均為 static 之產物**：`libVanguard.a`（聚合體，14 MB）與 `libVanguardSwiftExtension.a`（子套件，540 KB）；`.a` 係純 `ar` 封存、不帶任何 load command，故 minOS 不進產物。
- **角色（事主 2026-09-14 定調）**：本倉現為**實驗田**；`vChewing-macOS` 仍消費自己的 `Packages/vChewing_OSNeutral_LibVanguard`，兩者自此是「逐位元組同源、各自獨立」的兩份副本。LibVanguard 對 macOS 的**向前建置能力**屬後續 phase（**自 Phase 216 起開始落地**：5.10／legacy 側之雙 toolchain 建置已可行，見 §10.5）。

> 該專案本身不應視為 vChewing 唯音輸入法的一部分，除非今後刻意有此安排。

---

# 附錄一、開發階段歷史

因該章節過於龐大，故挪至 `vChewing-DevLogs/DevReqsHistory.md` 單獨管理。
