from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"
    verbose_name = "Notifications Service"
    
    def ready(self):
        """
        Create notification templates when the app starts.
        """
        # Import here to avoid AppRegistryNotReady error
        from .models import NotificationTemplate
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Define all templates
        templates = [
            # Loan templates
            {
                'name': 'loan_created',
                'type': 'EMAIL',
                'subject_template': '📚 Confirmation d\'emprunt - Bibliothèque',
                'message_template': '''Bonjour,

Nous vous confirmons l'emprunt du livre suivant :

📖 DÉTAILS DU LIVRE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Titre : {{ book_title }}
• Auteur : {{ book_author|default:"Non spécifié" }}
• ISBN : {{ book_isbn|default:"Non spécifié" }}
• Catégorie : {{ book_category|default:"Non spécifiée" }}

📅 INFORMATIONS D'EMPRUNT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Date d'emprunt : {{ loan_date }}
• Date de retour prévue : {{ due_date }}
• Durée : 14 jours
• Numéro d'emprunt : #{{ loan_id }}

⚠️ RAPPEL IMPORTANT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Merci de retourner le livre avant le {{ due_date }}.
En cas de retard, une amende de 50 DZD par jour sera appliquée.

Vous pouvez renouveler votre emprunt jusqu'à 2 fois si le livre n'est pas réservé par un autre utilisateur.

Cordialement,
L'équipe de la Bibliothèque''',
                'description': 'Email sent when a new loan is created',
            },
            {
                'name': 'loan_returned_ontime',
                'type': 'EMAIL',
                'subject_template': '✅ Retour confirmé - Bibliothèque',
                'message_template': '''Bonjour,

Nous confirmons le retour du livre suivant :

📖 DÉTAILS DU LIVRE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Titre : {{ book_title }}
• Numéro d'emprunt : #{{ loan_id }}

📅 INFORMATIONS DE RETOUR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Date de retour : {{ return_date }}
• Date prévue : {{ due_date }}
• Statut : ✅ Retour dans les délais

Merci d'avoir respecté les délais de retour !

Cordialement,
L'équipe de la Bibliothèque''',
                'description': 'Email sent when a book is returned on time',
            },
            {
                'name': 'loan_returned_late',
                'type': 'EMAIL',
                'subject_template': '✅ Retour confirmé - Bibliothèque',
                'message_template': '''Bonjour,

Nous confirmons le retour du livre suivant :

📖 DÉTAILS DU LIVRE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Titre : {{ book_title }}
• Numéro d'emprunt : #{{ loan_id }}

📅 INFORMATIONS DE RETOUR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Date de retour : {{ return_date }}
• Date prévue : {{ due_date }}
• Retard : {{ days_overdue }} jour(s)

💰 AMENDE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Montant : {{ fine_amount }} DZD
• Tarif : 50 DZD par jour de retard

⚠️ RAPPEL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Merci de régler cette amende auprès de la bibliothèque dans les plus brefs délais.

Cordialement,
L'équipe de la Bibliothèque''',
                'description': 'Email sent when a book is returned late with a fine',
            },
            {
                'name': 'loan_renewed',
                'type': 'EMAIL',
                'subject_template': '🔄 Renouvellement confirmé - Bibliothèque',
                'message_template': '''Bonjour,

Votre emprunt a été renouvelé avec succès !

📖 DÉTAILS DU LIVRE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Titre : {{ book_title }}
• Numéro d'emprunt : #{{ loan_id }}

🔄 INFORMATIONS DE RENOUVELLEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Nombre de renouvellements : {{ renewal_count }}/2
• Ancienne date de retour : {{ old_due_date }}
• Nouvelle date de retour : {{ new_due_date }}
• Durée supplémentaire : 14 jours

⚠️ RAPPEL IMPORTANT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Merci de retourner le livre avant le {{ new_due_date }}.
En cas de retard, une amende de 50 DZD par jour sera appliquée.

{{ renewal_message }}

Cordialement,
L'équipe de la Bibliothèque''',
                'description': 'Email sent when a loan is renewed',
            },
            # User registration template
            {
                'name': 'user_registered',
                'type': 'EMAIL',
                'subject_template': '🎉 Bienvenue à la Bibliothèque !',
                'message_template': '''Bonjour {{ user_name }},

Bienvenue à la Bibliothèque !

Votre compte a été créé avec succès. Vous pouvez maintenant :

📚 SERVICES DISPONIBLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Emprunter jusqu'à 3 livres simultanément
• Renouveler vos emprunts jusqu'à 2 fois
• Consulter notre catalogue en ligne
• Gérer vos emprunts depuis votre compte

📋 INFORMATIONS DE VOTRE COMPTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Email : {{ user_email }}
• Rôle : {{ user_role }}

⚠️ RÈGLES IMPORTANTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Durée d'emprunt : 14 jours
• Amende en cas de retard : 50 DZD par jour
• Maximum de renouvellements : 2 fois

Nous vous souhaitons une excellente expérience de lecture !

Cordialement,
L'équipe de la Bibliothèque''',
                'description': 'Welcome email sent when a new user registers',
            },
        ]
        
        # Create or update templates
        try:
            for template_data in templates:
                NotificationTemplate.objects.update_or_create(
                    name=template_data['name'],
                    defaults={
                        'type': template_data['type'],
                        'subject_template': template_data['subject_template'],
                        'message_template': template_data['message_template'],
                        'description': template_data['description'],
                        'is_active': True
                    }
                )
            logger.info(f"✅ Created/updated {len(templates)} notification templates")
        except Exception as e:
            # Don't crash the app if templates can't be created
            logger.warning(f"Could not create templates: {e}")