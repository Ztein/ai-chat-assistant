import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIAssistant:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.conversation_history = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        
    def get_response(self, prompt):
        try:
            # Add user's message to conversation history
            self.conversation_history.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=self.conversation_history,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Add assistant's response to conversation history
            assistant_message = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
        except Exception as e:
            return f"An error occurred: {str(e)}" 