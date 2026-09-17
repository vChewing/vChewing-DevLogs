# vChewing & LibVanguard 工作區 - 格物致知專用文件

- 本文檔供 AI Agent 在每次開工前迅速了解專案全貌。
- **FeatureRequest（FR）目錄註記**：`vChewing-DevLogs/PendingFeatureReqs/` 存放 FeatureRequest 類 PreResearch 文件（現含 `FR608-PreResearch.md`）。該目錄**僅在被要求處理時才處理**——除非事主明確指示，否則不得主動動工、不納入任何 Phase 排程、不預先分析其內容。
- **Reqs4LLM 分卷歸檔註記**：`vChewing-DevLogs/Reqs4LLM/` 之下，分卷以「至多 10 個 Phase」為單位；現行卷為 `vChewing-DevLogs/Reqs4LLM/Archive_P201-P300/Reqs_0221-0230.md`（收 Phase 221~230；同目錄的 `Reqs_0211-0220.md` 已滿、收 Phase 211~220），`vChewing-DevLogs/Reqs4LLM/Reqs_Other_Pending_Phases.md` 為不隨分卷歸檔的待定事項暫存。一卷寫滿、或經事主裁定結案後，即依其 Phase 區間移入 `vChewing-DevLogs/Reqs4LLM/Archive_P{首 Phase 所屬百位段}/`（既有：`Archive_P001-P100/`〔Phase 01~100〕、`Archive_P101-P200/`〔Phase 101~200〕、`Archive_P201-P300/`〔Phase 201~230〕）。**（archive 桶的「凍結」僅指該百位段的 100 個 Phase 已收齊；未滿 100 個 Phase 者只稱「已歸檔」、仍會續收後續結案的分卷——現下的 `Archive_P201-P300/` 即屬此態。）已滿或已結案的歸檔卷不再增改，新 Phase 之記錄一律寫入現行卷；惟對過往 Phase 之補記不在此限——無論該卷是否已歸檔，補記一律補進那個 Phase 自己的記錄內，不得佔用其他 Phase（含現行卷）的記錄空間。** 本文件群內所有路徑一律以**工作區根**為錨（`vChewing-DevLogs/…`、`vChewing-LibVanguard/…`、`vChewing-macOS/…` 等）。
- **授權註記**：本倉庫自身內容以 **LGPL-3.0-or-later** 授權，詳見 `COPYING` 與 `LICENSES/preferred/LGPL-3.0-or-later`。倉內**引用**的程式碼／資料仍依其來源授權、不受本倉庫授權影響（`vChewing-LibVanguard` LGPL-3.0-or-later〔附 Swift 靜態連結例外〕、`vChewing-macOS`／`vChewing-OSX-Legacy`（自 2026-09-13 起，**閉包以外之一切自研內容已換軌為 `MulanPSL-2.0`**，兩倉自此不再有 MIT-NTL；**以 `LibVanguard`（原 `OSNeutralAssembly`）為終末點之 8 個 SPM package 則為 LGPL-3.0-or-later**——`LibVanguard`／`LexiconAssembly`〔內含 `TrieKit`；`TrieKit` 係套件與 target 名，與本倉 `Sources/` 的 `LX_` 檔名前綴無關〕／`Homa`／`Shared`／`Tekkon`／`BrailleSputnik`／`BPMFVS`／`SwiftExtension`〔惟 `SwiftExtension` 為 `MulanPSL-2.0`〕；其遞移相依閉包以外者一律為 `MulanPSL-2.0`）、`vChewing-VanguardLexicon` `MulanPSL-2.0`、`vChewing-Homebrew` AGPL-3.0，另有 Megrez／ButKo BPMFVS／KeyKey／McBopomofo 等第三方片段）。清單見 `README.md`。
- 最後更新：2026-09-18 // 這一行只寫日期，不用贅述 DevReqHistory 裡面的那種記載格式。
- AI Agent 得特別注意本文所提到的「Response Pattern」。
- **倉庫現狀（2026-09-17，vChewing **4.8.0** 發版）**：`vChewing-OSX-Legacy`（Aqua 紀念版）**已封存、不再更新**——legacy 發行版（支援自 macOS 10.9 起）之建置自此**唯由 `vChewing-macOS` 之 legacy targets 承擔**（`debugLegacy`／`releaseLegacy`／`archiveLegacy`／`cleanLegacy`，見 §10.5.2）。封存倉**仍保留為 10.9-compliant 的 API 寫法參照**（AppKit availability 有疑者照它），但**不再接收任何回寫／同步**；本文檔與 `DevReqsHistory.md` 中凡「三倉同步」「legacy 倉逐檔同構」一類記述，一律視為 4.8.0 以前之歷史事實。
- **命名沿革（2026-09-13，Phase 201~204 ＋ 同日第二輪 ＋ Phase 205）**：本文檔在此日期之前的所有條目，所出現的 `Typewriter`／`LangModelAssembly`／`LMAssembly`／`LMInstantiator`／`LMI`／`LMMgr`／`LookupHub`／`lmi`／`lookupHub`／`lm*`（小寫家族）／`LMPlainBPMF`／`LangModel`／`langModel`／`TestLM` 等名稱，係各該階段當時的實際名稱，**依歷史記載原則原樣保留、不予改寫**。更名結果：兩倉（`vChewing-macOS`／`vChewing-OSX-legacy`）的 `OSNeutralAssembly`／`LexiconAssembly`／`LXAssembly`／`LXFacade`／`LXMgr`／`LXQuerier`／`lxQuerier`／`lx*`，對應目錄亦已同步（`Packages/vChewing_OSNeutralAssembly`、`Packages/vChewing_LexiconAssembly`、`Shared/vChewingComponents/OSNeutralAssembly`、`Shared/vChewingComponents/LXAssembly`、`LangModelManager/` → `LXManager/`）；另 `Shared.InputMode.langModel` → `.lexicon`、`LangModelCache` → `LexiconCache`、`resetLangModelCache` → `resetLexiconCache`、`initUserLangModels()` → `initUserLexicons()`、`targetLangModels` → `targetLexicons`，測試靶的 `TestLM` 族 → `TestLX` 族（`mockLM` → `mockLX`、`strLMSampleData*` → `strLXSampleData*` 等）。**本倉**的 `Lexicon.LMPlainBPMF` → `Lexicon.LXPlainBPMF`（檔名 `LX_LXPlainBPMF.swift`）、`lmPlainBPMFData` → `lxPlainBPMFData`、`HomaTests_Basic.swift` 的測試局部變數 `langModel` → `lexicon`。本倉程式碼除此與 3 處文字引用外零改動。詳見 `vChewing-DevLogs/Reqs4LLM/Archive_P201-P300/Reqs_0201-0210.md`。
- **命名沿革（2026-09-14 第二輪，Phase 214）**：`OSNeutralAssembly` → `LibVanguard`（**套件名、module 名、target 名、測試靶名、其目錄名，以及 macOS 的套件目錄名**）。範圍含兩倉（`vChewing-LibVanguard` 與 `vChewing-macOS`）之 import／`@testable import`／`@_exported import`、註解與 doc comment、`UserDefaults` suite 名、macOS 11 個 consumer manifest 的 product 名（改 `Vanguard`）、`plugin.swift` 的 bundle 名排除集、CI 檔名與 job 名、`Makefile` 目標名、以及兩倉的 README／EVOLUTION_MEMO／AGENTS／CLAUDE／algorithm／copilot-instructions／DevLab 散文。**macOS 套件目錄亦一併正名**（事主同日補佈置）：`Packages/vChewing_OSNeutralAssembly` → `Packages/vChewing_OSNeutral_LibVanguard`，故 11 個 consumer manifest 的 `.package(path:)` 與 `.product(…, package: "vChewing_OSNeutral_LibVanguard")`（SwiftPM 對本地路徑相依之 identity 取自目錄名）、3 處 CI `--package-path`、`Makefile` 2 處、`project.pbxproj` 2 處與全部文件路徑同步；但該目錄**內部**的 `Sources/OSNeutralAssembly/`、`Tests/OSNeutralAssemblyTests/` 已改名為 `LibVanguard/`、`LibVanguardTests/`。兩倉 `Package.swift` 自此**逐位元組相同**（並改用 `@resultBuilder` 的 ArrayBuilder DSL），兩倉 `Sources/` 內容**全等**、`Tests/` 僅差本倉獨有的 2 個搶救測檔。另含一項檔名殘端：聚合靶的 umbrella 檔 `OSNeutralAssemblySPM.swift` → `LibVanguardSPM.swift`（兩倉）——檔名不入 manifest，byte-identity 檢查與編譯都不會發現它，須靠「殘留的 `OSNeutralAssembly*` 建置產物」反查。
- **刻意保留、勿於後續命名清剿中更動（事主 2026-09-13 裁定）**：`ButKo_BPMFVS` 這個 **SwiftPM 套件**已更名為 `vChewing_BPMFVS`（macOS `Packages/vChewing_BPMFVS`），但以下一律**不動**——① `ButKo_BPMFVS_Accessors.swift` 檔名（macOS `Sources/BPMFVS/` 與 legacy `Shared/3rdParty/` 各一份；事主明示故意保留，legacy `project.pbxproj` 有 4 處引用）；② legacy `vChewing/Resources/ButKoBPMFVS_Assets/` 目錄（內含 ButKo 上游資產 `phonic_table_Z.txt`／`LICENSE_BPMFVS.txt`，只放第三方資產故不隨套件改名）；③ 使用者可見的**功能名**「ButKo BPMFVS」——含 4 語系 `Localizable.strings` 的 `i18n:UserDef.kReflectBPMFVSInCompositionBuffer.*`／`i18n:UserDef.kSpecifyCmdOptCtrlEnterBehavior.option.4` 文案與官網 `ReleaseNotes.md`／`Downloads.md`／`manual/preferences.md`；④ Swift 端的 `CommitableMarkupType.bpmfvsAnnotationButKo` 與測試函式名 `test_IH103*_ButKoBPMFVS*`。另：`build_darwin_SPMTestsAndPackage.yml` 的 `packages=(...)` **刻意不收** `./Packages/vChewing_BPMFVS`（該 package 有 `Tests/BPMFVSTests`，實測 6/6 通過；事主對該套件另有後續打算）。

---

## 一、專案概述

**LibVanguard**（先鋒引擎）是 vChewing Project 下一代輸入法的引擎的核心套件庫，以 Swift Package 形式提供。專案採用 LGPL v3.0 授權（`SwiftExtension` 模組例外：自 2026-09-13 起採 `MulanPSL-2.0`，見 `LICENSES/preferred/MulanPSL-2.0` 與 `COPYING`），涵蓋從注音符號解析、辭典樹查詢、語言模型聚合、到組字引擎的完整輸入法管線（pipeline）。

- **Swift 工具版本**：**Swift 6.4+**（6.2／6.3 為封堵對象——各套件之 `Package@swift-6.2.swift`／`6.3.swift` 以 `#error` 明文拒絕該兩版，理由見 §10.5 末段）；另備 **Swift 5.10.1**（open-source toolchain）供 macOS 10.9 legacy 側建置——自 Phase 216 起本倉具雙 toolchain 建置能力、Phase 217 起**推及 `vChewing-macOS` 全倉**，建置行為隨 toolchain 版本而異（見 §十）。
- **最低平台支援**：現行側 macOS 12（**.macOS(.v12)**）——自 Phase 213 起承襲 `vChewing-macOS` 的 `LibVanguard` 設定（原為 macOS 15 / macCatalyst 18 / iOS 18 / visionOS 2，事主裁定現階段一律承襲 macOS 側）；**5.10（legacy）側之 manifest 刻意不宣告平台（`platforms: nil`）、部署目標為 `x86_64-apple-macosx10.9`**（PackageDescription 能宣告的 macOS 最低值只有 10.10，一宣告即被明文寫入產物，索性不宣告；地板由 makefile 之 `-Xswiftc -target` 與 legacy 連結端決定。早前記為「`Data` 標為 macOS 10.10 起、故 `10.9` 不存在」——該說已經重測推翻——詳見 §十）。
- **跨平台目標**：保持對 Linux 與 Windows 的可建置性（透過 `#if canImport(Darwin)` 條件編譯平台限制）。
- **出貨產物**：**（6.4+ 側）單一動態庫 `libVanguard.dylib`**（manifest 之 `package.name = "LibVanguard"` 而 product 名為 `Vanguard`）。**聚合靶與其測試靶自 2026-09-14 第二輪起亦更名**為 `LibVanguard` / `LibVanguardTests`（原 `OSNeutralAssembly` / `OSNeutralAssemblyTests`），故 `import LibVanguard`；其餘模組名（`Homa`、`TrieKit`、`LexiconAssembly` 等）不變。SwiftPM 的資源 bundle 名取**套件名**，故實為 `LibVanguard_*.bundle`。**兩倉（本倉與 `vChewing-macOS`）自此 `Package.swift` 逐位元組相同、`Sources/` 全等**。**（5.10 側，自 Phase 216 起）兩顆均為 static 之產物**：`libVanguard.a`（聚合體，14 MB）與 `libVanguardSwiftExtension.a`（子套件，540 KB）；`.a` 係純 `ar` 封存、不帶任何 load command，故 minOS 不進產物。
- **角色（事主 2026-09-14 定調）**：本倉現為**實驗田**；`vChewing-macOS` 仍消費自己的 `Packages/vChewing_OSNeutral_LibVanguard`，兩者自此是「逐位元組同源、各自獨立」的兩份副本。LibVanguard 對 macOS 的**向前建置能力**屬後續 phase（**自 Phase 216 起開始落地**：5.10／legacy 側之雙 toolchain 建置已可行，見 §10.5）。

