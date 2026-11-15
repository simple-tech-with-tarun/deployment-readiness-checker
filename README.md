
# Deployment Readiness Checker

A Python CLI application that validates deployment configurations and evaluates whether deployments meet environment-specific readiness policies.

## Features

- Validate deployment configuration.
- Support development, staging, and production environments.
- Validate CPU and memory requests and limits.
- Load deployment configurations from JSON files.
- Evaluate deployment readiness using environment-specific policies.
- Generate human-readable or JSON readiness reports.
- Return meaningful exit codes for automation and CI/CD pipelines.

## Requirements

- Python 3.10 or newer
- pip

## Installation

Clone the repository:

```powershell
git clone https://github.com/simple-tech-with-tarun/deployment-readiness-checker.git
cd deployment-readiness-checker
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the application with development dependencies:

```powershell
python -m pip install -e ".[dev]"
```

## Usage

The application supports two ways to provide deployment configuration:

1. Individual CLI arguments.
2. A JSON configuration file.

### 1. CLI Arguments

Example:

```powershell
deployment-readiness-checker `
    --service payment-api `
    --environment production `
    --image payment-api:1.0.0 `
    --replicas 3 `
    --cpu-request 250m `
    --memory-request 256Mi `
    --cpu-limit 1000m `
    --memory-limit 512Mi
```

The default output format is human-readable text.

### 2. JSON Configuration

Create a file named `deployment.json`:

```json
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
```

Run the checker:

```powershell
deployment-readiness-checker --config .\deployment.json
```

The `--config` argument cannot be combined with individual deployment arguments.

## Output Formats

The application supports two output formats.

### Text Output

Text is the default output format.

```powershell
deployment-readiness-checker `
    --service payment-api `
    --environment production `
    --image payment-api:1.0.0 `
    --replicas 3 `
    --cpu-request 250m `
    --memory-request 256Mi `
    --cpu-limit 1000m `
    --memory-limit 512Mi
```

Example:

```text
Deployment 'payment-api' is READY for the 'production' environment.
```

### JSON Output

Use `--output json` to generate a structured readiness report.

```powershell
deployment-readiness-checker `
    --service payment-api `
    --environment production `
    --image payment-api:1.0.0 `
    --replicas 3 `
    --cpu-request 250m `
    --memory-request 256Mi `
    --cpu-limit 1000m `
    --memory-limit 512Mi `
    --output json
```

Example:

```json
{
  "deployment": {
    "service_name": "payment-api",
    "environment": "production",
    "image": "payment-api:1.0.0",
    "replicas": 3
  },
  "resources": {
    "requests": {
      "cpu": "250m",
      "memory": "256Mi"
    },
    "limits": {
      "cpu": "1000m",
      "memory": "512Mi"
    }
  },
  "readiness": {
    "status": "READY",
    "is_ready": true,
    "findings": []
  }
}
```

## Validation Rules

### Deployment Configuration

The application validates:

- Service name must not be empty.
- Environment must be development, staging, or production.
- Container image must not be empty.
- Replica count must be greater than zero.
- CPU and memory resource values must be valid and greater than zero.
- Resource limits cannot be lower than their corresponding requests.

### Resource Formats

CPU values support:

- Whole CPU values, such as `1`.
- Decimal CPU values, such as `1.5`.
- Millicore values, such as `250m`.

Memory values support:

- Byte values, such as `512`.
- Decimal units, such as `1G` and `512M`.
- Binary units, such as `256Mi` and `1Gi`.

### Environment-Specific Readiness Policies

| Environment | Minimum Replicas | Rejects `latest` Image |
|---|---:|---|
| Development | 1 | Yes |
| Staging | 1 | Yes |
| Production | 2 | Yes |

The application reports readiness findings when a deployment violates its environment-specific policies.

## Exit Codes

| Exit Code | Meaning |
|---|---|
| `0` | Deployment is READY |
| `1` | Deployment is NOT_READY or configuration error |
| `2` | CLI argument parsing error |

These exit codes allow the application to be integrated into shell scripts and CI/CD pipelines.

## Development

Install development dependencies:

```powershell
python -m pip install -e ".[dev]"
```

Run the test suite:

```powershell
python -m pytest -v
```

Run Ruff lint checks:

```powershell
python -m ruff check .
```

Check code formatting:

```powershell
python -m ruff format --check .
```

## Project Structure

```text
deployment-readiness-checker/
|
+-- src/
|   +-- deployment_readiness_checker/
|       +-- __init__.py
|       +-- cli.py
|       +-- config_loader.py
|       +-- models.py
|       +-- policies.py
|       +-- readiness.py
|       +-- reporting.py
|
+-- tests/
|   +-- test_cli.py
|   +-- test_config_loader.py
|   +-- test_models.py
|   +-- test_policies.py
|   +-- test_readiness.py
|   +-- test_reporting.py
|
+-- .gitignore
+-- pyproject.toml
```

## Technology Stack

- Python
- pytest
- Ruff
- Git

## Project Goal

This project is a practical exercise in Python application development, automated testing, Git workflows, and Trunk-Based Development.

It demonstrates how deployment configuration validation and readiness checks can be implemented as a reusable CLI application suitable for automation workflows.
