from django.contrib import admin

from .models import Comment, Post, Rating, Topic

# register models with django admin

admin.site.register(Post)
admin.site.register(Topic)
admin.site.register(Rating)
admin.site.register(Comment)
