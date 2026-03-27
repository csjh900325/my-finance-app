# 💰 上班族的第一桶金

> 實現財富自由，從每天的小事開始

一站式個人理財工具，專為台灣上班族設計。部署在 Netlify 上，使用 localStorage 儲存資料，無需後端。

## ✨ 功能

| 功能 | 說明 |
|------|------|
| 📒 記帳 | 收支紀錄、快速選取常用項目、分類統計 |
| 🏦 銀行帳戶 | 多帳戶管理、淨資產計算 |
| 📈 投資追蹤 | 台股 ETF + 個股、TWSE 即時股價同步 |
| 📊 報表分析 | 6 個月趨勢圖、支出結構、儲蓄率、年度總結 |
| 💡 理財建議 | 健康分數、個人化建議引擎 |
| 💳 信用卡 | 帳單週期、繳費提醒、30+ 張卡片優惠自動帶入 |
| 📄 債務管理 | 房貸/車貸/信貸追蹤、還款進度 |
| 📅 財務行事曆 | 所有財務事件整合月曆 |
| 🔁 固定收支 | 每月自動帶入薪水、房租等 |
| 📋 月預算 | 分類預算設定與追蹤 |
| 👨‍👩‍👧‍👦 多用戶 | 密碼登入、家人各自獨立帳本 |
| 🎨 四季主題 | 春櫻花粉/夏海洋藍/秋琥珀棕/冬霜藍夜 |

## 🚀 部署到 Netlify

### 方式一：拖曳部署（最快）
1. 到 [app.netlify.com/drop](https://app.netlify.com/drop)
2. 把整個專案資料夾拖進去
3. 完成！

### 方式二：連結 GitHub（推薦，自動部署）
1. 把此 repo push 到 GitHub
2. 到 [app.netlify.com](https://app.netlify.com) → New site from Git
3. 選擇此 repo
4. Build settings 不需要修改（靜態檔案 + Netlify Functions）
5. Deploy!

之後每次 push 到 main 分支，Netlify 會自動重新部署。

## 📁 專案結構

```
├── index.html                  # 主程式（單一 HTML 檔）
├── netlify.toml                # Netlify 設定
├── netlify/
│   └── functions/
│       └── stock.js            # 股價 API 代理（Serverless Function）
├── README.md
└── .gitignore
```

## 🔧 本地開發

本地預覽 `index.html` 即可看到介面，但**股價同步功能需要部署到 Netlify 後才能運作**（因為需要 Serverless Function 代理 TWSE API）。

## 📝 注意事項

- 所有資料存在瀏覽器 localStorage，清除瀏覽器資料會遺失
- 建議定期使用「匯出備份」功能
- 信用卡優惠內容可能隨銀行調整，請自行更新
- 股價資料來源：台灣證交所 (TWSE) / Yahoo Finance

## 📄 License

MIT
