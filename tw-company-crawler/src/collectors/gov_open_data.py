"""Government open data collector for Taiwan company registry."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

import requests

logger = logging.getLogger(__name__)

# NOTE:
# This endpoint is published by Taiwan MODA open data portal and may evolve.
# Keep it configurable for future source changes.
DEFAULT_DATASET_URL = (
    "https://data.gcis.nat.gov.tw/od/data/api/"
    "A9B24F0A-7DB1-4AB4-AEEE-5A776B4E9D85"
    "?$format=json&$top=1000&$skip={skip}"
)


@dataclass(slots=True)
class RawCompanyRecord:
    """Raw company record from upstream data source."""

    payload: dict
    source_url: str
    retrieved_at: str


class GovOpenDataCollector:
    """Collect Taiwan company records via open data endpoint."""

    def __init__(
        self,
        dataset_url_template: str = DEFAULT_DATASET_URL,
        page_size: int = 1000,
        timeout: int = 30,
        requests_per_second: float = 1.0,
    ) -> None:
        self.dataset_url_template = dataset_url_template
        self.page_size = page_size
        self.timeout = timeout
        self.requests_per_second = requests_per_second

    def fetch_page(self, skip: int) -> list[dict]:
        """Fetch a single page from upstream open data endpoint."""
        url = self.dataset_url_template.format(skip=skip)
        logger.info("Fetching page skip=%s", skip)

        response = requests.get(
            url,
            timeout=self.timeout,
            headers={"User-Agent": "tw-company-crawler/1.0"},
        )
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            logger.warning("Expected list payload, got: %s", type(data).__name__)
            return []

        return data

    def collect(self, max_pages: int | None = 1) -> Iterable[RawCompanyRecord]:
        """Collect records from open data source.

        Args:
            max_pages: number of pages to retrieve. None means infinite until no data.
        """
        retrieved_at = datetime.now(timezone.utc).isoformat()
        page_idx = 0
        while True:
            if max_pages is not None and page_idx >= max_pages:
                break

            skip = page_idx * self.page_size
            records = self.fetch_page(skip)
            if not records:
                break

            source_url = self.dataset_url_template.format(skip=skip)
            for item in records:
                yield RawCompanyRecord(
                    payload=item,
                    source_url=source_url,
                    retrieved_at=retrieved_at,
                )

            page_idx += 1
            time.sleep(1 / self.requests_per_second)
