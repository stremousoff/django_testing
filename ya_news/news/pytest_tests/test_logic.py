import random
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_user_can_create_comment(not_author_client, news_id, form_data):
    """Проверить, что авторизированный пользователь может оставлять комментарии
     к новостям.
     """
    url = reverse('news:detail', args=(news_id,))
    response = not_author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    assert Comment.objects.last().text == form_data['text']


def test_client_can_not_create_comment(client, news_id, form_data):
    """Проверить, что не авторизированный пользователь не может оставлять
    комментарии к новостям.
    """
    url = reverse('news:detail', args=(news_id,))
    response = client.post(url, data=form_data)
    user_login_url = reverse('users:login')
    assertRedirects(response, f'{user_login_url}?next={url}')
    assert Comment.objects.count() == 0


def test_create_comment_with_bad_words(not_author_client, news_id):
    """Проверить, что нельзя писать в комментарии запрещенные слова."""
    bad_words_data = {'text': f'{random.choice(BAD_WORDS)}...'}
    url = reverse('news:detail', args=(news_id,))
    response = not_author_client.post(url, data=bad_words_data)
    assert Comment.objects.count() == 0
    assertFormError(response,  form='form', field='text', errors=WARNING)


def test_author_can_edit_comment(author_client, comment, form_data):
    """Проверить, что автор может редактировать свои комментарии."""
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, form_data)
    url_news = reverse('news:detail', args=(comment.news_id,))
    assertRedirects(response, f'{url_news}#comments')
    assert Comment.objects.last().text == form_data['text']


def test_not_author_can_not_edit_comment(not_author_client, comment,
                                         form_data):
    """Проверить, что пользователь не может редактировать чужие комментарии."""
    url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.last().text != form_data['text']


def test_author_can_delete_comment(author_client, comment):
    """Проверить, что автор может удалять свои комментарии."""
    count_comments = Comment.objects.count()
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    url_news = reverse('news:detail', args=(comment.news_id,))
    assertRedirects(response, f'{url_news}#comments')
    assert Comment.objects.count() == count_comments - 1


def test_not_author_can_not_delete_comment(not_author_client,  comment_id):
    """Проверить, что пользователь не может удалять чужие комментарии."""
    count_comments = Comment.objects.count()
    url = reverse('news:delete', args=(comment_id,))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == count_comments
