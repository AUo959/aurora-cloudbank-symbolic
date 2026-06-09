"""Runtime guard: reject BUILD_PHASE_PLACEHOLDER_* secrets outside build phase."""

import os

_PLACEHOLDER_PREFIX = "BUILD_PHASE_PLACEHOLDER_"
_GUARDED_VARS = (
    "CSRF_SECRET_KEY",
    "AURORA_SECRET_KEY",
    "WS_AUTH_SECRET",
    "AES_KEY_256_HEX",
)


def assert_no_placeholder_secrets() -> None:
    """Raise RuntimeError if any guarded secret holds a build-phase placeholder.

    No-op when AURORA_BUILD_PHASE=1 (Vercel import / catalog-generation phase).
    """
    if os.getenv("AURORA_BUILD_PHASE", "").strip() == "1":
        return

    offenders = [
        var
        for var in _GUARDED_VARS
        if os.getenv(var, "").startswith(_PLACEHOLDER_PREFIX)
    ]

    if offenders:
        raise RuntimeError(
            f"Runtime started with build-phase placeholder secret(s): "
            f"{', '.join(offenders)}. "
            "Configure real values in Vercel environment settings before deployment. "
            "Set AURORA_BUILD_PHASE=1 only during Vercel build/import."
        )
