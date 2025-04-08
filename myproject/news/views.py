from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from .serializers import NewsSerializer
from .models import News
from django.shortcuts import get_object_or_404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import News
from .forms import NewsForm, CommentForm, SignUpForm
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group
from django.http import HttpResponseForbidden
from django.contrib.auth.mixins import PermissionRequiredMixin



def news_list(request):
    news_items = News.objects.all().order_by('-created_at')
    return render(request, 'news/news_list.html', {'news_items': news_items})

def news_detail(request, news_id):
    if request.user.is_authenticated and request.user.has_perm('news.add_comment'):
        news_item = get_object_or_404(News, id=news_id)
        comments = news_item.comments.all().order_by('-created_at')

    if request.user.is_authenticated:
        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.news = news_item
                comment.created_at = timezone.now()
                comment.author = request.user
                comment.save()
                return redirect('news_detail', news_id=news_id)
        else:
            comment_form = CommentForm()

    return render(request, 'news/news_detail.html', {
        'news_item': news_item,
        'comments': comments,
        'comment_form': comment_form,
    })
@permission_required('news.add_news', raise_exception=True)
@login_required
def news_create(request):
    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            news.created_at = timezone.now()
            news.author = request.user
            news.save()
            return redirect('news_detail', news_id=news.id)
    else:
        form = NewsForm()
    return render(request, 'news/news_create.html', {'form': form})


class NewsUpdateView(View):
    permission_required = 'news.change_news'
    raise_exception = True
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


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        default_group, created = Group.objects.get_or_create(name='default')
        self.object.groups.add(default_group)
        return response

@permission_required('news.delete_news', raise_exception=True)
@login_required
def delete_news(request, news_id):
    news = get_object_or_404(News, id=news_id)
    if request.user == news.author or request.user.has_perm('news.delete_news'):
        news.delete()
        return redirect('news_list')
    else:
        return HttpResponseForbidden("Нет прав")

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user == comment.author or request.user.has_perm('news.delete_comment'):
        comment.delete()
        return redirect('news_detail', news_id=comment.news.id)
    else:
        return HttpResponseForbidden("Нет прав")


@api_view(['POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def news_create_api(request):
    serializer = NewsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(author=request.user)  # автор автоматически — текущий пользователь
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


