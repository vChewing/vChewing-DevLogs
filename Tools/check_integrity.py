#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""唯音工作區之檔案完整性絆線（truncation tripwire）。

**事由**（2026-09-25，Phase 245 之施工事故）：以 Python 就地改檔時，一行無心的
`io.open(path, "w")`（開檔即截斷、其後未寫入）會把整份檔案清成 0 bytes——同一輪內
發生兩次：第一次僥倖被 `git checkout` 救回，第二次才被 `make typecheck` 的
「Cannot find name …」成堆錯誤抓到。此類事故之共同特徵是**靜默**：截斷當下沒有任何
徵兆，要等下一個讀它的工具（編譯器、測試、建置器）才引爆——而若那個檔案其時沒有
任何工具在讀它（例如只在某條罕用路徑上被讀），就可能一路帶進 commit。

**本檔即為此類事故之絆線**：比對工作區與 `HEAD` 之每一份受版控檔案的大小——

* **CRITICAL**：`HEAD` 有內容（> 0 bytes）而工作區該檔為 **0 bytes** ⇒ 幾乎必為截斷。
* **WARN**：較 `HEAD` 縮小逾 `--shrink-ratio`（預設 70%）且縮掉逾 `--shrink-min`
  （預設 200 bytes）⇒ 疑似意外大量刪除（正常之編輯刪減不至於如此，但大重構會）。
* **MISSING**：`HEAD` 有、工作區無 ⇒ 只是一般的刪除，僅列出（不算失敗）。

**用法**：

    python3 check_integrity.py                     # 掃描工作區內所有 git 倉
    python3 check_integrity.py --repo-root DIR     # 只掃 DIR 這一個倉（供 git hook 用）
    python3 check_integrity.py --strict            # WARN 也算失敗（exit 1）
    python3 check_integrity.py --quiet             # 只在有問題時輸出
    python3 check_integrity.py --self-test         # 以臨時倉自我驗證（紅綠雙驗）
    python3 check_integrity.py --install-hooks     # 將本絆線裝進各倉之 pre-commit

**安裝為 git hook 之後**：各倉之每次 commit 都會先跑本絆線（僅掃該倉）。若確實要
在明知有 0-byte 受版控檔（例如刻意新增之空檔）時提交，可用
`SKIP_INTEGRITY=1 git commit …` 略過。
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

def default_workspace():
    """工作區根：本檔所在之倉（vChewing-DevLogs）之上層目錄。

    以 `realpath` 解析 symlink——工作區根部有同名 symlink，`python3 check_integrity.py`
    之 `__file__` 會是那條捷徑而非本檔之真身。
    """
    here = os.path.dirname(os.path.realpath(__file__))   # …/vChewing-DevLogs/Tools
    repo = os.path.dirname(here)                          # …/vChewing-DevLogs
    workspace = os.path.dirname(repo)                     # …/_MainWorkspace
    if find_repos(workspace):
        return workspace
    # 後備：自本檔往上找第一個含 git 倉之目錄（本檔被複製而非 symlink 時）。
    probe = here
    for _ in range(5):
        probe = os.path.dirname(probe)
        if probe and find_repos(probe):
            return probe
    return workspace


# 掃描時略過之目錄（建置產物、暫存、其他 harness 之工作區…）。
SKIP_DIR_NAMES = {
    ".git", ".build", "Build", "node_modules", "dist", "tmp",
    "_MainWorkspace_tmp", "_ResearchScratch", ".codewhale", ".codewhale-worktrees",
    ".DS_Store", "DerivedData", ".swiftpm",
}

CRITICAL = "CRITICAL"
WARN = "WARN"
MISSING = "MISSING"


def run_git(repo, args):
    """在該倉執行 git；回傳 stdout（失敗則擲錯）。"""
    proc = subprocess.run(
        ["git", "-C", repo] + args,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "git %s 於 %s 失敗：%s" % (" ".join(args), repo, proc.stderr.decode("utf-8", "replace").strip())
        )
    return proc.stdout.decode("utf-8", "replace")


def is_repo(path):
    """該目錄是否為 git 倉（worktree 之 `.git` 是檔案，故不以目錄判斷）。"""
    return os.path.exists(os.path.join(path, ".git"))


def find_repos(workspace):
    """取工作區內之各 git 倉（一層深）。"""
    repos = []
    if is_repo(workspace):
        repos.append(workspace)
        return repos
    for name in sorted(os.listdir(workspace)):
        path = os.path.join(workspace, name)
        if not os.path.isdir(path) or name in SKIP_DIR_NAMES:
            continue
        if is_repo(path):
            repos.append(path)
    return repos


