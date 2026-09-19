# Phase 234 PostResearch：MixedAlnum 三元開關草案之實作可行性探究

> **文檔狀態**：PostResearch（本文記錄**規格探索與裁定過程**，不含實作細節）。
> **施行狀態**：本文件之全部裁定已於 **Phase 235 實作完畢**（2026-09-20），連同若干本次自決事項；實作記錄見 `vChewing-DevLogs/Reqs4LLM/Archive_P201-P300/Reqs_0231-0240.md` 之 Phase 235。本文保留原樣作為決策歷程；其後於 **2026-09-20 定稿**時另行補入文首〈施行現況〉一節（見下），俾使本文與最終實作之差異不致誤導讀者。
> 用途為供事主裁定；**未經裁定前不得據以動工**。
>
> **用詞沿革（2026-09-20 定案，commit 前全面換稱）**：本功能之定名統一為 `Latch`／「閂滯」（zh-Hans「闩滞」、ja「ラッチ」）——`UserDef.kEnableLatchedAlnumStateInMixedAlnumMode`、`PrefMgr.enableLatchedAlnumStateInMixedAlnumMode`、`MixedAlnumConfig.isLatchedToAlnum`、`releaseLatchedAlnumState(announce:)`、i18n `StateOfInputting.Tooltip.MixedAlnumLatchedStateReleased`。本文之概念敘述與現行名稱已同步改稱；惟本研究階段曾用過之舊寫法與未實作之提案識別字（如 `isStickyEnglishActive`（**提案、未實作**；最終作 `isLatchedToAlnum`））仍以原樣散見文中，係歷史痕跡、勿據以取用；舊稱與定名之對照見 `vChewing-DevLogs/KnowledgeMemo4LLM.md`。**（2026-09-20 補記：定稿後之二次換稱）**：事主於 commit 之後另將含 `EnglishAlnum` 之識別字全面換稱為 `Alnum`（`isLatchedToAlnum`／`commitLatchedAlnum`／`handleLatchedAlnumInput`），兩倉 feature commit 隨之 amend（`0cb3f14`→`427cfba`、`d47d7bb7`→`441186a8`），訊息與計數未變；本文之概念敘述已同步，未實作之提案識別字則維持原樣並加註。
>
> **施行現況（2026-09-20 定稿；本文動工前之構想與最終實作之差異）**：
> 1. **提示載體改為 StatusUI**：本文計劃沿用 `revolveTypingMethod` 之「空輸入狀態」繞道，實作途中兩度改轍——①`generateStateOfInputting(guarded: true)` 於空內容時塞入一顆空白、狀態恆為 `.ofInputting`，導致**解除後之 BkSp／Delete／Esc 仍被攔截**；②改 `State.ofEmpty()` ＋ tooltip 後攔截問題消失，但提示會被緊接著的按鍵事件之 `switchState` 換掉、連續打字時不可見。**最終作**：新增 `SessionCoreProtocol.showStatusHint(_:duration:)`（protocol extension 預設實作），提示與 `state` 完全脫鉤、時長 1.5 秒。
> 2. **`MixedAlnumConfig` 已由獨立新檔併入** `Sources/LibVanguard/Typewriter/Typewriter_MixedAlphanumerical.swift`（檔內 `// MARK: - MixedAlnumConfig`）。
> 3. **兩個復位粒度之收斂**：`resetAll()` 之唯一呼叫點為 `releaseLatchedAlnumState(announce:)`（即解除之唯一出口），先前「無呼叫點」之落差已消除。
> 4. **測試**：`test_IH442`～`test_IH448`（7 支／11 案例），含兩開關四態、五把解除鍵之攔截語意、「解除後 BkSp 必須放行」與 StatusUI 之發出斷言。
> 5. **四語系文案**已定稿為 `\n` 條列（5 條目）。
>
> **修訂記錄（共七輪）**：
> ① 2026-09-20 初稿。
> ② 同日第二輪——事主就狀態承載、tooltip、重設契機、命名、解除語意、偏好方案、優先序七項作出指示；其中「遷移機制已存在」一項推翻初稿之「無遷移機制」判斷（§2.1 已更正）。
> ③ 同日第三輪（Wave 2）——解除面收斂（除 `performServerActivation` 外不增額外觸發時機）、tooltip 載體定案、BkSp／Delete 定案、偏好方案定為乙案、Esc 入列。此輪使 Wave 1 之 `isASCIIMode` 結論**失效**（D8′／H1），並新增 §四·群六。
> ④ 同日第四輪（Wave 3）——`isASCIIMode` toggle 納入解除、四鍵攔截語意定案（Enter 放行）、Option+BkSp 納入、`resetInputHandler()` 納入解除。此輪新增 §四·群七（R1–R9），並將 §五 改寫為 **DoD：已定案與未決清單**。
> ⑤ 同日第五輪（Wave 4）——R8 採 (i)；進入條件以既有判定為基礎（另有 history 之提案）；**閂滯僅限英文**（「閂滯於中打」不存在）；`resetInputHandler()` 之解除一律靜默、`handleEvent(nil)` 可解除；命名定讞並附四語系文案草案（§2.5）；**新增「Tab／方向鍵之新規定」**（§5.1）。
> ⑥ 同日第六輪（Wave 5）——進入條件之「結合判定因素」**擱置**；新規定之用詞更正為 **`assembler`**（不涉注拼槽）；D10′ 重寫為人話（§四·D10′）；並修正本文一處筆誤（大千之 `-` 為 ㄦ、非 ㄥ）。
> ⑦ 同日第七輪（Wave 6）——**標點規則定案**（含 ASCII 解析工具之選定與陷阱之最優解）；**「新規定」之定義與適用範圍界定為閂滯態專屬**；新增 **§5.4 手術後人工測試清單**。§5.2 未決清單**全數結案**。
>
> **前置脈絡**：
> - Phase 233（Tekkon 新增讀音序列檢證 API `isSequentiallyTypedRawKeyOrder`）。
> - Phase 234（以該 API 改良 MixedAlnum 之英文判定；已 commit 為 `vChewing-LibVanguard` `215e69f`／`vChewing-macOS` `d770629a`）。
> - `vChewing-DevLogs/Research/Phase233_PostReport.md`、`PendingFeatureReqs/PendingApproval/FR608-PreResearch-v1a/v1b/v2.md`。
> - 微軟新注音 2007 反組譯研究（`_ResearchScratch/_MSIMEResearch/MSIME-AutoAlnumModeSwitch-ResearchReport.md`）。
>
> **本文之資料來源**：全部為**靜態閱讀現況碼**（兩倉 HEAD）＋ 一項 `UserDefaults` 型別行為之**離線實測**（§2.1）。凡屬推論者皆已標註。

---

## 一、草案原文與事主補充

### 1.1 草案（2026-09-20 提出，原文照錄）

> ```
> UserDef / Prefs 體系棄用 `kMixedAlphanumericalEnabled`，改為一個新的三元開關（rawValue: Int)。
>
> - 開關 enum 名稱：`UserDef.kMixedAlnumPreference`，RawValue Type: Int, Default Value: 0.
> - PrefMgrProtocol 可以新增 extended method `mixedAlphanumericalEnabled` 直接回 `self.mixedAlnumPreference != 0`。
> - 可用的 cases:
> 	- 0: Not Enabled.
> 	- 1: Auto-Switch (ASUS Style). // (沿用唯音輸入法 4.8.3 版為止的行為，包括咱們剛才實作的 P234 的行為).
> 	- 2: Manual-Switch (Microsoft Style).
> ```

### 1.2 第一則補充（`Semi-Auto Switch` 之落地方式；命名同日改定）

> 「不要想著切換 TIS 狀態。取而代之的是給 MixedAlnum 加上一個子狀態：該狀態在 Auto-Switch 不起作用，但 **Semi-Auto Switch** 會用來固定當前被閂滯到的中打/英打行為。如果當前被閂滯到英打行為的話（與 `isASCIIMode` 不是一回事，不要搞混），所有敲出的 ASCII 內容都得立刻 commit。但使用者敲 Enter / BkSp / Delete 等 trigger key 的時候會立刻取消對英打行為的閂滯。對英打的閂滯狀態也得體現在 tooltip 上。」

> **命名改定（同日）**：草案之 `Manual-Switch` **改名為 `Semi-Auto Switch`**。本文以下一律用新名。

### 1.3 第二則補充（解除時機）

> 「閂滯行為追加其他解除時機：InputHandler 自身的 clear 行為。」

### 1.4 第三則補充（同日第二輪，七項）

1. **狀態承載**：狀態放在 `InputHandler`；並可考慮為「MixedAlnum 會用到的屬性」新增專有 config type，將所有 MixedAlnum 特有之 InputHandler properties 收斂成同一個 Config-based Property。
2. **Tooltip**：調查 `.ofCommitting` 狀態本身是否會有 tooltip；若無且 Session 端缺乏支援，另有 `StatusUI` 可用。惟微軟新注音不對此狀態提供 tooltip，故**此處之 tooltip 需求可暫時記入備忘**，待日後有使用者提出 FeatureRequest 再議。
3. **重設契機**：掛在 session 的 `activateServer` 等「這個 Session Singleton 剛剛被選用」之時刻。本專案之 Session 現為**極性雙緩衝（Dual-Singleton Polarity）**模式；總之不要讓閂滯狀態之生存超出當前打字會話 context。
4. **BkSp／Delete 之解除為 blocked-action**：處理該行為時對 IMK 回傳 `true`；並以 **Inputting 狀態之 tooltip** 提示使用者「已解除對英打行為的閂滯」。
5. **偏好方案**：評估另一思路——不撤掉 `kMixedAlphanumericalEnabled`，改為追加一個預設值為 `false` 的 `kEnableLatchedAlnumStateInMixedAlnumMode`。
6. **`isASCIIMode` 之優先級別遠高於 Typewriters。**
7. （原文另註）`UserDef` 之資料遷移行為發生在 `PrefMgrProtocol` 層面，惟具體位置待查。

### 1.5 第四則補充（Wave 2，2026-09-20，四項裁定）

