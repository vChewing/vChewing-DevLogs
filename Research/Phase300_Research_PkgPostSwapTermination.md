# Phase 300 研究：PKG 安裝器之換檔後終止

> 狀態：研究稿（2026-10-11）。本 phase 為 PKG 安裝路徑之硬化；真實驗證待下一次 PKG 換裝。
> 前置：`Research/Phase298_Research_InstallerProcessTermination.md`（App 安裝器之同一病灶與其「換檔後保證刀」之設計）。

## 0. 起因：P298 未及之另一條安裝路徑

- P298（`9f9259d2`）硬化了 App 安裝器，惟其「## 未動」明列 PKG 安裝路徑：`ValueAdd/PKGInstallerAssets/pkgPreInstall.sh` 仍為 `killall … 2>/dev/null || true`。
- PKG 不是旁支：`vChewing-Homebrew/Casks/vchewing.rb:5` 以 `url "https://gitee.com/vChewing/vChewing-macOS/releases/download/#{version}/vChewing-macOS-#{version}-signed.pkg"` 取得安裝包、`:10` 以 `pkg "vChewing-macOS-#{version}-signed.pkg"` 安裝 ⇒ 凡以 Homebrew 安裝唯音者，走的都是這條路徑。
- 病灶與 P298 完全同型：`killall` 位於 payload 抽取**之前**（preinstall），且不看結束碼。IMK 隨選啟動、永遠自「當下磁碟上已註冊之 bundle」拉起 ⇒ 換檔前殺，系統只會把舊碼重新拉起（新 PID、舊碼），恰好躲過其後一切檢查。
- 一項 P298 沒有的變數：`pkg` 安裝（尤其由 Homebrew 觸發）以 **root** 執行安裝腳本 ⇒ 終止手續必須以「console user 之行程」為界，不得動到同一機器上其他已登入使用者之實例。

## 1. 動工前之終止手續（PKG 路徑）

| 落點 | 內容 | 問題 |
|:--|:--|:--|
| `pkgPreInstall.sh:11-12` | `killall "${TARGET}" 2>/dev/null \|\| true`、`killall "${TARGET}PhraseEditor" 2>/dev/null \|\| true` | 送出即忘；位於換檔前；`\|\| true` 連「有沒有殺到」一併吞掉 |
| `pkgPostInstall.sh:47-62` | 換檔後只終止 `TextInputMenuAgent`（root 時經 `su - "${login_user}"`）＋ `sleep 0.5` | 換檔後**無**任何針對輸入法本體之終止手續 |

- 執行序：`preinstall` → payload 抽取 → `postinstall`；且 `pkgPostInstall.sh:14-31` 自身尚把落於系統域（`/Library/Input Methods`）之 payload 搬入 console user 之家目錄 ⇒ **postinstall 才是 P298 之 `postSwap` 對應點**。
- `pkgPostInstall.sh` 之結尾以 console user 身分執行 `"${user_ime_path}/Contents/MacOS/${IME_EXECUTABLE}" install`（`MainSputnik.swift:114` 之 `case "install":` ⇒ `IMKHelper.registerInputMethod()` 後 `exit(exitCode)`）——註冊本身即可能請系統拉起輸入法，故終止區塊必須置於其前。

## 2. 排除項

- 兩支腳本須在裸 macOS 12 之 `/bin/sh` 下執行（`BuildPKG.sh:211-214` 以 `pkgbuild --scripts` 之 `preinstall`／`postinstall` 出貨）：所用工具 `pgrep`／`ps`／`tr`／`killall`／`stat`／`kill` 皆為系統既有，無額外相依。
- 不以 Swift 複用 P298 之實作：`vChewing-macOS/Package.swift:27-38` 之輸入法執行檔 target `vChewing` 只鏈 `MainAssembly4Darwin`；`:39-49` 之 `InstallerAssembly4Darwin` 僅由 `Sources/Installer_macOS` 鏈入 ⇒ 為約百行 shell 而新開共用套件、或把整個安裝器套件鏈進輸入法二進位，皆不成比例。
- 片語編輯器（`vChewingPhraseEditor`）已不出貨：全倉僅 `InstallerShared.swift:11` 一處引註、`Build/Products/Release` 無此產物 ⇒ 不列為換檔後之保證目標（只留在 preinstall 之盡力刀，與 P298「換檔前捕捉兩名、換檔後只捕捉 `kTargetBin`」同構）。

## 3. 設計

保證刀落於 `pkgPostInstall.sh` 之 chown 段之後、`TextInputMenuAgent` 之終止與 `install` 註冊之前，以**自足之 POSIX sh 區塊**實作（區塊由兩行 ASCII 標記界定，可整段抽出受測）：

