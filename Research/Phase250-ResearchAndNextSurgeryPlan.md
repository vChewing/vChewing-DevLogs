# Phase 250 研究暨後續手術規劃：狂打模式（Furious Typing）之注音化

> **文檔狀態**：研究暨規劃定案。本文即本 phase 之交付物，**不含實作**。
> **用途**：本文為 **Phase 252 起**各施工 phase 之設計依據；各 phase 之施工規格由其在所在卷（Reqs 記錄）內自述，惟凡本文已定案者一律不得於施工中悄然改寫——需改者，於該 phase 之記錄內明寫「與 P250 §X 之出入及其理由」。
> **資料來源**：`vChewing-macOS`（工作區 HEAD）、`vChewing-LibVanguard`、`vChewing-DevLogs` 之**靜態閱讀**，＋ 四項**本機離線實測**（兩倉逐位元組盤點、`UserDef`／`PrefMgr` 全表面清點、狂拼執行期管線全追蹤、Tekkon 動態注音排列與其單元測試資料之量化）。凡屬推論者皆已標註。
> **用詞**：本文稱 macOS 版輸入法為「唯音」、其 IME 進程為「IME 進程」；`UserDef` 之成員稱「偏好鍵」。**狂打**（Furious Typing；ja「狂打ち」）為本模式之總稱；**拼音狂打**（ja「弁音狂打ち」／en「Furious Pinyin」）專指拼音側、**注音狂打**（ja「注音狂打ち」／en「Furious Zhuyin」）專指注音側——**v22 起之新稱謂，舊稱「狂拼」／「狂注」正式停用**（歷史段落保留舊稱謂，換算表見 §1.2）。詳見 §一。
>
> **修訂沿革**：
> - **v1（2026-09-26）**：初稿。曾裁定「注音狂打不開 copilot 窗」，並以「當前內容須為合法完整音節」為自動提交之前提。
> - **v2（2026-09-26，事主覆核後）**：事主指出「注音的狂打模式還是需要 copilot 視窗的，比如打「ㄍㄋㄋ」可以預覽到「幹你娘」」。經實查生產辭典，確認 v1 之設計有**功能缺口**：單聲母縮寫打法（ㄍㄋㄋ、ㄋㄋ…）在 v1 下**完全打不出來**（三顆聲母互搶同一個槽）。**故 §3.0、§3.2、§3.5、§4.2、§八.4、§九 #4／#5b／#5c、§十、§十一 皆已改版**；凡與 §3.0 衝突之文字一律作廢。**改版之淨效果**：自動提交之判準由四條件簡化為三條件、注音狂打接入 copilot 窗體系、`SyllableIndex` 之職責邊界收緊為「只答前綴一問」，並新增 `unfinishedReading` 之分流實作。
> - **v3（2026-09-26，事主修訂 v2 之舉例後）**：事主修訂為「比如打「ㄍㄋㄋ」可以預覽到「幹你娘」「狗男女」」，並追加一項**方針改變**：「那麼注音狂打模式還是屏蔽掉注音文吧。我敲「ㄍㄢˋ-ㄋㄧˇ-ㄋㄧㄤˊ」是能看到有「幹你娘」候選字的。拼音的話可能因為 cartesian product 溢出等原因，敲 gnn 看不到「幹你娘」但能看到「狗男女」。」經以本機生產辭典**逐鍵複查**（結果見 §3.0.1 之 v3 表），確認：① 單聲母縮寫（`ㄍ-ㄋ-ㄋ`）之詞條值**確為字串 `ㄍ`**，**不是**「狗男女」；②「狗男女」之真源是**完整讀音鍵** `ㄍㄡˇ-ㄋㄢˊ-ㄋㄩˇ`（權重 `-6.649`，即該鍵之**唯一且最高**候選），而**拼音之 `gnn` 正是靠 `PinyinTrie` 之前綴展開把 `gnn` 還原成 `ㄍㄡˇ-ㄋㄢˊ-ㄋㄩˇ` 才看得到它**；③「幹你娘」在原廠辭典內**零命中**，其真源為**逐字音節之語言模型組句**（`幹` `ㄍㄢˋ` −5.206／`你` `ㄋㄧˇ` −5.075／`娘` `ㄋㄧㄤˊ` −5.257，且 `ㄍㄢˋ` 起首之鍵有 72 條、`ㄍㄢˋ-ㄋ` 起首者 **0 條**）**或使用者自有詞庫**。**故 v3 之兩項改版**：（a）「注音文抑制」由「注音狂打**不**抑制」改為「**注音狂打亦抑制**」（見 §3.1 第 5 點、§7.4）；（b）§3.0.1 之資料查核全面重做、並新增「`ㄍ-ㄋ-ㄋ` 之類單符號鍵對狂打**並非必要**」之說明；（c）§7.4／§8.5 新增「抑制旗標之落點商榷」一項施工工作。
> - **v4（2026-09-26，事主核定手術節奏後之編號重組）**：事主指示「按照你認為合理的手術順序重組 phase 編號（Phase 251 開始的編號）」，並定調節奏「每完成一個 phase 之後都檢討 Phase 250 做出你認為的必要調整」。**重組要點**：① **插入新的 P251「術前驗證靶」**（零生產碼，先把可實測者實測掉）——理由：本文之全部斷言皆來自唯讀閱讀、未曾編譯或執行，而事主兩次覆核所抓到之錯**兩次都在「由程式碼結構推導、但未實測」那一類**；② 原 P253「FSM 核心」**拆為 P254（閘門收束，行為零變動）＋ P255（自動切音節）＋ P256（copilot 窗）**三個獨立 phase，使「零變動」那一半能單獨取得綠燈；③ 原 P251 之「439 vs 427 對稱性測試」**移入 P251 驗證靶**（先量再建）；④ 原 P254 之「熱鍵查證」**由未決清單移入 P251**（那是我本可在規劃階段就查掉的東西）。**全系列由六個 phase 擴為九個（251–259）**。新增 §8.0.1「phase 收尾之回檢本文程序」，把事主之節奏寫成可執行之三動作。
> - **v5（2026-09-26，**Phase 251 術前驗證靶完工回檢**）**：P251（零生產碼，新增 `Tests/TekkonTests/TekkonTests_AutoChopPredicate.swift`）以 11 個排列、29,579 個合法中途前綴、276,446 個交界之實測，回答了 v4 所定之四項未知，並**推翻了本文之三處斷言**：
> - **v6（2026-09-26，**Phase 252 完工回檢**）**：P252 交付 `Tekkon.SyllableIndex`（新增 `Sources/Tekkon/Tekkon_SyllableIndex.swift` 138 行 ＋ `Tests/TekkonTests/TekkonTests_SyllableIndex.swift` 208 行，兩倉逐位元組相同）。**四項規劃斷言全部成立**（427／442／15 三項數字、以及「以 `mapHanyuPinyin` 之 value 為唯一來源可行且完足」——實測強於預期：素材之 422 條**全部為完整讀音**，不只是「成員或其前綴」）。**三處 API 出入皆為縮小或補明**：① `shared(for parser:)` → `shared(parser:)`（依 §4.3 設計要點 #3「照 `PinyinTrie.shared(parser:)`」，避免 Tekkon 內出現第二種共用存取器標籤風格）；② 另加實例屬性 `readings`（靜態 `allReadings` 為排列中立之正本，實例屬性為本索引持有之表，今日恆等）；③ `completions(of:)` 由 `public` 改為 `internal`（依 §8.3 v5 之裁定）。**一項未預期之查得**：`mapHanyuPinyin` 收有單字母條目 `"q": "ㄑ"`——它是**唯一**之單字母聲母條目（其餘 20 個聲母皆無），且 `"q"` 並非合法之漢語拼音音節（`qi` 才是，且另有條目）⇒ 它使 `ㄑ` 成為唯一擠身「完整單符號讀音」之聲母（24 條中聲母佔 8 而非 7）。**本系列不動它**（移除即改動 `allPossibleReadings`／`PinyinTrie`／單字母 `q` 之 `chop`），僅以測試釘死並列為**獨立事項**。**另新增一項交叉驗證**：37 條單符號前綴恰等於引擎三音素表之聯集。**受修訂之小節**：§0.2（#3 補註）、§4.2（新增單符號結構與 `q` 異常之註）、**§4.3（新增「與本節之出入」表）**、**§8.3（標記完工）**、§9（新增 #14–#16）、§11（新增一則未決事項）。**phase 編號未變**。
> - **v7（2026-09-26，**事主覆核 v6 之 §4.2 註後之更正**）**：v6 曾把 `Tekkon.mapHanyuPinyin["q"] == "ㄑ"` 記為「資料異常」並斷言「對自動切音節判準之影響：無」。事主覆核指出「`mapHanyuPinyin` 不是資料異常——拼音並擊模式需要用這個來轉換顯示」。經逐條複查：**該條目確實不是筆誤**（同四條單字母條目亦被**獨立複製**到 `LexiconAssembly/PinyinPhonaConverter.swift` 之內嵌表 `jsnHanyuPinyinToMPS`，該模組檔頭自陳「使得 LXAssembly 擺脫對 Tekkon 的依賴」），且**「影響：無」為誤**——它使**狂拼模式下 `q`＋`f` 會自動切音節並提交 `ㄑ`**（`b`＋`f` 不會），此即事主所觀察之症狀之機制。**惟「顯示」一節須澄清**：「拼音並擊」（`kShowHanyuPinyinInCompositionBuffer`）之顯示轉換走**方向相反**之 `cnvPhonaToHanyuPinyin` → `arrPhonaToHanyuPinyin`，該表 21 個聲母之單字母條目**齊全**，故顯示不經 `mapHanyuPinyin`。**§4.2 該註已全文改寫**（五段：非筆誤／三條消費路徑／唯一可觀測不對稱／事主期望本即不可得／對注音判準仍無影響），並新增測試 `PinyinSingleLetterEntries_DecodingConsequences` 釘死。**§9 #16 與 §11 #5 隨之改寫**（性質待事主裁定：有意之提供 vs 應予補齊／刪除）。
> - **v8（2026-09-26，**事主裁定刪去 `"q": "ㄑ"` 條目後之回檢**）**：事主覆核後裁定「`"q": "ㄑ"` 去掉吧」，遂自 **`Tekkon.mapHanyuPinyin`（`Tekkon_Constants.swift:357`）與 `LexiconAssembly` 之內嵌表 `jsnHanyuPinyinToMPS`（`PinyinPhonaConverter.swift:64`）兩處同步刪去**。**受影響之四項數字全部更動**：完整讀音 **427 → 426**、嚴格前綴 **15 → 16**（`ㄑ` 由「完整讀音」退回「嚴格前綴」）、單符號完整讀音 **24 → 23**、單符號嚴格前綴 **13 → 14**；**不變者**：全部非空前綴仍為 **442**（`ㄑ` 本來就是 `ㄑㄧ` 一族之前綴）、單符號前綴仍為 **37**、前綴總位元組數仍為 **3,069**。**連帶之資料面事實**：動態排列測試資料之 422 條無調詞幹中，**421 條**為詞幹集之成員，餘下 1 條 `ㄑ` 落於其外——該表收錄它是因為五個動態排列皆能將它編成單鍵、且原廠辭典確有 `ㄑ` 這個單符號詞條，惟它並非漢語音節；此即「音節表 vs 辭典」之職責邊界首次在資料上現形。**未受影響者**：自動切音節判準 v7（只用 `isPrefix`，而 `ㄑ` 無論如何皆為前綴）、以及 §3.2 之全部結論。**另一項收益**：狂拼之**簡拼（α）路徑**於 `q` 起首之緩衝上回復可達（原先被 `q` 觸發之自動切音節搶走；實測 `q`＋任一第二鍵有 24／26 會觸發，而 `b`／`z`／`j` 為 0／26）。**未動者**：`LexiconAssembly/PhonetCipher` 之音素↔ASCII 雙射（`"q": "ㄑ"` 在那裡是結構必需）、`Tekkon_Constants` 之各鍵盤排列表、以及 `arrPhonaToHanyuPinyin`（方向相反之顯示用表，21 個聲母之單字母條目齊全且未動）。**§4.2／§4.3／§8.3／§9 #16／§十一 #5 皆已隨之更正**；三支測試已改為釘住刪除後之契約。
> - **v9（2026-09-26，**Phase 253 完工回檢**）**：P253 交付狂打開關之兩分（`FuriousTypingEnabled` → `…4Pinyin` ＋ `…4Zhuyin`）、Swift 符號全量更名（生產 5 檔 ＋ 測試 141 處）、`migrateDeprecatedSettings()` 之第六段遷移、與 6 支遷移測試。**三項出入**：① **§8.4 之落點清單漏列 `SettingsUI` 之兩處渲染點**——case 更名後該套件無法編譯（實測 `error: type 'UserDef' has no member 'kFuriousTypingEnabled4Pinyin'`）⇒ 納入本 phase（兩處改指 `…4Pinyin`，注音側之第二列仍留 P259）；**§6.2 其實已載「另 `SettingsUI` 2 處」**，只是 §8.4 之摘要漏列。② **§8.4 記「`Sources/LibVanguard/**` 之 5 處引用」，實為 3 行**（1 行 doc comment ＋ 1 行判定 ＋ 其註解延續）。③ **i18n 之分工須調整**：若 `…4Pinyin` 之兩條 i18n 鍵留待 P259，則其**現役渲染點**會在 P253–P259 之間顯示未翻譯之鍵（可見回歸，違反本 phase 之「零行為變動」）⇒ **四語系之兩條 `…4Pinyin` 鍵於本 phase 同輪更名**（文案一字未改）。`…4Zhuyin` 之兩條新鍵**仍留 P259**——因注音側之渲染點要到 P259 才存在，此刻加鍵無消費者。**故 P259 之範圍不變**。**兩項數字更正**：① `UserDef.allCases.count` 之基線為 **117**（非 §8.4 所記之 118）⇒ 動工後為 **119**；② 測試基線為 **607**（非 §8.4 所記之 592——那是 P251 前之陳跡）⇒ 動工後 **613**。**受修訂之小節**：§6.1、§6.2、§8.4、§9、§11。**phase 編號未變**。
> - **v10（2026-09-26，**Phase 254 完工回檢**）**：P254 交付狂打閘門之家族解耦（`TypingMode` 新增 `.zhuyinFuriousTyping`、`typingMode` 改依鍵盤家族二選一、`isFuriousTypingModeEffective` 放寬、新增 `isPinyinFuriousTypingModeEffective`），**行為零變動**（617 支／0 失敗；`LibVanguardTests` 236 → 240，既有 236 支含 67 支狂拼逐支照舊）。**★ 一項紅線措辭之補強**：§8.5 原寫「`isPinyinFamilyTypingMode` **不得**放寬」，**惟「不放寬」在措辭上不足**——該旗子原為 `isComposerUsingPinyin || isFuriousTypingModeEffective`，而自本 phase 起後項亦可能於**注音**注拼槽上成立，**只「不動」則注音狂打一開即令本旗子為真、鍵盤佈局翻譯被跳過、注音完全打不出字**（§10.5 風險 1 之陷阱當場引爆）。故實作**收緊為 `isComposerUsingPinyin` 單一條件**（**等價變換、非放寬**：原析取之右項恆蘊含左項），並以 IH702 釘住。**受修訂之小節**：**§7.2（紅線措辭）**、§8.5（標記完工；落點補 `SessionProtocol.swift:337` 之 i18n 依賴）、**§8.7（P256 新增待辦：`confirmFuriousFrontCandidate` 須支援注音）**、§9（新增裁定）、§11（新增未決項）。**phase 編號未變**。
> - **v11（2026-09-26，**Phase 255 完工回檢**）**：P255 交付注音狂打之自動切音節（§3.2 之 v7 判準逐條移入生產碼）。**三項施工取捨**：① **判準置於 `Tekkon.Composer` 之擴充**而非 `InputHandlerProtocol` 之成員（純函式；回歸靶 30 萬次呼叫可零成本驅動；該擴充住在 `LibVanguard`，不違 §3.3 之紅線）；② **新增辭典閘**（本文 §3.2 未載）：判準可判切於 15 條嚴格前綴（如 `ㄈㄧ`）而辭典內無此讀音 ⇒ 以 `hasGrams` 為閘、回 `nil` 讓本鍵照常入槽（與拼音側政策相同）；③ **靶之語料仍為單一正本**（以 `#filePath` 就地解析，未另抄）。**P251 之靶整組搬入 `LibVanguardTests` 改打生產實作**，其參考實作與原檔**已刪**（杜絕兩份判準各自演化）。**★ 兩類缺陷（皆已修）**：（a）實作——清空注拼槽後即回傳 `true` 使**本鍵憑空消失**（§3.2 原文其實已寫明「然後才把本鍵送入」，是我漏讀；拼音側不需此步之原因見 §8.6）；（b）搬遷——語料解析漏跳表頭列、交界測試漏抄聲調鍵守衛（漏切率虛高至 17.2%，真值 2.19%）。**★ 事主指示**：功能底線原寫「必須能打出『ㄍㄋㄋ』」，惟測試辭典並無單聲母鍵 ⇒ 事主指示「測試用例不一定非得是『ㄍㄋㄋ』，你根據原始測試資料自己製作合理情形」⇒ 撤銷為湊該字串而追加 37 條素材條目之改動，改用素材自身之兩音節詞條造例。**受修訂之小節**：§8.6（標記完工；落點補兩項；測試編號更正為 7 支；功能底線之端到端未驗明列）、§9（新增裁定）、§11（新增未決項）。**phase 編號未變**。
> - **v12（2026-09-26，**Phase 256 完工回檢**）**：P256 交付注音狂打之 copilot 候選窗（「未完成讀音」由拼音專屬升為兩側同構，並使該窗在注音側**真正顯示得出來**）。**★ 兩處規劃錯誤之更正**（皆為本 phase 實作時查得）：① **§3.5 之「`isFuriousCopilotCandidateWindowVisible` 不需改——閘一改即通」為誤**——`State.ofInputting` 起手之 `candidates` 為空（`IMEStateProtocolAndData.swift:48–60`），該狀態之候選只有「狂打前方候選清單」與「磁帶快選」兩個寫入者，而 `isCandidateContainer` 對 `.ofInputting` 之定義即 `!candidates.isEmpty` ⇒ **只改閘門則注音側之窗永遠不會開**（§8.7 之落點清單亦未列 `InputHandler_HandleStates.swift`）。故本 phase 補上缺塊：`furiousFrontContext` 之讀音桶改依注拼槽之鍵盤家族分流（注音側之未完成音節本身即讀音，逕行展開聲調變體）；下游全段為語言中立之鍵值運算、一字未改，注音側因而免費取得置頂組句預覽、跨邊界詞、前方單音節查詢。② **§3.5 之注音分支 `!composer.isEmpty` 過寬**——注拼槽內**只有聲調**時 `isEmpty` 為假而 `getComposition()` 為 `"ˇ"` ⇒ 窗會在無讀音可示時開啟、且讀音桶會由聲調槽生成垃圾鍵。改以 **`isPronounceable`** 為閘，並把「旗子」（`hasFuriousFrontPending`）與「顯示源」（新增 `furiousFrontUnfinishedReading`）**收斂為同一判準**。**三項較規劃更進一步者**：① `unfinishedReading` 之判讀邏輯**上移到 `InputHandlerProtocol`** ⇒ 生產與 mock 只做轉發，同一判準不再有兩份（§8.7 之「mock 與生產須同步」風險由此根治）；② `solidifyFuriousFrontReading` 補注音分支（原 `guard !romaji.isEmpty` 使注音側靜默退回；且 `replacePinyinBuffer` 對非拼音模式是 no-op）——空格／Tab／Enter／標點／方向鍵五個讀取點因而對注音生效；③ `confirmFuriousFrontCandidate` 之注拼槽處理由「以字母流重建」升為**整體快照／還原**（拼音側等價且更忠實，注音側方為可行）。**★ 一項實測查得**：大千排列之 `,` **本身是注音符號鍵（ㄝ）**，故 `,` 走 P255 之自動切音節而**不進標點鏈路**——標點讀取點須以非注音鍵之標點驅動（IH162 已釘）。**既有靶之一支依規劃反轉**：P254 之 IH704 原釘「注音側 `hasFuriousFrontPending` 仍為假（屬 P256）」，本 phase 正是其交付者。**測試基線**：623 → **627 支／0 失敗**（`LibVanguardTests` 251 → 255）。**受修訂之小節**：**§3.5（新增 v12 事實更正段）**、**§8.7（標記完工；落點與完成定義更正）**、§9（新增裁定）、§11（新增未決項）。**phase 編號未變**；P257–P259 之範圍不變（P259 新增一項真機驗收項）。
> - **v13（2026-09-26，**Phase 257 完工回檢**）**：P257 交付**注音文抑制之四態化**——`shouldSuppressFactoryZhuyinwenData` 之語意由「拼音狂拼啟用」改為「**當前打字方式所屬那一側**之狂打開關啟用」（＝§8.8 v5 定案之析取式），即「兩種狂打皆抑制、兩種非狂打皆不抑制」。**§8.8 之判準逐字落地**，三條「可續留 `LexiconAssembly` 側」之理由逐一複驗成立，並補一項實查：熱鍵之動作實為**兩句**——`PrefMgr.shared.pinyinTypingEnabled.toggle()` ＋ `ensureKeyboardParser()`（`IMEMenuSputnik.swift:282–283`）⇒ `pinyinTypingEnabled` 即「使用者所宣告之打字方式」之真源、注拼槽之鍵盤家族係由其**導出**，故本式不依賴二者之先後。**落點之三項出入**：① **`Package.swift` 補 `LexiconAssemblyTests` 對 `Shared` 之直接依賴**（該靶從未 `import Shared`，而本 phase 之驗收必須經偏好；六份 manifest 中只有 `Package.swift` 宣告靶）；② `LXFacade_TextMapExtension.swift` 兩處消費點之註解由「狂拼啟用時」改為「當前打字方式所屬那一側之狂打啟用時」（純註解）；③ **新增一支整合靶 IH705**（`InputHandlerTests_TypingModeGate.swift`）——完成定義 ③ 之「下一拍」在 `LexiconAssemblyTests` 內無法表達（該靶無分診），故補一支以真實 `triageInput` 釘住「切換與分診之間旗標仍為舊值、分診之後即跟上」。**靶之強化**：四態由「四態」擴為 **8 組全枚舉**（旗標 ＋ 查詢結果兩層），熱鍵側則多驗「兩顆鍵盤排列槽一字未動」。**★ 變異測試**（本 phase 之靶是否真能轉紅）：把 `syncPrefs()` 暫時還原為舊式後，兩支既有靶照舊通過（它們直接驅動 config，與本案無關）、**兩支新靶分別轉紅 4 處與 2 處**，驗畢已還原並複驗轉綠 ⇒ 新靶確為交付內容之固化物。**測試基線**：627 → **630 支／0 失敗**（`LexiconAssemblyTests` 201 → 203、`LibVanguardTests` 255 → 256）。**受修訂之小節**：**§8.8（標記完工；落點、判準、完成定義三欄補述）**、§9（新增裁定）、§10.1（LexiconAssembly 一列改為已完成）、§11（新增未決事項：磁帶／SCPC 下本式仍以偏好為準、不以有效模式為準——承前語義，本 phase 未改）。**phase 編號未變**；P259 之範圍不變。
> - **v14（2026-09-26，**P257 追補：事主裁定「磁帶與 SCPC 先不要啟用狂打特性」**）**：事主此裁定結案了 §十一 #16（＝§九 #27）——本式不得以「偏好」為準而讓磁帶／SCPC 取得狂打特性。**追補兩處生產碼**：① 注音文抑制改為**三維合取**（模式 ∧ 該側打字方式 ∧ 該側開關），即 `!prefs.cassetteEnabled && !prefs.useSCPCTypingMode && (pinyinTypingEnabled ? furiousTypingEnabled4Pinyin : furiousTypingEnabled4Zhuyin)`，語意自此為「**狂打確實生效中**」，與 `typingMode` 之定義一致；② **本追補之審計查得**：`performPinyinAutoChopIfNeeded` 原本**沒有任何狂打閘門**（其注音孿生由 `isZhuyinFuriousTypingModeEffective` 把守）⇒ **SCPC 下拼音連打仍會自動切音節**（實測 `gaol` ⇒ `ㄍㄠ` 被切進組字器）——此即裁定所稱「SCPC 下不應啟用的狂打特性」之一，已補 `guard !prefs.useSCPCTypingMode else { return nil }`（磁帶無須設閘：`.cassette` → `CassetteTypewriter`，拼音自動切音節本不在該路徑上）。**審計表**（狂打特性 × 磁帶／SCPC）見 Phase 257 篇 §8.3：十項狂打特性自此於兩模式下**全數 off**。**不受影響**：SCPC 之逐音節選字窗仍由 `composeReadingIfReady` → `handleTypewriterSCPCTasks()` 供應。**刻意未動**：非 SCPC 且 `furiousTypingEnabled4Pinyin = false` 時拼音自動切音節仍照跑——該行為由 `test_IH116B`（標題即「狂打關閉時既有行為不受影響」）釘住，且不在裁定點名之兩模式內 ⇒ **新增未決事項 §十一 #17**。**靶**：真值表由 8 組擴為 **32 組**（新增磁帶 × SCPC 兩維；查詢層之斷言於磁帶下跳過——磁帶查詢走磁帶辭典，此為靶之界線）、**新增 IH706**（SCPC 關 ⇒ `gaol` 切出 `["ㄍㄠ"]`；SCPC 開 ⇒ 組字器空、注拼槽留 `gaol`）。**變異測試**：拿掉模式閘 ⇒ 真值表轉紅；拿掉 SCPC 閘 ⇒ IH706 轉紅 2 處。**測試基線**：630 → **631 支／0 失敗**。**phase 編號未變**（此為 P257 之同日補記）。
> - **v15（2026-09-26，**Phase 259 · Task 1 完工回檢**）**：P259 交付狂打開關之**使用者介面、四語系文案、暨助手防漂移產物之重生**——`kFuriousTypingEnabled4Zhuyin` 自此於設定介面現身，**本系列（P251–P257）之行為首次對使用者可及**（此為本 phase 最重要之副作用：`.zhuyinFuriousTyping` 不再只能靠手改 defaults 或匯入配置包觸及）。落點**全在 `vChewing-macOS` 倉**（13 檔）：`VwrSettingsPaneBehavior.swift`／`VwrSettingsPaneCocoaBehavior.swift`（兩列同 Section，**不做 UI 層之連動停用**——二者係並行選項）、四語系 `Localizable.strings`（各 ＋3 條）、助手之 `src/questions.ts`（種子鍵清單之舊名 → 兩新鍵）、`tests/metadata.test.js`（`count` 118 → 119）、`assets/{userdef-metadata.json,settings-surface.json}`（重生：119／108）、`tests/fixtures/{kimo-zhuyin,msnewphonetic-scpc,pinyin-newbie}.json`（重生：`FuriousTypingEnabled` → `…4Pinyin` ＋ `…4Zhuyin`）。**★ 文案定稿與 §7.5 草案之三項出入**（皆因草案寫在行為落地之前）：①「本模式**不會**過濾注音文」→ P257 已定案兩種狂打皆抑制，故改為「會過濾掉原廠辭典內的注音文」；②「**不會**以語言模型試算未完成的讀音」→ P256 已交付 copilot 窗，故刪去並改為「未完成的讀音會由候選窗即時預覽、可循「Shift+選字鍵」就地選字」；③ 補明空格（插入讀音）／Enter（僅固化）之語義。並依 §8.10.1 明示單聲母可用（「只敲聲母亦可（例如 ㄍㄋㄋ、ㄋㄋ…）」）。**★ 清償 P253 之三項助手漂移**（metadata／surface／fixtures 皆仍帶舊鍵名 `FuriousTypingEnabled`——它們在 P253 時不在該 phase 之完成定義內）；重生順序照 `Makefile` 之依賴鏈 `metadata-update` → `surface` → `fixtures`。**一項刻意未改**：en 之拼音行內提示仍為 "Furious Typing"（§8.10.1 之 i18n 清單只列新增 3 條）。**驗證**：助手 `make audit` **exit 0**（`test` 78 支／全過；四道防漂移全綠）、`Packages/vChewing_SettingsUI` 之 `swift test` **19 支／4 套／0 失敗**（含 4 支契約靶）、倉根 `swift build` ⇒ `Build complete!`、四語系**各 619 鍵且鍵集相同**、`LocalizableFileSorter.swift` **二次執行逐位元組不變**。**I2 為空操作**：本 phase 未動聚合體套件之任何受版控檔（助手之 `metadata-update` 只在該目錄產生未受版控之 `.build`）⇒ `vChewing-LibVanguard` 倉本 phase `git status` 為空。**受修訂之小節**：**§8.10.1（標記完工；落點、文案、可達性三處補述）**、§9（新增裁定）、§11（#7 結案）。**phase 編號未變**；P259 之範圍不變，惟其真機驗收項自此以「使用者已於偏好面板開啟該開關」為前提。
> - **v16（2026-09-26，**Phase 259 · Task 2 完工回檢＝全系列收束**）**：P259 為 **Phase 251–259 之收尾**，**零生產碼改動**。**完成定義六項全數成立**：① 跨倉逐位元組總驗——兩倉**各 220 檔、逐檔 SHA-256 全同**，六份 manifest ＋ `makefile` 之 `cmp` 8/8 `same`，`diff -rq` × {`Sources`,`Tests`,`Deps`} **0 行差異**（僅 `.DS_Store` 與未受版控之 `Deps/VanguardSwiftExtension/.build`）；② 兩倉 `swift test` **各自單獨跑**、各 **631 支／0 失敗**、exit 0；③ 可建置性——`make build510` 於聚合體與 `SettingsUI` **兩套件**皆過（**惟本機 harness 之檔案沙箱會擋掉 SwiftPM 編譯 manifest 的 `sandbox-exec`，須手動補 `--disable-sandbox`；此為環境事項，事主在未加該旗標下跑過 `make DebugLegacy`／`ReleaseLegacy` 即為反證**），legacy 路徑由**事主實測**通過、本 phase 對其產物做獨立複驗（universal `x86_64+arm64`；x86_64 `minos 10.9`／`sdk 13.3`、arm64 `minos 11.0`／`sdk 13.3`；兩份 `Info.plist` 之 `LSMinimumSystemVersion` 皆 10.9；辭典資產確實注入 SPM 資源 bundle；**產物時刻 16:30:37／16:30:39 晚於 P259 之提交 16:22:20／16:22:24 ⇒ 涵蓋 P251–P259 全部改動**）；④ 助手 `make audit` exit 0（78 支／全過）；⑤ 文書三件套（本卷 9 篇、`DevReqsHistory` 9 列、`KnowledgeMemo` 9 則）＋ **`AGENTS.md` 實查無過時敘述故未改**；⑥ 真機項收攏為 **11 項清單**（含 P259 起之新前提：可於偏好面板開啟，不必再手改 defaults）。**全系列測試基線**：**592 → 631（＋39）**；`LibVanguardTests` 236 → **257**、`LexiconAssemblyTests` 201 → 203、`TekkonTests` 58 → 53。**受修訂之小節**：**§8.10.2（標記完工；完成定義三項之實測值；新增 legacy 產物複驗表）**、§9（新增裁定）、§11（#1／#6 收束、#9／#14 收攏）。**本系列於此收束，無後續 phase 待排**；三項移交＝真機驗收 11 項（事主）、`vChewing-VanguardLexicon` 之注音文正本（另倉另立 phase）、iOS 移植（另立 phase）。
> - **v17（2026-09-26，**事主實機發現兩項 ⇒ 新開 Phase 258（Task 1）；術前實測已完成**）**：事主報告兩事並自陳「也可能是我歸因有誤」⇒ 本 phase 先實測後設計。**五支臨時探針（跑畢已刪）之結論**：**空格一事成立且已量化**——令去聲候選 −0.1、陰平 −9 之測資下：注音狂打＋空格 ⇒ 得去聲「號」；非狂打＋空格 ⇒ 得陰平「高」（狂打之固化插入的是**無調讀音桶**，故陰平無法被指定）；成因即 P256 把拼音側「空格＝無調確認組字」整組搬到注音側，而注音之空格本為陰平鍵（大千之五聲調鍵＝`3`／`4`／`6`／`7`／空格）。**「單注音插入組字器阻礙簡拼」之歸因則不成立**——`abbreviatedWordCandidates(keysChopped:)` 對單注音 cell 逐位置 byte 前綴匹配（單次有界 Trie 查詢、無展開表、無笛卡爾積），且「組字器尾段之單注音鍵 ＋ 注拼槽之待確認音節」恰可還原出完整 cells（實測：`ess` ⇒ cells `["ㄍ","ㄋ","ㄋ"]` ⇒ 查得 `["狗男女","幹你娘"]`）；真正的缺口是**注音側從未呼叫該 API**（P256 之注音分支只由當前音節之聲調變體桶產生候選，故 `ㄍㄋㄋ` 之窗只見 `["ㄋ"]`）。**故本 phase 不動單注音之輸入能力**（其插入語義照舊），改為兩項：① **空格還原為陰平鍵**（注音狂打之固化觸發集合移除 `isSpace`；固化另有 Tab／Enter／標點三條路，已實測其足）；② **注音簡拼**（於 `furiousFrontContext` 併入簡拼整詞候選；cells ＝ 組字器尾段之單注音鍵（有界 ≤ 4）＋注拼槽之當前讀音；**不新增狀態、不動 `furiousTrail`**）。**受影響之既有靶**：IH162 之「空格臂」（其原文釘住 P256 之過寬語義）須依本 phase 改寫；IH155（三鍵）與 IH163（注音不寫 trail）**照舊**。**待事主一句話即可施工**。詳見 §8.9.1。
> - **v18（2026-09-26，**Phase 258 · Task 1 完工回檢**）**：P258 交付**注音簡拼**與**空格／陰平之校正**。**空格**：注音之五聲調鍵為 `3`／`4`／`6`／`7` 與**空格**（陰平），而 P256 把拼音側「空格＝無調確認組字」整組搬來 ⇒ 狂打下按空格所得為**無調桶**、陰平無從指定（實測：同一測資下去聲 −0.1 必勝陰平 −9）。修法為「注音側之空格不屬固化觸發集合」（拼音側語義不變）；固化另有 Tab／Enter／標點三條路（實測其足）。**注音簡拼**：cells ＝「組字器尾段之單注音鍵（至多 3）＋ 注拼槽之當前讀音」，經既有 `abbreviatedWordCandidates(keysChopped:)`（逐位置 byte 前綴、單次有界 Trie 查詢）產生整詞候選、併入 copilot 窗（與前方候選同一清單）；**不新增狀態、不動 `furiousTrail`**（P255 之 IH163 照舊）、**亦不移除單注音之輸入能力**（事主之歸因不成立；P255 之 IH155 照舊）。**★ 施工查得（規劃書未載）**：`Homa.Assembler.overrideCandidateAgainst` 之守衛要求目標節點**已含**該 keyArray（`allActualKeyArraysCached.contains(keyArray)`），而簡拼時組字器之鍵鏈是**單注音**（`ㄍ`、`ㄋ`）而非該詞之讀音 ⇒ 「只補插尾段讀音再覆寫」之作法必然靜默落空（實測顯示成「ㄍㄋ女」）。**正解為「先 `dropKey` 移除尾段單注音鍵、再把該詞之讀音整段插入」**——鍵鏈因而恰為該詞之讀音，語言模組方得建立節點。**靶**：＋IH166（cells 之還原與三條界線）／IH167（整詞候選與就地選字）；IH162 之空格臂改寫為「空格＝陰平、且陰平須確實被選用」（其餘四臂照舊）。**變異測試**：拿掉空格閘 ⇒ IH162 轉紅 2 處（鍵變 `["ㄍㄠˋ"]`、顯示變「去聲測」——正是事主所述症狀）；拿掉簡拼併入 ⇒ IH167 轉紅（窗內僅餘 `["ㄋ"]`——正是 P258 前之實況）。**測試基線**：631 → **633 支／0 失敗**（`LibVanguardTests` 257 → 259）；兩倉 byte-sync 零差異、鏡像側獨立複跑同為 633 支。**受修訂之小節**：**§8.9.1（標記完工；依事主裁定移除「另立簡拼緩衝」之替代路線；新增 §8.9.1.6 施工查得）**、§9、§11。**無後續 phase 待排**；P259 之真機清單新增一項（簡拼於原廠辭典下能否給出「狗男女」）。
> - **v19（2026-09-26，**Phase 258 · Task 2 完工回檢＝copilot 窗排序**）**：事主以實機截圖指示「把單獨輸入的注音在 copilot 選字窗的優先權降低。或者說讓長詞更優先」。**診斷**：窗內第 1 名並非真詞，而是**待確認音節之讀音原字串回退值**（語言模組對該讀音查無詞條時，組句退回讀音原文）——`furiousFrontContext.preview` 原被**無條件置頂** ⇒ 三音節之真詞（狗男女／姑奶奶／告奶奶，即 P258 之簡拼候選）恆被壓於其下。**修法兩處**：① **置頂判定收緊**為「預覽值是否落在前方讀音桶內」——落在桶內者為讀音原文、不置頂，改降級入 `ranked`（權重取地板值 `rawReadingFallbackWeight` ＝ −1e9，故沉於同長度之真詞之後，但**仍保留於清單內**可供顯式選取）；② **★ 排序鍵須以「段數」而非 `keyArray.count` 為準**——初版只改 ①，結果降級項之 `keyArray` 是**前方讀音桶本身**（5 個元素）而**躍居首位**（實測 `["ㄋ","狗男女"]` 不變）；桶釘候選代表**一個**位置，此為 `applyFuriousFrontCandidate` 早已註明之 `isBucketPinned` 語義，本 phase 只是補進排序處（`effectiveSegmentCount`）。**與 P258 之關係**：P258 令簡拼候選**進得了**窗，本 phase 令其**排得上**位——二者合起來方為事主原始用例之完整交付。**靶**：IH167 增補「真詞須居首」之斷言（其變異測試之紅即事主截圖之順序）。**基線**：633 → **633 支／0 失敗**（只強化既有靶、未新增靶）。**無後續 phase 待排**；P259 真機清單中「簡拼候選排序觀感」一項之判準因而明確化。詳見 §8.9.2。
> - **v20（2026-09-26，**Phase 259 · Task 3 完工回檢＝UI 文案之對帳**）**：事主於實機複驗 P258 之兩項手術無誤後指示「再檢討各種 UI 文案、確保 description 描述準確」。**審計結果：全系列唯有 `i18n:UserDef.kFuriousTypingEnabled4Zhuyin.description` 一項不準確**（四語系各一條），且係**兩處**、皆因 P259 撰寫該稿時所據之行為已被 P258 改變：① 原文「按空格會將該音節插入組字器（不再兼任候選輪替）」——**P258 已令空格在注音側仍是陰平鍵**，固化改由 Tab／Enter／標點承擔；② 原文「這類以單一注音符號為音節的縮寫打法」——**P258 已改其語義**：連續之單注音不再被視為各自成音節，而是被當作**簡拼**（候選窗列整詞候選、長詞優先，如 ㄍㄋㄋ ⇒「狗男女」）。**定稿**已就兩處改寫（zh-Hant／zh-Hans 用「簡拼」、ja 用「略打ち」、en 用 "shorthand"）。**其餘一字未動**：拼音側之 `description`（逐句實查與實作相符——P258 只改了注音側之空格語義）、兩條行內模式提示、助手側全部文案（其題目與說明悉數取自 `userdef-metadata.json`，修正上游即自動跟上）。**驗證**：助手 `make audit` exit 0（78 支／全過、`missingI18nKeys` 與 `pendingMetadataKeys` 皆 `[]`）、`SettingsUI` 19 支／4 套／0 失敗、四語系**各 619 鍵且鍵集逐項相同**、`LocalizableFileSorter` 二次執行 sha256 不變；助手產物**僅 `userdef-metadata.json` 變更**（未增刪鍵 ⇒ surface 與 fixtures 不變）。**I2 為空操作**（未動聚合體套件）。**（同日之再修訂，以 amend 併入）**：事主另定兩條 `description` 之首句——狂注「**本開關是為了方便需要以不完整的讀音連續進行注音打字的使用者**」、狂拼「**本開關是為了方便需要以不完整的讀音連續進行拼音打字的使用者**」；狂注**移除 iOS 之提及**；狂拼**補上**「本模式會過濾掉原廠辭典內的注音文（注音符號字串）資料」（此為 P257 之交付行為、其舊稿從未載明 ⇒ 屬準確性之補正）。連帶刪去狂拼舊句中之「智能狂拼（ChineseStar）／搜狗拼音（Sogou）」指涉。詳見 §8.10.3 與 `Reqs_0251-0260.md` 之 Phase 259 篇 §六。
> - **v21（2026-09-26，**Phase 259 · Task 4 完工回檢＝助手後設資料機制之查核 ＋ presets 之狂打開關定值**）**：**① 機制查核（事主之提問）**：助手之 `assets/userdef-metadata.json` **未壞**——`metadata` ＝**檢查**（重新導出後 `cmp`，失敗即 `exit 1` 並印漂移訊息）、`metadata-update` ＝**寫入**，而 `audit` 含前者 ⇒ **該體系本即「亮紅燈」而非「自動改寫」**（`README.md` §六自陳）；**無任何 target／hook／CI 會自動跑 `metadata-update`**（倉根 Makefile 明文不呼叫該目錄、pre-commit 只做完整性檢查）⇒ 紅燈只在有人跑助手之 audit 時亮。**變異測試**證明該絆線有效（暫改資產 ⇒ `make metadata` exit 2 ＋漂移訊息）。**順帶查出並修正 README 之三個過期數字**（118 → **119** 條偏好鍵、17 → **28** 條 extra 標籤、78 → **79** 支測試）——**「產物重生」不等於「敘述對帳」**。**② presets 調整（事主裁定）**：注音各方案**刻意關閉狂注**（該模式非為桌面電腦而設）、拼音各方案**刻意開啟狂拼**。**關鍵機制**：起始配置之鍵全集由 `starterUniverse()` 產生，其過濾條件為「該題在任何 profile 下有推薦值」⇒ **兩顆狂打開關先前沒有任何推薦值、根本不在全集內、起始配置從不寫它們**（實測：`starter-macoszhuyin.json` 原為 **16** 鍵、兩鍵皆不在其中）⇒ 已自行開啟狂注之注音使用者，匯入任何注音配置都不會被糾正——此即事主所指之缺口。**實作**：`recommendationFor` 新增兩案（`4Zhuyin`：typing `zhuyin`／`zhuyinmix`／`scpc` ＋ 八個注音系 origin ⇒ `false`；`4Pinyin`：typing／origin `pinyin` ⇒ `true`）。**兩者之值皆等於各自之出廠預設** ⇒ 此為策展紀律①「值等於出廠預設者不收」之**經核定例外**（事主之「刻意」即此意）：**指名寫入之意義不在值、而在「主動覆蓋」**。**效果**：全集 16 → **18** 鍵；起始配置之契約樣本＋該兩鍵；其餘四份 fixture 值不變（僅指名／回歸之歸屬改變）；題庫之該兩題自此於注音方案顯示「關閉（推薦值）」。**新增靶 1 支**（「狂打開關之逐方案定值」；施工中之一項自我修正：初稿斷言「拼音方案下狂注鍵不得被指名」係**錯的**——`{macoszhuyin, pinyin}` 會由來源級指名之，值仍為 `false`、合乎裁定 ⇒ **修靶而非修實作**）。**驗證**：助手 `make audit` exit 0（**79 支**／全過；surface 108 無漂移）、`SettingsUI` 19 支／4 套／0 失敗；**I2 空操作**。**受修訂之小節**：**§8.10.4（新增）**、**§10.2（測試支數 78 → 79）**、§9、§11（新增兩項）。**無後續 phase 待排**。
> - **v22（2026-09-26，**Phase 259 · Task 5 完工回檢＝術語統一 ＋ 助手之三項來源裁定**）**：**① 術語統一（事主裁定）**：「狂注 → **注音狂打／注音狂打ち／Furious Zhuyin**；狂拼 → **拼音狂打／弁音狂打ち／Furious Pinyin**。**此前的功能稱謂正式停用。**」⇒ **§1.2 全面改版**（新表 ＋ 停用範圍之明示）、文首〈用詞〉行隨之改寫；**四語系 `.strings` 之六條 × 四語系一字不留舊稱謂**（行內模式提示 ×2、兩鍵之 `shortTitle`、以及兩條 `description` 內之舊稱謂引用），並新增**術語護欄**——助手之 `metadata.test.js` 斷言「舊稱謂不得出現於任何標籤」＋「新稱謂須在位」（後設資料係由 `.strings` 導出，故此護欄即四語系之固化物）。**歷史記錄保留舊稱謂**（含事主原文之逐字引用，改之即偽造引文）。**② 助手之三項來源裁定**：**CIN** 來源無須調整（維持不指名）；**newbie**（全新使用者）現階段**刻意停用**狂打特性 ⇒ 為此新增 **`ORIGIN_VETOED_KEYS`（來源級否決）**——因本檔之推薦序為「打字方式 ＞ 來源」，而「來源 × **任何**打字方式」之合取條件無從以既有兩表表達（`4Pinyin` 之一般規則為「拼音方案刻意開啟」，而 newbie 須否決之）；其固化物為 `pinyin-newbie.json` 之 `FuriousTypingEnabled4Pinyin` **true → false**；**GoingIME** 係自然輸入法（主推**許氏**注音佈局），**並非**兼有兩派 ⇒ 歸注音系為正解、**P259 記錄中「實務上兼有兩派」之記述為誤（已於 P259 更正）**。**驗證**：助手 `make test` **81 支／全過**（79 → 81）、`make audit` exit 0（surface 108 無漂移）、`SettingsUI` 19 支／4 套／0 失敗；**I2 空操作**。**受修訂之小節**：**§1.2（全面改版）**、文首〈用詞〉、**§8.10.5（新增）**、§9、§11（#21／#22 結案）。
> - **v23（2026-09-26，**Phase 258 · Task 3 完工回檢＝中英混合輸入回退對注音狂打之否決**）**：事主實機回報「**注音狂打開啟之後，注音之中英混合輸入回退失效**」。**根因**：`typingMode`（P254 之閘門收束）之判定**只問狂打開關**，回退旗標不在其視野內 ⇒ ASCII 按鍵悉數派給狂打的打字機、`MixedAlphanumericalTypewriter` **連建構都沒發生**——「回退失效」之實情是「回退整條路徑不存在」。**裁定**（事主）：「如果中英文輸入回退有被啟用的話，哪怕注音狂打模式開關有開啟，注音狂打模式也得被 InputHandler／Typewriter 認為是關閉的。」**實作**：否決置於 `typingMode` 之**注音臂**（`&& !prefs.mixedAlphanumericalEnabled`，生產碼 1 行）⇒ 全部狂打閘門、`handleComposition` 之分派、行內模式提示**自動**跟上且按鍵自動改走 `MixedAlphanumericalTypewriter`。**★ 施工查得**：模式判定在 `LexiconAssembly/LXFacade.syncPrefs()` 另有一份**就地複製品**（注音文抑制旗標之語意即「狂打確實生效中」），須同步補同一維度——否則出現「模式非狂打、抑制卻仍開」之**第五態**，違反 P257 之四態裁定。**拼音側刻意不否決**（回退本即注音鍵盤專屬；連帶否決會令注音時期遺留該偏好、其後改用拼音者無故失去狂拼）。**靶**：＋IH168（旗標層 ＋ **行為層之 ASCII 遞交**）、`LexiconAssemblyTests` 之真值表維度 5 → 6（32 → 64 組）；**變異測試**證明有效（拿掉否決 ⇒ IH168 轉紅 4 處，含行為層）。**文案**：四語系各 2 條 `description` 補上優先權之敘述（不新增 UI 連動停用）。**基線**：633 → **634 支／0 失敗**（兩倉同值）。**順帶修復**：本文 **§九／§十一 之表格遭空行切斷**、且 `## 十、驗證要求` 與 `### 10.1` 兩個標題**被黏進表格列**（歷次增補所遺留之結構缺陷，已重建；掃描複驗 0 處可疑）。**受修訂之小節**：**§8.9.3（新增）**、**§2.1**、**§7.1**、**§7.4**、**§10.1**、**§10.4**、§9、§11。**無後續 phase 待排**。
> - **v24（2026-09-26，**Phase 259 · Task 6 完工回檢＝注音狂打警示之置首**）**：事主裁定「`kFuriousTypingEnabled4Zhuyin` 的 description 得在**最開頭**就顯示『⚠︎ 該模式無法在中英文輸入回退模式啟用時起作用。』＋換行，因為插在其他位置的話不醒目」⇒ 四語系之該條 `description` 首行插入該警示（`⚠︎` ＝ U+26A0 ＋ U+FE0E、其後一個半形空格、其後 `\n`），並**移除 P258 加在句中**的那一句（同一件事在一條字串內說兩次既冗餘、又會出現兩種稱謂）⇒ 該條字串內之警告自此**只有一處、且在最前**。**事主隨即更正其措辭**（原文之「中英文輸入回退模式」為筆誤）：「**還得是「中英混合輸入回退」**」⇒ zh-Hant／zh-Hans 之首行改用該偏好 `shortTitle` 之正式稱謂（ja／en 原即用其對位之正式稱謂，不動）⇒ 四語系之首行與各自之 `shortTitle` 用語一致，先前的「刻意不對稱」**不復存在**。**處置**：本 phase 之兩份 commit（`vChewing-macOS` 與本倉）皆以 **amend** 併入，未另立 phase。**新增護欄**：助手 `metadata.test.js` 驗四語系之 `description` **以 `⚠︎` 開頭且含換行**——**位置即判準**，故斷言取 `indexOf(MARK) === 0`（只驗「在不在」守不住本裁定）；**變異測試**：把警示移到句末 ⇒ 轉紅。**基線**：助手 81 → **82 支／全過**；`make audit` exit 0、`SettingsUI` 19／4／0；**I2 空操作**（未動聚合體套件）。**受修訂之小節**：**§8.10.6（新增）**、**§10.2**（81 → 82）、§8.9.3（補一筆指向 §8.10.6）、§9（#43）。**無後續 phase 待排**。
> - **v25（2026-09-26，**Phase 260 完工回檢＝三項寄居型別之歸位**）**：本 phase **不在本規劃書原列之九個 phase 之列**，係事主於 P259 收束後**另行開立**者（事主原問：「`Typewriter_BPMFFullMatch.swift` 是否過於複雜到需要拆成 `Typewriter_BPMFClassic`／`Typewriter_BPMFFurious`／`Typewriter_SCPC` 這幾個不同的 Typewriter」；先評估、後裁定「一次交差。你新開 P260 落實」）。**評估之結論為「不拆型別、改做歸位」**，三項判定如下：① **`Typewriter_SCPC` 不成立**——SCPC 不是 `typingMode` 的值（§7.1 之推導式已把「狂打開關 ∧ 非 SCPC ∧ 鍵盤家族」算完），SCPC 之全部行為住在代理檔之 `handleTypewriterSCPCTasks()`、由各打字機在同三處呼叫 ⇒ Classic 與 SCPC 執行同一條路徑，拆之即約 500 行逐位元組重複；② **`Typewriter_BPMFFurious` 方向對而落點錯**——狂打側之專屬邏輯依「**鍵盤家族**」而非「模式」分支（§8.6 之 `isPinyin…`／`isZhuyin…` 兩旗子），推導式之兩臂會派給同一型別；③ `Typewriter_BPMFClassic` 只是把三個狂打 `guard` 恆假。**★ 本 phase 查出並登錄之最大盲區**：`typingMode` 謂之「模式之單一出口」，而打字機內部另有**就地重新推導**（`isPinyinFuriousTypingModeEffective` 2 處、`prefs.useSCPCTypingMode` 1 處），該同步義務**無型別層強制**——**實錄兩次**：P254 之家族兩分（`a74594d`）與 P257 之 SCPC 閘（`b4d4988`）皆**只動打字機、未動推導式**。**故「這檔好複雜」之體感，大半來自此冗餘、而非打字機本身。****交付**：`FuriousTypingConfig` → `InputHandler/InputHandler_FuriousTypingConfig.swift`（78 行，新檔）、`MixedAlnumConfig` → `InputHandler/InputHandler_MixedAlnumConfig.swift`（50 行，新檔——**成對之既有慣例，故成對處理**）、`Tekkon.Composer` 之自動切音節判準 ＋ 注音閘門 → `Typewriter/Typewriter_ZhuyinFuriousAutoChop.swift`（78 行，新檔）；`Typewriter_BPMFFullMatch.swift` 868 → **732** 行、`Typewriter_MixedAlphanumerical.swift` 1025 → **979** 行。**歸屬之判準（登錄為日後之通則）**：**純函式之判準住在其唯一呼叫者之目錄**（`shouldAutoChopZhuyin` 之生產側呼叫者實查僅 `performZhuyinAutoChopIfNeeded` 一處）、**執行住在打字機**；**狀態型別住在持有者之目錄**（兩顆 Config 之持有者恆為 `InputHandlerProtocol`）。**未移入 `Sources/Tekkon/`**：§3.3 之紅線「Tekkon 於本系列零改動」不破，且該擴充住在 `LibVanguard` 正是 P255 讓 30 萬次回歸靶零成本驅動之原因。**驗證**：**634 支／0 失敗、exit 0**（動工前後同值；**新增檔案不入任何靶**）、兩倉逐檔 SHA-256（`Sources` ＋ `Tests`，排除 `.DS_Store`）**211 檔全同、0 不符**；**無損證明**以逐行文字指紋行之（LOST 僅 1 行之陳舊 doc comment、GAINED 僅檔頭與 `import`／`MARK`／`- Note:` 共 20 行）——此形比「測試全綠」更強，因它同時證明**沒有任何一行被靜默丟棄**。**manifest 無需改動**（`sources:` 之命中皆為 `resources:` 之誤命中、靶皆目錄式、`project.pbxproj` 對此二檔零引用）。**「未動」亦為交付（明列）**：評估之第 2 步（`FuriousTypingPolicy` 之單向政策）與第 3 步（三型別）**本 phase 皆不做**；前者之日後判準為——**當兩側狂打之行為分岔到無法用同一個 `handle` 表達時，該拆的是「家族」；`SCPC` 永遠不該成為型別**（它是一個與模式正交之偏好，本節之推導式已正確地如此對待它）。**交付**：`vChewing-LibVanguard` `e6442886`／`vChewing-macOS` `312dec6b`（訊息逐字相同、末尾 `(Phase 260)`；pre-commit 掃描 CRITICAL 0／WARN 0、提交後兩倉 clean、最終 byte-sync 211 檔全同）。**受修訂之小節**：文首〈修訂沿革〉（本行），以及**凡以檔案行號指名該二檔之現況表**——§3.1（`FuriousTypingConfig` 之新址 25–78）、§8.3（狂打閘門讀取點之新行號 208／278／52／71）、§8.3.1（`handle` 之新範圍 6–76）、§8.6（`hasFuriousFrontPending` 之五個寫入點新行號）、§8.7（熱路徑 104）、§8.8 與其「新增」段（判準之新檔與新行號）。**未重編者（刻意）**：本卷各 phase 之**歷史記錄**（P251–P259 篇）與 `DevReqsHistory` 之各列——其行號係當時之實況、依歷史記載原則原樣保留。**順帶修復**：§8.8 之表格有一列（`判準之模式閘（v14）`）**被空行切離表格**——此為 v14 之增補所遺留（與 P258 修復者同型之結構缺陷），本 phase 就地接回並以掃描複驗 **0 處可疑**。**無後續 phase 待排。**

