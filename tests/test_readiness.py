from deployment_readiness_checker.models import DeploymentConfig
from deployment_readiness_checker.readiness import evaluate_readiness


def test_evaluate_readiness_accepts_ready_production_config():
    config = DeploymentConfig(
        service_name="payment-api",
        environment="production",
        image="payment-api:1.0.0",
        replicas=3,
    )

    result = evaluate_readiness(config)

    assert result.is_ready is True
    assert result.findings == []


def test_evaluate_readiness_rejects_production_with_one_replica():
    config = DeploymentConfig(
        service_name="payment-api",
        environment="production",
        image="payment-api:1.0.0",
        replicas=1,
    )

    result = evaluate_readiness(config)

    assert result.is_ready is False
    assert result.findings == ["Production deployments require at least 2 replicas."]


def test_evaluate_readiness_accepts_staging_with_one_replica():
    config = DeploymentConfig(
        service_name="payment-api",
        environment="staging",
        image="payment-api:1.0.0",
        replicas=1,
    )

    result = evaluate_readiness(config)

    assert result.is_ready is True
    assert result.findings == []


def test_evaluate_readiness_rejects_latest_image_tag():
    config = DeploymentConfig(
        service_name="payment-api",
        environment="staging",
        image="payment-api:latest",
        replicas=2,
    )

    result = evaluate_readiness(config)

    assert result.is_ready is False
    assert result.findings == [
        "Container image must use a specific version tag, not 'latest'."
    ]


def test_evaluate_readiness_reports_multiple_findings():
    config = DeploymentConfig(
        service_name="payment-api",
        environment="production",
        image="payment-api:latest",
        replicas=1,
    )

    result = evaluate_readiness(config)

    assert result.is_ready is False
    assert result.findings == [
        "Production deployments require at least 2 replicas.",
        "Container image must use a specific version tag, not 'latest'.",
    ]
