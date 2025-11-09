"""Base models for Aurora SDK."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class AuroraBaseModel(BaseModel):
    """Base model for all Aurora SDK models.

    All Aurora models inherit from this class and use Pydantic v2
    for validation and serialization.
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        use_enum_values=True,
        populate_by_name=True,
        extra="allow",  # Allow extra fields from API
    )

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary.

        Returns:
            Dictionary representation of model
        """
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AuroraBaseModel":
        """Create model from dictionary.

        Args:
            data: Dictionary data

        Returns:
            Model instance
        """
        return cls.model_validate(data)
