# Phase 301 研究：唯音雙拼支援（Arimitsu）之設計與校驗

> 狀態：研究稿（2026-10-12；同日按其架構定調與按鍵碼訂正、暨其架構再定之四項裁定修訂、暨其參考實作之實測、暨其內建之再令〔內建預設改微軟、autochop 明文不做〕與內建之定案〔兩方案皆保留、改以 decodable schema 並將 JSON 原文固化於原始碼檔尾〕、暨其 schema 標題自持之指示）。本 Phase 為研究任務、不落任何原始碼改動；交付物即本檔，外加現行 Reqs 卷之 Phase 篇與 `DevReqsHistory.md` 之一列。
> 前置：`Research/Phase148_Research_FuriousTypingMode.md`（狂打模式研究；其時判定「雙拼不存在、與狂拼正交」）、`Reqs4LLM/Archive_P101-P200/Reqs_0151-0160.md:394-396`（「雙拼不做、由磁帶承載」之永久定案）、Rime 之 `double_pinyin_mspy.schema.yaml`（微軟雙拼之權威實作；已存 `tmp/mspy.yaml`）、zh.wikipedia「雙拼」條目之 raw wikitext（已存 `tmp/wiki_raw_208.80.154.224.txt`；內含各方案之鍵位模板）、`macroxue/shuangpin` 之 `evaluator.js`（GB/T 34947-2017 方案之獨立實作；已存 `tmp/sp_evaluator.js`）。

> **後續註記（P302 收尾；事主 m01201）**：本文為規劃期原貌，其所載 schema 之 `minCodeLength`／`codeLength`／`alphabet` 三欄已於 P302 收尾時撤除——碼長改常數 `DualpinParser.codeLength = 2`、`alphabet` 改由兩表與零聲母政策推算，`ZeroInitialPolicy` 亦更名 `NullOnsetPolicy`。現行規格見 `Reqs4LLM/Archive_P301-P400/Reqs_0301-0310.md` P302 篇與 `KnowledgeMemo4LLM.md`〈雙拼 schema 之三處精簡〉。

## 0. 起因

- 事主交辦（逐字）：「然後是 Phase 301 (P301) 研究任務。請根據 knowledgeMemo 裡面的 response pattern 等規定施工。Phase 301 主要研究怎麼給唯音輸入法（vChewing-macOS，主要手術範圍包括 LibVanguard）加裝雙拼支援。Tekkon 套件需要一個平起平坐的模組來作為 Tekkon 的翻譯官、將雙拼訊號翻譯成漢語拼音餵食給 Tekkon。這個新模組暫定命名為 Arimitsu。Arimitsu 得允許使用者給出雙拼 schema 且檢證這個雙拼 schema 是否可以合理地打出 Tekkon 所能辨識的全部漢語拼音 reading stem 組合。(本次施術盡量不修改 Tekkon Composer 本身。)(宮保拼音、亞偉速錄、追音輸入法 都不是雙拼，而是對機械鍵盤有要求的真並擊輸入法方案，不屬於這次的研究範圍。)」
- 追加交辦（逐字）：「然後 Arimitsu 內建的雙拼方案可以暫時先僅內建微軟方案。其餘方案我還在檢討。」⇒ **其後一度由 改令 取代、再經 內建之再令 復位**：微軟終為**內建預設**，GB/T 34947-2017 為第二內建。
- 改令（**摘要**；因該則係口述、此處不作逐字引文）：內建方案不採微軟，改採 **GB/T 34947-2017《信息技术 汉语拼音双拼和三拼输入通用要求》**之雙拼方案；並指出 GB/T 34947-2017 與小鶴雙拼皆未用到分號鍵，主張「分號鍵的攔截與否也可以弄成 DualPin JSON Schema 裡面可以定義的內容」。⇒ 分號攔截自此由「內建方案之硬接線」升格為 **schema 之一等欄位**（見 §3.2 之 `KeyInterception`、§3.7）；微軟方案則降為「user-supplied schema 之參考例」（見 §3.8、附錄 B）——**此點其後由 內建之再令 復位**。惟該則以「`;` 即符號選單鍵」為前提，- 內建之再令（**摘要**；2026-10-12，取代上則之「內建＝GB/T 34947-2017」）：**集成微軟雙拼方案作為預設值**，且**先不做 autochop 支持**。理由（逐字要點）：「中國內地各種在電腦上完成的公共考試（法考等考試）只允許使用微軟雙拼方案，且禁止考生更改輸入法設置。而且連Windows自身的輸入法都不給用，就故意預先安裝2007版的谷歌拼音。似乎是因為有關部門不信任微軟內建的輸入法（因為有未經允許的雲同步之特性；谷歌拼音的雲同步在中國內地是廢的）。」⇒ 內建預設改為**微軟雙拼**（§3.8）、GB/T 34947-2017 降為第二內建（§3.6）；autochop 由「待裁定」變為**明文不做**（§3.2 之 `AutochopPolicy` 以 `.disabled` 為預設）；考場一致性自此成為設計驅動力（§5.1）。
- 架構定調（**摘要**；該則係條列口述，此處逐字引其關鍵句，惟其中涉忌諱俗稱者改作摘要）：①「新增 Arimitsu 命名空間（與 Tekkon 平級），其中有 DualpinParser（不是 Enum 而是 Struct）」；②「Tekkon 與 Arimitsu 沒有互相的硬性依賴，只是在同一個 Swift Package Target 內、允許被同時互相搭配使用」；③「Tekkon::MandarinParser 不作修改，因為實際上打雙拼的時候 MandarinParser 恆為漢語拼音」；④「雙拼不存在亂序輸入。Rime 作者佛振指出：雙拼是對漢語拼音的二次編碼。整個鍵入順序仍舊是得按照聲介韻調這種宏觀順序鍵入的，所以雙拼的兩碼必定得按照這個順序」；⑤「磁帶模式的既有語意不動。目前階段暫時不考慮雙拼與磁帶模式的聯立，但今後…可能還會考慮允許使用者將磁帶模式作為雙拼模式的第三四碼的提供者、以藉此降低重碼率」；⑥「該標準之一切稱呼一律作『GB/T 34947-2017』（代碼層面直接寫 `GBT17`）」；⑦「DualpinTypewriter 也屬於 Furious 狂打模式的支援範圍」；⑧「你把 `;` 的 keycode 搞錯了…波浪符號鍵在 JIS 鍵盤走羊字鍵、在其餘鍵盤走 tilde 鍵」。
- 收束（**摘要**）：①「`eh` 等『Dualpin-Incompatible Pinyin Expression』得忽略處理」——孤立 ㄝ 打不出不妨事，蓋**漢語拼音不教孤立 ㄝ**（母語者只識「整體認讀音節」）；並確立處理序（逐字）：「**Arimitsu 將原始雙拼訊號翻譯成漢語拼音聲介韻 Stem String、然後塞給 Tekkon 處理、之後直接就是輸入法既有的漢語拼音打字處理流程**」；②「雙拼模式下所有正式插入 assembler 的 kanji reading 都是『沒有聲調的、完整的聲介韻讀音（注音）』」；③「雙拼最大碼長恆為 2，一般情況下不需要 autocrop，除非你想敲『阿爸』（a-ba）這種情況。這或許可以根據具體的雙拼 schema 自動判定。」⇒ 分別落實於 §3.3（DIPE）、§3.4.2 第 5 條、§3.4.4。
- 架構再定（**摘要**）：①「Arimitsu 與 Tekkon 同 target」（⇒ §1.4 之 `internal` 界限消失；**此點其後由 架構再定之二 反轉為「拆 target」**）；②現階段手術範圍集中於 `LibVanguard`——`WebConfigAssistant` 不急、`vChewing-macOS` 若加選項則落「鍵盤設定」畫面，惟呈現方式與**雙拼方案之 persistence** 仍待商榷（太複雜時或於 `SettingsUI`／`SettingsCocoa` 另開一頁）；③「雙拼狂打承襲拼音狂打之涵義」；④提問「Typewriters 如果可以套接使用的話，`DualpinTypewriter` 是否可以僅處理雙拼辨識、讓 `Typewriter_BPMFFullMatch` 與 `CassetteTypewriter` 給 `DualpinTypewriter` 打工（磁帶之參與僅在日後確定要做第三四碼提供者時）」⇒ 實查與結論見 §3.9。
- 參考實作之實測（逐字要點）：「macOS 內建的雙拼直接敲 `aba` 是會被拆成 `a ba` 來讀的。」暨「（剛才那個擷圖是小鶴雙拼。）」⇒ 該實作容許**單鍵成碼**、切分不得貪婪；且同一方案於 Apple 與 Rime 之實作碼長不同（詳 §4.6）。
- 小鶴雙拼之暫緩（逐字）：「小鶴暫時不集成的原因是我不知道小鶴雙拼是否受智財權保護。我已經給作者寫電郵詢問許可了，得等他回應。」⇒ 本 Phase 不實作小鶴；其碼表已隨 Wikipedia 條目取得（見 §4.1），列為「待授權」項。**其後由架構再定之三覆示收束為「先不討論」**（作者迄未回信）——自此不在「未裁定」之列。Wikipedia 同頁之 `{{efn}}` 旁註可供事主參酌：「小鹤的官方网站提供一个禁止商业使用的码表。键位和音形映射的概念本身没有条款约束，因此有称为『開源小鸛』的第三方码表。」——即**鍵位映射之概念本身不受條款約束**，受約束者是官方碼表檔案本身。
- **標題之自持**（事主指示，逐字要點）：「每個 Schema 需要允許有 RawTitle 與 LocalizedTitle 這兩個格式。當查不到 Localized Title 時就使用 English Localized Title、如果還撲空的話就用 RawTitle。」⇒ 落於 §3.2 之資料模型（`rawTitle`／`localizedTitle`）、§3.3 之標題解析（五級 fallback；E7／W8）與 §6.2 之測試；其查表收**語系標籤字串**、不收 Foundation `Locale`。
- 架構再定之二（**摘要**；逐字引其關鍵句）：①「Arimitsu 與 Tekkon 拆 Target、將 Arimitsu 單獨放成一個 Target，Tekkon 需曝露公開所有需要的 Target、或者單獨實作一個公開 API 介面來開放相關資料供 Arimitsu 存取。」——其目的（逐字）：「讓 Tekkon 的修改量被縮減到最小、便於減輕 TekkonWorkspace 那邊的跨語言遷移工作量」；②「Arimitsu Target 獨立化的處理方式也可以將相關的單元測試全部獨立出來」；③「Arimitsu 的 DefaultIsolation 暫定為 MainActor」。⇒ 取代「同 target」（架構再定①），落於 §1.4、§3.1、§5.2、§6.1；其歸屬其後再由架構再定之三定為 **`LibVanguard` 之直屬 SubTarget**（見下則）。
- schema 之身分與持久化（**摘要**；逐字引其關鍵句）：①「每個 Schema 需要有 DNS Name 作為唯一 ID (RawID)。例：`dualPin.Microsoft` `dualPin.GBT17` 等」；②「雙拼的 Persistence 採 UserDefaults，但 UserDefaults 僅承載一筆 Schema 的內容。而且，如果使用者選擇的是原廠 Schema 的話，UserDefaults 只需要記住這是原廠的哪個 Schema 及其 RawID 即可。」⇒ 落於 §3.2（`rawID` 欄位、內建兩者之 DNS 名）、§3.3（E9、持久化）、§5.2。
- 待裁定諸項之收束（**摘要**；逐字引其關鍵句）：①「pending 首鍵之顯示：一律顯示原始鍵。」理由（逐字）：「雙拼用戶往往都沒學過注音」；②「TypingMode Enum 需要加上 DualPin」；③「雙拼下之『單鍵簡拼』暫時擱置、暫時不實作。回頭可以在 Arimitsu 套件裡面補上相關輔助工具來實作」；④「`minCodeLength = 1 之 schema 是否支援` 先拒絕載入。或者一律只承認 2。雙拼本來就是二碼，不用把事情搞複雜。那種『以 a 代替 aa』的方法更像是一個通用邏輯方案。」⇒ 落於 §3.3（E8）、§3.4.3、§3.5、§5.2。
- 架構再定之三與 P302 施工序（**摘要**；逐字引其關鍵句，2026-10-12）：①「`Arimitsu` 屬於 LibVanguard 的直屬 SubTarget。」②「無效兩鍵序之提示形為直接 Beep ＋ Drop 掉這兩個無效 keyHit。」③「小鶴雙拼先不討論。那個作者是個懶人，到現在都沒回我電郵，不用管他。」④「macOS 側設定界面我還在考量。」⑤「P302 的手術範圍限制在 LibVanguard 內，且 Tekkon 相關的修改必須單獨獨立一個 Commit 先行遞交、其後才是 LibVanguard 的其他內容。」⇒ 落於 §1.4、§3.1（歸屬、manifest 與巢狀 target 之實測）、§3.4.1（無效序之處置）、§5.1／§5.2（未裁定收為二項）、§6.4（施工序）。
- 他牌輸入法之 autochop 實測（事主供圖，2026-10-12）：Apple（macOS 內建）、微信輸入法、搜狗拼音皆「**不成碼即切**」，惟切出之殘段處置各異（回溯為短音節／前綴候選／原文 ASCII）；**微軟拼音（Win11）之內建方案則不切**。其方案編輯器之資料模型（音節→按鍵、零聲母三態枚舉）與本稿同構 ⇒ 逐條見 §4.6–§4.8。
- 事主之原始構想（**摘要**；本 Phase 之緣起，其後由架構定調、架構再定、收束諸則逐項收束）：雙拼須支援**使用者自備之 Dualpin Schema**；其處置裝置獨立於 `Tekkon.Composer`；把雙拼訊號譯成**無聲調**之漢語拼音後，由打字機側將譯得之訊號**當作完整漢語拼音**插入 Composer。⇒ §3 之 `DualpinParser`／翻譯器／前控式打字機即此構想之落地。
- 名詞：雙拼之英語稱謂＝**Dualpin**、日語稱謂＝**双弁／双弁入力**；本文一律作「雙拼」。
- 反轉之定性：`Reqs_0151-0160.md:394-396` 之永久定案（事主 2026-08-27）為「**雙拼（`MandarinParser` 新增 case＋雙拼表）——決定不做**：有需求的雙拼用戶（小鶴雙拼、小鶴音形等）自行以磁帶模式（Cassette）準備對應磁帶方案，唯音不內建雙拼鍵盤」。該定案之前提為「雙拼＝由磁帶承載之外部方案」；P301 要求內建（初令為微軟，其後經 改令 改為 GB/T 34947-2017）＋ user-supplied schema ⇒ 該定案自此僅存於歷史記錄。**磁帶模式本身不動**（架構定調⑤再確認其既有語意不動），仍為雙拼以外之客製方案之路；惟日後可能允許磁帶提供雙拼之第三／四碼以降低重碼率（見 §3.5、§5.3）。
- 範圍界定：真並擊方案（宮保拼音／亞偉速錄／追音輸入法）不在範圍——彼等要求機械鍵盤之 N-key rollover 與並擊，與雙拼「兩鍵定長、有序」之模型不同構。
- **引用慣例**：本文所引事主來訊皆為 **2026-10-12** 同日往返，一律以「日期＋主題」記之（如「架構定調」「架構再定」「收束」「參考實作之實測」「微信實測①／②」「搜狗實測」），不採工作階段內部之訊息編號——該等編號於本倉陳列時無從解析。

## 1. 動工前盤點

### 1.1 Tekkon 之拼音管線（`vChewing-LibVanguard/Sources/Tekkon/`，七檔 3,014 行）

| 檔案 | 行數 | 對 P301 之意義 |
| --- | --- | --- |
| `Tekkon_Constants.swift` | 1,020 | `mapHanyuPinyin`（:249–360；426 條、key＝無調拼音詞幹、value＝注音）為全部讀音之正本；`mapArayuruPinyin`（:238）、`mapArayuruPinyinIntonation`（:245） |
| `Tekkon_Phonabets.swift` | 270 | `MandarinParser`（6 拼音案・11 注音案；`isPinyin` 為 `rawValue >= 100`）、`mapZhuyinPinyin`（:73，拼音→注音） |
| `Tekkon_SyllableComposer.swift` | 985 | 組音區：`replacePinyinBuffer(with:)`（:306–313）＝插入完整漢拼之既有正門 |
| `Tekkon_SyllableIndex.swift` | 139 | `allReadings`（:59，426 條**注音**）、`shared(parser:)`（:72） |
| `Tekkon_PinyinTrie.swift` | 293 | `chop`／`search`／`zhuyinReadings(forPinyinFragment:)`；供全拼之貪婪切分 |
| `Tekkon_PhonabetAutoChop.swift` | 64 | `shouldAutoChopPhonabets(byTyping:)`——**注音側**之自動切分判準 |
| `Tekkon_Utilities.swift` | 243 | `makeToneInsensitiveVariants(of:)`（:12–22）＝一個讀音之五態聲調桶 |

拼音側**沒有**與 `shouldAutoChopPhonabets` 對應之物：全拼之切分是 `Composer.pinyinAutoChopResult(appending:)`（:276–302），走 `PinyinTrie.chop` 之貪婪最長前綴。雙拼定長兩鍵 ⇒ 切分為先驗，兩者皆不需要。

### 1.2 接入點（打字機側）

