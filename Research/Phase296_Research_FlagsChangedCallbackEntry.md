# Phase 296 研究：`flagsChanged` 之回呼進入點診斷

> 狀態：研究稿（2026-10-10）。本 phase 只擴日誌、不修病；分岔之定案仍待樓主下次失靈之日誌。
> 前置：`Research/Phase291_Research_FlagsChangedDeliveryFailure.md`（P291 之原始分岔與儀器）。

## 0. 樓主 2026-10-10 之新證據（客訴 #618）

- 09:30–09:45 計數：`OmitNSEvent` 253、`[Event] guard fail` **0**、`Current State:` 376、`activateServer(` 75、`deactivateServer` **0**。
- 09:37:24.353–09:39:18.693 唯音日誌全靜默 114 秒；同期旁聽程式（09:38:26–09:38:34）記到約 10 次右 Shift。
- 09:39:18–09:39:21 有 `Omit keyDown`：k126 ×1、k51 ×21。
- 09:39:22–09:39:39 約 25 次右 Shift（按下／放開皆有，旁聽記錄）而唯音**零** `flagsChanged`。
- 09:39:41.349 第一次 Caps Lock 只留 iTerm2 之 `Committing()`／`Empty`（**無** `flagsChanged k57`、**無** `CapsLock key tap detected`）；09:39:44.726 第二次才 Chrome 之 `Committing()`／`Empty` → `activateServer(com.googlecode.iterm2)` → `Omit flagsChanged f0 k57` ＋ `CapsLock key tap detected`；09:39:46.411 起右 Shift 恢復。
- 第 6 項受控實驗（nightly 4.8.7 build 4870、Cmd+Tab、iTerm2↔Chrome；A 組切走 2 秒內切回、B 組停留 >15 秒）：**兩組皆未重現**，每次切回後第一下右 Shift 皆有切換通知。

## 1. 由此確立之事實

- **`deactivateServer 0` 非證據**：4.8.6 全倉僅 `Packages/vChewing_OSNeutral_LibVanguard/Sources/LibVanguard/Session/SessionProtocol.swift:247` 之 `vCLog("activateServer(\(senderBundleID))")`，並無 deactivate 日誌。P291 於 ObjC 側加者為 `ActivateServer:`／`DeactivateServer:`（不同拼法），統計時勿混用。
- **「有抵達可解析 session 之 flagsChanged 必留痕」在 4.8.6 亦成立**：`Packages/vChewing_MainAssembly4Darwin/Sources/MainAssembly4Darwin/SessionController/SessionControllerSputnik.swift:150-164`（4.8.6）之 nil 分支靜默；`Packages/vChewing_OSNeutral_LibVanguard/Sources/LibVanguard/Session/InputSession_HandleEvent.swift:33-58` 之 shift／caps 命中各自印字，未命中則落到 `handleKeyDown` 之 `if event.isFlagChanged { return false }` ⇒ 必印 `OmitNSEvent`。
- 唯音自身（HEAD 與 4.8.6）**無任何 CGEventTap／`addGlobalMonitor`** ⇒ 唯音不可能自行吞掉 flagsChanged。
- 4.8.6 已有 parity 雙緩衝池（`InputSession.swift` 之 `sessionEven`／`sessionOdd`）。
- **版本字串無法區分**：build 4870 同時見於 tag `4.8.7`（`ec4e64aa`，2026-10-07）與 HEAD（`Release-Version.plist`／`Update-Info.plist`／`vChewing.xcodeproj/project.pbxproj`／`ValueAdd/WebConfigAssistant/version.txt`）⇒ 夜版是否含 P291 只能由發版時間推斷（P291 兩筆 commit 為 2026-10-09 14:22 +0800）。

## 2. 判定樹（P296 版）

| 分岔 | 內容 | P296 日誌之判別 |
|:--|:--|:--|
| A | 事件根本未進唯音行程 | 該時段**無** `EventEntry:`，但同期其他事件型別仍有 |
| A′ | 已進 App 事件流之前、被別支 event tap 刪除（旁聽在鏈前段故仍看得到） | 同 A |
| B | 已進行程，但 controller 位址已自 tracker 除名 | `alive=false` 或 `session=nil` |
| C | 已進行程，卻被路由到另一枚仍存活之 controller | `slot(assigned:)` ≠ `addr=`，或 `client=` 非前景客體 |

- **已退休**：「離開多久／3 秒剪線致 delayed dealloc」——A／B 受控實驗兩組皆未重現，且失靈時 keyDown 仍正常。
- **最尖線索**：同一 ~20 秒內 keyDown 進得來、flagsChanged 進不來 ⇒ 分岔 B 單獨不足（位址已死會連 keyDown 一起死）⇒ 指向 C 或 A／A′。

## 3. 本 phase 之儀器

- `SessionControllerSputnik.logEventEntry(event:controllerAddr:session:)`，於 `configureHandlingGivenNullableEvent` 之 block 進入時（解析 session 之後、nil 分支之前）呼叫；除錯模式閘門在函式內。
- 格式：`EventEntry: addr=<controller 位址> alive=<bool> gen=<generation> tracked=<count> session=slot(assigned=<位址> client=<bundle id> ascii=<bool>) event=<KBEvent 描述|[NOEVENT]|[RAW]…>`
- 保留 P291 之 `UnresolvableController:`（查無 session）與 `OmitNSEvent:`（放行）兩行，維持日誌連續性與可比性。

## 4. 判讀步驟（樓主下次失靈時）

1. 於失靈時段濾 `vChewingDebug:` 之 `EventEntry:`，找 `event=KBEvent(type: flagsChanged…)`：
   - **完全沒有** ⇒ A／A′（唯音未收到）⇒ 續查 event tap 鏈（AltTab／BetterDisplay／Mac Mouse Fix／Wacom）與 SecureEventInput。
   - **有** ⇒ 依位址與 session 欄位分岔 B／C。
2. 比對同期 keyDown 之 `EventEntry:` 之 `addr`：若 flagsChanged 之 `addr` 與 keyDown 者不同 ⇒ C 成立（TSM／IMK 之 per-event-type 路由）。
3. 若 `alive=false` ⇒ 查 tracker 除名與 `_controllers` prune／3 秒剪線之交互。

## 5. 界線

- 本 phase 只加日誌、零行為改動；未在任何失靈現場實測。
- nightly 暫不重切：先用含 P291 之現行夜版分辨 A／B；分岔 C 須待本 phase 之碼進入夜版後方能判別。
- 樓主第 9 項（開啟「對所有客體共用中英文切換狀態」）之觀察仍在進行，其結果與本 phase 之分岔無直接關係。
