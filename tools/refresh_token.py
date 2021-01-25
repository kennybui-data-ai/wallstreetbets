"""This example demonstrates the flow for retrieving a refresh token.

In order for this example to work your application's redirect URI must be set to
http://localhost:8080.

This tool can be used to conveniently create refresh tokens for later use with your web
application OAuth2 credentials.

"""
import random
import socket
import sys
import json

import praw


def receive_connection():
    """Wait for and then return a connected socket..

    Opens a TCP connection on port 8080, and waits for a single client.

    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 8080))
    server.listen(1)
    client = server.accept()[0]
    server.close()
    return client


def send_message(client, message):
    """Send message to client and close the connection."""
    print(message)
    client.send(f"HTTP/1.1 200 OK\r\n\r\n{message}".encode("utf-8"))
    client.close()


def main(credentials_path):
    """Provide the program's entry point when directly executed."""
    # print(
    #     "Go here while logged into the account you want to create a token for: "
    #     "https://www.reddit.com/prefs/apps/"
    # )
    # print(
    #     "Click the create an app button. Put something in the name field and select the"
    #     " script radio button."
    # )
    # print("Put http://localhost:8080 in the redirect uri field and click create app")
    # client_id = input(
    #     "Enter the client ID, it's the line just under Personal use script at the top: "
    # )
    # client_secret = input("Enter the client secret, it's the line next to secret: ")
    # commaScopes = input(
    #     "Now enter a comma separated list of scopes, or all for all tokens: "
    # )

    # if commaScopes.lower() == "all":
    #     scopes = ["*"]
    # else:
    #     scopes = commaScopes.strip().split(",")

    with open(credentials_path, "r") as f:
        credentials = json.loads(f.read())

    # scopes = ["identity"]
    scopes = credentials["scopes"]

    reddit = praw.Reddit(client_id=credentials["client_id"],
                         client_secret=credentials["client_secret"],
                         redirect_uri=credentials["redirect_uri"],
                         user_agent=credentials["user_agent"]
                         )
    state = str(random.randint(0, 65000))
    url = reddit.auth.url(scopes, state, "permanent")
    print(f"Open this url in your browser: {url}")
    sys.stdout.flush()

    client = receive_connection()
    data = client.recv(1024).decode("utf-8")
    param_tokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
    params = {
        key: value for (key, value) in [token.split("=") for token in param_tokens]
    }

    if state != params["state"]:
        send_message(
            client,
            f"State mismatch. Expected: {state} Received: {params['state']}",
        )
        return 1
    elif "error" in params:
        send_message(client, params["error"])
        return 1

    refresh_token = reddit.auth.authorize(params["code"])
    credentials["refresh_token"] = refresh_token

    send_message(client, f"Refresh token: {refresh_token}")

    with open(credentials_path, "w") as f:
        f.write(json.dumps(credentials, indent=4))

    # check scopes
    reddit = praw.Reddit(client_id=credentials["client_id"],
                         client_secret=credentials["client_secret"],
                         refresh_token=credentials["refresh_token"],
                         user_agent=credentials["user_agent"]
                         )
    print(reddit.auth.scopes())

    return 0


if __name__ == "__main__":
    credentials_path = "../wsb/credentials.json"
    sys.exit(main(credentials_path))
