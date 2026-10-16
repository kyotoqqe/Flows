from sqlalchemy import MetaData
from sqlalchemy.orm import registry

test_metadata_obj = MetaData()
test_mapper_registry = registry(metadata=test_metadata_obj)
