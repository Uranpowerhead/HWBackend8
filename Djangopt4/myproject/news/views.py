from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import News
from .forms import NewsForm, CommentForm
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse


def news_list(request):
    news_items = News.objects.all().order_by('-created_at')
    return render(request, 'news/news_list.html', {'news_items': news_items})

def news_detail(request, news_id):
    news_item = get_object_or_404(News, id=news_id)
    comments = news_item.comments.all().order_by('-created_at')

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.news = news_item
            comment.created_at = timezone.now()
            comment.save()
            return redirect('news_detail', news_id=news_id)
    else:
        comment_form = CommentForm()

    return render(request, 'news/news_detail.html', {
        'news_item': news_item,
        'comments': comments,
        'comment_form': comment_form,
    })

def news_create(request):
    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            news.created_at = timezone.now()
            news.save()
            return redirect('news_detail', news_id=news.id)
    else:
        form = NewsForm()
    return render(request, 'news/news_create.html', {'form': form})


class NewsUpdateView(View):
    def get(self, request, news_id):
        news_item = get_object_or_404(News, id=news_id)
        form = NewsForm(instance=news_item)
        return render(request, 'news/news_edit.html', {'form': form, 'news_id': news_id})

    def post(self, request, news_id):
        news_item = get_object_or_404(News, id=news_id)
        form = NewsForm(request.POST, instance=news_item)
        if form.is_valid():
            form.save()
            return redirect('news_detail', news_id=news_id)
        return render(request, 'news/news_edit.html', {'form': form, 'news_id': news_id})