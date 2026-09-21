import os
from dotenv import load_dotenv
from openai import OpenAI
import argparse

def main() -> None:
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY must be set in .env")


    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    prompt = str(args.user_prompt)
    if args.verbose:
        print(f"User prompt: {prompt}")
    messages = [
        {"role": "user", "content": prompt}
    ]
    generate_content(client, messages, args.verbose)

def generate_content(client: OpenAI, messages: list, verbose: bool):
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
    )

    if response.usage is None:
        raise RuntimeError("response is missing usage, failed API request?")

    if verbose:
        print(f"Prompt tokens: {response.usage.prompt_tokens}")
        print(f"Response tokens: {response.usage.completion_tokens}")
    print(f"Response: {response.choices[0].message.content}")

if __name__ == "__main__":
    main()