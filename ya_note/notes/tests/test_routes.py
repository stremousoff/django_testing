from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note


class TestRoutes(TestCase):
    """Тестирование роуминга приложения 'Заметки'."""

    TITLE = 'заголовок_заметки'
    TEXT = 'текст_заметки'
    SLUG = 'slug'
    AUTHOR = 'автор_заметки'
    USER = 'зарегистрированный_пользователь'

    HOME_URL = reverse('notes:home')
    LOGIN_URL = reverse('users:login')
    LOGOUT_URL = reverse('users:logout')
    SIGNUP_URL = reverse('users:signup')
    EDIT_URL = reverse('notes:edit', args=(SLUG,))
    DETAIL_URL = reverse('notes:detail', args=(SLUG,))
    DELETE_URL = reverse('notes:delete', args=(SLUG,))
    ADD_NOTE_URL = reverse('notes:add')
    LIST_URL = reverse('notes:list')
    SUCCESS_URL = reverse('notes:success')

    urls = (
        HOME_URL,
        EDIT_URL,
        DETAIL_URL,
        DELETE_URL,
        ADD_NOTE_URL,
        LIST_URL,
        SUCCESS_URL,
        LOGIN_URL,
        SIGNUP_URL,
        LOGOUT_URL,
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=cls.AUTHOR)
        cls.user = User.objects.create_user(username=cls.USER)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug=cls.SLUG,
            author=cls.author,
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.user_client = Client()
        self.user_client.force_login(self.user)

    def test_page_for_author(self):
        """Проверка доступности страниц для пользователя автора."""
        for url in self.urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_for_user(self):
        """Проверка доступности страниц для пользователя."""
        urls_not_available_for_user = (
            self.EDIT_URL, self.DELETE_URL, self.DETAIL_URL
        )
        for url in self.urls:
            response = self.user_client.get(url)
            with self.subTest(url=url):
                if url in urls_not_available_for_user:
                    self.assertEqual(response.status_code,
                                     HTTPStatus.NOT_FOUND)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_for_anonymous(self):
        """Проверка доступности страниц для анонимного пользователя."""
        urls_available_for_anonymous = (
            self.HOME_URL, self.LOGIN_URL, self.SIGNUP_URL, self.LOGOUT_URL
        )
        for url in self.urls:
            response = self.client.get(url)
            with self.subTest(url=url):
                if url in urls_available_for_anonymous:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    redirect_url = f'{self.LOGIN_URL}?next={url}'
                    self.assertRedirects(
                        response,
                        redirect_url,
                        msg_prefix=f'Проверьте что страница {url} не доступна '
                                   f'для не зарегистрированного пользователя'
                                   f' и осуществляется редирект на '
                                   f'{redirect_url}'
                    )
