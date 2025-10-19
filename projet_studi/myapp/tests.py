from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Ticket, Epreuve
from django.utils import timezone

User = get_user_model()

class TicketModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.epreuve = Epreuve.objects.create(
            discipline="Course",
            competition="Championnat",
            date=timezone.now(),
            heure="12:00",
            tarif=10
        )

    def test_ticket_creation(self):
        ticket = Ticket.objects.create(user=self.user, epreuve=self.epreuve, quantite=2)
        self.assertEqual(ticket.total, 20)
        self.assertEqual(ticket.quantite, 2)
        self.assertTrue(ticket.code)  # vérifie que le code est généré

    def test_ticket_quantity_validation(self):
        from django.core.exceptions import ValidationError
        ticket = Ticket(user=self.user, epreuve=self.epreuve, quantite=3)
        with self.assertRaises(ValidationError):
            ticket.clean()