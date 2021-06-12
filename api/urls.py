from django.urls import include, path
from rest_framework_nested import routers

from .views import CommentViewSet, PostViewSet, RatingViewSet, TopicViewSet

# create a new router for automatic endpoint creation
router = routers.DefaultRouter()
# register topics by passing in the url prefix and the viewset class
router.register('topics', TopicViewSet)

# create nested routers with the 'drf-nested-routers' library:
# https://github.com/alanjds/drf-nested-routers#infinite-depth-nesting

# posts are nested within topics
topics_router = routers.NestedSimpleRouter(router, 'topics', lookup='topic')
topics_router.register('posts', PostViewSet, basename='topic-posts')

# ratings are nested within posts
rating_router = routers.NestedSimpleRouter(topics_router, 'posts', lookup='post')
rating_router.register('ratings', RatingViewSet, basename='post-ratings')

# comments are nested within posts
comment_router = routers.NestedSimpleRouter(topics_router, 'posts', lookup='post')
comment_router.register('comments', CommentViewSet, basename='post-comments')

# include the urls from the routers
urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/', include(topics_router.urls)),
    path('v1/', include(rating_router.urls)),
    path('v1/', include(comment_router.urls)),
]
