# Phase 299 研究：IMKSwift 私面干涉之診斷開關

> 狀態：研究稿（2026-10-11）。本 phase 為「開發道場（DevZone）擴充」；四開關之運行期效果尚待真機翻動驗證（本 phase 只做到建置與靜態檢核）。現場判別之最小流程見 §6（四步、不必窮舉 16 種組態）。
> 前置：`Research/Phase291_Research_FlagsChangedDeliveryFailure.md`、`Research/Phase296_Research_FlagsChangedCallbackEntry.md`、本卷 P296／P298 兩篇。

## 0. 起因：兩處能讓症狀「完全靜默」的干涉

客訴 #618 之症狀（右 Shift 單擊切換英數失靈、事後按 Caps Lock 可救）在 P296 之 `EventEntry:` 上線後已可三分：事件未進本行程／位址已除名／被投給別枚 controller。惟 `Packages/vChewing_IMKUtils/Sources/IMKSwiftModernHeaders/IMKSwift.m` 內有兩處對 `IMKServer` 私有面之干涉，**皆能使症狀完全不留下我方日誌**（事件根本未被派送到本行程）：

| 代號 | 干涉 | 落點 | 為何能解釋「零日誌」 |
|:--|:--|:--|:--|
| I1 | 無條件剔除 `IMKServer._private._controllers` 內最舊且非當前者 | `+IMKSwift_pruneStaleControllersOnServer:excludingSelf:`（由 `initWithServer:delegate:client:` 呼叫） | 除名後 IMK 不再把該 controller 視為可派送對象 |
| I2 | 停用 3 秒後終止客體之 XPC 連線 | `IMKSwift_delayedDealloc`（由 `deactivateServer:` 以 3.0 秒排程） | 連線若已斷，其後事件無從送達 |

- 判別因果之障礙：兩項干涉都在唯音自己的程式碼內、且都生效於事件派送之前；若只能改碼重編後才觀察得到，使用者端（客訴現場）便無法參與判定。
- 附帶障礙：`_IMKServerLegacy`／`IMKClient_Modern` 之分身由系統 `+subclass` 於執行期挑選、與建置 SDK 無關 ⇒「現場跑的究竟是哪個分身」原本無從辨識（見 KnowledgeMemo §12.6 之 P298 ★ 條）。

## 1. 四開關之定義（S1...S4）

| 代號 | UserDef 鍵（即 `UserDefaults` 鍵） | 停用者 | 守衛落點 |
|:--|:--|:--|:--|
| S1 | `_IMKSwift_disableServerControllerPruning` | I1 之整段剔除 | `IMKSwift_pruneStaleControllersOnServer:excludingSelf:` 之 `@autoreleasepool` 首段 |
| S2 | `_IMKSwift_disableEvictedClientInvalidation` | I1 剔除時對**該筆登記所對應客體 XPC 連線**所施之作廢（剔除本身照舊） | 同上剔除段之 `[(id)key invalidate]` |
| S3 | `_IMKSwift_disableClientWrapperTermination` | I2 之客體 wrapper 終止（除名照舊） | `IMKSwift_delayedDealloc` 之 wrapper 終止段 |
| S4 | `_IMKSwift_disableControllerDelayedDeallocation` | 延遲釋放之**整個流程**（既不除名、亦不終止連線） | `IMKSwift_scheduleDelayedDeallocAfterDelay:` 之排程前 ＋ `IMKSwift_delayedDealloc` 之首段 |

- 巢狀關係：S4 ⊃ S3（S4 開啟時除名改由 `- (void)dealloc` 之 `_IMKSwift_onDealloc` 承擔，故不會永失除名）；S2 為 S1 之細粒度一半，**S1 開啟時 S2 無效**（剔除既已不發生，自無連線可保）。
- 四者一律預設 `false`＝現行出貨行為；皆為**診斷用**，於偏好設定 → 開發道場露出（該 section 置於「JSON 交換」section 之上方）。

## 2. 設計要點：決策當下求值、不快取

- ObjC 端不以 `NSUserDefaults` 直讀（違反 `UserDef`＋`PrefMgrProtocol`＋`PrefMgr` 三位一體之紀律），改由 Swift 端安裝回傳 `BOOL` 之 block（`configureServerControllerPruningDisabled(_:)`、`configureEvictedClientInvalidationDisabled(_:)`、`configureClientWrapperTerminationDisabled(_:)`、`configureControllerDelayedDeallocationDisabled(_:)` 四支），ObjC 端每次決策都呼叫一次。
- 未安裝（或 `nil`）之 block 一律視為「未停用」＝出貨行為 ⇒ 私物或呼叫端缺席時退化為 no-op。
- **此設計之全部價值在於「就地實驗」**：使用者可在失靈當下翻開關，而無須換版重裝；故不得快取、亦不得以 `#if DEBUG` 為閘（夜版即 release 建置）。
- 計時器可能早於「翻開關」之時刻即已排定 ⇒ `IMKSwift_delayedDealloc` 之首段必須**再驗一次**（雙重守衛）。

## 3. 判讀：日誌對照

