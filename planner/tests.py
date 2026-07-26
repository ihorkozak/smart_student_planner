import pytest
from django.contrib.auth.models import User
from .models import Course, Task, Comment, Tag, TaskTag
from django.utils import timezone
from datetime import timedelta
from django.test import Client

@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='testpass123')


@pytest.fixture
def course(db, user):
    return Course.objects.create(
        name='Math',
        instructor='Himanshu',
        schedule='Mon 10:00',
        user=user
    )


@pytest.fixture
def task(db, user, course):
    return Task.objects.create(
        title='Test Task',
        description='Test Description',
        deadline=timezone.now() + timedelta(days=1),
        priority='high',
        course=course,
        user=user
    )


class TestCourseModel:
    def test_course_created(self, course):
        assert course.name == 'Math'
        assert course.instructor == 'Himanshu'

    def test_course_str(self, course):
        assert str(course) == 'Math'

    def test_course_belongs_to_user(self, course, user):
        assert course.user == user


class TestTaskModel:
    def test_task_created(self, task):
        assert task.title == 'Test Task'
        assert task.is_completed == False
        assert task.priority == 'high'

    def test_task_str(self, task):
        assert str(task) == 'Test Task'

    def test_task_complete(self, task):
        task.is_completed = True
        task.save()
        assert task.is_completed == True

    def test_task_belongs_to_course(self, task, course):
        assert task.course == course

    def test_task_deadline_in_future(self, task):
        assert task.deadline > timezone.now()


class TestCommentModel:
    def test_comment_created(self, db, user, task):
        comment = Comment.objects.create(
            content='Test comment',
            task=task,
            user=user
        )
        assert comment.content == 'Test comment'
        assert comment.task == task
        assert comment.user == user

    def test_multiple_comments(self, db, user, task):
        Comment.objects.create(content='Comment 1', task=task, user=user)
        Comment.objects.create(content='Comment 2', task=task, user=user)
        assert Comment.objects.filter(task=task).count() == 2


class TestTagModel:
    def test_tag_created(self, db):
        tag = Tag.objects.create(name='important')
        assert tag.name == 'important'

    def test_tag_str(self, db):
        tag = Tag.objects.create(name='urgent')
        assert str(tag) == 'urgent'


class TestTaskTag:
    def test_tasktag_created(self, db, task):
        tag = Tag.objects.create(name='exam')
        tasktag = TaskTag.objects.create(task=task, tag=tag)
        assert tasktag.task == task
        assert tasktag.tag == tag

    def test_task_can_have_multiple_tags(self, db, task):
        tag1 = Tag.objects.create(name='exam')
        tag2 = Tag.objects.create(name='important')
        TaskTag.objects.create(task=task, tag=tag1)
        TaskTag.objects.create(task=task, tag=tag2)
        assert TaskTag.objects.filter(task=task).count() == 2

@pytest.fixture
def django_client():
    return Client()

@pytest.fixture
def logged_client(db,user):
    client = Client()
    client.login(username="testuser", password='testpass123')
    return client
class TestViews:
    def test_login_page(self, django_client):
        response = django_client.get('/login/')
        assert response.status_code == 200

    def test_register_page(self, django_client):
        response = django_client.get('/register/')
        assert response.status_code == 200

    def test_dashboard_requires_login(self, django_client):
        response = django_client.get('/dashboard/')
        assert response.status_code == 302

    def test_dashboard_logged_in(self, logged_client):
        response = logged_client.get('/dashboard/')
        assert response.status_code == 200

    def test_courses_requires_login(self, django_client):
        response = django_client.get('/courses/')
        assert response.status_code == 302

    def test_courses_logged_in(self, logged_client):
        response = logged_client.get('/courses/')
        assert response.status_code == 200

    def test_tasks_logged_in(self, logged_client):
        response = logged_client.get('/tasks/')
        assert response.status_code == 200

    def test_create_course(self, logged_client, user):
        response = logged_client.post('/courses/create/', {
            'name': 'English',
            'instructor': 'Tatiana',
            'schedule': 'Tue 12:00'
        })
        assert response.status_code == 302
        assert Course.objects.filter(name='English').exists()

    def test_create_task(self, logged_client, user, course):
        response = logged_client.post('/tasks/create/', {
            'title': 'New Task',
            'description': 'Description',
            'deadline': '2027-01-01 07:00',
            'priority': 'low',
            'course': course.id
        })
        assert response.status_code == 302
        assert Task.objects.filter(title='New Task').exists()

    def test_delete_course(self, logged_client, course):
        response = logged_client.get(f'/courses/delete/{course.id}/')
        assert response.status_code == 302
        assert not Course.objects.filter(id=course.id).exists()

    def test_task_detail(self, logged_client, task):
        response = logged_client.get(f'/tasks/{task.id}/')
        assert response.status_code == 200

    def test_task_delete(self, logged_client, task):
        response = logged_client.get(f'/tasks/delete/{task.id}/')
        assert response.status_code == 302
        assert not Task.objects.filter(id=task.id).exists()

    def test_task_complete_view(self, logged_client, task):
        response = logged_client.get(f'/tasks/complete/{task.id}/')
        assert response.status_code == 302
        task.refresh_from_db()
        assert task.is_completed == True

    def test_add_comment_view(self, logged_client, task):
        response = logged_client.post(f'/tasks/{task.id}/comment/', {
            'content': 'Test comment from view'
        })
        assert response.status_code == 302
        assert Comment.objects.filter(content='Test comment from view').exists()

    def test_user_cannot_delete_others_course(self, db, course):
        other_user = User.objects.create_user(username='other', password='pass123')
        other_client = Client()
        other_client.login(username='other', password='pass123')
        response = other_client.get(f'/courses/delete/{course.id}/')
        assert Course.objects.filter(id=course.id).exists()

    def test_empty_task_title_fails(self, logged_client, course):
        response = logged_client.post('/tasks/create/', {
            'title': '',
            'description': 'desc',
            'deadline': '2027-01-01 07:00',
            'priority': 'low',
            'course': course.id
        })
        assert not Task.objects.filter(title='').exists()
class TestTagViews:
    def test_tag_list(self, logged_client):
        response = logged_client.get('/tags/')
        assert response.status_code == 200

    def test_create_tag(self, logged_client):
        response = logged_client.post('/tags/create/', {
            'name': 'important'
        })
        assert response.status_code == 302
        assert Tag.objects.filter(name='important').exists()

    def test_add_tag_to_task(self, logged_client, task):
        tag = Tag.objects.create(name='exam')
        response = logged_client.post(f'/tasks/{task.id}/add-tag/', {
            'tag': tag.id
        })
        assert response.status_code == 302
        assert TaskTag.objects.filter(task=task, tag=tag).exists()