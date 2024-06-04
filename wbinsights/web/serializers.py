import logging

from django.db import transaction
from django.db.models import ForeignKey, ManyToManyField, OneToOneField
from rest_framework import serializers
from web.models import ExpertProfile, Category, CustomUser, Education, Document


logger = logging.getLogger(__name__)


def create_dynamic_serializer(model_class, depth=0):
    class Meta:
        model = model_class
        fields = '__all__'

    serializer_fields = {'Meta': Meta}

    for field in model_class._meta.get_fields():
        if isinstance(field, (ForeignKey, ManyToManyField)) and not field.auto_created:
            related_model = field.related_model
            if depth > 0:
                related_serializer_class = create_dynamic_serializer(related_model, depth=depth - 1)
                serializer_fields[field.name] = related_serializer_class(many=isinstance(field, ManyToManyField),
                                                                         read_only=True)

    serializer_class = type(f'{model_class.__name__}Serializer', (serializers.ModelSerializer,), serializer_fields)

    return serializer_class


def deserialize_data(model_class, data, depth=0):
    # Создаем экземпляр сериализатора для модели
    DynamicSerializer = create_dynamic_serializer(model_class, depth=depth)
    serializer = DynamicSerializer(data=data)

    # Проверяем валидность данных
    serializer.is_valid(raise_exception=True)

    # Сохраняем основной объект
    instance = serializer.save()

    # Обрабатываем связанные данные
    for field_name, related_data in data.items():
        field = model_class._meta.get_field(field_name)
        if isinstance(field, ForeignKey) and not field.auto_created:
            # Десериализуем связанный объект ForeignKey
            related_instance = deserialize_data(field.related_model, related_data, depth=depth - 1)
            setattr(instance, field_name, related_instance)
            instance.save()
        elif isinstance(field, ManyToManyField) and not field.auto_created:
            # Десериализуем связанные объекты ManyToManyField
            related_instances = [deserialize_data(field.related_model, item, depth=depth - 1) for item in related_data]
            getattr(instance, field_name).set(related_instances)
    return instance


def universal_deserializer(data, model_class):
    with transaction.atomic():
        # Десериализуем данные в объекты модели
        instance = deserialize_data(model_class, data, depth=1)
        return instance


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'


class EducationSerializer(serializers.ModelSerializer):
    degree_documents = DocumentSerializer(many=True)

    class Meta:
        model = Education
        fields = '__all__'


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ExpertProfileSerializer(serializers.ModelSerializer):
    # user = CustomUserSerializer()
    expert_categories = CategorySerializer(many=True)
    educations = EducationSerializer(many=True)
    documents = DocumentSerializer(many=True)
    # user = CustomUserSerializer()
    # documents = DocumentSerializer()
    # educations = EducationSerializer()
    # expert_categories = CategorySerializer()

    class Meta:
        model = ExpertProfile
        exclude = ['anketa', 'user']

    # def update(self, instance, validated_data):
    #     # Обновляем простые поля
    #     instance.about = validated_data.get('about', instance.about)
    #     instance.age = validated_data.get('age', instance.age)
    #     instance.hour_cost = validated_data.get('hour_cost', instance.hour_cost)
    #     instance.consulting_experience = validated_data.get('consulting_experience', instance.consulting_experience)
    #     instance.experience = validated_data.get('experience', instance.experience)
    #     instance.hh_link = validated_data.get('hh_link', instance.hh_link)
    #     instance.linkedin_link = validated_data.get('linkedin_link', instance.linkedin_link)
    #     instance.is_verified = validated_data.get('is_verified', instance.is_verified)
    #     instance.rating = validated_data.get('rating', instance.rating)
    #     instance.save()
    #
    #     # Обновляем связанные объекты ManyToMany
    #     categories_data = validated_data.get('expert_categories')
    #     if categories_data:
    #         instance.expert_categories.set([Category.objects.get_or_create(**cat_data)[0] for cat_data in categories_data])
    #
    #     # Обновляем связанные объекты OneToMany
    #     educations_data = validated_data.get('educations')
    #     if educations_data:
    #         for education_data in educations_data:
    #             education_id = education_data.get('id')
    #             if education_id:
    #                 education = Education.objects.get(id=education_id, expert_profile=instance)
    #                 education.education_type = education_data.get('education_type', education.education_type)
    #                 education.specialized_education = education_data.get('specialized_education', education.specialized_education)
    #                 education.educational_institution = education_data.get('educational_institution', education.educational_institution)
    #                 education.diploma_number = education_data.get('diploma_number', education.diploma_number)
    #                 education.save()
    #             else:
    #                 Education.objects.create(expert_profile=instance, **education_data)
    #
    #     # Обновляем связанные документы
    #     documents_data = validated_data.get('documents')
    #     if documents_data:
    #         for document_data in documents_data:
    #             document_id = document_data.get('id')
    #             if document_id:
    #                 document = Document.objects.get(id=document_id, expert_profile=instance)
    #                 document.file = document_data.get('file', document.file)
    #                 document.uploaded_at = document_data.get('uploaded_at', document.uploaded_at)
    #                 document.save()
    #             else:
    #                 Document.objects.create(expert_profile=instance, **document_data)
    #
    #     return instance
