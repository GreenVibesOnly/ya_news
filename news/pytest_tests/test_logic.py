from django.urls import reverse
from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects

from news.forms import WARNING
from news.models import Comment


# Создание комментария авторизованным пользователем
def test_user_can_create_comment(
    author_client,
    author, news,
    form_data,
    news_detail_url
):
    response = author_client.post(news_detail_url, data=form_data)
    # Проверка редиректа после создания:
    assertRedirects(response, f'{news_detail_url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    # Проверка соответствия формы:
    assert new_comment.text == form_data['text']
    assert new_comment.news == news
    assert new_comment.author == author


# Анонимный пользователь не может создать коммментарий
@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client,
    form_data,
    news_detail_url
):
    response = client.post(news_detail_url, data=form_data)
    # Проверка редиректа на страницу логина:
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={news_detail_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


# Нельзя создать комментарий с запрещенными словами
def test_user_cant_use_bad_words(
    admin_client,
    bad_words_form_data,
    news_detail_url
):
    # Узнаем, сколько комментариев уже есть у автора:
    comment_count = Comment.objects.count()
    response = admin_client.post(news_detail_url, data=bad_words_form_data)
    # Проверяем, что ответ содержит ошибку:
    assert response.context['form'].errors.get('text') == [WARNING]
    comment_count_after_response = Comment.objects.count()
    # Проверяем, что коммент не создался:
    assert comment_count == comment_count_after_response


# Автор может изменить свой комментарий
def test_author_can_edit_comment(
    author_client,
    form_data,
    comment,
    comm_id_for_args,
    news_detail_url
):
    url = reverse('news:edit', args=(comm_id_for_args))
    response = author_client.post(url, form_data)
    # Проверка редиректа после изменения:
    assertRedirects(response, f'{news_detail_url}#comments')
    comment.refresh_from_db()
    # Проверка соответствия текста комментария:
    assert comment.text == form_data['text']


def test_other_user_cant_edit_comment(
    admin_client,
    form_data,
    comment,
    comm_id_for_args
):
    url = reverse('news:edit', args=(comm_id_for_args))
    response = admin_client.post(url, form_data)
    # Проверяем, что страница не найдена:
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    # Проверяем, что коммент не изменился:
    assert comment.text == comment_from_db.text


def test_author_can_delete_comment(
    author_client,
    comm_id_for_args,
    news_detail_url
):
    # Узнаем, сколько комментариев уже есть у автора:
    comment_count = Comment.objects.count()
    url = reverse('news:delete', args=comm_id_for_args)
    response = author_client.post(url)
    assertRedirects(response, f'{news_detail_url}#comments')
    comment_count_after_response = Comment.objects.count()
    # Проверяем, что коммент удалился:
    assert comment_count - 1 == comment_count_after_response


def test_other_user_cant_delete_comment(admin_client, comm_id_for_args):
    # Узнаем, сколько комментариев уже есть у автора:
    comment_count = Comment.objects.count()
    url = reverse('news:delete', args=comm_id_for_args)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_count_after_response = Comment.objects.count()
    # Проверяем, что коммент не удалился:
    assert comment_count == comment_count_after_response
