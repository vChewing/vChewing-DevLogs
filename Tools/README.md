# 唯音工作區之工具（給 AI agent 與人類共用）

本目錄收容「跨倉、與 phase 無關、但少了就會出事」的小工具。兩支皆為**零相依**之
Python 3 單檔（只用標準庫），可直接執行。

| 工具 | 一句話 | 典型用法 |
|---|---|---|
| `check_integrity.py` | **截斷絆線**：比對工作區與 `HEAD` 之每一份受版控檔案大小，凡「HEAD 有內容而工作區為 0 bytes」即 CRITICAL | `python3 check_integrity.py` |
| `safepatch.py` | **安全改檔**：read → 逐字替換 → 原子寫入，附三道守衛（錨點次數、非空結果、不得大幅縮減） | `python3 safepatch.py --file X --old-file /tmp/old --new-file /tmp/new` |

工作區根部另有同名之 symlink（`_MainWorkspace/check_integrity.py`、
`_MainWorkspace/safepatch.py`），與既有之 `lint_zhtw.*` 同居，故在根部直接跑即可。

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
