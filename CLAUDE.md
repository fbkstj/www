# stjweb — 簡老師的個人網站

楊梅高中實習處主任簡樹桐的教學網站。純靜態 HTML，沒有建置流程，每個 `.html` 各自獨立（CSS/JS 大多內嵌）。

- 正式站：https://fbkstj.github.io/www/ （GitHub Pages，repo `fbkstj/www`，分支 `main`）
- 備用站：https://stjwww.netlify.app/
- 本機測試：`python serve.py` → http://127.0.0.1:18456/ （Python 3.14 全域安裝，需 PyMuPDF）

## 主要頁面

| 檔案 | 內容 |
|---|---|
| `index.html` | 入口首頁（側欄導覽，連到下列各頁） |
| `digi_el.html` | 數位電子乙級評審表設定，呼叫 `serve.py` 的 `/api/generate_pdf` 產生 PDF |
| `cpld_simulator.html`、`pcb_layout.html`、`CPLD/` | 數位電子乙級 CPLD 模擬器、PCB 佈線工具、題目資料 |
| `roster.html` | 實習處輪值表系統 |
| `coursemap*.html` | 各學年度（110、112–115）課程地圖；`premium` 是另一種版型 |
| `arduino.html`、`app_inventor*.html`、`fpga_keypad.html`、`instrument*.html` 等 | 各科教材 |
| `ai_vision_course_guide.html`、`mcp_course_automation_guide.html`、`teaching_video_pipeline_guide.html` | AI 研習手冊 |
| `airtouch_*.html` | AirTouch 專題展示與競賽報告 |
| `ymhs_calendar.js/.json` | 學校行事曆資料，由 `update_calendar.py` 從學校 Google 日曆抓取產生 |

## 工具腳本

- `serve.py`：本機靜態伺服器（port 18456），加上 `/api/generate_pdf`。這支 API **只在本機能用**，GitHub Pages 上跑不了。
- `update_calendar.py`：更新 `ymhs_calendar.json` / `.js`。
- `build_map.py`、`build_map2.py`：合併各學年度課程地圖。它們讀的是 `web/` 子資料夾，但這個資料夾已經不存在，要用的話得先改路徑。
- `skills/`：教學影片後製、MCP 研習自動化等技能包的原始檔。

## 推送（重要）

- 直接執行 `git push` 可能卡住：Git Credential Manager 的登入視窗在背景跳不出來（詳見 `GIT_PUSH_NOTES.md`）。使用者要求推送時，改用 `GCM_INTERACTIVE=never GIT_TERMINAL_PROMPT=0 timeout 90 git push origin main`，已存好的憑證可以直接用（2026-09-16 驗證成功），失敗也不會卡住。失敗時再請使用者雙擊 `一鍵推送到GitHub.bat` 或 `deploy.bat`。不要用 `--force`。
- 這兩個 bat 都會 `git add .` 並 `git push --force`。commit 之前先看 `git status`，確認沒有夾帶機密或不該上傳的檔案。

## 注意事項

- **機密檔**：`client_secrets.json`、`yt_token.json` 是 YouTube API 憑證，已列在 `.gitignore`，不可 commit，也不可寫進網頁。**打包 zip 時也要排除**：`.gitignore` 管不到 zip 裡面的檔案，2026-09 曾有兩個影片技能包夾帶這兩個檔案被公開，之後已重新打包並改附 `README_憑證請自行建立.txt`。
- **公開網站**：所有內容都會公開，不要放學生個資（像是身分證、電話、完整座號對照）。
- `.git` 已經約 1.3 GB，追蹤的檔案裡有 zip、mp4、7z。新的大型檔案（影片、壓縮包）盡量放 YouTube 或雲端硬碟，網頁只放連結。
- 頁面語言是 `zh-Hant-TW`，字型用 Google Fonts（Noto Sans TC / Outfit）。新頁面要比照既有頁面的風格、響應式版面，並符合無障礙 WCAG AA（對比度、alt 文字、語意標籤）。
- `ai_vision_course_guide.html` 的 Tailwind 已預先產生並內嵌在 `<style id="tailwind-build">`（不再用 cdn.tailwindcss.com），新增或修改 class 後要用 `npx tailwindcss@3.4.17` 重新產生。其他頁面仍用 CDN。
- 下載包：`ai_vision_starter_pack.zip`（AI 視覺入門，不附模型）、`airtouch_project_pack.zip`（AirTouch 展示頁用）。打包時不要放測試照片、錄音、開發紀錄或重複檔案。這兩包裡的講義 md 沒有獨立原始檔，要改得先從 zip 取出。
- 導盲磚專題：手冊 `tactile_paving_project_guide.html`，程式原始碼在 `tactile_paving_starter/`（改完要重新打包成 `tactile_paving_starter_pack.zip`，zip 內保留 `tactile_paving_starter/` 資料夾層）。測試方式：`make_demo_video.py` → `paving_monitor.py --config demo_config.json --no-window` → `evaluate.py`，執行產物已列在 `.gitignore`。
- `ai_vision_course_guide.html` 的專題庫（9 題）與下載包講義單元六內容要一致。
- 新增頁面時，要一起更新 `index.html` 的導覽連結和 `遠端網址備忘.txt`。
- 專案之前放在 `antigravity\stjweb`，舊文件裡如果還看到這個路徑，現在的位置是 `J:\我的雲端硬碟\claude\stjweb`。
