from django.conf import settings
from django.db import models


class Topic(models.Model):
    """
    The database model representing the topics of a post.

    """
    
    # types of topic objects that can be created
    TYPES = [
        ('politics', 'Politics'),
        ('health', 'Health'),
        ('sport', 'Sport'),
        ('tech', 'Tech'),
    ]

    title = models.CharField(primary_key=True, max_length=8, choices=TYPES)

    def __str__(self):
        return self.title


class Post(models.Model):
    """
    The database model representing posts.
    """
    

    title = models.CharField(max_length=150)
    message = models.CharField(max_length=1000)

    topics = models.ManyToManyField(Topic)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    date_created = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()

    def __str__(self):
        return self.title


class Rating(models.Model):
    """
    The database model representing ratings for posts.
    """
    
    class Rate(models.TextChoices):
        """
        Enum representing the values that may be used to rate a post
        """

        LIKE = ('LIKE', 'Like')
        DISLIKE = ('DISLIKE', 'Dislike')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    rating = models.CharField(max_length=7, choices=Rate.choices, default=Rate.LIKE)
    time_left_until_post_expiry = models.DurationField()

    def __str__(self):
        return self.rating


class Comment(models.Model):
    """
    The database model representing comments for posts.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    
    comment = models.CharField(max_length=256)
    time_left_until_post_expiry = models.DurationField()

    def __str__(self):
        return self.comment
