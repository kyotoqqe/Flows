from src.core.redis.interfaces.repository import RedisRepository
from src.auth.interfaces.repository import RefreshSessionsRepository
from src.auth.domain.value_obj import RefreshSession

class RedisRefreshSessionsRepository(RedisRepository, RefreshSessionsRepository):
    model = RefreshSession
    key_fields = ["user_id", "token"]