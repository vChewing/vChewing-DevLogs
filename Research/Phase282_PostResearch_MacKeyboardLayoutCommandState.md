# Phase 282 後續研究：macOS 鍵盤佈局的 Command state 與 Chromium 的 `KeyboardEvent.key`

> 狀態：研究稿（2026-10-06）。用途＝把「`⌃⌘` 系熱鍵在 Chromium 系客體失效」的病灶定到行、交代為何「甲」「乙」兩案經
> 事主裁定不可行、備妥可直接投遞上游的三份 issue 稿（Chromium／W3C UI Events／WebKit），並記錄唯音自帶五個
> Ukelele 佈局的 command state 之補正（§7.3，屬本 phase 之交付）。
> 相關 phase 記錄見 `vChewing-DevLogs/Reqs4LLM/Archive_P201-P300/Reqs_0281-0290.md` 之 Phase 282。

## 0. 結論摘要

1. **病根不在唯音（也不在 IMK 的交還動作）**：唯音已正確放行該鍵（`OmitNSEvent` 即 `handleEvent` 回 `false`）；失效發生在客體把
   `NSEvent` 換算成 DOM `KeyboardEvent` 的那一步。
2. **Chromium 的具體病灶**：`ui/events/keycodes/keyboard_code_conversion_mac.mm` 之 `DomKeyFromNSEvent()`（`:843`）在
   「`characters` 不是合法 DOM key 字元」時，會以 **僅含 glyph modifiers** 的狀態重查鍵盤佈局（`:877-884`，`kGlyphModifiers`），
   而該檔的翻譯輔助函式 `NsKeyCodeAndModifiersToCharacter()` **明文把 Control 與 Command 的映射註解掉了**（`:256-263`）。
   於是 macOS 佈局為 Command 準備的那一層（command state）**永遠不會被諮詢**。
3. **關鍵實證**：本機以 `UCKeyTranslate` 逐佈局實測，Apple 的 `com.apple.keylayout.ZhuyinBopomofo`、`ZhuyinEten`、
   `DVORAK-QWERTYCMD` **都定義了 command state**，且在該狀態下 `c`→`c`、`w`→`w`（`⌃⌘` 亦然）；Chromium 卻回報基礎狀態的
   `ㄏ`／`ㄊ`。**即：佈局已經給了正確答案，Chromium 只是沒問。**
4. **唯音自有資源亦有一處缺口（已於本 phase 修畢，見 §7.3）**：五個 Ukelele 佈局**本來就有** Command 條目
   （`mapIndex` 3／7 → 拉丁小寫），惟**同時帶 Control 的 Command 和弦**會命中「控制字元表」（`mapIndex` 6）而回
   控制字元（`0x03`）；Apple 的注音佈局（`ZhuyinBopomofo`／`ZhuyinEten`）則一律走 command state、回 `c`。
5. **可行路徑**：① 上游 Chromium 補回 command state（§7.2 有可直接貼的 issue 與 patch 素材）；② 唯音自己的五個佈局
   與 Apple 對齊（**已施工**，見 §7.3；**不動客體佈局政策、不重貼事件**，故與「甲」「乙」皆不衝突）；③ 規範面
   （W3C UI Events，§7.4）與 WebKit 對位（§7.5）之 issue 稿皆已備妥。

## 1. 症狀與重現

- 環境：macOS 27（26A5428）、Chrome、唯音（`kBasicKeyboardLayout` 為出廠預設 `com.apple.keylayout.ZhuyinBopomofo`）。
- 於 Chrome 內按 `⌃⌘C`／`⌃⌘W`（網頁／擴充功能所用的熱鍵），客體收不到；熱鍵的有效性**隨當前鍵盤佈局而變**——
  事主以 HEAD 與 4.8.6 release 皆複驗。
- 唯音側的 debug log（`vCLog`，`_DebugMode` 開啟）顯示唯音**已放行**：

```
OmitNSEvent: KBEvent(type: .keyDown, modifierFlags: rawValue: 1310720 /* ⌘|⌃ */,
                     characters: "\u{03}", charactersIgnoringModifiers: "ㄏ", keyCode: 8 /* C */)
```

`OmitNSEvent` 只在 `configureHandlingGivenNullableEvent` 收到 `session.handleNSEvent(event) == false` 時輸出，即
**唯音回 `NO`（不處理）**；且該筆事件到達時 state 已是 `Empty`（前一次 `Committing()→Empty` 在 470 ms 前），
故「先 `commitComposition` 再交還」那條路本次並未涉入。

## 2. Chromium 側的推導鏈（附行號；檔在 `ui/events/keycodes/keyboard_code_conversion_mac.mm`）

| 位置 | 內容 | 對本症狀的意義 |
|---|---|---|
| `:783` `KeyboardCodeFromNSEvent()` | 先讀 `[event characters]`，再讀 `charactersIgnoringModifiers`，皆非 ASCII 才退回 `keyCode` | **瀏覽器級加速鍵**靠 `keyCode` 兜底 ⇒ `⌘C`／`⌘W` 之類照常運作（故 Chrome 自己的表裡也只放 `⌘` 系） |
| `:843` `DomKeyFromNSEvent()` | Step pre-3 死鍵 → Step 2/3 讀 `event.characters` → Step 4 | `⌃⌘C` 的 `characters` 是 `\u{03}`（Control 轉換後的）⇒ 不是合法 DOM key 字元 ⇒ 落到 Step 4 |
| `:877-884` Step 4 | `NsKeyCodeAndModifiersToCharacter(event.keyCode, event.modifierFlags & kGlyphModifiers)`；`kGlyphModifiers`（`:34`）＝`Shift ｜ CapsLock` | **Command／Control 被剝掉** ⇒ 查到的是佈局的**基礎狀態**字元（`ㄏ`） |
| `:244-263` `NsKeyCodeAndModifiersToCharacter()` | 逐位轉 `UCKeyTranslate` 的 modifier，其中：`// if (modifiers & NSEventModifierFlagControl) …`、`// if (modifiers & NSEventModifierFlagCommand) …` **皆為註解** | 該 helper **在設計上就無法表達 command state** |

