import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@example.com")
        self.app_name = os.getenv("APP_NAME", "StockX Clone")

    def send_email(self, to_email: str, subject: str, body_html: str, body_text: Optional[str] = None) -> bool:
        """Send an email"""
        if not body_text:
            body_text = body_html  # Use HTML as fallback text if not provided
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.app_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Attach parts
            part1 = MIMEText(body_text, "plain")
            part2 = MIMEText(body_html, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.from_email, to_email, message.as_string())
            
            logger.info(f"Email sent to {to_email}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    def send_password_reset(self, to_email: str, reset_link: str) -> bool:
        """Send a password reset email"""
        subject = f"Reset Your {self.app_name} Password"
        
        html_content = f"""
        <html>
        <body>
            <h2>Reset Your Password</h2>
            <p>You've requested to reset your password. Click the link below to set a new password:</p>
            <p><a href="{reset_link}">Reset Password</a></p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't request this reset, you can ignore this email.</p>
            <p>Thank you,<br>{self.app_name} Team</p>
        </body>
        </html>
        """
        
        text_content = f"""
        Reset Your Password
        
        You've requested to reset your password. Use the link below to set a new password:
        
        {reset_link}
        
        This link will expire in 24 hours.
        
        If you didn't request this reset, you can ignore this email.
        
        Thank you,
        {self.app_name} Team
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_welcome_email(self, to_email: str, name: str) -> bool:
        """Send a welcome email to a new user"""
        subject = f"Welcome to {self.app_name}!"
        
        html_content = f"""
        <html>
        <body>
            <h2>Welcome to {self.app_name}, {name}!</h2>
            <p>Thank you for creating an account with us. We're excited to have you on board!</p>
            <p>You can now log in to your account and start exploring our marketplace.</p>
            <p>Best regards,<br>{self.app_name} Team</p>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to {self.app_name}, {name}!
        
        Thank you for creating an account with us. We're excited to have you on board!
        
        You can now log in to your account and start exploring our marketplace.
        
        Best regards,
        {self.app_name} Team
        """
        
        return self.send_email(to_email, subject, html_content, text_content)