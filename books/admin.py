from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'rating', 'added_date']
    list_filter = ['status', 'rating', 'added_date']
    search_fields = ['title', 'author']
    date_hierarchy = 'added_date'
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('title', 'author', 'status', 'description')
        }),
        ('Detaylar', {
            'fields': ('page_count', 'isbn', 'cover_image')
        }),
        ('Tarihler', {
            'fields': ('start_date', 'finish_date')
        }),
        ('Değerlendirme', {
            'fields': ('rating', 'review')
        }),
    )