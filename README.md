# slack-chatbot
Slack bot that tunnels via ngrok, listens to commands, and returns AI-generated content.<br/>
<br/>
Obtain a ngrok, slack, and openai account.<br/>
Create Slack app.   [Slack](https://api.slack.com/quickstart)<br/>
Install ngrok.      [ngrok](https://ngrok.com/docs/getting-started/)<br/>
Access OpenAI API.  [OpenAI](https://openai.com/api/)<br/>
<br/>
Obtain the keys outlined in the .env and paste and save them in their places.<br/>
Expose port 5000 to ngrok with command 'ngrok http 5000' (Flask uses port 5000 by default).<br/>
Write the ngrok address obtained above to the Slack events URL (under event subscriptions in the Slack API).<br/>
For Example: ht<span>tps://example.ngrok-free.app/slack/events<br/>
<br/>
Install the appropriate packages to your virtual environment as outlined in requirements.txt.<br/>
Run the main file.<br/>
Test the bot by @-ing it in your slack channel.  It should respond with a list of commands you can use.<br/>
