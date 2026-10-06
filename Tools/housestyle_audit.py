#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""唯音工作區之 DevLogs 記述預算稽核（House Style audit）。

**事由**（2026-09-27，P261 之後）：逐 Phase 之記述量自 P200 起翻倍、P240 之後再翻，
至 P250–P261 之時已達每 phase 約 22,700 chars（P160 段為 6,400）——其中大半非「事實」，
而是同批事實在一份 phase 內、以及跨四份文件之間的重複。本稽核即把該預算寫成可執行之量尺：
它**不判內容好壞**，只報「誰超預算、超在哪一份文件」。

**量尺**（規則本體見 `KnowledgeMemo4LLM.md` §12.7；改規則請同步改本檔之 BUDGETS）：

* **Reqs 卷之 Phase 篇**：標準 ≤ 5,000 chars；修補型 ≤ 2,500；大型／系列／規劃 ≤ 8,000。
  本稽核以「該篇佔本卷全部 Phase 之中位數之 K 倍」不判斷，只列字數與超標倍率。
* **`DevReqsHistory.md` 各列**：≤ 300 chars。
* **`KnowledgeMemo4LLM.md` 開頭之逐 Phase 記述**：**不得存在**（該檔只收「現況」與
  「施工注意事項」，見該檔文首〈沿革不再寫入本文檔〉）。本稽核以「開頭部（首個 `## ` 之前）
  有無 `- **…Phase NNN…已完工` 形之條目」偵測之。
* **儀式小節**：`§8.0.1 三步`（對帳／回寫本文／重排後續）、`兩倉 byte-sync`、
  `測試基線之同框對照`、`變異測試` 四類——**不得逐 Task 重複**；同一 phase 內出現
  逾一次即列出。

**判與不判**：**預算只管「現行卷之首 Phase 起」**（預設自動判定；可用 `--enforce-from N` 覆寫）。
在此之前之各卷為**已歸檔之歷史記錄**，一律照舊——本稽核只把它們列為 `legacy（不判）`，
不使其左右退出碼。此界線與 `KnowledgeMemo4LLM.md` §12.7.6 之「不回改歷史」一致。

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

# ── 量尺（改這裡即改規則；請與 KnowledgeMemo4LLM.md §12.7 同步）────────────────
BUDGETS = {
    "patch": 2500,     # 修補型：1–3 檔、零設計
    "standard": 5000,  # 標準
    "large": 8000,     # 大型／系列／規劃
}
HISTORY_ROW_MAX = 300          # DevReqsHistory 單列
# §12.7 係 2026-09-27（P261 完工後）訂立 ⇒ 預算自 **P262** 起適用；
# 其前之各卷為「訂立前之歷史記錄」，一律 legacy（不判），與 §12.7.6 之「不回改歷史」一致。
HOUSESTYLE_EPOCH_PHASE = 262
MEMO_HEAD_FORBIDDEN = True     # KnowledgeMemo 開頭部不得有逐 Phase 記述
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
# **P262 起**：作者已於該篇聲明型態者續登錄於此（P262 ＝ 標準：四檔、含兩支新靶與一項落點取捨）。
LARGE_PHASES = {241, 245, 250, 251, 252, 258, 259, 260, 261,      # 大型／系列／規劃 ⇒ 8,000
                286}  # P286 ＝ 大型：25 檔（12 檔裁併為 18 檔）＋ 283 支測試逐支改號與標題
                      # 英文化 ＋ 兩倉同步；自動推測誤判為「修補」（字數 3,790 落在推測門檻
                      # 內），惟該篇載三項病灶、五項被否決之方案與五條界線。
STANDARD_PHASES = {242, 243, 244, 246, 247, 248, 249,                # 標準 ⇒ 5,000
                   253, 254, 255, 256, 257,
                   262, 263, 264, 265, 266, 267,
                   272,  # P272 ＝ 標準：四檔、含五支新靶與兩項落點取捨。
                   274,  # P274 ＝ 標準：四檔（生產碼 3 行 ＋ 2 支回歸靶 ＋ 說明）；自動推測
                         # 誤判為「修補」（3 行生產碼 ⇒ 字數 3,007 落在推測門檻內），
                         # 惟該篇載一項跨 phase 之開關語義（P238／P270／P273）與兩條界線。
                   277,  # P277 ＝ 標準：四檔生產碼（新共用純函式 ＋ 窗頂 pane 與混打 Tooltip
                         # 兩處顯示轉換 ＋ 一處去重）＋ 兩支新靶與四支改寫；自動推測誤判為
                         # 「修補」（字數 3,723 落在推測門檻內），惟該篇載兩項刻意之不對稱
                         # （不問方向／不補陰平）與一項被否決之方案。
                   285,  # P285 ＝ 標準：八檔（兩支新原文 ＋ 產製器擴及四語系 ＋ 說明與 makefile
                         # ＋ 兩份產物重生）；自動推測誤判為「修補」（字數 3,397 落在推測門檻
                         # 內），惟該篇載兩項結構破損之判定、四項被否決之方案與一項證據界線。
                   287,  # P287 ＝ 標準：三檔（生產碼一處 ＋ 兩支新靶）＋ 一項實測排除之假說；
                         # 自動推測誤判為「修補」（字數 3,179 落在推測門檻內），惟該篇載兩項病灶
                         # （投機預覽外洩／原文重複遞交）、一項單點修法之取捨與 PCB 之排除證據。
                   288}  # P288 ＝ 標準：三檔（兩份繪製各一行 ＋ 一支新靶與其離屏掃描器）＋ 一項
                         # 對事主原擬手術目標之偏離（原案經實測不可行，另立等效修法）與其證據；
                         # 自動推測誤判為「修補」（字數 3,341 落在推測門檻內）。