- `Sources/LibVanguard/InputHandler/InputHandler_HandleComposition.swift:36-44`：`isMixedAlphanumericalLayerInEffect` 優先 → `switch typingMode`（五值；`.cassette` 交 `CassetteTypewriter`，其餘四值交 `BPMFFullMatchTypewriter`）。**該 `switch` 無 `default` ⇒ 新增 `TypingMode` case 會 Compile Error（編譯器強制補全，屬良性）——P302 增 `.DualPin` 即藉此補全（§3.5）。**
- **打字機之套接已有先例**（架構再定④之實查）：`Sources/LibVanguard/Typewriter/Typewriter_MixedAlphanumerical.swift:24-28`（亦見 `:195-212`、`:249-263`）即「持有同一 `handler`、於自身 `handle` 內具現 `BPMFFullMatchTypewriter(handler)` 並 `return typewriter.handle(input)`」之形，並以 `isToneOverrideEnabled = { false }`／`isLeadingIntonationAccepted = { false }` 收束被套接者。`Typewriter_BPMFFullMatch` 之可注入面＝`public var onLexiconMatchFailure`（`:23`）／`isToneOverrideEnabled`（`:26`）／`isLeadingIntonationAccepted`（`:29`）。
- `Sources/LibVanguard/Typewriter/Typewriter_BPMFFullMatch.swift`（734 行）：`handle(_:)`（:34）之序為「記 `existedIntonation` → `skipPhoneticHandling`（:40-42）→ `confirmCombination`（:43）→ 狂拼就地選字 → Enter 固化 → `consumeReadingInputIfNeeded`（:172）→ `composeReadingIfReady`（:354）→ `handleStandaloneIntonation`（:436）」。其中 `consumeReadingInputIfNeeded` 內序為 `performRearIntonationOverrideIfNeeded`（:185）→ `performPinyinAutoChopIfNeeded`（:191）→ `performPhonabetAutoChopIfNeeded`（:200）→ `composer.receiveKey(fromString:)`（:211）。
- `performPinyinAutoChopIfNeeded`（:226）即**「固化舊音節 → 插入組字器 → 以新詞幹替換組音區」之既有樣板**：`pinyinAutoChopResult(appending:)`（:240）→ `makeToneInsensitiveVariants`＋`lxQuerier.hasGrams` 過濾（:251-258）→ 逐鍵 `assembler.insertKey(readingKey)`（:261）→ 記 `furiousTrail`（:271-282）→ `commitOverflownComposition`／`retrievePOMSuggestions(apply:)`／`replacePinyinBuffer(with: remainingRomaji)`（:284-286）→ `switchState`／`handleTypewriterSCPCTasks`／`resegmentFuriousTrailIfNeeded`（:293-298）。**雙拼之固化步驟與此同構**，差別僅在「切分結果由誰給出」。
- `Composer.receiveKey(fromScalar:)`（:243–268）：拼音側**先判聲調**（`if let theTone = mapArayuruPinyinIntonation[input] { intonation = Phonabet(theTone) }`），否則方累積羅馬字並在 `romajiBuffer.count > maxCount - 1` 時自首端丟字（`maxCount` 為 6；威妥瑪 7）。⇒ **聲調鍵必須在翻譯器之前分岔**。
- `Composer.replacePinyinBuffer(with:)`（:306–313）＝`guard isPinyinMode` → `clear()` → `guard !romaji.isEmpty` → `receiveSequence(romaji, isRomaji: true)` → `romajiBuffer = romaji`。其語義即「以完整漢拼重建組音區」。**不得直呼 `receiveSequence`**：它不會同步 `romajiBuffer`，會令顯示與狀態脫節、退格時 `_refreshRomajiBufferIfNeeded()` 算錯。
- `Composer.phonabetKeyForQuery(pronounceableOnly:)`（:567–588）＝取 `getComposition()`（聲介韻調串接、陰平為空白），拼音側以 `isPronounceable` 為有效判準。
- `Sources/LibVanguard/InputHandler/InputHandler_TypingMode.swift:14`：`TypingMode` 五值（`cassette`／`bopomofoKeyblock`／`pinyinKeyblock`／`pinyinFuriousTyping`／`zhuyinFuriousTyping`；**P302 增第六值 `.DualPin`**，見 §3.5）；`typingMode`（:58–68）之序為「磁帶優先 → 狂打開關（依注拼槽之鍵盤家族）＋非 SCPC → 依 `composer.isPinyinMode` 分注音／拼音鍵盤」。`:15` 之 `cassette` 註釋仍寫「雙拼…由磁帶承載」——**P301 之後此文句不再成立（將有內建雙拼方案與 user-supplied schema），屬文案漂移，P302 須回檢**。
- `Sources/LibVanguard/InputHandler/InputHandler_CoreProtocol.swift:461-477`：以 `switch` 把打字模式之排列映到 `composer.ensureParser(arrange:)`（17 個排列全列）⇒ 雙拼之排列恆為 `.ofHanyuPinyin`（架構定調③：`MandarinParser` 不改），故此處無須新增分支，只需令雙拼生效時 `composer.parser == .ofHanyuPinyin`。

### 1.3 組字器之多讀音設施（重碼之既有出路）

- `Sources/Homa/Homa_BasicTypes/Homa_PossibleKey.swift:11-13`：`public enum PossibleKey: Hashable, Sendable { case singleKey(String); case multipleKeys([String]) }`，其文件註釋明言「**代表組字器某一個位置的所有可能讀音**」，`allValues` 回傳全部候選。
- `Sources/Homa/Homa_MainComponents/Homa_Assembler.swift`：`insertKey(_ key: String)`（:176）／**`insertKey(_ key: [String])`（:182；＝同一位置之多個替代讀音）**／`insertKeys(_ givenKeys: [PossibleKey])`（:189）／`insertKeys(_ givenKeys: [[String]])`（:227）／`insertKeys(_ givenKeys: [String])`（:237）。
- `Tekkon.makeToneInsensitiveVariants(of:)`（`Tekkon_Utilities.swift:12-22`）＝對 `allowedIntonations`（`[" ", "ˊ", "ˇ", "ˋ", "˙"]`）逐項串接（陰平串空字串）＝**五態聲調桶**。`performPinyinAutoChopIfNeeded:251-258` 即以「桶」為單位交給組字器。
- ⇒ 雙拼之「一碼多音節」（如 `lo` → {`lo`, `luo`}）可表示為**單一位置之多讀音鍵**，由 Homa 之 DP 依語言模型裁定，**無須在翻譯層靜默擇一**，亦無須為雙拼新增組字器介面。

### 1.4 模組邊界（決定 Arimitsu 之可及面）

- `Tekkon_Constants.swift:249 static let mapHanyuPinyin`＝**internal**，跨 target 不可讀。
- `Tekkon_Phonabets.swift:49 public var isPinyin`、`:73 public var mapZhuyinPinyin: [String: String]?`（`ofHanyuPinyin` 回 `mapHanyuPinyin`）＝**public**。
- `Tekkon_SyllableIndex.swift:59 public static var allReadings: [String]`＝其源為 `Set(mapHanyuPinyin.values)` ⇒ 內容係**注音**讀音 426 條，**不是**拼音詞幹（易誤用）。
- ⇒ **Arimitsu 取「426 條漢語拼音詞幹」之既有公開途徑＝`MandarinParser.ofHanyuPinyin.mapZhuyinPinyin!.keys`**（其後架構再定之二另立專用之公開 API，見下）。
- **拆 target（架構再定之二；取代前此之「同 target」）**：Arimitsu 自成 target ⇒ `mapHanyuPinyin` 等 `internal` 成員**不可直讀**（上列界限回復、且為設計之前提）。Tekkon 須自行曝露所需之公開面（事主逐字：「Tekkon 需曝露公開所有需要的 Target、或者單獨實作一個公開 API 介面來開放相關資料供 Arimitsu 存取」）⇒ **首選：Tekkon 增一枚純值公開 API**——`public static var allHanyuPinyinStems: [String]`（即 `mapHanyuPinyin.keys` 之公開投影，426 條），落 `Tekkon_Constants.swift` 或 `Tekkon_SyllableIndex.swift`，僅數行。理由：①`mapZhuyinPinyin!.keys` 語義迂迴（**值**才是注音、**鍵**才是拼音），而 `SyllableIndex.allReadings` 係**注音**（易誤用）；②純值 API 對 `TekkonWorkspace` 之 C++／C# 版遷移成本最低（一枚「字串陣列」級之介面）。`MandarinParser.ofHanyuPinyin.mapZhuyinPinyin!.keys` 自此降為**交叉核對**之用。**歸屬（架構再定之三）**：Arimitsu 係 `LibVanguard` 之**直屬 SubTarget**——仍是獨立 target、仍由 `LibVanguard` 直接依賴，惟不與 `Tekkon`／`Homa` 等並列為 package 之頂層同儕；其原始碼置於 `Sources/LibVanguard/Arimitsu/`（§3.1）。

### 1.5 雙拼之既有史實

- Phase 148（狂打研究）：`MandarinParser` 100–105 全為全拼式（雙拼零支援）、Tekkon 全倉「雙拼」零命中；並判定「雙拼是與狂拼正交的獨立工作量（需在 Tekkon 新增 `MandarinParser` case＋`mapZhuyinPinyin` 表）」。
- Phase 151 之永久定案（§0 已引）。
- 全倉 `Arimitsu` 零命中 ⇒ 本 Phase 係從零起造，無既有實作可依附。

## 2. 排除項

1. **真並擊方案**（宮保拼音／亞偉速錄／追音輸入法）：非雙拼，見 §0。
2. **亂序雙拼**：並非「一時不可行」而已，而係不符雙拼之定義——雙拼是對漢語拼音之二次編碼，鍵入仍按聲介韻調之宏觀順序（架構定調④引 Rime 作者佛振之論）⇒ 兩碼必依序。算術上亦無餘裕（見 §4.3）。
3. **趙元任國語羅馬字**：聲調寫進拼寫本身、無獨立聲調槽 ⇒ 與 Composer「聲調獨佔一槽、`receiveKey(fromScalar:)` 先判聲調」之模型不相容。
4. **改動 `Tekkon.Composer` 本體**（事主明示）：不得改 `receiveKey`／`receiveSequence`／`pinyinAutoChopResult` 之語義；Arimitsu 不得令 Tekkon 反向依賴之。`MandarinParser` 之既有 17 案亦不動（架構定調③）。
5. **磁帶模式之既有語義**：不動；雙拼不寄生於磁帶（Phase 151 之「由磁帶承載」路線作廢）。雙拼×磁帶之聯立（磁帶作第三／四碼之提供者）列為將來之可能（架構定調⑤），本 Phase 不設計。
6. **小鶴雙拼（含小鶴音形）之實作**：非技術性排除，而係**智財權未釐清**——事主去信作者迄未得覆，其後明示「先不討論…不用管他」（架構再定之三）⇒ 本 Phase 不納入、亦不再列為待裁定項。技術上小鶴亦為「無分號鍵、26 鍵」之方案，日後若有授權，加入成本即 §3.6 之三張表＋一組測試。
7. **autochop（未滿碼之回溯／前綴猜測）之實作**：內建之再令明示「先不做」；§4.8 之各牌實測僅作設計依據，本 Phase 只把該行為記入 schema（§3.2 之 `AutochopPolicy`），P302 不施工。
8. **考場環境本身**（法考等之專用機與其 2007 版谷歌拼音之部署）：不研究；只取其**方案碼表**與**行為**作等同性驗收之目標（§5.1、§6.2）。

## 3. 設計

### 3.1 模組歸屬與檔案佈局

- 新增 target `Arimitsu`，係 **`LibVanguard` 之直屬 SubTarget**（架構再定之三；仍獨立於 `Tekkon`，架構再定之二）：仍為獨立 target、仍由 `LibVanguard` 直接依賴，惟**不**與 `Tekkon`／`Homa`／`Shared` 等並列為 package 之頂層同儕；其原始碼置於 `Sources/LibVanguard/Arimitsu/`，父 target 以 `exclude: ["Arimitsu"]` 讓出該子目錄。依賴方向單向：`Arimitsu` → `Tekkon`（僅經 Tekkon 之公開 API 取讀音清單，§1.4）；`LibVanguard` → `Arimitsu`（打字機側）。Tekkon **不**依賴 Arimitsu ⇒ 其改動量僅「一枚公開 API」，便於 `TekkonWorkspace` 之跨語言遷移（架構再定之二之目的）。
- 主要型別為 `Arimitsu.DualpinParser`（**struct**，非 enum）：一份雙拼方案之載入＋檢證＋編解碼。所謂「Dualpin Schema」即該方案之 **JSON 檔案格式**（使用者自備者亦此形）。
- 建議檔案：

| 檔案 | 職責 |
| --- | --- |
| `Sources/LibVanguard/Arimitsu/DualpinParser.swift` | `public struct DualpinParser`：schema 之型別、`Decodable` 載入、`validate(inventory:) -> DualpinValidationReport`、`encode(stem:) -> [String]`、`decode(code:) -> [String]`；**檔尾**另附內建兩方案之 JSON 原文（三引號字串塊）暨解碼所得之 `public static let mspy`／`gbt17` |
| `Sources/LibVanguard/Arimitsu/DualpinTranslator.swift` | 狀態機（`pending` 之持有人；兩鍵 → 詞幹集合） |
| `Package.swift` 與 `Package@swift-5.10.swift`（`vChewing-LibVanguard`） | 兩份 manifest **皆**新增 target `Arimitsu`（依賴 `Tekkon`）暨測試 target `ArimitsuTests`；6.4 側設 `defaultIsolation(MainActor.self)`，5.10 對位版無此設定；`Vanguard` 產品之 target 清單亦加 `"Arimitsu"`（該清單本即明列整個閉包） |
| `Tests/LibVanguardTests/Arimitsu/` | 見 §6.2（**獨立之測試目標 `ArimitsuTests`**，同法巢狀於 `Tests/LibVanguardTests/` 之下） |

- **巢狀 target 之可行性已實測**（P301）：SwiftPM 容許「子目錄為另一 target 之 `path`」，只須父 target 以 `exclude` 讓出該子目錄——以 tools 6.0 造最小 manifest（`Sources/A/B` 為 `B` 之 `path`、`A` 施 `exclude: ["B"]`），`swift package describe --disable-sandbox` 載入成功（`B` 之 `Path` 作 `Sources/A/B`）。故「直屬 SubTarget」於檔案佈局上即 `Sources/LibVanguard/Arimitsu/`，無須另闢頂層目錄。
- **實作須通過兩側建置**：Arimitsu 之原始碼同受 `Package.swift`（tools 6.4）與 `Package@swift-5.10.swift`（語言模式 Swift 5、無 `defaultIsolation`）兩份 manifest 建置（§6.1、§6.2）。
- 命名維持所有者所定之「Arimitsu」（暫定）；其緣起（事主補述）＝**漢語拼音發明人周有光**之名「有光」的日文漢字音讀（ありみつ／Arimitsu）——係人名之音讀轉寫、非字面語義詞，勿於後續「正名」時改之。代碼層以 `MSPY` 指涉**微軟雙拼**（內建預設）、以 `GBT17` 指涉 GB/T 34947-2017（第二內建；架構定調⑥）。
- **內建＝同一 JSON 格式之 decodable schema**（架構再定之延伸）：內建方案**不另立 per-scheme Swift 型別與檔案、不手寫表**；其 JSON 原文以三引號字串塊固化於 `DualpinParser.swift` **檔尾**，經**與使用者自備檔完全相同之 decoder** 載入 ⇒ ①格式一旦改動，內建即於載入與測試期大聲失敗；②「Swift 表」與「JSON 格式」不致成兩份真相；③使用者自備者係同一格式之 `.json` 檔，而內建之原文即其範例。
- **讀音清單之來源（拆 target 之故）**：校驗器不再直讀 `Tekkon.mapHanyuPinyin`（`internal`）；改以 `DualpinParser.validate(inventory:)` 之**參數**收受（純值 `[String]`，426 條），預設值由新增之 `Tekkon.allHanyuPinyinStems` 給出；`MandarinParser.ofHanyuPinyin.mapZhuyinPinyin!.keys` 作交叉核對（§1.4）。
- **`DefaultIsolation` 暫定為 `MainActor`**（事主明示）：target 以 `defaultIsolation(MainActor.self)` 建置 ⇒ 未標註之型別與函式預設 MainActor 隔離。影響：①schema 之載入／校驗與翻譯器之狀態機皆在主執行緒（雙拼係逐鍵互動，本即主執行緒）；②資料模型仍照列 `Sendable`，以備他日鬆綁；③測試目標 `ArimitsuTests`（住 `Tests/LibVanguardTests/Arimitsu/`）須 `@MainActor`（§6.2）；④Tekkon 之公開 API 為不可變之 `static let`（`Sendable`），自 MainActor 讀取無礙。此係「暫定」——日後改 `nonisolated` 僅動標註、不動模型。

### 3.2 `DualpinParser` 之資料模型

```swift
public struct DualpinParser: Codable, Hashable, Sendable {
  public enum ZeroInitialPolicy: Codable, Hashable, Sendable {
    case fixedKey(Character)              // ①固定一鍵作零聲母：GB/T 34947-2017＝"a"；微軟／智能ABC／紫光／搜狗＝"o"
    case finalInitial                     // ②以韻母首字母為零聲母：拼音加加
    case finalInitialOrVerbatimDigraph    // ③單韻母與三韻母取首字母、雙韻母照原樣輸入：自然碼、小鶴
  }

  /// 主機保留鍵之攔截政策：本方案之 alphabet 中，哪些鍵須先於主機既有處理序交 Arimitsu。
  /// （事主改令之要求；其原文以「分號鍵」為題，按鍵碼經其架構定調訂正後，動機例改為波浪符號鍵。）
  public enum KeyInterception: Codable, Hashable, Sendable {
    case none                             // 不攔截（預設；GB/T 34947-2017 與微軟之 ";" 皆屬此）
    case explicit(Set<Character>)         // 僅攔截明列之鍵（如波浪符號鍵、漢音符號熱鍵）
    case schemeAlphabet                   // 攔截 alphabet 內之全部鍵（最保守）
  }

  /// 未滿碼之殘段如何處置。**預設 `.disabled`**——此係內建之再令「先不做 autochop 支持」之落點，
  /// 亦即：本設計把「不做」寫成一個明示之規格狀態，而非功能缺口；日後支援他形時只增 case，schema 檔不必改版。
  /// 各家實作之行為分歧見 §4.8（Apple／微信／搜狗切、微軟／谷歌拼音不切）。
  public enum AutochopPolicy: Codable, Hashable, Sendable {
    case disabled                          // 不回溯、不猜：未成碼之鍵序列不進組音區（本版唯一實作；微軟／谷歌拼音亦此）
    case backtrackToShorterReading         // Apple 形：不成碼即退一鍵、固化為較短之合法音節（§4.6）
    case prefixCandidates                  // 微信形：未滿碼者留置並列前綴候選（§4.8）
    case passThroughVerbatim               // 搜狗形：切界＋殘段以原文 ASCII 出字（§4.8）
  }

  /// 方案之唯一 ID：**DNS 名**（反向域名形，如 `dualPin.Microsoft`／`dualPin.GBT17`；事主明示）。
  /// 用途：內建方案之指名、持久化之鍵（見本節末）、他日方案庫之識別。空／非 DNS 形／相衝 ⇒ E9。
  public var rawID: String
  /// 方案之原文標題（該方案所屬語境之原文，可為簡體；不得為空 ⇒ E7）。
  public var rawTitle: String
  /// 語系標籤（Apple 形，如 "en"／"zh-Hant"／"zh-Hans"／"ja"；比對時 "_" 與 "-" 等價，ICU 形 "zh_Hant" 亦命中）→ 該語系之標題。
  /// 解析序：精確標籤 → 去區域（"zh-Hant-TW" → "zh-Hant"）→ 語言主標籤 → "en" → `rawTitle`（見 §3.3）。
  public var localizedTitle: [String: String] = [:]
  public var alphabet: Set<Character>        // GB/T 34947-2017＝26 字母；微軟＝26 字母＋";"
  public var minCodeLength: Int = 2          // 最短碼（**恆為 2**；非 2 ⇒ E8 拒收——收束：雙拼本來就是二碼）
  public var codeLength: Int = 2             // 最長碼（**恆為 2**；非 2 ⇒ E8）
  public var initials: [String: Character]   // 聲母 → 鍵（含 zh/ch/sh；可含 y/w）
  public var finals: [String: Character]     // 尾綴 → 鍵（**全等**匹配；辭典形，與 initials 同制）
  public var zeroInitial: ZeroInitialPolicy
  public var keyInterception: KeyInterception = .none  // 主機保留鍵之處置（§3.7）
  public var autochopPolicy: AutochopPolicy = .disabled  // 未滿碼之殘段（本版只支援 .disabled；§3.3 之 W7）
  public var overrides: [String: String] = [:]      // 詞幹 → 碼（最高優先）
  public var aliases: [String: String] = [:]        // 額外可接受之碼 → 詞幹
  public var acknowledgedUnreachable: Set<String> = []
}
```

