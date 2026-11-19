from dataclasses import dataclass
from typing import Callable


@dataclass
class ToolPermission:
    allowed_agents: list[str]
    requires_approval: bool = False
    is_destructive: bool = False
    rate_limit: int = 60
    rate_window: int = 60
    cooldown: int = 0


@dataclass
class RegisteredTool:
    name: str
    func: Callable
    description: str
    permission: ToolPermission
    category: str = "general"
