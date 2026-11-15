import json
from pathlib import Path

from deployment_readiness_checker.models import (
    DeploymentConfig,
    ResourceRequirements,
    ResourceValues,
)


def load_config(file_path: str | Path) -> DeploymentConfig:
    try:
        with Path(file_path).open(encoding="utf-8") as config_file:
            config_data = json.load(config_file)
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON: {error}") from error

    if not isinstance(config_data, dict):
        raise ValueError("JSON configuration must be an object.")

    resources_data = config_data.get("resources")

    if not isinstance(resources_data, dict):
        raise ValueError("Deployment resources are required.")

    try:
        resources = ResourceRequirements(
            requests=ResourceValues(**resources_data["requests"]),
            limits=ResourceValues(**resources_data["limits"]),
        )
    except (KeyError, TypeError) as error:
        raise ValueError(f"Invalid resource configuration: {error}") from error

    config_data["resources"] = resources

    return DeploymentConfig(**config_data)
