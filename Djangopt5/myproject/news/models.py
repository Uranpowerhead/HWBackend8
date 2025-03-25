from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class News(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField()

    def has_comments(self):
        return self.comments.exists()

class Comment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField()


class News(models.Model):
    ...
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news')

class Comment(models.Model):
    ...
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')