from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser

from rest_framework.authtoken.models import Token

import uuid

# Create your models here.
class User(AbstractUser):
    userid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,)
    username = models.CharField(null=False, max_length=64, unique=True)
    avatar = models.ImageField(null=True)
    bio = models.TextField(null=True, max_length=256)
    createdAt = models.DateTimeField(auto_now_add=True)
    editedAt = models.DateTimeField(auto_now=True)
    lastactive = models.DateTimeField(null=True)
    

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(user=instance)
    
class Post(models.Model):
    postid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    caption = models.TextField(null=True)
    image = models.ImageField(upload_to='images', null=True)
    likes_no = models.BigIntegerField(default=0)
    createdAt = models.DateTimeField(auto_now_add=True)
    editedAt = models.DateTimeField(auto_now=True)
    
class Like(models.Model):
    likeid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    postid = models.ForeignKey(Post, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    

    
class Follow(models.Model):
    followid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    follower = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower} follows {self.following}"
    

