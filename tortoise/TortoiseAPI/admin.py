import imp
from pydoc import plain
from django.contrib import admin
from .models import Plan,Promotions,CustomerGoals



# Register your models here.
admin.site.register(Plan)
admin.site.register(Promotions)
admin.site.register(CustomerGoals)