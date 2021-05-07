from rest_framework import serializers
from .models import *
from django_countries.serializer_fields import CountryField as CountryFieldSerializer
# from django_countries.serializers import CountryFieldMixin
from django_celery_results.models import TaskResult
from .full_text_search_model import FullTextSearchModel


class UserSerializer(serializers.ModelSerializer):

    @staticmethod
    def serialize(data, is_list=False):
        return UserSerializer(data, many=is_list).data

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']


class UsernameSerializer(serializers.ModelSerializer):

    @staticmethod
    def serialize(data, is_list=False):
        return UsernameSerializer(data, many=is_list).data

    class Meta:
        model = get_user_model()
        fields = ['username']


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
        exclude = ['orb_descriptor']


class SingleImageRequestSerializer(serializers.ModelSerializer):
    country = CountryFieldSerializer(country_dict=True)

    class Meta:
        model = Image
        fields = ['img', 'country', 'description', 'categories']


class ImageMetaSerializer(serializers.ModelSerializer):
    country = CountryFieldSerializer(country_dict=True)

    class Meta:
        model = Image
        fields = ['country', 'description', 'categories']


class ImageSerializerWithAllDetails(serializers.ModelSerializer):
    country = CountryFieldSerializer(country_dict=True)
    categories = ImageCategorySerializer(many=True)
    owner = UsernameSerializer()

    @staticmethod
    def serialize(data, is_list=False):
        return ImageSerializerWithAllDetails(data, many=is_list).data

    class Meta:
        model = Image
        exclude = ['orb_descriptor']


class MultiImageRequestSerializer(serializers.Serializer):
    images = serializers.ListField(child=serializers.FileField())
    meta = serializers.ListField(child=ImageMetaSerializer(),
                                 help_text='size of this list must be either exactly 1 or exactly the number of images')

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class FullTextSearchModelSerializer(serializers.Serializer):
    phrase = serializers.CharField(allow_blank=True, allow_null=True, default=None)
    keywords = serializers.ListField(child=serializers.CharField(), allow_empty=True, allow_null=True, default=None)
    country_name_or_code = serializers.CharField(allow_null=True, allow_blank=True, default=None)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):

        def get_safe_value_from_dict(data, key):
            if key in data:
                return data[key]
            else:
                return None

        phrase = get_safe_value_from_dict(validated_data, 'phrase')
        country = get_safe_value_from_dict(validated_data, 'country_name_or_code')
        keywords = get_safe_value_from_dict(validated_data, 'keywords')
        return FullTextSearchModel(phrase=phrase, country_name_or_code=country, keywords=keywords)
