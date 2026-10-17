# Phase 314 研究：測試隔離之兩道縫——`UserDefaults` 之協定化與使用者資料之語意開關

- 撰寫日期：2026-10-15。
- 適用範圍：`vChewing-LibVanguard`（正本）之 **10 個測試目標（另 1 個測試素材目標）、768 支用例**；設計落點主在 `Sources/Shared`、`Sources/LexiconAssembly`、`Sources/LibVanguard`，以及 `Deps/VanguardSwiftExtension`。
- 本檔為長篇推導、全量落點表與分期草案；Phase 篇（`Reqs_0311-0320.md`）只留決定性取捨與驗證。
- **本 phase 不動任何生產碼**（依 P301「研究任務」之先例）：交付＝本檔 ＋ 分期草案；實際手術自 P315 起。

## 〇、事主指示（原文）

> 這個研究任務所試圖解決的一個長遠目標：**這樣可以讓 LibVanguard 整個脈絡的所有單元測試脫離那種「被迫 serialized 執行」的枷鎖。**

> 這個研究任務的具體目的（**不一定 valid，你來判斷**）：
> - 讓整個 LibVanguard 對 `UserDefaults` 的依賴徹底 Protocol 化、而不是直接依賴到 `UserDefaults` 本體。這可能會使得很多類型需要依賴 Associated Type 或 Generics。
> - 讓整個 LibVanguard 對檔案系統的依賴可以用語意來開關，這樣的話在做沙箱測試時不會出現「多個 test case 讀寫同一片使用者片語硬碟區域」的情況。

事主既明言「不一定 valid，你來判斷」，故第一節先給裁定，其後各節為其證據。

---

## 一、裁定（先給結論）

### 1.1 兩項具體目的

| 目的 | 裁定 | 理由 |
|:--|:--|:--|
| 對 `UserDefaults` 徹底協定化 | **成立、且必要；但不足以單獨成事** | 枷鎖**不是**「依賴了 `UserDefaults` 這個型別」——`@AppProperty` 早就經由 `UserDefaults.current` 這層間接讀寫，測試也早已能換容器（`UserDefaults.unitTests = .init(suiteName:)`）。枷鎖是**該間接層本身係行程級可變全域**，且**仍有兩處繞過它直讀 `.standard`**。協定化是讓「容器」變成**注入值**的必要手段，不是目的本身。 |
| 對檔案系統以語意開關 | **成立、且成本遠低於第一項** | 需要控制的**不是「檔案系統」全體**，而是**可寫的使用者資料落點**。**唯讀**資源（辭典 fixture、CIN 磁帶、SwiftPM 資源 bundle）跨測試共用無害、不構成競爭，故**不須**協定化。把 `FileManager` 整個換掉是本提案最容易走偏之處。 |
| 「很多類型需要 Associated Type 或 Generics」 | **不成立——此憂可解，且應主動避免** | 全倉 127 處 `@AppProperty` 全部經由**同一個** `@propertyWrapper` 進入。縫只要開在該 wrapper 的 `container`（`Deps/VanguardSwiftExtension/Sources/SwiftExtension/SwiftFoundationImpl.swift:251`，現為 `public var container: UserDefaults { .current }`）⇒ **宣告端零改動、無泛型傳染**。泛型只有在「要求 store 於**編譯期**依型別解析」時才會被迫；那正是應避免的設計（見 §四之駁回 2）。 |

### 1.2 真正的枷鎖有四條，不是兩條

事主列出兩條。實測後另有一條被漏看、一條是既有病灶的延續：

| 代號 | 枷鎖 | 是否本 phase 之射程 |
|:--|:--|:--|
| **A** | 行程級可變偏好容器（`UserDefaults.current`／`.unitTests`／`.pendingUnitTests`） | 是（縫一） |
| **B** | 行程內可變**靜態**（`PrefMgr.sharedSansDidSetOps`、`LXFacade.factoryTrie`／`lxCassette`／`lxPlainBopomofo`、`ResourceLocator` 之 static） | 部分（縫開好後才可能收）——**這條才是 `LibVanguardTests` 之 `.serialized` 的主因** |
| **C** | 可寫落盤區之**固定檔名**共用（`NSTemporaryDirectory()` ＋ 固定檔名；`/dev/null` 之雜用） | 是（縫二） |
| **D** | 歷史慣性——根 suite 之 `.serialized` 被整棵子樹繼承，其真因早已不在 | 是（可直接撤，見 §二.4） |

**故本 phase 是「前置」、不是「終局」**：縫一與縫二開好之後，才具備把 B 類靜態降為實例的條件；而撤 `.serialized` 的**充分條件是 B 類清空**。

---

## 二、現況盤點

### 2.1 測試基線與 `.serialized` 之分佈

全量 **768 支／71 套**（與 P312 完工時相同）。逐目標：

| 目標 | Swift 檔 | 載 `.serialized` 之檔 | `@Test` |
|:--|--:|--:|--:|
| `LexiconAssemblyTests` | 33 | **32** | 220 |
| `LibVanguardTests` | 28 | 6 | 334 |
| `HomaTests` | 9 | 6 | 63 |
| `TekkonTests` | 9 | 7 | 58 |
| `TrieKitTests` | 5 | 3 | 18 |
| `SharedTests` | 3 | 3 | 24 |
| `BPMFVSTests` | 1 | 1 | 7 |
| `ResourceLocatorTests` | 1 | 1 | 6 |
| `BrailleSputnikTests` | 1 | 1 | 3 |
| `ArimitsuTests` | 2 | **0** | 35 |
| `HomaSharedTestComponents` | 2 | 0（非測試目標） | 0 |

- **載 `.serialized` 者佔 60／92 檔（65%）**。
- `LibVanguardTests` 之 334 支**全部**落於唯一根 suite `@Suite("LibVanguardTestsRoot", .serialized) final class LibVanguardTestsRoot {}`（`Tests/LibVanguardTests/LibVanguardTests_Root.swift:35`）之下；`POMTestSuite`（`Tests/LexiconAssemblyTests/POMBasicTests.swift:13-14`）同理，其 8 個子 suite 皆繼承之。
- **既有反證**：`ArimitsuTests`（獨立目標、`Tests/LibVanguardTests/Arimitsu/`、35 支、3 個 `@Suite` 全無 `.serialized`）**現已並行且全綠**。這是「不必人人都 `.serialized`」的倉內實證，且證明該目標對 `Shared`／`Tekkon` 之依賴並不引入行程級可變狀態。

### 2.2 `.serialized` 之真因分類（逐檔量測）

以「該目標之測試檔是否引用 `UserDefaults`／`FileManager`／`NSTemporaryDirectory`／`.shared`／`static var`」為尺：

| 目標 | (A) 偏好容器 | (B) 行程內靜態 | (C) 共用落盤 | (D) 慣性 | 直觀判定 |
|:--|:--:|:--:|:--:|:--:|:--|
| `LibVanguardTests` | ✓ `InputHandlerTests_Basics.swift:176-177`、`SessionTests_Basics.swift`、`LibVanguardTests_Root.swift:30` | ✓ `LXFacade.factoryTrie`／`lxCassette`／`PrefMgr.shared`／`SessionHost.shared`（見該檔 12–20 行自陳） | ✓ `SessionTests_Basics.swift` | — | 四因皆有，最難 |
| `LexiconAssemblyTests` | ✓ `LXFacade_FuriousZhuyinwenTests.swift:193-200` | ✓ `LXFacade` 之 static ＋ `PrefMgr.sharedSansDidSetOps` | ✓ 14 檔碰 FS | ✓ `POMTestSuite` 根 (32/33，壓倒性) | (D) 為大宗，真因集中 |
| `SharedTests` | ✓ 3/3（`UserDefExchangeTests.swift:14-15`、`PrefMgrFuriousTypingMigrationTests.swift:10-14`） | ✓ `PrefMgr.sharedSansDidSetOps` | ✓ `SharedTests.swift` | — | (A) 為主 |
| `TekkonTests` | 無 | 無（僅 `SyllableIndex.shared` 為唯讀） | `TekkonTests_PhonabetAutoChopPredicate.swift:104` 一處 `fileExists` | ✓ 7/9 | **零真因之可能** |
| `HomaTests` | 無 | 無 | 無 | ✓ 6/9（根 suite 繼承） | **零真因之可能** |
| `TrieKitTests` | 無 | 無 | 無 | ✓ 3/5 | **零真因之可能** |
| `BPMFVSTests` | 無 | 無 | 無 | ✓ 1/1 | **零真因之可能** |
| `BrailleSputnikTests` | 無 | 無 | 無 | ✓ 1/1 | **零真因之可能** |
| `ArimitsuTests` | 無 | 無 | 無 | **無** | 已並行、已綠 |

### 2.3 三條已入冊之紀律（本 phase 所治之痛的既成記載）

三條全住 `KnowledgeMemo_SubArticles/18-WorkDetails-BuildAndTest.md`：