另有一處同源影響：`components/input/web_input_event_builders_mac.mm` 之 `UnmodifiedTextFromEvent()`（`:79-83`）＝
`[event charactersIgnoringModifiers]`——依 AppKit 定義，它**本來就忽略 Command**，故 `unmodifiedText` 亦為 `ㄏ`；
`DomKeyFromEvent()` 在 `:215`。

## 3. Apple 自家（WebKit）怎麼做

`Source/WebCore/platform/mac/PlatformEventFactoryMac.mm` 之 `keyForKeyEvent()`：

```objc
// …the key value should be the printable key value that would have been produced if the key had been
// typed with the default keyboard layout with no modifier keys except for Shift and AltGr applied.
bool isControlDown = ([event modifierFlags] & NSEventModifierFlagControl);
RetainPtr<NSString> string = isControlDown ? [event charactersIgnoringModifiers] : [event characters];
```

⇒ WebKit 在**有 Control** 時同樣退到 `charactersIgnoringModifiers`（同樣得 `ㄏ`）；**無 Control** 時用 `characters`
（← 這個會讀到 command state）。故「`⌃⌘` 系在非拉丁佈局下拿不到拉丁字元」是 **Chromium 與 WebKit 共有的行為**，
且與 UI Events 規範 Algorithm 的 Step 4 文字一致（Chromium 的註解即照抄規範）——**這正是上游 PR 必須處理的爭點**：
不能只說「Chromium 有 bug」，要說「同一支檔案裡的加速鍵路徑已為 Dvorak-QWERTY⌘ 去讀 command state，而 DOM key 路徑沒有，
兩者不一致；且 macOS 自身的選單／捷徑解析走的是 command state」。

## 4. 實測：各佈局的 command state（`UCKeyTranslate`，modifier 編碼 `carbon >> 8`：cmd=0x01、shift=0x02、option=0x08、ctrl=0x10）

| 佈局 | base `c` | `⌘c` | `⌃c` | `⌃⌘c` | `⌘w` | 佈局檔的 `keyMapSelect` 規格（若可得原始檔） |
|---|---|---|---|---|---|---|
| `com.apple.keylayout.ABC` | c | c | `^C` | `^C` | w | （編譯檔） |
| `com.apple.keylayout.ZhuyinBopomofo`（唯音出廠預設） | ㄏ | **c** | ㄏ | **c** | **w** | （編譯檔） |
| `com.apple.keylayout.ZhuyinEten` | ㄒ | **c** | ㄒ | **c** | **w** | 原始檔只有 `<modifier keys=""/>` |
| `com.apple.keylayout.Dvorak` | j | j | — | j | , | （編譯檔；無 command state） |
| `com.apple.keylayout.DVORAK-QWERTYCMD` | j | **c** | `^C` | **c** | **w** | 「Dvorak – QWERTY ⌘」＝**該佈局存在的唯一目的就是 command state** |

**註**：`ZhuyinBopomofo` 的原始 `.keylayout` 不在本機（編譯進 `.uchr`），故其 `keyMapSelect` 未能直讀；但上表的
`⌘c = c` 已足以證明其 command state 存在。`Dvorak` 之 `⌘c = j` 說明「無 command state 者維持原樣」，
可作為「本 patch 不會動搖既有拉丁佈局」的證據。

唯音自帶五個 Ukelele 佈局的實查（`vChewing-macOS/Sources/vChewingIME_macOS/Resources/vChewingKeyLayout.bundle/Contents/Resources/`；
五檔結構一致，`defaultIndex="0"`＝未命中者回注音表）：

| `keyMapSelect` 序 | modifier 規格 | 目標 map 內容 | 含 Command |
|---|---|---|---|
| 0 | `""` | **注音**（`0:ㄇ 1:ㄋ 2:ㄎ 13:ㄊ`） | — |
| 1 | `anyShift` | 拉丁**大寫** | — |
| 2 | `caps` | 拉丁小寫 | — |
| 3 | `anyShift caps? anyOption? command` | 拉丁小寫 | ✔ |
| 4 | `caps? anyOption` | 拉丁小寫 | — |
| 5 | `anyShift caps? anyOption` | 拉丁大寫 | — |
| 6 | `anyShift caps? option? command? control` ／ `shift? caps? anyOption command? control` ／ `caps? anyOption? command? control` | **控制字元**（`0:&#x0001; 13:&#x0017;`） | 規格中 `command?` 為**可選**，故「只需 Control」即命中 |
| 7 | `caps? anyOption? command` | 拉丁小寫 | ✔ |
| 8 | `anyShift caps` | 拉丁大寫 | — |

**真實病灶的精確描述（初稿誤判為「完全沒有 command state」，已更正）**：`⌘C` 命中序 7 → 拉丁小寫 `c` ✔；
但 `⌃⌘C` 因**序 6 在前**、而其規格只**要求** `control`（`command?` 為可選），先被序 6 接走 → 回控制字元 `0x03`。
Apple 的注音佈局則把「任何含 Command 的狀態」都指向拉丁表（實測 `cmd+ctrl(c) = c`）。

Apple 的 `TraditionalPinyin.keylayout`／`Pinyin.keylayout` 則是（其 `mapIndex="0"` 即**拉丁小寫**）：

```xml
<keyMapSelect mapIndex="0">
    <modifier keys="command?"/>
    <modifier keys="anyShift? caps? command"/>
</keyMapSelect>
```

