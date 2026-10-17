#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""唯音工作區之 DevLogs 記述預算稽核（House Style audit）。

**事由**（2026-09-27，P261 之後）：逐 Phase 之記述量自 P200 起翻倍、P240 之後再翻，
至 P250–P261 之時已達每 phase 約 22,700 chars（P160 段為 6,400）——其中大半非「事實」，
而是同批事實在一份 phase 內、以及跨四份文件之間的重複。本稽核即把該預算寫成可執行之量尺：
它**不判內容好壞**，只報「誰超預算、超在哪一份文件」。

**量尺**（規則本體見 `KnowledgeMemo_SubArticles/22-HouseStyle.md` §12.7；改規則請同步改本檔之
`BUDGETS` 與 `SUB_ARTICLE_MAX`）：

* **Reqs 卷之 Phase 篇**：標準 ≤ 5,000 chars；修補型 ≤ 2,500；大型／系列／規劃 ≤ 8,000。
  本稽核以「該篇佔本卷全部 Phase 之中位數之 K 倍」不判斷，只列字數與超標倍率。
* **`DevReqsHistory.md` 各列**：≤ 300 chars。
* **`KnowledgeMemo4LLM.md` 之各分卷**（`KnowledgeMemo_SubArticles/*.md`）：**每卷 ≤ 12,000 chars**
  （2026-10-15 拆分時訂立）。其故：該備忘錄原為單檔 188,646 chars，AI Agent 一見即「寧願只讀一部分」
  ⇒ 拆成「索引 ＋ 分卷」後，**每一卷都必須小到能整卷讀完**。索引本體 `KnowledgeMemo4LLM.md` 亦一併列報。
* **`KnowledgeMemo4LLM.md`（含各分卷）之逐 Phase 記述**：**不得存在**（該檔只收「現況」與
  「施工注意事項」，見該檔文首〈沿革不再寫入本文檔〉）。本稽核以「索引全文與各分卷全文中
  有無 `- **…Phase NNN…已完工` 形之條目」偵測之（**不限於開頭部**——各分卷亦一併掃）。
* **儀式小節**：`§8.0.1 三步`（對帳／回寫本文／重排後續）、`兩倉 byte-sync`、
  `測試基線之同框對照`、`變異測試` 四類——**不得逐 Task 重複**；同一 phase 內出現
  逾一次即列出。

**判與不判**：**預算只管「現行卷之首 Phase 起」**（預設自動判定；可用 `--enforce-from N` 覆寫）。
在此之前之各卷為**已歸檔之歷史記錄**，一律照舊——本稽核只把它們列為 `legacy（不判）`，
不使其左右退出碼。此界線與 `KnowledgeMemo_SubArticles/23-HouseStyleCleanup.md` §12.7.6 之
「不回改歷史」一致。

**用法**：

    python3 housestyle_audit.py                    # 掃全倉；判斷範圍＝現行卷起
    python3 housestyle_audit.py --enforce-from 250 # 覆寫判斷起點
    python3 housestyle_audit.py --all-history      # 連歷史卷一併判（嚴苛模式）
    python3 housestyle_audit.py --quiet            # 只在有超標時輸出
    python3 housestyle_audit.py --json             # 供其他工具消費
    python3 housestyle_audit.py --self-test        # 以臨時檔自我驗證（紅綠雙驗）

