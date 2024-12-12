from assistant import AIAssistant

def main():
    assistant = AIAssistant()
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
            
        response = assistant.get_response(user_input)
        print(f"\nAssistant: {response}")

if __name__ == "__main__":
    main() 