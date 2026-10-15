<!-- 本檔為 vChewing-DevLogs/KnowledgeMemo4LLM.md 之分卷；索引：../KnowledgeMemo4LLM.md
     開工前請先讀索引，再依〈三、任務→必讀分卷〉取用本檔。 -->

# 二、專案架構

### 2.1 目錄結構

```
vChewing-LibVanguard/
├── Package.swift                    # SPM 套件定義（package name: LibVanguard, 出貨 product: Vanguard）
├── makefile                         # lint / format / test / dockertest 指令
├── EVOLUTION_MEMO.md                # 各模組研發備忘錄
├── README.md                        # 專案說明（含〈What Is In This Repository〉）
├── COPYING / LICENSES/              # 授權（LGPL-3.0-or-later；SwiftExtension 與 ResourceLocator 例外為 MulanPSL-2.0）
├── .github/workflows/               # CI：test_ubuntu / test_winnt / test_darwin_LibVanguard.yml
├── Sources/
│   ├── LibVanguard/                 # 作業系統中立層：輸入控制器與狀態機（動態產品 Vanguard 之聚合目標）
│   ├── LexiconAssembly/             # 辭典聚合與洞察（LXFacade / LXQuerier / LXPerceptor）
│   ├── LXAssemblyMaterials4Tests/   # 測試專用辭典素材目標（獨立於出貨動態庫之外）
│   ├── Homa/                        # 護摩組字引擎
│   ├── TrieKit/                     # 辭典樹（RAM Trie + TextMap Trie）
│   ├── Tekkon/                      # 注拼引擎（聲韻並擊）
│   ├── BrailleSputnik/              # 盲文點字轉換
│   ├── BPMFVS/                      # 注音資產與存取器（ButKo BPMFVS）
│   ├── Shared/                      # 全體共用型別與常數
│   ├── SwiftExtension/              # Swift 語言擴展（MulanPSL-2.0）
│   ├── ResourceLocator/             # 執行期資源定位（MulanPSL-2.0）
│   └── vChewingSharedCLI/           # 跨模組共享命令列工具
└── Tests/
    ├── LibVanguardTests/
    ├── LexiconAssemblyTests/        # POM 測試族之大本營
    ├── HomaTests/ + HomaSharedTestComponents/
    ├── TrieKitTests/ / TekkonTests/ / BrailleSputnikTests/ / BPMFVSTests/
    ├── SharedTests/ / SwiftExtensionTests/ / ResourceLocatorTests/
    └── (本倉獨有) LexiconAssemblyTests/POMDecayWindowTests.swift
                 LexiconAssemblyTests/LXPlainBopomofoEtenDOSTests.swift
```

> **2026-09-14（Phase 213）之佈局變更**：本倉原有之 `Sources/LibVanguard/`、`Sources/_Modules/<模組>` 與
> `Tests/_Tests4Components/<模組>Tests`、`Tests/LibVanguardTests/` 已全數退場（73 檔），改為上表之
> **聚合式佈局**——即 `vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard` 的同源複製。該表所列 12 個
> `Sources/` 子目錄與 10 個測試目標與 macOS 側逐位元組一致，唯二差異為兩處硬編碼資源 bundle 名與本倉
> 獨有的 2 個測試檔。`TrieHub`／`FactoryTrieDBType`／`LexiconHub` 三個殘骸隨舊佈局一併退場。

> **本文件所屬的 `vChewing-DevLogs` 倉庫**：開發記錄已自 LibVanguard 獨立為工作區中的 `vChewing-DevLogs` 倉庫
> （原為 LibVanguard 的 `DevPlans/`，現供整個 vChewing 組織跨倉使用）：
>
> ```
> vChewing-DevLogs/
> ├── KnowledgeMemo4LLM.md               # 本文件
> ├── DevReqsHistory.md                  # 開發階段歷史
> ├── Reqs4LLM/                          # Phase 需求文件（分卷與現行卷之判定見 §12.2）
> ├── Research/                          # 各 Phase 研究報告
> └── PendingFeatureReqs/                # FeatureRequest 類 PreResearch
> ```

### 2.2 技術架構

模組依賴關係（上層依賴下層）：

```
Vanguard (動態產品 / libVanguard.dylib) — 出貨產品之 target 清單共 10 個
└── LibVanguard (聚合目標；唯一的出貨動態庫之根)
    ├── BPMFVS ── ResourceLocator ── SwiftExtension
    ├── BrailleSputnik ── Shared ── SwiftExtension
    ├── LexiconAssembly ── TrieKit ── SwiftExtension
    │                    ├── Homa
    │                    └── Shared
    ├── Homa
    ├── ResourceLocator
    ├── Shared
    ├── SwiftExtension
    └── Tekkon

（出貨產品清單另以逐 target 列出，故上圖之邊即 `Package.swift` 內 `dependencies:` 之實際內容。）
```

**出貨產品（Products）**：`Vanguard`（`.dynamic`，targets 為 `LibVanguard`／`Shared`／`SwiftExtension`／`ResourceLocator`／`LexiconAssembly`／`TrieKit`／`Homa`／`Tekkon`／`BrailleSputnik`／`BPMFVS`）；另有 `LXAssemblyMaterials4Tests` 與 `HomaSharedTestComponents` 兩個**測試素材目標**動態產品（刻意不進出貨庫），以及 `vChewingSharedCLI` executable。

> **2026-09-14（Phase 213）後之模組集合**：本倉已無「公開／內部模組」之分——12 個 `Sources/` 子目錄即 10 個出貨 target ＋ 2 個支援 target（`LXAssemblyMaterials4Tests`、`vChewingSharedCLI`），其中 **`LibVanguard` 同時是唯一聚合目標**（SwiftPM 拒絕讓同一 target 同時被動態與靜態產品取用，故整個閉包只能以單一動態庫出貨）。舊圖（`LibVanguard` 聚合 target ＋ `Sources/_Modules/*` 六模組）已全部退場。

> **已移除模組（2026-09-13，Phase 206）**：`SharedCore`（`KBEvent` / `KeyCode` / `KBEventProtocol`）與 `CandidateKit`（`CandidateCellData`）兩模組已自本倉切除，連同其空殼測試目標。`SharedCore` 內與 FCITX 有關的相容項已遷入 `vChewing-macOS` 與 `vChewing-OSX-Legacy` 兩倉、且於 Phase 206 改掛 MIT-NTL 標頭（惟該二檔皆落在 Phase 207 的授權閉包內，故其標頭已於同日隨閉包換軌回 LGPL-3.0-or-later）；`KBEvent` / `InputSignalProtocol` 在兩倉各有獨立副本，本倉移除不影響其運作。
