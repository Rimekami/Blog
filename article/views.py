from django.shortcuts import render,HttpResponse,redirect
from .forms import ArticleForm
from django.contrib import messages


# Create your views here.

def index(request):
    return render(request, "index.html")

def about(request):
    return render(request, "about.html")

def dashboard(request):
    return render(request, "dashboard.html")

def addarticle(request):
    form = ArticleForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Makale başarıyla oluşturuldu.")
        return redirect("index")

    return render(request, "addarticle.html",{"form":form})