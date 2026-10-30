from dataclasses import dataclass, field
from backend.models.enums import ValidationSeverity


@dataclass
class ValidationIssue:
    code: str
    message: str
    stage: str
    severity: ValidationSeverity


@dataclass
class ValidationReport:

    issues: list[ValidationIssue] = field(default_factory=list)
    
    @property
    def has_critical_issue(self) -> bool:
        return any(issue.severity == ValidationSeverity.CRITICAL for issue in self.issues)

    @property
    def has_recoverable_issue(self) -> bool:
        return any(issue.severity ==  ValidationSeverity.RECOVERABLE for issue in self.issues)


    def add(
        self,
        code: str,
        message: str,
        stage: str,
        severity: ValidationSeverity = ValidationSeverity.CRITICAL
    ):
        self.issues.append(
            ValidationIssue(
                code=code,
                messagae=message,
                stage=stage,
                severity=severity
            )
        )

    def to_dict(self):
        return {
            "issues": [
                {
                    "code": issue.code,
                    "message": issue.message,
                    "stage": issue.stage,
                    "severity": issue.severity.value
                }
                for issue in self.issues
            ]
        }
