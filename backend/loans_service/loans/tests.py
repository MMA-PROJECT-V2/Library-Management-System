from django.test import TestCase

# Create your tests here.
# Import des modules nécessaires
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Book, Loan

# Ensuite, tu peux écrire ta classe de tests
class LoanAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.book = Book.objects.create(title="Livre Test", author="Auteur Test")
        self.create_loan_url = reverse('loans-list')
        self.list_loans_url = reverse('loans-list')

    # Tests ici...
