"""Main entrypoint for Taiwan company crawler MVP."""

from __future__ import annotations

import argparse
import csv
import logging
from pathlib import Path

from collectors.gov_open_data import GovOpenDataCollector
from storage.db import connect_db, init_db, upsert_company
from transform.normalize import normalize_company_record

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_once(db_path: str, pages: int, export_csv: str | None = None) -> int:
    collector = GovOpenDataCollector()
    conn = connect_db(db_path)
    init_db(conn)

    count = 0
    with conn:
        for raw_record in collector.collect(max_pages=pages):
            normalized = normalize_company_record(
                raw_record.payload,
                raw_record.source_url,
                raw_record.retrieved_at,
            )
            upsert_company(conn, normalized)
            count += 1

    if export_csv:
        export_to_csv(conn, export_csv)

    logger.info("Done. Upserted %s records.", count)
    conn.close()
    return count


def export_to_csv(conn, csv_path: str) -> None:
    rows = conn.execute(
        """
        SELECT tax_id, name, status, owner, capital, setup_date,
               address, business_scope, source, source_url, retrieved_at, updated_at
        FROM companies
        ORDER BY tax_id
        """
    ).fetchall()

    Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(rows[0].keys() if rows else [
            "tax_id", "name", "status", "owner", "capital", "setup_date",
            "address", "business_scope", "source", "source_url", "retrieved_at", "updated_at"
        ])
        for row in rows:
            writer.writerow(list(row))


def run_daily(db_path: str, pages: int, export_csv: str | None = None, hour: int = 2, minute: int = 0) -> None:
    from apscheduler.schedulers.blocking import BlockingScheduler

    scheduler = BlockingScheduler(timezone="Asia/Taipei")

    def job() -> None:
        run_once(db_path=db_path, pages=pages, export_csv=export_csv)

    scheduler.add_job(job, "cron", hour=hour, minute=minute)
    logger.info("Scheduler started. Daily run at %02d:%02d (Asia/Taipei)", hour, minute)
    scheduler.start()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Taiwan company info crawler MVP")
    parser.add_argument("--db", default="data/company.db", help="SQLite DB path")
    parser.add_argument("--pages", type=int, default=1, help="Pages to fetch per run")
    parser.add_argument("--export-csv", default="", help="Optional CSV export path")
    parser.add_argument("--daily", action="store_true", help="Run in daily scheduler mode")
    parser.add_argument("--hour", type=int, default=2, help="Daily run hour in Asia/Taipei")
    parser.add_argument("--minute", type=int, default=0, help="Daily run minute in Asia/Taipei")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    export_csv = args.export_csv or None

    if args.daily:
        run_daily(
            db_path=args.db,
            pages=args.pages,
            export_csv=export_csv,
            hour=args.hour,
            minute=args.minute,
        )
    else:
        run_once(db_path=args.db, pages=args.pages, export_csv=export_csv)
