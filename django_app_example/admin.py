"""Django admin configuration."""

from django.contrib import admin

from .models import Example


@admin.register(Example)
class ExampleAdmin(admin.ModelAdmin):
    """Admin for Example model."""

    list_display = ["name", "message", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "message"]

