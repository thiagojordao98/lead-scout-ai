from django.test import TestCase
from django.urls import reverse

class HomePageTest(TestCase):
    def test_home_page_renders_successfully(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/home.html')
        self.assertContains(response, "Pare de caçar leads frios. Encontre empresas prontas para comprar seus serviços.")
        self.assertContains(response, "Prospecção no piloto automático")
        self.assertContains(response, "Planos simples e transparentes")
