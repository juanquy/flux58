#!/usr/bin/env python3
import os
from flask import Flask, session, request, jsonify

app = Flask(__name__)
app.secret_key = 'testing123'

@app.route('/')
def index():
    if 'user_id' in session:
        return f"""
        <html>
        <body>
            <h1>Session Test Page</h1>
            <p>You are logged in!</p>
            <p>User ID: {session.get('user_id')}</p>
            <p>Username: {session.get('username')}</p>
            <p>Role: {session.get('role')}</p>
            <p>Your IP address: {request.remote_addr}</p>
            <p>Your session: {str(session)}</p>
        </body>
        </html>
        """
    else:
        return """
        <html>
        <body>
            <h1>Session Test Page</h1>
            <p>You are NOT logged in.</p>
            <p>Your IP address: {}</p>
        </body>
        </html>
        """.format(request.remote_addr)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)