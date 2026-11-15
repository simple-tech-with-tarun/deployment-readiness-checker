import pytest

from deployment_readiness_checker.models import (
    DeploymentConfig,
    ResourceRequirements,
    ResourceValues,
    parse_cpu,
    parse_memory,
)


def create_resources():
    return ResourceRequirements(
        requests=ResourceValues(cpu="250m", memory="256Mi"),
        limits=ResourceValues(cpu="1000m", memory="512Mi"),
    )


def test_deployment_config_creation():
    config = DeploymentConfig(
        service_name="payment-api",
        environment="production",
        image="payment-api:1.0.0",
        replicas=3,
        resources=create_resources(),
    )

    assert config.service_name == "payment-api"
    assert config.environment == "production"
    assert config.image == "payment-api:1.0.0"
    assert config.replicas == 3
    assert config.resources.requests.cpu == "250m"
    assert config.resources.limits.memory == "512Mi"


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
        resources=create_resources(),
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
        "resources": create_resources(),
    }
    values[field] = value

    with pytest.raises(ValueError, match=error):
        DeploymentConfig(**values)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1", 1.0),
        ("500m", 0.5),
        ("250m", 0.25),
        ("1.5", 1.5),
    ],
)
def test_parse_cpu_accepts_valid_values(value, expected):
    assert parse_cpu(value) == expected


@pytest.mark.parametrize(
    "value",
    ["0", "0m", "-1", "invalid", "500mm"],
)
def test_parse_cpu_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        parse_cpu(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("256Mi", 256 * 1024**2),
        ("1Gi", 1024**3),
        ("1G", 1000**3),
        ("512", 512),
    ],
)
def test_parse_memory_accepts_valid_values(value, expected):
    assert parse_memory(value) == expected


@pytest.mark.parametrize(
    "value",
    ["0Mi", "-1Gi", "invalid", "256MB"],
)
def test_parse_memory_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        parse_memory(value)


def test_resource_requirements_rejects_cpu_limit_below_request():
    with pytest.raises(ValueError, match="CPU limit cannot be lower"):
        ResourceRequirements(
            requests=ResourceValues(cpu="1000m", memory="256Mi"),
            limits=ResourceValues(cpu="500m", memory="512Mi"),
        )


def test_resource_requirements_rejects_memory_limit_below_request():
    with pytest.raises(ValueError, match="Memory limit cannot be lower"):
        ResourceRequirements(
            requests=ResourceValues(cpu="250m", memory="512Mi"),
            limits=ResourceValues(cpu="1000m", memory="256Mi"),
        )


def test_resource_requirements_accepts_equal_requests_and_limits():
    resources = ResourceRequirements(
        requests=ResourceValues(cpu="500m", memory="512Mi"),
        limits=ResourceValues(cpu="0.5", memory="512Mi"),
    )

    assert resources.requests.cpu == "500m"
    assert resources.limits.cpu == "0.5"