> 該專案本身不應視為 vChewing 唯音輸入法的一部分，除非今後刻意有此安排。

---

## 二、專案架構

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
│   ├── LibVanguard/                 # 作業系統中立層：輸入控制器與狀態機（動態產品 Vanguard 之聚合靶）
│   ├── LexiconAssembly/             # 辭典聚合與洞察（LXFacade / LXQuerier / LXPerceptor）
│   ├── LXAssemblyMaterials4Tests/   # 測試專用辭典素材靶（獨立於出貨動態庫之外）
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
> `Sources/` 子目錄與 10 個測試靶與 macOS 側逐位元組一致，唯二差異為兩處硬編碼資源 bundle 名與本倉
> 獨有的 2 個測試檔。`TrieHub`／`FactoryTrieDBType`／`LexiconHub` 三個殘骸隨舊佈局一併退場。

> **本文件所屬的 `vChewing-DevLogs` 倉庫**：開發記錄已自 LibVanguard 獨立為工作區中的 `vChewing-DevLogs` 倉庫
> （原為 LibVanguard 的 `DevPlans/`，現供整個 vChewing 組織跨倉使用）：
>
> ```
> vChewing-DevLogs/
> ├── KnowledgeMemo4LLM.md               # 本文件
> ├── DevReqsHistory.md                  # 開發階段歷史
> ├── Reqs4LLM/                          # Phase 需求文件（現行卷見 Archive_P201-P300/）
> ├── Research/                          # 各 Phase 研究報告
> └── PendingFeatureReqs/                # FeatureRequest 類 PreResearch
> ```

### 2.2 技術架構

模組依賴關係（上層依賴下層）：

