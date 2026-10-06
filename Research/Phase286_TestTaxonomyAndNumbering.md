# Phase 286 研究：InputHandler／Session 單元測試之分類與編號新制

- 撰寫日期：2026-10-06。
- 適用範圍：`vChewing-LibVanguard/Tests/LibVanguardTests/` 之 `InputHandlerTests`（235 支）與 `SessionTests`（48 支）兩套，合計 **283 支**。
- 本檔為長篇推導與全量對照表；Phase 篇（`Reqs_0281-0290.md`）只留決定性取捨與驗證。
- 事主指示：**test case 與 test suite 之 customized human-friendly title 一律英文**（該內容不屬 inline comment／API documentation 之範疇）。

## 一、舊制之病灶（動工前逐項實測）

1. **兩套共用同一批數字區間**：`InputHandlerTests` 用 `test_IH1xx`～`IH7xx`，`SessionTests` 用裸 `test2xx`～`test5xx`；後者之 2xx／3xx／4xx／5xx 與前者之 IH2xx／IH3xx／IH4xx／IH5xx **完全重疊**（例：`IH204` 是「覆寫候選時之下鍵」、`test204` 是「空狀態遞交組字」）。
2. **同一區間在 IH 內部跨義**：5xx 既作「朗讀」（`IH501`–`IH503`、`IH511`）又作「混打空白鍵偏好」（`IH512`–`IH519`）；7xx 既作「打字模式閘門」（`IH701`–`IH706`）又作「POM 語境記憶」（`IH707`–`IH709`）。
3. **重號三對**：`IH111`（倚天獨占候選／符號表初值）、`IH303`（POM 附掛過濾／低權重建議）、`IH430`（倚天注音標點鍵／camelCase 前綴＋注音後綴）。
4. **字母後綴用法不一**：`IH103A`–`IH103F` 有基底 `IH103`；`IH112B` 卻無 `IH112A`；`IH108A`（磁帶退格）與 `IH108`（羅馬數字空格）義不相涉。
5. **空號**：`IH140`／`IH141`／`IH144`–`IH146`、`IH202`、`IH532`–`IH534`。
6. **檔名為歷史卷而非分類**：`InputHandlerTests_Cases1`–`Cases5`；`SessionTests` 更缺 `Cases1`／`Cases4`（其檔名之卷號從未補齊）。
7. **標題語言不一**：部分 `@Test("…")` 為中文，其餘無自訂標題。
8. **跨倉對照已失效**：`SessionTests` 之源頭註記稱「個案編號沿用 MainAssembly 測試案，方便與 `MainAssembly4Darwin` 之既有案例互相對照」，惟該對照歷經多輪改寫後名存實亡。

## 二、新制

**識別字（函式名）**：`test_<Suite>_<Category>_<NNN>_<Summary>`
- `<Suite>`＝`IH`（`InputHandlerTests`）／`SS`（`SessionTests`）——兩套自此各有獨立號域，跨套重號在構造上不可能。
- `<Category>`＝語義分類（見第三節）；分類進標識自身，故數字不再承載分類、亦不可能被跨用。
- `<NNN>`＝該（suite, category）內之三位序號（`001` 起）。
- `<Summary>`＝英文 PascalCase 摘要（由舊函式名之尾段取得，僅少數為可讀性而改寫）。

**顯示名（`@Test` 之第一引數）**：`[<Suite>-<Category>-<NNN>] <English sentence>`
- 每支測試皆有；**一律英文**。參數化測試之 `arguments:` 原樣保留於其後。
- 子案例標籤（原 `IH401A` 之類）一律改作 `<新 ID>.<字母>`（如 `IH-MixedAlnum-002.A`）——該標籤僅為斷言訊息之標籤、非測試身分。

**分類即檔案**：一分類一檔（`InputHandlerTests_<Category>.swift`／`SessionTests_<Category>.swift`），檔頭以 `// MARK: - <Suite>.<Category>` 起頭並附該分類之義界；檔內之子標記沿用原檔之 `// MARK:`（僅保留該分類之主要來源檔者）。

**suite 階層與序列化不變**：根 suite `LibVanguardTestsRoot`（`.serialized`）→ `InputHandlerTests` → `SessionTests` 之三層結構、以及 `.serialized` 之繼承關係一字未動——此為本靶共用行程內全域狀態之必要條件（見 `LibVanguardTests_Root.swift`）。

## 三、分類註冊表

### 3.1 `InputHandlerTests`（前綴 `IH`；235 支）

| 分類 | 支數 | 檔 | 義界 |
|---|---|---|---|
| `Composition` | 12 | `InputHandlerTests_Composition.swift` | 基本組句、逐字選字、遞交（含 BPMFVS 四態）與候選輪替、游標復原、覆寫候選時之下鍵。 |
| `Cassette` | 9 | `InputHandlerTests_Cassette.swift` | 磁帶（CIN）模組：快速選字、符號表多選、組筆區之滿筆長自動組字、溢位、退格與 Shift+方向、花牌鍵三明治。 |
| `InputMode` | 7 | `InputHandlerTests_InputMode.swift` | 特殊輸入模式：碼點輸入、羅馬數字（含空格鍵）、符號表狀態之組字區顯示、單獨聲調鍵與其 Enter 遞交。 |
| `CandidateOrder` | 8 | `InputHandlerTests_CandidateOrder.swift` | 候選序與讀音過濾／查詢：倚天排列之候選序強制（含 zai4）、非 CNS 讀音之降級單字仍可選、拼音去調前綴查詢四態。 |
| `FuriousPinyin` | 57 | `InputHandlerTests_FuriousPinyin.swift` | 狂拼（拼音狂打）：前方預覽、重切分、固化、跨邊界候選與反查、置頂猜測、copilot 全句組句、高亮與方向鍵、標記態、整詞簡拼、執行期狀態複位。 |
| `FuriousZhuyin` | 41 | `InputHandlerTests_FuriousZhuyin.swift` | 狂注（注音狂打）：自動切音節、簡拼 cells 與整詞候選、未完成讀音之顯示源、與中英混輸回退並存時之語義（含空白鍵陰平與 Shift+Space 逃生口）。 |
| `POM` | 25 | `InputHandlerTests_POM.swift` | 漸退記憶（POM）：漂白、附掛過濾、短鍵不劫長鍵、語境例外、多元組合，以及語境詞界（寫入側／讀取側／整合）。 |
| `MixedAlnum` | 66 | `InputHandlerTests_MixedAlnum.swift` | 中英混打：緩衝分流、auto-split、標點與符號語義、前導數字／大寫阻斷、英數閂滯狀態、槽序檢定開關、空白鍵行為偏好。 |
| `TypingMode` | 6 | `InputHandlerTests_TypingMode.swift` | 打字模式閘門：`typingMode` 真值表、`isPinyinFamilyTypingMode` 之紅線、兩顆狂打閘門之家族歸屬、熱鍵於下一拍之反映、SCPC 對拼音自動切音節之停用。 |
| `Narration` | 4 | `InputHandlerTests_Narration.swift` | 朗讀（旁白）：防禦性注音轉換、以 actualKeys 組字、後置聲調覆寫補朗讀與其內文提示抑制。 |

### 3.2 `SessionTests`（前綴 `SS`；48 支）

| 分類 | 支數 | 檔 | 義界 |
|---|---|---|---|
| `EventTriage` | 9 | `SessionTests_EventTriage.swift` | 事件分診：Home／End／時鐘鍵、Esc 變體、退格與刪除分支、小鍵盤、Shift 字母鍵偏好、候選狀態之呼叫、無效邊緣游標、輪替罕例、空狀態 Shift+Space 寬度。 |
| `Composition` | 3 | `SessionTests_Composition.swift` | 狀態遞交：`switchState` 空狀態遞交組字內容、其原文不滲 BPMFVS、SCPC 選取之原文。 |
| `CandidateWindow` | 7 | `SessionTests_CandidateWindow.swift` | 選字窗與候選：標點與符號選單、延伸操作、服務選單、候選預覽更新、關聯詞語（SCPC／非 SCPC）、候選過濾快捷鍵。 |
| `TooltipAndMarking` | 4 | `SessionTests_TooltipAndMarking.swift` | Tooltip 與標記：標記態提示之生成、混打讀音樣式、錨點隨未完成讀音後方之游標、強化組字區之 marker 不變量。 |
| `Lifecycle` | 11 | `SessionTests_Lifecycle.swift` | 啟用／停用：快速路徑、對當前副本之 no-op、反覆啟用之身分維持、CapsLock 重置遞交、打字模式提示之顯示／抑制／時序／收起。 |
| `HotKey` | 11 | `SessionTests_HotKey.swift` | 熱鍵：copilot 窗之 Shift 提示與 JKHL 之隔離、功能鍵（F1–F20）守護四態、Command 系未認領熱鍵之先遞交後交還。 |
| `UserPhrase` | 1 | `SessionTests_UserPhrase.swift` | 就地加詞：升權／降權／過濾於當前組字器立即生效。 |
| `ClientBridge` | 2 | `SessionTests_ClientBridge.swift` | 客體橋接：`AttributedString` 之標記段 API、QEMU 游標放行熱鍵之略過。 |