- **為何採「聲母表＋尾綴改寫表」而非 426 條全表**：全表無從稽核其內部一致性（改一條即需重驗其餘 425 條）；而「聲母 23 條＋尾綴 25 條＋單韻母 5 條＋零聲母政策」共約 55 條即足以生成全部碼。此形式對兩種公開描述皆可承載：微軟之權威描述係 Rime 之 `algebra` 尾綴改寫鏈（逐條見 §3.8）、GB/T 34947-2017 之權威描述係逐鍵表（Wikipedia 模板與 `macroxue/shuangpin` 之 `schemes` 表內之 GB/T 條目皆此形），二者皆可直譯為本模型。實際碼由 §3.6 之演算法生成、由 §6.2 之 round-trip 測試釘死。
- **內建方案之參數**（兩個，皆內建；使用者可二擇，**預設為微軟**——內建之再令；兩者皆為上述 JSON 格式之 decodable schema，其原文固化於 `DualpinParser.swift` 檔尾）：
  - **預設：微軟雙拼（`MSPY`）**——`alphabet` ＝ 26 字母＋`;`（`;`＝`ing`，11 條音節用及）、`zeroInitial` ＝ `.fixedKey("o")`、`keyInterception` ＝ `.none`、`autochopPolicy` ＝ `.disabled`、`minCodeLength` ＝ `codeLength` ＝ 2、`rawID` ＝ `dualPin.Microsoft`（§3.8、附錄 B）。
  - **第二：GB/T 34947-2017（`GBT17`）**——`alphabet` ＝ 26 字母（**不含 `;`**）、`zeroInitial` ＝ `.fixedKey("a")`（Wikipedia 該條目 `:18` 明言其零聲母鍵固定為 `A`）、`keyInterception` ＝ `.none`、`autochopPolicy` ＝ `.disabled`、`minCodeLength` ＝ `codeLength` ＝ 2、`rawID` ＝ `dualPin.GBT17`、`acknowledgedUnreachable` ＝ `[]`（`eh` 屬 DIPE，見 §3.3，不須明列）（§3.6、附錄 A）。
- **`rawID` ＝ DNS 名**（事主明示）：每份 schema 以 DNS 名作唯一 ID（內建＝`dualPin.Microsoft`／`dualPin.GBT17`；自備者由作者自定，如 `dualPin.MyScheme`）。用途：①內建方案之指名——`UserDefaults` 只存其 `rawID` 即可完整複現；②他日方案庫之鍵；③報告與顯示之穩定識別（**顯示名**另有 `rawTitle`／`localizedTitle`，兩者不可混用）。校驗見 **E9**（§3.3）。
- **持久化＝`UserDefaults`、僅承載一筆**（事主明示）：`UserDefaults` 只承載**當前**一份 schema——自備者存其 JSON 內容原文；若所選為**原廠 schema**，則僅存該方案之 `rawID`（如 `dualPin.Microsoft`），載入時由內建 JSON 原文還原。⇒ **無多方案庫、無外部檔案、無資料庫**；「同時保有兩份自備方案」不在本版語義內。macOS 側界面之歸屬仍待裁定（§5.2）。
- **拼寫正規化**：本引擎內之 ü 有兩種拼寫——n/l 之後作 `v`（`nv`／`nve`／`lv`／`lve`／`lvan`），j/q/x/y 之後作 `u`（`ju`／`jue`／`juan`／`jun`／`yu`／`yuan`／`yue`／`yun`）。schema 載入時對 n/l 後之 ü 一律正規化為 `v`（使用者若寫 `nü` 則自動改寫為 `nv`），並發 WARNING。另一型正規化為**方案級之韻母合併**：GB/T 34947-2017 依 Wikipedia 之注記「`un` 同时表示 `un` 和 `ün`，`uan` 同时表示 `uan` 和 `üan`」，故 üan 併入 `uan` 之規則、ün 併入 `un` 之規則——`lvan`（ㄌㄩㄢ，非標準音節）即藉此得碼 `lw`；微軟則將 üan 與 ün 分別作 `r`／`p` 之別名（見附錄 B）。
- **微軟拼音之方案編輯器（Win11，事主實測）即此模型之現成對照**：其「新增配置」以**逐條「音節 → 按鍵」配對**編輯（音節清單含 `ch`／`sh`／`zh` 與 `ai`／`an`／`ang`／`ao`／`ei`／`en`／`eng`／`er`／`ia`…，未設定者作 `-`），零聲母政策作**三態枚舉**、`範本` 三選（「（無）」／「智慧型 ABC」／「自然代碼」）。⇒ 與本稿之 `initials` ＋ `finals` ＋ `zeroInitial` 同構，可作欄位命名與 JSON 形之參考（逐項見 §4.8）。

### 3.3 校驗：`DualpinParser.validate(inventory:)`

輸入：schema＋讀音清單（inventory ＝ 純值 `[String]`，426 條；預設由 Tekkon 之新增公開 API `allHanyuPinyinStems` 給出，`MandarinParser.ofHanyuPinyin.mapZhuyinPinyin!.keys` 作交叉核對——§1.4）。演算法五步：

1. **分解**：對每個詞幹，以 `initials` 中最長匹配者取聲母（`zh`／`ch`／`sh` 先於單字母）；餘部以 `finals` 作**全等**查表改寫（辭典取鍵，不涉次序）；零聲母者依 `zeroInitial` 加前綴。
2. **取碼**：`overrides` 優先於上一步之結果。
3. **反向建索引**：碼 → 詞幹集合。
4. **分類**：逐條比對下表。
5. **結算**：`isUsable ＝ errors.isEmpty`。

| 級別 | 代號 | 判準 |
| --- | --- | --- |
| ERROR | E1 | 碼含 `alphabet` 外之鍵 |
| ERROR | E2 | 碼長 ≠ 2（且未經 `overrides` 明示） |
| ERROR | E3 | 讀音清單內有詞幹無法得碼，且既未列於 `acknowledgedUnreachable`、亦非 DIPE（見下） |
| ERROR | E4 | `alphabet` 含聲調鍵（`1`–`5`、空格、`ˊˇˋ˙`）或不可列印字元——會與 Composer 之聲調語義相撞 |
| ERROR | E5 | 同一詞幹得兩個非別名之碼（映射非函式） |
| ERROR | E6 | `keyInterception.explicit` 所列之鍵不在 `alphabet` 內（或非可攔截之字元鍵） |
| ERROR | E7 | `rawTitle` 為空——標題解析鏈之最終退路不得缺 |
| ERROR | E8 | 碼長之宣告非 2——`minCodeLength ≠ 2`／`codeLength ≠ 2`／`overrides` 之任一碼非二鍵 ⇒ **整份拒收**（收束：雙拼本來就是二碼） |
| ERROR | E9 | `rawID` 為空、非 DNS 形（反向域名，如 `dualPin.Microsoft`）、或與現存 schema（含內建兩方案）相衝 |
| WARNING | W1 | `acknowledgedUnreachable` 所列之詞幹（可表達而刻意不表達者；DIPE 不列於此） |
| WARNING | W2 | 重碼：一碼對多詞幹（雙拼之常態；由 §1.3 之多讀音鍵與語言模型裁定） |
| WARNING | W3 | 碼使用主機保留鍵（波浪符號鍵、漢音符號熱鍵 `¥`／`\`）而未於 `keyInterception` 明列 |
| WARNING | W4 | 載入時對 ü／`v` 拼寫作了正規化改寫 |
| WARNING | W5 | `alphabet` 內有冗餘鍵（無任何碼使用） |
| — | ~~W6~~ | **已廢**：原「詞幹以 `overrides` 之非定長碼表達（如三鍵之 `eh`）」條——碼長一律 2 後不再適用，改列 **E8** 拒收（編號保留，以免他處引用漂移） |
| WARNING | W7 | `autochopPolicy` 非 `.disabled`（本版尚未支援他形；載入後以 `.disabled` 運行並明示） |
| WARNING | W8 | `localizedTitle` 缺 `en`（fallback 鏈之第二級缺席；不致無標題，惟英文係各語系之通用退路） |

- 報告型別：`DualpinValidationReport { rawID, errors, warnings, codeToStems, stemToCode, stats }`，`stats` 含碼長分布、相異碼數、鍵使用率、**自由槽位數**（`alphabet.count^codeLength − 相異碼數`）。
- **Dualpin-Incompatible Pinyin Expression（下稱 DIPE）**（收束①）：指「存在於漢語拼音之拼式空間、卻無從於雙拼之鍵位空間表達」者；426 條中之首例即 `eh`（孤立 ㄝ）。此類詞幹**一律忽略**——不列 E3、不列 W1、不進 `stemToCode`，僅記於 `stats.ignoredStems` 並印一行 INFO。理由（事主）：打不出孤立 ㄝ 不困擾雙拼用戶，蓋漢語拼音不教孤立 ㄝ，母語者只識「整體認讀音節」（`ye`／`yue` 等之寫法）；`acknowledgedUnreachable` 則保留給 schema 作者**明示**「本可表達而刻意不表達」之音節（兩者語義不同，不可混用）。
- **重碼不視為 ERROR 之理由**：雙拼不減少重碼（同碼本即多音節）；且組字器原生支援「同位置多讀音」。再者，若將重碼列為 ERROR，則**GB/T 34947-2017 方案本身即不合格**（實測 5 組；微軟亦 3 組），違背「內建方案得為合法 schema」之要求。
- **`autochopPolicy` 之宣告與本版之能力**（內建之再令）：該欄位係 schema 之明示欄位，惟本版**只實作 `.disabled`**。schema 若宣告他形，載入發 **W7** 而**不拒收**（其餘 425 條之編解碼仍應可用），執行時一律以 `.disabled` 之語義運行，並於報告及（P302 之）設定界面明示「尚未支援」——**不得靜默降級**（不支援之行為若默默生效，考場習慣與肌肉記憶即失真，見 §5.1）。
- **標題之解析**（事主指示）：每份 schema 具 `rawTitle` 與 `localizedTitle` 兩欄。解析序為①精確標籤（如 `zh-Hant`）→②同語言同文字系統、去區域（`zh-Hant-TW`→`zh-Hant`）→③語言主標籤（`zh`）→④`en`→⑤`rawTitle`（E7 保證其非空）。比對時標籤大小寫不拘、`_` 與 `-` 等價（故 ICU 形 `zh_Hant` 亦命中同一鍵）。**鍵之形制**：以 **Apple（BCP-47）形**為準——`-` 連接、如 `zh-Hant`；ICU 之 `_` 形因等價而可用，惟非本設計之書寫形。region variant 不寫（唯音之 App UI L10n 不需之），故內建僅備 `en` 與 `zh-Hant`；撰寫時一律以 Apple 之形為優先。**為何不交主機之 i18n 機制**：方案係**使用者自備之 JSON**，其標題不可能預先落於 app 之 `.strings`；故標題必須隨 schema 自持，內建兩方案亦然（內建之 `localizedTitle` 即其範例）。API：`public func title(forLocaleTag tag: String) -> String`——參數為**語系標籤字串**、非 Foundation 之 `Locale`：本模組之公開面須與 Tekkon 各語言版（其他 workspace 之 C++／C# 版）所共有的純值語彙相容，不引入 Swift Foundation 型別；比對全以字串進行（`_` 與 `-` 等價之規則亦即為 Apple 之 `zh-Hant_TW` 一類標籤而設），主機側自可取 `Locale.current.identifier` 後傳入。
- **`rawID` 與持久化**（事主明示）：`rawID` 係 schema 之 DNS 名唯一 ID（§3.2）；校驗見 E9。持久化以 `UserDefaults` 承載**一筆**——自備 schema 存其 JSON 原文，內建者只存 `rawID`（§3.2、§5.2）。
- **碼長一律 2**（收束）：`minCodeLength`／`codeLength`／`overrides` 之碼皆須為 2，否則 **E8** 整份拒收（先前之 W6 廢止）。理由（事主逐字）：「雙拼本來就是二碼，不用把事情搞複雜。那種『以 a 代替 aa』的方法更像是一個通用邏輯方案。」
- **自由槽位**：GB/T 34947-2017 26 鍵定長二碼共 676 槽，實用 420 ⇒ 256 槽空閒；微軟 27 鍵（含 `;`）共 729 槽，實用 422 ⇒ 307 槽空閒。此等槽位可供 `overrides` 為重碼詞幹（如 `lvan`）另行分流。內建方案**不**如此做（忠於原方案之定義），但機制須存在，供 user-supplied schema 使用。

### 3.4 翻譯器 `DualpinTranslator`

#### 3.4.1 狀態機

- 狀態：`idle` ／ `pending(firstKey: Character)`。
- `ingest(key:) -> Action`：
 - 鍵 ∉ `alphabet` ⇒ `.passthrough`（呼叫者交既有路徑處理；聲調鍵、空白、Enter、退格皆屬此類）。
 - `idle` ⇒ 轉 `pending`，回 `.bufferOnly`（僅更新顯示，不碰組音區）。
 - `pending(f)` ⇒ 組碼 `f`＋本鍵；查表（`overrides` → `finals` 生成之表 → `aliases`）：
 - 命中 ⇒ 回 `.translate(stems: [String])`（重碼時多於一條），轉 `idle`。
 - 未命中（兩鍵不成任何碼）⇒ 回 `.invalid(firstKey:secondKey:)`；其處置為**直接 Beep ＋ Drop**（架構再定之三；事主逐字：「無效兩鍵序之提示形為直接 Beep ＋ Drop 掉這兩個無效 keyHit」）——**兩鍵皆丟棄**（首鍵不 passthrough、次鍵不另作新碼之首鍵）、**不進組音區**（否則即複現 `q → ㄑ` 之形態）、**不落字面**；響鈴由打字機側呼叫 `SessionHost.shared.soundBuzz()`（`Sources/LibVanguard/Session/SessionHost.swift:94` 之既有 beep 掛鉤；macOS 側接 `NSSound.buzz()`，先例見 `Sources/LibVanguard/Session/InputSession_Delegates.swift:175`）——**Arimitsu 自身不發聲**（該模組 OS-neutral、不得引 AppKit）。`autochopPolicy` 所管者係另一事（未滿碼之殘段，§3.2）；`.backtrackToShorterReading`／`.prefixCandidates`／`.passThroughVerbatim` 三形皆列為後續（§4.8）。（此條即「不支援 autochop」在翻譯器側之全部語義。）
- `flush()`：於確認鍵、方向鍵、輸入法切換、游標移動時清 `pending`。
- **不得**以「兩鍵之間有延時」為由自動確認：雙拼之兩鍵為一次輸入之兩個半，非兩次輸入。

#### 3.4.2 與 Composer 之三條協定

1. **直通集**：聲調鍵（數字、空白、`mapArayuruPinyinIntonation` 所覆蓋者）與非 `alphabet` 鍵一律直通，**絕不可**進翻譯器——因為 `receiveKey(fromScalar:)` 在拼音側係**先判聲調**再累積羅馬字，若聲調鍵被譯為詞幹則聲調無處附掛。
2. **提交時機**：收到新碼之首鍵且組音區已非空 ⇒ 先固化前一音節（步驟同 `performPinyinAutoChopIfNeeded:251-286`：取 `phonabetKeyForQuery(pronounceableOnly: true)`＋`makeToneInsensitiveVariants`＋`hasGrams` 過濾 → `assembler.insertKey(...)` → `commitOverflownComposition`／`retrievePOMSuggestions(apply:)`），再 `replacePinyinBuffer(with: 本碼之首候選)`。**不得**動用 `pinyinAutoChopResult`（其前提為 `intonation.isEmpty`，而雙拼允許聲調於固化前附掛）。
3. **重碼**：本碼之首候選進組音區（供顯示與聲調附掛），其餘候選暫存於翻譯器；凡固化該未決音節之處，皆須把暫存候選一併併入讀音鍵陣列。實際需接之處有二：`Typewriter_BPMFFullMatch.swift:251-258`（自動切分路徑）與 `:135 readingKeyForQuery`（確認鍵路徑）。附掛聲調時，對每個候選詞幹以其注音＋當前聲調符號構成單鍵（非五態桶）。
4. **不做之事**：不碰 `allowsExtendedRomajiBuffer`（其為全拼簡拼流而設，會把 `pinyinAutoChopResult` 之貪婪邏輯拉回來）；不改 `romajiBuffer` 之長度上限（雙拼碼恆 2、永不觸發上限）。狂打之 `furiousTrail` 則**要**記（架構定調⑦，見 §3.5）。
5. **處理序（收束①，逐字）**：「Arimitsu 將原始雙拼訊號翻譯成漢語拼音聲介韻 Stem String、然後塞給 Tekkon 處理、之後直接就是輸入法既有的漢語拼音打字處理流程。」⇒ 翻譯器之輸出邊界即「**無調、完整聲介韻之漢語拼音詞幹**」（即 `mapHanyuPinyin` 之 key）；一經 `replacePinyinBuffer` 入組音區，其後一切皆既有拼音流程，Arimitsu 不再介入（除重碼候選之暫存，第 3 條）。
6. **序**：兩碼之鍵入必依聲介韻調之宏觀順序（§2）⇒ 翻譯器只認「首鍵屬聲母槽、次鍵屬韻母槽」之組合，反向者屬無效序（處置見 §3.4.1）。

#### 3.4.3 顯示

- 完整碼 → 詞幹 → 進組音區 ⇒ 組音區之顯示由 `Composer.getInlineCompositionForDisplay(isHanyuPinyin:)` 免費給出（漢拼，含 ü 還原）。
- `pending` 首鍵之顯示：**一律顯示原始鍵**（已收束；事主逐字：「pending 首鍵之顯示：一律顯示原始鍵」，理由逐字：「雙拼用戶往往都沒學過注音」）。⇒ **不**借用 `PinyinTrie.zhuyinReadings(forPinyinFragment:)` 作注音前綴擴張之提示（該路徑把非音節之物暴露於顯示，對雙拼用戶亦無實益）。顯示僅更新組字區之 pending 提示，**不進組音區**（§3.9）。

#### 3.4.4 讀音鍵之形態與 auto-chop

- **插入 assembler 之讀音恆為「無聲調、完整聲介韻」之注音**（收束②）：「完整」＝聲母／介音／韻母皆已定（雙拼碼本身即定長完成之音節，不存在只打了半個音節之狀態）；「無聲調」＝讀音鍵不帶聲調符——`Tekkon.makeToneInsensitiveVariants`（`Tekkon_Utilities.swift:12-22`）之五態桶係**查詢**用（確認鍵路徑），非插入用。若使用者於固化前按了聲調鍵，該聲調係附掛於組音區（`composer.intonation`），固化時以「該候選之注音＋當前聲調符」構成單鍵（§3.4.2 第 3 條）；重碼時同一位置容多讀音（`Homa.PossibleKey.multipleKeys`）。
- **最長碼長恆為 2 ⇒ 一般無須 auto-chop**（收束③）：每次 `replacePinyinBuffer` 皆承載**恰好一個**完整音節，組音區不會出現多音節之拼音流 ⇒ `pinyinAutoChopResult`（`Tekkon_SyllableComposer.swift:276-302`）與 `performPinyinAutoChopIfNeeded`（`Typewriter_BPMFFullMatch.swift:226`）於雙拼下自然 no-op（既不必停用，亦**不得倚賴**）。切分之職權在翻譯器：碼長已知、逐鍵抵達，收滿即知本音節已完整。
- **例外：連續音節之斷句**（事主舉「阿爸」a-ba）。此例之鍵流為 阿＝`aa`（零聲母固定鍵 `a`＋韻母 `a`，§3.6）緊接 爸＝`ba`，即 `a a b a`；若把兩音節之詞幹併成一串（`aba`）交既有拼音路徑，即須回頭倚賴 greedy chop 才能再切開。**故翻譯器一律逐音節 `replacePinyinBuffer`、永不併串**；斷句所需之知識（碼長、零聲母政策、各前綴是否已成碼）皆可由 schema 靜態導出——此即事主所謂「或許可以根據具體的雙拼 schema 自動判定」。內建 GB/T 34947-2017 與微軟皆為定長二碼，故不觸發回溯；且**碼長一律 2 已裁**（收束：雙拼本來就是二碼）⇒ 宣告 `minCodeLength = 1` 之 schema 逕以 **E8** 拒收（§3.3），翻譯器**不存在**「遇第三鍵回溯」之態——本項原列為後續，自此註銷（參考實作之實測見 §4.6–§4.7）。**就內建方案言之，其真陷阱不在切分而在「碼之首鍵」**：阿＝`aa` 完成後組音區存詞幹 `a`，此時爸之首鍵 `b` **絕不可**落進組音區（否則累積成非法之 `ab`）——故前控者必須把 `alphabet` 內之鍵**連碼之首鍵一併自收**，並於此時固化前一音節（§3.4.2 第 2 條、§3.9）。

### 3.5 打字機側接線

- **新增 `DualpinTypewriter`**（與 `CassetteTypewriter` 同形），惟**其職責僅止於雙拼辨識**（架構再定④）：認鍵、維持 `pending`、於碼完成時把組音區重建為該詞幹；其餘一切（聲調附掛、確認組字、候選窗、狂打、退格、標點）一律**轉交** `BPMFFullMatchTypewriter` 打工（見 §3.9）。理由：①雙拼之按鍵語義與 `receiveKey(fromString:)` 之「逐字累積」根本不同；②`pending` 與無效序須有持有人；③不使 BPMF 打字機再長一層條件。
- **分派判準**：`MandarinParser` 恆為 `.ofHanyuPinyin`（架構定調③）⇒ `TypingMode` 增設 **`.DualPin`** case（已收束；事主逐字：「TypingMode Enum 需要加上 DualPin」），並於 `handleComposition`（`InputHandler_HandleComposition.swift:13`）之 `switch typingMode` **直接分派**（該 `switch` 無 `default`，編譯器強制補全，§1.2）；再以「schema 已載入且校驗通過 ∧ 非磁帶 ∧ 非 SCPC」作生效閘（下條）。增設範圍＝case 一枚＋`i18n:TypingMode.i18nKey4InlineModeHint.*` 一條（§6.1）。
- **生效閘（gating）**：`composer.parser == .ofHanyuPinyin` ∧ schema 可用 ∧ `!prefs.cassetteEnabled` ∧ `!prefs.useSCPCTypingMode`。狂打**不**關；`allowsExtendedRomajiBuffer = false`。
- **`;` 之實況（架構定調⑧訂正）**：`;` 係 keycode **41**（`kVK_ANSI_Semicolon = 0x29`），**不是**符號選單鍵。符號選單鍵係**波浪符號鍵** `` ` ``／`~`：`Sources/Shared/KBEvent.swift:284` 之 `kSymbolMenuPhysicalKeyIntl = 50`（＝Apple SDK `HIToolbox/…/Events.h:243` 之 `kVK_ANSI_Grave = 0x32`），JIS 側為同檔 `:305` 之 `kSymbolMenuPhysicalKeyJIS = 94`（＝`Events.h:325` 之 `kVK_JIS_Underscore = 0x5E`）。`;` 不在 `InputHandler_TriageInput.swift:95` 之 `switch keyCodeType` 任何 case 內 ⇒ 必然抵達同檔 `:341` 之 `handleComposition` ⇒ **微軟方案之 11 條 `ing` 系音節於打字機層即可直接消化、無須觸及 triage**（詳 §3.7）。
- **狂打（Furious）＝拼音狂打之語義**（架構再定③）：`DualpinTypewriter` 屬狂打支援範圍（架構定調⑦）⇒ 不因磁帶而關；且因本設計於碼完成後即把組音區交回既有拼音路徑，**拼音狂打之諸義自動同義**——無調確認組字、copilot 候選窗、就地選字、`furiousTrail` 與 `resegmentFuriousTrailIfNeeded()` 皆照舊（`prefs.furiousTypingEnabled4Pinyin` 預設 true）。唯一須自決者係「**單鍵簡拼**」：雙拼之首鍵是**碼前綴**、不是拼音詞幹前綴 ⇒ 不得交 `pinyinAutoChopResult`。**已裁定暫時擱置、暫不實作**（收束未裁定 6；事主逐字：「雙拼下之『單鍵簡拼』暫時擱置、暫時不實作。回頭可以在 Arimitsu 套件裡面補上相關輔助工具來實作」）——日後若補，於 `Arimitsu` 套件內另立輔助工具（以 schema 之碼前綴集合自算），不動打字機。
- 排列註冊：`InputHandler_CoreProtocol.swift:461-477` 無須改動（雙拼之組音區即 `.ofHanyuPinyin` 排列），惟生效時須確保 `composer.parser == .ofHanyuPinyin`。

