from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route('/icons/<path:filename>')
def serve_icon(filename):
    return send_from_directory('icons', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route('/icons/<path:filename>')
def serve_icon(filename):
    return send_from_directory('icons', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)