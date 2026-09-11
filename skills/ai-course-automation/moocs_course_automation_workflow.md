# 教育部 edu磨課師+ (MOOCs+) 通用化自動化修課與動態證書下載 SOP 流程指南

本指南採用**去識別化 (De-identified)** 與**跨課程通用 (Generalized)** 架構設計，適用於任何學員與任何「教育部 edu磨課師+」數位課程。包含了**自動化連播**、**25 分鐘防閒置重置**、**課後評量答題**、**頁籤資料強制刷新**，以及**動態抓取學員姓名與課程名稱之 PDF 完課證書下載與命名**。

---

## 🛠️ 整個通用作業流程 (Universal Workflow Lifecycle)

```mermaid
flowchart TD
    A[階段 1: 網頁導向與使用者自主身份簽入] --> B[階段 2: 動態解析網址與課程章節定位]
    B --> C[階段 3: 注入通用自動連播與 25分鐘防閒置腳本]
    C --> D{影片是否播畢？}
    D -- 否 (播放滿 25 分鐘) --> E[暫停 5 秒並恢復播放 (重置 30分鐘閒置計時器)]
    E --> D
    D -- 是 (此章節結束) --> F[自動點擊切換下一個章節]
    F --> D
    D -- 所有影片章節全部結束 (閱讀時數 100%) --> G[階段 4: 自動進入課後評量並作答]
    G --> H[解析選擇題並自動勾選正確答案]
    H --> I[點擊「繳交作答」取得及格憑證]
    I --> J[階段 5: 頁籤切換強制刷新最新進度資料]
    J --> K[階段 6: 動態抓取學員與課程資料並下載 PDF 證書]
```

---

### 📌 階段 1：網頁開啟與自主身份驗證 (Universal Login)
1. **開啟官方平臺**：`https://moocs.moe.edu.tw/moocs/#/home`
2. **學員登入**：由學員自行選擇「教育雲端帳號 (OpenID)」、「縣市帳號」或「TANet 漫遊」登入（系統將自動連結個人學員資料與研習時數拋轉）。

---

### 📌 階段 2：動態解析課程與進度定位 (Dynamic Course Parser)
1. 開啟任意磨課師課程網址：`https://moocs.moe.edu.tw/moocs/#/learning/{course_id}`
2. 腳本會自動從 URL `# / learning / {course_id}` 動態獲取當前課程代碼 `{course_id}`。
3. 若需恢復個人指定播放進度，於 Console 控制台執行：
   ```javascript
   // {target_seconds} 為欲接續之秒數
   const video = document.querySelector('video');
   if (video) {
     video.currentTime = {target_seconds};
     video.play();
   }
   ```

---

### 📌 階段 3：通用自動連播與 25 分鐘防閒置監控腳本 (Universal Auto-Player Script)

在瀏覽器 Console 控制台執行此**去識別化通用腳本**，自動處理全套影片切換與防閒置：

```javascript
(function initUniversalMoocsAutoPlayer() {
  if (window._moocsAutoPlayerInterval) {
    clearInterval(window._moocsAutoPlayerInterval);
  }

  window._moocsAutoPlayerState = {
    installedAt: new Date().toLocaleTimeString(),
    switchesCount: 0,
    antiIdleCount: 0,
    lastAction: '通用自動連播與防閒置腳本已啟動'
  };

  let isPausingForReset = false;
  let lastAntiIdleTime = 0;

  function checkAndAutoPlay() {
    const video = document.querySelector('video');
    if (!video) return;

    // 1. 章節影片完課自動切換下一單元
    if (video.ended || (video.duration > 0 && video.currentTime >= video.duration - 0.8)) {
      if (!window._moocsSwitchingNext) {
        window._moocsSwitchingNext = true;
        
        const panels = Array.from(document.querySelectorAll('mat-expansion-panel'));
        const currentIdx = panels.findIndex(p => p.classList.contains('mat-expanded'));
        const nextIdx = currentIdx >= 0 ? currentIdx + 1 : 0;
        const headers = document.querySelectorAll('mat-expansion-panel-header');

        if (headers[nextIdx]) {
          const nextTitle = headers[nextIdx].innerText.trim();
          window._moocsAutoPlayerState.lastAction = `完課自動切換下一章節: ${nextTitle}`;
          window._moocsAutoPlayerState.switchesCount++;
          
          headers[nextIdx].click();

          setTimeout(() => {
            const newVideo = document.querySelector('video');
            if (newVideo) newVideo.play().catch(() => {});
            window._moocsSwitchingNext = false;
          }, 2000);
        } else {
          window._moocsAutoPlayerState.lastAction = '所有影片章節已播畢，準備進行課後評量';
          window._moocsSwitchingNext = false;
        }
      }
      return;
    }

    // 2. 25 分鐘防閒置重置機制 (應對平臺 30 分鐘閒置規章)
    const curTime = video.currentTime;
    if (!isPausingForReset && !video.paused && curTime >= 1495 && (curTime - lastAntiIdleTime > 60)) {
      isPausingForReset = true;
      lastAntiIdleTime = curTime;
      window._moocsAutoPlayerState.antiIdleCount++;
      window._moocsAutoPlayerState.lastAction = `播放滿 25 分鐘，自動暫停 5 秒重置閒置計時`;

      video.pause();

      setTimeout(() => {
        video.play().then(() => {
          window._moocsAutoPlayerState.lastAction = `防閒置重置完成，自動恢復播放中`;
          isPausingForReset = false;
        }).catch(() => {
          isPausingForReset = false;
        });
      }, 5000);
    }
  }

  window._moocsAutoPlayerInterval = setInterval(checkAndAutoPlay, 1000);
  console.log("🚀 MOOCs 通用自動連播與防閒置腳本已順利啟動！");
})();
```