1. **解除面收斂**：先不為「解除行為閂滯」增設額外觸發時機；**除 `performServerActivation` 確定觸發解除之外**，Wave 1 第二則補充之「`InputHandler` 自身的 clear 行為」**撤回**。惟須說明其隱患（本文 §四·群六）。
2. **Tooltip 方案定案**：採 `revolveTypingMethod` 所用之方法（即 `guarded: true` 之可為空輸入狀態 ＋ tooltip，見 D3′）。
3. **BkSp／Delete 定案**：閂滯於英打時字元已立刻 commit 至客體，故該鍵**不刪字、只解除**；此行為**需要 tooltip 視覺反饋**。
4. **偏好方案定案**：**不做三元開關**；採 §2.2 之乙案（追加 `kEnableLatchedAlnumStateInMixedAlnumMode`，預設 `false`）。

### 1.5b 第五則補充（同日，Wave 2 追加）

> 「**Esc 鍵也是觸發解除閂滯行為的 trigger key**。」

⇒ trigger key 之清單確認為 **Enter／BkSp／Delete／Esc** 四者。（此項解消了本文初稿所担心之「無逃生口」隱患；惟仍留下一項逐鍵放行語意之待裁定，見 H9。）

### 1.5c 第六則補充（Wave 3，2026-09-20，五項裁定）

1. **`isASCIIMode` 之 toggle 得解除閂滯**——採前述 (b) 案（將該變更列為解除點）。
2. **trigger key 之攔截語意定案**：**僅 BkSp／Delete／Esc 攔截**；**Enter 於觸發解除之後放行**。（事主並提示：專案內應已有類似 「Esc Clean Composition Buffer」之攔截先例。）
3. **Option+BkSp 得解除閂滯、且不攔截**。
4. **`resetInputHandler()` 仍觸發對閂滯之解除**（惟事主要求列出風險）。
5. 據此更新 DoD 未決清單。

### 1.5d 第七則補充（Wave 4，2026-09-20，七項裁定）

1. **R8**：trigger key 之分支**置於護欄之前**（採 (i)）。
2. **D5′（進入條件）**：以**既有判定**為基礎。**（同日 Wave 5 補充：「連續落空門檻」之結合判定因素已擱置、不納入本階段。）**
3. **D7′＋D11′**：**只有英文可以被閂滯**（無「閂滯於中打」）。⇒ 閂滯態降為二值：{ 未閂滯, 閂滯於英打 }。
4. **R4＋R1**：`resetInputHandler()` 之解除**一律靜默**；`handleEvent(nil)` **可以**解除——該事件係 macOS Emoji 面板所觸發。
5. **D10′**：**原文僅列項、未附決定**（該項已於 Wave 6 定案，見 D10′）。
6. **D4′ 遺留（同日補充修正為「新規定」）**：閂滯於英打時 Space 之語意為「即刻遞交半形空格」；**只要 `assembler` 與 MixedAlnum 緩衝區皆為空，Tab／方向鍵即直接洩漏給客端**。事主明示此為「**新規定**」——即不僅是現況記述，而係一條須被遵守之要求。其與現況之落差見 §5.1〈按鍵語意〉。
   > **Wave 5 更正**：事主原用「composition buffer」一詞，後更正為 **`assembler`**（亦即新規定**不涉注拼槽**）。本文已按 `assembler` 理解。
7. **命名與文案**：UserDef 鍵名定讞為 **`kEnableLatchedAlnumStateInMixedAlnumMode`**（同日曾一度定為另一寫法，旋即更正為單數 `State`、且 `Alnum` 而非 `Alphanumerical`）；文案不再提 `Semi-Auto Switch`，改用 `Enable latched alphanumerical state in mixed alphanumerical mode` 此較準確之稱謂；Description 須寫到足夠詳細。

### 1.5e 第八則補充（Wave 6，2026-09-20，三項）

1. **標點之定案**：閂滯於英打時，標點鍵**一律直接 commit 該按鍵在當前英數鍵盤佈局下、連同修飾鍵所對應的 ASCII 符號**（committed result 可能因修飾鍵而異）；「閂滯」之新規則**發生在中文標點查詢之前**；`matchesCJKPunctuation` 之實作陷阱**按本文認為之最優解迴避**。
2. **「新規定」之定義須界定**（並重申本次手術之總前提）：「本次手術所有新行為都是在『閂滯模式開關 ON』且『mixedAlnum 模式 ON』時才生效」。⇒ 已於 §5.1〈新手術總前提〉與〈新規定（界定後）〉兩處界定。
3. **`guarded: true` 列入「手術後需要人工測試」之情況**。⇒ 已建 §5.4。

### 1.6 本文之範圍

只做可行性辨識，不做設計；不提出最終 API、不寫規格、不改任何程式碼。

---

## 二、草案本體之可實作性核對

### 2.1 偏好遷移：**機制已存在**，且已有「舊 Bool → 新 Int」之直接前例（初稿此處判斷有誤，已更正）

**初稿之錯誤**：本文初稿寫「`UserDef` 內無任何遷移機制」。**實查有誤**——遷移不在 `UserDef`，而在 **PrefMgr 層**：`PrefMgr_Core.fixOddPreferencesCore()`（`Sources/Shared/PrefMgr_Core.swift:456`）於結尾呼叫 `migrateDeprecatedSettings()`（同檔 `:510`）。

**該函式內已有兩類可直接沿用之樣式**：

1. **多元選項之合法性糾錯**（`fixOddPreferencesCore()` 內）：
   ```swift
   if ![0, 1, 2].contains(spaceKeyBehaviorAgainstICB) { spaceKeyBehaviorAgainstICB = 1 }
   ```
   ⇒ 三元開關之值域防護可完全比照。
2. **「舊版 Bool → 新版 Int」之遷移**（`migrateDeprecatedSettings()` 內，鍵 `ChooseCandidateUsingSpace` → `spaceKeyBehaviorAgainstICB`）：
   ```swift
   let oldKey = "ChooseCandidateUsingSpace"
   if let oldValue = defaults.object(forKey: oldKey) {
     if let oldBool = oldValue as? Bool {
       if spaceKeyBehaviorAgainstICB == 1 { // 僅在仍為預設值時遷移。
         spaceKeyBehaviorAgainstICB = oldBool ? 1 : 0
       }
     }
     defaults.removeObject(forKey: oldKey)
   }
   ```
   ⇒ **這正是本草案所需之遷移形狀**（舊 `kMixedAlphanumericalEnabled` 為 `Bool`、新鍵為 `Int`），連「僅在新鍵仍為預設值時才遷移」之護欄都已有先例可循。

**另有一項事實值得記錄**：`AppProperty` 之取值為 `container.object(forKey: key) as? Value ?? defaultValue`（`.../VanguardSwiftExtension/Sources/SwiftExtension/SwiftFoundationImpl.swift:196` 起）——**型別不符即靜默回退預設值**。故若**不做遷移**且換鍵名，既有已啟用者會靜默失去功能。既然遷移機制已存在，（初稿所提之）「沿用同鍵以省遷移」之權宜做法**已無必要**。
（該權宜做法之實測結論仍有效、一併記錄：`UserDefaults` 內 `Bool(true)` 以 `as? Int` 讀會經 `NSNumber` 橋接為 `1`，`Bool(false)` 讀為 `0`，鍵不存在則 `nil`；反向 `Int` → `as? Bool` 為 `nil`。腳本存於 `_ResearchScratch/_P234Post/udtest-UserDefaults-CrossType.swift`。）

### 2.2 偏好方案之評估：草案之三元開關 vs. 事主提出之「追加子開關」

事主提出之另一思路：**不撤掉 `kMixedAlphanumericalEnabled`（Bool），改為追加 `kEnableLatchedAlnumStateInMixedAlnumMode`（Bool，預設 `false`）**。兩種編碼之對照：

| 面向 | 甲案：三元開關（草案） | 乙案：追加子開關（事主提出） |
|---|---|---|
| 狀態編碼 | `kMixedAlnumPreference: Int`（0／1／2） | `kMixedAlphanumericalEnabled: Bool` ＋ `kEnableLatchedAlnumStateInMixedAlnumMode: Bool` |
| 語意映射 | 0＝關；1＝Auto；2＝Semi-Auto | (false, ＊)＝關；(true, false)＝Auto；(true, true)＝Semi-Auto |
| 資料遷移 | **需要**（機制已有，見 §2.1） | **不需要**（舊鍵語意不變、新鍵預設 false） |
| 既有行為變更 | 無（只要遷移寫對） | **無**（純追加） |
| 原始碼 6 處閘門（見 D4） | 每處都要改寫成三元判斷 | 6 處之既有閘門**一字不動**；祇有需要 Semi-Auto 感知者追加一個內層判斷 |
| 測試 30 處賦值 | 需改（除非 extended method 連 setter 一併給） | **零改動** |
| i18n | 新鍵 4 語系 × 5 條 ＝ 20 條；舊鍵 8 條待處置 | 新鍵 4 語系 × 2 條 ＝ 8 條；舊鍵 8 條不動 |
| 非法態 | 無 | 有：(false, true)＝「子開關開、母功能關」——語意空洞，須以 UI 依附（母關則子禁用／隱藏）＋程式護欄吸收 |
| 擴充性 | 佳（日後加第 4 態即加一個 option） | 差（再加一態就得改用位元或改型別） |
| 回退成本 | 中 | 低（新鍵一刪即回舊觀） |

