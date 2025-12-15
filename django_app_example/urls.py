from django.urls import path

from . import views

app_name = "django_app_example"

urlpatterns = [
    path("hello/", views.hello_world, name="hello"),
    path("hello-template/", views.hello_template, name="hello-template"),
]

