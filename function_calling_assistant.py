import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from datetime import datetime

# Load environment variables
load_dotenv()

class FunctionCallingAssistant:
    def __init__(self, api_base_url: str = None):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.api_base_url = api_base_url or os.getenv('API_BASE_URL', 'http://localhost:8000')
        self.conversation_history = [
            {"role": "system", "content": "You are a helpful service desk assistant capable of using tools and functions. Greet the user by asking what the problem might be and then use the available tools to help the user. If the user has a problem, try to get a knowledge item from the knowledge base to help the user. If the users problem is not solved, create an incident and assign it to the user."}
        ]
        self.available_functions = self._get_available_functions()
        
    def _get_available_functions(self) -> Dict[str, callable]:
        """Define available functions that can be called by the assistant."""
        return {
            "create_incident": self._create_incident,
            "get_incidents": self._get_incidents,
            "get_knowledge_item": self._get_knowledge_item,
            "get_user_profile": self._get_user_profile,
            "get_all_knowledge_items": self._get_all_knowledge_items
        }
    
    def _get_tools_definition(self) -> List[Dict[str, Any]]:
        """Define the tools schema for the API."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_incident",
                    "description": "Create a new service desk incident",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "caller_name": {
                                "type": "string",
                                "description": "Name of the person reporting the incident"
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of the incident"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["High", "Medium", "Low"],
                                "description": "Priority level of the incident"
                            },
                            "category": {
                                "type": "string",
                                "description": "Category of the incident"
                            }
                        },
                        "required": ["caller_name", "description", "priority"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_incidents",
                    "description": "Get incidents by caller name",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "caller_name": {
                                "type": "string",
                                "description": "Name of the caller to filter incidents"
                            }
                        },
                        "required": ["caller_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_knowledge_item",
                    "description": "Get a knowledge base article",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "item_id": {
                                "type": "string",
                                "description": "ID of the knowledge base article"
                            }
                        },
                        "required": ["item_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_user_profile",
                    "description": "Get user profile information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "username": {
                                "type": "string",
                                "description": "Username to look up"
                            }
                        },
                        "required": ["username"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_all_knowledge_items",
                    "description": "Get a list of all available knowledge base articles",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]

    def _make_api_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make an API request to the local server."""
        url = f"{self.api_base_url}{endpoint}"
        print(f"Making {method} request to: {url}")  # Debug log
        
        try:
            if method.lower() == "get":
                response = requests.get(url, params=data)
            elif method.lower() == "post":
                response = requests.post(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            print(f"Response status code: {response.status_code}")  # Debug log
            
            if response.status_code == 404:
                return {"error": f"Endpoint not found: {endpoint}"}
                
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")  # Debug log
            return {"error": f"API request failed: {str(e)}"}

    def _create_incident(self, caller_name: str, description: str, priority: str, category: str = "General") -> str:
        """Create an incident through the API."""
        data = {
            "caller": {
                "dynamicName": caller_name
            },
            "priority": {
                "name": priority
            },
            "description": description,
            "category": category,
            "status": "Öppen",
            "urgency": priority,
            "impact": priority
        }
        response = self._make_api_request("POST", "/TOPDESK_POST/incidents", data)
        
        if "error" in response:
            return f"Failed to create incident: {response['error']}"
            
        return (f"Incident created successfully:\n"
                f"Caller: {response.get('callerName', 'N/A')}\n"
                f"Priority: {response.get('priorityName', 'N/A')}\n"
                f"Category: {response.get('category', 'N/A')}\n"
                f"Status: {response.get('status', 'N/A')}")

    def _get_incidents(self, caller_name: str) -> str:
        """Get incidents by caller name through the API."""
        response = self._make_api_request("GET", f"/TOPDESK_POST/incidents/name/{caller_name}")
        
        if "error" in response:
            return f"Failed to get incidents: {response['error']}"
            
        if isinstance(response, list):
            incidents = response
        else:
            incidents = []
            
        if not incidents:
            return f"No incidents found for {caller_name}"
            
        result = f"Found {len(incidents)} incidents for {caller_name}:\n"
        for incident in incidents:
            result += (f"Description: {incident.get('description', 'N/A')}\n"
                      f"Status: {incident.get('status', 'N/A')}\n"
                      f"Priority: {incident.get('priority', {}).get('name', 'N/A')}\n"
                      f"Category: {incident.get('category', 'N/A')}\n"
                      f"---\n")
        return result

    def _get_knowledge_item(self, item_id: str) -> str:
        """Get knowledge base article through the API."""
        response = self._make_api_request("GET", f"/knowledgeItems/{item_id}")
        
        if "error" in response:
            if "not found" in str(response['error']).lower():
                return f"Knowledge article {item_id} not found"
            return f"Failed to get knowledge item: {response['error']}"
            
        return (f"Knowledge Article {item_id}:\n"
                f"Title: {response.get('title', 'N/A')}\n"
                f"Content: {response.get('content', 'N/A')}")

    def _get_all_knowledge_items(self) -> str:
        """Get all knowledge base articles through the API."""
        response = self._make_api_request("GET", "/knowledgeItems")
        
        if "error" in response:
            if "not found" in str(response['error']).lower():
                return "No knowledge base articles found"
            return f"Failed to get knowledge items: {response['error']}"
            
        if isinstance(response, list):
            knowledge_items = response
        else:
            knowledge_items = []
            
        if not knowledge_items:
            return "No knowledge base articles found"
            
        result = "Available Knowledge Base Articles:\n"
        for item in knowledge_items:
            result += f"ID: {item.get('id', 'N/A')} - Title: {item.get('title', 'N/A')}\n"
        return result

    def _get_user_profile(self, username: str) -> str:
        """Get user profile through the API."""
        response = self._make_api_request("GET", "/v1.0/users")
        
        if "error" in response:
            return f"Failed to get user profile: {response['error']}"
            
        if isinstance(response, list):
            users = response
        else:
            users = []
            
        user = next((u for u in users if u.get('displayName') == username), None)
        
        if not user:
            return f"User profile not found for username: {username}"
            
        return (f"User Profile for {username}:\n"
                f"Display Name: {user.get('displayName', 'N/A')}\n"
                f"User Principal Name: {user.get('userPrincipalName', 'N/A')}\n"
                f"Last Sign In: {user.get('signInActivity', {}).get('lastSignInDateTime', 'N/A')}\n"
                f"Risk Level: {user.get('signInActivity', {}).get('riskLevelAggregated', 'N/A')}")

    def _handle_tool_call(self, tool_call) -> Optional[str]:
        """Handle the execution of called functions."""
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        if function_name not in self.available_functions:
            return f"Function {function_name} not found"
        
        function_to_call = self.available_functions[function_name]
        return function_to_call(**function_args)

    def get_response(self, prompt: str) -> str:
        try:
            # Add user's message to conversation history
            self.conversation_history.append({"role": "user", "content": prompt})
            
            # Make the API call with tools definition
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=self.conversation_history,
                tools=self._get_tools_definition(),
                tool_choice="auto",
                temperature=0.7,
                max_tokens=1000
            )
            
            response_message = response.choices[0].message
            
            # Check if the model wants to call a tool
            if response_message.tool_calls:
                # Handle each tool call
                for tool_call in response_message.tool_calls:
                    function_response = self._handle_tool_call(tool_call)
                    
                    # Add the tool call and its response to the conversation
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tool_call]
                    })
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": function_response
                    })
                
                # Get a new response from the model that includes the function results
                second_response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=self.conversation_history,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                final_response = second_response.choices[0].message.content
            else:
                final_response = response_message.content
            
            # Add the final response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": final_response
            })
            
            return final_response
            
        except Exception as e:
            return f"An error occurred: {str(e)}"

def main():
    assistant = FunctionCallingAssistant()
    response = assistant.get_response("Hello!")
    print(f"\nFunction Calling Assistant: {response}")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
            
        response = assistant.get_response(user_input)
        print(f"\nFunction Calling Assistant: {response}")

if __name__ == "__main__":
    main() 