**評估**：
- **乙案在本次之風險與成本上明顯較優**：它把「偏好治理」與「Semi-Auto 行為」徹底解耦——前者零改動，後者是一個純追加。初稿所列之 D13／D14／D15（遷移、呼叫端、i18n 之遷移面）**在乙案下幾近消失**，而 D4 之六個決策點亦縮減為「哪幾處需要感知子開關」。
- **乙案之唯一實質代價是非法態**（母關子開）。SwiftUI 側已有依附式呈現之先例——`.disabled(<另一個偏好>)` 見 `VwrSettingsPaneCandidates.swift:26`（`.disabled(useRearCursorMode)`）與同檔 `:52`／`:54`。**惟 Cocoa 側無此先例**：`Packages/vChewing_SettingsUI/Sources/SettingsUI/SettingsCocoa/VwrSettingsPaneCocoaBehavior.swift` 內 `enabled`／`disabled`／`isEnabled` 皆 0 命中（實查），故「母關則子禁用」在 Cocoa 面板須新寫（或改採「母關則隱藏該列」之更簡單做法）。此為乙案在本倉之**唯一新增 UI 工作量**；程式端只需在讀取點以 `mixedAlphanumericalEnabled && enableLatchedAlnumStates` 取合。
- **甲案之優勢在語意與擴充性**，但那屬**長期**考量。若日後真需要第 4 態，屆時再遷移即可——而 §2.1 已證明遷移機制存在且形狀現成。
- **建議採乙案**。惟若事主仍偏好甲案，其成本亦已清楚（遷移 1 處 ＋ 6 處閘門改寫 ＋ 30 處測試賦值 ＋ 20 條 i18n），非不可行。

> **【已裁定（Wave 2 第 4 項）】採乙案；甲案（三元開關）不實作。** 以下凡提及「甲案」之段落皆保留為評估記錄，不再作為施工依據。

### 2.3 狀態承載：Config-based Property 之收斂（事主第三則補充第 1 項）

**現況**：`InputHandler` 上屬 MixedAlnum 專有者僅 `mixedAlphanumericalBuffer`（`Sources/LibVanguard/InputHandler/InputHandler.swift:74`；協定宣告於 `InputHandler_CoreProtocol.swift:49`）。若採行 Semi-Auto，至少再增一個閂滯態旗標，屆時「零散 transient 欄位」的問題才會成立。

**既有先例（可直接比照）**：`Homa.Assembler`——
```swift
// Sources/Homa/Homa_MainComponents/Homa_Assembler.swift:71
public internal(set) var config = Config()
// 其後每一員皆為薄存取器（同檔 :84 起）：
public var keys: [PossibleKey] { get { config.keys } set { config.keys = newValue } }
```
`Homa.Config`（`Sources/Homa/Homa_BasicTypes/Homa_Config.swift:9`）本身是 `public struct Config: Codable, Hashable`，帶完整 `init` 預設值與 `didSet` 值域糾錯。

**落點建議**：新增 `MixedAlnumConfig`（內含 `buffer: String` 與 `stickiness` 等），以 `@AppProperty`… **否**——此為**執行期狀態**、非偏好，不應進 `UserDef`。應比照 `Homa.Config` 做成值型別，並於 `InputHandler` 以 `public internal(set) var mixedAlnumConfig = .init()` 持有，其後以薄存取器維持 `mixedAlphanumericalBuffer` 之既有呼叫端不變。
**注意**：`Homa.Config` 帶 `Codable` 係為組字器快照用途；MixedAlnum 之 config **不需要** `Codable`／`Hashable`，勿照抄。
**附帶收益**：`Typewriter_MixedAlphanumerical.swift` 內現有 **14 處** `mixedAlphanumericalBuffer.removeAll()`（11 處在本檔、2 處在 `InputHandler_HandleStates.swift`、1 處在 `InputHandler_CoreProtocol.swift`），收斂後可改為對 config 之單一 reset 方法。

### 2.4 三元／雙開關之設定介面：兩側 renderer 皆已支援

- SwiftUI 側 `UserDefRenderableImpl.swift:331` 有 `case .integer where !options.isEmpty:`（下拉選單）；Cocoa 側 `UserDefRenderableCocoa.swift:17` 起亦對 `metaData.options` 有所處理。
- 甲案比照 `kSpaceKeyBehaviorAgainstICB`（`.integer(1)` ＋ `options: [0:…,1:…,2:…]`）即可；乙案則新增一個 `.bool(false)` 項，並需在該項之呈現上依附母開關：SwiftUI 側可循 `VwrSettingsPaneCandidates.swift:26` 之 `.disabled(useRearCursorMode)` 先例；**Cocoa 側無先例**——實查 `Packages/vChewing_SettingsUI/Sources/SettingsUI/SettingsCocoa/VwrSettingsPaneCocoaBehavior.swift` 內 `enabled`／`disabled`／`isEnabled` 皆 0 命中，故須新寫（或改採「母關則隱藏該列」）。

### 2.5 命名與文案（Wave 4 定讞）

#### 2.5.1 識別名

| 項目 | 值 |
|---|---|
| `UserDef` case | `kEnableLatchedAlnumStateInMixedAlnumMode` |
| `rawValue`（即 UserDefaults 鍵） | `"EnableLatchedAlnumStateInMixedAlnumMode"`（依本倉慣例：case 名之 `k` 前綴不入 rawValue；參 `kSpaceKeyBehaviorAgainstICB = "SpaceKeyBehaviorAgainstICB"`） |
| `dataType` | `.bool(false)` |
| 使用者可見名稱（en） | `Enable latched alphanumerical state in mixed alphanumerical mode` |
| 廢語 | 不再使用 `Semi-Auto Switch`（Wave 4 第 7 項） |
| 顯示位置 | 「行為設定」頁、緊鄰 `kMixedAlphanumericalEnabled`（延續 FR608-v1a §三 之裁定） |

> **備註**：事主同日曾一度定為另一寫法，旋即更正為本名（單數 `State`、且 `Alnum` 而非 `Alphanumerical`）。本文一律以本名為準。

#### 2.5.2 `shortTitle`（四語系）

- **en**：`Enable latched alphanumerical state in mixed alphanumerical mode`
- **zh-Hant**：`啟用中英混打模式的英數閂滯狀態`
- **zh-Hans**：`启用中英混打模式的英数闩滞状态`
- **ja**：`中英混在モードで英数のラッチ状態を有効化`

> **附註**：依事主指定，en 之 shortTitle 即採完整稱謂（較本倉其他開關之標題長）。若日後覺得設定面板內過寬，可另備短版（如 `Enable latched alphanumeric state`）——但不建議，蓋因縮短後極易與「啟用中英混合輸入回退」混淆。

#### 2.5.3 `description`（四語系草案；依事主指示寫至足夠詳細）

**共同涵蓋之要點**（共 11 項，四語系一一對應）：
① 依附於母選項、預設關閉；② 判定落定後予以固定；③ 其後每一顆可列印 ASCII 即刻遞交；④ 效果＝連續打英文之體驗接近英數模式；⑤ 帶提示之解除鍵（Enter／BkSp／Delete／Esc／Option+BkSp）；⑥ **誤解防範**：BkSp／Delete／Esc 只解除、不送不刪（內容已遞交、無從回收）；⑦ 不解除之鍵（Space／Tab／方向鍵，其中 Space 會遞交半形空格；Tab 與方向鍵在組字緩衝區為空時直接放行給客體）；⑧ 靜默自動解除之三情形（切中英數模式／換客體／重新啟用）；⑨ 與英數模式之區別（唯音仍為中文打字模式）；⑩ 「閂滯」僅作用於英文；⑪ 落定前之最初幾顆按鍵仍逐鍵判定。

**zh-Hant**
```
本選項僅在「啟用中英混合輸入回退」已開啟時才有作用，且預設為關閉。
開啟後，中英混打模式對英數內容的判定結果會被「閂滯」住：一旦判定落定為英文，其後敲出的每一顆可列印 ASCII 字元都會立刻遞交給當前的輸入客體，不再累積在輸入法內等待確認，直到您按下解除鍵為止。這讓「一次打一整串英文」的體驗接近英數輸入模式，而不需逐段確認。
解除鍵（按下時輸入法會以內文提示告知您已解除）：Enter（解除後放行，不作攔截）、BackSpace、Delete、Esc、Option+BackSpace。
請特別留意：BackSpace、Delete 與 Esc 只會解除閂滯，並不會送出或刪除任何字元——因為先前的英數內容早已遞交出去，輸入法無從回收。也就是說，這些鍵並不能「撤銷」您剛剛打的英文。
不會解除閂滯的按鍵：鍵盤空白鍵（閂滯於英打時會即刻遞交一個半形空格）、Tab 鍵與方向鍵（組字緩衝區為空時，這些鍵會直接放行給輸入客體）。
以下情形會自動解除閂滯（不另發提示）：切換中英數模式（Shift 鍵、CapsLock 鍵、或 JIS 英數鍵）、切換到另一個輸入客體、或輸入法被重新啟用。
請注意：本選項並不是把唯音切換成英數模式——唯音仍處於中文打字模式，只是中英混打的判定結果被固定住了而已。另外，「閂滯」只作用於英文，不存在「閂滯於中文」的狀態；而在判定落定之前的最初幾顆按鍵，仍會走原有的逐鍵判定。
若您感受不到「判定結果被固定」所帶來的差別，建議維持關閉本選項。
```

**zh-Hans**
```
本选项仅在「启用中英混合输入回退」已开启时才有作用，且默认为关闭。
开启后，中英混打模式对英数内容的判定结果会被「闩滞」住：一旦判定落定为英文，其后敲出的每一颗可打印 ASCII 字符都会立刻递交给当前的输入客体，不再累积在输入法内等待确认，直到您按下解除键为止。这让「一次打一整串英文」的体验接近英数输入模式，而不需逐段确认。
解除键（按下时输入法会以内文提示告知您已解除）：Enter（解除后放行，不作拦截）、BackSpace、Delete、Esc、Option+BackSpace。
请特别留意：BackSpace、Delete 与 Esc 只会解除闩滞，并不会送出或删除任何字符——因为先前的英数内容早已递交出去，输入法无从回收。也就是说，这些键并不能「撤销」您刚刚打的英文。
不会解除闩滞的按键：键盘空白键（闩滞于英打时会即刻递交一个半角空格）、Tab 键与方向键（组字缓冲区为空时，这些键会直接放行给输入客体）。
以下情形会自动解除闩滞（不另发提示）：切换中英数模式（Shift 键、CapsLock 键、或 JIS 英数键）、切换到另一个输入客体、或输入法被重新启用。
请注意：本选项并不是把唯音切换成英数模式——唯音仍处于中文打字模式，只是中英混打的判定结果被固定住了而已。另外，「闩滞」只作用于英文，不存在「闩滞于中文」的状态；而在判定落定之前的最初几颗按键，仍会走原有的逐键判定。
若您感受不到「判定结果被固定」所带来的差别，建议维持关闭本选项。
```

