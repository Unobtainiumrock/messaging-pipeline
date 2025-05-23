"""Test OpenAI API credentials."""

import os
import openai
import sys
import pytest
from openai import OpenAI
from colorama import Fore, Style


def test_openai_credentials():
    """Test OpenAI API key and connectivity."""
    print("\n============================================================")
    print("TESTING OPENAI CREDENTIALS")
    print("============================================================")

    # Check if API key exists
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print(f"- API Key: {Fore.RED}✗ Not found{Style.RESET_ALL}")
        print(f"\n{Fore.RED}❌ ERROR: OpenAI API key not found in environment variables.{Style.RESET_ALL}")
        print("Please add your OpenAI API key to the .env file as OPENAI_API_KEY.")
        pytest.skip("OpenAI API key not found in environment variables")

    print(f"- API Key: {Fore.GREEN}✓ Found{Style.RESET_ALL}")

    # Test the API connection with a simple completion request
    try:
        client = OpenAI(api_key=api_key)

        print("\nTesting OpenAI API connection...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, OpenAI!"},
            ],
            max_tokens=10,
        )

        # If we get here, the API call was successful
        print(f"{Fore.GREEN}✅ OpenAI API connection successful!{Style.RESET_ALL}")
        print(f"  Model: {response.model}")
        print(f"  Response: {response.choices[0].message.content}")

    except openai.APIError as e:
        print(f"{Fore.RED}❌ OpenAI API Error: {e}{Style.RESET_ALL}")
        print("\nTroubleshooting tips:")
        print("1. Verify your API key in the .env file")
        print("2. Check if your OpenAI account has sufficient credit")
        print("3. Make sure you're using a valid model name")
        pytest.fail(f"OpenAI API Error: {e}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error connecting to OpenAI API: {e}{Style.RESET_ALL}")
        pytest.fail(f"Error connecting to OpenAI API: {e}")


def run_test() -> bool:
    """Run the test and return boolean result for command line usage."""
    try:
        test_openai_credentials()
        return True
    except pytest.skip.Exception:
        return False
    except Exception:
        return False


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
