import sys, socket, threading, queue, time

'''
 + - + - + - + - + - + - Recursos compartidos - + - + - + - + - + - + - +
'''

# Fila de mensajes recibidos del cliente
mensajes_entrada = queue.Queue()

# Fila de mensajes a responder al cliente
mensajes_salida = queue.Queue()

# Bandera para saber si el estacionamiento está abierto
abierto = False

# Contador de lugares disponibles
lugares_disp

# Semáforo binario para proteger lugares_disp
mutex_lugares = threading.Lock()

# Lista de threads de entradas
entradas

# Cuando un alguien usa una entrada se bloquea, para eso es esta lista de mutex
# Cada mutex corresponde con la entrada i
mutex_entradas

# Lista de banderas para saber si un carro cruza por el laser de entrada
cruzando_laser_entrada

# Lista de threads de salidas
salidas

# Cuando un alguien usa una salida se bloquea, para eso es esta lista de mutex
# Cada mutex corresponde con la salida i
mutex_salidas

# Lista de banderas para saber si un carro cruza por el laser de salida
cruzando_laser_salida

'''
 + - + - + - + - + - + - + - + Entrada + - + - + - + - + - + - + - + - +
'''

# Funciones necesarias para entrada

def oprime_boton(hora, num_entrada):
    global lugares_disp, mutex_lugares, mutex_entradas, mensajes_salida

    mutex_entradas[num_entrada].acquire()
    mutex_lugares.acquire()

    if lugares_disp > 0:
        lugares_disp -= 1
        mensajes_salida.put(f'Imprimiendo tarjeta en entrada {num_entrada}')
    else:
        mensajes_salida.put('Estacionamiento lleno, inténtelo después')

    mutex_lugares.release()



def laser_off_e(hora, num_entrada)
    global mensajes_salida, cruzando_laser_entrada

    cruzando_laser_entrada[num_entrada] = True

    mensajes_salida.put(f'Auto pasando por entrada {num_entrada}')



def laser_on_e(hora, num_entrada)
    global mutex_entradas, mensajes_salida, cruzando_laser_entrada

    if cruzando_laser_entrada[num_entrada]:
        mensajes_salida.put(f'Auto termina de pasar por entrada {num_entrada}')
        mensajes_salida.put(f'Se baja barrera en entrada {num_entrada}')
    else:
        mensajes_salida.put(f'Error: no hay auto en salida {num_entrada}')

    mutex_entradas[i].release()



# Función base para thread de entrada

def entrada(hora, num_entrada):
    global abierto, mensajes_salida

    while abierto:
        pass

'''
 + - + - + - + - + - + - + - + Salida + - + - + - + - + - + - + - + - +
'''

# Funciones necesarias para salida

def mete_tarjeta(hora, num_salida, pagado, tiempo_pago):
    global lugares_disp, mutex_lugares, mutex_salidas, mensajes_salida

    mutex_salidas[num_salida].acquire()

    if pagado == 1:
        if tiempo_pago - hora < 15:     # TODO: Hacer chequeo de hora correcto
            mutex_lugares.acquire()

            lugares_disp += 1

            mutex_lugares.release()

            mensajes_salida.put('Levantando barrera')
        else:
            mensajes_salida.put('Tiempo de tolerancia terminado')
    else:
        mensajes_salida.put('No se ha pagado el tiempo de estancia')



def laser_off_s(hora, num_salida):
    global mensajes_salida, cruzando_laser_salida

    cruzando_laser_salida[num_salida] = True

    mensajes_salida.put(f'Auto pasando por salida {num_salida}')



def laser_on_s(hora, num_salida):
    global mensajes_salida, cruzando_laser_salida

    if cruzando_laser_salida[num_salida]:
        mensajes_salida.put(f'Auto termina de pasar por salida {num_salida}')
        mensajes_salida.put(f'Se baja barrera en salida {num_salida}')
    else:
        mensajes_salida.put(f'Error: no hay auto en salida {num_salida}')

    mutex_salidas[num_salida].release()



# Función base para thread de salida

def salida(num_salida):
    global abierto

    while abierto:
        pass

'''
 + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - +
'''

# Función para inicializar estacionamiento

def apertura(num_lugares, num_entradas, num_salidas):
    global abierto, lugares_disp, entradas, salidas
    global mutex_entradas, mutex_salidas

    abierto = True
    lugares_disp = num_lugares

    for i in range(num_entradas):
        entradas[i] = threading.Thread(target=entrada, args=(i,))
        entradas[i].start()

        mutex_entradas[i] = threading.Lock()

    for i in range(num_salidas):
        salidas[i] = threading.Thread(target=salida, args=(i,))
        salidas[i].start()

        mutex_salidas[i] = threading.Lock()



# Función para cerrar estacionamiento

def cierre():
    global abierto, entradas, salidas
    global mutex_entradas, mutex_salidas

    abierto = False

    mutex_entradas = []
    mutex_salidas = []

    for entrada in entradas:
        entrada.join()

    for salida in salidas:
        salida.join()

'''
 + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - +
'''

# Función para recibir mensajes del cliente

def recibir_cliente(connection):
    global mensajes_entrada

    try:
        while True:
            datos = connection.recv(256)
            mensaje = datos.decode('utf-8')

            if msg:
                mensajes_entrada.put(mensaje)
            else:
                break
    finally:
        print('closing server')
        connection.close()



# Función para enviar mensajes del cliente

def enviar_cliente(sock):
    global mensajes_entrada, mensajes_salida

    while True:
        mensaje = mensajes_salida.get()
        sock.sendall(mensaje.encode('utf-8'))



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
    
    # Inicialización de threads
    thread1 = threading.Thread(target=recibir_cliente, args=(connection,))
    thread2 = threading.Thread(target=enviar_cliente, args=(sock,))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()