from typing import List, TypeVar, Type, Sequence, Generic
from sqlmodel import or_, inspect, func, col
from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

ModelType = TypeVar("ModelType", bound=SQLModel)

class SearchableRepository(Generic[ModelType]):
    
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.db = session
        self._column_names = [c.key for c in inspect(model).columns]
    
    def _get_column(self, name: str):
        if name not in self._column_names:
            raise ValueError(f"Column '{name}' không tồn tại trong {self.model.__name__}")
        return getattr(self.model, name)
    
    def _build_search_clause(
        self,
        query: str,
        search_columns: List[str],
        exact_match: bool,
        case_sensitive: bool
    ) -> ColumnElement[bool]:
        clauses = []
        
        for col_name in search_columns:
            column = self._get_column(col_name)
            
            if exact_match:
                if case_sensitive:
                    clauses.append(column == query)
                else:
                    clauses.append(col(column).ilike(query))
            else:
                pattern = f"%{query}%"
                if case_sensitive:
                    clauses.append(col(column).like(pattern))
                else:
                    clauses.append(col(column).ilike(pattern))
        
        return or_(*clauses)
    
    async def search(
        self,
        query: str,
        search_columns: List[str],
        *,
        exact_match: bool = False,
        case_sensitive: bool = False,
        skip: int = 0,
        limit: int = 20
    ) -> Sequence[ModelType]:
        if not query.strip() or not search_columns:
            return []
        
        clause = self._build_search_clause(query, search_columns, exact_match, case_sensitive)
        statement = select(self.model).where(clause).offset(skip).limit(limit)
        return ( await self.db.exec(statement)).all()
    
    async def count_search(
        self,
        query: str,
        search_columns: List[str],
        *,
        exact_match: bool = False,
        case_sensitive: bool = False
    ) -> int:
        if not query.strip() or not search_columns:
            return 0
        
        clause = self._build_search_clause(query, search_columns, exact_match, case_sensitive)
        count_statement = select(func.count()).select_from(self.model).where(clause)
        result = await self.db.exec(count_statement)
        return result.one()