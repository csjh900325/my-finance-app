# Taiwan Company Crawler (MVP)

台灣公司資訊自動蒐集 MVP：
- 來源：政府開放資料（可擴充）
- 流程：collect → normalize → SQLite upsert → CSV 匯出
- 排程：每日定時執行（Asia/Taipei）

## 1) 安裝

```bash
cd tw-company-crawler
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) 單次執行

```bash
python src/main.py --db data/company.db --pages 1 --export-csv data/companies.csv
```

## 3) 每日排程執行（前景模式）

```bash
python src/main.py --daily --db data/company.db --pages 1 --hour 2 --minute 0
```

## 4) 欄位設計

`companies` 資料表欄位：
- tax_id（統編，主鍵）
- name
- status
- owner
- capital
- setup_date
- address
- business_scope
- source
- source_url
- retrieved_at
- updated_at

## 5) 注意事項

1. 請遵守來源網站使用條款與授權條件。
2. 請保留來源 URL 與抓取時間，便於稽核。
3. 建議設定合理限速（預設約每秒 1 次請求）。

## 6) 下一步可擴充

- 增加新聞資料來源（關鍵字 + 公司統編關聯）
- 新增異動比對表（每日新增/更新筆數）
- 改用 PostgreSQL + Docker 部署