**ja**
```
この項目は「中英混在入力のフォールバックを有効化」がオンの場合にのみ機能し、既定ではオフです。
オンにすると、中英混在モードの英数内容に対する判定結果がラッチされます。英文と判定された時点以降、打鍵した印字可能な ASCII 文字は一文字ずつ直ちにクライアントへコミットされ、解除キーを押すまで入力法内に蓄積されません。これにより「英文をまとめて一気に入力する」体験が英数入力モードに近くなり、逐次確認が不要になります。
解除キー（押すと入力法がインライン通知で解除をお知らせします）：Enter（解除後に通過させます。傍受しません）、BackSpace、Delete、Esc、Option+BackSpace。
ご注意：BackSpace・Delete・Esc はラッチを解除するだけであって、文字を送信も削除もしません。先に打った英数内容はすでにコミット済みで、入力法側から取り消せないためです。つまりこれらのキーで「今打った英文を撤回」することはできません。
ラッチを解除しないキー：スペースキー（ラッチ中は半角スペースを即座にコミットします）、Tab キーと方向キー（組字バッファが空のとき、これらのキーはそのままクライアントへ通過します）。
次の場合はラッチが自動的に解除されます（通知は出ません）：英数モードの切替（Shift キー・CapsLock キー・JIS 英数キー）、別の入力クライアントへの切替、入力法の再有効化。
ご注意：この項目は唯音を英数入力モードに切り替えるものではありません。唯音は中文入力モードのままで、中英混在の判定結果が固定されるだけです。また、ラッチは英文にのみ作用し、「中文にラッチされる」状態は存在しません。判定が確定するまでの最初の数打鍵は、従来どおり打鍵ごとの判定になります。
「判定結果が固定される」違いをはっきり感じられない場合は、オフのままでを推奨します。
```

**en**
```
This option takes effect only when "Enable mixed Chinese-English typing fallback" is on, and it is off by default.
When enabled, the mixed-alphanumerical mode latches its verdict on alphanumerical content: once a run is judged to be English, every subsequent printable ASCII character is committed to the input client immediately instead of accumulating inside the input method, until you press a release key. This makes typing a long English run feel closer to a plain alphanumerical input mode, without confirming it piece by piece.
Release keys (the input method notifies you with an inline tooltip when the latch is released): Enter (releases and then passes through, not intercepted), BackSpace, Delete, Esc, and Option+BackSpace.
Please note in particular: BackSpace, Delete and Esc only release the latch — they do not send or delete any character, because what you typed earlier has already been committed and the input method cannot take it back. In other words, these keys cannot "undo" the English you just typed.
Keys that do not release the latch: the Space bar (while latched, it commits a half-width space immediately), the Tab key and the arrow keys (while the composition buffer is empty, these keys are passed straight through to the input client).
The latch is released automatically, without any notification, when you toggle the alphanumerical mode (Shift, CapsLock, or the JIS Eisu key), when you switch to another input client, or when the input method is reactivated.
Please note: this option does not switch vChewing into an alphanumerical input mode. vChewing stays in Chinese typing mode; only the verdict of its mixed-typing judgement is latched. Also, the latch applies to English only — there is no such state as "latched to Chinese". The first few keystrokes, before a verdict is reached, still go through the per-keystroke judgement as before.
If you cannot clearly perceive the difference that a latched verdict makes, leaving this option off is recommended.
```

> **附註**：以上四語系草案僅供實作時填寫 `.strings` 之用；實作時須另遵 i18n 流程（key 名前綴、`LocalizableFileSorter` 排序、四語系齊備）。本文不做 `.strings` 異動。

---

## 三、閂滯態之語意界定

### 3.1 三個「不是」

1. **不是 TIS／系統輸入源切換**（事主明示）。
2. **不是 `isASCIIMode`**（事主明示）。`isASCIIMode` 由 Shift／Eisu／CpLk 切換，其狀態存於**跨客體**容器（`InputSession.isASCIIModeForAllClients`／`isASCIIModeForEachClient`，`Sources/LibVanguard/Session/InputSession.swift:50-53`）；閂滯態則仍在中文模式下、只改 MixedAlnum 之行為分支。
3. **不是微軟新注音之功能 A（逐字元閘門）之照搬**。微軟之 `CPhoneticConvModeless::OnChar` 是「非注音字元 ⇒ 先 `Settle()` 再一律回 1」，**每一鍵各自判定、不留狀態**；本草案反而**留一個閂滯狀態**。兩者雖同為「不做中英競賽」，狀態機形狀相反。

### 3.2 子狀態模型（Wave 6 後之最終形狀）

> **Wave 4 第 3 項之簡化**：閂滯態**只有英文一種**（「閂滯於中打」已裁定不存在）。故子狀態降為二值：`hasLatchedAlnumState: Bool`（提案名；換稱前作 `hasLatchedEnglishAlnumState`，最終實作則作 `MixedAlnumConfig.isLatchedToAlnum`）。

```
MixedAlnum 模式（母開關啟用）
  ├─ 閂滯功能關閉（`kEnableLatchedAlnumStateInMixedAlnumMode == false`，預設）
  │    ⇒ 行為與 4.8.3 之前完全一致（Auto）
  └─ 閂滯功能開啟
       │  未閂滯：跑既有判定管線（與 Auto 同）；判定落定為英文時 → 進入閂滯
       │          （進入條件僅取既有判定；結合判定因素已於 Wave 5 擱置）
       └─ 已閂滯於英打：
             · 每一顆可列印 ASCII → 即刻 commit（進 mixedAlphanumericalBuffer）
             · 每鍵 commit 後 state 為 `.ofEmpty`（R8）
             · Space → 即刻遞交半形空格（Wave 4 第 6 項）
             · 標點 → 一律遞交「該鍵在當前英數佈局下、連同修飾鍵所對應之 ASCII 字元」（復用 `resolveVisibleInputText`）；
             │    規則置於中文標點查詢**之前**（Wave 6 定案）
             · Tab／方向鍵 → 新規定：**`assembler`** 與 MixedAlnum 緩衝區皆空 ⇒ 直接洩漏給客端
             │    （閂滯態下兩者本已洩漏；若立為通用規則，Tab 之護欄須放寬——見 §5.1）
             · 不為「閂滯於中打」——不存在該態（Wave 4 第 3 項）

解除（帶提示者標 ▲，靜默者標 △）：
  ▲ Enter → 解除後放行（不攔截）                  [Wave 3]
  ▲ BkSp／Delete／Esc → 解除且**攔截**（回 true）  [Wave 3]
  ▲ Option+BkSp → 解除、不攔截                    [Wave 3]
  △ `isASCIIMode` 之 toggle（由 `resetInputHandler()` 涵蓋） [Wave 3]
  △ `resetInputHandler()`（一律靜默）              [Wave 3＋4]
  △ `handleEvent(nil)`（macOS Emoji 面板觸發，可解除） [Wave 4]
  保險：`performServerActivation()`（不呼 `resetInputHandler`，須獨立實作）

【已撤回】`InputHandler.clear()` 本身（Wave 2 第 1 項）
【施工限制】① 解除不得寫入 `clear()`，須為 `resetInputHandler()` 內之獨立語句（R2）
            ② trigger key 之分支須置於三處 `.ofInputting` 護欄**之前**（Wave 4 第 1 項）
            ③ `MixedAlnumConfig` 須有兩個復位粒度（H5）
【Tooltip】解除之 ▲ 類帶提示（`guarded: true` 之輸入狀態）；△ 類一律靜默（Wave 4 第 4 項）。
```

---

## 四、難點清單（Wave 6 後之定版）

### 群一：狀態承載

**D1′｜狀態放 InputHandler——已定案；惟須留意 `@frozen struct` 之改建構。**
`MixedAlphanumericalTypewriter` 是 `@frozen public struct`（`Typewriter_MixedAlphanumerical.swift:9-10`）且**每鍵重新建構**（`InputHandler_HandleComposition.swift:31`），故狀態只能落 handler——此與事主定案一致。§2.3 之 `MixedAlnumConfig` 收斂為建議之落地形狀。

**D2′｜「每鍵立刻 commit」與「`clear()` 解除閂滯」互相矛盾——Wave 2 已裁定撤回後者。** **【硬】**
實查：

```swift
// Sources/LibVanguard/Session/SessionCoreProtocol.swift:94-105（switchState 內）
case .ofAbortion, .ofCommitting, .ofEmpty:
  if next.type == .ofCommitting { commit(text: next.textToCommit) }
  else if next.type == .ofEmpty, previous.hasComposition, let inputHandler { … }
  inputHandler?.clear()            // ← 第 102 行
  if state.type != .ofEmpty { state = .ofEmpty() }
```

而 `InputHandlerProtocol.clear()`（protocol extension，`InputHandler_CoreProtocol.swift:211`）會連帶呼叫 `clearComposerAndCalligrapher()`。⇒ **`switchState(.ofCommitting)` 恆會呼叫 `inputHandler.clear()`。**

**矛盾**：閂滯於英打時，每一顆 ASCII 按鍵都要 commit；每次 commit 都走 `.ofCommitting`；每次 `.ofCommitting` 都 `clear()`。若把解除掛在 `clear()`，則**第一顆鍵就解除閂滯**，功能當場自我消滅。

> **【已裁定（Wave 2 第 1 項）】**：不掛 `clear()`；解除點收斂為 **trigger key ＋ `performServerActivation`**。此舉解消了上述矛盾，但**引入了四項新隱患**（含一項推翻本文 Wave 1 之結論者），見 §4·群六。

**遺留之施工約束**：`SessionCoreProtocol.swift:102` 那行 `inputHandler?.clear()` 會連帶清 `assembler`、`purgeInputTokenHashMap()`、復位 `currentTypingMethod`——閂滯於英打時**每鍵都要付這筆成本**（見 D17′）。

