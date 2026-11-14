from dataclasses import dataclass


@dataclass
class DeploymentConfig:
    service_name: str
    environment: str
    image: str
    replicas: int
