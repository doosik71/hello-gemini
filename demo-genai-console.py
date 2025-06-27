import google.generativeai as genai
import os
from dotenv import load_dotenv


def list_available_models():
    """Lists the available Gemini models that support content generation."""

    print("\nAvailable Gemini models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"  - {m.name}")


def main():
    """Main function to run the console-based Gemini chatbot."""

    load_dotenv()

    print("Hello from hello-gemini!")

    # Configure the Gemini API with your API key
    # It's recommended to store your API key securely, e.g., in an environment variable.
    # For this example, we'll use a placeholder. Replace 'YOUR_API_KEY' with your actual key.
    # You can get an API key from Google AI Studio: https://aistudio.google.com/app/apikey
    # Replace with your actual API key or set as environment variable
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)

    # list_available_models()

    # Initialize the Gemini model (replace 'gemini-pro' with an available model name from the list above)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # Start a chat session
    chat = model.start_chat(history=[])

    print("\nStart chatting with Gemini! Type 'exit' or 'quit' to end the conversation.")

    while True:
        user_input = input("👤 ( User ): ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting chat. Goodbye!")
            break

        try:
            response = chat.send_message(user_input, stream=True)
            print("🤖 (Gemini): ", end="")
            for chunk in response:
                print(chunk.text, end="")
            print() # Newline after the full response
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print(
                "Please ensure your API key is correct and you have network connectivity.")
            print("You can try again or type 'exit' to quit.")


if __name__ == "__main__":
    main()