**D3′｜Tooltip：問題已釐清，需求暫緩（事主第二則補充）。**
**調查結論**：
- `.ofCommitting` **可以**帶 tooltip——`switchState` 不分狀態型別，一律把 `state.tooltip` 轉給 `showTooltip(...)`（`SessionCoreProtocol.swift:121-125`）。故「Commit 狀態有沒有 tooltip」**不是型別限制**。
- **但定位不可靠**：`tooltipAnchorRect()` 對非 `.ofInputting` 狀態一律沿用「組字區最前方之矩形」（`InputSession_HandleDisplay.swift` 該函式之註解明載）；而 commit 之後 `updateCompositionBufferDisplay()` 已清空 marked text，該矩形無從量得。
- **專案已有繞道**：`InputHandler_TypingMethod.revolveTypingMethod`（`:44`）之收尾——
  ```swift
  session.switchState(State.ofCommitting(textToCommit: committableDisplayText(sansReading: true)))  // :69
  updatedState = generateStateOfInputting(guarded: true)                                            // :70
  updatedState.tooltipDuration = 0                                                                  // :71
  updatedState.tooltip = newMethod.getTooltip(vertical: session.isVerticalTyping)                    // :72
  session.switchState(updatedState)
  ```
  `guarded: true` 正是「即使 `isConsideredEmptyForNow` 也照樣生成 `.ofInputting`」之開關（`InputHandler_HandleStates.swift:333` 之參數、`:337` 之 guard）。⇒ **可為空之輸入狀態 ＋ 恆久 tooltip** 這條路已在生產環境上線多時（4.7.4 起之打字模式提示）。
- **另有 `ui?.statusUI` 獨立通道**（`Sources/Shared/Protocols/SessionUIProtocol.swift:17`）：`maybeShowModeDescriptionHintUponActivation()`（`SessionProtocol.swift:326`）以 `.ofEmpty()` ＋ tooltip ＋ `statusUI.show(...)` 顯示 0.7 秒之模式提示，與 state 之 tooltip 機制並存。

**處置（Wave 2 定案）**：**解除時之視覺反饋採 `guarded: true` 之可為空輸入狀態 ＋ tooltip**（即 `revolveTypingMethod` 所用之方法）——BkSp／Delete／Enter／Esc 四者解除閂滯時一律走此路徑。閂滯態之**持續性指示**仍**記入備忘、暫不實作**（微軟新注音亦無此提示）。
**施工注意（見 H6／H8）**：解除與 tooltip 宜在同一次 `switchState` 內完成（勿比照 `maybeShowModeDescriptionHintUponActivation` 之 0.05s 延遲，否則出現「已解除但提示未至」之可觀察縫）；且該「空 `.ofInputting`」在本次是**使用者按鍵的直接回應**（既有用例是遞交後之瞬時狀態），對客體之影響未實測。

### 群二：判定與分派

**D4′｜六處閘門——乙案（§2.2）下多數不動。**
以 `mixedAlphanumericalEnabled` 為閘者共 6 處（原始碼）：
| 落點（所屬函式） | 現行語意 | 乙案下是否需感知子開關 |
|---|---|---|
| `InputHandler_HandleComposition.swift:31` | 注音鍵盤之 Typewriter 分派 | 否（仍以母開關分派） |
| `InputHandler_TriageInput.swift:162`（`triageByKeyCode()`） | Space 攔截 | **是**（閂滯於英打時應即刻遞交半形空格） |
| `InputHandler_HandleStates.swift:444`（`generateStateOfInputting()`） | Tooltip 產生 | 否（該需求暫緩） |
| `InputHandler_HandleStates.swift:881`（`handleEnter()`） | Enter／commit 分支 | **是**（Enter 為 trigger key） |
| `InputHandler_HandleStates.swift:935`（`handleBackSpace()`） | BkSp 之緩衝刪字元 | **是**（BkSp 為 trigger key） |
| `InputHandler_CoreProtocol.swift:423`（`ensureKeyboardParser()`） | 注音組合自動更正之關閉 | 否 |

⇒ 乙案把「六個獨立決策點」縮減為**三處需感知**，其餘三處不動。

**D5′｜「閂滯到英打」之進入條件——Wave 4 定方針、Wave 5 縮至單一來源。**
**已定**：進入條件**僅取既有判定**（即 Auto 已用之啟發式：`shouldPreferASCIIWordPath`、`isNotSequentiallyTypedReading`、auto-split 之成立等）。
**已擱置（Wave 5）**：事主原提之「結合判定因素」——追蹤「recent-committed single ASCII char history」——**不納入本階段**（事主原話：「算了，先不做結合判定了……先擱置」）。
> **唯供日後參考（本文已擱置但仍記錄）**：若他日重提，須先解一項定義問題——“committed” 之字面對應在 Auto 模式下不成立：一段英文串在鍵入過程中**不會**產生單字元遞交（`tod` 之 `t`／`o`／`d` 三鍵均只累積進 `mixedAlphanumericalBuffer`，直到邊界鍵才一次遞交），故該歷史在「使用者正在打英文」時恆為空；宜改追「判定事件」而非「遞交產物」。

⇒ **本項結案**（進入條件＝既有判定）。

**D6′｜閂滯態下 P234 判定管線被旁通。**
`shouldPreferASCIIWordPath`／`isNotSequentiallyTypedReading`／`bestAutoSplitCandidate`／`twoCharPrefixIsPhonetic` 在「ASCII 不進緩衝」下全部無效。因 D5′ 已定為「既有判定觸發、之後固定」，故同一批啟發式**既是進入條件、又在該態下失效**——驗證面須同時覆蓋兩種有效／無效狀態（已列入 D16′）。

**D7′｜「閂滯於中打」——Wave 4 已裁定其不存在。**
事主定調：「**目前來看，只有英文是可以被閂滯的**」。⇒ 閂滯態降為二值（{ 未閂滯, 閂滯於英打 }），**本項結案**；連帶 D11′ 之「閂滯於中打時是否維持現行哲學」亦自動消解（閂滯於英打時 Shift 僅剩大小寫語意乃當然耳）。

### 群三：與既有機制之交互

**D8′｜與 `isASCIIMode` 之邊界——Wave 1 之結論已因解除面收斂而失效，此為本文最重要的一項隱患。**
事主指示「`isASCIIMode` 之優先級別遠高於 Typewriters」，**次序部分實查成立**：
- 次序上，`InputHandler_TriageInput.swift:213` 之 `handleCapsLockAndAlphanumericalMode(input:)` **早於** `:229` 之 `handleComposition(input:)`（即 Typewriter 分派）。故 `isASCIIMode == true` 期間 Typewriter 根本不會執行、閂滯態自動失效。**此半仍成立。**
- **但後半已失效**：Wave 1 曾依「`isASCIIMode` 之 setter 已呼 `resetInputHandler()`（`SessionProtocol.swift:110-116`）→ `switchState` → `inputHandler.clear()`」推得「切進／切出 `isASCIIMode` 都會清掉閂滯態、雙重狀態不可能發生」。該推論**成立之前提是閂滯旗標隨 `clear()` 而清**；Wave 2 第 1 項既撤回 `clear()` 之解除，此推論**遂不成立**：
  - `isASCIIMode` 期間唯音**仍 active**（不觸發 activation），故 `performServerActivation` 亦不介入。
  - ⇒ **使用者 Shift 切到英數、再 Shift 切回中文，會在毫無提示之情況下發現自己仍閂滯於英打。**
  - 這是 Wave 1 本人保証「不可能發生」之事，謹此更正。

**H1（見群六）為此項之專論。**

**D9′｜trigger key 之語意——清單已定為 Enter／BkSp／Delete／Esc（Wave 2），惟逐鍵之放行語意尚未齊備。**
- **BkSp／Delete**：處理時對 IMK 回 **`true`**（攔截、不轉交客體），同時解除閂滯。**本質限制仍在**：閂滯於英打時字元已立刻 commit 至客體，輸入法無從回收，故該鍵**不刪除**已遞交之字元——其語意為「解除閂滯」而非「刪字」。**此點須於文案與實作註解中寫明**，以免使用者誤解（微軟新注音之間接行為亦同：其英數內容直接進客體）。
- **Enter**：解除閂滯。**惟攔截或放行未定、且方向與 BkSp／Delete 相反**：現行 `handleEnter()`（`:862` 起）於 `.ofInputting` 一律回 `true`（消費、不換行），但閂滯於英打時緩衝恆空、無物可遞交，若仍回 `true` 則使用者**喫不到換行**（終端機情境不可用）；而若放行則 Enter 既是「解除」又是「換行」，兩者不矛盾。⇒ 建議 Enter 為**解除 ＋ 放行**（見 H9）。
- **Esc**：解除閂滯。惟放行與否同樣未定：Esc 在 vi／全螢幕 App 係客體級按鍵，若攔截則使用者**在 vi 裡失去 Esc**（FR608-v1b §四·3 曾將「Esc 恆被消費」列為該設計之對價）。⇒ 建議 Esc 為**解除 ＋ 放行**（見 H9）。
- **提醒**：事主指示「此時需要用 Inputting 狀態的 tooltip 提示使用者已經解除對英打行為的閂滯」——載體即 D3′ 所列之 `guarded: true` 輸入狀態 ＋ tooltip。
- **仍未列之鍵**：Space（閂滯於英打時應遞交半形空格，見 D4′）、Tab、方向鍵、Shift、CpLk——均不解除。須確保使用者知道「只有這四個鍵 + 換客體才是出口」（見 H4）。

**D10′｜與標點之關係——Wave 6 定案。**

**規則**：閂滯於英打時，標點鍵**一律直接遞交「該按鍵在當前英數鍵盤佈局下、連同修飾鍵所對應的 ASCII 字元」**；此規則**發生在中文標點查詢之前**（即在 `matchesCJKPunctuation` 之前）。

**為何這是個問題（背景）**：在大千排列下，`, . / ; -` 五鍵各自兼為注音鍵（`,`＝ㄝ、`.`＝ㄡ、`/`＝ㄥ、`;`＝ㄤ、`-`＝ㄦ）；另有 `[ ] \ =` 等非注音鍵但平常會被轉為中文標點。若不特別處理，閂滯態下打英文時這些鍵會被注音或中文標點管線攔走。

