from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('url', 'parametrized_client', 'expected_status'),
    (
        (lf('url_news_home'), lf('client'), HTTPStatus.OK),
        (lf('url_news_detail'), lf('client'), HTTPStatus.OK),
        (lf('url_users_signup'), lf('client'), HTTPStatus.OK),
        (lf('url_users_login'), lf('client'), HTTPStatus.OK),
        (lf('url_users_logout'), lf('client'), HTTPStatus.OK),
        (lf('url_comment_delete'), lf('author_client'), HTTPStatus.OK),
        (lf('url_comment_edit'), lf('author_client'), HTTPStatus.OK),
        (lf('url_comment_delete'), lf('user_client'), HTTPStatus.NOT_FOUND),
        (lf('url_comment_edit'), lf('user_client'), HTTPStatus.NOT_FOUND),
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
