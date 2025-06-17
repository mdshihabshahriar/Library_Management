from django.contrib import admin
from .models import Book,Transaction,Category

admin.site.register(Book)
admin.site.register(Transaction)
admin.site.register(Category)