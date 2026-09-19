# FR608 一階‧再設計（PreResearch-v1b）：「英數暫存輸入模式」需求逆推與體驗風險評估（Auto-English Buffer Mode，2026-09-13）

> **文檔狀態**：PreResearch（FR608 系列第三份；對應同一分支 `feat/smart-zh-en-auto-switch` 於 2026-09-13 的**再設計**；「產品需求固定」仍暫緩；**其實作不得照搬**）
> **對應實作**：fork `doggy8088/vChewing-macOS` 分支 `feat/smart-zh-en-auto-switch` @ `7761d6a5`（2026-09-13 01:06 +0800；寫作前複核 fork tip 未變）。其基底為 main@`645eb64a`（2026-09-12）；分支線 = 14 筆 PR608 提交之 **rebase 改寫** ＋ 2 筆新提交（`8cece6a0`、`7761d6a5`），共 16 筆。
> **系列脈絡**：`FR608-PreResearch-v1a.md`（下稱 **v1a**）＝由 PullReq608 逆推（gen-1）；**本文件（v1b）＝由同一分支 09-13 再設計逆推（gen-2）**；`FR608-PreResearch-v2.md`（下稱 **v2**）＝由 09-18/19 新分支逆推（gen-3）。三代對照見 §三。
> **範疇**：vChewing-macOS（當代舊套件佈局：`Packages/vChewing_Typewriter`、`vChewing_Tekkon`、`vChewing_SettingsUI`、`vChewing_Shared`、`vChewing_IMKUtils` 等）；其後架構（LibVanguard）見 v2。

---

## 一、取材與事實摘要

- **歷史已被改寫**：現行舊分支已 rebase 到 main@`645eb64a`（09-12）。PR608 封存 head `34621edb`（14 筆、author 日期 09-06）**不在**現行分支歷史內（其 14 筆提交以新 hash 重現、committer 日期改為 09-13）。欲對照 PR608 原貌僅能靠 `refs/pull/608/head`（或本地殘存物件）。
- **本代兩筆新提交**（均為 2026-09-13 01:06，同一分鐘內）：
  - `8cece6a0`：自「一般設定」頁移除舊的「連續打字錯誤自動切換半形英文」開關與門檻（−10 行）。
  - `7761d6a5`（**本文件主體**）：把自動切換的落地方式整體改寫為唯音內部的「英數暫存輸入模式」（28 檔、+1350/−394）。
- **改動面**：新增 `Typewriter/InputHandler/InputHandler_AutoEnglishMode.swift`（298 行）與 `ChineseTypingSnapshot`／`AutoEnglishModeState` 型別；`InputHandler_CoreProtocol.swift` 之偵測邏輯大改（±218）；`Typewriter_BPMFFullMatch.swift`、`InputHandler_TriageInput.swift`、`InputHandler_HandleStates.swift` 接線；Session 層**移除**：`SessionHost.switchToSystemABCInputSource` 接線、`isPassThroughUntilDeactivated` 系列、`InputSession.isAutoSwitchedToABC`、reactivation 自動回中文邏輯；`Shared` 新增 2 偏好；新增設定頁籤「Smart Typing」；四語系；測試大改（`InputHandlerTests_AutoSwitchOnErrors.swift` 779 行變動）。
- **實測**（於 `/tmp/vchewing-gen1b-7761d6a5/` 快照、Swift 6.4 工具鏈；真 Typewriter 核心＋測試 mock 客體）：
  - 分支自帶 `--filter AutoSwitchOnConsecutiveErrors`：**29/29 通過**（log：`/tmp/gen1b-suite.log`）。
  - 追加探針 `Scratch_AutoEnglishMode_Probe.swift`（log：`/tmp/gen1b-scratch.log`）：
    - `cd ../` → 觸發、緩衝內容 == `cd ../`（頭號案例成立）。
    - `ls ` → **不觸發**；組字區讀數 `displayed=峱`（ㄋㄠ＋一聲直接成字）——「音位順序顛倒」已被自誤鍵定義中剔除（見 §四·5）。
- **本地保存**：`refs/remotes/doggy8088/feat/smart-zh-en-auto-switch` → `7761d6a5`（本文件主體）；`refs/remotes/doggy8088/feat-smart-zh-en-auto-switch-mvp-1-abc-2-shift-3-a` → `99c22637`（v2 主體，本地鏡像分支 `lab-260919`）。

---

## 二、他（09-13 版）想要什麼（需求逆推）

### 2.1 一句話

