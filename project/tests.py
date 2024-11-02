import unittest
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.test import RequestFactory, TestCase, Client
from django.http import HttpResponse
from django.urls import reverse
from .forms import EnterpriseForm, SurveyForm
from .models import Enterprise, SurveyResponse
from .views import your_view, enterprise_detail, enterprise_list, enterprise_edited, generate_pie_chart


class TestYourView(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()
    
    @patch('project.views.create_plot.delay')
    def test_view_returns_http_response(self, mock_create_plot):
        request = self.factory.get('/')
        response = your_view(request)
        self.assertIsInstance(response, HttpResponse)
    
    @patch('project.views.create_plot.delay')
    def test_view_returns_expected_message(self, mock_create_plot):
        request = self.factory.get('/')
        response = your_view(request)
        self.assertEqual(response.content, b'Plot creation started')
    
    @patch('project.views.create_plot.delay')
    def test_create_plot_task_is_called(self, mock_create_plot):
        request = self.factory.get('/')
        your_view(request)
        mock_create_plot.assert_called_once()


class TestAddEnterpriseView(TestCase):
    def test_post_request_valid_form(self):
        # Create a valid form data
        data = {'name': 'Test Enterprise', 'employees': 10}
        response = self.client.post(reverse('add_enterprise'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_enterprise_success.html')
        self.assertEqual(Enterprise.objects.count(), 1)
    
    def test_post_request_invalid_form(self):
        # Create an invalid form data
        data = {'name': '', 'employees': -1}
        response = self.client.post(reverse('add_enterprise'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_enterprise.html')
        self.assertEqual(Enterprise.objects.count(), 0)
    
    def test_get_request(self):
        response = self.client.get(reverse('add_enterprise'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_enterprise.html')
        self.assertIsInstance(response.context['form'], EnterpriseForm)


class EnterpriseDetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.enterprise = Enterprise.objects.create(name='Test Enterprise', slug='test-enterprise',
                                                    employees=1)  # Provide a default value for employees
    
    def test_existing_enterprise(self):
        response = self.client.get(reverse('enterprise_detail', args=[self.enterprise.slug]))
        self.assertEqual(response.status_code, 200)
    
    def test_non_existing_enterprise(self):
        response = self.client.get(reverse('enterprise_detail', args=['non-existing-slug']))
        self.assertEqual(response.status_code, 404)
    
    def test_template_rendering(self):
        response = self.client.get(reverse('enterprise_detail', args=[self.enterprise.slug]))
        self.assertTemplateUsed(response, 'enterprise_detail.html')
    
    def test_context_passing(self):
        response = self.client.get(reverse('enterprise_detail', args=[self.enterprise.slug]))
        self.assertIn('enterprise', response.context)
        self.assertIn('has_records', response.context)
        self.assertIn('survey_url', response.context)
    
    def test_survey_url_generation(self):
        response = self.client.get(reverse('enterprise_detail', args=[self.enterprise.slug]))
        # Use response.wsgi_request to get the original request object
        survey_url = response.wsgi_request.build_absolute_uri(reverse('survey', args=[self.enterprise.id]))
        self.assertEqual(response.context['survey_url'], survey_url)
    
    def test_has_records(self):
        SurveyResponse.objects.create(enterprise=self.enterprise)
        response = self.client.get(reverse('enterprise_detail', args=[self.enterprise.slug]))
        self.assertTrue(response.context['has_records'])
    
    def test_no_records(self):
        response = self.client.get(reverse('enterprise_detail', args=[self.enterprise.slug]))
        self.assertFalse(response.context['has_records'])


class EnterpriseListViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.enterprise = Enterprise.objects.create(name='Test Enterprise', slug='test-enterprise', employees=1)
        self.url = reverse('enterprise_list')
    
    def test_view_returns_successful_response(self):
        request = self.factory.get(self.url)
        response = enterprise_list(request)
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'enterprise_list.html')  # Use assertTemplateUsed
    
    def test_view_passes_enterprises_to_template(self):
        Enterprise.objects.create(name='Test Enterprise 2', slug='test-enterprise-2', employees=1)
        response = self.client.get(self.url)
        self.assertEqual(len(response.context['enterprises']), 2)
        self.assertEqual(response.context['enterprises'][0].name, 'Test Enterprise')
        self.assertEqual(response.context['enterprises'][1].name, 'Test Enterprise 2')


class TestEditEnterpriseView(TestCase):
    def setUp(self):
        self.enterprise = Enterprise.objects.create(name='Test Enterprise', slug='test-enterprise', employees=1)
        self.url = reverse('edit_enterprise', args=[self.enterprise.slug])
    
    def test_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_enterprise.html')
        self.assertIsInstance(response.context['form'], EnterpriseForm)
    
    def test_post_request_valid_form(self):
        data = {'name': 'Updated Test Enterprise', 'employees': 10}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Enterprise.objects.count(), 1)
        self.assertEqual(Enterprise.objects.first().name, 'Updated Test Enterprise')
    
    def test_post_request_invalid_form(self):
        data = {'name': '', 'employees': -1}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_enterprise.html')
        self.assertEqual(Enterprise.objects.count(), 1)
        self.assertEqual(Enterprise.objects.first().name, 'Test Enterprise')


class TestEnterpriseEdited(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_enterprise_edited_returns_rendered_template(self):
        url = reverse('edit_enterprise_success', args=['test-slug'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_enterprise_success.html')
    
    def test_enterprise_edited_passes_slug_to_template(self):
        url = reverse('edit_enterprise_success', args=['test-slug'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_enterprise_success.html')
        self.assertIn('slug', response.context)
        self.assertEqual(response.context['slug'], 'test-slug')


class EnterpriseAddedTestCase(TestCase):
    def test_enterprise_added(self):
        response = self.client.get(reverse('add_enterprise_success'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_enterprise_success.html')


class TestGeneratePieChart(unittest.TestCase):
    def test_valid_data(self):
        data = {'A': 10, 'B': 20, 'C': 30}
        title = 'Test Chart'
        svg_data, colors = generate_pie_chart(data, title)
        self.assertIsInstance(svg_data, str)
        self.assertIsInstance(colors, list)
        self.assertEqual(len(colors), 3)
    
    def test_empty_data(self):
        data = {}
        title = 'Test Chart'
        with self.assertRaises(ValueError):
            generate_pie_chart(data, title)
    
    def test_invalid_data_type(self):
        data = 'invalid data'
        title = 'Test Chart'
        with self.assertRaises(TypeError):
            generate_pie_chart(data, title)
    
    def test_missing_title(self):
        data = {'A': 10, 'B': 20, 'C': 30}
        with self.assertRaises(TypeError):
            generate_pie_chart(data)
    
    def test_custom_figsize(self):
        data = {'A': 10, 'B': 20, 'C': 30}
        title = 'Test Chart'
        figsize = (8, 6)
        svg_data, colors = generate_pie_chart(data, title, figsize)
        self.assertIsInstance(svg_data, str)
        self.assertIsInstance(colors, list)
        self.assertEqual(len(colors), 3)


if __name__ == '__main__':
    unittest.main()
