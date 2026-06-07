from django.urls import path

from sentinel import views

urlpatterns = [
    path("", views.index, name="index"),
]
