import logging
from livekit.agents import function_tool, RunContext
import requests
from langchain_community.tools import DuckDuckGoSearchRun

# --- Missing Imports for Email ---
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# ---------------------------------

@function_tool()
async def get_weather(
    context: RunContext,
    city: str) -> str:
    """Get the current weather for a given city using wttr.in API."""
    try:
        response = requests.get(f"https://wttr.in/{city}?format=3")
        if response.status_code == 200:
            logging.info(f"Weather for {city}: {response.text.strip()}")
            return response.text.strip()
        else:
            logging.error(f"Failed to fetch weather for {city}: {response.status_code}")
            return f"Could not retrieve weather data for {city}."
    except Exception as e:
        logging.error(f"Error fetching weather for {city}: {e}")
        return f"An error occurred while fetching the weather {city}."
    
@function_tool()
async def web_search(
    context: RunContext,
    query: str) -> str:
    """Perform a web search using DuckDuckGo."""
    try:
        results = DuckDuckGoSearchRun().run(tool_input=query)
        logging.info(f"Search results for '{query}': {results}")
        return results
    except Exception as e:
        logging.error(f"Error performing web search for '{query}': {e}")
        return f"An error occurred while performing the web search for '{query}'."

@function_tool()
async def send_email(
    context: RunContext,
    to_email: str,
    subject: str,
    message: str,
    cc_email: str = None, # Added cc_email with a default value
) -> str:
    """Simulate sending an email."""
    try:
        #Gmail SMTP Config
        smtp_server="smtp.gmail.com" # Corrected typo: gamil -> gmail
        smtp_port=587
        
        #Get credentials from environment variables or secure vault
        gmail_user=os.getenv("GMAIL_USER")
        gmail_password=os.getenv("GMAIL_PASSWORD")

        if not gmail_user or not gmail_password:
            logging.error("Gmail credentials are not set in environment variables.")
            return "Email sending failed due to missing credentials."
        
        #Create message
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to_email            
        msg['Subject'] = subject

        #Add cc if provided
        recipients = [to_email]
        if cc_email:
            msg['Cc'] = cc_email
            recipients.append(cc_email)

        #Attach message body
        msg.attach(MIMEText(message, 'plain'))

        #connect to Gmail SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(gmail_user, gmail_password)

        #send email
        text = msg.as_string() # Corrected typo: masg -> msg
        server.sendmail(gmail_user, recipients, text)
        server.quit()

        logging.info(f"Email sent successfully to {to_email}")
        return f"Email sent successfully to {to_email}"
    except smtplib.SMTPAuthenticationError:
        logging.error("Gmail authentication failed. Check your username and password or App Password.")
        return "Email sending failed due to authentication error. Ensure you use an App Password if 2FA is enabled."
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
        return f"Email sending failed: SMTP error - {str(e)}"
    except Exception as e:
        logging.error(f"An error occurred while sending email: {e}")
        return f"Email sending failed: {str(e)}"