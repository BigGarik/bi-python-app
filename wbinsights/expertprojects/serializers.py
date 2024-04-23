from rest_framework import serializers
from web.models import CustomUser
from .models import UserProject, Category, UserProjectCustomer


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


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name')


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
        fields = ('name', 'author', 'members', 'category', 'key_results', 'customer', 'year', 'goals')
