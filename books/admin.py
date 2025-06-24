from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'rating', 'added_date', 'get_progress']
    list_filter = ['status', 'rating', 'added_date', 'author']
    search_fields = ['title', 'author', 'isbn']
    date_hierarchy = 'added_date'
    ordering = ['-added_date']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('title', 'author', 'status', 'description')
        }),
        ('Detaylar', {
            'fields': ('page_count', 'isbn', 'cover_image'),
            'classes': ('collapse',)
        }),
        ('Tarihler', {
            'fields': ('start_date', 'finish_date'),
            'classes': ('collapse',)
        }),
        ('Değerlendirme', {
            'fields': ('rating', 'review'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['added_date']
    
    def get_progress(self, obj):
        """Okuma durumu emoji ile göster"""
        status_icons = {
            'to_read': '📚',
            'reading': '📖', 
            'read': '✅'
        }
        return f"{status_icons.get(obj.status, '❓')} {obj.get_status_display()}"
    
    get_progress.short_description = 'Durum'
    
    actions = ['mark_as_reading', 'mark_as_read', 'mark_as_to_read']
    
    def mark_as_reading(self, request, queryset):
        updated = queryset.update(status='reading')
        self.message_user(request, f'{updated} kitap "Okunuyor" olarak işaretlendi.')
    mark_as_reading.short_description = "Seçili kitapları 'Okunuyor' olarak işaretle"
    
    def mark_as_read(self, request, queryset):
        from django.utils import timezone
        updated = 0
        for book in queryset:
            book.status = 'read'
            if not book.finish_date:
                book.finish_date = timezone.now().date()
            book.save()
            updated += 1
        self.message_user(request, f'{updated} kitap "Okundu" olarak işaretlendi.')
    mark_as_read.short_description = "Seçili kitapları 'Okundu' olarak işaretle"
    
    def mark_as_to_read(self, request, queryset):
        updated = queryset.update(status='to_read')
        self.message_user(request, f'{updated} kitap "Okunacak" olarak işaretlendi.')
    mark_as_to_read.short_description = "Seçili kitapları 'Okunacak' olarak işaretle"