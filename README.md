# vChewing & LibVanguard 工作區 - DevLogs

本倉庫是 vChewing 專案的**跨倉開發記錄**，收納原位於 `vChewing-LibVanguard/DevPlans/` 的全部內容，現供整個 vChewing 組織跨倉使用——`vChewing-macOS`、`vChewing-OSX-Legacy`、`vChewing-LibVanguard`、`vChewing-VanguardLexicon` 等倉的 Phase 手術都記在這裡。

> vChewing 輸入法在「威注音時代（v4.1.2 版為止）」是以人力為主完成開發的。v4.1.3 版起屬於「唯音時代」，利用 LLM 提升開發效率。為了保證相關修改內容有據可查、便於之後的 LLM 工作或人力工作能夠了解情況，故整理此倉庫。

## 目錄結構

```text
vChewing-DevLogs/
├── KnowledgeMemo4LLM.md       # 架構知識 ＋ 給 AI Agent 的 Response Pattern（開工前必讀）
├── DevReqsHistory.md          # 逐 Phase 開發史摘要
├── Reqs4LLM/                  # Phase 需求書與實作記錄
│   ├── Reqs_Other_Pending_Phases.md
│   ├── Archive_P001-P100/     # 已凍結（Phase 01~100 收齊）
│   ├── Archive_P101-P200/     # 已凍結（Phase 101~200 收齊）
│   └── Archive_P201-P300/     # 未凍結；內含現行卷 Reqs_0201-0210.md（Phase 201~210）
├── Research/                  # 各 Phase 的研究報告
└── PendingFeatureReqs/        # FeatureRequest 類 PreResearch
```

## 使用方式

- **AI Agent**：開工前先讀 `KnowledgeMemo4LLM.md`，尤其其中的〈Response Pattern〉與 §12 的文件更新規則。新增記錄一律寫入**現行卷**（現為 `Archive_P201-P300/Reqs_0201-0210.md`，收 Phase 201~210）；已滿或已結案的歸檔卷不再增改，僅在本次 Phase 牽涉其所載記錄時，於該歸檔處補記一行簡述（何時／哪個 Phase／何種修改）。
- **人類讀者**：`DevReqsHistory.md` 是最快的入口（逐 Phase 一行摘要），要細節再進 `Reqs4LLM/` 或 `Research/`。

## 慣例

- 本倉庫所有文件內的路徑一律以**工作區根**為錨（`vChewing-DevLogs/…`、`vChewing-LibVanguard/…`、`vChewing-macOS/…`）。
- 文書以繁體中文（zh-Hant）撰寫。
- 臨時檔案請放倉庫根目錄的 `tmp/` 或 `.tmp/`（已 gitignore），勿用系統的 `/tmp/`。
- 分卷以「十年前綴 `0NN1`–`0NN0`」為界、每卷至多 10 個 Phase（如 `Reqs_0201-0210.md` 收 Phase 201~210），一律置於 `Archive_P{首 Phase 所屬百位段}/` 之下——該目錄同時容納**尚在續寫的現行卷**與已結案的歸檔卷。**同一區間內的新 Phase 續寫同一卷，不另立新卷**；卷滿或經事主裁定結案後，該卷不再增改。
- **「凍結」的定義**：`Archive_P…/` 桶要收齊該百位段的 **100 個 Phase** 才稱「凍結」；未滿 100 個 Phase 者只稱「已歸檔」，該桶仍會續收後續結案的分卷（現下的 `Archive_P201-P300/` 即屬後者）。

## 授權

本倉庫自身內容以 **LGPL-3.0-or-later** 授權，詳見 `COPYING` 與 `LICENSES/preferred/LGPL-3.0-or-later`。

倉內**引用**的程式碼與資料仍依其來源授權，不受本倉庫授權影響：

| 來源 | 授權 |
|---|---|
| `vChewing-LibVanguard` | LGPL-3.0-or-later（附 Swift 靜態連結例外） |
| `vChewing-macOS`／`vChewing-OSX-Legacy` | MIT-NTL |
| `vChewing-VanguardLexicon` | 3-Clause BSD（語料編譯器） |
| `vChewing-Homebrew` | AGPL-3.0 |

另有引自 ButKo BPMFVS 等第三方專案的片段，各依其原始授權，請洽各自上游。