**驗證手段之界線**：這些檔宣告 `<?xml version="1.1"` 且以 `&#x0001;` 一類字元引用存放控制字元 ⇒ **libxml2（XML 1.0）與
Python `minidom` 皆無法解析**（`xmllint` 報 `xmlParseCharRef: invalid xmlChar value`，於**未修改的原檔亦同**）。
故此類檔只能靠結構檢查（標籤配對、條目序位、目標 map 內容）＋ DTD 之結構要求
（`/System/Library/DTDs/KeyboardLayout.dtd`：`modifierMap (keyMapSelect+)`、`keyMapSelect (modifier+)`；
`modifier` 之 `keys` 為 CDATA，故語法靠 Ukelele 慣例，且 `anyControl?`／`anyOption?` 等 term 見於 Ukelele 本體之字串表）。

## 5. 兩個互相獨立的缺陷

- **（A）上游 Chromium**：Step 4 以 glyph-only 狀態重查佈局，且 `NsKeyCodeAndModifiersToCharacter` 未映射 `cmdKey`／`controlKey`
  ⇒ **`⌃⌘` 系一律拿不到 command state 的字元**（全佈局通用）。`⌘` 系（無 Control）靠 Step 2/3 讀 `characters` 而無恙，
  **前提是該佈局有定義 command state**。
- **（B）唯音自有資源**：五個 Ukelele 佈局已有 `⌘` 系（無 Control）的 command 條目（序 3／7 → 拉丁小寫），
  惟**同時帶 Control 的 Command 和弦**被「只需 Control」的序 6 接走而回控制字元 `0x03`；Apple 的同類佈局（`ZhuyinBopomofo`／
  `ZhuyinEten`）在 `cmd+ctrl` 下回 `c`。此與 Apple 不一致，屬本倉可自行修好的缺陷——**已於本 phase 修畢**（§7.3）。
  其效果界線見 §7.3 末：真機 `NSEvent.characters` 對 Control 和弦另施控制字元轉換，故本修**不會**單獨救回 `⌃⌘` 熱鍵。

## 6. 為何「甲」「乙」皆不可行（2026-10-06 事主裁定）

- **甲**（把客體的鍵盤佈局改成 `alphanumericalKeyboardLayout`）：「使用者體驗不一致性問題太嚴重」——客體所見字元與使用者所選佈局脫鉤。
- **乙**（唯音吃掉該鍵、自行以完整 modifier state 查準字元後再 `CGEvent` 重貼）：會**破壞 VSCode 依當前佈局自動調整熱鍵體系**的機制
  （該機制本身即為此病灶的擦屁股；其外顯症狀＝使用者在 VSCode 看到**以注音符號組成的熱鍵組合**）。

⇒ 唯一方向＝**修上游**（A），並可並行修本倉資源（B）。

## 7. 上游投遞素材

> **投遞紀律（2026-10-06 兩次實證）**：WebKit Bugzilla 與 Chromium Buganizer **皆不允許編輯已發出之訊息**
> （描述亦然、作者自己也不行）⇒ 更正只能另開留言；Buganizer 之 summary 另有 **100 字元**硬限且為純文字。
> 故投遞前務必逐項驗：標題長度、markdown 渲染結果（表格可渲染，見 §7.7）、內部引用殘留、環境號（`sw_vers`）。

### 7.1 venue 清單

| 目標 | 位置 | 備註 |
|---|---|---|
| **Chromium issue** | `https://issues.chromium.org/issues/new` | 建議元件 **`Blink>Input`**（DOM `KeyboardEvent` 語意）；若 triage 認為屬 `ui/events` 則轉 **`UI>Events`**。內文務必指名檔案 `ui/events/keycodes/keyboard_code_conversion_mac.mm` 與 `ui/events/OWNERS`（flackr@chromium.org／hidehiko@chromium.org／jonross@chromium.org），triage 才找得到人 |
| **Chromium patch** | Gerrit `https://chromium-review.googlesource.com` | 需 Google 帳號 ＋ 簽 **CLA**（`https://cla.developers.google.com/`）；`git cl upload` 之後由 owner 給 `Code-Review+1` 並 land。流程見 `docs/contributing.md`、`docs/gerrit_guide.md`、`docs/commit_checklist.md`。**無 commit 權者亦可上傳**，只是要人代 land |
| **規範（若上游以「規範如此」擋下）** | `https://github.com/w3c/uievents/issues` | Step 4 的「glyph modifier keys only」是規範文字（Chromium 註解即照抄）；Apple 的 WebKit 亦照此實作 ⇒ 只改 Chromium 會被以「偏離規範」為由退回，宜同時提規範面 |
| **WebKit（要 Safari／WKWebView 一起修）** | `https://bugs.webkit.org/` | Product `WebKit`、Component **`UI Events`**（該 component 確實存在）。病灶位置＝`Source/WebCore/platform/mac/PlatformEventFactoryMac.mm` 之 `keyForKeyEvent()` |
| **下游（僅作佐證，不是 patch 目標）** | — | Electron／VSCode 只是受災與自行繞道者；在 Chromium issue 裡引用 VSCode 的「依佈局調整熱鍵體系」作為**危害證據**即可 |

**既有同域回報之查核（2026-10-06）**

| issue | 標題 | 類別 | 元件／平台 | 時間 |
|---|---|---|---|---|
| `40778452` | KeyboardEvent.key produces wrong value for Ctrl+semicolon on MacOS and UK keyboard | **同類值錯**（Ctrl + `;` 在 UK 佈局回 `:`；報告者語：「looks like Ctrl acts like Shift」） | `Blink>Input`（1222907）／Mac | 2021-07 建立、2025-12 仍有活動 |
| `40276733` | SendKeyPass can trigger NOTREACHED in ui::DomKeyFromNSEvent (on unsupported code path) | DCHECK／crash（`NOTREACHED`） | `Blink>Input, IO>Keyboard`／Mac | ≈2023-07～08 |
| `339187209` | Converting character ui::KeyEvent to content::NativeWebKeyboardEvent hits NOTREACHED | DCHECK／crash（`NOTREACHED`） | `Blink>Input`／Mac | ≈2024-05～06 |

