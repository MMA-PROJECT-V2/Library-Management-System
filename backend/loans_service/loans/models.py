from django.db import models
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


class Loan(models.Model):
    """
    Modèle représentant un emprunt de livre
    """
    STATUS_CHOICES = [
        ('ACTIVE', 'Actif'),
        ('RETURNED', 'Retourné'),
        ('OVERDUE', 'En retard'),
        ('RENEWED', 'Renouvelé'),
    ]
    
    # Relations avec autres services (Foreign Keys logiques)
    user_id = models.IntegerField(db_index=True, help_text="ID de l'utilisateur (User Service)")
    book_id = models.IntegerField(db_index=True, help_text="ID du livre (Books Service)")
    
    # Dates
    loan_date = models.DateField(auto_now_add=True, verbose_name="Date d'emprunt")
    due_date = models.DateField(verbose_name="Date de retour prévue")
    return_date = models.DateField(null=True, blank=True, verbose_name="Date de retour réelle")
    
    # Statut et gestion
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Montant de l'amende (DZD)")
    fine_paid = models.BooleanField(default=False, verbose_name="Amende payée")
    
    # Renouvellement
    renewal_count = models.IntegerField(default=0, verbose_name="Nombre de renouvellements")
    max_renewals = models.IntegerField(default=2, verbose_name="Nombre maximum de renouvellements")
    
    # Métadonnées
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'loans'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['book_id']),
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
        ]
        verbose_name = 'Emprunt'
        verbose_name_plural = 'Emprunts'
    
    def save(self, *args, **kwargs):
        """Calculer due_date automatiquement si non fourni"""
        if not self.due_date:
            self.due_date = timezone.now().date() + timedelta(days=14)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Loan #{self.id} - User {self.user_id} - Book {self.book_id} [{self.status}]"
    
    def is_overdue(self):
        """Vérifier si l'emprunt est en retard"""
        if self.status == 'RETURNED':
            return False
        return timezone.now().date() > self.due_date
    
    def calculate_fine(self, fine_per_day=50.00):
        """Calculer l'amende en fonction du nombre de jours de retard"""
        if not self.is_overdue():
            return Decimal('0.00')
        
        days_overdue = (timezone.now().date() - self.due_date).days
        fine = Decimal(str(fine_per_day)) * days_overdue
        self.fine_amount = fine
        self.save()
        return fine
    
    def can_renew(self):
        """Vérifier si l'emprunt peut être renouvelé"""
        return (
            self.status == 'ACTIVE' and
            self.renewal_count < self.max_renewals and
            not self.is_overdue()
        )
    
    def renew(self, additional_days=14):
        """Renouveler l'emprunt"""
        if self.can_renew():
            self.due_date = self.due_date + timedelta(days=additional_days)
            self.renewal_count += 1
            self.status = 'RENEWED'
            self.save()
            return True
        return False
    
    def mark_as_returned(self):
        """Marquer l'emprunt comme retourné"""
        self.return_date = timezone.now().date()
        self.status = 'RETURNED'
        
        # Calculer l'amende si en retard
        if self.is_overdue():
            self.calculate_fine()
        
        self.save()
        return True


class LoanHistory(models.Model):
    """
    Historique des actions sur les emprunts (audit)
    """
    ACTION_CHOICES = [
        ('CREATED', 'Créé'),
        ('RENEWED', 'Renouvelé'),
        ('RETURNED', 'Retourné'),
        ('OVERDUE', 'Marqué en retard'),
        ('FINE_CALCULATED', 'Amende calculée'),
        ('FINE_PAID', 'Amende payée'),
    ]
    
    loan_id = models.IntegerField(db_index=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    performed_by = models.IntegerField(null=True, blank=True, help_text="ID de l'utilisateur qui a effectué l'action")
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'loan_history'
        ordering = ['-created_at']
        verbose_name = 'Historique d\'emprunt'
        verbose_name_plural = 'Historiques d\'emprunts'
    
    def __str__(self):
        return f"{self.action} - Loan #{self.loan_id} - {self.created_at}"