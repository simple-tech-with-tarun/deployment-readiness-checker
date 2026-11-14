from dataclasses import dataclass

from deployment_readiness_checker.models import DeploymentConfig


@dataclass
class ReadinessResult:
    is_ready: bool
    findings: list[str]


def evaluate_readiness(config: DeploymentConfig) -> ReadinessResult:
    findings = []

    if config.environment == "production" and config.replicas < 2:
        findings.append("Production deployments require at least 2 replicas.")

    if config.image.endswith(":latest"):
        findings.append(
            "Container image must use a specific version tag, not 'latest'."
        )

    return ReadinessResult(
        is_ready=not findings,
        findings=findings,
    )
