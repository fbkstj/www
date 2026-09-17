# 自行車「後方來車」警示：學生實作程式包

騎單車時看不到後方逼近的大車。這個專題用朝後拍攝的影片，讓 YOLO 找出汽車、機車、公車、貨車，
再從車框「變大的速度」估計還有幾秒會到，提早亮燈或發出嗶聲。

完整教學（功能設計、拍攝方法、原理、流程、測試、評分）：https://fbkstj.github.io/www/#page/bike_rear_alert_project_guide

> **安全第一**：請用錄好的影片或桌上模型測試，**不要邊騎車邊測試或看螢幕**。這是教學原型，不能取代後照鏡、車燈、安全帽等正規安全裝備。

## 一、安裝
0. AI 助手（擇一）：Google Antigravity（免費），或 Claude Code（需 Claude 付費方案）。手冊的提示語兩者通用。
1. 安裝 Python 3.10 以上版本（勾選 **Add Python to PATH**）。
2. 在這個資料夾開啟命令提示字元：`pip install -r requirements.txt`
3. 第一次執行會自動下載 YOLO 模型 `yolo11n.pt`（約 5 MB），需要網路。
4. 桌上模型展示才需要：安裝 Arduino IDE 與 ESP32 開發板套件，開啟 `esp32_rear_alert/esp32_rear_alert.ino`，
   開發板選「ESP32 Dev Module」後上傳（不需要額外程式庫）。

## 二、操作順序
| 檔案 | 說明 |
|---|---|
| `0_demo_practice.bat` | 產生練習影片 → 分析 → 計算成績，確認環境沒問題 |
| `1_test_lights.bat` | 測試 ESP32 的三色燈與蜂鳴器 |
| `2_label_video.bat` | **把影片拖曳到這個檔案上**：播放影片，車輛經過時按鍵，在影片旁邊存成 `影片名_truth.csv` |
| `3_analyze_video.bat` | **把影片拖曳到這個檔案上**：分析一支影片（開視窗），輸出標註影片；有答案檔就順便算成績 |
| `4_batch_evaluate.bat` | 分析 `videos/` 裡每支有答案檔的影片，整理成一張成績表 |
| `5_bench_demo.bat` | 桌上模型展示：鏡頭＋ESP32 燈號（沒接 ESP32 會改用電腦嗶聲） |

練習影片的預期結果：兩次逼近都有警示、沒有誤報，平均提早約 1.3 秒（第一台約 2.1 秒、第二台約 0.5 秒）。

### 標記按鍵（2_label_video.bat）
在車頭到達鏡頭旁邊、離開畫面的那一刻按：
`1` 汽車、`2` 機車、`3` 公車、`4` 貨車、`空白鍵` 不分車種；
`u` 取消上一個、`p` 暫停、`a`／`d` 倒退／快轉 3 秒、暫停時 `,`／`.` 逐格、`q` 存檔離開。

### 參數實驗（不會改到 config.json）
```
python batch_run.py videos --tag base
python batch_run.py videos --set ttc_warn=5 --tag warn5
python batch_run.py videos --set imgsz=960 --set confirm_count=1 --tag test3
```
每次結果存在 `output/summary_<標籤>_<時間>.csv`，用 Excel 開啟比較。

## 三、資料夾
| 位置 | 內容 |
|---|---|
| `videos/` | 自己拍的影片與答案檔（`影片名_truth.csv`）。**不要上傳到網路** |
| `logs/` | 每次分析的警示紀錄（CSV）與摘要（JSON）；批次分析在 `logs/batch_…/` |
| `output/` | 標註影片、成績表、`snapshots/` 警示截圖（都已模糊行人與車牌） |

## 四、config.json 重要設定
| 設定 | 預設 | 說明 |
|---|---|---|
| `ttc_warn` | 4.0 | 估計幾秒內會到達就「注意」（黃燈） |
| `ttc_danger` | 2.0 | 估計幾秒內會到達就「危險」（紅燈） |
| `zone_x` | [0.35, 1.0] | 只看畫面這個左右範圍內的車（0＝最左、1＝最右）。台灣靠右行駛，超車的車在朝後畫面的右半邊 |
| `min_width_ratio` | 0.04 | 車框寬度小於畫面寬度的幾倍就先不判斷（太遠、太不準） |
| `size_window_sec` | 0.8 | 用最近幾秒的車框變化來估計到達時間 |
| `min_points` | 4 | 至少要有幾個框才開始估計 |
| `confirm_count` | 2 | 連續幾次判定逼近才發出警示（越大誤報越少，但越慢） |
| `hold_sec` | 1.0 | 警示至少維持幾秒，避免燈號一直閃 |
| `lost_sec` | 0.8 | 車子幾秒沒被認出來，就當作離開 |
| `imgsz` | 640 | 辨識解析度；改 960 可以看到更遠的車，但比較慢 |
| `confidence` | 0.25 | YOLO 信心門檻 |
| `detect_interval_sec` | 0.1 | 每隔幾秒辨識一次；電腦慢可改 0.2 |
| `camera` | 0 | 桌上展示用的鏡頭編號（外接鏡頭可能是 1） |
| `serial_port` | auto | ESP32 序列埠；自動找不到時改成例如 `"COM5"` |
| `privacy_blur` | true | 輸出影片與截圖時，把行人和車輛下半部（車牌）模糊 |
| `snapshot_on_alert` | true | 每次警示開始或升級時存一張截圖 |

## 五、拍攝影片注意事項
- **最安全的做法**：在人行道或路邊安全位置架腳架，鏡頭朝向來車方向拍攝，不要站在車道上。
- 如果要把鏡頭裝在自行車後方實際騎乘錄影，要經老師同意、在車少的路段、戴安全帽，騎車時**不看手機或螢幕**。
- 鏡頭要固定牢靠、水平，拍到的畫面要包含後方車道；建議 1080p、30fps。
- 影片裡有車牌和路人，**不要把原始影片上傳到網路**；報告與展示請用 `output/` 裡已模糊的影片或截圖。

## 六、程式檔案
- `rear_alert.py`：主程式（辨識、追蹤、估計到達時間、警示狀態、燈號、紀錄、截圖）
- `label_events.py`：標記正確答案
- `evaluate.py`：比對一支影片，算出提早秒數、漏報、誤報、各車種成績
- `batch_run.py`：批次分析與參數實驗
- `make_demo_video.py`：產生練習影片 `videos/demo.mp4` 與答案 `videos/demo_truth.csv`
- `test_lights.py`：測試 ESP32 燈號
- `esp32_rear_alert/`：ESP32 程式（綠燈＝安全、黃燈閃＝注意、紅燈快閃＝危險、綠燈慢閃＝沒收到電腦訊號）
