from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site
from email.mime.base import MIMEBase
from email import encoders

def get_auth_response_data(user, token):
    """
    Constructs an authentication response data dictionary.
    """
    return {
        'token': token.key,
        'email': user.email,
        'user_id': user.pk,
    }

def get_domain():
    """
    Returns the current domain.
    In debug mode, a hard-coded value is being used.
    """
    if settings.DEBUG:
        return 'http://localhost:8000'
    current_site = Site.objects.get_current()
    return current_site.domain

def generate_email_base_data(recipient):
    """
    Returns basic data required for every email template.
    """
    return {
        'recipient': recipient.split('@')[0]
    } 

def render_email_content(template_name, email_data):
    """
    Renders email content in plain text and html format.
    Both alternatives each require a corresponding template in the "emails" directory.
    """
    text_file = f"emails/{template_name}.txt"
    html_file = f"emails/{template_name}.html"
    try:
        text_content = render_to_string(text_file, context=email_data)
        html_content = render_to_string(html_file, context=email_data)        
        return text_content, html_content
    except:
        raise Exception("Email rendering failed. Please check email template names and paths.")
    
def prepare_logo(svg_file):
    """
    Prepares the logo SVG to be displayed as an inline image in an email,
    defining its MIME type and Content-ID.
    """
    mime_svg = MIMEBase('image', 'svg+xml')
    mime_svg.set_payload(svg_file.read())
    encoders.encode_base64(mime_svg)
    mime_svg.add_header('Content-ID', '<logo>')
    mime_svg.add_header('Content-Disposition', 'inline', filename='logo.svg')
    return mime_svg
    
def send_email_with_data(subject, template_name, recipient, email_data):
    """
    Sends an email to the specified recipient using the specified template
    and filling it with customizable data.
    """
    text, html = render_email_content(template_name, email_data)
    msg = EmailMultiAlternatives(
        subject,
        text,
        "noreply@bengt-fruechtenicht.de",
        [recipient],
    )
    msg.attach_alternative(html, "text/html")
    with open('static/img/logo.svg', 'rb') as svg_file:
        mime_svg = prepare_logo(svg_file)
        msg.attach(mime_svg)
    msg.send()

def send_account_activation_email(recipient, activation_url):
    """
    Sends an account activation email.
    The activation URL links to the frontend and must contain a valid token.
    """
    email_data = generate_email_base_data(recipient)
    email_data.update({'activation_url': activation_url})
    send_email_with_data('Confirm your email', 'account_activation', recipient, email_data)

def send_password_reset_email(recipient, reset_url):
    """
    Sends a password reset email.
    The reset URL links to the frontend and must contain a valid token.
    """
    email_data = generate_email_base_data(recipient)
    email_data.update({'reset_url': reset_url})
    send_email_with_data('Reset your password', 'reset_password', recipient, email_data)