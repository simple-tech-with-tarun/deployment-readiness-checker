import json

import pytest

from deployment_readiness_checker.config_loader import load_config
from deployment_readiness_checker.models import DeploymentConfig


def create_config_data():
    return {
        "service_name": "payment-api",
        "environment": "production",
        "image": "payment-api:1.0.0",
        "replicas": 3,
        "resources": {
            "requests": {"cpu": "250m", "memory": "256Mi"},
            "limits": {"cpu": "1000m", "memory": "512Mi"},
        },
    }


def write_config(tmp_path, config_data):
    config_file = tmp_path / "deployment.json"
    config_file.write_text(json.dumps(config_data), encoding="utf-8")
    return config_file


def test_load_config_from_valid_json(tmp_path):
    config_file = write_config(tmp_path, create_config_data())

    config = load_config(config_file)

    assert isinstance(config, DeploymentConfig)
    assert config.service_name == "payment-api"
    assert config.environment == "production"
    assert config.image == "payment-api:1.0.0"
    assert config.replicas == 3
    assert config.resources.requests.cpu == "250m"
    assert config.resources.requests.memory == "256Mi"
    assert config.resources.limits.cpu == "1000m"
    assert config.resources.limits.memory == "512Mi"


def test_load_config_rejects_malformed_json(tmp_path):
    config_file = tmp_path / "deployment.json"
    config_file.write_text("{ invalid json }", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid JSON"):
        load_config(config_file)


def test_load_config_rejects_missing_file(tmp_path):
    config_file = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        load_config(config_file)


def test_load_config_rejects_missing_required_field(tmp_path):
    config_data = create_config_data()
    del config_data["replicas"]
    config_file = write_config(tmp_path, config_data)

    with pytest.raises(TypeError, match="replicas"):
        load_config(config_file)


def test_load_config_rejects_missing_resources(tmp_path):
    config_data = create_config_data()
    del config_data["resources"]
    config_file = write_config(tmp_path, config_data)

    with pytest.raises(ValueError, match="Deployment resources are required"):
        load_config(config_file)


def test_load_config_rejects_invalid_environment(tmp_path):
    config_data = create_config_data()
    config_data["environment"] = "testing"
    config_file = write_config(tmp_path, config_data)

    with pytest.raises(ValueError, match="Unsupported environment: testing"):
        load_config(config_file)


def test_load_config_rejects_invalid_resource_limits(tmp_path):
    config_data = create_config_data()
    config_data["resources"]["limits"]["cpu"] = "100m"
    config_file = write_config(tmp_path, config_data)

    with pytest.raises(ValueError, match="CPU limit cannot be lower"):
        load_config(config_file)


def test_load_config_rejects_non_object_json(tmp_path):
    config_file = tmp_path / "deployment.json"
    config_file.write_text('["payment-api", "production"]', encoding="utf-8")

    with pytest.raises(ValueError, match="JSON configuration must be an object"):
        load_config(config_file)
