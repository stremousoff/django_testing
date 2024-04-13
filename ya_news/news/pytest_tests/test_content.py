import pytest

from news.forms import CommentForm
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_per_main_page(news_for_main_page, client, url_news_home):
    """Проверить, что на главной странице выводится десять новостей."""
    response = client.get(url_news_home)
    object_list = response.context['object_list']
    assert len(object_list) == NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_sort_news_for_main_page(news_for_main_page, client, url_news_home):
    """Новости должны быть отсортированы от самой свежей к самой старой."""
    response = client.get(url_news_home)
    object_list = response.context['object_list']
    all_dates = [object_news.date for object_news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comment_order(
        client, author, news, comments_for_same_news, url_news_detail
):
    """Комментарии должны быть отсортированы в хронологическом порядке."""
    response = client.get(url_news_detail)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_dates = [object_comment.created for object_comment in all_comments]
    sorted_dates = sorted(all_dates)
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_status, form',
    (
        (pytest.lazy_fixture('client'), False, None),
        (pytest.lazy_fixture('author_client'), True, CommentForm),
    ),
)
def test_form_unavailable_for_anonymous_users(
        parametrized_client, expected_status, form, url_news_detail
):
    """Проверка (не)доступности формы для разных пользователей."""
    response = parametrized_client.get(url_news_detail)
    assert ('form' in response.context) == expected_status
    if form:
        assert isinstance(response.context['form'], form)
