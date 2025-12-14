"""Models for django_app_example."""

from django.db import models


class Example(models.Model):
    """Example model."""

    name = models.CharField(max_length=100)
    message = models.TextField(default="Hello World")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options."""

        verbose_name = "Example"
        verbose_name_plural = "Examples"

    def __str__(self) -> str:
        """String representation."""
        return f"{self.name}: {self.message}"

