# Phase 298 研究：換裝時執行中輸入法實例之終止

> 狀態：研究稿（2026-10-11）。本 phase 為安裝器硬化；真實驗證待下一次夜版換裝。
> 前置：`Research/Phase291_Research_FlagsChangedDeliveryFailure.md`、本卷 P296 之雙臂探針實驗。

## 0. 起因：換裝殘影

2026-10-11 02:41 之雙臂探針實驗中，磁碟上之 `~/Library/Input Methods/vChewing.app` 已由 legacy 夜版換回 modern 建置（sha256 前 12 碼 `45878cef1aad`），而**舊 legacy 行程仍在服務前景客體**：

| 行程 | 時段 | `EventEntry:` |
|:--|:--|:--|
| PID 65261（legacy） | 02:41:03.335–02:41:31.099 | 11 |
| （真空） | 02:41:31.099–02:41:50.998（約 19 秒） | — |
| PID 65504（modern） | 02:41:50.998 起 | 0 |

- 判讀：安裝器未使舊行程立刻退場 ⇒「換裝後之第一段日誌未必出自新碼」；該次擷取即因此混入舊碼，一度被誤讀為「modern 建置冒出 P296 之 `EventEntry`」。
- 附帶事實（同窗）：兩行程之 tap 合計 10 次，正好對上「右 Shift 單擊 ×5 ×2」；堆疊內 `_IMKServerLegacy` 幀數與裝置疑影無關。

## 1. 動工前之終止手續

| 落點 | 內容 | 問題 |
|:--|:--|:--|
| `InstallerVMProtocol.swift:50-62` | `Process` 跑 `/usr/bin/killall vChewing`、`killall vChewingPhraseEditor`；`launch()`＋`waitUntilExit()` | 不讀 `terminationStatus`；送出即忘、無驗證 |
| `InstallerVMProtocol.swift:269-275` | `killall TextInputMenuAgent` | 同上 |
| `ValueAdd/PKGInstallerAssets/pkgPreInstall.sh:11-12` | `killall "${TARGET}" 2>/dev/null \|\| true` | 另一條安裝路徑（PKG）；本次未動 |

- `killall` 只認程序名；呼叫端從未檢查「到底有沒有殺到、殺乾淨沒有」。
- `installInputMethod()`（`:128-236`）之重試機制（`kInstallRetryInterval = 0.5`、`kInstallRetryTimeout = 60`）**只涵蓋複製**，不涵蓋終止。

## 2. 排除項（為何不是環境問題）

- **兩個安裝器皆無 App Sandbox**：`Build/vChewingInstaller.app` 之 entitlements 僅 `com.apple.security.cs.disable-library-validation`；`Build/vChewingInstallerNightly.app` 為空 entitlements。
- **唯音未自接訊號處理**：全倉（`Packages/`、`Sources/`）無 `SIGTERM`／`SIGKILL`／`makeSignalSource`／`signal(SIG`／`sigaction` ⇒ SIGTERM 一到即應終止。
- **`killall` 本身正常**：`/usr/bin/killall` 於 macOS 27.0.1（26A434）仍存在（184,416 B、root:wheel）。事主於終端機實測 `killall vChewing` 有效（PID 65504 消失）。
- **但「殺掉」不是穩定狀態**：IMK 隨選啟動，唯音幾乎立刻以新 PID（66141）重生 ⇒ postcondition **不可**寫成「沒有行程」（必被重拉、永遠逾時）。

## 3. 設計

- **保證之所在＝換檔之後那一刀**：IMK 永遠自「當下磁碟上、已註冊之 bundle」拉起輸入法；換檔**前**殺，系統只會把舊碼重新拉起（新 PID、舊碼），該行程恰好躲過其後一切檢查。故於 `moveItem`（`:144`）成功、停計時器（`:151`）之後補一刀，且**務必留在 `if allRegisteredInstancesOfThisInputMethod.isEmpty` 之外**（升級安裝時該分支不執行，而升級安裝正是最需要此刀之情境），亦須先於輸入源註冊／啟用（那些動作本身就可能請系統拉起輸入法）。
- **postcondition＝「那批捕捉到的 PID 皆已消失」**：捕捉 → SIGTERM → 0.1 秒級輪詢（上限 3 秒）→ 必要時 SIGKILL → 再驗 ≤3 秒；結果記 `escalated`／`surviving`。
- **捕捉三路**：
  1. `NSWorkspace.shared.runningApplications` 之執行檔名（認 `Contents/MacOS/` 之下該檔名，不受 `MAXCOMLEN` 截斷影響）；
  2. `NSRunningApplication.runningApplications(withBundleIdentifier:)`（識別字取自 `Bundle(url: imeURLInstalled)`，不寫死）；
  3. `pgrep -x <name>`（作業系統之程序表，不倚賴 AppKit 之應用程式註冊）。
- **第一刀保留但不承擔保證**：改走 `terminateByProcessName` 並記錄 `killall` 結束碼 ⇒「第一刀究竟跑到沒有、結果如何」此後可觀測（P298 對「第一刀何以失效」此一未解疑點之交代：不再猜，改為留痕）。
- 日誌格式：
  - `Terminate: reason=preSwap|postSwap|textInputMenuAgent captured=[…] escalated=… result=vacated|stuck surviving=[…]`
  - `Terminate: reason=… target=… killall=<碼|launchFailed> output=…`
- 終止目標之清單另含 `vChewingPhraseEditor`（僅換檔前，`.bestEffort`、不升級）；換檔後之保證刀只針對 `vChewing`。

## 4. 測試與踩坑

- `swift test --disable-sandbox`（本工具沙盒下不加旗標會 `Invalid manifest`／`sandbox_apply: Operation not permitted`）→ **17 支／2 套全過**。
- 踩坑一：`FileHandle.readToEnd()` 回傳 `Data?`，`try?` 攤平後**僅能一層**條件綁定（多綁一層編譯失敗）。
- 踩坑二：探針**不可**用 `/bin/sh -c "sleep 30 & echo $!"` 造孤兒行程——本環境中 shell 一退出，其背景行程即消失，探針當場非存活，「測不出東西」。
- 踩坑三：探針命令列一律寫絕對路徑（`exec /bin/sleep 30`）：測試行程之 `PATH` 未必含 `/bin`，否則 shell 以 127 退出，而「SIGTERM 有效」之結論將是假象。
- 踩坑四：`pgrep -x` 只認 `MAXCOMLEN`（16 位元組）以內之程序名 ⇒ `vChewingPhraseEditor`（20 字元）於該路徑認不到；換檔後之保證刀只針對 `vChewing`、且另有 AppKit 名路徑補位，故無實害。

## 5. 已知界線

- 保證刀只保證「此後被拉起的行程是新碼」，不保證舊行程於安裝當下未正在處理某客體之輸入（IMK 會於下次連線重建 session）。
- 未以真實安裝實測（會動到事主機器上正在使用中之輸入法）；真實驗證＝下一次夜版換裝後查 `Terminate:` 兩行與 `pgrep -x vChewing` 之 PID 是否更新。
- PKG 路徑仍為「送出即忘」之 `killall … || true`，本次未動。
