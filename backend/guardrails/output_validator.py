
from typing import Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict
from dataclasses import dataclass, field


class EntitiesModel(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)

    order_id: str | None = Field(default=None, max_length=64)
    product_name: str | None = Field(default=None, max_length=64)
    amount: float | None = Field(default=None, ge=0)
    date: str | None = Field(default=None, max_length=32)

    @field_validator("order_id")
    @classmethod
    def validate_order_id(cls, v:str | None) -> str | None:
        if v and not v.startswith("ORD-"):
            raise ValueError(f"OrderID must start with ORD- given orderId {v}")
        return v


class ActionTakenModel(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)

    tool: str | None = Field(default=None, max_length=100, min_length=1)
    result: str | None = Field(default=None, max_length=2000, min_length=1)


class DataForResponseModel(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)

    order_id: str | None = Field(default=None, max_length=64)
    order_status: Literal[
        "created",
        "processing",
        "shipped",
        "delivered",
        "cancelled",
        "refunded",
        "unknown"
    ] | None = None
    action_taken: str | None = Field(default=None, max_length=500)
    ticket_id: str | None = Field(default=None, max_length=64)
    additional_info: str | None = Field(default=None, max_length=2000)
    refund_amount: str | None = Field(default=None, max_length=32)
    refund_status: Literal[
        "not_requested",
        "pending",
        "approved",
        "processing",
        "completed",
        "rejected",
        "unknown"
    ] | None = None
    estimated_timeline: str | None = Field(default=None, max_length=200)
    tracking_status: str | None = Field(default=None, max_length=200)
    estimated_delivery: str | None = Field(default=None, max_length=100)
    customer_tier: Literal[
        "standard",
        "silver",
        "gold",
        "platinum",
        "unknown"
    ] | None = None

    @field_validator("order_id")
    @classmethod
    def validate_order_id(cls, v:str | None) -> str | None:
        if v and not v.startswith("ORD-"):
            raise ValueError(f"OrderID must start with ORD- given orderId {v}")
        return v

    @field_validator(
        "order_id",
        "ticket_id",
        "action_taken",
        "additional_info",
        "estimated_timeline",
        "tracking_status",
        "estimated_delivery"
    )
    @classmethod
    def reject_blank_strings(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError("Blank strings are not allowed")
        return v


class OutputValidationIssue(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)

    code: str
    severity: Literal[
        "warning",
        "recoverable",
        "critical"
    ]
    message: str
    stage: str


# Define validation report


@dataclass
class ValidationReport:

    issues: list[dict] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not any(issue["severity"] in ("critical", "recoverable") for issue in self.issues)
    
    @property
    def has_critical_severity(self) -> bool:
        return any(issue["severity"] == "critical" for issue in self.issues)

    def add(
        self,
        code: str,
        message: str,
        stage: str,
        severity: str = "critical"
    ):
        self.issues.append({
            "code": code,
            "message": message,
            "stage": stage,
            "severity": severity
        })


