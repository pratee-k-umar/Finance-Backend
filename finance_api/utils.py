"""
Utility functions for email notifications and webhooks
"""
import hashlib
import hmac
import json
from datetime import datetime

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from finance_core.models import EmailNotification, WebhookEvent


def send_email_notification(user, subject, template_name, context=None):
    """
    Send email notification to user
    
    Args:
        user: User object
        subject: Email subject
        template_name: Path to email template
        context: Dictionary of template context
    """
    if context is None:
        context = {}
    
    # Check if user has email notifications enabled
    try:
        email_settings = user.email_notifications
        if not getattr(email_settings, context.get('notification_type', 'budget_alerts')):
            return False
    except EmailNotification.DoesNotExist:
        pass  # Send if no settings exist (default=True)
    
    context['user'] = user
    context['site_name'] = 'Finance Dashboard'
    
    try:
        html_message = render_to_string(template_name, context)
        send_mail(
            subject,
            f"Message from {context['site_name']}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email to {user.email}: {str(e)}")
        return False


def send_budget_alert_email(user, budget, spent_amount, percentage_used):
    """Send budget alert email"""
    context = {
        'notification_type': 'budget_alerts',
        'category': budget.category,
        'limit_amount': budget.limit_amount,
        'spent_amount': spent_amount,
        'percentage_used': percentage_used,
        'remaining': budget.limit_amount - spent_amount,
        'frequency': budget.get_frequency_display(),
    }
    
    return send_email_notification(
        user,
        f"Budget Alert: {budget.category} Budget {percentage_used}% Used",
        'emails/budget_alert.html',
        context
    )


def send_monthly_summary_email(user, summary_data):
    """Send monthly summary email"""
    context = {
        'notification_type': 'monthly_summary',
        'summary': summary_data,
        'month': timezone.now().strftime('%B %Y'),
    }
    
    return send_email_notification(
        user,
        f"Monthly Financial Summary - {context['month']}",
        'emails/monthly_summary.html',
        context
    )


def send_recurring_transaction_email(user, transaction):
    """Send recurring transaction creation email"""
    context = {
        'notification_type': 'recurring_alerts',
        'transaction': transaction,
        'frequency': transaction.get_frequency_display(),
    }
    
    return send_email_notification(
        user,
        f"Recurring {transaction.get_record_type_display()} Created: {transaction.category}",
        'emails/recurring_transaction.html',
        context
    )


def trigger_webhook(webhook, event_data):
    """
    Trigger a webhook with event data
    
    Args:
        webhook: Webhook object
        event_data: Dictionary of event data
    
    Returns:
        WebhookEvent object
    """
    payload = {
        'event_type': webhook.event_type,
        'timestamp': timezone.now().isoformat(),
        'data': event_data,
    }
    
    # Create webhook event record
    webhook_event = WebhookEvent.objects.create(
        webhook=webhook,
        payload=payload,
        status='pending',
    )
    
    # Try to send immediately
    send_webhook(webhook_event)
    
    return webhook_event


def send_webhook(webhook_event, retry_count=0, max_retries=3):
    """
    Send webhook to external URL
    
    Args:
        webhook_event: WebhookEvent object
        retry_count: Current retry attempt
        max_retries: Maximum number of retries
    """
    webhook = webhook_event.webhook
    
    if not webhook.is_active:
        webhook_event.status = 'failed'
        webhook_event.error_message = 'Webhook is inactive'
        webhook_event.save()
        return
    
    # Generate HMAC signature
    payload_json = json.dumps(webhook_event.payload)
    signature = hmac.new(
        webhook.secret.encode(),
        payload_json.encode(),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        'Content-Type': 'application/json',
        'X-Webhook-Signature': signature,
        'X-Webhook-Event': webhook.event_type,
        'X-Webhook-Timestamp': timezone.now().isoformat(),
    }
    
    try:
        response = requests.post(
            webhook.url,
            data=payload_json,
            headers=headers,
            timeout=30,
        )
        
        webhook_event.response_status = response.status_code
        webhook_event.response_body = response.text
        webhook_event.status = 'sent' if response.status_code < 400 else 'failed'
        webhook_event.attempts += 1
        webhook_event.last_attempt_at = timezone.now()
        
        if response.status_code >= 400 and retry_count < max_retries:
            webhook_event.status = 'pending'
        
        webhook_event.save()
        
    except requests.exceptions.RequestException as e:
        webhook_event.error_message = str(e)
        webhook_event.status = 'failed' if retry_count >= max_retries else 'pending'
        webhook_event.attempts += 1
        webhook_event.last_attempt_at = timezone.now()
        webhook_event.save()


def trigger_record_webhook(user, record, event_type):
    """Trigger webhook for financial record event"""
    from finance_core.models import Webhook
    
    webhooks = Webhook.objects.filter(
        user=user,
        event_type=event_type,
        is_active=True,
    )
    
    event_data = {
        'record_id': str(record.id),
        'user_id': user.id,
        'amount': str(record.amount),
        'type': record.record_type,
        'category': record.category,
        'date': record.date.isoformat(),
        'created_at': record.created_at.isoformat(),
    }
    
    for webhook in webhooks:
        trigger_webhook(webhook, event_data)


def trigger_budget_alert_webhook(user, budget, spent_amount, percentage_used):
    """Trigger webhook for budget alert"""
    from finance_core.models import Webhook
    
    webhooks = Webhook.objects.filter(
        user=user,
        event_type='budget_exceeded',
        is_active=True,
    )
    
    event_data = {
        'budget_id': str(budget.id),
        'category': budget.category,
        'limit_amount': str(budget.limit_amount),
        'spent_amount': str(spent_amount),
        'percentage_used': percentage_used,
        'frequency': budget.frequency,
    }
    
    for webhook in webhooks:
        trigger_webhook(webhook, event_data)


# Email template context helpers
def get_budget_alert_context(user, budget, spent_amount, percentage_used):
    """Generate context for budget alert"""
    return {
        'user': user,
        'category': budget.category,
        'limit_amount': budget.limit_amount,
        'spent_amount': spent_amount,
        'percentage_used': percentage_used,
        'remaining': budget.limit_amount - spent_amount,
        'frequency': budget.get_frequency_display(),
    }