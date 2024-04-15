from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf

URL_NEWS_HOME = lf('url_news_home')
URL_NEWS_DETAIL = lf('url_news_detail')
URL_USERS_SIGNUP = lf('url_users_signup')
URL_USERS_LOGIN = lf('url_users_login')
URL_USERS_LOGOUT = lf('url_users_logout')
URL_COMMENT_DELETE = lf('url_comment_delete')
URL_COMMENT_EDIT = lf('url_comment_edit')


ANONYMOUS_CLIENT = lf('client')
USER_CLIENT = lf('user_client')
AUTHOR_CLIENT = lf('author_client')


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ('url', 'parametrized_client', 'expected_status'),
    (
        (URL_NEWS_HOME, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (URL_NEWS_DETAIL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (URL_USERS_SIGNUP, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (URL_USERS_LOGIN, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (URL_USERS_LOGOUT, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (URL_COMMENT_DELETE, AUTHOR_CLIENT, HTTPStatus.OK),
        (URL_COMMENT_EDIT, AUTHOR_CLIENT, HTTPStatus.OK),
        (URL_COMMENT_DELETE, USER_CLIENT, HTTPStatus.NOT_FOUND),
        (URL_COMMENT_EDIT, USER_CLIENT, HTTPStatus.NOT_FOUND),
    )
)
def test_pages_availability_for_different_user(
        url, parametrized_client, expected_status, news):
    """Проверка рутинга для страниц для разных пользователей."""
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url', (lf('url_comment_delete'), lf('url_comment_edit'))
)
def test_redirect_for_anonymous_user(url, url_users_login, client):
    """Проверка редиректов для анонимного пользователя."""
    expected_url = f'{url_users_login}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
