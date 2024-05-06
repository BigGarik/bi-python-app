import logging

from rest_framework import serializers
from web.models import CustomUser, Profile
from .models import UserProject, Category, UserProjectCustomer


logger = logging.getLogger(__name__)


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    Сериализатор, который позволяет динамически изменять поля, которые должны быть сериализованы.
    """

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Удаляем любые поля, которые не указаны в параметре 'fields'
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class CustomUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('avatar')

class CustomUserSerializer(serializers.ModelSerializer):
    profile_photo = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'email', 'profile_photo')

    def get_profile_photo(self, customuser):
        request = self.context.get('request')
        photo_url = customuser.profile.avatar.url
        #return request.build_absolute_uri(photo_url)
        return customuser.profile.avatar.url


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name',)


class UserProjectCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProjectCustomer
        fields = ('name',)


class UserProjectSerializer(DynamicFieldsModelSerializer):
    author = CustomUserSerializer()
    members = CustomUserSerializer(many=True, read_only=True)
    category = CategorySerializer(many=True, read_only=True)
    customer = UserProjectCustomerSerializer()

    class Meta:
        model = UserProject
        fields = ('name', 'author', 'members', 'category', 'key_results', 'customer', 'year', 'goals', 'slug', 'files')
