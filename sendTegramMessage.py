import requests

# Replace 'your_bot_token' with your bot's token
bot_token = '6867104517:AAHaY84LQ4tZKVUvXP133NP6KJNxIGQe6qw'

# Replace 'your_chat_id' with the chat ID or the recipient's user ID
chat_id = '420134022'

# The message you want to send
message = "Hello from Python!"

# Telegram API URL for sending messages
url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

# Parameters for the API request
params = {
    'chat_id': chat_id,
    'text': message
}

# Send the message
response = requests.get(url, params=params)

# Check if the message was sent successfully
if response.status_code == 200:
    print("Message sent successfully!")
else:
    print("Failed to send message.")
