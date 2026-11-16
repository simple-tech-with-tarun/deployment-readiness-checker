import argparse
import json
import sys
from collections.abc import Sequence

from deployment_readiness_checker.config_loader import load_config
from deployment_readiness_checker.models import (
    DeploymentConfig,
    ResourceRequirements,
    ResourceValues,
)
from deployment_readiness_checker.readiness import evaluate_readiness
from deployment_readiness_checker.reporting import create_readiness_report


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
    parser.add_argument(
        "--cpu-request",
        help="Requested CPU resources (e.g. 250m).",
    )
    parser.add_argument(
        "--memory-request",
        help="Requested memory resources (e.g. 256Mi).",
    )
    parser.add_argument(
        "--cpu-limit",
        help="Maximum CPU resources (e.g. 1000m).",
    )
    parser.add_argument(
        "--memory-limit",
        help="Maximum memory resources (e.g. 512Mi).",
    )
    parser.add_argument(
        "--output",
        choices=("text", "json"),
        default="text",
        help="Output format (text or json).",
    )
    parser.add_argument(
        "--experimental-insights",
        action="store_true",
        default=False,
        help="Enable experimental deployment insights.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)

    individual_arguments = (
        args.service,
        args.environment,
        args.image,
        args.replicas,
        args.cpu_request,
        args.memory_request,
        args.cpu_limit,
        args.memory_limit,
    )

    try:
        if args.config:
            if any(value is not None for value in individual_arguments):
                parser.error("--config cannot be combined with individual arguments.")

            config = load_config(args.config)

        else:
            if any(value is None for value in individual_arguments):
                parser.error(
                    "Provide either --config or all deployment and resource arguments."
                )

            resources = ResourceRequirements(
                requests=ResourceValues(
                    cpu=args.cpu_request,
                    memory=args.memory_request,
                ),
                limits=ResourceValues(
                    cpu=args.cpu_limit,
                    memory=args.memory_limit,
                ),
            )

            config = DeploymentConfig(
                service_name=args.service,
                environment=args.environment,
                image=args.image,
                replicas=args.replicas,
                resources=resources,
            )

        result = evaluate_readiness(config)

    except (OSError, ValueError, TypeError) as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 1

    if args.output == "json":
        report = create_readiness_report(config, result)
        print(json.dumps(report, indent=2))
        return 0 if result.is_ready else 1

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
