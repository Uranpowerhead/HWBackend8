from django.test import TestCase
from django.urls import reverse
from .models import News, Comment
from django.utils import timezone

class NewsModelTests(TestCase):
    def test_has_comments_true(self):
        news = News.objects.create(title='Test', content='...', created_at=timezone.now())
        Comment.objects.create(news=news, content='comment', created_at=timezone.now())
        self.assertTrue(news.has_comments())

    def test_has_comments_false(self):
        news = News.objects.create(title='Test', content='...', created_at=timezone.now())
        self.assertFalse(news.has_comments())

class NewsViewTests(TestCase):
    def setUp(self):
        self.news1 = News.objects.create(title='News 1', content='...', created_at=timezone.now())
        self.news2 = News.objects.create(title='News 2', content='...', created_at=timezone.now())

    def test_news_list_order(self):
        response = self.client.get(reverse('news_list'))
        self.assertEqual(response.status_code, 200)
        news = list(response.context['news_items'])
        self.assertGreaterEqual(news[0].created_at, news[1].created_at)

    def test_news_detail_view(self):
        response = self.client.get(reverse('news_detail', args=[self.news1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.news1.title)

    def test_news_detail_comment_order(self):
        Comment.objects.create(news=self.news1, content='Old', created_at=timezone.now())
        Comment.objects.create(news=self.news1, content='New', created_at=timezone.now())
        response = self.client.get(reverse('news_detail', args=[self.news1.id]))
        comments = list(response.context['comments'])
        self.assertGreaterEqual(comments[0].created_at, comments[1].created_at)
