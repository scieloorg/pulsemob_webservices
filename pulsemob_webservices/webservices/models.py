from xylose import choices

__author__ = 'vitor'

from django.db import models
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webservices.webservices.settings")

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


class UserFavorite(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    article_id = models.CharField(max_length=255)

    class Meta:
        db_table = "webservices_user_favorite"


class Feed (models.Model):
    id = models.AutoField(primary_key=True)
    feed_name_en = models.CharField(max_length=255)
    feed_name_pt = models.CharField(max_length=255)
    feed_name_es = models.CharField(max_length=255)

    def to_dict(self):
        return {"id": self.id, "feed_name_en": self.feed_name_en, "feed_name_es": self.feed_name_es,
                "feed_name_pt": self.feed_name_pt}


class Publication (models.Model):
    id = models.AutoField(primary_key=True)
    publication_name = models.CharField(max_length=255)
    feeds = models.ManyToManyField(Feed)

    def to_dict(self):
        return {"id": self.id, "publication_name": self.publication_name}


class UserFeedExclusion(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    feed = models.ForeignKey(Feed)

    def to_dict(self):
        return {'id': self.id, 'user_id': self.user.id, 'feed_id': self.feed.id}

    class Meta:
        db_table = "webservices_user_feed_exclusion"


class UserPublicationFeedExclusion(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    publication = models.ForeignKey(Publication)
    feed = models.ForeignKey(Feed)

    def to_dict(self):
        return {'id': self.id, 'user_id': self.user.id, 'publication_id': self.publication.id, 'feed_id': self.feed.id}

    class Meta:
        db_table = "webservices_user_publication_feed_exclusion"


if __name__ == '__main__':
    feed = Feed('Feed Test')
    feed.save()