**ASCII 之解析（選定之最優解）**：**直接復用既有 `resolveVisibleInputText(_:)`**（`Typewriter_MixedAlphanumerical.swift` 之 private helper）——其語意為「`input.text` 經 `applyingTransformFW2HW(reverse: false)`」，並於事件未提供 shifted 字元時，以 `inferredLatinKeyboardLayout().mapTable[keyCode]` 之第二元回填。
⇒ **修飾鍵之差異自然被涵蓋**（如 Shift+`=` 得 `+`），無須另立規則、亦無須自行維護對照表。

**Option 之字符替換**：沿用本檔既有慣例（`resolveLiteralASCIIMainAreaText` 一帶之註解：Shift 決定 base／shifted 變體，Option 之字符替換不予採用）。故 Option+字母（其 `input.text` 為 `å` 之類的非 ASCII）**不會**被閂滯分支接走，而會落到既有之 `resolveLiteralASCIIMainAreaText` 路徑、遞交其基底 ASCII。此為**刻意之重用**、非新規則。

**`matchesCJKPunctuation` 陷阱之最優解（本文選定、兩層）**：
- **第一層（主機制）**：閂滯分支置於**中文標點查詢之前**並逕回 `true`（＝「已處理」）。如此 `matchesCJKPunctuation` 在閂滯態下**根本不會被求值**——陷阱由構造上消除。**此層為必要且充分。**
- **第二層（防重構，本文一併採用）**：於 `matchesCJKPunctuation` 之計算式中增一項 `!isStickyEnglishActive` 之前提，並在其旁加註說明。
  **理由**：第一層之正確性**僅靠程式碼次序**維持。日後一旦有人重排該區塊，症狀是「閂滯態下某個標點鍵漏給上層分診」——**靜默、無編譯錯誤、且只在特定鍵上出現**（因 `return nil` 與 `return true` 之別）。第二層讓該不變式**自我防衛**，代價僅為一項條件與一行註解。
  **若您偏好單一處表達**：第一層已足夠，可逕刪第二層——但請勿改動第一層之位置（該處為載重之次序）。

**D11′｜與大小寫／Shift 之關係——Wave 4 已隨 D7′ 一併消解。**
閂滯態僅英文一種，故「閂滯於中打」不存在。閂滯於英打時 Shift 只剩大小寫語意、`shouldBlockPhoneticAbsorption`／`suffixHasUppercase` 在該態下**永不執行**（因為不進注音管線）——此為自然結果，無須額外定義。

**D12′｜生命週期——重設契機掛 `performServerActivation()`（事主定案；惟有一項實查發現）。**
本專案 Session 為**極性雙緩衝**：`InputSession.sessionEven`／`sessionOdd` 兩個預配置單例（`InputSession.swift:58-60`），經 `reassign(toAddr:)` 與 controller 綁定；而 `initInputHandler()`（同檔 `:226`）在 handler 已存在時**只重接回呼、不重建**。⇒ 掛在 handler 上之狀態**會跨 activation 存活**。

事主指示之掛點為 `activateServer`。實查 `performServerActivation()` 之範圍為 `SessionProtocol.swift:208-314`，其內**無任何** `clear`／`resetInputHandler`／`mixedAlphanumerical` 字樣，但**結尾已有**：
```swift
// SessionProtocol.swift:305
this.state = .ofEmpty()
```
⇒ **閂滯態之重設宜緊鄰此行**（與 state 復位同一拍），語意一致且位置自然。

**附帶發現（非本草案範圍，僅記錄）**：`performServerActivation()` 復位 `state` 卻**不觸碰 handler 之 `mixedAlphanumericalBuffer`**。於既有設計下，該緩衝通常已由 `performServerDeactivation()` 之 `resetInputHandler(commitExisting: false)`（`SessionProtocol.swift:188-195`）清掉，故未必可達；惟兩者之復位範圍不對稱，日後若為 config 收斂（§2.3），此處值得一併對齊。

### 群四：偏好治理

**D13′｜遷移機制已存在（初稿判斷有誤，已更正）。** 詳 §2.1。

**D14′｜甲案之呼叫端遷移面（乙案下多數消失）。**
- 原始碼：6 處（D4′ 表）＋ macOS 倉 2 處 render 呼叫（`VwrSettingsPaneBehavior.swift:31`、`VwrSettingsPaneCocoaBehavior.swift:68`）。
- 測試：**30 處賦值**（`InputHandlerTests_Cases4.swift` 20／`SessionTests_Cases2.swift` 7／`SessionTests_Cases5.swift` 3）。甲案下若 extended method 連 setter 一併提供則零改動；**乙案下則完全不受影響**。

**D15′｜i18n**：甲案 20 條新文案（另舊鍵 8 條待處置）；乙案 8 條新文案、舊鍵不動。

### 群五：測試與驗證

**D16′｜雙模式必須參數化。** 既有 MixedAlnum 相關測項共 **45 支**（`test_IH4*` 之唯一編號數），全綁在 Auto 語意上；Semi-Auto 需成對護欄。

**D17′｜「立刻 commit」之成本尚未量測（新增）。**
由 D2′ 可知：閂滯於英打時每一鍵 commit ⇒ 每一鍵 `switchState(.ofCommitting)` ⇒ 每一鍵 `inputHandler.clear()` ⇒ 每一鍵 `assembler.clear()` ＋ `currentLM.purgeInputTokenHashMap()` ＋ `currentTypingMethod` 復位。**此為每鍵之常數開銷，須量測**（連續快速鍵入英數時尤然）。此項在初稿中未見。

**D18′｜「立刻」如何驗證。** 既有測項以 `MockSession.recentCommissions`（`array`）觀測；即時 commit 會令其逐鍵增長——`joined() == "…"` 式斷言仍成立，惟「立刻」須改為逐鍵斷言（每敲一鍵即檢查尾項）。解除之提示則需觀測 `session.state.tooltip`（`test_IH435` 有先例）。

---

### 群六：解除面收斂之隱患（Wave 2 新增；H1–H9）

> 背景：解除點收斂為 **trigger key（Enter／BkSp／Delete／Esc）＋ `performServerActivation`**，Wave 1 之「`InputHandler.clear()` 亦解除」已撤回（原委見 D2′）。此舉解消了「每鍵 commit 即自我解除」之矛盾，但引入下列代價。

**H1｜`isASCIIMode` 之切換不再能解除閂滯。** **【重】**
詳見 D8′。要點：Wave 1 本人依據「`isASCIIMode` 之 setter 已呼 `resetInputHandler()` ⇒ `switchState` ⇒ `inputHandler.clear()`」保證過「Shift 切英數再切回、不可能仍黏著」；該保證以「閂滯隨 `clear()` 清」為前提，**前提既撤、保証即失效**。實際會發生：`isASCIIMode` 期間唯音仍 active（無 activation 事件）⇒ 閂滯保存 ⇒ 使用者切回中文後仍在英打閂滯，且無提示。
**出路**：(a) 接受並在偏好說明文中交代；(b) 將 `isASCIIMode` 之變更納入解除點（雖係「額外觸發時機」，但可論證為「`isASCIIMode` 優先級遠高於 Typewriters」之必然延伸）；(c) `isASCIIMode` 期間凍結、切回時清除。

**H2｜`resetInputHandler()` 之其餘呼叫者亦不再解除 ⇒ 「輸入結束即歸零」之不變式不再成立。**
`resetInputHandler()` 之呼叫點（實查）與其語意：
- `InputSession.swift:177`：輸入模式（繁簡）變更——不解除。
- `InputSession.swift:300`：`inputControllerWillClose()`——不解除（下次 activation 會補）。
- `InputSession.swift:325`：`commitComposition()`——客體主動要求遞交（換焦點、被 App 攔截之 Ctrl+Enter 等），語意上是「一次輸入會話結束」——不解除。
- `SessionProtocol.swift:110-116`：`isASCIIMode` setter——即 H1。
- `SessionProtocol.swift:193`：`performServerDeactivation()`——不解除，靠下次 activation 補。
- `InputSession_HandleEvent.swift:21`——待確認其語意。
⇒ 唯一保証只剩「**下一次 `performServerActivation`**」。凡不觸發 activation 之路徑，閂滯一律殘留。

**H3｜「清空緩衝」類按鍵不解除（Esc 入列後之殘餘）。**
Wave 2 已將 Esc 納入 trigger key，故「無逃生口」之隱患已解。惟仍有兩處不一致：`handleEsc()`（`:1194` 起）之兩分支與 `refreshState()`（`:1049`）之 Option+BkSp。其中 Esc 已因入列而覆蓋；**Option+BkSp（清空注拼槽／緩衝）仍不解除**——使用者可能預期「清空即重置」。建議至少在偏好說明文中明示「解除只認四個鍵」。

**H4｜會話內之唯一出口是四個 trigger key；不在列之鍵均無效。**
Space（閂滯於英打時應遞交半形空格，見 D4′）、Tab、方向鍵、Home/End、Shift、CpLk 均**不解除**。使用者的直覺出口（尤其是 Space 與 Tab）不成立。文案必須把「出口」講清楚，否則使用者會誤判為故障。

**H5｜工程陷阱：`MixedAlnumConfig` 不可整體 reset。** **【施工必記】**
§2.3 建議將 MixedAlnum 狀態收斂進 config 並以單一 reset 處理（全倉 14 處 `removeAll()`）。但如今**緩衝與閂滯旗標之生命週期不同**（緩衝每鍵清、閂滯僅 trigger key／activation 清），故 config **不可** `mixedAlnumConfig = .init()` 式整體重置——那會靜默殺掉閂滯態。
⇒ 須在 config 內提供兩個粒度（如 `resetContent()` 與 `resetAll()`），而 `clearComposerAndCalligrapher()` 只呼前者。**此點須寫進原始碼註解**，否則日後任何「統一 reset」之重構都會踩到，且症狀隱蔽（功能乎焉失效、無編譯錯誤）。

