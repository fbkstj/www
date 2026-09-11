# ⚡ 02. MCP 模式系統配置與工具鏈指南 (Model Context Protocol)

MCP (Model Context Protocol) 是讓 AI 能夠以**原生特權視角**操作瀏覽器的關鍵技術標準。透過 Chrome DevTools MCP，AI 能徹底克服傳統 F12 腳本在跳轉頁面時被清除、以及無法自動按掉警示彈窗的缺陷。

---

## 🛠️ 環境配置 3 步驟

### 步驟 1：安裝 Node.js
在 Windows PowerShell 或命令提示字元中檢查環境：
```powershell
node -v
npm -v
```
若未安裝，請至 [nodejs.org](https://nodejs.org) 下載安裝 LTS 版本。

### 步驟 2：建立 MCP 設定檔 (`mcp_config.json`)
將設定檔置於 AI 代理程式之設定目錄（如 `~/.gemini/antigravity/mcp/`）：
```json
{
  "mcpServers": {
    "chrome-devtools-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "chrome-devtools-mcp@latest"
      ]
    }
  }
}
```

### 步驟 3：以遠端除錯埠啟動 Chrome（保留既有登入態）
若要讓 AI 共享您目前 Chrome 視窗內已登入的公務帳號 Cookie，請在捷徑中附加除錯參數：
```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\user\AppData\Local\Google\Chrome\User Data"
```

---

## 🧰 核心 MCP 工具鏈說明

| 工具名稱 | 自動化功能 | 實際處理效益 |
| :--- | :--- | :--- |
| **`handle_dialog`** | 自動攔截彈窗 | 0 秒自動按下「確定」，徹底破解「**禁止多重視窗瀏覽課程**」警示中斷。 |
| **`evaluate_script`** | 原生腳本注入 | 背景自動呼叫 `API.LMSSetValue` 累計時數，並自動比對題庫勾選答案。 |
| **`navigate_page`** | 特權頁面導航 | 無需使用者手動打網址，AI 自動切換至測驗、問卷與證書下載頁。 |
| **`take_snapshot` / `click`** | DOM 精準點擊 | 自動定位「下一單元」、「繳交作答」、「產製證書」按鈕並精準觸發。 |
| **`list_pages` / `select_page`** | 頁籤切換監控 | 當新開分頁產出 PDF 證書時，自動鎖定新分頁網址並保存。 |