1. **★ 測偏好之測試用例須自備隔離容器，且不可只清輸入鍵**（2026-09-26，P253／P257）：以 `UserDefaults.unitTests = .init(suiteName:)` ＋ `pendingUnitTests = true` ＋ `UserDef.resetAll()` 起手，事後還原並 `removeSuite`；`@AppProperty` 之 get／set **逐次**讀寫 `UserDefaults.current`（容器一切換即生效、無快取）。同條末：**兩顆 `swift test` 不得並行**（同源：同一行程內之跨 suite 偏好汙染）。
2. **★ 共用層（`Sources/Shared`）之改動須兩倉同源、逐位元組相同**（2026-10-11，P299）：`UserDef`／`PrefMgrProtocol`／`PrefMgr_Core` 三檔同時存在於正本與 `vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard`；**漏改一側不會有任何建置或測試徵兆**。
3. **★ 單元測試不得並行跑兩支 `swift test` 行程**（2026-10-14，P302）：兩倉之測試共用同一份 `UserDefaults`／語彙／POM 落盤狀態 ⇒ 並行執行（即使分屬不同倉）會互相踩踏；症狀是「先前全綠之雙拼用例成批失敗」，逐一序列執行即復綠。

> 第 1 條所載之「隔離容器」**正是本 phase 要拆掉的東西**——它有效，但代價是：每個 suite 各據一個**落在磁碟上的具名 suite**，故它只隔離了**容器**，未隔離**行程**；第 3 條即其後果。
>
> 另：`vChewing-macOS/Makefile:546` 之註記「單元測試一律 `--no-parallel`：本倉的測試共用大量行程內靜態狀態」與 `vChewing-LibVanguard/Makefile:157` 之 `swift test -c release --no-parallel` 為同一紀律之落地處。

### 2.4 兩道現行防線的層級（為何「被迫 serialized」是雙重的）

| 層 | 手段 | 治什麼 | 不治什麼 |
|:--|:--|:--|:--|
| CLI | `swift test --no-parallel`（`Makefile:157`） | 同一顆 `swift test` 內**多個測試目標**之並行 | 目標**內**之 suite 交錯；跨行程（另一顆 `swift test`、CI、Docker）之競爭 |
| 型別 | 根 suite ＋ `.serialized` | 該子樹內**絕不並行**（`Swift Testing` 之保證） | 跨行程之競爭；跨目標之競爭 |

故 P302 之禁令與 `.serialized` **互不替代、缺一不可**——這正是事主所稱「枷鎖」之實體：**兩道鎖同時上著**。

### 2.5 `UserDefaults` 面之全量落點

| 位置 | 檔數 | 出現數 | 性質 |
|:--|--:|--:|:--|
| `Sources/**`（正本生產碼） | 16 | **47** | 見附錄 A |
| `Deps/VanguardSwiftExtension/Sources/SwiftExtension/SwiftFoundationImpl.swift` | 1 | **6** | 縫之機制本體 |
| `Tests/**` | 6 | **43** | 測試側之佈置與斷言 |

**縫之機制**（`SwiftFoundationImpl.swift:207-228`）：

```swift
extension UserDefaults {
  nonisolated public static var pendingUnitTests: Bool { … }   // NSMutex<Bool>
  nonisolated public static var unitTests: UserDefaults? { … } // NSMutex<UserDefaults?>,
                                                               // 預設 UserDefaults(suiteName: "UnitTests")
  nonisolated public static var current: UserDefaults {
    pendingUnitTests ? (unitTests ?? .standard) : .standard
  }
}
```

以及 `@AppProperty`（同檔 `:234-260`）之 `public var container: UserDefaults { .current }`（`:251`）——**這一行是全倉 127 處偏好宣告的唯一出入口**。

**三處洩漏**（本 phase 之直接對象）：

| # | 位置 | 病灶 |
|:--|:--|:--|
| 1 | `Sources/Shared/PrefMgr_Core.swift:563` `let defaults = UserDefaults.standard` | `migrateDeprecatedSettings()` **繞過** `current`，直讀寫**真機網域**。故 `Tests/SharedTests/PrefMgrFuriousTypingMigrationTests.swift:10-14` 必須明言「**不經** `UserDefaults.current`」「全程強制 `pendingUnitTests = false`」「**直接對 `.standard` 佈置與清理**」，且該檔 `:155` 自陳 `candidateStateJKHLBehavior` 是「**跨測試共用**之 `UserDefaults.standard`」。⇒ 單元測試**正在讀寫開發者的真實偏好檔**，並可與同一機器上執行中的唯音實例互踩。 |
| 2 | `Sources/LexiconAssembly/vChewingLXAssembly_Common.swift:153` `UserDefaults.standard.object(forKey: "_DebugMode")` | 熱路徑（`vCLMLog`）直讀 `.standard`；而 `Sources/Shared/Shared.swift:21` 之間義讀取卻走 `.current`。**同一語義兩處實作、兩處判準**。 |
| 3 | `unitTests` 之**預設值**係 `UserDefaults(suiteName: "UnitTests")` | 具名 suite ＝ **落盤 plist**（`~/Library/Preferences/…`）⇒ 即使各 suite 各換名字，**跨行程**仍共寫同一批檔案（P302 之根因）。 |

**另有一類非儲存之雜用**：`UserDefaults.pendingUnitTests` 同時是**排程語意之開關**——以 `bypassAsync: UserDefaults.pendingUnitTests`（或其複合式）為引數者共 **9 處**（`SessionProtocol.swift` 7、`InputSession_HandleEvent.swift` 1、`InputSession_HandleStates.swift` 1；另一處 `InputSession_HandleStates.swift:170` 之 `bypassAsync: !async` 與此無涉），另有 `Sources/LexiconAssembly/LXFacade.swift:326` 與 `vChewingLXAssembly_Common.swift:170` 以 `= !pendingUnitTests` 決定 `asyncLoadingUserData`，及 `vChewingLXAssembly_Common.swift:150` 之「測試模式僅於 `--filter` 時輸出日誌」。`Sources/**` 內 `pendingUnitTests` 共 **21 處**。**這是把「測試中」當成生產語意之全域旗標，應與儲存分家**（見 §三.1.4）。

### 2.6 檔案系統面之全量落點

`Sources/**` 內 `FileManager` 之引用共 **27 處**；扣除 `Sources/vChewingSharedCLI/` 之 5 處與 `ResourceLocator` 之 2 處（皆不在射程）後，**射程內 20 處**：

| 檔 | `FileManager` | 性質 |
|:--|--:|:--|
| `Sources/LexiconAssembly/LXFacade.swift` | 8 | 全為 `isReadableFile(atPath:)`（載入閘門）——`:283`／`:300`／`:451`／`:483`／`:520`／`:535`／`:564`／`:598` |
| `Sources/LexiconAssembly/SubLMs/lxPerceptionPersistor.swift` | 6 | `:178`／`:246`／`:358`／`:398`／`:463`／`:564`（快照與 `.journal` 之讀寫、輪替、清理） |
| `Sources/LexiconAssembly/LXConsolidator.swift` | 3 | `:22`／`:59`／`:121`（`fileExists`＋`attributesOfItem`） |
| `Sources/LexiconAssembly/SubLMs/lxCassette.swift` | 1 | `:934` `fileExists` |
| `Sources/LexiconAssembly/LXFacade_TextMapExtension.swift` | 1 | `:559` `resolveTextMapPath` |
| `Sources/ResourceLocator/ResourceLocator.swift` | 2 | `:96`／`:103`——**唯讀資源查找**，不在射程 |
| `Sources/vChewingSharedCLI/VCSharedCLI_main.swift` | 5 | 命令列工具，不在射程 |

**落點之實體係「字串型別之路徑成員」**：

| 型別 | 成員 | 位置 |
|:--|:--|:--|
| `LXCoreEX`（`lxUserPhrases`／`lxFiltered`／`lxUserSymbols`） | `var filePath: String?` | `Sources/LexiconAssembly/SubLMs/lxCoreEX.swift:45`（寫入於 `LXFacade.swift:469`／`:501`／`:553`；落盤於 `lxCoreEX.swift:192-204`） |
| `LXAssociates` | `var filePath: String?` | `Sources/LexiconAssembly/SubLMs/lxAssociates.swift:37`（`LXFacade.swift:588`；落盤於 `lxAssociates.swift:169-175`） |
| `LXReplacements` | `var filePath: String?` | `Sources/LexiconAssembly/SubLMs/lxReplacements.swift`（`LXFacade.swift:616`；落盤於 `:131-137`） |
| `LXCassette` | `private(set) var filePath: String?` | `Sources/LexiconAssembly/SubLMs/lxCassette.swift:23`（`:1135`） |
| `LXPerceptionPersistor` | `public var fileSaveLocationURL: URL?` | `Sources/LexiconAssembly/SubLMs/lxPerceptionPersistor.swift:32`（存入於 `:25`、消費於 `:173`／`:242`／`:295`） |