**H6｜解除與 tooltip 之間不得排延遲。**
若比照 `maybeShowModeDescriptionHintUponActivation` 之 0.05s `asyncOnMain`，會出現「已解除但提示未至」之可觀察縫。⇒ 解除與 tooltip 須在同一次 `switchState` 內完成（即 D3′ 之 `guarded: true` ＋ tooltip 一併送）。

**H7｜【利好、非隱患】跨客體殘留為極性雙緩衝所界。**
閂滯旗標只可能存在於 `sessionEven`／`sessionOdd` 兩個靜態單例之 handler 上，且每次 activation 必清，故**無洩漏出界之虞**。即使日後 Session 改為非單例模型，狀態亦隨物件回收——兩種模型下皆安全。

**H8｜`guarded: true` 之「空 `.ofInputting`」在本次之情境未實測。**
該路徑雖已在生產線（4.7.4 起之打字模式提示），但那是**遞交之後之瞬時狀態**；本次是**使用者按鍵之直接回應**，客體可能連續收到多次「空 marked range ＋ 狀態切換」（閂滯於英打時每鍵 commit 後再進 guarded 狀態）。務必在真機目視（TextEdit／Safari／Electron 各一），且**須先量測 D17′ 之每鍵成本**。

**H9｜四個 trigger key 之「放行 vs 攔截」方向相反，需逐鍵釘死。**
- **BkSp／Delete**：必須**攔截**（回 `true`）——放行會讓客體刪掉一個字元，與「不刪字」相悖。已定案。
- **Enter**：宜**放行**——閂滯時緩衝恆空、無物可遞交，若仍攔截則使用者**喫不到換行**（終端機不可用）。
- **Esc**：宜**放行**——Esc 係 vi／全螢幕 App 之客體級按鍵，攔截會讓使用者在 vi 裡失去 Esc（FR608-v1b §四·3 曾將「Esc 恆被消費」列為設計對價）。
⇒ 四個鍵、三種語意（兩個攔截、兩個放行），且要以同一套 tooltip 反饋統一呈現。**此為 Wave 2 新增之最高優先未決項。**

---

### 群七：Wave 3 之風險與新發現（R1–R9）

**R1｜`handleEvent(nil)` 會誤觸發解除。** **【具體、已取證】**
`InputSession_HandleEvent.swift:15-22`——逐事件入口 `handleEvent(_ event: KBEvent?)` 之開頭：
```swift
// 就這傳入的 KBEvent 都還有可能是 nil，Apple InputMethodKit 團隊到底在搞三小。
guard let event else {
  resetInputHandler(forceComposerCleanup: true)
  return false
}
```
IMK 確實會送 nil event（原始碼註解即為此而寫）。⇒ 使用者正在英打閂滯時，一個 nil event 就會**靜默解除**。
**建議**：該呼叫改用「靜默解除」變體（見 R4）——nil event 不是使用者意圖。

**R2｜解除不得實作在 `clear()` 內——兩者只差一層，極易搞錯。** **【施工必記】**
`resetInputHandler()`（`SessionCoreProtocol.swift:134`）之流程會經 `switchState(.ofCommitting)`，而該分支會 `inputHandler?.clear()`（同檔 `:102`）。因此：
- 若把解除寫進 `clear()` ⇒ 回到「每鍵 commit 即自我解除」之矛盾（D2′）。
- 若把解除寫成 `resetInputHandler()` 內的**獨立語句** ⇒ 正確。
兩者在編譯期無感、執行期天差地遠，**必須寫進實作註解**。

**R3｜`isASCIIMode` 之解除是「免費」的，且三條切換路徑皆經同一 setter（已全數查證）。**
`isASCIIMode` 之 setter（`SessionProtocol.swift:108-116`）先寫入儲存位、再呼 `resetInputHandler()`。全倉之賦值點實查唯三：`InputSession_HandleEvent.swift:46`（CpLk 檢查器之閉包，`self?.isASCIIMode.toggle()`）、同檔 `:218`（`toggleAlphanumericalMode`，Shift 輕敲／Eisu）、`SessionProtocol.swift:298`／`:301`（activate 時之強制復位）——**皆經同一 setter**。另 `isASCIIModeForThisClient`（`:93` 之宣告）之直接寫入點實查僅有 setter 內部一處（`:112`），無繞道者。
⇒ **Wave 3 第 1 點無需另行實作，由第 4 點涵蓋**。

**R4｜解除必須有「有提示」與「靜默」兩種風味。** **【新 API 需求】**
Wave 3 要求 BkSp／Delete／Esc 之解除有 tooltip 反饋（Wave 2 第 3 項）；但 `resetInputHandler()` 觸發之解除（繁簡切換、換客體、`commitComposition()`、`handleEvent(nil)`）**不該**彈「已解除閂滯」——那會是噪音，且此時未必有可用之 tooltip 錨點。
⇒ 需兩個入口（如 `releaseStickiness(announce: Bool)`）。

**R5｜測試隔離面（利好）。**
既有測項大量以 `resetInputHandler(forceComposerCleanup: true)` 作重置手段 ⇒ 閂滯態逐案被清掉，測試天然隔離。惟 Semi-Auto 之測項**不可**依賴跨 `resetInputHandler` 之狀態延續。

**R6｜`performServerActivation()` 之重設變成「保險」而非唯一防線。**
Wave 2 曾以 activation 為唯一保証；如今 `resetInputHandler()` 亦解除（且 `performServerDeactivation()` 會呼它），兩者職責重疊。**建議兩者都保留**——`performServerActivation()` 本身並不呼 `resetInputHandler`（見 D12′），仍屬必要之保險，須在註解中說明其冗餘關係。

**R7｜次序：建議「先解除、後 `switchState`」。**
`resetInputHandler(commitExisting: true)` 會把緩衝併入 commit；閂滯於英打時緩衝恆空，故無影響。惟若日後半閂滯態（緩衝非空）成真，次序就會影響產物。先解除可避開競態。

**R8｜【新發現、決定實作形狀】latched-English 之 state 是 `.ofEmpty`，三個攔截函式之前置護欄會把 trigger key 全部擋掉。** **【重】**
- `switchState(.ofCommitting)` 於 commit 後會 `inputHandler?.clear()`、接著 `if state.type != .ofEmpty { state = .ofEmpty() }`（`SessionCoreProtocol.swift:102-104`）。⇒ **每鍵即時 commit 之後，state 恆為 `.ofEmpty`。**
- 而三個攔截函式之入口皆有 `.ofInputting` 護欄：`handleBackSpace()`（`:925`）、`handleDelete()`（`:1085`）、`handleEsc()`（`:1202`）。
- ⇒ **閂滯於英打時按 BkSp／Delete／Esc，會直接 `return false`——既不解除也不攔截，功能看似全然失效。**
**兩條出路**：
- **(i) 把閂滯之解除分支置於該護欄之前**（或於護欄處加「閂滯態則轉交解除」之例外）。改動小，風險限在三個入口。
- **(ii) 閂滯於英打時，每次 commit 後改進一個 `guarded: true` 之空 `.ofInputting` 狀態**（即 tooltip 之同一載體）。則三個護欄自然通過。代價：每鍵一次「空 marked range ＋ 狀態切換」（H8 之風險面擴大），且須先量成本。
**建議 (i)**——它不把每鍵成本再推高。此事須於 DoD 中先行釘死，否則實作者極可能寫出一個「能進入閂滯但無法退出」的半成品。

**R9｜攔截先例已存在（利好）。**
事主推測之「Esc Clean Composition Buffer」確實存在：`handleEsc()` 內之 `prefs.escToCleanInputBuffer`（`InputHandler_HandleStates.swift:1206`／`:1217`），且該函式於 `.ofInputting` 狀態下一律回 `true`（攔截）。⇒ Esc 之攔截有現成慣例可循；惟如 R8 所述，閂滯態不走 `.ofInputting`，仍須前置分支。

---

## 五、DoD：已定案與未決清單（Wave 6 後）

### 5.1 已定案（可作為施工依據）

**新手術總前提（Wave 6 界定）**
> **本次手術之所有新行為，一律以「閂滯開關 ON」**（`kEnableLatchedAlnumStateInMixedAlnumMode == true`）**且「MixedAlnum 開關 ON」**（`kMixedAlphanumericalEnabled == true`）**為前提。**
> 兩開關未同時成立時，程式行為**必須與本 phase 之前完全一致**——此為本 phase 之**首要不變式**，且須以測項鎖住（見 D16′：新測項應以 `@Test(arguments:)` 同時跑「雙開」「僅母開」「僅子開」「雙關」四態）。

**偏好與治理**
- 方案：**乙案**——不撤 `kMixedAlphanumericalEnabled`，追加 **`kEnableLatchedAlnumStateInMixedAlnumMode`**（`rawValue: "EnableLatchedAlnumStateInMixedAlnumMode"`，`.bool(false)`）。（§2.2／§2.5）
- 顯示位置：行為設定頁、緊鄰母開關。母關子開之非法態以 UI 依附（SwiftUI 有 `.disabled(...)` 先例；Cocoa 側須新寫）＋ 程式合取吸收。
- 命名與四語系文案：見 §2.5（含 11 項要點之完整 description 草案）。**不再使用 `Semi-Auto Switch` 一詞。**

**狀態語意**
- **閂滯態為二值**：只有英文可被閂滯，不存在「閂滯於中打」。（Wave 4 第 3 項）
- **未閂滯時之行為與 Auto 完全相同**——Semi-Auto ≡ Auto ＋ 「判定落定後予以固定」。故此二者可共用同一條判定管線，差異僅在落定後是否固定。
- 進入條件：**僅取既有判定**（Wave 4 第 2 項）。原提之「結合判定因素」（recent-committed single ASCII char history）已於 Wave 5 **擱置**、不納入本階段。

**承載**
- 閂滯態放 `InputHandler`；建議收斂進 `MixedAlnumConfig`（比照 `Homa.Assembler.config`）。
- **`MixedAlnumConfig` 須提供兩個復位粒度**（內容 vs 全部）；`clearComposerAndCalligrapher()` 只呼前者。（H5）