- `40778452`（**真正相關者**）：同屬「macOS 上修飾和弦之 `key` 由佈局推導錯誤」之**值錯**家族、同一支 `keyForKeyEvent()` 之
  Control 分支、同一元件 `Blink>Input`（1222907，該 id 由多筆內嵌資料互證）；已指派 `mu...@chromium.org`。
  **與本病灶之別**：該案是**純 Ctrl**（無 Command）在**拉丁**佈局上取到 Shift 側字元；本病灶是**Ctrl＋Command**
  在**非拉丁**佈局上取到基礎狀態字元。兩者對應之修法方向不同（前者不得再套 shift 側映射；後者須補 command state），
  **故非重複**，但本案之 patch 與其共用同一分支 ⇒ 其既有病例正是「不可把 Control 一併帶入 fallback」之旁證。
  其描述附帶提供了一個比自寫 HTML 更好的重現工具：<https://w3c.github.io/uievents/tools/key-event-viewer.html>（見 §7.2 步驟 2）。
- 其餘兩筆皆為「算不出字元 ⇒ `NOTREACHED`」之**崩潰類**回報：`40276733` 正是 `DomKeyFromNSEvent()` 的
  `default: NOTREACHED()`（現行 main 之 `:896-897`）；`339187209` 在 `ui::KeyEvent` → `NativeWebKeyboardEvent`
  之轉換路徑（其引用 `keyboard_code_conversion_mac.mm;l=933` 屬附帶連結）。**本病灶是「值錯」、不崩不 DCHECK**，
  故**本問題未被提報過**。
- 投遞本案時**不引用**此二筆（引用同檔之 NOTREACHED bug 易被反射式判為 duplicate）；惟若 triage 反問
  「command state 算不出來是否可接受」，`DomKeyFromNSEvent()` 之 `NOTREACHED()` 即為「該函式不容忍此類無解」
  之現成旁證，留作第二輪材料。
- 元件亦由此二例佐證為 **`Blink>Input`**（`40276733` 另掛 `IO>Keyboard`）。
- 本沙箱無法搜 Buganizer（其 RPC／搜尋端點皆回 405），故「是否尚有其他同類回報」未能窮盡；建議於 tracker 內以
  元件 `Blink>Input` 配 `"keyboard layout"`／`"charactersIgnoringModifiers"`／`"command state"`／`"Zhuyin"` 各掃一遍。

### 7.2 可直接貼的 Chromium issue 草稿（英文；已重寫）

> **Buganizer 之硬限制（2026-10-06 實測）**：① summary（標題）**≤ 100 字元**且為**純文字**（不吃 markdown，故勿放反引號）——
> 下列草稿之標題已改為 **88 字元**版；② 其描述區之富文字編輯器**不是** GitHub-flavoured markdown，
> markdown 表格**不保證**渲染成表格 ⇒ 若表格失效，改用下方 [P] 之純文字條列版（內容相同）。

> 重寫要點：① 補「**Why this is worth fixing even though step 4 says what it says**」（同檔 `KeyboardCodeFromNSEvent()` 為
> Dvorak-QWERTY⌘ 而依賴 command state，DOM key 路徑卻看不到 ⇒ **同檔內部不一致**，此點可獨立於規範爭議而修）；
> ② 補環境（macOS 27.0 `26A428`、arm64）與可自驗的 repro；③ 補 `UCKeyTranslate` 實測表；
> ④ patch 草稿附**為何不可把 Control 一併帶入**（`ABC` 會退回 `Unidentified`，屬 regression）；
> ⑤ 補 Scope（純 `⌃` 和弦須維持基礎狀態字元）；⑥ Related 交叉引用 WebKit `326363`（已 triage）與 W3C `#420`；
> ⑦ 行號連結改用帶 SHA 之 GitHub 永久連結（與 #420 貼稿同一 SHA，便於互照）。

````markdown
**Title**: macOS: KeyboardEvent.key ignores the keyboard layout's command state for Ctrl+Cmd chords

**Summary**

On macOS a keyboard layout can define a *command state* — the key map selected while Command is held. It is the platform's own answer to "what character does this shortcut chord mean": Apple ships `Dvorak – QWERTY ⌘` (whose only purpose is that state) and its CJK input-source layouts (`com.apple.keylayout.ZhuyinBopomofo`, `ZhuyinEten`) define it as well, and AppKit's menu key-equivalent resolution honours it. Chromium's macOS DOM-key path never queries it: `NsKeyCodeAndModifiersToCharacter()` has the `cmdKey` (and `controlKey`) mappings commented out, and `DomKeyFromNSEvent()` step 4 re-translates with glyph modifiers (Shift/CapsLock) only. A `Ctrl`+`Cmd`+`C` chord on a Bopomofo layout therefore reports `key == "ㄏ"` — the layout's *base-state* character — instead of `c`.

**Steps to reproduce**

