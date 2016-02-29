from rest_framework import serializers
from models import Administrator, Magazine, Category, CoverArticle
import logging

# Get logger.
logger = logging.getLogger(__name__)


class MagazineSerializer (serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=False, required=False)

    class Meta:
        model = Magazine
        fields = ['id', 'magazine_name',]


class AdministratorSerializer (serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=False, required=False)
    magazines = MagazineSerializer(many=True, required=False)

    def update(self, instance, validated_data):
        instance.profile = validated_data['profile']
        instance.name = validated_data['name']
        instance.email = validated_data['email']
        instance.active = True

        instance.save()

        magazines = validated_data.get('magazines', [])
        for index, element in enumerate(magazines):
            try:
                magazine = Magazine.objects.get(id=element.get('id', 0))
                instance.magazines.add(magazine)
            except Magazine.DoesNotExist:
                logger.warn('Magazine related to user was not found. This value will be ignored.')

        instance.save()

        return instance

    def create(self, validated_data):
        admin = Administrator()

        admin.profile = validated_data.get('profile', None)
        admin.name = validated_data.get('name', None)
        admin.email = validated_data.get('email', None)

        admin.save()

        magazines = validated_data.get('magazines', [])
        for index, element in enumerate(magazines):
            try:
                magazine = Magazine.objects.get(id=element.get('id', 0))
                admin.magazines.add(magazine)
            except Magazine.DoesNotExist:
                logger.warn('Magazine related to user was not found. This value will be ignored.')

        return admin

    class Meta:
        model = Administrator
        fields = ['id', 'profile', 'name', 'email', 'active', 'magazines',]


class CategorySerializer (serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=False, required=False)

    class Meta:
        model = Category
        fields = ['id', 'category_name_en', 'category_name_pt', 'category_name_es',]


class CoverArticleSerializer (serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=False, required=False)
    administrator = AdministratorSerializer(many=False, required=False)


    class Meta:
        model = CoverArticle
        fields = ['id', 'upload_time', 'image', 'article_id', 'administrator']
