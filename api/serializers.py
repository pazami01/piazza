from django.utils import timezone
from rest_framework import serializers

from .models import Comment, Post, Rating, Topic


class RatingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Rating model.
    Must pass the request object and the post primary key to the constructor via context:

    context={'request': request, 'post_pk': post_pk}
    """

    # custom field for displaying the user's username
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Rating
        fields = ('id', 'username', 'post', 'rating', 'time_left_until_post_expiry')
        read_only_fields = ('post', 'time_left_until_post_expiry')
    
    def validate(self, data):
        """
        Checks that:
            - the requester is not rating their own post
            - The post being rated isn't expired
            - the requester hasn't already rated the post
        """

        user = self.context['request'].user
        post = Post.objects.get(pk=self.context['post_pk'])
        

        if user == post.owner:
            raise serializers.ValidationError('A person cannot rate their own post.')

        if post.expiry_date < timezone.now():
            raise serializers.ValidationError('Cannot rate an expired post.')
        
        if post.rating_set.filter(user=user).count():
            raise serializers.ValidationError('User has already rated this post.')

        return data
    
    def create(self, validated_data):
        """
        Sets the values for the user, post, and time_left_until_post_expiry before
        creating a Rating object with the validated data.
        """

        user = self.context['request'].user
        post = Post.objects.get(pk=self.context['post_pk'])
        time_left_until_post_expiry = post.expiry_date - timezone.now()

        rating = Rating.objects.create(
            user=user,
            post=post,
            time_left_until_post_expiry=time_left_until_post_expiry,
            **validated_data
        )
        
        return rating


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Comment model.
    Must pass the request object and the post primary key to the constructor via context:

    context={'request': request, 'post_pk': post_pk}
    """

    # custom field for displaying the user's username
    username = serializers.ReadOnlyField(source='user.username')
    

    class Meta:
        model = Comment
        fields = ('id', 'username', 'post', 'comment', 'time_left_until_post_expiry')
        read_only_fields = ('post', 'time_left_until_post_expiry')
    
    def validate(self, data):
        """
        Checks that the post being rated isn't expired.
        """

        post = Post.objects.get(pk=self.context['post_pk'])

        if post.expiry_date < timezone.now():
            raise serializers.ValidationError('Cannot rate an expired post.')

        return data
    
    def create(self, validated_data):
        """
        Sets the values for the user, post, and time_left_until_post_expiry before
        creating a Comment object with the validated data.
        """

        user = self.context['request'].user
        post = Post.objects.get(pk=self.context['post_pk'])
        time_left_until_post_expiry = post.expiry_date - timezone.now()

        comment = Comment.objects.create(
            user=user,
            post=post,
            time_left_until_post_expiry=time_left_until_post_expiry,
            **validated_data
        )
        
        return comment


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for the Post model.
    Must pass the request object to the constructor via context:

    context={'request': request}
    """

    # custom field for displaying the status of the post
    status = serializers.SerializerMethodField()
    # custom field for displaying the author's username
    author_username = serializers.ReadOnlyField(source='owner.username')
    # custom field for displaying the number of times the post has been rated with a like
    likes = serializers.SerializerMethodField()
    # custom field for displaying the number of times the post has been rated with a dislike
    dislikes = serializers.SerializerMethodField()
    # display the Comment objects associated with the Post object
    comment_set = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            'id', 'title', 'topics', 'date_created', 'message',
            'expiry_date', 'status', 'author_username', 'likes', 'dislikes', 'comment_set',
        )

    def validate_expiry_date(self, value):
        """
        Check that the expiry date of the post is not set to the past.
        """

        if value < timezone.now():
            raise serializers.ValidationError('Expiry date must not be in the past.')

        return value
    
    def create(self, validated_data):
        """
        Set the requesting user as the owner of the post before creating a Post object.
        Add each topic passed through to the list of topics on the Post object.
        """

        user = self.context['request'].user
        topics = validated_data.pop('topics')

        post = Post.objects.create(
            owner=user,
            **validated_data
        )

        for topic in topics:
            post.topics.add(topic)
        
        return post
    
    def get_status(self, obj):
        """
        Returns the value for the 'status' field.
        'Live' if the post isn't expired, 'Expired' otherwise.
        """
        
        LIVE  = 'Live'
        EXPIRED = 'Expired'

        if obj.expiry_date < timezone.now():
            return EXPIRED
        
        return LIVE
    
    def get_likes(self, obj):
        """
        Returns the value for the 'like' field.
        Calculates and returns the number of times the post has been rated with a like.
        """
        
        return obj.rating_set.filter(rating='LIKE').count()

    def get_dislikes(self, obj):
        """
        Returns the value for the dislike field.
        Calculates and returns the number of times the post has been rated with a dislike.
        """

        return obj.rating_set.filter(rating='DISLIKE').count()


class TopicSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the Topic model.
    """
    
    # a url field to the list of posts in the given topic
    posts = serializers.HyperlinkedIdentityField(
        view_name='topic-posts-list',
        lookup_url_kwarg='topic_pk'
    )

    class Meta:
        model = Topic
        fields = ('title', 'url', 'posts',)
        # specify the url to view the details of a given topic
        # based on documentation: https://www.django-rest-framework.org/api-guide/serializers/#how-hyperlinked-views-are-determined
        extra_kwargs = {
            'url': {'view_name': 'topic-detail', 'lookup_field': 'pk'},
        }

