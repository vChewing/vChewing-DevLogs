# 硬規則與工作細節索引

> 本檔是 `KnowledgeMemo4LLM.md` 全部分卷之**條目級索引**：每一條 durable 規則與工作細節
> 都有一列，並指出它住哪一卷。**開工前整份讀完**——此即「不跳過任何一條」之保證。
> 條目之正文住 `KnowledgeMemo_SubArticles/` 之各分卷；各分卷標題仍保留原節號。

## 一、§12.6 之六個分卷

| 分卷 | 涵蓋 | 條數 |
|---|---|---|
| `16-WorkDetails-L10nAndTerminology.md` | 語系、語體、術語、命名與文案 | 16 |
| `17-WorkDetails-ProcessAndLint.md` | 工作流程、lint／format、提交與產物對帳 | 17 |
| `18-WorkDetails-BuildAndTest.md` | 建置、工具鏈、測試紀律與安裝換檔 | 16 |
| `19-WorkDetails-TypingEngineAndIMK.md` | 輸入引擎、查詢語義、IMK 診斷與狀態護欄 | 29 |
| `20-WorkDetails-DualpinSchema.md` | 雙拼 schema、引擎與其精簡 | 10 |
| `21-WorkDetails-DualpinUI.md` | 雙拼之界面行為、編輯器與偏好槽 | 14 |

## 二、條目