---

## 〇、摘要

### 0.1 目標與交付

**目標**：把唯音既有的「狂拼模式」（拼音連續組句）擴展為一個**同時涵蓋拼音與注音兩種打字方式**的「**狂打模式**」，並使其在使用者偏好層面**可分開開關**——注音側預設**停用**、拼音側維持預設**啟用**（＝既有使用者的行為零變動）。

**交付**：① 本文（設計依據與手術路線圖）；② **九個**後續 phase 的界線與完成定義（v4 重組；其中 **251 已完成**，見 §8.2）（§八）；③ 需事主知悉之自動裁定記錄（§九）。

**本 phase 不動任何生產碼。** 唯二的落點是本文與 `Reqs_0241-0250.md` 內的 Phase 250 記錄。

**四項決定性事實（實查）**：

1. **狂打之「拼音專利」只是一道五元合取閘門，不是管線結構。** `isFuriousTypingModeEffective`（`InputHandler_FuriousResegmentation.swift:63`）＝ `currentTypingMethod == .vChewingFactory` ∧ `!prefs.cassetteEnabled` ∧ `prefs.furiousTypingEnabled` ∧ `!prefs.useSCPCTypingMode` ∧ **`composer.isPinyinMode`**。該五元之中唯最後一項排除注音，而它同時被 12 處讀取點當作「狂拼有效」之定義（§二.1）。**注音化的核心工作量，不在「新寫一套注音管線」，而在「把這道閘門與其 12 個下游讀取點所隱含的『狂拼⇒拼音』假設逐一解耦」，並為注音補上一條等價的『自動切音節』機構**（§二.2）。
2. **注音側所需的資料結構，比拼音側小兩個數量級。** 拼音狂拼需要 `PinyinTrie`（每排列 498–571 節點）以支援「不完整 romaji 前綴 → 可能注音」之反向展開；注音鍵流本身即為注音符號，**不需要反向推導**。實測：`mapHanyuPinyin` 之 427 條注音詞幹，其**全部非空前綴**僅 **442 條**（427 完整 ＋ 15 嚴格前綴），UTF-8 共約 **3 KB**（§四.2）。故注音側所需者是一個**前綴集合**，而非 Trie；且其成本可忽略。
3. **單聲母／單韻母是辭典內之 first-class 讀音鍵，這是整個狂打功能之樞紐。** 實查生產辭典（`VanguardFactoryDict4Typing.txtMap`，206,266 條鍵）：**21 個聲母與 16 個單韻母／介母全部**是合法讀音鍵（各有一條「以自身為值」之詞條，如 `ㄍ → ㄍ`），另有 **85** 條「各段皆為單一注音符號」之多音節鍵（如 `ㄍ-ㄋ-ㄋ → ㄍ`、`ㄋ-ㄋ → ㄋㄟㄋㄟ`）。⇒ 自動提交單聲母在技術上完全可行；而**不做此事就等於縮寫打法在狂打模式下永遠打不出來**（三顆聲母互搶同一個槽位）。此即事主異議之技術根據（§3.0）。**惟須注意：那 85 條單符號鍵之值多為「回聲字串」，狂打之真正價值在於逐字組句與整鍵詞條**——「狗男女」來自完整讀音鍵 `ㄍㄡˇ-ㄋㄢˊ-ㄋㄩˇ`（−6.649），「幹你娘」則來自逐字語言模型組句（原廠辭典**無**該詞；§3.0.1 之 v3 表）。
4. **動態注音排列之「按鍵 ↔ 讀音」對照，引擎內不存在。** 反向（讀音 → 按鍵序列）**無任何 API**；正向（按鍵 → 讀音）是**逐鍵程序式解碼**且**依賴當前聲介韻槽狀態**（`handleETen26`／`handleHsu` 等五支 handler ＋ 共用的 `commonFixWhenHandlingDynamicArrangeInputs`），非純函式、亦非查表。唯一的全量對照在**測試資料**內：`Tests/TekkonTests/TestAssets_Tekkon/Tekkon_TestData.swift` 之 1485 行 × 5 排列 ＝ **7366 筆**已斷言之編碼（§五.1）。**故「把動態注音的讀音組合窮舉成 Trie」在技術上可行、但與現行程式碼是兩份各自維護的真相**——這是本 phase 對事主之存疑所給出的核心答覆（§五）。

### 0.2 關鍵取捨

| # | 議題 | 結論 | 依據 |
|---|---|---|---|
| 1 | 注音狂打是否沿用 `FuriousTypingSegmentor` 之 DP 重切分 | **不沿用**。注音鍵流之音節邊界由「槽位型別遞降」決定，非由語言模型猜測；且拼音重切分之全部前提是「相鄰音節可無分隔連寫」（`furiousTrail.joined()`），注音不成立 | §二.2、§三.4 |
| 2 | 注音狂打之「自動切音節」落點 | **Handler 執行切分**（不在 Tekkon 內自動 chop）。**v5 收緊**：Tekkon 於本系列只提供 `SyllableIndex.isPrefix` 一問；判準之全部素材（當前槽內容、本鍵之固有語意、切點）皆由 Handler 以既有 `public` API 取得（§4.4） | §3.3、§4.4 |
| 2b | **注音狂打是否開 copilot 窗** | **要開**（事主 v2 異議之直接結果）：縮寫／逐字打法**非開不可**——不開則該打法打不出，且「幹你娘」（逐字組句）與「狗男女」（整鍵詞條）一類候選永無露面之日 | §3.0、§3.5 |
| 2c | **自動切音節之判準** | **v5 定案為 §3.2 之 v7（六條）**。v4 原文之第四問（假想內容是否為讀音之前綴）經 P251 實測證偽：單音節誤切 12 次、交界漏切 48.05%、且大千下 `ess`（＝ㄍㄋㄋ）只得一顆「ㄋ」 | §3.2、P251 |
| 3 | Tekkon 是否新增 Trie | **否**。新增一個 **442 條**之前綴索引（`Tekkon.SyllableIndex`，**已於 P252 交付**），非 Trie；**不**收錄動態排列之按鍵序列 | §5.2、§5.3、§8.3 |
| 4 | 動態鍵盤「下一步可敲哪些鍵」之 API | **本輪不實作**；逐鍵模擬派生（simulation-derived）列為**後續選項**，且**若實作則置於 `LibVanguard` 而非 Tekkon** | §5.4 |
| 5 | 偏好鍵之處理 | 既有 `FuriousTypingEnabled` **兩分為** `FuriousTypingEnabled4Pinyin`（承接舊值）與 `FuriousTypingEnabled4Zhuyin`（預設 `false`）；**Swift 端符號亦全量重新命名，不留別名** | §6.1、§6.2 |
| 6 | 資料遷移之落點 | 既有之 `PrefMgr.migrateDeprecatedSettings()`（`PrefMgr_Core.swift:516`）內新增一段，**逐字照** `UsingHotKeyHalfWidthASCII → UsingHotKeyHalfWidthPunctuation` 之成例 | §6.3 |
| 7 | 「注音文抑制」之歸屬 | **兩種狂打皆抑制**（v3，事主明示）。由「拼音狂打 且 拼音方式」改為依當前打字方式二選一之析取式。**v5 定案：續留 `LXFacade.syncPrefs()`**（原「傾向移到 Handler 側」之議已由 P251 未知四否決——熱鍵改的正是 `pinyinTypingEnabled`，且 `syncPrefs()` 每拍皆跑 ⇒ 無脫鉤之虞） | §7.4、§8.8 |
| 8 | Phase 切分 | **九個**後續 phase（**251 已完成**，252–259 待動；v4 重組之結果）。次序：251 驗證靶 → 252 Tekkon API → 253 偏好層 → 254 閘門收束 → 255 自動切音節 → 256 copilot 窗 → 257 注音文抑制 → 258 偏好介面與 i18n → 259 跨倉驗收 | §8.1、§八 |
| 9 | 兩倉 byte-sync | 每一個後續 phase **同輪**鏡像 `Sources/`／`Tests/`／`Deps/`／六份 manifest／`makefile`，並以 `cmp`／`diff -rq` 之**實際輸出**為驗收證據 | §8.0、§10.3 |

**★ 三則不可退讓之約束**：① **注音狂打之出廠預設值為 `false`**——未表態之既有使用者，其拼音狂拼行為、乃至一切既有行為，一律零變動；② **本系列不動 `FuriousTypingSegmentor`、不動 Homa**——注音化是「新增一條與拼音並行的路徑」，不是「把拼音路徑改造成通用路徑」。凡遇「不如把拼音那套抽象化」之施工衝動，一律以本條擋下；真要抽象化，另立 phase；③ **單聲母／單韻母之縮寫打法必須可用**（§3.0）——自動提交之判準**不得**要求「當前內容已為完整音節」，且 `unfinishedReading` 於注音側必須回傳當前音節。此為本系列之**功能底線**，非加分項。

### 0.3 四則關鍵約束

1. **`UserDef.rawValue` 一經發佈即不可更名**（`UserDef.swift:9–10` 之明文紀律），而 `rawValue` 就是 `UserDefaults` 之鍵（`UserDef.swift:1427`）。故本系列之「重新命名」**必然**是一次**有損**的鍵遷移，必須配套 §六.3 之遷移碼；且 `UserDef.exportAsJSON()` 之輸出鍵亦即 `rawValue`，故**外部既有之配置包一旦含舊鍵，其匯入將以 `"Unknown key"` 失敗**（§六.4）。
2. **`migrateDeprecatedSettings()` 於每次 `InputSession.activateServer()` 執行**（`PrefMgr_Utilities.swift:8, 11–12`），且其內部直接使用 `UserDefaults.standard`（`PrefMgr_Core.swift:517`）而非 `UserDefaults.current`。新增之遷移段**必須自我守衛、冪等**——以「舊鍵存在與否」為閘，處理完即 `removeObject`。
3. **兩個 IME 行程之測試不得並行**：兩倉之 `swift test` 共用同一批**磁碟上**之具名 `UserDefaults` suite，併跑會產生游移之偽紅（`KnowledgeMemo4LLM.md:399`；P242 實錄）。本系列涉及偏好鍵之遷移，此紀律尤須遵守。
4. **`Tekkon` 靶不受 `defaultIsolation(MainActor.self)` 規範**（`Package.swift:92–94`；`Tekkon_PinyinTrie.swift:108–109` 有明文）。故 Tekkon 內任何新增之全域可變快取，**必須**照 `PinyinTrie.sharedCache` 之成例（`NSLock` ＋ `nonisolated(unsafe) private static var`）明示其同步責任。

---

## 一、術語定案：狂打／狂拼／狂注

### 1.1 事主之裁定

> 「從這個 Phase 起，Furious 作為 vChewing 輸入法的模式而言的中日翻譯由「狂拼」擴展到新的稱謂「狂打／狂打ち」。」
> 「從這個手術開始，Furious Typing 模式不再是拼音打字的專利。」

### 1.2 三層命名與其對位（**v22 全面改版；舊稱謂正式停用**）

> **v22 之改版（事主 2026-09-26 裁定）**：「狂注 → **注音狂打**／**注音狂打ち**／**Furious Zhuyin**；狂拼 → **拼音狂打**／**弁音狂打ち**／**Furious Pinyin**。**此前的功能稱謂正式停用。**」故下表取代 v1 之原表；**本節以下之「狂拼／狂注」一律作廢**。

| 層級 | zh-Hant | zh-Hans | ja | en | 說明 |
|---|---|---|---|---|---|
| **總稱**（模式本身） | 狂打模式 | 狂打模式 | **狂打ち**モード | Furious Typing | 涵蓋拼音與注音兩側 |
| **拼音側** | **拼音狂打** | **拼音狂打** | **弁音狂打ち** | **Furious Pinyin** | v22 新定；舊稱「狂拼」**停用** |
| **注音側** | **注音狂打** | **注音狂打** | **注音狂打ち** | **Furious Zhuyin** | v22 新定；舊稱「狂注」**停用** |

**新命名之構成**：兩側皆以**輸入法之第一等術語**（`注音`／`拼音`；ja 之對位為 `注音`／`弁音`）修飾總稱「狂打」（ja「狂打ち」）——故「同構」不再靠生造單字動詞，而是靠**共用總稱**。此舉之收益有三：① 兩側之名**自明**（不必先知道「狂拼＝拼音側」）；② 與**既有 i18n 之語彙**一致（ja 之 `弁音` 本即該語系對拼音之定譯，見既有之「弁音配列」「弁音入力」）；③ en 之 "Furious Pinyin"／"Furious Zhuyin" 與既有之產品語彙（`Furious Pinyin Typing` 一類）**對位整齊**，且不再需要「Typing」贅尾。

**「狂打ち」之字形**：照事主原文用**漢字 ＋ 平假名送假名**（`狂打ち`），不寫成全漢字「狂打」——後者在日文內易被讀作「きょうだ」，失其動詞性。**新名之 ja 亦然**（`注音狂打ち`／`弁音狂打ち`），不寫成 `注音狂打`。

