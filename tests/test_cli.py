import pytest

from deployment_readiness_checker.cli import main


def test_cli_accepts_valid_configuration(capsys):
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
        "Deployment configuration for 'payment-api' "
        "is valid in the 'production' environment."
    ) in captured.out


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
def test_cli_rejects_invalid_configuration(arguments, error, capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(arguments)

    captured = capsys.readouterr()

    assert exc_info.value.code == 2
    assert error in captured.err
