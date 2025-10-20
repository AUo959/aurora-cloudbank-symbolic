"""Compatibility shim for legacy Opal2 API imports."""
import modules.opal2.api.opal2_api as _opal2_api

# Re-export all public symbols from modules.opal2.api.opal2_api
__all__ = _opal2_api.__all__

# Inject all public symbols into the current module's namespace
for name in __all__:
    globals()[name] = getattr(_opal2_api, name)