**停用之範圍（v22 明示）**：① **使用者可見之文案**（四語系 `.strings`）——舊稱謂**一字不留**，並以**術語護欄**（助手之 `metadata.test.js`）釘住；② **本規劃書與 `KnowledgeMemo4LLM.md` 之現況敘述**——一律改用新稱謂；③ **歷史記錄**（本卷各 phase 記錄、`DevReqsHistory.md` 各列、本文之〈修訂沿革〉）——**保留舊稱謂**，因其中多有**事主原文之逐字引用**（如「比如打「ㄍㄋㄋ」可以預覽到「幹你娘」」一段前後之「狂拼」），改之即偽造引文。凡讀歷史段落者，請以本節之對位表換算。

**一項不在停用範圍者**：助手之「**狂拼流漢語拼音輸入法**」標籤（`origin.opt.pinyin`／`origin.short.pinyin`，en "Furious-typing Hanyu Pinyin IMEs"）——該處之「狂拼」**指他款輸入法之譜系**（其列舉即含產品「智能狂拼」等七款），非本模式之稱謂，故不改。

### 1.3 落點：四語系字串與 `TypingMode`

`TypingMode` 之 `rawValue` 直接構成 i18n 鍵（`InputHandler_TypingMode.swift:27–29`：`"i18n:TypingMode.i18nKey4InlineModeHint.\(rawValue)"`）。故新增 `.zhuyinFuriousTyping` 即自動要求一條新鍵 `i18n:TypingMode.i18nKey4InlineModeHint.zhuyinFuriousTyping`（現有 `.pinyinFuriousTyping` 之四語系值為：zh-Hant／zh-Hans「狂拼模式」、ja「狂拼モード」、en「Furious Typing」——**該值建議同步改為「狂拼模式」語義不動、但 en 改「Furious Pinyin Typing」以與注音側對稱**；此為 §九 之自動裁定事項之一）。

**既有 i18n 之清單**（皆在 `Sources/vChewingIME_macOS/Resources/{en,ja,zh-Hans,zh-Hant}.lproj/Localizable.strings` 之 444–445 行與 349 行；`Base.lproj` **無** `Localizable.strings`）：

| 鍵 | 現值（zh-Hant） | 處置 |
|---|---|---|
| `i18n:UserDef.kFuriousTypingEnabled.shortTitle` | 啟用狂拼模式（連續拼音打字） | 隨 case 更名；文案改「啟用狂拼模式（連續拼音打字）」**不變**（其語義本即拼音） |
| `i18n:UserDef.kFuriousTypingEnabled.description` | （長文，見 §六.1） | 隨 case 更名；**內容不動** |
| `i18n:TypingMode.i18nKey4InlineModeHint.pinyinFuriousTyping` | 狂拼模式 | 值**不動**（zh 側）；en 建議改 `Furious Pinyin Typing` |
| `i18n:TypingMode.i18nKey4InlineModeHint.zhuyinFuriousTyping` | — | **新增**：狂注模式／狂注模式／狂注モード／Furious Zhuyin Typing |
| `i18n:UserDef.kFuriousTypingEnabled4Zhuyin.shortTitle` | — | **新增**：啟用狂注模式（連續注音打字）／啟用狂注模式（连续注音打字）／狂注モードを有効化（連続注音入力）／Enable Furious Zhuyin Typing (continuous bopomofo) |
| `i18n:UserDef.kFuriousTypingEnabled4Zhuyin.description` | — | **新增**：zh-Hant 草案見 §七.5 |

zh-Hans 一律照 **zh-Hans-TW** 紀律（僅簡化字形、詞彙沿用臺灣用法）。

---

## 二、現況盤點（實查）

### 2.1 閘門與其讀取點

| 名稱 | 落點 | 內容 |
|---|---|---|
| `TypingMode` | `InputHandler_TypingMode.swift:14–30` | `.cassette`／`.bopomofoKeyblock`／`.pinyinKeyblock`／`.pinyinFuriousTyping` |
| `typingMode` | 同檔 `:56–66`（**P258 後之實況**） | `if prefs.cassetteEnabled { return .cassette }`；`let isFurious = composer.isPinyinMode ? prefs.furiousTypingEnabled4Pinyin : (prefs.furiousTypingEnabled4Zhuyin && !prefs.mixedAlphanumericalEnabled)`；`if isFurious, !prefs.useSCPCTypingMode { return composer.isPinyinMode ? .pinyinFuriousTyping : .zhuyinFuriousTyping }`；`return composer.isPinyinMode ? .pinyinKeyblock : .bopomofoKeyblock` |
| `isFuriousTypingModeEffective` | `InputHandler_FuriousResegmentation.swift:63–65` | `currentTypingMethod == .vChewingFactory && typingMode == .pinyinFuriousTyping` |
| `hasFuriousFrontPending` | 同檔 `:68–70` | `isFuriousTypingModeEffective && !composer.romajiBuffer.isEmpty` |

`isFuriousTypingModeEffective` 之**讀取點共 12 處**（實查）：
`Typewriter_BPMFFullMatch.swift:208`（`allowsExtendedRomajiBuffer`）、【P260 新址】`:278`（trail 記錄）；`InputHandler_CoreProtocol.swift:215`（`isPinyinFamilyTypingMode`）、`:873`（POM matchMode）、`:885`（POM 自動套用抑制）；`InputHandler_HandleCandidate.swift:281`（`furiousShift`）；`InputHandler_FuriousResegmentation.swift:69, 166, 352, 441`；`InputHandler_HandleStates.swift:43`（`furiousFrontContext`）、`:119`（`furiousAbbreviatedCells`）；`Session/InputSession_Delegates.swift:352`。

`hasFuriousFrontPending` 之**讀取點共 6 處**：
`Typewriter_BPMFFullMatch.swift:52`（Shift＋選字鍵路由）、【P260 新址】`:71`（Enter 固化）；`InputHandler_TriageInput.swift:35`（固化後之空格消費）、`:49`（Tab）；`InputHandler_HandleStates.swift:271`（`confirmFuriousFrontCandidate` 之守衛）、`:813`（標點前固化）；`Session/SessionCoreProtocol.swift:198`（`isFuriousCopilotCandidateWindowVisible`）。

`typingMode` 之讀取點共 3 處：`InputHandler_HandleComposition.swift:27`（typewriter 分派）、`InputHandler_FuriousResegmentation.swift:64`、`Session/SessionProtocol.swift:337`（內文模式提示之 i18n 鍵）。

**關鍵觀察**：`InputHandler_HandleComposition.swift:27–37` 之 `switch typingMode` **已把 `.bopomofoKeyblock` 與 `.pinyinFuriousTyping, .pinyinKeyblock` 一併派給同一個 `BPMFFullMatchTypewriter`**。故注音狂打**不需要新的 typewriter**，只需要該 typewriter 內部的狂打分支認得注音。

### 2.2 拼音狂拼與注音狂打之根本差異

| 面向 | 拼音狂拼（現況） | 注音狂打（本案） |
|---|---|---|
| 注拼槽之內在 | `romajiBuffer`（**無分隔之字母流**，可橫跨多音節）＋ 聲介韻調四槽 | **僅**聲介韻調四槽；鍵流本身即帶分隔（聲介韻調之槽位型別是天然邊界），**不需要** extended buffer |
| 音節邊界之判定 | 未知。以 `PinyinTrie.chop` 貪婪最長匹配 ＋ LM 引導之 DP 重切分修正 | **已知**。新鍵之目標槽位若早於或等於已填之最高槽位，則當前音節已了結 |
| 「不完整讀音」之表示 | `romajiBuffer`（如 `bian` 打了一半之 `bia`） | 四槽之部分填充（如只有聲母 `ㄅ`）——`composer.isEmpty == false` 即「有未完成讀音」 |
| 前綴合法性 | `PinyinTrie.search(romaji)` 前綴展開 | `Tekkon.SyllableIndex.isPrefix(_:)` |
| 重切分之必要性 | **必要**（greedy chop 會切錯，如 `fangan` → `fang\|an` 而使用者要 `fan\|gan`） | **不必要**（邊界為結構所決定）；且「相鄰音節無分隔連寫」之前提不成立 |
| 簡拼（`ysxb` → 整詞） | 有（α 路徑：`abbreviatedWordCandidates(keysChopped:)`） | **無**（注音不打簡拼；注音符號本身已是音節之最小成分） |
| 注音文抑制 | 啟用 | **啟用**（v3，事主明示；與拼音同，見 §7.4） |

**故注音狂打是拼音狂拼之「退化情形」**：少掉 segmentor、少掉 trail、少掉簡拼、少掉 extended buffer，換來一條新的「自動切音節」判準。這正是「新增並行路徑」而非「抽象化既有路徑」在工程上更省的理由（§0.2 ★②）。

### 2.3 `FuriousTypingConfig` 與注音之關係

`FuriousTypingConfig`（【P260 新址】`InputHandler_FuriousTypingConfig.swift:25–78`）之三欄——`trail`（拼音字母 blob 序列）、`highlightOverride`、`coSegmentedOffers`——**皆為拼音專屬**。注音狂打**不寫入 trail、不建立 offers**；`furiousHighlightOverride`／`coSegmentedOffers` 於注音側**無生產者**（前者由 copilot 窗之高亮驅動、後者為拼音之聯合重切產物）——**注音狂打不寫入對方**，故：

- `furiousConfig` 這一項**協定要求**（`InputHandler_CoreProtocol.swift:50`）**不動**（避免打破 `InputHandler`／`MockInputHandler` 兩個 conformer）；
- 注音狂打**不呼叫** `invalidateFuriousTrail()`／`popFuriousTrail(_:)`（呼叫亦無害，因其只動拼音狀態）；
- 需要動的是 `hasFuriousFrontPending` 與 `unfinishedReading`（見 §3.5）；註音側之 highlight 與 co-segmented 路徑自然不被觸發（無生產者）。

### 2.4 既有資產之可複用度（逐段）

| 段 | 落點 | 注音可否複用 |
|---|---|---|
| `BPMFFullMatchTypewriter.handle` 之選字鍵路由、Enter 固化、Backspace | 【P260 新址】`Typewriter_BPMFFullMatch.swift:6–76` | **可**（皆以 `hasFuriousFrontPending` 為閘，閘一放寬即通） |
| `consumeReadingInputIfNeeded` 之「先送注拼槽」骨架 | 同檔 `:240–283` | **可**（注音分支已在 `receiveKey(fromScalar:)` 內） |
| `performPinyinAutoChopIfNeeded` | 同檔 `:285–350` | **不可**（拼音專屬）；注音另立一支 |
| `composeReadingIfReady` ＋ `readingKeyForQuery` | 同檔 `:352` 起 | **可**（與拼音無關；`phonabetKeyForQuery` 本即注音） |
| `furiousFrontContext`／`buildFuriousFrontCandidates` 之 Homa 段 | `InputHandler_HandleStates.swift:39–101, 154–253` | **部分可**（候選評分、POM、交叉邊界詞皆與音節表示無關）；其**輸入**（`romaji` → `zhuyinReadings`）**不可** |
| `applyFuriousFrontCandidate`／`previewFuriousHighlightedCandidate` | `InputHandler_FuriousResegmentation.swift:192–341` | **可**（純 Homa 鍵桶操作） |
| `enumerateFuriousResegmentationCandidates`／`resegmentFuriousTrailIfNeeded` | 同檔 `:351–431, 549–573` | **不可**（trail 為拼音字母） |
| `unfinishedReading`（copilot 窗頂部） | `InputSession_Delegates.swift:204–208` | **需改**（改讀 `composer` 之當前音節） |
| 註音文抑制 | `LXFacade.swift:334` | **需改**（見 §7.4） |

---

## 三、注音狂打之規格

### 3.0 ★ 注音狂打之原始需求：**單聲母狂打**（事主 2026-09-26 之異議）

> 事主原文：「竊以為注音的狂打模式還是需要 copilot 視窗的，比如打「ㄍㄋㄋ」可以預覽到「幹你娘」。」

此異議推翻本文初稿之兩項設計（初稿曾主張「不開 copilot 窗」並以「音節須為合法完整讀音」為自動提交之前提）。其原因不只是「少了預覽」，而是**單聲母狂打根本打不出來**：

| 步驟 | 初稿之行為 | 後果 |
|---|---|---|
| 敲 `ㄍ` | 注拼槽＝`ㄍ`；因非完整讀音故不提交 | — |
| 敲 `ㄋ` | `S_new(1) <= S_max(1)`，但 `ㄍ` 非**完整**讀音 ⇒ 不切、逕行覆寫 | **`ㄍ` 消失**，注拼槽＝`ㄋ` |
| 敲 `ㄋ` | 同上 | 注拼槽＝`ㄋ`（第二顆） |

即：初稿之設計會讓「ㄍㄋㄋ」在狂打模式下**永遠打不出來**——三顆聲母互搶同一個槽，最終只剩一顆。而這正是網路注音文最典型之打法。

**故本節（含 §3.2 之判準與 §3.5 之 copilot 窗）已然改版；凡與本節衝突之初稿文字一律作廢。**

#### 3.0.1 決定性證據：原廠辭典之實況（**v3 全面複查**）

實查 `VanguardFactoryDict4Typing.txtMap`（生產辭典，206,266 條鍵；取自 `Build/…/vChewing.app` 之既有產物）：

| # | 事實 | 值 |
|---|---|---|
| 1 | **21 個注音聲母全部**都是合法讀音鍵（`ㄅ`…`ㄙ`） | 21／21；其詞條為「以自身為值」之單條目，權重一律 `-8.863`（如 `ㄅ → ㄅ`、`ㄍ → ㄍ`、`ㄋ → ㄋ`） |
| 2 | 16 個單獨韻母／介母亦全部是合法讀音鍵（`ㄚ`…`ㄩ`） | 16／16，同形 |
| 3 | 「各段皆為單一注音符號」之多音節鍵 | **85** 條（`ㄋ-ㄋ`、`ㄓ-ㄓ`、`ㄔ-ㄔ`、`ㄕ-ㄕ`、`ㄓ-ㄨ`…） |
| 4 | **`ㄍ-ㄋ-ㄋ` 之詞條值** | **字串 `ㄍ`**（權重 `-8.863`）——**不是**「狗男女」、亦不是「幹你娘」 |
| 5 | **「狗男女」之真源** | 完整讀音鍵 **`ㄍㄡˇ-ㄋㄢˊ-ㄋㄩˇ`**（權重 `-6.649`，**該鍵之唯一條目**）；`ㄍㄡˇ-ㄋㄢˊ-ㄋㄩ`／`ㄍㄡ-ㄋㄢ-ㄋㄩ` 皆**不存在** |
| 6 | **「幹你娘」於原廠辭典內** | **零命中**（全檔 450,484 行；`幹你`／`你娘` 亦皆 0）。其逐字單音節為：`幹`＝`ㄍㄢˋ`（−5.206）、`你`＝`ㄋㄧˇ`（−5.075）、`娘`＝`ㄋㄧㄤˊ`（−5.257） |
| 7 | `ㄍㄢˋ` 起首之鍵共 **72** 條（`ㄍㄢˋ-ㄅㄢˋ`、`ㄍㄢˋ-ㄇㄚˊ`…），但 `ㄍㄢˋ-ㄋ` 起首者 **0 條** | ⇒ 該三字**只能**由語言模型逐字組句，或由使用者自有詞庫提供 |

**上游正本**：`vChewing-VanguardLexicon` 之 `Sources/LibVanguardChewingData/Resources/components/common/data-zhuyinwen.txt`，**全檔 8 行**：

```
ㄅㄧㄤ   ㄅㄧㄤ    -9.6
ㄅㄧㄤˋ  ㄅㄧㄤˋ   -9.6
ㄉㄨㄤ   ㄉㄨㄤ    -9.6
ㄋㄟ     ㄋㄟ      -9.6
ㄋㄟㄋㄟ  ㄋ-ㄋ     -9.6
ㄋㄟㄋㄟ  ㄋㄟ-ㄋㄟ  -9.6
ㄎㄧㄤ   ㄎㄧㄤ    -9.6
ㄍㄋㄋ   ㄍ-ㄋ-ㄋ   -9.6
```

該檔之型別標記為 `EntryType.zhuyinwen`（`10 << 0`；其詞條之值**皆為注音符號字串**），**即 §7.4 那個抑制旗標所過濾之對象**——這 8 行就是「注音文」的全部。

**三項結論**：

1. **單聲母音節在辭典內是 first-class**：`assembler.insertKey("ㄍ")` 本即會成功，故自動提交單聲母在技術上可行（v1 之缺口因此純屬設計判斷之誤，非資料限制）。
2. **但單符號多音節鍵（`ㄍ-ㄋ-ㄋ`）對狂打並非必要**：其值只是回聲字串 `ㄍ`。狂打之所以需要 `ㄍ|ㄋ|ㄋ` 三鍵，理由是**逐字組句**（候選來自語言模型）與**不吞鍵**（v1 之病灶），與那 85 條單符號鍵無關。**故 §4.2 之 `SyllableIndex` 不收單符號之裁定不變**。
3. **「狗男女」與「幹你娘」各有其真源、且互不相同**：

| 候選 | 真源 | 為何拼音之 `gnn` 看得到／看不到 |
|---|---|---|
| **狗男女** | **完整讀音鍵** `ㄍㄡˇ-ㄋㄢˊ-ㄋㄩˇ`（−6.649） | 拼音側之 `gnn` 經 `PinyinTrie` 之前綴展開，可得 `ㄍㄡˇ`／`ㄋㄢˊ`／`ㄋㄩˇ` 等一眾注音桶，恰含該鍵 ⇒ **看得到** |
| **幹你娘** | **逐字語言模型組句**（`ㄍㄢˋ`＋`ㄋㄧˇ`＋`ㄋㄧㄤˊ`）**或**使用者自有詞庫 | 拼音側同樣可得該三桶，但依 P155 之量化，拼寫之笛卡爾積會觸發 Homa 之 `maxSegLength` 半徑偵測與防禦 ⇒ **繁雜度壓過收益、看不到**。**故事主所見之對比（`gnn` 見「狗男女」而不見「幹你娘」）正是此二源之差異** |

**⇒ 對事主之例之誠實答覆（v3）**：在**完整讀音**之輸入下（`ㄍㄢˋ-ㄋㄧˇ-ㄋㄧㄤˊ`、`ㄍㄡˇ-ㄋㄢˊ-ㄋㄩˇ`），注音狂打之 copilot 窗**會**預覽到「幹你娘」與「狗男女」——前者靠**逐字組句**、後者靠**整鍵詞條**，而**兩者都不需要注音文那 8 行**。在**單聲母縮寫**（`ㄍㄋㄋ`）之輸入下，則只會得到回聲字串 `ㄍ`（且該字串將因 §7.4 之抑制而不再出現）——**這正是事主 v3 追加「注音狂打也屏蔽注音文」之合理性所在：屏蔽掉回聲字串，留下的才是使用者要的詞。**

#### 3.0.2 自動提交之**充分**條件（比必要條件更強、且與拼音一致）

既然單聲母本即為合法音節，則「自動提交」**不必**等到結構上確定為新音節——只要「當前串已不可能再延伸成更長之讀音」即可提交。此與拼音狂拼之 greedy 語義同源（拼音之 `pinyinAutoChopResult` 亦是在「延伸後不再是單一可唸讀音」時才 chop）。

上表之三步遂變為：

| 步驟 | 新行為 |
|---|---|
| 敲 `ㄍ` | 注拼槽＝`ㄍ` |
| 敲 `ㄋ` | `ㄍㄋ` **非**任一讀音之前綴 ⇒ **提交 `ㄍ`**、注拼槽重設為 `ㄋ` |
| 敲 `ㄋ` | `ㄋㄋ` **非**任一讀音之前綴 ⇒ **提交 `ㄋ`**、注拼槽＝`ㄋ`（第二顆） |
| （paused） | 組字器三鍵皆在；copilot 窗以 `ㄍ-ㄋ-ㄋ` 查得詞條 ⇒ 預覽 `ㄍㄋㄋ` |
| 空格／Enter | 固化第三顆並遞交 |

**「不必等到結構上確定」是本改版之關鍵**：條件 ③（目標槽位不升）只是「新音節開始」之**必要**條件，用來避免在**同一**音節內誤提交（如 `ㄅㄧ` ＋ `ㄢ`）；真正之**充分**條件是條件 ④ 之否定（不再可能是任何讀音之前綴）。

> **v5 附註（P251 實測）**：本小節之三步表以**接續語意**表述「`ㄍㄋ` 非任一讀音之前綴」——此與 §3.2 正文之**覆寫語意**（「以 K 寫入其目標槽後之假想內容」）本即不一致。P251 之實測判**兩者皆不可用**：接續語意於合法單音節誤切 4,387 次、且在大千26 `qquu`（＝ㄅㄚ）之第二拍即誤切；覆寫語意於大千 `ess`（＝ㄍㄋㄋ）上判「不切」而使單聲母縮寫全滅。**本表之語意僅保留為歷史記錄**，正確之判準見 §3.2 之 v7。

### 3.1 使用者可見之行為

1. 使用者以任一注音排列連續鍵入，**不需逐音節敲聲調、亦不需按空格確認**。
2. 每當當前注拼槽內容連同本拍按鍵**已不可能再延伸成任何合法讀音**時，當前內容自動寫入組字器（＝「自動切音節」）；**單聲母亦照此提交**（§3.0）。
3. 聲調鍵之語義**完全不動**：敲聲調即照既有行為確認該音節（含後置聲調覆寫）。狂打只免除「不敲聲調也要能前進」這一件事。
4. 空格／Tab／Enter／標點之語義**沿用拼音狂拼**（固化當前讀音並停留於組字狀態；標點前先固化）。
5. **不進行重切分**；**建立 copilot 未完成讀音窗**（見 §3.5）；**觸發注音文抑制**（v3：與拼音同；見 §7.4）。
6. 逐字選字模式（SCPC）下狂打**不生效**（沿用既有 `!prefs.useSCPCTypingMode` 條件）。

### 3.2 自動切音節之判準（本案之核心規格；**v5 依 P251 實測全文改寫**）

> **v5 改寫說明**：原文之第四問為「以 K 寫入其目標槽後之假想內容是否為讀音之前綴」。P251 以 11 個排列、29,579 個合法中途前綴、276,446 個交界實測，判其**不可用**：單音節誤切 12 次、交界漏切 **48.05%**，且**大千排列下鍵入 `ess`（＝ㄍㄋㄋ）只得一顆「ㄋ」**（§3.0 ★③ 之功能底線失效）。原文之依據「假想內容之字串」把動態排列**狀態相依**之效果壓扁成一個字串，此為其根本缺陷。**下列 v7 判準即本系列之權威規格**，實作見 `Tests/TekkonTests/TekkonTests_AutoChopPredicate.swift` 之 `shouldAutoChopZhuyin`。

設當前注拼槽為 `C`（`Tekkon.Composer`，值語義），本拍按鍵為 `k`。以值語義副本探得三份內容：

- `post` ＝ `C` 接收 `k` 後之四槽（聲／介／韻／調）；
- `emptyPost` ＝ **空注拼槽**接收 `k` 後之四槽（＝以副本探得「本鍵之固有語意」，**不需任何 Tekkon 新 API**）；
- `changed` ＝ `post` 與 `C` 相異之槽位集合。

**判準（六條，施工以此為準）**：

```
切音節 ⇔ ① C 非空
        ② k 非聲調鍵：emptyPost[調] 為空 且 changed 不含調槽
        ④a changed 為空                      ⇒ 切
        ③ 固有目標槽 S_new ≦ S_max           （不成立 ⇒ 不切）
        ④b′ 非「真實延伸」                    （成立 ⇒ 不切）
        ④d 非「本鍵自毀己產」                  （成立 ⇒ 不切）
        ④c 接續探針為否定                     （成立 ⇒ 切）

  S_max       ＝ 聲/介/韻 中最高已填槽之序（聲 1 ＜ 介 2 ＜ 韻 3；全空為 0）
  S_new       ＝ emptyPost 之首個非空槽之序；若 emptyPost 全空，退回 changed 之最低槽 ＋ 1
  真實延伸     ≔ 「post 之讀音字串」為合法前綴 ∧ 其長度 ＞ 「C 之讀音字串」之長度
  本鍵自毀己產 ≔ C 中被毀去之各槽值，恰等於 emptyPost 於同槽之值
  接續探針     ≔ isPrefix(C 之讀音字串 ＋ emptyPost[S_new] 之注音)
→ 成立時：以 phonabetKeyForQuery(pronounceableOnly: true) 取出 C 之內容、寫入組字器、
          清空注拼槽，然後才把本鍵送入。不成立時：照既有行為把本鍵送入注拼槽。
```

**逐條理由**：

| # | 條件 | 為何需要 | 缺它會怎樣（P251 實測） |
|---|---|---|---|
| ① | 注拼槽非空 | 空槽無可提交 | — |
| ② | 非聲調 | 聲調是**同一**音節之延續（含後置聲調覆寫），提交它會把該音節拆成兩半 | — |
| ④a | 零槽位變動 ⇒ 切 | 冗餘鍵＝新音節之始 | 缺它則 `ㄋㄋ`（靜態排列下第二擊不改槽值）永遠打不出第二顆；**實測：合法單音節編碼之 29,579 個中途前綴中此情形為 0 ⇒ 無誤殺之虞** |
| ③ | `S_new <= S_max` | 「新音節開始」之**必要**條件；且 `S_new` **必須取自 `emptyPost`** | 若取「實動之最低槽」，則動態排列之糾錯副作用（倚天26 `be`＝ㄐㄧ：鍵 `e` 寫介母 ㄧ之餘另把 ㄓ 糾正為 ㄐ）會使 ③ 失效 ⇒ 劉氏／倚天26 之糾錯型誤切 |
| ④b′ | 結果為合法前綴且更長 ⇒ 不切 | 同音節之**真實延伸**（補空槽、或長度增長之糾錯） | 缺它則 `ㄙㄥ` 之第二擊 `n`、`ㄆㄧㄚ` 之第三擊 `u`、劉氏 `ha` 之第二擊 `a` 皆誤切 |
| ④d | 本鍵所毀者恰為本鍵空槽產物 ⇒ 不切 | 動態排列之**逐槽覆寫**（`qquu`＝ㄅㄚ：首擊譯得 ㄆ、次擊覆寫為 ㄅ） | 缺它則大千26 `qquu`、`qqii`（ㄅㄞ）第二擊即被誤切 ⇒ 該排列之合法編碼不可打 |
| ④c | 接續探針 | 「新音節開始」之**充分**條件，亦為單聲母狂打之解藥 | 缺它則 `ㄍ`＋`ㄋ` 判「不切」、`ㄍㄋㄋ` 全滅 |

**四則對照實例（施工者以此自查）**：

| 輸入 | 關鍵條件 | 結果 |
|---|---|---|
| 大千 `e`（ㄍ）＋ `s`（ㄋ） | ④b′ 否（`ㄋ` 不長於 `ㄍ`）、④d 否（所毀 ㄍ ≠ `s` 之空槽產物 ㄋ）、④c 是（`ㄍㄋ` 非前綴） | **切** ⇒ 提交 `ㄍ`，新音節 `ㄋ` |
| 大千 `s`（ㄋ）＋ `s`（ㄋ） | ④a 是（`changed` 為空） | **切** ⇒ 提交 `ㄋ`，新音節 `ㄋ` |
| 大千 `1` `u` `0`（ㄅㄧㄢ） | 第三拍：④b′ 是（`ㄅㄧㄢ` 為合法前綴且更長） | **不切** ⇒ 全程零中途提交（保護欄） |
| 大千26 `q` `q` `u` `u`（ㄅㄚ） | 第二拍：④d 是（所毀 ㄆ 恰為 `q` 之空槽產物 ㄆ）；第四拍：④d 是（所毀 ㄧ 恰為 `u` 之空槽產物 ㄧ） | **不切** ⇒ 四拍合為一音節 |

**已知界線（P251 實測，明列而非隱藏）**：

| # | 界線 | 量 | 成因 | 處置 |
|---|---|---|---|---|
| 1 | 交界處之殘餘漏切 | 6,054／276,446 ＝ **2.19%**，**全在 5 個動態排列**（6 個靜態排列為 0） | 「A 之終態 ＋ 本鍵」與 `qquu` 之逐槽覆寫在**全部局部可觀測量上同構**（單槽改寫為不同值／所毀之值恰為本鍵空槽產物／本鍵與前拍同鍵／當前內容為完整讀音，四項逐一比對皆相同） | **P255 接受並記錄**。使用者之繞道為「以聲調或空格先行固化」——§3.1.3 已保證聲調語義不動。若日後有實機抱怨，再議「延遲一拍決定」之架構改動。 |
| 2 | 動態排列之「新音節首鍵」若與 A 之末鍵同鍵，該次切分可能不發生 | 界線 1 之子集 | 同上 | 同上 |
| 3 | 貪婪延伸之代價 | — | ③ 與 ④b′ 允許把完整讀音繼續延伸（`ㄓ`＋`ㄚ`＝`ㄓㄚ`） | 既有之已知代價，方向正確 |

**紅線（v5 新增）**：`S_new` **不得**取「本次實際變動之最低槽位」——此為 v4 原文之未定義處，P251 實測證明它會使動態排列之糾錯副作用破壞條件 ③。

### 3.3 為何 Tekkon 不自動 chop

`Composer` 是 `@frozen public struct`，且 `/` 之語義（`pinyinAutoChopResult` 僅回傳「預測」，實際 chop 由 handler 執行）已是本倉之既有分工。**注音沿用同一分工**：Tekkon 提供**判準所需之素材**（當前槽內容、目標槽位、前綴合法性），Handler 執行切分與寫入。

**紅線**：`Tekkon` **不得**新增任何知曉「狂打」概念之 API，亦不得在 `receiveKey` 內做任何自動提交。Tekkon 是無狀態偏好、無會話概念之音節組裝器，此邊界一破即為不可維護（§5.5）。

### 3.4 為何不沿用 `FuriousTypingSegmentor`

`FuriousTypingSegmentor` 之 DP 以「字母流之位置切分」為搜尋空間，其輸入是 `furiousTrail.joined()`（`InputHandler_FuriousResegmentation.swift:378`）——**無分隔之連寫字串**。注音鍵流**不具此性質**：每一鍵已由排列與槽位型別唯一決定其歸屬，故「切分」不是搜尋問題而是判定問題。

若硬要沿用，須先構造一個「注音鍵流之無分隔字串」——但該字串在注音內**根本不存在**（排列對若干鍵是一對多、且依賴槽狀態），構造它的成本高於直接判定。**故不沿用，且不動 segmentor 一行**（§0.2 ★②）。

### 3.5 copilot 窗與 `unfinishedReading` 之處理（**已依事主異議改版**）

> 初稿曾主張「注音狂打不需要 copilot 窗，因使用者打出的注音符號本身即為讀音」——**該主張已被事主之「ㄍㄋㄋ」一例推翻**（§3.0）。注音狂打**需要** copilot 窗，且其必要性有三層：① **縮寫／逐字打法**（ㄍㄋㄋ、ㄋㄋ、ㄓㄓ…）之讀音序列由多個單符號音節組成，只有 copilot 窗能把它們拼起來顯示；② **完整讀音之逐字組句**（`ㄍㄢˋ-ㄋㄧˇ-ㄋㄧㄤˊ` → 「幹你娘」）與**整鍵詞條**（`ㄍㄡˇ-ㄋㄢˊ-ㄋㄩˇ` → 「狗男女」）皆須候選窗才可見——**此二者為事主所舉之正例**（§3.0.1 之 v3 表）；③ 拼音側既有之 copilot 機制（交叉邊界詞、POM 前置、就地選字）本身即是狂打模式之核心價值，注音沒有理由自外。

**故本案之決定**：**為注音狂打開啟 copilot 窗**。作法是把 `hasFuriousFrontPending` 對注音之語義訂為 **`!composer.isEmpty`**——與拼音之 `!composer.romajiBuffer.isEmpty` 同構（皆為「注拼槽內尚有未固化之讀音素材」）。

```swift
public var furiousFrontUnfinishedReading: String? {   // v12 新增：顯示源即判準之唯一正本
  guard isFuriousTypingModeEffective else { return nil }
  switch typingMode {
  case .pinyinFuriousTyping:
    let romaji = composer.romajiBuffer
    return romaji.isEmpty ? nil : romaji
  case .zhuyinFuriousTyping:
    // v12 更正：非「!composer.isEmpty」——純聲調槽非空、卻無讀音可示。
    guard composer.isPronounceable else { return nil }
    let zhuyin = composer.getComposition(isHanyuPinyin: false)
    return zhuyin.isEmpty ? nil : zhuyin
  default:
    return nil
  }
}

public var hasFuriousFrontPending: Bool { furiousFrontUnfinishedReading != nil }
```

> **v12 事實更正（P256 實作時查得；本節初稿之兩處斷言為誤）**：
>
> ① **「`isFuriousCopilotCandidateWindowVisible` 不需改——閘一改即通」為誤。** `State.ofInputting(displayTextSegments:cursor:)` 起手之 `candidates` **為空**（`IMEStateProtocolAndData.swift:48–60`），而 `isCandidateContainer` 對 `.ofInputting` 之定義即 **`!candidates.isEmpty`**；該狀態之候選只有兩個寫入者——**狂打之前方候選清單**（`buildFuriousFrontCandidates`）與**磁帶快選**（`Typewriter_Cassette.swift:79／117`）。故**只改閘門則注音側之窗永遠不會開**。**處置**：`furiousFrontContext`（`InputHandler_HandleStates.swift`）之讀音桶改依注拼槽之鍵盤家族分流——拼音側由字母流反推注音音節、注音側之未完成音節**本身即讀音**（逕行展開聲調變體）；下游全段（組字器副本試算、主段／越界擷取、橫跨節點偵測、候選排序）為語言中立之鍵值運算、**一字未改** ⇒ 注音側免費取得置頂組句預覽、跨邊界詞、前方單音節查詢。
>
> ② **注音分支之 `!composer.isEmpty` 過寬。** 注拼槽內**只有聲調**（先敲 `3`＝ˇ、尚無聲介韻）時 `isEmpty` 為假、而 `getComposition()` 為 `"ˇ"` ⇒ 窗會在**無讀音可示**時開啟，且其讀音桶會由該聲調槽生成 `["ˇ","ˇˊ",…]` 一類垃圾鍵。**處置**：改以 **`isPronounceable`** 為閘，並把「旗子」與「顯示源」**收斂為同一判準**（旗子即「顯示源非 nil」）。

