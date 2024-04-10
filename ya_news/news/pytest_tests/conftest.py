from datetime import timedelta

import pytest
from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News
from yanews import settings


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Фикстура для включения доступа к БД."""
    pass


@pytest.fixture
def news_id(news: News) -> int:
    """Фикстура для получения id новости."""
    return news.id


@pytest.fixture
def comment_id(comment: Comment) -> int:
    """Фикстура для получения id комментария."""
    return comment.id


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Фикстура для создания пользователя."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Фикстура для создания клиента с автором."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Фикстура для создания клиента с пользователя не автор."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Фикстура для создания новости."""
    news = News.objects.create(
        title='Заголовок_новости',
        text='Текст_новости',
    )
    return news


@pytest.fixture
def comment(author, news):
    """Фикстура для создания комментария к новости пользователем автор."""
    comment = Comment.objects.create(
        news_id=news.id,
        author_id=author.id,
        text='Текст_комментария',
    )
    return comment


@pytest.fixture
def news_for_main_page():
    """Фикстура для создания новостей."""
    today = timezone.now()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comments_for_same_news(author, news):
    """Фикстура для создания 2 комментариев к одной новости."""
    today = timezone.now()
    for index in range(2):
        comment_object = Comment.objects.create(
            news_id=news.id,
            author_id=author.id,
            text=f'Текст_комментария{index}',
        )
        comment_object.date = today - timedelta(days=index)
        comment_object.save()


@pytest.fixture
def form_data(author, news):
    """Фикстура для создания формы комментария."""
    return {
        'text': 'Новый_текст_комментария',
    }
