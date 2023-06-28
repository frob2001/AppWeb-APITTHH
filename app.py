from flask import Flask, render_template, request, redirect, url_for, session
import json
import requests

app = Flask(__name__)

app.secret_key = 'mi_clave_secreta'


def obtener_datos_api(url):
    respuesta = requests.get(url)

    if respuesta.status_code == 200:
        datos = respuesta.json()
        return datos
    else:
        print("Error al obtener los datos de la API:", respuesta.status_code)
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        emisor = int(request.form['emisor'])

        #Validacion de usuario con API    
        url_api = f"http://apiservicios.ecuasolmovsa.com:3009/api/Usuarios?usuario={usuario}&password={contrasena}"
        datos_api = obtener_datos_api(url_api)


        if datos_api == "error":
            return("Algo esta mal ingresado")
        else:
            if datos_api[0]["OBSERVACION"] != None:
                if datos_api[0]["OBSERVACION"] == "INGRESO EXITOSO":
                    if datos_api[0]["Emisor"] == emisor:
                        print(datos_api)
                        session['nombre_usuario'] = datos_api[0]['NOMBREUSUARIO']
                        return redirect(url_for('dashboard'))
                    else:
                        return("El emisor no coincide")
                else:
                    return("La contrasena es incorrecta")
    else:
        url_api = "http://apiservicios.ecuasolmovsa.com:3009/api/Varios/GetEmisor"
        emisores = obtener_datos_api(url_api)
        return render_template('index.html', emisores=emisores)
    
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    nombre_usuario = session.get('nombre_usuario', None)
    return render_template('dashboard.html', nombre_usuario=nombre_usuario)

if __name__ == '__main__':
    app.run(debug=True)
    
    