### 3.6 第二內建方案：GB/T 34947-2017 之權威碼表

來源有二，本 Phase 已逐項覆核其一致：①zh.wikipedia「雙拼」條目之 GB/T 34947-2017 碼表模板（`tmp/wiki_raw_208.80.154.224.txt:307-337`）；②`macroxue/shuangpin` 之 `evaluator.js` 之 `schemes` 表內之 GB/T 條目（`tmp/sp_evaluator.js`）。GB/T 34947-2017 之權威描述係**逐鍵表**（微軟之權威描述則是 Rime 之尾綴改寫鏈，見 §3.8）；本 schema 以「聲母表＋韻母表＋零聲母政策」表達之。

三項要點：

- **零聲母鍵＝`a`**：Wikipedia 該條目 `:18` 明言其零聲母鍵固定為 `A`；`evaluator.js` 之 `A=0` 同義。⇒ `zeroInitial ＝ .fixedKey("a")`。
- **`alphabet` 不含 `;`**：Wikipedia 模板之 `semicolon` 欄留空、`evaluator.js` 之映射無 `;` ⇒ `keyInterception ＝ .none`（其 alphabet 不含主機保留鍵）。
- **`un` 兼表 `ün`、`uan` 兼表 `üan`**（Wikipedia 該條目之注記）⇒ `lvan`（ㄌㄩㄢ，Tekkon 表內之非標準音節）藉 `uan→w` 得碼 `lw`。

**表 A：逐鍵對照（26 鍵；仿 Wikipedia `{{Shuangpin}}` 之形）**

| 鍵 | 聲母 | 韻母 | 鍵 | 聲母 | 韻母 |
| --- | --- | --- | --- | --- | --- |
| `a` | （零聲母） | `a` | `n` | `n` | `iang`／`uang` |
| `b` | `b` | `ei` | `o` | | `o`／`uo` |
| `c` | `c` | `ao` | `p` | `p` | `ou` |
| `d` | `d` | `ian` | `q` | `q` | `ia`／`ua` |
| `e` | | `e` | `r` | `r` | `en` |
| `f` | `f` | `an` | `s` | `s` | `iong`／`ong` |
| `g` | `g` | `ang` | `t` | `t` | `ie` |
| `h` | `h` | `eng` | `u` | `sh` | `u` |
| `i` | `ch` | `i` | `v` | `zh` | `v`／`ui` |
| `j` | `j` | `ing` | `w` | `w` | `uan` |
| `k` | `k` | `ai` | `x` | `x` | `ue`／`ve` |
| `l` | `l` | `er`／`in` | `y` | `y` | `iu`／`uai` |
| `m` | `m` | `iao` | `z` | `z` | `un` |

（`v` 一格兼兩職：作聲母表 `zh`、作韻母表 `ü` 與 `ui`——此即各方案皆以 `V` 鍵承 `zh` 之故。`a` 之聲母欄作零聲母鍵，其韻母欄另有單韻母 `a`。）

**表 B：零聲母（12 條；一律以 `a` 為前綴）**：`a→aa`／`ai→ak`／`an→af`／`ang→ag`／`ao→ac`／`e→ae`／`ei→ab`／`en→ar`／`eng→ah`／`er→al`／`o→ao`／`ou→ap`；**`eh`（ㄝ）無兩鍵碼**（其韻不入表 A 之韻母欄、亦非單韻母 ⇒ 僅三鍵形，見 §4.4）。

**樣本**：`zhong→vs`／`guo→go`／`ren→rr`／`min→ml`／`shuang→un`／`wei→wb`／`ruan→rw`／`ju→ju`／`jue→jx`／`jun→jz`／`juan→jw`／`yu→yu`／`yuan→yw`／`yun→yz`／`yue→yx`／`nv→nv`／`nve→nx`／`lv→lv`／`lve→lx`／`gui→gv`／`nui→nv`／`ye→ye`／`yi→yi`／`wu→wu`／`wo→wo`／`weng→wh`／`ying→yj`／`ding→dj`／`zhuang→vn`／`chuang→in`／`er→al`／`ang→ag`／`o→ao`／`ou→ap`。

**實測統計**（`tmp/gbt17_final.py`）：426 條詞幹中 **425 條可得兩鍵碼**（`eh` 除外）；**相異碼 420 條**；**26 鍵全用、`;` 完全未用**；**重碼 5 組**＝`kn{kiang, kuang}`／`ky{kiu, kuai}`／`lo{lo, luo}`／`lw{luan, lvan}`／`nv{nui, nv}`。內建 schema 之 `acknowledgedUnreachable = ["eh"]`。

**與微軟之對照**：GB/T 34947-2017 之重碼（5 組）多於微軟（3 組），因 GB/T 34947-2017 把 `üan`／`ün`／`ü` 分別併入 `uan`／`un`／`ui` 之鍵（`lw`／`nv` 兩組即由此而生）；微軟則令 `ü` 獨佔 `y`、`üe` 併入 `t`，代價是 `ing` 落在 `;`。兩者皆為「425／426、`eh` 不可得」。

### 3.7 主機保留鍵之攔截：schema 之一等欄位

