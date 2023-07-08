from __future__ import print_function

import os
from typing import List
from .models import Order
from django.conf import settings

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.message import EmailMessage
import tempfile

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://mail.google.com/']


class MailSender():
    def __init__(self):
        """Shows basic usage of the Gmail API.
            Lists the user's Gmail labels.
            """
        self.creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        token_file = os.path.join(settings.BASE_DIR, 'token.json')
        if os.path.exists(token_file):
            self.creds = Credentials.from_authorized_user_file(
                token_file, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.path.join(settings.BASE_DIR, 'credentials.json'), SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_file, 'w') as token:
                token.write(self.creds.to_json())

    def gmail_send_invoice(self,
                           to_addreses,
                           doc,
                           order: Order,
                           expenses=[]):
        """Create and send an email message
        Print the returned  message id
        Returns: Message object, including message id
        """

        try:
            service = build('gmail', 'v1', credentials=self.creds)
            message = EmailMessage()

            name = "client"
            if order.associated is not None:
                name = order.associated.name
            elif order.company is not None:
                name = order.company.name

            date = order.created_date
            if order.terminated_date is not None:
                date = order.terminated_date

            expenses_txt = ""
            if len(expenses) > 0:
                expenses_txt = "\nThe following third party expenses are included in your service:\n"
                for expense in expenses:
                    expenses_txt += F"  - {expense.concept}"
                    try:
                        expenses_txt += F" ({expense.image.url})"
                    except:
                        pass
                    expenses_txt += "\n"

            content_text = f'''
Dear {name},

This is an invoice for {order.concept} provided on {date.strftime('%d/%m/%Y')}. 
The total amount is ${order.amount:.2f}.

Please find the invoice details in the document attached to this mail.
{expenses_txt}
If you have any questions, please do not hesitate to contact us.

Thank you, 
TOWIT HOUSTON LLC
6011 Liberty Rd
Houston, TX 77026
(832) 963-5145 / (305) 833-6144
info@towithouston.com
            '''
            # print(content_text)
            # return
            message.set_content(content_text)

            message['To'] = to_addreses
            message['From'] = 'info@towithouston.com'
            message['Subject'] = f'Invoice for {order.concept}'

            # Attachment 9
            mime_type = "application"
            mime_subtype = "pdf"
            with tempfile.NamedTemporaryFile() as output:
                if settings.ENVIRONMENT == 'production':
                    from weasyprint import Document
                    output.write(doc)
                    output.flush()
                    with open(output.name, 'rb') as file:
                        message.add_attachment(file.read(),
                                               maintype=mime_type,
                                               subtype=mime_subtype,
                                               filename=F"invoice_towit_{order.id}.pdf")

            # encoded message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
                .decode()

            create_message = {
                'raw': encoded_message
            }
            # pylint: disable=E1101
            send_message = (service.users().messages().send
                            (userId="me", body=create_message).execute())
            print(F'Message Id: {send_message["id"]}')
        except HttpError as error:
            print(F'An error occurred: {error}')
            send_message = None
        return send_message
