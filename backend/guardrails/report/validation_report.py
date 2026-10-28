from dataclasses import dataclass, field

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
