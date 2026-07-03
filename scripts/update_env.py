import os
import re

def validate_env_file(env_path=".env"):
    if not os.path.exists(env_path):
        return

    with open(env_path, "r") as f:
        content = f.read()

    # Check if Google config exists
    if "GOOGLE_CLIENT_ID" not in content:
        google_config = """
# Google OAuth Configuration
# Ensure these match the values in your Google Cloud Console
# Authorized JavaScript Origins MUST include your frontend origin (e.g. http://localhost:8000)
# Authorized Redirect URIs MUST include your callback URI if using redirect mode (e.g. http://localhost:8000/api/v1/auth/google/callback)
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000
"""
        with open(env_path, "a") as f:
            f.write(google_config)
        print("Appended Google OAuth configuration to .env file.")

if __name__ == "__main__":
    validate_env_file()