- 變數：`TERMINATION_NAME="${TERMINATION_NAME:-${IME_EXECUTABLE}}"`、`TERMINATION_POLL_INTERVAL=0.1`、`TERMINATION_GRACE_TICKS=30`（SIGTERM 後 3.0 秒）、`TERMINATION_FORCE_TICKS=30`（SIGKILL 後 3.0 秒）。
- `process_is_alive()` 以 `/bin/ps -o pid= -p <pid> | grep -q '[0-9]'` 判存活（POSIX sh 取不到 `kill -0` 之 `EPERM`）；`wait_until_vacant()` 逐拍回聲仍存活者，上限為 ticks。
- 捕捉兩路：`pgrep -x "${TERMINATION_NAME}"`（與 `killall` 同認 comm ⇒ 自 `*.appTrashed` 舊 bundle 啟動之實例亦在內）∪ `pgrep -f "Contents/MacOS/${TERMINATION_NAME}"`（補 comm 被截斷或改過者）；剔除 `''`／`1`／自身 PID、去重，再以 `ps -o user= -p` 過濾至 `${login_user}`。
- 升級（escalation）：SIGTERM 全發 → 輪詢 → 仍有存活者則 `escalated=true` 並 SIGKILL → 再輪詢 → `result=vacated|stuck`。
- postcondition＝「**捕捉到的那批 PID 皆已消失**」，刻意不寫「沒有行程」（IMK 必重拉）——與 P298 同。
- 日誌與 P298 之 Swift 側**逐字同型**：`Terminate: reason=postSwap captured=[…] escalated=… result=… surviving=[…]`（PID 以逗號連接）；preinstall 之第一刀改記 `killall` 之結束碼與輸出：`Terminate: reason=preSwap target=… killall=<碼> output=…`。shell 側無 P298 之 `launchFailed` 一詞（該詞對應「連行程都沒起來」之 Swift 語境）。
- 標記註解一律 ASCII（`# Phase 300: post-swap termination of stale instances (begin).` 與 `# Phase 300: end of post-swap termination helper.`）：出貨之 PKG 腳本宜保持純 ASCII（全倉 `──` 框線之前例僅 `ValueAdd/WebConfigAssistant/tools/embed-into-bundle.sh` 一支開發工具）。
- 否決之方案：①換檔後裸 `killall vChewing`（同為送出即忘，病灶未除）；②把 preinstall 之殺移到 postinstall 而不加保證（只解決順序、未解決驗證）；③以 `TERMINATION_NAME` 承載萬用字元 pattern（`pgrep` 之 pattern 語意會波及無關行程）。

## 4. 測試與踩坑

- `/bin/sh -n` 兩檔皆過；兩檔非 ASCII 行數＝0。
- 保證刀以 `/tmp/vcprobe/probe_final.sh` 施測：`sed -n '/^# Post-swap termination of stale instances (begin)\.$/,/^# End of post-swap termination helper\.$/p'` 抽出區塊後以 `/bin/sh` source，對自編 stub（`clang -O0 -o stub stub.c`；`Mach-O 64-bit executable arm64`）跑 7 例，全過：
  1. 合作型（SIGTERM 即退）⇒ `captured=[32473] escalated=false result=vacated surviving=[]`。
  2. `signal(SIGTERM, SIG_IGN)` 者 ⇒ `escalated=true result=vacated`（SIGKILL 後退場）。
  3. 無目標 ⇒ `captured=[] escalated=false result=vacated surviving=[]`。
  4. owner 閘拒絕：`login_user` 指為他人 ⇒ `captured=[]` 且靶不動；正向對照（真 console user）⇒ 捕捉並退場。
  5. 名長 19 字元（`vcProbeLongNameHere`）⇒ 捕捉成功。
  6. 僅 `-f` 可辨者（`exec -a "Contents/MacOS/vcProbePathRoute"`）⇒ 捕捉成功。
  7. 同名 zombie（`holder.c` fork 後 exec 一枚即退之 stub、父端 `pause()` 不 wait）⇒ 屍體不出現在 `ps -ax` 亦不出現在 `pgrep` ⇒ `captured=[] result=vacated`，保證刀不會把屍體誤報為 `stuck`。
- 第一刀（preinstall）以 `sed -n '/^terminate_by_name() {/,/^}/p' pkgPreInstall.sh` 抽出後施測：有靶 ⇒ `Terminate: reason=preSwap target=vcProbeCoop killall=0 output=`（靶退場）；無靶 ⇒ `killall=1 output=No matching processes belonging to you were found`。
- 踩坑一：**P298 所記「`pgrep -x` 只認 `MAXCOMLEN`（16 位元組）以內之程序名」在本機 macOS 27 不成立**——19 字元名之 stub 以 `pgrep -x <全名>` 命中；反之，`exec -a` 改過之 comm 在 `ps -o comm=` 顯示為截斷之 `Contents/MacOS/v`（15 字元），該情形由 `-f` 路徑補位。
- 踩坑二：**平台二進位之複本不得自可寫卷重執行**——於 `/tmp` 執行 `/bin/sleep`、`/bin/sh`、`/usr/bin/jq` 之複本一律 `Killed: 9`（AMFI／封印卷）⇒ 探針須自編 stub，不可倚賴改名之系統二進位。
- 踩坑三：直譯腳本之 `comm` 為**直譯器**（`ps -o comm=` 得 `/bin/sh`）⇒ 改名之 shell 腳本只能驗 `-f` 路徑。
- 踩坑四：本工具沙盒之 `cmd &; pid=$!` 取到的是外層 shell 之 PID（實測 `$!`＝`bash`，真行程為其子）⇒ 探針一律以 `pgrep` 反查，不倚賴 `$!`。
- 未實測：完整 `postinstall` 執行（會終止事主正在使用之輸入法與 `TextInputMenuAgent`）、root／`su -` 分支、「SIGKILL 後仍存活」之分支（無法以 stub 穩定製造）。

## 5. 已知界線

- 保證刀只保證「此後被拉起之行程為新碼」，不保證舊行程於安裝當下未正在處理某客體之輸入（IMK 會於下次連線重建 session）——與 P298 同。
- 只終止 `${login_user}`（`/usr/bin/stat -f%Su /dev/console`）之行程；同一機器上其他已登入使用者之實例不在射程。
- 片語編輯器不在換檔後之射程：其已不出貨，僅 preinstall 之盡力刀仍會嘗試（且其名 19 字元 > `MAXCOMLEN`，該路徑本即可能失效）。
- PKG 之簽章／公證／`productbuild` 之 distribution（`enable_currentUserHome="true"`、`auth="none"`）與 `BuildPKG.sh` 之其餘語意未動。
