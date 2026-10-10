# Phase 291 研究：切換 App 後 `flagsChanged` 投遞失效（客訴 #618）

> 狀態：研究稿（2026-10-09）。用途＝把「切換 App 後輸入法收不到 `flagsChanged`、右 Shift 單擊失效、按 Caps Lock 才恢復」
> 收斂成可證偽的分岔，交代已排除者與其證據，並記錄本 phase 加入之 instrumentation（唯讀診斷、不改行為語意）。
> 定性＝**本 phase 不以解決該客訴為目的**：它只把診斷日誌之覆蓋範圍擴及足以定案之程度，助樓主抓取更詳細之資訊、
> 以便指出真正的誘因。因樓主之排程未能配合，本 phase 於此階段性收束，後續另有開發任務優先。
> 工單：<https://github.com/vChewing/vChewing-macOS/issues/618>（回報者非事主，以下稱「工單樓主」）。
> 相關 phase 記錄見 `vChewing-DevLogs/Reqs4LLM/Archive_P201-P300/Reqs_0291-0300.md` 之 Phase 291。
> 前置文獻：`Research/Phase112_ExtraResearch.md`、`Research/Phase112_PostResearch_ClientAddressReuse.md`。

## 0. 客訴事實（僅登錄、不自證）

- 環境：唯音 4.8.6（Build 4860）；macOS 27.0.1 (26A434)；Apple M5；主要客體 iTerm2 3.7.3（內跑 tmux），失靈前常在
  Chrome 154、Discord、Finder 之間切換；另裝 AltTab 11.7.1／BetterDisplay／Mac Mouse Fix／Wacom 驅動（皆自帶 event tap）。
- 設定：`TogglingAlphanumericalModeWithRShift = 1`、`LShift = 0`、`ShiftEisuToggleOffTogetherWithCapsLock = 1`、
  `ShareAlphanumericalModeStatusAcrossClients = 0`、除錯模式開啟。
- 症狀：右 Shift 單擊偶發不切換英數模式；同段時間注音輸入、退格、方向鍵皆正常。按一下 Caps Lock 即恢復。
  當天單獨按右 Shift 約 381 次，只有少數失敗。
- 2026-10-09 時間軸：09:34 於 Chrome 右 Shift 正常（日誌有 `Shift key tap detected`）→ 09:35:07～09:35:12 前景於
  Chrome／通知中心／Finder 輪替 → 09:37:00 切至 iTerm2（日誌有 `activateServer(com.googlecode.iterm2)`）→
  09:38～09:39 於 iTerm2 按右 Shift 約 25 次，**唯音日誌一筆 `flagsChanged` 都沒有**（同時段 keyDown 有記錄）→
  09:39:41／09:39:44 各按一次 Caps Lock，第二次出現：

  ```
  09:39:44.881 Current State: Committing(), client: com.google.Chrome
  09:39:44.881 Current State: Empty, client: com.google.Chrome
  09:39:44.882 activateServer(com.googlecode.iterm2)
  09:39:44.899 OmitNSEvent: KBEvent(type: flagsChanged, ... keyCode: 57)
  09:39:44.899 CapsLock key tap detected, toggling Alphanumerical Mode if should.
  09:39:46.410 OmitNSEvent: KBEvent(type: flagsChanged, modifierFlags: 131072, ... keyCode: 60)
  09:39:46.570 Shift key tap detected, toggling Alphanumerical Mode if should.
  ```

- 樓主自寫 listenOnly CGEventTap（HID ＋ Session 各一）於失靈當下旁聽：系統兩層每一下右 Shift 都有
  （`key=60 flags=131332` 與 `flags=256` 成對出現），且無卡住的修飾鍵；`SecurityAgentHelper` 一直回報 0 個 SecureEventInput。
- 10/8 前例：在 iTerm2 用右 Shift 切成英文後，經 AltTab 切到 Chrome、Discord，再回 iTerm2 就一直停在英文、右 Shift 無反應。

## 1. 已排除者（附證據）

1. **唯音自身的 `flagsChanged` 判定／Shift 判定／英數切換邏輯**。`InputSession_HandleEvent.handleEvent` 對 `.flagsChanged` 轉呼
   `handleKeyDown`，而 `handleKeyDown` 在 `InputSession_HandleEvent.swift:132` 對所有 `isFlagChanged` 一律 `return false`
   （Phase 147 之決策：放行）。`configureHandlingGivenNullableEvent` 於 `!result && PrefMgr.shared.isDebugModeEnabled` 時
   **必印 `OmitNSEvent: …`**。即：任何抵達「位址仍在 tracker 登錄表內之 controller」的 `flagsChanged` 必留日誌，
   故「一筆都沒有」不可能由此產生。
