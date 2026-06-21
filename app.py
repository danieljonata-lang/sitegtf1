from flask import Flask, render_template, jsonify, request
import json
from urllib.request import Request, urlopen
from urllib.error import URLError

app = Flask(__name__)

FIREBASE_URL = 'https://gtf1-4f4be-default-rtdb.firebaseio.com'

def firebase_get(path):
    try:
        req = Request(f'{FIREBASE_URL}/{path}.json')
        with urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode())
    except (URLError, json.JSONDecodeError):
        return None

def firebase_patch(path, data):
    try:
        body = json.dumps(data).encode()
        req = Request(f'{FIREBASE_URL}/{path}.json', data=body, method='PATCH')
        req.add_header('Content-Type', 'application/json')
        with urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode())
    except (URLError, json.JSONDecodeError):
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/contadores')
def contadores():
    d = firebase_get('contadores') or {}
    return jsonify({
        "visitantes": d.get("visitantes", 0),
        "vip": d.get("vip", 0)
    })

@app.route('/visita', methods=['POST'])
def visita():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    ip = ip.split(',')[0].strip()

    d = firebase_get('contadores') or {}
    ips = d.get("ips_vistos", [])

    if ip not in ips:
        ips.append(ip)
        d["visitantes"] = d.get("visitantes", 0) + 1
        firebase_patch('contadores', {
            "visitantes": d["visitantes"],
            "ips_vistos": ips
        })

    return jsonify({"visitantes": d["visitantes"]})

@app.route('/cadastro-vip', methods=['POST'])
def cadastro_vip():
    d = firebase_get('contadores') or {}
    d["vip"] = d.get("vip", 0) + 1
    firebase_patch('contadores', {"vip": d["vip"]})
    return jsonify({"vip": d["vip"]})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
