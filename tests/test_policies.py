from dataclasses import FrozenInstanceError

import pytest

from deployment_readiness_checker.policies import (
    ENVIRONMENT_POLICIES,
    EnvironmentPolicy,
)


def test_environment_policies_cover_all_environments():
    assert set(ENVIRONMENT_POLICIES) == {
        "development",
        "staging",
        "production",
    }


@pytest.mark.parametrize(
    ("environment", "minimum_replicas"),
    [
        ("development", 1),
        ("staging", 1),
        ("production", 2),
    ],
)
def test_environment_policies_define_minimum_replicas(environment, minimum_replicas):
    policy = ENVIRONMENT_POLICIES[environment]

    assert policy.minimum_replicas == minimum_replicas


def test_environment_policies_reject_latest_images():
    assert all(policy.reject_latest_image for policy in ENVIRONMENT_POLICIES.values())


def test_environment_policy_is_immutable():
    policy = EnvironmentPolicy(minimum_replicas=2)

    with pytest.raises(FrozenInstanceError):
        policy.minimum_replicas = 3