def head_sizes(repo):
    """`HEAD` 內各 blob 之大小：{相對路徑: bytes}。

    以 `git ls-tree -r -l` 一次取得（一個行程、不做逐檔 subprocess）；
    `core.quotePath=false` 令非 ASCII 之路徑原樣輸出（否則會被反斜線轉義）。
    """
    out = run_git(repo, ["-c", "core.quotePath=false", "ls-tree", "-r", "-l", "HEAD"])
    sizes = {}
    for line in out.splitlines():
        if not line.strip():
            continue
        meta, _, path = line.partition("\t")
        parts = meta.split()
        if len(parts) < 4:
            continue
        kind, size_text = parts[1], parts[3]
        if kind != "blob":
            continue
        try:
            sizes[path] = int(size_text)
        except ValueError:
            continue  # 子模組（gitlink）之大小為 "-"
    return sizes


def check_repo(repo, shrink_ratio, shrink_min):
    """掃一個倉；回傳 findings（每項為 dict）。"""
    findings = []
    sizes = head_sizes(repo)
    for path in sorted(sizes):
        head_size = sizes[path]
        full = os.path.join(repo, path)
        if not os.path.exists(full):
            findings.append({"level": MISSING, "path": path, "head": head_size, "work": None})
            continue
        work_size = os.path.getsize(full)
        if head_size > 0 and work_size == 0:
            findings.append({"level": CRITICAL, "path": path, "head": head_size, "work": 0})
            continue
        if head_size >= shrink_min:
            lost = head_size - work_size
            if work_size < head_size * (1.0 - shrink_ratio) and lost >= shrink_min:
                findings.append({"level": WARN, "path": path, "head": head_size, "work": work_size})
    return findings


def report(repo, findings, quiet, total):
    """輸出單一倉之結果；回傳 (critical, warn) 之數。"""
    critical = [f for f in findings if f["level"] == CRITICAL]
    warnings = [f for f in findings if f["level"] == WARN]
    missing = [f for f in findings if f["level"] == MISSING]
    name = os.path.basename(repo.rstrip("/"))
    # 靜默模式下，刪除檔（工作中極常見）不列印；有 CRITICAL／WARN 時一律列印。
    show_missing = missing and not quiet
    if not quiet or critical or warnings or show_missing:
        print("== %s" % name)
        for f in critical:
            print("  %s  %s（HEAD %d bytes → 工作區 0 bytes；幾乎必為截斷）"
                  % (CRITICAL, f["path"], f["head"]))
        for f in warnings:
            print("  %s      %s（HEAD %d bytes → 工作區 %d bytes，縮掉 %d bytes）"
                  % (WARN, f["path"], f["head"], f["work"], f["head"] - f["work"]))
        for f in missing:
            print("  %s   %s（已刪除）" % (MISSING, f["path"]))
        if not critical and not warnings:
            print("  OK（受版控之 %d 檔皆完好）" % total)
    return len(critical), len(warnings)


def cmd_self_test():
    """以臨時倉自我驗證：正常檔綠、截斷檔紅、刪除檔僅列出。"""
    tmp = tempfile.mkdtemp(prefix="integrity-selftest-")
    failures = []
    try:
        repo = os.path.join(tmp, "sample")
        os.makedirs(repo)
        run_git(repo, ["init", "-q"])
        run_git(repo, ["config", "user.email", "selftest@example.com"])
        run_git(repo, ["config", "user.name", "selftest"])
        good = os.path.join(repo, "good.txt")
        victim = os.path.join(repo, "victim.txt")
        deleted = os.path.join(repo, "deleted.txt")
        with open(good, "w", encoding="utf-8") as handle:
            handle.write("x" * 5000)
        with open(victim, "w", encoding="utf-8") as handle:
            handle.write("y" * 5000)
        with open(deleted, "w", encoding="utf-8") as handle:
            handle.write("z" * 5000)
        run_git(repo, ["add", "-A"])
        run_git(repo, ["commit", "-q", "-m", "sample"])

        # ① 綠：三檔皆完好。
        findings = check_repo(repo, 0.7, 200)
        if any(f["level"] in (CRITICAL, WARN) for f in findings):
            failures.append("完好之倉竟報 CRITICAL／WARN：%s" % findings)

        # ② 紅：截斷 victim.txt。
        with open(victim, "w", encoding="utf-8"):
            pass
        findings = check_repo(repo, 0.7, 200)
        critical = [f for f in findings if f["level"] == CRITICAL]
        if [f["path"] for f in critical] != ["victim.txt"]:
            failures.append("截斷未被判為 CRITICAL：%s" % findings)

        # ③ 橙：大幅縮減而未歸零。
        with open(victim, "w", encoding="utf-8") as handle:
            handle.write("y" * 100)
        findings = check_repo(repo, 0.7, 200)
        warnings = [f for f in findings if f["level"] == WARN]
        if [f["path"] for f in warnings] != ["victim.txt"]:
            failures.append("大幅縮減未被判為 WARN：%s" % findings)

        # ④ 刪除僅列出、不判失敗。
        shutil.copyfile(victim, os.path.join(tmp, "victim.bak"))
        os.remove(deleted)
        findings = check_repo(repo, 0.7, 200)
        if not any(f["level"] == MISSING and f["path"] == "deleted.txt" for f in findings):
            failures.append("刪除未被列出：%s" % findings)
        if any(f["level"] == CRITICAL for f in findings):
            failures.append("刪除竟被判為 CRITICAL：%s" % findings)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if failures:
        for line in failures:
            print("SELFTEST FAIL: %s" % line)
        return 1
    print("SELFTEST PASS：完好檔綠、截斷檔 CRITICAL、大幅縮減 WARN、刪除僅列出。")
    return 0


