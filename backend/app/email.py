import logging
import resend
from .config import get_settings

settings = get_settings()
resend.api_key = settings.resend_api_key
logger = logging.getLogger(__name__)


def send_api_key_email(email: str, api_key: str, tier: str) -> bool:
    """Send API key to new customer. Returns True if sent, False on failure."""
    try:
        resend.Emails.send({
            "from": "no-reply@mothership-ai.com",
            "to": email,
            "subject": "Your Snip by NextEleven API Key",
            "html": f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Your Snip by NextEleven API Key</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333;">
  <h1 style="color: #3B82F6;">Welcome to Snip by NextEleven!</h1>
  
  <p>Your account has been created. Here's your login information:</p>
  
  <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
    <h2 style="margin-top: 0;">Login Dashboard</h2>
    <p><strong>URL:</strong> https://snip.mothership-ai.com</p>
    
    <div style="background: #e3f2fd; padding: 15px; border-radius: 6px; margin: 15px 0;">
      <strong>API Key:</strong><br>
      <code style="font-family: monospace; font-size: 16px; letter-spacing: 1px; background: white; padding: 10px; border-radius: 4px; display: block; word-break: break-all;">{api_key}</code>
      <small style="color: #666;">⚠️ Save this securely - it's shown only once!</small>
    </div>
  </div>
  
  <div style="background: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
    <h2>Next Steps</h2>
    <ol>
      <li><a href="https://snip.mothership-ai.com" style="color: #3B82F6;">Login to dashboard</a></li>
      <li>Customize branding and settings</li>
      <li>Copy your embed code</li>
      <li>Paste on your website</li>
    </ol>
  </div>
  
  <p style="margin-top: 30px; font-size: 14px; color: #666;">
    Need help? <a href="mailto:support@mothership-ai.com" style="color: #3B82F6;">Email support</a>
  </p>
  
  <hr style="margin: 40px 0;">
  <p style="font-size: 12px; color: #999; text-align: center;">
    © 2026 Snip by NextEleven
  </p>
</body>
</html>
            """
        })
        logger.info("API key email sent", extra={"email": email, "tier": tier})
        return True
    except Exception as e:
        logger.exception("Failed to send API key email to %s: %s", email, e)
        return False
