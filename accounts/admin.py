from django.contrib import admin

# Register your models here.

from .models import UserProfile,Role


admin.site.register(UserProfile) 
admin.site.register(Role) 
