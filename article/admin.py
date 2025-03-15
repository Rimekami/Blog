from django.contrib import admin
from .models import Article

@admin.register(Article)

class ArticleAdmin(admin.ModelAdmin):  
    class Meta:
        model = Article
        

    list_display = ['title', 'author', 'date']
    list_filter = ['date']



# Register your models here.
