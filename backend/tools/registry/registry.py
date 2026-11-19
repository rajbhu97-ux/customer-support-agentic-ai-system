from backend.models.tools import ToolPermission, RegisteredTool
from collections import defaultdict
from typing import Callable, Optional
import time


class ToolRegistry:

    def __init__(self):
        self._tools: dict[str, RegisteredTool] = {}
        self._call_logs: dict[str, list[str]] = defaultdict(list)

    def register(
        self,
        name: str,
        func: Callable,
        description: str,
        permission: ToolPermission,
        category: str = "general",
    ):
        self._tools[name] = RegisteredTool(
            name=name,
            func=func,
            description=description,
            permission=permission,
            category=category,
        )

    def get(self, name: str) -> Optional[RegisteredTool]:
        return self._tools.get(name)

    def list_for_agents(self, agent_id: str) -> list[RegisteredTool]:
        return [
            tool
            for tool in self._tools.values()
            if agent_id in tool.permission.allowed_agents
        ]

    def check_access(self, tool_name: str, agent_id: str) -> tuple[bool, str]:
        tool = self.get(tool_name)
        if not tool:
            return False, f"Tool {tool_name} not found"
        if agent_id not in tool.permission.allowed_agents:
            return False, f"Agent {agent_id} not allowed to use tool {tool_name}"

        if not self._check_rate_limit(tool_name):
            return False, f"Rate limit exceed for the tool '{tool_name}'"
        return True, "Allowed"

    def _check_rate_limit(self, tool_name: str) -> bool:
        tool = self.get(tool_name)
        now = time.time()
        cutoff = now - tool.permission.rate_window
        self._call_logs[tool_name] = [
            t for t in self._call_logs[tool_name] if t > cutoff
        ]
        if len(self._call_logs[tool_name]) >= tool.permission.rate_limit:
            return False
        self._call_logs[tool_name].append(now)
        return True

    def is_requires_approval(self, tool_name: str) -> bool:
        tool = self.get(tool_name)
        return tool.permission.requires_approval if tool else False


tool_registry = ToolRegistry()