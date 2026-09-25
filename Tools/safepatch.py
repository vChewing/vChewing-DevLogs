#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""安全就地改檔（read → 逐字替換 → 原子寫入），附三道守衛。

**事由**（2026-09-25，Phase 245 之施工事故）：以手寫 Python 就地改檔時，一次誤寫
`io.open(path, "w")`（`"w"` 於**開檔當下**即截斷，其後未寫入任何內容）把
`src/questions.ts` 清成 0 bytes。同一輪內發生兩次。手寫 `open(..., "w")` 之危險在於
**語意與意圖分離**：`"w"` 是「我要寫」與「現在就清空」之合體，只要忘了後續的 `write`
就是災難，而且完全靜默。

**本檔即為那條安全路徑**：所有就地改檔一律走 `patch_file()`／`write_text()`——它們
**先讀全文、在記憶體裡替換、確認結果合理，才**以「同目錄臨時檔 ＋ `os.replace`」
原子換上（`os.replace` 在同一檔案系統內為原子操作，故中途失敗不會留下半截檔案）。

**三道守衛**（任一不通過即**不寫入**、原檔分毫未動）：

1. `old` 必須在原文內**恰出現 `count` 次**（預設 1）——避免「以為改了一處、其實改了
   三處」或「錨點已漂移而根本沒改到」。
2. 結果**不得為空**（0 bytes）——直接封殺本文開頭那類事故。
3. 結果**不得較原文縮小逾 `--shrink-ratio`**（預設 75%）——除非明示 `--allow-shrink`
   （正常之編輯刪減不至於如此；要大幅刪減時請明示意圖）。

**用法（命令列）**：

    # 逐字替換（old／new 置於檔案內，免得 shell 與 CJK 引號互相折磨）
    python3 safepatch.py --file src/questions.ts --old-file /tmp/old.txt --new-file /tmp/new.txt
    python3 safepatch.py --file x.ts --old-file /tmp/old.txt --new-file /tmp/new.txt --count 4
    python3 safepatch.py --file x.ts --old-file /tmp/old.txt --new-file /tmp/new.txt --dry-run
    python3 safepatch.py --self-test        # 驗證三道守衛與原子性（紅綠雙驗）

**用法（程式內）**：

    import sys; sys.path.insert(0, "<工作區>/vChewing-DevLogs/Tools")
    from safepatch import patch_file, write_text
    patch_file("src/x.ts", old="…", new="…")          # 多處時 count=N
    write_text("src/new.ts", text)                     # 新建／整檔覆寫亦同受守衛

