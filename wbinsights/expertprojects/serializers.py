import logging

from hitcount.models import HitCount
from rest_framework import serializers
from web.models import CustomUser, Profile
from .models import UserProject, Category, UserProjectCustomer


logger = logging.getLogger("django-info")


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
    hit_count = serializers.SerializerMethodField()

    class Meta:
        model = UserProject
        fields = '__all__'

    def get_hit_count(self, obj):
        hit_count = HitCount.objects.get_for_object(obj)
        return hit_count.hits if hit_count else 0
