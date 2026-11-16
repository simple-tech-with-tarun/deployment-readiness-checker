from dataclasses import dataclass


@dataclass(frozen=True)
class EnvironmentPolicy:
    minimum_replicas: int
    maximum_replicas: int
    reject_latest_image: bool = True


ENVIRONMENT_POLICIES = {
    "development": EnvironmentPolicy(
        minimum_replicas=1,
        maximum_replicas=3,
    ),
    "staging": EnvironmentPolicy(
        minimum_replicas=1,
        maximum_replicas=10,
    ),
    "production": EnvironmentPolicy(
        minimum_replicas=0,
        maximum_replicas=100,
    ),
}
