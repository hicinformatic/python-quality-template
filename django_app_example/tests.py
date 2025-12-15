from django.test import TestCase
from django.urls import reverse

from .models import Example


class ExampleModelTestCase(TestCase):
    """Test case for Example model."""

    def test_create_example(self):
        """Test creating an example."""
        example = Example.objects.create(name="Test", message="Hello World")
        assert example.name == "Test"
        assert example.message == "Hello World"
        assert str(example) == "Test: Hello World"


class HelloWorldViewTestCase(TestCase):
    """Test case for hello_world view."""

    def test_hello_world(self):
        """Test hello_world view."""
        url = reverse("django_app_example:hello")
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.content == b"Hello World!"

