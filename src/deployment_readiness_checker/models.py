import re
from dataclasses import dataclass

VALID_ENVIRONMENTS = {"development", "staging", "production"}

CPU_PATTERN = re.compile(r"^(?:\d+(?:\.\d+)?|\d+m)$")
MEMORY_PATTERN = re.compile(r"^\d+(?:\.\d+)?(?:Ki|Mi|Gi|Ti|Pi|Ei|K|M|G|T|P|E)?$")

MEMORY_UNITS = {
    "": 1,
    "K": 1000,
    "M": 1000**2,
    "G": 1000**3,
    "T": 1000**4,
    "P": 1000**5,
    "E": 1000**6,
    "Ki": 1024,
    "Mi": 1024**2,
    "Gi": 1024**3,
    "Ti": 1024**4,
    "Pi": 1024**5,
    "Ei": 1024**6,
}


def parse_cpu(value: str) -> float:
    if not isinstance(value, str) or not CPU_PATTERN.fullmatch(value):
        raise ValueError(f"Invalid CPU resource value: {value}")

    amount = float(value[:-1]) / 1000 if value.endswith("m") else float(value)

    if amount <= 0:
        raise ValueError("CPU resource values must be greater than zero.")

    return amount


def parse_memory(value: str) -> float:
    if not isinstance(value, str) or not MEMORY_PATTERN.fullmatch(value):
        raise ValueError(f"Invalid memory resource value: {value}")

    unit = next(
        (suffix for suffix in MEMORY_UNITS if suffix and value.endswith(suffix)),
        "",
    )
    amount = float(value[: -len(unit)]) if unit else float(value)
    total = amount * MEMORY_UNITS[unit]

    if total <= 0:
        raise ValueError("Memory resource values must be greater than zero.")

    return total


@dataclass
class ResourceValues:
    cpu: str
    memory: str

    def __post_init__(self) -> None:
        parse_cpu(self.cpu)
        parse_memory(self.memory)


@dataclass
class ResourceRequirements:
    requests: ResourceValues
    limits: ResourceValues

    def __post_init__(self) -> None:
        if not isinstance(self.requests, ResourceValues):
            raise ValueError("Resource requests must be ResourceValues.")

        if not isinstance(self.limits, ResourceValues):
            raise ValueError("Resource limits must be ResourceValues.")

        if parse_cpu(self.limits.cpu) < parse_cpu(self.requests.cpu):
            raise ValueError("CPU limit cannot be lower than CPU request.")

        if parse_memory(self.limits.memory) < parse_memory(self.requests.memory):
            raise ValueError("Memory limit cannot be lower than memory request.")


@dataclass
class DeploymentConfig:
    service_name: str
    environment: str
    image: str
    replicas: int
    resources: ResourceRequirements

    def __post_init__(self) -> None:
        if not self.service_name.strip():
            raise ValueError("Service name cannot be empty.")

        if self.environment not in VALID_ENVIRONMENTS:
            raise ValueError(f"Unsupported environment: {self.environment}")

        if not self.image.strip():
            raise ValueError("Container image cannot be empty.")

        if self.replicas < 1:
            raise ValueError("Replica count must be greater than zero.")

        if not isinstance(self.resources, ResourceRequirements):
            raise ValueError("Deployment resources are required.")
