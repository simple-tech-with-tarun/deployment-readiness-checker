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
