from django.shortcuts import render, get_object_or_404, redirect
from .models import News, Comment
from .forms import NewsForm, CommentForm


def news_list(request):
    news = News.objects.all().order_by('-created_at')
    return render(request, 'news/news_list.html', {'news': news})


def news_detail(request, news_id):
    news_item = get_object_or_404(News, id=news_id)
    comments = news_item.comments.all()

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.news = news_item
            comment.save()
            return redirect('news_detail', news_id=news_id)
    else:
        form = CommentForm()

    return render(request, 'news/news_detail.html', {'news_item': news_item, 'comments': comments, 'form': form})


def add_news(request):
    if request.method == "POST":
        form = NewsForm(request.POST)
        if form.is_valid():
            news = form.save()
            return redirect('news_detail', news_id=news.id)
    else:
        form = NewsForm()

    return render(request, 'news/add_news.html', {'form': form})
