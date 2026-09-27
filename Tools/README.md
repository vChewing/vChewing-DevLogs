# 唯音工作區之工具（給 AI agent 與人類共用）

本目錄收容「跨倉、與 phase 無關、但少了就會出事」的小工具。兩支皆為**零相依**之
Python 3 單檔（只用標準庫），可直接執行。

| 工具 | 一句話 | 典型用法 |
|---|---|---|
| `check_integrity.py` | **截斷絆線**：比對工作區與 `HEAD` 之每一份受版控檔案大小，凡「HEAD 有內容而工作區為 0 bytes」即 CRITICAL | `python3 check_integrity.py` |
| `safepatch.py` | **安全改檔**：read → 逐字替換 → 原子寫入，附三道守衛（錨點次數、非空結果、不得大幅縮減） | `python3 safepatch.py --file X --old-file /tmp/old --new-file /tmp/new` |
| `housestyle_audit.py` | **記述預算稽核**：量 Reqs 卷各 Phase 篇之字數與儀式重複、`DevReqsHistory` 各列長度、`KnowledgeMemo` 開頭部是否混入逐 Phase 記述 | `python3 housestyle_audit.py`（交差前跑一次） |

工作區根部另有同名之 symlink（`_MainWorkspace/check_integrity.py`、
`_MainWorkspace/safepatch.py`），與既有之 `lint_zhtw.*` 同居，故在根部直接跑即可。

## `housestyle_audit.py`：記述預算

```sh
python3 housestyle_audit.py            # 全倉；列出超標項與統計（exit 1 表有超標）
python3 housestyle_audit.py --since 250
python3 housestyle_audit.py --enforce-from 241   # 複驗 2026-09-27 第二輪回溯之 P241–P261
python3 housestyle_audit.py --quiet    # 只在有超標時出聲
python3 housestyle_audit.py --json
python3 housestyle_audit.py --self-test
```

> `--since N` 只決定**載入哪些 phase**；真正的**判斷起點**是 `--enforce-from N`（或預設之
> `max(現行卷首 phase, HOUSESTYLE_EPOCH_PHASE)`）。要複驗某段範圍，用後者。

**量尺**（規則本體見 `KnowledgeMemo4LLM.md` §12.7；改規則請同步改本檔之 `BUDGETS`）：

- **Reqs 卷之 Phase 篇**：修補型 ≤ 2,500／標準 ≤ 5,000／大型 ≤ 8,000 chars。
- **`DevReqsHistory.md` 各列** ≤ 300 chars（該檔是索引，非第二份正本）。
- **`KnowledgeMemo4LLM.md` 開頭部不得有逐 Phase 記述**（該檔只收「現況」與「施工注意事項」）。
- **儀式小節**（§8.0.1 收尾回檢／兩倉 byte-sync／測試基線／變異測試）同一 phase 內至多一次。
- **分隔線**：`--------------------`（恰 20 連字號）**只准出現於 Phase 分界**；**Phase 篇之內部不得有任何以連續 `-` 組成之段落分割線**（§12.7.4）。表格表頭之 `|---|` 不算橫線，不會誤判。

**型態額度**：§12.7.3 之型態係按 phase 之**性質**（修補／標準／大型），自動量尺無從得知，
故預設以字數推之；已明示型態者登錄於本檔之 `BUDGET_OVERRIDES`（現載 P241–P261 之回溯額度）。
**新 phase 通常不必登記**——預算本容超標，記一行理由即可。

**適用起點＝P262**（§12.7 訂於 2026-09-27、即 P261 完工之後；**P241–P261 已回溯套用**，見 §12.7.6；
P240 及以前列為 `legacy（不判）`，`--all-history` 可改為嚴苛模式）。**它不判內容好壞**——只報「誰超預算、超在哪一份文件」。超標並非一律要改：**超標者須在交差回報中寫明一行理由**。

## 為何要有這兩支

