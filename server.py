import socket, threading, queue, time
from tabulate import tabulate

'''
 + - + - + - + - + - + - Recursos compartidos - + - + - + - + - + - + - +
'''

# Fila de mensajes recibidos del cliente
mensajes_entrada = queue.Queue()

# Fila de mensajes a responder al cliente
tabla = [['Timestamp', 'Comando', 'El servidor despliega', 'Libres', 'Ocupados']]

# Bandera para saber si el estacionamiento está abierto
abierto = False

# Constante para saber la capacidad del estacionamiento
CAPACIDAD = 0

# Contador de lugares disponibles
lugares_libres = 0

# Semáforo binario para proteger lugares_libres
mutex_lugares = threading.Lock()

# Lista de threads de entradas
entradas = []

# Cuando un alguien usa una entrada se bloquea, para eso es esta lista de mutex
# Cada mutex corresponde con la entrada i
mutex_entradas = []

# Lista de banderas para saber si un carro cruza por el laser de entrada
cruzando_laser_entrada = []

# Lista de threads de salidas
salidas = []

# Cuando un alguien usa una salida se bloquea, para eso es esta lista de mutex
# Cada mutex corresponde con la salida i
mutex_salidas = []

# Lista de banderas para saber si un carro cruza por el laser de salida
cruzando_laser_salida = []

'''
 + - + - + - + - + - + - + - + Entrada + - + - + - + - + - + - + - + - +
'''

# Funciones necesarias para entrada

def oprime_boton(hora, num_entrada):
    mutex_entradas[num_entrada - 1].acquire()
    mutex_lugares.acquire()

    if lugares_libres > 0:
        row = [
            hora,
            f'oprimeBoton {num_entrada}',
            f'Imprimiendo tarjeta en entrada {num_entrada}',
            lugares_libres,
            CAPACIDAD - lugares_libres]

        tabla.append(row)

        time.sleep(5)

        row = [
            hora + 5,
            f'oprimeBoton {num_entrada}',
            f'Se imprimió tarjeta. Hora: {num_entrada}', # TODO: agregar hora
            lugares_libres,
            CAPACIDAD - lugares_libres]

        tabla.append(row)
    else:
        row = [
            hora,
            f'oprimeBoton {num_entrada}',
            'Estacionamiento lleno, inténtalo después',
            lugares_libres,
            CAPACIDAD - lugares_libres]

        tabla.append(row)

    mutex_lugares.release()


def recoge_tarjeta(hora, num_entrada):
    mutex_lugares.acquire()

    row = [
        hora,
        f'recojeTarjeta {num_entrada}',
        f'Se levanta barrera entrada {num_entrada}',
        lugares_libres,
        CAPACIDAD - lugares_libres]

    tabla.append(row)

    time.sleep(5)

    row = [
        hora + 5,
        f'recojeTarjeta {num_entrada}',
        f'Barrera de entrada {num_entrada} levantada',
        lugares_libres,
        CAPACIDAD - lugares_libres]

    tabla.append(row)

    mutex_lugares.release()



def laser_off_e(hora, num_entrada):
    cruzando_laser_entrada[num_entrada] = True

    mutex_lugares.acquire()

    row = [
        hora,
        f'laserOffE {num_entrada}',
        f'Auto pasando por entrada {num_entrada}',
        lugares_libres,
        CAPACIDAD - lugares_libres]

    tabla.append(row)

    mutex_lugares.release()



def laser_on_e(hora, num_entrada):
    global lugares_libres

    mutex_lugares.acquire()

    if cruzando_laser_entrada[num_entrada]:
        lugares_libres -= 1

        row = [
            hora,
            f'laserOnE {num_entrada}',
            f'Auto termina de pasar por entrada {num_entrada}',
            lugares_libres,
            CAPACIDAD - lugares_libres]

        tabla.append(row)

        time.sleep(5)

        row = [
            hora,
            f'laserOnE {num_entrada}',
            f'Se bajó barrera de entrada {num_entrada}',
            lugares_libres,
            CAPACIDAD - lugares_libres]

        tabla.append(row)
    else:
        row = [
            hora,
            f'laserOnE {num_entrada}',
            f'Error: no hay auto en salida {num_entrada}',
            lugares_libres,
            CAPACIDAD - lugares_libres]

        tabla.append(row)

    mutex_lugares.release()
    mutex_entradas[num_entrada - 1].release()