**測試側之共用落盤**（15 檔碰 FS，代表性三例）：

| 檔 | 現況 | 病灶 |
|:--|:--|:--|
| `Tests/LexiconAssemblyTests/POMFileHandleTests.swift` | `NSTemporaryDirectory()` ＋ **固定檔名**（`test_pom_fix.json`／`test_pom_logging.json`／`test_pom_journal.json` 等六個） | **正是事主所指「多個 test case 讀寫同一片硬碟區域」**；故須 `.serialized` |
| `Tests/LexiconAssemblyTests/POMIndexedRetrievalTests.swift` | 已用 `pom-indexed-\(UUID())` 目錄，卻另立 `private let indexedNullURL = URL(fileURLWithPath: "/dev/null")`（`:12`） | 以 `/dev/null` 當「語意上之不落盤」；`lxPerceptionPersistor` 之 `saveData` 先問 `fileExists` ⇒ `/dev/null` **存在** ⇒ 走「只寫日誌」之分支。此為**靠巧合成立之語意**，且 `filePath = nil` 之另一條不落盤路徑語義不同，兩者雜用。 |
| `Tests/LexiconAssemblyTests/POMJournalReplayTests.swift` | 已用 `pom-journal-\(UUID())` 目錄（`:12-16`） | 目錄已隔離，惟其 `@Suite(.serialized)` 仍存 ⇒ 屬 (D) 類慣性 |

---

## 三、設計：兩道縫

### 3.1 縫一：`UserDefaults` → `DefaultsStore`

#### 3.1.1 目標形狀（存在型別，非泛型）

```swift
public protocol DefaultsStore: Sendable {
  func object(forKey key: String) -> Any?
  func set(_ value: Any?, forKey key: String)
  func removeObject(forKey key: String)
  func bool(forKey key: String) -> Bool
  func data(forKey key: String) -> Data?
  func dictionaryRepresentation() -> [String: Any]
}
```

**必須可用作存在型別**（`any DefaultsStore`）：協定之 API 面上不得出現 `Self` 或 associated type。此即避開事主所憂之泛型傳染之關鍵。

#### 3.1.2 兩種實作

| 實作 | 用途 | 要點 |
|:--|:--|:--|
| `UserDefaultsStore` | 生產 | 包一顆 `UserDefaults`；`.standard` 與具名 suite 皆可 |
| `InMemoryDefaultsStore` | 測試 | 以 `NSMutex<[String: Any]>` 承載；**零落盤、跨行程天然無互踩** |

#### 3.1.3 「當前 store」之解析點——三個候選與取捨

| 案 | 形狀 | 改動量 | 是否解 (A) | 是否解 (B) |
|:--|:--|:--|:--:|:--:|
| (a) | 保留 `current` 之形，改為 `DefaultsStoreRuntime.current: any DefaultsStore` | 最小（`SwiftFoundationImpl.swift` 一檔 ＋ 各 `UserDefaults.current` 之 21 處呼叫點） | ✓（記憶體實作下亦解跨行程） | ✗ |
| (b) | 將 store 收進 `PrefMgr` **實例**——`@AppProperty` 之 `container` 由 computed 改為 **stored**，於 `PrefMgr_Core.swift` 之 126 處初期化時逐處傳入 | 大（`Shared` 全層 ＋ macOS 側數十個 `PrefMgr.shared` 取用點；且觸 §2.3 第 2 條之兩倉逐位元組同源紀律） | ✓ | ✓ |
| **(c)** | (a) 之形，但 `container` 改 stored、由 `AppProperty(userDef:container:)` 之**預設引數**讀 `DefaultsStoreRuntime.current` | 中（wrapper 一處 ＋ 生產端零改動） | ✓ | ✗ |

**建議 (c)**：生產端不動、測試端只需換 runtime 之當前 store；**將 (b) 留給後續 phase**。(b) 雖是「真解」，但它把本 phase 變成跨倉大遷徙，且與 §2.3 第 2 條之同源紀律正面相撞。

**明確否決**：以 `@TaskLocal` 承載當前 store——`@AppProperty` 之讀寫可發生於任意佇列，而 `TaskLocal` 不跨 `DispatchQueue` 之邊界傳遞。

#### 3.1.4 `pendingUnitTests` 必須與儲存分家

現況 `pendingUnitTests` 一事二職：**（i）「測試中」之事實**（決定用哪顆容器）、**（ii）排程語意**（9 處 `bypassAsync:`、2 處 `asyncLoadingUserData`、1 處日誌靜音）。

(i) 由縫一吸納；(ii) 應析出為獨立之**排程政策**（暫名 `AsyncDispatchPolicy.enabled`／`LXAssembly.asyncLoadingUserData` 之直接供給），其值在測試中由測試自己指定，而非由「有沒有人在跑單元測試」推得。理由：把「當前是否為測試」當成生產語意，會使**測試觀測到之排程行為與生產不同構**，且遮蓋真正的並行缺陷——本 phase 要治的正是這一類。

#### 3.1.5 順帶修復兩處 `.standard` 洩漏

- `PrefMgr_Core.swift:563`：`migrateDeprecatedSettings()` 改讀注入之 store。該函式之「一次性遷移」語意另需一個遷移狀態之抽象（否則遷移測試永遠得碰真機網域）。
- `vChewingLXAssembly_Common.swift:153`：改走與 `Shared.swift:21` 同一判準。
- 兩者之共同收益：**測試行程不再觸碰 `~/Library/Preferences/` 之真機網域**——這才是事主「沙箱測試」一語之實質。

### 3.2 縫二：使用者資料落點 → `UserDataLocator`（語意開關）

#### 3.2.1 何以不以 `FileManager` 為介面

把 `FileManager` 整體協定化是**過度**：熱路徑（trie 載入、CIN 解析、POM 快照）會多一層存在型別派發，而**唯讀資源本無競爭**。應以**語意**為介面——「這一份使用者資料落在哪裡、是否落盤」——而非「檔案系統」。此即事主「以語意來開關」之正解。

#### 3.2.2 目標形狀

```swift
public enum UserDataModule: Sendable {
  case userPhrases, userFilter, userReplacements, userAssociates, userSymbols
  case pomSnapshot, pomJournal, cassette
}

public protocol UserDataLocator: Sendable {
  func dataURL(for module: UserDataModule) -> URL?   // nil ＝ 該模組不落盤
  func exists(at url: URL) -> Bool
  func read(at url: URL) throws -> Data
  func write(_ data: Data, to url: URL) throws
}
```

三態實作：

| 態 | 語意 | 用途 |
|:--|:--|:--|
| `.disk(root: URL)` | 落於指定根目錄 | 生產；亦可供「單一測試獨占一整個目錄」 |
| `.memory` | 記憶體映射 | **沙箱測試**——多個 test case 各持一份，不再共寫同一片硬碟 |
| `.disabled` | 一切寫入為 no-op、一切讀取為空 | 取代現行之 `/dev/null`（`POMIndexedRetrievalTests.swift:12`）與 `filePath = nil` 之雜用 |

#### 3.2.3 落點改法

- §2.6 之五個「字串型別路徑成員」一律改持 `(locator, module)` 之一對，或由 `LXFacade` 供給 `UserDataModule`。
- `LXFacade.swift` 之 8 處 `isReadableFile` → `locator.exists(at:)`。
- `saveData()` 之 `Data.write(to: .atomic)` → `locator.write(_:to:)`。
- `LXPerceptionPersistor` 之快照／日誌／輪替／清理六處 → 同一介面。
- **不動**：`ResourceLocator` 與 `BPMFVS.specifyDataURL` 之既有全域（唯讀資源，「讀哪裡」不構成競爭）。

#### 3.2.4 測試側之可量測收益

- `POMFileHandleTests` 之固定檔名 ＋ `.serialized` **可直接撤**。
- `indexedNullURL` 改 `.disabled`，語意由「靠 `/dev/null` 存在」變為顯式。
- 15 個碰 FS 之測試檔可各用 `.memory`，免 `NSTemporaryDirectory()` 與 `defer { removeItem }`。

### 3.3 兩縫之交會：誰持有

- `PrefMgr`（`Sources/Shared`）持 `any DefaultsStore`（或其解析來源）。
- `LXFacade`（`Sources/LexiconAssembly`）持 `any UserDataLocator`。
- 二者現皆為行程級（`static`／`sharedSansDidSetOps`）。**縫開好之後，才可能把 `LXFacade` 與 `PrefMgr` 降為測試各持一份之實例**——那才是撤 `.serialized` 的充分條件。

---

## 四、被否決之方案