**連帶效果（已於 §八 Phase 256 逐一驗證）**：

| 項 | 處置 |
|---|---|
| `isFuriousCopilotCandidateWindowVisible`（`SessionCoreProtocol.swift:196–199`） | **本身不需改**（其定義已是三項之合取）——**惟「閘一改即通」為誤**（見上之 v12 更正 ①）：`.ofInputting` 之候選另有來源，注音側須先補**讀音桶** |
| 其餘 5 個 `hasFuriousFrontPending` 讀取點（`Typewriter_BPMFFullMatch.swift:52／56`（Shift＋選字鍵就地選字）、【P260 新址】`:65`（Enter 固化）；`InputHandler_TriageInput.swift:30`（固化後之空格消費）、`:49`（Tab）；`InputHandler_HandleStates.swift:271`（就地確認）、`:813`（標點前固化）） | **皆為所欲**：注音狂打悉數沿用。**v12 補述**：`solidifyFuriousFrontReading` 原以 `guard !romaji.isEmpty` 起手 ⇒ 注音側**靜默退回**，故本列之前提是「固化函式須一併補注音分支」（已補）；另 `TriageInput` 之標點讀取點在**大千排列下不經 `,`**（`,` 是注音符號鍵ㄝ，走自動切音節） |
| `unfinishedReading`（`InputSession_Delegates.swift:204–208`） | **須改**：其現行實作取 `inputHandler?.composer.romajiBuffer`（拼音專屬），注音下恆空。改為依 `typingMode` 分流。**v12 補述**：分流之實作**上移至 `InputHandlerProtocol.furiousFrontUnfinishedReading`**，session 與 mock 皆只轉發 ⇒ 判準不再有兩份 |
| `CtlCandidateProtocol.unfinishedReading`（`:38`）之協定形狀 | **不動**（本來就是 `String?`） |
| `MockSession.unfinishedReading`（`Tests/…/MockedInputHandlerAndStates.swift:127–135`） | **須同步改**（其註解已自陳「與生產端 `InputSession_Delegates` 對應」）；測試須釘住注音下之回傳值。**v12 補述**：實際作法是讓它與生產端**逐字相同**（皆為一行轉發），而非各自重寫一遍 |
| `confirmFuriousFrontCandidate`（`HandleStates.swift:266` 起；由 `InputSession_Delegates.swift:352` 之 `.ofInputting` 分支可達） | **v10 補列、v12 落實**：注拼槽之清空與還原原為拼音專屬（`romajiBuffer` ＋ `replacePinyinBuffer`，後者對非拼音模式是 no-op）⇒ 改為**整體快照／還原**（`let composerBackup = composer` ／ `composer = composerBackup`）。拼音側等價且更忠實 |
| tooltip 回顯（`HandleStates.swift:466–469`：`result.tooltip = composer.romajiBuffer`） | **不動**。該行有 `furiousContext != nil \|\| (furiousContext == nil && furiousAbbreviatedCells != nil)` 之前提，注音不滿足（`furiousAbbreviatedCells` 是拼音簡拼；且注音之讀音已在組字區讀音欄）⇒ 自然不觸發 |
| 組字區讀音欄（`readingForDisplay` → `inlineReadingPreview`） | **不動**。`InputHandler_CoreProtocol.swift:613` 之 `guard !prefs.cassetteEnabled, !composer.isPinyinMode` 本即為注音準備了正確路徑 |

> **與初稿之淨差異**：`hasFuriousFrontPending` 由「注音恆 `false`」改為「注音 ＝ 注拼槽內有未完成音節」，並因此多出三項實作（**前方讀音桶之注音分支**、`unfinishedReading` 之分流、`solidifyFuriousFrontReading` 與 `confirmFuriousFrontCandidate` 之通用化）與四個新測試靶。**代價小、收益是整個單聲母狂打能力**。

---

## 四、Tekkon 側之 API 設計

### 4.1 為何需要新 API

`Composer` 現有之公開表面（實查，`Tekkon_SyllableComposer.swift`）足以回答「當前槽內容是什麼」（`value`／`getComposition()`）、「可不可以唸」（`isPronounceable`）、「可否查詢」（`phonabetKeyForQuery`），**但不足以回答**：

- 「`ㄅㄧ` 是否為某合法讀音之前綴？」（§3.2 條件 ④；**此為單聲母狂打之唯一判準**——`ㄍㄋ` 非前綴 ⇒ 提交 `ㄍ`，見 §3.0.2）
- 「`ㄅㄧ` 本身是否已是完整讀音？」
- 「以 `ㄅㄧ` 開頭之合法讀音有哪些？」（供前綴之後綴展開。**注音狂打之 copilot 窗已定案要開**（§3.5），但**不**由此列舉驅動——驅動它的是組字器之既有跨鍵詞查詢（如 `ㄍ-ㄋ-ㄋ`），故本項仍非本輪之必需）

且既有之 `MandarinParser.allPossibleReadings`（`Tekkon_Phonabets.swift:85–103`）**不可**用於此：其對注音排列回傳 **2562** 條字串，是「427 讀音詞幹 × 6 種聲調後綴」之乘積，**每條皆帶聲調後綴**，故對「`ㄅㄧ` 是否為前綴」之 `hasPrefix` 判定會產生大量偽陽性（`ㄅㄧㄢˊ` 以 `ㄅㄧ` 開頭，但 `ㄅㄧˊ` 亦然，而使用者敲的是無調之 `ㄅㄧ`）。**且該集合之唯一呼叫者是 `PinyinTrie` 之建構子**（`Tekkon_PinyinTrie.swift:24`）——為注音排列建 `PinyinTrie` 是無意義的（其 trie 恆為空，`mapZhuyinPinyin == nil`）。

### 4.2 資料規模（實測）

以 `Tekkon.mapHanyuPinyin`（`Tekkon_Constants.swift:249`，**426** 條；原 427，`"q"` 條目已刪）之 value 為注音詞幹，逐一展開其全部非空前綴：

| 量 | 值 |
|---|---|
| 拼音條目數 | **426**（v8 更正；原 427） |
| 相異注音詞幹數 | **426**（v8 更正；原 427） |
| 相異非空前綴數 | **442**（不變） |
| 其中「本身即完整讀音」 | **426**（v8 更正；原 427） |
| 其中「嚴格前綴（不完整但合法）」 | **16**（v8 更正；原 15） |
| 全部前綴字串之 UTF-8 位元組數 | 約 **3,069** |
| 詞幹長度分佈 | 1 字：**23**；2 字：227；3 字：176（v8 更正；原 1 字：24） |
| 最長詞幹 | 3 個注音符號（如 `ㄔㄨㄤ`、`ㄐㄩㄥ`） |

**16 條嚴格前綴之全表**（v8 更正；原 15 條）：`ㄅ ㄆ ㄇ ㄈ ㄈㄧ ㄉ ㄊ ㄋ ㄌ ㄍ ㄎ ㄎㄧ ㄏ ㄐ ㄑ ㄒ`。
（皆為聲母；`ㄈㄧ`／`ㄎㄧ` 之所以成為嚴格前綴，是因 `ㄈㄧㄠ`／`ㄎㄧㄡ`／`ㄎㄧㄤ` 這幾個音節無對應之完整詞幹。**此 15 條即「打了半截之注音」之全部可能**。）

> **註（v5 全文改寫——P251 實測推翻了原文之數字與理由）**：原文記「動態排列測試資料內之相異無調詞幹為 **439** 條，439 ＞ 427 之差（12 條）係該表納入若干『無獨立完整詞幹、僅以聲母形出現』之音節所致」。**實測結果與此不符**：
>
> | 量 | 原文 | 實測 |
> |---|---|---|
> | 測試資料之相異無調詞幹 | 439 | **422** |
> | 與 427 之交集 | （未載） | **422**（＝全部） |
> | 「只在測試資料」者 | 12 條 | **0 條** |
> | 「只在字典」者 | （未載） | **5 條**：`ㄈㄨㄥ`(fong)、`ㄍㄧ`(gi)、`ㄍㄨㄜ`(gue)、`ㄎㄧㄡ`(kiu)、`ㄘㄟ`(cei) |
>
> **439 之成因**：測試資料以 `_` 代記空格（＝陰平），如 `ㄔ_`、`ㄕ_`、`ㄛ_`、`ㄞ_` 等 **17 列**。若未先把 `_` 正規化為空格再剝調，這 17 列便被當成 17 個獨立詞幹 ⇒ `422 + 17 = 439`。**故落差不是「該表多收了 12 條聲母形音節」，而是「少剝了 17 個調記」；且差集之方向與原文所稱相反——是測試資料少了 5 條，不是多了 12 條。**
>
> **對 Phase 252 之定案**：`SyllableIndex` **以 `mapHanyuPinyin` 之 value 為唯一來源，可行且完足**——測試資料之 422 條無一落在 427 之外。原文所建議之「另立一則斷言」已於 P251 落地，且結論**強於**原設想：**422 條全部皆為 427 之成員**（無一僅為前綴）。

**單符號讀音之處置（★ 依 §3.0 之新證據修訂）**：`SyllableIndex` 之**語意定義為「多數派之漢語音節」**（427 條詞幹 ＋ 15 條嚴格前綴 ＝ **442**），故 `isComplete("ㄍ") == false`（`ㄍ` 非獨立音節，僅是 `ㄍㄚ` 一族之嚴格前綴）。**但原廠辭典確實收錄 21 個單聲母與 16 個單韻母之讀音鍵**（§3.0.1 實查），且 `ㄍ` 恰在 15 條嚴格前綴之列 ⇒ `isPrefix("ㄍ") == true`、`isPrefix("ㄋ") == true`。

**單符號前綴之全貌（v6 補註、v8 更正，P252 實測）**：37 條單符號前綴恰等於引擎三音素表之聯集（`allowedConsonants` 21 ＋ `allowedSemivowels` 3 ＋ `allowedVowels` 13）——此為對索引派生之獨立交叉驗證。其內部再分為 **23 條完整讀音**（`ㄓ ㄔ ㄕ ㄖ ㄗ ㄘ ㄙ` ＋ `ㄧ ㄨ ㄩ` ＋ 13 韻母）與 **14 條嚴格前綴**（`ㄅ ㄆ ㄇ ㄈ ㄉ ㄊ ㄋ ㄌ ㄍ ㄎ ㄏ ㄐ ㄑ ㄒ`）。**`ㄑ` 已自完整讀音退回嚴格前綴**（原 24／13 分裂 → 23／14）。

> **★ `mapHanyuPinyin` 之單字母條目（v6 查得、v7 經事主覆核後更正、v8 已裁定刪去 `q`）。**
>
> **處置（v8，事主裁定）**：`"q": "ㄑ"` 已自 **`Tekkon.mapHanyuPinyin`** 與 **`LexiconAssembly` 之內嵌表 `jsnHanyuPinyinToMPS`** **兩處同步刪去**；單字母條目自此**僅餘 `a`／`e`／`o` 三條真音節**。**未動者**：`LexiconAssembly` 之音素↔ASCII 雙射表 `charPhonabet4ASCII`（`"q": "ㄑ"` 在那裡是**結構必需**——每個音素皆須有一個專屬 ASCII 字元）、以及 `Tekkon_Constants` 之各鍵盤排列表（`q` 鍵在那些排列下確實輸出 ㄑ）。**亦未動** `arrPhonaToHanyuPinyin`——那是**方向相反**之顯示用表，21 個聲母之單字母條目齊全。
>
> **刪去之收益**：狂拼之**簡拼（α）路徑**於 `q` 起首之緩衝上回復可達——原先 auto-chop 會在第二鍵即搶走本拍（`performPinyinAutoChopIfNeeded` 先於 `autoApplyFuriousAbbreviationIfClearWinner` 執行）。實測（以單字母為緩衝、遍歷 26 個第二鍵）：`q` **24／26**、`a` 24／26、`o` 24／26、`e` 23／26 會觸發自動切音節，而 `b`／`z`／`j` 為 **0／26**。對 `a`／`e`／`o` 而言「打一個 `a` 就切出 ㄚ」是音節事實所支持之行為，故保留；對 `q` 則不然，故刪去後 21 個聲母之行為歸於一致。
>
> **刪去前之事實（保留為記錄）**：該表之單字母鍵曾恰為 `a`／`e`／`o`／`q` 四條，其值為 `ㄚ`／`ㄜ`／`ㄛ`／`ㄑ`。前三者為合法之漢語拼音音節，`q` 不是（`qi` 才是，且 `mapHanyuPinyin["qi"] == "ㄑㄧ"` 另有條目）；其餘 20 個聲母皆無單字母條目。**它並非筆誤**——同四條亦被獨立複製到 `LexiconAssembly` 之內嵌表（該模組檔頭自陳「使得 LXAssembly 擺脫對 Tekkon 的依賴」），可見是有意之提供。**其三條消費路徑**：① 輸入解碼（`Composer.receiveSequence(_:isRomaji:)`）；② 拼音→注音之轉換（`Tekkon.cnvHanyuPinyinToPhona`）；③ 辭典讀音之正規化（`String.convertToPhonabets`，走內嵌 JSON）。
>
> **而「顯示」從未經過此表**：偏好 `kShowHanyuPinyinInCompositionBuffer`（zh-Hant 文案即「**拼音並擊**（組字區內顯示漢語拼音）」）之顯示轉換走的是**方向相反**之 `Tekkon.cnvPhonaToHanyuPinyin` → `arrPhonaToHanyuPinyin`（注音 → 拼音）。
>
> **對注音自動切音節判準（v7）之影響：零。** v7 只用注音字串之 `isPrefix`，而 `ㄑ` 無論該條目存在與否皆為前綴（`ㄑㄧ` 等之故）。惟刪去後 `isComplete("ㄑ")` 由真轉假——此為**更正確**之狀態：`ㄑ` 本即非漢語音節。

**故 `SyllableIndex` 之用途界定為**：只服務 §3.2 條件 ④ 那**一問**——「此串是否還可能延伸成合法讀音」。**它不負責「此串在辭典內有無詞條」**，那由 `assembler` 之查詢鏈（`currentLM.lxQuerier.hasGrams(for:)`）回答，兩者職責分明、互不替代。

**兩項由此而來的施工紅線**：

| # | 紅線 | 理由 |
|---|---|---|
| 1 | **不得**把 `SyllableIndex.isComplete(_:)` 當作「可否提交」之依據 | 否則單聲母狂打全滅（§3.0 之初稿錯誤即源於此）。「可否提交」之依據是 §3.2 之三條件 ＋ 第四問（**其第四問對單符號前綴為假** ⇒ 得提交） |
| 2 | **禁止**為了涵蓋單符號而把 37 個單符號硬塞進 `SyllableIndex.allReadings` | 那會使 `isComplete("ㄍ")` 為真，進而讓 §3.2 條件 ④ 對 `ㄍ` 之外推失真；且會使「427」這個可稽核數字失去意義。單符號之合法性是**辭典之事實**，不是**音節表之事實** |

### 4.3 建議之 API 形狀

**新增型別**：`Tekkon.SyllableIndex`（`public struct`，`Sendable`），置於**新檔** `Sources/Tekkon/Tekkon_SyllableIndex.swift`。

```swift
extension Tekkon {
  /// 注音／拼音音節之唯讀前綴索引。
  ///
  /// 由 `Tekkon.mapHanyuPinyin` 之 426 條注音詞幹派生（含其全部非空前綴，共 442 條）。
  /// **僅為查詢結構，不含任何排列、會話或偏好狀態**——排列相關之判定一律留在 `Composer`。
  public struct SyllableIndex: Sendable {
    public static func shared(for parser: MandarinParser) -> SyllableIndex

    /// 該字串是否為某合法讀音之完整形式。
    public func isComplete(_ reading: String) -> Bool
    /// 該字串是否為某合法讀音之非空前綴（含其本身即完整者）。
    public func isPrefix(_ reading: String) -> Bool
    /// 以該字串為前綴之全部完整讀音（升冪，內容穩定）。
    public func completions(of prefix: String) -> [String]

    /// 全部完整讀音（426 條；升冪）。供測試與防漂移比對。
    public static var allReadings: [String] { get }
  }
}
```

**與本節之出入（v6：P252 完工回檢，三處，皆為縮小或補明）**：

| # | 本節原文 | P252 實作 | 理由 |
|---|---|---|---|
| 1 | `public static func shared(for parser: MandarinParser)` | **`shared(parser:)`**（去 `for`） | 本節設計要點 #3 明言「共用作法照 `PinyinTrie.shared(parser:)`」；Tekkon 內不應出現第二種共用存取器之標籤風格。語意不變 |
| 2 | 只列 `public static var allReadings` | **另加 `public let readings`** | 靜態版為「排列中立之正本」，實例屬性為「本索引持有之表」；今日二者恆等（已由測試釘住），未來若真有排列專屬讀音集才會分岔 |
| 3 | `public func completions(of prefix: String)` | **`internal`** | 依 §8.3（v5）之裁定：v7 判準只用 `isPrefix`，今日無生產端消費者，故不預先承諾此 API 之形狀 |

**實作要點之補註（v6）**：快取為**單一實例**（`nonisolated(unsafe) private static var sharedCache: SyllableIndex?`），**不照搬** `PinyinTrie` 之「以 `parser.rawValue` 為鍵逐排列一份」——因注音是排列中立之表記，427 條詞幹對所有排列相同（本節設計要點 #1 之明文）。已由測試 `sharedIndexIsParserNeutral` 釘住。

**設計要點**：

| # | 要點 | 理由 |
|---|---|---|
| 1 | **無狀態、與排列無關** | 426 條詞幹對**所有**排列相同（注音是排列中立之表記）。以 `parser` 為參數是為了**保留未來之擴充位**（若某排列真有專屬讀音集，屆時不必改簽名）；實作上所有排列共用同一份索引。 |
| 2 | **`completions(of:)` 為升冪、內容穩定** | 沿用 `PinyinTrie.zhuyinReadings` 之既有紀律（`:291`：`Array(Set(expanded)).sorted()`），以保證測試可斷言。 |
| 3 | **共用作法照 `PinyinTrie.shared(parser:)`** | 同一模式：`NSLock` ＋ `nonisolated(unsafe) private static var` 快取（`Tekkon_PinyinTrie.swift:83–110`），並提供 `clearSharedCache()` 供測試。**不新增第二種快取範式。** |
| 4 | **索引本體用 `Set<String>`，不用 Trie** | 442 條字串、查詢只有「成員資格」與「前綴列舉」兩種；`Set` 之 O(1) 成員查詢勝過 Trie 之逐字元走訪，且無自訂資料結構之維護成本。`completions(of:)` 以 `allReadings.filter { $0.hasPrefix(prefix) }` 實作（427 條線性掃描，**非熱路徑**——只在前綴不完整時才需列舉）。 |
| 5 | **不觸碰 `PinyinTrie`、不觸碰 `Composer`** | 純新增檔；`Tekkon_SyllableComposer.swift` 於 Phase 252 **零改動**（唯一例外見 §4.4）。 |

### 4.4 `Composer` 側需新增者（**v5 降級：由「必需」改為「非必需」**）

> **v5 改寫說明**：原文主張「§3.2 之最終判準需要『本鍵譯得之目標槽位』，而 `Composer.translate(key:)` 是 `internal mutating`，故須新增一個 `public` 唯讀探針 `incomingPhoneType(forKey:)`」。**P251 之實測推翻了此推論**：v7 判準所賴之全部素材——`isEmpty`、四槽之 `public internal(set)` 值、**值語義副本上之 `receiveKey(fromScalar:)`**、`getComposition()`、`phonabetKeyForQuery(pronounceableOnly:)`——**皆為既有之 `public` API**；P251 之參考實作 `shouldAutoChopZhuyin` 即以此寫成、未動 Tekkon 一字。**故該探針非必需。**

**原文之設計（保留為備案，不再主張）**：

```swift
extension Tekkon.Composer {
  /// 本鍵若被接收，將寫入之槽位型別；`nil` 表該鍵非本排列之可用鍵。
  public func incomingPhoneType(forKey key: String) -> Tekkon.PhoneType?
}
```

**v5 之裁定**：`incomingPhoneType(forKey:)` **不列入 P252 之交付**。理由有三：① 可由既有 public API 以兩次值語義複製達成，成本為常數級小字串操作；② 新增 API 即新增需永久維護之表面積，且其實作本身（`var probe = self; probe.receiveKey(...)` 後比對四槽）與呼叫端之手寫版本並無二致；③ §3.3 之紅線要求 Tekkon **不得**知曉「狂打」概念，而「固有目標槽」正是狂打判準之概念——把它升為 Tekkon 之公開 API 反而模糊了該邊界。

**替代方案（原文所列，現已成唯一案）**：由 Handler 以值語義副本試跑候選流程。原文曾以「會把 Tekkon 內之槽位語義洩漏到 Handler 內」為由不主張此案；惟 P251 證明該「洩漏」在 v7 之寫法下僅是「讀四個公開屬性」與「對副本呼叫一次公開方法」，**不構成實質洩漏**。

**若 P252 仍決定新增該探針**：須於該 phase 之記錄內明寫「與 P250 §4.4（v5）之出入及其理由」，並以本節之 P251 實測數據為據。

### 4.5 明確**不**做者（本輪）

| # | 不做 | 理由 |
|---|---|---|
| 1 | 動態注音排列之「讀音 → 按鍵序列」反向表 | 引擎內不存在；唯一真相在測試資料內。建成正式表即等於**把測試資料升格為規格**，而該資料是**既有行為之錄影**、非規格（§五.1、§五.2） |
| 2 | 動態注音排列之「當前可敲哪些鍵」查詢 | 需要「正向 key → phonabet」之**純函式**化，而 `handleETen26`／`handleHsu` 等**不是純函式**（它們依賴並改寫整個槽狀態、且有 `receiveKey` 之副作用）。真要提供，唯一不失真之方式是**逐鍵模擬**（§五.4） |
| 3 | 把 `translate(key:)` 拆成「純翻譯」與「副作用」兩段 | 表面上很誘人（可望一次解決 #2），但五支 handler 之語意**本即**與槽狀態交纏（此為動態排列之定義），硬拆會在 handler 內製造出「半套狀態」之新概念。風險與收益不成比例 |
| 4 | 把 442 條前綴索引升格為 Trie | 見 §五.3 |

---

## 五、事主存疑之答覆：動態注音「窮舉成 Trie」是否值得

### 5.1 現況事實（實查）

| 事實 | 數據 | 出處 |
|---|---|---|
| 動態注音排列之數目 | 5（`.ofDachen26`／`.ofETen26`／`.ofHsu`／`.ofStarlight`／`.ofAlvinLiu`） | `Tekkon_Phonabets.swift:51–71` |
| 讀音 ↔ 按鍵對照之**引擎內** API | **不存在**（正向為程序式解碼；反向無） | `Tekkon_SyllableComposer.swift:601–629`；`grep` 全倉零命中的反向表 |
| 逐鍵解碼之熱路徑 | `translate(key:)` 於**每次注音按鍵**執行；`inputValidityCheck(charStr:)` 至少每鍵一次 | `:246`；【P260 新址】`Typewriter_BPMFFullMatch.swift:251` |
| 唯一之全量對照 | 測試資料 `TestAssets_Tekkon/Tekkon_TestData.swift`：**1485** 行 × 5 排列；扣除 59 個 `` `NULL `` 單元後**已斷言 7366 筆** | 該檔 `:5–1492`；`TekkonTests_Arrangements.swift:218–246` |
| 該表之相異無調詞幹 | **422**（v5 更正；原記 439 係 `_` 未正規化之誤算，見 §4.2） | 本文實測（P251 複核） |
| 該表之（情境無關之）相異按鍵序列 | **5888** 條、19658 字元、**6072** 相異前綴 | 本文實測 |
| 若為單一排列之按鍵序列建 Trie，節點數 | Dachen26 **1620**、ETen26 **1551**、Hsu **1557**、Starlight **1550**、AlvinLiu **1553** | 本文實測 |
| 該表是否為規格 | **否**。其為既有行為之錄影；且**59 個 `` `NULL `` 單元**明文承認「某些讀音在某些排列下打不出來」 | `TekkonTests_Arrangements.swift:107` |

### 5.2 為何「窮舉成 Trie」之正面價值有限

**① 需要的問題只有兩個，而它們不需要 Trie。** 注音狂打實際要問的只有「這串注音符號是不是某讀音之前綴」（§3.2 條件 ④）與「它本身是否已完整」。前者以 `Set<String>` 之成員查詢即可 O(1) 回答；後者亦然。**Trie 的獨門本事是「列舉下一步」**——而在 §4.5 #2 未實作之前，無人要問這個問題。

**② 真正的那個 Trie 不可能是靜態的。** 若真要做「當前可敲哪些鍵」，其真相來源是**五支依賴槽狀態之 handler**，不是五份 key→phonabet 的靜態表（後者明文「未包含全部的映射內容」）。要以靜態 Trie 覆蓋，唯一的辦法是**逐鍵模擬既有 `Composer` 走遍所有路徑**——這在技術上完全可行（見 §5.4），但它產出的是**實作之導出物**，而非一份可獨立審閱之規格。

**③ 於是維護成本是雙份。** 一旦該 Trie 成為正式資產，任何 `handleETen26`／`handleHsu`／`commonFixWhenHandlingDynamicArrangeInputs` 之修改都**必須**連帶重新生成並複驗該 Trie；而「生成器忘了跑」是本倉屢見之失效模式（`assets/userdef-metadata.json` 與 `assets/settings-surface.json` 皆為同型之生成物，皆須靠 Makefile 之 `cmp` 擋漂移）。**在沒有任何消費者之前，先引入一個需要漂移守衛之生成物，是純負債。**

**④ 而它會把「測試資料」錯升為「規格」。** `Tekkon_TestData.swift` 是**錄影**：它記錄的是「某日之實作在這 1485 個讀音上給出什麼按鍵序列」。若把它 tokenize 成 Trie 並讓生產碼查詢之，則該錄影內**任何既有瑕疵**都會被固化為規格，且日後修 handler 反而會「弄壞規格」。此與本倉「測試不得反向定義生產行為」之精神相悖。

### 5.3 那麼，取代方案是什麼

| 需求 | 本案之答覆 | 成本 |
|---|---|---|
| 「打了半截之注音是否可能成音」 | `SyllableIndex.isPrefix(_:)`（442 條） | 約 3 KB 字串 ＋ 一個 `Set` |
| 「它是否已完整」 | `SyllableIndex.isComplete(_:)` | 同上 |
| 「以它開頭之讀音有哪些」 | `SyllableIndex.completions(of:)`（線性掃描 427 條，非熱路徑） | 同上 |
| 「動態排列下，下一步可敲哪些鍵」 | **本輪不做**；若日後要做，採 §5.4 | — |
| 「現行 5 個排列之 7366 筆編碼是否仍正確」 | **既有測試已足**（`testDynamicKeyLayouts` ＋ `testDynamicLayoutsCorpus`）。本案**不動**它，僅另加一則**對稱性斷言**（§4.2 註） | 一則測試 |

### 5.4 若日後真要做「動態鍵盤之可敲鍵集」：建議路徑（本輪不實作）

**原則**：**由既有 `Composer` 模擬派生（simulation-derived）**，而非另立對照表；**且置於 `LibVanguard` 而非 Tekkon**。

```
演算法（草案）：
  輸入：當前 Composer 狀態 c、排列 p
  輸出：[(key, resultingPhoneType)] 之集合
  步驟：
    1. for key in p 之全部可敲鍵（≈ 40–45 個；由既有 11 份鍵盤表之鍵集聯集得出）：
    2.   var probe = c; guard probe.receiveKey(fromString: key) else { continue }
    3.   若 probe 之槽內容通過「合法性」檢查（SyllableIndex.isPrefix）則收錄
    4. 去重、排序
```

**為何置於 `LibVanguard`**：此查詢之消費者必然是 UI／FSM（動態鍵盤顯示、狂打之合法性提示），而 `Tekkon` 之既有紀律是「不知曉會話與偏好」。且此函式只用到 `Composer` 之 public 介面（`receiveKey` 之 `@discardableResult Bool` ＋ 四槽 ＋ `getComposition()`），不需 Tekkon 讓步任何邊界。

**量化**：每鍵一次複製 ＋ 一次 `receiveKey`；單次查詢 ≈ 40 次此等操作。若此查詢只在「鍵盤佈局重繪」時呼叫（而非每鍵），成本完全可忽略。**故「是否值得」之判準不是算力，而是「有沒有消費者」**——目前沒有。

### 5.5 一句話結論（供事主覆核）

> **不必為動態注音建 Trie。** 狂打所需者是一個 442 條之前綴集合（約 3 KB、零維護）；Trie 的獨門本事（列舉下一步）在沒有「動態鍵盤高亮／限制可敲鍵」這個消費者之前是空轉，而它一旦成為正式資產，就會把一份**錄影式測試資料**升格為**規格**，並替 `handleETen26` 一類高度情境相依之程式碼添上第二份必須同步的真相。**故 Tekkon 不承擔此職能**；日後若真有消費者，正確的做法是「以既有 `Composer` 模擬派生」而非「建表」，且該派生程式碼應落在 `LibVanguard`。

---

## 六、偏好層之設計

### 6.1 `UserDef` 之變更

**現況**（`UserDef.swift`）：

| 項 | 值 |
|---|---|
| case | `kFuriousTypingEnabled`（`:62`）（v9：`allCases` 之基線為 **117**，非下段所言之 118） |
| rawValue | `"FuriousTypingEnabled"` |
| `dataType` | `.bool(true)`（`:670`） |
| `metaData` | `:971–974`，引用 `i18n:UserDef.kFuriousTypingEnabled.{shortTitle,description}` |

**目標**：

| 項 | `…4Pinyin` | `…4Zhuyin` |
|---|---|---|
| case | `kFuriousTypingEnabled4Pinyin` | `kFuriousTypingEnabled4Zhuyin` |
| rawValue | `"FuriousTypingEnabled4Pinyin"` | `"FuriousTypingEnabled4Zhuyin"` |
| `dataType` | `.bool(true)`（**承接既有預設**） | `.bool(false)`（**新功能、預設停用**） |
| `metaData` | 沿用既有兩條 i18n 鍵（隨 case 更名） | 新增兩條 i18n 鍵 |
| 交換格式 | 不在黑名單內（可匯出匯入） | 同左 |

**命名理由**：rawValue 之 `4` 後綴為本倉既有之**分流慣例**（`KeyboardParser4Pinyin`／`KeyboardParser4Zhuyin`，`UserDef.swift:34–35`）。用同一慣例可讓「同族兩鍵」在 `Localizable.strings` 之全域排序內相鄰（實測：`…Enabled4Pinyin`／`…Enabled4Zhuyin` 排於 `…Enabled` 之後、`kHalfWidthPunctuationEnabled` 之前），亦讓 `dump-userdef-metadata` 之輸出可肉眼歸族。

**case 宣告之位置**：`UserDef.swift:62` 改為兩行（`4Pinyin` 在前、`4Zhuyin` 在後）。該 case 區塊（`:18–141`）**非**字母序，故無需重排。

### 6.2 Swift 端符號：全量更名，不留別名

`prefs.furiousTypingEnabled` 現有 **141** 處測試引用 ＋ **5** 處生產引用（`Sources/`）＋ **2** 處 `PrefMgrProtocol`／`PrefMgr_Core` 宣告；另 `SettingsUI` 2 處、`LXFacade` 1 處。

**決定：全量更名為 `furiousTypingEnabled4Pinyin`，並新增 `furiousTypingEnabled4Zhuyin`；不留 `furiousTypingEnabled` 之別名。**

| 方案 | 優 | 劣 | 裁定 |
|---|---|---|---|
| 留別名（`var furiousTypingEnabled: Bool { get { furiousTypingEnabled4Pinyin } … }`） | 改動小（約 150 處免動） | 一個 `rawValue` 是 `…4Pinyin` 之偏好卻名為 `furiousTypingEnabled`——正是本案要消滅之 disambiguation 債；且日後必有人以為它是「總開關」而寫出 `if furiousTypingEnabled` 之錯誤 | **否** |
| 全量更名 | 名實相符；`grep furiousTypingEnabled` 之結果即為完整清單 | 一次機械式大改（約 150 處，其中 141 處為測試） | **採** |

**測試之機械式更名須注意**：`InputHandlerTests_Cases1.swift` 之 137 處皆為 `testHandler.prefs.furiousTypingEnabled = …` 之**同型賦值**，故以逐字取代 `prefs.furiousTypingEnabled` → `prefs.furiousTypingEnabled4Pinyin` 即可；CJK 緊鄰變數之陷阱不適用（此處為 ASCII），但**仍須以 `git diff --stat` 覆核改動數與預期相符**。**建議落點**：Phase 253 內一次完成，並於該 phase 之驗收內跑滿 `swift test`（兩倉各自、不並行）。

### 6.3 資料遷移

**落點**：`PrefMgr_Core.swift` 之 `migrateDeprecatedSettings()`（`:516`）之**末段**（緊接既有之 `UsingHotKeyHalfWidthASCII` 段之後）。**逐字照**該段之成例（`:573–578`）：

```swift
// 遷移舊設定：狂拼 pref 更名並兩分（"FuriousTypingEnabled" → "FuriousTypingEnabled4Pinyin" ＋ 新增 "FuriousTypingEnabled4Zhuyin"）。
// 舊 key 之用戶設定值搬移至拼音側；注音側維持其出廠預設（false）——該側在舊版並不存在，無值可承。
if defaults.object(forKey: "FuriousTypingEnabled") != nil {
  furiousTypingEnabled4Pinyin = defaults.bool(forKey: "FuriousTypingEnabled")
  defaults.removeObject(forKey: "FuriousTypingEnabled")
}
```

**設計要點**：

