from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    ('name', 'id_news'),
    (
            ('news:home', None),
            ('users:login', None),
            ('users:signup', None),
            ('users:logout', None),
            ('news:detail', pytest.lazy_fixture('news_id')),
    )
)
def test_home_availability_for_anonymous_user(client, name, id_news):
    """Проверка рутинга анонимного пользователя.

    Анонимный пользователь может перейти:
    - на главную страницу;
    - на страницу входа;
    - на страницу регистрации;
    - на страницу выхода;
    - на страницу новости.
    """
    url = reverse(name, args=((id_news,) if id_news else None))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('client'), None),
    ),
)
@pytest.mark.parametrize(
    ('name', 'id_comment'),
    (
        ('news:delete', pytest.lazy_fixture('comment_id')),
        ('news:edit', pytest.lazy_fixture('comment_id')),
    )
)
def test_pages_availability_for_different_users(parametrized_client, name,
                                                id_comment, expected_status):
    """Проверка рутинга редактирования и удаления комментариев.

    Комментарии могут редактироваться или удаляться только автором. При
    попытке перейти на страницу редактирования или удаления комментария
    анонимный пользователь перенаправляется на страницу авторизации.

    """
    url = reverse(name, args=(id_comment,))
    response = parametrized_client.get(url)
    if expected_status:
        assert response.status_code == expected_status
    else:
        auth_url = reverse('users:login')
        expected_url = f'{auth_url}?next={url}'
        assertRedirects(response, expected_url)