**退出碼**：`0` ＝ 判斷範圍內無超標；`1` ＝ 有超標（供交差前之一鍵檢核）。
"""

import argparse
import io
import json
import os
import re
import sys
import tempfile

# ── 量尺（改這裡即改規則；請與 22-HouseStyle.md §12.7 同步）──────────────────
BUDGETS = {
    "patch": 2500,     # 修補型：1–3 檔、零設計
    "standard": 5000,  # 標準
    "large": 8000,     # 大型／系列／規劃
}
HISTORY_ROW_MAX = 300          # DevReqsHistory 單列
# §12.7 係 2026-09-27（P261 完工後）訂立 ⇒ 預算自 **P262** 起適用；
# 其前之各卷為「訂立前之歷史記錄」，一律 legacy（不判），與 §12.7.6 之「不回改歷史」一致。
HOUSESTYLE_EPOCH_PHASE = 262
MEMO_HEAD_FORBIDDEN = True     # KnowledgeMemo（索引與各分卷）皆不得有逐 Phase 記述
# 2026-10-15 起 KnowledgeMemo4LLM.md 之正文移入下列子目錄之分卷；
# 每卷之上限即「一眼可讀完」之尺（索引本體不受此限，另列報）。
SUB_ARTICLES_DIR = "KnowledgeMemo_SubArticles"
SUB_ARTICLE_MAX = 12000        # 單一分卷之 chars 上限
RITUAL_ONCE_MAX = 1            # 同一 phase 內每類儀式小節至多一次

RITUALS = {
    "§8.0.1 收尾回檢": r"8\.0\.1|第 ?[123] ?步：(對帳|回寫本文|重排後續)",
    "兩倉 byte-sync": r"byte-sync",
    "測試基線之同框對照": r"測試基線|同框對照",
    "變異測試": r"變異測試",
}

# §12.7.3 之型態係**按該 phase 之性質**（修補／標準／大型），非按字數；自動量尺無從得知性質，
# 故預設以字數推之。下表為**已明示型態者**之覆寫——凡作者已聲明其型態者登錄於此，以免誤報。
# **新 phase 通常不必登記**：預設推測已夠用，且預算本容超標（記一行理由即可）。
# 以下為 2026-09-27 第二輪回溯套用（P241–P261）時逐篇訂定之額度；
# **P262 起**：作者已於該篇聲明型態者續登錄於此（P262 ＝ 標準：四檔、含兩支新測試用例與一項落點取捨）。
LARGE_PHASES = {241, 245, 250, 251, 252, 258, 259, 260, 261,      # 大型／系列／規劃 ⇒ 8,000
                286,  # P286 ＝ 大型：25 檔（12 檔裁併為 18 檔）＋ 283 支測試逐支改號與標題
                      # 英文化 ＋ 兩倉同步；自動推測誤判為「修補」（字數 3,790 落在推測門檻
                      # 內），惟該篇載三項病灶、五項被否決之方案與五條界線。
                294,  # P294 ＝ 大型：三倉（macOS 19 檔、LibVanguard 同源同步 11 檔、官網 1 檔）；生產碼
                      # 跨八檔——新公開枚舉 `VirtualSpaceKey` 與單元圖之就地合成、偏好值域擴為
                      # `-1 ... 2`、分診之新分支與既有 Shift+Space 輪替守衛之必要修正——＋ 8
                      # 支新測試用例 ＋ 四語系文案 ＋ 助手來源與三份產物重生；自動推測判為「標準」。
                292,  # P292 ＝ 大型：七倉（三倉術語更動 ＋ Tekkon 三倉之複核與再修 ＋ 官網重製）——跨本地化
                      # 文案、原始碼註解、助手後設資料與產物鏈，另含一次 zh-Hans-TW 之全面稽核；四次
                      # 追加交辦皆就地併入該篇。篇內已依 §12.7.4 收束至 4,688 chars（長篇推導移入
                      # `Research/Phase292_Research_TerminologyAndHansTWAudit.md`），惟其型態為大型：
                      # 自動推測按字數會誤判為「標準」。
                301,  # P301 ＝ 大型／規劃：研究任務（不動任何原始碼），交付 806 行研究稿
                      # `Research/Phase301_Research_DualpinSupport.md` ＋ 439 行 P303 規劃稿
                      # `Research/Phase303_Research_DualpinSettingsUI.md`（後者係 P301 之產物、
                      # 界定 P303 之手術範圍）；自動推測按字數（原 7,991；2026-10-13 改寫為
                      # 一氣呵成之形態後為 5,853）會誤判為「標準」，惟該篇載一項對 P151 永久
                      # 定案（雙拼不做、由磁帶承載）之反轉、一座新模組（`Arimitsu`）之完整設計
                      # 與校驗分級、426 條詞幹之覆蓋率實證（425／426、相異 422 碼、重碼 3 組）
                      # 與六項原待事主裁定之決策。
                302,  # P302 ＝ 大型：引擎側（`Arimitsu` 子目標 1,199 行、輸入路徑 9 檔、兩份 manifest
                      # 與 6 檔測試）＋兩倉逐位元組同步；同日之事主覆核與實機回報皆就地修訂
                      # （值域 106–108 ⇒ 200…202、三槽分離、`isPinyin`／`isZhuyin` 立為新判準、
                      # 七處修正與 2026-10-13 之再三日定案），2026-10-13 改寫為一氣呵成之
                      # 形態後為 7,993 chars；原判「標準」（4,147）之推定已不適用。
                303,  # P303 ＝ 大型：界面側（三槽下拉、雙拼開關、匯入 Section 之兩版面板、四語系各
                      # 19＋38 鍵、兩份導出物重生、方案編輯器之草稿模型與兩版界面（1,484 行）、
                      # 序列化 ＋147、兩份新測試檔 13 支用例）＋助手側同案（`settings-surface.js`
                      # 三桶、題庫與 fixture 重生）。7,984 chars。
                      # 型態係按性質判定，非按字數。
                314,  # P314 ＝ 大型／規劃：研究任務（不動任何生產碼，依 P301 之先例），交付
                      # `Research/Phase314_Research_TestIsolationSeams.md`（研究稿）；自動推測按
                      # 字數（5,423）會誤判為「標準」，惟該篇載兩項具體目的之裁定（一成立且必要
                      # 但不足、一成立且成本極低、一（泛型之憂）不成立）、**四條**真正枷鎖（事主
                      # 僅列兩條）、三處 `UserDefaults` 縫之洩漏（含兩處直讀 `.standard`）、七項
                      # 被否決之方案、兩道縫之設計、P315–P320+ 之分期草案、五項驗收判準與五個
                      # 待事主裁定之點；型態按性質判定，非按字數。
                315,  # P315 ＝ 大型：兩道縫下推至實例（17 檔：`LXFacade` 收 `locator:` 並派給五個
                      # 使用者語言模組與感知器、`AppProperty` 改為建構時捕獲 `store`、`PrefMgr`
                      # 收 `init(store:)` 逐一套 126 項、`sharedSansDidSetOps` 改依容器身分快取、
                      # POM 五套房與遷移套房撤六處 `.serialized`、新 5 支用例），非「1–3 檔、零設計」
                      # 之修補型：其載一條病灶（縫釘在全域 ⇒ 換容器全有全無）、一條根因（`container`
                      # 逐次求值對實例化是阻礙）、兩處相反之取捨（包裝器必捕獲／共用管理器必逐次
                      # 解析）、一項實測反轉（`LXFacade.prefs` 捕獲致兩支紅）與三條陷阱；型態按
                      # 性質判定，非按字數。
                316}  # P316 ＝ 大型：類 B 靜態之收束（36 檔、＋849／−477：新 `FactoryDictionary`
                      # 物件收辭典／卡帶／注音文、`SessionHost` 收逐宿主辭典快取並注入會話、
                      # `Shared.InputMode.lexicon` 之三層行程級快取整塊刪除、`inputMode` 升為
                      # 會話協定要求（碼點解碼與提示不再問 `IMEApp.currentInputMode`）、
                      # `UserDef` 七個靜態入口收 `store:`、`LibVanguardTests` 根與六個子套房撤
                      # `.serialized`、新 `TestEnvironment` 慣用語與 5 支證明用例）。非修補型：
                      # 其載一條取捨（辭典共用同一物件以保住生產端單次解析）、一條分工（會話
                      # 宿主為唯一狀態根）、一項刪除（`productionCache`／`unitTestCache`／
                      # `activeCache`）、三條界線延續（`IMEApp`／`LexiconAssemblyTests` 之 137
                      # 處靜態呼叫／`SessionHost.shared` 未刪）與三條陷阱；型態按性質判定，非按字數。
STANDARD_PHASES = {242, 243, 244, 246, 247, 248, 249,                # 標準 ⇒ 5,000
                   253, 254, 255, 256, 257,
                   262, 263, 264, 265, 266, 267,
                   272,  # P272 ＝ 標準：四檔、含五支新測試用例與兩項落點取捨。
                   274,  # P274 ＝ 標準：四檔（生產碼 3 行 ＋ 2 支回歸測試用例 ＋ 說明）；自動推測
                         # 誤判為「修補」（3 行生產碼 ⇒ 字數 3,007 落在推測門檻內），
                         # 惟該篇載一項跨 phase 之開關語義（P238／P270／P273）與兩條界線。
                   277,  # P277 ＝ 標準：四檔生產碼（新共用純函式 ＋ 窗頂 pane 與混打 Tooltip
                         # 兩處顯示轉換 ＋ 一處去重）＋ 兩支新測試用例與四支改寫；自動推測誤判為
                         # 「修補」（字數 3,723 落在推測門檻內），惟該篇載兩項刻意之不對稱
                         # （不問方向／不補陰平）與一項被否決之方案。
                   285,  # P285 ＝ 標準：八檔（兩支新原文 ＋ 產製器擴及四語系 ＋ 說明與 makefile
                         # ＋ 兩份產物重生）；自動推測誤判為「修補」（字數 3,397 落在推測門檻
                         # 內），惟該篇載兩項結構破損之判定、四項被否決之方案與一項證據界線。
                   287,  # P287 ＝ 標準：三檔（生產碼一處 ＋ 兩支新測試用例）＋ 一項實測排除之假說；
                         # 自動推測誤判為「修補」（字數 3,179 落在推測門檻內），惟該篇載兩項病灶
                         # （投機預覽外洩／原文重複遞交）、一項單點修法之取捨與 PCB 之排除證據。
                   288,  # P288 ＝ 標準：三檔（兩份繪製各一行 ＋ 一支新測試用例與其離屏掃描器）＋ 一項
                         # 對事主原擬手術目標之偏離（原案經實測不可行，另立等效修法）與其證據；
                         # 自動推測誤判為「修補」（字數 3,341 落在推測門檻內）。
                   293,  # P293 ＝ 標準：純用詞清剿（兩倉各 9／4 檔、＋35／−35 與 ＋23／−23），
                         # 無新測試用例、無行為改動；自動推測誤判為「修補」（字數落於 4,000 門檻內），
                         # 惟該篇載兩枚漂移之溯源與一條 durable 名詞通則。
                   298,  # P298 ＝ 標準：三檔（新終止助手 259 行 ＋ 換檔後保證刀與第一刀去神祕化
                         # ＋ 新測試檔 12 支）；自動推測誤判為「修補」（字數 3,402 落在推測門檻
                         # 內），惟該篇載一項跨 phase 之取捨（保證只能在換檔後、postcondition
                         # 不可寫「沒有行程」）與三坑之界線。
                   300,  # P300 ＝ 標準：兩檔（換檔後之保證刀 101 行 POSIX sh ＋ 第一刀去神祕化），
                         # 無新測試用例；自動推測誤判為「修補」（字數 3,475 落在推測門檻內），惟該篇
                         # 載一項跨 phase 之承接（P298「未動」之 PKG 路徑）、一項新約束（以 root
                         # 執行之安裝須以 console user 為界）與一條對 P298 記載之訂正（`pgrep -x`
                         # 與 `MAXCOMLEN` 之關係於本機 macOS 27 不成立）。
                   305,  # P305 ＝ 標準：兩檔（生產碼 ＋284／−43 之三組 head 索引、解析快取與容量收斂
                         # ＋ 新測試檔 9 支用例）；自動推測誤判為「修補」（字數 3,950 落在推測門檻
                         # 內），惟該篇載兩條病灶（日誌重播繞過容量、檢索全表掃描）、四項被否決
                         # 之方案與一條持久化層之既有界線（移除記錄不被重播採納）。
                   306,  # P306 ＝ 標準：四檔（`replayApplicator` 之介面改為有序變化流 ＋ 標記層不再
                         # 靜默丟棄移除 ＋ 新測試檔 5 支用例）；自動推測誤判為「修補」（字數 3,587
                         # 落在推測門檻內），惟該篇載兩條病灶（移除無從表達於鍵值映射、節流連移除
                         # 一併丟棄）、三項被否決之方案與兩條已知界線（節流之殘餘、逐出標記被重播
                         # 尾端之 pending 清理一併清掉）。型態係按性質判定，非按字數。
                   307,  # P307 ＝ 標準 ×2（併案）：其型態與額度之理由見下方 `MERGED_PHASES` 之登錄
                   308,  # P308 ＝ 標準：五檔（協定之 `switchState` 增延後參數、雙拼執行期之旗標與
                         # 結算、分診入口之結算、退位者改採延後，暨一支新用例），非「1–3 檔、
                         # 零設計」之修補型：其載一條病灶（退位時之投機刷新必被同輪之下筆覆寫）、
                         # 一條根因（首鍵不落組字器 ⇒ 顯示之刷新全靠切態）、三項被否決之方案
                         # （不切態而由 Session 比對、令首鍵落地、素材空即不切態）與一項實作中
                         # 踩到之陷阱（`IMEState.tooltip` 係空字串而非 `nil`）；自動推測誤判為
                         # 「修補」（字數 3,608 落在推測門檻內）。型態按性質判定，非按字數。
                         # （事主將浮動組字窗一項併入同一 phase）。
                   311,  # P311 ＝ 標準：六檔（狀態層之 provisional 標記與兩枚工廠、`switchState` 之
                         # 帶過與落筆受抑、輪末結算、生產者之收尾，暨兩支新用例），非「1–3 檔、
                         # 零設計」之修補型：其載一條病灶（延後之憑據住會話參數與 handler 旗標
                         # ⇒ 狀態一經強制轉換即失據）、一條根因（結算懸於分診入口 ⇒ 早退即不
                         # 結算）、一項取捨（標記住狀態而型別仍正規化為 `.ofEmpty`，捨「保留
                         # `.ofAbortion`」一途）與兩條界線；自動推測誤判為「修補」（字數 2,980
                         # 落在推測門檻內）。型態按性質判定，非按字數。
                   312}  # P312 ＝ 標準：兩檔（`candidateWindowOriginInfo()` 之翻轉量避讓 PCB ＋ 一支
                         # 新用例），非「1–3 檔、零設計」之修補型：其載一條病灶（翻轉後之底緣
                         # 恰落打字列頂端，而橫排之浮動組字窗自打字列底緣向上生長 ⇒ 兩者必咬）、
                         # 一項取捨（抬翻轉量而捨移組字窗／改回傳避讓矩形——後者須動 `Shared`
                         # 協定與兩實作）與三條界線（`delta` 只在翻轉分支被讀、直排不與、上限
                         # 100 點之由）；自動推測誤判為「修補」（字數落在 4,000 門檻內）。
                         # 型態按性質判定，非按字數。

# 併案之 phase：原已按性質登錄於上表，其事後經事主將另一病灶併入同一 phase ⇒ 6,000。
MERGED_PHASES = {307}  # P307 ＝ 標準 ×2（併案）：原案為會話層之啟用路徑陳跡收斂（`SessionProtocol`
                       # 之三處直接賦值各補素材之丟棄與客體內文組字區之清空 ＋ 兩支新用例，其一係
                       # 既有語義之釘樁）；事主續將浮動組字窗（Darwin 側 `PopupCompositionBuffer`）
                       # 之「遲到之收合請求收掉剛顯之窗」併入同一 phase，遂增協定之
                       # `isRetainedOnCloseRequest` 與第三支用例。兩病灶各載一條關鍵不變量、一項取捨
                       # （捨遞交而取丟棄）、數項被否決之方案（`updateCompositionBufferDisplay()`、
                       # `switchState(.ofEmpty())`、於雙拼層拒收待配首鍵期間之數字）與一項經事主實測
                       # 否證之假說（聲調鍵之說——`9` 非聲調鍵亦然）；5,840 chars 係兩案之總和，
                       # 型態按性質判定，非按字數。

BUDGET_OVERRIDES = dict([(p, 8000) for p in LARGE_PHASES]
                        + [(p, 5000) for p in STANDARD_PHASES]
                        + [(p, 6000) for p in MERGED_PHASES])


def budget_for(phase, chars):
    """回傳 (額度, 型態名)。"""
    if phase in BUDGET_OVERRIDES:
        lim = BUDGET_OVERRIDES[phase]
        name = {2500: "修補", 5000: "標準", 6000: "標準", 8000: "大型"}[lim]
        return lim, name
    if chars <= 4000:
        return BUDGETS["patch"], "修補"
    if chars <= 12000:
        return BUDGETS["standard"], "標準"
    return BUDGETS["large"], "大型"

PHASE_RE = re.compile(r"^# Phase (\d+)", re.M)
HEADING_RE = re.compile(r"^(#{2,4}) ")
TAIL_SEP_RE = re.compile(r"\n+-{3,}\s*$")
RULE_RE = re.compile(r"-{3,}")
MEMO_PHASE_ENTRY_RE = re.compile(r"^- \*\*.*?Phase \d+.*?已完工")


def find_workspace(start):
    """自 start 往上找含 vChewing-DevLogs 之目錄。"""
    cur = os.path.abspath(start)
    while True:
        cand = os.path.join(cur, "vChewing-DevLogs", "Reqs4LLM")
        if os.path.isdir(cand):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent


def repo_root(start):
    here = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(here) == "Tools" and os.path.isdir(os.path.join(os.path.dirname(here), "Reqs4LLM")):
        return os.path.dirname(here)
    ws = find_workspace(start)
    if ws:
        return os.path.join(ws, "vChewing-DevLogs")
    return None


def split_phases(text):
    """回傳 [(phase:int, title_line:str, body:str)]，body 含標題行。"""
    marks = list(PHASE_RE.finditer(text))
    out = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        out.append((int(m.group(1)), m.group(0).strip(), text[m.start():end]))
    return out


def sections(body):
    """回傳 [(heading_line, chunk)]，以 2–4 級標題切。"""
    lines = body.split("\n")
    idx = [i for i, l in enumerate(lines) if HEADING_RE.match(l)]
    out = []
    for k, i in enumerate(idx):
        end = idx[k + 1] if k + 1 < len(idx) else len(lines)
        out.append((lines[i], "\n".join(lines[i:end])))
    return out


def current_volume_first_phase(root):
    """依 `KnowledgeMemo4LLM.md` 文首〈Reqs4LLM 分卷歸檔註記〉所定之規則，現算現行卷之首 Phase。
    （實作只走檔案系統，不讀該檔內文——故本函式不隨該檔之拆分而變。）"""
    vols = []
    for dirpath, _d, files in os.walk(os.path.join(root, "Reqs4LLM")):
        for fn in files:
            m = re.match(r"^Reqs_(\d{4})-(\d{4})\.md$", fn)
            if m:
                vols.append((int(m.group(1)), os.path.join(dirpath, fn)))
    if not vols:
        return 0
    vols.sort()
    lo, path = vols[-1]
    n = len(PHASE_RE.findall(io.open(path, encoding="utf-8").read()))
    if n >= 10:                       # 末卷已滿 ⇒ 現行卷為其後繼
        return lo + 10
    marks = sorted(int(x) for x in PHASE_RE.findall(io.open(path, encoding="utf-8").read()))
    return marks[0] if marks else lo


def audit_reqs(root, since=0):
    rows = []
    vols = os.path.join(root, "Reqs4LLM")
    for dirpath, _dirs, files in os.walk(vols):
        for fn in sorted(files):
            if not re.match(r"^Reqs_0\d{2,3}-\d{4}\.md$", fn):
                continue
            path = os.path.join(dirpath, fn)
            text = io.open(path, encoding="utf-8").read()
            src = text.split("\n")
            heading_at = {}
            for k, l in enumerate(src):
                m = re.match(r"^# Phase (\d+)", l)
                if m:
                    heading_at[int(m.group(1))] = k
            first_heading = min(heading_at.values()) if heading_at else None
            for phase, _title, body in split_phases(text):
                if phase < since:
                    continue
                # 量「該 Phase 篇本身」之 chars：去尾部分隔線後，補回一個換行
                # （與獨立檔 len(open(...).read()) 同義；§12.7.3 之預算即以此計）。
                core = TAIL_SEP_RE.sub("", body).rstrip("\n")
                chars = len(core) + 1
                # §12.7.4：Phase 篇之內部不得有任何以連續 `-` 組成之段落分割線。
                rules = [l for l in core.split("\n") if RULE_RE.fullmatch(l)]
                # §12.7.4：卷際分隔線＝`--------------------`（恰 20 連字號），置於 `# Phase NNN`
                # 之上一行，且其上下各一空行；該卷之首篇不設（其前無 Phase）。
                i = heading_at.get(phase)
                boundary = None
                if i is not None and i != first_heading:
                    boundary = (i >= 2 and src[i - 1].strip() == "" and src[i - 2] == "-" * 20)
                rituals = {}
                for name, rx in RITUALS.items():
                    hits = [h for h, _c in sections(body) if re.search(rx, h)]
                    if hits:
                        rituals[name] = len(hits)
                rows.append({
                    "phase": phase,
                    "volume": os.path.relpath(path, root),
                    "chars": chars,
                    "headings": len([1 for l in body.split("\n") if HEADING_RE.match(l)]),
                    "rituals": rituals,
                    "rules": len(rules),
                    "boundary": boundary,
                })
    return rows


def audit_history(root):
    path = os.path.join(root, "DevReqsHistory.md")
    text = io.open(path, encoding="utf-8").read()
    rows = []
    for line in text.split("\n"):
        m = re.match(r"^\|\s*Phase\s*(\d+)\s*\|", line)
        if m:
            rows.append({"phase": int(m.group(1)), "chars": len(line)})
    return rows, len(text)


def list_sub_articles(root):
    """回傳 [(檔名, chars, 內容)]，即 KnowledgeMemo4LLM.md 之各分卷（依檔名遞增）。"""
    sd = os.path.join(root, SUB_ARTICLES_DIR)
    out = []
    if not os.path.isdir(sd):
        return out
    for fn in sorted(os.listdir(sd)):
        if not fn.endswith(".md"):
            continue
        text = io.open(os.path.join(sd, fn), encoding="utf-8").read()
        out.append((fn, len(text), text))
    return out


def audit_memo(root):
    path = os.path.join(root, "KnowledgeMemo4LLM.md")
    text = io.open(path, encoding="utf-8").read()
    head = text.split("\n## ", 1)[0]
    entries = [l for l in text.split("\n") if MEMO_PHASE_ENTRY_RE.match(l)]
    blocks = [l for l in text.split("\n") if l.startswith("- **") and ("狂打" in l or "之注音化" in l)]
    subs = list_sub_articles(root)
    for _fn, _chars, st in subs:
        entries += [l for l in st.split("\n") if MEMO_PHASE_ENTRY_RE.match(l)]
        blocks += [l for l in st.split("\n") if l.startswith("- **") and ("狂打" in l or "之注音化" in l)]
    rows = sorted([{"name": fn, "chars": c} for fn, c, _ in subs], key=lambda r: -r["chars"])
    return {
        "chars": len(text),
        "bytes": len(text.encode("utf-8")),
        "head_chars": len(head) + head.count("\n"),
        "phase_entries": len(entries),
        "phase_entry_chars": sum(len(l) + 1 for l in entries),
        "furious_blocks": len(blocks),
        "furious_block_chars": sum(len(l) + 1 for l in blocks),
        "sub_articles": rows,
        "sub_chars": sum(r["chars"] for r in rows),
        "sub_over": [r for r in rows if r["chars"] > SUB_ARTICLE_MAX],
    }


def run(root, since=0):
    reqs = audit_reqs(root, since)
    hist, hist_chars = audit_history(root)
    memo = audit_memo(root)
    hist = [r for r in hist if r["phase"] >= since]
    return {"reqs": reqs, "history": hist, "history_chars": hist_chars, "memo": memo,
            "enforce_from": since}


def report(data, since=0):
    over = []
    print("═══ Reqs 卷之 Phase 篇（預算：修補 %d／標準 %d／大型 %d chars；判斷起點 P%d）═══"
          % (BUDGETS["patch"], BUDGETS["standard"], BUDGETS["large"], since))
    reqs = sorted(data["reqs"], key=lambda r: -r["chars"])
    n_legacy = 0
    for r in reqs:
        if r["phase"] < since:
            if r["chars"] > BUDGETS["large"] or any(v > RITUAL_ONCE_MAX for v in r["rituals"].values()):
                n_legacy += 1
            continue
        flag = ""
        lim, kind = budget_for(r["phase"], r["chars"])
        if r["chars"] > lim:
            flag = "  ← 逾%s預算 %.2f×" % (kind, r["chars"] / lim)
        rit = ""
        bad = {k: v for k, v in r["rituals"].items() if v > RITUAL_ONCE_MAX}
        if bad:
            rit = "  儀式重複：" + "、".join("%s×%d" % (k, v) for k, v in sorted(bad.items()))
        if r.get("rules"):
            rit += "  ← 篇內橫線 %d 條（§12.7.4 所禁）" % r["rules"]
        if r.get("boundary") is False:
            rit += "  ← 卷際分隔線不合規（須 20 連字號、上下各一空行）"
        print("  P%-4d %7d chars  %2d 小節  %s%s%s" % (r["phase"], r["chars"], r["headings"], r["volume"], flag, rit))
        if flag:
            over.append("P%d（%d chars）" % (r["phase"], r["chars"]))
        if bad:
            over.append("P%d 儀式重複" % r["phase"])
        if r.get("rules"):
            over.append("P%d 篇內橫線 %d 條" % (r["phase"], r["rules"]))
        if r.get("boundary") is False:
            over.append("P%d 卷際分隔線不合規" % r["phase"])

    if n_legacy:
        print("  （另有 %d 個歷史 phase 逾預算——`legacy（不判）`，見 §12.7.6）" % n_legacy)
    print()
    print("═══ DevReqsHistory.md（每列 ≤ %d chars；判斷起點 P%d）═══" % (HISTORY_ROW_MAX, since))
    for r in sorted([x for x in data["history"] if x["phase"] >= since], key=lambda x: -x["chars"])[:15]:
        flag = "  ← 逾 %.1f×" % (r["chars"] / HISTORY_ROW_MAX) if r["chars"] > HISTORY_ROW_MAX else ""
        print("  P%-4d %6d chars%s" % (r["phase"], r["chars"], flag))
        if flag:
            over.append("DevReqsHistory P%d 列（%d chars）" % (r["phase"], r["chars"]))
    print("  全檔 %d chars；本段 %d 列" % (data["history_chars"], len(data["history"])))

    print()
    m = data["memo"]
    print("═══ KnowledgeMemo4LLM.md ═══")
    print("  全檔 %d chars / %d bytes" % (m["chars"], m["bytes"]))
    print("  索引開頭部 %d chars；逐 Phase 記述 %d 條、%d chars（索引與各分卷合計）"
          % (m["head_chars"], m["phase_entries"], m["phase_entry_chars"]))
    print("  狂打相關區塊 %d 條、%d chars" % (m["furious_blocks"], m["furious_block_chars"]))
    if MEMO_HEAD_FORBIDDEN and m["phase_entries"]:
        over.append("KnowledgeMemo（索引或分卷）仍有 %d 條逐 Phase 記述" % m["phase_entries"])

    if m["sub_articles"]:
        print()
        print("═══ %s/（每卷 ≤ %d chars）═══" % (SUB_ARTICLES_DIR, SUB_ARTICLE_MAX))
        for r in m["sub_articles"]:
            flag = "  ← 逾 %.2f×" % (r["chars"] / SUB_ARTICLE_MAX) if r["chars"] > SUB_ARTICLE_MAX else ""
            print("  %-44s %6d chars%s" % (r["name"], r["chars"], flag))
            if flag:
                over.append("%s（%d chars）" % (r["name"], r["chars"]))
        print("  共 %d 卷、%d chars（均 %d）"
              % (len(m["sub_articles"]), m["sub_chars"], m["sub_chars"] // len(m["sub_articles"])))

    print()
    if over:
        print("✗ 超標 %d 項：" % len(over))
        for o in over[:40]:
            print("   -", o)
    else:
        print("✓ 全數在預算內。")
    return 1 if over else 0


def self_test():
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.join(tmp, "vChewing-DevLogs")
        os.makedirs(os.path.join(root, "Reqs4LLM", "Archive_P201-P300"))
        vol = os.path.join(root, "Reqs4LLM", "Archive_P201-P300", "Reqs_0251-0260.md")

        # 紅：超預算 ＋ 儀式重複 ＋ 篇內橫線
        bad = "# Phase 251\n\n" + ("x" * 100 + "\n") * 90
        bad += "## 六、§8.0.1 之執行記錄\n### 8.1 第 1 步：對帳\n" + "y\n" * 5
        bad += "## 七、§8.0.1 之執行記錄\n### 7.1 第 1 步：對帳\n" + "z\n" * 5
        bad += "---\n\n## 八、篇內橫線\n"
        io.open(vol, "w", encoding="utf-8").write(bad)
        io.open(os.path.join(root, "DevReqsHistory.md"), "w", encoding="utf-8").write(
            "| Phase 251 | " + "a" * 400 + " |\n")
        io.open(os.path.join(root, "KnowledgeMemo4LLM.md"), "w", encoding="utf-8").write(
            "# T\n\n- **狂打模式之注音化：**Phase 251 已完工（2026-09-26）——敘述。\n\n## 一、專案概述\n")
        os.makedirs(os.path.join(root, SUB_ARTICLES_DIR))
        io.open(os.path.join(root, SUB_ARTICLES_DIR, "00-Oversized.md"), "w", encoding="utf-8").write(
            "# 過大之分卷\n\n" + ("w" * 100 + "\n") * (SUB_ARTICLE_MAX // 100 + 5))
        d = run(root, 251)
        red = (d["reqs"][0]["chars"] > BUDGETS["large"]
               and sum(1 for v in d["reqs"][0]["rituals"].values() if v > RITUAL_ONCE_MAX) >= 1
               and any(x["chars"] > HISTORY_ROW_MAX for x in d["history"])
               and d["memo"]["phase_entries"] == 1
               and d["reqs"][0]["rules"] == 1
               and len(d["memo"]["sub_over"]) == 1)
        print("紅驗：超預算／儀式重複／History 超長／Memo 逐 Phase 記述／篇內橫線／分卷過大 —— %s"
              % ("偵得" if red else "★漏檢★"))
        ok &= red

        # 綠：全數合規（含表格表頭之 `|---|` 不得誤判為橫線）
        io.open(vol, "w", encoding="utf-8").write(
            "# Phase 251\n\n## 手術範圍\n\n|---|------|\n| a | b |\n\n## 未動\n\n短。\n")
        io.open(os.path.join(root, "DevReqsHistory.md"), "w", encoding="utf-8").write(
            "| Phase 251 | 短摘要。 |\n")
        io.open(os.path.join(root, "KnowledgeMemo4LLM.md"), "w", encoding="utf-8").write(
            "# T\n\n- 本文檔供 AI Agent 參考。\n\n## 一、專案概述\n")
        io.open(os.path.join(root, SUB_ARTICLES_DIR, "00-Oversized.md"), "w", encoding="utf-8").write(
            "# 合規之分卷\n\n短。\n")
        d = run(root, 251)
        green = (d["reqs"][0]["chars"] <= BUDGETS["large"]
                 and all(v <= RITUAL_ONCE_MAX for v in d["reqs"][0]["rituals"].values())
                 and all(x["chars"] <= HISTORY_ROW_MAX for x in d["history"])
                 and d["memo"]["phase_entries"] == 0
                 and d["memo"]["sub_over"] == []
                 and d["reqs"][0]["rules"] == 0)
        print("綠驗：合規樣本不誤報（表格表頭、分卷不誤判） —— %s" % ("通過" if green else "★誤報★"))
        ok &= green
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="DevLogs 記述預算稽核（House Style audit）")
    ap.add_argument("--since", type=int, default=0, help="只列出 Phase >= N（預設全部列出）")
    ap.add_argument("--enforce-from", type=int, default=None,
                    help="預算之判斷起點（預設＝現行卷之首 Phase）")
    ap.add_argument("--all-history", action="store_true", help="連歷史卷一併判（嚴苛模式）")
    ap.add_argument("--quiet", action="store_true", help="只在有超標時輸出")
    ap.add_argument("--json", action="store_true", help="輸出 JSON")
    ap.add_argument("--self-test", action="store_true", help="以臨時檔紅綠雙驗")
    ap.add_argument("--repo-root", default=None, help="vChewing-DevLogs 之路徑")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(self_test())

    root = args.repo_root or repo_root(os.getcwd())
    if not root or not os.path.isfile(os.path.join(root, "KnowledgeMemo4LLM.md")):
        print("找不到 vChewing-DevLogs；請以 --repo-root 指定，或自工作區內執行。", file=sys.stderr)
        sys.exit(2)

    if args.all_history:
        enforce = 0
    elif args.enforce_from is not None:
        enforce = args.enforce_from
    else:
        enforce = max(current_volume_first_phase(root), HOUSESTYLE_EPOCH_PHASE)

    data = run(root, args.since, )
    data["enforce_from"] = enforce
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        sys.exit(0)
    if args.quiet:
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        code = report(data, enforce)
        sys.stdout = old
        if code:
            print("✗ DevLogs 記述預算稽核：現行卷起有超標項。以 `python3 Tools/housestyle_audit.py` 看明細。")
        sys.exit(code)
    sys.exit(report(data, enforce))


if __name__ == "__main__":
    main()