| # | 方案 | 否決理由 |
|:--|:--|:--|
| 1 | 全 `FileSystemProtocol`（把 `FileManager` 整個換掉） | 過度：熱路徑多一層存在型別派發；唯讀資源本無競爭；且會把 `ResourceLocator` 之職責與使用者資料落點混為一談 |
| 2 | `AppProperty<Value, Store>` 之泛型化 | 126 處宣告與其全部消費端型別皆須長出泛型參數；收益為零（本不需編譯期解析）；與事主「最小變更」之原則相牴 |
| 3 | 只把 `unitTests` 之預設 suite 名改成含 UUID | 治跨行程，不治行程內；且**仍落盤、仍是全域**；亦不解 (B) |
| 4 | 只撤 `.serialized` 而保留全域 | 必紅（`LibVanguardTests_Root.swift:12-20` 之實測已載其症狀） |
| 5 | 以 `@TaskLocal` 承載當前 store | `@AppProperty` 之讀寫可發生於任意佇列；`TaskLocal` 不跨 `DispatchQueue` 邊界 |
| 6 | 以 `UserDefaults` 之 `volatileDomain` 替代 | 不解決多行程共寫；且 `volatileDomain` 之寫入需自管 `setVolatileDomain`，語意反而更窄 |
| 7 | 令測試各自 `removeSuite` 後重建 | 已行（P253／P257）且**不夠**——跨行程之競爭與行程內 (B) 類皆未治 |

---

## 五、分期草案（P315 起）

| 期 | 內容 | 完成後可撤之枷鎖 |
|:--|:--|:--|
| **P315** | 縫一之最小可行形：`DefaultsStore` 協定 ＋ `UserDefaultsStore` ＋ `InMemoryDefaultsStore` ＋ `@AppProperty.container` 之注入點（案 (c)）；`SharedTests` 與 `LexiconAssemblyTests` 之 6 檔改注入；`PrefMgr_Core.swift:563` 與 `vChewingLXAssembly_Common.swift:153` 之 `.standard` 收口 | (A) 之儲存面、兩處 `.standard` 洩漏 |
| **P316** | `pendingUnitTests` 之排程語意析出（9 處 `bypassAsync:`、2 處 `asyncLoadingUserData`、1 處日誌靜音） | (A) 之雜用面 |
| **P317** | 縫二：`UserDataLocator` ＋ 三態 ＋ 五個路徑成員收口 ＋ 15 檔測試改用 `.memory`／`.disabled` | (C) |
| **P318** | `LXFacade` 之可變靜態（`factoryTrie`／`lxCassette`／`lxPlainBopomofo`）之實例化 | (B) 之 LexiconAssembly 側 ⇒ 可撤 `LexiconAssemblyTests` 之 32 檔 `.serialized` |
| **P319** | `PrefMgr.sharedSansDidSetOps`／`SessionHost.shared` 之實例化 | (B) 之 Shared／Session 側 ⇒ 可撤 `LibVanguardTests` 之根 suite `.serialized` |
| **P320+** | 實測並撤 `--no-parallel`（`Makefile:157`） | 兩道防線之 CLI 層 |
| **並行可行者** | `HomaTests`／`TrieKitTests`／`BPMFVSTests`／`BrailleSputnikTests`／`ResourceLocatorTests` 之 `.serialized` 撤除（§2.2 判為「零真因」） | (D)——**可立即並行於 P315** |

> **P314 施行後之實際狀態**：上表之 **P315 與 P317 兩期已由 P314 一次完成**（含兩道縫、兩處 `.standard` 收口、POM 五套房改記憶體容器），最末一列「並行可行者」亦已完成。**仍未做者**為 P316（`pendingUnitTests` 之排程語意析出）、P318／P319（類 B 之實例化）、P320+（撤 `--no-parallel`），以及「案 (b) 之逐型別實例注入」——後者因兩道縫之解析點皆為行程級全域，已由可選升為必要。

> **每期之獨立驗收**：該期之目標須能在**不撤任何 `.serialized`** 之下，以 `--filter` 反覆並行跑綠；且該期不得使既有全量基線之支數變動。

---

## 六、驗收判準（如何證明枷鎖已解）

1. `.serialized` 之覆蓋率由 **60／92** 分階段降至 **0／92**（逐期量測、記錄於該期之 Phase 篇）。
2. `swift test`（**不加** `--no-parallel`）連跑 ≥10 次全綠。
3. **兩顆 `swift test`（正本 ＋ macOS 子套件）同時**跑全綠——即推翻 §2.3 第 3 條之禁令。
4. 測試行程**不觸碰** `~/Library/Preferences/` 之真機網域：以 `defaults read` 之前後 diff 為證，或於 `HOME` 重導之下跑。
5. 測試行程於共用 temp 目錄**不留固定檔名之殘留**。

---

## 七、未決之裁定點（須事主裁定）

1. **縫一之解析點**：案 (a)／(c)（全域 runtime，建議）vs 案 (b)（`PrefMgr` 實例持有，跨倉）。後者才真正解 (B)，但須連帶同步 macOS 側。
2. **縫二之命名與粒度**：`UserDataLocator`／`UserDataStore`／`VanguardSandbox`；三態 vs 兩態。
3. **`Shared` 層改動之兩倉同源**：本 phase 是否連帶同步 `vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard`（依 P299 慣例，凡改 `Sources/Shared` 者須同步並逐檔 `diff -q` 複核）。
4. **是否接受「本 phase 不動任何生產碼」之 P301 式定位**（本檔之建議：是）。
5. **P313／P314 之號序**：全倉（含 `Research/`、`Reqs4LLM/`、`DevReqsHistory.md`）經 `grep` 覆核**無 P313 之任何記錄**，事主亦未指派該號；本文照事主指定之 **314** 立篇，P313 之空缺維持不補。

---

## 附錄 A：`Sources/**` 之 47 處 `UserDefaults`

| 檔 | 處 |
|:--|--:|
| `Sources/LibVanguard/Session/SessionProtocol.swift` | 9（全為 `bypassAsync:` 之排程語意） |
| `Sources/Shared/UserDef/UserDef.swift` | 18（`:219`／`:269`／`:277`／`:288`／`:544`／`:555-560`…；全走 `.current`） |
| `Sources/LexiconAssembly/vChewingLXAssembly_Common.swift` | 3（`:150` 日誌靜音、`:153` **`.standard` 洩漏**、`:170` `asyncLoadingUserData`） |
| `Sources/LibVanguard/Session/InputSession.swift` | 2 |
| `Sources/LibVanguard/Session/InputSession_HandleStates.swift` | 2 |
| `Sources/Shared/Shared.swift` | 2（`:18` 測試探測、`:21` `_DebugMode`） |
| `Sources/Shared/IMEApp.swift` | 2 |
| `Sources/Shared/PrefMgr_Core.swift` | 1（`:563` **`.standard` 洩漏**） |
| `Sources/LexiconAssembly/LXFacade.swift` | 1（`:326`） |
| `Sources/LexiconAssembly/SubLMs/LXPerceptor.swift` | 1 |
| `Sources/LibVanguard/Typewriter/Typewriter_MixedAlphanumerical.swift` | 1 |
| `Sources/LibVanguard/InputHandler/InputHandler_TypingMode.swift` | 1 |
| `Sources/LibVanguard/Session/SessionHost.swift` | 1 |
| `Sources/LibVanguard/Session/InputSession_Delegates.swift` | 1 |
| `Sources/LibVanguard/Session/SessionCoreProtocol.swift` | 1 |
| `Sources/LibVanguard/Session/InputSession_HandleEvent.swift` | 1 |
| **合計** | **47**（16 檔） |

另：`Deps/VanguardSwiftExtension/Sources/SwiftExtension/SwiftFoundationImpl.swift` 6 處（`:207`／`:213`／`:218`／`:225`／`:226`／`:251`）；`Tests/**` 43 處（6 檔）。

## 附錄 B：測試目標 × 枷鎖 × 可撤性

| 目標 | A | B | C | D | 期 |
|:--|:--:|:--:|:--:|:--:|:--|
| `LexiconAssemblyTests` | ✓ | ✓ | ✓ | ✓✓（32/33） | P317–P318 |
| `LibVanguardTests` | ✓ | ✓ | ✓ | — | P319 |
| `SharedTests` | ✓ | ✓ | ✓ | — | P315 |
| `TekkonTests` | — | — | △（1 處唯讀 `fileExists`） | ✓✓ | **可並行** |
| `HomaTests` | — | — | — | ✓✓ | **可並行** |
| `TrieKitTests` | — | — | — | ✓✓ | **可並行** |
| `BPMFVSTests` | — | — | — | ✓ | **可並行** |
| `BrailleSputnikTests` | — | — | — | ✓ | **可並行** |
| `ResourceLocatorTests` | — | — | △（自身即測 temp 目錄之建立與複製） | ✓ | 待複核 |
| `ArimitsuTests` | — | — | — | 無 | 已並行 |

## 附錄 C：`Sources/**` 之 FS 落點逐檔

