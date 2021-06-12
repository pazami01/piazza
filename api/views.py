from django.db.models import Count
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Comment, Post, Rating, Topic
from .serializers import CommentSerializer, PostSerializer, RatingSerializer, TopicSerializer


class TopicViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing available topics.
    
    **Only the following four topics are available:**

    - politics
    - health
    - sport
    - tech
    """
    
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    # restrict what http request methods are allowed
    # taken from https://stackoverflow.com/questions/23639113/disable-a-method-in-a-viewset-django-rest-framework
    http_method_names = ['get', 'head', 'options']


class PostViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and creating Posts for particular topics.

    Must have a 'topic_pk' in the url.

    **Example format for creating a new post:**

        {
            "title": "Example Title",
            "topics": ["tech", "health"],
            "message": "Example message.",
            "expiry_date": "2021-04-18T10:30:00"
        }

    **Only the following topics are valid:**

    - politics
    - health
    - sport
    - tech

    Optionally filter the posts that are returned with query params in the url.

    **Example url with query params:**

        http://10.61.64.102:8000/api/v1/topics/tech/posts/?status=expired&interest=highest

    **Available query params:**

    - status=expired  -  to only get expired posts
    - status=live  -  to only get live posts
    - interest=highest  -  to get the post with the highest number of ratings
    - interest=lowest  -  to get the post with the lowest number of ratings

    """

    serializer_class = PostSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        """
        Returns a Post queryset that has been filtered by the 'topic_pk' in the url.

        Optionally, the returned queryset may be further filtered by query params:
            - status=expired
            - status=live
            - interest=highest
            - interest=lowest
        """

        # initial queryset filtered by topic
        queryset = Post.objects.filter(topics=self.kwargs['topic_pk'])

        # optional query params
        status = self.request.query_params.get('status')
        interest = self.request.query_params.get('interest')

        if status == 'expired':
            queryset = queryset.filter(expiry_date__lt=timezone.now())
        elif status == 'live':
            queryset = queryset.filter(expiry_date__gte=timezone.now())

        # interest level calculation solution based on code from
        # https://docs.djangoproject.com/en/3.1/topics/db/aggregation/#cheat-sheet
        if interest == 'highest':
            queryset = queryset.annotate(num_ratings=Count('rating')).order_by('-num_ratings')[:1]
        elif interest == 'lowest':
            queryset = queryset.annotate(num_ratings=Count('rating')).order_by('num_ratings')[:1]

        return queryset
        


class RatingViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and creating ratings for a particular post.

    Must have a 'post_pk' in the url.

    **Example format for creating a new rating:**

        {
            "rating": "like"
        }

    **Only the following rating values are valid:**

    - like
    - dislike
    """

    serializer_class = RatingSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        """
        Returns Rating queryset that has been filtered by the 'post_pk' in the url.
        """
        
        return Rating.objects.filter(post=self.kwargs['post_pk'])

    def create(self, request, *args, **kwargs):
        """
        Reponsible for handling POST request method for Rating.
        Passes 'post_pk' in the url to the serializer.
        """
        
        # https://www.django-rest-framework.org/api-guide/serializers/#including-extra-context
        serializer = self.get_serializer(
            data=request.data,
            context={
                'request': request,
                'post_pk': self.kwargs['post_pk']  # must explicitly pass to serializer
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CommentViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and creating comments for a particular post.

    Must have a 'post_pk' in the url.

    **Example format for creating a new comment:**

        {
            "comment": "Example comment."
        }
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        """
        Returns Comment queryset that has been filtered by the 'post_pk' in the url.
        """

        return Comment.objects.filter(post=self.kwargs['post_pk'])

    def create(self, request, *args, **kwargs):
        """
        Reponsible for handling POST request method for Comment.
        Passes 'post_pk' in the url to the serializer.
        """

        # https://www.django-rest-framework.org/api-guide/serializers/#including-extra-context
        serializer = self.get_serializer(
            data=request.data,
            context={
                'request': request,
                'post_pk': self.kwargs['post_pk']  # must explicitly pass to serializer
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

