from typing import Dict, TypedDict, Union


class Filters(TypedDict, total=False):
    gt: Union[int, str, float, list]
    gte: Union[int, str, float, list]
    lt: Union[int, str, float, list]
    lte: Union[int, str, float, list]
    not_: Union[int, str, float, list]
    contains: Union[int, str, float, list]
    startswith: Union[int, str, float, list]
    endswith: Union[int, str, float, list]
    in_: Union[int, str, float, list]


class Row(TypedDict, total=False):
    """Represents a dict of row"""

    _id: str


Where = Dict[str, Filters]
