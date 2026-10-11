# 驗證矩陣（v0.0.1）

| Gate | 結果 | 證據／限制 |
|---|---|---|
| 官方來源版本 | VERIFIED | GitHub `v0.9.3` commit `7b116c05bfda646af39d2524c54e70c751f57ee8` |
| 靜態原始字串比對 | VERIFIED | 13 檔、209 鍵、228 處；全部可在官方標籤找到 |
| 格式參數維持 | VERIFIED | Python 逐項比較 Rust format placeholder |
| 補丁單元測試 | VERIFIED | 5 項通過（模擬來源） |
| 真實原始碼套用 | NOT RUN | 工作環境沒有可下載的 Git checkout |
| cargo fmt/check/build/test | NOT RUN | 工作環境沒有 Rust toolchain，也沒有依賴／網路 |
| Windows 可執行檔 | NOT PRODUCED | 需 Windows 本機完整開發環境 |
| Windows TUI、IME、通知 | NOT TESTED | 需實際 Windows Terminal 與服務端狀態 |
| 全介面 zh-TW 覆蓋率 | INCOMPLETE | 目前僅選定 UI/Client 字串 |

## 驗證底線

**若建置腳本失敗，沒有可用中文版 exe。** 不得將已套用補丁與實際編譯成功混為一談。不能因修正了兩處文字寬度計算，就推定所有 CJK 排版都正確。