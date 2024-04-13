import random
from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_user_can_create_comment(
        user_client, news, form_data, url_news_detail
):
    """Авторизированный пользователь может оставлять комментарии к новостям."""
    count_comments = Comment.objects.count()
    response = user_client.post(url_news_detail, data=form_data)
    assertRedirects(response, f'{url_news_detail}#comments')
    assert Comment.objects.count() == count_comments + 1
    assert Comment.objects.last().text == form_data['text']


@pytest.mark.django_db
def test_client_can_not_create_comment(
        client, news, form_data, url_news_detail, url_users_login
):
    """Не авторизированный пользователь не может оставлять комментарии."""
    count_comments = Comment.objects.count()
    response = client.post(url_news_detail, data=form_data)
    assertRedirects(response, f'{url_users_login}?next={url_news_detail}')
    assert Comment.objects.count() == count_comments


def test_create_comment_with_bad_words(user_client, news, url_news_detail):
    """Проверить, что нельзя писать в комментарии запрещенные слова."""
    count_comments = Comment.objects.count()
    bad_words_data = {'text': f'{random.choice(BAD_WORDS)}...'}
    response = user_client.post(url_news_detail, data=bad_words_data)
    assert Comment.objects.count() == count_comments
    assertFormError(response, form='form', field='text', errors=WARNING)


def test_author_can_edit_comment(
        author_client, comment, form_data, url_comment_edit, url_news_detail
):
    """Проверить, что автор может редактировать свои комментарии."""
    response = author_client.post(url_comment_edit, form_data)
    assertRedirects(response, f'{url_news_detail}#comments')
    assert Comment.objects.last().text == form_data['text']
    assert Comment.objects.last().author_id == comment.author_id
    assert Comment.objects.last().news_id == comment.news_id


def test_not_author_can_not_edit_comment(
        user_client, comment, form_data, url_comment_edit
):
    """Проверить, что пользователь не может редактировать чужие комментарии."""
    count_comments = Comment.objects.count()
    response = user_client.post(url_comment_edit, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == count_comments
    assert Comment.objects.last().text == comment.text
    assert Comment.objects.last().author_id == comment.author_id
    assert Comment.objects.last().news_id == comment.news_id


def test_author_can_delete_comment(
        author_client, comment, url_comment_delete, url_news_detail
):
    """Проверить, что автор может удалять свои комментарии."""
    count_comments = Comment.objects.count()
    response = author_client.post(url_comment_delete)
    assertRedirects(response, f'{url_news_detail}#comments')
    assert Comment.objects.count() == count_comments - 1


def test_not_author_can_not_delete_comment(
        user_client, comment, url_comment_delete
):
    """Проверить, что пользователь не может удалять чужие комментарии."""
    count_comments = Comment.objects.count()
    response = user_client.post(url_comment_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == count_comments