- **按鍵碼訂正（架構定調⑧）**：本稿初版誤以 `;` 為符號選單鍵。實則——`;` 係 keycode **41**（Apple SDK `HIToolbox.framework/…/Events.h:236` 之 `kVK_ANSI_Semicolon = 0x29`）；**符號選單鍵係波浪符號鍵**，`Sources/Shared/KBEvent.swift:284` 之 `case kSymbolMenuPhysicalKeyIntl = 50`＝`Events.h:243` 之 `kVK_ANSI_Grave = 0x32`，JIS 側係同檔 `:305` 之 `case kSymbolMenuPhysicalKeyJIS = 94`＝`Events.h:325` 之 `kVK_JIS_Underscore = 0x5E`（該鍵在 JIS 之落字為 `_`）。事主另註：波浪符號鍵在 JIS 鍵盤走羊字鍵（`kVK_JIS_Yen = 0x5D`＝93，同檔 `:304` 之 `kYen`）、在其餘鍵盤走 tilde 鍵。出處清單見 `KBEvent.swift:275-276`（eastmanreference 之 AppleScript key codes 頁與 HIToolbox 之 `Events.h`）。
- **機制**：波浪符號鍵於**第一層按鍵碼分診**即被取走——`Sources/LibVanguard/InputHandler/InputHandler_TriageInput.swift:144-152` 之 `case .kSymbolMenuPhysicalKeyIntl, .kSymbolMenuPhysicalKeyJIS:` 依 `input.commonKeyModifierFlags` 分派：`[]` → `handlePunctuationList(alternative: false, isJIS:)`（叫出 `State.ofSymbolTable(node: CandidateNode.root)`）；`[.option, .shift]` → 同函式 `alternative: true`（插 `_punctuation_list`）；`.option` → `revolveTypingMethod()`（以上三者見 `InputHandler_HandleStates.swift:1766` 起）。此分診在 `triageByKeyCode()`（同檔 `:95`）之內，**早於** `triageByState` 之 `handleComposition`（同檔 `:341`）。同層另有主機保留鍵：漢音鍵盤符號熱鍵（同檔 `:337`，判準 `"¥\\".contains(x)`）、九宮格數字鍵、功能鍵、`Caps Lock` 等。
- **故 `;` 於主機無衝突**：`;` 不在 `triageByKeyCode()` 之任何 case 內、亦不屬上列保留鍵 ⇒ 雙拼生效時直接進 `handleComposition` ⇒ 微軟方案之 11 條 `ing` 系音節（`bing`／`ding`／`jing`／`ling`／`ming`／`ning`／`ping`／`qing`／`ting`／`xing`／`ying`，即 `b;`／`d;`／`j;`／`l;`／`m;`／`n;`／`p;`／`q;`／`t;`／`x;`／`y;`）**無須任何 triage 手術**。（`Sources/LibVanguard/SymbolMenuDefaultData.swift:127` 之 `";": ["；", "ㄤ", "﹔", "：", "︰", "﹕"]` 係符號表**資料樹**（`CandidateNode.defaultSymbolRoot`）裡的一個 node，與按鍵攔截無涉；全倉亦無任何 `SymbolMenuDefaultData` 識別名之引用。）
- **何時才需攔截**：唯有方案之 `alphabet` 含**主機保留鍵**（波浪符號鍵、`¥`／`\`、`Option` 系組合）時，方須於 `InputHandler_TriageInput.swift:144` 之分支**之前**諮詢 Arimitsu（如 `if dualpinClaimsKey(input) { return handleComposition(input: input) }`）。GB/T 34947-2017 與微軟之 `alphabet` 皆不含該等鍵 ⇒ 兩者之 `keyInterception` 皆為 `.none`。
- **事主改令之要求如何落地**：其原文以「分號鍵的攔截與否」為題，前提（`;` 即符號選單鍵）已由 架構定調 訂正；然「哪些鍵須先於主機處理序交 Arimitsu」仍屬方案之性質，故 `DualpinParser.keyInterception` 保留為 schema 之一等欄位，三態為 `.none`（預設）／`.explicit(Set<Character>)`／`.schemeAlphabet`，動機例改為波浪符號鍵（見 §3.2、§3.3 之 E6／W3）。
- 微軟方案之完整推導（Rime `algebra` 逐條直譯）見 §3.8；426 條逐條碼表見附錄 B。

### 3.8 內建預設方案：微軟雙拼（兼 user-supplied schema 之參考實作）

（本節保留微軟方案之完整推導——它既是**內建預設方案**，亦是「使用者自備 schema」之參考實作（§0 內建之再令）；GB/T 34947-2017 為第二內建，見 §3.6。）

來源：Rime `double_pinyin_mspy`（佛振；`double_pinyin_mspy.schema.yaml`）。其 `algebra` 之 `xform` 鏈係**對漢語拼音拼寫作尾綴改寫**（非音位正規化），下表即其逐條直譯。

**表 A：聲母 → 鍵（23 條）**

| 聲母 | 鍵 | 聲母 | 鍵 | 聲母 | 鍵 | 聲母 | 鍵 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `zh` | `v` | `ch` | `i` | `sh` | `u` | `b` | `b` |
| `p` | `p` | `m` | `m` | `f` | `f` | `d` | `d` |
| `t` | `t` | `n` | `n` | `l` | `l` | `g` | `g` |
| `k` | `k` | `h` | `h` | `j` | `j` | `q` | `q` |
| `x` | `x` | `r` | `r` | `z` | `z` | `c` | `c` |
| `s` | `s` | `y` | `y` | `w` | `w` | | |

**表 B：尾綴 → 鍵（25 條；查表為全等匹配、與書寫次序無涉）**

| 序 | 尾綴 | 鍵 | 序 | 尾綴 | 鍵 | 序 | 尾綴 | 鍵 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `iu` | `q` | 10 | `ong`／`iong` | `s` | 19 | `ai` | `l` |
| 2 | `ia`／`ua` | `w` | 11 | `iang`／`uang` | `d` | 20 | `ei` | `z` |
| 3 | `er` | `r` | 12 | `en` | `f` | 21 | `ie` | `x` |
| 4 | `uan`／`van` | `r` | 13 | `eng` | `g` | 22 | `ui` | `v` |
| 5 | `ue`／`ve` | `t` | 14 | `ang` | `h` | 23 | `ou` | `b` |
| 6 | `v` | `y` | 15 | `ian` | `m` | 24 | `in` | `n` |
| 7 | `uai` | `y` | 16 | `an` | `j` | 25 | `ing` | `;` |
| 8 | `uo` | `o` | 17 | `iao` | `c` | | | |
| 9 | `un`／`vn` | `p` | 18 | `ao` | `k` | | | |

**表 C：單韻母（5 條）**：`a→a`／`o→o`／`e→e`／`i→i`／`u→u`。

**表 D：零聲母（13 條；一律以 `o` 為前綴）**：`a→oa`／`ai→ol`／`an→oj`／`ang→oh`／`ao→ok`／`e→oe`／`ei→oz`／`en→of`／`eng→og`／`er→or`／`o→oo`／`ou→ob`；**`eh`（ㄝ）無兩鍵碼**（其韻不入表 B、亦非單韻母 ⇒ 僅 `oeh`／`eeh` 之三鍵形）。

**樣本**：`zhong→vs`／`guo→go`／`ren→rf`／`min→mn`／`shuang→ud`／`wei→wz`／`ruan→rr`／`ju→ju`／`jue→jt`／`jun→jp`／`juan→jr`／`yu→yu`／`yuan→yr`／`yun→yp`／`yue→yt`／`nv→ny`／`nve→nt`／`lv→ly`／`lve→lt`／`gui→gv`／`nui→nv`／`gue→gt`／`ye→ye`／`yi→yi`／`wu→wu`／`wo→wo`／`weng→wg`／`ying→y;`／`ding→d;`。

**實測統計**：426 條詞幹中 **425 條可得兩鍵碼**（`eh` 除外）；**相異碼 422 條**；27 鍵全用（`a`–`z` 與 `;` 各至少一次）；**重碼 3 組**＝`kd{kiang, kuang}`／`lo{lo, luo}`／`lr{luan, lvan}`。微軟 schema 之 `acknowledgedUnreachable = ["eh"]`。

**可選別名（Rime 接受、非必要）**：`derive/^([jqxy])u$/$1v/` 所生之 `jv`／`qv`／`xv`／`yv`，與 `derive/T$/V/` 所生之 `jv`（決）／`qv`／`xv`／`nv`（虐）／`lv`（略）。**內建表不採用**（每條別名皆須有測試）；機制上以 `aliases` 支援。

### 3.9 打字機之套接（typewriter composition）：實查與結論

事主之提問（架構再定④）：`DualpinTypewriter` 能否只作雙拼辨識，令 `Typewriter_BPMFFullMatch`（暨日後之 `CassetteTypewriter`）為其打工？**結論：可以，且庫內已有同形先例。**

| 契約 | 事實 |
| --- | --- |
| `TypewriterProtocol.handle`（`Sources/LibVanguard/Typewriter/TypewriterProtocol.swift:17`） | 回 `Bool?`＝「本鍵是否已被輸入法攔截處理」；`nil` 為未處理。 |
| 套接之先例 | `Typewriter_MixedAlphanumerical.swift:24-28`：自身 `handle` 內具現 `BPMFFullMatchTypewriter(handler)` 並 `return typewriter.handle(input)`；即「同一 handler、多型別接力」（`:195-212`、`:249-263` 同形）。 |
| 可注入面 | `Typewriter_BPMFFullMatch.swift:23` `onLexiconMatchFailure`、`:26` `isToneOverrideEnabled`、`:29` `isLeadingIntonationAccepted`（皆 `public var`）＝呼叫方得以收束被套接者之行為。 |
| 狀態之共享 | 各打字機僅持有 `handler`；組音槽、組字器（`assembler`）、`session` 皆在其上 ⇒ 套接不須搬運狀態。 |
| 分派之優先序 | `InputHandler_HandleComposition.swift:28-44`：中英混輸層先於 `switch typingMode` ⇒ 新層須置於 `case .vChewingFactory` 臂內。 |

**建議形（前控式）**：`DualpinTypewriter.handle(input)` 之序為——

1. 鍵 ∈ `alphabet` ∧ 生效閘成立 ⇒ 本型別自收（交 `DualpinTranslator.ingest`）；碼完成時固化前一未決音節，並 `composer.replacePinyinBuffer(with: 詞幹)`；回 `true`。
2. 其餘一切鍵（聲調鍵、空白、Enter、退格、數字、標點、修飾鍵、非 `alphabet` 之字母）⇒ `return BPMFFullMatchTypewriter(handler).handle(input)`。因組音區已在拼音模式且為完整詞幹，`composeReadingIfReady`（`:354`）／`handleStandaloneIntonation`（`:436`）／`performPinyinAutoChopIfNeeded`（`:226`）皆照舊生效。
3. `pending` 首鍵之顯示由本型別自行 `session.switchState` 生成，**不進組音區**（避免複現 `q → ㄑ` 之形態）。

**`CassetteTypewriter` 之日後參與**：當 schema 之 `codeLength > 2` 且確定要做「磁帶供第三／四碼」時，步驟 1 於收滿兩鍵後把**殘餘鍵**轉交 `CassetteTypewriter(handler)` 取碼、取回碼後再 `replacePinyinBuffer`。本 Phase 不動磁帶（架構定調⑤），故僅記此接口位置。

**否決之替代形**：於 `Typewriter_BPMFFullMatch.consumeReadingInputIfNeeded`（`:172`）內插一段雙拼前置判斷（初稿之備選）——代價是 BPMF 打字機再長一層條件、且雙拼之 `pending` 與無效序無持有人；既有前控先例可循，不採。

## 4. 實證（本 Phase 所跑之探針）

### 4.1 探針與產物

| 產物（皆在倉庫根之 `tmp/`） | 用途 |
| --- | --- |
| `wiki_raw_208.80.154.224.txt` | zh.wikipedia「雙拼」條目之 raw wikitext（20,785 bytes／464 行；內含 11 個方案之 `{{Shuangpin}}` 鍵位模板，含**GB/T 34947-2017**、微軟、小鶴） |
| `sp_evaluator.js` | `macroxue/shuangpin` 之評測器（32,886 bytes；`:schemes` 含**GB/T 34947-2017**之獨立定義） |
| `gbt17_final.py`／`gbt17_table.json` | GB/T 34947-2017 編碼器與 426 條詞幹 → 碼（§3.6、附錄 A 之資料源） |
| `mspy.yaml` | Rime 微軟雙拼 schema 原檔（3,233 bytes；`curl -sSL raw.githubusercontent.com/rime/rime-double-pinyin/master/double_pinyin_mspy.schema.yaml`） |
| `mspy_final.py`／`mspy_table.json` | 微軟之直譯編碼器與 426 條詞幹 → 碼（§3.8、附錄 B 之資料源） |
| `mspy_probe.py`／`mspy_probe2.py`／`mspy_chart.py`／`mspy_chart2.py` | 早期探針（保留其教訓，見 §4.5） |
| `zrm.yaml`／`flypy.yaml` | Rime `double_pinyin.schema.yaml`（自然碼，`schema_id: double_pinyin`）與 `double_pinyin_flypy.schema.yaml`（小鶴）原檔（3,074／3,125 bytes）。 |
| `zrm_probe.py` | 忠實實作二者之 algebra 並於 426 條詞幹上求解碼集（§4.7）。 |
| `wiki_ziranma_198.35.26.96.txt` | zh.wikipedia「自然碼」條目之 raw wikitext（4,628 bytes／71 行；`{{IME|周志农|1989 年|双拼加形}}`、第 3 行「自然码采用双拼方案，**每种汉语拼音固定有两个字母表示**」、首行 `{{distinguish|自然輸入法}}`）。 |
| `flypy_wv.md` | 小鶴官方〈谈谈双拼零声母方案〉等〈相关文章〉之 md 原檔（35,677 bytes；`curl -sSL https://flypy.cc/help/wv.md`）。 |

外部來源之取用：`zh.wikipedia.org` 於本機 DNS 回偽位址（198.18.0.x），`web_fetch` 一律以 `URL hostname … resolves to a non-public IP address` 拒收（連線逾時 75 秒）；以 `curl --resolve zh.wikipedia.org:443:208.80.154.224 …&action=raw` 即得 HTTP 200（同法可解 `*.wikipedia.org` 各站）。百度百科仍回 `HTTP 403`。⇒ GB/T 34947-2017 之兩來源皆可稽核，無須倚賴二手轉述。

### 4.2 結論

1. **兩方案之覆蓋率皆為 425／426**：唯一不可得兩鍵碼者為 `eh`（ㄝ）——其為 Tekkon 表內之非標準音節（`欸`）；GB/T 34947-2017 與微軟皆然（彼等之韻母表皆無 `eh`，亦非單韻母）。⇒ 列 W1 acknowledged。
2. **重碼處置**：GB/T 34947-2017 5 組（`kn{kiang, kuang}`／`ky{kiu, kuai}`／`lo{lo, luo}`／`lw{luan, lvan}`／`nv{nui, nv}`）、微軟 3 組（`kd{kiang, kuang}`／`lo{lo, luo}`／`lr{luan, lvan}`）。其中 `lo`／`luo` 與 `nui`／`nv` 兩組係**兩個真實音節之真重碼**；其餘各組之一方為 426 條內之非標準條目（`kiang`／`kiu`／`lvan`，Tekkon 表之遺留）。⇒ 重碼係架構級議題，惟既有之「同位置多讀音鍵」（`Homa.Assembler.insertKey(_ key: [String])`）已足承載。
3. **鍵集**：GB/T 34947-2017 僅用 26 字母；微軟用滿 27 鍵，其中 `;` 承 `ing`（11 條）。**`;` 並非主機保留鍵**（keycode 41；符號選單鍵係波浪符號鍵，見 §3.7）⇒ 兩方案在 triage 層皆零改動。
4. **定長性**：兩方案於 425 條上皆為 2 鍵 ⇒ 切分 O(1)、無前綴歧義（`eh` 之三鍵為唯一例外，且已 acknowledged）。微軟之尾綴鏈雖有「首中即用」之序，實際命中皆為 2 鍵。
5. **`eh` 之外，`lvan` 為第二個敏感點**：GB/T 34947-2017 靠「`uan` 兼表 `üan`」之注記始得 `lw`；若嚴格按韻母表而不承認 üan 之合併，`lvan` 亦不可得（424／426）。微軟則以 `[uv]an→r` 之別名直接涵蓋。

### 4.3 亂序雙拼之不可能性（證明級）

模型上之根因先於算術：雙拼係對漢語拼音之二次編碼，鍵入順序仍按聲介韻調之宏觀順序（架構定調④引 Rime 作者佛振）⇒ **亂序不屬雙拼之定義**，並非「暫不可行」。以下是其算術旁證。

設鍵集為 $K$（GB/T 34947-2017 之 $|K| = 26$；微軟之 $|K| = 27$，多一枚 `;`）：

- 有序、可重複（雙拼之真實模型）：$|K|^2 = 26^2 = 676$（GB/T 34947-2017）／$27^2 = 729$（微軟）$\ge 426$ ⇒ 可行。
- **順序無關**（並擊或亂序串擊）：可重對之數為 $\binom{|K|+1}{2} = \binom{27}{2} = 351$（GB/T 34947-2017）／$\binom{28}{2} = 378$（微軟）$< 426$ ⇒ **不可行**。
- 順序無關之嚴格形（每鍵至多用一次）：$\binom{|K|}{2} = \binom{26}{2} = 325$（GB/T 34947-2017）／$\binom{27}{2} = 351$（微軟）$< 426$ ⇒ 更不可行。

根因：注音之每一鍵本身即完整之 phonabet，故其鍵空間與音節空間同構；雙拼之單鍵不是。此結論亦與既有算術相符（以 26 元素得 `C(27,2) = 351`；微軟含 `;` 共 27 鍵，故可重對為 `C(28,2) = 378`，**兩者皆 < 426，結論不變**）。⇒ 校驗器可於**載入時**靜態回報此理由（非啟發式）。

### 4.4 四項邊界（對 schema 之意義）

1. **ü 之拼寫**：表內 n/l 後作 `v`（含 `v` 之 key 僅 `lv`／`lvan`／`lve`／`nv`／`nve`），j/q/x/y 後作 `u`。schema 若寫 `nü` 會被拒 ⇒ 載入時正規化＋WARNING。
2. **成音節鼻音**（`m`／`n`／`ng`／`hm`／`hng`）：皆不在 426 內 ⇒ 呣／嗯／哼類字無合法雙拼碼；schema 若編碼之，翻譯必落空 ⇒ **WARNING 而非 ERROR**（否則誤傷一切主流方案）。
3. **最長拼寫 6**（`shuang`／`zhuang`）恰等於 `romajiBuffer` 之上限 6；雙拼碼恆 2 ⇒ 永不觸發。惟**簡拼流**（`allowsExtendedRomajiBuffer`）會觸發 ⇒ 雙拼生效時該開關一律關。
4. **單字母 key 僅 `a`／`e`／`o`**（`mapHanyuPinyin` 內），歷史上 `q → ㄑ` 之條目已刪；`Tests/TekkonTests/TekkonTests_Pinyin.swift` 之 `testSingleLetterEntriesAreRealSyllablesOnly` 即其防線。schema 宣告單字母碼時須警惕同一 bug 形態。

### 4.5 踩坑（逐條）

1. `mapHanyuPinyin` 係 internal ⇒ 跨 target 不可讀；Arimitsu 須經 `mapZhuyinPinyin!.keys`。
2. `SyllableIndex.allReadings` 係**注音**而非拼音詞幹（誤用即整盤校驗錯位）。
3. 直呼 `Composer.receiveSequence` 不同步 `romajiBuffer` ⇒ 必用 `replacePinyinBuffer(with:)`。
4. `receiveKey(fromScalar:)` 之拼音分支先判聲調 ⇒ 聲調鍵不可進翻譯器（否則聲調無處附掛、且會被當聲母吃掉）。
5. 首輪探針 `mspy_chart.py` 曾把 j/q/x 後之 `u` 正規化為 ü（`ju` 誤編為 `jy`）。**mspy 之規則係對拼寫作尾綴改寫，不可作音位正規化**——此為本次最易犯之錯。
6. **按鍵碼之連鎖誤判**（架構定調⑧訂正）：`;` 係 keycode **41**（`kVK_ANSI_Semicolon`），符號選單鍵係**波浪符號鍵**（keycode 50 ＝ `kVK_ANSI_Grave`）。原稿見 `kSymbolMenuPhysicalKeyIntl = 50` 而逕以之為「ANSI 分號」，遂誤判微軟之 `;` 須於 triage 攔截。教訓：**按鍵碼以 Apple SDK 之 `HIToolbox/…/Events.h` 為準，不任由 Swift 常數名反推**（見 §3.7）。
7. `eh` 無兩鍵碼（`oeh`／`eeh` 皆三鍵）。
8. 早期探針對不可分解之 `eh` 以「取末字元」拙劣回退，得出偽重碼 `oh{ang, eh}` ⇒ 已作廢，不得引用。
9. Wikipedia 之 `action=raw` 取用須帶 `--resolve`：本機 DNS 對 `*.wikipedia.org` 回 198.18.0.x 之非公網位址，`web_fetch` 與裸 `curl` 皆不可用（詳 §4.1）。
10. GB/T 34947-2017 之 üan 須靠「`uan` 兼表 `üan`」之注記，否則 `lvan` 不可得（424／426）；此類「方案級韻母合併」不可由 426 條之表反推，須以原文注記為憑。

### 4.6 參考實作之行為：`aba` 之切分與「一鍵碼」（事主實測）

事主來訊（逐字）：「**macOS 內建的雙拼直接敲 `aba` 是會被拆成 `a ba` 來讀的。**」暨 該圖歸屬附註（逐字）：「（剛才那個擷圖是小鶴雙拼。）」附圖（`image.png`，600×172）：組字區作 `a ba ba ba ba ua ua ua`（`u` 即 `sh` 之鍵、`ua` 即 `sha`），候選 1「阿巴巴巴巴莎莎莎」恰 8 格與之逐格對應，候選 2「啊」、3「阿爸」則係其前 1／2 格之局部組字。

