from src.core.redis.interfaces.repository import RedisRepository

from src.profiles.interfaces.repository import FollowRequestsRepository
from src.profiles.domain.value_obj import FollowRequest

class RedisFollowRequetstRepository(RedisRepository, FollowRequestsRepository):
    model=FollowRequest
    key_fields = ["follower_id", "following_id"]