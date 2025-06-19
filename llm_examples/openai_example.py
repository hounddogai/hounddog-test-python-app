import os
import sys
from pathlib import Path
from openai import AsyncOpenAI

# Add the parent directory to the path so we can import the database module
sys.path.append(str(Path(__file__).parent.parent))
from database import get_database, close_database

openai_api_key = os.environ.get("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=openai_api_key)

PROMPT_TEMPLATE = """
User information:
{{var1}} 
{{var2}}
{{var3}}
"""


def get_username():
    """Get a random username from the test database."""
    try:
        db = get_database()
        user = db.get_random_user()
        if user:
            return user["username"]
        else:
            # Fallback if no users found
            print("Warning: No users found in database, using fallback")
            return "fallback_user"
    except Exception as e:
        print(f"Error getting username from database: {e}")
        # Fallback to hardcoded value if database fails
        return "johnsmith"


def get_ip_address():
    """Get a random IP address from the test database."""
    try:
        db = get_database()
        ip = db.get_random_ip()
        if ip:
            return ip["ip_address"]
        else:
            # Fallback if no IPs found
            print("Warning: No IP addresses found in database, using fallback")
            return "127.0.0.1"
    except Exception as e:
        print(f"Error getting IP address from database: {e}")
        # Fallback to hardcoded value if database fails
        return "192.168.1.1"


def get_full_name():
    """Get a random user's full name from the test database."""
    try:
        db = get_database()
        user = db.get_random_user()
        if user and user.get("email"):
            # Extract name from email (simple approach)
            email_name = user["email"].split("@")[0]
            # Convert email format to proper name (e.g., john.smith -> John Smith)
            name_parts = email_name.replace(".", " ").split()
            full_name = " ".join(word.capitalize() for word in name_parts)
            return full_name
        elif user:
            # Fallback to username if email not available
            return user["username"].capitalize()
        else:
            # Fallback if no users found
            print("Warning: No users found in database, using fallback")
            return "Fallback User"
    except Exception as e:
        print(f"Error getting full name from database: {e}")
        # Fallback to hardcoded value if database fails
        return "John Smith"


async def main() -> None:
    try:
        # Get user data from database
        var1 = get_username()
        var2 = get_ip_address()
        var3 = get_full_name()

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": PROMPT_TEMPLATE.format(var1=var1, var2=var2, var3=var3),
                }
            ],
            max_tokens=1000,
        )
        print(f"OpenAI Response: {response.choices[0].message.content}")

    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        close_database()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
