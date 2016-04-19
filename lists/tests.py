from __future__ import absolute_import
from django.core.urlresolvers import resolve
from django.test import TestCase
from django.http import HttpRequest
from django.template.loader import render_to_string

from .views import home_page


class HomePageTest(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = home_page(request)
        expected_html = render_to_string('home.html', request=request)
        self.assertEqual(response.content.decode(), expected_html)

    def test_home_page_can_save_a_POST_request(self):
        request = HttpRequest()
        request.method = 'POST'
        request.POST['item_text'] = 'A new list item'

        response = home_page(request)

        self.assertIn('A new list item', response.content.decode())
        expected_html = render_to_string('home.html',
                                         context={'new_item_text':
                                                  'A new list item'},
                                         request=request)
        self.assertEqual(response.content.decode(), expected_html)
