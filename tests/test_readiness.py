from deployment_readiness_checker.models import (
    DeploymentConfig,
    ResourceRequirements,
    ResourceValues,
)
from deployment_readiness_checker.readiness import (
    evaluate_readiness,
    is_release_ready,
)


def create_resources():
    return ResourceRequirements(
        requests=ResourceValues(cpu="250m", memory="256Mi"),
        limits=ResourceValues(cpu="1000m", memory="512Mi"),
    )


def test_evaluate_readiness_accepts_ready_production_config():
    config = DeploymentConfig(
        service_name="payment-api",
        environment="production",
        image="payment-api:1.0.0",
        replicas=3,
        resources=create_resources(),
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
        resources=create_resources(),
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
        resources=create_resources(),
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
        resources=create_resources(),
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
        resources=create_resources(),
    )

    result = evaluate_readiness(config)

    assert result.is_ready is False
    assert result.findings == [
        "Production deployments require at least 2 replicas.",
        "Container image must use a specific version tag, not 'latest'.",
    ]


def test_evaluate_readiness_accepts_development_with_one_replica():
    config = DeploymentConfig(
        service_name="payment-api",
        environment="development",
        image="payment-api:1.0.0",
        replicas=1,
        resources=create_resources(),
    )

    result = evaluate_readiness(config)

    assert result.is_ready is True
    assert result.findings == []


def test_evaluate_readiness_rejects_latest_image_in_development():
    config = DeploymentConfig(
        service_name="payment-api",
        environment="development",
        image="payment-api:latest",
        replicas=1,
        resources=create_resources(),
    )

    result = evaluate_readiness(config)

    assert result.is_ready is False
    assert result.findings == [
        "Container image must use a specific version tag, not 'latest'."
    ]


def test_evaluate_readiness_rejects_staging_with_latest_image():
    config = DeploymentConfig(
        service_name="payment-api",
        environment="staging",
        image="payment-api:latest",
        replicas=1,
        resources=create_resources(),
    )

    result = evaluate_readiness(config)

    assert result.is_ready is False
    assert result.findings == [
        "Container image must use a specific version tag, not 'latest'."
    ]


def test_evaluate_readiness_rejects_development_above_maximum_replicas():
    config = DeploymentConfig(
        service_name="payment-api",
        environment="development",
        image="payment-api:1.0.0",
        replicas=4,
        resources=create_resources(),
    )

    result = evaluate_readiness(config)

    assert result.is_ready is False
    assert result.findings == ["Development deployments are limited to 3 replicas."]


def test_evaluate_readiness_rejects_staging_above_maximum_replicas():
    config = DeploymentConfig(
        service_name="payment-api",
        environment="staging",
        image="payment-api:1.0.0",
        replicas=11,
        resources=create_resources(),
    )

    result = evaluate_readiness(config)

    assert result.is_ready is False
    assert result.findings == ["Staging deployments are limited to 10 replicas."]


def test_evaluate_readiness_rejects_production_above_maximum_replicas():
    config = DeploymentConfig(
        service_name="payment-api",
        environment="production",
        image="payment-api:1.0.0",
        replicas=101,
        resources=create_resources(),
    )

    result = evaluate_readiness(config)

    assert result.is_ready is False
    assert result.findings == ["Production deployments are limited to 100 replicas."]


def test_scoring_is_disabled_by_default():
    config = DeploymentConfig(
        service_name="payment-api",
        environment="production",
        image="payment-api:1.0.0",
        replicas=3,
        resources=create_resources(),
    )

    result = evaluate_readiness(config)

    assert result.score is None


def test_scoring_returns_100_for_ready_config():
    config = DeploymentConfig(
        service_name="payment-api",
        environment="production",
        image="payment-api:1.0.0",
        replicas=3,
        resources=create_resources(),
    )

    result = evaluate_readiness(config, enable_scoring=True)

    assert result.score == 100
    assert result.is_ready is True


def test_scoring_deducts_30_for_minimum_replica_violation():
    config = DeploymentConfig(
        service_name="payment-api",
        environment="production",
        image="payment-api:1.0.0",
        replicas=1,
        resources=create_resources(),
    )

    result = evaluate_readiness(config, enable_scoring=True)

    assert result.score == 70
    assert result.is_ready is False


def test_scoring_deducts_20_for_maximum_replica_violation():
    config = DeploymentConfig(
        service_name="payment-api",
        environment="development",
        image="payment-api:1.0.0",
        replicas=4,
        resources=create_resources(),
    )

    result = evaluate_readiness(config, enable_scoring=True)

    assert result.score == 80
    assert result.is_ready is False


def test_scoring_deducts_25_for_latest_image():
    config = DeploymentConfig(
        service_name="payment-api",
        environment="staging",
        image="payment-api:latest",
        replicas=2,
        resources=create_resources(),
    )

    result = evaluate_readiness(config, enable_scoring=True)

    assert result.score == 75
    assert result.is_ready is False


def test_scoring_applies_multiple_deductions():
    config = DeploymentConfig(
        service_name="payment-api",
        environment="production",
        image="payment-api:latest",
        replicas=1,
        resources=create_resources(),
    )

    result = evaluate_readiness(config, enable_scoring=True)

    assert result.score == 45
    assert result.is_ready is False


def test_release_gate_accepts_ready_production_config():
    config = DeploymentConfig(
        service_name="payment-api",
        environment="production",
        image="payment-api:1.0.0",
        replicas=3,
        resources=create_resources(),
    )

    assert is_release_ready(config) is True


def test_release_gate_rejects_unready_production_config():
    config = DeploymentConfig(
        service_name="payment-api",
        environment="production",
        image="payment-api:1.0.0",
        replicas=1,
        resources=create_resources(),
    )

    assert is_release_ready(config) is False
