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

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=cls.AUTHOR)
        cls.user = User.objects.create_user(
            username=cls.USER
        )
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug=cls.SLUG,
            author=cls.author,
        )

    def test_page_available_for_all_users(self):
        """Проверка доступности страниц для анонимного пользователя.

        Для анонимного пользователя доступны следующие страницы:
        - главная страница сайта;
        - страница входа в аккаунт;
        - страница выхода из аккаунта;
        - страница регистрации аккаунта.
        """
        names = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in names:
            with self.subTest():
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f'Проверьте что для любого пользователя доступна '
                    f'страница по ссылке {url}'
                )

    def test_pages_available_for_only_user(self):
        """Проверка доступности страниц только для аутентифицированного
        пользователя.

        Для аутентифицированного пользователя доступны следующие страницы:
        - страница со списком заметок;
        - страница успешного добавления заметки;
        - страница добавления новой заметки.
        """
        names = (
            'notes:list',
            'notes:add',
            'notes:success',
        )
        self.client.force_login(self.user)
        for name in names:
            with self.subTest():
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f'Проверьте что страница {url} доступна только '
                    f'автору заметки.'
                )

    def test_pages_available_for_only_author(self):
        """Проверка доступности страниц только для автора заметки.

        Для автора заметки доступны следующие страницы:
        - детальная страница заметки;
        - страница редактирования заметки;
        - страница удаления заметки.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.user, HTTPStatus.NOT_FOUND),
        )
        names = (
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name, args in names:
                with self.subTest():
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(
                        response.status_code,
                        status,
                        f'Проверьте что страница {url} доступна только '
                        f'автору заметки.'
                    )

    def test_redirects_for_anonymous(self):
        """Проверка редиректа для незарегистрированного пользователя.

        Незарегистрированным пользователям не доступны следующие страницы:
        - страница со списком заметок;
        - страница успешного добавления заметки;
        - страница добавления новой заметки;
        - детальная страница заметки;
        - страница редактирования заметки;
        - страница удаления заметки.

        Незарегистрированный пользователь должен быть перенаправлен на страницу
        входа для пользователя.
        """
        names = (
            ('notes:list', ()),
            ('notes:add', ()),
            ('notes:success', ()),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        login_url = reverse('users:login')
        for name, args in names:
            with self.subTest():
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    redirect_url,
                    msg_prefix=f'Проверьте что страница {url} не доступна для'
                               f'не зарегистрированного пользователя и '
                               f'осуществляется редирект на {redirect_url}'
                )