**把「連續誤鍵轉英」的落地方式，從「遞交文字＋切去系統 ABC 輸入法」改寫為唯音內部的「英數暫存輸入模式」**：英數內容先以組字區**可見、可編輯、尚未遞交**的緩衝形態存在；使用者可隨時**棄置並完整還原**中斷前的中文進度，或以明確鍵（Enter／Tab）／閒置逾時完成遞交。

### 2.2 需求清單（R1–R8）

- **R1 偵測（繼承自 gen-1，但大幅收斂）**：連續誤鍵達門檻（3–8、預設 5）。判定改為「**純觀測者**」：門檻未滿前不吞鍵、不清注拼槽（「打錯了照樣可以 BackSpace 修正、照樣可以重打」）；且將「音位順序顛倒」（如先 ㄨ 後 ㄙ）**自誤鍵定義中剔除**（改用「結果是否為合法音節」把關）。
- **R2 落地（本代新定義）**：不切系統輸入源、不碰 `isASCIIMode`；後續按鍵改由唯音內部緩衝模式承接。
- **R3 緩衝可見、可編輯**：組字區顯示「進入模式前既有組字內容 + 英數緩衝」（順序即鍵入順序，修正過「鍵入 `Claude` 卻得到 `laudeC`」類案例）；BackSpace 在緩衝內逐字刪除、刪空即退出並還原中文。
- **R4 完成遞交**：Enter／Tab＝遞交緩衝並返回中文（按鍵由唯音消費、**不代客體遞交**）；閒置逾時（預設 2 秒、0–10 秒可調、0＝停用）＝自動遞交緩衝並返回中文。
- **R5 放棄與還原**：Esc（恆定）／自訂熱鍵（⌃Space／⌥Enter／⌃Enter）／Shift 輕敲＝**棄置緩衝**並還原：注拼槽（含拼到一半的讀音與其鍵入序列）＋**組字器整份快照**。
- **R6 使用者知情**：進入模式時彈工具提示＋系統通知（文案：`i18n:InfoMessage.AutoSwitchedEnglishModeEntered`「智慧中英混打：已自動切換為英數輸入（唯音未離開中文輸入法）。」＋返回熱鍵提示＋逾時提示）。
- **R7 可調可控**：總開關（`kAutoSwitchToAlphanumericalOnConsecutiveErrors`，預設 **true**）、門檻、逾時秒數、退出熱鍵；集中於新設「智慧輸入」頁籤（`PrefUITabs.tabSmartTyping`）；四語系。
- **R8 範圍**：`imeModeCHT` ＋ 注音鍵盤 ＋ 非 ASCII ＋ 非拼音 ＋ 非混打 ＋ 非磁帶（與 v1a 相同）。

### 2.3 與 v1a 相較的主要變更與矛盾

1. **落地反轉（最大變更）**：v1a 的核心之一是「遞交後切至系統英數輸入源、尊重使用者佈局偏好」（前作 §2.4／§4.3）；本代**整個刪除** TIS 機制與相關狀態。與 Customer 在 PR608 的自述「我想達成的行為與**留在唯音內持續中英混輸有所不同**」（他要真的切去 ABC）**直接相反**。→ 這是本線自「切源派」轉向「留內派」的轉折點。
2. **遞交時機反轉**：v1a＝觸發即遞交英數（即時、無緩衝）；本代＝**延後遞交**（緩衝可見可改，明確鍵或逾時才落地）。
3. **救援語義升級**：v2 的救援是「三連退格還原注拼槽＋鍵序」；本代則連**組字器快照**都還原——「打到一半的整段中文原樣歸還」，且任一退出鍵（Esc／熱鍵／Shift 輕敲）皆觸發。
4. **與前作凍結條目的落差（沿用 v1a 對 PR608 的裁定框架）**：`imeModeCHT` 仍在（前作 §4.4 簡中注音未涵蓋）；`!mixedAlphanumericalEnabled` 硬閘仍在（前作 §2.1／§七所忌）；`Tekkon.allValidMandarinSyllables`（靜態集）仍用於合法音節判定（前作 §4.1「Tekkon 不能替 Lexicon 擦屁股」——本代另有一處改良：空格計入與否改查 Lexicon「該讀音是否只剩注音自身兜底」，屬混合做法）；預設仍 `true`（前作 §三裁示 `false`）；設定另立新頁籤（前作 §三：應與 MixedAlnum 同 Section——本代距之更遠）。
5. **命名家族化**：UI 文案改稱「**智慧中英混打**」，將本功能敘事收進 MixedAlnum 家族語境之下（與 v1a 的「切換至 ABC」舊文案脫鉤）。

---

## 三、三代對照（v1a / v1b / v2）