| 檔 | 處 | 行 |
|:--|--:|:--|
| `Sources/LexiconAssembly/LXFacade.swift` | 8 | `:283`／`:300`／`:451`／`:483`／`:520`／`:535`／`:564`／`:598` |
| `Sources/LexiconAssembly/SubLMs/lxPerceptionPersistor.swift` | 6 | `:178`／`:246`／`:358`／`:398`／`:463`／`:564` |
| `Sources/LexiconAssembly/LXConsolidator.swift` | 3 | `:22`／`:59`／`:121` |
| `Sources/LexiconAssembly/SubLMs/lxCassette.swift` | 1 | `:934` |
| `Sources/LexiconAssembly/LXFacade_TextMapExtension.swift` | 1 | `:559` |
| `Sources/ResourceLocator/ResourceLocator.swift` | 2 | `:96`／`:103`（唯讀，不動） |
| `Sources/vChewingSharedCLI/VCSharedCLI_main.swift` | 5 | `:89`／`:154`／`:208`／`:274`／`:339`（CLI，不動） |

另：`Sources/**` 內 `Data(contentsOf:)`／`.write(to:)` 共 17 處；`Tests/**` 內碰 FS 者 15 檔。

## 八、實作結果（2026-10-15 當日施行）

事主於讀畢本稿後指示「你可以手術了，這手術也是 P314」——即不另立 P315，研究與施行同屬 P314。以下是施行後之實際狀態；本節為**唯一之事後記錄**，第二至七節維持研究當時（施行前）之語境。

施行後兩倉提交：`vChewing-LibVanguard` `4103d0b`、`vChewing-macOS` `6f63e0e3`＋`ee15e19d`（均未推送；經事主指示，LibVanguard 倉濃縮為單一提交，macOS 倉則拆為「子套件鏡像」與「消費端」兩筆）。兩倉之 `Sources`／`Tests`／`Deps` 逐位元組相同（`diff -rq` 無差異），`Package.swift` 亦相同。

### 8.1 縫一：`DefaultsStore`

新檔 `Deps/VanguardSwiftExtension/Sources/SwiftExtension/DefaultsStore.swift`：

```swift
public protocol DefaultsStore: AnyObject {
  nonisolated func object(forKey key: String) -> Any?
  nonisolated func set(_ value: Any?, forKey key: String)
  nonisolated func removeObject(forKey key: String)
}
extension DefaultsStore {
  nonisolated public func bool(forKey key: String) -> Bool { (object(forKey: key) as? Bool) ?? false }
}
nonisolated public final class UserDefaultsStore: DefaultsStore, @unchecked Sendable {
  public let defaults: UserDefaults
  public init(_ defaults: UserDefaults) { self.defaults = defaults }
}
nonisolated public final class InMemoryDefaultsStore: DefaultsStore, @unchecked Sendable {
  public init(_ initial: [String: Any] = [:])
  public func removeAll()
  public var sortedKeys: [String]
}
```

三點與本稿 §三 之出入，皆為施行時才顯影之必然：

1. **協定刻意不繼承 `Sendable`**。`object(forKey:)` 回 `Any`，而 `Any` 非 `Sendable` ⇒ 一旦 `DefaultsStore: Sendable`，`InMemoryDefaultsStore` 之 `NSMutex<[String: Any]>` 尚可，惟任何自訂 store 都得自行閃避。改由各實作自行宣告：`UserDefaultsStore`／`InMemoryDefaultsStore` 皆 `@unchecked Sendable`。
2. **`bool(forKey:)` 為協定之預設實作，而非要求**。原稿把它列為要求，但 `UserDefaults.bool(forKey:)` 對「鍵不存在」回 `false`、與預設實作同旨，故降為擴充可減少兩實作之重複。
3. **`data(forKey:)` 與 `dictionaryRepresentation()` 移除**。施行時全倉 `AppProperty` 之 127 個儲存屬性皆為 `Bool`／`Int`／`String`／`Double` 等標量，無一使用 `data` 或整表枚舉；留白比留死代碼好，日後有需再加。

`SwiftFoundationImpl.swift` 之改動：舊 `extension UserDefaults { pendingUnitTests / unitTests / current }`（施行前 `:205-228`）**整塊刪除**（同時滿足 17-WorkDetails-ProcessAndLint.md 之「行程級之系統 API 一律住 `OSUtils`、不得再以 extension 掛在 Foundation 型別上」）；`OSUtils`（同檔 `:29`）內新增：

```swift
nonisolated public static var defaultsStore: any DefaultsStore   // getter/setter 皆走 NSMutex
nonisolated public static var isRunningUnitTests: Bool
nonisolated private static let _defaultsStore: NSMutex<any DefaultsStore> = .init(UserDefaultsStore(.standard))
nonisolated private static let _isRunningUnitTests = NSMutex(false)
```

`AppProperty`（同檔 `:234-260`）僅改一行：`:251` `public var container: UserDefaults { .current }` ⇒ `public var container: any DefaultsStore { OSUtils.defaultsStore }`。**仍是逐次求值、無快取**——這是刻意的：`@AppProperty` 之「換容器即時生效」性質（18-WorkDetails-BuildAndTest.md 之 P253／P257 條目所載）必須保住，否則測試改了 store 卻讀到舊值。

`@AppProperty` 之宣告端**零改動**（127 處一個字都沒動），驗證了 §三 之判斷：泛型不必需。

全倉替換兩組符記（12 檔）：`UserDefaults.pendingUnitTests` → `OSUtils.isRunningUnitTests`（21 處）、`UserDefaults.current` → `OSUtils.defaultsStore`。其中 `Sources/LibVanguard/Session/` 之七檔原本沒有 `import SwiftExtension`（`@_exported import` 只在 `Sources/Shared/Shared.swift`），已補上匯入。

兩處 `.standard` 洩漏收口：`Sources/Shared/PrefMgr_Core.swift:563` `let defaults = UserDefaults.standard` ⇒ `let defaults: any DefaultsStore = OSUtils.defaultsStore`；`Sources/LexiconAssembly/vChewingLXAssembly_Common.swift:153` ⇒ `OSUtils.defaultsStore.object(forKey: "_DebugMode")`。前者即 `PrefMgrFuriousTypingMigrationTests` 那條「本 suite 直接對 `.standard` 佈置與清理」之根；收口後該 suite 之 66 行改動中約 50 行係刪除。

測試側新慣用語（取代 `UserDefaults.unitTests = .init(suiteName:)` ＋ `pendingUnitTests = true` ＋ `removeSuite`）：

```swift
OSUtils.defaultsStore = InMemoryDefaultsStore()
OSUtils.isRunningUnitTests = true
```

### 8.2 縫二：`UserDataLocator`

新檔 `Sources/LexiconAssembly/UserDataLocator.swift`：

```swift
public protocol UserDataLocator: Sendable {
  var isBackedByFileSystem: Bool { get }
  func exists(at url: URL) -> Bool
  func read(at url: URL) throws -> Data
  func write(_ data: Data, to url: URL) throws
  func append(_ data: Data, to url: URL) throws
  func remove(at url: URL) throws
  func byteSize(at url: URL) -> UInt64?
}
```

三實作：`DiskUserDataLocator`（逐項委派 `FileManager.default`／`FileHandle`）、`InMemoryUserDataLocator`（`NSMutex<[URL: Data]>`，`removeAll()`／`sortedPaths`）、`DisabledUserDataLocator`（`isBackedByFileSystem == false`，`exists` 恆 `false`、`read` 拋 `CocoaError(.fileNoSuchFile)`、寫入與移除皆為 no-op）。解析點＝`LXAssembly.userDataLocator`（`nonisolated public static var`，底層 `NSMutex`，預設 `DiskUserDataLocator()`）——即 §七 之案 (c)。

**與原稿 §三 之修訂**：原稿把 `dataURL(for: UserDataModule)` 列為協定要求。施行時確認五個字串路徑成員（`LXCoreEX.filePath`／`LXAssociates.filePath`／`LXReplacements.filePath`／`lxCassette.filePath`／`LXPerceptionPersistor.fileSaveLocationURL`）之**路徑決策早已發生在 `LXFacade` 內**（`:469`／`:501`／`:553`／`:588`／`:616`），成員只負責 I/O。故協定只保留 I/O 六項，`UserDataModule` 與目錄語意**不予引入**——留給真正需要它的生產端（候選：macOS 側之 userDataFolder 設定）。這是本次最重要的一條範圍收斂：縫只要能替換 I/O，就能達成「語意開關」的目的。

新增 `append(_:to:)`（原稿未列）。POM 之 WAL 以 `FileHandle(forWritingTo:)` 追加；若只用 `read`＋`write`，記憶體實作要自行做讀-改-寫，且喪失「追加」之語意。`byteSize(at:)` 同理，供 `shouldCompactJournal` 之 64 KiB 門檻判讀。

改走此縫之生產端落點（`Sources/LexiconAssembly`）：