## 四、舊→新全量對照表（283 列）

| 新 ID | 新函式名 | 舊函式名 | 新檔 |
|---|---|---|---|
| `IH-CandidateOrder-001` | `test_IH_CandidateOrder_001_ETenExclusiveCandidatesAppendAtTailWithoutReordering` | `test_IH111_ETenExclusiveCandidatesAppendAtTailWithoutReordering` | `InputHandlerTests_CandidateOrder.swift` |
| `IH-CandidateOrder-002` | `test_IH_CandidateOrder_002_ETenSequenceEnforcementStillReordersCandidates` | `test_IH112_ETenSequenceEnforcementStillReordersCandidates` | `InputHandlerTests_CandidateOrder.swift` |
| `IH-CandidateOrder-003` | `test_IH_CandidateOrder_003_ETenSequenceEnforcementWithZai4PreservesZai4ZaiOrder` | `test_IH112B_ETenSequenceEnforcementWithZai4PreservesZai4ZaiOrder` | `InputHandlerTests_CandidateOrder.swift` |
| `IH-CandidateOrder-004` | `test_IH_CandidateOrder_004_FilterNonCNSReadingsStillAllowsSelectingDemotedSingleKanji` | `test_IH113_FilterNonCNSReadingsStillAllowsSelectingDemotedSingleKanji` | `InputHandlerTests_CandidateOrder.swift` |
| `IH-CandidateOrder-005` | `test_IH_CandidateOrder_005_PinyinTonelessQueryUsesStemPartialMatch` | `test_IH114A_PinyinTonelessQueryUsesStemPartialMatch` | `InputHandlerTests_CandidateOrder.swift` |
| `IH-CandidateOrder-006` | `test_IH_CandidateOrder_006_PinyinExplicitToneKeepsFullMatch` | `test_IH114B_PinyinExplicitToneKeepsFullMatch` | `InputHandlerTests_CandidateOrder.swift` |
| `IH-CandidateOrder-007` | `test_IH_CandidateOrder_007_PinyinTonelessQueryDoesNotMatchLongerSyllableStem` | `test_IH114C_PinyinTonelessQueryDoesNotMatchLongerSyllableStem` | `InputHandlerTests_CandidateOrder.swift` |
| `IH-CandidateOrder-008` | `test_IH_CandidateOrder_008_PinyinContinuousStemAutoChopsLeadingReadings` | `test_IH114D_PinyinContinuousStemAutoChopsLeadingReadings` | `InputHandlerTests_CandidateOrder.swift` |
| `IH-Cassette-001` | `test_IH_Cassette_001_CassetteQuickPhraseSelection` | `test_IH104_CassetteQuickPhraseSelection` | `InputHandlerTests_Cassette.swift` |
| `IH-Cassette-002` | `test_IH_Cassette_002_CassetteQuickPhraseSymbolTableMultiple` | `test_IH105_CassetteQuickPhraseSymbolTableMultiple` | `InputHandlerTests_Cassette.swift` |
| `IH-Cassette-003` | `test_IH_Cassette_003_CassetteAutoCompositeWithLongestPossibleKey` | `test_IH105A_CassetteAutoCompositeWithLongestPossibleKey` | `InputHandlerTests_Cassette.swift` |
| `IH-Cassette-004` | `test_IH_Cassette_004_CassetteOverflowDoesNotLeakToBlockedDataTrap` | `test_IH105B_CassetteOverflowDoesNotLeakToBlockedDataTrap` | `InputHandlerTests_Cassette.swift` |
| `IH-Cassette-005` | `test_IH_Cassette_005_CassetteBackspaceWorksAtFullCalligrapherLength` | `test_IH105C_CassetteBackspaceWorksAtFullCalligrapherLength` | `InputHandlerTests_Cassette.swift` |
| `IH-Cassette-006` | `test_IH_Cassette_006_CassetteShiftBackspaceDisassemblesPreviousCalligraph` | `test_IH105D_CassetteShiftBackspaceDisassemblesPreviousCalligraph` | `InputHandlerTests_Cassette.swift` |
| `IH-Cassette-007` | `test_IH_Cassette_007_CassetteShiftQuestionTypesAnySingleCharKey` | `test_IH105E_CassetteShiftQuestionTypesAnySingleCharKey` | `InputHandlerTests_Cassette.swift` |
| `IH-Cassette-008` | `test_IH_Cassette_008_CassetteWildcardSandwichStaysInCalligrapher` | `test_IH105F_CassetteWildcardSandwichStaysInCalligrapher` | `InputHandlerTests_Cassette.swift` |
| `IH-Cassette-009` | `test_IH_Cassette_009_CassetteBackspaceShrinksCalligrapher` | `test_IH108A_CassetteBackspaceShrinksCalligrapher` | `InputHandlerTests_Cassette.swift` |
| `IH-Composition-001` | `test_IH_Composition_001_BasicSentenceComposition` | `test_IH101_BasicSentenceComposition` | `InputHandlerTests_Composition.swift` |
| `IH-Composition-002` | `test_IH_Composition_002_BasicSCPCTyping` | `test_IH102_BasicSCPCTyping` | `InputHandlerTests_Composition.swift` |
| `IH-Composition-003` | `test_IH_Composition_003_MiscCommissionTest` | `test_IH103_MiscCommissionTest` | `InputHandlerTests_Composition.swift` |
| `IH-Composition-004` | `test_IH_Composition_004_MiscCommissionButKoBPMFVS` | `test_IH103A_MiscCommissionButKoBPMFVS` | `InputHandlerTests_Composition.swift` |
| `IH-Composition-005` | `test_IH_Composition_005_ButKoBPMFVSDisplayReflection` | `test_IH103B_ButKoBPMFVSDisplayReflection` | `InputHandlerTests_Composition.swift` |
| `IH-Composition-006` | `test_IH_Composition_006_ButKoBPMFVSPlainEnterCommitsRawText` | `test_IH103C_ButKoBPMFVSPlainEnterCommitsRawText` | `InputHandlerTests_Composition.swift` |
| `IH-Composition-007` | `test_IH_Composition_007_ButKoBPMFVSMarkingStateDoesNotPollute` | `test_IH103D_ButKoBPMFVSMarkingStateDoesNotPollute` | `InputHandlerTests_Composition.swift` |
| `IH-Composition-008` | `test_IH_Composition_008_ButKoBPMFVSCandidatePreviewKeepsRawStateInSync` | `test_IH103E_ButKoBPMFVSCandidatePreviewKeepsRawStateInSync` | `InputHandlerTests_Composition.swift` |
| `IH-Composition-009` | `test_IH_Composition_009_MarkingStateRawTextPassing` | `test_IH103F_MarkingStateRawTextPassing` | `InputHandlerTests_Composition.swift` |
| `IH-Composition-010` | `test_IH_Composition_010_RevolvingCandidates` | `test_IH201_RevolvingCandidates` | `InputHandlerTests_Composition.swift` |
| `IH-Composition-011` | `test_IH_Composition_011_CursorPlacementRestoreAfterSelectingCandidate` | `test_IH203_CursorPlacementRestoreAfterSelectingCandidate` | `InputHandlerTests_Composition.swift` |
| `IH-Composition-012` | `test_IH_Composition_012_DropKeyAgainstAnOverriddenCandidate` | `test_IH204_DropKeyAgainstAnOverriddenCandidate` | `InputHandlerTests_Composition.swift` |
| `IH-FuriousPinyin-001` | `test_IH_FuriousPinyin_001_FuriousTypingPreviewsFrontReading` | `test_IH116A_FuriousTypingPreviewsFrontReading` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-002` | `test_IH_FuriousPinyin_002_FuriousTypingDisabledKeepsRawPinyinDisplay` | `test_IH116B_FuriousTypingDisabledKeepsRawPinyinDisplay` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-003` | `test_IH_FuriousPinyin_003_FuriousTypingEnterSolidifiesThenCommitsPreviewedFront` | `test_IH116C_FuriousTypingEnterSolidifiesThenCommitsPreviewedFront` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-004` | `test_IH_FuriousPinyin_004_FuriousTypingAttachesFrontCandidates` | `test_IH117A_FuriousTypingAttachesFrontCandidates` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-005` | `test_IH_FuriousPinyin_005_FuriousTypingShiftSelection` | `test_IH117B_FuriousTypingShiftSelection` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-006` | `test_IH_FuriousPinyin_006_FuriousTypingPlainDigitKeyKeepsToneSemantics` | `test_IH117C_FuriousTypingPlainDigitKeyKeepsToneSemantics` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-007` | `test_IH_FuriousPinyin_007_SCPCForcesFuriousTypingInert` | `test_IH117D_SCPCForcesFuriousTypingInert` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-008` | `test_IH_FuriousPinyin_008_FuriousTypingResegmentsFangAn` | `test_IH118A_FuriousTypingResegmentsFangAn` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-009` | `test_IH_FuriousPinyin_009_FuriousTypingNoResegmentationWhenDisabled` | `test_IH118B_FuriousTypingNoResegmentationWhenDisabled` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-010` | `test_IH_FuriousPinyin_010_FuriousTrailPopOnBackspace` | `test_IH118C_FuriousTrailPopOnBackspace` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-011` | `test_IH_FuriousPinyin_011_FuriousTrailInvalidatedByConsolidateNode` | `test_IH118D_FuriousTrailInvalidatedByConsolidateNode` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-012` | `test_IH_FuriousPinyin_012_FuriousTypingSpaceSolidifiesAndOpensCandidateWindow` | `test_IH119A_FuriousTypingSpaceSolidifiesAndOpensCandidateWindow` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-013` | `test_IH_FuriousPinyin_013_FuriousTypingDownArrowSolidifiesAndOpensCandidateWindow` | `test_IH119B_FuriousTypingDownArrowSolidifiesAndOpensCandidateWindow` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-014` | `test_IH_FuriousPinyin_014_FuriousTypingLetterKeyNotSolidifiedButEnterSolidifies` | `test_IH119C_FuriousTypingLetterKeyNotSolidifiedButEnterSolidifies` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-015` | `test_IH_FuriousPinyin_015_FuriousTypingSuppressesTooltipWhenCandidatesShow` | `test_IH119D_FuriousTypingSuppressesTooltipWhenCandidatesShow` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-016` | `test_IH_FuriousPinyin_016_FuriousTypingSolidifyingIncompletePrefixInvalidatesTrail` | `test_IH119E_FuriousTypingSolidifyingIncompletePrefixInvalidatesTrail` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-017` | `test_IH_FuriousPinyin_017_FuriousTypingCandidatesIncludeCrossBoundaryWord` | `test_IH120A_FuriousTypingCandidatesIncludeCrossBoundaryWord` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-018` | `test_IH_FuriousPinyin_018_FuriousTypingShiftSelectionConfirmsCrossBoundaryWord` | `test_IH120B_FuriousTypingShiftSelectionConfirmsCrossBoundaryWord` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-019` | `test_IH_FuriousPinyin_019_FuriousTypingUnfinishedReadingExposedViaTopPane` | `test_IH120C_FuriousTypingUnfinishedReadingExposedViaTopPane` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-020` | `test_IH_FuriousPinyin_020_FuriousTypingNoCrossBoundaryWhenAssemblerEmpty` | `test_IH120D_FuriousTypingNoCrossBoundaryWhenAssemblerEmpty` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-021` | `test_IH_FuriousPinyin_021_FuriousTypingPinsCrossBoundaryWordAtTop` | `test_IH121A_FuriousTypingPinsCrossBoundaryWordAtTop` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-022` | `test_IH_FuriousPinyin_022_FuriousTypingShiftOneConfirmsTopCrossBoundaryWord` | `test_IH121B_FuriousTypingShiftOneConfirmsTopCrossBoundaryWord` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-023` | `test_IH_FuriousPinyin_023_FuriousTypingUnfinishedReadingBypassesVerticalGuard` | `test_IH121C_FuriousTypingUnfinishedReadingBypassesVerticalGuard` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-024` | `test_IH_FuriousPinyin_024_FuriousTypingDisplayUsesCopilotJointComposition` | `test_IH122A_FuriousTypingDisplayUsesCopilotJointComposition` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-025` | `test_IH_FuriousPinyin_025_FuriousTypingEnterSolidifiesThenCommitsCopilotJointText` | `test_IH122B_FuriousTypingEnterSolidifiesThenCommitsCopilotJointText` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-026` | `test_IH_FuriousPinyin_026_FuriousTypingBackwardArrowSolidifiesThenMovesCursor` | `test_IH122C_FuriousTypingBackwardArrowSolidifiesThenMovesCursor` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-027` | `test_IH_FuriousPinyin_027_FuriousTypingHighlightPreviewReflectsCandidate` | `test_IH123A_FuriousTypingHighlightPreviewReflectsCandidate` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-028` | `test_IH_FuriousPinyin_028_FuriousTypingEnterSolidifiesHighlightedCandidateThenCommits` | `test_IH123B_FuriousTypingEnterSolidifiesHighlightedCandidateThenCommits` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-029` | `test_IH_FuriousPinyin_029_FuriousTypingCursorKeyRejectedWithoutCopilotWindow` | `test_IH123C_FuriousTypingCursorKeyRejectedWithoutCopilotWindow` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-030` | `test_IH_FuriousPinyin_030_FuriousTypingCursorKeySolidifiesAndNavigatesCandidates` | `test_IH123D_FuriousTypingCursorKeySolidifiesAndNavigatesCandidates` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-031` | `test_IH_FuriousPinyin_031_FuriousTypingShiftBackwardSolidifiesThenMarks` | `test_IH124A_FuriousTypingShiftBackwardSolidifiesThenMarks` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-032` | `test_IH_FuriousPinyin_032_ShiftBackwardConfirmsCompletableReadingThenMarks` | `test_IH124B_ShiftBackwardConfirmsCompletableReadingThenMarks` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-033` | `test_IH_FuriousPinyin_033_ShiftBackwardRejectsIncompleteReading` | `test_IH124C_ShiftBackwardRejectsIncompleteReading` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-034` | `test_IH_FuriousPinyin_034_FuriousTypingShiftBackwardDoesNotRecurseWithVisibleWindow` | `test_IH125A_FuriousTypingShiftBackwardDoesNotRecurseWithVisibleWindow` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-035` | `test_IH_FuriousPinyin_035_FuriousTypingSpaceConsumedAfterSolidify` | `test_IH125B_FuriousTypingSpaceConsumedAfterSolidify` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-036` | `test_IH_FuriousPinyin_036_FuriousTypingBackspaceThenSpaceRevolves` | `test_IH126A_FuriousTypingBackspaceThenSpaceRevolves` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-037` | `test_IH_FuriousPinyin_037_FuriousTypingAutoCommitCommitsCopilotJointText` | `test_IH126B_FuriousTypingAutoCommitCommitsCopilotJointText` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-038` | `test_IH_FuriousPinyin_038_FuriousTypingSpaceSolidificationMergesLongWord` | `test_IH129_FuriousTypingSpaceSolidificationMergesLongWord` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-039` | `test_IH_FuriousPinyin_039_FuriousTypingTabSolidifiesThenRevolves` | `test_IH130_FuriousTypingTabSolidifiesThenRevolves` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-040` | `test_IH_FuriousPinyin_040_FuriousTypingShiftTabSolidifiesThenRevolvesReverse` | `test_IH131_FuriousTypingShiftTabSolidifiesThenRevolvesReverse` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-041` | `test_IH_FuriousPinyin_041_FuriousTypingAbbreviatedWholeWordCandidates` | `test_IH132_FuriousTypingAbbreviatedWholeWordCandidates` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-042` | `test_IH_FuriousPinyin_042_FuriousTypingAbbreviatedWholeWordSelectionWritesActualReadings` | `test_IH133_FuriousTypingAbbreviatedWholeWordSelectionWritesActualReadings` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-043` | `test_IH_FuriousPinyin_043_FuriousTypingAbbreviatedSpaceSolidifiesTopCandidate` | `test_IH134_FuriousTypingAbbreviatedSpaceSolidifiesTopCandidate` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-044` | `test_IH_FuriousPinyin_044_FuriousTypingCopilotWindowFrontsPOMSuggestion` | `test_IH135_FuriousTypingCopilotWindowFrontsPOMSuggestion` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-045` | `test_IH_FuriousPinyin_045_FuriousTypingAbbreviationAutoAppliesClearWinner` | `test_IH139_FuriousTypingAbbreviationAutoAppliesClearWinner` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-046` | `test_IH_FuriousPinyin_046_FuriousTypingAbbreviationAmbiguousStays` | `test_IH142_FuriousTypingAbbreviationAmbiguousStays` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-047` | `test_IH_FuriousPinyin_047_FuriousTypingXianShengNotSplit` | `test_IH143_FuriousTypingXianShengNotSplit` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-048` | `test_IH_FuriousPinyin_048_FuriousTypingCoSegmentedOffersEnterCopilotWindow` | `test_IH147_FuriousTypingCoSegmentedOffersEnterCopilotWindow` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-049` | `test_IH_FuriousPinyin_049_FuriousTypingSelectingCoSegmentedOfferReplacesTrail` | `test_IH148_FuriousTypingSelectingCoSegmentedOfferReplacesTrail` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-050` | `test_IH_FuriousPinyin_050_FuriousTypingCoSegmentedOfferRanksBeforeSingleSyllables` | `test_IH149_FuriousTypingCoSegmentedOfferRanksBeforeSingleSyllables` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-051` | `test_IH_FuriousPinyin_051_FuriousTypingTamaPreviewNoDuplicate` | `test_IH150_FuriousTypingTamaPreviewNoDuplicate` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-052` | `test_IH_FuriousPinyin_052_FuriousCopilotWindowDedupsPOMFrontedCandidate` | `test_IH151_FuriousCopilotWindowDedupsPOMFrontedCandidate` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-053` | `test_IH_FuriousPinyin_053_FuriousCopilotWindowRejectsOversizedPOMSuggestion` | `test_IH152_FuriousCopilotWindowRejectsOversizedPOMSuggestion` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-054` | `test_IH_FuriousPinyin_054_FuriousPunctuationSolidifiesThenInserts` | `test_IH153_FuriousPunctuationSolidifiesThenInserts` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-055` | `test_IH_FuriousPinyin_055_FuriousLongAbbreviationKeepsFrontLetters` | `test_IH154_FuriousLongAbbreviationKeepsFrontLetters` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-056` | `test_IH_FuriousPinyin_056_FuriousConfigResetGranularity` | `test_IH449_FuriousConfigResetGranularity` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousPinyin-057` | `test_IH_FuriousPinyin_057_FuriousCopilotListsCrossBoundaryWholeWords` | `test_IH507_FuriousCopilotListsCrossBoundaryWholeWords` | `InputHandlerTests_FuriousPinyin.swift` |
| `IH-FuriousZhuyin-001` | `test_IH_FuriousZhuyin_001_ZhuyinFuriousAutoChopsConsecutiveSyllables` | `test_IH155_ZhuyinFuriousAutoChopsConsecutiveSyllables` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-002` | `test_IH_FuriousZhuyin_002_IncompleteSyllableIsNotChopped` | `test_IH156_IncompleteSyllableIsNotChopped` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-003` | `test_IH_FuriousZhuyin_003_DynamicLayoutSlotOverwriteIsNotChopped` | `test_IH157_DynamicLayoutSlotOverwriteIsNotChopped` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-004` | `test_IH_FuriousZhuyin_004_ToneKeysNeverTriggerAutoChop` | `test_IH158_ToneKeysNeverTriggerAutoChop` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-005` | `test_IH_FuriousZhuyin_005_ZhuyinFuriousIsInactiveUnderSCPC` | `test_IH159_ZhuyinFuriousIsInactiveUnderSCPC` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-006` | `test_IH_FuriousZhuyin_006_UnfinishedReadingIsTheComposerSyllableInZhuyinFurious` | `test_IH160_UnfinishedReadingIsTheComposerSyllableInZhuyinFurious` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-007` | `test_IH_FuriousZhuyin_007_ZhuyinFuriousCopilotWindowAndInPlaceSelection` | `test_IH161_ZhuyinFuriousCopilotWindowAndInPlaceSelection` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-008` | `test_IH_FuriousZhuyin_008_FrontReadPointsUnderZhuyinFurious` | `test_IH162_FrontReadPointsUnderZhuyinFurious` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-009` | `test_IH_FuriousZhuyin_009_ZhuyinFuriousDoesNotRecordTrail` | `test_IH163_ZhuyinFuriousDoesNotRecordTrail` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-010` | `test_IH_FuriousZhuyin_010_BehaviourUnchangedWhenZhuyinFuriousIsOff` | `test_IH164_BehaviourUnchangedWhenZhuyinFuriousIsOff` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-011` | `test_IH_FuriousZhuyin_011_PinyinFuriousPendingSemanticsUnchanged` | `test_IH165_PinyinFuriousPendingSemanticsUnchanged` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-012` | `test_IH_FuriousZhuyin_012_ZhuyinAbbreviationCells` | `test_IH166_ZhuyinAbbreviationCells` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-013` | `test_IH_FuriousZhuyin_013_ZhuyinAbbreviationCandidatesAndInPlaceSelection` | `test_IH167_ZhuyinAbbreviationCandidatesAndInPlaceSelection` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-014` | `test_IH_FuriousZhuyin_014_MixedAlnumCoexistsWithZhuyinFurious` | `test_IH168_MixedAlnumCoexistsWithZhuyinFurious` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-015` | `test_IH_FuriousZhuyin_015_AbbreviationCandidatesStayWithinPairedSegmentCount` | `test_IH169_AbbreviationCandidatesStayWithinPairedSegmentCount` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-016` | `test_IH_FuriousZhuyin_016_AbbreviationCandidateOrderMatchesPinyinAlphaWindow` | `test_IH170_AbbreviationCandidateOrderMatchesPinyinAlphaWindow` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-017` | `test_IH_FuriousZhuyin_017_UserPhrasesControlFrequencyInFuriousWindows` | `test_IH171_UserPhrasesControlFrequencyInFuriousWindows` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-018` | `test_IH_FuriousZhuyin_018_AbbreviationRankIsScoreBased` | `test_IH172_AbbreviationRankIsScoreBased` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-019` | `test_IH_FuriousZhuyin_019_StandardWindowKeepsAbbreviationCandidates` | `test_IH173_StandardWindowKeepsAbbreviationCandidates` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-020` | `test_IH_FuriousZhuyin_020_FrequencyControlledPairSkipsAutoApply` | `test_IH174_FrequencyControlledPairSkipsAutoApply` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-021` | `test_IH_FuriousZhuyin_021_HandoverWithoutAlignedWordStillInsertsBucket` | `test_IH175_HandoverWithoutAlignedWordStillInsertsBucket` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-022` | `test_IH_FuriousZhuyin_022_IncompletePrefixBucketMatchesPinyinSide` | `test_IH176_IncompletePrefixBucketMatchesPinyinSide` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-023` | `test_IH_FuriousZhuyin_023_IncompletePrefixSolidifyMatchesPinyinSide` | `test_IH177_IncompletePrefixSolidifyMatchesPinyinSide` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-024` | `test_IH_FuriousZhuyin_024_MixedAlnumBufferServesAsUnfinishedReading` | `test_IH520_MixedAlnumBufferServesAsUnfinishedReading` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-025` | `test_IH_FuriousZhuyin_025_SpaceSolidifiesMixedAlnumReading` | `test_IH521_SpaceSolidifiesMixedAlnumReading` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-026` | `test_IH_FuriousZhuyin_026_MixedAlnumCopilotCandidateAppliesInPlace` | `test_IH522_MixedAlnumCopilotCandidateAppliesInPlace` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-027` | `test_IH_FuriousZhuyin_027_AutoChopRemainsSealedUnderMixedAlnum` | `test_IH523_AutoChopRemainsSealedUnderMixedAlnum` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-028` | `test_IH_FuriousZhuyin_028_AutoChopStillWorksWithoutMixedAlnum` | `test_IH524_AutoChopStillWorksWithoutMixedAlnum` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-029` | `test_IH_FuriousZhuyin_029_MixedAlnumBufferShowsInCompositionReadingArea` | `test_IH525_MixedAlnumBufferShowsInCompositionReadingArea` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-030` | `test_IH_FuriousZhuyin_030_MixedAlnumReadingGoesToCopilotOrTooltip` | `test_IH526_MixedAlnumReadingGoesToCopilotOrTooltip` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-031` | `test_IH_FuriousZhuyin_031_MixedAlnumSpaceConfirmsPendingReadingWithFirstTone` | `test_IH527_MixedAlnumSpaceConfirmsPendingReadingWithFirstTone` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-032` | `test_IH_FuriousZhuyin_032_TonedReadingKeepsSpaceAsCommit` | `test_IH528_TonedReadingKeepsSpaceAsCommit` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-033` | `test_IH_FuriousZhuyin_033_FragmentBufferIsNotAReading` | `test_IH529_FragmentBufferIsNotAReading` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-034` | `test_IH_FuriousZhuyin_034_SpaceIsFirstToneNotCandidateConfirmation` | `test_IH530_SpaceIsFirstToneNotCandidateConfirmation` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-035` | `test_IH_FuriousZhuyin_035_SpacePinsReadingToFirstTone` | `test_IH531_SpacePinsReadingToFirstTone` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-036` | `test_IH_FuriousZhuyin_036_SlotOrderSwitchOffRestoresFuriousReadingSource` | `test_IH536_SlotOrderSwitchOffRestoresFuriousReadingSource` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-037` | `test_IH_FuriousZhuyin_037_MixedAlnumPaneTextShowsRawThenReading` | `test_IH538_MixedAlnumPaneTextShowsRawThenReading` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-038` | `test_IH_FuriousZhuyin_038_PaneReadingFollowsHanyuPinyinPreference` | `test_IH539_PaneReadingFollowsHanyuPinyinPreference` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-039` | `test_IH_FuriousZhuyin_039_MixedTooltipReadingFollowsHanyuPinyinPreference` | `test_IH540_MixedTooltipReadingFollowsHanyuPinyinPreference` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-040` | `test_IH_FuriousZhuyin_040_MixedTooltipReadingComesFromBuffer` | `test_IH541_MixedTooltipReadingComesFromBuffer` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-FuriousZhuyin-041` | `test_IH_FuriousZhuyin_041_MixedAlnumShiftSpaceCommitsASCII` | `test_IH542_MixedAlnumShiftSpaceCommitsASCII` | `InputHandlerTests_FuriousZhuyin.swift` |
| `IH-InputMode-001` | `test_IH_InputMode_001_CodePointInputCheck` | `test_IH106_CodePointInputCheck` | `InputHandlerTests_InputMode.swift` |
| `IH-InputMode-002` | `test_IH_InputMode_002_RomanNumeralInputCheck` | `test_IH107_RomanNumeralInputCheck` | `InputHandlerTests_InputMode.swift` |
| `IH-InputMode-003` | `test_IH_InputMode_003_RomanNumeralSpaceKeyHandling` | `test_IH108_RomanNumeralSpaceKeyHandling` | `InputHandlerTests_InputMode.swift` |
| `IH-InputMode-004` | `test_IH_InputMode_004_SymbolMenuKeyTablePreviewInCompositionBuffer` | `test_IH109_SymbolMenuKeyTablePreviewInCompositionBuffer` | `InputHandlerTests_InputMode.swift` |
| `IH-InputMode-005` | `test_IH_InputMode_005_SymbolTableInitSetsDisplaySegments` | `test_IH111_SymbolTableInitSetsDisplaySegments` | `InputHandlerTests_InputMode.swift` |
| `IH-InputMode-006` | `test_IH_InputMode_006_IntonationKeyBehavior` | `test_IH110_IntonationKeyBehavior` | `InputHandlerTests_InputMode.swift` |
| `IH-InputMode-007` | `test_IH_InputMode_007_StandaloneIntonationEnterCommitsToneMark` | `test_IH115_StandaloneIntonationEnterCommitsToneMark` | `InputHandlerTests_InputMode.swift` |
| `IH-MixedAlnum-001` | `test_IH_MixedAlnum_001_MixedAlnumKanjiInputTestIzanami` | `test_IH400_MixedAlnumKanjiInputTest_Izanami` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-002` | `test_IH_MixedAlnum_002_MixedBufferExitPaths` | `test_IH401_MixedBufferExitPaths` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-003` | `test_IH_MixedAlnum_003_MixedSpacePhoneticCommit` | `test_IH402_MixedSpacePhoneticCommit` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-004` | `test_IH_MixedAlnum_004_MixedUppercaseLeadStaysASCII` | `test_IH403_MixedUppercaseLeadStaysASCII` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-005` | `test_IH_MixedAlnum_005_MixedCommitChinesePlusASCIIByEnterOrSpace` | `test_IH404_MixedCommitChinesePlusASCIIByEnterOrSpace` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-006` | `test_IH_MixedAlnum_006_MixedAutoSplitASCIIAndPhoneticSuffix` | `test_IH405_MixedAutoSplitASCIIAndPhoneticSuffix` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-007` | `test_IH_MixedAlnum_007_MixedPurePhoneticSpaceLeavesNoASCIIResidue` | `test_IH406_MixedPurePhoneticSpaceLeavesNoASCIIResidue` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-008` | `test_IH_MixedAlnum_008_AutoSplitWithPriorChinese` | `test_IH407_AutoSplitWithPriorChinese` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-009` | `test_IH_MixedAlnum_009_MixedAutoSplitBoundaryCases` | `test_IH408_MixedAutoSplitBoundaryCases` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-010` | `test_IH_MixedAlnum_010_MixedSpaceFinalizeAutoSplit` | `test_IH409_MixedSpaceFinalizeAutoSplit` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-011` | `test_IH_MixedAlnum_011_MixedLeadingIntonationAlwaysBlockedRegardlessOfPref` | `test_IH410_MixedLeadingIntonationAlwaysBlockedRegardlessOfPref` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-012` | `test_IH_MixedAlnum_012_MixedSpaceFinalizeASCIIWord` | `test_IH411_MixedSpaceFinalizeASCIIWord` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-013` | `test_IH_MixedAlnum_013_MixedSymbolKeepsVisibleSemantics` | `test_IH412_MixedSymbolKeepsVisibleSemantics` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-014` | `test_IH_MixedAlnum_014_MixedSymbolSequenceCommitsAsASCII` | `test_IH413_MixedSymbolSequenceCommitsAsASCII` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-015` | `test_IH_MixedAlnum_015_MixedEnterCommitsChinesePlusSymbolASCII` | `test_IH414_MixedEnterCommitsChinesePlusSymbolASCII` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-016` | `test_IH_MixedAlnum_016_MixedDigitAndSymbolStayDistinct` | `test_IH415_MixedDigitAndSymbolStayDistinct` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-017` | `test_IH_MixedAlnum_017_MixedAutoSplitKeepsASCIIWithEqualsPrefix` | `test_IH416_MixedAutoSplitKeepsASCIIWithEqualsPrefix` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-018` | `test_IH_MixedAlnum_018_MixedEqualsKeyCommitsAsASCIIInUSDachenContext` | `test_IH417_MixedEqualsKeyCommitsAsASCIIInUSDachenContext` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-019` | `test_IH_MixedAlnum_019_MixedBackslashKeyCommitsAsASCIIInUSDachenContext` | `test_IH418_MixedBackslashKeyCommitsAsASCIIInUSDachenContext` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-020` | `test_IH_MixedAlnum_020_MixedASCIIChunksWithEqualsAndBackslashStayLiteral` | `test_IH419_MixedASCIIChunksWithEqualsAndBackslashStayLiteral` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-021` | `test_IH_MixedAlnum_021_MixedOptionShiftOrthogonalPaths` | `test_IH420_MixedOptionShiftOrthogonalPaths` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-022` | `test_IH_MixedAlnum_022_MixedPlainPunctuationUsesDynamicLexiconKey` | `test_IH421_MixedPlainPunctuationUsesDynamicLexiconKey` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-023` | `test_IH_MixedAlnum_023_MixedPunctuationVsPhoneticKey` | `test_IH422_MixedPunctuationVsPhoneticKey` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-024` | `test_IH_MixedAlnum_024_MixedSymbolMenuPhysicalKeyFlushesThenFallsThroughToMenu` | `test_IH423_MixedSymbolMenuPhysicalKeyFlushesThenFallsThroughToMenu` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-025` | `test_IH_MixedAlnum_025_MixedShiftSlashKeepsQuestionMarkVisibleSemantics` | `test_IH424_MixedShiftSlashKeepsQuestionMarkVisibleSemantics` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-026` | `test_IH_MixedAlnum_026_MixedLeadingDigitBlockedFromComposer` | `test_IH425A_MixedLeadingDigitBlockedFromComposer` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-027` | `test_IH_MixedAlnum_027_MixedShiftDigitBlockedFromComposer` | `test_IH425B_MixedShiftDigitBlockedFromComposer` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-028` | `test_IH_MixedAlnum_028_MixedUppercaseBlockedFromComposer` | `test_IH425C_MixedUppercaseBlockedFromComposer` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-029` | `test_IH_MixedAlnum_029_MixedLeadingDigitAutoSplitWithTone` | `test_IH426_MixedLeadingDigitAutoSplitWithTone` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-030` | `test_IH_MixedAlnum_030_MixedLeadingDigitAndUppercaseAutoSplitWithTone` | `test_IH427_MixedLeadingDigitAndUppercaseAutoSplitWithTone` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-031` | `test_IH_MixedAlnum_031_MixedNonToneDigitAllowedAsPhoneticPrefix` | `test_IH428_MixedNonToneDigitAllowedAsPhoneticPrefix` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-032` | `test_IH_MixedAlnum_032_MixedCamelCaseSuffixNotTreatedAsPhonetic` | `test_IH429_MixedCamelCaseSuffixNotTreatedAsPhonetic` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-033` | `test_IH_MixedAlnum_033_MixedCamelCasePrefixWithPhoneticSuffix` | `test_IH430_MixedCamelCasePrefixWithPhoneticSuffix` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-034` | `test_IH_MixedAlnum_034_EtenPhoneticPunctuationKeysInMixedMode` | `test_IH430_EtenPhoneticPunctuationKeysInMixedMode` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-035` | `test_IH_MixedAlnum_035_CtrlASCIIPassesThroughInHalfWidthMode` | `test_IH431_CtrlASCIIPassesThroughInHalfWidthMode` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-036` | `test_IH_MixedAlnum_036_OptionPunctuationWorksInFullWidthMode` | `test_IH432_OptionPunctuationWorksInFullWidthMode` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-037` | `test_IH_MixedAlnum_037_PureDigitSequenceStaysASCII` | `test_IH433_PureDigitSequenceStaysASCII` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-038` | `test_IH_MixedAlnum_038_OptionMainAreaNumeralsBypassedInHalfWidthMode` | `test_IH434_OptionMainAreaNumeralsBypassedInHalfWidthMode` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-039` | `test_IH_MixedAlnum_039_MixedTooltipInlineReadingPreview` | `test_IH435_MixedTooltipInlineReadingPreview` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-040` | `test_IH_MixedAlnum_040_MixedOptionBackspaceClearsWholeBuffer` | `test_IH436_MixedOptionBackspaceClearsWholeBuffer` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-041` | `test_IH_MixedAlnum_041_CursorPosBehindUnfinishedReadingCarriedInState` | `test_IH437_CursorPosBehindUnfinishedReadingCarriedInState` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-042` | `test_IH_MixedAlnum_042_MixedOutOfSlotOrderASCIITokenStaysASCII` | `test_IH438_MixedOutOfSlotOrderASCIITokenStaysASCII` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-043` | `test_IH_MixedAlnum_043_MixedInSlotOrderTwoLetterTokenStaysPhonetic` | `test_IH439_MixedInSlotOrderTwoLetterTokenStaysPhonetic` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-044` | `test_IH_MixedAlnum_044_MixedDynamicLayoutMultiWriteKeysStayPhonetic` | `test_IH440_MixedDynamicLayoutMultiWriteKeysStayPhonetic` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-045` | `test_IH_MixedAlnum_045_MixedRedundantKeyDemarcatesASCIISuffix` | `test_IH441_MixedRedundantKeyDemarcatesASCIISuffix` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-046` | `test_IH_MixedAlnum_046_LatchedAlnumLatchesAndCommitsPerKey` | `test_IH442_LatchedAlnumLatchesAndCommitsPerKey` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-047` | `test_IH_MixedAlnum_047_LatchedAlnumInertUnlessBothSwitchesOn` | `test_IH443_LatchedAlnumInertUnlessBothSwitchesOn` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-048` | `test_IH_MixedAlnum_048_LatchedAlnumReleaseKeys` | `test_IH444_LatchedAlnumReleaseKeys` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-049` | `test_IH_MixedAlnum_049_LatchedAlnumCommitsASCIIPunctuation` | `test_IH445_LatchedAlnumCommitsASCIIPunctuation` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-050` | `test_IH_MixedAlnum_050_LatchedAlnumReleasedSilentlyByResetInputHandler` | `test_IH446_LatchedAlnumReleasedSilentlyByResetInputHandler` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-051` | `test_IH_MixedAlnum_051_LatchedAlnumLatchPreemptsSubsequentMixedInput` | `test_IH447_LatchedAlnumLatchPreemptsSubsequentMixedInput` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-052` | `test_IH_MixedAlnum_052_LatchedAlnumCommitsHalfWidthNumPadASCII` | `test_IH448_LatchedAlnumCommitsHalfWidthNumPadASCII` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-053` | `test_IH_MixedAlnum_053_MixedSequentialOrderJudgeDefaultsOn` | `test_IH450_MixedSequentialOrderJudgeDefaultsOn` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-054` | `test_IH_MixedAlnum_054_MixedOutOfSlotOrderTokenStaysPhoneticWhenJudgeDisabled` | `test_IH451_MixedOutOfSlotOrderTokenStaysPhoneticWhenJudgeDisabled` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-055` | `test_IH_MixedAlnum_055_MixedDynamicLayoutMultiWriteKeysWhenJudgeDisabled` | `test_IH452_MixedDynamicLayoutMultiWriteKeysWhenJudgeDisabled` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-056` | `test_IH_MixedAlnum_056_LatchedAlnumLatchPointUnaffectedBySequentialOrderJudgeSwitch` | `test_IH453_LatchedAlnumLatchPointUnaffectedBySequentialOrderJudgeSwitch` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-057` | `test_IH_MixedAlnum_057_MixedSpacePrefInsertSpaceCommitsWholeBuffer` | `test_IH512_MixedSpacePrefInsertSpaceCommitsWholeBuffer` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-058` | `test_IH_MixedAlnum_058_MixedSpaceKeepsStatusQuoUnderDefaultAndRevolvePreferences` | `test_IH513_MixedSpaceKeepsStatusQuoUnderDefaultAndRevolvePreferences` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-059` | `test_IH_MixedAlnum_059_MixedShiftSpaceStillCommitsWholeBufferUnderDefaultPreference` | `test_IH514_MixedShiftSpaceStillCommitsWholeBufferUnderDefaultPreference` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-060` | `test_IH_MixedAlnum_060_MixedSpacePrefInsertSpaceDoesNotAffectPhoneticFlow` | `test_IH515_MixedSpacePrefInsertSpaceDoesNotAffectPhoneticFlow` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-061` | `test_IH_MixedAlnum_061_PendingTonelessReadingKeepsSpaceAsToneKeyTwoKeySyllable` | `test_IH516_PendingTonelessReadingKeepsSpaceAsToneKey_TwoKeySyllable` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-062` | `test_IH_MixedAlnum_062_PendingTonelessReadingKeepsSpaceAsToneKeyThreeKeySyllable` | `test_IH517_PendingTonelessReadingKeepsSpaceAsToneKey_ThreeKeySyllable` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-063` | `test_IH_MixedAlnum_063_PendingTonelessReadingKeepsSpaceAsToneKeySingleConsonant` | `test_IH518_PendingTonelessReadingKeepsSpaceAsToneKey_SingleConsonant` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-064` | `test_IH_MixedAlnum_064_NonReadingBufferStillCommitsWholeBufferOnSpace` | `test_IH519_NonReadingBufferStillCommitsWholeBufferOnSpace` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-065` | `test_IH_MixedAlnum_065_MixedInsertSpacePrefAbsorbsOutOfSlotOrderTokenWhenJudgeDisabled` | `test_IH535_MixedInsertSpacePrefAbsorbsOutOfSlotOrderTokenWhenJudgeDisabled` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-MixedAlnum-066` | `test_IH_MixedAlnum_066_MixedOutOfSlotOrderTokenWithToneFollowsJudge` | `test_IH537_MixedOutOfSlotOrderTokenWithToneFollowsJudge` | `InputHandlerTests_MixedAlnum.swift` |
| `IH-Narration-001` | `test_IH_Narration_001_NarrationDefensivePinyinToBopomofo` | `test_IH501_NarrationDefensivePinyinToBopomofo` | `InputHandlerTests_Narration.swift` |
| `IH-Narration-002` | `test_IH_Narration_002_NarrationUsesActualKeysOnComposition` | `test_IH502_NarrationUsesActualKeysOnComposition` | `InputHandlerTests_Narration.swift` |
| `IH-Narration-003` | `test_IH_Narration_003_RearIntonationOverrideTriggersNarration` | `test_IH503_RearIntonationOverrideTriggersNarration` | `InputHandlerTests_Narration.swift` |
| `IH-Narration-004` | `test_IH_Narration_004_RearIntonationOverrideTooltipSuppression` | `test_IH511_RearIntonationOverrideTooltipSuppression` | `InputHandlerTests_Narration.swift` |
| `IH-POM-001` | `test_IH_POM_001_POMBleacherIntegrationTest` | `test_IH301_POMBleacherIntegrationTest` | `InputHandlerTests_POM.swift` |
| `IH-POM-002` | `test_IH_POM_002_POMStopShortKeyArrFromHijackingLongKeyArr` | `test_IH302_POMStopShortKeyArrFromHijackingLongKeyArr` | `InputHandlerTests_POM.swift` |
| `IH-POM-003` | `test_IH_POM_003_POMIgnoresLowerWeightSuggestedUnigramMatchingRawQueriedUnigram` | `test_IH303_POMIgnoresLowerWeightSuggestedUnigramMatchingRawQueriedUnigram` | `InputHandlerTests_POM.swift` |
| `IH-POM-004` | `test_IH_POM_004_FilterPOMAppendablesRejectsLowerScoreMatches` | `test_IH303_FilterPOMAppendablesRejectsLowerScoreMatches` | `InputHandlerTests_POM.swift` |
| `IH-POM-005` | `test_IH_POM_005_SaisoukiNoGaika` | `test_IH304_SaisoukiNoGaika` | `InputHandlerTests_POM.swift` |
| `IH-POM-006` | `test_IH_POM_006_SaisoukiOnly` | `test_IH305_SaisoukiOnly` | `InputHandlerTests_POM.swift` |
| `IH-POM-007` | `test_IH_POM_007_ConsolidationWhenCursorAtNodeEdge` | `test_IH306_ConsolidationWhenCursorAtNodeEdge` | `InputHandlerTests_POM.swift` |
| `IH-POM-008` | `test_IH_POM_008_POMShortToLongMarginBehavior` | `test_IH307_POMShortToLongMarginBehavior` | `InputHandlerTests_POM.swift` |
| `IH-POM-009` | `test_IH_POM_009_EndToEndPreventWrongFirstCandidate` | `test_IH308_EndToEnd_PreventWrongFirstCandidate` | `InputHandlerTests_POM.swift` |
| `IH-POM-010` | `test_IH_POM_010_PreviousContextExceptionEndToEnd` | `test_IH309_PreviousContextException_EndToEnd` | `InputHandlerTests_POM.swift` |
| `IH-POM-011` | `test_IH_POM_011_MultiSegCombinationEndToEnd` | `test_IH310_MultiSegCombination_EndToEnd` | `InputHandlerTests_POM.swift` |
| `IH-POM-012` | `test_IH_POM_012_FuriousEnterDirectCommitDoesNotMemorizePOM` | `test_IH127_FuriousEnterDirectCommitDoesNotMemorizePOM` | `InputHandlerTests_POM.swift` |
| `IH-POM-013` | `test_IH_POM_013_FuriousExplicitSelectionMemorizesPOM` | `test_IH128_FuriousExplicitSelectionMemorizesPOM` | `InputHandlerTests_POM.swift` |
| `IH-POM-014` | `test_IH_POM_014_FuriousTypingSolidifyAppliesPOMSuggestionTolerantly` | `test_IH136_FuriousTypingSolidifyAppliesPOMSuggestionTolerantly` | `InputHandlerTests_POM.swift` |
| `IH-POM-015` | `test_IH_POM_015_MainSwitchOffKeepsCompositionUnaffected` | `test_IH137_MasterSwitchOffKeepsCompositionUnaffected` | `InputHandlerTests_POM.swift` |
| `IH-POM-016` | `test_IH_POM_016_FuriousTypingNGramSourceSkipsAutoPOMApply` | `test_IH138_FuriousTypingNGramSourceSkipsAutoPOMApply` | `InputHandlerTests_POM.swift` |
| `IH-POM-017` | `test_IH_POM_017_NonFuriousPinyinNGramSourceSkipsDuplicateAnchor` | `test_IH504_NonFuriousPinyinNGramSourceSkipsDuplicateAnchor` | `InputHandlerTests_POM.swift` |
| `IH-POM-018` | `test_IH_POM_018_FuriousCopilotCompositionPreviewSurvivesFixedOrder` | `test_IH505_FuriousCopilotCompositionPreviewSurvivesFixedOrder` | `InputHandlerTests_POM.swift` |
| `IH-POM-019` | `test_IH_POM_019_FuriousCopilotFrontsUnigramMemoryUnlessFixedOrder` | `test_IH506_FuriousCopilotFrontsUnigramMemoryUnlessFixedOrder` | `InputHandlerTests_POM.swift` |
| `IH-POM-020` | `test_IH_POM_020_POMInjectionRequiresExactTone` | `test_IH508_POMInjectionRequiresExactTone` | `InputHandlerTests_POM.swift` |
| `IH-POM-021` | `test_IH_POM_021_MisalignedPOMCandidateIgnored` | `test_IH509_MisalignedPOMCandidateIgnored` | `InputHandlerTests_POM.swift` |
| `IH-POM-022` | `test_IH_POM_022_FirstToneQueryNotHijackedByCrossToneMemory` | `test_IH510_FirstToneQueryNotHijackedByCrossToneMemory` | `InputHandlerTests_POM.swift` |
| `IH-POM-023` | `test_IH_POM_023_SingleSelectionRecordsWordLevelContextMemory` | `test_IH707_SingleSelectionRecordsWordLevelContextMemory` | `InputHandlerTests_POM.swift` |
| `IH-POM-024` | `test_IH_POM_024_SingleSelectionFixSurvivesRetype` | `test_IH708_SingleSelectionFixSurvivesRetype` | `InputHandlerTests_POM.swift` |
| `IH-POM-025` | `test_IH_POM_025_ContextualBonusIsRecomputedOnEveryAssembly` | `test_IH709_ContextualBonusIsRecomputedOnEveryAssembly` | `InputHandlerTests_POM.swift` |
| `IH-TypingMode-001` | `test_IH_TypingMode_001_TypingModeTruthTable` | `test_IH701_TypingModeTruthTable` | `InputHandlerTests_TypingMode.swift` |
| `IH-TypingMode-002` | `test_IH_TypingMode_002_IsPinyinFamilyTypingModeStaysFalseForZhuyin` | `test_IH702_IsPinyinFamilyTypingModeStaysFalseForZhuyin` | `InputHandlerTests_TypingMode.swift` |
| `IH-TypingMode-003` | `test_IH_TypingMode_003_GateFamilyMembership` | `test_IH703_GateFamilyMembership` | `InputHandlerTests_TypingMode.swift` |
| `IH-TypingMode-004` | `test_IH_TypingMode_004_ZhuyinFuriousIsUnreachableButPendingGateWorks` | `test_IH704_ZhuyinFuriousIsUnreachableButPendingGateWorks` | `InputHandlerTests_TypingMode.swift` |
| `IH-TypingMode-005` | `test_IH_TypingMode_005_TypingModeHotKeyReflectsOnNextBeat` | `test_IH705_TypingModeHotKeyReflectsOnNextBeat` | `InputHandlerTests_TypingMode.swift` |
| `IH-TypingMode-006` | `test_IH_TypingMode_006_SCPCDisablesPinyinAutoChop` | `test_IH706_SCPCDisablesPinyinAutoChop` | `InputHandlerTests_TypingMode.swift` |
| `SS-CandidateWindow-001` | `test_SS_CandidateWindow_001_PunctuationFeaturesAndSymbolMenus` | `test205_InputHandler_PunctuationFeaturesAndSymbolMenus` | `SessionTests_CandidateWindow.swift` |
| `SS-CandidateWindow-002` | `test_SS_CandidateWindow_002_CandidateWindowExtendedOperations` | `test209_InputHandler_CandidateWindowExtendedOperations` | `SessionTests_CandidateWindow.swift` |
| `SS-CandidateWindow-003` | `test_SS_CandidateWindow_003_ServiceMenuInitiation` | `test210_InputHandler_ServiceMenuInitiation` | `SessionTests_CandidateWindow.swift` |
| `SS-CandidateWindow-004` | `test_SS_CandidateWindow_004_CandidatePreviewUpdates` | `test212_InputHandler_CandidatePreviewUpdates` | `SessionTests_CandidateWindow.swift` |
| `SS-CandidateWindow-005` | `test_SS_CandidateWindow_005_AssociatedPhraseTriggersSCPC` | `test214_InputHandler_AssociatedPhraseTriggers_SCPC` | `SessionTests_CandidateWindow.swift` |
| `SS-CandidateWindow-006` | `test_SS_CandidateWindow_006_AssociatedPhraseTriggersNonSCPC` | `test215_InputHandler_AssociatedPhraseTriggers_NonSCPC` | `SessionTests_CandidateWindow.swift` |
| `SS-CandidateWindow-007` | `test_SS_CandidateWindow_007_CandidateFilterShortcuts` | `test301_InputHandler_CandidateFilterShortcuts` | `SessionTests_CandidateWindow.swift` |
| `SS-ClientBridge-001` | `test_SS_ClientBridge_001_AttrStrAPITests` | `test401_Session_AttrStrAPITests` | `SessionTests_ClientBridge.swift` |
| `SS-ClientBridge-002` | `test_SS_ClientBridge_002_QEMUCursorReleaseHotKeyOmission` | `test402_Session_QEMUCursorReleaseHotKeyOmission` | `SessionTests_ClientBridge.swift` |
| `SS-Composition-001` | `test_SS_Composition_001_SwitchStateEmptyCommitsComposition` | `test204_SwitchStateEmptyCommitsComposition` | `SessionTests_Composition.swift` |
| `SS-Composition-002` | `test_SS_Composition_002_SwitchStateEmptyCommitsRawTextWithoutBPMFVSLeak` | `test204A_SwitchStateEmptyCommitsRawTextWithoutBPMFVSLeak` | `SessionTests_Composition.swift` |
| `SS-Composition-003` | `test_SS_Composition_003_SCPCSelectionCommitsRawTextWithoutBPMFVSLeak` | `test204B_SCPCSelectionCommitsRawTextWithoutBPMFVSLeak` | `SessionTests_Composition.swift` |
| `SS-EventTriage-001` | `test_SS_EventTriage_001_HomeEndAndClockKeys` | `test201_InputHandler_HomeEndAndClockKeys` | `SessionTests_EventTriage.swift` |
| `SS-EventTriage-002` | `test_SS_EventTriage_002_EscapeBehaviorVariants` | `test202_InputHandler_EscapeBehaviorVariants` | `SessionTests_EventTriage.swift` |
| `SS-EventTriage-003` | `test_SS_EventTriage_003_BackspaceAndDeleteBranches` | `test203_InputHandler_BackspaceAndDeleteBranches` | `SessionTests_EventTriage.swift` |
| `SS-EventTriage-004` | `test_SS_EventTriage_004_NumPadBehaviors` | `test207_InputHandler_NumPadBehaviors` | `SessionTests_EventTriage.swift` |
| `SS-EventTriage-005` | `test_SS_EventTriage_005_ShiftLetterKeyPreferences` | `test208_InputHandler_ShiftLetterKeyPreferences` | `SessionTests_EventTriage.swift` |
| `SS-EventTriage-006` | `test_SS_EventTriage_006_CallCandidateStateTriggers` | `test211_InputHandler_CallCandidateStateTriggers` | `SessionTests_EventTriage.swift` |
| `SS-EventTriage-007` | `test_SS_EventTriage_007_DodgeInvalidEdgeCursor` | `test213_InputHandler_DodgeInvalidEdgeCursor` | `SessionTests_EventTriage.swift` |
| `SS-EventTriage-008` | `test_SS_EventTriage_008_RevolverRareCaseJiHuQiKeng` | `test216_InputHandler_RevolverRareCase_JiHuQiKeng` | `SessionTests_EventTriage.swift` |
| `SS-EventTriage-009` | `test_SS_EventTriage_009_ShiftSpaceEmptyStateWidth` | `test219_InputHandler_ShiftSpaceEmptyStateWidth` | `SessionTests_EventTriage.swift` |
| `SS-HotKey-001` | `test_SS_HotKey_001_FuriousCopilotWindowTooltipShowsShiftHint` | `test505_FuriousCopilotWindowTooltipShowsShiftHint` | `SessionTests_HotKey.swift` |
| `SS-HotKey-002` | `test_SS_HotKey_002_FuriousCopilotWindowIgnoresJKHLReinterpretation` | `test507_FuriousCopilotWindowIgnoresJKHLReinterpretation` | `SessionTests_HotKey.swift` |
| `SS-HotKey-003` | `test_SS_HotKey_003_FunctionKeyDoesNotDisturbUncommittedReading` | `test516_FunctionKeyDoesNotDisturbUncommittedReading` | `SessionTests_HotKey.swift` |
| `SS-HotKey-004` | `test_SS_HotKey_004_FunctionKeyDoesNotDisturbUnfinishedReading` | `test517_FunctionKeyDoesNotDisturbUnfinishedReading` | `SessionTests_HotKey.swift` |
| `SS-HotKey-005` | `test_SS_HotKey_005_FunctionKeyPassesThroughWhenNothingPending` | `test518_FunctionKeyPassesThroughWhenNothingPending` | `SessionTests_HotKey.swift` |
| `SS-HotKey-006` | `test_SS_HotKey_006_FnNonFunctionKeyCombinationStillPassesThrough` | `test519_FnNonFunctionKeyCombinationStillPassesThrough` | `SessionTests_HotKey.swift` |
| `SS-HotKey-007` | `test_SS_HotKey_007_UnclaimedCommandShortcutsCommitThenReachClient` | `test520_UnclaimedCommandShortcutsCommitThenReachClient` | `SessionTests_HotKey.swift` |
| `SS-HotKey-008` | `test_SS_HotKey_008_UnclaimedCommandShortcutsReachClientWhenNothingPending` | `test521_UnclaimedCommandShortcutsReachClientWhenNothingPending` | `SessionTests_HotKey.swift` |
| `SS-HotKey-009` | `test_SS_HotKey_009_NonCommandChordsAreStillBlockedWhileComposing` | `test522_NonCommandChordsAreStillBlockedWhileComposing` | `SessionTests_HotKey.swift` |
| `SS-HotKey-010` | `test_SS_HotKey_010_UnclaimedCommandShortcutsCommitThenReachClientInCandidateWindow` | `test523_UnclaimedCommandShortcutsCommitThenReachClientInCandidateWindow` | `SessionTests_HotKey.swift` |
| `SS-HotKey-011` | `test_SS_HotKey_011_UnfinishedReadingIsTrimmedWhenReleasingCommandShortcut` | `test524_UnfinishedReadingIsTrimmedWhenReleasingCommandShortcut` | `SessionTests_HotKey.swift` |
| `SS-Lifecycle-001` | `test_SS_Lifecycle_001_ActivationFastPathSkipsInitInputHandler` | `test501_ActivationFastPath_SkipsInitInputHandler` | `SessionTests_Lifecycle.swift` |
| `SS-Lifecycle-002` | `test_SS_Lifecycle_002_DeactivationIsNoOpForCurrentSession` | `test502_DeactivationIsNoOpForCurrentSession` | `SessionTests_Lifecycle.swift` |
| `SS-Lifecycle-003` | `test_SS_Lifecycle_003_RapidReactivationMaintainsHandlerIdentity` | `test503_RapidReactivation_MaintainsHandlerIdentity` | `SessionTests_Lifecycle.swift` |
| `SS-Lifecycle-004` | `test_SS_Lifecycle_004_CapsLockResetCommitsPendingMixedASCIIBuffer` | `test504_CapsLockResetCommitsPendingMixedASCIIBuffer` | `SessionTests_Lifecycle.swift` |
| `SS-Lifecycle-005` | `test_SS_Lifecycle_005_ModeDescriptionHintShownUponActivationWhenEnabled` | `test508_ModeDescriptionHintShownUponActivationWhenEnabled` | `SessionTests_Lifecycle.swift` |
| `SS-Lifecycle-006` | `test_SS_Lifecycle_006_ModeDescriptionHintSuppressedUponActivationWhenDisabled` | `test509_ModeDescriptionHintSuppressedUponActivationWhenDisabled` | `SessionTests_Lifecycle.swift` |
| `SS-Lifecycle-007` | `test_SS_Lifecycle_007_ModeDescriptionHintShownUponActivationInASCIIMode` | `test510_ModeDescriptionHintShownUponActivationInASCIIMode` | `SessionTests_Lifecycle.swift` |
| `SS-Lifecycle-008` | `test_SS_Lifecycle_008_ModeDescriptionHintShownUponActivationWithCapsLockLit` | `test511_ModeDescriptionHintShownUponActivationWithCapsLockLit` | `SessionTests_Lifecycle.swift` |
| `SS-Lifecycle-009` | `test_SS_Lifecycle_009_ModeDescriptionHintShownOnceDespitePostActivationSetValue` | `test512_ModeDescriptionHintShownOnceDespitePostActivationSetValue` | `SessionTests_Lifecycle.swift` |
| `SS-Lifecycle-010` | `test_SS_Lifecycle_010_ModeDescriptionHintClearsPopupCompositionBuffer` | `test513_ModeDescriptionHintClearsPopupCompositionBuffer` | `SessionTests_Lifecycle.swift` |
| `SS-Lifecycle-011` | `test_SS_Lifecycle_011_ModeDescriptionHintDismissedWhenCompositionBufferAppears` | `test514_ModeDescriptionHintDismissedWhenCompositionBufferAppears` | `SessionTests_Lifecycle.swift` |
| `SS-TooltipAndMarking-001` | `test_SS_TooltipAndMarking_001_MarkingStateTooltipGeneratedInSwitchState` | `test217_MarkingStateTooltipGeneratedInSwitchState` | `SessionTests_TooltipAndMarking.swift` |
| `SS-TooltipAndMarking-002` | `test_SS_TooltipAndMarking_002_MixedTooltipReadingPreviewStyle` | `test218_InputHandler_MixedTooltipReadingPreviewStyle` | `SessionTests_TooltipAndMarking.swift` |
| `SS-TooltipAndMarking-003` | `test_SS_TooltipAndMarking_003_MixedAlnumTooltipAnchorsAtCursorPosBehindReading` | `test220_MixedAlnumTooltipAnchorsAtCursorPosBehindReading` | `SessionTests_TooltipAndMarking.swift` |
| `SS-TooltipAndMarking-004` | `test_SS_TooltipAndMarking_004_HardenedBufferKeepsMarkerEqualToCursorPosBehindReading` | `test221_HardenedBufferKeepsMarkerEqualToCursorPosBehindReading` | `SessionTests_TooltipAndMarking.swift` |
| `SS-UserPhrase-001` | `test_SS_UserPhrase_001_InPlaceUserPhraseOperationsApplyToCurrentAssemblerImmediately` | `test515_InPlaceUserPhraseOperationsApplyToCurrentAssemblerImmediately` | `SessionTests_UserPhrase.swift` |

## 五、駁回之方案

- **保留原數字、只補空號與去重**：不能解「數字不反映分類」與「跨套重號」兩項根因，僅是把病灶修得整齊些。
- **分類只寫進標題、函式名沿用 `test_IH###`**：`--filter` 與測試報告之主要手柄是函式名；分類不入函式名即等於沒有分類。
- **以 Swift Testing 之 `@Tag` 取代分類**：標籤不出現在函式名、亦不影響檔案佈局；且本靶之 suite 階層受 `.serialized` 之結構約束（測試方法住同一個 `InputHandlerTests` 類別，無法再按分類拆成子 suite 而不搬動 harness 狀態）。
- **為壓低單檔行數而把大分類再切細**：分類粒度以語義為準、不以行數為準；動工前之 `Cases1` 已有 4,951 行之前例，行數不是本 phase 要治的病。
- **改寫歷史文書中之舊測試名**：違反本倉「歷史記錄保留舊稱」之既例（沿 P261 狂拼更名之例）；僅更新**現況性**引用（`KnowledgeMemo4LLM.md` 之兩處）。

