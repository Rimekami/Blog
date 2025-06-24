# books/utils.py
import requests
import json
from django.conf import settings

class GoogleBooksAPI:
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"
    
    @staticmethod
    def search_books(query, max_results=10):
        """Kitap ara"""
        try:
            params = {
                'q': query,
                'maxResults': max_results,
                'langRestrict': 'tr',  # Türkçe öncelik
                'printType': 'books'
            }
            
            response = requests.get(GoogleBooksAPI.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            books = []
            
            for item in data.get('items', []):
                book_info = GoogleBooksAPI._extract_book_info(item)
                if book_info:
                    books.append(book_info)
            
            return books
            
        except Exception as e:
            print(f"Google Books API Hatası: {e}")
            return []
    
    @staticmethod
    def get_book_by_isbn(isbn):
        """ISBN ile kitap getir"""
        try:
            params = {
                'q': f'isbn:{isbn}',
                'maxResults': 1
            }
            
            response = requests.get(GoogleBooksAPI.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            items = data.get('items', [])
            
            if items:
                return GoogleBooksAPI._extract_book_info(items[0])
            
            return None
            
        except Exception as e:
            print(f"ISBN arama hatası: {e}")
            return None
    
    @staticmethod
    def _extract_book_info(item):
        """API yanıtından kitap bilgilerini çıkar"""
        try:
            volume_info = item.get('volumeInfo', {})
            
            # Temel bilgiler
            title = volume_info.get('title', '')
            authors = volume_info.get('authors', [])
            author = ', '.join(authors) if authors else ''
            
            # Eğer başlık veya yazar yoksa atla
            if not title or not author:
                return None
            
            # Detay bilgiler
            description = volume_info.get('description', '')
            page_count = volume_info.get('pageCount')
            published_date = volume_info.get('publishedDate', '')
            
            # ISBN bilgileri
            isbn_10 = ''
            isbn_13 = ''
            identifiers = volume_info.get('industryIdentifiers', [])
            for identifier in identifiers:
                if identifier.get('type') == 'ISBN_10':
                    isbn_10 = identifier.get('identifier', '')
                elif identifier.get('type') == 'ISBN_13':
                    isbn_13 = identifier.get('identifier', '')
            
            # Öncelikle ISBN-13, yoksa ISBN-10 kullan
            isbn = isbn_13 or isbn_10
            
            # Kapak resmi
            images = volume_info.get('imageLinks', {})
            cover_image = ''
            
            # En yüksek kaliteli resmi seç
            if 'extraLarge' in images:
                cover_image = images['extraLarge']
            elif 'large' in images:
                cover_image = images['large']
            elif 'medium' in images:
                cover_image = images['medium']
            elif 'small' in images:
                cover_image = images['small']
            elif 'thumbnail' in images:
                cover_image = images['thumbnail']
            
            # HTTPS'e çevir
            if cover_image and cover_image.startswith('http:'):
                cover_image = cover_image.replace('http:', 'https:')
            
            # Kategoriler
            categories = volume_info.get('categories', [])
            category = ', '.join(categories) if categories else ''
            
            # Puan (Google Books'tan gelen average rating)
            average_rating = volume_info.get('averageRating')
            google_rating = None
            if average_rating:
                # Google'ın 1-5 sistemi zaten bizimkiyle uyumlu
                google_rating = min(5, max(1, round(average_rating)))
            
            return {
                'title': title,
                'author': author,
                'description': description,
                'page_count': page_count,
                'isbn': isbn,
                'cover_image': cover_image,
                'published_date': published_date,
                'category': category,
                'google_rating': google_rating,
                'google_id': item.get('id', ''),
                'preview_link': volume_info.get('previewLink', ''),
            }
            
        except Exception as e:
            print(f"Kitap bilgisi çıkarma hatası: {e}")
            return None
    
    @staticmethod
    def search_by_title_author(title, author=''):
        """Başlık ve yazar ile arama"""
        query = title
        if author:
            query += f' inauthor:{author}'
        
        return GoogleBooksAPI.search_books(query, max_results=5)


# Yardımcı fonksiyonlar
def clean_isbn(isbn):
    """ISBN'i temizle"""
    if not isbn:
        return ''
    
    # Sadece rakam ve X harfi kalsın
    clean = ''.join(c for c in isbn.upper() if c.isdigit() or c == 'X')
    return clean

def format_book_info_for_form(api_book):
    """API'den gelen bilgiyi form formatına çevir"""
    if not api_book:
        return {}
    
    return {
        'title': api_book.get('title', ''),
        'author': api_book.get('author', ''),
        'description': api_book.get('description', '')[:500],  # Açıklamayı kısalt
        'page_count': api_book.get('page_count'),
        'isbn': api_book.get('isbn', ''),
        'cover_image': api_book.get('cover_image', ''),
        'rating': api_book.get('google_rating'),  # Google puanını önerilmiş puan olarak kullan
    }