# Función base para thread de entrada

def entrada(num_entrada):
    while abierto:
        mensaje = mensajes_entrada.get()

        if len(mensaje) > 2 and mensaje[2] == num_entrada:
            if mensaje[1] == 'oprimeBoton':
                oprime_boton(mensaje[0], num_entrada)
            elif mensaje[1] == 'recojeTarjeta':
                recoge_tarjeta(mensaje[0], num_entrada)
            elif mensaje[1] == 'laserOffE':
                laser_off_e(mensaje[0], num_entrada)
            elif mensaje[1] == 'laserOnE':
                laser_on_e(mensaje[0], num_entrada)
            else:
                mensajes_entrada.put(mensaje)
        else:
            mensajes_entrada.put(mensaje)



'''
 + - + - + - + - + - + - + - + Salida + - + - + - + - + - + - + - + - +
'''

# Funciones necesarias para salida

def mete_tarjeta(hora, num_salida, pagado, hora_pago):
    mutex_salidas[num_salida - 1].acquire()

    if pagado == 1:
        if hora - hora_pago < 15:     # TODO: Hacer chequeo de hora correcto
            row = [
                hora,
                f'meteTarjeta {num_salida} {pagado} {hora_pago}',
                f'Levantando barrera de salida {num_salida}',
                lugares_libres,
                CAPACIDAD - lugares_libres]

            tabla.append(row)
        else:
            row = [
                hora,
                f'meteTarjeta {num_salida} {pagado} {hora_pago}',
                'Tiempo de tolerancia terminado, vuelva a pagar',
                lugares_libres,
                CAPACIDAD - lugares_libres]

            tabla.append(row)
    else:
        row = [
            hora,
            f'meteTarjeta {num_salida} {pagado} {hora_pago}',
            'No se ha pagado el tiempo de estancia',
            lugares_libres,
            CAPACIDAD - lugares_libres]

        tabla.append(row)



def laser_off_s(hora, num_salida):
    cruzando_laser_salida[num_salida] = True

    mutex_lugares.acquire()

    row = [
        hora,
        f'laserOffS {num_salida}',
        f'Auto pasando por salida {num_salida}',
        lugares_libres,
        CAPACIDAD - lugares_libres]

    tabla.append(row)

    mutex_lugares.release()



def laser_on_s(hora, num_salida):
    if cruzando_laser_salida[num_salida]:
        mutex_lugares.acquire()

        lugares_libres += 1

        mutex_lugares.release()

        row = [
            hora,
            f'laserOnS {num_salida}',
            f'Auto termina de pasar por salida {num_salida}',
            lugares_libres,
            CAPACIDAD - lugares_libres]

        tabla.append(row)

        time.sleep(5)

        row = [
            hora + 5,
            f'laserOnS {num_salida}',
            f'Se baja barrera en salida {num_salida}',
            lugares_libres,
            CAPACIDAD - lugares_libres]

        tabla.append(row)
    else:
        row = [
            hora,
            f'laserOnS {num_salida}',
            f'Error: no hay auto en salida {num_salida}',
            lugares_libres,
            CAPACIDAD - lugares_libres]

        tabla.append(row)

    mutex_salidas[num_salida - 1].release()



# Función base para thread de salida

def salida(num_salida):
    global abierto

    while abierto:
        mensaje = mensajes_entrada.get()

        if len(mensaje) > 2 and mensaje[2] == num_salida:
            if mensaje[1] == 'meteTarjeta':
                mete_tarjeta(mensaje[0], num_salida, mensaje[2], mensaje[3])
            elif mensaje[1] == 'laserOffS':
                laser_off_s(mensaje[0], num_salida)
            elif mensaje[1] == 'laserOnS':
                laser_on_s(mensaje[0], num_salida)
            else:
                mensajes_entrada.put(mensaje)
        else:
            mensajes_entrada.put(mensaje)

'''
 + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - +
'''

# Función para inicializar estacionamiento

