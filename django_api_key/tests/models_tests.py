"""Tests for the models of the django_api_key app."""
from django.test import Client, TestCase

from django_api_key.models import APIKey, IPAccess, KeyGroup


class APIKeyModelTests(TestCase):
    def test_no_key_no_access(self):
        c = Client()
        response = c.get('/admin/')
        self.assertEqual(response.status_code, 403)

    def test_correct_key_can_access(self):
        me = APIKey.objects.create(name="test", path_re="/admin.*")

        c = Client()
        response = c.get('/admin/', follow=True, HTTP_API_KEY=me.key)
        self.assertEqual(response.status_code, 200)

    def test_incorrect_key_can_not_access(self):
        APIKey.objects.create(name="test", path_re="/admin.*")

        c = Client()
        response = c.get('/admin/', follow=True, HTTP_API_KEY="random_key")
        self.assertEqual(response.status_code, 403)

    def test_incorrect_path_can_not_access(self):
        me = APIKey.objects.create(name="test", path_re="/admin111.*")

        c = Client()
        response = c.get('/admin/', follow=True, HTTP_API_KEY=me.key)
        self.assertEqual(response.status_code, 403)

    def test_no_key_whitelisted_ip_can_access(self):
        IPAccess.objects.create(name="test", path_re="/admin.*", ip="1.2.3.4")
        c = Client()

        response = c.get('/admin/', follow=True, REMOTE_ADDR="1.2.3.4")
        self.assertEqual(response.status_code, 200)

    def test_no_key_non_whitelisted_ip_can_not_access(self):
        IPAccess.objects.create(name="test", path_re="/admin.*", ip="1.2.3.4")
        c = Client()

        response = c.get('/admin/', follow=True, REMOTE_ADDR="2.3.4.5")
        self.assertEqual(response.status_code, 403)

    def test_empty_path_re_use_group_one(self):
        group = KeyGroup.objects.create(name="test_group", path_re="/admin.*")
        me = APIKey.objects.create(name="test_key", path_re="", group=group)

        c = Client()
        response = c.get('/admin/', follow=True, HTTP_API_KEY=me.key)
        self.assertEqual(response.status_code, 200)

    def test_empty_path_re_no_group_allow_all(self):
        me = APIKey.objects.create(name="test_key", path_re="")

        c = Client()
        response = c.get('/admin/', follow=True, HTTP_API_KEY=me.key)
        self.assertEqual(response.status_code, 200)

    def test_key_path_re_override_group_one(self):
        group = KeyGroup.objects.create(name="test_group", path_re="/admin.*")
        me = APIKey.objects.create(name="test_key", path_re="/abc", group=group)

        c = Client()
        response = c.get('/admin/', follow=True, HTTP_API_KEY=me.key)
        self.assertEqual(response.status_code, 403)
        print("{} overrides {} correctly".format(me, group))