| 檔 | 改動 |
|:--|:--|
| `LXFacade.swift` | 六處 `FileManager.default.isReadableFile(atPath: path)`（`:451`／`:483`／`:520`／`:535`／`:564`／`:598`）⇒ `LXAssembly.userDataLocator.exists(at:)`。`:283`／`:300` 之 cassette 兩處維持不動（唯讀資源） |
| `SubLMs/lxCoreEX.swift` | `open(_:)` 之 `LXConsolidator` 前置處理加 `if LXAssembly.userDataLocator.isBackedByFileSystem`；`Data(contentsOf:)` ⇒ `read(at:)`；`saveData()` 之 `.write(to:options: .atomic)` ⇒ `write(_:to:)` |
| `SubLMs/lxAssociates.swift` | 同上（含 `open` 之 consolidate 閘） |
| `SubLMs/lxReplacements.swift` | 同上 |
| `vChewingLXAssembly_Common.swift` | `readFileContentAsync` 兩分支：consolidate 加閘、`String(contentsOfFile:encoding:)` ⇒ `String(data: try locator.read(at:), encoding: .utf8)`（解碼失敗時拋既有之 `LXAssembly.FileErrors`） |
| `SubLMs/lxPerceptionPersistor.swift` | 六處 `FileManager.default`（`:178`／`:246`／`:358`／`:398`／`:463`／`:564`）全數改走 locator：存在性、快照讀寫、日誌追加、日誌大小、日誌重播、日誌刪除 |

日誌追加一處值得記：原本逐筆 `fileHandle.write` 後再 `synchronize()`，現在改為先在記憶體組好整批 payload（每筆 `encoder.encode(record)` ＋ `0x0A`）再一次 `append`。磁碟實作之寫入次數因此由 N 降為 1，屬附帶收益。

**磁碟實作在 `write` 時仍用 `.atomic` 與 `FileHandle`**，故磁碟行為與施行前等價（除日誌批次化外）。

### 8.3 測試側

POM 五套房（`POMEncodingTests`／`POMFileHandleTests`／`POMIndexedRetrievalTests`／`POMJournalReplayTests`／`POMLockDisciplineTests`）改裝：各套房之 `init` 設 `LXAssembly.userDataLocator = InMemoryUserDataLocator()`、`deinit` 還原為 `DiskUserDataLocator()`；並以機械替換把

- `try? FileManager.default.removeItem(at: x)` ⇒ `try? LXAssembly.userDataLocator.remove(at: x)`
- `FileManager.default.fileExists(atPath: x.path)` ⇒ `LXAssembly.userDataLocator.exists(at: x)`
- `try Data(contentsOf: x)`（讀回自己剛寫之檔者）⇒ `try LXAssembly.userDataLocator.read(at: x)`

`POMFileHandleTests` 之六個固定檔名（`test_pom_fix.json`／`test_pom_old_format.json`／`test_pom_logging.json`／`test_pom_journal.json`／`test_pom_journal_invalid.json`／`test_pom_journal_corrupt.json`）自此只存在於該測試用例自己的記憶體容器內——**類 C 之實體消失**。`private let nullURL = URL(fileURLWithPath: "/dev/null")` 保留（走磁碟實作，唯讀空檔語意）。

`.serialized` 之撤除：**五個目標、11 檔**。`Tests/BPMFVSTests/BPMFVSTests.swift`、`Tests/BrailleSputnikTests/BrailleSputnikTests.swift`、`Tests/HomaTests/HomaTests_Root.swift`、`Tests/TrieKitTests/` 三檔、`Tests/ResourceLocatorTests/ResourceLocatorTests.swift`。依據為 §附錄 B 之「零真因」判定——此五目標之測試全無 `UserDefaults`／`FileManager`／`.shared` 引用。

### 8.4 驗證

```
cd vChewing-LibVanguard
swift test --disable-sandbox -c debug          # 刻意不帶 --no-parallel
```

**全綠、退出碼 0**：`768 tests in 71 suites`。逐目標：`TrieKitTests` 18 支／3 套 0.027s、`HomaTests` 63／10 4.502s、`TekkonTests` 58／9 8.529s、`SharedTests` 24／3 0.012s、`ResourceLocatorTests` 6／1 0.006s、`LibVanguardTests` 334／6 136.189s、`LexiconAssemblyTests` 220／34 4.461s、`BrailleSputnikTests` 3／1 0.002s、`BPMFVSTests` 7／1 0.472s、`ArimitsuTests` 35／3 0.364s。

注意「不帶 `--no-parallel` 亦全綠」**不等於**「枷鎖已解」：`.serialized` 仍在 `LibVanguardTests` 之根與 `LexiconAssemblyTests` 之 POM 根上，故該兩處仍是序列。這條命令之意義是**無回歸**——施行前後同命令同結果，且新增的五個並行目標亦綠。

建置命令之環境事實：本 shell 內 `swift build`／`swift test` 均須加 `--disable-sandbox`，否則 `sandbox-exec: sandbox_apply: Operation not permitted`；另 `swift test` 即使加 `--disable-sandbox` 仍會印三條 `~/Library/org.swift.swiftpm` 與 `~/Library/Caches/org.swift.swiftpm` 不可寫之警告（不影響結果）。`--cache-path`／`--config-path`／`--security-path` 可用 `.tmp/` 下之目錄消除之。

### 8.5 施行後仍未解者（P315、P316 兩期已施行，此處改記其後之狀態）

1. **類 A／類 B 已除**：類 A（行程級偏好容器）已於 P314 整塊刪除，代之以 `DefaultsStore`；類 B 分兩期收束——P315 把偏好容器與使用者資料 I/O 下推到實例，P316 再把 `LXFacade` 之 `factoryTrie`／`lxCassette`／`lxPlainBopomofo` 收進 `FactoryDictionary`、把 `SessionHost` 立為會話層唯一狀態根。`LibVanguardTests` 之根 suite 與其六個子套房之 `.serialized` 因此於 P316 撤除，全量 **781 支／75 套**全綠（不帶 `--no-parallel`）。
2. **全域解析點仍在，但只管不注入者**：`OSUtils.defaultsStore` 與 `LXAssembly.userDataLocator` 皆保留（生產端無法逐型別注入），未注入者照舊受其管轄。P316 之後另有三處殘餘：`IMEApp.currentInputMode`（`InputSession_Delegates` 之四處 bleach、`IMEStateParsed` 之兩處仍問它；會話層則已改讀 `session.inputMode`）、`LexiconAssemblyTests` 之 137 處靜態呼叫（仍以 `FactoryDictionary.shared` 為域）、以及 `SharedTests` 根之 `.serialized`（其 `init` 之 `CandidateTextService.disableFinalSanityCheck()` 係行程級開關）。
3. **`LXCassette` 與 `LXConsolidator` 未走縫**（原判定：前者唯讀資源、後者職責即就地修整檔案，皆無競爭）——此判定於同日第三波被事主推翻並已補做，見 §十。
4. **`PrefMgr` 已收 `DefaultsStore`**（P315 之 `init(store:)` 逐一套 126 項），惟 `PrefMgrProtocol` 未強制 `store` 出席——此一型別層之強制仍屬未解。

### 8.6 施行後補正：Swift 5.10 工具鏈對等（同日）

6.x 側全綠**不等於** 5.10 可編（此即 18-WorkDetails-BuildAndTest.md 之既有 ★）。本 phase 之首輪建置（`vChewing-LibVanguard` `4103d0b`／`vChewing-macOS` `6f63e0e3` 之前身）正是在此栽了兩處，皆為**只有 legacy 側工具鏈才會現形**的建構，故補記於此：

1. **型別宣告層之 `nonisolated` 是 6.2+ 語法。** 初稿寫的是
   `nonisolated public final class UserDefaultsStore: DefaultsStore, @unchecked Sendable { … }`
   與 `nonisolated public protocol UserDataLocator: Sendable { … }`。Swift 5.10.1 對二者一律以
   `error: 'nonisolated' modifier cannot be applied to this declaration` 拒絕——**protocol 宣告與 class 宣告皆然**；`nonisolated` 只准掛在成員（`func`／`var`／`init`）與 `extension` 內之成員上。此語法差異在 6.4 側完全無徵兆（`-default-isolation MainActor` 之下，型別層 `nonisolated` 是消除「整類被收歸 MainActor」最省事的寫法，故極易寫成習慣）。
   本倉既有之正解有兩式，視情況取用：
   - **成員式**（本 phase 最終採用）：拿掉型別層之 `nonisolated`，改為逐成員標註，`init` 亦須標（不標則 class 之 `init` 仍屬 MainActor，於 `nonisolated` 之靜態初始值裡呼叫會得
     `error: main actor-isolated default value in a nonisolated context`）；儲存屬性若其型別非 `Sendable`（如 `UserDefaults`），須寫 `nonisolated(unsafe)`，否則在預設隔離下仍被收歸 MainActor，與同型別之 `nonisolated` 成員相斥。此式**兩套工具鏈皆通**，且無 `#if` 分岔。
   - **`#if compiler(>=6.2)` 分岔式**：`SwiftFoundationImpl.swift` 之 `NSMutex` 即是——`#if compiler(>=6.2)` 內寫 `nonisolated public final class`、`#else` 內寫不帶修飾詞之同名同內容宣告。代價是整段重複，好處是型別層語意得以保留。新檔宜用成員式，既有檔之修補宜循其原式。

