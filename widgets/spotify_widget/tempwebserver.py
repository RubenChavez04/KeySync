from flask import Flask, request

app = Flask(__name__)

@app.route('/callback')
def callback():
    # Extract the authorization from request
    auth_code = request.args.get('code')
    if auth_code:
        print(f"Authorization code received: {auth_code}")
        #Spotify successfully authenticated
        return "Authentication successful! You can close this tab."
    else:
        return "Authentication failed. No authorization code received."

if __name__ == '__main__':
    app.run(port=2266)
