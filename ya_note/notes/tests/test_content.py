from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


class TestContent(TestCase):
    """Тестирование контента приложения 'Заметки'."""

    TITLE = 'заголовок_заметки'
    TEXT = 'текст_заметки'
    AUTHOR = 'автор_заметки'
    USER = 'зарегистрированный_пользователь'
    SLUG = 'slug'

    NOTE_LIST_URL = reverse('notes:list')
    ADD_NOTE_URL = reverse('notes:add')
    EDIT_NOTE_URL = reverse('notes:edit', args=(SLUG,))

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username=cls.AUTHOR)
        cls.user = User.objects.create_user(username=cls.USER)
        cls.note = Note.objects.create(title=cls.TITLE, text=cls.TEXT,
                                       author=cls.author, slug=cls.SLUG)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.user_client = Client()
        self.user_client.force_login(self.user)

    def test_note_in_note_list_page_for_author(self):
        """Заметка должна быть в списке object_list в словаре context."""
        response = self.author_client.get(self.NOTE_LIST_URL)
        object_list = response.context['object_list']
        self.assertEqual(
            object_list.count(),
            1,
            'Проверьте что заметки пользователя передаются на страницу со '
            'списком заметок списке object_list в словаре context.'
        )
        note = object_list[0]
        self.assertEqual(note.title, self.note.title, 'Неверный заголовок')
        self.assertEqual(note.text, self.note.text, 'Текст заметки неверен.')
        self.assertEqual(note.slug, self.note.slug, 'Slug заметки неверен.')
        self.assertEqual(note.author, self.note.author, 'Автор неверен.')

    def test_only_notes_for_author_in_note_list_page(self):
        """Список заметок должен содержать только заметки одного автора."""
        response = self.user_client.get(self.NOTE_LIST_URL)
        object_list = response.context['object_list']
        self.assertEqual(
            object_list.count(),
            0,
            'Проверьте что заметки одного пользователя не попадают в список '
            'заметок другого пользователя.'
        )

    def test_available_form_for_page(self):
        """Страницы создания и редактирования заметки содержит форму."""
        urls = (self.ADD_NOTE_URL, self.EDIT_NOTE_URL)
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
