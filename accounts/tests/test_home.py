from django.test import TestCase
from django.urls import reverse

class HomePageTest(TestCase):
    def test_home_page_renders_successfully(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/home.html')
        self.assertContains(response, "Encontre leads qualificados e audite a presença digital deles em segundos")
        self.assertContains(response, "Como Funciona o Mecanismo")
        self.assertContains(response, "Planos Simples e Claros")
