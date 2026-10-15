<!-- 本檔為 vChewing-DevLogs/KnowledgeMemo4LLM.md 之分卷；索引：../KnowledgeMemo4LLM.md
     開工前請先讀索引，再依〈三、任務→必讀分卷〉取用本檔。 -->

# 九、關鍵檔案速查

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
| `vChewing-macOS/Packages/vChewing_MainAssembly4Darwin/Sources/MainAssembly4Darwin/SessionController/SessionControllerSputnik.swift` | Darwin 側 IMK 回呼轉發（14 個類別層級 block）：controller 位址 → parity session 之解析、啟用／停用、`recognizedEvents` 與 `handleEvent`；查無 session 之四處分支留有 `UnresolvableController:` 日誌（Phase 291） |
| `Tests/LexiconAssemblyTests/` | POM 測試族之大本營（含本倉獨有之 `POMDecayWindowTests.swift`／`LXPlainBopomofoEtenDOSTests.swift`） |
| `vChewing-macOS/ValueAdd/WebConfigAssistant/` | 配置助手（Phase 241；**Phase 246 起免除 node／npm**）：TypeScript ＋ JXA 宿主、外部相依只有 `tsc`（**須原生版**）、單檔自足 HTML；入內跑 `make audit`／`make bundle`；建置與部署細節見該目錄之 `README.md` |
| `Sources/vChewingSharedCLI/VCSharedCLI_UserDefMetadata.swift` | `dump-userdef-metadata` 動詞（Phase 241）：導出 118 條 `UserDef` 之後設資料與四語系標籤，供助手防漂移；`--strict` 為 i18n 稽核 |

---

# 十一、參考資料

- 詳見 `vChewing-DevLogs` 目錄的其餘 Markdown 檔案。
- `vChewing-LibVanguard/EVOLUTION_MEMO.md` 記錄了各模組的原始設計備忘錄。

---

> ⚠️ **注意**: 本文檔為 LLM 用的「格物致知」文件——只承載**現況**與**施工注意事項**。**最後更新：2026-09-26。**
>
> **沿革不再寫入本文檔（2026-09-17 修訂）**：逐 Phase 的施工記述一律見 `vChewing-DevLogs/DevReqsHistory.md`（逐 Phase 一行摘要）與 `vChewing-DevLogs/Reqs4LLM/Archive_P{…}/Reqs_0NN1-0NN0.md`（規格與實作全文）。先前於此逐 Phase 累積的長篇「最後更新」記述（Phase 201~223）已移除——那些內容本即 `DevReqsHistory.md` 各列的複寫，需要舊敘述時請看本檔的 git 歷史。此後本文檔只增刪「現況」與「施工注意事項」兩類內容。
