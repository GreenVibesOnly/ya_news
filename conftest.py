import pytest
from datetime import datetime, timedelta
from django.urls import reverse
from yanews import settings

from news.forms import BAD_WORDS
from news.models import Comment, News


# Возвращает объект пользователя "Автор"
@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


# Возвращает клиент с залогиненным пользователем "Автор"
@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


# Возвращает объект новости
@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


# Возвращает список новостей для гл страницы
@pytest.fixture
def news_list():
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=datetime.today() - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    news_list = News.objects.bulk_create(all_news)
    return news_list


# Возвращает объект комментария к новости 1 от "Автора"
@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


# Возвращает список комментариев к новости 1 от "Автора"
@pytest.fixture
def comment_list(author, news):
    all_comments = [
        Comment(
            news=news,
            author=author,
            text=f'Tекст {index}',
        )
        for index in range(2)
    ]
    comment_list = Comment.objects.bulk_create(all_comments)
    return comment_list


# Возвращает кортеж с ID новости
@pytest.fixture
def news_id_for_args(news):
    return news.id,


# Возвращает кортеж с ID комментария от "Автора"
@pytest.fixture
def comm_id_for_args(comment):
    return comment.id,


# Возвращает ссылку на страницу новости 1
@pytest.fixture
def news_detail_url(news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    return url


# Возвращает данные для заполнения формы комментария
@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }


# Возвращает данные для заполнения формы с запрещен. словами
@pytest.fixture
def bad_words_form_data():
    return {
        'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст',
    }
