import argparse
import sys
from collections.abc import Sequence

from deployment_readiness_checker.config_loader import load_config
from deployment_readiness_checker.models import DeploymentConfig
from deployment_readiness_checker.readiness import evaluate_readiness


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deployment-readiness-checker",
        description="Evaluate deployment readiness.",
    )

    parser.add_argument(
        "--config",
        help="Path to a JSON deployment configuration file.",
    )
    parser.add_argument(
        "--service",
        help="Name of the service.",
    )
    parser.add_argument(
        "--environment",
        help="Deployment environment.",
    )
    parser.add_argument(
        "--image",
        help="Container image.",
    )
    parser.add_argument(
        "--replicas",
        type=int,
        help="Number of replicas.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)

    try:
        if args.config:
            if any(
                value is not None
                for value in (
                    args.service,
                    args.environment,
                    args.image,
                    args.replicas,
                )
            ):
                parser.error("--config cannot be combined with individual arguments.")

            config = load_config(args.config)

        else:
            if any(
                value is None
                for value in (
                    args.service,
                    args.environment,
                    args.image,
                    args.replicas,
                )
            ):
                parser.error(
                    "Provide either --config or all four deployment arguments."
                )

            config = DeploymentConfig(
                service_name=args.service,
                environment=args.environment,
                image=args.image,
                replicas=args.replicas,
            )

        result = evaluate_readiness(config)

    except (OSError, ValueError, TypeError) as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 1

    if result.is_ready:
        print(
            f"Deployment '{config.service_name}' is READY "
            f"for the '{config.environment}' environment."
        )
        return 0

    print(
        f"Deployment '{config.service_name}' is NOT READY "
        f"for the '{config.environment}' environment."
    )

    for finding in result.findings:
        print(f"- {finding}")

    return 1
