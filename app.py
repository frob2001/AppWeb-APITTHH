from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)

app.secret_key = 'mi_clave_secreta'


class APIClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.session = requests.Session()
        return cls._instance

    def obtener_datos_api(self, url):
        respuesta = self.session.get(url)

        if respuesta.status_code == 200:
            datos = respuesta.json()
            return datos
        else:
            print("Error al obtener los datos de la API:", respuesta.status_code)
            return None


@app.route('/', methods=['GET', 'POST'])
def index():
    api_client = APIClient()
    url_api = "http://apiservicios.ecuasolmovsa.com:3009/api/Varios/GetEmisor"
    emisores = api_client.obtener_datos_api(url_api)

    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        emisor = int(request.form['emisor'])
        session['emisor'] = emisor

        url_api = f"http://apiservicios.ecuasolmovsa.com:3009/api/Usuarios?usuario={usuario}&password={contrasena}"
        datos_api = api_client.obtener_datos_api(url_api)

        if datos_api == "error":
            return render_template('index.html', emisores=emisores, message="Algo esta mal ingresado")
        else:
            if datos_api[0]["OBSERVACION"] != None:
                if datos_api[0]["OBSERVACION"] == "INGRESO EXITOSO":
                    if datos_api[0]["Emisor"] == emisor:
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
    api_client = APIClient()
    nombre_usuario = session.get('nombre_usuario', None)
    url_api = "http://apiservicios.ecuasolmovsa.com:3009/api/Varios/CentroCostosSelect"
    ccostos = api_client.obtener_datos_api(url_api)
    return render_template('dashboard.html', nombre_usuario=nombre_usuario, ccostos=ccostos)


@app.route('/crear/<string:codigo>/<string:descripcion>', methods=['GET', 'POST'])
def crear(codigo, descripcion):
    api_client = APIClient()
    url_api = f"http://apiservicios.ecuasolmovsa.com:3009/api/Varios/CentroCostosInsert?codigocentrocostos={codigo}&descripcioncentrocostos={descripcion}"
    creado = api_client.obtener_datos_api(url_api)

    if creado[0]["Mensaje"] == 'El registro que desea ingresar ya existe':
        nombre_usuario = session.get('nombre_usuario', None)
        url_api = "http://apiservicios.ecuasolmovsa.com:3009/api/Varios/CentroCostosSelect"
        ccostos = api_client.obtener_datos_api(url_api)
        return render_template('dashboard.html', nombre_usuario=nombre_usuario, ccostos=ccostos, message="El centro ya existe")

    return redirect(url_for('dashboard'))


@app.route('/actualizar/<string:codigo>/<string:descripcion>', methods=['GET', 'POST'])
def actualizar(codigo, descripcion):
    api_client = APIClient()
    url_api = f"http://apiservicios.ecuasolmovsa.com:3009/api/Varios/CentroCostosUpdate?codigocentrocostos={codigo}&descripcioncentrocostos={descripcion}"
    actualizado = api_client.obtener_datos_api(url_api)
    return redirect(url_for('dashboard'))


@app.route('/trabajadores', methods=['GET', 'POST'])
def trabajadores():
    api_client = APIClient()
    nombre_usuario = session.get('nombre_usuario', None)
    url_api = f"http://apiservicios.ecuasolmovsa.com:3009/api/Varios/TrabajadorSelect?sucursal={session['emisor']}"
    traba = api_client.obtener_datos_api(url_api)
    return render_template('trabajadores.html', nombre_usuario=nombre_usuario, traba=traba)


@app.route('/detalles_trabajadores/<int:id_trabajador>', methods=['GET'])
def detalles_trabajadores(id_trabajador):
    api_client = APIClient()
    url_api = f"http://apiservicios.ecuasolmovsa.com:3009/api/Varios/TrabajadorSelect?sucursal={session['emisor']}"
    traba = api_client.obtener_datos_api(url_api)

    # Buscar el trabajador por su ID en los datos obtenidos de la API
    trabajador = next((item for item in traba if item['Id_Trabajador'] == id_trabajador), None)

    if trabajador:
        #Tipo de trabajdor
        num = trabajador['Tipo_trabajador']
        url_api = "http://apiservicios.ecuasolmovsa.com:3009/api/Varios/TipoTrabajador"
        tipo = api_client.obtener_datos_api(url_api)

        for item in tipo:
            if item['Descripcion'] == num:
                tipo_trabajador = item['Codigo']
                break

        #Ocupacion
        ocu = trabajador['Codigo_Categoria_Ocupacion']
        url_api = "http://apiservicios.ecuasolmovsa.com:3009/api/Varios/CategoriaOcupacional"
        ocupa = api_client.obtener_datos_api(url_api)

        for item in ocupa:
            if item['Codigo'] == int(ocu):
                ocpation = item['Descripcion']
                break

        #Nivel salarial
        niv = trabajador['Nivel_Salarial']
        url_api = "http://apiservicios.ecuasolmovsa.com:3009/api/Varios/NivelSalarial"
        sal = api_client.obtener_datos_api(url_api)

        for item in sal:
            if item['Codigo'] == int(niv):
                nivel = item['Descripcion']
                break

        #Tipo de contrato
        con = trabajador['Tipo_Contrato']
        url_api = "http://apiservicios.ecuasolmovsa.com:3009/api/Varios/TipoContrato"
        tipoc = api_client.obtener_datos_api(url_api)

        for item in tipoc:
            if item['Codigo'] == str(con):
                tipo_contrato = item['Descripcion']
                break

        #Tipo de cuenta
        cue = trabajador['Tipo_Cuenta']
        url_api = "http://apiservicios.ecuasolmovsa.com:3009/api/Varios/TipoCuenta"
        cuentas = api_client.obtener_datos_api(url_api)

        for item in cuentas:
            if cue in item['Codigo']:
                cuenta = item['Descripcion']
                break

        return render_template('detalles_trabajadores.html', trabajador=trabajador, tipo_trabajador=tipo_trabajador, nivel=nivel, ocpation=ocpation, tipo_contrato=tipo_contrato, cuenta=cuenta)

    return render_template('detalles_trabajadores.html', message="Trabajador no encontrado")


