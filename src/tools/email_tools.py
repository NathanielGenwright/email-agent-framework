"""Email tools that agents can use to interact with email systems."""

import imaplib
import email
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from bs4 import BeautifulSoup

from ..config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class EmailMessage:
    """Represents an email message with parsed content."""
    id: str
    subject: str
    sender: str
    recipients: List[str]
    body: str
    html_body: Optional[str]
    date: datetime
    labels: List[str]
    is_read: bool
    is_important: bool
    attachments: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "subject": self.subject,
            "sender": self.sender,
            "recipients": self.recipients,
            "body": self.body,
            "html_body": self.html_body,
            "date": self.date.isoformat(),
            "labels": self.labels,
            "is_read": self.is_read,
            "is_important": self.is_important,
            "attachments": self.attachments
        }


class EmailConnection:
    """Manages email connection and basic operations."""
    
    def __init__(self):
        self.imap_conn = None
        self.smtp_conn = None
        self.is_connected = False
    
    def connect(self) -> bool:
        """Establish connection to email server."""
        try:
            # IMAP connection for reading
            self.imap_conn = imaplib.IMAP4_SSL(settings.imap_server, settings.imap_port)
            self.imap_conn.login(settings.email_address, settings.email_password)
            
            # SMTP connection for sending (we'll set this up when needed)
            self.is_connected = True
            logger.info("Email connection established")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to email: {e}")
            return False
    
    def disconnect(self):
        """Close email connections."""
        if self.imap_conn:
            self.imap_conn.close()
            self.imap_conn.logout()
        if self.smtp_conn:
            self.smtp_conn.quit()
        self.is_connected = False
        logger.info("Email connection closed")
    
    def select_folder(self, folder: str = "INBOX") -> bool:
        """Select email folder."""
        if not self.is_connected:
            return False
        
        try:
            status, _ = self.imap_conn.select(folder)
            return status == 'OK'
        except Exception as e:
            logger.error(f"Failed to select folder {folder}: {e}")
            return False


class EmailTools:
    """Collection of email-related tools for agents."""
    
    def __init__(self):
        self.connection = EmailConnection()
    
    def fetch_recent_emails(self, limit: int = 20, folder: str = "INBOX") -> List[EmailMessage]:
        """
        Tool: Fetch recent emails from inbox.
        This is a core perception tool for email agents.
        """
        if not self.connection.connect():
            return []
        
        try:
            if not self.connection.select_folder(folder):
                return []
            
            # Search for recent emails
            status, messages = self.connection.imap_conn.search(None, 'ALL')
            if status != 'OK':
                return []
            
            email_ids = messages[0].split()
            
            # Get most recent emails
            recent_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            emails = []
            
            for email_id in reversed(recent_ids):  # Most recent first
                email_msg = self._fetch_email_by_id(email_id.decode())
                if email_msg:
                    emails.append(email_msg)
            
            logger.info(f"Fetched {len(emails)} recent emails")
            return emails
            
        except Exception as e:
            logger.error(f"Failed to fetch emails: {e}")
            return []
        finally:
            self.connection.disconnect()
    
    def search_emails(self, query: str, limit: int = 50) -> List[EmailMessage]:
        """
        Tool: Search emails by subject, sender, or content.
        """
        if not self.connection.connect():
            return []
        
        try:
            if not self.connection.select_folder():
                return []
            
            # Convert query to IMAP search format
            search_criteria = f'(OR SUBJECT "{query}" FROM "{query}")'
            status, messages = self.connection.imap_conn.search(None, search_criteria)
            
            if status != 'OK':
                return []
            
            email_ids = messages[0].split()
            recent_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            emails = []
            for email_id in reversed(recent_ids):
                email_msg = self._fetch_email_by_id(email_id.decode())
                if email_msg:
                    emails.append(email_msg)
            
            logger.info(f"Found {len(emails)} emails matching query: {query}")
            return emails
            
        except Exception as e:
            logger.error(f"Email search failed: {e}")
            return []
        finally:
            self.connection.disconnect()
    
    def mark_as_read(self, email_id: str) -> bool:
        """
        Tool: Mark email as read.
        """
        if not self.connection.connect():
            return False
        
        try:
            if not self.connection.select_folder():
                return False
            
            self.connection.imap_conn.store(email_id, '+FLAGS', '\\Seen')
            logger.info(f"Marked email {email_id} as read")
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark email as read: {e}")
            return False
        finally:
            self.connection.disconnect()
    
    def add_label(self, email_id: str, label: str) -> bool:
        """
        Tool: Add label to email (Gmail specific).
        """
        # This would be implemented for Gmail API
        # For now, we'll simulate the action
        logger.info(f"Would add label '{label}' to email {email_id}")
        return True
    
    def archive_email(self, email_id: str) -> bool:
        """
        Tool: Archive email.
        """
        # Implementation depends on email provider
        logger.info(f"Would archive email {email_id}")
        return True
    
    def send_email(self, to: List[str], subject: str, body: str, 
                   reply_to: Optional[str] = None) -> bool:
        """
        Tool: Send email or reply.
        """
        try:
            # Set up SMTP connection
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(settings.email_address, settings.email_password)
            
            msg = MIMEMultipart()
            msg['From'] = settings.email_address
            msg['To'] = ', '.join(to)
            msg['Subject'] = subject
            
            if reply_to:
                msg['In-Reply-To'] = reply_to
                msg['References'] = reply_to
            
            msg.attach(MIMEText(body, 'plain'))
            
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Sent email to {to} with subject: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def _fetch_email_by_id(self, email_id: str) -> Optional[EmailMessage]:
        """Helper method to fetch and parse a single email."""
        try:
            status, msg_data = self.connection.imap_conn.fetch(email_id, '(RFC822)')
            if status != 'OK':
                return None
            
            email_msg = email.message_from_bytes(msg_data[0][1])
            
            # Parse email components
            subject = email_msg.get('Subject', '')
            sender = email_msg.get('From', '')
            recipients = email_msg.get('To', '').split(',')
            date_str = email_msg.get('Date', '')
            
            # Parse date
            try:
                date = email.utils.parsedate_to_datetime(date_str)
            except:
                date = datetime.now()
            
            # Extract body
            body = ""
            html_body = None
            
            if email_msg.is_multipart():
                for part in email_msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif part.get_content_type() == "text/html":
                        html_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        # Extract text from HTML if no plain text
                        if not body:
                            soup = BeautifulSoup(html_body, 'html.parser')
                            body = soup.get_text()
            else:
                body = email_msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            return EmailMessage(
                id=email_id,
                subject=subject,
                sender=sender,
                recipients=[r.strip() for r in recipients],
                body=body.strip(),
                html_body=html_body,
                date=date,
                labels=[],  # Would be populated by Gmail API
                is_read=False,  # Would check flags
                is_important=False,  # Would check importance markers
                attachments=[]  # Would extract attachment info
            )
            
        except Exception as e:
            logger.error(f"Failed to parse email {email_id}: {e}")
            return None


# Create global email tools instance
email_tools = EmailTools()