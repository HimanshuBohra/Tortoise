from django.urls import re_path as url
from TortoiseAPI import views



urlpatterns = [
    url(r'^plan$',views.planApi),
    url(r'^promotion$',views.promotionApi),
    url(r'^customergoals$',views.customerGoalsApi),
]