from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from src.core.domain.entities import AbstractModel

@dataclass
class Image(AbstractModel):
    key: str
    checksum: str
    created_at: datetime = field(init = False)
    updated_at: datetime = field(init = False)
    alt_text: Optional[str] = None