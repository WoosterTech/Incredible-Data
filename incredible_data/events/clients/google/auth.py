from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


def get_credentials(scopes: list[str]) -> Credentials:
    """Get credentials for the Google API.

    Args:
        scopes: The scopes of the credentials.

    Returns:
        The credentials.
    """

    # If modifying these scopes, delete the file token.json.
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_path = Path("token.json")
    if token_path.exists():
        creds = Credentials.from_authorized_user_file("token.json", scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with token_path.open("w") as token:
            token.write(creds.to_json())

    return creds
