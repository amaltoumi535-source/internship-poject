"""Email service for sending verification codes via SendGrid."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import random
import string
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.sendgrid.net")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER", "apikey")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("SMTP_FROM_EMAIL", "noreply@sendgrid.net")
    
    def generate_code(self) -> str:
        """Generate 6-digit verification code."""
        return "".join(random.choices(string.digits, k=6))
    
    def send_verification_email(self, email: str, verify_url: str) -> bool:
        """Send an email verification link via SMTP."""
        if not self.smtp_password:
            logger.error("SMTP_PASSWORD not configured")
            return False
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Verify Your IT-Gate Account"
            msg["From"] = self.from_email
            msg["To"] = email
            
            html = f"""
            <html>
              <head></head>
              <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                  <h2 style="color: #333; text-align: center; margin-bottom: 20px;">Verify your account</h2>
                  <p style="color: #666; font-size: 16px; text-align: center;">Click the button below to verify your email and activate your account.</p>
                  <div style="text-align: center; margin: 30px 0;">
                    <a href="{verify_url}" style="background: #4f46e5; color: white; padding: 14px 32px; border-radius: 10px; text-decoration: none; font-weight: bold; font-size: 16px; display: inline-block;">Verify my email</a>
                  </div>
                  <p style="color: #999; font-size: 13px; text-align: center;">This link expires in 10 minutes.</p>
                  <p style="color: #999; font-size: 13px; text-align: center; margin-top: 30px;">If you didn't request this, ignore this email.</p>
                </div>
              </body>
            </html>
            """
            
            part = MIMEText(html, "html")
            msg.attach(part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Verification email sent to {email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {email}: {str(e)}")
            return False

    def send_password_reset_email(self, email: str, code: str) -> bool:
        """Send password reset code email via SMTP."""
        if not self.smtp_password:
            logger.error("SMTP_PASSWORD not configured")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Reset Your IT-Gate Password"
            msg["From"] = self.from_email
            msg["To"] = email

            html = f"""
            <html>
              <head></head>
              <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                  <h2 style="color: #333; text-align: center; margin-bottom: 20px;">Reset your password</h2>
                  <p style="color: #666; font-size: 16px; text-align: center;">Your password reset code is:</p>
                  <h1 style="color: #007bff; font-size: 48px; text-align: center; letter-spacing: 5px; margin: 30px 0; font-weight: bold;">{code}</h1>
                  <p style="color: #999; font-size: 14px; text-align: center;">This code expires in 10 minutes.</p>
                  <p style="color: #999; font-size: 14px; text-align: center; margin-top: 30px;">If you didn't request this, ignore this email — your password will stay the same.</p>
                </div>
              </body>
            </html>
            """

            part = MIMEText(html, "html")
            msg.attach(part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Password reset email sent to {email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send reset email to {email}: {str(e)}")
            return False


email_service = EmailService()