| 維度 | v1a（PR608 需求） | v1b（本代） | v2（新分支） |
|---|---|---|---|
| 落地 | 遞交＋切系統英數輸入源（失敗退 `isASCIIMode`） | 唯音內部緩衝模式 | 唯音內部逐字即時遞交 |
| 觸發 | 連續誤鍵門檻 | 連續誤鍵門檻（判定收斂、純觀測） | 門檻＋Tab＋Space＋路徑前綴 |
| 英數形態 | 立即遞交 | 組字區可見緩衝、可 BackSpace 編輯 | 逐字直接遞交、無緩衝 |
| 完成遞交 | 觸發即完成 | Enter／Tab／逾時（預設 2 秒） | 逐字即時（無待遞交） |
| 退出／救援 | 切源後以 CpLk 等回切；無還原 | Esc／熱鍵／Shift 輕敲＝棄置＋**全還原**（含組字器） | Enter／Esc 放行；500ms 逾時；三連退格還原注拼槽 |
| 進入告知 | 無 | 工具提示＋系統通知 | 無（僅設定說明） |
| Enter／Tab／Esc 對客體 | 不適用 | **消費**（不放行） | **放行** |
| 範圍 | CHT＋注音 | CHT＋注音 | 繁簡＋注音 |
| 設定區位 | General 頁 | 新「智慧輸入」頁籤 | 行為頁新 Section |
| 預設 | false（事主裁示） | true | true |

（v2 細節以 `FR608-PreResearch-v2.md` 為準。）

---

## 四、需求層面的既有體驗風險（gen-2 的需求本身）

1. **閒置自動遞交（預設 2 秒）**：以打字節奏為模式判準——停頓超過 2 秒即「**沉默定案**」：遞交緩衝並退出。誤觸若未在 2 秒內察覺，內容自動落地；反之設 0（停用）時，模式會滯留到使用者明確退出。兩端皆有體驗代價。
2. **Enter／Tab 被消費（不放行）**：終端機「打完命令按 Enter」場景需**多按一次 Enter**（第一下只完成遞交、不換行）；Tab 完全不放行，無 shell completion 補償。
3. **Esc 恆被消費**：App 級 Esc（vi／全螢幕等）在模式期間被吃掉（換得「無條件救援」——這是本代刻意的對價）。
4. **Shift 輕敲語義佔用**：模式中 Shift 不再是 ASCII 切換、而是「棄置並還原」——與 Shift-切換英數的使用者習慣相衝（僅在模式內、且需 Shift 偵測啟用）。
5. **覆蓋面取捨（已實測）**：`ls ` 不觸發、直接輸出漢字「峱」；「順序顛倒但結果像合法音節」的序列（`ls`-class）在本代設計下屬**已知不覆蓋**。相較 v1a 敘述的終端機案例（PR608 內文曾自稱支援 `ls -la`），覆蓋面有實質縮減——「誤判面↓」與「覆蓋面↓」是一體兩面，須在需求書明列已知邊界，不得宣稱全面涵蓋終端機指令。
6. **預設 ON 與 CHT-only**：延續既有的裁示落差（曝光面、涵蓋面）。
7. **冷門衝突**：⌃Space 退出熱鍵選項與 macOS 預設「切換輸入來源」熱鍵同鍵（預設為 Esc，故僅在選用該項時構成衝突）。

---

## 五、實作層面的既有體驗風險

1. **緩衝生命週期（主路徑安全，邊界待驗證）**：組字區顯示與「可遞交內容」都含緩衝（`InputHandler_HandleStates.swift:341-347`、`:525-535`，後者註解明言為 IMK 強制遞交〔如客體失焦時的 `commitComposition`〕而設）；`clearComposerAndCalligrapher()` 會取消計時任務並清模式（`InputHandler_CoreProtocol.swift:443-444`）。惟失活路徑 `resetInputHandler(commitExisting: false)` 不遞交——是否恆有 IMK `commitComposition` 先行護航，建議列入實機驗證矩陣（失焦、切輸入源、App 崩潰等情境）。
2. **計時器路徑存在測試盲區**：生產環境以 `Task` 排程逾時；單元測試以 `UserDefaults.pendingUnitTests` **繞過**、改走事件驅動的懶惰檢查（`InputHandler_AutoEnglishMode.swift` 末尾）——**真實時間行為（計時競態、取消時機）無自動化覆蓋**。
3. **偵測邏輯重寫的複雜度**：stash／fold／preserve 邏輯往返於 `CoreProtocol` 與 `BPMFFullMatch`（含 `preservedChineseStash` 這類權宜保留），回歸面仍高——本代以 29 項測試護航，覆蓋品質尚可（含「組字失敗重打不受罰」「順序顛倒照常入槽」等實機案例回歸）。
4. **殘留死代碼**：`IMKUtils.selectSystemABCInputSource()` 仍存在、已無任何呼叫者（TIS 語義整體退役後未清理）。
5. **Session 級別無新模式專屬測試**：`SessionTests_Cases5` 的 501–507 與本模式無關；模式與會話生命週期（啟動／失活／快取）之交會未被測試釘死。

