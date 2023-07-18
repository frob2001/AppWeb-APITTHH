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
        session['emisor'] = emisor

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
    return render_template('dashboard.html', nombre_usuario=nombre_usuario, ccostos=ccostos)


@app.route('/crear/<string:codigo>/<string:descripcion>', methods=['GET', 'POST'])
def crear(codigo, descripcion):
    url_api = f"http://apiservicios.ecuasolmovsa.com:3009/api/Varios/CentroCostosInsert?codigocentrocostos={codigo}&descripcioncentrocostos={descripcion}"
    creado = obtener_datos_api(url_api)
    print(creado)
    if creado[0]["Mensaje"] == 'El registro que desea ingresar ya existe':
        nombre_usuario = session.get('nombre_usuario', None)
        url_api = "http://apiservicios.ecuasolmovsa.com:3009/api/Varios/CentroCostosSelect"
        ccostos = obtener_datos_api(url_api)
        return render_template('dashboard.html', nombre_usuario=nombre_usuario, ccostos=ccostos, message="El centro ya existe")

    return redirect(url_for('dashboard'))



@app.route('/actualizar/<string:codigo>/<string:descripcion>', methods=['GET', 'POST'])
def actualizar(codigo, descripcion):
    url_api = f"http://apiservicios.ecuasolmovsa.com:3009/api/Varios/CentroCostosUpdate?codigocentrocostos={codigo}&descripcioncentrocostos={descripcion}"
    actualizado = obtener_datos_api(url_api)
    print(actualizado)
    return redirect(url_for('dashboard'))

@app.route('/trabajadores', methods=['GET', 'POST'])
def trabajadores():
    nombre_usuario = session.get('nombre_usuario', None)
    url_api = f"http://apiservicios.ecuasolmovsa.com:3009/api/Varios/TrabajadorSelect?sucursal={session['emisor']}"
    traba = obtener_datos_api(url_api)
    print(traba)
    return render_template('trabajadores.html', nombre_usuario=nombre_usuario, traba=traba)

@app.route('/detalles_trabajadores/<int:id_trabajador>', methods=['GET'])
def detalles_trabajadores(id_trabajador):
    url_api = f"http://apiservicios.ecuasolmovsa.com:3009/api/Varios/TrabajadorSelect?sucursal={session['emisor']}"
    traba = obtener_datos_api(url_api)

    # Buscar el trabajador por su ID en los datos obtenidos de la API
    trabajador = next((item for item in traba if item['Id_Trabajador'] == id_trabajador), None)

    if trabajador:
        #Tipo de trabajdor
        num = trabajador['Tipo_trabajador']
        url_api = "http://apiservicios.ecuasolmovsa.com:3009/api/Varios/TipoTrabajador"
        tipo = obtener_datos_api(url_api)

        for item in tipo:
            if item['Descripcion'] == num:
                tipo_trabajador = item['Codigo']
                break

        #Ocupacion
        ocu = trabajador['Codigo_Categoria_Ocupacion']
        url_api = "http://apiservicios.ecuasolmovsa.com:3009/api/Varios/CategoriaOcupacional"
        ocupa = obtener_datos_api(url_api)

        for item in ocupa:
            if item['Codigo'] == int(ocu):
                ocpation = item['Descripcion']
                break

        #Nivel salarial
        niv = trabajador['Nivel_Salarial']
        url_api = "http://apiservicios.ecuasolmovsa.com:3009/api/Varios/NivelSalarial"
        sal = obtener_datos_api(url_api)

        for item in sal:
            if item['Codigo'] == int(niv):
                nivel = item['Descripcion']
                break

        #Tipo de contrato
        con = trabajador['Tipo_Contrato']
        url_api = "http://apiservicios.ecuasolmovsa.com:3009/api/Varios/TipoContrato"
        tipoc = obtener_datos_api(url_api)

        for item in tipoc:
            if item['Codigo'] == str(con):
                tipo_contrato = item['Descripcion']
                break

        #Tipo de cuenta
        cue = trabajador['Tipo_Cuenta']
        url_api = "http://apiservicios.ecuasolmovsa.com:3009/api/Varios/TipoCuenta"
        cuentas = obtener_datos_api(url_api)
        print(type(cue))
        print(cuentas)

        for item in cuentas:
            if cue in item['Codigo']:
                cuenta = item['Descripcion']
                break
        


    return render_template('detalles_trabajadores.html', trabajador=trabajador, tipo_trabajador=tipo_trabajador, nivel=nivel, ocpation=ocpation, tipo_contrato=tipo_contrato, cuenta=cuenta)


if __name__ == '__main__':
    app.run(debug=True)
    
    