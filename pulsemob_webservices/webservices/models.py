__author__ = 'cadu'

from django.db import models
import os
import logging

# Get logger.
logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webservices.settings")

FONT_SIZE_OPTIONS = (
    ('S', 'Small'),
    ('M', 'Medium'),
    ('L', 'Large'),
)

LANGUAGE_OPTIONS = (
    ('ES', 'Spanish'),
    ('PT', 'Portuguese'),
    ('EN', 'English'),
)

PROFILE_OPTIONS = (
    (0, 'SciELO'),
    (1, 'Editor'),
    (2, 'Operador'),
)


class User (models.Model):
    id = models.AutoField(primary_key=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    facebook_id = models.CharField(max_length=255, null=True)
    google_id = models.CharField(max_length=255, null=True)
    language = models.CharField(max_length=2, choices=LANGUAGE_OPTIONS)
    font_size = models.CharField(max_length=1, choices=FONT_SIZE_OPTIONS)

    def to_dict(self):
        return {'id': self.id, 'create_time': str(self.create_time), 'update_time': str(self.update_time),
                'email': self.email, 'name': self.name, 'facebook_id': self.facebook_id,
                'google_id': self.google_id, 'language': self.language, 'font_size': self.font_size}

    class Meta:
        db_table = "mobile_user"


class UserFavorite(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    article_id = models.CharField(max_length=255)

    class Meta:
        db_table = "mobile_user_favorite"


class Category (models.Model):
    id = models.AutoField(primary_key=True)
    category_name_en = models.CharField(max_length=255)
    category_name_pt = models.CharField(max_length=255)
    category_name_es = models.CharField(max_length=255)

    def to_dict(self):
        return {"id": self.id, "category_name_en": self.category_name_en, "category_name_es": self.category_name_es,
                "category_name_pt": self.category_name_pt}

    class Meta:
        db_table = "common_category"


class Feed (models.Model):
    id = models.AutoField(primary_key=True)
    feed_name = models.CharField(max_length=255)
    user = models.ForeignKey(User)
    magazines = models.ManyToManyField('Magazine', blank=True)

    def to_dict(self):
        return {"id": self.id, "feed_name": self.feed_name}

    class Meta:
        db_table = "mobile_feed"


class Magazine (models.Model):
    id = models.AutoField(primary_key=True)
    magazine_name = models.CharField(max_length=255)
    magazine_issn = models.CharField(max_length=255)
    magazine_domain = models.CharField(max_length=255)
    magazine_acronym = models.CharField(max_length=255)
    magazine_abbreviated_title = models.CharField(max_length=255)
    categories = models.ManyToManyField(Category)
    feeds = models.ManyToManyField('Feed', through=Feed.magazines.through, blank=True)

    def to_dict(self):
        return {"id": self.id, "magazine_name": self.magazine_name, "magazine_issn": self.magazine_issn,
                "magazine_domain": self.magazine_domain, "magazine_acronym": self.magazine_acronym,
                "magazine_abbreviated_title": self.magazine_abbreviated_title}

    class Meta:
        db_table = "common_magazine"


class Administrator (models.Model):
    id = models.AutoField(primary_key=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    profile = models.IntegerField(max_length=1, default=0, choices=PROFILE_OPTIONS)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255, null=True)
    active = models.BooleanField(default=True)
    magazines = models.ManyToManyField('Magazine', blank=True)

    class Meta:
        db_table = "backoffice_administrator"


def generate_filename(self, filename):
    url = "uploads/covers/{dynamic_path}/magazine_{magazine_id}/{filename}".format(dynamic_path=self.upload_time.strftime("%Y/%m"), filename=filename, magazine_id=self.magazine.id)
    return url


class CoverArticle (models.Model):
    id = models.AutoField(primary_key=True)
    upload_time = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to=generate_filename)
    article_id = models.CharField(max_length=255)
    administrator = models.ForeignKey(Administrator)
    magazine = models.ForeignKey(Magazine)

    class Meta:
        db_table = "backoffice_cover_article"