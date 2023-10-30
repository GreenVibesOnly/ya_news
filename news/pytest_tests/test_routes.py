from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse


# Доступные страницы для анонимного пользователя
@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_id_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ),
)
def test_pages_availability_for_anonymous_user(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


# Доступ к страницам управления комментарием для авторизованных пользователей
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, comm_id_for_args, expected_status
):
    url = reverse(name, args=(comm_id_for_args))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


# Редирект для анонимных пользователей
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_redirect_for_anonymous_client(client, name, comm_id_for_args):
    login_url = reverse('users:login')
    url = reverse(name, args=comm_id_for_args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
