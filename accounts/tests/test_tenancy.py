from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from accounts.models import Organization

User = get_user_model()

class TenancyOnboardingTest(TestCase):
    def test_registration_creates_organization_and_assigns_owner(self):
        response = self.client.post(reverse('accounts:register'), {
            'email': 'tenant_owner@test.com',
            'password1': 'OnboardingSecurePassword2026!',
            'password2': 'OnboardingSecurePassword2026!'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Check user is created and has an organization
        user = User.objects.get(email='tenant_owner@test.com')
        self.assertIsNotNone(user.organization)
        self.assertEqual(user.role, 'OWNER')
        self.assertEqual(user.organization.credits_balance, 10)
        self.assertEqual(user.organization.name, "Agência tenant_owner@test.com")

