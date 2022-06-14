from django.urls import re_path as url
from TortoiseAPI import views



urlpatterns = [
    url(r'^plan$',views.planApi),
]