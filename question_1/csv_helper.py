# csv_helper.py
import os
import csv
import logging
from typing import List, Dict, Optional


class CSVHelper:
    """
    CSV 儲存管理：
    - load(): 讀取 CSV → List[Dict]
    - save(): 覆寫 CSV（初始化）
    - append(): 增量寫入 CSV
    """

    def __init__(
        self,
        path: str,
        fieldnames: List[str],
        logger: Optional[logging.Logger] = None,
    ):
        self.path = path
        self.fieldnames = fieldnames

        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(self.__class__.__name__)
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
                    "%Y-%m-%d %H:%M:%S",
                )
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
                self.logger.setLevel(logging.INFO)

    def load(self) -> List[Dict]:
        """讀取現有 CSV（若不存在則回傳空 list）"""
        if not os.path.exists(self.path):
            self.logger.info(f"CSV 不存在，回傳空列表：{self.path}")
            return []

        rows: List[Dict] = []
        try:
            with open(self.path, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append(row)

            self.logger.info(f"成功讀取 CSV：{self.path}（共 {len(rows)} 筆）")
        except Exception as e:
            self.logger.error(f"讀取 CSV 發生錯誤：{e}")
            raise

        return rows

    def save(self, rows: List[Dict]) -> None:
        """覆寫 CSV（初始化使用）"""
        if not rows:
            self.logger.warning("save() 被呼叫但 rows 為空，不進行寫入。")
            return

        try:
            with open(self.path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
                for r in rows:
                    writer.writerow(r)

            self.logger.info(f"成功覆寫 CSV：{self.path}（共 {len(rows)} 筆）")
        except Exception as e:
            self.logger.error(f"寫入 CSV 發生錯誤：{e}")
            raise

    def append(self, rows: List[Dict]) -> None:
        """增量寫入 CSV，不 overwrite 原資料"""
        if not rows:
            self.logger.warning("append() 被呼叫但 rows 為空，不寫入。")
            return

        file_exists = os.path.exists(self.path)

        try:
            with open(
                self.path,
                "a" if file_exists else "w",
                encoding="utf-8-sig",
                newline="",
            ) as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)

                if not file_exists:
                    writer.writeheader()

                for r in rows:
                    writer.writerow(r)

            self.logger.info(f"成功 append {len(rows)} 筆資料至 CSV：{self.path}（已存在？{file_exists}）")
        except Exception as e:
            self.logger.error(f"append CSV 發生錯誤：{e}")
            raise