| # | 要點 | 理由 |
|---|---|---|
| 1 | **只讀 `object(forKey:) != nil` 為閘** | 舊鍵存在即處理、處理完即刪；故冪等（§0.3 約束 2）。第二次執行時舊鍵已不存在，直接略過 |
| 2 | **不寫入注音側** | 注音側在舊版不存在，任何「推測之值」都是捏造。其 `.bool(false)` 之出廠預設由 `@AppProperty` 之 self-register 機制處理（`SwiftFoundationImpl.swift:199–205`） |
| 3 | **以 `defaults.bool(forKey:)` 讀值** | 照既有段之寫法；`bool(forKey:)` 對非布林之型別會回傳 `false`，但因 `object(forKey:) != nil` 已先確認存在，且該鍵在舊版恆為布林（`dataType` 為 `.bool`），故無風險 |
| 4 | **經 `PrefMgr` 之型別化屬性寫入**（`furiousTypingEnabled4Pinyin = …`）而非 `defaults.set(_:forKey:)` | 照既有段之成例；且能觸發 `@AppProperty` 之 setter（本鍵無 `didSet`，但一致性更重要） |
| 5 | **遷移碼使用 `UserDefaults.standard`** | 該函式既有之首行即 `let defaults = UserDefaults.standard`（`:517`），故與測試 suite 脫鉤。**此為既有行為，本案不改變**——但須於 Phase 253 之驗收內，以「直接對 `UserDefaults.standard` 佈置舊鍵、再呼叫 `fixOddPreferencesCore()`」之**獨立測試**驗證遷移（不可依賴測試 suite） |

**附帶之風險與緩解**：

| 風險 | 影響 | 緩解 |
|---|---|---|
| 使用者從未改過該鍵（＝從未於兩處寫入過 `FuriousTypingEnabled`） | **無值可遷**（`object(forKey:) == nil`），新鍵由 `@AppProperty` 註冊為 `true` | 無事。**此為絕大多數使用者之情形**——因 `@AppProperty` 之 init 會把預設值寫入，故實際上幾乎所有使用者**都**有該鍵。此時遷移即為「把 `true` 搬過去」，結果相同 |
| 使用者曾關掉狂拼（值為 `false`） | 遷移後拼音側為 `false`，行為不變 | 正確 |
| 使用者之系統上同時跑著舊版與新版之 IME | 舊版會把新鍵視為未知鍵（不影響 IME 運作，僅 `UserDef` 匯出時少一項） | 已知、可接受 |
| **匯入外部舊配置包** | 含 `"FuriousTypingEnabled"` 之配置包將以 `"Unknown key"` **整包失敗** | 見 §6.4 |

### 6.4 交換格式之破壞性（本系列之**已知代價**，須讓事主知悉）

`UserDef.exportAsJSON()`／`importFromDictionary(_:)` 以 `rawValue` 為鍵（`UserDef.swift:271, 285`），而**未知鍵會被拒**（`:285–288`：`reason: "Unknown key"`）。

**故**：任何在本次更名前由助手（或使用者手改）產生、含 `"FuriousTypingEnabled"` 之配置包，**在新版上會匯入失敗**。

**三種處置（本文主張第三種）**：

| 案 | 內容 | 評價 |
|---|---|---|
| 甲 | 不動，任其失敗 | 代價明確但使用者體驗差；且失敗訊息為 `Unknown key`，使用者無從得知「跑一次新版就好了」 |
| 乙 | 於 `importFromDictionary` 內加一張「舊鍵 → 新鍵」之別名表 | **違反本倉對「LLM 式向後相容 shim」之既有紀律**（`migrateDeprecatedSettings` 之模式是「一次性搬移」，不是常駐別名）；且會讓交換格式之鍵空間永久帶著歷史債 |
| **丙** | **於 `migrateDeprecatedSettings()` 內「先遷移、後匯入」**——因匯入路徑必然先經 `reconcileAfterExternalPrefsImport()` → `fixOddPreferencesCore()`，而遷移段會把**磁碟上**之舊鍵搬走。但**配置包檔案內**之舊鍵仍在 ⇒ 丙案**不足以解決** | **不足** |

**故最終裁定**：**採甲案**，並於 Phase 257 之 i18n 內**加強 `Unknown key` 之可讀性**（將失敗訊息改為可指出「此鍵可能在較新／較舊之版本中不存在」）——**此為本文之自動裁定，列於 §九**。理由是：本專案之配置助手（P240–P249）才剛上線，其產物尚未大規模流通；而犧牲交換格式之簡潔以換取一次性之相容，是長期的負債。

**若事主不同意**：替代方案是「在 `importFromDictionary` 之最前端加一段**一次性的鍵重寫**（僅當偵測到舊鍵時），並於 rewrite 後照常走既有驗證路徑」。此案之改動面僅一處、且與乙案之差別是「一次性重寫」而非「常駐別名」。**留待 Phase 253 施工時依事主之覆核決定。**

### 6.5 `PrefMgrProtocol` 之變更

`:93` 之 `var furiousTypingEnabled: Bool { get set }` 改為兩行：

```swift
var furiousTypingEnabled4Pinyin: Bool { get set }
var furiousTypingEnabled4Zhuyin: Bool { get set }
```

該協定為 124 行「一屬性一行」之平鋪結構（`:5` 起，無 `@MainActor` 屬性、`MainActor` 由 `Package.swift:117–118` 之 `.defaultIsolation(MainActor.self)` 供給），故新增一行無任何結構性影響。**實作者只有 `PrefMgr` 一個**（`PrefMgr_Core.swift:9`），故無需改動任何 mock。

---

## 七、語意層之設計

### 7.1 `typingMode` 之新形狀

```swift
public enum TypingMode: String, Equatable {
  case cassette
  case bopomofoKeyblock
  case pinyinKeyblock
  case pinyinFuriousTyping   // 狂拼
  case zhuyinFuriousTyping   // 狂注（新增）

  public var i18nKey4InlineModeHint: String {
    "i18n:TypingMode.i18nKey4InlineModeHint.\(rawValue)"
  }
}

extension InputHandlerProtocol {
  public var typingMode: TypingMode {
    if prefs.cassetteEnabled { return .cassette }
    let isFurious = composer.isPinyinMode
      ? prefs.furiousTypingEnabled4Pinyin
      : (prefs.furiousTypingEnabled4Zhuyin && !prefs.mixedAlphanumericalEnabled) // ← P258
    if isFurious, !prefs.useSCPCTypingMode {
      return composer.isPinyinMode ? .pinyinFuriousTyping : .zhuyinFuriousTyping
    }
    return composer.isPinyinMode ? .pinyinKeyblock : .bopomofoKeyblock
  }
}
```

**既有行為之等價性**：拼音側之條件由 `prefs.furiousTypingEnabled` 變為 `prefs.furiousTypingEnabled4Pinyin`，而經 §6.3 之遷移後二者同值 ⇒ **既有使用者之 `typingMode` 逐值不變**。此為 Phase 255 之首要回歸斷言（既有 67 支狂拼測試即是）。

**v23（P258）之增修——注音臂之中英混合輸入回退否決**：本屬性即「當前處於哪個打字模式」之**單一出口**（讀取點 3 處：`handleComposition` 之分派、`isFuriousTypingModeEffective`、`Session` 之行內模式提示），而狂打之全部閘門皆由其推導 ⇒ 否決置於此處，上下游一次一致。**判準**：`prefs.mixedAlphanumericalEnabled` 為真 ⇒ 注音狂打一律不成立（**即便其開關仍為真**）。**理由**：兩者對**同一批 ASCII 按鍵**爭奪語義——回退要求逐鍵累積 ASCII 緩衝、待整段不再構成讀音時再回退；狂打要求連續注音即時自動切音節。前者係使用者**顯式指定**之相容行為，故由前者勝出。**拼音側不設同一否決**：回退本即注音鍵盤專屬（`handleComposition` 對拼音兩模式一律走 `BPMFFullMatchTypewriter`，該旗標於拼音下完全不生效），連帶否決會令「注音時期開過回退、其後改用拼音」之使用者無故失去狂拼。

**★ v23 之同步義務**：`typingMode` 之「單一出口」性質**僅及於 InputHandler／Typewriter 系**。§8.8 為模組邊界之故，在 `LexiconAssembly/LXFacade.syncPrefs()` 內**就地複製**了模式判定（注音文抑制旗標 `shouldSuppressFactoryZhuyinwenData`，其語意即「狂打確實生效中」）；**凡在本屬性新增維度者，必須同步補進該處**，否則即出現「模式已非狂打、抑制卻仍開」之第五態（違反 P257 之四態裁定）。此同步義務**無編譯期或型別層之強制**，目前由 `LexiconAssemblyTests` 之 64 組真值表守住。

### 7.2 `isFuriousTypingModeEffective` 與 `hasFuriousFrontPending`

```swift
extension InputHandlerProtocol {
  public var isFuriousTypingModeEffective: Bool {
    currentTypingMethod == .vChewingFactory
      && (typingMode == .pinyinFuriousTyping || typingMode == .zhuyinFuriousTyping)
  }
  public var isPinyinFuriousTypingModeEffective: Bool {
    isFuriousTypingModeEffective && typingMode == .pinyinFuriousTyping
  }
  public var hasFuriousFrontPending: Bool {
    switch typingMode {
    case .pinyinFuriousTyping: return !composer.romajiBuffer.isEmpty
    case .zhuyinFuriousTyping: return !composer.isEmpty   // §3.5：注音之未完成讀音即其槽內容
    default: return false
    }
  }
}
```

**新增 `isPinyinFuriousTypingModeEffective` 之必要性**：既有 12 個讀取點之中，至少三者**必須**保持拼音專屬——

| 讀取點 | 為何必須拼音專屬 |
|---|---|
| 【P260 新址】`Typewriter_BPMFFullMatch.swift:208`（`allowsExtendedRomajiBuffer = …`） | 該旗子只對 `romajiBuffer` 有意義；注音側若設為 `true` 則 `romajiBuffer`（恆空）無影響，但語意上不該設 |
| 【P260 新址】`Typewriter_BPMFFullMatch.swift:278`（trail 記錄） | trail 是拼音字母 blob |
| `InputHandler_CoreProtocol.swift:215`（`isPinyinFamilyTypingMode`） | 該旗子之語意就是「拼音系」（`:209–213` 之註解已明言）。**注音狂打不是拼音系** ⇒ 鍵盤佈局翻譯**必須**照常執行（注音要美規鍵盤翻譯！） |

**紅線**：`isPinyinFamilyTypingMode` 之語意**不得**因本案而放寬。若在 Phase 255 之施工中發現 `isFuriousTypingModeEffective` 之某讀取點對注音也該為真，**逐點改用 `isFuriousTypingModeEffective`**，而非把 `isPinyinFamilyTypingMode` 改成 `isFuriousTypingModeEffective`。

> **v10 補強（P254 施工實錄）**：上列紅線之措辭在施工上**不足**。該旗子原實作為 `isComposerUsingPinyin || isFuriousTypingModeEffective`，而自 P254 起後項亦可能於**注音**注拼槽上成立 ⇒ **只「不放寬、保持原樣」會使注音狂打一開即令本旗子為真、鍵盤佈局翻譯被跳過、注音完全打不出字**。**正解是「收緊」**：`isPinyinFamilyTypingMode` 改為**單一條件** `isComposerUsingPinyin`——此為**等價變換、非放寬**（原析取之右項恆蘊含左項：`.pinyinFuriousTyping` 之成立本身即要求 `composer.isPinyinMode`），且自此對新值免疫。已以 IH702 釘住，並於 `InputHandler_CoreProtocol.swift` 之 doc comment 內載明原委。

**`hasFuriousFrontPending` 於注音側之語意變更之漣漪（須逐點複驗）**：初稿訂為 `false`、現訂為 `!composer.isEmpty`（§3.5）。此一改動使注音狂打**進入** copilot 窗體系，故 Phase 255 須逐點確認那 6 個讀取點在注音下皆為所欲——特別是 `InputHandler_TriageInput.swift:35` 之「固化後消費空格」與 `:49` 之 Tab：二者在注音下會先固化當前音節再續行，正是狂打所欲；而 `Typewriter_BPMFFullMatch.swift:122` 之 Shift＋選字鍵就地選字，於注音下亦應成立（該窗顯示的是組字器之候選）。

### 7.3 自動切音節之落點

**新增**（自 P260 起住在 `Typewriter_ZhuyinFuriousAutoChop.swift`；判準 `shouldAutoChopZhuyin` 於該檔 `:38`，執行端仍與 `performPinyinAutoChopIfNeeded` 並列，【P260 新址】）：

```swift
/// 注音狂打：本鍵是否應先把當前音節固化進組字器。
/// - Returns: 已固化則 `true`；不應固化則 `nil`（呼叫方照常把按鍵送入注拼槽）。
private func performZhuyinAutoChopIfNeeded(
  inputText: String,
  prefs: some PrefMgrProtocol,
  session: Session
) -> Bool?
```

呼叫點：`consumeReadingInputIfNeeded` 內 `receiveKey` 之**正前方**，與 `performPinyinAutoChopIfNeeded` 同一位置（【P260 新址】`Typewriter_BPMFFullMatch.swift:194–208`），以 `switch handler.typingMode` 分流。

**固化之實際動作**：以 `phonabetKeyForQuery(pronounceableOnly: true)` 取當前讀音鍵 → `assembler.insertKey(...)`（照 `composeReadingIfReady` 之既有寫法，`:407`）→ `composer.clear()` → 續行本鍵之接收。**不觸碰 trail、不做重切分。**

**POM 自動套用之處置**：拼音側之 `performPinyinAutoChopIfNeeded` 於每次自動 chop 後會呼叫 `handler.retrievePOMSuggestions(apply: true)`（`:334`），使感知覆寫／n-gram 記憶能立即回饋。注音側**建議一併照做**（同一語意：每次自動提交後重取 POM 建議），但**須列為 Phase 255 之實測項**——若發現它與呼叫 `composeReadingIfReady` 之既有 POM 路徑重複，則以不重複者為準。

**`phonabetKeyForQuery(pronounceableOnly:)` 之參數**：注音側應傳 `true`（`isPronounceable` ＝ 聲／介／韻任一非空），**不可**傳 `false`——後者對空槽亦可能回傳非空字串（其判定為 `!readingKey.isEmpty`，而 `ㄍ` 本身即非空）。此點於 Phase 255 須以測試釘住（`IH160` 一類）。

> **v5 補註（P251 定案）**：本函式內之判準**即 §3.2 之 v7（六條）**。P251 已把 v7 寫成可執行形式（`Tests/TekkonTests/TekkonTests_AutoChopPredicate.swift` 之 `shouldAutoChopZhuyin`）並以 11 個排列實測；**施工時須把該函式逐條移入本處，不得另行重寫一份**。本節其餘設計（呼叫點、固化動作、POM 之處置、`pronounceableOnly: true`）經 P251 之閱讀複核**仍然成立**。
>
> 另：本節所述之「以 `phonabetKeyForQuery(pronounceableOnly: true)` 取當前讀音鍵」**必須在清空注拼槽之前執行**——v7 之 ④c 需要 `C` 之原始內容。

### 7.4 注音文抑制：**兩種狂打皆抑制**（v3 改版；事主明示）

**事主原文（v3）**：「那麼注音狂打模式還是屏蔽掉注音文吧。我敲「ㄍㄢˋ-ㄋㄧˇ-ㄋㄧㄤˊ」是能看到有「幹你娘」候選字的。」

**現況**：`LXFacade.swift:334`：`config.shouldSuppressFactoryZhuyinwenData = prefs.furiousTypingEnabled && prefs.pinyinTypingEnabled`。

**目標**：**拼音狂打與注音狂打皆抑制**。因 `LXFacade` 拿不到 `composer`（它不知曉當前打字方式），故以偏好之**析取**近似：

```swift
// 兩種狂打皆抑制注音文（v3）：
// 拼音側：狂拼開關已開 且 當前在拼音方式
// 注音側：狂注開關已開 且 當前在注音方式（＝ !pinyinTypingEnabled）
let inPinyinMode = prefs.pinyinTypingEnabled
config.shouldSuppressFactoryZhuyinwenData =
  inPinyinMode
    ? prefs.furiousTypingEnabled4Pinyin
    : prefs.furiousTypingEnabled4Zhuyin
```

**理由**：① 事主明示；② 抑制之對象是 §3.0.1 那 8 行**以注音符號字串為值**之詞條（如 `ㄍ-ㄋ-ㄋ → ㄍ`）——它們在**兩種**狂打模式下都是雜訊：拼音側因使用者不會想在拼音連續輸入時看到注音字串；注音側則因使用者要的是「狗男女」「幹你娘」一類**真詞**，而非回聲字串。**兩側之訴求一致**。

**★★ 落點（**v5 已定案——原「商榷」一節由 P251 未知四結案**）**：

P251 已把熱鍵路徑查清（依據逐條見 §8.8 之「為何可續留」一欄）：

| 情形 | `pinyinTypingEnabled` 是否改變 | 意義 |
|---|---|---|
| 使用者在設定介面改「拼音／注音打字模式」 | **會**（`PrefMgr_Core.swift:359–369` 之 `keyboardParser` setter） | 上述析取式即時跟上 |
| 使用者按熱鍵 `⌃⌘J` | **會**（`IMEMenuSputnik.swift:280–283` 直接 `PrefMgr.shared.pinyinTypingEnabled.toggle()`） | 同上；熱鍵**不改** `keyboardParser4Pinyin`／`4Zhuyin` 兩槽 |
| 是否另有其它路徑改動打字方式 | **有，但皆為偏好寫入、且皆受 `syncPrefs()` 每拍同步之覆蓋**。全倉（不含鏡像）寫入 `pinyinTypingEnabled` 者共 **5 處**：`PrefMgr_Core.swift:365`／`:368`（計算屬性 `keyboardParser` 之 setter）、`:552`／`:555`（P153 之鍵遷移）、`VwrSettingsPaneGeneral.swift:257`（SwiftUI 設定介面）、`VwrSettingsPaneCocoaGeneral.swift:153`（AppKit 設定介面）、`IMEMenuSputnik.swift:282`（`⌃⌘J` 熱鍵） | — |

且 `syncPrefs()` 於**每一次分診之頂端**執行（`InputHandler_TriageInput.swift:14`）⇒ 上述任一變更**必然在下一拍按鍵被處理之前**反映進 `config`。**故無脫鉤之虞，毋須把旗標移到 Handler 側。**

**v5 之裁定**：**續留 `LXFacade.syncPrefs()`**（上式之析取式）。原「傾向採 Handler 側之寫法」之議**撤銷**——其唯一理由（熱鍵脫鉤）已被實測否定，而 Handler 側之寫法會引入一項新依賴（`LexiconAssembly` 之 config 由 `LibVanguard` 推入），得不償失。**惟 P257 仍須新增一則熱鍵測試**：於 `pinyinTypingEnabled` 切換後之下一拍，抑制旗標須即時改變——此為上表第三列「無第三條路徑」之固化物。

**v23（P258）之補述——本旗標之第四維**：本旗標之語意既然就是「**狂打確實生效中**」，則 §7.1 之模式判定每增一維，此處即須同步增一維。P258 增補者為**注音側之中英混合輸入回退否決**：

```swift
let furiousSideEnabled = prefs.pinyinTypingEnabled
  ? prefs.furiousTypingEnabled4Pinyin
  : (prefs.furiousTypingEnabled4Zhuyin && !prefs.mixedAlphanumericalEnabled) // ← P258
```

**只改 `typingMode` 而不改此處**即產生第五態（模式非狂打、抑制仍開）；**只改此處而不改 `typingMode`** 則產生反向之割裂（模式為狂打、注音文卻不被抑制）。二者皆由靶守住：前者由真值表之注音側組合、後者由 IH168。

### 7.5 `UserDef.kFuriousTypingEnabled4Zhuyin.description` 之草案（zh-Hant）

> 本開關是為了方便需要連續注音打字的使用者，亦為日後於 iOS 等觸控裝置上使用螢幕注音鍵盤之場合預作準備。僅對注音輸入（任一注音排列）生效，且與拼音側之「狂拼模式」各自獨立開關；對磁帶、逐字選字（SCPC）、內碼、漢音鍵盤符號與羅馬數字等輸入方法不適用。啟用後，連續鍵入注音符號即可組句，無需逐音節敲聲調或空格鍵確認：每當當前音節已經打完、而下一鍵屬於新音節時，該音節會自動寫入組字器。與狂拼模式不同，本模式不會刻意過濾掉注音文，亦不會以語言模型試算未完成的讀音。

（zh-Hans 照 zh-Hans-TW；en／ja 對位文案於 Phase 257 定稿。）

**文案之關鍵一句（v2 新增）**：上稿之「無需逐音節敲聲調或空格鍵確認」須在 Phase 257 之定稿內**明示單聲母可用**——例如續寫「只敲聲母亦可（如 `ㄍㄋㄋ`、`ㄋㄋ`），未完成的讀音會由選字窗即時預覽」。理由：此為本模式最不易被使用者自行發現之能力（§3.0），而它正是注音使用者最想要的那一項。

---

## 八、後續手術之 Phase 切分

### 8.0 全系列之共同紀律（每一 phase 皆適用）

| # | 紀律 | 出處 |
|---|---|---|
| 1 | **兩倉 byte-sync**：凡動 `vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard/**`（含 `Deps/`）或 `vChewing-LibVanguard/**`，**另一倉必須同輪鏡像**，範圍含 `Sources/`、`Tests/`、`Deps/`、`Package.swift`、`Package@swift-5.10.swift`、`Package@swift-6.0…6.3.swift`、`makefile`；並在回報中附 `cmp`／`diff -rq` 之**實際輸出** | `Phase217_SOP.md:56`（I2）、`:1043`（§11.2）、`:1045`（`makefile` 納入 I2） |
| 2 | 鏡像於 `make lintFormatUncommitted` **之後**複驗（SwiftLint `--fix` ＋ SwiftFormat 會改檔） | P242／P243／P244 之成例 |
| 3 | **同一時間只跑一顆 `swift test`**（兩倉不得並行） | `KnowledgeMemo4LLM.md:399` |
| 4 | SwiftPM 一律附 `--disable-sandbox`；測試一律 `--no-parallel` | `KnowledgeMemo4LLM.md:397` |
| 5 | Commit 標題照 `ModuleName // SubModuleName: Change.`，描述末行 `(Phase XXX - Task YYY)` | `KnowledgeMemo4LLM.md` §12.6 |
| 6 | 文書三件套：本卷之 phase 記錄、`DevReqsHistory.md` 一行、`KnowledgeMemo4LLM.md` 之更新 | §12.2 |
| 7 | **CI 之 macOS 側一律以本機代跑**（同環境豁免）；Linux／Windows 仍以 CI 為唯一途徑 | `KnowledgeMemo4LLM.md` §12.6 |
| **8** | **★ 每完成一個 phase，即回頭檢討本文並作必要之調整**（事主 2026-09-26 定調之節奏）——作法見 §8.0.1 | 事主指示 |

#### 8.0.1 phase 收尾之「回檢本文」程序（事主定調之節奏）

**每一 phase 完工時，除該 phase 自身之文書三件套外，尚須在**該 phase 之記錄內**完成下列三事**：

| # | 動作 | 內容 |
|---|---|---|
| 1 | **對帳** | 逐條核對本文對該 phase 之規劃與實作結果之差異。**凡本文之推論被實測推翻者，一律明列**（例：「§3.2 條件 ④ 於 Dachen26 之 X 情形失準，實測結果為…」） |
| 2 | **回寫本文** | 依差異修訂本文之**對應小節**（非只改 §八），並於文首〈修訂沿革〉追加一行 `vN（日期，Phase 2XX 完工回檢）`，扼述改了哪幾節、為什麼 |
| 3 | **重排後續** | 若差異足以影響**尚未動工**之 phase 的範圍、依賴或完成定義，則**就地重編 §八**（含編號；重編時須同步更新本文其餘小節之交叉引用、以及三件套內之引用） |

**紅線**：第 2 步不得只改「實作結果」而不動「設計依據」——本文是後續 phase 之設計依據，**留著一個已知錯誤的依據比沒有依據更危險**。

**既有之成例**：本 phase（250）自身之 v1→v2→v3 三次改版即此程序之最早演練（事主兩次覆核所促）。

### 8.1 依賴圖（重組後）

```
P251（術前驗證靶：自動切音節判準 ＋ 熱鍵推入路徑）   ← ✅ 已完成（2026-09-26）
   │  零生產碼；產出「四個未知之答案」 ⇒ §3.2 之判準由 v1 改為 v7
   ▼
P252（Tekkon API：SyllableIndex；**已刪 incomingPhoneType**）   ← ✅ 已完成（2026-09-26）
   │  四項斷言全成立；另得 37＝三音素表聯集、以及 mapHanyuPinyin 之 `"q": "ㄑ"` 異常
   ▼
P253（偏好層：兩分 ＋ 更名 ＋ 遷移）        ← 與 P251／P252 無交集，理論上可並行；
   │                                          但本系列一律循序、不得並行測試（§8.0 紀律 3）
   ▼
P254（FSM 閘門收束；行為零變動）            ← 依賴 P253（兩個偏好鍵）
   │
   ▼
P255（自動切音節；★ 功能底線：ㄍㄋㄋ 可打）  ← 依賴 P252 ＋ P254
   │
   ▼
P256（copilot 窗與 unfinishedReading 分流）  ← 依賴 P255
   │
   ▼
P257（注音文抑制之落點定案）                ← 依賴 P251 之熱鍵答案 ＋ P253 ＋ P254
   │
   ▼
P259（偏好介面 ＋ i18n ＋ 助手後設資料）    ← 依賴 P253（偏好名）＋ P256（TypingMode case）
   │
   ▼
P259（跨倉驗收 ＋ Swift 5.10 可建置性 ＋ 文書）← 依賴 P252–P259 全部
```

**九個 phase（251–259）。**

**重組之三項理由**：

| # | 變更 | 理由 |
|---|---|---|
| 1 | **插入新的 P251「術前驗證靶」** | 本文之全部斷言都來自唯讀閱讀，**未曾編譯或執行**。而事主兩次覆核所抓到之錯，**兩次都在「我從程式碼結構推導、但沒有實測」之那一類**（v1 之 copilot 窗判斷、v2 之辭典值誤讀）。故在動任何生產碼之前，先花一個 phase 把**可實測者實測掉** |
| 2 | **原 P253 之「FSM 核心」拆為 P254（閘門收束）＋ P255（自動切音節）＋ P256（copilot 窗）** | 原規劃已建議「分兩半施工」，惟仍列為同一 phase 之內部紀律。**改為三個獨立 phase**，使「行為零變動」那一半（P254）能單獨取得綠燈與單獨之回檢，風險不再與行為改動混在同一筆 commit |
| 3 | **原 P251（Tekkon）之「對稱性測試」移入 P251** | 439 vs 427 之落差是**實測問題**、非 API 問題。留在 API phase 會讓「先量再建」變成「邊建邊量」 |

### 8.2 Phase 251 — 術前驗證靶（★ 全新）——**✅ 已完成（2026-09-26）**

> **完工狀態**：零生產碼。新增 `Tests/TekkonTests/TekkonTests_AutoChopPredicate.swift`（733 行／34,867 位元組，兩倉逐位元組相同，SHA-256 `e4f80ec9…`），內含 5 支測試。全倉 `swift test` **597 支／0 失敗**（動工前 592 ⇒ ＋5）；`TekkonTests` **48 支／9 套**（動工前 43 支／7 套 ⇒ ＋5 支／＋2 套，既有 43 支逐支照舊）。詳細驗證報告見 `Reqs4LLM/Archive_P201-P300/Reqs_0251-0260.md`。**四項未知之結論**：① 判準被證偽 ⇒ 改採 v7（§3.2）；② `qquu` 逐槽覆寫已釘死、且接續語意於此案誤切；③ 「439」為誤、真相 422 且全部 ⊆ 427（§4.2）；④ 熱鍵改 `pinyinTypingEnabled`、不改兩 parser 槽 ⇒ P257 可續留 `LexiconAssembly`（§8.8）。

| 項 | 內容（原規劃，保留為記錄） |
|---|---|
| **目標** | **不動任何生產碼**，以測試靶回答四個未知，產出一份「驗證報告」小節（寫入本 phase 之 Reqs 記錄） |
| **落點** | 新增 `Tests/TekkonTests/TekkonTests_AutoChopPredicate.swift`（或同義檔名）；必要時於 `Tests/LibVanguardTests/` 新增一則查證用之測試；**零生產碼改動** |
| **依賴** | 無。**本 phase 不動 `Sources/` 一字**，故與 byte-sync 無關（但 `Tests/` 仍受 I2 覆蓋，須鏡像） |
| **未知一（主項）：自動切音節判準** | 取 `Tests/TekkonTests/TestAssets_Tekkon/Tekkon_TestData.swift` 之 1485 行 × 5 排列，對**每一筆合法編碼**之**每一個中途前綴**，以「值語義之 `Composer` 副本」模擬 §3.2 之三條件 ＋ 第四問，斷言：**中途不得誤切**、且**該編碼之音節邊界與判準給出之切點一致**。**本項若失敗 ⇒ §3.2 之判準須重寫，P252 之 API 形狀亦可能連帶改變** |
| **未知二：Dachen26 之 `qquu` 逐槽覆寫案** | 單獨一則測試，逐步斷言 `qquu` 之四拍中，第二拍**不得**被判為新音節（此為第四問承重最重之處） |
| **未知三：439 vs 427** | 以 Python 或 Swift 列出 `Tekkon_TestData` 之 439 條無調詞幹與 `mapHanyuPinyin` 之 427 條之**對稱差集**，將差異**逐條列出**；並斷言「439 條全部為 427 條之成員或其前綴」（或據實推翻此斷言） |
| **未知四：熱鍵推入路徑** | 追查「純打字方式切換（熱鍵 `kUsingHotKeyPinyinZhuyinTypingSwitch`）是否改動 `prefs.pinyinTypingEnabled`／`keyboardParser`」——起點：`SessionProtocol` 之 TIS 路徑、`InputSession_HandleEvent`、`InputHandler_TriageInput:14`、`InputHandler_CoreProtocol.currentKeyboardParserType:565`。**產出：一句可引用的結論 ＋ 其 `path:line` 依據** |
| **完成定義** | ① 四項未知各有明確結論（**允許結論為「判準失敗」**——那正是本 phase 之價值）；② 既有 43 支 Tekkon 測試＋全部 LibVanguard 測試**逐支照舊通過**（本 phase 只新增測試，不得使任何既有測試轉紅）；③ 兩倉 `Tests/` byte-sync 之輸出；④ **於 Reqs 記錄內寫出「驗證報告」小節**，供 P252 起直接引用 |
| **不動** | `Sources/` 之任何檔案、任何偏好、任何 i18n、任何 manifest |
| **風險** | 低（零生產碼）。**唯一之風險是「本 phase 得出顛覆性結論而需重編 §八」——那正是 §8.0.1 之回檢程序所為而設** |

**v5 之實際結果與原規劃之三項出入**：

| # | 原規劃 | 實際 | 理由 |
|---|---|---|---|
| 1 | 未知一只涵蓋 5 個**動態**排列 | 擴至 **11 個排列**（＋6 個靜態排列，以鍵表反推 442 條前綴之編碼） | §3.0 之頭號案例（`ㄍㄋㄋ`）在**靜態**排列（大千）上；單音節步數 23,441 → **29,579** |
| 2 | 未知一之二（交界）未列 | **新增**：276,446 個交界之必切性 | 只驗「單音節不走火」不足——v1 正是**單音節幾乎不誤切（12 例）而交界全滅（48.05%）** |
| 3 | 未知三之斷言為「439 條全部為 427 條之成員**或其前綴**」 | 實得「**422** 條全部為 427 條之**成員**」 | 439 本身即為誤算（`_` 未正規化） |

### 8.3 Phase 252 — Tekkon API：注音前綴索引（**✅ 已完成（2026-09-26）**）

> **完工狀態**：交付 `Tekkon.SyllableIndex`，**零行為變動**。新增 `Sources/Tekkon/Tekkon_SyllableIndex.swift`（138 行／6,195 位元組）＋ `Tests/TekkonTests/TekkonTests_SyllableIndex.swift`（208 行／9,805 位元組，9 支測試），兩倉逐位元組相同（SHA-256 `36042438…`／`dbd811bb…`）。**`Tekkon_SyllableComposer.swift` 零改動**；六份 manifest ＋ `makefile` 亦未動（實查：靶以名稱宣告、不逐檔列舉 `sources:`）。全倉 `swift test` **606 支／0 失敗**（動工前 597 ⇒ ＋9）；`TekkonTests` **57 支／10 套**（動工前 48 支／9 套，既有 48 支逐支照舊）。四項規劃斷言全部成立，另得兩項新事實（37 條單符號前綴 ＝ 三音素表之聯集；`mapHanyuPinyin["q"] == "ㄑ"` 之單字母異常）。**與本節原文之三處出入見 §4.3 之「與本節之出入」表**；§4.4 之探針依 v5 裁定未交付。完整記錄見 `Reqs4LLM/Archive_P201-P300/Reqs_0251-0260.md` 之 Phase 252 篇。
> **v8 追加（P252 完工後之裁定執行）**：`"q": "ㄑ"` 已自 `Tekkon.mapHanyuPinyin` 與 `LexiconAssembly` 之內嵌表 `jsnHanyuPinyinToMPS` 兩處同步刪去，故上列四項數字**再更動為**：完整讀音 **426**、全部非空前綴 **442**（不變）、嚴格前綴 **16**（`ㄑ` 加入）、單符號前綴 **37**（不變）。全倉 607 支測試／0 失敗（支數不變：原「行為面釘死」一支已改寫為「刪除後之契約」）。

| 項 | 內容（原規劃，保留為記錄） |
|---|---|
| **目標** | 交付 `Tekkon.SyllableIndex`；**零行為變動** |
| **落點** | 新增 `Sources/Tekkon/Tekkon_SyllableIndex.swift`；新增 `Tests/TekkonTests/TekkonTests_SyllableIndex.swift`。**`Tekkon_SyllableComposer.swift` 於本 phase 零改動**（v4 原文於此處曾列「新增一個 `public` 擴充」，v5 已刪，見 §4.4） |
| **依賴** | **P251 之結論**（已得）。§3.2 之 v7 判準只用到 `isPrefix` 一問；`S_new` 之取得改由既有 public API 於 Handler 側完成 |
| **完成定義** | ① `SyllableIndex.allReadings.count == 426`（v8 更正；原 427）；② `allReadings` 之全部非空前綴集合 ＝ 442 條；③ `isComplete`／`isPrefix` 之行為測試（含 15 條嚴格前綴之全表斷言）；④ **建構來源為 `mapHanyuPinyin` 之 value**，並斷言「測試資料之 422 條無調詞幹全部為其成員」；⑤ 既有 48 支 Tekkon 測試**逐支照舊通過**（項數不得少於動工前基線 48）；⑥ 兩倉 byte-sync 之 `cmp`／`diff -rq` 輸出 |
| **`completions(of:)` 之去留** | 保留為 `internal`（供測試與防漂移比對）並暫緩公開 |
| **`incomingPhoneType(forKey:)`** | **不在本 phase 之交付內**（§4.4 之 v5 裁定） |
| **SyllableIndex 之職責邊界** | 只答前綴一問（**不收** 37 個單符號讀音）；單符號之合法性是**辭典之事實**、非音節表之事實（§4.2 之兩條紅線） |
| **不動** | `PinyinTrie`、`Composer` 之既有成員、`MandarinParser`、任何鍵盤表、任何偏好、任何 i18n |
| **風險** | 低（已由 P251 先量後建；範圍較 v4 縮小一個 API） |