2. **不是 Phase 147 之前「`return true` 吞掉修飾鍵」之病灶復發**（現行碼已改回放行）。
3. **不是 `unregisterSessionAddr` 造成之 split-brain**。`InputSession.session(forControllerAddr:)`（`InputSession.swift:196`）
   全倉**無生產呼叫點**；class-level blocks 一律走 `SessionControllerSputnik.session(forAddr:)`
   → `IMKControllerLifetimeTracker.shared().isAddressAlive(_:)` ＋ `generation(forAddress:) & 1` 之 parity 解析。
   故 `-IMKSwift_delayedDealloc` 內那次 `_IMKSwift_onDealloc`（→ `unregisterSessionAddr`）幾乎無害。
4. **不是 3 秒延遲釋放計時器單獨造成**。兩次實例之前景切換間隔皆遠超 3 秒；計時器唯一保護是「同客體在 3 秒內回來時
   `-activateServer:` 之 `IMKSwift_cancelDelayedDealloc`」。且若真凶是「3 秒後剪斷 client XPC」，症狀應為
   「事件收得到、文字送不出」，與「連事件都沒有」不符。
5. **不是「4.8.7 已修、只是樓主沒升」**。4.8.6 GM（`b0ff7864`，2026-09-30）至 HEAD（`d6826630`，2026-10-07）之 commit
   全為 MixedAlnum／`FirstTone` 更名／WebAssistant／CMD-chord 讓位等，**無任何 IMK 事件路由或 session 生命週期修正**；
   客訴日 2026-10-09 亦在 4.8.7 之後 ⇒ 4.8.6 與現行 HEAD 都含全部 2026-07 之 session 機制。

## 2. 存活的兩個分岔

「唯音一筆 `flagsChanged` 都沒有」只剩兩種可能：

- **(A) 事件根本未投遞到唯音的 controller**——OS 或客體之輸入上下文未把 `NSEvent` 交給本 IME。
- **(B) 事件投遞到了，但該 controller 之位址已不在 `IMKControllerLifetimeTracker` 登錄表**——
  `SessionControllerSputnik.session(forAddr:)` 回 nil，`configureHandlingGivenNullableEvent` 之
  `guard … else { return false }` **靜默放行、不留任何日誌**；同一分支亦使 `configureProvidingRecognizedEvents` 回 `0`
  （⇒ HIToolbox 自此不再為該 controller 投遞任何鍵事件）。

### H1：唯音自身 2026-07 之三連改（2026-07-22／07-24／07-28）

1. `-IMKSwift_delayedDealloc`（`Packages/vChewing_IMKUtils/Sources/IMKSwiftModernHeaders/IMKSwift.m:352-383`）：
   `-deactivateServer:` 後固定 3.0 秒無條件呼叫 `terminateForClientXPCConn:`／`terminateForClientDOProxy:`／
   `terminateForClient:` 剪斷客體連線。若該 controller 之後被 IMK 重新啟用，即成「客體連線已死」之殼——
   而 `-activateServer:`（同檔 `:232-239`）只做 `IMKSwift_cancelDelayedDealloc` ＋ 回呼，**不呼叫 `super`、不使用 `sender`、
   亦不更新 `[self client]`**。
2. `+IMKSwift_pruneStaleControllersOnServer:excludingSelf:`（同檔 `:163-197`）：**每次 controller 初始化**都自
   `IMKServer._private._controllers` 剔除一個「generation 最小」且非 `_currentController`、非自身者。原 `count` 門檻
   （`count <= 2`，Phase 113）已於 `8a734b4d`（2026-07-28）移除 ⇒ 現行碼無條件執行，且該處以 `_currentController`
   為啟發式；客訴日誌那三行（Chrome 之 session 先 `Committing()` → `Empty`，1 ms 後才 `activateServer(iterm2)`）正顯示
   **唯音內部的 current 是另一個客體**。
3. 兩者共同之上游事實（`Research/Phase112_ExtraResearch.md` 逆向）：`_controllers` 以 **client proxy 記憶體位址**為鍵，
   而切換客體時 HIToolbox 每次都產生**全新 DO/XPC proxy**；`_mapClientToController:` 永遠命不中舊 controller，
   而 `-sessionFinished:`（`_controllers` 唯一的正常移除點）永不為舊 proxy 觸發 ⇒ 舊 controller 永久孤兒。

### H2：macOS 27.0.1 側未重綁前景客體

唯音內部仍停在 Chrome（見 §0 之 `Current State: …, client: com.google.Chrome`），而前景實為 iTerm2。
`Research/Phase112_PostResearch_ClientAddressReuse.md` 已記錄同向之未驗證推測：「macOS 27.0 之 `_IMKServerLegacy` ＋
`IMKSignPostInputController`／`IMKLoggingInputController`／`IMKTracingInputController` 包裝層改變了事件時序，
`-activateServer:` 被呼叫時 `client()` 尚未就緒」。按 Caps Lock 之所以恢復，正因它觸發一次完整之 deactivate→activate 週期，
把前景客體重新綁上。

### H3：環境放大因子

AltTab／BetterDisplay／Mac Mouse Fix／Wacom 皆有自帶 event tap；10/8 之實例正是經 AltTab 切換。此非病根，但可能是
(A) 分岔之觸發條件（前景切換時之輸入上下文交接被打斷）。

