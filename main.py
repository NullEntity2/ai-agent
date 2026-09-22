import json
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
import argparse
import prompts
from call_function import available_functions, call_function

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
        {"role": "system", "content": prompts.system_prompt},
        {"role": "user", "content": prompt}
    ]

    for _ in range(20):
        has_more = generate_content(client, messages, args.verbose)
        if not has_more:
            break
    else:
        print("Error: Too many iterations")
        sys.exit(1)

def generate_content(client: OpenAI, messages: list, verbose: bool) -> bool:
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        tools=available_functions,
        temperature=0,
    )

    if not response.usage:
        raise RuntimeError("response is missing usage, failed API request?")
    
    if verbose:
        print(f"Prompt tokens: {response.usage.prompt_tokens}")
        print(f"Response tokens: {response.usage.completion_tokens}")

    message = response.choices[0].message
    messages.append(message)
    if not message.tool_calls:
        print("Response:")
        print(message.content)
        return False
    
    for tool_call in message.tool_calls: # type: ignore tool_calls is not None
        if tool_call.type != "function":
            continue
        result = call_function(tool_call, verbose)
        if not result.get("content"):
            raise RuntimeError(f"Empty function response for {tool_call.function.name}")

        messages.append(result)
        if verbose:
            print(f"-> {result['content']}")
    return True

if __name__ == "__main__":
    main()