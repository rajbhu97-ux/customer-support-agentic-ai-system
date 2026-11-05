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
    stages_validated: set = field(default_factory=set)
    
    @property
    def has_critical_issue(self) -> bool:
        return any(issue.severity == ValidationSeverity.CRITICAL for issue in self.issues)

    @property
    def is_valid(self) -> bool:
        return not self.has_critical_issue


    def get_issues(self, stage=None, severity=None):
        if stage:
            return [issue for issue in self.issues if issue.stage == stage]
        if severity:
            return [issue for issue in self.issues if issue.severity == severity]
        if stage and severity:
            return [issue for issue in self.issues if issue.stage == stage and issue.severity == severity]
        return self.issues


    def count_by_severity(self):
        return {
          severity.value: len([issue for issue in self.issues if issue.severity.value == severity.value]) for severity in ValidationSeverity
        }


    def mark_validated(self, stage:str):
        self.stages_validated.add(stage)


    def merge(other: ValidationReport):
        self.issues.extend(other.issues)
        self.stages_validated.update(other.stages_validated)


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
                message=message,
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
            ],
            "stages_validated": list(self.stages_validated)
        }
