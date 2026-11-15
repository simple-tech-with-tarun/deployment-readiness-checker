import pytest

from deployment_readiness_checker.cli import main


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


def test_cli_accepts_ready_configuration(capsys):
    result = main(create_cli_arguments())

    captured = capsys.readouterr()

    assert result == 0
    assert (
        "Deployment 'payment-api' is READY for the 'production' environment."
    ) in captured.out


def test_cli_rejects_unready_configuration(capsys):
    arguments = create_cli_arguments()
    arguments[arguments.index("--replicas") + 1] = "1"

    result = main(arguments)

    captured = capsys.readouterr()

    assert result == 1
    assert "Deployment 'payment-api' is NOT READY" in captured.out
    assert "Production deployments require at least 2 replicas." in captured.out


def test_cli_accepts_ready_json_configuration(tmp_path, capsys):
    config_file = tmp_path / "deployment.json"
    config_file.write_text(
        """
        {
            "service_name": "payment-api",
            "environment": "production",
            "image": "payment-api:1.0.0",
            "replicas": 3,
            "resources": {
                "requests": {
                    "cpu": "250m",
                    "memory": "256Mi"
                },
                "limits": {
                    "cpu": "1000m",
                    "memory": "512Mi"
                }
            }
        }
        """,
        encoding="utf-8",
    )

    result = main(["--config", str(config_file)])

    captured = capsys.readouterr()

    assert result == 0
    assert "Deployment 'payment-api' is READY" in captured.out


def test_cli_rejects_invalid_configuration(capsys):
    arguments = create_cli_arguments()
    arguments[arguments.index("--image") + 1] = "payment-api:latest"
    arguments[arguments.index("--replicas") + 1] = "1"

    result = main(arguments)

    captured = capsys.readouterr()

    assert result == 1
    assert "is NOT READY" in captured.out
    assert "Production deployments require at least 2 replicas." in captured.out
    assert "Container image must use a specific version tag, not 'latest'." in (
        captured.out
    )


@pytest.mark.parametrize(
    ("argument", "value", "error"),
    [
        ("--service", " ", "Service name cannot be empty."),
        ("--environment", "testing", "Unsupported environment: testing"),
        ("--image", "", "Container image cannot be empty."),
        ("--replicas", "0", "Replica count must be greater than zero."),
        ("--cpu-request", "invalid", "Invalid CPU resource value"),
        (
            "--cpu-limit",
            "100m",
            "CPU limit cannot be lower than CPU request.",
        ),
        (
            "--memory-limit",
            "128Mi",
            "Memory limit cannot be lower than memory request.",
        ),
    ],
)
def test_cli_handles_invalid_configuration(argument, value, error, capsys):
    arguments = create_cli_arguments()
    arguments[arguments.index(argument) + 1] = value

    result = main(arguments)

    captured = capsys.readouterr()

    assert result == 1
    assert error in captured.err


def test_cli_rejects_missing_arguments():
    with pytest.raises(SystemExit) as exc_info:
        main(["--service", "payment-api"])

    assert exc_info.value.code == 2


def test_cli_rejects_combined_input_modes():
    with pytest.raises(SystemExit) as exc_info:
        main(
            [
                "--config",
                "deployment.json",
                "--service",
                "payment-api",
            ]
        )

    assert exc_info.value.code == 2
