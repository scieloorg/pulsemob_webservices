from django.conf.urls import url
import views

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # region Mobile webservices.
    url(r'^mobile/login', views.login_mobile),
    url(r'^mobile/home', views.home),

    url(r'^mobile/solr/version', views.solr_version),

    url(r'^mobile/magazine/search', views.search),

    url(r'^mobile/favorite/create', views.create_favorite),
    url(r'^mobile/favorite/read', views.read_favorite),
    url(r'^mobile/favorite/delete', views.delete_favorite),

    url(r'^mobile/category/magazines/list', views.list_category_magazines),

    url(r'^mobile/feed/create', views.create_feed),
    url(r'^mobile/feed/update', views.update_feed),
    url(r'^mobile/feed/delete', views.delete_feed),

    url(r'^mobile/user/language', views.user_change_language),
    url(r'^mobile/user/font', views.user_change_font_size),
    # endregion

    # region Backoffice webservices.
    url(r'^backoffice/users/login', views.bo_administrator_login),
    url(r'^backoffice/users/me', views.bo_administrator_me),
    url(r'^backoffice/users/change-password', views.bo_administrator_change_password),
    url(r'^backoffice/users/set-password', views.bo_administrator_set_password),
    url(r'^backoffice/users/recover-password', views.bo_administrator_recover_password),
    url(r'^backoffice/users/validate-recovery-token', views.bo_administrator_validate_recovery_token),

    url(r'^backoffice/users/save', views.bo_administrator_save),
    url(r'^backoffice/users/list', views.bo_administrator_list),
    url(r'^backoffice/users/delete/(?P<pk>[0-9]+)', views.bo_administrator_delete),

    url(r'^backoffice/magazines/list', views.bo_magazine_list),
    url(r'^backoffice/categories/list', views.bo_category_list),

    url(r'^backoffice/articles/upload-cover', views.bo_cover_save),
    url(r'^backoffice/articles/delete-cover/(?P<article_id>[0-9a-zA-Z-]+)', views.bo_cover_delete),

    url(r'^backoffice/articles/get-cover/(?P<article_id>[0-9a-zA-Z-]+)', views.bo_cover_get),
    # endregion
]