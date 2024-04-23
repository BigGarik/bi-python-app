from rest_framework import serializers

from web.models import CustomUser
from .models import UserProject


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    Сериализатор, который позволяет динамически изменять поля, которые должны быть сериализованы.
    """

    def __init__(self, *args, **kwargs):
        # Не передавайте поле 'fields' в super конструктор
        fields = kwargs.pop('fields', None)
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Удаляем любые поля, которые не указаны в параметре 'fields'
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name')


class MembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name')


class CategorySerializer(serializers.ModelSerializer):
    pass


class CustomerSerializer(serializers.ModelSerializer):
    pass


class UserProjectSerializer(DynamicFieldsModelSerializer):
    author = AuthorSerializer()
    members = AuthorSerializer()

    class Meta:
        model = UserProject
        fields = '__all__'