def apertura(hora, num_lugares, num_entradas, num_salidas):
    global CAPACIDAD, lugares_libres
    global abierto, entradas, salidas, mutex_entradas, mutex_salidas

    if not abierto:
        abierto = True
        CAPACIDAD = num_lugares
        lugares_libres = num_lugares

        row = [
            hora,
            f'apertura {num_lugares} {num_entradas} {num_salidas}',
            f'Se abre el estacionamiento con {num_lugares} lugares, {num_entradas} entradas, y {num_salidas} salidas',
            lugares_libres,
            CAPACIDAD - lugares_libres]

        tabla.append(row)

        for i in range(num_entradas):
            entradas.append(threading.Thread(target=entrada, args=(i,)))
            entradas[i].start()

            mutex_entradas.append(threading.Lock())

            cruzando_laser_entrada.append(False)

        for i in range(num_salidas):
            salidas.append(threading.Thread(target=salida, args=(i,)))
            salidas[i].start()

            mutex_salidas.append(threading.Lock())

            cruzando_laser_salida.append(False)
    else:
        mutex_lugares.acquire()

        row = [
            hora,
            f'apertura {num_lugares} {num_entradas} {num_salidas}',
            'Error: El estacionamiento ya está abierto',
            lugares_libres,
            CAPACIDAD - lugares_libres]

        tabla.append(row)

        mutex_lugares.release()



# Función para cerrar estacionamiento

def cierre(hora):
    global abierto, entradas, salidas, mutex_entradas, mutex_salidas

    if abierto:
        abierto = False

        for entrada in entradas:
            entrada.join()

        for salida in salidas:
            salida.join()

        mutex_entradas = []
        mutex_salidas = []

        row = [
            hora,
            f'cierre',
            f'Se cierra estacionamiento',
            lugares_libres,
            CAPACIDAD - lugares_libres]

        tabla.append(row)
    else:
        mutex_lugares.acquire()

        row = [
            hora,
            f'cierre',
            'Error: No hay estacionamiento abierto',
            lugares_libres,
            CAPACIDAD - lugares_libres]

        tabla.append(row)

        mutex_lugares.release()

'''
 + - + - + - + - Validación de mensajes del cliente - + - + - + - + - +
'''

class Error(Exception):
    pass

class ComandoInvalido(Error):
    pass

class FormatoInvalido(Error):
    pass