## 3. 本 Phase 加入之 instrumentation（唯讀）

(A)／(B) 在日誌上原本同樣安靜——**(B) 完全無輸出**，這正是難以定案之唯一原因。故補上下列日誌（皆以 `vChewingDebug:`
為前綴、經 `vCLog` 輸出；macOS 26+ 走 `Logger(subsystem: "vChewing", category: "Log")`）：

| 落點 | 日誌內容 |
| --- | --- |
| `IMKSwift.m` `-initWithServer:delegate:client:` | `ControllerInit: addr=… gen=…` |
| 同上所呼叫之 prune | `Prune: controllers=… current=… self=…`；其後 `Prune: evicted addr=… gen=… remaining=…` 或 `Prune: nothing evictable (controllers=…)` |
| `-activateServer:` | `ActivateServer: addr=… gen=… clientTerminatedBefore=YES/NO` |
| `-deactivateServer:` | `DeactivateServer: addr=… gen=…` |
| `-IMKSwift_delayedDealloc` | `DelayedDealloc: addr=… gen=…`，並於該 controller 掛 `clientTerminatedBefore` 旗標（關聯物件） |
| `SessionControllerSputnik` 之 `session(forAddr:) == nil` 四處（activate／deactivate／recognizedEvents／handleEvent） | `UnresolvableController: callSite=… addr=… alive=… gen=… tracked=…` |
| `configureProvidingRecognizedEvents` | `RecognizedEvents: addr=… mask=…` |

實作紀律：新增第 14 個 class-level static block 作日誌通道，訊息以 **UTF-8 C 字串**傳遞（維持該檔「ObjC↔Swift 邊界不傳物件」
之既有約定）；除錯模式閘門由 Swift 端 `vCLog` 統一承擔，故 ObjC 側可無條件呼叫。**不動任何行為語意**；
`clientTerminatedBefore` 僅為關聯物件旗標、不影響控制流。

## 4. 判定樹（取得樓主之日誌後即定案）

1. 失靈期間若出現 `UnresolvableController:` ⇒ **(B)**。接著看同一 addr 是否曾出現 `Prune: evicted addr=…`：
   - 是 ⇒ **H1-2**（prune 誤殺）。此即最短路徑，不需再等後續日誌。
   - 否 ⇒ 該 controller 之 `-dealloc` 已跑（tracker 除名）；追其 `DelayedDealloc` 與最後一次 `DeactivateServer` 之時差。
2. 若**完全沒有** `UnresolvableController:`、keyDown 有 `OmitNSEvent:`／`[Event] guard fail` 而 `flagsChanged` 沒有 ⇒ **(A)**。
   此時看 `RecognizedEvents: addr=… mask=…` 是否為 0，並看該 addr 是否出現 `ActivateServer: … clientTerminatedBefore=YES`
   （⇒ 該 controller 曾在 3 秒後被剪線、而後又被啟用）。
3. 若連 keyDown 都完全沒有 ⇒ 唯音在此客體上從未收到任何事件 ⇒ 更上游之輸入上下文問題（H2／H3）。
4. `Prune: evicted …` 中被剔除者若正是失靈客體之 controller ⇒ 直接坐實 H1-2。

## 5. 待實作之處置（依分岔；本 phase 不動手）

- **H1-1 成立** ⇒ 把 `terminateForClient*` 自 3 秒計時器**搬進 prune**（以「IMK 已放手——即已自 `_controllers` 移除」為事實點），
  或直接廢除計時器、改以 `_controllers` 之狀態為唯一依據。
- **H1-2 成立** ⇒ 恢復 `count` 門檻 ＋ 加護欄（`_currentController` 為 nil 或已不在 `_controllers` 時不剔除）。
- **H2 成立** ⇒ 唯音側只能加防禦：`handleEvent` 收到事件時比對 `[self client]` 之 bundleID 與 `clientBundleIdentifier`，
  不符即以該 controller 重跑激活；上游另案。
- **H3** ⇒ 請樓主以「暫停其他 event tap」作對照組（非唯音可修）。

## 6. 界線

- 本 phase 只加日誌與一處關聯物件旗標，**不修病**；`_controllers` 之掃描式「是否仍登記」檢查刻意不做
  （避免 dealloc 路徑之 KVC 風險，且由 prune 日誌＋nil 分支日誌即可推得同一結論）。
- 3 秒延遲釋放與 prune 之行為語意完全不變。
- 未動：`SessionControllerSputnik` 之 parity 解析、`InputSession` 之極性雙緩衝池、`performServerActivation` 之快速路徑、
  `InputSession_HandleEvent` 之任何判定。
- 樓主之受控實驗（切走 <2 秒 vs >15 秒各 20 次往返）仍可切開 H1-1；該實驗之設計已見工單回覆稿。
- **本 phase 就此階段性收束**：樓主之排程無法配合該實驗，且後續另有開發任務優先；§4 之判定樹與 §5 之處置留待日後
  取得樓主日誌時再用。