1. macOS 27.0 (26A428), arm64. Select the built-in input source 注音 – 標準 (`com.apple.keylayout.ZhuyinBopomofo`); `com.apple.keylayout.ZhuyinEten` and `Dvorak – QWERTY ⌘` (`DVORAK-QWERTYCMD`) behave the same way.
2. Open the UI Events key event viewer (<https://w3c.github.io/uievents/tools/key-event-viewer.html>) or any page containing
   `<input onkeydown="console.log(event.key, event.code)">`. Confirm the layout is active by pressing `c` with no modifiers —
   it reports `ㄏ`, i.e. the layout's base state.
3. Press `Ctrl`+`Cmd`+`C` and `Ctrl`+`Cmd`+`W`.

**Expected**: `key == "c"` / `"w"` — the character the layout's command state maps those chords to, and the character macOS itself uses for command shortcuts on that layout.
**Actual**: `key == "ㄏ"` / `"ㄊ"`. `code` is correct (`KeyC` / `KeyW`), `keyCode` is correct, and `Cmd`-only chords are correct, so only chords that hold Control *together with* Command are affected.

**Evidence** — `UCKeyTranslate` (key code 8, `C`), no modifiers → with the Command modifier:

| layout | no modifiers | Command |
| --- | --- | --- |
| `com.apple.keylayout.ZhuyinBopomofo` | `ㄏ` | `c` |
| `com.apple.keylayout.ZhuyinEten` | `ㄒ` | `c` |
| `com.apple.keylayout.DVORAK-QWERTYCMD` | `j` | `c` |
| `com.apple.keylayout.ABC` | `c` | `c` |

So the layout already provides the shortcut character; only the reading drops it.

**Root cause** — all in `ui/events/keycodes/keyboard_code_conversion_mac.mm`:

* `NsKeyCodeAndModifiersToCharacter()` [never maps `NSEventModifierFlagCommand` to `cmdKey`](https://github.com/chromium/chromium/blob/c50cbaca28ae90f203498eaa8b4ce6b5a121f4da/ui/events/keycodes/keyboard_code_conversion_mac.mm#L256-L263) — the two `if`s for Control and Command are commented out — so the helper cannot express the command state at all.
* `DomKeyFromNSEvent()` [step 4](https://github.com/chromium/chromium/blob/c50cbaca28ae90f203498eaa8b4ce6b5a121f4da/ui/events/keycodes/keyboard_code_conversion_mac.mm#L877-L884) re-translates the key code with `event.modifierFlags & kGlyphModifiers` (`Shift | CapsLock`), so even a helper that *could* express the command state would not be asked for it.
* The same file is internally inconsistent: `KeyboardCodeFromNSEvent()` ([line ~783](https://github.com/chromium/chromium/blob/c50cbaca28ae90f203498eaa8b4ce6b5a121f4da/ui/events/keycodes/keyboard_code_conversion_mac.mm#L783-L805)) deliberately reads `[event characters]` first "to handle the Dvorak-QWERTY Cmd case" — the accelerator path *does* rely on the command state — while the DOM-key path cannot see it.

**Why this is worth fixing even though step 4 says what it says**

The UI Events `key` algorithm's step 4 prescribes the modifier-stripped string, and a W3C issue is filed to clarify that (see *Related*). Independently of how the spec lands, Chromium's present result is self-inconsistent on macOS: the same layout reports the command-state character for `Cmd`+`C` (step 3 reads `characters`, which does reflect the command state) and flips to the base-state character as soon as Control is added — even though the command state is still in effect and the physical key is unchanged. `KeyboardEvent.code` is not a substitute for layout-aware users either: `code` is a physical-key identifier, so an application switching to it would break users whose command shortcuts follow the layout — exactly the case `Dvorak – QWERTY ⌘` exists for.

**Proposed change (patch sketch)**

```cpp
// NsKeyCodeAndModifiersToCharacter(): restore the Command mapping
if (modifiers & NSEventModifierFlagCommand)
  unicode_modifiers |= cmdKey;

// DomKeyFromNSEvent() step 4: keep Command in the re-translation state
NSEventModifierFlags fallback = event.modifierFlags & kGlyphModifiers;
if (event.modifierFlags & NSEventModifierFlagCommand)
  fallback |= NSEventModifierFlagCommand;
character = std::get<UniChar>(
    NsKeyCodeAndModifiersToCharacter(event.keyCode, fallback));
```

Control is deliberately **not** added to the fallback state: `UCKeyTranslate` with Control yields the control character (`^C` on `ABC`), which is not a usable DOM key, so the glyph-only result (`c`) would regress to `Unidentified`. With Command alone, every layout keeps its current result except the ones that define a command state — which is the point.

**Scope**: keep the change conditional on Command. For a plain `Ctrl`+key chord (no Command) the base-state character *is* the correct value, and no layout exposes a "control-state" mapping for that purpose, so the fallback should not be replaced wholesale. Note that the Control-only path already has its own,
pre-existing defect on Latin layouts (issue 40778452: `Ctrl`+`;` reports `:` on a UK layout), so this change must not
disturb that path in either direction.

**Related**
* WebKit: https://bugs.webkit.org/show_bug.cgi?id=326363 — same root cause in `Source/WebCore/platform/mac/PlatformEventFactoryMac.mm` `keyForKeyEvent()` (triaged).
* Spec: https://github.com/w3c/uievents/issues/420 — the step 4 wording that both engines cite.
* Related (same code path, different trigger — not a duplicate): https://issues.chromium.org/issues/40778452 —
  `Ctrl`+`;` reports `:` on a UK layout, i.e. the Control-only branch mis-deriving the character as well.

**Impact**: web apps and Electron apps that match shortcuts against `key` fail only on non-Latin input-source layouts. VS Code works around it by remapping its keybindings against the active layout, which is why users end up seeing shortcuts labelled with Bopomofo letters.
````

**\[P\] Evidence 之純文字版**（若 Buganizer 描述不吃 markdown 表格時替換用；同樣可直接貼）

````markdown
Evidence — UCKeyTranslate, key code 8 (`C`), no modifiers → with the Command modifier:

* com.apple.keylayout.ZhuyinBopomofo: ㄏ → c
* com.apple.keylayout.ZhuyinEten: ㄒ → c
* com.apple.keylayout.DVORAK-QWERTYCMD: j → c
* com.apple.keylayout.ABC: c → c

So the layout already provides the shortcut character; only the reading drops it.
````

### 7.3 唯音側可自行完成的那一半（「B」）——**已施工**

**修法**（五檔一致）：在「控制字元表」那條（`mapIndex="6"`）**之前**插入一條「凡含 Command 者一律走拉丁小寫表」的條目。
置於序 6 之前是本修法的**關鍵**（IMK 取首個命中者）；`mapIndex` 取 **7**（五檔的序 7 皆指向拉丁小寫表，
且 `⌘C` 之類原本就命中序 7，故此舉不改變 `⌘` 系既有行為，只把 `⌃⌘` 系從控制字元表拉回來）：

```xml
        <keyMapSelect mapIndex="7">
            <modifier keys="anyShift? anyOption? caps? command control"/>
        </keyMapSelect>
```

**護欄**：`Packages/vChewing_MainAssembly4Darwin/Tests/MainAssembly4DarwinTests/KeyLayoutCommandStateTests.swift`
（fixture 以 `#filePath` 錨定工作區根）釘住兩件事：① 每檔都存在一條「**必須同時**要求 `command` 與 `control`」的條目，
且它**排在**「只要求 `control`」那條之前（**位置即判準**）；② 凡規格**要求** `command` 的條目，其目標 map 的
`keyCode` 0／1／2／13 輸出必須是 `a`／`s`／`d`／`w`（不得是注音）。此靶當場抓到初稿測試自身的一處解析缺陷
（檔案有兩個 `keyMapSet`，稀疏的那個會覆寫完整的那個），已修正為只取第一個。

**效果界線（務必明記）**：本修**不會**單獨救回 `⌃⌘` 系熱鍵。真機上 AppKit 對「含 Control」的和弦會再施一次控制字元轉換
（實測：Apple 的 `ZhuyinBopomofo` 其 command state 已回 `c`，但事主 log 裡真事件的 `characters` 仍是 `\u{03}`）⇒
Chromium 的 Step 3 仍拿到控制字元、仍落 Step 4。本修的意義是：**與 Apple 的佈局對齊**（`cmd+ctrl` 回 `c` 而非 `0x03`），
並使 §7.2 之上游修法一旦落地，唯音佈局的使用者也能即刻受益（`⌘` 系則本來就已經正確）。
另：唯音**預設**用的是系統的 `ZhuyinBopomofo`（非本五檔），故「B」的受益者是**自選唯音佈局者**；
「A」的受益者是**全體唯音使用者**。

### 7.4 可直接貼的 W3C UI Events issue 草稿（英文；已含三處補強）

> 事主已於 2026-10-06 貼出 [`w3c/uievents#420`](https://github.com/w3c/uievents/issues/420)。其**已貼版本**與此稿之差異：
> ① 缺「**Why this is a spec question**」那一段（此即「為何這是規範問題而非實作 bug」之最強論據：同佈局下 `⌘C` 得 `c`、
> 加 Control 後卻翻成基礎狀態字元，屬**自我不一致**）；② Summary 那句把 Chromium（重譯 keyCode）與 WebKit（改讀
> `charactersIgnoringModifiers`）之機制混為一談；③ 無「Evidence」段（`UCKeyTranslate` 實測表 ＋ 三行 HTML 重現）與
> 「會回補交叉引用」之承諾。以下為**重寫後全稿**，可直接整段貼上、或以補充留言貼出。

````markdown
**Title**: `key` determination step 4 ("glyph modifier keys" only) discards the platform's command-state mapping on macOS, so `Ctrl`+`Cmd`+key chords report non-Latin characters

**Summary**

On macOS a keyboard layout may define a *command state* — the key map selected while Command is held. It is the platform's own answer to "what character does this shortcut chord mean": Apple ships `Dvorak – QWERTY ⌘` (whose only purpose is that state) and its CJK input-source layouts (`com.apple.keylayout.ZhuyinBopomofo`, `ZhuyinEten`) define it too, and AppKit's menu key-equivalent resolution honours it.

The `key` determination algorithm's step 4 says: *"If the key event has any modifier keys other than glyph modifier keys, then set key to the key string that would have been generated by this event if it had been typed with all modifier keys removed except for glyph modifier keys."* On macOS, Chromium implements that by re-translating the key code with glyph modifiers (Shift/CapsLock) only; WebKit reaches the same result by falling back to `charactersIgnoringModifiers` whenever Control is down (a property that ignores Command by definition). In both cases the layout's command state is dropped, so `Ctrl`+`Cmd`+`C` on a Bopomofo layout reports `key == "ㄏ"` — the layout's *base-state* character — even though that layout's command state maps the same chord to `c`. (`Cmd`-only chords are unaffected in practice, because `characters` is consulted first and does reflect the command state.)

**Why this is a spec question**

The present result is self-inconsistent, and the inconsistency comes from step 4's wording rather than from either engine. On the same layout, `Cmd`+`C` reports `key == "c"` (step 3 reads `characters`, which reflects the command state), while adding Control flips `key` to the layout's base-state character (`"ㄏ"`). Step 4 exists to remove the effect of modifiers that merely select a different key value; here it changes which character the layout says the key means, while the command state is still in effect. On macOS that state is the platform's own shortcut-resolution answer — it is why `Dvorak – QWERTY ⌘` exists — so step 4 as written defeats its own purpose for command chords.

`KeyboardEvent.code` is not a workaround for layout-aware users: `code` is a physical-key identifier, so an application that switched to it would break users whose command shortcuts are expected to follow the layout — exactly the case `Dvorak – QWERTY ⌘` addresses.

**Request**

Clarify step 4 for platforms that expose a modifier-state mapping for shortcut chords. Either:

(a) add a note that on macOS the command state must be applied before the remaining modifiers are stripped, or
(b) state that the "key string ... with all modifier keys removed except for glyph modifier keys" is to be produced through the platform's *shortcut* resolution for command chords.

Interop matters here because shortcut-matching application code (including Electron apps) reads `key`; today's behaviour forces workarounds that push layout letter shapes (e.g. Bopomofo) into user-visible keybinding UI — for example VS Code remaps its keybindings against the active layout, which is how users end up seeing shortcuts labelled with Bopomofo letters.

Happy to propose concrete spec text (or a PR to this repository) if the WG agrees that the command state should be applied.

**Evidence**

`UCKeyTranslate`, key code 8 (`C`), without modifiers → with the Command modifier:

| layout | no modifiers | Command |
| --- | --- | --- |
| `com.apple.keylayout.ZhuyinBopomofo` | `ㄏ` | `c` |
| `com.apple.keylayout.ZhuyinEten` | `ㄒ` | `c` |
| `com.apple.keylayout.DVORAK-QWERTYCMD` | `j` | `c` |
| `com.apple.keylayout.ABC` | `c` | `c` |

The layouts already provide the shortcut character; the reading described above is what drops it.

Minimal repro on macOS:

```html
<input onkeydown="console.log(event.key, event.code)">
```

Select 注音 – 標準 (`com.apple.keylayout.ZhuyinBopomofo`), then press `⌘C` (reports `c` / `KeyC`) and `⌃⌘C` (reports `ㄏ` / `KeyC`).

I will cross-reference the Chromium and WebKit reports here once they are filed.

**Reference implementations**

* Chromium `ui/events/keycodes/keyboard_code_conversion_mac.mm`: `DomKeyFromNSEvent()` [step 4](https://github.com/chromium/chromium/blob/c50cbaca28ae90f203498eaa8b4ce6b5a121f4da/ui/events/keycodes/keyboard_code_conversion_mac.mm#L877-L884); `NsKeyCodeAndModifiersToCharacter()` [has the `cmdKey`/`controlKey` mappings commented out](https://github.com/chromium/chromium/blob/c50cbaca28ae90f203498eaa8b4ce6b5a121f4da/ui/events/keycodes/keyboard_code_conversion_mac.mm#L256-L263).
* WebKit `Source/WebCore/platform/mac/PlatformEventFactoryMac.mm`: `keyForKeyEvent()` [falls back to `charactersIgnoringModifiers` whenever Control is down](https://github.com/WebKit/WebKit/blob/7cbfa3e8792f0a9164dab133bf3278613b0aa2e1/Source/WebCore/platform/mac/PlatformEventFactoryMac.mm#L259-L300).
````

### 7.5 可直接貼的 WebKit bugzilla 草稿（英文）

> ⚠️ 此為**已貼出之原稿**（`bugs.webkit.org 326363`）；其末句含本稿節號、而 Bugzilla 之 comment 不可編輯，
> 故更正只能以 §7.6 [A] 之留言為之。**若要另貼他處（別倉／別 tracker），請先刪掉末句那半句內部引用。**
> 反之，§7.2（Chromium）與 §7.4（W3C）兩稿皆已確認**不含品牌名、不含任何內部引用**，可直接貼。

````markdown
**Product**: WebKit ｜ **Component**: UI Events
**Title**: `KeyboardEvent.key` on macOS: `Ctrl`+`Cmd`+key chords report the layout's base-state character instead of its command-state character

**Steps to reproduce**
1. On macOS select an input-source layout that defines a command state, e.g. `com.apple.keylayout.ZhuyinBopomofo`, `com.apple.keylayout.ZhuyinEten`, or `Dvorak – QWERTY ⌘`.
2. Open a page with a `keydown` listener that logs `event.key` and `event.code`.
3. Press `⌃⌘C` and `⌃⌘W`.

**Expected**: `key == "c"` / `"w"` — the character those chords map to in the layout's command state (`UCKeyTranslate` with the Command modifier returns `c`/`w` for these layouts; AppKit resolves Command shortcuts through the same state).
**Actual**: `key == "ㄏ"` / `"ㄊ"` (the base-state character). `event.code` is correct, and `⌘`-only chords are correct.

**Cause**: `Source/WebCore/platform/mac/PlatformEventFactoryMac.mm`, `keyForKeyEvent()`:
```objc
bool isControlDown = ([event modifierFlags] & NSEventModifierFlagControl);
RetainPtr<NSString> string = isControlDown ? [event charactersIgnoringModifiers] : [event characters];
```
With Control down this reads `charactersIgnoringModifiers`, which by definition ignores Command, so the layout's command state is never consulted. (Chromium reaches the same result through a different path: `DomKeyFromNSEvent()` step 4 re-translates with `NSShiftKeyMask|NSAlphaShiftKeyMask` only.)

**Impact**: Web apps and Electron apps that match shortcuts against `key` fail on non-Latin input-source layouts. For example VS Code remaps its keybindings to the active layout, which is why users end up seeing shortcuts labelled with Bopomofo letters.

**Suggested fix**: when Control is held *and* Command is also held, prefer the command-state translation — e.g. translate with the Command modifier included (the same lookup `windowsKeyCodeForKeyEvent()` already relies on for the "Cmd switches Roman letters for Dvorak-QWERTY layout" case).

**Note**: filed together with a W3C UI Events issue, because the current step-4 wording prescribes the modifier-stripped string (see §7.4 of the accompanying analysis).
````

### 7.6 WebKit bug 之後續留言稿（英文、可直接貼）

> **WebKit Bugzilla 之 comment 不可編輯**（comment 0 同樣只是 comment；作者無 `editbugs` 權限者亦然）——故**一切更正一律以新留言為之**，
> 此與 GitHub Issues（可編輯）／Gerrit（可 upload 新 patch set）皆不同。事主已貼
> [`326363`](https://bugs.webkit.org/show_bug.cgi?id=326363)（Product `WebKit`／Component `UI Events`，當日 triage 為 **P2**、
> 指派 **Abrar Rahman Protyasha**）；其貼稿末句仍留本稿節號（「see §7.4 of the accompanying analysis」），該句**無法回收**，
> 只能以 [A] 就地更正並補齊環境、範圍與證據——**一則即可，不必拆三則**（少 noise，且更正與證據同框）。

````markdown
[A] Follow-up comment (correction + environment + scope + evidence)

One correction first: the closing note of the description says "see §7.4 of the accompanying analysis" — that pointed at a private write-up which is not attached to this bug. The self-contained version is:

> the `key` determination algorithm's step 4 (UI Events) is what prescribes the modifier-stripped string, so this was filed together with a W3C spec issue: https://github.com/w3c/uievents/issues/420

Environment: macOS 27 (26A5428), Apple silicon. The keyboard-layout tables involved are the same on macOS 26.x, so this is not Safari-version-specific — the path is entirely inside the macOS event translation (`keyForKeyEvent()`).

A scope note for whoever fixes this: the change has to stay conditional on Command being held *together with* Control. For a plain `⌃`+key chord (no Command) the base-state character *is* the correct `key`, so the fallback should not be replaced wholesale.

Evidence — `UCKeyTranslate` (key code 8, `C`), no modifiers → with the Command modifier:

| layout | no modifiers | Command |
| --- | --- | --- |
| `com.apple.keylayout.ZhuyinBopomofo` | `ㄏ` | `c` |
| `com.apple.keylayout.ZhuyinEten` | `ㄒ` | `c` |
| `com.apple.keylayout.DVORAK-QWERTYCMD` | `j` | `c` |
| `com.apple.keylayout.ABC` | `c` | `c` |

So the layout already provides the shortcut character; only the reading drops it.

The asymmetry is the clearest way to see it: on the *same* layout, `⌘C` reports `key == "c"` (the `characters` branch does reflect the command state), while `⌃⌘C` reports `ㄏ`. Adding Control changes which character the layout says the key means, which is not what step 4 was written to do.

Minimal repro: `<input onkeydown="console.log(event.key, event.code)">`, select 注音 – 標準 (`com.apple.keylayout.ZhuyinBopomofo`), press `⌘C` and then `⌃⌘C`.

Filed on the Chromium side as well: <link>
````

### 7.7 Chromium issue 已投遞（`569927808`）與其追評稿

> 事主已於 2026-10-05 投遞 [`issues.chromium.org 569927808`](https://issues.chromium.org/issues/569927808)：
> 標題＝`macOS: KeyboardEvent.key ignores the keyboard layout's command state for Ctrl+Cmd chords`（88 字元，未用反引號）；
> 元件＝**`Blink>Input`（1222907）＋ `Mac`**（正確）；P3／S3；內文即 §7.2 之全稿。
> 經查其已存之描述（由該頁內嵌資料判讀，未動用瀏覽器）：① **markdown 表格已正確渲染成 `<table>`**（`<th>`×4、`<td>`×12），
> 有序清單、`<code>` 亦皆渲染 ⇒ **無須**改用 [P] 純文字版；② **無任何內部引用殘留**（`§7`／`accompanying analysis`／
> `Research/`／`DevLogs`／`vChewing`／`唯音` 皆 0 命中）；③ 唯一殘留＝**附件檔名** `p282_keyprobe.html`（描述末段亦提及它），
> 屬無害之內部編號，內容本身已確認無品牌與內部引用。
> `40778452` 之狀態經事主確認為 **New**（2021 年提報、四年未 triage）⇒ 追評稿**不得**寫「A 病例已修」；
> 此事亦為預期管理：`Blink>Input` 對此家族之處理並不積極，本案縱使寫得完整亦可能久懸 New。
> **Buganizer 之 comment 亦不可編輯**（與 WebKit Bugzilla 同），故下列補正一律以**一則追評**為之。

````markdown
Two follow-ups — one of them is a directly related report, the other is history in the same file.

**Related report (not a duplicate)**: https://issues.chromium.org/issues/40778452 — "KeyboardEvent.key produces wrong value for Ctrl+semicolon on MacOS and UK keyboard" (reported 2021; still open, status New). Same class of defect and the same component, different trigger: that one is Control-only on a Latin layout (`Ctrl`+`;` reports `:`), this one is Control+Command on a non-Latin layout (the layout's base-state character comes back instead of its command-state character). The fixes therefore differ — and that report's case is exactly why Control must stay out of the fallback state in the patch sketch above.

**This file has been fixed for the same phenomenon before**: https://chromium.googlesource.com/chromium/src/+/e53e6c8ae286cf73d06e0f75eff67244dfa8b288 — "Virtual keycodes on Mac were incorrect for control characters. Mac generates unicode control characters for key sequences like Ctrl-[. This was fixed about 5 years ago in WebKit; but the chromium code which was a copy of that hadn't changed since." That change modified `ui/events/keycodes/keyboard_code_conversion_mac.mm` for exactly this "macOS hands us a layout-derived character for a chord" family. This report asks only for the Command mapping to come back and leaves Control out, so the behaviour that earlier fix addressed is not disturbed.

For convenience, the UI Events key event viewer works fine for reproducing this as well: https://w3c.github.io/uievents/tools/key-event-viewer.html
````

## 8. 待決事項

1. **Chromium issue**：**已投遞**（[`569927808`](https://issues.chromium.org/issues/569927808)，元件 `Blink>Input`＋`Mac`）。
   其 comment 不可編輯 ⇒ 追評稿見 §7.7（補 `40778452` 之相關性與非重複、`e53e6c8` 之同檔前例、以及 UI Events
   key event viewer 之重現法）。需要時我可再壓成 Gerrit CL 描述（含 `Bug:` 行與 commit message 格式）。
2. **W3C UI Events**：**已貼**（[`#420`](https://github.com/w3c/uievents/issues/420)）；建議以**補充留言**貼上 §7.4 之重寫全稿
   （已貼版缺「Why this is a spec question」與 Evidence 段），並在 Chromium／WebKit 那兩份貼出後回補交叉引用。
3. **WebKit bugzilla**：**已貼**（[`326363`](https://bugs.webkit.org/show_bug.cgi?id=326363)，triage **P2**、assignee **Abrar Rahman Protyasha**）。
   其 comment **不可編輯**，故貼稿末句之節號收不回來——**以 §7.6 [A] 一則留言就地更正**並補齊環境／範圍／證據。
4. §7.3 已施工（五個佈局 ＋ `KeyLayoutCommandStateTests`）。**另一件仍未決**：是否連**基礎狀態**也改為拉丁
   （＝Apple 拼音佈局那種做法）——那會讓**現行** Chromium 的 `⌃⌘` 直接可用（因為 Step 4 查的正是基礎狀態），
   代價是佈局不再對客體輸出注音（螢幕鍵盤與「動態基礎鍵盤佈局」之表徵隨之改變）。此屬政策決定，待事主裁定。
