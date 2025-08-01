import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from userauth.models import UserProfile, Skill, UserSkill
from django.test import Client

User = get_user_model()

@pytest.mark.django_db
def test_user_registration():
    user = User.objects.create_user(username='testuser', password='testpass')
    assert UserProfile.objects.filter(user=user).exists()

@pytest.mark.django_db
def test_skill_creation():
    skill = Skill.objects.create(title='Python', slug='python')
    assert Skill.objects.filter(slug='python').exists()

@pytest.mark.django_db
def test_start_skill_view():
    user = User.objects.create_user(username='testuser2', password='testpass')
    skill = Skill.objects.create(title='Django', slug='django')
    client = Client()
    client.force_login(user)
    response = client.post(reverse('start_skill'), {'skill_slug': 'django'})
    assert response.status_code == 302
    assert UserSkill.objects.filter(user=user, skill=skill).exists()

@pytest.mark.django_db
def test_dashboard_view_authenticated():
    user = User.objects.create_user(username='dashuser', password='testpass')
    client = Client()
    client.force_login(user)
    response = client.get(reverse('dashboard'))
    assert response.status_code == 200
    assert b'Welcome Back' in response.content

@pytest.mark.django_db
def test_leaderboard_view():
    client = Client()
    response = client.get(reverse('leaderboard'))
    assert response.status_code == 200
    assert b'Leaderboard' in response.content

@pytest.mark.django_db
def test_skill_detail_view():
    user = User.objects.create_user(username='detailuser', password='testpass')
    skill = Skill.objects.create(title='AI', slug='ai')
    UserSkill.objects.create(user=user, skill=skill)
    client = Client()
    client.force_login(user)
    response = client.get(reverse('skill_detail', args=['ai']))
    assert response.status_code == 200
    assert b'Lessons' in response.content

@pytest.mark.django_db
def test_archive_skill():
    user = User.objects.create_user(username='archiveuser', password='testpass')
    skill = Skill.objects.create(title='ML', slug='ml')
    us = UserSkill.objects.create(user=user, skill=skill)
    client = Client()
    client.force_login(user)
    response = client.post(reverse('archive_skill', args=[us.id]))
    us.refresh_from_db()
    assert not us.is_active

@pytest.mark.django_db
def test_delete_skill():
    user = User.objects.create_user(username='deleteuser', password='testpass')
    skill = Skill.objects.create(title='Data', slug='data')
    us = UserSkill.objects.create(user=user, skill=skill)
    client = Client()
    client.force_login(user)
    response = client.post(reverse('delete_skill', args=[us.id]))
    assert not UserSkill.objects.filter(id=us.id).exists()

@pytest.mark.django_db
def test_download_skill_data():
    user = User.objects.create_user(username='downloaduser', password='testpass')
    skill = Skill.objects.create(title='Cloud', slug='cloud')
    us = UserSkill.objects.create(user=user, skill=skill)
    client = Client()
    client.force_login(user)
    response = client.get(reverse('download_skill_data', args=[us.id]))
    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'

@pytest.mark.django_db
def test_logout_view():
    user = User.objects.create_user(username='logoutuser', password='testpass')
    client = Client()
    client.force_login(user)
    response = client.get(reverse('logout'))
    assert response.status_code == 302

