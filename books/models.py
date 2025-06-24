# books/models.py
from django.db import models
from django.urls import reverse

class Book(models.Model):
    STATUS_CHOICES = [
        ('to_read', 'Okunacak'),
        ('reading', 'Okunuyor'),
        ('read', 'Okundu'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Kitap Adı")
    author = models.CharField(max_length=100, verbose_name="Yazar")
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='to_read',
        verbose_name="Durum"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    page_count = models.PositiveIntegerField(blank=True, null=True, verbose_name="Sayfa Sayısı")
    isbn = models.CharField(max_length=13, blank=True, null=True, verbose_name="ISBN")
    cover_image = models.URLField(blank=True, null=True, verbose_name="Kapak Resmi URL")
    
    # Tarih alanları
    added_date = models.DateTimeField(auto_now_add=True, verbose_name="Eklenme Tarihi")
    start_date = models.DateField(blank=True, null=True, verbose_name="Okumaya Başlama Tarihi")
    finish_date = models.DateField(blank=True, null=True, verbose_name="Bitirme Tarihi")
    
    # Değerlendirme
    rating = models.PositiveSmallIntegerField(
        blank=True, 
        null=True, 
        choices=[(i, i) for i in range(1, 6)],
        verbose_name="Puan (1-5)"
    )
    review = models.TextField(blank=True, null=True, verbose_name="Değerlendirme")
    
    class Meta:
        verbose_name = "Kitap"
        verbose_name_plural = "Kitaplar"
        ordering = ['-added_date']
    
    def __str__(self):
        return f"{self.title} - {self.author}"
    
    def get_absolute_url(self):
        return reverse('books:detail', kwargs={'pk': self.pk})
    
    def get_status_display_with_color(self):
        status_colors = {
            'to_read': 'secondary',
            'reading': 'warning', 
            'read': 'success'
        }
        return {
            'status': self.get_status_display(),
            'color': status_colors.get(self.status, 'secondary')
        }
