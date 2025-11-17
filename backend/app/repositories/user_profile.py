from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.user_profile import ProfileCreate, ProfileUpdate
from app.models.user_profile import UserProfile
from sqlalchemy.ext.asyncio import AsyncSession

class UserProfileRepository(BaseCRUD[UserProfile, ProfileCreate, ProfileUpdate], SearchableRepository):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, UserProfile, db)
        SearchableRepository.__init__(self, UserProfile, db)