```
Vanguard (動態產品 / libVanguard.dylib) — 出貨產品之 target 清單共 10 個
└── LibVanguard (聚合靶；唯一的出貨動態庫之根)
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

**出貨產品（Products）**：`Vanguard`（`.dynamic`，targets 為 `LibVanguard`／`Shared`／`SwiftExtension`／`ResourceLocator`／`LexiconAssembly`／`TrieKit`／`Homa`／`Tekkon`／`BrailleSputnik`／`BPMFVS`）；另有 `LXAssemblyMaterials4Tests` 與 `HomaSharedTestComponents` 兩個**測試素材靶**動態產品（刻意不進出貨庫），以及 `vChewingSharedCLI` executable。

> **2026-09-14（Phase 213）後之模組集合**：本倉已無「公開／內部模組」之分——12 個 `Sources/` 子目錄即 10 個出貨 target ＋ 2 個支援 target（`LXAssemblyMaterials4Tests`、`vChewingSharedCLI`），其中 **`LibVanguard` 同時是唯一聚合靶**（SwiftPM 拒絕讓同一 target 同時被動態與靜態產品取用，故整個閉包只能以單一動態庫出貨）。舊圖（`LibVanguard` 聚合 target ＋ `Sources/_Modules/*` 六模組）已全部退場。

> **已移除模組（2026-09-13，Phase 206）**：`SharedCore`（`KBEvent` / `KeyCode` / `KBEventProtocol`）與 `CandidateKit`（`CandidateCellData`）兩模組已自本倉切除，連同其空殼測試靶。`SharedCore` 內與 FCITX 有關的相容項已遷入 `vChewing-macOS` 與 `vChewing-OSX-Legacy` 兩倉、且於 Phase 206 改掛 MIT-NTL 標頭（惟該二檔皆落在 Phase 207 的授權閉包內，故其標頭已於同日隨閉包換軌回 LGPL-3.0-or-later）；`KBEvent` / `InputSignalProtocol` 在兩倉各有獨立副本，本倉移除不影響其運作。

---

## 三、核心資料模型

| 型別 | 模組 | 用途 |
|------|------|------|
| `Homa.Gram` | Homa | 元圖單位（Unigram/Bigram），承載讀音、字詞、機率、前驗詞 |
| `Homa.Node` | Homa | 組字節點，含元圖陣列、覆寫狀態、Bigram 快取 |
| `Homa.Segment` | Homa | 字詞幅節，`[Int: Node]` 字典（鍵為幅節長度） |
| `Homa.Assembler` | Homa | 組字核心處理器，持有遊標、段落、配置、動態規劃演算法 |
| `VanguardTrie.Trie.TNode` | TrieKit | Trie 節點，含 id / readingKey / children / entries |
| `VanguardTrie.Trie.Entry` | TrieKit | Trie 詞條，含 value / typeID / probability / previous |
| `Tekkon.Phonabet` | Tekkon | 單注音符號（Unicode Scalar + PhoneType） |
| `Tekkon.Composer` | Tekkon | 音節合成器，逐字元組合注音 |
| `VanguardTrie.TrieGram` | TrieKit | 元圖資料結構（`keyArray` / `value` / `probability` / `previous` / `anterior`）。原為 5 元 tuple，已改具名 struct。**Phase 213 前**的 LibVanguard `LexiconKit` 曾以 `public typealias HomaGram = VanguardTrie.TrieGram` 引用之，該模組已退場；macOS／LibVanguard 兩倉現以 `Homa.Gram` 為組字引擎的元圖型別，另有 `Homa.Gram.init(_ trieGram:)` 橋接。 |

---

## 四、核心組件詳解

### 4.1 Tekkon — 注拼引擎

負責注音符號與拼音的解析、輸入法鍵盤映射。

- **`Tekkon.Composer`**：音節合成器，接收按鍵輸入並組合出完整的注音音節。
- **`Tekkon.MandarinParser`**：支援 11 種注音排列（大千、ETen、許氏、IBM、星光等）與 6 種拼音風格（漢語拼音、耶魯、韋氏等）。
- **`Tekkon.PinyinTrie`**：簡化版拼音辨析 Trie，用於狂拼輸入的 `chop()` 拆解。
- **轉換 API**：`cnvPhonaToHanyuPinyin`、`cnvHanyuPinyinToPhona` 等注音⇄拼音雙向轉換。

### 4.2 TrieKit — 辭典樹

支援對讀音的多音字首字元檢索配對，分兩種實現：

- **`VanguardTrie.Trie`**（記憶體型）：全 RAM 常駐、無 QueryBuffer。序列化入口僅 **Vanguard Pragma TextMap 格式**一途（見下方說明）；不支援 Plist 序列化。
- **`VanguardTrie.TextMapTrie`**（TextMap 專用型）：Phase 35 定案後，已不再只是「惰性解析版 Trie」，而是 canonical specialized backend。其核心結構為 raw `Data` 常駐、排序後 full-key index、binary search exact lookup、lexicographic prefix-range scan、eager reverse lookup table、bounded parsed-entry cache，以及 partial-match 用的 `keyInitialsIDMap` prefilter。這讓它既維持低穩態記憶體占用，又能在 exact / longer-segment / revlookup 熱路徑上避免舊有通用 node materialization 成本。（Phase 11 曾嘗試 DFD 模式以 `pread()` 取代常駐 Data，但實機測試記憶體反飆升 20~30 MB 而作廢；詳見 Reqs4LLM/Archive_P001-P100/Reqs_0011-0020.md。）Phase 38 起，Typing TextMap 的 `KEY_LINE_MAP` canonical key 已改為 raw phonabet；TextMap caller layer 不得再對該 backend 做額外 encrypt/decrypt。
- **`VanguardTrieProtocol`**：統一查詢介面。核心 surface 為 `getNode(...)`、`getNodes(...)`、`getEntryGroups(...)`；高階 query API（`hasGrams` / `queryGrams` / `queryAssociatedPhrasesAsGrams`）已改以 entry groups 為主要抽象，使 `any VanguardTrieProtocol` existential 仍能命中 TextMapTrie specialized backend。
- **特殊功能**：部分比對（不完全讀音）、多音切割（分隔器 `&` 用於拼音→TrieKit 的多候選搜尋）。
- **三倉全等（Phase 200 收尾；Phase 213 後路徑更新）**：TrieKit 現於 `vChewing-LibVanguard`（`Sources/TrieKit/`）、`vChewing-macOS`（`Packages/vChewing_OSNeutral_LibVanguard/Sources/TrieKit/`）、`vChewing-OSX-legacy`（`Shared/vChewingComponents/LXAssembly/TrieKit/`）逐位元組一致，LibVanguard 的 `TrieKitTests/` 亦與 macOS 相同。兩處**不可清除**的工具鏈限制必須保留：① `TrieProtocol.swift` 的排序比較是手寫 unrolled 條件分支而**非** 5 元 tuple 的 `>`——後者在 legacy 的 Xcode-15／Swift-5 下 type-check 超時（語義已逐元核對等價，含 `seq` 交叉比較怪癖）；② `TK_QueryBuffer.swift` 的 `import SwiftExtension` 包在 `#if canImport(SwiftExtension)` 內，因 legacy 無該模組（其 `NSMutex` 與本檔同模組）。**另：TrieKit 的 5 元 tuple 已改為具名 struct `VanguardTrie.TrieGram`**（欄位名 `keyArray` / `value` / `probability` / `previous` / `anterior` 與原 tuple 標籤逐一相同，故成員存取點無需改動）；`TrieIO.parseValueLine` 改回傳 `[Trie.Entry]`（該 tuple 形狀與 `Entry` 逐欄相同，不需新型別）；`queryGrams` / `queryAssociatedPhrasesAsGrams` 回傳 `[VanguardTrie.TrieGram]`；LexiconKit 以 `public typealias HomaGram = VanguardTrie.TrieGram` 引用。`queryAssociatedPhrasesAsGrams` 內部那個帶 `seq` 的 6 元 tuple 與手寫 comparator 維持原樣。

#### TextMap 格式概要

`VanguardTrieIO` 提供 `parseTextMap` / `serializeToTextMap` / `loadFromTextMap` / `loadFromTextMapLazy`。`parseValueLine` 為共用的 VALUES 行解析方法，供全物化與惰性兩條路徑共用；RevLookup 由 MainTextMap 自動生成，不再讀取 external `.revlookup`。

TextMap 現行為單一 `.txtMap`（三段式 PRAGMA：HEADER / VALUES / KEY_LINE_MAP）。RevLookup 不再有獨立 sidecar，而是由 runtime 依 MainTextMap 自動構建。VALUES 行有三種型別：

- **型別 A 合併行** `>typeID\tencodedCell`：具有 DEFAULT_PROB 的 typeID 條目按讀音合併為單行，grouped cell 使用 escaped pipe 編碼。
- **型別 B CHS/CHT 機率分組行** `@probability\tchsCell\tchtCell`：僅限 `TYPE=TYPING`。`@` 前綴用來消除與一般三欄個體行的歧義，grouped cell 同樣使用 escaped pipe 編碼，BEL (`\u{7}`) 佔位空側。
- **型別 C 個體行** `value\tprobability\ttypeID[\tprevious]`：不具備 DEFAULT_PROB 或需要 Bigram `previous` 的條目。

完整格式規格引用：`vChewing-DevLogs/Reqs4LLM/Archive_P001-P100/Reqs_0000-0010.md` Phase 02 格式規格段落。

### 4.3 Homa — 護摩組字引擎

Megrez 的繼任者，實現漢字組句動態規劃演算法。

- **Bigram 支援**：Gram 承載真實讀音；Bigram 描述僅以前驗字詞為準（不糾結前驗讀音）。
- **節點覆寫**：`OverrideType.withTopGramScore`（頂分覆寫）與 `.withSpecified`（明確指定）。
- **候選字輪替與鞏固**：內建 `Homa_CandidateAPIs_Revolver`（輪替）與 `Homa_ConsolidatorAPIs`（上下文鞏固）。
- **路徑搜尋**：`PathFinder` 以動態規劃 + Unigram/Bigram 結合評分產生最佳組句。
- 取消了舊版 `LangModelProtocol` 協定，改用回調函式 `gramQuerier`。`gramAvailabilityChecker` 已於 Phase 44 移除（`insertKeys()` 直接使用 `queryGrams()` 檢查可用性，無需獨立回調）。
- **Phase 05 熱路徑最佳化**：`Assembler` 具備跨連續 `insertKey()` 的 bounded gram query cache；`queryGrams(using:cache:)` 以結構化 comparator / hash 去除原本字串插值排序與去重成本。

### 4.4 LexiconAssembly — 辭典聚合與洞察中樞（macOS／LibVanguard 兩倉同源）

整合多種辭典來源，向上層提供統一查詢介面。**本節原名 `LexiconKit`，其對位物自 Phase 213 起於 `vChewing-LibVanguard` 亦已更名為 `LexiconAssembly`（原 `Sources/_Modules/LexiconKit/` 整目錄退場）。`vChewing-macOS` 側早於 Phase 202 更名、Phase 210 併入 `Packages/vChewing_OSNeutral_LibVanguard`。**

- **`LXAssembly.LXFacade`**：辭典查詢門面（Phase 201~204 由 `LMInstantiator`／`LMI` 更名而來）。原 LibVanguard 的 `VanguardTrie.TrieHub`（Trie 資料庫中樞，唯一資料來源為 Vanguard Pragma TextMap 的 `updateTrieFromTextMapFile`）**已於 Phase 213 隨舊佈局退場**，其角色由 `LXFacade` ＋下述來源抽象承接。唯一公開查詢面為 `LXAssembly.LXQuerier`（Phase 201~204 之 API 壓縮）。
- **`LXAssembly.LXPerceptor`**：使用者習慣洞察器（POM），基於 Ngram 的行為追蹤、時間衰減三次曲線。原 LibVanguard 側名為 `Perceptor`。其持久化層 `LXAssembly.PerceptionPersistor` 的鎖恆為**葉鎖**——取鎖期間不得呼叫任何回呼，因為 `LXPerceptor` 會在持自有鎖時呼叫該層的 `markKeyForUpsert(_:)`／`markKeyForRemoval(_:)`，兩者互相嵌套即成取鎖順序倒置的死鎖（2026-09-17 修正，回歸斷言見 `Tests/LexiconAssemblyTests/POMLockDisciplineTests.swift`）。
- **`LXAssembly.LXPlainBopomofo`**：倚天中文 DOS 注音表（Phase 201~204 由 `Lexicon.LMPlainBPMF` 更名）。
- **`LXAssembly.LexiconGramSupplierProtocol`**：統一所有辭典來源的元圖供應協定。
- **`LXAssembly.LXGramSupplyHub`／`LXFactoryGramSupplier`**：多來源中樞與「把原廠辭典包成可掛載來源」的轉接器（Phase 212 落地，兩倉同源）。另有合流 API（`LXAssembly.GramConcatFlags`／`concatGramQueryResults`／`concatGramAvailabilityCheckResults`／`makeGramIdentityHash`）。宿主或測試可經 `LXFacade.mountGramSupplier(_:)`（或 `lxQuerier` 的同名方法）掛載任意來源，其元圖會併入 `unigramsFor` 的一般查詢結果、並被 `hasUnigramsForFast` 承認。**兩倉於此完全同源**（`vChewing-macOS` 為正本、`vChewing-OSX-legacy` 為減去模組 import 與 `nonisolated` 的同構副本；legacy 不承擔單元測試）；LibVanguard 自 Phase 213 起為 macOS 的逐位元組複製，故 Phase 212 所記之「四項刻意差異（命名空間／元圖型別／`makeGramIdentityHash` 之可見性／`Homa.Gram.init(_ trieGram:)` 橋接）」**已不再存在**。
- 不負責去重複化（交由 Homa 引擎處理）。

### 4.5 BrailleSputnik — 盲文點字

- 支援 1947 與 2018 兩種盲文標準。
- 核心 API：`convertToBraille(smashedPairs:, extraInsertion:) -> String`。
- 內含聲介韻調完整映射表與標點符號映射。

### 4.6 SwiftExtension — Swift 語言擴展（出貨產品名 `VanguardSwiftExtension`）

- Bool / Double / String / Array / Set 等型別的便利運算符與擴展。
- `LatinKeyboardMappings`：拉丁字母鍵盤映射表。
- `SwiftFoundationImpl`：Foundation 相容實現（跨平台）。
- **打包形態（2026-09-14）**：已自聚合體析出為獨立套件，置於**聚合體目錄之內**（macOS `Packages/vChewing_OSNeutral_LibVanguard/Deps/VanguardSwiftExtension/`、LibVanguard `Deps/VanguardSwiftExtension/`——如此 `.package(path:)` 兩倉同字串、聚合體 manifest 得以逐位元組相同），由該套件出貨 dynamic product `VanguardSwiftExtension`（Darwin 為 dynamic、其餘平台為 static）——**模組名仍為 `SwiftExtension`，故全倉一律 `import SwiftExtension`**（SwiftPM 不要求產品名與模組名相同）。聚合體之 `libVanguard.dylib` 對它是**動態相倚**而非靜態內嵌，故每個行程內本模組恰一份 image；App-based installer 亦僅同捆這一顆（383 KB）。授權為 MulanPSL-2.0（見該套件 `LICENSE`）。

---

## 五、已實作功能清單

- **Homa Revolver soft revolve**：`Homa.Assembler.revolveCandidate` 具 `softRevolve: Bool = false`（先以 `isCandidateSafeToSoftRevolve` 過濾安全子集）；`current` 為目標候選在**原始候選列表**中的索引。SPACE 鍵啟動的輪替一律 `softRevolve: true`，其餘入口（Tab / ContextMenu / 方向鍵 / 方括號）維持 hard。
- **`UserDef.kPreferredRevolverForceLevel`**（integer, default 2, range 0...2）：0＝一律強輪替、1＝僅 SPACE 路徑弱輪替、2（預設）＝一律弱輪替。Typewriter 各 revolve 呼叫點依 `prefs.preferredRevolverForceLevel` 決定 `softRevolve`。
- **InputHandler 的 `rotation` 改名為 `revolution`**：`InputHandler_TriageInput.swift` 的 `triageByKeyCode` 內箭頭鍵分診臨時變數 `rotation` → `revolution`。既有 API 名（含 `revolveCandidate` / `revolveTypingMethod`）不受影響。
- **Installer app bundle 舊版清除**：安裝前 `killall vChewing` / `killall vChewingPhraseEditor`；以 `InputMethodConnectionName` 掃描 `~/Library/Input Methods` 與 `/Library/Input Methods` 的 `.app`；舊版改名 `vChewing-yyyy-MM-ddTHH-mm-ss.appTrashed` 後 trash，系統層級以 `osascript` 提權 `mv`。i18n key `i18n:Installer.AdminRenameFailureNotice`。
- **SwiftUI app installer alert refactor**：`VwrAppInstaller4SwiftUI.swift` 的多個 chained `.alert(...)` 改為單一 `.alert(item: $vm.config.alertItem)`；新增 `InstallerAlertItem` 與 `AlertType.makeAlertItem(paths:)`；Cocoa 端僅 `alertItem == nil` 時才轉換 `currentAlertContent`。

- 注音符號與拼音的雙向解析與轉換（Tekkon）
- 11 種注音排列 + 6 種拼音風格支援（Tekkon）
- RAM 常駐 Trie + TextMap Trie 兩模式辭典（TrieKit）
- Vanguard Pragma TextMap 格式讀寫（TrieKit / TrieIO）：三種 VALUES 行型別（`>typeID\tencodedCell` / `@probability\tchsCell\tchtCell` / 個體行），DEFAULT_PROB 壓縮，escaped pipe grouped cell，BEL 佔位空側；RevLookup 由主 `.txtMap` 自動生成；Typing TextMap `KEY_LINE_MAP` 直接儲存 raw phonabet key（format version `1.1`）
- TextMapTrie canonical specialized backend（TrieKit）：原始 Data 常駐 + 排序後 full-key index + binary search + prefix-range scan + eager reverse lookup + entry-group fast path；穩態記憶體約為全物化 Trie 的三分之一。
- **SQLite 與 Plist 支援已全面移除**：`VanguardTrie.SQLTrie`、`VanguardTrie.TrieSQLScriptGenerator`、`TrieHighFrequencyDecoder` 與本地 `CSQLite3` 套件全刪；`VanguardTrie.TrieHub` 不再持有 `sqlTrieMap` / `plistTrieMap`（`updateTrieFromSQLFile` / `updateTrieFromSQLScript` / `updateTrieFromPlistFile` 退場）；`TrieIO` 的 plist 出入徑與 `Trie` / `TNode` / `Entry` 的 `Codable` 皆移除。**序列化僅餘 TextMap 一途**；**判死的是 plist 檔案格式，不是 `VanguardTrie.Trie` 這個 RAM 型資料結構**；`TrieIO.validate(_:)` 的根節點假設為 `0`（設回 `1` 必誤報 `isValid: false`）。
- 兩倉的 factory dictionary runtime 維持 `factoryTrie: VanguardTrie.TextMapTrie?`，不回退下游 `FactoryTextMapLexicon`；`VanguardTrieProtocol.getEntryGroups(...)` 讓 existential query fast path 成立。
- `LMInstantiator.Config` 具 `partialMatchEnabled = false`（partial-match 總控）；`LMInstantiator.lookupHub` 為唯一 canonical public lookup surface。
- Phase 36 的完整敘事，以及 P5 wrapper retirement 的準入清單與 kickoff template，見 `vChewing-DevLogs/Research/Phase036_Research.md` appendix。
- `vChewing-LibVanguard` 的 `TrieHub` TextMap path 與兩倉的 `LMInstantiator_TextMapExtension` 均已移除 TextMap backend 的 phonabet encrypt/decrypt 假設；raw phonabet key 為唯一 canonical TextMap query surface。
- 以下 A~D 四項：
   - **Phase A**：`mergedAlternativeBucketUnigrams(for:)` 的原廠辭典查詢走 `factoryChoppedUnigramsFor()` / `factoryChoppedCoreUnigramsFor()`。**注意**：`makeTextMap` 輔助函式的 `VERSION` 為 `1.1`（否則 10+ 測試靜默失敗）。
  - **Phase B**：`TextMapTrie.getNodeIDsForKeyArray` 的 `keyInitials` 直接取 `$0.first?.description`（零鎖），不走 `getCachedFirstChar` 與 `internKey` 的雙重 NSLock。
  - **Phase C**：`QueryBuffer<T>` 以 `NSLock` 取代 `DispatchQueue.sync`（時間戳改用 `DispatchTime.now().uptimeNanoseconds`）。**注意**：`cleanupCheckInterval` 必須是 `static var`——Swift 不允許 generic type 內的 `static let` stored property。
   - **Phase D**：`Homa.Assembler.gramQueryCache` 的鍵自 `[[String]: [Homa.Gram]]` 改為 `GramQueryCacheKey`，`gramQueryCacheOrder` 同步為 `[GramQueryCacheKey]`，以插入順序實現 LRU 半量淘汰（汰最舊 50%）取代 `removeAll()`。**注意**：不可用裸 `Int` hash（碰撞誤命中）。
   - Phase B/C/D 已鏡像至 `vChewing-macOS`（`vChewing_LangModelAssembly/TrieKit/`、`vChewing_Homa/`）與 `vChewing-OSX-Legacy`（`Shared/vChewingComponents/LMAssembly/TrieKit/`、`Shared/vChewingComponents/Homa/`）。
- **`Homa.PossibleKey` 結構化枚舉**：`Config.keys` / `Assembler.keys` 為 `[PossibleKey]`（取代 `&` 字串編碼）；`unigramsFor` 具 LRU cache。**注意**：`insertTemporaryData` / `clearTemporaryData` / `injectTestData` 等資料變更入口皆須使該 cache 失效，否則 sub-LM 查詢返回過時結果。
- **就地加詞之即時生效鏈路（2026-09-17 定案）**：`SessionProtocol.performUserPhraseOperation` 之次序恆為「寫檔 → `insertTemporaryData` → `updateUnigramData()`」——熱重載（`assignNodes(.refreshExisting)`：清空組字器查詢快取、就地重查所有既有節點）看得見的只有已入庫的臨時資料，次序顛倒即無從立刻生效。`insertTemporaryData` 必須**全量**使 `LXFacade.unigramLRUCache` 失效（替代讀音路徑以 `ALT\t…` 定址、無法以 keyChain 枚舉）；`LXFacade.loadUserPhrasesData` 之非同步路徑不得在新資料就緒前清空既有資料（「舊資料已清空、新資料尚未讀入」之空窗期會讓熱重載把組字器重建成沒有使用者詞語的狀態），該清除延後至 `replaceData`（成功）／`readFileContentAsync` 之 `onFailure`（失敗）；且只清「本次將重新載入者」（`filterPath` 為 nil 時不動 `lxFiltered`）。
- **動態 `maxSegLength`**：`Homa.PossibleKey` 具 `count` 與 `isMultiple`；`assignNodes` 在 span 遍歷前檢查 `rangeOfPositions` 內是否有 `isMultiple` 的 key，有且 `maxSegLength > 4` 則縮為 4。無 `.multipleKeys` 者保持 `maxSegLength = 10`；有者每次插入查詢量封頂 780 次。
- **`LMCoreEX` 前綴部分匹配**：具輕量前綴索引 `sortedKeys: [String]`、`keys(matchingPrefix:)` 與 `unigramsFor(keyPrefix:)`；`LMInstantiator.unigramsFor(keyArray:)` 具 `partiallyMatch: Bool` 過載（預設 `false`）；`LookupHub.grams(for:)` 傳 `partiallyMatch: lmi.config.partialMatchEnabled`，使 `lmUserPhrases` 亦回前綴匹配。LRU 快取鍵含模式維度（`PM0`/`PM1`）。
- **`narrateTheComposer` 朗讀**：目標含 ASCII 字母時先試以 `Tekkon.cnvHanyuPinyinToPhona` 轉注音；組字路徑以 `actualKeys[cursor - 1]` 為朗讀對象。**陷阱**：`getPreviousRearSyllableSnapshot` 必須走 `receiveKey(fromPhonabet:)`——`actualKeys` 存注音，用 `receiveSequence(readingKey, isRomaji: true)` 重建會令拼音模式的後置聲調覆寫失效。
- **聲調覆寫提示之抑制偏好（2026-09-18，Phase 228）**：`kSuppressTooltipForIntonationKeyOverrideEvents`（`suppressTooltipForIntonationKeyOverrideEvents`；預設關）——啟用後，聲調鍵覆寫游標身後的漢字的音調時不再顯示「已覆寫游標身後的漢字的音調」內文提示。該提示之三行賦值（`tooltip`／`tooltipDuration`／`tooltipColorState`）收在 `BPMFFullMatchTypewriter.performRearIntonationOverrideIfNeeded` 之 `.success` 分支的偏好閘門內、**三行同進同退**（否則會留 `2` 秒之殘值）；覆寫行為、朗讀與 `session.switchState` 皆在閘門外、不受本偏好影響。同檔 `handleStandaloneIntonation` 之「獨立聲調鍵」提示（`IntonationMarkInstruction`）屬另一事件、不在本偏好管轄範圍。
- **混輸 Tooltip 之錨點（2026-09-18，Phase 229）**：中英混打模式下，內文 Tooltip 之錨點改以「未完成讀音後方之游標位置」為準（此前恆錨在組字區最前方＝客體量測座標 0 之矩形），與選字窗之錨定（`candidateWindowOriginInfo()` → `lineHeightRect()` → `clientLineHeightRect(forU16CursorPos:)`）同源。該位置須另存於 `IMEState`：`IMEStateData.cursorPosRightBehindTheUnfinishedReading`（Character 索引）＋唯讀 `u16CursorPosRightBehindTheUnfinishedReading`（UTF-16 對位）——**凡 `generateStateOfInputting()` 生成之輸入狀態一律賦值**：未完成讀音非空時取其插入處（`cursorSansReading`），為空時繼承當前輸入游標位置（`result.cursor`）；nil 僅見於非輸入狀態（標記／選字／關聯詞／符號表）。蓋因 `.ofInputting` 狀態之 `marker` 會被 `getMitigatedState(_:)` 拉平至 `cursor`（IMK 要求 selectionRange 之長度為 0），該位置於 Session 層無從回收。**用語**：護摩引擎以「與文字輸入方向相反的方向」為後方（Rear）——`isCursorAtAssemblerEdge(direction:)` 之中 `pos == 0` 為 `.rear`、`pos == length` 為 `.front`；故「未完成讀音後方」＝該讀音所占區段之起始側。消費端為 `SessionProtocol.showTooltip` 之 private `tooltipAnchorRect()`：輸入狀態一律改走 `lineHeightRect(atU16Pos:)`（未完成讀音為空者因而錨在輸入游標位置），非輸入狀態沿用既有錨定；客體量測無效（`CGRectNull`／原點為零）時退回既有錨定。**陷阱**：`updateVerticalTypingStatus()` 仍須先呼——縱排判定（`isVerticalTyping`）靠它，不可因換錨點而略過。**附註（2026-09-18 補記）**：面板定位須晚於客體之組字區更新——`switchState` 原先在 `updateCompositionBufferDisplay()` **之前**呼叫 `showTooltip`／`toggleCandidateUIVisibility`，導致量測當下客體仍持有上一狀態之組字區、本狀態之索引對其越界，`clientLineHeightRectForU16CursorPos:` 遂逐位遞減而退回前一個字元（症狀：Tooltip／選字窗定位恆落後一個字元）。現次序已改為「先更新組字區、後擺放面板」。經事主於真機覆驗，該症狀已解決（2026-09-18）。**相關不變量**：`clientMitigationLevel >= 2`（安全強化組字區／PCB 路徑）時 `getMitigatedState(_:)` 不拉平 `.ofInputting` 之 `marker`，故 `state.marker` 恆等於 `cursorPosRightBehindTheUnfinishedReading`、`markedRange` 即該未完成讀音所占區段；PCB（`vChewing_PopupCompositionBuffer` 之 `CompositionView.update(using:)`）以 `state.u16MarkedRange` 繪標記底色（故整段讀音成 marked range）、以 `state.u16Cursor` 擺閃爍游標（故游標在區段終點、非該欄位）。級別 < 2 時 `marker` 被拉平至 `cursor`、`markedRange` 為空（該欄位仍為讀音插入處）。
- **冗餘 `assemble()` 清理與 Homa `dropKey`**：`insertKey`、`dropKey`、`overrideCandidate`、`updateUnigramData` 等路徑已無冗餘 `assemble()`。`assembler.dropKey` 為 `do { try assignNodes() } catch { assemble() }`——不可只寫 `try? assignNodes()`，否則 `noNodesAssigned` 時 `assembledSentence` 停在刪鍵前狀態。
- **Homa revolver 首輪 pre-consolidation**：`revolveCandidate(...)` 具 `skipInitialConsolidation: Bool = false`；Typewriter 依 `homaCandidateCursorType` 與 `assembler.isCursorAtAssemblerEdge(direction:)` 決定是否跳過首輪鞏固——僅 `.placedFront` / `.placedRear` 且游標在對應 edge 時啟用。
- **MixedAlphanumericalTypewriter 前綴吸收**：修復八類缺陷（純注音超長吞噬、auto-split 偏向長後綴、Space 缺 fallback、ETenDOS 被 `hasUnigramsForFast` 過濾、auto-correct 干擾 suffix）。現行規則：動態碼長上限（Dachen26=6，其餘=4）、關 auto-correct、長後綴優先、Gated `hasNoDestructiveOverwrite`。
- **MixedAlphanumericalTypewriter camelCase 後綴防禦**：`buildAutoSplitCandidate` 具 `suffixHasUppercase` guard，拒絕後綴含大寫字母的候選（避免 `macOS ` 被拆成 `ma` + `OS`）。僅檢查 suffix（prefix 允許含大寫如 `Hello你好`）。**已知限制**：`iPhone ` 等中段大寫 + 單字母後綴仍可能誤拆。
- **MixedAlphanumericalTypewriter 聲調與 Shift ASCII 阻斷**：對 `BPMFFullMatchTypewriter` 委派點強制關閉 `isToneOverrideEnabled` 與 `isLeadingIntonationAccepted`；**Mixed mode 永遠不接受聲調前置鍵入**（相關偏好於 mixed mode 無效）。`isShiftASCII` 與 `shouldBlockPhoneticAbsorption`（digit + uppercase）閘門使 Shift 敲入的 ASCII 與純數字 / 大寫字母不被 Tekkon composer 吸收。
- **`LMInstantiator` TextMap path 收斂到 `VanguardTrie.Trie.EntryType`**：`CoreColumn` 已自兩倉的 factory lookup surface 退場；`factoryUnigramsFor` / `factoryChoppedUnigramsFor` / `hasFactoryCoreUnigramsFor` 等一律以 `entryType:` 傳參。**注意**：`suppressFactoryUnigramsOfKanaSyllables` 須也覆蓋 `queryGrams(...)` 的 `makeFactoryUnigrams(queriedGrams:...)`。
- **Typewriter 層中英文混輸 `MixedAlphanumericalTypewriter`**（`TypewriterProtocol` 實作；由 `mixedAlphanumericalEnabled` 控制，**預設關閉**；與 cassette/pinyin 互斥）：`composer` + `mixedAlphanumericalBuffer` 雙軌。auto-split 即時算最優 ASCII/Phonetic 邊界；Space finalize 具 `onLexiconMatchFailure` fallback。**已知限制**：全 parser-covered 短英文 token 持續鍵入時仍可能 zhuyin-first。
- **混輸緩衝區之 Option+BkSp 整段作廢**：`handleBackSpace` 之混輸分支對「恰為 Option」之 BkSp 採 `removeAll()` 一次清空 `mixedAlphanumericalBuffer`（尚待辨識的英文緩衝區），其餘維持刪末字元；清空後注拼槽由 `syncComposerWithMixedAlphanumericalBuffer()` 同清，組字區既有中文不受波及。判準 `commonKeyModifierFlags == .option` 與同函式 codePoint／romanNumerals 兩支一致。
- **nonKanji（假名、鴨蛋零等）原廠辭典查詢**：`theDataMISC` 查詢原受 `keyChain.hasPrefix("_")` 限制，普通讀音 key 下的 `nonKanji`（typeID 8）條目永遠不會被返回；現以 `CoreColumn.theDataNonKanji`（textMapTypeIDs = [8]）在 `unigramsFor` / `hasUnigramsForFast` 為所有普通讀音 key 啟用該路徑，並保留 `_` 開頭 key 的 MISC 行為。
- **`suppressFactoryUnigramsOfKanaSyllables` 偏好旗標**：可停用原廠假名音節輸出（以詞值的 kana script 判定濾除，保留 `〇` 等非假名 nonKanji）。另：mixed mode 下除 `input.isSymbolMenuPhysicalKey` 外，主鍵盤數字 / 字母 / 符號鍵只要 Alt 被摁著就以 keyCode + `LatinKeyboardMappings` 還原 raw ASCII。
- 完整 Lexicon partial-match 熱路徑最佳化（Phase 05）：Assembler 跨插入查詢快取、Trie split cache 重用、node.id 去重、SQL prepared statement reuse
- `vChewing-macOS/Packages/vChewing_LangModelAssembly` 以 `vanguardTextMap` 取代 legacy SQLite。**現行規則**：runtime 與測試路徑都不接受 external `.revlookup` payload；反查只索引 single-segment `@` 分組行內的 ideographic characters，並無條件納入全部 CNS 條目；輸出會將 ASCII phonabet key 還原為注音。
- 不完全讀音部分比對與多音切割查詢（TrieKit）
- Unigram + Bigram 動態規劃組句（Homa）
- 節點覆寫、候選字輪替、上下文鞏固（Homa）
- Homa rare-case candidate revolver / consolidator：`CandidatePairWeighted.weight` 退回語言模型 metadata 身分，不可當成 `.withSpecified` explicit override score；`revolveCandidate()` 對 non-explicit 且 target span 改變的首輪情形有條件式 consolidation。
- 多來源辭典聚合（`LexiconAssembly`；Phase 213 前於本倉名為 `LexiconKit`）
- 使用者習慣 Ngram 洞察與時間衰減（`LexiconAssembly.LXPerceptor`；Phase 213 前於本倉名為 `LexiconKit.Perceptor`）
- 1947 與 2018 盲文標準轉換（BrailleSputnik）
- **原廠 VanguardTextMap 非同步載入**：`connectFactoryDictionary` 依 `asyncLoadingUserData` 拆分同步 / 非同步雙路徑；生產環境走 `VanguardTrie.TextMapTrie` 初始化路徑，避免載入時 1-2 秒 UI 凍結。
- **factory dictionary completion-driven 載入狀態**：`connectFactoryDictionary` 以 completion callback 回報最終載入結果；`LMMgr.connectCoreDB()` 先發 Started 通知、再於 completion 成功時發 Complete 通知（消除 async 路徑的「提前宣告完成」謊報）；Legacy 端以 main-queue + `@MainActor` 發通知。
- **拼音免聲調長句效能（TrieKit / LMInstantiator）**：`TextMapTrie` 具 chopped lookup specialized fast path（避免 protocol default 的笛卡爾積全展開）；`LMInstantiator.mergedAlternativeBucketUnigrams(for:)` 先索引原廠候選再做 deferred filter removal。
- **拼音免聲調長句效能精修**：`TextMapTrie` chopped path 的 ASCII initials / prefix/equality 走 UTF-8 bytes（遇非 ASCII 自動 fallback string path）；Tekkon `PinyinTrie` 具 parser-keyed shared cache，`pinyinAutoChopResult` 走 shared trie。
- **`QueryBuffer` NSMutex 清理 + `LMInstantiator` 單輪 memo**：`QueryBuffer` 每個 mutable property 各自以 `NSMutex` 保護。`LMInstantiator.mergedAlternativeBucketUnigrams` 具單輪 scope memo（`FactoryLookupMemoKey`）與 `joinedKey` cache。
- **`hasUnigramsForFast` 與非原廠迴路**：`LMInstantiator.hasUnigramsForFast(keyArray:)` 跳過濾除表、語彙置換、InputToken 展開、DateTime、倚天排序等後處理。`LookupHub.hasGrams(for:)` 與 `Typewriter_BPMFFullMatch` 亦走 fast path；`mergedAlternativeBucketUnigrams` 迴路前有 `Set<String>` 批量預篩選，非原廠迴路自 O(M^N) 降為 O(1) 或 O(K)。
- ~~下游 FactoryTextMapLexicon DFD 硬碟直讀（Phase 11，已作廢）~~：實機測試記憶體飆升 20~30 MB，全數撤銷。失敗根因：pread() 碎片化 heap allocation + 物化讀音鍵字串陣列開銷 + Data(contentsOf:) 隱性 mmap purgeable 優勢被低估。
- **LMCassette（CIN2 磁帶模組）連續記憶體最佳化**：`charDefMap`、`charDefWildcardMap`、`symbolDefMap`、`reverseLookupMap` 四個大型 Dictionary 改為 `CassetteSortedMap`（contiguous Data + byte-range index + binary search）；`octagramMap` / `octagramDividedMap` 改為 `CassetteOctagramMap` / `CassetteOctagramDividedMap`。
- **LMCassette 索引壓縮與 wildcard map 去重**：offset / count 欄位由 `Int` 改 `UInt32`；移除 `CassetteByteRange`；刪除 `charDefWildcardMap` 與 `buildWildcard(from:wildcard:)`；wildcard 查詢改對 `charDefMap` 做前綴掃描，經 `wildcardValuesFor(key:wildcard:)` / `containsWildcardMatch(key:wildcard:)` 即時產生。
- **LMCassette CIN v2.7 花牌鍵與任意單字元鍵分化**：新增 `%anysinglecharkey` 解析（**僅首次生效**、與 `%wildcardkey` 碰撞時後來者被忽略）。`patternValuesFor(key:wildcard:anySingleChar:)` / `containsPatternMatch(key:wildcard:anySingleChar:)` 為通用 pattern matcher（anySingleChar 恰好 1 字元）。`processCassetteQuickSelection` 具 functional-key bypass，使 `Shift+?` 在 `?` 為當前磁帶 functional key 時讓位給組筆錄入。`LMInstantiator` 具 `cassetteAnySingleCharKey`。**注意**：前提是磁帶已把 `?` 定義為 `%anysinglecharkey` / `%wildcardkey` 且未被同名資料鍵失效化。
- **LMCassette 反查索引零複製化**：廢除 `reverseLookupMap: CassetteSortedMap`，改為 `CassetteReverseIndex`（`revChars` = 去重後唯一反查字詞 bytes、`revEntries` 16B、`revCodeRefs` 指向 charDef/symbolDef 合併 namespace 的 entry 索引），查詢時依 refs 自來源 map 的既有 `rawData` 按需物化碼字串。**注意**：同字詞多碼順序自非穩定 sort 的未定義順序改為確定性（charDef 先、各依碼 bytes 序）。
- **`LMCoreEX` / `LMReplacements` / `LMAssociates` 索引壓縮**：三模組的 Dictionary + `strData: String` 改為 `rawData: [UInt8]` + sorted UInt32 byte-offset entries + binary search；`strData` 對外維持 `String` computed 唯讀屬性。`RangeParserAPI` 新增 `[UInt8]` byte 級 helper。LMReplacements 保留「同 key 最後一行覆蓋」；LMAssociates 保留 `#` cell 提早停止與雙鍵查詢；LMCoreEX 保留 tab 正規化與第三欄權重。
- **磁帶模式花牌鍵三明治組合**：`Typewriter_Cassette` 已無「組筆區非空時敲花牌鍵立即組字」條件——花牌鍵與任意單字元鍵一律僅作普通筆畫錄入，組字時機與一般筆畫一致（滿筆長自動組字、或空白/Enter 強制組字）；`shouldFormLongestCassetteKey` 無花牌鍵豁免（`zzzx*` 類無更長可能時仍自動組字，`y*` 因 `y**` 仍有匹配而保留錄入空間）。**行為變更**：敲 `y*` 後需按空白/Enter 組字。
- **Homa Assembler 查詢結果去重與元圖位置唯一性**：`queryGrams` 以 keyArray 為鍵的快取會把同一批 `[Homa.Gram]`（含相同 FIUUID）分發給不同節點，使 `generateKeyForPerception` 以 `lastIndex(id ==)` 定位 head 時誤判。現行設計：快取為純模板角色，`assignNodes` 新建節點與 `syncingGrams` 兩條路徑一律以 `Gram.withNewIdentity()` 物化節點專屬副本。
- **LMAssembly 共用 parser / cell tokenizer**：`RangeParserAPI.parse()` 對單一 ASCII separator 走 `String.UTF8View` byte scan、非 ASCII 者走 `Character` fallback。**注意**：單元測試 `UserDefaults` reset 順序不當會造成 stale `cassetteEnabled`、令 associated phrase 測試誤報。
- **InputHandler 倚天 DOS 候選補缺字**：`generateArrayOfCandidates()` 尾段具 `segregateCandidatesForETenDOS(from:)` 與 `supplementalETenSingleKanjiCandidates(reading:existingSingleSegments:)`：`prefs.enforceETenDOSCandidateSequence` 開啟時維持既有單字重排，關閉時把缺席的 ideographic 單漢字以 `-9.5` 權重追加到尾端。**注意**：`segregateCandidatesForETenDOS` 須防禦空 `keyArray` 候選。
- **ButKo BPMFVS 特殊遞交**：本地 package `ButKo_BPMFVS` 具 `phonic_table_Z.txt` parser 與 `convertToBPMFVS(smashedPairs:)`，以 ButKo 的讀音順序決定 IVS slot（首讀音維持原字、次讀音起附加 `U+E01E0 + slot`）；查表前須把 raw key 的後置輕聲（如 `ㄉㄜ˙`）正規化成前置輕聲。`UserDef.kReflectBPMFVSInCompositionBuffer` 令組字區 / 候選預覽只在 `CommitableMarkupType.bpmfvsAnnotationButKo = 4` 且開關啟用時投影成 BPMFVS。
- **`vChewing-VanguardLexicon` C-based 新酷音辭典純 Swift 生成器**：`chewingCBasedCHS` / `chewingCBasedCHT` 由 `ChewingCBasedDatabaseGenerator` 直接生成 `dictionary.dat` 與 `index_tree.dat`（不依賴 precompiled 版本）。**注意**：單字 `char-misc-nonkanji` 類的負詞頻行直接忽略；root node key 採 16-bit truncation 以對齊原版 C 行為。
- **`vChewing-VanguardLexicon` HealthCheck duplicate 偵查**：`Collector.healthCheckPerMode()` 直接重讀 raw source assets（含 `char-kanji-core` / `char-misc-bpmf` / 當前語系所有 `phrases-*`），以與 ingest 相同的 normalization 重建 occurrence；只要 `phrase + reading` 相同即視為 duplication，彙總後寫入 `healthCheckException([String])` 再拋出失敗。
- **`vChewing-VanguardLexicon` Rust 版新酷音辭典純 Swift 生成器**：`chewingRustCHS` / `chewingRustCHT` 由 `ChewingRustDatabaseGenerator` 自 `tsi.src` / `word.src` 生成 libchewing-rust 可讀的 `tsi.dat` / `word.dat`。**注意**：單字負詞頻（如 `ば -1 ㄅㄚ`）忽略、多字負詞頻拒絕。
- **BPMFVS commit 洩漏修復與詞庫 Unicode 污染稽核**：`committableDisplayText(...)` 為兩倉的統一 raw commit source——各提交路徑全部收斂到不含 BPMFVS 投影的原始字串；唯一產出 BPMFVS 的路徑是刻意的 `commissionByCtrlOptionCommandEnter`。`InputSession_HandleStates.swift` 的 `.ofEmpty` auto-commit 分支須以 `if let inputHandler` 條件綁定，不用 `?? previous.displayedText` fallback。
- **BPMFVS marking state 使用者詞語污染修復**：`IMEStateData` 具 `rawDisplayTextSegments: [String]?` 作 raw/display 雙軌——`displayTextSegments` 供渲染、`rawDisplayTextSegments` 儲存未投影原始字串；`userPhraseKVPair` 改從 `rawDisplayedText` 截取標記範圍；candidate preview 須同步更新兩個欄位。
- **Hotenka 繁簡轉換引擎 v2.0.0**：兩倉自 SQLite 後端（v1.3.1）升級至 StringMap 後端（v2.0.0）：`HotenkaChineseConverter` 無 `CSQLite3Lib` 依賴、新增 `HotenkaStringMap.swift`；`convdict.sqlite` 換為 `convdict.stringmap`；`init(sqliteDir:)` 換為 `init(stringMapPath:)` throwing initializer。
- **CNS11643 全字庫讀音過濾 UX**：`kFilterNonCNSReadingsForCHTInput` 對單一讀音（`keyArray.count == 1`）的不合規 Unigram 以 `-9.5` 權重 demote（建新 `Megrez.Unigram`，`score` 為 `let`），**多讀音詞組仍維持濾除**；否則啟用該選項時「播」（CNS 僅收 ㄅㄛˋ）等常用漢字會在 ㄅㄛ 讀音下消失。
- **`BookmarkManager` 熱點快取**：`LMMgr.dataFolderPath(isDefaultFolder: false)` / `cassettePath()` 每次無條件 `BookmarkManager.shared.loadBookmarks()`——在 iCloud Drive 路徑下成為 restore 熱點；`Jad_BookmarkManager` 與 legacy copy 具 bookmark store signature 快取（bookmark 檔未變且 access 尚在時直接返回）。
- **沙盒卸除 Fallback UX**：兩倉收緊 sandbox 後不再以 NSOpenPanel 取得 `~/Library/Input Methods/` 授權自刪，改由 `AppDelegate.selfUninstall()` 顯示指引 NSAlert，並以 Finder 揭示使用者詞語資料夾、App Support 父資料夾與 runtime `Bundle.main.bundleURL`。
- **iCloud Drive 磁帶書籤持久化失敗 workaround**：iCloud Drive 管理的 `~/Documents`、`~/Desktop` 等目錄中的 CIN2 磁帶 security-scoped bookmark 無法跨 reboot 持久化。`LMMgr` 具「Import to AppSupport cache」：選取 CIN2 檔案時同步複製到 `~/Library/Application Support/vChewing/Cassettes/`；`cassettePath()` 在 bookmark 還原失敗時 fallback 至快取副本；`resetCassettePath()` 清理快取檔（不誤刪使用者指定在 `Cassettes/` 的來源檔）；UI 入口須在 `saveBookmark` 後呼叫 `importCassetteFileToCache`。
- **磁帶最長可能碼自動組字、overflow trap、滿碼刪退與 Shift+Backspace 析構**：`Typewriter_Cassette.handle(...)` 不於 append 之前判定 `isStrokesFull` / longest-possible key，而拆成「既有滿碼 overflow」與「append 後 auto-combine」兩段；quick-set refresh 移到 combine 判定之後（否則未改動 calligrapher 的刪鍵會被 `renderQuickSetsIfNeeded(...)` 誤吞）。第 5 碼只回報 `2268DD51`，不漏到 `A9BFF20E` blocked-data trap。
- **Perception Override / Megrez 演進落地**：Megrez `Compositor` 具 Assembler 級 `perceptor` 注入，`3_KeyValuePaired.swift` 以 `perceptionHandler ?? perceptor` dual-dispatch 送出 `PerceptionIntel`；`LMPerceptionOverride` 的 `kDecayThreshold` 為 `-13.0`，WAL / JSON snapshot / CRC32 compaction 抽離至 `PerceptionPersistor`。
- **Homa transplant / LXPerceptor 對齊**：三倉（`vChewing-macOS`、`vChewing-LibVanguard`、`vChewing-OSX-Legacy`）完成 Megrez → Homa、`LMPerceptionOverride` → `LXPerceptor` canonical rename，並修補 `CandidatePair` 權重語義與同分標點保序；LibVanguard 側補 `LX_Perceptor.reducedLifetime` parity。
- **`LMCoreEX` tab→space 正規化**：`LMCoreEX.replaceData()` 最前端有一行 `let rawStrData = rawStrData.replacingOccurrences(of: "\t", with: " ")`。**理由**：`parseCells(in: splitee: " ")` 只認 ASCII space，而 `LMConsolidator.consolidate()` 在 pragma header 完好時會 early-return，故 `open()` 與 `readFileContentAsync` 都不做 tab→space 正規化。
- **候選字排序與原廠辭典重載 LRU cache 失效**：`LMInstantiator.unigramsFor()` 在 consolidate 後須補 `sort { $0.probability > $1.probability }`；`Homa.Assembler.fetchCandidates()` 排序須含第三級鍵 `$0.weight` / `$1.weight`。`static var factoryGeneration` 於 `factoryTrie` setter 遞增，`unigramsFor()` 的 LRU fingerprint 為 `config.hashValue ^ factoryGeneration`。
- **IME 之 varargs CLI 偏好 JSON 交換入口 `--dump-prefs-json` 與 `--import-prefs-json`**（落點 `MainSputnik.swift` 之 `MainSputnik4IME`：`dumpPrefsAsJSON` / `applyPrefsJSON(_:)`）：`--dump-prefs-json` 把可交換偏好以**純 JSON** 印至標準輸出；`--import-prefs-json <path>` 自 JSON 檔匯入，匯入後做 `fixOddPreferencesCore()`（機制係既有之 `UserDef.exportAsJSON()` / `importFromJSON(_:)`，含 `jsonExchangeBlacklist`）。**沙盒**：container 外 JSON 直讀必被拒，故與 `--import-kimo` 同款先試直讀、失敗則取 security-scoped 授權。

---

## 附錄一、開發階段歷史

因該章節過於龐大，故挪至 `vChewing-DevLogs/DevReqsHistory.md` 單獨管理。

---

## 附錄二、已知問題與注意事項

### A2.1 當前已知問題

1. `TrieJoinedTestSuite/testTrieJoinedAssemblyingUsingPartialMatchAndChops`（Phase 213 前於本倉名為 `LXTests4TrieHub/testTrieHubAssemblyingUsingPartialMatchAndChops`）若暫時使用完整 Lexicon 測資，會因語料語義與 Tiny Sample 不同而出現 sentence expectation failure；目前應將 benchmark 視為有效信號、將 assertion mismatch 視為已知暫時狀態。
2. **CI（linux／WinNT）測試行程硬崩（`Illegal instruction`／`c000001d`）——`mainSync` 對主佇列之遞迴 `sync`（2026-09-16 查明；已修於 P219）**：自 **`95a609c`**（2026-09-15，該筆把 CI 之 Swift 版自 `latest`＝當時的 6.3.3 抬到 **6.4**）起，兩條 workflow 之 `swift test --no-parallel` 每次都在同一處崩潰、且恰為兩個測試靶各一次（`LibVanguardTests`／`LexiconAssemblyTests`）。**堆疊**（WinNT 版有符號）：`InputSession.deinit` → `String.mainSync` → `DispatchQueue.main.sync` → `__DISPATCH_WAIT_FOR_QUEUE__` → libdispatch 之 client crash（`src/queue.c:1646`「`dispatch_sync called on queue already owned by current thread`」；Darwin 編成 SIGTRAP、Linux／WinNT 編成 ud2＝SIGILL）；另一條為 `LXAssociates.saveData()` → `withFileHandleQueueSync` 內之 `mainSync`。**機理**：`mainSync` 以 `Thread.isMainThread` 判斷「是否已在主執行緒」——在 Linux／WinNT 上主佇列之工作是由 dispatch worker 執行（該執行緒 `Thread.isMainThread` 為假、卻已持有主佇列之 drain 鎖），於是走 `DispatchQueue.main.sync` 慢路徑而遞迴 `sync`。**macOS 不受影響**（主佇列跑在主執行緒、走就地執行之快速路徑；本機同款 `test202_InputHandler_EscapeBehaviorVariants` 綠燈）。**同期 macOS 那條 CI 之紅燈與此無關**：`setup-xcode` 找不到 Xcode 27.0（runner 映像只到 26.6）。**已落地之修法（P219，2026-09-16；兩倉 byte-sync）**：① `mainSync`（`SwiftExtension/SwiftFoundationImpl.swift`）改以「註冊在 `DispatchQueue.main` 上之 `DispatchSpecificKey`」判斷是否已在主佇列（`getSpecific` 問的是「當前正在執行的佇列」、非執行緒身分，故兩平台通用）——命中則就地執行；② `withFileHandleQueueSync`（`LexiconAssembly/vChewingLXAssembly_Common.swift`）同法加掛 `fileHandleQueueKey` 之判斷。**兩項 6.2+ 側之實作約束**：該判斷函式須標 `nonisolated`（否則自身即成為 MainActor 隔離、反而無法自 `nonisolated` 的 `mainSync` 呼叫），且該 `DispatchSpecificKey` 與其註冊動作須收進**函式內之區域型別**——置於檔案層級會被 `-default-isolation MainActor` 收歸 MainActor，`nonisolated(unsafe)` 雖可編過、但 6.4 會對它誤發「對 Sendable 常數為多餘」之診斷（照該診斷移除即編不過）。**本機驗收**：6.4 側 **535 項 0 失敗**、5.10 側（兩倉）與 macOS 側皆 `Build complete!`；`vChewing-OSX-legacy` 之同構同步（`mainSync` 改走新增之 `isOnMainQueue()`、`withFileHandleQueueSync` 之檔案本已符合、僅補 doc comment）經 `make debug-core` `** BUILD SUCCEEDED **`。**未驗**：Linux／WinNT 之止崩須推一次 CI 方能確認。**仍未辦**：③ `InputSession.deinit`（本體僅一行 log）與 `Debouncer.deinit`（僅動 lock 保護之狀態）不再 hop 至主佇列——此僅為先前提議、未採納為 P219 之範圍。

   **第二輪（2026-09-16，CI 複驗後）**：上述修法只解了一半——`InputSession.deinit` 那條已止（linux／WinNT 之 `LibVanguardTests` 各 **60 項全綠**），惟 `LexiconAssemblyTests.testSaveDataRoundTrip` 仍崩、兩平台各一次。**真因**（WinNT 符號化堆疊：`testSaveDataRoundTrip` → `LXAssociates.saveData()` → `withFileHandleQueueSync` → `closure #1` → `mainSync` → `DispatchQueue.main.sync` → `_dispatch_sync_f_slow` → `__DISPATCH_WAIT_FOR_QUEUE__`）：`fileHandleQueue.sync` 於未受競爭時**就地在呼叫端執行**（libdispatch 之 `_dispatch_sync_f_fast`），而該呼叫端（`@MainActor` 之測試本體）**正在主佇列上**；於是內層 `mainSync` 眼中「當前正在執行的佇列」已被壓成 `fileHandleQueue`——`Thread.isMainThread` 為假、`DispatchQueue.getSpecific(key: mainQueueSpecificKey)` 亦為 `nil`（**它問的是當前佇列**），兩者皆不命中，遂對主佇列 `sync`，而主佇列之 drain 鎖正由本執行緒持有。**教訓（通用）**：`getSpecific` 這一招問得出「當前佇列是否為主佇列」，卻**問不出「本執行緒是否代持著主佇列」**；凡「先 `Q.sync` 進某佇列、再於其內 `mainSync` 回主佇列」之寫法，都必須在**進入 `Q.sync` 之前**擋掉在主佇列上的呼叫方——補在內層無效。**修法**：① `isOnMainQueue()` 由 `private` 改 `public nonisolated func`；② `withFileHandleQueueSync` 之第一關由在 corelibs 上形同虛設的 `if Thread.isMainThread` 換成 `if isOnMainQueue() { return try execute() }`（macOS 側行為不變）。`withFileHandleQueueAsync`／`readFileContentAsync` 走 async、block 必落別的 worker，無此互鎖，不動。`vChewing-OSX-legacy` 之 `withFileHandleQueueSync` 不 hop `mainSync`、亦無此互鎖，只對齊 `isOnMainQueue()` 之存取級別並在 doc 註明「本倉不應加掛那一關」。**本機驗收**：LibVanguard 6.4 側 **535 項 0 失敗**；三倉建置與格式管線皆過。**未驗**：本機無法複現（Darwin 上主佇列恆在主執行緒），故止崩只能靠 CI 判準——第二輪推上去後（run `35087157715`＝linux／`35087157691`＝WinNT，同 SHA `2b5b360a`）**兩平台全綠、`Program crashed` 計 0 次**（9 靶共 534 項；此前必崩之 `LexiconAssemblyTests` 為 193 項 30 套全綠）。**本項自此結清。** 附帶之同批改動：`TekkonTests` 之 `"[Tekkon] StringProcessingPerformance"` 門檻自 0.1 放寬至 0.2（`vChewing-LibVanguard` `caeaccc`／`vChewing-macOS` `3d7938a6`）——實測散佈：本機 0.016s／linux runner 0.034s／WinNT runner **0.1035 → 0.0560 s**（同一 runner 兩輪相差 1.85×），故 0.2 對最慢觀測值僅約 1.9× 餘裕、與 runner 自身抖動同量級；再遇 flake 宜升至 0.3。

### A2.2 開發注意事項

1. 始終保持對 Linux 與 Windows 的可建置性（透過 `#if canImport(Darwin)` 處理平台差異）。
2. TrieKit 不計畫直接支援 Regex Fuzzy Match；不完全讀音檢索需先經 Tekkon 的 `chop()` 拆解。
3. Homa 引擎取消了舊版 `LangModelProtocol` 協定，改用回調函式。
4. `LexiconAssembly` 不負責查詢結果的去重複化，該工作由 Homa 引擎完成。（Phase 213 前於本倉名為 `LexiconKit`。）
5. 下游 `vChewing_LangModelAssembly` 目前的預設 factory lookup 已由 `FactoryCoreLookupStrategy.configuredLookup` 表達；當 `partialMatchEnabled` 開啟時，這條預設路徑可走 partial-match path。`FactoryCoreLookupStrategy.strictSuperset` 則是獨立的 strict-superset strategy，不得將兩者混為一談。另在 plain BPMF / 倚天 DOS 與 cassette quick-result facade 上，`SupplementalLookupStrategy` 已明確區分 `.configuredLookup` / `.exactMatch` / `.partialMatch`；其中 `configuredLookup` 保留各 backend default，不等於強制 exact，也不等於強制 partial。Phase 36 結束後，repo 內唯一 canonical public lookup surface 已是 `LMInstantiator.lookupHub`；舊 `query*` / `cassetteQuickSetsFor` wrappers 已自 current tree 移除。若未來再做類似 breaking cleanup，請直接以 `Phase036_Research.md` appendix 內的 P5 gate 與 kickoff template 為範本。
6. **Phase 46 後 `&` 字串編碼已從 Homa ↔ LMInstantiator 介面移除**。`Homa.Assembler` 現以 `[PossibleKey]` 儲存每個位置的可能讀音，並在 `assignNodes` 內部以笛卡爾積展開為精確 `[String]` 陣列後呼叫 `gramQuerier`。Typewriter 不再產生 `&` 字串；TrieKit `keysChopped:` 仍保留內部 `&` 處理供自身 partial-match 路徑使用，但 Homa 傳遞至 `LMInstantiator` 的皆為精確陣列。
6. 下游測試 fixture 的 typeID 必須與 VanguardLexicon 建置器的實際 typeID 分配一致（Phase 09 教訓：`_punctuation_list` 等 `_` 前綴 key 在 production 為 typeID=4，fixture 誤標為 5/6 導致漏洞）。
7. 不要再把 Phase 35 理解成「回退到下游 `FactoryTextMapLexicon`」。那條路徑只屬中間驗證；最終 source of truth 是 canonical `VanguardTrie.TextMapTrie` 與 `VanguardTrieProtocol.getEntryGroups(...)`。
8. **`SwiftExtension` 符號之鏈接前提（2026-09-17，Phase 225 實錄）**：`SwiftExtension` 已析出為獨立 dynamic 產品 `VanguardSwiftExtension`，而 `libVanguard.dylib` 對它只有 `LC_LOAD_DYLIB`（**非 `LC_REEXPORT_DYLIB`**），且 SwiftPM 6.4 起之預設引擎（`swiftbuild`）**不代 dynamic 產品傳導其動態依賴**（舊 llbuild 引擎會代傳，故 6.3 世代不顯此坑）。故凡直接使用 SwiftExtension 符號之**靶**——**含只靠 `@_exported import SwiftExtension` 轉出、自身沒寫 import 者**——其 manifest 必須自行宣告 `.product(name: "VanguardSwiftExtension", package: "VanguardSwiftExtension")`（套件依賴之 `path:` 指 `../vChewing_OSNeutral_LibVanguard/Deps/VanguardSwiftExtension`），或至少鏈一個「已宣告它」的**靜態**產品（`IMKUtils`／`OSFrameworkImpl`／`InstallerAssembly4Darwin` 三家即已如此；靜態產品會把自身動態依賴往下帶）。只鏈 `Vanguard` 這一 dynamic 產品不足——`Jad_BookmarkManager` 即因此在 macOS CI 之 test 靶 link 期報 `Undefined symbols: SwiftExtension.mainSync…`（`mainSync` 於 `deinit` 內被呼叫）。另註：5.10 側之 `VanguardSwiftExtension` 是 `.static`，無此缺口。**本倉盤點（2026-09-17）**：全倉使用 SwiftExtension 符號者 15 家，屬「裸露形狀」（只鏈 dynamic 的 `Vanguard`、自身未宣告）者為 `Jad_BookmarkManager`／`vChewing_FolderMonitor`／`vChewing_UpdateSputnik` 三家——皆已補齊（6.4 ＋ 5.10 兩側各一檔）；其餘八家（`SettingsUI`／`MainAssembly4Darwin`／`Shared_DarwinImpl`／`CandidateWindow`／`NotifierUI`／`PopupCompositionBuffer`／`TooltipUI`／`Uninstaller`）係經**靜態**產品鏈獲得（`CandidateWindow` 為兩層：`Shared_DarwinImpl`→`IMKUtils`），惟這層安全性寫在**鄰居**的 manifest 內、不在自己的 manifest 內——改動上游依賴（尤其移除某家的產品宣告）前須重查此鏈。
9. **就地加詞／濾除之即時生效紀律（2026-09-17，Phase 226 實錄）**：寫檔後的就地生效唯一靠 `LXFacade.insertTemporaryData`；其後必須緊接 `InputHandler.updateUnigramData()`（順序顛倒即無效——熱重載（`.refreshExisting`）查不到尚未入庫的臨時資料）。凡新增查詢快取路徑，該路徑之快取鍵必須能被 `insertTemporaryData` 失效（現行作法是全量 `unigramLRUCache.removeAll`，因替代讀音路徑以 `ALT\t…` 定址、無法以 keyChain 枚舉）；凡在非同步重載前清空資料來源，必須確認該清除不會被「就地熱重載」撞上（現行作法：同步路徑照舊即清，非同步路徑延後至 `replaceData`／`onFailure`，且只清本次將重新載入者）。

---

## 九、關鍵檔案速查

| 檔案路徑 | 說明 |
|----------|------|
| `Package.swift` | SPM 套件定義（package name `LibVanguard`、出貨 product `Vanguard`） |
| `makefile` | `make lint` / `make format` / `make lintFormat` / `make lintFormatUncommitted` / `make test` / `make dockertest` |
| `EVOLUTION_MEMO.md` | 各模組研發備忘錄（人工維護） |
| `.github/workflows/test_{ubuntu,winnt,darwin}_LibVanguard.yml` | CI（Phase 213 新增；倉根直接 `swift test --no-parallel`） |
| `Sources/Homa/Homa_MainComponents/Homa_Assembler.swift` | 組字核心引擎（Phase 05：跨插入 gram query cache / 熱路徑去 allocation） |
| `Sources/Homa/Homa_MainComponents/Homa_PathFinder.swift` | 動態規劃路徑搜尋 |
| `Sources/Tekkon/Tekkon_SyllableComposer.swift` | 音節合成引擎 |
| `Sources/TrieKit/VanguardTrie_Core.swift` | Trie 核心資料結構 |
| `Sources/TrieKit/TrieProtocol.swift` | Trie 共用查詢邏輯（Phase 35：`getEntryGroups(...)` / existential fast path） |
| `Sources/TrieKit/TrieTextMap_Core.swift` | TextMapTrie canonical specialized backend（Phase 35） |
| `Sources/TrieKit/VanguardTrieIO.swift` | Trie IO（Vanguard Pragma TextMap 序列化/反序列化 + 結構驗證） |
| `Sources/TrieKit/TK_QueryBuffer.swift` | 7 秒動態清理查詢快取 |
| `Sources/LexiconAssembly/LXFacade.swift` | 辭典查詢門面（原 `LMInstantiator`／`LMI`） |
| `Sources/LexiconAssembly/LX_GramConcatAPI.swift` | 元圖查詢結果聚合（構造化排序 / 具型雜湊） |
| `Sources/LexiconAssembly/LXGramSupplyHub.swift` | 多來源元圖供應中樞（Phase 212） |
| `Sources/LexiconAssembly/SubLMs/LXPerceptor.swift` | 使用者習慣洞察器（POM；原 `Perceptor`） |
| `Sources/LibVanguard/` | 作業系統中立層（輸入控制器與狀態機；原 `OSNeutralAssembly`） |
| `Tests/LexiconAssemblyTests/` | POM 測試族之大本營（含本倉獨有之 `POMDecayWindowTests.swift`／`LXPlainBopomofoEtenDOSTests.swift`） |

---

## 十、建置與開發

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
swift build
```

### 10.3 測試指令

```bash
make test          # Release 模式測試
make test-debug    # Debug 模式測試
make dockertest    # Docker 容器測試（Linux）
```

### 10.4 程式碼格式化

```bash
make lintFormatUncommitted  # 交差／commit 前慣用：僅對 tracked 且未 commit 的 Swift 檔依序執行 lint＋format
make lintFormat             # 全倉：SwiftLint 自動修正（先）＋ SwiftFormat（後）
make lint                   # 僅 SwiftLint 自動修正
make format                 # 僅 SwiftFormat（縮排 2 空格）
```

> 交差前「一次性運行」 `make lintFormatUncommitted` 即可（先 lint 後 format 的順序已內建）。注意 lint+format 可能將 `count == 0` 轉為 `.isEmpty`，需確認對應型別確有此屬性，否則改用 `.count * 1 == 0`。

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

> 5.10 側之 manifest（`Package@swift-5.10.swift`——Phase 216 先在聚合體與子套件各鋪一份，**Phase 217 起 `vChewing-macOS` 之 19 個 subpackage 各一份**）刻意**不宣告測試靶**、**不收 `vChewingSharedCLI`**、**`platforms: nil`**，產物一律 static；`Package@swift-6.0.swift`／`6.1.swift`（自 Phase 217 起另含 **`6.2.swift`／`6.3.swift`**）為 `#error` 封堵檔（令各該版 toolchain 明文拒絕建置）。擇定規則與其餘坑見 `vChewing-DevLogs/Research/Phase216_PostResearch.md` 與 `Phase217_SOP.md`。

#### 10.5.1 Phase 217：`vChewing-macOS` 全倉（19 個目錄）的逐包入口

**每個 subpackage 都自成一個可單獨驗證的單位**——各自六份 manifest（`Package.swift`@6.4 ＋ `Package@swift-5.10／6.0／6.1／6.2／6.3`）與**各一份 `makefile`**：

| 入口 | 用途 |
|---|---|
| `cd Packages/<name> && make build510` | **單包深挖**（產物落該包自己的 `.build/.legacy`；`make clean510` 清之） |
| `cd Packages && make build510-all` | **全倉批次**：逐包跑、個別失敗不中斷、逐包列 ✓／✗（`make clean510-all` 清全部分支） |
| `make build510-<目錄名>`（倉根 `Makefile`） | 同上的單包快捷；`make build510-swiftExtension` 走巢狀子套件 |

**性質**：這是**可建置性驗證（compilation test）**，**不是單元測試**——5.10 側的 manifest 與 makefile **刻意不含任何測試靶／測試目標**；測試一律在 6.4 側跑（§10.3）。

**5.10 側的原始碼層原則（P217 貫徹）**：SwiftUI 之任何內容——**含 `#Preview` 這類巨集**——一律整段圈進 `#if compiler(>=6.2)`；`nonisolated` 自 extension／型別標頭**下放到成員**；availability 用 `if #unavailable() {} else {}` 兩分支；`nonisolated deinit` 改樸素 `deinit`（內容以 `mainSync` 裹上）；`@Sendable` 閉包內不得碰 MainActor 成員（legacy 形狀為 `DispatchQueue.main.async { @MainActor in … }`）；**不得為消錯新增 `@MainActor`**（會殺死 ≤ macOS 10.14 的執行期相容性）。

**終點與驗收**：兩支終點產物 **`libInstallerAssembly4Darwin.a`（3.2 MB）** 與 **`libMainAssembly4Darwin.a`（26 MB）**（`file` → `current ar archive`、`vtool` → `not mach-o`，即不帶任何 load command、minOS 不進產物）；`make build510-all` 於 2026-09-15 達 **19／19 rc=0、0 error**，6.4 側 `swift build` rc=0＋**535 項測試 0 失敗**。

**現值一項例外（2026-09-16）**：`vChewing_MainAssembly4Darwin` 之 5.10 manifest 依事主指示**改回與 `Package.swift` 同構**（收遠端 `vChewing-VanguardLexicon` 依賴與兩支 build plugin），故**該包於 5.10 側復歸 rc≠0、全倉 18／19**——5.10 SwiftPM 對非根套件的 `unsafeFlags` 一律硬拒（該 lexicon 的 `CSQLite3` 靶帶 `.unsafeFlags(["-w"])`），`--disable-sandbox` 無效、改本地 `.package(path:)` 則撞 macOS 10.15 平台下限；**正解在 lexicon 倉**（見 `Phase217_SOP.md` §十四 **N4**）。

**本項已由 P218 接管（2026-09-16）**：lexicon 之 deploy 工具真正用上 Swift Concurrency（故其 manifest 須宣告 macOS 10.15），與本側 5.10 之 10.13 地板相衝；現行作法是 5.10 manifest 不再收該依賴與兩支 plugin（`make build510-all` 因而復歸 19／19 rc=0），「另尋資料注入他法」移入 P218——原因、實測與後續見 P218 之紀錄。（此補註同時取代上方「現值一項例外」所述之狀態。）

**Swift 6.2／6.3 之封堵（Phase 216 起、Phase 217 補齊）**：五個位置各鋪兩份 `#error` 封堵檔（兩倉 12 組 manifest 逐位元組相同），`Package.swift` 之 tools version 抬到 **6.4**，三系統 CI 之 toolchain pin 同批抬到 ≥6.4。**封堵訊息之正本模板**見 `Phase217_SOP.md` §十二 R22 末段（46 份封堵檔同構）。**測試紀律**：`swift test --no-parallel`（CLI 層）與 `@Suite(…, .serialized)`（型別層）**缺一不可**，且單元測試下 `LXFacade.asyncLoadingUserData` 恆為 `false`——見同 SOP §十二 R23。

#### 10.5.2 雙 toolchain 之終點推進（Phase 218 起）

5.10 側自此**真的產出可交付的執行檔**：倉根 `Package@swift-5.10.swift` 出 `vChewing` 與 `vChewingInstallerLegacy`。

- **libArcLite**：以 `-Xlinker -force_load -Xlinker ./LegacyZone/ARCLite/libarclite_macosx.a` 摻入（`-L` ＋ `-larclite_macosx` 實測為虛——`ld` 逕以 SDK 版 libobjc 之匯出滿足符號、**不抽任何成員**；swift driver 亦不認裸 `-force_load`）。**只有 x86_64 支線**摻它（arm64 自 macOS 11 起 ARC 執行期即在 libobjc 內），故該 flag 依 triple 下在倉根 `makefile`。
- **執行期（兩段式 rpath）**：載入記錄保持 `@rpath/libswift*.dylib`，由 `BundleAppsLegacy` 把 Xcode 內 `usr/lib/swift-5.0|5.5/macosx` 之 back-deployment 副本放進 `<build-dir>/Frameworks/` 並追加 `@loader_path/Frameworks`——現行 macOS 之 `/usr/lib/swift/*` 由 dyld shared cache 供貨、故系統執行期勝出，10.9–10.13 才落到內嵌副本。**勿**改用 `install_name_tool -change` 逕指內嵌副本：那會令現行系統也載入 10.9 版本而 abort。該 plugin 另以 `pruneForeignRPATHs(of:)` 清掉建置機 toolchain 的絕對 `LC_RPATH`（`…/swift-5.10.1-RELEASE.xctoolchain/…`），只留 `/usr/lib/swift`、`@loader_path*`、`@executable_path/../Frameworks`。
- **入口與環境**：`make debugLegacy`／`releaseLegacy`／`archiveLegacy`／`cleanLegacy`（scratch `.build/.legacy-root`）；`releaseLegacy` 另建 arm64 slice 並逐支 `lipo` 成 universal（`x86_64-apple-macosx10.9` ＋ `arm64-apple-macosx11.0`）。`DEVELOPER_DIR` **必須 pin 一個「預設 macOS SDK ≤ 14.x」的 Xcode（Xcode 15 即可，任何 ≤ 15.4 者等價）**——這是 `swift build` 一併編譯的 build plugin `BundleAppsLegacy` 之 SDK 來源（`--sdk`／`SDKROOT`／`-Xswiftc -sdk` 三者對它**皆無效**，實測 plugin 之 `commandLine` 記的仍是 active dev dir 的預設 SDK）；CLT 不能當 dev dir（無 `Platforms/`），自製 dev dir 會被 `xcode-select` 判 malformed。C／ObjC 靶另須 `-Xcc -target -Xcc x86_64-apple-macosx10.9`（`-Xcc -mmacosx-version-min` 會被 SwiftPM 自己那條 `-target …10.13` 壓住；clang 讓後出現的 `-target` 勝）。`LEGACY_SDK` 綁 **CLT 那份** `/Library/Developer/CommandLineTools/SDKs/MacOSX13.3.sdk`（Xcode 15 內的同名目錄只是指過去的 symlink；該 SDK **非現行 CLT 所附**——現行 CLT 已把它改成移除包，換機須自行自 macOS 13.3 之 CLT／Xcode 14.3 備妥）。
- **`archiveLegacy`（2026-09-17 補）**：前置 `releaseLegacy`，再令 plugin 以 `--archive` 組出 `Build/Products/vChewingInstallerLegacy-<stamp>hrs.xcarchive`（內含安裝程式（IME 棲於其 `Contents/Resources/`）與兩支執行檔之 dSYM，外加 `Info.plist` 之 `ArchiveVersion`／`ApplicationProperties`），並搬進 `~/Library/Developer/Xcode/Archives/<date>/` 供 Xcode Organizer 手動以 Developer ID 簽名與公證；archive 之所以不直接寫進那裡，是因為 command plugin 之寫入權止於套件目錄。
- **10.9 專屬陷阱**：① **絕不可把 Optional block 交給 libdispatch**——`setEventHandler(handler: nil)` 會被本路徑內建的 Swift 5.0 Dispatch shim 原樣轉成 `dispatch_source_set_event_handler(source, NULL)`，而 10.9 的 libdispatch 對此直接 BUG（SIGILL）；一律改傳 `{}`（現代 libdispatch 容忍 NULL，故 6.4 側從未顯露）。② 辭典資產**自動建置**：`lexiconLegacy` 是 `bundleLegacy` 之前置、跑 `LegacyZone/LexiconBuildTrigger`；其 config 變數是 `LEXICON_CONFIG`（預設 `release`）、**刻意不叫 `LEGACY_CONFIG`**（後者指 app 的 config 且會隨 sub-make 外洩，實測會把詞典建置拖回 debug）。③ `CGRect.seniorTheBeast` 這類跨模組常數一律是各消費檔**檔尾的 `fileprivate` 常數**、不放 `SwiftExtension`（Swift 5.10 `-O` 對跨模組 `CGRect` 常數會 SIL verifier 崩潰）；`vChewing-OSX-legacy` 逐檔同構。
- **concurrency**：整個 5.10 閉包**零 concurrency 引用**（每 slice 20／20 archive 乾淨、兩支執行檔無 `swift_task_*` 未定符號），`@rpath/libswift_Concurrency.dylib` 不再是任何載入記錄；`BundleAppsLegacy` 仍整批備齊該副本，屬未被引用的死重（事主 2026-09-16 裁定不用管）。
- **lexicon 無法被 5.10 側消費**：其 deploy 工具真正用上 Swift Concurrency（需 macOS 10.15），故 `MainAssembly4Darwin` 之 5.10 manifest 不收它——資料改由 `LegacyZone/LexiconBuildTrigger` 這一 throwaway 套件出帶外產出，再由 plugin 注入安裝程式之 `MainAssembly4Darwin_MainAssembly4Darwin.bundle`（`Bundle.currentSPM` 解析的即該 bundle）。
- **legacy 安裝程式的在地化名稱**：與主線共用同一份 `<lproj>`，故 Finder 顯示名原與主線相同；解法是 `LSHasLocalizedDisplayName`（兩側 plist 本已帶）＋ `LegacyZone/InstallerLocalizations/<lproj>/InfoPlist.strings` 的不同 `CFBundleName`，由 plugin 於複製 lproj 後 **merge**（非取代——`CFEULAContent` 必須存續）；IME 側對位者為 `LegacyZone/IMELocalizations/…`（把 `NSHumanReadableCopyright` 改寫為 `Aqua Special Build. …`，供 About 面板顯示）。落點刻意選在 `LegacyZone/`：`Sources/Installer_macOS/` 在 `vChewing.xcodeproj` 裡是同步根群組，把帶 `.lproj` 的新目錄放其下會被掃進**現代**安裝程式的資源 phase。`project.pbxproj` 事主明示**不動**。
- **現況（2026-09-17）**：10.9 真機之輸入法本體運作正常；安裝程式在 10.9 按「安裝」數秒即崩之缺陷已修（見上①）、**修後之 10.9 複驗尚未回報**；10.10／11.x 真機仍未驗。legacy 產物之總記憶體佔用實測**降至 macOS 15 Sequoia／Intel Mac 之水位**（開著偏好設定視窗亦僅 80 餘 MB），機理未查。**本路徑自此為 legacy 發行版之唯一建置來源**——`vChewing-OSX-Legacy` 已於 vChewing **4.8.0** 封存（僅存為 10.9 寫法之參照、不再回寫）。

## 十一、參考資料

- 詳見 `vChewing-DevLogs` 目錄的其餘 Markdown 檔案。
- `vChewing-LibVanguard/EVOLUTION_MEMO.md` 記錄了各模組的原始設計備忘錄。

---

> ⚠️ **注意**: 本文檔為 LLM 用的「格物致知」文件——只承載**現況**與**施工注意事項**。**最後更新：2026-09-18。**
>
> **沿革不再寫入本文檔（2026-09-17 修訂）**：逐 Phase 的施工記述一律見 `vChewing-DevLogs/DevReqsHistory.md`（逐 Phase 一行摘要）與 `vChewing-DevLogs/Reqs4LLM/Archive_P{…}/Reqs_0NN1-0NN0.md`（規格與實作全文）。先前於此逐 Phase 累積的長篇「最後更新」記述（Phase 201~223）已移除——那些內容本即 `DevReqsHistory.md` 各列的複寫，需要舊敘述時請看本檔的 git 歷史。此後本文檔只增刪「現況」與「施工注意事項」兩類內容。


---

## 十二、AI Agent 反應模式（Response Pattern）

> 本節供 AI Agent 參考，當用戶提出新的 Phase 開發任務時，應遵循以下標準流程。

### 12.1 工作流程（Workflow）

當用戶提出新的 Phase 需求時，按以下順序執行：

```
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: 讀取相關檔案                                           │
│  - 讀取用戶指定的 Phase 描述                                    │
│  - 讀取需要修改的原始碼檔案                                     │
│  - 確認現有實作與新需求的關聯                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: 程式碼實作                                             │
│  - 根據需求實作功能                                             │
│  - 遵循專案現有程式碼風格（Swift 6, @MainActor, 層級結構）      │
│  - 複用既有組件和工具函數                                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: 編譯驗證                                               │
│  - swift build（於 vChewing-LibVanguard/）                      │
│  - 確保無錯誤、無警告                                           │
│  - 如有錯誤立即修復                                             │
│  - 然後用 Xcode build 觸發 localized strings key 生成           │
│  - 完成 localization 之後再次重試編譯                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: 文件同步（並行執行）                                   │
│  ├─ vChewing-DevLogs/Reqs4LLM: Phase 規格與實作備忘錄           │
│  ├─ vChewing-DevLogs/DevReqsHistory.md: 追加 Phase 歷史摘要     │
│  ├─ vChewing-DevLogs/KnowledgeMemo4LLM.md: 更新標記與近期摘要   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 5: 彙總報告                                               │
│  - 列出所有變更的檔案                                           │
│  - 說明核心實作邏輯                                             │
│  - 確認編譯狀態                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 12.2 文件更新規則

| 檔案 | 更新時機 | 內容格式 |
|------|---------|----------|
| **vChewing-DevLogs/Reqs4LLM/Archive_P201-P300/Reqs_0221-0230.md**（現行卷） | 每個 Phase 必須 | `# Phase XX` 標題 + 規格說明 + `## Phase XX 實作結果` 小節（歸檔卷不再增改；惟對過往 Phase 之補記一律補進該 Phase 自己的記錄內——無論該卷是否已歸檔，回填規則見 §12.5） |
| **vChewing-DevLogs/DevReqsHistory.md** | 每個 Phase 必須 | 追加一行 `\| Phase XX \| 簡短描述 \|` |
| **KnowledgeMemo4LLM.md** | 每個 Phase 必須 | 更新 `最後更新` 標記，並按需要補上近期 phase 摘要或修正過時指引 |
| **UserGuide (4語言)** | 影響使用者操作時 | 在對應章節添加功能說明（鍵盤熱鍵、滑鼠操作等） |

### 12.3 程式碼實作原則

1. **最小變更原則**：只做必要的修改，不改動無關程式碼
2. **風格一致性**：
   - **勿在 Swift 原始碼正文內提及 Phase 編號**（各 Phase 規格之既有要求；原「使用 `// Phase XX:` 註解標記新代碼」之指引與此相牴觸，已於 Phase 210 更正）
   - 遵循現有命名慣例（如 `handleXxx`, `onXxx`）
   - 保持縮排和空行風格
3. **平台相容性**：
   - (今後會按需求補充)
4. **狀態管理**：
   - (今後會按需求補充)

### 12.4 常見任務類型

| 任務類型 | 典型檔案 | 注意事項 |
|----------|----------|----------|

### 12.5 回報格式範本

> 注意**各個 Phase 檔案內部的標題層級**：一級標題（`#`）僅保留給 `# Phase NNN`；`--------------------` 大分隔線亦僅保留於 Phase 之間。

```markdown
## 變更總結

### 程式碼變更

**檔案名稱.swift**:
- 變更項目 1
- 變更項目 2

### 文件更新

| 檔案 | 更新內容 | 注意事項 |
|------|---------|---------|
| vChewing-DevLogs/Reqs4LLM/Archive_P201-P300/Reqs_0221-0230.md（現行卷） | 新增 Phase XX 規格與實作備忘錄 | 一律寫入**現行卷**；**歸檔卷**（已滿 10 個 Phase、或經事主裁定結案者）不再增改。分卷以「十年前綴 `0NN1`–`0NN0`」為界、每卷至多 10 個 Phase（如 `Reqs_0201-0210.md` 收 Phase 201~210）；**同一區間內的新 Phase 續寫同一卷，不另立新卷**。該區間寫滿或結案後始自立為一卷，並置於 `Archive_P{首 Phase 所屬百位段}/`（現行卷尚未寫滿，故雖置於 `Archive_P201-P300/` 內仍屬現行卷）。**對過往 Phase 之補記不寫入現行卷**：無論該 Phase 所屬之卷是否已歸檔，補記一律逕補進**那個 Phase 自己的記錄內**，不得佔用其他 Phase 的記錄空間。 |
| vChewing-DevLogs/KnowledgeMemo4LLM.md | 根據專案實際情況更新內容（如適用） | 參考既往記錄的文書風格。 |
| vChewing-DevLogs/DevReqsHistory.md | 新增 Phase XX 到開發階段歷史 | 參考既往記錄的文書風格。 |

### 編譯狀態

✅ 編譯通過 / ❌ 有錯誤（說明）
```

### 12.6 工作細節附註

- 交差前注意與 L10n 有關的內容是否全部補齊。
- 如果要使用 tmp 目錄的話，請使用**所在倉庫根目錄**的 `tmp/` 或 `.tmp/`（例如 `vChewing-LibVanguard/tmp/`、`vChewing-DevLogs/tmp/`）、而非系統的 `/tmp/`。使用 `/tmp/` 這種 out-of-workspace 的路徑會迫使事主每次都得手動設定存取權限，非常麻煩。
- **腳本內的全形字元陷阱（2026-09-13 實錄）**：本工作區的 shell 常以 `LC_ALL=C` 執行，此時 bash 會把緊接在全形字元（如 `（`）之前的高位元組**一併視為變數名的一部分**——`log "…：$scheme（Debug）…"` 會以 `scheme\xef…: 未綁定的變數` 失敗（在 `set -u` 下直接中止腳本，且若已把 stderr 重導就完全看不出原因）。**凡變數緊鄰 CJK／全形字元者，一律寫成 `${var}`。** 同源的坑：Python `re` 的 `\b` 視中日韓字元為 word character，故 `\bTypewriter\b` 不會命中 `Typewriter的`（見 `DevReqsHistory.md` Phase 201 的〈方法學教訓〉）；腳本化取代 CJK 文本時請改用 `(?<![A-Za-z0-9_])`／`(?![A-Za-z0-9_])` 這類斷言。
- **跨平台 manifest 的 `platforms:` 陷阱（2026-09-14 實錄）**：`Package(platforms:)` 之參數型別是 **`[SupportedPlatform]?`**，故 **`platforms: []` 會讓 SwiftPM 報 `supported platforms can't be empty`**（Linux／Windows CI 當場炸），正解是 **`platforms: nil`**（＝不宣告平台限制）。要條件編譯分流者，須把變數宣告為 **optional**：`#if canImport(Darwin) let p: [SupportedPlatform]? = [.macOS(.v12)] #else let p: [SupportedPlatform]? = nil #endif`。**此誤在本機（Darwin）永遠測不出來**——務必以「把 `canImport(Darwin)` 反轉為假」的 scratch 套件預驗（見 `_MainWorkspace/tmp/p215LinuxSim` 之做法），或直接等 CI。
- 如果事主丟給您 Xcode Instruments Profile 檔案的話，可能會是二進位檔案，請先嘗試用 `xctrace export` 解讀成 XML 再分析。
- 每次交差之前「一次性運行」 `make lintFormatUncommitted` 這一條命令。如果事主明確要你對某些工作單獨 commit 的話，每次 commit 之前也請運行 `make lintFormatUncommitted`。該命令僅對 tracked 且未 commit 的 Swift 檔案下動作，且依序執行 SwiftLint 自動修正與 SwiftFormat（先 lint 後 format 的順序已內建）。但注意在運行之後也請 build 一次，因為這些自動修正對 `count == 0` 的範式會頑固地轉換成 `.isEmpty` 而不會檢查相關 type 是否有 `isEmpty` 這個 read-only property。發現這種情況的話，可以用 `.count * 1 == 0` 取代之。commit 的 title 格式是 `ModuleName // WhatHasBeenFixed`、且在 commit 的 description 的末尾單獨一行寫明 `(Phase XXX - Task YYY)`。Commit Titles 始終以 ASCII Period `.` 結尾，除非是疑問句時才使用 `?` 結尾。
- 給 ChatGPT、Codex、Raptor 的特殊指令：Do not intentionally stop with tasks incompleted to ask me whether you do the next step I already told you. Just do it. I have backups, hence no worry. // Claude、Kimi、GLM、QwenCoder 從來不用問這些問題，就能把這些事情全部做好。唯獨 ChatGPT、Codex、Raptor 不這樣，就很奇怪很令人窩火。
- **Phase 文書之用語與署名（事主 2026-09-18 定調）**：① Phase 檔頭之 `Assignee:` 行**必須同時寫明 Model 與 Harness**——形如 `Deepseek-v4-flash（Codewhale harness）。`；只寫「（harness）」而未冠 harness 之名、或把 harness 之名填進 model 位者（如 `Codewhale（harness）`），皆屬誤標。② 文書提及 GitHub issue 之發起人時：**非 ShikiSuen 者一律稱「工單樓主」**；「事主」一詞**專指 ShikiSuen 本人**（含其於 issue 串／討論區內之發言在內）。

---

> ⚠️ **注意**: 本文檔需要定期更新以反映最新程式碼狀態。如有發現過期內容，請及時修正。
