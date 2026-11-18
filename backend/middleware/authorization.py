
from fastapi import HTTPException


class RequireRole:

    def __init__(self, required_roles: list[str]):
        self.required_roles = required_roles


    def __call__(self, user: dict) -> dict:
        user_role = user.get("role")
        if user_role not in self.required_roles:
            raise HTTPException(status_code=403, detail=f"user role {user_role} not in required roles {self.required_roles}")
        
        return user

require_admin = RequireRole(["admin"])
require_agent = RequireRole(["admin", "agent"])
require_customer = RequireRole(["admin", "agent", "customer"])