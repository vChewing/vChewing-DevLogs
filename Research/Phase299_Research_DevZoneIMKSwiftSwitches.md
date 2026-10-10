# Phase 299 研究：IMKSwift 私面干涉之診斷開關

> 狀態：研究稿（2026-10-11）。本 phase 為「開發道場（DevZone）擴充」；三開關之運行期效果尚待真機翻動驗證（本 phase 只做到建置與靜態檢核）。
> 前置：`Research/Phase291_Research_FlagsChangedDeliveryFailure.md`、`Research/Phase296_Research_FlagsChangedCallbackEntry.md`、本卷 P296／P298 兩篇。

## 0. 起因：兩處能讓症狀「完全靜默」的干涉

客訴 #618 之症狀（右 Shift 單擊切換英數失靈、事後按 Caps Lock 可救）在 P296 之 `EventEntry:` 上線後已可三分：事件未進本行程／位址已除名／被投給別枚 controller。惟 `Packages/vChewing_IMKUtils/Sources/IMKSwiftModernHeaders/IMKSwift.m` 內有兩處對 `IMKServer` 私有面之干涉，**皆能使症狀完全不留下我方日誌**（事件根本未被派送到本行程）：

| 代號 | 干涉 | 落點 | 為何能解釋「零日誌」 |
|:--|:--|:--|:--|
| I1 | 無條件剔除 `IMKServer._private._controllers` 內最舊且非當前者 | `+IMKSwift_pruneStaleControllersOnServer:excludingSelf:`（由 `initWithServer:delegate:client:` 呼叫） | 除名後 IMK 不再把該 controller 視為可派送對象 |
| I2 | 停用 3 秒後終止客體之 XPC 連線 | `IMKSwift_delayedDealloc`（由 `deactivateServer:` 以 3.0 秒排程） | 連線若已斷，其後事件無從送達 |

- 判別因果之障礙：兩項干涉都在唯音自己的程式碼內、且都生效於事件派送之前；若只能改碼重編後才觀察得到，使用者端（客訴現場）便無法參與判定。
- 附帶障礙：`_IMKServerLegacy`／`IMKClient_Modern` 之分身由系統 `+subclass` 於執行期挑選、與建置 SDK 無關 ⇒「現場跑的究竟是哪個分身」原本無從辨識（見 KnowledgeMemo §12.6 之 P298 ★ 條）。

## 1. 三開關之定義

| UserDef 鍵（即 `UserDefaults` 鍵） | 停用者 | 守衛落點 |
|:--|:--|:--|
| `_IMKSwift_disableServerControllerPruning` | I1 之整段剔除 | `IMKSwift_pruneStaleControllersOnServer:excludingSelf:` 之 `@autoreleasepool` 首段 |
| `_IMKSwift_disableClientWrapperTermination` | I2 之客體 wrapper 終止（除名照舊） | `IMKSwift_delayedDealloc` 之 wrapper 終止段 |
| `_IMKSwift_disableDelayedDeallocation` | 延遲釋放之**整個流程**（既不除名、亦不終止連線） | `IMKSwift_scheduleDelayedDeallocAfterDelay:` 之排程前 ＋ `IMKSwift_delayedDealloc` 之首段 |

- 巢狀關係：S3 ⊃ S2。S3 開啟時除名改由 `- (void)dealloc` 之 `_IMKSwift_onDealloc` 承擔，故不會永失除名。
- 三者一律預設 `false`＝現行出貨行為；皆為**診斷用**，於偏好設定 → 開發道場露出。

## 2. 設計要點：決策當下求值、不快取

- ObjC 端不以 `NSUserDefaults` 直讀（違反 `UserDef`＋`PrefMgrProtocol`＋`PrefMgr` 三位一體之紀律），改由 Swift 端安裝回傳 `BOOL` 之 block（`configureServerControllerPruningDisabled(_:)` 等三支），ObjC 端每次決策都呼叫一次。
- 未安裝（或 `nil`）之 block 一律視為「未停用」＝出貨行為 ⇒ 私物或呼叫端缺席時退化為 no-op。
- **此設計之全部價值在於「就地實驗」**：使用者可在失靈當下翻開關，而無須換版重裝；故不得快取、亦不得以 `#if DEBUG` 為閘（夜版即 release 建置）。
- 計時器可能早於「翻開關」之時刻即已排定 ⇒ `IMKSwift_delayedDealloc` 之首段必須**再驗一次**（雙重守衛）。

## 3. 判讀：日誌對照

| 日誌 | 意義 |
|:--|:--|
| `Prune: skipped (disableServerControllerPruning)` | I1 已停用（剔除未執行） |
| `DelayedDealloc: not scheduled (disableDelayedDeallocation) addr=…` | 排程當下即被擋下 |
| `DelayedDealloc: skipped (disableDelayedDeallocation) addr=…` | 已排定之計時器於觸發時被擋下 |
| `DelayedDealloc: client wrapper kept (disableClientWrapperTermination) addr=…` | 除名照舊、僅保留客體連線 |
| `ServerFlavor: server=… client=…` | 本行程所用之 IMK 分身（`_IMKServerLegacy` 等）；P299 Task 1 |

## 4. 已知界線

- 開關只停「唯音主動施加之干涉」，不停系統自身行為；亦不改 IMK 之派送語意。
- `_private` 之 KVC **讀取**本身（`_controllers`／`_currentController`）未加開關 ⇒ 私物改名時仍可能拋例外（既有風險、本次未動）。
- 停用 I2 之代價：客體 XPC 連線不即時釋放（每條約 440 bytes），長時間掛著會累積。
- 三開關之運行期效果尚待真機驗證；本 phase 未做任何自動化測試（開關本身無獨立可測之邏輯，其效果須在真實 IMK 派送路徑上觀察日誌）。