**回傳值**：`patch_file` 回 `{"path", "replacements", "bytes_before", "bytes_after"}`；
`--dry-run` 時不寫入，僅印出將變動之位元組數。
"""

import argparse
import io
import os
import sys
import tempfile

DEFAULT_SHRINK_RATIO = 0.75


class PatchRefused(Exception):
    """守衛攔下之改動（原檔未動）。"""


def read_text(path):
    with io.open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def write_text(path, text, allow_empty=False, allow_shrink=False):
    """以原子換檔寫入整份文字；回傳變動報告。

    `allow_empty`／`allow_shrink` 只在**明確知悉後果**時使用（例如刻意清空一個檔案）。
    """
    if text is None:
        raise PatchRefused("拒絕寫入 None")
    if not allow_empty and len(text) == 0:
        raise PatchRefused("拒絕寫入空內容（%s）——此即 2026-09-25 事故之形態" % path)
    before = os.path.getsize(path) if os.path.exists(path) else 0
    result = text.encode("utf-8")
    if not allow_shrink and before > 0 and len(result) < before * DEFAULT_SHRINK_RATIO:
        raise PatchRefused(
            "拒絕寫入：%s 由 %d bytes 縮至 %d bytes（逾 %.0f%%）；如係刻意，請用 allow_shrink"
            % (path, before, len(result), (1 - DEFAULT_SHRINK_RATIO) * 100)
        )
    directory = os.path.dirname(os.path.abspath(path)) or "."
    handle = tempfile.NamedTemporaryFile(
        mode="wb", dir=directory, prefix=".safepatch-", delete=False
    )
    try:
        handle.write(result)
        handle.flush()
        os.fsync(handle.fileno())
        handle.close()
        os.chmod(handle.name, 0o644)
        os.replace(handle.name, path)
    except BaseException:
        try:
            os.unlink(handle.name)
        except OSError:
            pass
        raise
    return {"path": path, "bytes_before": before, "bytes_after": len(result)}


def patch_file(path, old, new, count=1, allow_shrink=False, allow_empty=False, dry_run=False):
    """把 `path` 內的 `old` 逐字換成 `new`（恰 `count` 處），原子寫回。

    三道守衛見檔首；任一不通過即擲 `PatchRefused`，**原檔不變**。
    """
    if count < 1:
        raise PatchRefused("count 須 >= 1")
    if len(old) == 0:
        raise PatchRefused("old 不得為空字串（那等於無錨點）")
    text = read_text(path)
    found = text.count(old)
    if found != count:
        raise PatchRefused(
            "拒絕改動：%s 內之錨點出現 %d 次，與 --count %d 不符（錨點已漂移？）"
            % (path, found, count)
        )
    updated = text.replace(old, new, count)
    if dry_run:
        return {
            "path": path, "replacements": count, "dry_run": True,
            "bytes_before": len(text.encode("utf-8")), "bytes_after": len(updated.encode("utf-8")),
        }
    report = write_text(path, updated, allow_empty=allow_empty, allow_shrink=allow_shrink)
    report["replacements"] = count
    return report


def cmd_self_test():
    """紅綠雙驗：正常替換綠；三道守衛各自紅；失敗時原檔分毫未動。"""
    failures = []

    def expect_refusal(label, call):
        try:
            call()
        except PatchRefused:
            return
        except Exception as error:  # noqa: BLE001 - 自我測試需報告任何非預期例外
            failures.append("%s：預期 PatchRefused，竟得 %r" % (label, error))
            return
        failures.append("%s：預期 PatchRefused，竟成功" % label)

    tmp = tempfile.mkdtemp(prefix="safepatch-selftest-")
    try:
        target = os.path.join(tmp, "sample.txt")
        with io.open(target, "w", encoding="utf-8") as handle:
            handle.write("alpha\nbeta\ngamma\nbeta\n")

        # ① 綠：正常替換。
        report = patch_file(target, "beta", "BETA", count=2)
        if report["replacements"] != 2 or read_text(target) != "alpha\nBETA\ngamma\nBETA\n":
            failures.append("正常替換之結果不符：%r" % read_text(target))

        # ② 紅：錨點次數不符 ⇒ 拒寫且原檔不變。
        before = read_text(target)
        expect_refusal("錨點次數不符", lambda: patch_file(target, "BETA", "x", count=9))
        if read_text(target) != before:
            failures.append("錨點次數不符時竟動了原檔")

        # ③ 紅：結果為空 ⇒ 拒寫且原檔不變（本檔存在之由）。
        expect_refusal("空結果", lambda: patch_file(target, before, ""))
        if read_text(target) != before:
            failures.append("空結果被拒之後竟動了原檔")

        # ④ 紅：大幅縮減 ⇒ 拒寫；明示 allow_shrink 則放行。
        expect_refusal("大幅縮減", lambda: patch_file(target, before, "tiny"))
        if read_text(target) != before:
            failures.append("大幅縮減被拒之後竟動了原檔")
        patch_file(target, before, "tiny", allow_shrink=True)
        if read_text(target) != "tiny":
            failures.append("allow_shrink 未放行")

        # ⑤ 紅：write_text 之空內容守衛（此即 `io.open(..., 'w')` 事故之形態）。
        expect_refusal("write_text 空內容", lambda: write_text(target, ""))
        if read_text(target) != "tiny":
            failures.append("write_text 空內容被拒之後竟動了原檔")

        # ⑥ 綠：新建檔案（原不存在）。
        created = os.path.join(tmp, "created.txt")
        write_text(created, "hello")
        if read_text(created) != "hello":
            failures.append("新建檔案失敗")

        # ⑦ 原子性：目錄內不留 .safepatch-* 殘骸。
        leftovers = [n for n in os.listdir(tmp) if n.startswith(".safepatch-")]
        if leftovers:
            failures.append("留下臨時檔：%s" % leftovers)
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    if failures:
        for line in failures:
            print("SELFTEST FAIL: %s" % line)
        return 1
    print("SELFTEST PASS：正常替換綠；錨點不符、空結果、大幅縮減三者皆拒寫且原檔不動；"
          "allow_shrink 放行；新建成功；無臨時檔殘骸。")
    return 0


def main():
    parser = argparse.ArgumentParser(description="安全就地改檔（逐字替換 ＋ 三道守衛 ＋ 原子寫入）")
    parser.add_argument("--file", help="要改的檔案")
    parser.add_argument("--old-file", help="錨點文字所在之檔案（逐位元組照用）")
    parser.add_argument("--new-file", help="替換文字所在之檔案（可為空檔＝刪除該段）")
    parser.add_argument("--count", type=int, default=1, help="錨點應出現之次數（預設 1）")
    parser.add_argument("--allow-shrink", action="store_true", help="明示允許大幅縮減")
    parser.add_argument("--dry-run", action="store_true", help="只報告，不寫入")
    parser.add_argument("--self-test", action="store_true", help="驗證守衛與原子性")
    args = parser.parse_args()

    if args.self_test:
        return cmd_self_test()

    if not args.file or not args.old_file:
        parser.error("需 --file 與 --old-file（或 --self-test）")
    new_text = ""
    if args.new_file:
        new_text = read_text(args.new_file)
    old_text = read_text(args.old_file)
    try:
        report = patch_file(
            args.file, old_text, new_text, count=args.count,
            allow_shrink=args.allow_shrink, dry_run=args.dry_run,
        )
    except PatchRefused as error:
        print("REFUSED: %s" % error)
        return 1
    print("%s %s：替換 %d 處，%d → %d bytes%s" % (
        "DRY-RUN" if args.dry_run else "OK", report["path"], report["replacements"],
        report["bytes_before"], report["bytes_after"],
        "（未寫入）" if args.dry_run else "",
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
