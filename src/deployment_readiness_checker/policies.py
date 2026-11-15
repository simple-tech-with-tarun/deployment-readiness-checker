from dataclasses import dataclass


@dataclass(frozen=True)
class EnvironmentPolicy:
    minimum_replicas: int
    reject_latest_image: bool = True


ENVIRONMENT_POLICIES = {
    "development": EnvironmentPolicy(minimum_replicas=1),
    "staging": EnvironmentPolicy(minimum_replicas=1),
    "production": EnvironmentPolicy(minimum_replicas=2),
}