def cmd_install_hooks(repos, script_path):
    """將本絆線裝進各倉之 `.git/hooks/pre-commit`（可重複執行）。"""
    hook = """#!/bin/sh
# 唯音工作區之檔案完整性絆線（由 vChewing-DevLogs/Tools/check_integrity.py --install-hooks 安裝）。
# 略過之法：SKIP_INTEGRITY=1 git commit …
if [ "${SKIP_INTEGRITY:-0}" = "1" ]; then exit 0; fi
exec python3 %s --repo-root "$(git rev-parse --show-toplevel)" --quiet
""" % shlex_quote(script_path)
    installed = []
    for repo in repos:
        # worktree 之 .git 是檔案（指向真正的 git 目錄），此時 hooks 由 git 自行解析。
        common = run_git(repo, ["rev-parse", "--git-common-dir"]).strip()
        if not os.path.isabs(common):
            common = os.path.join(repo, common)
        hooks = os.path.join(os.path.normpath(common), "hooks")
        os.makedirs(hooks, exist_ok=True)
        target = os.path.join(hooks, "pre-commit")
        with open(target, "w", encoding="utf-8") as handle:
            handle.write(hook)
        os.chmod(target, 0o755)
        installed.append(target)
    return installed


def shlex_quote(text):
    """最小限度之 shell 引號（避免引入 shlex 之行為差異）。"""
    return "'" + text.replace("'", "'\"'\"'") + "'"


def main():
    parser = argparse.ArgumentParser(description="唯音工作區之檔案完整性絆線（截斷偵測）")
    parser.add_argument("--workspace", default=None,
                        help="工作區根（預設為本檔所在倉之上層目錄）")
    parser.add_argument("--repo-root", default=None, help="只掃此倉（供 git hook 用）")
    parser.add_argument("--strict", action="store_true", help="WARN 亦視為失敗")
    parser.add_argument("--quiet", action="store_true", help="只在有問題時輸出")
    parser.add_argument("--shrink-ratio", type=float, default=0.7, help="WARN 之縮減比例門檻")
    parser.add_argument("--shrink-min", type=int, default=200, help="WARN 之最小縮減位元組數")
    parser.add_argument("--self-test", action="store_true", help="以臨時倉自我驗證")
    parser.add_argument("--install-hooks", action="store_true", help="裝進各倉之 pre-commit")
    args = parser.parse_args()

    if args.self_test:
        return cmd_self_test()

    workspace = os.path.abspath(args.workspace or default_workspace())
    repos = [os.path.abspath(args.repo_root)] if args.repo_root else find_repos(workspace)
    if not repos:
        print("找不到任何 git 倉：%s" % workspace)
        return 2

    if args.install_hooks:
        script = os.path.abspath(__file__)
        installed = cmd_install_hooks(repos, script)
        for path in installed:
            print("已安裝 pre-commit：%s" % path)
        return 0

    total_critical = 0
    total_warn = 0
    total_files = 0
    for repo in repos:
        findings = check_repo(repo, args.shrink_ratio, args.shrink_min)
        total = len(head_sizes(repo))
        total_files += total
        critical, warn = report(repo, findings, args.quiet, total)
        total_critical += critical
        total_warn += warn

    print("掃描 %d 倉／%d 份受版控檔案：CRITICAL %d、WARN %d。"
          % (len(repos), total_files, total_critical, total_warn))
    if total_critical > 0:
        print("有檔案被截斷（0 bytes）。請以 `git checkout -- <path>` 還原，或自備份回復。")
        return 1
    if args.strict and total_warn > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
