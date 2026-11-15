from deployment_readiness_checker.models import (
    DeploymentConfig,
    ResourceRequirements,
    ResourceValues,
)
from deployment_readiness_checker.readiness import ReadinessResult
from deployment_readiness_checker.reporting import (
    create_readiness_report,
    create_text_readiness_report,
)


def create_deployment_config():
    return DeploymentConfig(
        service_name="payment-api",
        environment="production",
        image="payment-api:1.0.0",
        replicas=3,
        resources=ResourceRequirements(
            requests=ResourceValues(cpu="250m", memory="256Mi"),
            limits=ResourceValues(cpu="1000m", memory="512Mi"),
        ),
    )


def test_create_readiness_report_for_ready_deployment():
    config = create_deployment_config()
    result = ReadinessResult(is_ready=True, findings=[])

    report = create_readiness_report(config, result)

    assert report == {
        "deployment": {
            "service_name": "payment-api",
            "environment": "production",
            "image": "payment-api:1.0.0",
            "replicas": 3,
        },
        "resources": {
            "requests": {"cpu": "250m", "memory": "256Mi"},
            "limits": {"cpu": "1000m", "memory": "512Mi"},
        },
        "readiness": {
            "status": "READY",
            "is_ready": True,
            "findings": [],
        },
    }


def test_create_readiness_report_for_unready_deployment():
    config = create_deployment_config()
    result = ReadinessResult(
        is_ready=False,
        findings=["Production deployments require at least 2 replicas."],
    )

    report = create_readiness_report(config, result)

    assert report["readiness"]["status"] == "NOT_READY"
    assert report["readiness"]["is_ready"] is False
    assert report["readiness"]["findings"] == [
        "Production deployments require at least 2 replicas."
    ]


def test_create_text_readiness_report_for_ready_deployment():
    config = create_deployment_config()
    result = ReadinessResult(is_ready=True, findings=[])

    report = create_text_readiness_report(config, result)

    assert report == (
        "Deployment Readiness Report\n"
        "===========================\n"
        "Service: payment-api\n"
        "Environment: production\n"
        "Image: payment-api:1.0.0\n"
        "Replicas: 3\n"
        "Status: READY\n"
        "Findings:\n"
        "- None"
    )


def test_create_text_readiness_report_for_unready_deployment():
    config = create_deployment_config()
    result = ReadinessResult(
        is_ready=False,
        findings=[
            "Production deployments require at least 2 replicas.",
            "Container image must use a specific version tag, not 'latest'.",
        ],
    )

    report = create_text_readiness_report(config, result)

    assert "Status: NOT_READY" in report
    assert "Findings:" in report
    assert "- Production deployments require at least 2 replicas." in report
    assert "- Container image must use a specific version tag, not 'latest'." in report
