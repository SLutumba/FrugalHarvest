from django.contrib import admin
from .models import Category, Customer, Product, Order, Profile
from django.contrib.auth.models import User

admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Profile)

#Mix profile and User info

class ProfileInline(admin.StackedInline):
    model = Profile

#Extend User model
class UserAdmin(admin.ModelAdmin):
    model = User
    field = ['username', 'first_name', 'last_name', 'email']
    inlines = [ProfileInline]

#Unregister old way
admin.site.unregister(User)

#register new way
admin.site.register(User, UserAdmin)