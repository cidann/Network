from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='user')
    content=models.TextField()
    time=models.DateTimeField(auto_now_add=True)
    like=models.IntegerField(default=0)
    def __str__(self):
        return f'Post by {self.user.username}'

