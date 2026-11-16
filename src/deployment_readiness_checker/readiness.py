from dataclasses import dataclass

from deployment_readiness_checker.models import DeploymentConfig
from deployment_readiness_checker.policies import ENVIRONMENT_POLICIES


@dataclass
class ReadinessResult:
    is_ready: bool
    findings: list[str]
    score: int | None = None


def evaluate_readiness(
    config: DeploymentConfig,
    enable_scoring: bool = False,
) -> ReadinessResult:
    findings = []
    policy = ENVIRONMENT_POLICIES[config.environment]

    if config.replicas < policy.minimum_replicas:
        findings.append(
            f"{config.environment.capitalize()} deployments require at least "
            f"{policy.minimum_replicas} replicas."
        )
    if config.replicas > policy.maximum_replicas:
        findings.append(
            f"{config.environment.capitalize()} deployments are limited to "
            f"{policy.maximum_replicas} replicas."
        )
    if policy.reject_latest_image and config.image.endswith(":latest"):
        findings.append(
            "Container image must use a specific version tag, not 'latest'."
        )

    return ReadinessResult(
        is_ready=not findings,
        findings=findings,
    )