---

## 六、干擾較小的替代實作方向

> 本代已被 v2 取代，但**其架構是三代中「誤切代價最低」者**（見下表），其中若干資產值得在最終設計中回收。

**誤切代價對照（越小越好）**：
- v1a：觸發即遞交＋切源——誤切後內容已送出、輸入源已換，救援成本最高。
- v1b：**全程可見、可編輯；任一退出鍵皆全還原（含組字器）**——救援成本最低，唯受 2 秒逾時競賽限制。
- v2：逐字即時遞交——救援靠「三連退格」且僅還原注拼槽；誤切時內容已部分外送。

**建議回收／修正**：
1. 保留本代「緩衝＋全還原」核心理念，修正其風險點：
   - 逾時：預設拉長（≥5 秒）或「逾時僅提示、不遞交」，或提供遞交／等待二選一；停用時提供滯留提示。
   - Enter：遞交後**放行**（終端機一行到底，v2 已採此語義）；Tab 同理。
   - Esc：退出後放行（v2 已採）。
   - Shift 輕敲：避免佔用，改用專屬熱鍵。
   - 退出熱鍵預設避開 ⌃Space。
2. 偵測維持「純觀測者＋門檻」結構（本代最大亮點），但把「適用讀音」權威統一改由 Lexicon 供給（前作 §4.1）。
3. 治理項：預設 OFF（或首啟引導）；涵蓋簡中注音；設定回歸「行為設定」頁。
4. 測試：補計時器路徑與失活／強制遞交流程之覆蓋。
5. 若最終仍採 v2 的「不緩衝」路線：至少吸收本代的兩項資產——**進入模式的明確告知**與**全面還原（含組字器快照）語義**。

---

## 七、待事主裁示（收斂）

1. **三代「落地形態」定於哪一種**（切源／緩衝／逐字透傳）：本代證明緩衝形態可通過 29 項測試、且誤切代價最低，值得列入正式候選。
2. **逐一裁定模式內鍵語義**：逾時（遞交 vs 提示）、Enter／Tab／Esc（消費 vs 放行）、Shift 輕敲之歸屬。
3. **已知邊界**：`ls`-class 不覆蓋是否可接受（需求書須明列）。
4. **向 Customer 求證**：「為何自 v1b 轉向 v2、放棄緩衝路線」——此答案將直接影響最終需求設計。

---

> **備註（文檔關係）**：v2 成稿時本代尚不為其作者所知；如要系列一致，建議 v2 補一段「前史：v1b」的引用。
> **證據清單**：分支 `7761d6a5`（本地 ref `refs/remotes/doggy8088/feat/smart-zh-en-auto-switch`）；快照 `/tmp/vchewing-gen1b-7761d6a5/`；實作 `Packages/vChewing_Typewriter/Sources/Typewriter/InputHandler/InputHandler_AutoEnglishMode.swift`（含 `ChineseTypingSnapshot`、`AutoEnglishModeState`）；偵測 `.../InputHandler_CoreProtocol.swift`（`handleConsecutiveTypingErrorsSwitchIfNeeded`、`isConsideredPhoneticErrorKey`、`noteCompositionFailureForConsecutiveTypingErrors`）；顯示/遞交 `.../InputHandler_HandleStates.swift:341-347, 525-535`；偏好 `Packages/vChewing_Shared/Sources/Shared/UserDef/UserDef.swift`（`kAutoSwitchedEnglishModeExitHotkey` 0–3 預設 0；`kAutoSwitchedEnglishModeIdleTimeout` 0–10 預設 2）；設定頁 `Packages/vChewing_SettingsUI/.../VwrSettingsPaneSmartTyping.swift`；測試命令 `swift test --disable-sandbox --filter AutoSwitchOnConsecutiveErrors`（29/29，log `/tmp/gen1b-suite.log`）與探針 `Scratch_AutoEnglishMode_Probe.swift`（`cd ../` ✓；`ls ` ✗→峱；log `/tmp/gen1b-scratch.log`）；PR608 原貌對照 `refs/pull/608/head`（`34621edb`）。
> **用語**：沿用前作（v1a）用語：「事主」＝唯音專案維護者；「plausible／適用讀音」＝當前載入 Lexicon 中實際可用之讀音集合。