- **實測所證**：該實作容許**單鍵成碼**——一鍵 `a` 即為「阿」之完整音節，故 3 鍵之 `aba` 讀作 阿＋爸。若一律貪婪二二成對，`aba` 即得 `ab`＋`a`，而 `ab` 在該方案不成音節（其韻母鍵 `B` ＝ `in`）⇒ 切分必須能「一鍵成節」並回溯。
- **同一方案、兩種實作、兩種碼長**：Rime 之 `double_pinyin_flypy.schema.yaml:58` 作 `xform/^([aoe])(ng)?$/$1$1$2/` ⇒ 阿＝`aa`（**兩鍵**）；而 Apple 之實作則以一鍵 `a` 成阿。⇒ **碼長與零聲母之處置不得由方案名推斷，必須由 schema 明確宣告**（§3.2 之 `minCodeLength` 與 `ZeroInitialPolicy` 即為此；事主收束③「這或許可以根據具體的雙拼 schema 自動判定」同旨）。此為「執行時動態回溯（Apple）」與「載入時靜態判定（本設計）」之實益分界：前者可容忍未宣告之變體，後者要求宣告，換得確定性與可校驗性。
- **對內建方案之影響**：GB/T 34947-2017 之零聲母固定鍵 `a` ⇒ 阿＝`aa`（§3.6 表 B）⇒ 兩內建方案皆不生此歧義（GB/T 34947-2017 之零聲母固定鍵 `a`；微軟之 `o`）；此問只存於 user-supplied schema。
- **事主追報（逐字）**：「macOS 內建的雙拼在選用自然碼時也 autochop。我猜可能是 apple 的方案在偵測到 `ab` 不成音的時候就 autochop 了。」⇒ 自然碼之 `ab` 非其任何碼（其 `B`＝`ou`，§4.7），卻同樣切作 `a`＋`ba`。故 Apple 之切分**既非貪婪二二成對、亦非一律要求滿 `minCodeLength` 鍵**，而是「**已累積之鍵序列不成碼（且不成前綴）時，回溯一鍵並固化为獨立音節**」——此為「一鍵成節」之另一面。對本設計之意義：`minCodeLength` 僅宣告**最短合法碼**，尚不足以描述此行為；若日後支援（§5.2 第 10 條），切分演算法須同時涵蓋「無效碼回溯」，本 Phase 仍維持「先只支援定長二碼」之建議。事主另將查考其他輸入法於此之預設行為後彙報（本文暫記為待補）。
- **小鶴之引用界線**：小鶴雙拼現因智財權待釐清而暫緩（§2 第 6 條），故本節只引其**行為**與 Rime 實作中之**單行規則**為證，**不登錄亦不生成其碼表**。
- **未竟**：本 Phase 未能在系統內尋得 Apple 用以承載雙拼佈局之資料——`/System/Library/Input Methods/SCIM.app/Contents/`（含 `PlugIns/SCIM_Extension.appex`）僅見字串 `isPinyinOrShuangpinSimplified`、`Pinyin.keylayout`、`Wubihua.keylayout`，無明文對照表；`CoreChineseEngine.framework` 與 `TextInputCJK.framework` 之 Resources 亦無。其佈局之權威來源待考（或為隨系統下載之資產）。**故本節只引其行為、不引其表。**

### 4.7 零聲母方案之三族與「一鍵碼」之實測歸零

- **三族（兩份獨立來源同旨）**：Wikipedia〈双拼〉之 raw wikitext 第 17–21 行分「固定一個字母做零聲母＋韻母所在鍵」（微軟／智能ABC／紫光／搜狗＝固定 `o`；**GB/T 34947-2017＝固定 `a`**）與「以韻母首字母為零聲母＋韻母所在鍵」（拼音加加），並記第三種＝第二種但「**雙字母的零聲母拼音保留全拼輸入方式**」。小鶴官方〈谈谈双拼零声母方案〉（`tmp/flypy_wv.md:79-107`）同旨，且列出零聲母音節恰 12 條：`a an ai ao ang e en ei er eng o ou`。微軟拼音（Win11）之方案編輯器**即以該三族為零聲母模式之三態枚舉**（標籤逐字見 §4.8），係此分類之獨立旁證。
- **自然碼之署名與定義**：發明人**周志農**，1989 年（Wikipedia「自然碼」條目之 `{{IME|周志农|1989 年|双拼加形}}`，`tmp/wiki_ziranma_198.35.26.96.txt`），其第 3 行並明言「自然码采用双拼方案，**每种汉语拼音固定有两个字母表示**」——即**每音恆兩鍵**，為 `minCodeLength = 2` 之權威表述；該條目首行 `{{distinguish|自然輸入法}}` 亦提醒勿與 iQTech 之「自然輸入法」混為一談（不同產品）。
- **自然碼與小鶴之實測**（`tmp/zrm_probe.py`，對 426 條詞幹忠實套用 Rime 之 algebra）：
  - **自然碼**（`double_pinyin.schema.yaml`，`name: 自然碼雙拼`）：426 條全得碼，**相異碼 432 且長度全為 2**；單韻母零聲母作 `aa`／`oo`／`ee`，`ang`→`ah`／`eng`→`eg`，雙字母零聲母照全拼（`ai`／`an`）**另**收衍生形（`al`／`aj`，Rime 之 `derive`）；重碼 4 組＝`kd{kiang,kuang}`／`lo{lo,luo}`／`lr{luan,lvan}`／`nv{nui,nv}`。
  - **小鶴**（`double_pinyin_flypy.schema.yaml`）：**相異碼 433＝432 條 2 鍵＋1 條 3 鍵**，同樣無一鍵碼；該 3 鍵者為非標準詞幹 `lvan`→`lvj`；重碼 3 組＝`kl{kiang,kuang}`／`lo{lo,luo}`／`nv{nui,nv}`。
  - ⇒ **`minCodeLength = 1` 於 GB/T 34947-2017、微軟、自然碼、小鶴四者皆不成立**；單韻母零聲母作雙字母（`aa`／`oo`／`ee`）乃此四族之共識。
- **與 §4.6 之關係**：「一鍵 `a` 成阿」既非自然碼亦非小鶴之聲明碼長，而是 **Apple 實作之容忍**（以 `a` 為可成節之前綴）。其表不可讀取，故僅記載行為——此正是「`minCodeLength` 必須由 schema 宣告、不得由方案名推斷」之最強論據。**本 Phase 已據此裁定：一律只承認 2**（§5.2）。
- **對 P302 之建議（已成交集）**：只支援定長二碼；載入時遇 `minCodeLength ≠ 2`／`codeLength ≠ 2`／`overrides` 之非二鍵碼即**拒收整份**（§3.3 之 **E8**）。回溯切分自此註銷——「以 `a` 代替 `aa`」屬**通用邏輯方案**之範疇、非雙拼（§5.2）。

### 4.8 他牌輸入法之 autochop 行為（事主調查；Apple／微信／搜狗／微軟拼音／谷歌拼音已測）

事主來訊（逐字；微信輸入法之特性）：「已知微信輸入法有這個 autochop 特性。我準備測試一下搜狗。」

- **微信輸入法之附圖（與上則併讀；待事主確認方案名）**：組字區作 `a'ba'ba'ba'ba`——**以 `'` 明示音節界**（§4.6 之 Apple 實作不作此顯示）；候選 1「愛爸爸爸爸」、2「阿巴巴巴巴」、3「啊叭叭叭叭」。
- **可讀出之兩項觀察**：①**切分與 Apple 同族**——`a` 之後遇 `b` 使 `ab` 不成碼，即回溯一鍵固化為 `a`，再以 `ba` 起新音節（`a`｜`ba`×4）；②**首段 `a` 之候選橫跨「單字母音節」（啊＝`a`）與「其前綴之雙字母音節」（愛＝`ai`）**，此係**前綴延伸**（未滿碼者仍列候選），與「一鍵成節」不同層。
- **模式已確認：雙拼（事主第二輪來訊逐字：「雙拼。行為與 apple 一致。考慮到搜狗拼音輸入法的開發也被騰訊接管的緣故，我估計搜狗也有類似行為。但我還得親自安裝確認。」）**⇒ 該圖之候選橫跨即非全拼之前綴比對，而是雙拼引擎自身之「未滿碼成節＋前綴延伸」並存。所選方案名未知（待補，不影響行為歸類）。
- **微信輸入法之第二圖**：組字區作 `ba'a'ba'ba'•••`（`'` 逐段標界；段序為 `ba`｜`a`｜`ba`×n），候選 1「把愛爸爸爸爸爸爸爸爸爸爸爸爸爸爸」、候選 2「巴阿•••」。⇒ ①首段 `ba` 直接成「把」；②次段 `a` 之候選同時含「愛」（`ai` 之前綴延伸）與「阿」（`aa` 之前綴或單鍵成節）——**同一段內兩種政策並存**；③段落界以 `'` 明示，與 微信實測①（圖） 一致。
- **調查矩陣（兩維；五牌已測）**：A＝「未滿碼之鍵序列不成碼時，是否回溯一鍵固化」；B＝「不成碼之殘段，是否回溯為**較短之合法音節**（或列為候選）；抑或回退為**原文 ASCII**」。**Apple＝A ✅／B ✅**（單鍵成阿）；**微信輸入法（雙拼）＝A ✅／B ✅**（且 B 之表現為前綴延伸、以 `'` 標界）；**搜狗拼音＝A ✅／B ❌**（殘段以原文 ASCII 輸出，見下）；**微軟拼音（Win11）＝A ❌**（其內建方案一並不切，殘段逕留原文，見下）；**谷歌拼音＝A ❌**（同微軟，見下）。⇒ 合觀（五牌）：Apple／微信／搜狗**切**，微軟拼音與谷歌拼音**不切** ⇒ autochop 係**各家實作之選配**、非雙拼輸入法之共通義務；且切者之間對殘段之思維亦三樣。**內建之再令即據此定為「先不做 autochop」**（`.disabled`），故本版之目標不是取勝於某一行為，而是**與考場環境一致**（§5.1）。
- **搜狗拼音（已測）**：事主來訊（逐字）：「搜狗拼音的雙拼也有 autochop，但似乎比 apple 還有 wetype 而言更弱智。」兩張附圖：
  - 圖 A：組字區 `a'b'a'ba'ba'ba'ba'ba`（段序 `a`｜`b`｜`a`｜`ba`×5），候選 1「**aba**爸爸爸爸」（`aba` 以橙字示為**原文 ASCII**）、2「叭叭叭叭叭」、3「阿爸巴巴爸」。
  - 圖 B：組字區 `b'a'a'b'a'ba'ba`（段序 `b`｜`a`｜`a`｜`b`｜`a`｜`ba`｜`ba`），候選 1「**Baaba**爸爸」（原文 ASCII）、2「拿吧拿吧」、3「把愛」。
  - **可讀出者**：①仍有 autochop（`'` 逐段標界）⇒ A ✅；②**不成音之單鍵段不作讀音解讀**，而係以原文 ASCII 輸出（候選 1 即此形態）⇒ B ❌；③其「A」之實作形態為「**插入界＋原文回退**」，非「回溯為較短之合法音節」。
- **微軟拼音（Win11）之方案自訂畫面（事主實測）**：事主來訊（逐字）：「微軟拼音預設的方案都沒有這個特性。」暨「另外，這幾個擷圖是微軟拼音(Win11)內建的方案自訂畫面（有些畫面有 dropdown picker 展開條目）。」擷圖五張（`image.png`×5）為「新增配置」對話框。讀出者：①**A ❌**——內建方案一並不切，未滿碼之鍵序列逕留原樣；②資料模型為**逐條「音節 → 按鍵」配對**（音節清單含 `ch`／`sh`／`zh` 與 `ai`／`an`／`ang`／`ao`／`ei`／`en`／`eng`／`er`／`ia`…，未設定者作 `-`）；③零聲母政策作**三態枚舉**，標籤逐字為「固定式零子音」／「母音第一個字元的按鍵」／「母音第一個字元的按鍵（2 個字元的母音是完整拼音）」——與 §4.7 之三族一一對應；④`範本` 三選＝「（無）」／「智慧型 ABC」／「自然代碼」；⑤零聲母鍵之可選清單含 `;` 與 A／E／I／O／U／V，`按鍵` 之可選清單為 A／E／I／O／U／V；⑥`名稱` 上限 32 個字元；⑦預覽區逐鍵顯示該鍵所承之聲母與韻母。⇒ 微軟自家即以表式模型與三態枚舉實作（§3.2 之同構對照）；其**不切**亦說明「未滿碼殘段」之處置須由 schema 或使用者明示，不能期望引擎代勞。**第二輪擷圖三張**（事主來訊逐字：「有關於微軟拼音原廠雙拼schema「不支援autochop」的證據。」）：圖 1 組字區 `abababa` ⇒ 候選 1 即**原文** `abababa`（不成碼之整串逕留原文、無任何切分）；圖 2 組字區 `ba'ababababab` ⇒ 段首 `ba` 成「吧」、其後原文（`'` 係**手工**分節，非自動回溯）；圖 3 為其設定之「雙拼音」區，讀出「**自動展開至完整拼音＝關閉**」「**超級縮寫拼音＝關閉**」兩枚開關，`雙拼音配置` 之預設項為「自然代碼」；同圖 Notepad 中 `ba'ba'ba'ba'ba` ⇒ 候選「八八八八八」等——每段 `ba` 本即完整碼，故無須切分。⇒ 微軟把「展開至完整拼音」（＝未滿碼之補全／殘段之處置）與「超級縮寫拼音」（＝單鍵簡拼）**兩者皆作預設關閉之開關**，即此類行為在微軟係**使用者可宣告之選配**，與本稿「`minCodeLength` 與殘段政策交由 schema 宣告」之主張同向（§5.2 第 8、10 條）。
- **谷歌拼音（2007 版；A ❌，事主供圖）**：組字區作 `巴巴爸爸ababababa`（前段已固化＋後段未成碼之殘段），其前編輯列逐段示 `ba ba ba ba ababababa`（未成碼者以原文留於列中）、候選 1「巴巴爸爸」。⇒ 不成碼之殘段**逕留原文**，既不回溯為較短之合法音節、亦不列前綴候選——與微軟拼音同；其 `ba` 段能成節係**碼本即完整**（`ba`＝ㄅㄚ）、非 autochop。此即考場環境所預裝之輸入法（§0 內建之再令），故其行為之等同性為 P302 之驗收項（§6.2）。
- **不可借道之現成機制（事主訂正）**：殘段之「原文回退」**不可**由中英混輸層承擔——`isMixedAlphanumericalLayerInEffect`（`vChewing-LibVanguard/Sources/LibVanguard/InputHandler/InputHandler_MixedAlnumConfig.swift:99-102`）之閘為 `currentTypingMethod == .vChewingFactory && typingMode != .cassette && !composer.isPinyinMode && prefs.mixedAlphanumericalEnabled`（**該層僅為注音服務**），且 `MixedAlphanumericalTypewriter` 對拼音模式逕轉 `BPMFFullMatchTypewriter`（`InputHandler_HandleComposition.swift:32-33` 之註）⇒ 雙拼（`composer.isPinyinMode == true`）不在該層之服務範圍，若採「回退原文」須由 `DualpinTypewriter` 自持或另闢路徑（§5.2 第 10 條）。
- **待補**：①微信所用之雙拼方案名。②其餘他牌（如有；微軟拼音已測、其餘待補）。

## 5. 已知界線與待裁定

### 5.1 界線