2. **`FileHandle` 之拋錯 API 起自 macOS 10.15.4。** `DiskUserDataLocator.append` 初稿寫 `try fileHandle.close()`／`try fileHandle.seekToEnd()`／`try fileHandle.write(contentsOf: data)`，於 `-Xswiftc -target x86_64-apple-macosx10.9` 下依序得
   `'close()' is only available in macOS 10.15 or newer`、
   `'seekToEnd()' is only available in macOS 10.15.4 or newer`、
   `'write(contentsOf:)' is only available in macOS 10.15.4 or newer`。
   正解是走 `SwiftExtension` 早已為 10.9 鋪好的 `FileHandle` 相容層（`SwiftFoundationImpl.swift:701` 起）：`closeTheFile()`／`seekToEOF()`／`writeData(_:)`（另有 `seek(to:)`／`readToEndOfFile()`）。該相容層以 `if #unavailable(macOS 10.15.4)` 分派，故同一份碼兩側皆可編、亦無 deprecation 警告。**凡新寫之 `FileHandle` 用法，一律先查此相容層有沒有對應名。**

驗證：`swift-5.10.1-RELEASE.xctoolchain` ＋ `MacOSX13.3.sdk` ＋ `-Xswiftc -target x86_64-apple-macosx10.9`，對 `vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard` 分別跑
`swift build --package-path Deps/VanguardSwiftExtension …`（巢狀套件）與 `swift build --package-path . …`（聚合體），二者皆 `Build complete!`、0 筆 `error:`，產物為 `.build/.legacy/x86_64-apple-macosx/debug/libVanguard.a` 與同目錄之 `libVanguardSwiftExtension.a`。此後 6.4 側全量重跑仍為 `768 tests in 71 suites` 全綠。修正已併入同一次提交（`vChewing-LibVanguard` `4103d0b`、`vChewing-macOS` `6f63e0e3`）。

教訓（可移植）：本 phase 新增之兩型別，其「成員多標幾個 `nonisolated`」在 6.x 側看似冗餘，卻是 5.10 側唯一能過的形式；**凡動到模組頂層型別之隔離修飾詞，驗收即須含 5.10 側建置**，否則錯的只有 legacy 分支，且沒有任何 6.x 徵兆。


## 九、消費端之補課（同日第二波）

### 9.1 為何非補不可

縫一刪掉的是**掛在 `UserDefaults` 上之擴充**（`SwiftFoundationImpl.swift` 之 `extension UserDefaults { pendingUnitTests / unitTests / current }`）。正本倉（`vChewing-LibVanguard`）內之呼叫點已於同一提交內改完；但 `vChewing-macOS` 之各套件是**獨立於聚合體**之消費端（`vChewing_MainAssembly4Darwin`、`vChewing_Shared_DarwinImpl`、`vChewing_SettingsUI`、`vChewing_OSFrameworkImpl`、`Sources/vChewingDebuggable`），其呼叫點不在該次提交之射程內 ⇒ 建置即斷。首輪漏改，經事主追問後補（「`vChewing-macOS` 的除了 LibVanguard 以外的部分 你是否忘記做了對應修正？」）。

**教訓**：縫一之「宣告端零改動」只對**經 `@AppProperty` 之宣告**成立；**直接呼叫舊間接層**者不受此保證。凡刪除跨倉共用之擴充，驗收須含消費端建置，不能只看正本倉。

### 9.2 機械改道之實測量

| 原式 | 新式 | 處數 |
|:--|:--|--:|
| `UserDefaults.current` | `OSUtils.defaultsStore` | 36 |
| `UserDefaults.pendingUnitTests` | `OSUtils.isRunningUnitTests` | 36 |
| `UserDefaults.unitTests = .init(suiteName:)` | `OSUtils.defaultsStore = InMemoryDefaultsStore()` | 13 |
| `UserDefaults.unitTests?.removeSuite(named:)` | 整行刪除 | 13 |

落點：`MainAssembly4Darwin` 7 檔（含 2 測試）、`Shared_DarwinImpl` 6 檔（含 3 測試）、`SettingsUI` 8 檔（含 3 測試）、`OSFrameworkImpl` 1 檔、`Debuggable` 1 檔 ＝ 23 檔（＋91／−94）；另 2 檔（`DefaultsStore.swift`／`PrefMgrProtocol.swift`）屬子套件鏡像，與正本倉之 43 檔同額（兩側皆 ＋675／−275，逐位元組相同）。

另一項為 `DefaultsStore` 補齊 `UserDefaults` 之讀取家族：`string(forKey:)`／`array(forKey:)`／`integer(forKey:)`／`double(forKey:)`（皆為協定擴充、`nonisolated`），因 Darwin 側三處直接以該等型別讀偏好（`IMKUtilsImpl` 之 `BasicKeyboardLayout`、`UserDefRenderableCocoa` 之選單勾選、`PhraseEditorUI` 之語系）。

### 9.3 意外現形之真缺陷：`kAppleLanguages` 之空陣列

`UserDef.kAppleLanguages` 之 `dataType` 預設值為 `.arrayOfStrings([])`（`UserDef.swift:696`）——**空陣列**。生產環境之所以讀得到語系，是因為 `UserDefaults` 之網域搜尋**續查全域網域**（`AppleLanguages` 住在 `NSGlobalDomain` 之 `.GlobalPreferences`）。`PrefMgr_Utilities.swift:18` 之 `removeObject(forKey: kAppleLanguages)` 正是此設計之自白：app 刻意不存該鍵，靠系統補值。

`InMemoryDefaultsStore` 沒有這層後援，於是：

- `@AppProperty(userDef: .kAppleLanguages)` 之 `init` 見「鍵不存在」即寫入預設值 `[]`；
- 其後 `array(forKey:)` 回傳**非 nil 之空陣列**（與「無此鍵」不同）；
- 凡 `appleLanguages[0]` 者即 `Fatal error: Index out of range`。

兩處現形（皆在 `vChewing_SettingsUI`）：

- `Sources/SettingsUI/SettingsUI/CtlSettingsUI.swift:126`（`sentenceSeparator` 之 static 初始化）——先崩；
- `Sources/SettingsUI/PhraseEditor/PhraseEditorUI.swift:15`（file-scope `let loc`）——修完前一處後續崩。

判別法（可移植）：`SWIFT_BACKTRACE=enable=yes,threads=crashed swift test … --filter <test>` 可取得具名 backtrace——本 phase 若無此步，`ContiguousArrayBuffer.swift:695` 一行訊息不足以定位到 static 初始化器。

**正解**：`PrefMgrProtocol` 加 `effectiveAppleLanguage`（`appleLanguages.first ?? Locale.preferredLanguages.first ?? "en"`；`import Foundation` 亦須補，該檔原本不 import），六處直取 `[0]` 者（`CtlSettingsUI` 3、`PrefUITabs` 3）一律改道；`PhraseEditorUI` 之 `(... ?? ["auto"])[0]` 改 `.first ?? "auto"`。生產語意不變（非空時逐字相同），空陣列自此有定義。

### 9.4 驗收

| 套件 | 結果 |
|:--|:--|
| `SettingsUITests` | 27 支／5 套全綠（修復前 SIGILL 崩潰） |
| `MainAssembly4DarwinTests` | 29 支／5 套 |
| `Shared_DarwinImplTests` | 15 支／3 套 |
| `CandidateWindow`／`Installer`／`NotifierUI`／`Hoteka`／`Jad`／`OtherIMEDataReader`／`OSFrameworkImpl` | 28／17／15／8／10／6／3 支 |
| `vChewing_OSNeutral_LibVanguard`（鏡像） | 768 支／71 套重跑全綠 |
| 倉根 `swift build` | `Build complete!` |

兩倉鏡像：`Sources`／`Tests`／`Deps` 逐位元組相同（`diff -rq` 無差異、`Package.swift` 亦同）。提交：`vChewing-LibVanguard` `4103d0b`（`effectiveAppleLanguage` 與 `DefaultsStore` 之讀取家族已併入同一提交）、`vChewing-macOS` `ee15e19d`（消費端 23 檔）。

### 9.5 未因而改變者

類 A／類 B 之判定不變：`OSUtils.defaultsStore` 仍是行程級可變全域，故「逐型別實例注入」仍是撤 `LibVanguardTests` 根 suite `.serialized` 之必要條件。本波只是把**消費端**拉回可建置、可測之狀態。

## 十、第三波：卡帶與就地整理器（同日）

### 10.1 為何補做