**事由**（2026-09-25，Phase 245 施工事故；同一輪內發生兩次）：以手寫 Python 就地改檔時，
一行無心的 `io.open(path, "w")`（`"w"` 於**開檔當下**即截斷，其後未寫入）把
`ValueAdd/WebConfigAssistant/src/questions.ts`（600 餘行）清成 0 bytes。第一次僥倖以
`git checkout` 救回；第二次才由 `make typecheck` 之成堆「Cannot find name …」抓到。
**危險之處在於靜默**：截斷當下毫無徵兆，要等下一個讀它的工具才引爆——若該檔其時無任何
工具在讀，就可能一路帶進 commit。

## `check_integrity.py`：絆線

```sh
python3 check_integrity.py                  # 掃描工作區內所有 git 倉（一層深）
python3 check_integrity.py --strict         # WARN（大幅縮減）亦視為失敗
python3 check_integrity.py --self-test      # 以臨時倉紅綠雙驗
python3 check_integrity.py --install-hooks  # 裝進各倉之 .git/hooks/pre-commit
```

- **CRITICAL**：`HEAD` > 0 bytes 而工作區為 0 bytes ⇒ 幾乎必為截斷（exit 1）。
- **WARN**：較 `HEAD` 縮小逾 70% 且縮掉逾 200 bytes ⇒ 疑似意外大量刪除（`--strict` 下失敗）。
- **MISSING**：`HEAD` 有、工作區無 ⇒ 一般之刪除，僅列出，不算失敗。

**已裝 git hook**：各倉之每次 commit 皆會先跑本絆線（僅掃該倉）。明知有 0-byte 受版控檔
（例如刻意新增之空檔）而仍要提交時，用 `SKIP_INTEGRITY=1 git commit …` 略過。

> **注意**：`.git/hooks/` 不入版控，故 hook 是「每份 clone 各裝一次」。新機器或新 clone
> 之後跑一次 `python3 check_integrity.py --install-hooks` 即可（可重複執行、會覆寫為當前版本）。
> 以 worktree 工作時，hook 由 `--git-common-dir` 指向之主倉 hooks 目錄統一供應，無須另裝。

**設計取捨**：以 `git ls-tree -r -l HEAD` 一次取齊 `HEAD` 內各 blob 之大小（一個行程，
不做逐檔 subprocess），故 1400 餘檔之工作區掃一遍在彈指之間；只比對**大小**而不比對內容
——本絆線要抓的是「整檔被清空」這一類，而非一般的編輯。

## `safepatch.py`：安全改檔

```sh
# 錨點與替換文字置於檔案內——免得 shell 與 CJK 引號互相折磨
python3 safepatch.py --file src/x.ts --old-file /tmp/old.txt --new-file /tmp/new.txt
python3 safepatch.py --file src/x.ts --old-file /tmp/old.txt --new-file /tmp/new.txt --count 4
python3 safepatch.py --file src/x.ts --old-file /tmp/old.txt --new-file /tmp/new.txt --dry-run
python3 safepatch.py --self-test
```

程式內使用：

```python
import sys
sys.path.insert(0, "<工作區>/vChewing-DevLogs/Tools")
from safepatch import patch_file, write_text

patch_file("src/x.ts", old="…", new="…")     # 多處時 count=N
write_text("src/new.ts", text)                # 新建／整檔覆寫亦同受守衛
```

**三道守衛**（任一不通過即**不寫入**、原檔分毫未動）：

1. 錨點須**恰出現 `count` 次**——避免「以為改了一處、其實改了三處」或「錨點已漂移而根本沒改到」。
2. 結果**不得為空**——直接封殺本檔存在之由（那一類事故）。
3. 結果**不得較原文縮小逾 75%**——除非明示 `--allow-shrink`（大幅刪減請明示意圖）。

寫入一律「同目錄臨時檔 ＋ `os.replace`」（同檔案系統內為原子操作），故中途失敗不會留下
半截檔案；`--self-test` 會一併驗證此點與「被拒時原檔不動」。

## 給 AI agent 之紀律

- 就地改檔**一律**走 `safepatch.py`（或其 `patch_file()`），不要手寫 `open(..., "w")`
  ——`"w"` 是「我要寫」與「現在就清空」之合體，語意與意圖分離正是事故之源。
- 一整輪 patch 之後跑一次 `python3 check_integrity.py`（幾百毫秒），再進建置與測試。
- 兩支工具本身亦有 `--self-test`：改動它們之後請各跑一次。
