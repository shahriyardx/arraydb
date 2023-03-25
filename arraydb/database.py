from __future__ import annotations

import copy
from typing import Any, Dict, List

import json
from cuid import cuid

from .types import Row, Where


class ArrayDb:
    def __init__(
        self, column_names: List[str], data: List[Dict[str, Any]] = []
    ) -> None:
        self.data = data
        self.column_names = list(set(column_names))

        if "_id" not in self.column_names:
            self.column_names = ["_id", *self.column_names]

    def __str__(self) -> str:
        return f"<ArrayDb rows={len(self.data)} columns={len(self.column_names)}>"

    def __repr__(self) -> str:
        return f"<ArrayDb rows={len(self.data)} columns={len(self.column_names)}>"

    @staticmethod
    def load(data: str) -> ArrayDb:
        database = json.loads(data)

        return ArrayDb(column_names=database["column_names"], data=database["rows"])

    def __update(self, row: Row, data: dict):
        cleaned_data = self.__clean_row(data, fix_missing=False)

        for key in row.keys():
            if key in cleaned_data:
                row[key] = cleaned_data[key]

    def __fix_missing(self, row):
        data_keys = list(row.keys())

        row = {"_id": cuid(), **row}
        for key in self.column_names:
            if key not in data_keys and key != "_id":
                row[key] = None
                continue

        return row

    def __clean_row(self, row: Dict[str, Any], fix_missing=True) -> Any:
        data_keys = list(row.keys())
        table_columns = self.column_names

        for key in data_keys:
            if key not in table_columns:
                row.pop(key)

        if fix_missing:
            row = self.__fix_missing(row)

        for key in table_columns:
            if key not in row:
                continue

            if not isinstance(row[key], (int, str, list, dict)):
                try:
                    row[key] = str(row[key])
                except:
                    row[key] = None

        return row

    def add_col(self, col_name: str, default_value: Any = None) -> None:
        rows: List[Row] = copy.deepcopy(self.data)
        self.column_names.append(col_name)
        for row in rows:
            row[col_name] = default_value or None

        self.data = rows

    def delete_col(self, col_name):
        if not col_name in self.column_names:
            return

        rows: List[Row] = copy.deepcopy(self.data)

        self.column_names.remove(col_name)
        for row in rows:
            row.pop(col_name)

        self.data = rows

    def rename_col(self, col_name, new_name):
        if not col_name in self.column_names or col_name == new_name:
            return

        col_index = self.column_names.index(col_name)
        self.column_names[col_index] = new_name

        rows: List[Row] = copy.deepcopy(self.data)
        for row in rows:
            row[new_name] = row[col_name]
            row.pop(col_name)

        self.data = rows

    def insert(self, row: Dict[str, Any]) -> Row:
        data = self.__clean_row(row)
        self.data.append(data)

        return data

    def update(self, where: Where, data: Dict[str, Any]) -> Any | None:
        updating_rows = self.__find(where)
        updating_row_ids = [row["_id"] for row in updating_rows]

        rows: List[Row] = copy.deepcopy(self.data)
        result = {"updated_count": 0}

        for row in rows:
            if row["_id"] in updating_row_ids:
                self.__update(row, data)
                result["updated_count"] += 1

        self.data = rows
        return result

    def delete(self, where: Where):
        rows: List[Row] = copy.deepcopy(self.data)
        result = self.__find(where)
        row_ids = [row["_id"] for row in result]

        updated_rows = []
        result = {"deleted_count": 0}
        for row in rows:
            if row["_id"] in row_ids:
                result["deleted_count"] += 1
                continue
            updated_rows.append(row)

        self.data = updated_rows
        return result

    def __find(
        self, where: Where, sort: dict = {}, return_first: bool = False
    ) -> List[Row] | None:
        rows = copy.deepcopy(self.data)

        for column, filters in where.items():
            if not isinstance(filters, dict):
                rows = [row for row in rows if row[column] == filters]
            else:
                for operator, value in filters.items():
                    if operator == "gt":
                        rows = [row for row in rows if row[column] > value]
                    elif operator == "lt":
                        rows = [row for row in rows if row[column] < value]
                    elif operator == "gte":
                        rows = [row for row in rows if row[column] >= value]
                    elif operator == "lte":
                        rows = [row for row in rows if row[column] <= value]
                    elif operator == "not":
                        rows = [row for row in rows if row[column] != value]
                    elif operator == "contains":
                        rows = [row for row in rows if value in row[column]]
                    elif operator == "startswith":
                        rows = [row for row in rows if row[column].startswith(value)]
                    elif operator == "endswith":
                        rows = [row for row in rows if row[column].endswith(value)]
                    elif operator == "in":
                        rows = [row for row in rows if row[column] in value]

        for column, order in reversed(list(sort.items())):
            rows = sorted(
                rows,
                key=lambda row: row[column],
                reverse=True if order.lower() == "desc" else False,
            )

        if return_first:
            if rows:
                return rows[0]
            return None

        return rows

    def find_first(self, where: Where, sort: dict = {}) -> List[Row] | None:
        return self.__find(where=where, sort=sort, return_first=True)

    def find(self, where: Where, sort: dict = {}) -> List[Row] | None:
        return self.__find(where=where, sort=sort)

    def serialize(self) -> str:
        return json.dumps(
            {
                "rows": self.data,
                "column_names": self.column_names,
            }
        )


__all__ = ["ArrayDb"]