### 8.4 Phase 253 — 偏好層：兩分、更名、遷移

| 項 | 內容 |
|---|---|
| **目標** | `kFuriousTypingEnabled` → `kFuriousTypingEnabled4Pinyin` ＋ `kFuriousTypingEnabled4Zhuyin`（後者預設 `false`）；Swift 符號全量更名；`migrateDeprecatedSettings()` 內新增遷移段；**零行為變動**（§7.1 之等價性） |
| **落點（v9 補列 `SettingsUI`）** | **`Packages/vChewing_SettingsUI/Sources/SettingsUI/SettingsUI/VwrSettingsPaneBehavior.swift:105` ＋ `…/SettingsCocoa/VwrSettingsPaneCocoaBehavior.swift:210`（兩處渲染點；漏列即無法編譯）**；四語系 `Localizable.strings` 之兩條 `…4Pinyin` 鍵更名；`Sources/Shared/UserDef/UserDef.swift`（case／`dataType`／`metaData`）；`Sources/Shared/PrefMgr_Core.swift`（`@AppProperty` ×2、遷移段）；`Sources/Shared/Protocols/PrefMgrProtocol.swift`；`Sources/LexiconAssembly/LXFacade.swift:334`（僅改屬性名以維持可編譯，語意變動留待 P257）；`Sources/LibVanguard/**` 之 5 處引用；`Tests/LibVanguardTests/InputHandlerTests_Cases1.swift`（137 處）、`SessionTests_Cases5.swift`（4 處）；新增遷移測試（見下） |
| **依賴** | 無（P251／P252 未落地亦可——三者之落點互不相交） |
| **遷移測試之落點** | 建議置於 `Tests/SharedTests/`（新增一檔）。**關鍵**：因 `migrateDeprecatedSettings()` 用 `UserDefaults.standard`，測試須直接對 `.standard` 佈置／清理，**不可**依賴 `UserDefaults.unitTests` suite。測試須涵蓋：① 舊鍵為 `true` → 新拼音鍵為 `true`、舊鍵消失；② 舊鍵為 `false` → 新拼音鍵為 `false`；③ 舊鍵不存在 → 不動任何鍵；④ **冪等**：連跑兩次結果相同；⑤ 注音鍵於三種情形下皆為出廠預設 `false`；⑥ 遷移**不**影響既有之五段舊遷移 |
| **完成定義** | ① 兩倉 `swift test` 各自單獨跑、**項數不得少於動工前基線**（**v9 更正：動工前實測為兩倉各 607 支**；原文所記之 592 為 P251 前之陳跡）；② 新增遷移測試 6 項全過；③ `UserDef.allCases.count` 由 **117 → 119**（v9 更正；原文記 118）（此數字另有兩處會斷言：助手之 `tests/metadata.test.js:26` 與 `VCSharedCLI_UserDefMetadata.swift:119` 之 `assert`——**後者為 source 側 assert，會自動跟上；前者須於 P259 一併改**，故本 phase 之完成定義內**不含**助手側綠燈，僅要求「Swift 側綠燈 ＋ 助手側之漂移為**已知且已記錄**」）；④ 兩倉 byte-sync 之輸出 |
| **風險** | 中。141 處測試之機械式更名；遷移碼之冪等性與 `UserDefaults.standard` 之測試隔離。**緩解**：更名以單一 `sed` 式取代 ＋ `git diff --stat` 覆核；遷移測試獨立檔、獨立 suite |

### 8.5 Phase 254 — FSM 閘門收束（**行為零變動**）——**✅ 已完成（2026-09-26）**

| 項 | 內容 |
|---|---|
| **目標** | 把「狂打有效」之閘門與其 12 個讀取點，由「狂拼⇒拼音」之隱式假設解耦；新增 `TypingMode.zhuyinFuriousTyping` 之**型別與分派**，但**不使其可達**（新偏好預設 `false`） |
| **落點** | `InputHandler_TypingMode.swift`（新 case ＋ `typingMode` 新形狀）；`InputHandler_FuriousResegmentation.swift`（`isFuriousTypingModeEffective` 放寬 ＋ 新增 `isPinyinFuriousTypingModeEffective`）；`InputHandler_HandleComposition.swift`（`:27–37` 分派）；`Typewriter_BPMFFullMatch.swift` 之三處閘門逐點收束；`InputHandler_HandleStates.swift`（`:43`／`:119`）；`Session/InputSession_Delegates.swift:352` |
| **依賴** | P253（兩個偏好鍵） |
| **完成定義** | ① **既有 67 支狂拼測試逐支照舊通過**（此為「零變動」之主證）；② 新增閘門層測試（`typingMode` 五值之真值表；`isPinyinFamilyTypingMode` 於注音排列下**仍為假**）；③ 測試項數不得少於動工前基線；④ 兩倉 byte-sync 之輸出 |
| **紅線** | `InputHandler_CoreProtocol.swift:215` 之 `isPinyinFamilyTypingMode` **不得**放寬——它是鍵盤佈局翻譯之守衛，一破即注音完全打不出字（§7.2、§10.5 風險 1） |
| **為何獨立成 phase** | 因新偏好預設 `false`，`zhuyinFuriousTyping` **永不出現** ⇒ 本 phase 可**證明**其行為變動為零。把這一半單獨取得綠燈，後續 P255／P256 之行為改動才有乾淨之基準線可比對 |
> **完工狀態（v10）**：全倉 `swift test` **617 支／0 失敗**（動工前 613 ⇒ ＋4）；`LibVanguardTests` **240 支**（動工前 236，既有 236 支含 67 支狂拼逐支照舊）。新增閘門層測試 IH701–IH704。**`isPinyinFamilyTypingMode` 以「收緊」而非「不動」處置**——見 §7.2 之 v10 補強。**四項已知界線**見 `Reqs_0251-0260.md` 之 Phase 254 篇 §五；其中兩項成為後續 phase 之新增待辦（§8.7 之 `confirmFuriousFrontCandidate`、§8.10.1 之 `TypingMode…zhuyinFuriousTyping` i18n 鍵）。

### 8.6 Phase 255 — 自動切音節（★ 功能底線；**v5 依 P251 定案判準**）——**✅ 已完成（2026-09-26）**

| 項 | 內容 |
|---|---|
| **目標** | 注音狂打下，當前音節於「不可能再延伸」時自動提交——**含單聲母** |
| **落點** | `Typewriter_BPMFFullMatch.swift`（新 `performZhuyinAutoChopIfNeeded`，與 `performPinyinAutoChopIfNeeded` 並列；呼叫點在 `receiveKey` 之正前方）；`Tests/LibVanguardTests/InputHandlerTests_Cases1.swift`（或新增檔）加入新測試 |
| **判準** | **§3.2 之 v7（六條）**。參考實作見 `Tests/TekkonTests/TekkonTests_AutoChopPredicate.swift` 之 `shouldAutoChopZhuyin`；本 phase 須把該函式**逐條**移入生產碼，並在測試端改為對生產實作之呼叫（或反向：以本 phase 之實作替換之），**不得**留下兩份各自演化之判準 |
| **依賴** | P252（`SyllableIndex` 之 `isPrefix`）＋ P254（閘門） |
| **功能底線** | **必須能打出「ㄍㄋㄋ」並在組字器取得 `ㄍ`／`ㄋ`／`ㄋ` 三鍵**（§3.0、§0.2 ★③）。此為本 phase 之唯一不可退讓之驗收項；`IH155` 即其固化物。**P251 已於引擎層以三版判準實測過此序列**（v1 → `["ㄋ"]` 失敗；v5／v7 → `["ㄍ","ㄋ","ㄋ"]` 成功）⇒ 本 phase 之該項可望一次成功，風險已由 P251 吸收 |
| **建議之新測試** | **IH155 縮寫打法**（逐鍵斷言三鍵入組字器、且**不得**因互搶同槽而只剩一顆）；IH156 「`ㄅㄧ` ＋ `ㄢ` ＝ `ㄅㄧㄢ`」之不被誤切（v7 之 ④b′）；IH157 動態排列之覆寫不被誤切（`qquu` 之 Dachen26 案，v7 之 ④d）；IH158 聲調鍵語義不變（含後置聲調覆寫）；IH159 SCPC 下注音狂打不生效；IH162 注音狂打之空格／Tab／Enter／標點語義；IH163 注音狂打**不**寫入 `furiousTrail`；IH164 注音狂打關閉時之行為與今日完全一致 |
| **完成定義** | ① 上列測試全過；② 既有 67 支狂拼測試照舊；③ **P251 之 5 支靶轉為對生產實作之回歸靶**（或以生產實作取代其參考實作），且其四項地面真相（單音節零誤切／交界漏切率／`ㄍㄋㄋ` 之三音節／`qquu` 之四拍合一）逐項照舊成立；④ 兩倉 byte-sync 之輸出 |
| **風險** | **低於 v4**。切點判準已由 P251 以 11 個排列、29,579 ＋ 276,446 例實測過；本 phase 之新增風險僅餘「呼叫點之位置」與「與既有 `composeReadingIfReady` 之交互」 |
| **已知界線（承 P251）** | v7 於交界處有 **2.19%** 之殘餘漏切，**全在 5 個動態排列**，且已證不可由任何局部判準分離（§3.2 之界線表）。本 phase **接受並記錄**，不得為消除它而引入更大之狀態或架構改動——該決策留待實機抱怨出現後再議 |
| **實測項（留待事主）** | `ㄍㄢˋ-ㄋㄧˇ-ㄋㄧㄤˊ` → 「幹你娘」（逐字組句）、`ㄍㄡˇ-ㄋㄢˊ-ㄋㄩˇ` → 「狗男女」（整鍵詞條） |
> **完工狀態（v11）**：全倉 `swift test` **623 支／0 失敗**（動工前 617 ⇒ ＋6；`LibVanguardTests` 240 → 251、`TekkonTests` 58 → 53）。行為靶 7 支（IH155／156／157／158／159／163／164）、判準靶 4 支。**落點出入一項**：判準置於 `Tekkon.Composer` 之擴充而非 `InputHandlerProtocol` 之成員（純函式，回歸靶可零成本驅動）。**新增設計一項**：辭典閘。**已知界線四項**見 `Reqs_0251-0260.md` 之 Phase 255 篇 §四；其中**單聲母縮寫之端到端**為唯一未闔之門（測試辭典無單符號鍵；原廠辭典有）⇒ 列為實機實測項。**IH162 未做**。）

### 8.7 Phase 256 — copilot 窗與 `unfinishedReading` 分流——**✅ 已完成（2026-09-26）**

| 項 | 內容 |
|---|---|
| **目標** | 為注音狂打接入 copilot 未完成讀音窗；`unfinishedReading` 依 `typingMode` 分流 |
| **落點（v10 補列一項、v12 再補兩處）** | **`InputSession_Delegates.swift:352` 路徑之 `confirmFuriousFrontCandidate`（P254 查得；v12 已通用化）**；`InputHandler_FuriousResegmentation.swift`（新增 `furiousFrontUnfinishedReading`、`hasFuriousFrontPending` 收斂為其非空、`solidifyFuriousFrontReading` 之注音分支）；`Session/InputSession_Delegates.swift`（`unfinishedReading` 改為一行轉發）；`Tests/LibVanguardTests/TestComponents/MockedInputHandlerAndStates.swift`（mock 同步，與生產逐字相同）；**`InputHandler_HandleStates.swift`（v12 補：`furiousFrontContext` 之注音讀音桶——無此則窗永不可見，見下之出入 ①）**；`Tests/LibVanguardTests/InputHandlerTests_FuriousCopilotWindow.swift`（新檔） |
| **依賴** | P255 |
| **完成定義** | ① 注音狂打且有未完成音節時 `isFuriousCopilotCandidateWindowVisible` 為真（IH161）；② 注音狂打時 `unfinishedReading` 回傳當前音節之注音字串、空槽時為 `nil`（IH160）；③ 其餘 5 個 `hasFuriousFrontPending` 讀取點於注音下皆為所欲（§3.5 之表，逐點驗）（IH162）；④ 既有拼音狂拼之 `hasFuriousFrontPending` 語意不變（IH165，回歸護欄）；⑤ 兩倉 byte-sync 之輸出 |
| **風險** | 中。`hasFuriousFrontPending` 之語意變更會波及其 6 個讀取點；mock 與生產須同步，否則測試與生產行為分岔。**v12 後記**：前者已由 IH162 逐點驗掉；後者已由「判讀邏輯上移」根治（兩側皆只轉發） |
| **為何與 P255 分開** | P255 交付「讀音進得了組字器」，P256 交付「讀音看得見」。二者之失效模式完全不同、可獨立歸因；合併會使診斷變難 |
> **完工狀態（v12）**：全倉 `swift test` **627 支／0 失敗**（動工前 623 ⇒ ＋4；`LibVanguardTests` 251 → 255）。行為靶 4 支（IH160／161／162／165）；既有靶 1 支依規劃反轉（P254 之 IH704）。**規劃錯誤二項**（皆為本 phase 實作時查得，已更正 §3.5）：①「閘一改即通」為誤——`.ofInputting` 之候選另有來源 ⇒ 須補 `furiousFrontContext` 之注音讀音桶；② 注音分支之 `!composer.isEmpty` 過寬（純聲調槽）⇒ 改 `isPronounceable` 並把旗子與顯示源收斂為同一判準。**落點之出入三項**：`unfinishedReading` 之判讀上移至協議擴充（生產與 mock 同源）、`solidifyFuriousFrontReading` 補注音分支（否則讀取點全數靜默退回）、`confirmFuriousFrontCandidate` 改整體快照／還原。**一項實測查得**：大千排列之 `,` 是注音符號鍵（ㄝ），標點讀取點須以非注音鍵之標點驅動。**IH162 已補做**（P255 之遺留）。**已知界線四項**見 `Reqs_0251-0260.md` 之 Phase 256 篇 §四；P259 新增一項真機驗收項（注音狂打之 copilot 窗可見性）。

### 8.8 Phase 257 — 注音文抑制之落點定案（**v5 大幅簡化**）——**✅ 已完成（2026-09-26）**

| 項 | 內容 |
|---|---|
| **目標** | `shouldSuppressFactoryZhuyinwenData` 改為**兩種狂打皆抑制、兩種非狂打皆不抑制** |
| **落點（v13 補三項）** | `Sources/LexiconAssembly/LXFacade.swift`（`Config` 之 doc comment ＋ `syncPrefs()` 之析取式）；`Tests/LexiconAssemblyTests/LXFacade_FuriousZhuyinwenTests.swift`（＋2 支）。**v13 補**：① **`Package.swift` 之 `LexiconAssemblyTests` 補 `Shared` 直接依賴**（該靶從未 `import Shared`，而本 phase 之驗收必須經偏好；六份 manifest 中只有 `Package.swift` 宣告靶）；② `Sources/LexiconAssembly/LXFacade_TextMapExtension.swift:478／521` 兩處消費點之註解（純註解）；③ **新增整合靶 IH705**（`Tests/LibVanguardTests/InputHandlerTests_TypingModeGate.swift`）——完成定義 ③ 之「下一拍」在 `LexiconAssemblyTests` 內無從表達（該靶無分診） |
| **依賴** | P253（新偏好名）＋ P254（`typingMode` 之新值） |
| **判準（v5 定案）** | `config.shouldSuppressFactoryZhuyinwenData = (prefs.pinyinTypingEnabled && prefs.furiousTypingEnabled4Pinyin) \|\| (!prefs.pinyinTypingEnabled && prefs.furiousTypingEnabled4Zhuyin)` |
| **判準之實查補強（v13）** | 熱鍵之動作實為**兩句**——`PrefMgr.shared.pinyinTypingEnabled.toggle()` **＋** `self.core?.inputHandler?.ensureKeyboardParser()`（`vChewing-macOS/…/MainAssembly4Darwin/SessionController/IMEMenuSputnik.swift:282–283`）⇒ `pinyinTypingEnabled` 即「使用者所宣告之打字方式」之真源，注拼槽之鍵盤家族係由其**導出**、非獨立狀態。故本式不依賴二者之先後，亦不依賴注拼槽之即時狀態 |
| **判準之模式閘（v14，事主裁定）** | 上式再與 `!prefs.cassetteEnabled && !prefs.useSCPCTypingMode` 合取 ⇒ 語意為「**狂打確實生效中**」。**同輪審計另查得**：`performPinyinAutoChopIfNeeded` 原本無任何狂打閘門 ⇒ SCPC 下拼音連打仍自動切音節，已補 `guard !prefs.useSCPCTypingMode`（磁帶不經該型別）。詳見 `Reqs_0251-0260.md` 之 Phase 257 篇 §八 || **為何可續留 `LexiconAssembly` 側（P251 未知四之結論）** | ① `⌃⌘J`（選單項之鍵等效）之動作即 `PrefMgr.shared.pinyinTypingEnabled.toggle()`（`IMEMenuSputnik.swift:280–283`）⇒ 熱鍵改的**正是** `pinyinTypingEnabled`；② `keyboardParser4Pinyin`／`keyboardParser4Zhuyin` 兩槽**不受熱鍵影響**（只有計算屬性 `keyboardParser` 之 setter 才會分流寫入，`PrefMgr_Core.swift:361–370`）；③ `syncPrefs()` 於**每一次分診之頂端**執行（`InputHandler_TriageInput.swift:14`）⇒ 熱鍵之效果**必然在下一拍按鍵被處理之前**反映進 `config`。**故無須**改動 `InputHandler_TriageInput.swift`、**無須**以 `typingMode` 重構推入端 |
| **完成定義（v13 補述）** | ① 既有 2 支測試照舊通過；② 新增斷言：**四態**（拼音狂打／注音狂打／拼音非狂打／注音非狂打）——**實作強化為 8 組全枚舉**，且每組驗兩層（`syncPrefs()` 寫入 config 之值 ＋ 查詢結果是否仍見注音文）；③ **新增一則熱鍵測試**：於 `pinyinTypingEnabled` 切換後之下一拍，抑制旗標須即時改變（**實作強化為兩支**：靶內之 `syncPrefs()` 版 ＋ **整合靶 IH705** 之真實 `triageInput` 版，後者釘住「切換與分診之間仍為舊值」）；④ 兩倉 byte-sync 之輸出 |
| **風險** | **低**。熱鍵那一題已於 P251 查清；本 phase 之改動縮小為一行析取式 |
| **注意** | 該測試族以 `instance.setOptions { $0.shouldSuppressFactoryZhuyinwenData = true }` **直接驅動 config**（`LXFacade_FuriousZhuyinwenTests.swift:45`），**不經偏好** ⇒ 新測試必須改走 `syncPrefs()`，否則它驗不到本案之改動 |
> **完工狀態（v13）**：全倉 `swift test` **630 支／0 失敗**（動工前 627 ⇒ ＋3；`LexiconAssemblyTests` 201 → 203、`LibVanguardTests` 255 → 256）。**靶**：四態真值表（8 組全枚舉、旗標＋查詢兩層）、熱鍵靶（兩顆排列槽一字未動）、整合靶 IH705（真實 `triageInput`；切換與分診之間仍為舊值 ⇒ 分診後即跟上）。**★ 變異測試**：把 `syncPrefs()` 還原為舊式後兩支新靶分別轉紅 4 處與 2 處（兩支既有靶照舊通過——它們直接驅動 config），驗畢已還原。**§8.8 之判準逐字落地**；三條「可續留 `LexiconAssembly` 側」之理由複驗成立，並補一項實查（熱鍵實為 toggle ＋ `ensureKeyboardParser()`）。**落點之出入三項**見上表。**已知界線四項**見 `Reqs_0251-0260.md` 之 Phase 257 篇 §五；其中**磁帶／SCPC 下本式仍以偏好為準**為承前語義（本 phase 未改），已列 §十一。

### 8.9 Phase 258 — 行為層之校正（三項手術；皆由實機回報驅動）——**✅ 已完成（2026-09-26）**

| 項 | 內容 |
|---|---|
| **三筆提交** | ① 注音簡拼與空格：`926cecc`（LV）／`b48a42f2`（macOS）；② copilot 窗排序：`3f6e325`／`e2ba6d61`；③ 回退否決：`30c26dd`／`a7a8103d` |
| **基線** | 631 → **634 支／0 失敗**（`LibVanguardTests` 257 → 260）；兩倉 byte-sync 零差異、鏡像側獨立複跑同值 |
| **靶** | IH162（空格臂改寫）／IH166／IH167（簡拼與窗內排序）／IH168（回退否決）；`LexiconAssemblyTests` 真值表 32 → 64 組 |
| **變異測試** | 三項皆如預期轉紅（逐條見各 Task） |
| **詳細記錄** | `Reqs_0251-0260.md` 之 Phase 258 篇（Task 1／2／3） |

#### 8.9.1 Task 1：注音簡拼與空格／陰平之校正（`926cecc`／`b48a42f2`）

> **事由（事主 2026-09-26 之實機發現，兩項）**：
> ① 「注音狂打模式可能得處理掉對單獨注音的輸入能力，不然注音簡拼怕是沒有辦法處理「ㄍㄋㄋ」這種場合、會永遠被當作三個注音符號插入 assembler。」
> ② 「注音狂打模式不能用空格鍵確認 copilot candidate，不然陰平沒辦法輸入了。」
> 事主其後補充：「**也可能是我歸因有誤**。」⇒ 本節先實測、後設計；**實測已完成，結論是：② 成立且已量化；① 之歸因不成立、但所指之功能確實缺失。**

| 項 | 內容 |
|---|---|
| **目標** | ① 讓注音狂打能處理「ㄍㄋㄋ」類**單注音序列之簡拼**（整詞查詢）；② 讓**空格在注音狂打下仍是陰平鍵** |
| **落點** | `Typewriter_BPMFFullMatch.swift`（空格之固化語義分流、簡拼 cells 之生成）、`InputHandler_HandleStates.swift`（`furiousFrontContext` 之注音分支擴充、copilot 窗候選之併入）、`InputHandler_TriageInput.swift`（空白鍵之狂打觸發集合）、`LXFacade`（既有 `abbreviatedWordCandidates(keysChopped:)` 之消費者首次出現）；測試：`InputHandlerTests_ZhuyinFurious.swift`（＋新靶）、`InputHandlerTests_FuriousCopilotWindow.swift`（IH162 之空格臂改寫） |
| **依賴** | P255（自動切音節）＋ P256（copilot 窗）＋ P257（注音文抑制） |

##### 8.9.1.1 術前實測（2026-09-26，本機；五支臨時探針，跑畢已刪）

| # | 問題 | 實測 |
|---|---|---|
| A | 注音狂打下鍵入 ㄍㄋㄋ（大千 `ess`）之實況 | `assembler.actualKeys ＝ ["ㄍ","ㄋ"]`、注拼槽＝「ㄋ」、顯示＝「ㄍㄋㄋ」、copilot 候選＝`["ㄋ"]`、窗可見 ✔ **事主之「三個注音符號插入」之觀察正確**（兩顆已入組字器、一顆待確認） |
| B | 單注音可否作簡拼 cell | `abbreviatedWordCandidates(["ㄍ","ㄋ","ㄋ"])` ⇒ **`["狗男女", "幹你娘"]`**（以臨時插入之兩條整詞 gram 驗之）；`(["ㄍ"])` ⇒ 高／供／公／… 共 59 筆（單注音展開成整個聲母家族）✔ **API 完全吃得下單注音 cell** |
| C | 空格之語義（狂打 vs 非狂打） | 令去聲候選分數遠高於陰平（−0.1 vs −9）：**狂打＋空格 ⇒ `["ㄍㄠˋ"]`（顯示「號去聲」）**；**非狂打＋空格 ⇒ `["ㄍㄠ"]`（顯示「高」）** ⇒ **事主②成立**：狂打下空格插入的是**無調讀音桶**，故使用者無法指定陰平 |
| D | Tab／Enter 於注音狂打之意義 | 兩者皆固化（插入桶）並停留 `.ofInputting`、注拼槽清空 ⇒ 與空格同語義；**此即「空格不必兼任固化」之依據**：固化另有 Tab／Enter／標點三條路 |
| E | 「尾段鍵＋注拼槽」可否還原成簡拼 cells | 鍵入 `ess` 後：`assembler.suffix(2) ＝ ["ㄍ","ㄋ"]`、注拼槽＝「ㄋ」⇒ cells ＝ `["ㄍ","ㄋ","ㄋ"]` ⇒ **查得 `["狗男女", "幹你娘"]`** ✔ **序列可還原，無須新增緩衝** |

##### 8.9.1.2 歸因之更正（② 成立；① 不成立）

- **② 成立**：空格在注音側本為**陰平鍵**（大千排列之五個聲調鍵＝`3`／`4`／`6`／`7`／**空格**），而 P256 把拼音側「空格＝無調確認組字」之語義整組搬了過來（`TriageInput` 之狂打分支把 `isSpace` 收進固化觸發集合）⇒ 陰平**無法被指定**（實測 C）。
- **① 之歸因不成立**：單注音被插入組字器**不是**簡拼之障礙——實測 B／E 顯示：① 既有 `abbreviatedWordCandidates(keysChopped:)` 對單注音 cell 逐位置 byte 前綴匹配，**無須任何展開表或笛卡爾積**（單次有界 Trie 查詢）；② 已入組字器之單注音鍵與注拼槽之待確認音節**恰可還原**出完整之 cells。⇒ **無須**「處理掉對單獨注音的輸入能力」；真正的缺口是**注音側從未呼叫該 API**（P256 之注音分支只由「當前音節之聲調變體桶」產生候選，故 `ㄍㄋㄋ` 只見 `["ㄋ"]`）。
- **故本 phase 不動單注音之輸入能力**：其自動切出之語義照舊（P255 之 IH155 未改），簡拼只是**額外**提供整詞候選——兩者為互補而非互斥（`ㄍㄋㄋ` 之序列既進得了組字器、亦查得出整詞）。

##### 8.9.1.3 設計（兩項）

1. **空格還原為陰平鍵**：注音狂打之固化觸發集合**移除 `isSpace`**（拼音側不變——拼音之空格本即確認鍵）。空格自此照常送入注拼槽（＝陰平），並由既有 `composeReadingIfReady` 之路徑完成組字；Tab／Enter／標點之固化語義不變（實測 D 已證其足）。
2. **注音簡拼（α 之注音對位）**：於 `furiousFrontContext` 之注音分支併入**簡拼候選**——cells 之取法為「組字器尾段之單注音鍵（至多有界，建議 ≤ 4）＋ 注拼槽之當前讀音」，經 `abbreviatedWordCandidates(keysChopped:)` 取得整詞候選後，**與既有之前方候選同一清單**（沿用 `buildFuriousFrontCandidates` 之置頂／排序／去重與就地選字語義）。**不新增狀態**（實測 E）；**不動 `furiousTrail`**（`trail` 之語義仍為拼音字母 blob；注音側不寫 trail 之 P255 斷言照舊）。

##### 8.9.1.4 完成定義

| # | 項 |
|---|---|
| ① | 空格在注音狂打與非狂打下**同義**（皆為陰平；以實測 C 之分數配置為靶：同一測資下兩者皆得陰平候選） |
| ② | 注音狂打下 `ㄍㄋㄋ` 之 copilot 窗**可見簡拼整詞候選**（以臨時插入之 `狗男女`／`幹你娘` gram 為靶），且可就地選字寫入組字器 |
| ③ | 既有之拼音側語義**逐支照舊**（67 支狂拼測試 ＋ P256／P257 之各靶）；P255 之 IH155（自動切音節之三鍵）與 IH163（注音不寫 trail）**照舊** |
| ④ | IH162 之「空格臂」依本 phase 改寫（其原文釘住之「空格固化」為 P256 之過寬語義） |
| ⑤ | 兩倉 byte-sync 之輸出 |

##### 8.9.1.5 風險

| # | 風險 | 等級 | 緩解 |
|---|---|---|---|
| 1 | 簡拼候選與「前方候選」同窗時之排序／去重 | 低 | 沿用既有 `buildFuriousFrontCandidates`（詞長降冪 → 分數降冪 → 去重） |
| 2 | 尾段掃描之界線（幾個 cell？） | 中 | 有界（建議 ≤ 4）；超出即有界截斷，並以靶釘住 |
| 3 | 單注音被視為「已提交之音節」時，簡拼選字須**回頭覆寫**已入組字器之鍵 | 中 | 沿用 P256 之就地確認機制（`applyFuriousFrontCandidate`／`confirmFuriousFrontCandidate`），其本即處理「跨多鍵之覆寫」 |
| 4 | 空格語義變更之回歸面 | 低 | 注音側之靶（IH155／156／157／159／162／163／164）逐支複跑 |

##### 8.9.1.6 施工查得（規劃書未載；實作障礙與其正解）

**障礙**：初稿把簡拼視為「跨邊界候選」之變體（只補插尾段讀音、覆寫焦點退至 `anchor - span`）。**該作法必然落空**，因 `Homa.Assembler.overrideCandidateAgainst` 之守衛要求目標節點**已含**該 keyArray：

```swift
if let keyArray, !anchor.node.allActualKeyArraysCached.contains(keyArray) { continue }
```

而簡拼時組字器之鍵鏈是**單注音**（`ㄍ`、`ㄋ`），與該詞之讀音（`ㄍㄡˇ`、`ㄋㄢˊ`、`ㄋㄩˇ`）不符 ⇒ 語言模組不會為該 span 建立含該 keyArray 之節點 ⇒ 覆寫**靜默落空**（實測：僅尾段讀音入庫、顯示成「ㄍㄋ女」）。

**正解**：**先 `dropKey(direction: .rear)` 移除尾段之單注音鍵、再把該詞之讀音整段插入**——鍵鏈因而恰為該詞之讀音，語言模組方得建立節點、`overrideCandidate(.withSpecified)` 方得成立。實作為 `applyFuriousFrontCandidate` 內之獨立 early-return 路徑，並以模式旗標設閘（拼音側之尾鍵為完整讀音、不存在此情形）。

**通則**：凡「以候選覆寫既有鍵」之新路徑，皆須先自問「目標節點是否可能已含該 keyArray」——若鍵鏈與候選讀音不同源，覆寫必落空，須改為「先改鍵鏈、再覆寫」。

| **落點** | 見上 |
| **真機項** | 簡拼於原廠辭典下能否給出「狗男女」；以及簡拼候選於實機之排序觀感 |
> **完工狀態（v18）**：全倉 `swift test` **633 支／0 失敗**（動工前 631 ⇒ ＋2；`LibVanguardTests` 257 → 259）；兩倉 byte-sync 零差異、**鏡像側獨立複跑同為 633 支／0 失敗**。**靶**：IH166（cells 之還原與三條界線）／IH167（整詞候選與就地選字）／IH162 之空格臂改寫。**變異測試**：拿掉空格閘 ⇒ IH162 轉紅 2 處（`["ㄍㄠˋ"]`、「去聲測」——正是事主所述症狀）；拿掉簡拼併入 ⇒ IH167 轉紅（窗內僅餘 `["ㄋ"]`——正是 P258 前之實況）。**一項實作障礙與其正解**見 §8.9.1.6（`overrideCandidate` 之 keyArray 守衛）。**已知界線五項**見 `Reqs_0251-0260.md` 之 Phase 258 篇 §四。**未驗**：真機。

#### 8.9.2 Task 2：copilot 候選窗之排序校正（`3f6e325`／`e2ba6d61`）

| 項 | 內容 |
|---|---|
| **事由** | 事主 2026-09-26 以實機截圖指示：「你方便介入一下這個 copilot 選字窗的排序嗎？把單獨輸入的注音在 copilot 選字窗的優先權降低。或者說讓長詞更優先。」截圖所示之窗（注音狂打、鍵入 ㄍㄋㄋ）依序為 `ㄋ`、`狗男女`、`姑奶奶`、`告奶奶`——**第 1 名係讀音原字串回退值、非真詞** |
| **目標** | ① 讀音原字串回退值不置頂；② 長詞優先（既有 `ranked` 之規則本即如此，缺的只是把該筆回退值自置頂段請下來） |
| **落點** | `InputHandler_HandleStates.swift` 之 `buildFuriousFrontCandidates`（置頂判定 ＋ 排序鍵之段數折算 ＋ `rawReadingFallbackWeight`）；`Tests/LibVanguardTests/InputHandlerTests_FuriousCopilotWindow.swift`（IH167 增補斷言） |
| **判準** | 置頂 ⇔ 預覽值**不**落在前方讀音桶內（桶內者＝讀音原文）；排序段之段數以 `effectiveSegmentCount` 折算（桶釘候選為 1 段） |
| **完成定義** | ① 真詞須居首（IH167）；② 拼音側與 POM／crossingPair 之置頂語義不變；③ 全倉測試 0 失敗；④ 兩倉 byte-sync |
| **風險** | 低。惟**桶釘候選之段數折算**為必要配套——少了它，降級項會因 5 個桶內讀音而被當成「5 段長詞」而躍居首位（實測） |
| **真機項** | 原廠辭典下之候選集合與排序觀感（併入 P259 之真機清單） |
> **完工狀態（v19）**：全倉 `swift test` **633 支／0 失敗**（支數不變——只強化既有靶）；兩倉 byte-sync 零差異、鏡像側獨立複跑同為 633 支。**變異測試**：置頂判定改回無條件置頂 ⇒ IH167 轉紅，實得 `["ㄋ","狗男女"]`（**與事主截圖逐項相同**）。**已知界線四項**見 `Reqs_0251-0260.md` 之 Phase 258 篇 §四；其中「回退值是否改為過濾而非降級」列為 §十一 #20 待事主裁定。