- 亂序雙拼不在雙拼之模型內（§2、§4.3）。
- 成音節鼻音無碼可編（WARNING）。
- 雙拼不減少重碼；重碼之裁定權在 Homa 之 DP 與語言模型，不在翻譯層。
- `eh` 係 DIPE（內建兩方案皆靜默忽略之，§3.3）；GB/T 34947-2017 之 `lvan` 則倚賴其原文注記「`uan` 同時表示 `uan` 和 `üan`」始得 `lw`。
- 雙拼與磁帶、逐字選字（SCPC）之並存語義未定 ⇒ 生效時關閉該二者；**狂打則在支援範圍內**（架構定調⑦），其細節見 §3.5（單鍵簡拼已擱置）。
- **碼長一律 2**：`minCodeLength = 1` 之 schema 拒收（E8）；「以 `a` 代替 `aa`」屬通用邏輯方案、不屬雙拼（§5.2）。
- **單鍵簡拼不實作**（暫時擱置）：雙拼之首鍵係碼前綴，不得走全拼簡拼之路（§3.5）；日後得於 Arimitsu 套件內補輔助工具。
- **Arimitsu 係 `LibVanguard` 之直屬 SubTarget**（獨立 target、由 `LibVanguard` 直接依賴；架構再定之三）：Tekkon 側之改動僅一枚公開 API ⇒ 其跨語言（C++／C#）遷移不受本 Phase 牽動（§1.4、§3.1）。
- 主機保留鍵（波浪符號鍵、`¥`／`\` 等）之攔截須落在 `InputHandler_TriageInput.swift:144` 之前；惟 GB/T 34947-2017 與微軟皆不觸及該等鍵 ⇒ 本 Phase 之設計於 triage 層**零改動**（§3.7）。
- 雙拼×磁帶之聯立不在本 Phase（§3.5、§5.3）。
- **考場一致性**（內建之再令）：中國內地之電腦化公共考試（法考等）只允許「微軟雙拼方案」、禁止考生改動輸入法設置，且考場預裝者為 2007 版谷歌拼音 ⇒ 唯音之微軟雙拼內建不得只求覆蓋率（425／426），尚須**碼表逐條等同**該方案、**行為等同**（不 autochop——兩者皆然；不打聲調——雙拼用戶之常態）。P302 之驗收須含「以考場側樣本交叉驗證內建表」（§6.2）。

### 5.2 待事主裁定

**已裁定（架構再定、收束）**：

- **Arimitsu 係 `LibVanguard` 之直屬 SubTarget**（架構再定之二＋之三；**取代**前此之「同 target」）⇒ `internal` 不再可直讀；Arimitsu 獨立成一 target、單元測試全部獨立（`Tests/LibVanguardTests/Arimitsu/`）、`DefaultIsolation` 暫定 `MainActor`；Tekkon 另立**公開 API** 供其取 426 條詞幹（首選 `public static var allHanyuPinyinStems: [String]`）。目的：Tekkon 之改動量縮至最小、便於 TekkonWorkspace 之跨語言遷移（§1.4、§3.1）。
- **雙拼狂打承襲拼音狂打之涵義** ⇒ 生效時不關狂打；碼完成後組音區交回既有拼音路徑，狂打諸義自動同義（§3.5）；「單鍵簡拼」一項則已裁為暫時擱置（見下）。
- **DIPE 得忽略**（收束①）：`eh` 等「漢語拼音有、雙拼無」之表達一律靜默略過，不報 E3／W1（§3.3）。
- **處理序**（收束①）：雙拼訊號 → 漢語拼音聲介韻 stem string → Tekkon → 既有拼音流程；翻譯器之輸出邊界即無調之完整詞幹（§3.4.2 第 5 條）。
- **讀音鍵之形態**（收束②）：插入 assembler 者恆為無聲調、完整聲介韻之注音（§3.4.4）。
- **碼長與 auto-chop**（收束③）：最長碼恆 2、逐音節 `replacePinyinBuffer`、不倚賴 `pinyinAutoChopResult`；連續音節之斷句由 schema 靜態判定（「阿爸」例，§3.4.4）。
- **無效兩鍵序 ⇒ 直接 Beep ＋ Drop**（架構再定之三）：兩鍵皆丟棄、不進組音區、不落字面，僅由打字機側 `SessionHost.shared.soundBuzz()` 響鈴（§3.4.1）——此即原列於「未裁定」之「無效兩鍵序之提示形」，該項自此移出。
- **不做 autochop**（內建之再令）：未滿碼之殘段一律 `.disabled`——不回溯、不猜、不成碼之鍵序列不進組音區；該行為仍以 `autochopPolicy` 之欄位明示（本版唯一實作之 case），他形列為後續（§3.2、§3.4.1、§4.8）。
- **手術範圍**：現階段集中於 `LibVanguard`；`WebConfigAssistant` 之處置不急、不在本 Phase。`vChewing-macOS` 若加選項則落「鍵盤設定」畫面；具體呈現方式與**雙拼方案之 persistence** 仍待商榷——太複雜時或於 `SettingsUI`／`SettingsCocoa` 另開一頁（下「未裁定」2）。
- **內建者同時保留兩方案**（事主明示）：微軟雙拼為預設、**GB/T 34947-2017 亦內建**，由使用者二擇；兩者皆為下述 JSON 格式之 decodable schema。
- **標題隨 schema 自持**（事主明示，已收束）：每份 schema 具 `rawTitle` 與 `localizedTitle`，解析序＝精確標籤 → 去區域 → 語言主標籤 → `en` → `rawTitle`（查表以**字串標籤**進行，`title(forLocaleTag:)`；公開面不引 Foundation 型別；鍵依 Apple 形 `zh-Hant`）；內建兩方案之預設值＝微軟〔`rawTitle`＝「微软双拼」；`en`＝Microsoft Dualpin；`zh-Hant`＝微軟雙拼〕、GB/T 34947-2017〔`rawTitle`＝`GBT17`；四語系 `localizedTitle` 皆「GB/T 34947-2017」〕（代碼層仍以 `MSPY`／`GBT17` 指涉）。
- **內建之打包形態**（事主明示，已收束）：**不作 per-scheme Swift 型別與檔案、亦不作 bundled `.json` 資源**；方案之 JSON 原文以三引號字串塊固化於 `DualpinParser.swift` 檔尾，與使用者自備檔走同一 decoder（§3.1）。
- **`pending` 首鍵一律顯示原始鍵**（已收束）：事主逐字：「pending 首鍵之顯示：一律顯示原始鍵」，理由逐字：「雙拼用戶往往都沒學過注音」⇒ 不作注音前綴擴張提示（§3.4.3）。
- **`TypingMode` 增設 `.DualPin`**（已收束）：直接於 `switch typingMode` 分派；生效閘另計（§3.5）。
- **雙拼下之「單鍵簡拼」暫時擱置**（已收束）：暫不實作；日後可於 Arimitsu 套件內補輔助工具（§3.5）。
- **碼長一律 2**（已收束）：`minCodeLength = 1` 之 schema **先拒絕載入**（E8）；「以 `a` 代替 `aa`」屬通用邏輯方案、非雙拼之範疇（§3.3、§4.7、§5.1）。
- **RawID ＝ DNS 名**（事主明示）：每份 schema 以 DNS 名作唯一 ID（`dualPin.Microsoft`／`dualPin.GBT17` 等）；校驗見 E9、用途見 §3.2。
- **持久化＝`UserDefaults`、僅一筆**（事主明示，已收束）：自備 schema 存其 JSON 原文；所選為原廠方案時只存其 `rawID`。**無多方案庫**；macOS 側界面之歸屬仍待（下「未裁定」2）。

**未裁定**（架構再定之三後收為二項）：

1. `keyInterception` 之預設值（建議 `.none`）。
2. macOS 側設定界面之歸屬（置於「鍵盤設定」內 vs 另開 Settings 頁）——persistence 之**形態**已定（`UserDefaults` 單筆、見上「已裁定」），所餘者僅界面落點（§6.1）。

> 小鶴雙拼自架構再定之三起**不在未裁定之列**（事主明示「先不討論」）；無效兩鍵序之提示形則已裁定（Beep ＋ Drop，見上「已裁定」）。

### 5.3 未動

- `Tekkon.Composer` 本體、`MandarinParser` 之既有 17 案（架構定調③明示不改）、磁帶模式、SCPC、狂打之既有語義。
- `InputHandler_TypingMode.swift:15` 之註釋（現況已漂移，P302 施工時回檢）。
- `vChewing-macOS` 側之設定界面（`SettingsUI`／`SettingsCocoa`）與 `WebConfigAssistant`：本 Phase 不動，亦不預設其形態（架構再定②）。
- **鏡像與鏡照**：`vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard`（與本倉逐位元組同源之鏡像）與 `_DedicatedComponentRepos/TekkonWorkspace` 之三倉皆不在本 Phase（亦不在 P302 手術範圍）——依 2026-09-28／P268 之職責邊界，鏡照不由本倉手術 session 兼任（§6.4）。

## 6. 後續（P302 建議手術範圍）

### 6.1 落點

| 落點 | 檔 | 規模 |
| --- | --- | --- |
| 新 target `Arimitsu`（`LibVanguard` 之**直屬 SubTarget**） | `Sources/LibVanguard/Arimitsu/DualpinParser.swift`、`Sources/LibVanguard/Arimitsu/DualpinTranslator.swift`＋`Package.swift` 暨 `Package@swift-5.10.swift`（兩份 target 定義；6.4 側帶 `defaultIsolation(MainActor.self)`） | 約 600–800 行 |
| **內建兩方案**（微軟雙拼〔預設〕、GB/T 34947-2017） | `Sources/LibVanguard/Arimitsu/DualpinParser.swift` **檔尾**之兩枚 JSON 字串塊（＋解碼所得之 `mspy`／`gbt17`） | 約 400 行（兩份 JSON 原文） |
| **Tekkon 公開 API**（拆 target 之最小改動） | `Sources/Tekkon/Tekkon_Constants.swift`（或 `Tekkon_SyllableIndex.swift`）：`public static var allHanyuPinyinStems: [String]` | 數行 |
| 打字機 | `Sources/LibVanguard/Typewriter/Typewriter_Dualpin.swift`（新） | 約 200 行 |
| 分派與生效閘 | `InputHandler_HandleComposition.swift:13-44`（`switch typingMode` 增 `.DualPin` case＋生效閘；`MandarinParser` 不動） | 數行 |
| 狂打對接 | `Typewriter_Dualpin.swift` 與既有 `furiousTrail`／`resegmentFuriousTrailIfNeeded()` | 數行 |
| 主機保留鍵之攔截 | `InputHandler_TriageInput.swift:144-152`（**僅當 schema 用波浪符號鍵等保留鍵時才需**；內建兩方案與谷歌拼音皆不需） | 數行 |
| 打字模式 | `InputHandler_TypingMode.swift`（新增 `.DualPin` case；已裁定） | 數行＋i18n |
| 偏好 | `Shared/Prefs*`（雙拼開關＋schema 選擇；`UserDefaults` 單筆、內建僅存 `rawID`） | 數行 |
| macOS 側設定（P302+） | 「鍵盤設定」畫面（`SettingsUI`）或另開一頁；`WebConfigAssistant` 不在本階段（架構再定②） | 待裁定 |
| 測試 | `Tests/LibVanguardTests/Arimitsu/`（**獨立之測試目標 `ArimitsuTests`**；`@MainActor`） | 約 300 行 |
| 文書 | 現行 Reqs 卷、`DevReqsHistory.md`、KnowledgeMemo 現況塊、UserGuide（四語系） | — |

### 6.2 驗證計畫

1. **Round-trip**：`MandarinParser.ofHanyuPinyin.mapZhuyinPinyin!.keys` 之 426 條中，425 條皆得兩鍵碼、且 `decode(encode($0)) == [$0]`（重碼組回集合）。**內建兩方案（微軟、GB/T 34947-2017）各跑一遍**；另各取一份等值之 user-supplied `.json` 檔跑同一組測試，確認內建原文即使用者格式之範例（§3.1）。
2. **快照**：微軟（內建預設）表逐條與 Rime 之 `algebra` 輸出比對（`mspy_final.py`），並**以考場側樣本（2007 版谷歌拼音之微軟雙拼）交叉驗證若干組**（§5.1）；GB/T 34947-2017（第二內建）表逐條與 Wikipedia 模板及 `evaluator.js` 之 `schemes` 表內之 GB/T 條目比對（`gbt17_final.py`）。兩者皆由**內建之 JSON 原文**解碼所得（§3.1），故亦覆蓋 decoder 本身。
3. **校驗器**：對 §3.3 之**九類 ERROR**（E1–E9）各造一個反例 schema，確認皆被拒。
4. **翻譯器**：狀態機（idle／pending／無效序／flush）、聲調直通、重碼多讀音；**無效序之驗收＝Beep ＋ Drop**（不打字、不進組音區、不落字面；響鈴經 `soundBuzz()` 掛鉤取得，測試以替換閉包計次）。
4b. **標題解析**：`title(forLocaleTag:)` 之五級 fallback 各造一例（`zh-Hant` 命中／`zh-Hant-TW` 去區域命中／僅 `zh`／僅 `en`／空 table ⇒ `rawTitle`），並驗 E7 與 W8；另驗 ICU 形 `zh_Hant` 之等價命中。
5. **整合**：兩鍵 → 詞幹 → 組音區顯示 → 聲調 → 確認鍵 → 組字結果；`;` 之 11 條音節（以微軟 schema 測：應於打字機層直接消化）；與磁帶／SCPC 之互斥，暨與狂打之並存（單鍵簡拼）。
6. **建置**：`make build510`（沙箱擋 SwiftPM 之 sandbox-exec，須補 `--disable-sandbox`）；暨基線測試不得退化；並確認**兩份 manifest**（tools 6.4 與 5.10 對位版）皆納入 `Arimitsu` 與 `ArimitsuTests`。
7. **按鍵碼覆核**：以 Apple SDK 之 `HIToolbox/…/Events.h` 覆核 `KBEvent.swift` 之 `kSymbolMenuPhysicalKeyIntl`（50）與 `kSymbolMenuPhysicalKeyJIS`（94），並確認 `;`（41）不被任何 triage case 取走（§3.7）。
8. **身分與持久化**：`rawID` 非 DNS 形／為空／與內建相衝皆被 E9 拒；`UserDefaults` 僅一筆（自備存 JSON 原文、原廠僅存 `rawID`），以 `rawID` 指名內建方案後可完整複現（§3.2、§5.2）。
9. **隔離**：`Tests/LibVanguardTests/Arimitsu/` 於 `@MainActor` 下運行（`DefaultIsolation` 暫定 `MainActor`），並驗自 MainActor 讀 Tekkon 之公開 API 無礙。
10. **套接（composition）**：`DualpinTypewriter` 對非自收之鍵須逐鍵與 BPMFFullMatch 之直呼等價（同一輸入序列下之組字結果、狀態與 `Bool?` 回值皆須一致）；並測「雙拼碼完成後之聲調／空白／Enter／退格」確由被套接者處理（§3.9）。

### 6.3 資料流

```
按鍵（字母；微軟另有 `;`）
  └─ InputHandler_HandleComposition.handleComposition
       └─（雙拼生效閘：schema 可用 ∧ 非磁帶 ∧ 非 SCPC）
            └─ DualpinTypewriter
                 ├─ 鍵 ∉ alphabet ⇒ 交既有 BPMF 路徑（聲調鍵、空白、Enter、退格）
                 ├─ 鍵 ∈ alphabet 但屬主機保留鍵且未列於 keyInterception ⇒ 交既有路徑
                 └─ 鍵 ∈ alphabet ⇒ DualpinTranslator.ingest
                      ├─ pending(first) ∧ 本鍵成完整碼 ⇒ [詞幹]（重碼時多條）
                      │    ├─ 固化前一未決音節（readingKey 陣列 ⇒ assembler.insertKey）
                      │    └─ composer.replacePinyinBuffer(with: 首候選)
                      ├─ idle ⇒ 記 pending（僅顯示；狂打時可即時簡拼固化）
                      └─ 無效序 ⇒ Beep ＋ Drop（兩鍵皆丟；§3.4.1）
                 └─（本型別不自收之任何鍵）⇒ return BPMFFullMatchTypewriter(handler).handle(input)
                      （聲調／空白／Enter／退格／候選窗／狂打皆由該型別照舊處理；§3.9）
                      （日後 codeLength > 2 時，殘餘鍵轉交 CassetteTypewriter 取第三／四碼）
```

### 6.4 施工序（P302 之提交紀律）

- **手術範圍限於 `vChewing-LibVanguard`**（架構再定之三；事主逐字：「P302 的手術範圍限制在 LibVanguard 內」）。
- **Tekkon 之改動獨立先行**（事主逐字：「Tekkon 相關的修改必須單獨獨立一個 Commit 先行遞交、其後才是 LibVanguard 的其他內容」）——此係 2026-09-28／P268 既有紀律之重申：凡動 `Sources/Tekkon/` 或 `Tests/TekkonTests/` 者，先以**獨立一筆** commit 遞交，**不得**與 LibVanguard 之其餘改動混筆。本倉之標題格式為 `Tekkon // <DirectConcernedNameSpace>: <WhatChangedInTheMember>.`（例：`Tekkon // Constants: Expose allHanyuPinyinStems.`）。
- 故 P302 之提交序為：**①** Tekkon 之公開 API（`allHanyuPinyinStems`，§1.4）；**②** LibVanguard 側之全部（Arimitsu target 與兩份 manifest、打字機、分派與生效閘、prefs、測試）。若最終改採既有公開途徑（即不新增 Tekkon API，§1.4 之「交叉核對」路徑），則第 ① 筆不存在。
- **鏡照不在本 session**：`vChewing-macOS/Packages/vChewing_OSNeutral_LibVanguard`（byte-sync 鏡像）與 `_DedicatedComponentRepos/TekkonWorkspace` 之三倉皆屬**鏡照**工作——依 P268 之職責邊界，本倉手術 session 之職責止於「正本乾淨、提交分離、並於交付報告指明哪些 commit 待鏡照」。

## 7. 附錄

### 附錄 A：GB/T 34947-2017（第二內建）之 426 條碼表

（由 `tmp/gbt17_final.py` 生成。`—` 表示無兩鍵碼；重碼格以 `*` 標示——`kn`／`ky`／`lo`／`lw`／`nv` 五組。）

