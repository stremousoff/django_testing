from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


class TestContent(TestCase):
    """Тестирование контента приложения 'Заметки'."""

    TITLE = 'заголовок_заметки'
    TEXT = 'текст_заметки'
    AUTHOR = 'автор_заметки'
    USER = 'зарегистрированный_пользователь'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username=cls.AUTHOR)
        cls.user = User.objects.create_user(username=cls.USER)
        cls.note = Note.objects.create(title=cls.TITLE, text=cls.TEXT,
                                       author=cls.author)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.user_client = Client()
        self.user_client.force_login(self.user)

    def test_note_in_note_list_page(self):
        """Проверка, что отдельная заметка передаётся на страницу со списком
        заметок в списке object_list в словаре context.
        """
        response = self.author_client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        self.assertIn(
            self.note,
            object_list,
            f'Проверьте что заметки пользователя передаются на страницу '
            f'со списком заметок списке object_list в словаре context.'
        )

    def test_only_notes_for_author_in_note_list_page(self):
        """Проверка, что в список заметок одного пользователя не попадают
        заметки другого пользователя.
        """
        response = self.user_client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        self.assertNotIn(
            self.note,
            object_list,
            f'Проверьте что заметки одного пользователя не попадают в'
            f'список заметок другого пользователя.'
        )

    def test_available_form_for_page(self):
        """Проверка, что на страницы создания и редактирования заметки
        отображается форма.
        """
        names = (
            ('notes:add', ()),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in names:
            with self.subTest():
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn(
                    'form',
                    response.context,
                    f'Проверьте что на странице {url} отображается форма.'
                )
