from mistralai import Mistral
import os
 
# --------------------------
# SET YOUR API KEY
# --------------------------
API_KEY = os.getenv("MISTRAL_API_KEY")  # or replace with "your-key-here"
MODEL = "mistral-large-latest"          # You can choose other models
 
client = Mistral(api_key='pljIOh9sB6iKrowFlb352pioad28YcVr')
 
print("🤖 Mistral Chatbot is running! Type 'exit' to quit.\n")
 
conversation_history = []
 
while True:
    user_input = input("You: ")
 
    if user_input.lower() in ["exit", "quit"]:
        print("Chatbot: Goodbye!")
        break
 
    # Add the user message to the history
    conversation_history.append({"role": "user", "content": user_input})
 
    # Call the Mistral API
    try:
        response = client.chat.complete(
            model=MODEL,
            messages=conversation_history
        )
 
        bot_reply = response.choices[0].message["content"]
        print(f"Chatbot: {bot_reply}")
 
        # Add reply to the conversation history
        conversation_history.append({"role": "assistant", "content": bot_reply})
 
    except Exception as e:
        print("⚠️ Error:", e)
