import os
from slack_bolt.adapter.flask import SlackRequestHandler  # Connect Slack Bolt with Flask
from slack_bolt import App  # Core Slack app framework for handling events and interactions
from dotenv import find_dotenv, load_dotenv  # For loading environment variables from .env file
from flask import Flask, request  # Flask framework for handling HTTP requests
from openai import OpenAI
from functions import summarize_text, draft_email, sentiment, therapy, generate_image  # Custom functions for summarization and email drafting

# Load environment variables from .env file
# These variables include sensitive credentials like the Slack bot token and signing secret.
load_dotenv(find_dotenv())

# Set Slack API credentials from environment variables
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_BOT_USER_ID = os.environ["SLACK_BOT_USER_ID"]

# Initialize the Slack app with the bot token
# This manages events, commands, and interactions within Slack
# This should be more secure with the signing secret required.
app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)

# Initialize the Flask app for handling HTTP requests
flask_app = Flask(__name__)

# Create a SlackRequestHandler to connect the Slack app with Flask
handler = SlackRequestHandler(app)

# Create OpenAI client for image generation
client = OpenAI()

@app.event("app_mention")
def handle_mentions(body, say):
    """
    Event listener for mentions in Slack.
    When the bot is mentioned, it processes the user's message to determine the intent
    and calls the appropriate function to generate a response.

    Args:
        body (dict): The event data received from Slack, including the message text.
        say (callable): A function for sending responses back to the Slack channel.
    """
    # Extract text and remove the bot's mention
    mention = f"<@{SLACK_BOT_USER_ID}>"
    text = body["event"]["text"].replace(mention, "").strip()
    # Extract the channel
    channel = body["event"]["channel"]

    # Determine the intent based on keywords in the message
    if any(x in text.lower() for x in ["email:", "draft:", "respond:"]): # If the message relates to email drafting
        response = draft_email(text)  # Call the email drafting function
    elif any(x in text.lower() for x in ["outline:", "summary:", "summarize:"]):  # If the message relates to summarization
        response = summarize_text(text)  # Call the text summarization function
    elif any(x in text.lower() for x in ["sentiment:", "attitude:", "urgency:"]):  # If the message relates to sentiment/urgency
        response = sentiment(text)  # Call the text sentiment function
    elif any(x in text.lower() for x in ["therapy:", "feeling:", "help:"]):  # If the message relates to "therapy"
        response = therapy(text)  # Call the text "therapy" function
    elif any(x in text.lower() for x in ["image:", "picture:", "generate:"]):  # If the message relates to image generation
        img_buf = generate_image(text, client)

        # Upload to Slack
        app.client.files_upload_v2(
            file=img_buf,
            filename=img_buf.name,
            channel=channel,
            initial_comment="Here’s the image you asked for!"
        )
        return
    else:
        # Default response if intent is unclear
        response = (
            "I couldn't figure out what you need. Try mentioning:\n"
            "- 'email:', 'draft:', or 'respond:' for email generation.\n"
            "- 'outline:', 'summary:', or 'summarize:' for text summaries.\n"
            "- 'sentiment:', 'attitude:', or 'urgency:' for sentiment and urgency analysis.\n"
            "- 'therapy:', 'feeling:', or 'help:' for on-the-spot therapy.\n"
            "- 'image:', 'picture:', or 'generate:' for image generation.\n"
            "Don't forget the colon! ( : )"
        )

    # Send the generated response back to the Slack channel
    say(response)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    """
    Route for handling Slack events.
    Slack sends HTTP POST requests to this endpoint when events (e.g., mentions) occur.

    Returns:
        Response: The result of handling the request, as processed by SlackRequestHandler.
    """
    return handler.handle(request)

# Start the Flask app when the script is executed
if __name__ == "__main__":
    flask_app.run()