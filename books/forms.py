# books/forms.py
from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'author', 'status', 'description', 
            'page_count', 'isbn', 'cover_image', 
            'start_date', 'finish_date', 'rating', 'review'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Kitap adını girin'
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Yazar adını girin'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Kitap hakkında kısa açıklama'
            }),
            'page_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'isbn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ISBN numarası'
            }),
            'cover_image': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Kapak resmi URL\'si'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'finish_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'rating': forms.Select(attrs={
                'class': 'form-select'
            }),
            'review': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Kitap hakkındaki düşünceleriniz'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        finish_date = cleaned_data.get('finish_date')
        status = cleaned_data.get('status')
        
        # Tarih kontrolleri
        if start_date and finish_date:
            if start_date > finish_date:
                raise forms.ValidationError(
                    "Başlama tarihi, bitirme tarihinden sonra olamaz."
                )
        
        # Durum ve tarih uyumu
        if status == 'read' and not finish_date:
            from django.utils import timezone
            cleaned_data['finish_date'] = timezone.now().date()
        
        if status == 'reading' and not start_date:
            from django.utils import timezone
            cleaned_data['start_date'] = timezone.now().date()
            
        return cleaned_data