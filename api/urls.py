from django.urls import path
from . import views

urlpatterns = [
    path("translate/", views.translate_text, name="translate"),
    path("summarize/", views.summarize_text, name="summarize"),


]
