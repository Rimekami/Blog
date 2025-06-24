# books/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Book
from .forms import BookForm
from .utils import GoogleBooksAPI, format_book_info_for_form
import json

class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Book.objects.all()
        status = self.request.GET.get('status')
        search = self.request.GET.get('search')
        
        if status:
            queryset = queryset.filter(status=status)
        
        if search:
            queryset = queryset.filter(
                title__icontains=search
            ) | queryset.filter(
                author__icontains=search
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('search', '')
        
        # Durum sayıları
        context['status_counts'] = {
            'all': Book.objects.count(),
            'to_read': Book.objects.filter(status='to_read').count(),
            'reading': Book.objects.filter(status='reading').count(),
            'read': Book.objects.filter(status='read').count(),
        }
        
        return context

class BookDetailView(DetailView):
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'

class BookCreateView(CreateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('books:list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Kitap başarıyla eklendi!')
        return super().form_valid(form)

class BookUpdateView(UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Kitap bilgileri güncellendi!')
        return super().form_valid(form)

class BookDeleteView(DeleteView):
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('books:list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Kitap silindi!')
        return super().delete(request, *args, **kwargs)

def update_book_status(request, pk):
    """Ajax ile kitap durumunu güncelle"""
    if request.method == 'POST':
        book = get_object_or_404(Book, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in ['to_read', 'reading', 'read']:
            book.status = new_status
            
            # Tarih güncellemeleri
            if new_status == 'reading' and not book.start_date:
                from django.utils import timezone
                book.start_date = timezone.now().date()
            elif new_status == 'read' and not book.finish_date:
                from django.utils import timezone
                book.finish_date = timezone.now().date()
            
            book.save()
            
            return JsonResponse({
                'success': True,
                'new_status': book.get_status_display(),
                'status_color': book.get_status_display_with_color()['color']
            })
    
    return JsonResponse({'success': False})

@require_http_methods(["GET"])
def search_books_api(request):
    """Google Books API'den kitap ara"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'success': False, 'error': 'Arama terimi gerekli'})
    
    if len(query) < 2:
        return JsonResponse({'success': False, 'error': 'En az 2 karakter girin'})
    
    try:
        books = GoogleBooksAPI.search_books(query, max_results=8)
        return JsonResponse({
            'success': True, 
            'books': books,
            'count': len(books)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["GET"])
def get_book_by_isbn_api(request):
    """ISBN ile kitap bilgisi getir"""
    isbn = request.GET.get('isbn', '').strip()
    
    if not isbn:
        return JsonResponse({'success': False, 'error': 'ISBN gerekli'})
    
    try:
        book_info = GoogleBooksAPI.get_book_by_isbn(isbn)
        
        if book_info:
            # Form için uygun formata çevir
            form_data = format_book_info_for_form(book_info)
            return JsonResponse({
                'success': True, 
                'book': form_data
            })
        else:
            return JsonResponse({
                'success': False, 
                'error': 'Bu ISBN ile kitap bulunamadı'
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["GET"])
def search_by_title_author_api(request):
    """Başlık ve yazar ile kitap ara"""
    title = request.GET.get('title', '').strip()
    author = request.GET.get('author', '').strip()
    
    if not title:
        return JsonResponse({'success': False, 'error': 'Kitap başlığı gerekli'})
    
    try:
        books = GoogleBooksAPI.search_by_title_author(title, author)
        
        if books:
            # İlk sonucu döndür (en alakalı)
            form_data = format_book_info_for_form(books[0])
            return JsonResponse({
                'success': True, 
                'book': form_data,
                'alternatives': books[1:3]  # Alternatif seçenekler
            })
        else:
            return JsonResponse({
                'success': False, 
                'error': 'Bu bilgilerle kitap bulunamadı'
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})