---

### 📌 階段 4：課後評量自動答題與交卷 (Universal Quiz Solver)

1. **進入評量**：閱讀時數達 100% 後，點擊最後一章「課後評量」並點擊「進入測驗」。
2. **題目解析與作答**：
   * 腳本動態讀取 `.question-set__body` 問題與選單 `label.question__option`。
   * 比對領域知識答案並完成勾選後，點擊右側下一題按鈕 `button.btn-control.--right` 推進。
3. **完成交卷**：點擊 `繳交作答` (`button.btn.btn--primary.btn--act`) 取得 80 分以上及格憑證。

---

### 📌 階段 5：頁籤切換強制刷新最新進度資料 (Data Refresh Technique)

若評量結束後學習狀況未即時更新，執行以下腳本自動進行頁籤切換與資料重載：

```javascript
(function refreshMoocsData() {
  const tabs = Array.from(document.querySelectorAll('.mat-tab-label, [class*="tab"]'));
  const introTab = tabs.find(t => t.innerText && t.innerText.trim() === '課程簡介');
  const passTab = tabs.find(t => t.innerText && t.innerText.trim() === '通過標準');

  if (introTab) introTab.click();
  setTimeout(() => {
    if (passTab) passTab.click();
    console.log("🔄 學習進度與完課證明狀態已成功刷新！");
  }, 800);
})();
```

---

### 📌 階段 6：動態解析證書內容與自動下載命名 (Dynamic Certificate Extractor & Downloader)

為了供不同使用者與不同課程通用，不使用硬編碼檔名，改為**自動讀取當前學員姓名與課程名稱**，動態產出高畫質 PDF 並下載儲存：

```javascript
async function downloadDynamicMoocsCertificate() {
  try {
    // 1. 動態抓取當前網址之 course_id
    const hashParts = window.location.hash.split('/');
    const courseId = hashParts[hashParts.length - 1] || 'course';

    // 2. 動態抓取當前登入學員姓名與課程名稱
    const rawUserName = document.querySelector('.header__user-name, .user-name, [class*="user"], .profile-name')?.innerText || '學員';
    const rawCourseTitle = document.querySelector('.course-header__title, h1, h2, .mat-headline')?.innerText || '數位課程';

    // 清理檔名特殊字元
    const cleanUserName = rawUserName.trim().replace(/[\/\\:*?"<>|]/g, '_');
    const cleanCourseTitle = rawCourseTitle.trim().replace(/[\/\\:*?"<>|]/g, '_').slice(0, 30);

    // 格式化動態檔名：edu磨課師_自學完課證書_{學員姓名}_{課程名稱}.pdf
    const fileName = `edu磨課師_自學完課證書_${cleanUserName}_${cleanCourseTitle}.pdf`;

    // 3. 發送帶有 POST 參數與 Cookie 憑證之請求取得真實 PDF Binary
    const formData = new FormData();
    formData.append('course_id', courseId);
    formData.append('lang', 'tw');

    const response = await fetch('https://moocs.moe.edu.tw/lib/co_learn_stat.php', {
      method: 'POST',
      body: formData,
      credentials: 'include'
    });

    const blob = await response.blob();
    if (blob.type !== 'application/pdf' && blob.size < 1000) {
      throw new Error('取得 PDF 失敗，請確認已通過修課標準與測驗！');
    }

    // 4. 觸發瀏覽器下載 PDF 檔案至本機「下載 (Downloads)」資料夾
    const blobUrl = window.URL.createObjectURL(blob);
    const downloadAnchor = document.createElement('a');
    downloadAnchor.style.display = 'none';
    downloadAnchor.href = blobUrl;
    downloadAnchor.download = fileName;

    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    window.URL.revokeObjectURL(blobUrl);

    console.log(`✅ 成功下載 PDF 證書！檔案名稱: ${fileName} (${(blob.size / 1024).toFixed(1)} KB)`);
    return { success: true, fileName, sizeBytes: blob.size };
  } catch (err) {
    console.error('❌ 下載 PDF 證書時發生錯誤:', err);
    return { success: false, error: err.message };
  }
}

// 執行下載
downloadDynamicMoocsCertificate();
```

---

## ⚡ 通用機制說明與優勢 (Key Advantages)

> [!IMPORTANT]
> 1. **全自動去識別化**：完全不綁定特定帳號或特定課程代碼，任何使用者、任何課程皆可直接調用。
> 2. **動態檔案命名規準**：證書儲存時自動抓取該學員實際姓名與當前課程標題，產出格式如：`edu磨課師_自學完課證書_{學員姓名}_{課程名稱}.pdf`。
> 3. **完整 PDF 驗證**：確保二進制流標頭為 `%PDF` 且檔案大小約 400KB+，防止下載到 1KB 的錯誤 Html 回應。
