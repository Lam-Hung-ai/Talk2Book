from collections.abc import Sequence

from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import SQLModel, col, func, inspect, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession


class SearchableRepository[ModelType: SQLModel]:
    def __init__(self, model: type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
        self._column_names = [c.key for c in inspect(model).columns]

    def _get_column(self, name: str):
        """Lấy attribute của model dựa trên tên string, có kiểm tra tồn tại."""
        if name not in self._column_names:
            raise ValueError(f"Column '{name}' không tồn tại trong model {self.model.__name__}")
        return getattr(self.model, name)

    def _build_search_clause(
        self,
        query: str,
        search_columns: list[str],
        exact_match: bool,
        case_sensitive: bool,
    ) -> ColumnElement[bool]:
        clauses = []

        for col_name in search_columns:
            column = self._get_column(col_name)

            if exact_match:
                if case_sensitive:
                    # Exact match + Case sensitive: col == 'value'
                    clauses.append(column == query)
                else:
                    # Exact match + Case insensitive: ILIKE 'value' (Postgres)
                    # col(column) giúp đảm bảo tương thích tốt hơn với sqlmodel/sqlalchemy functions
                    clauses.append(col(column).ilike(query))
            else:
                pattern = f"%{query}%"
                if case_sensitive:
                    # Partial match + Case sensitive: LIKE '%value%'
                    clauses.append(col(column).like(pattern))
                else:
                    # Partial match + Case insensitive: ILIKE '%value%'
                    clauses.append(col(column).ilike(pattern))

        # Dùng OR để nối các điều kiện: (col1 LIKE %q%) OR (col2 LIKE %q%)
        return or_(*clauses)

    async def search(
        self,
        query: str,
        search_columns: list[str],
        *,
        exact_match: bool = False,
        case_sensitive: bool = False,
        skip: int = 0,
        limit: int = 20,
    ) -> Sequence[ModelType]:
        if not query.strip() or not search_columns:
            return []

        clause = self._build_search_clause(query, search_columns, exact_match, case_sensitive)
        statement = select(self.model).where(clause).offset(skip).limit(limit)

        result = await self.db.exec(statement)
        return result.all()

    async def count_search(
        self,
        query: str,
        search_columns: list[str],
        *,
        exact_match: bool = False,
        case_sensitive: bool = False,
    ) -> int:
        if not query.strip() or not search_columns:
            return 0

        clause = self._build_search_clause(query, search_columns, exact_match, case_sensitive)
        # Tối ưu hóa đếm: SELECT COUNT(*) FROM ... WHERE ...
        count_statement = select(func.count()).select_from(self.model).where(clause)

        result = await self.db.exec(count_statement)
        return result.one()
