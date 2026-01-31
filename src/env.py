"""Environment variable handler."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
import os

# =============================================================================
# CORE CLASSES
# =============================================================================
class EnvHandler:
    """Typed environment variable retriever."""

    @staticmethod
    def get_str(key: str, default: str | None = None) -> str:
        """Get string value from env.

        Args:
            key: Env variable name.
            default: Default value if not found.

        Returns:
            Value as string.

        Raises:
            ValueError: If key not found and no default provided.
        """
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Environment variable '{key}' is required.")
        return value

    @staticmethod
    def get_bool(key: str, default: str = "false") -> bool:
        """Get boolean value from env.

        Args:
            key: Env variable name.
            default: Default string value ("true"/"false").

        Returns:
            True if value is "true" (case-insensitive), else False.
        """
        val = os.getenv(key, default).lower()
        return val == "true"

    @staticmethod
    def get_int(key: str, default: int | None = None) -> int:
        """Get integer value from env.

        Args:
            key: Env variable name.
            default: Default integer value.

        Returns:
            Value as int.

        Raises:
            ValueError: If conversion fails or key missing.
        """
        val_str = os.getenv(key)
        if val_str is None:
            if default is not None:
                return default
            raise ValueError(f"Environment variable '{key}' is required.")
        try:
            return int(val_str)
        except ValueError:
            raise ValueError(f"Environment variable '{key}' must be an integer.")