#### 8.9.3 Task 3：中英混合輸入回退否決注音狂打（`30c26dd`／`a7a8103d`）

| 項 | 內容 |
|---|---|
| **事由** | 事主實機回報：「注音狂打模式開啟之後、注音中英文輸入回退會失效」。裁定：「如果中英文輸入回退有被啟用的話，哪怕注音狂打模式開關有開啟，注音狂打模式也得被 InputHandler / Typewriter 認為是關閉的。」 |
| **根因** | 不是「相爭落敗」而是「**回退從未執行**」：`typingMode` 之判定只問狂打開關 ⇒ 得 `.zhuyinFuriousTyping` ⇒ `handleComposition` 把 ASCII 按鍵全數派給 `BPMFFullMatchTypewriter`，回退之打字機**連建構都沒發生**。旁證：空格不走 `handleComposition`（`TriageInput` 之 `kSpace` 分診只讀 `mixedAlphanumericalEnabled`），故空格仍走回退、字母鍵則被狂打吸收——事主所見之割裂即此 |
| **① 之落點（模式層）** | `Sources/LibVanguard/InputHandler/InputHandler_TypingMode.swift`：`typingMode` 之注音臂加 `&& !prefs.mixedAlphanumericalEnabled`（生產碼 1 行）；`.zhuyinFuriousTyping` 之文件註解補述 |
| **② 之落點（辭典層；施工查得）** | `Sources/LexiconAssembly/LXFacade.swift`：`syncPrefs()` 內 `shouldSuppressFactoryZhuyinwenData` 之析取式同步補同一維度（該處為模式判定之就地複製品，見 §7.1／§7.4 之補述） |
| **判準** | 回退啟用 ⇒ `typingMode == .bopomofoKeyblock`、`isFuriousTypingModeEffective`／`isZhuyinFuriousTypingModeEffective` 皆假、`hasFuriousFrontPending` 假、copilot 窗不成立、注音文**不**被抑制；**開關本身之值一字不改**。**拼音側不受影響**（回退於拼音下本即不生效） |
| **不打折者** | 否決**可逆**（關掉回退 ⇒ 狂打即刻復活）；ASCII 回退本身須如常工作（行為層之遞交） |
| **靶** | ① **IH168**（`InputHandlerTests_FuriousCopilotWindow.swift`）——五段：基線／否決／**行為層之 `film ` 遞交**／可逆／拼音側不牽連；② `LexiconAssemblyTests/LXFacade_FuriousZhuyinwenTests.swift` 之真值表維度 5 → 6（**32 → 64 組**），期望式之注音側改為 `furious4Zhuyin && !mixedAlnum` |
| **文案** | 四語系各 2 條：`kFuriousTypingEnabled4Zhuyin.description` 與 `kMixedAlphanumericalEnabled.description` 各補一句優先權之敘述。**不新增 UI 連動停用**——沿用 P259「兩者係並行選項、非從屬關係，故不做 UI 層之連動停用」之既有決定；同型先例（`kAcceptLeadingIntonations`／`kSpecifyIntonationKeyBehavior`／`kAutoCorrectReadingCombination`）亦皆為**文案 ＋ 程式閘** |
| **風險** | 低。① 唯一之系統性風險是**兩處模式判定之脫鉤**（見 §7.1 之「同步義務」）——已以 64 組真值表 ＋ IH168 雙向守住；② 助手之 presets 無待改之項（實查：**無任何 profile 同時推薦兩者為真**——注音狂打在所有具名 profile 下一律 `false`，見 `questions.ts`） |
| **完成定義** | ① 兩處同步補維；② IH168 入靶且變異測試轉紅；③ 真值表擴至 64 組；④ 四語系文案就位、後設資料重生且無漂移；⑤ 聚合體套件兩倉同值全綠；⑥ 兩倉 byte-sync |
> **完工狀態（v23）**：聚合體套件 **634 支／0 失敗**（基線 633 ⇒ ＋1；`LibVanguardTests` 259 → 260）、**鏡像側獨立複跑同值**；助手 `make test` **81 支／全過**、`make audit` **exit 0**（surface 108 鍵無漂移）、`SettingsUI` **19 支／4 套／0 失敗**；**變異測試**：拿掉 `typingMode` 之否決 ⇒ IH168 轉紅 **4 處**（含行為層之 `"film "` 遞交失敗）。**已知界線四項**見 `Reqs_0251-0260.md` 之 Phase 258 篇 §九。**未驗**：真機。**（v24 補註）**：本節之「四語系各 2 條 `description` 補上優先權之敘述」中，**注音側那一句已由 §8.10.6（P259）改為置首警示**——即同一件事不再於句中重述；混輸回退側（`kMixedAlphanumericalEnabled.description`）之句照舊。

---

### 8.10 Phase 259 — 介面、文案與助手之收束（**含全系列之驗收**）——**✅ 已完成（2026-09-26）；本系列於此收束**

| 項 | 內容 |
|---|---|
| **提交** | 單筆 `9f90dd12`（「SettingsUI & WebAssistant // Furious: Necessary updates.」）——於定稿時吸收了原本分列之五項工作 |
| **驗證** | 四語系各 619 鍵且鍵集逐項相同；助手 `make audit` exit 0（**82 支／全過**）＋曝露面 108 鍵無漂移；`SettingsUI` 19 支／4 套／0 失敗 |
| **I2** | 本 phase 未動聚合體套件 ⇒ 空操作 |
| **詳細記錄** | `Reqs_0251-0260.md` 之 Phase 259 篇（六節） |

#### 8.10.1 設定介面之露出、四語系文案與助手之對帳

| 項 | 內容 |
|---|---|
| **目標** | 兩顆開關在使用者可及之處現身；四語系文案齊備；防漂移產物重生 |
| **落點** | `Packages/vChewing_SettingsUI/Sources/SettingsUI/SettingsUI/VwrSettingsPaneBehavior.swift:104–106`（SwiftUI）；`…/SettingsCocoa/VwrSettingsPaneCocoaBehavior.swift:209–214`（AppKit 對位）；`Sources/vChewingIME_macOS/Resources/{en,ja,zh-Hans,zh-Hant}.lproj/Localizable.strings`（**v10 補一條**：`i18n:TypingMode.i18nKey4InlineModeHint.zhuyinFuriousTyping`；＋4 條 × 4 語系：兩條 `…4Zhuyin` 之新鍵、一條 `…4Pinyin` 之改名、一條 `TypingMode…zhuyinFuriousTyping` 之新鍵）；`ValueAdd/WebConfigAssistant/src/questions.ts:521`（手寫之種子鍵清單）；`ValueAdd/WebConfigAssistant/tests/metadata.test.js:26`（`count` 118 → 119）；`ValueAdd/WebConfigAssistant/assets/{userdef-metadata.json, settings-surface.json}`（重生）；`ValueAdd/WebConfigAssistant/tests/fixtures/{kimo-zhuyin,msnewphonetic-scpc,pinyin-newbie}.json`（重生） |
| **依賴** | P253（偏好名）＋ P256（新 `TypingMode` case 之 i18n 鍵） |
| **完成定義** | ① 助手 `make audit` 全綠（含 `metadata`／`metadata-audit`／`surface-check`／`fixtures-check` 四道防漂移）；② `Localizable.strings` 之四語系鍵集一致、且經 `LocalizableFileSorter.swift` 排序後逐位元組穩定；③ `SUI/Tests/SettingsUITests/AssistantContractTests.swift` 之 4 支契約測試全綠（**此即 §6.4 之舊配置包問題在測試上之現形處**）；④ 兩倉 byte-sync 之輸出（`Sources/` 之改動僅 `Shared/` 之 i18n 鍵字串，須鏡像） |
| **兩顆開關之排版（建議）** | SwiftUI 側：**同一 `Section` 內兩列**（`4Pinyin` 在上、`4Zhuyin` 在下），**不**做 UI 層之連動停用——因二者是**並行**選項、非從屬關係。AppKit 側：照 `NSStackView.buildSection` 之既有形制，兩列同一 section（`VwrSettingsPaneCocoaBehavior.swift:85–90` 之既有說明已交代為何不做連動停用） |
| **文案之關鍵一句** | 注音側之 `description` 須**明示單聲母可用**（§7.5）；且須寫明**注音文會被過濾**（P257 之行為） |
| **風險** | 中。四語系文案之語體（zh-Hans-TW）與 ja 之「狂打ち／狂拼／狂注」定譯；防漂移產物之重生順序（**須照 `Makefile` 之依賴鏈：`metadata-update` → `surface` → `fixtures`**） |
> **完工狀態（v15）**：**13 檔全在 `vChewing-macOS` 倉**；聚合體套件零改動 ⇒ **I2 為空操作**（`vChewing-LibVanguard` 之 `git status` 為空）。**驗證**：助手 `make audit` **exit 0**（`test` 78 支／全過；`metadata`／`metadata-audit`／`surface-check`／`version-check`／`fixtures-check` 全綠）、`Packages/vChewing_SettingsUI` **19 支／4 套／0 失敗**（含 4 支契約靶）、倉根 `swift build` ⇒ `Build complete!`、四語系 `Localizable.strings` **各 619 鍵、鍵集逐項相同**、`LocalizableFileSorter.swift` **二次執行 sha256 不變**；`metadata.count` 119、`missingI18nKeys`／`pendingMetadataKeys` 皆 `[]`、surface `count` 108。**★ 三項文案出入**（§7.5 草案寫在行為落地之前）：草案之「不會過濾注音文」「不會以 LM 試算未完成讀音」兩句皆已與 P256／P257 之實況不符 ⇒ 定稿改寫，並補明空格／Enter 之語義與單聲母可用（§8.10.1「文案之關鍵一句」）。**（v20 補註）**：該定稿之「空格固化」與「單注音為音節」兩處，已因 P258 之兩項手術（空格仍是陰平鍵；單注音序列改視為簡拼、長詞優先）而**再度修訂**——見 §8.10.3 與 `Reqs_0251-0260.md` 之 Phase 259 篇 §二。**★ 清償 P253 之三項助手漂移**（metadata／surface／fixtures 皆仍帶舊鍵名）。**★ 可達性自此改變**：`.zhuyinFuriousTyping` 不再只能靠手改 defaults 或匯入配置包觸及 ⇒ P255／P256／P257 之行為自此進入正式使用情境（P259 之真機驗收項亦隨之改以前提敘述）。**一項刻意未改**：en 之拼音行內提示仍為 "Furious Typing"（§8.10.1 之 i18n 清單只列新增 3 條）。**已知界線四項**見 `Reqs_0251-0260.md` 之 Phase 259 篇 §四。

#### 8.10.2 跨倉驗收與可建置性（本系列之收束）

| 項 | 內容 |
|---|---|
| **目標** | 全系列之收尾：跨倉逐位元組總驗、Swift 5.10 側之可建置性、文書三件套 |
| **落點** | 無生產碼改動（除本 phase 自身發現之缺漏）；`vChewing-DevLogs` 三件套；`vChewing-macOS/AGENTS.md` 若有過時敘述則一併修 |
| **依賴** | P252–P259 全部 |
| **完成定義** | ① 兩倉 `Sources/`／`Tests/`／`Deps/`／六份 manifest／`makefile` 之 `cmp`／`diff -rq`／`shasum` 逐項輸出，且**零差異**（僅 `.DS_Store`）；② 兩倉 `swift test` 各自單獨跑、全綠、項數與動工前基線之**同框對照**；③ `make build510`（逐套件）與可及之 legacy 路徑之可建置性（**注意**：`Tekkon` 之 5.10 側為 static archive，新增檔須自動納入；`Package@swift-5.10.swift` 之 `Tekkon` 靶若列舉檔案則須同步——**實查：本倉 manifest 以目錄為單位、不逐檔列舉**，故無需改 manifest）；④ 助手 `make audit` 全綠；⑤ 文書：本卷之各 phase 記錄（252–259 各自寫入其所屬卷，251 亦然）、`DevReqsHistory.md` 逐 phase 一行、`KnowledgeMemo4LLM.md` 之更新；⑥ 若 P255／P256 之行為於實機上有未及之情形，於本 phase 記錄為「已知界線」而非強行修補 |

> **v8 預驗（2026-09-26，P252 收尾時順帶執行）**：本 phase 之完成定義 ③（Swift 5.10 側之可建置性）**已先行驗過一次**——於 P252 之交付狀態下：
> - `/Library/Developer/Toolchains/swift-5.10.1-RELEASE.xctoolchain/usr/bin/swift build --triple x86_64-apple-macosx10.9 --sdk /Library/Developer/CommandLineTools/SDKs/MacOSX13.3.sdk …` ⇒ **`Build complete!`**（整包 106 步全過，含 `Tekkon` 之新檔）。**故「新增檔須自動納入」之斷言得到編譯器層之確認**（六份 manifest 皆以靶名宣告、不逐檔列舉 `sources:`）。
> - **注意（環境事項，非倉之問題）**：本機 harness 之檔案沙箱會擋掉 SwiftPM 自身用以編譯 manifest 的 `sandbox-exec`（`sandbox_apply: Operation not permitted`），故 **`make build510` 在此環境下必失敗**；解法是在命令列手動補 `--disable-sandbox`。此與本倉紀律「SwiftPM 一律附 `--disable-sandbox`」（`KnowledgeMemo4LLM.md:397`）一致——該紀律是**呼叫端**之紀律，`makefile` 之 `build510`／`test` 等 target **並未**內建該旗標（實查：`grep -n "disable-sandbox" makefile` 無命中）。在一般開發機上 `make build510` 應可正常通過。
> - **另一件順帶驗過者**：P255 之判準可否只以 Tekkon 之 public API 實作。作法：把 §3.2 之 v7 判準**原樣**搬進 `Sources/LibVanguard/`（該靶只有 `import Tekkon`，非 `@testable`）並以**兩套 toolchain 各編一次** ⇒ 6.4 與 5.10 皆 **`Build complete!`**。**故 P255 不需任何 Tekkon 新 API**（該探針檔已刪，未入庫）。此為「Tekkon 於本系列之改動已全部完成」之**編譯器層證據**。

> **完工狀態（v16）**：**零生產碼改動**。完成定義六項全數成立——逐位元組總驗（220 檔 SHA-256 全同、`cmp` 8/8、`diff` 0 行）、兩倉各自 **631 支／0 失敗**、5.10 逐套件（聚合體 ＋ `SettingsUI`）與 legacy 路徑皆可建置、助手 `make audit` exit 0（78 支）、文書三件套 ＋ `AGENTS.md` 實查無過時敘述、真機項收攏為 11 項清單。**legacy 產物之獨立複驗**：universal、x86_64 `minos 10.9`／arm64 `minos 11.0`、兩份 plist 皆 `LSMinimumSystemVersion 10.9`、辭典資產注入正確、**時刻晚於 P259 之提交 ⇒ 涵蓋全系列改動**。**環境事項（非倉之問題）**：本機 harness 之沙箱擋掉 SwiftPM 之 `sandbox-exec` ⇒ `make build510` 在此環境必失敗，須補 `--disable-sandbox`；事主未加該旗標而 legacy 兩目標皆過，即為該失敗純屬 harness 之反證。**全系列基線**：**592 → 631（＋39）**。**移交三項**：真機驗收 11 項（事主）、`vChewing-VanguardLexicon` 之注音文正本（另倉）、iOS 移植（另立 phase）。詳見 `Reqs_0251-0260.md` 之 Phase 259 篇。

#### 8.10.3 UI 文案之對帳

| 項 | 內容 |
|---|---|
| **事由** | 事主實機複驗 P258 之兩項手術無誤後指示：「你現在再檢討各種 UI 文案、確保 description 描述準確。」 |
| **目標** | 逐條檢討與狂打模式相關之**全部**使用者可見文案，確保與**現行**行為相符（不限本系列新增者） |
| **落點** | 四語系 `Sources/vChewingIME_macOS/Resources/{zh-Hant,zh-Hans,ja,en}.lproj/Localizable.strings`（各改 1 條）＋ 助手 `assets/userdef-metadata.json`（重生） |
| **依賴** | P255–P258（文案所描述之行為即其交付物） |
| **完成定義** | ① 審計表逐條成立（見 `Reqs_0251-0260.md` Phase 259 篇 §一）；② 四語系鍵集一致且排序穩定；③ 助手 `make audit` 全綠；④ `SettingsUI` 之 4 支契約靶全綠；⑤ I2（本 phase 為空操作） |
| **審計之結論** | **僅 1 項不準確**（注音側 `description`，兩處），其餘（拼音側 `description`、兩條行內模式提示、助手全部文案）**準確、未動** |
| **風險** | 低。惟**文案隨行為漂移**為結構性風險：凡改動狂打之行為，**同一 phase 內**即須回檢其文案（本 phase 即 P258 改空格語義後之補課） |
| **真機項** | 偏好面板內說明欄之實際排版（文案變長後之行數與換行） |
> **完工狀態（v20）**：助手 `make audit` **exit 0**（78 支／全過）；`SettingsUI` **19 支／4 套／0 失敗**；四語系**各 619 鍵、鍵集逐項相同**、排序冪等；助手產物僅 `userdef-metadata.json` 變更（未增刪鍵 ⇒ surface／fixtures 不變）。**I2 為空操作**。**已知界線三項**見 `Reqs_0251-0260.md` 之 Phase 259 篇 §四。**（同日再修訂，以 amend 併入）**：事主另定兩條 `description` 之首句（狂注「以不完整的讀音連續進行注音打字」／狂拼「以不完整的讀音連續進行拼音打字」），狂注移除 iOS 之提及、狂拼補上注音文過濾之說明（P257 之行為、舊稿缺載）。

#### 8.10.4 助手之後設資料機制查核與 presets 之狂打開關定值

| 項 | 內容 |
|---|---|
| **事由** | ① 事主之提問：「`assets/userdef-metadata.json` 的自動同步機制現在是壞掉了還是？我記得 WebConfigAssistant 的倉庫的 makefile 體系會自動更新這個檔案的？」② 事主之裁定：「WebConfigAssistant 注意調整 presets：所有注音打字方案都需要刻意關閉注音狂打模式，因為這個模式就不是給桌面電腦用的。所有拼音打字方案都需要刻意開啟拼音狂打模式。」 |
| **① 之結論** | **未壞、且本即設計為「亮紅燈」**：`metadata` ＝檢查（`cmp` ＋ `exit 1`）、`metadata-update` ＝寫入、`audit` 含前者；**無任何 target／hook／CI 自動改寫之**。變異測試證明絆線有效。順帶修正 README 之三個過期數字。 |
| **② 之落點** | `ValueAdd/WebConfigAssistant/src/questions.ts`（`recommendationFor` 新增兩案）、`tests/questions.test.js`（＋1 支靶）、`tests/fixtures/starter-macoszhuyin.json`（重生）、`README.md` |
| **② 之判準** | 注音各方案（`typing` ∈ {`zhuyin`,`zhuyinmix`,`scpc`}，或 `typing=unsure` 而來源為注音系之八者）⇒ `kFuriousTypingEnabled4Zhuyin` **指名 `false`**；拼音各方案（`typing=pinyin`，或 `typing=unsure` 而來源為 `pinyin`）⇒ `kFuriousTypingEnabled4Pinyin` **指名 `true`** |
| **為何「指名」而不只是「值對」** | 值雖等於出廠預設，但**只有指名才會被起始配置寫入**——而只有寫入才能**主動覆蓋**使用者機器上與之相左之現值（尤其是自行開啟之狂注）。此為策展紀律①之**經核定例外**。 |
| **完成定義** | ① 兩鍵進入 `starterUniverse()`（全集 16 → 18）；② 三種注音打字方式與八個注音系來源皆指名關閉、拼音方案指名開啟（新靶）；③ 助手 `make audit` 全綠；④ `SettingsUI` 之契約靶全綠；⑤ 兩倉 byte-sync |
| **風險** | 低。惟**「全集之收錄條件」為本類需求之隱形閘**：凡「起始配置未涵蓋某鍵」之症狀，先查該鍵是否有推薦值（否則它根本不在全集內），而非先查值之推算 |
> **完工狀態（v21）**：助手 `make audit` **exit 0**（`test` **79 支／全過**；四道防漂移全綠、surface 108 鍵無漂移）；`Packages/vChewing_SettingsUI` **19 支／4 套／0 失敗**。`starterUniverse()` 16 → **18** 鍵；`starter-macoszhuyin.json` 重生為 18 鍵（＋`FuriousTypingEnabled4Pinyin: true`（回歸）＋`FuriousTypingEnabled4Zhuyin: false`（指名））；其餘四份 fixture 值不變。**I2 空操作**。**已知界線四項**見 `Reqs_0251-0260.md` 之 Phase 259 篇 §四。

#### 8.10.5 術語統一暨助手之三項來源裁定

| 項 | 內容 |
|---|---|
| **事由** | ① 事主之術語裁定：「狂注 -> **注音狂打 / 注音狂打ち / Furious Zhuyin**；狂拼 -> **拼音狂打 / 弁音狂打ち / Furious Pinyin**。**此前的功能稱謂正式停用。**」② 事主對 P259 §十一 #21／#22 之答覆：「CIN 來源無須調整該特性；Newbie 來源現階段刻意停用該特性。GoingIME 是自然輸入法（不是自然碼輸入法，自然碼是字根輸入法），是主推許氏注音鍵盤佈局打字的，預設情況下關閉注音狂打。」 |
| **① 之落點** | 四語系 `Sources/vChewingIME_macOS/Resources/{zh-Hant,zh-Hans,ja,en}.lproj/Localizable.strings`（各 6 條）、助手 `assets/userdef-metadata.json`（重生）、`tests/metadata.test.js`（**新增術語護欄**）、`README.md`（測試支數） |
| **① 之判準** | 舊稱謂（`狂拼`／`狂注`／`狂拼モード`／`狂注モード`／`Furious Typing`／`Furious Zhuyin Typing`）於**四語系字串與後設資料中一字不留**；新稱謂須見於兩鍵之四語系 `shortTitle` 與兩條行內模式提示 |
| **② 之落點** | 助手 `src/questions.ts`（**新增 `ORIGIN_VETOED_KEYS` 來源級否決** ＋ 兩案之註解）、`tests/questions.test.js`（改 1 支、＋1 支）、`tests/fixtures/pinyin-newbie.json`（重生）、`README.md` |
| **② 之判準** | **CIN**：不指名（維持原狀）；**newbie**：**任何**打字方式下兩鍵皆**指名 `false`**；**GoingIME**：歸注音系（其 zhuyin 鍵指名 `false`）、不涉拼音側 |
| **為何需要新機制** | 本檔之推薦序為「打字方式 ＞ 來源」；而「newbie 之**任何**打字方式皆停用」是「來源 × 打字方式」之合取條件，**無從以既有之兩張表表達**（`kFuriousTypingEnabled4Pinyin` 之一般規則為「拼音方案刻意開啟」，newbie 須否決之）⇒ 新增 `ORIGIN_VETOED_KEYS`：**來源級否決優先於一切**，其值一律 `false`（該表所列皆 bool、語義即「停用」）。**被否決之鍵仍屬全集**（否決＝指名 `false`，非不予輸出） |
| **完成定義** | ① 舊稱謂清零、新稱謂在位（四語系 ＋ 後設資料）；② 術語護欄入靶；③ newbie 之否決以靶釘住、`pinyin-newbie.json` 反映之；④ 助手 `make audit` 全綠；⑤ `SettingsUI` 契約靶全綠；⑥ 兩倉 byte-sync |
| **風險** | 低。惟**歷史記錄之處理**須明示：本卷各 phase 記錄、`DevReqsHistory.md` 各列、本文之〈修訂沿革〉**一律保留舊稱謂**——因其中多有**事主原文之逐字引用**，改之即偽造引文 |
> **完工狀態（v22）**：助手 `make test` **81 支／全過**（79 → 81：＋newbie 否決靶、＋術語護欄）、`make audit` **exit 0**（surface 108 鍵無漂移）、`Packages/vChewing_SettingsUI` **19 支／4 套／0 失敗**；四語系**各 619 鍵且鍵集逐項相同**、排序冪等、舊稱謂於四語系與後設資料**皆為 0**；`pinyin-newbie.json` 之 `FuriousTypingEnabled4Pinyin` 由 `true` 改為 **`false`**（newbie 否決之固化物）。**I2 空操作**。**已知界線三項**見 `Reqs_0251-0260.md` 之 Phase 259 篇 §四。

**卷之歸屬**：`Reqs_0241-0250.md` 於本 phase（250）之後即達 10 個 Phase（241–250）之滿卷條件 ⇒ **Phase 252 起寫入後繼之新卷**。依〈Reqs4LLM 分卷歸檔註記〉之現算紀律，新卷為 `Reqs_0251-0260.md`，其落點目錄仍為 `Archive_P201-P300/`（該百位段未滿 100 個 Phase，故仍續收）。

#### 8.10.6 注音狂打警示之置首

| 項 | 內容 |
|---|---|
| **事由** | 事主：「`kFuriousTypingEnabled4Zhuyin` 的 description 得在**最開頭**就顯示『⚠︎ 該模式無法在中英文輸入回退模式啟用時起作用。』＋換行，因為插在其他位置的話不醒目。」 |
| **處置 ①** | 四語系之該條 `description` 首行插入警示句（`⚠︎` ＝ **U+26A0 ＋ U+FE0E**、其後一個半形空格、其後 `\n`）。**定稿四語系一律用各自 `shortTitle` 之正式稱謂**（見「處置 ③」） |
| **處置 ②** | **移除 §8.9.3（P258）加在句中**的那一句——同一件事在一條字串內說兩次既冗餘、又會出現兩種稱謂（P258 之句用「中英混合輸入回退」、事主之句用「中英文輸入回退模式」）⇒ 以事主之句為唯一出處 |
| **處置 ③（事主之再修訂）** | 事主更正其措辭（「我剛才寫錯，還得是「中英混合輸入回退」。」）⇒ zh-Hant／zh-Hans 之首行改用正式稱謂「中英混合輸入回退」；ja／en 原即用其對位之正式稱謂（「中英混在入力のフォールバック」／“the mixed Chinese-English typing fallback”）故不動 ⇒ **四語系之首行與各自 `shortTitle` 之用語一致** |
| **落點** | `Sources/vChewingIME_macOS/Resources/{zh-Hant,zh-Hans,ja,en}.lproj/Localizable.strings`（各 1 條鍵）、助手 `assets/userdef-metadata.json`（重生）、`tests/metadata.test.js`（**新增醒目性護欄**） |
| **判準** | 四語系之該條 `description` **首碼位即 U+26A0 U+FE0E**、其後一個半形空格、其後為換行；其餘 618 條鍵不動；舊稱謂仍為 0 |
| **為何要護欄** | **位置即本裁定之內容**——只驗「警示在不在」守不住它。故斷言取 `indexOf('\u26a0\ufe0e') === 0` 並另驗含換行（`.strings` 之 `\n` 轉義在導出之 JSON 內為**真換行**，實查） |
| **風險** | 極低。唯一之系統性風險是「日後有人把警示挪回句中」⇒ 已由新靶固化 |
| **完成定義** | ① 四語系置首；② 護欄入靶且變異測試轉紅；③ 後設資料重生且 `audit` 全綠；④ `SettingsUI` 不受影響 |
> **完工狀態（v24）**：助手 `make test` **82 支／全過**（81 → 82：＋醒目性護欄）、`make audit` **exit 0**（surface 108 鍵無漂移、五份 fixture 全 same）、`SettingsUI` **19 支／4 套／0 失敗**；後設資料 `count` 119、四語系之首行即事主之句與其對位譯文；**變異測試**：警示移至句末 ⇒ 新靶轉紅（訊息附首 20 字）。**I2 空操作**。**已知界線四項**見 `Reqs_0251-0260.md` 之 Phase 259 篇 §四。**未驗**：真機（設定介面之實際行距與字形）。

---

## 九、自動裁定記錄（事主已授權「先自動落實最優解」）

> 事主原文：「你在規劃完畢之後如有需要我親自裁示的事情的話，你可以先自動落實你的最優解。我信任你對唯音輸入法這個產品的全局理解能力。」

