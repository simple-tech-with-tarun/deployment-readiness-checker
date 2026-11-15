from deployment_readiness_checker.models import DeploymentConfig
from deployment_readiness_checker.readiness import ReadinessResult


def create_readiness_report(
    config: DeploymentConfig,
    result: ReadinessResult,
) -> dict:
    return {
        "deployment": {
            "service_name": config.service_name,
            "environment": config.environment,
            "image": config.image,
            "replicas": config.replicas,
        },
        "resources": {
            "requests": {
                "cpu": config.resources.requests.cpu,
                "memory": config.resources.requests.memory,
            },
            "limits": {
                "cpu": config.resources.limits.cpu,
                "memory": config.resources.limits.memory,
            },
        },
        "readiness": {
            "status": "READY" if result.is_ready else "NOT_READY",
            "is_ready": result.is_ready,
            "findings": result.findings,
        },
    }


def create_text_readiness_report(
    config: DeploymentConfig,
    result: ReadinessResult,
) -> str:
    status = "READY" if result.is_ready else "NOT_READY"

    findings = (
        "\n".join(f"- {finding}" for finding in result.findings)
        if result.findings
        else "- None"
    )

    return (
        "Deployment Readiness Report\n"
        "===========================\n"
        f"Service: {config.service_name}\n"
        f"Environment: {config.environment}\n"
        f"Image: {config.image}\n"
        f"Replicas: {config.replicas}\n"
        f"Status: {status}\n"
        "Findings:\n"
        f"{findings}"
    )
