from rest_framework import serializers
from .models import *
from django_countries.serializer_fields import CountryField as CountryFieldSerializer
# from django_countries.serializers import CountryFieldMixin
from django_celery_results.models import TaskResult


class TaskResultSerializer(serializers.ModelSerializer):
    @staticmethod
    def serialize(data, is_list=False):
        return TaskResultSerializer(data, many=is_list).data

    class Meta:
        model = TaskResult
        fields = ['task_id', 'status', 'result', 'date_created', 'date_done']


class ImageCategorySerializer(serializers.ModelSerializer):

    @staticmethod
    def serialize(data, is_list=False):
        return ImageCategorySerializer(data, many=is_list).data

    class Meta:
        model = ImageCategory
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):
    country = CountryFieldSerializer(country_dict=True)

    @staticmethod
    def serialize(data, is_list=False):
        return ImageSerializer(data, many=is_list).data

    class Meta:
        model = Image
        fields = '__all__'


class ImageSerializerIn(ImageSerializer):
    class Meta:
        model = Image
        exclude = ['owner', 'date_modified']


class ImageMetaSerializer(ImageSerializer):
    class Meta:
        model = Image
        exclude = ['img', 'owner', 'date_modified']


class UserSerializer(serializers.ModelSerializer):

    @staticmethod
    def serialize(data, is_list=False):
        return UserSerializer(data, many=is_list).data

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']


class MultiImageRequestSerializer(serializers.Serializer):
    images = serializers.ListField(child=serializers.FileField())
    meta = serializers.ListField(child=ImageMetaSerializer(),
                                 help_text='size of this list must be either exactly 1 or exactly the number of images')

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
