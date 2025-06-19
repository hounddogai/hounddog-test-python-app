import os

from anthropic import Anthropic as Client

api_key = os.environ.get("ANTHROPIC_API_KEY")

if __name__ == "__main__":
    # Here are some example variables handling sensitive data.
    email = "test@example.com"
    phone = "123-456-7890"
    ssn = "123-45-6789"

    # We track the dataflow (e.g., variable assignment, string interpolation, nested data structures)
    alias1 = email
    alias2 = phone
    alias3 = ssn
    prompt = f"User information: {alias1}, {alias2}, {alias3}"
    messages = [{"role": "user", "content": prompt}]

    response = Client(api_key=api_key).messages.create(
        max_tokens=1024,
        messages=messages,
        model="claude-3-5-sonnet-latest",
    )
    print(response.content)
