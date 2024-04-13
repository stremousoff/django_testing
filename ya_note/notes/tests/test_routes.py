from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


class TestRoutes(TestCase):
    """Тестирование роуминга приложения 'Заметки'."""

    TITLE = 'заголовок_заметки'
    TEXT = 'текст_заметки'
    SLUG = 'slug'
    AUTHOR = 'автор_заметки'
    USER = 'зарегистрированный_пользователь'

    LOGIN_URL = reverse('users:login')

    # URL-адреса
    urls = (
        reverse('notes:home'),
        LOGIN_URL,
        reverse('users:logout'),
        reverse('users:signup'),
        reverse('notes:list'),
        reverse('notes:add'),
        reverse('notes:success'),
        reverse('notes:detail', args=(SLUG,)),
        reverse('notes:edit', args=(SLUG,)),
        reverse('notes:delete', args=(SLUG,))
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

    def test_page_for_author(self):
        """Проверка доступности страниц для автора заметки."""
        for url in self.urls:
            with self.subTest(url=url):
                self.client.force_login(self.author)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_for_user(self):
        """Проверка доступности страницы для пользователя."""
        for url in self.urls:
            with self.subTest(url=url):
                self.client.force_login(self.user)
                if self.SLUG in url:
                    response = self.client.get(url)
                    self.assertEqual(response.status_code,
                                     HTTPStatus.NOT_FOUND)
                else:
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_for_anonymous(self):
        """Проверка доступности страницы для анонима."""
        for url in self.urls:
            with self.subTest(url=url):
                self.client.force_login(self.user)
                if self.AUTHOR in url:
                    redirect_url = f'{self.LOGIN_URL}?next={url}'
                    response = self.client.get(url)
                    self.assertRedirects(
                        response,
                        redirect_url,
                        msg_prefix=f'Проверьте что страница {url} не доступна '
                                   f'для не зарегистрированного пользователя'
                                   f' и осуществляется редирект на '
                                   f'{redirect_url}'
                    )
                elif self.SLUG in url:
                    response = self.client.get(url)
                    self.assertEqual(response.status_code,
                                     HTTPStatus.NOT_FOUND)
                else:
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