| # | 事項 | 本文之裁定 | 若事主不同意之替代 |
|---|---|---|---|
| 1 | 注音側之簡稱 | **「狂注」**（ja「狂注」） | 改「狂打注音」一類；惟 `shortTitle` 會與總稱撞名 |
| 2 | ja 之「狂打ち」字形 | 漢字＋送假名（`狂打ち`） | 全漢字「狂打」 |
| 3 | en 之 `TypingMode` 提示值 | `Furious Pinyin Typing`（原為 `Furious Typing`，因總稱讓位） | 保留 `Furious Typing` |
| 4 | ~~注音狂打是否開 copilot 未完成讀音窗~~ | **【已作廢——事主 2026-09-26 之異議】** 初稿裁定「不開」係基於「注音不需要猜測」之判斷，而該判斷漏掉了**單聲母縮寫打法**（§3.0）。**現行裁定：要開**；`hasFuriousFrontPending` 對注音 ＝ `!composer.isEmpty`（§3.5） | —（已改版，無替代案） |
| 5 | 動態鍵盤可敲鍵集 | **本輪不做**；日後若做，以模擬派生且置於 `LibVanguard`（§5.4） | 逕行實作於 Tekkon 內 |
| 5b | `SyllableIndex` 是否收錄 37 個單符號讀音 | **不收**。其語意為「多數派漢語音節」（427 ＋ 15 嚴格前綴 ＝ 442）；單符號之合法性是**辭典之事實**、由 `assembler` 之查詢鏈回答（§4.2 之兩條施工紅線） | 併入 `allReadings` 成 479 條；惟此舉會使「427」失去可稽核性、且令條件 ④ 之外推失真 |
| 5c | 單聲母狂打之提交是否需先問辭典 | **不問**。§3.2 之判準純由結構 ＋ `SyllableIndex` 決定；提交後若辭典無詞條，`composeReadingIfReady` 之既有錯誤路徑自會處置（`B49C0979`） | 提交前先 `hasGrams` 探測；惟該查詢在熱路徑上，且會使「注音不收簡拼」之界線模糊 |
| 6 | 舊配置包之相容 | **不**加別名，採甲案（§6.4）；改為加強 `Unknown key` 之訊息 | 於匯入端加一次性鍵重寫 |
| 7 | 兩顆開關之排版 | 同一 Section 之兩列、不做連動停用（§8.6） | 各一 Section |
| 7b | 注音文抑制之旗標落點 | **v5 定案：續留 `LexiconAssembly` 側**（`LXFacade.syncPrefs()` 內之一行析取式）。原「傾向移到 Handler 側」之議由 P251 未知四否決（熱鍵改的正是 `pinyinTypingEnabled`，且 `syncPrefs()` 每拍皆跑） | 若實測發現脫鉤，改以 `typingMode` 單一真源、並在 Handler 側推入（§8.8） |
| 8 | 遷移失敗之處置 | **不**回滾、**不**補償；舊鍵處理完即刪 | — |
| 9 | 新 `UserDef` case 之插入位置 | `:62` 原位改兩行（`4Pinyin` 先、`4Zhuyin` 後） | 併入 `KeyboardParser4*` 一族 |
| **10** | **v5：§3.2 之判準改版** | **採 v7（六條）**：三條件 ＋ ④a 冗餘鍵 ＋ ④b′ 真實延伸 ＋ ④d 自毀己產守衛 ＋ ④c 接續探針；`S_new` 取自空槽試跑 | 若 v7 之 2.19% 殘餘漏切於實機不可接受，再議「延遲一拍決定」或引入鍵序重播（皆為架構級改動，須另立 phase） |
| **11** | **v5：`incomingPhoneType(forKey:)` 之去留** | **不列入 P252**（可由既有 `public` API 達成；新增 API 反而模糊 §3.3 之邊界） | P252 若仍決定新增，須於該 phase 記錄內明寫出入與理由 |
| **12** | **v5：`completions(of:)` 之去留** | **暫緩公開、保留為 `internal`**（v7 無生產端消費者） | 日後出現消費者（如動態鍵盤提示）時升為 `public` |
| **13** | **v5：P251 之靶之後續** | P255 落地後，**P251 之 5 支靶轉為對生產實作之回歸靶**（其四項地面真相不變） | 若生產實作改採別形，則以生產實作取代其參考實作、並保留地面真相斷言 |
| **14** | **v6：`SyllableIndex.shared` 之標籤** | **`shared(parser:)`**（不採 §4.3 原文之 `shared(for:)`） | 若事主偏好 `shared(for:)`，改一行即可；語意不變 |
| **15** | **v6：`completions(of:)` 之可見性** | **`internal`**（暫緩公開） | 日後出現消費者時升為 `public` |
| **16** | **v6（v7 更正、v8 結案）：`mapHanyuPinyin` 之單字母條目** | **已裁定刪去 `q`**（自 `mapHanyuPinyin` 與 `LexiconAssembly` 內嵌 JSON 兩處同步），單字母條目僅餘 `a`／`e`／`o` 三條真音節。三則測試已改為釘住刪除後之契約 | 若事主裁定「應補齊」：為其餘 20 個聲母各加單字母條目——**後果嚴重**（每一個「聲母鍵＋任意鍵」之組合都會在狂拼下提前切音節），故**不建議**。**（已執行，見下行）** 若日後欲回復：兩表須同進退。 |
| **17** | **v8：`"q": "ㄑ"` 之處置** | **刪去**（事主 2026-09-26 裁定）。兩表同步；下游四處已複查；連帶更正 427→426、15→16、24→23、13→14 四項數字 | 若日後要回復：`Tekkon.mapHanyuPinyin` 與 `LexiconAssembly` 內嵌 JSON 兩處同加，並還原三則測試 |
| **18** | **v9：`SettingsUI` 兩處渲染點之歸屬** | **納入 P253**（改指 `…4Pinyin`）；注音側之第二列仍留 P259 | 若事主希望在 P253 就同時露出兩列，則須把 P259 之 UI 工作前移（連同 `…4Zhuyin` 之兩條 i18n 鍵） |
| **19** | **v9：`…4Pinyin` 之兩條 i18n 鍵更名之歸屬** | **納入 P253**（與 `metaData` 同輪，避免現役渲染點露出未翻譯鍵） | 若事主接受 P253–P259 之間之暫時回歸，可改回 P259 一次做完 |
| **20** | **v10：`isPinyinFamilyTypingMode` 之處置** | **收緊為 `isComposerUsingPinyin`**（等價變換；「保持原樣」會引爆陷阱） | 若事主認為應保留析取之形式以存其文檔價值，可改寫為 `isComposerUsingPinyin \|\| isPinyinFuriousTypingModeEffective`（語意相同、右項多餘） |
| **21** | **v11：判準之落點** | **`Tekkon.Composer` 之擴充**（非 `InputHandlerProtocol` 之成員） | 若事主偏好協議成員之形式，可加一層薄轉發；語意相同 |
| **22** | **v11：辭典閘** | **加上**（`hasGrams`）；不設則嚴格前綴會觸發插入失敗 | 若事主希望「凡判準判切即切」，須另設計嚴格前綴之落庫方式 |
| **23** | **v12：注音側「未完成讀音」之判準** | **`composer.isPronounceable` 且組字結果非空**（非 §3.5 初稿之 `!composer.isEmpty`）——純聲調槽非空卻無讀音可示，該式會開啟空窗並生成垃圾讀音桶 | 若事主希望「敲了聲調即算未完成讀音」，則須另行定義該狀態下之桶與 pane 內容（本系列不採） |
| **24** | **v12：注音側 copilot 窗之候選來源** | **於 `furiousFrontContext` 內依鍵盤家族分流讀音桶**（注音側之未完成音節即讀音），下游候選建構全段共用 | 另一種作法是在 `InputHandler_CoreProtocol` 另闢注音專用之候選建構——代價是同一套排序／去重／跨邊界邏輯出現第二份 |
| **25** | **v12：`unfinishedReading` 之判讀歸屬** | **上移至 `InputHandlerProtocol.furiousFrontUnfinishedReading`**，session 與 mock 皆只轉發 | 若事主偏好「session 端自行判讀」，則 mock 須逐字對抄（§8.7 風險欄所描述之分岔風險隨之復活） |
| **26** | **v12：`confirmFuriousFrontCandidate` 之注拼槽處理** | **整體快照／還原**（`let composerBackup = composer`）；拼音側等價且更忠實 | 若事主希望保留 `replacePinyinBuffer` 之逐欄重建路徑，則注音側須另寫一份清槽與還原 |
| **27** | **v13：注音文抑制之判準所用之「當前打字方式」**（**v14 已由事主裁定結案**） | **`prefs.pinyinTypingEnabled`**（而非 `typingMode`／`composer.isPinyinMode`）——熱鍵之兩句實作使其成為真源、注拼槽之家族係由其導出 | 若事主希望改以「有效模式」為準（磁帶／SCPC 下不抑制），則須改由 Handler 推入並重驗拼音側之既有語義（§十一 #16） **惟事主 2026-09-26 裁定「磁帶與 SCPC 先不要啟用狂打特性」⇒ 模式維度已就地補齊（v14）；本式自此為三維合取** |
| **28** | **v13：`LexiconAssemblyTests` 對 `Shared` 之依賴** | **補為直接依賴**（`Package.swift` 一處）——本 phase 之驗收必須經偏好，而該靶從未 `import Shared` | 若事主不希望動 manifest，則該靶須遷入 `LibVanguardTests`（但會使「同一主題之靶分居兩處」） |
| **29** | **v13：「下一拍」之靶之歸屬** | **兩支**：`LexiconAssemblyTests` 之 `syncPrefs()` 版（機制）＋ `LibVanguardTests` 之 IH705（真實分診） | 若事主認為重複，可只留 IH705——代價是失去「偏好寫入與分診之間旗標不動」這一條釘子 |
| **30** | **v14：拼音自動切音節是否應一律以狂打開關為閘** | **暫不動**：非 SCPC 且 `furiousTypingEnabled4Pinyin = false` 時仍照跑——此為既有行為，且由 `test_IH116B_FuriousTypingDisabledKeepsRawPinyinDisplay`（標題即「狂打關閉時既有行為不受影響」）釘住 | 若事主欲使「關閉狂拼即無自動切音節」，須改該靶之斷言（行為變更，見 §十一 #17） |
| **31** | **v15：`description` 草案與實況不符之處理** | **改寫為實況**（注音文會被過濾、未完成讀音由 copilot 窗預覽、並補空格／Enter 語義）——草案寫在行為落地之前，行為既已由 P255–P257 定案，文案不得留舊 | 若事主希望保留草案之原句，則須回頭撤銷 P256／P257 之行為（不建議） |
| **32** | **v15：en 之拼音行內提示是否一併更名** | **不改**（維持 "Furious Typing"）——§8.10.1 之 i18n 清單只列新增 3 條，改既有之使用者可見字串屬計畫外 | 若事主欲使二者對稱，改為 "Furious Pinyin Typing" 即一行 ×1 語系 |
| **33** | **v15：助手漂移之清償範圍** | **三項全清**（metadata／surface／fixtures）——三者皆為 P253 更名所遺留，且三道防漂移檢查皆會因此轉紅 | 若事主希望分批，可只清 metadata（但 `surface-check` 仍會紅） |
| **34** | **v16：`make build510` 於本 harness 之失敗之登錄方式** | **登錄為環境事項**（沙箱擋 `sandbox-exec`），並以「事主未加 `--disable-sandbox` 而 legacy 兩目標皆過」為反證；**不**在 `makefile` 內加該旗標 | 若事主欲使 `makefile` 內建該旗標，則須同步兩倉之 `makefile`（受 I2 覆蓋）——惟該旗標本是呼叫端紀律，內建會放寬 CI 之沙箱約束 |
| **35** | **v16：真機驗收項 #11（`SyllableIndex` 首拍延遲）之收束** | **降級為「實機觀察」**——該索引係對靜態表之純計算、惰性建構、只在狂打路徑觸發；測試端冷啟 0.014 秒即其量級 | 若事主要求實測，須於 IME 行程內加暫存計時（屬生產碼改動，另立 phase） |
| **36** | **v18：注音簡拼之套用路徑** | **先 `dropKey` 移除尾段單注音鍵、再把該詞之讀音整段插入**（鍵鏈因而恰為該詞之讀音、`overrideCandidate` 方得成立；§8.9.1.6） | 另一路是讓 `overrideCandidate` 接受「前綴對齊之 keyArray」——須動 `Homa` 之守衛，超出本案範圍且放寬了其他呼叫端之語義 |
| **37** | **v18：單注音之輸入能力是否移除** | **維持不移除**（事主 2026-09-26 裁定：「**去掉這個方案**。原因：單獨注音一事：歸因不成立」）——單注音照舊自動切出，簡拼只是額外提供整詞候選 | 若日後真要移除，須另立 phase 並處理「組字區不再顯示所敲注音」與 undo／游標語義 |
| **38** | **v19：讀音原字串回退值之優先權** | **降級**（不置頂、權重取地板值）——仍保留於清單內可供顯式選取 | 若事主欲完全不顯示該類候選，改為過濾即可（一行；見 §十一 #20） |
| **39** | **v20：文案隨行為漂移之處理** | **同一 phase 內回檢**（本 phase 即 P258 改空格語義後之補課）；本次逐條審計後僅改注音側 `description` 一條 × 四語系 | 若事主欲更嚴格，可於 §10.1 增設「文案靶」——惟 i18n 之語義對帳難以自動化，暫以人工逐條審計為之 |
| **40** | **v21：狂打開關之「指名」與「回歸」** | **指名**（值等於出廠預設亦指名）——理由為「主動覆蓋使用者機器上之現值」；此為策展紀律①之經核定例外 | 若事主日後認為「值同預設即不必指名」，則撤去該兩案即可（代價：匯入配置不再糾正已開啟之狂注） |
| **41** | **v22：來源級否決之機制** | **新增 `ORIGIN_VETOED_KEYS`**（優先於打字方式級之一般規則；值一律 `false`）——「來源 × 任何打字方式」之合取條件於既有兩表無從表達 | 若事主偏好改以「逐 profile 之列舉表」表達，則該表須列 11 來源 × 6 打字方式（66 格）——可讀性遠劣於否決表 |
| **42** | **v23：中英混合輸入回退與注音狂打之優先權** | **回退勝**：回退一經啟用，注音狂打即一律被視為關閉（否決置於 `typingMode` 之注音臂）；**拼音側不設同一否決**（回退本即注音鍵盤專屬） | 另一路是「**逐段共存**」——同一串按鍵內，讓回退只在純 ASCII 段落生效、注音段落仍狂打。此須在打字機層重構（同一組字週期內換手），屬架構級改動、且與回退「整段判定後才回退」之既有語義衝突 ⇒ 本 phase 不採（見 §十一 #24） |
| **43** | **v24：警示文案之位置與稱謂** | **置於該條 `description` 之首行**（事主：「插在其他位置的話不醒目」）⇒ 並移除 P258 加在句中者，使警告在該條字串內**只有一處、且在最前**。**稱謂**：初以事主原句之「中英文輸入回退模式」，事主隨即更正（「我剛才寫錯」）⇒ 四語系一律改用該偏好 `shortTitle` 之正式稱謂（zh-Hant／zh-Hans：「中英混合輸入回退」；ja／en 原即對位） | 若欲連拼音側亦加同型警示，則須另立理由（拼音側不受回退影響） |

## 十、驗證要求

### 10.1 Swift 側單元測試

| 層 | 測什麼 | 落在 |
|---|---|---|
| Tekkon | **P251 已交付**：判準之四版對照 ＋ 29,579 步單音節 ＋ 276,446 例交界 ＋ `qquu` 逐拍 ＋ `ㄍㄋㄋ`／`ㄋㄋ` 之逐鍵（5 支，48 支／8 套）。**P252 續加**：`SyllableIndex` 之 `isComplete`／`isPrefix` ＋ 442 條之集合斷言 ＋ 15 條嚴格前綴全表 ＋ 422 條無調詞幹之成員斷言。**P255 後**：P251 之靶整組搬入 `LibVanguardTests` 改打生產實作，`TekkonTests` 回歸 53 支／8 套 | **P251（已完成）**／P252（已完成）／P255（已完成） |
| Shared | `migrateDeprecatedSettings()` 之六項（含冪等） | **P253（已完成）** |
| LibVanguard | 既有 67 支狂拼回歸 ＋ 新 IH155–IH164（**P255 交付 7 支**）。**P256 續加**：未完成讀音之分流（IH160）＋ copilot 窗與就地選字（IH161）＋ 六個讀取點之注音語義（IH162）＋ 拼音側回歸護欄（IH165）。**P258 續加**：IH162 之空格臂改寫、IH166（簡拼 cells 與界線）、IH167（簡拼候選與窗內排序）、IH168（中英混合輸入回退對注音狂打之否決：旗標層 ＋ 行為層） | **P255（已完成）**／**P256（已完成）**／**P258（已完成）** |
| LexiconAssembly | 注音文抑制：**兩種狂打皆抑制、兩種非狂打皆不抑制**（四態）＋ 熱鍵切換後之下一拍即時反映。**P257 已交付**：四態擴為 8 組全枚舉（旗標＋查詢兩層）＋ 熱鍵靶 ＋（`LibVanguardTests` 側）整合靶 IH705。**P258 續加**：真值表維度 5 → 6（＋中英混合輸入回退，**32 → 64 組**） | **P257（已完成）**／**P258（已完成）** |
| SettingsUI | 助手 4 支契約測試 ＋ 既有 `PrefsExchange` 群 | **P259（已完成）** |

### 10.2 助手側（TypeScript）

`make audit` ＝ `typecheck` ＋ `es5` ＋ `test`（**82 支**；其沿革全在 P259 之內——P258 及以前為 78 支，P259 歷 79 → 81 → 82）＋ `metadata` ＋ `metadata-audit` ＋ `surface-check` ＋ `version-check` ＋ `fixtures-check`。**本系列會動到其中五道**（鍵集變動 ⇒ `metadata`／`metadata-audit`／`surface-check`／`fixtures-check` 之輸入變動；`count` 斷言變動）。**重生順序須照 `Makefile` 之依賴：`metadata-update` → `surface` → `fixtures`。**

### 10.3 兩倉 byte-sync（每一 phase 之硬性驗收）

```bash
A=vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard
B=vChewing-LibVanguard
diff -rq -x '.build' -x 'Build' -x '.DS_Store' -x '.git' "$A/Sources" "$B/Sources"
diff -rq -x '.build' -x 'Build' -x '.DS_Store' -x '.git' "$A/Tests"   "$B/Tests"
diff -rq -x Build -x '.DS_Store' -x '.build' "$A/Deps" "$B/Deps"
for f in Package.swift Package@swift-5.10.swift Package@swift-6.0.swift \
         Package@swift-6.1.swift Package@swift-6.2.swift Package@swift-6.3.swift makefile; do
  cmp "$A/$f" "$B/$f"
done
```

**動工前基線（本 phase 實測，2026-09-26）**：`Sources/` 各 **125** 檔、`Tests/` 各 **76** 檔，`diff -rq` 與 `shasum -a 256` **零差異**；`Deps/` 各 12 檔零差異；七份固定檔之 SHA-256 兩兩相同。**唯一之差異是 `.DS_Store` 之類未追蹤噪聲。**

### 10.4 實機實測項（須事主）

| 項 | 為何須人眼 |
|---|---|
| **完整讀音之兩例**：`ㄍㄢˋ-ㄋㄧˇ-ㄋㄧㄤˊ` → 應見「幹你娘」（逐字組句）；`ㄍㄡˇ-ㄋㄢˊ-ㄋㄩˇ` → 應見「狗男女」（整鍵詞條）——★ 本案之首選實測項 | 需真人連續輸入；且須**與注音文抑制一併驗**（v3） |
| **縮寫打法**（`ㄍㄋㄋ`、`ㄋㄋ`、`ㄓㄓ`、`ㄔㄔ`…）之實際手感 | 需真人連續輸入。**注意**：v3 起注音文已被抑制，故縮寫打法之候選將**不再**含 `ㄍ`／`ㄋ` 一類回聲字串——**須確認剩下的候選仍有用**（此即 v3 方針之成敗所在） |
| 注音狂打之一般手感（自動切音節是否符合直覺、有無誤切） | 需真人連續輸入 |
| 注音狂打於**動態排列**（ETen26／Hsu／Starlight／AlvinLiu／Dachen26）下之表現 | 五種排列各有獨門特例 |
| 兩顆開關於設定介面之排版與文案 | 目視 |
| **預設值之實際效果**：既有使用者升級後，拼音狂拼行為應完全如舊；注音側應為關閉 | 需真機驗 |
| **（P258 新增）回退啟用時之讓路**：開啟「中英混合輸入回退」後，注音狂打須確實被視為關閉（無自動切音節、無 copilot 窗），**且回退本身如常工作**（ASCII 序列遞交原文） | 需真機驗：本 phase 只在靶內驗了狀態機與遞交語義，實機之按鍵路徑（含 IME 行程與輸入客體）須人眼 |

### 10.5 風險與緩解（總表）

| # | 風險 | 等級 | 緩解 |
|---|---|---|---|
| 1 | `isFuriousTypingModeEffective` 之 12 個讀取點收束不完全，導致注音打字路徑被誤判為拼音系 ⇒ 鍵盤佈局翻譯被跳過 ⇒ 注音打不出字 | **高** | P255 分兩半施工（先閘門、後行為）；`isPinyinFamilyTypingMode` 列為紅線；IH156／IH157 為關鍵回歸 |
| 2 | 自動切音節於動態排列之覆寫語意下誤切 | **已證實並已解** | v4 之 §3.2 原文確實誤切（P251 實測：`qquu` 被切、`ㄍㄋㄋ` 全滅）；v5 之 v7 判準含 ④d 自毀己產守衛（`SyllableIndex.isPrefix` 之否定）＋ IH157 |
| 2b | **單聲母狂打打不出來**（初稿之實際缺陷，事主已指出） | **高（已於本案解除）** | §3.2 條件 ④ 之 `isPrefix` 判準使 `ㄍ`／`ㄋ` 得被提交；`IH155` 為其固化物。**施工者不得以「當前內容須為完整音節」為提交前提** |
| 2c | 注音狂打接入 copilot 窗後，`unfinishedReading` 分流未同步 mock ⇒ 測試與生產行為分岔 | 中 | §3.5 之表已列明須同步 `MockSession.unfinishedReading`；`IH160` 之斷言須在**真** `InputSession` 與 **mock** 兩處皆成立 |
| 3 | 遷移碼不冪等 ⇒ 每次 `activateServer()` 都改寫偏好 | 中 | 以 `object(forKey:) != nil` 為閘 ＋ 處理完即 `removeObject` ＋ 連跑兩次之測試 |
| 4 | 141 處測試之機械式更名漏改或誤改 | 中 | 單一取代樣式 ＋ `git diff --stat` 覆核 ＋ 兩倉各跑滿測試 |
| 5 | 助手之防漂移四道未同步重生 | 中 | 照 `Makefile` 依賴鏈重生；`make audit` 全綠為 P257 之完成定義 |
| 6 | 兩倉 byte-sync 於 `make lintFormatUncommitted` 之後失守 | 中 | §8.0 紀律 1／2；每一 phase 附實際輸出 |
| 7 | 427 vs 422 之落差被誤當 bug 而擴大範圍 | **已消滅** | **P251 已釘死**：422 全部 ⊆ 427、差集為 5 條指名之讀音（§4.2） |
| 8 | 舊配置包之 `Unknown key` 失敗 | 低 | §6.4 之已知代價 ＋ §九 #6 之裁定 |

---

## 十一、未決事項（留待事主或後續 phase）

| # | 事項 | 何時需要定案 |
|---|---|---|
| 1 | 舊配置包是否採「匯入端一次性鍵重寫」（§6.4 之替代案） | **收束（v16）**：P253–P259 皆未採該替代案——交換格式仍以 `rawValue` 為鍵、未知鍵仍被拒；含舊鍵名之配置包會匯入失敗。**現行處置**：P259 已令助手之題庫與產物跟上現行鍵名，故新產出之配置包不再含舊鍵；舊包之使用者須自行重匯或手改 |
| 2 | ~~注音狂打是否要開 copilot 未完成讀音窗~~ | **已定案：要開**（事主 2026-09-26 異議；§3.0、§3.5）。此項自未決清單移除 |
| 3 | 「動態鍵盤之可敲鍵集」是否有真實消費者（§5.4） | 無時程。**若 iOS 版之螢幕鍵盤要做「動態注音鍵盤高亮／限制」，此即其前置** |
| 4 | ~~`kUsingHotKeyPinyinZhuyinTypingSwitch` 熱鍵切換時，兩顆狂打開關之互動是否需進一步細化~~ | **已定案（P251 未知四）**：熱鍵改 `pinyinTypingEnabled` 而不改兩 parser 槽 ⇒ 析取式自動跟上、無互動問題（§7.4、§8.8）。**惟 P257 仍須新增一則熱鍵測試以釘住之。** |
| 5 | ~~`mapHanyuPinyin` 之四條單字母條目之性質~~ | **已結案（v8）**：`"q"` 已刪、`a`／`e`／`o` 保留。三則測試即為其契約 |
| 6 | `Tekkon.SyllableIndex` 之建構成本於**輸入法行程首拍**之實際延遲 | **收束（v16）**：降級為「實機觀察是否落在可感知之臨界」——該建構係對靜態表之純計算（`Set(mapHanyuPinyin.values)` 之排序結果）、無 I/O、無 client 狀態，且惰性建構、只在狂打路徑上觸發；測試端冷啟 **0.014 秒**即其量級（§九 #35） |
| 7 | ~~`…4Zhuyin` 之出廠文案（zh-Hant／zh-Hans／ja／en 四語系）之定稿~~ | **已結案（v15，P259）**：四語系各 ＋3 條已落地（619 鍵 ×4 逐項相同）；定稿與 §7.5 草案之三項出入見 §8.10.1 之完工狀態。規劃書 §7.5 之草案為 zh-Hant 之底稿；關鍵一句「只敲聲母亦可（如 `ㄍㄋㄋ`、`ㄋㄋ`）」須待 P255 之行為落地後方能寫準 |
| 8 | 於 P255 落地前手動開啟注音狂打所得之中間態是否有害 | 無時程。**P255／P256 已先後落地** ⇒ 該中間態（有自動切音節、有 copilot 窗）已成為本系列所支援之組合；P254 §五 所列之「不受支援」僅指 P254 當時之狀態 |
| 9 | **單聲母縮寫之端到端**（判準 ＋ 辭典閘 ＋ 組字器） | **實機（P259 已收攏為清單 §六 #1，含新前提：可於偏好面板開啟）**。判準層已驗（`ess` → 三顆鍵）；端到端需辭典內有 `ㄍ`／`ㄋ` 等單符號鍵，測試辭典無、原廠辭典有 |
| 10 | ~~IH162（注音狂打之空格／Tab／Enter／標點語義）~~ | **已補做（P256）**。`Tests/LibVanguardTests/InputHandlerTests_FuriousCopilotWindow.swift` 之 IH162；並查得大千排列之 `,` 是注音符號鍵（ㄝ）、標點讀取點須以非注音鍵驅動 |
| 11 | iOS 移植之整體規劃（本案僅為其前置之一） | 另立 phase |
| 12 | **是否於 `vChewing-VanguardLexicon` 之 8 行注音文正本內補一條 `幹你娘` ↔ `ㄍ-ㄋ-ㄋ` 之對照** | 無時程。**該倉係另一倉、本系列不動之**；惟此為「讓事主之例如願顯示漢字」之最直接手段（§3.0.1）。若採，須同步重生辭典產物並於該倉另立 phase |
| 13 | 單聲母狂打之提交是否應加「辭典無詞條則不提交」之保護（§九 #5c 之替代案） | P255 實測後——若觀察到單聲母提交後常態落進 `B49C0979` 之錯誤路徑，則須回頭補此保護 |
| 14 | **注音側 copilot 窗於真機之可見性與版面**（含：其「前方預覽」與組字區讀音欄是否顯示重複、`unfinishedReading` 於頂部 pane 之呈現） | **實機（P259 已收攏為清單 §六 #4）**。本 phase 只在測試靶內驗了狀態機語義；版面須真機判 |
| 15 | ~~「純打字方式切換（熱鍵）是否改變 `prefs.pinyinTypingEnabled`」~~（§7.4） | **已結案（P251 未知四）**：熱鍵改的正是 `pinyinTypingEnabled`、且 `syncPrefs()` 於每次分診頂端執行 ⇒ 抑制旗標可續留 `LexiconAssembly` 側（§8.8） |
| 16 | ~~注音文抑制是否應改以「有效模式」為準（磁帶／逐字選字下不抑制）~~ | **已結案（v14）**：事主 2026-09-26 裁定「磁帶與 SCPC 先不要啟用狂打特性」⇒ 模式閘已補（§九 #27）。本 phase 之式以**偏好**為準（承舊式之語義，且 `4Pinyin` 出廠為 `true` ⇒「拼音宣告 ＋ 磁帶」今日已在抑制之列）。改以「有效模式」為準即須由 Handler 以 `typingMode` 推入，並重驗拼音側之既有行為——**此為行為變更，須事主裁定**（§九 #27） |
| 17 | **拼音之自動切音節是否應一律以狂打開關為閘**（現行：非 SCPC 且狂拼關閉時仍自動切音節） | 無時程。**此為既有行為且已被 `test_IH116B` 釘住**；事主之裁定點名磁帶與 SCPC，未及於此 ⇒ 暫維持現狀（§九 #30） |
| 18 | ~~注音簡拼之尾段掃描界線（幾個 cell？有界截斷之值）~~ | **已定案（v18，P258）**：總格數上限 **4**（＝尾段單注音鍵至多 3 ＋ 注拼槽之當前讀音 1）；超出即不再向前收集（遇完整音節亦停）。界線值常數為 `maxZhuyinAbbreviationCells` |
| 19 | ~~注音簡拼候選與既有前方候選之同窗排序~~ | **已定案（v18，P258）**：沿用 `buildFuriousFrontCandidates` 之「詞長降冪 → 分數降冪 → 按 value 去重」；其**實機排序觀感**已併入 P259 之真機驗收清單 |
| 20 | **`rawReadingFallbackWeight` 之回退值是否改為完全不顯示** | **P258 已定案為「降級」**（事主之原話為「降低優先權」）；若實機上仍嫌其佔位，改為過濾即可（§九 #38） |
| 21 | ~~`cin`／`newbie` 等非注音亦非拼音之來源，其狂打開關是否亦須指名~~ | **已結案（v22，P259）**：**CIN 無須調整**（維持不指名——其值仍為出廠預設）；**newbie 現階段刻意停用**狂打特性 ⇒ 以新增之 `ORIGIN_VETOED_KEYS` 於**任何**打字方式下否決兩鍵（指名 `false`） |
| 22 | ~~`goingime`（自然輸入法）之歸派~~ | **已結案（v22，P259）**：事主指出 GoingIME 即**自然輸入法**（**不是**自然碼輸入法——後者為字根輸入法），主推**許氏**注音鍵盤佈局 ⇒ **歸注音系為正解**（其 zhuyin 鍵指名 `false`、不涉拼音側），**無須改動**。**P259 記錄中「該輸入法實務上兼有注音與拼音兩派」之記述為誤**，已於 P259 更正 |
| 23 | **模式判定之兩處同步義務是否收束為一處**（`InputHandler_TypingMode.typingMode` 與 `LexiconAssembly/LXFacade.syncPrefs()` 之就地複製品） | 無時程。P258 已於兩處之註解互指，並以 64 組真值表 ＋ IH168 雙向守住；**收束為一處**須由 Handler 以 `typingMode` 推入 config（§九 #27 之替代案），而該案於 P257 已因「熱鍵脫鉤」之疑慮被否決——今再評估時，該疑慮已被 P251 未知四否定，故障礙僅餘「模組邊界之新依賴」。**若日後再有維度加入，此項之優先權即應提高** |
| 24 | **「逐段共存」語義是否要做**（回退只在純 ASCII 段落生效、注音段落仍狂打） | 無時程、且**不建議**：同一串按鍵需在同一次組字內換手（打字機層重構），且與回退「先吸收、整段不成立才回退」之語義衝突。事主若於實機上仍覺兩者本應並存，再議（§九 #42 之替代案） |

## 附錄 A：本 phase（250）之實作結果

### A.1 落地

**改 4 檔**（皆為文書，**零生產碼**）：

| 檔 | 改動 |
|---|---|
| `vChewing-DevLogs/Research/Phase250-ResearchAndNextSurgeryPlan.md` | **新檔**（本文） |
| `vChewing-DevLogs/Reqs4LLM/Archive_P201-P300/Reqs_0241-0250.md` | 新增 `# Phase 250` 記錄（本文之摘要與其落點索引） |
| `vChewing-DevLogs/DevReqsHistory.md` | 追加 Phase 250 一列 |
| `vChewing-DevLogs/KnowledgeMemo4LLM.md` | `最後更新` 改 2026-09-26；文首新增「狂打模式之注音化：規劃已定案」一則，摘記五則後續施工必須遵守之事實 |

**同 phase 內之修訂（v2）**：上表四檔於同日經一次改版（事主對 copilot 窗之異議，見文首〈修訂沿革〉）。**未新增任何檔案、未新增任何生產碼**——改版完全落在同一批文書內。**唯一新增之生產碼路徑為規劃性質**（`unfinishedReading` 之分流），其實作仍屬 Phase 255。

**未動**：`vChewing-macOS` 之任何檔案、`vChewing-LibVanguard` 之任何檔案、助手之任何資產、任何 CI、任何 `Package*.swift`。

### A.2 研究方法

四路並行之唯讀盤點，各自以「`path:line` 為證、凡未實查者標 `unverified`」為紀律：

| 路 | 範圍 | 主要產出 |
|---|---|---|
| A | `UserDef`／`PrefMgr`／`PrefMgrProtocol` 之全表面 ＋ 全倉引用點 ＋ i18n ＋ SettingsUI ＋ 會壞之測試 | §六、§1.3 |
| B | 狂拼執行期管線（triage／auto-chop／segmentor／重切分／候選／顯示）＋ 27 條 romaji 專屬 vs 21 條音素中立之對照表 ＋ 66 支狂打相關測試 | §二、§3.4 |
| C | Tekkon 全模組（公開表面、音素模型、動態排列、`PinyinTrie`、43 支測試、熱路徑、快取）＋ 測試資料之量化 | §四、§五 |
| D | 兩倉 byte-sync 之範圍與現況、權威條文、歷史成例、遷移前例、CI 事實 | §8.0、§10.3 |

**方法學要點**：C 路與本文另以 Python 直接解析 `Tekkon_Constants.swift` 之 `mapHanyuPinyin` 字面與 `Tekkon_TestData.swift` 之測試表，獨立算出 §4.2 與 §5.1 之全部數字（427／442／15／3,069 bytes／1485／439／7366／5888／6072／各排列之 Trie 節點數）。**故 §五之結論建立在可複算之量化上，非印象。**

### A.3 本 phase 之關鍵查得（施工者勿重複踩）

1. **`InputHandler_HandleComposition.swift:27–37` 已把注音與拼音派給同一個 `BPMFFullMatchTypewriter`** ⇒ 注音狂打**不需要**新 typewriter。此為本案工作量估計之樞紐。
2. **`InputHandler_CoreProtocol.swift:611–617` 之 `inlineReadingPreview` 本即為注音準備了正確路徑**（`:613` 之 `guard !prefs.cassetteEnabled, !composer.isPinyinMode`）⇒ 注音狂打之讀音顯示**泰半免費**。
3. **`InputHandler_CoreProtocol.swift:215` 之 `isPinyinFamilyTypingMode` 恆等於 `isComposerUsingPinyin`**（其註解 `:209–213` 已自陳此點，並說明該命名是為了「避免鍵盤佈局翻譯等外部條件依賴『狂拼是否拼音』的隱式假設」）。**此事實使 P255 之風險具體化**：一旦 `isFuriousTypingModeEffective` 對注音為真，若施工者順手把 `:215` 改成它，注音之鍵盤佈局翻譯即被跳過。**此為本案點名之最大陷阱。**
4. **`FuriousTypingSegmentor` 之兩個生產建構點**（`InputHandler_FuriousResegmentation.swift:379–389`、`:452–462`）之注入閉包**逐字相同** ⇒ 若日後真要為注音做重切分（本案不做），那兩處即為落點。
5. **`migrateDeprecatedSettings()` 用 `UserDefaults.standard` 而 `@AppProperty` 用 `UserDefaults.current`**（僅測試時二者才分岔）⇒ 遷移碼之測試**必須**走 `.standard`，否則測不到。
6. **★ 生產辭典內，21 個聲母與 16 個單韻母／介母全部都是合法讀音鍵**（各一條「以自身為值」之詞條，權重 `-8.863`，如 `ㄍ → ㄍ`），另有 **85** 條「各段皆為單一注音符號」之多音節鍵（如 `ㄍ-ㄋ-ㄋ → ㄍ`、`ㄋ-ㄋ → ㄋㄟㄋㄟ`）——**其值皆為「回聲字串」**。上游正本 `vChewing-VanguardLexicon/…/data-zhuyinwen.txt` **全檔 8 行**（權重一律 `-9.6`；型別 `EntryType.zhuyinwen` ＝ §7.4 抑制旗標所過濾者）：`ㄅㄧㄤ`／`ㄅㄧㄤˋ`／`ㄉㄨㄤ`／`ㄋㄟ`／`ㄋㄟㄋㄟ`×2／`ㄎㄧㄤ`／`ㄍㄋㄋ`。**此為 P255「縮寫打法」之技術根據。**
7. **★ 事主所舉之兩個候選各有其真源、且互不相同**（v3 複查）：**「狗男女」**來自**完整讀音鍵** `ㄍㄡˇ-ㄋㄢˊ-ㄋㄩˇ`（權重 `-6.649`，該鍵之唯一條目）——而拼音之 `gnn` 正是靠 `PinyinTrie` 之前綴展開還原出該三桶才看得到它；**「幹你娘」**在原廠辭典內**零命中**，來自**逐字語言模型組句**（`ㄍㄢˋ` −5.206 ＋ `ㄋㄧˇ` −5.075 ＋ `ㄋㄧㄤˊ` −5.257；`ㄍㄢˋ` 起首之鍵有 72 條，而 `ㄍㄢˋ-ㄋ` 起首者 **0 條**）或使用者自有詞庫。**故事主所見之對比（拼音 `gnn` 見「狗男女」而不見「幹你娘」）即此二源之差異**（後者受 P155 所述之笛卡爾積防禦所抑）。**意涵：注音狂打之 copilot 窗之所以更強，正因它不必做那層前綴展開。**
8. **`hasFuriousFrontPending` 於注音側之語意，初稿訂為 `false` 是錯的**——它使注音狂打被排除在 copilot 窗體系之外，連帶使單聲母縮寫打法**完全不可用**（三顆聲母互搶同一個槽）。**本 phase 之規劃書已依事主異議改版**（§3.0、§3.5）；施工者若在任何處見到「注音不開 copilot 窗」之文字，一律以 §3.5 為準。
9. **`UserDef.allCases.count == 118` 這個數字被三處硬寫**：`VCSharedCLI_UserDefMetadata.swift:119` 之 `assert`（source 側，自動跟上）、助手 `tests/metadata.test.js:26` 之 `assert.strictEqual(metadata.count, 118)`（**須手改**）、以及助手之 `assets/userdef-metadata.json` 之 `count`（重生時自動跟上）。本案將使其成為 **119**。

### A.4 未驗／已知界線

| 項 | 說明 |
|---|---|
| 注音狂打之**實機手感** | 無法於本 phase 驗（無實作）。此為 P255 之後之事主驗收項 |
| 五種動態排列下之自動切音節是否全部正確 | 本文之判準（§3.2）係由程式碼結構推導，**未**逐排列窮舉驗證其正確性。P255 須以 IH157 一類測試覆蓋至少 Dachen26 與 ETen26（覆寫語意最強者） |
| 「`ㄅㄧ` ＋ `ㄢ`」之猜測是否符合使用者直覺 | 本文主張「不切、續接為 `ㄅㄧㄢ`」（§3.2）。此與拼音狂拼之 greedy 語義一致，但**注音使用者之直覺可能不同**。列為事主實測項 |
| `DevReqsHistory.md`／`KnowledgeMemo4LLM.md` 之更新 | **已執行**（即時補記，未延後） |
| 官網／`UserGuide` | 本案不動（功能尚未存在） |
