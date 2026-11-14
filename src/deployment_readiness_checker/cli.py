import argparse
from collections.abc import Sequence

from deployment_readiness_checker.models import DeploymentConfig


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deployment-readiness-checker",
        description="Validate deployment configuration.",
    )

    parser.add_argument(
        "--service",
        required=True,
        help="Name of the service.",
    )
    parser.add_argument(
        "--environment",
        required=True,
        help="Deployment environment.",
    )
    parser.add_argument(
        "--image",
        required=True,
        help="Container image.",
    )
    parser.add_argument(
        "--replicas",
        required=True,
        type=int,
        help="Number of replicas.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)

    try:
        config = DeploymentConfig(
            service_name=args.service,
            environment=args.environment,
            image=args.image,
            replicas=args.replicas,
        )
    except ValueError as error:
        parser.error(str(error))

    print(
        f"Deployment configuration for '{config.service_name}' "
        f"is valid in the '{config.environment}' environment."
    )

    return 0
