from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note


class TestCreateNote(TestCase):
    """Тестирование создания заметки."""

    TITLE = 'заголовок_заметки'
    TEXT = 'текст_заметки'
    AUTHOR = 'автор_заметки'
    USER = 'зарегистрированный_пользователь'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = User.objects.create_user(username=cls.USER)
        cls.notes_add_url = reverse('notes:add')
        cls.form_data = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'author': cls.user
        }

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_anonymous_user_cant_create_comment(self):
        """Проверить, что анонимный пользователь не может создать заметку."""
        self.client.post(reverse('notes:add'), data=self.form_data)
        comments_count = Note.objects.count()
        self.assertEqual(
            comments_count,
            0,
            'Убедитесь, что незарегистрированный пользователь не может '
            'создавать заметки.'
        )

    def test_auth_user_can_create_note(self):
        """Проверить что зарегистрированный пользователь может создать заметку.
        """
        self.auth_client.force_login(self.user)
        response = self.auth_client.post(
            self.notes_add_url,
            data=self.form_data
        )
        self.assertRedirects(
            response,
            reverse('notes:success'),
            msg_prefix=f'Убедитесь что после заполнения формы создания '
                       f'заметки пользователь перенаправляется на страницу '
                       f'{reverse("notes:success")}.'
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.TITLE, 'Заголовок заметки неверен')
        self.assertEqual(note.text, self.TEXT, 'Текст заметки неверен')
        self.assertEqual(note.slug, slugify(self.TITLE), 'Slug неверен')
        self.assertEqual(note.author, self.user, 'Автор заметки неверен')

    def test_unique_slug(self):
        """Проверить, что невозможно создать две заметки с одинаковым slug."""
        note = Note.objects.create(**self.form_data)
        response = self.auth_client.post(
            self.notes_add_url,
            data=self.form_data
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(note.slug + WARNING),
            msg_prefix='Убедитесь, что нельзя создать две заметки с '
                       'одинаковым slug.'
        )
        self.assertEqual(
            Note.objects.count(),
            1,
            'Убедитесь, что нельзя создать две заметки с одинаковым slug.'
        )

    def test_empty_slug_take_title(self):
        """Проверить, что если slug не заполнен, то он формируется
        автоматически из title.
        """
        self.form_data['slug'] = ''
        self.auth_client.post(self.notes_add_url, data=self.form_data)
        note = Note.objects.get()
        self.assertEqual(
            note.slug,
            slugify(note.title),
            'Убедитесь, что slug формируется автоматически из title.')


class TestNoteEdit(TestCase):
    """Тестирование редактирования заметки."""

    NOTE_TITLE = 'заголовок_заметки'
    NEW_NOTE_TITLE = 'новый_заголовок_заметки'
    NOTE_TEXT = 'текст_заметки'
    NEW_NOTE_TEXT = 'новый_текст_заметки'
    SLUG = 'slug'
    NEW_SLUG = 'newslug'
    AUTHOR = 'автор_заметки'
    USER = 'зарегистрированный_пользователь'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username=cls.AUTHOR)
        cls.user = User.objects.create(username=cls.USER)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author,
            slug=cls.SLUG
        )
        cls.success_url = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', kwargs={'slug': cls.note.slug})
        cls.delete_url = reverse('notes:delete',
                                 kwargs={'slug': cls.note.slug})
        cls.form_data = {'title': cls.NEW_NOTE_TITLE,
                         'text': cls.NEW_NOTE_TEXT,
                         'author': cls.author,
                         'slug': cls.NEW_SLUG}

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.user_client = Client()
        self.user_client.force_login(self.user)

    def test_author_can_edit_note(self):
        """Пользователь может редактировать свои заметки."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(
            response,
            self.success_url,
            msg_prefix=f'Убедитесь, что после редактирования заметки '
                       f'пользователь перенаправляется на страницу '
                       f'{self.success_url}'
        )
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE,
                         'Заголовок неверен')
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT,
                         'Текст неверен')
        self.assertEqual(self.note.slug, self.NEW_SLUG,
                         'Slug неверен')
        self.assertEqual(self.note.author, self.author)

    def test_author_can_delete_note(self):
        """Пользователь может удалять свои заметки."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(
            response,
            self.success_url,
            msg_prefix=f'Убедитесь, что после удаления заметки пользователь '
                       f'перенаправляется на страницу {self.success_url}'
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0, 'Убедитесь, что заметка удалена')

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалять чужие заметки"""
        self.user_client.delete(self.delete_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1, 'Убедитесь, что заметка не удалена')

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может редактировать чужие заметки."""
        response = self.user_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
            'Убедитесь, что заметка не доступна для редактирования '
            'не автором заметки'
        )
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE, 'Заголовок неверен')
        self.assertEqual(self.note.text, self.NOTE_TEXT, 'Текст неверен')
        self.assertEqual(self.note.slug, self.SLUG, 'Slug неверен')
        self.assertEqual(self.note.author, self.author, 'Автор неверен')