BUDGET_OVERRIDES = dict([(p, 8000) for p in LARGE_PHASES]
                        + [(p, 5000) for p in STANDARD_PHASES])


def budget_for(phase, chars):
    """回傳 (額度, 型態名)。"""
    if phase in BUDGET_OVERRIDES:
        lim = BUDGET_OVERRIDES[phase]
        name = {2500: "修補", 5000: "標準", 8000: "大型"}[lim]
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
    """依 KnowledgeMemo4LLM.md 文首〈Reqs4LLM 分卷歸檔註記〉現算現行卷之首 Phase。"""
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
            for phase, _title, body in split_phases(text):
                if phase < since:
                    continue
                # 量「該 Phase 篇本身」之 chars：去尾部分隔線後，補回一個換行
                # （與獨立檔 len(open(...).read()) 同義；§12.7.3 之預算即以此計）。
                core = TAIL_SEP_RE.sub("", body).rstrip("\n")
                chars = len(core) + 1
                # §12.7.4：Phase 篇之內部不得有任何以連續 `-` 組成之段落分割線。
                rules = [l for l in core.split("\n") if RULE_RE.fullmatch(l)]
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


def audit_memo(root):
    path = os.path.join(root, "KnowledgeMemo4LLM.md")
    text = io.open(path, encoding="utf-8").read()
    head = text.split("\n## ", 1)[0]
    entries = [l for l in head.split("\n") if MEMO_PHASE_ENTRY_RE.match(l)]
    blocks = [l for l in head.split("\n") if l.startswith("- **") and ("狂打" in l or "之注音化" in l)]
    return {
        "chars": len(text),
        "bytes": len(text.encode("utf-8")),
        "head_chars": len(head) + head.count("\n"),
        "phase_entries": len(entries),
        "phase_entry_chars": sum(len(l) + 1 for l in entries),
        "furious_blocks": len(blocks),
        "furious_block_chars": sum(len(l) + 1 for l in blocks),
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
        print("  P%-4d %7d chars  %2d 小節  %s%s%s" % (r["phase"], r["chars"], r["headings"], r["volume"], flag, rit))
        if flag:
            over.append("P%d（%d chars）" % (r["phase"], r["chars"]))
        if bad:
            over.append("P%d 儀式重複" % r["phase"])
        if r.get("rules"):
            over.append("P%d 篇內橫線 %d 條" % (r["phase"], r["rules"]))

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
    print("  開頭部 %d chars；逐 Phase 記述 %d 條、%d chars"
          % (m["head_chars"], m["phase_entries"], m["phase_entry_chars"]))
    print("  狂打相關區塊 %d 條、%d chars" % (m["furious_blocks"], m["furious_block_chars"]))
    if MEMO_HEAD_FORBIDDEN and m["phase_entries"]:
        over.append("KnowledgeMemo 開頭部仍有 %d 條逐 Phase 記述" % m["phase_entries"])

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
        d = run(root, 251)
        red = (d["reqs"][0]["chars"] > BUDGETS["large"]
               and sum(1 for v in d["reqs"][0]["rituals"].values() if v > RITUAL_ONCE_MAX) >= 1
               and any(x["chars"] > HISTORY_ROW_MAX for x in d["history"])
               and d["memo"]["phase_entries"] == 1
               and d["reqs"][0]["rules"] == 1)
        print("紅驗：超預算／儀式重複／History 超長／Memo 逐 Phase 記述／篇內橫線 —— %s"
              % ("偵得" if red else "★漏檢★"))
        ok &= red

        # 綠：全數合規（含表格表頭之 `|---|` 不得誤判為橫線）
        io.open(vol, "w", encoding="utf-8").write(
            "# Phase 251\n\n## 手術範圍\n\n|---|------|\n| a | b |\n\n## 未動\n\n短。\n")
        io.open(os.path.join(root, "DevReqsHistory.md"), "w", encoding="utf-8").write(
            "| Phase 251 | 短摘要。 |\n")
        io.open(os.path.join(root, "KnowledgeMemo4LLM.md"), "w", encoding="utf-8").write(
            "# T\n\n- 本文檔供 AI Agent 參考。\n\n## 一、專案概述\n")
        d = run(root, 251)
        green = (d["reqs"][0]["chars"] <= BUDGETS["large"]
                 and all(v <= RITUAL_ONCE_MAX for v in d["reqs"][0]["rituals"].values())
                 and all(x["chars"] <= HISTORY_ROW_MAX for x in d["history"])
                 and d["memo"]["phase_entries"] == 0
                 and d["reqs"][0]["rules"] == 0)
        print("綠驗：合規樣本不誤報（表格表頭不誤判） —— %s" % ("通過" if green else "★誤報★"))
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
