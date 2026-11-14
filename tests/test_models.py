import pytest

from deployment_readiness_checker.models import DeploymentConfig


def test_deployment_config_creation():
    config = DeploymentConfig(
        service_name="payment-api",
        environment="production",
        image="payment-api:1.0.0",
        replicas=3,
    )

    assert config.service_name == "payment-api"
    assert config.environment == "production"
    assert config.image == "payment-api:1.0.0"
    assert config.replicas == 3


@pytest.mark.parametrize(
    "environment",
    ["development", "staging", "production"],
)
def test_deployment_config_accepts_valid_environments(environment):
    config = DeploymentConfig(
        service_name="payment-api",
        environment=environment,
        image="payment-api:1.0.0",
        replicas=3,
    )

    assert config.environment == environment


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("service_name", " ", "Service name cannot be empty."),
        ("environment", "testing", "Unsupported environment: testing"),
        ("image", "", "Container image cannot be empty."),
        ("replicas", 0, "Replica count must be greater than zero."),
        ("replicas", -1, "Replica count must be greater than zero."),
    ],
)
def test_deployment_config_rejects_invalid_values(field, value, error):
    values = {
        "service_name": "payment-api",
        "environment": "production",
        "image": "payment-api:1.0.0",
        "replicas": 3,
    }
    values[field] = value

    with pytest.raises(ValueError, match=error):
        DeploymentConfig(**values)