| 日誌 | 意義 |
|:--|:--|
| `Prune: skipped (disableServerControllerPruning)` | I1 已停用（剔除未執行） |
| `Prune: evicted addr=… gen=… remaining=… (client connection kept)` | S2 開啟：剔除照舊、僅保留該筆登記之客體連線 |
| `DelayedDealloc: not scheduled (disableControllerDelayedDeallocation) addr=…` | 排程當下即被擋下 |
| `DelayedDealloc: skipped (disableControllerDelayedDeallocation) addr=…` | 已排定之計時器於觸發時被擋下 |
| `DelayedDealloc: client wrapper kept (disableClientWrapperTermination) addr=…` | 除名照舊、僅保留客體連線 |
| `ServerFlavor: server=… client=…` | 本行程所用之 IMK 分身（`_IMKServerLegacy` 等）；P299 Task 1 |

## 4. 已知界線

- 開關只停「唯音主動施加之干涉」，不停系統自身行為；亦不改 IMK 之派送語意。
- `_private` 之 KVC **讀取**本身（`_controllers`／`_currentController`）未加開關 ⇒ 私物改名時仍可能拋例外（既有風險、本次未動）。
- 停用 I2 之代價：客體 XPC 連線不即時釋放（每條約 440 bytes），長時間掛著會累積。S2 之代價與此同型（被剔除者之連線亦然）。
- 四開關之運行期效果尚待真機驗證；本 phase 未做任何自動化測試（開關本身無獨立可測之邏輯，其效果須在真實 IMK 派送路徑上觀察日誌）。
- 鍵名之沿革：S4 之鍵於本 phase 內一度為 `_IMKSwift_disableDelayedDeallocation`，後改名為 `_IMKSwift_disableControllerDelayedDeallocation`（明示所延遲者為 controller 之析構）；該鍵未曾出貨，故無偏好遷移問題。

## 5. 連帶影響：配置助手之防漂移產物

- `UserDef` 增四鍵即動到助手（`ValueAdd/WebConfigAssistant/`）之產物，須照 `Makefile` 依賴序重生：`make metadata-update` → `make surface` → `make fixtures`（無 target／hook／CI 會自動跑第一步）。本次實測：`assets/userdef-metadata.json` 之 `count` 119→123（＋129 行）、`assets/settings-surface.json` 之曝露面 108→112 鍵（掃 31 檔）、六份契約 fixture 不變。
- `tests/metadata.test.js:28` 之 `assert.strictEqual(metadata.count, 119)` 須同步改 **123**，否則 `make audit` 之測試即以 `strictEqual: 123 !== 119` 失敗（本次即如此擋下）；改後 `make audit` 全綠（92 支、含 `metadata`／`metadata-audit --strict`／`surface-check`／`version-check`／`fixtures-check`）。
- 四鍵**不進**助手題庫（`src/questions.ts`）——**事主 2026-10-11 明示**（「這四個先不用加入配置助手」）。`metadata-audit --strict` 與 `surface-check` 皆通過 ⇒ 現行 audit 不要求覆蓋；四鍵屬診斷面，改由 DevZone 提供。

## 6. 現場判別之最小流程（不須窮舉）

四鍵雖有 2⁴＝16 種組態，但兩條巢狀關係令其**可分辨之行為只有 9 種**：S1 開啟 ⇒ S2 失效（無剔除則無連線可保）；S4 開啟 ⇒ S3 失效（S3 之守衛落於 S4 所守之 body 內，程式碼級不可達）。逐組態計數：

| S1 | S4 | S2 可否生效 | S3 可否生效 | 行為數 |
|:--:|:--:|:--:|:--:|:--:|
| 0 | 0 | ✓ | ✓ | 4 |
| 0 | 1 | ✓ | ✗ | 2 |
| 1 | 0 | ✗ | ✓ | 2 |
| 1 | 1 | ✗ | ✗ | 1 |
| | | | **合計** | **9** |

- 兩家族又住**不同路徑**：S1／S2 在「建立輸入控制器時」之 prune（`IMKSwift_pruneStaleControllersOnServer:excludingSelf:`）；S3／S4 在「停用後 3 秒」之延遲析構（`IMKSwift_scheduleDelayedDeallocAfterDelay:`／`IMKSwift_delayedDealloc`）。故兩者可分別施測、互不干擾。
- 現場只需**四步**（每次只翻一鍵、設計上即時生效、無須重啟）：

| 步 | 動作 | 症狀消失 ⇒ | 症狀仍在 ⇒ |
|:--:|:--|:--|:--|
| 1 | 開 S1（最粗） | 病灶在 prune 路徑 → 進第 2 步 | 換測延遲析構 → 進第 3 步 |
| 2 | 關 S1、改開 S2 | 病灶是「剔除時之作廢（`invalidate`）」 | 病灶是「剔除本身」（S1 所涵蓋之語意） |
| 3 | 開 S4（整段延遲析構停用） | 病灶在延遲析構 → 進第 4 步 | 兩家族皆非病灶（改查 `ServerFlavor:` 與其他派送環節） |
| 4 | 關 S4、改開 S3 | 病灶是「客體 wrapper 之 XPC 終止」 | 病灶是延遲析構之其餘部分（除名與 `_IMKSwift_onDealloc`） |

- 每步皆可由日誌確認該開關確已生效（§3）：`Prune: skipped`／`Prune: evicted … (client connection kept)`／`DelayedDealloc: not scheduled`／`DelayedDealloc: skipped`／`DelayedDealloc: client wrapper kept`——**不必以症狀是否重現來反推開關是否生效**（此即「零日誌」症狀下仍能判別之關鍵）。
- 界線：開關「即時生效」係設計（決策當下求值、不快取）而非實測；若現場翻動後日誌未出現對應字樣，先以 `defaults read` 確認該 `_IMKSwift_*` 鍵確已寫入，再論其它。
