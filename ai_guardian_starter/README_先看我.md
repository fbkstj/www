# AI 守望：公共場所 AI 監控通報｜學生實作程式包

用網路攝影機加上 YOLO 影像辨識，做出「發現危險 → 確認 → 通報」的監控系統：
找出畫面中的人、判斷有沒有人手持危險物品、持續一段時間才成立警示、給保全 5 秒取消誤報，最後用 LINE 通報。
七個關卡，每關都能跑、都看得到成果。

完整教學（關卡說明、調參實驗、疑難排解、評量規準）：https://fbkstj.github.io/www/#page/ai_guardian_project_guide

> **安全規定**：練習「手持危險物品」一律用**剪刀**代替（刀尖朝下、不揮動），禁止攜帶真刀進教室。
>
> **法律規定**：只能連線自己的或已取得授權的攝影機（未經同意連線他人攝影機，觸犯《刑法》第 358 條）。
> 拍攝他人要遵守《個人資料保護法》：設置錄影告示、只用在安全用途、定期刪除 `events/` 裡的截圖。
>
> 這是教學原型，只能**輔助**人員判斷，不能取代保全、警察或 110。

## 一、安裝
1. 安裝 Python 3.10 以上版本（勾選 **Add python.exe to PATH**）。
2. 在這個資料夾的網址列輸入 `cmd` 按 Enter，執行：
   ```
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
   第一次會下載 PyTorch，約需 5～10 分鐘。之後每次開新的命令視窗，都要先執行 `.venv\Scripts\activate`。
   （用下面的 bat 檔之前，也要先在同一個視窗啟用虛擬環境，或把套件裝在全域 Python。）
3. 第一次執行會自動下載 YOLO 模型 `yolov8n.pt`（約 6 MB），需要網路。

## 二、操作順序
| 檔案 | 說明 |
|---|---|
| `0_test_rules.bat` | 不用攝影機：用假資料檢查判斷規則與通報流程（應顯示 26 項通過） |
| `1_camera.bat` | 關卡 1：打開攝影機畫面 |
| `2_people.bat` | 關卡 2：用 YOLO 找出人並計算人數 |
| `3_weapon.bat` | 關卡 3：判斷危險物品是不是「拿在手上」 |
| `4_sustain.bat` | 關卡 4：持續 0.6 秒才成立警示（防誤報） |
| `5_alert.bat` | 關卡 5：截圖存證、寫入 `events/events.csv`、5 秒取消窗口（按 c 取消） |
| `6_line_test.bat` | 關卡 6：發一則 LINE 測試訊息（要先設定金鑰，見下方） |
| `7_monitor_wall.bat` | 關卡 7：多路監控牆（先編輯 `system/sources_config.py`；這個 bat 不發 LINE） |

關卡 1～5 的 bat：**雙擊**用 0 號攝影機；**把影片檔拖曳到 bat 上**就改用那支影片（沒有攝影機也能練習）。
視窗裡按 `q` 離開。

## 三、LINE 金鑰
LINE Notify 已在 2025 年 3 月停止服務，要改用 LINE Messaging API 的官方帳號（申請步驟見網頁手冊關卡 6）。
金鑰就是密碼：**不要寫進程式、不要貼到群組、不要上傳到網路**。用環境變數設定：
```
set LINE_TOKEN=貼上你的 Channel access token
python step6_line.py
```
完整系統要發 LINE：在同一個視窗 `cd system`，再執行 `python monitor.py`（不加 `--no-line`）。

## 四、檔案
| 檔案 | 用途 |
|---|---|
| `step1～step6_*.py` | 各關卡程式 |
| `tw_text.py` | 在畫面寫中文、開啟影像來源、縮小畫面 |
| `guard_core.py` | 關卡 4、5 共用的判斷模組（手持判斷、持續判斷） |
| `system/monitor.py` | 關卡 7 主程式：監控牆、推論迴圈（`--no-line`、`--headless --seconds 30`） |
| `system/sources.py`、`sources_config.py` | 影像來源（USB 攝影機、RTSP、公開快照、影片、圖片） |
| `system/threat_rules.py` | 持械、奔逃、倒地、聚集四種規則；門檻都在檔案最上方 |
| `system/alerter.py` | 截圖、CSV、分級通報、取消窗口、冷卻時間 |
| `system/line_*.py` | LINE 推播（獨立行程、http.client） |
| `system/test_rules.py` | 規則測試（改了門檻或規則就跑一次） |

`system/threat_rules.py` 的 `PRACTICE_SCISSORS = True` 會把剪刀當成危險物品，方便上課練習；
正式展示「真的場景」時改成 `False`。

## 五、限制
- 模型用 COCO 資料集訓練，**沒有槍、火焰、煙霧**類別，要偵測這些得自己蒐集資料訓練。
- 小模型（yolov8n）在遠距離、低解析度下不容易認出刀具與剪刀，鏡頭要近、背景要單純。
- 「倒地」用人框的長寬比判斷，比較粗略；延伸挑戰可以改用姿態辨識。
- 手機上的「國家級警報」（細胞廣播）只有政府機關能發送，民間系統不能串接。
