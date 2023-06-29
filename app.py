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
    url_api = "http://apiservicios.ecuasolmovsa.com:3009/api/Varios/GetEmisor"
    emisores = obtener_datos_api(url_api)
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        emisor = int(request.form['emisor'])

        #Validacion de usuario con API    
        url_api = f"http://apiservicios.ecuasolmovsa.com:3009/api/Usuarios?usuario={usuario}&password={contrasena}"
        datos_api = obtener_datos_api(url_api)


        if datos_api == "error":
            return render_template('index.html', emisores=emisores, message="Algo esta mal ingresado")
        else:
            if datos_api[0]["OBSERVACION"] != None:
                if datos_api[0]["OBSERVACION"] == "INGRESO EXITOSO":
                    if datos_api[0]["Emisor"] == emisor:
                        print(datos_api)
                        session['nombre_usuario'] = datos_api[0]['NOMBREUSUARIO']
                        return redirect(url_for('dashboard'))
                    else:
                        return render_template('index.html', emisores=emisores, message="El emisor no coincide")
                else:
                    return render_template('index.html', emisores=emisores, message="La contrasena es incorrecta")
    else:
        return render_template('index.html', emisores=emisores)
    
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    nombre_usuario = session.get('nombre_usuario', None)
    url_api = "http://apiservicios.ecuasolmovsa.com:3009/api/Varios/CentroCostosSelect"
    ccostos = obtener_datos_api(url_api)
    print(ccostos)
    return render_template('dashboard.html', nombre_usuario=nombre_usuario, ccostos=ccostos)


@app.route('/crear/<string:codigo>/<string:descripcion>', methods=['GET', 'POST'])
def crear(codigo, descripcion):
    url_api = f"http://apiservicios.ecuasolmovsa.com:3009/api/Varios/CentroCostosInsert?codigocentrocostos={codigo}&descripcioncentrocostos={descripcion}"
    creado = obtener_datos_api(url_api)
    print(creado)
    return redirect(url_for('dashboard'))



@app.route('/actualizar/<string:codigo>/<string:descripcion>', methods=['GET', 'POST'])
def actualizar(codigo, descripcion):
    url_api = f"http://apiservicios.ecuasolmovsa.com:3009/api/Varios/CentroCostosUpdate?codigocentrocostos={codigo}&descripcioncentrocostos={descripcion}"
    actualizado = obtener_datos_api(url_api)
    print(actualizado)
    return redirect(url_for('dashboard'))




if __name__ == '__main__':
    app.run(debug=True)
    
    