| 詞幹 | 碼 | 詞幹 | 碼 | 詞幹 | 碼 | 詞幹 | 碼 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `a` | `aa` | `ai` | `ak` | `an` | `af` | `ang` | `ag` |
| `ao` | `ac` | `ba` | `ba` | `bai` | `bk` | `ban` | `bf` |
| `bang` | `bg` | `bao` | `bc` | `bei` | `bb` | `ben` | `br` |
| `beng` | `bh` | `bi` | `bi` | `bian` | `bd` | `biang` | `bn` |
| `biao` | `bm` | `bie` | `bt` | `bin` | `bl` | `bing` | `bj` |
| `bo` | `bo` | `bu` | `bu` | `ca` | `ca` | `cai` | `ck` |
| `can` | `cf` | `cang` | `cg` | `cao` | `cc` | `ce` | `ce` |
| `cei` | `cb` | `cen` | `cr` | `ceng` | `ch` | `cha` | `ia` |
| `chai` | `ik` | `chan` | `if` | `chang` | `ig` | `chao` | `ic` |
| `che` | `ie` | `chen` | `ir` | `cheng` | `ih` | `chi` | `ii` |
| `chong` | `is` | `chou` | `ip` | `chu` | `iu` | `chua` | `iq` |
| `chuai` | `iy` | `chuan` | `iw` | `chuang` | `in` | `chui` | `iv` |
| `chun` | `iz` | `chuo` | `io` | `ci` | `ci` | `cong` | `cs` |
| `cou` | `cp` | `cu` | `cu` | `cuan` | `cw` | `cui` | `cv` |
| `cun` | `cz` | `cuo` | `co` | `da` | `da` | `dai` | `dk` |
| `dan` | `df` | `dang` | `dg` | `dao` | `dc` | `de` | `de` |
| `dei` | `db` | `den` | `dr` | `deng` | `dh` | `di` | `di` |
| `dia` | `dq` | `dian` | `dd` | `diao` | `dm` | `die` | `dt` |
| `ding` | `dj` | `diu` | `dy` | `dong` | `ds` | `dou` | `dp` |
| `du` | `du` | `duan` | `dw` | `duang` | `dn` | `dui` | `dv` |
| `dun` | `dz` | `duo` | `do` | `e` | `ae` | `eh` | `—` |
| `ei` | `ab` | `en` | `ar` | `eng` | `ah` | `er` | `al` |
| `fa` | `fa` | `fan` | `ff` | `fang` | `fg` | `fei` | `fb` |
| `fen` | `fr` | `feng` | `fh` | `fiao` | `fm` | `fo` | `fo` |
| `fong` | `fs` | `fou` | `fp` | `fu` | `fu` | `ga` | `ga` |
| `gai` | `gk` | `gan` | `gf` | `gang` | `gg` | `gao` | `gc` |
| `ge` | `ge` | `gei` | `gb` | `gen` | `gr` | `geng` | `gh` |
| `gi` | `gi` | `giao` | `gm` | `gin` | `gl` | `gong` | `gs` |
| `gou` | `gp` | `gu` | `gu` | `gua` | `gq` | `guai` | `gy` |
| `guan` | `gw` | `guang` | `gn` | `gue` | `gx` | `gui` | `gv` |
| `gun` | `gz` | `guo` | `go` | `ha` | `ha` | `hai` | `hk` |
| `han` | `hf` | `hang` | `hg` | `hao` | `hc` | `he` | `he` |
| `hei` | `hb` | `hen` | `hr` | `heng` | `hh` | `hong` | `hs` |
| `hou` | `hp` | `hu` | `hu` | `hua` | `hq` | `huai` | `hy` |
| `huan` | `hw` | `huang` | `hn` | `hui` | `hv` | `hun` | `hz` |
| `huo` | `ho` | `ji` | `ji` | `jia` | `jq` | `jian` | `jd` |
| `jiang` | `jn` | `jiao` | `jm` | `jie` | `jt` | `jin` | `jl` |
| `jing` | `jj` | `jiong` | `js` | `jiu` | `jy` | `ju` | `ju` |
| `juan` | `jw` | `jue` | `jx` | `jun` | `jz` | `ka` | `ka` |
| `kai` | `kk` | `kan` | `kf` | `kang` | `kg` | `kao` | `kc` |
| `ke` | `ke` | `ken` | `kr` | `keng` | `kh` | `kiang` | `kn`\* |
| `kiu` | `ky`\* | `kong` | `ks` | `kou` | `kp` | `ku` | `ku` |
| `kua` | `kq` | `kuai` | `ky`\* | `kuan` | `kw` | `kuang` | `kn`\* |
| `kui` | `kv` | `kun` | `kz` | `kuo` | `ko` | `la` | `la` |
| `lai` | `lk` | `lan` | `lf` | `lang` | `lg` | `lao` | `lc` |
| `le` | `le` | `lei` | `lb` | `leng` | `lh` | `li` | `li` |
| `lia` | `lq` | `lian` | `ld` | `liang` | `ln` | `liao` | `lm` |
| `lie` | `lt` | `lin` | `ll` | `ling` | `lj` | `liu` | `ly` |
| `lo` | `lo`\* | `long` | `ls` | `lou` | `lp` | `lu` | `lu` |
| `luan` | `lw`\* | `lun` | `lz` | `luo` | `lo`\* | `lv` | `lv` |
| `lvan` | `lw`\* | `lve` | `lx` | `ma` | `ma` | `mai` | `mk` |
| `man` | `mf` | `mang` | `mg` | `mao` | `mc` | `me` | `me` |
| `mei` | `mb` | `men` | `mr` | `meng` | `mh` | `mi` | `mi` |
| `mian` | `md` | `miao` | `mm` | `mie` | `mt` | `min` | `ml` |
| `ming` | `mj` | `miu` | `my` | `mo` | `mo` | `mou` | `mp` |
| `mu` | `mu` | `na` | `na` | `nai` | `nk` | `nan` | `nf` |
| `nang` | `ng` | `nao` | `nc` | `ne` | `ne` | `nei` | `nb` |
| `nen` | `nr` | `neng` | `nh` | `ni` | `ni` | `nian` | `nd` |
| `niang` | `nn` | `niao` | `nm` | `nie` | `nt` | `nin` | `nl` |
| `ning` | `nj` | `niu` | `ny` | `nong` | `ns` | `nou` | `np` |
| `nu` | `nu` | `nuan` | `nw` | `nui` | `nv`\* | `nun` | `nz` |
| `nuo` | `no` | `nv` | `nv`\* | `nve` | `nx` | `o` | `ao` |
| `ou` | `ap` | `pa` | `pa` | `pai` | `pk` | `pan` | `pf` |
| `pang` | `pg` | `pao` | `pc` | `pei` | `pb` | `pen` | `pr` |
| `peng` | `ph` | `pi` | `pi` | `pia` | `pq` | `pian` | `pd` |
| `piao` | `pm` | `pie` | `pt` | `pin` | `pl` | `ping` | `pj` |
| `po` | `po` | `pou` | `pp` | `pu` | `pu` | `qi` | `qi` |
| `qia` | `qq` | `qian` | `qd` | `qiang` | `qn` | `qiao` | `qm` |
| `qie` | `qt` | `qin` | `ql` | `qing` | `qj` | `qiong` | `qs` |
| `qiu` | `qy` | `qu` | `qu` | `quan` | `qw` | `que` | `qx` |
| `qun` | `qz` | `ran` | `rf` | `rang` | `rg` | `rao` | `rc` |
| `re` | `re` | `ren` | `rr` | `reng` | `rh` | `ri` | `ri` |
| `rong` | `rs` | `rou` | `rp` | `ru` | `ru` | `ruan` | `rw` |
| `rui` | `rv` | `run` | `rz` | `ruo` | `ro` | `sa` | `sa` |
| `sai` | `sk` | `san` | `sf` | `sang` | `sg` | `sao` | `sc` |
| `se` | `se` | `sei` | `sb` | `sen` | `sr` | `seng` | `sh` |
| `sha` | `ua` | `shai` | `uk` | `shan` | `uf` | `shang` | `ug` |
| `shao` | `uc` | `she` | `ue` | `shei` | `ub` | `shen` | `ur` |
| `sheng` | `uh` | `shi` | `ui` | `shou` | `up` | `shu` | `uu` |
| `shua` | `uq` | `shuai` | `uy` | `shuan` | `uw` | `shuang` | `un` |
| `shui` | `uv` | `shun` | `uz` | `shuo` | `uo` | `si` | `si` |
| `song` | `ss` | `sou` | `sp` | `su` | `su` | `suan` | `sw` |
| `sui` | `sv` | `sun` | `sz` | `suo` | `so` | `ta` | `ta` |
| `tai` | `tk` | `tan` | `tf` | `tang` | `tg` | `tao` | `tc` |
| `te` | `te` | `teng` | `th` | `ti` | `ti` | `tian` | `td` |
| `tiao` | `tm` | `tie` | `tt` | `ting` | `tj` | `tong` | `ts` |
| `tou` | `tp` | `tu` | `tu` | `tuan` | `tw` | `tui` | `tv` |
| `tun` | `tz` | `tuo` | `to` | `wa` | `wa` | `wai` | `wk` |
| `wan` | `wf` | `wang` | `wg` | `wei` | `wb` | `wen` | `wr` |
| `weng` | `wh` | `wo` | `wo` | `wu` | `wu` | `xi` | `xi` |
| `xia` | `xq` | `xian` | `xd` | `xiang` | `xn` | `xiao` | `xm` |
| `xie` | `xt` | `xin` | `xl` | `xing` | `xj` | `xiong` | `xs` |
| `xiu` | `xy` | `xu` | `xu` | `xuan` | `xw` | `xue` | `xx` |
| `xun` | `xz` | `ya` | `ya` | `yai` | `yk` | `yan` | `yf` |
| `yang` | `yg` | `yao` | `yc` | `ye` | `ye` | `yi` | `yi` |
| `yin` | `yl` | `ying` | `yj` | `yo` | `yo` | `yong` | `ys` |
| `you` | `yp` | `yu` | `yu` | `yuan` | `yw` | `yue` | `yx` |
| `yun` | `yz` | `za` | `za` | `zai` | `zk` | `zan` | `zf` |
| `zang` | `zg` | `zao` | `zc` | `ze` | `ze` | `zei` | `zb` |
| `zen` | `zr` | `zeng` | `zh` | `zha` | `va` | `zhai` | `vk` |
| `zhan` | `vf` | `zhang` | `vg` | `zhao` | `vc` | `zhe` | `ve` |
| `zhei` | `vb` | `zhen` | `vr` | `zheng` | `vh` | `zhi` | `vi` |
| `zhong` | `vs` | `zhou` | `vp` | `zhu` | `vu` | `zhua` | `vq` |
| `zhuai` | `vy` | `zhuan` | `vw` | `zhuang` | `vn` | `zhui` | `vv` |
| `zhun` | `vz` | `zhuo` | `vo` | `zi` | `zi` | `zong` | `zs` |
| `zou` | `zp` | `zu` | `zu` | `zuan` | `zw` | `zui` | `zv` |
| `zun` | `zz` | `zuo` | `zo` | | | | |

### 附錄 B：微軟雙拼（內建預設）之 426 條碼表

（由 `tmp/mspy_final.py` 生成。`—` 表示無兩鍵碼；重碼格以 `*` 標示——`kd`／`lo`／`lr` 三組。）

| 詞幹 | 碼 | 詞幹 | 碼 | 詞幹 | 碼 | 詞幹 | 碼 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `a` | `oa` | `ai` | `ol` | `an` | `oj` | `ang` | `oh` |
| `ao` | `ok` | `ba` | `ba` | `bai` | `bl` | `ban` | `bj` |
| `bang` | `bh` | `bao` | `bk` | `bei` | `bz` | `ben` | `bf` |
| `beng` | `bg` | `bi` | `bi` | `bian` | `bm` | `biang` | `bd` |
| `biao` | `bc` | `bie` | `bx` | `bin` | `bn` | `bing` | `b;` |
| `bo` | `bo` | `bu` | `bu` | `ca` | `ca` | `cai` | `cl` |
| `can` | `cj` | `cang` | `ch` | `cao` | `ck` | `ce` | `ce` |
| `cei` | `cz` | `cen` | `cf` | `ceng` | `cg` | `cha` | `ia` |
| `chai` | `il` | `chan` | `ij` | `chang` | `ih` | `chao` | `ik` |
| `che` | `ie` | `chen` | `if` | `cheng` | `ig` | `chi` | `ii` |
| `chong` | `is` | `chou` | `ib` | `chu` | `iu` | `chua` | `iw` |
| `chuai` | `iy` | `chuan` | `ir` | `chuang` | `id` | `chui` | `iv` |
| `chun` | `ip` | `chuo` | `io` | `ci` | `ci` | `cong` | `cs` |
| `cou` | `cb` | `cu` | `cu` | `cuan` | `cr` | `cui` | `cv` |
| `cun` | `cp` | `cuo` | `co` | `da` | `da` | `dai` | `dl` |
| `dan` | `dj` | `dang` | `dh` | `dao` | `dk` | `de` | `de` |
| `dei` | `dz` | `den` | `df` | `deng` | `dg` | `di` | `di` |
| `dia` | `dw` | `dian` | `dm` | `diao` | `dc` | `die` | `dx` |
| `ding` | `d;` | `diu` | `dq` | `dong` | `ds` | `dou` | `db` |
| `du` | `du` | `duan` | `dr` | `duang` | `dd` | `dui` | `dv` |
| `dun` | `dp` | `duo` | `do` | `e` | `oe` | `eh` | `—` |
| `ei` | `oz` | `en` | `of` | `eng` | `og` | `er` | `or` |
| `fa` | `fa` | `fan` | `fj` | `fang` | `fh` | `fei` | `fz` |
| `fen` | `ff` | `feng` | `fg` | `fiao` | `fc` | `fo` | `fo` |
| `fong` | `fs` | `fou` | `fb` | `fu` | `fu` | `ga` | `ga` |
| `gai` | `gl` | `gan` | `gj` | `gang` | `gh` | `gao` | `gk` |
| `ge` | `ge` | `gei` | `gz` | `gen` | `gf` | `geng` | `gg` |
| `gi` | `gi` | `giao` | `gc` | `gin` | `gn` | `gong` | `gs` |
| `gou` | `gb` | `gu` | `gu` | `gua` | `gw` | `guai` | `gy` |
| `guan` | `gr` | `guang` | `gd` | `gue` | `gt` | `gui` | `gv` |
| `gun` | `gp` | `guo` | `go` | `ha` | `ha` | `hai` | `hl` |
| `han` | `hj` | `hang` | `hh` | `hao` | `hk` | `he` | `he` |
| `hei` | `hz` | `hen` | `hf` | `heng` | `hg` | `hong` | `hs` |
| `hou` | `hb` | `hu` | `hu` | `hua` | `hw` | `huai` | `hy` |
| `huan` | `hr` | `huang` | `hd` | `hui` | `hv` | `hun` | `hp` |
| `huo` | `ho` | `ji` | `ji` | `jia` | `jw` | `jian` | `jm` |
| `jiang` | `jd` | `jiao` | `jc` | `jie` | `jx` | `jin` | `jn` |
| `jing` | `j;` | `jiong` | `js` | `jiu` | `jq` | `ju` | `ju` |
| `juan` | `jr` | `jue` | `jt` | `jun` | `jp` | `ka` | `ka` |
| `kai` | `kl` | `kan` | `kj` | `kang` | `kh` | `kao` | `kk` |
| `ke` | `ke` | `ken` | `kf` | `keng` | `kg` | `kiang` | `kd`\* |
| `kiu` | `kq` | `kong` | `ks` | `kou` | `kb` | `ku` | `ku` |
| `kua` | `kw` | `kuai` | `ky` | `kuan` | `kr` | `kuang` | `kd`\* |
| `kui` | `kv` | `kun` | `kp` | `kuo` | `ko` | `la` | `la` |
| `lai` | `ll` | `lan` | `lj` | `lang` | `lh` | `lao` | `lk` |
| `le` | `le` | `lei` | `lz` | `leng` | `lg` | `li` | `li` |
| `lia` | `lw` | `lian` | `lm` | `liang` | `ld` | `liao` | `lc` |
| `lie` | `lx` | `lin` | `ln` | `ling` | `l;` | `liu` | `lq` |
| `lo` | `lo`\* | `long` | `ls` | `lou` | `lb` | `lu` | `lu` |
| `luan` | `lr`\* | `lun` | `lp` | `luo` | `lo`\* | `lv` | `ly` |
| `lvan` | `lr`\* | `lve` | `lt` | `ma` | `ma` | `mai` | `ml` |
| `man` | `mj` | `mang` | `mh` | `mao` | `mk` | `me` | `me` |
| `mei` | `mz` | `men` | `mf` | `meng` | `mg` | `mi` | `mi` |
| `mian` | `mm` | `miao` | `mc` | `mie` | `mx` | `min` | `mn` |
| `ming` | `m;` | `miu` | `mq` | `mo` | `mo` | `mou` | `mb` |
| `mu` | `mu` | `na` | `na` | `nai` | `nl` | `nan` | `nj` |
| `nang` | `nh` | `nao` | `nk` | `ne` | `ne` | `nei` | `nz` |
| `nen` | `nf` | `neng` | `ng` | `ni` | `ni` | `nian` | `nm` |
| `niang` | `nd` | `niao` | `nc` | `nie` | `nx` | `nin` | `nn` |
| `ning` | `n;` | `niu` | `nq` | `nong` | `ns` | `nou` | `nb` |
| `nu` | `nu` | `nuan` | `nr` | `nui` | `nv` | `nun` | `np` |
| `nuo` | `no` | `nv` | `ny` | `nve` | `nt` | `o` | `oo` |
| `ou` | `ob` | `pa` | `pa` | `pai` | `pl` | `pan` | `pj` |
| `pang` | `ph` | `pao` | `pk` | `pei` | `pz` | `pen` | `pf` |
| `peng` | `pg` | `pi` | `pi` | `pia` | `pw` | `pian` | `pm` |
| `piao` | `pc` | `pie` | `px` | `pin` | `pn` | `ping` | `p;` |
| `po` | `po` | `pou` | `pb` | `pu` | `pu` | `qi` | `qi` |
| `qia` | `qw` | `qian` | `qm` | `qiang` | `qd` | `qiao` | `qc` |
| `qie` | `qx` | `qin` | `qn` | `qing` | `q;` | `qiong` | `qs` |
| `qiu` | `qq` | `qu` | `qu` | `quan` | `qr` | `que` | `qt` |
| `qun` | `qp` | `ran` | `rj` | `rang` | `rh` | `rao` | `rk` |
| `re` | `re` | `ren` | `rf` | `reng` | `rg` | `ri` | `ri` |
| `rong` | `rs` | `rou` | `rb` | `ru` | `ru` | `ruan` | `rr` |
| `rui` | `rv` | `run` | `rp` | `ruo` | `ro` | `sa` | `sa` |
| `sai` | `sl` | `san` | `sj` | `sang` | `sh` | `sao` | `sk` |
| `se` | `se` | `sei` | `sz` | `sen` | `sf` | `seng` | `sg` |
| `sha` | `ua` | `shai` | `ul` | `shan` | `uj` | `shang` | `uh` |
| `shao` | `uk` | `she` | `ue` | `shei` | `uz` | `shen` | `uf` |
| `sheng` | `ug` | `shi` | `ui` | `shou` | `ub` | `shu` | `uu` |
| `shua` | `uw` | `shuai` | `uy` | `shuan` | `ur` | `shuang` | `ud` |
| `shui` | `uv` | `shun` | `up` | `shuo` | `uo` | `si` | `si` |
| `song` | `ss` | `sou` | `sb` | `su` | `su` | `suan` | `sr` |
| `sui` | `sv` | `sun` | `sp` | `suo` | `so` | `ta` | `ta` |
| `tai` | `tl` | `tan` | `tj` | `tang` | `th` | `tao` | `tk` |
| `te` | `te` | `teng` | `tg` | `ti` | `ti` | `tian` | `tm` |
| `tiao` | `tc` | `tie` | `tx` | `ting` | `t;` | `tong` | `ts` |
| `tou` | `tb` | `tu` | `tu` | `tuan` | `tr` | `tui` | `tv` |
| `tun` | `tp` | `tuo` | `to` | `wa` | `wa` | `wai` | `wl` |
| `wan` | `wj` | `wang` | `wh` | `wei` | `wz` | `wen` | `wf` |
| `weng` | `wg` | `wo` | `wo` | `wu` | `wu` | `xi` | `xi` |
| `xia` | `xw` | `xian` | `xm` | `xiang` | `xd` | `xiao` | `xc` |
| `xie` | `xx` | `xin` | `xn` | `xing` | `x;` | `xiong` | `xs` |
| `xiu` | `xq` | `xu` | `xu` | `xuan` | `xr` | `xue` | `xt` |
| `xun` | `xp` | `ya` | `ya` | `yai` | `yl` | `yan` | `yj` |
| `yang` | `yh` | `yao` | `yk` | `ye` | `ye` | `yi` | `yi` |
| `yin` | `yn` | `ying` | `y;` | `yo` | `yo` | `yong` | `ys` |
| `you` | `yb` | `yu` | `yu` | `yuan` | `yr` | `yue` | `yt` |
| `yun` | `yp` | `za` | `za` | `zai` | `zl` | `zan` | `zj` |
| `zang` | `zh` | `zao` | `zk` | `ze` | `ze` | `zei` | `zz` |
| `zen` | `zf` | `zeng` | `zg` | `zha` | `va` | `zhai` | `vl` |
| `zhan` | `vj` | `zhang` | `vh` | `zhao` | `vk` | `zhe` | `ve` |
| `zhei` | `vz` | `zhen` | `vf` | `zheng` | `vg` | `zhi` | `vi` |
| `zhong` | `vs` | `zhou` | `vb` | `zhu` | `vu` | `zhua` | `vw` |
| `zhuai` | `vy` | `zhuan` | `vr` | `zhuang` | `vd` | `zhui` | `vv` |
| `zhun` | `vp` | `zhuo` | `vo` | `zi` | `zi` | `zong` | `zs` |
| `zou` | `zb` | `zu` | `zu` | `zuan` | `zr` | `zui` | `zv` |
| `zun` | `zp` | `zuo` | `zo` | | | | |
