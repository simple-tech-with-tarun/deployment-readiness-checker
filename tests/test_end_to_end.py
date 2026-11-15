import json
import subprocess
import sys


def run_cli(arguments):
    return subprocess.run(
        [
            sys.executable,
            "-c",
            "from deployment_readiness_checker.cli import main; "
            "raise SystemExit(main())",
            *arguments,
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def create_cli_arguments():
    return [
        "--service",
        "payment-api",
        "--environment",
        "production",
        "--image",
        "payment-api:1.0.0",
        "--replicas",
        "3",
        "--cpu-request",
        "250m",
        "--memory-request",
        "256Mi",
        "--cpu-limit",
        "1000m",
        "--memory-limit",
        "512Mi",
    ]


def test_end_to_end_ready_deployment_json_output():
    result = run_cli(create_cli_arguments() + ["--output", "json"])

    report = json.loads(result.stdout)

    assert result.returncode == 0
    assert report["deployment"]["service_name"] == "payment-api"
    assert report["readiness"]["status"] == "READY"
    assert report["readiness"]["is_ready"] is True
    assert report["readiness"]["findings"] == []


def test_end_to_end_unready_deployment_text_output():
    arguments = create_cli_arguments()
    arguments[arguments.index("--replicas") + 1] = "1"

    result = run_cli(arguments)

    assert result.returncode == 1
    assert "Deployment 'payment-api' is NOT READY" in result.stdout
    assert "Production deployments require at least 2 replicas." in (result.stdout)