@app.route('/crear_trabajador/<string:codigo>/<string:descripcion>', methods=['GET', 'POST'])
def crear_trabajador(codigo, descripcion):
    api_client = APIClient()
    COMP_Codigo = session['emisor']
    Tipo_trabajador = request.form.get('Tipo_trabajador', 'N/A')
    Apellido_Paterno = request.form.get('Apellido_Paterno', 'N/A')
    Apellido_Materno = request.form.get('Apellido_Materno', 'N/A')
    Nombres = request.form.get('Nombres', 'N/A')
    Identificacion = request.form.get('Identificacion', 'N/A')
    Entidad_Bancaria = request.form.get('Entidad_Bancaria', 'N/A')
    CarnetIESS = request.form.get('CarnetIESS', 'N/A')
    Direccion = request.form.get('Direccion', 'N/A')
    Telefono_Fijo = request.form.get('Telefono_Fijo', 'N/A')
    Telefono_Movil = request.form.get('Telefono_Movil', 'N/A')
    Genero = request.form.get('Genero', 'N/A')
    Nro_Cuenta_Bancaria = request.form.get('Nro_Cuenta_Bancaria', 'N/A')
    Codigo_Categoria_Ocupacion = request.form.get('Codigo_Categoria_Ocupacion', 'N/A')
    Ocupacion = request.form.get('Ocupacion', 'N/A')
    Centro_Costos = request.form.get('Centro_Costos', 'N/A')
    Nivel_Salarial = request.form.get('Nivel_Salarial', 'N/A')
    EstadoTrabajador = request.form.get('EstadoTrabajador', 'N/A')
    Tipo_Contrato = request.form.get('Tipo_Contrato', 'N/A')
    Tipo_Cese = request.form.get('Tipo_Cese', 'N/A')
    EstadoCivil = request.form.get('EstadoCivil', 'N/A')
    TipodeComision = request.form.get('TipodeComision', 'N/A')
    FechaNacimiento = request.form.get('FechaNacimiento', 'N/A')
    FechaIngreso = request.form.get('FechaIngreso', 'N/A')
    FechaCese = request.form.get('FechaCese', 'N/A')
    PeriododeVacaciones = request.form.get('PeriododeVacaciones', 'N/A')
    FechaReingreso = request.form.get('FechaReingreso', 'N/A')
    Fecha_Ult_Actualizacion = request.form.get('Fecha_Ult_Actualizacion', 'N/A')
    EsReingreso = request.form.get('EsReingreso', 'N/A')
    Tipo_Cuenta = request.form.get('Tipo_Cuenta', 'N/A')
    FormaCalculo13ro = request.form.get('FormaCalculo13ro', 'N/A')
    FormaCalculo14ro = request.form.get('FormaCalculo14ro', 'N/A')
    BoniComplementaria = request.form.get('BoniComplementaria', 'N/A')
    BoniEspecial = request.form.get('BoniEspecial', 'N/A')
    Remuneracion_Minima = request.form.get('Remuneracion_Minima', 'N/A')
    Fondo_Reserva = request.form.get('Fondo_Reserva', 'N/A')
    Mensaje = request.form.get('Mensaje', 'N/A')

@app.route('/eliminar_trabajador/<int:id_trabajador>', methods=['GET', 'POST'])
def eliminar_trabajador(id_trabajador):
    api_client = APIClient()
    url_api = f"http://apiservicios.ecuasolmovsa.com:3009/api/Varios/TrabajadorDelete?sucursal={session['emisor']}&codigoempleado={id_trabajador}"
    actualizado = api_client.obtener_datos_api(url_api)
    print(actualizado)
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
