import pytest

from deployment_readiness_checker.cli import main


def test_cli_accepts_ready_configuration(capsys):
    result = main(
        [
            "--service",
            "payment-api",
            "--environment",
            "production",
            "--image",
            "payment-api:1.0.0",
            "--replicas",
            "3",
        ]
    )

    captured = capsys.readouterr()

    assert result == 0
    assert (
        "Deployment 'payment-api' is READY for the 'production' environment."
    ) in captured.out


def test_cli_rejects_unready_configuration(capsys):
    result = main(
        [
            "--service",
            "payment-api",
            "--environment",
            "production",
            "--image",
            "payment-api:1.0.0",
            "--replicas",
            "1",
        ]
    )

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
            "replicas": 3
        }
        """,
        encoding="utf-8",
    )

    result = main(["--config", str(config_file)])

    captured = capsys.readouterr()

    assert result == 0
    assert "Deployment 'payment-api' is READY" in captured.out


def test_cli_rejects_invalid_configuration(capsys):
    result = main(
        [
            "--service",
            "payment-api",
            "--environment",
            "production",
            "--image",
            "payment-api:latest",
            "--replicas",
            "1",
        ]
    )

    captured = capsys.readouterr()

    assert result == 1
    assert "is NOT READY" in captured.out
    assert "Production deployments require at least 2 replicas." in captured.out
    assert "Container image must use a specific version tag, not 'latest'." in (
        captured.out
    )


@pytest.mark.parametrize(
    ("arguments", "error"),
    [
        (
            [
                "--service",
                " ",
                "--environment",
                "production",
                "--image",
                "payment-api:1.0.0",
                "--replicas",
                "3",
            ],
            "Service name cannot be empty.",
        ),
        (
            [
                "--service",
                "payment-api",
                "--environment",
                "testing",
                "--image",
                "payment-api:1.0.0",
                "--replicas",
                "3",
            ],
            "Unsupported environment: testing",
        ),
        (
            [
                "--service",
                "payment-api",
                "--environment",
                "production",
                "--image",
                "",
                "--replicas",
                "3",
            ],
            "Container image cannot be empty.",
        ),
        (
            [
                "--service",
                "payment-api",
                "--environment",
                "production",
                "--image",
                "payment-api:1.0.0",
                "--replicas",
                "0",
            ],
            "Replica count must be greater than zero.",
        ),
    ],
)
def test_cli_handles_invalid_configuration(arguments, error, capsys):
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
