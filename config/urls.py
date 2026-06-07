from django.urls import path

from sentinel import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/config", views.config, name="config"),
    path("api/inject", views.inject, name="inject"),
    path("api/reset", views.reset, name="reset"),
]
