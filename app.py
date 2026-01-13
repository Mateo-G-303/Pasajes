from flask import Flask, render_template
from routes.rutas import rutas_bp
from routes.unidades import unidades_bp
from routes.tipos import tipos_bp
from routes.pasajes import pasajes_bp

app = Flask(__name__)

app.register_blueprint(rutas_bp)
app.register_blueprint(unidades_bp)
app.register_blueprint(tipos_bp)
app.register_blueprint(pasajes_bp)

@app.route('/')
def home():
    return render_template('home.html') 

if __name__ == '__main__':
    app.run(debug=True, port=5000)