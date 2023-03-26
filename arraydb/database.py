from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from typing import Any, Dict, List

from cuid import cuid

from .types import Row, Where


@dataclass
class Column:
    """A Column"""

    name: str
    default: Any = None

    @staticmethod
    def get_defaults():
        return {
            "list": list(),
            list: list(),
            "dict": dict(),
            dict: dict(),
            "true": True,
            True: True,
            "false": False,
            False: False,
            "null": None,
            "none": None,
            "None": None,
            None: None,
        }


class ArrayDb:
    """The database"""

    def __init__(self, columns: List[Column], data: List[Dict[str, Any]] = []) -> None:
        self.data = data
        self.columns: List[Column] = list()

        for col in columns:
            if isinstance(col, str):
                self.columns.append(Column(col))
                continue

            if isinstance(col, Column):
                default = Column.get_defaults().get(col.default, None)
                col.default = default

            self.columns.append(col)

        self.column_names = list(set([col.name for col in self.columns]))
        self.default_values = {col.name: col.default for col in self.columns}

        if "_id" not in self.column_names:
            self.column_names = ["_id", *self.column_names]

    def __str__(self) -> str:
        return f"<ArrayDb rows={len(self.data)} columns={len(self.column_names)}>"

    def __repr__(self) -> str:
        return f"<ArrayDb rows={len(self.data)} columns={len(self.column_names)}>"

    @staticmethod
    def load(data: str) -> ArrayDb:
        database = json.loads(data)
        columns = list()

        for col in database["columns"]:
            columns.append(Column(col["name"], col["default"]))

        return ArrayDb(columns=columns, data=database["rows"])

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
                row[key] = self.default_values.get(key)
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

            if row[key] is None:
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
                    elif operator in ["not", "not_"]:
                        rows = [row for row in rows if row[column] != value]
                    elif operator == "contains":
                        rows = [row for row in rows if value in row[column]]
                    elif operator == "startswith":
                        rows = [row for row in rows if row[column].startswith(value)]
                    elif operator == "endswith":
                        rows = [row for row in rows if row[column].endswith(value)]
                    elif operator in ["in", "in_"]:
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
        columns = list()

        for column in self.columns:
            columns.append(
                {
                    "name": column.name,
                    "default": column.default,
                }
            )
        return json.dumps(
            {
                "rows": self.data,
                "columns": columns,
            }
        )


__all__ = ["ArrayDb", "Column"]
