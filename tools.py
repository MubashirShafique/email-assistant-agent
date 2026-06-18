from gmail_auth import get_smtp_connection, get_imap_connection, EMAIL_USER
from email.mime.text import MIMEText
import email
from email.policy import default
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from pydantic import Field,BaseModel


load_dotenv()




def read_unread_emails():
    """Tool to read all unread emails from the inbox and return their content as objects."""
    # Get authenticated IMAP connection
    mail = get_imap_connection()
    
    if not mail:
        return "Failed to authenticate or connect to IMAP server."
        
    try:
       
        mail.select("inbox", readonly=False)
        
        # Search for all UNREAD emails
        status, data = mail.search(None, "UNSEEN")
        mail_ids = data[0].split()
        
        if not mail_ids:
            mail.logout()
            return [] # Return empty list if no unread emails
            
        unread_emails_list = []
        
        # Loop through all unread email IDs
        for mail_id in mail_ids:
            status, data = mail.fetch(mail_id, "(RFC822)")
            raw_email = data[0][1]
            
            
            msg = email.message_from_bytes(raw_email, policy=default)
            
            
            subject = msg["Subject"]
            sender = msg["From"]
            
           
            body_content = ""
            if msg.is_multipart():
                
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body_content = part.get_content().strip()
                        break
            else:
              
                body_content = msg.get_content().strip()
            
            # Creating a clean object for each email
            email_object = {
                "email_id": mail_id.decode('utf-8'),
                "from": sender,
                "subject": subject,
                "content": body_content
            }
            unread_emails_list.append(email_object)
            
        # Close connection
        mail.logout() 
        
        # Returns the list of clean email objects
        return unread_emails_list
        
    except Exception as e:
        return f"Error while reading emails: {e}"
    




def send_email(to_email, subject, body):
    """Tool to send an email to someone."""
    # Get authenticated SMTP connection
    server = get_smtp_connection()
    
    if not server:
        return "Failed to authenticate or connect to SMTP server."
        
    try:
        # Prepare the email structure
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        
        # Send the email
        server.sendmail(EMAIL_USER, to_email, msg.as_string())
        server.quit() 
        return f"Email successfully sent to {to_email}!"
        
    except Exception as e:
        return f"Error while sending email: {e}"
    




# Load the OpenAI model name from environment variables
OPENAI_MODEL = os.getenv('OPENAI_MODEL','gpt-4o-mini')

# Define Pydantic schema for structured output
class EmailSchema(BaseModel):
    subject: str = Field(description="Appropriate subject for the reply email")
    body: str = Field(description="The actual content/body of the reply email")

# Configure the model to return structured output matching the schema
structured_model = ChatOpenAI(model=OPENAI_MODEL).with_structured_output(EmailSchema)

def write_email_reply(incoming_subject: str, incoming_body: str) -> dict:
    """Invokes the AI model to generate a professional reply based on the incoming email's subject and body."""
    try:
        # Create a prompt for the model to generate a reply
        prompt = f"""
        You are an AI assistant. Analyze the following incoming email and write a reply.
        
        Incoming Email Subject: {incoming_subject}
        Incoming Email Body: {incoming_body}
        
        Generate a new appropriate subject line for the reply (e.g., adding 'Re:') and draft the complete reply body.
        """
        
        # Invoke the model with the prompt
        ai_response = structured_model.invoke(prompt)
        
        # Return the structured data as a clean dictionary
        return {
            "subject": ai_response.subject,
            "body": ai_response.body
        }
    except Exception as e:
        return {"error": f"Error while generating email reply: {e}"}



