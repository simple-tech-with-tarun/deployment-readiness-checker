import json

import pytest

from deployment_readiness_checker.config_loader import load_config
from deployment_readiness_checker.models import DeploymentConfig


def test_load_config_from_valid_json(tmp_path):
    config_data = {
        "service_name": "payment-api",
        "environment": "production",
        "image": "payment-api:1.0.0",
        "replicas": 3,
    }

    config_file = tmp_path / "deployment.json"
    config_file.write_text(json.dumps(config_data), encoding="utf-8")

    config = load_config(config_file)

    assert isinstance(config, DeploymentConfig)
    assert config.service_name == "payment-api"
    assert config.environment == "production"
    assert config.image == "payment-api:1.0.0"
    assert config.replicas == 3


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
    config_data = {
        "service_name": "payment-api",
        "environment": "production",
        "image": "payment-api:1.0.0",
    }

    config_file = tmp_path / "deployment.json"
    config_file.write_text(json.dumps(config_data), encoding="utf-8")

    with pytest.raises(TypeError, match="replicas"):
        load_config(config_file)


def test_load_config_rejects_invalid_environment(tmp_path):
    config_data = {
        "service_name": "payment-api",
        "environment": "testing",
        "image": "payment-api:1.0.0",
        "replicas": 3,
    }

    config_file = tmp_path / "deployment.json"
    config_file.write_text(json.dumps(config_data), encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported environment: testing"):
        load_config(config_file)


def test_load_config_rejects_non_object_json(tmp_path):
    config_file = tmp_path / "deployment.json"
    config_file.write_text('["payment-api", "production"]', encoding="utf-8")

    with pytest.raises(ValueError, match="JSON configuration must be an object"):
        load_config(config_file)