第二波把使用者資料之讀寫全部改走 `UserDataLocator`，但仍有兩個讀者握著 `FileManager`：`LXCassette.open(_:)` 之 `fileExists` ＋ `FileHandle(forReadingAtPath:)`，與 `LXConsolidator` 之三處（`checkPragma`、`fixEOF`、`consolidate(path:pragma:)`）。原判定是「皆無競爭，不必下推」；事主改判為須一併處理，理由在於**縫之意義是語意可換**，而非僅治競爭——只要有一條路徑仍硬綁硬碟，「整個 LibVanguard 對檔案系統之依賴可以用語意開關」這項目的就只完成了一半。

### 10.2 卡帶：串流與記憶體兩路並存

`LXCassette` 之讀取是串流的（`ByteLineIterator` 逐塊讀），CIN 檔可達數 MB，故不能為走縫而把整個檔案讀進記憶體。解法是給 `ByteLineIterator` 添第二個初期化器：

```swift
nonisolated public init(file: FileHandle, chunkSize: Int = 4_096)
nonisolated public init(data: Data, chunkSize: Int = 4_096)
```

兩者共用同一套斷行掃描與 `harvestLine`，差別只在取塊：類別內新增 `readNextChunk()`，實體檔案走 `fileHandle.read(upTo:)`、記憶體來源走 `Data` 之切片與游標。**串流語意不變**——記憶體模式同樣是逐塊推進，不整檔複製。

`LXCassette.open` 因而分岔：`locator.isBackedByFileSystem` 為真時仍走 `FileHandle`（保住串流），否則走 `locator.read` ＋ `ByteLineIterator(data:)`。

### 10.3 就地整理器：從「改檔案」變成「改位元組」

`LXConsolidator` 原本三函式皆直接 `FileManager`／`FileHandle`：`checkPragma` 以 `FileHandle` 讀前綴、`fixEOF` 以 `attributesOfItem` 取大小再 `seek` 到倒數一位元組、`consolidate(path:)` 以 `Data(contentsOf:)` 讀、`Data.write(to:)` 寫。改道後全部只剩 locator 之四項操作：

| 原實作 | 現行 |
|:--|:--|
| `fileExists` ＋ `FileHandle(forReadingAtPath:)` ＋ 讀前綴 | `locator.read` 後以既有之 `hasIntactPragmaHeader(bytes:)` 判定 |
| `attributesOfItem` 取 `fileSize` ＋ `seek(to: fileSize - 1)` ＋ `readToEndOfFile` | `locator.read` 後看 `data.last`，缺則 `locator.append(Data([0x0A]))` |
| `Data(contentsOf:)` ＋ `Data.write(to:)` | `locator.read` ＋ `locator.write` |

副產物是**程式碼變短且語意更清楚**：`fixEOF` 原本要處理「檔案為空時 `seek` 不可用」之特例，現在 `data.last == nil` 自然落入「缺尾端斷行」，特例消失。

隨之而來的是四個呼叫點之 `isBackedByFileSystem` 閘被撤除（`lxCoreEX`／`lxAssociates`／`lxReplacements`／`readFileContentAsync` 兩份分支）：既然整理器已走縫，記憶體通道亦該得到同樣之標頭與空白正規化，否則「記憶體模式」與「磁碟模式」會給出不同內容——那正是縫最該避免的。

### 10.4 逐次指定之 locator：比全域置換更安全的測試法

第三波一併把 `using locator:` 參數加到四個入口上（`LXCassette.open`、`LXConsolidator.checkPragma`／`fixEOF`／`consolidate(path:pragma:)`），預設值為 `LXAssembly.userDataLocator`。這使測試可以在**不碰行程級全域**的前提下指定自己的容器：

```swift
let locator = InMemoryUserDataLocator()
try locator.write(raw, to: url)
lxCassette.open(pathCINFile, using: locator)   // 全域未被置換
```

此設計直接消解了 §8.5 第 2 條之一半代價：全域仍在，但**新測試不必依賴它**。P314 新增之三個測試用例即以此寫成（卡帶之記憶體載入、`consolidate` 與 `fixEOF` 之記憶體通道），且皆斷言「全程未於硬碟留下檔案」。

### 10.5 驗證

| 項目 | 結果 |
|:--|:--|
| `LXCassetteTests` | 6 支（含新增之記憶體載入）全綠 |
| `LXConsolidatorTests` | 20 支／3 套（含新增之記憶體 `consolidate`／`fixEOF`）全綠 |
| 全量 | **771 支／71 套**全綠（`--no-parallel` **未加**，`LexiconAssemblyTests` 由 220 增至 223） |
| 6.4 側建置 | `Build complete!` |
| 5.10 側建置 | 巢狀套件與聚合體皆 `Build complete!`、0 筆 `error:` |

`ByteLineIterator` 之新初期化器位於 `#if compiler(>=6.2)` 之外（兩分支共用同一份 `Sequence` 擴充），故 legacy 側只須驗證成員式隔離修飾詞即可——與 §8.6 第 1 條同型。

提交（經事主指示，皆以 amend 併入 P314 之既有提交）：`vChewing-LibVanguard` `4103d0b`、`vChewing-macOS` `6f63e0e3`（鏡像）＋`ee15e19d`（消費端）。

## 十一、P315 之界定（為何兩道縫之解析點須另立一期）

### 11.1 判定

**是，須另立一期。** 理由不是「改動行數多」，而是三項**性質**之差異：

1. **它是 API 變更，不是內部改道**。P314 之兩個縫是「新增解析點、既有呼叫端一行不動」；把解析點下推到實例，則 `PrefMgr`／`LXFacade`／`LXPerceptor` 之初期化器要長出新參數，凡是 `PrefMgr()`／`LXFacade(isCHS:)` 之處皆須重新決定「它用哪一顆 store／locator」。
2. **它跨倉且跨共用層**。`Sources/Shared` 之三檔（`UserDef`／`PrefMgrProtocol`／`PrefMgr_Core`）在 `vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard` 有第二份同源副本；`PrefMgr` 是全倉 126 處 `@AppProperty` 之宿主，動它就是動消費端（P314 第二波已演示過：刪一個擴充 ⇒ 23 檔補課）。
3. **它與類 B 糾纏**。`LibVanguardTests` 根 suite 之真因是類 B（`LXFacade.factoryTrie`／`lxCassette`／`PrefMgr.sharedSansDidSetOps`／`SessionHost.shared`），縫之實例化只是**必要條件之一**；單獨完成它並不能撤根 suite 之 `.serialized`。若把三者塞進同一期，驗收會失去「一期一可證」之性質。

### 11.2 建議之切法：兩條獨立軌

| 軌 | 內容 | 完成後可撤 | 風險 |
|:--|:--|:--|:--|
| **A（LexiconAssembly 軌）** | `LXCassette.open(_:using:)`／`LXConsolidator` 之四入口**已備** `using locator:`；本軌只須讓 `LXFacade` 持有 `locator`（預設取全域）並在內部五處路徑賦值與 `LXPerceptor` 建構時下傳；`LXPerceptor`／`PerceptionPersistor` 添 `locator:` 參數（生產端僅 `LXFacade.swift:67` 一處建構點） | POM 五套房之 `.serialized`（不再置換全域） | 低：生產端建構點各一，且 `using locator:` 已存在 |
| **B（Shared 軌）** | `PrefMgr` 添 `init(store: any DefaultsStore = OSUtils.defaultsStore)`，`OSUtils.defaultsStore` 降為「預設值之來源」而非唯一解析點；`SessionHost.prefs` 已是閉包，故測試可直接給自己的 `PrefMgr` 實例 | `SharedTests` 與 `LibVanguardTests` 內「測偏好」之隔離可改為實例持有（仍不足以撤根 suite，見 §11.1 第 3 點） | 中：`Sources/Shared` 兩倉同源、126 處 `@AppProperty` 之宿主 |

軌 A 與軌 B 之間無依賴，可並行或分期；建議先 A（改動面小、且**當期即可用「POM 五套房撤 `.serialized` 後仍全綠」作唯一驗收**）。

### 11.3 驗收（兩軌共通）

- 該期不得使全量基線之支數變動（現為 771 支／71 套）。
- 該期之目標須在**不撤其他任何 `.serialized`** 之下，以「撤掉本期所解之那幾個 `.serialized`」後反覆並行跑綠（`swift test --disable-sandbox -c debug --filter …`，**刻意不加 `--no-parallel`**）。
- 軌 B 須附兩倉 `diff -rq` 之逐位元組同源證明（`Sources`／`Tests`／`Deps`）。

### 11.4 與 P314 之界

P314 交付的是**縫本身**：「有一顆可換的容器」與「有一條可換的資料通道」。P315 交付的是**縫之歸屬**：容器與通道由誰持有。前者已完工並全綠；後者仍是 `LibVanguardTests` 根 suite 與 POM 五套房之唯一障礙，但兩者不可混為一期。

