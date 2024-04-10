import pytest

from django.urls import reverse

from yanews import settings


def test_news_per_main_page(news_for_main_page, client):
    """Проверить, что на главной странице выводится десять новостей."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


def test_sort_news_for_main_page(news_for_main_page, client):
    """Проверить, что новости отсортированы от самой свежей к самой старой
    на главной странице.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [object_news.date for object_news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comment_order(client, author, news, comments_for_same_news):
    """Комментарии на странице отдельной новости отсортированы
    в хронологическом порядке: старые в начале списка, новые — в конце.
    """
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_dates = [object_comment.created for object_comment in all_comments]
    sorted_dates = sorted(all_dates)
    assert all_dates == sorted_dates


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
            (pytest.lazy_fixture('client'), False),
            (pytest.lazy_fixture('author_client'), True)
    ),
)
def test_form_unavailable_for_anonymous_users(
        parametrized_client, expected_status, news):
    """Проверить, что анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости, а авторизованному доступна.
    """
    url = reverse('news:detail', args=(news.id,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) == expected_status