## 六、施工方法與其驗證

以一次性腳本（臨時檔案、不入庫）完成：
1. **抽出**：逐檔以擴充區塊之直接成員深度切出「測試／輔助函式」成員，並以「下一成員之註解與屬性起點」為上一成員之終點（首版以「下一 `func` 行」為終點，造成成員互疊、已修）。
2. **改寫**：函式名與 `@Test` 標題依第二節重寫；內文一字不動。
3. **引用改寫**：內文註解與字串中之舊測試編號（實測 109 處）依對照表改寫；子案例標籤依第二節改寫；跨檔引用之舊檔名（5 處）同步改寫。
4. **守恆檢查**：成員數 328（測試 283 ＋ 輔助 45）逐支對號；`#expect` 1,935、`Issue.record` 234、`#require` 9 三項計數與動工前**逐項相同**。
5. **綠燈**：兩倉 `swift test -c release --no-parallel --disable-sandbox` 各 680 支／0 失敗；`make lintFormatUncommitted` rc=0；兩倉 `Tests/` 90 檔逐檔 SHA-256 全同。

輔助函式之落點依「呼叫者所屬分類」決定；**跨分類者**（`insertShiJieSolidificationFixture`、`prepareMixedModeHandler`）升為模組層 internal 並隨其主要呼叫者落檔，其餘 `fileprivate` 一律降為 `private`。輔助之**型別**（`MixedBufferExitScenario` 等 8 個 struct、`CandidateManipulatorTask`）隨其用之測試落檔。
