import google.generativeai as genai
import os
from dotenv import load_dotenv


def main():
    load_dotenv()

    print("Hello from hello-gemini!")

    # Configure the Gemini API with your API key
    # It's recommended to store your API key securely, e.g., in an environment variable.
    # For this example, we'll use a placeholder. Replace 'YOUR_API_KEY' with your actual key.
    # You can get an API key from Google AI Studio: https://aistudio.google.com/app/apikey
    # Replace with your actual API key or set as environment variable
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)

    # List available models
    print("\nAvailable Gemini models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"  - {m.name}")

    # Initialize the Gemini model (replace 'gemini-pro' with an available model name from the list above)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # Example: Generate content
    prompt = "Write a short story about a robot who discovers art."
    print(f"\nGenerating content for prompt: '{prompt}'")

    try:
        response = model.generate_content(prompt)
        print("\nGenerated Story:")
        print(response.text)
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please ensure your API key is correct and you have network connectivity.")


if __name__ == "__main__":
    main()
