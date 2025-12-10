from rest_framework import serializers
from .models import Notification, NotificationTemplate, NotificationLog


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "user_id", "type", "subject", "message", "status", "sent_at", "created_at"]
        read_only_fields = ["id", "sent_at", "created_at"]
    
    def validate_user_id(self, value):
        """Validate user_id is positive."""
        if value <= 0:
            raise serializers.ValidationError("User ID must be a positive integer")
        return value
    
    def validate_subject(self, value):
        """Validate subject length."""
        if len(value) > 255:
            raise serializers.ValidationError("Subject cannot exceed 255 characters")
        if not value.strip():
            raise serializers.ValidationError("Subject cannot be empty")
        return value.strip()
    
    def validate_message(self, value):
        """Validate message content."""
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        return value.strip()
    
    def validate_type(self, value):
        """Validate notification type."""
        valid_types = [choice[0] for choice in Notification.TYPE_CHOICES]
        if value not in valid_types:
            raise serializers.ValidationError(f"Type must be one of: {', '.join(valid_types)}")
        return value
    
    def validate_status(self, value):
        """Validate notification status."""
        valid_statuses = [choice[0] for choice in Notification.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value


class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = ["id", "name", "type", "subject_template", "message_template", 
                  "description", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
    
    def validate_name(self, value):
        """Validate template name."""
        if not value.strip():
            raise serializers.ValidationError("Template name cannot be empty")
        if len(value) > 150:
            raise serializers.ValidationError("Template name cannot exceed 150 characters")
        return value.strip()
    
    def validate_subject_template(self, value):
        """Validate subject template."""
        if not value.strip():
            raise serializers.ValidationError("Subject template cannot be empty")
        if len(value) > 255:
            raise serializers.ValidationError("Subject template cannot exceed 255 characters")
        return value.strip()
    
    def validate_message_template(self, value):
        """Validate message template."""
        if not value.strip():
            raise serializers.ValidationError("Message template cannot be empty")
        return value.strip()
    
    def validate_type(self, value):
        """Validate template type."""
        valid_types = [choice[0] for choice in Notification.TYPE_CHOICES]
        if value not in valid_types:
            raise serializers.ValidationError(f"Type must be one of: {', '.join(valid_types)}")
        return value


class NotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog
        fields = ["id", "notification", "status", "detail", "created_at"]
        read_only_fields = ["id", "created_at"]


class SendFromTemplateSerializer(serializers.Serializer):
    template_id = serializers.IntegerField(min_value=1)
    user_id = serializers.IntegerField(min_value=1)
    context = serializers.DictField(child=serializers.CharField(), required=False, default=dict)
    type = serializers.ChoiceField(choices=Notification.TYPE_CHOICES, required=False)
    
    def validate_template_id(self, value):
        """Check if template exists."""
        from .models import NotificationTemplate
        if not NotificationTemplate.objects.filter(pk=value).exists():
            raise serializers.ValidationError(f"Template with ID {value} does not exist")
        return value