# Herdr v0.9.3 臺灣繁體中文化補丁（v0.0.1）

**狀態：部分介面字串實作／Windows 建置尚未實機驗證；不是完整中文版。**

## 來源與邊界

- 原始專案：https://github.com/herdrdev/herdr
- 固定版本：`v0.9.3`，commit `7b116c05bfda646af39d2524c54e70c751f57ee8`
- 不更改官方安裝 `%LOCALAPPDATA%\Programs\Herdr`、既有穩定版或 `%USERPROFILE%\.herdr` 中的設定／資料。
- 補丁僅針對經人工檢視的 Client/UI Rust 檔案，不翻譯 API method、設定檔 key、Command、機器可讀狀態，也不自動變更通知通訊協定。
- 依 Apache-2.0 授權，原作者及授權聲明以原始碼為準；本包僅包含增量翻譯資料及建置輔助工具，不轉載上游完整程式碼。

## 先備條件（Windows PowerShell，一般使用者權限）

1. [Git for Windows](https://git-scm.com/downloads/win)、[Python 3](https://www.python.org/downloads/windows/)、[Rust/Rustup](https://rustup.rs/) 與 [Zig 0.16.0](https://ziglang.org/download/)（`zig version` 須為 `0.16.0`）。
2. 使用 **Visual Studio Build Tools C++**（MSVC）及 Windows SDK，Rust toolchain 由儲存庫 `rust-toolchain.toml` 指定 `1.96.1`。
3. 設定 `git`、`python`（或 `py -3`）、`cargo`、`zig` 皆在 PATH 中。
4. 如果執行政策不允許 PowerShell 腳本，可開啟一般 PowerShell，以 `powershell -NoProfile -ExecutionPolicy Bypass -File .\Build-Herdr-zhTW.ps1` 單次執行（請先檢查腳本內容）。

## 建置與啟動

開啟一般 PowerShell，切換到解壓縮後本包所在的目錄：

```powershell
.\Build-Herdr-zhTW.ps1
```

腳本先在 `%USERPROFILE%\Herdr-zhTW-v0.0.1\herdr-v0.9.3-zhTW` 另行 clone 官方 tag、驗證 commit、翻譯、`cargo fmt`、`cargo check --locked`、`cargo build --locked`，最後執行 `--version`。

若全部通過，再在**一般權限**的 PowerShell 啟動：

```powershell
.\Launch-Herdr-zhTW.ps1
```

使用 debug build，Herdr 原始碼中的 `cfg!(debug_assertions)` 會讓設定／Server 使用 `herdr-dev` 命名空間，而非已安裝的穩定版。啟動腳本移除繼承的 socket override，並指定 `HERDR_WINDOWS_CONPTY=system`，因為本包不是含官方 app-local ConPTY runtime 的 Windows 發行包。此方式可能與部分終端機功能不完全相容。

## 驗證

- `translation-report.json` 提供逐檔的成功字串與未匹配清單。**未匹配項目表示對應翻譯沒有套用。**
- 手動檢查設定頁、右鍵選單、工作樹、快捷鍵、Agent 狀態及通知排版；目前未提供通過 Windows GUI 的證據。
- 必要時在獨立 checkout 執行 `cargo test --locked`；上游英文字串快照測試可能因中文化而需要相應修改，**不能視為已通過**。
- **完整覆蓋尚未達成**：此版本僅翻譯指定 Client/UI 字串，其他介面、CLI 人類可讀錯誤訊息、Agent 插件等仍可能顯示英文。未把「無法驗證」當成「已完成」。

## 還原與安全

- 本包不覆蓋 `%LOCALAPPDATA%\Programs\Herdr\bin\herdr.exe`。
- 要使用原版，關閉測試版並執行你既有的 `Herdr_Launch_v0.0.2.bat`。
- 不必以管理員權限編譯或啟動；不會執行 `herdr server stop`、刪除原版工作階段或改動 ACL。
- 測試版 server 也會保留自己執行的工作階段；若要刪除測試用目錄，請先確認沒有重要的 `herdr-dev` 工作在執行。

## 此版實作驗證紀錄（2026-10-11）

- 經 GitHub 上游 `v0.9.3` 原始檔逐項比對：**13 個檔案、209 個翻譯鍵、228 處英文原文字面值**符合，沒有未匹配翻譯鍵。
- Python 補丁程式的 **5 項單元測試通過**：取代結果、乾跑不改檔、Rust 格式參數不變、拒絕錯誤來源 commit、拒絕有修改的工作樹。
- **尚未驗證的項目**：真實 Git clone 後的補丁套用、Rust 格式化、`cargo check`、Windows 編譯與中文介面執行結果。這些需在具備 Rust/Zig/Windows SDK 的電腦執行 `Build-Herdr-zhTW.ps1` 才有驗證證據。
- 209 個翻譯鍵是人工挑選並驗證的文字，**不是** Herdr 全部介面字串的總數。仍需翻譯其他 Client/UI 區塊與所有人類可讀錯誤訊息，並針對 CJK 寬度、固定寬度控制項與通知顯示做全介面驗證。