| 條目 | ★ | 所在分卷 | 原行 |
|---|---|---|---|
| - 交差前注意與 L10n 有關的內容是否全部補齊。 |  | `16-WorkDetails-L10nAndTerminology.md` | 625 |
| zh-Hans 之語體一律為「zh-Hans-TW」（臺灣華語、簡體字形）、非大陸普通話 |  | `16-WorkDetails-L10nAndTerminology.md` | 626 |
| zh-Hans-TW 之稽核法 | ★ | `16-WorkDetails-L10nAndTerminology.md` | 627 |
| - **ja：凡指「可交換之配置檔（exchangeable configuration profile／配置包）」此一… |  | `16-WorkDetails-L10nAndTerminology.md` | 628 |
| - **`i18n:Settings.ImportConfigFromClipboard`**（事主 2026-09-2… |  | `16-WorkDetails-L10nAndTerminology.md` | 629 |
| Phase 文書之用語與署名 |  | `16-WorkDetails-L10nAndTerminology.md` | 637 |
| 設定面板之兩側命名與「Section」之形制 |  | `16-WorkDetails-L10nAndTerminology.md` | 641 |
| 「位置即判準」之文案裁定，其護欄必須用 `indexOf(...) === 0` 而非 `>= 0` | ★ | `16-WorkDetails-L10nAndTerminology.md` | 648 |
| 同一件事別在一條偏好字串內說兩次 | ★ | `16-WorkDetails-L10nAndTerminology.md` | 649 |
| 兩軸命名規則 | ★ | `16-WorkDetails-L10nAndTerminology.md` | 657 |
| 文案會隨行為漂移——改動某模式之行為時，同一 phase 內即須回檢其文案 | ★ | `16-WorkDetails-L10nAndTerminology.md` | 658 |
| 窗體縮放動畫期間，繪製之矩形一律取視圖當下之 `bounds`，不得取佈局之終值（`fittingSize`／`metr… | ★ | `16-WorkDetails-L10nAndTerminology.md` | 683 |
| `Arimitsu` 之命名緣起 | ★ | `16-WorkDetails-L10nAndTerminology.md` | 704 |
| Schema 之標題自持 | ★ | `16-WorkDetails-L10nAndTerminology.md` | 706 |
| `String.makeNSLabel(fixWidth:)` 之回傳型別係 `NSLabelView` 而非 `NST… | ★ | `16-WorkDetails-L10nAndTerminology.md` | 726 |
| 後置聲調覆寫之提示字串末尾恆附聲調記號 | ★ | `16-WorkDetails-L10nAndTerminology.md` | 728 |
| - 如果要使用 tmp 目錄的話，請使用**所在倉庫根目錄**的 `tmp/` 或 `.tmp/`（例如 `vChewi… |  | `17-WorkDetails-ProcessAndLint.md` | 630 |
| CI 之豁免：同環境者以本機代跑之 |  | `17-WorkDetails-ProcessAndLint.md` | 631 |
| - 每次交差之前「一次性運行」 `make lintFormatUncommitted` 這一條命令。如果事主明確要你對… |  | `17-WorkDetails-ProcessAndLint.md` | 635 |
| - 給 ChatGPT、Codex、Raptor 的特殊指令：Do not intentionally stop wit… |  | `17-WorkDetails-ProcessAndLint.md` | 636 |
| `make lintFormatUncommitted` 只涵蓋「tracked 且未 commit」之 Swift 檔 |  | `17-WorkDetails-ProcessAndLint.md` | 642 |
| SwiftLint 之「報錯」不是目標——只管「lint → format 依序跑完」的最終結果 | ★ | `17-WorkDetails-ProcessAndLint.md` | 644 |
| 表格類文書之增補紀律：追加列時務必確認「錨點行不含下一節之標題」 | ★ | `17-WorkDetails-ProcessAndLint.md` | 647 |
| 「產物重生」不等於「敘述對帳」 | ★ | `17-WorkDetails-ProcessAndLint.md` | 659 |
| Tekkon 之 documentation 一律自持——不得與具體 commit／phase number／CI 掛勾 | ★ | `17-WorkDetails-ProcessAndLint.md` | 668 |
| 正本之界定：`vChewing-LibVanguard` 才是正本；`TekkonWorkspace` 係「面向單獨的開… | ★ | `17-WorkDetails-ProcessAndLint.md` | 670 |
| 對 LibVanguard package 內之 Tekkon 之修改，一律以「獨立而先行」之 commit 遞交；鏡照… | ★ | `17-WorkDetails-ProcessAndLint.md` | 672 |
| 三語言 Tekkon 之對位只求「行為」一致，不求「內部 helper 表面」一致 | ★ | `17-WorkDetails-ProcessAndLint.md` | 673 |
| 正本側改寫已推送之歷史時，須標明「內容等價（tree 未變）」 | ★ | `17-WorkDetails-ProcessAndLint.md` | 674 |
| dedicated 三倉之版本號與正本非同線 | ★ | `17-WorkDetails-ProcessAndLint.md` | 675 |
| `shortcuts.html` 係產物、不得手改 | ★ | `17-WorkDetails-ProcessAndLint.md` | 682 |
| 行程級之系統 API 一律住 `OSUtils`，不得再以 extension 掛在 Foundation 型別上 | ★ | `17-WorkDetails-ProcessAndLint.md` | 684 |
| 新增 `UserDef`／`KeyboardParser` 成員之 phase 須同 phase 重生兩份導出物 | ★ | `17-WorkDetails-ProcessAndLint.md` | 722 |
| 腳本內的全形字元陷阱 |  | `18-WorkDetails-BuildAndTest.md` | 632 |
| 跨平台 manifest 的 `platforms:` 陷阱 |  | `18-WorkDetails-BuildAndTest.md` | 633 |
| - 如果事主丟給您 Xcode Instruments Profile 檔案的話，可能會是二進位檔案，請先嘗試用 `xc… |  | `18-WorkDetails-BuildAndTest.md` | 634 |
| 回歸測試用例之輸入域必須自資料導出，不得由測試自建 | ★ | `18-WorkDetails-BuildAndTest.md` | 653 |
| 變異測試是判準類測試用例之驗收手段 | ★ | `18-WorkDetails-BuildAndTest.md` | 654 |
| 測偏好之測試用例須自備隔離容器，且不可只清輸入鍵 | ★ | `18-WorkDetails-BuildAndTest.md` | 655 |
| 兩倉同源之子套件：byte-sync 成立即無須重複確認 CI | ★ | `18-WorkDetails-BuildAndTest.md` | 662 |
| 有副作用之輔助函式不得寫進 `#expect` 之運算式 | ★ | `18-WorkDetails-BuildAndTest.md` | 665 |
| `swift build -c release` 建不出 `HomaSharedTestComponents`——任何平… | ★ | `18-WorkDetails-BuildAndTest.md` | 685 |
| iconv 之鏈接處置因平台而異 | ★ | `18-WorkDetails-BuildAndTest.md` | 686 |
| 共用層（`Sources/Shared`）之改動須兩倉同源、逐位元組相同 | ★ | `18-WorkDetails-BuildAndTest.md` | 695 |
| PKG 安裝路徑與 App 安裝器同罪；換檔後之保證刀須以 console user 為界 | ★ | `18-WorkDetails-BuildAndTest.md` | 696 |
| 單元測試不得並行跑兩支 `swift test` 行程 | ★ | `18-WorkDetails-BuildAndTest.md` | 725 |
| 工具鏈對等：6.x 側全綠**不等於**5.10 可編 | ★ | `18-WorkDetails-BuildAndTest.md` | 727 |
| 測試目標之 `.serialized` 分佈與其四類真因 | ★ | `18-WorkDetails-BuildAndTest.md` | 831 |
| 偏好容器與使用者資料 I/O 之兩道縫 | ★ | `18-WorkDetails-BuildAndTest.md` | 832 |
| 判「某模式是否生效」時，凡有第二處就地複製其判定者，即為新增維度時之盲區 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 645 |
| 一個功能「失效」時，先分清「相爭落敗」與「從未執行」 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 646 |
| 紅線之判讀：先讀其自陳之理由，再讀其禁令 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 651 |
| 「閘門變真」不等於「視窗出現」——先查該 UI 的資料由誰供給 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 652 |
| 歸位之判準＝「它讀誰的狀態、誰持有它」 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 656 |
| 以 `rawValue` 查表者，鍵一律不得帶 `k` 前綴 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 660 |
| 功能缺口之歸因須先實測，勿依症狀推論因果 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 661 |
| `partialMatchEnabled` 係全域查詢閘，不得為「只豐富候選窗」而開 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 663 |
| 查詢之回傳序即名次序；陳列之分層留給窗 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 664 |
| 一查詢若由兩分區（原廠／使用者辭典）合成，其匹配語義與呈現順序須逐項對齊 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 666 |
| 「當次推導」之結果不得寫進持久狀態：語境加分只准移動選取、不准記成覆寫種類 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 676 |
| 上下文鞏固保全「值」時亦須保全「詞界」 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 677 |
| 「拼音並擊」之讀音轉換分兩式，不得互換 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 678 |
| 混打之讀音量測不拘狂打開關；顯示路徑不得只讀注拼槽 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 679 |
| 並存態之空白鍵歸屬須有單一正本；Shift+Space 為 ASCII 逃生口 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 680 |
| 「顯示什麼」與「遞交什麼」須由同一取值鏈導出 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 681 |
| IMK 回呼路徑上「查無 session」之分支不得靜默 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 688 |
| 診斷日誌只寫在失敗分支上不足；成功路徑亦須記身分 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 689 |
| `IMKInputSessionController` 之兩條現行行為 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 690 |
| 拼音對照表之方向：key＝拼音、value＝注音——勿信屬性名 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 691 |
| 換裝輸入法時「殺舊行程」須在換檔之後、且須驗證 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 692 |
| IMK 之 Legacy／Modern 分身由 `+subclass` 挑選、與建置 SDK 無關 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 693 |
| 私面干涉之診斷開關須「決策當下求值」、不得快取 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 694 |
| 打字機（Typewriter）可套接：同一 `handler` 上多型別接力 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 700 |
| 中英混輸層僅為注音服務、拼音側不得借道 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 702 |
| POM（`LXPerceptor`）之容量與索引不變量 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 826 |
| 客體顯示刷新與狀態切換之解耦 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 827 |
| 未完成讀音之兩種住所與「先結算、再落本鍵」 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 828 |
| provisional 狀態：客體落筆之延後須住狀態自身 | ★ | `19-WorkDetails-TypingEngineAndIMK.md` | 830 |
| 雙拼類對照表之規則是對「拼音拼寫」作尾綴改寫、不是音位正規化 | ★ | `20-WorkDetails-DualpinSchema.md` | 697 |
| 雙拼之非字母鍵：按鍵碼須以 Apple SDK `HIToolbox/…/Events.h` 為準，不可由 Swift … | ★ | `20-WorkDetails-DualpinSchema.md` | 698 |
| 雙拼零聲母之三族與碼長 | ★ | `20-WorkDetails-DualpinSchema.md` | 701 |
| 雙拼之 autochop 係各家實作之選配、非雙拼之義務 | ★ | `20-WorkDetails-DualpinSchema.md` | 703 |
| 內建方案＝同一 JSON 格式之 decodable schema，其原文固化於原始碼檔尾 | ★ | `20-WorkDetails-DualpinSchema.md` | 705 |
| 雙拼之架構、身分與碼長 | ★ | `20-WorkDetails-DualpinSchema.md` | 707 |
| 雙拼之歸屬、無效序與施工序 | ★ | `20-WorkDetails-DualpinSchema.md` | 708 |
| 雙拼設定界面（macOS 側）之掛載點與三項硬事實 | ★ | `20-WorkDetails-DualpinSchema.md` | 709 |
| 雙拼 schema 之三處精簡 | ★ | `20-WorkDetails-DualpinSchema.md` | 822 |
| 雙拼首鍵之可行性與「死首鍵」之處置 | ★ | `20-WorkDetails-DualpinSchema.md` | 829 |
| 雙拼之排列值域與偏好槽 | ★ | `21-WorkDetails-DualpinUI.md` | 711 |
| E9 之自身豁免 | ★ | `21-WorkDetails-DualpinUI.md` | 712 |
| 雙拼下拉之段落分隔線有**兩處**就地複製 | ★ | `21-WorkDetails-DualpinUI.md` | 713 |
| 雙拼方案匯入之語義 | ★ | `21-WorkDetails-DualpinUI.md` | 714 |
| 雙拼之狂打不另立開關，隨拼音側之狂打開關 | ★ | `21-WorkDetails-DualpinUI.md` | 715 |
| 雙拼之刪除鍵撤銷待配之首鍵 | ★ | `21-WorkDetails-DualpinUI.md` | 716 |
| 雙拼之固化時機隨狂打開關而異 | ★ | `21-WorkDetails-DualpinUI.md` | 717 |
| 雙拼之待配首鍵作廢後必刷新組字區 | ★ | `21-WorkDetails-DualpinUI.md` | 718 |
| 雙拼之無效碼＝Beep＋Drop＋一過性 tooltip | ★ | `21-WorkDetails-DualpinUI.md` | 719 |
| 雙拼 schema 之 `aliases` 係既有欄位，內建七案皆不宣告（收官後兩案亦然） | ★ | `21-WorkDetails-DualpinUI.md` | 720 |
| 雙拼之授權界線：小鶴雙拼（含小鶴音形）無免費授權 | ★ | `21-WorkDetails-DualpinUI.md` | 721 |
| 字面節點之後的數字連打：聲調覆寫不得吞鍵 | ★ | `21-WorkDetails-DualpinUI.md` | 723 |
| 雙拼之退格粒度＝「碼所譯出之整個音節」；狂打之 copilot 窗於首鍵即出 | ★ | `21-WorkDetails-DualpinUI.md` | 724 |
| 雙拼方案編輯器 | ★ | `21-WorkDetails-DualpinUI.md` | 823 |
| 本備忘錄與 `DevReqsHistory`／Reqs 卷之正文，一律以 zh-Hant-TW 書寫 | ★ | `本檔（索引）` | 24 |
| `git push` 為事主之專權——AI Agent 只做到 commit 為止 | ★ | `本檔（索引）` | 25 |
| 術語裁定：「陰平」之英文一律作 `FirstTone`／“First Tone” | ★ | `本檔（索引）` | 28 |
| 術語裁定：漢文正文不再以「靶」稱測試標的 | ★ | `本檔（索引）` | 30 |
| `⌘`／`⌃⌘` 的拉丁字元取決於佈局的 command state | ★ | `09-Features-HotkeysAndRules.md` | 317 |
| WebKit Bugzilla 與 Chromium Buganizer：已發出的訊息（描述與留言）皆不可編輯 | ★ | `09-Features-HotkeysAndRules.md` | 318 |
| 空白鍵可插入內文組字區：`kSpaceKeyBehaviorAgainstICB == -1` | ★ | `09-Features-HotkeysAndRules.md` | 320 |
| 「空格」之術語判準與改名之範圍 | ★ | `09-Features-HotkeysAndRules.md` | 321 |
| LibVanguard 測試之分類與編號新制 | ★ | `11-BuildAndDev.md` | 435 |

（共 111 列；其中 ★ 標記 97 條。§12.6 原 93 條 bullet 全數在此，另含原檔尾之 7 條 ★（其性質同 §12.6）與各卷之 ★ 條。）

## 三、§12.6 以外之 ★ 條目之正文所在

- `本檔（索引）` 之四條住 `../KnowledgeMemo4LLM.md`〈一、開工前必讀之鐵律〉。
- `09-Features-HotkeysAndRules.md` 之四條住同檔之末。
- `11-BuildAndDev.md` 之一條住該檔之 10.3 測試指令節。
