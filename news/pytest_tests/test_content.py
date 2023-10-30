import pytest
from django.urls import reverse
from yanews import settings


# Ограничение кол-ва новостей на гл странице
@pytest.mark.django_db
def test_news_count(news_list, client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


# Сортировка новостей
@pytest.mark.django_db
def test_news_order(news_list, client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert sorted_dates == all_dates


# Сортировка комментариев
@pytest.mark.django_db
def test_comments_order(client, news_id_for_args, comment_list):
    url = reverse('news:detail', args=news_id_for_args)
    response = client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_dates = [comment.created for comment in all_comments]
    sorted_dates = sorted(all_dates)
    assert sorted_dates == all_dates


# Доступность формы с авторизацией и без
@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, form_in_list',
    (
        (pytest.lazy_fixture('admin_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_pages_contains_form(
    parametrized_client, form_in_list, news_id_for_args
):
    url = reverse('news:detail', args=news_id_for_args)
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_in_list
