from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_restx import Api

from back_end.apis import index_blueprint, register_routes

app = Flask(__name__)
CORS(app)  # This will allow all origins. For production, you might want to restrict this.
api = Api(app, title="Flask Api", version="1.0")

register_routes(api)
app.register_blueprint(index_blueprint)

@app.route('/home')
def index():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
