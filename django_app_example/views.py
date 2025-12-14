"""Views for django_app_example."""

from django.http import HttpResponse
from django.shortcuts import render


def hello_world(request):
    """Hello World view."""
    return HttpResponse("Hello World!")


def hello_template(request):
    """Hello World view with template."""
    return render(request, "django_app_example/hello.html", {"message": "Hello World!"})

