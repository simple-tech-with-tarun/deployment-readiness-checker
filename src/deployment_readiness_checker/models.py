from dataclasses import dataclass

VALID_ENVIRONMENTS = {"development", "staging", "production"}


@dataclass
class DeploymentConfig:
    service_name: str
    environment: str
    image: str
    replicas: int

    def __post_init__(self) -> None:
        if not self.service_name.strip():
            raise ValueError("Service name cannot be empty.")

        if self.environment not in VALID_ENVIRONMENTS:
            raise ValueError(f"Unsupported environment: {self.environment}")

        if not self.image.strip():
            raise ValueError("Container image cannot be empty.")

        if self.replicas < 1:
            raise ValueError("Replica count must be greater than zero.")
