from dataclasses import dataclass, field
from datetime import datetime

from src.core.domain.rules import BaseRule

def check_rule(rule: BaseRule):
    if rule.is_broken():
        raise rule.exception()

class BusinessRuleValidationMixin:
    def check_rule(self, rule: BaseRule):
        check_rule(rule)

@dataclass
class TimeStampMixin:
    created_at: datetime = field(init = False)
    updated_at: datetime = field(init = False)