def validar_mensajes(mensaje):
    es_valido = True
    args = mensaje.split(' ')

    try:
        args[0] = float(args[0])
        try:
            if args[1] == 'apertura':
                try:
                    if len(args) != 5:
                        raise FormatoInvalido
                    else:
                        try:
                            args[2] = int(args[2])
                        except ValueError:
                            es_valido = False
                            print(f'Formato numero de lugares en {args[1]} invalido')
                            pass
                        try:
                            args[3] = int(args[3])
                        except ValueError:
                            es_valido = False
                            print(f'Formato numero de puertas de entrada en {args[1]} invalido')
                            pass
                        try:
                            args[4] = int(args[4])
                        except ValueError:
                            es_valido = False
                            print(f'Formato numero de puertas de salida en {args[1]} invalido')
                            pass
                except FormatoInvalido:
                    es_valido = False
                    print(f'Formato de mensaje {args[1]} invalido')
                    pass
            elif args[1] == 'oprimeBoton':
                try:
                    if len(args) != 3:
                        raise FormatoInvalido
                    else:
                        try:
                            args[2] = int(args[2])
                        except ValueError:
                            es_valido = False
                            print(f'Formato numero de entrada en {args[1]} invalido')
                            pass
                except FormatoInvalido:
                    es_valido = False
                    print(f'Formato de mensaje {args[1]} invalido')
                    pass
            elif args[1] == 'recojeTarjeta':
                try:
                    if len(args) != 3:
                        raise FormatoInvalido
                    else:
                        try:
                            args[2] = int(args[2])
                        except ValueError:
                            es_valido = False
                            print(f'Formato numero de barrera en {args[1]} invalido')
                            pass
                except FormatoInvalido:
                    es_valido = False
                    print(f'Formato de mensaje {args[1]} invalido')
                    pass
            elif args[1] == 'laserOffE':
                try:
                    if len(args) != 3:
                        raise FormatoInvalido
                    else:
                        try:
                            args[2] = int(args[2])
                        except ValueError:
                            es_valido = False
                            print(f'Formato numero de estacionamiento en {args[1]} invalido')
                            pass
                except FormatoInvalido:
                    es_valido = False
                    print(f'Formato de mensaje {args[1]} invalido')
                    pass
            elif args[1] == 'laserOnE':
                try:
                    if len(args) != 3:
                        raise FormatoInvalido
                    else:
                        try:
                            args[2] = int(args[2])
                        except ValueError:
                            es_valido = False
                            print(f'Formato numero de estacionamiento en {args[1]} invalido')
                            pass
                except FormatoInvalido:
                    es_valido = False
                    print(f'Formato de mensaje {args[1]} invalido')
                    pass
            elif args[1] == 'meteTarjeta':
                try:
                    if len(args) != 4:
                        raise FormatoInvalido
                    else:
                        try:
                            args[2] = int(args[2])
                        except ValueError:
                            es_valido = False
                            print(f'Formato numero de estacionamiento en {args[1]} invalido')
                            pass
                        try:
                            args[3] = float(args[3])
                        except ValueError:
                            es_valido = False
                            print(f'Formato numero de estacionamiento en {args[1]} invalido')
                            pass
                except FormatoInvalido:
                    es_valido = False
                    print(f'Formato de mensaje {args[1]} invalido')
                    pass
            elif args[1] == 'laserOffS':
                try:
                    if len(args) != 3:
                        raise FormatoInvalido
                    else:
                        try:
                            args[2] = int(args[2])
                        except ValueError:
                            es_valido = False
                            print(f'Formato numero de estacionamiento en {args[1]} invalido')
                            pass
                except FormatoInvalido:
                    es_valido = False
                    print(f'Formato de mensaje {args[1]} invalido')
                    pass
            elif args[1] == 'laserOnS':
                try:
                    if len(args) != 3:
                        raise FormatoInvalido
                    else:
                        try:
                            args[2] = int(args[2])
                        except ValueError:
                            es_valido = False
                            print(f'Formato numero de estacionamiento en {args[1]} invalido')
                            pass
                except FormatoInvalido:
                    es_valido = False
                    print(f'Formato de mensaje {args[1]} invalido')
                    pass
            elif args[1] == 'cierre':
                try:
                    if len(args) != 2:
                        raise FormatoInvalido
                except FormatoInvalido:
                    es_valido = False
                    print(f'Formato de mensaje {args[1]} invalido')
                    pass
            else:
                raise ComandoInvalido
        except ComandoInvalido:
            es_valido = False
            print(f'Comando {args[1]} invalido')
            pass
    except ValueError:
        es_valido = False
        print(f'Formato numero de lugares en {args[1]} invalido')
        pass

    if es_valido:
        comando = []
        comando.append(float(args[0]))
        comando.append(args[1])

        if len(args) > 2:
            comando.append(int(args[2]))

        if len(args) > 3:
            if str(args[3]).find('.') != -1:
                comando.append(float(args[3]))
            else:
                comando.append(int(args[3]))

        if len(args) > 4:
            comando.append(int(args[4]))

        return comando




'''
 + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - +
'''

def main(connection):
    try:
        servidor_abierto = True

        while servidor_abierto:
            datos = connection.recv(256)
            mensaje = datos.decode('utf-8')

            if mensaje:
                comando = validar_mensajes(mensaje)

                if comando:
                    mensajes_entrada.put(comando)

            if not mensajes_entrada.empty():
                comando = mensajes_entrada.get()

                if not abierto and comando[1] == 'apertura':
                    apertura(comando[0], comando[2], comando[3], comando[4])
                elif abierto and comando[1] == 'cierre':
                    cierre(comando[0])
                    servidor_abierto = False
                else:
                    mensajes_entrada.put(comando)

            print('\n')
            print(tabulate(tabla, headers='firstrow', tablefmt='orgtbl'))
            print('\n')
    finally:
        print('closing server')
        connection.close()



# Procedimientos necesarios para iniciar servidor

if __name__ == '__main__':
    # Inicialización del servidor
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10000)

    print('starting server on %s:%s' % server_address)

    sock.bind(server_address)
    sock.listen(1)

    print('waiting for connection')

    connection, client_address = sock.accept()
    print('connection from %s:%s' % client_address)

    # Inicio del ciclo del servidor
    main(connection)
