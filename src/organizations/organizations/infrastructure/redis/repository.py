from src.core.redis.interfaces.repository import RedisRepository

from src.organizations.organizations.interfaces.repository import OrganizationRequestsRepository
from src.organizations.organizations.domain.value_obj import OrganizationRequest

class RedisOrganizationRequestsRepository(RedisRepository, OrganizationRequestsRepository):
    model = OrganizationRequest
    key_fields = ["nickname"]