**解除面**
- 觸發點：① trigger key ② `Option+BkSp` ③ `isASCIIMode` toggle ④ `resetInputHandler()` ⑤ `handleEvent(nil)`；另加 `performServerActivation()` 為保險。
- **攔截語意**：BkSp／Delete／Esc **攔截**（回 `true`）；Enter **解除後放行**；Option+BkSp **解除、不攔截**。
- **提示區分**：① ② 帶提示（▲）；③ ④ ⑤ 一律**靜默**（△）（Wave 4 第 4 項）。
- **R8 採 (i)**：trigger key 之分支**置於三處 `.ofInputting` 護欄之前**。（Wave 4 第 1 項）
- **R2**：解除不得寫入 `clear()`，須為 `resetInputHandler()` 內之獨立語句。
- **R3**：`isASCIIMode` 之解除無需另行實作（由 `resetInputHandler()` 涵蓋，且三條切換路徑皆經同一 setter）。
- **R6**：`performServerActivation()` 仍須獨立實作（它不呼 `resetInputHandler`）。

**按鍵語意（閂滯於英打）**
- 每一顆可列印 ASCII → 即刻遞交。
- **Space → 即刻遞交半形空格**（Wave 4 第 6 項）。
- **標點鍵 → 遞交「該鍵在當前英數佈局下、連同修飾鍵所對應之 ASCII 字元」**，規則置於**中文標點查詢之前**；ASCII 之解析**復用既有 `resolveVisibleInputText(_:)`**（Wave 6 定案；細節與陷阱之迴避見 §四·D10′）。
- **Tab／方向鍵 → 見〈新規定〉**。

**新規定（Wave 4 提出、Wave 5 更正用詞、Wave 6 界定適用範圍）**

**界定後之定義**：

> **適用前提**：閂滯開關 ON **且** MixedAlnum 開關 ON，**且當前正閂滯於英打**。（參〈新手術總前提〉）
> **規則內容**：只要 **`assembler` 為空** 且 **`mixedAlphanumericalBuffer` 為空**，Tab 與方向鍵即**直接放行給輸入客體**（不攔截、不消費）。
> **適用範圍**：**僅限閂滯態**。不適用於未閂滯時之任何狀態（含一般中文打字、未啟用閂滯之混打、母開關關閉者）。
> ⇒ **本規定不是通用規則**；不要求改動非閂滯路徑之行為。

**因此之實際效力（無需改動現行碼）**：閂滯態之 state 為 `.ofEmpty`（R8），而 `revolveCandidate()`（Tab）與 `handleForward()`／`handleBackward()`／`handleClockKey()`（方向鍵）皆以 `state.type == .ofInputting` 為第一道護欄 ⇒ **閂滯態下兩者本即洩漏**，新規定**已由現行程式碼滿足**。其效力有二：
1. **實作時不得採 R8 (ii)**——若每次 commit 後改進 `guarded: true` 之空 `.ofInputting`，Tab 與方向鍵**會被吞掉**，直接違反本規定。⇒ **R8 之裁定與本規定相互鎖住。**（此即 Wave 4 已裁定 (i) 之理由。）
2. **須以測項鎖住此行為**——否則日後若有人改動 state 形狀（例如為別的目的引入空 `.ofInputting`），本規定會**靜默失守**。

**備註（與現行之差異，供參考、不要求改動）**：非閂滯態下，Tab 之護欄（`isComposerOrCalligrapherEmpty`）**額外要求注拼槽為空**，比本規定嚴；此差異僅在非閂滯態可觀察，且**不在本次手術之範圍內**。

**Tooltip**
- ▲ 類解除以 `guarded: true` 之可為空輸入狀態 ＋ tooltip 反饋（`revolveTypingMethod` 之方法）；△ 類不彈。
- 閂滯態之持續性指示暫不實作（備忘）。
- 解除與 tooltip 須在同一次 `switchState` 內完成，不排延遲。（H6）

### 5.2 未決（待事主裁定）

**（全數結案。）**

- D10′（標點優先序）：**Wave 6 定案**，見 §四·D10′。
- 「新規定」之適用範圍：**Wave 6 界定為閂滯態專屬**，見 §5.1。
- 進入條件之「結合判定因素」：**Wave 5 擱置**，不納入本階段（進入條件＝既有判定）。

【施工前之未閉合項】改列於 §5.3（待實測／待量測）與 §5.4（手術後人工測試清單）——二者皆**非裁定事項**。

### 5.3 待實測／待量測（非裁定事項，但動工前須閉合）

- **H8**：`guarded: true` 之「空 `.ofInputting`」在「使用者按鍵之直接回應」情境下對客體之影響（既有用例為遞交後之瞬時狀態）。**已併入 §5.4 第 1 項**（事主指定列入人工測試）。
- **D17′**：閂滯於英打時每鍵 commit ⇒ 每鍵 `clear()` ⇒ 每鍵 `assembler.clear()` ＋ `purgeInputTokenHashMap()` ＋ `currentTypingMethod` 復位。**須量測**（連續快速鍵入英數時尤然）。

### 5.4 手術後人工測試清單（非裁定事項；動工後須逐項目視）

> 本清單收錄**無法由單元測試充分覆蓋**之項目。其中第 1 項由事主於 Wave 6 指定列入。

1. **`guarded: true` 之空輸入狀態對客體之影響**（＝ H8；事主指定）。
   閂滯態下每鍵 commit 之後，若以 `guarded: true` 之空 `.ofInputting` 承載解除提示，客體會接連收到「空 marked range ＋ 狀態切換」。既有用例（打字模式提示）為**遞交後之瞬時狀態**，本次則是**使用者按鍵之直接回應**，兩者對客體之影響未必相同。
   **須於 ≥3 類客體各目視一次**：TextEdit（原生）、Safari（WebKit）、VS Code（Electron）。
2. **閂滯態下之實際輸出**：`, . / ; -` 與 `[ ] \ =` 諸鍵、及其 Shift 變體與 Option 變體（含「Option+字母之非 ASCII 字符應落回基底 ASCII」一路）。
3. **每鍵 commit 之視覺流暢度**：連續快速鍵入英數時有無閃爍、游標跳動、或組字區殘影（D17′ 所量測之成本在視覺上之表現）。
4. **四個解除鍵之實際手感**：
   - Enter——解除後是否正常換行（終端機／編輯器情境）。
   - BkSp／Delete——解除後客體是否照常刪字（應刪，因攔截只作用於「閂滯中」該一次）。
   - Esc——**於 vi／全螢幕 App** 確認未因此失去 Esc。
5. **解除時 tooltip 之位置與時長**（`guarded: true` 空輸入狀態之錨點）。
6. **Tab／方向鍵**於閂滯態下是否確實洩漏給客體（新規定之實機複驗）。
7. **動態排列**（酷音大千26鍵等）下進入閂滯之行為——該類排列之判定已由 P234 改動，須一併目視。
8. **Electron 系客體**之整體表現（本倉對其 NSTextInputClient 實作早有記載之疑慮）。

## 六、建議之推進順序

**第一階段：偏好與承載（零行為變更）**
建立 `kEnableLatchedAlnumStateInMixedAlnumMode`（純追加，預設 `false`）＋ 設定介面（含 Cocoa 側之依附式呈現——本次須新寫）；同時依 §2.3 建立 `MixedAlnumConfig` 並把 `mixedAlphanumericalBuffer` 收斂進去（薄存取器維持呼叫端不變）；閂滯欄位先建立但**恆不生效**。
**H5 須在本階段落實**：config 之兩個復位粒度預先切開並加註。
此階段可完整驗證：偏好讀寫、45 支既有測項全綠、設定介面。**風險最低、可獨立交付。**

**第二階段：會話邊界與解除面**
實作 `performServerActivation()` 之重設（D12′，緊鄰 `state = .ofEmpty()`）；`resetInputHandler()` 之解除（含 R2 之施工限制與 R4 之兩種風味）；依 R3 確認 `isASCIIMode` 走同一 setter；依 R8 之裁定決定 trigger key 之分支位置。此時仍需**恆不進入閂滯**，故可先以測項把「解除時機」全部釘死。

**第三階段：接「閂滯於英打 → 立刻 commit」**
依 D5′ 之裁定接上進入條件；以 D16′／D18′ 之方式補護欄；**並先量測 D17′ 之每鍵成本與 H8 之客體相容性**（真機目視 TextEdit／Safari／Electron 各一），通過再往下。

**第四階段：解除提示**
以 `guarded: true` 之輸入狀態 ＋ tooltip 實作「已解除閂滯」之提示（D3′／H6）。
**持續性指示**（D3′）**不在本階段**——已依事主指示記入備忘，待日後有 FeatureRequest 再議。

---

## 七、備忘（暫緩項）

- **閂滯態之持續性可視化指示**：需求暫緩（事主指示）。技術上可行之路徑已查明——`guarded: true` 之可為空輸入狀態 ＋ `tooltipDuration = 0`（`revolveTypingMethod` 之既有作法），或 `ui?.statusUI` 獨立通道（`maybeShowModeDescriptionHintUponActivation` 之既有作法）。屆時無需重新調研，直接取用即可。

---

## 八、本文之證據邊界

- **未實作、未跑任何行為探針**。所有難點判斷皆由靜態閱讀現況碼得出；所引行號以本文寫作時之 HEAD 為準。
- **`UserDefaults` 跨型別讀取行為已離線實測**（§2.1），涵蓋 `Bool`／`Int` 與「鍵不存在」三種情形，未涵蓋 `Double`／`String`。
- **`performServerActivation()` 之範圍與內容係以括號配對解析後全文掃描得出**（`:208-314`），非逐行目視。
- **每鍵 `clear()` 之成本未量測**（D17′）。
- **微軟新注音之對照僅引用既有反組譯研究**，本次未再反組譯、未實機比對。
- **未評估之面向**：Electron 系客體之實機行為、`@AppProperty` 與 SwiftUI `DynamicProperty` 之互動（甲案下 extended method 之變更通知）、閂滯態與關聯詞／POM 之交互。
