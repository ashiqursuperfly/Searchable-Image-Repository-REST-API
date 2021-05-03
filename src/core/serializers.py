from rest_framework import serializers
from .models import *


class ImageCategorySerializer(serializers.ModelSerializer):

    @staticmethod
    def serialize(data, is_list=False):
        return ImageCategorySerializer(data, many=is_list).data

    class Meta:
        model = ImageCategory
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):

    @staticmethod
    def serialize(data, is_list=False):
        return ImageSerializer(data, many=is_list).data

    class Meta:
        model = Image
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):

    @staticmethod
    def serialize(data, is_list=False):
        return UserSerializer(data, many=is_list).data

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']
