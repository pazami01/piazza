from rest_framework import serializers
from django.contrib.auth.models import User

# THE ENTIRE CODE IN THIS FILE IS FROM CCC LAB4 #

class CreateUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """

    def create(self, validated_data):
        """
        Creates a new User object with the validated data.
        """
        
        user = User.objects.create_user(**validated_data)

        return user
    
    class Meta:
        model = User
        fields = ('id', 'first_name', 'username', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }
    

