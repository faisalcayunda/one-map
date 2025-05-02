from typing import List, Optional

from fastapi import Query


class CommonParams:
    def __init__(
        self,
        filter: List[str] = Query(default_factory=list),
        sort: List[str] = Query(default_factory=list),
        search: str = Query(default=""),
        group_by: Optional[str] = Query(default=None),
        limit: int = Query(default=100, ge=1),
        offset: int = Query(default=0, ge=0),
    ):
        self.filter = filter
        self.sort = sort
        self.search = search
        self.group_by = group_by
        self.limit = limit
        self.offset = offset
