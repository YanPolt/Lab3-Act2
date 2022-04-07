
import os
import socket
import threading
import time
from datetime import datetime
#host_ip = "127.0.0.1"
host_ip = "localhost" #TODO
port = 8081 #TODO

num_clientes = int(input('Ingrese la cantidad de clientes que desea crear, recuerde que el servidor quedara esperando '
                         'conexión hasta completar las cantidad de clientes que se le especifico atender'))
while (num_clientes>25 and num_clientes <= 0):
    num_clientes = int(input('Ingrese un número válido de clientes (Entre 0 y 25)'))
def generarLog(fsize,finalSize, tiempo, fname, id_cliente):
    if not os.path.isdir("./logs"):
        os.mkdir("./logs")

    fActual = datetime.now()
    log = f"{fActual.year}-{fActual.month}-{fActual.day}-{fActual.hour}-{fActual.minute}-{fActual.second}-Cliente{id_cliente}-log.txt"

    fileLog = open(f"logs/cliente/{log}", "x")

    fileLog.write("Log {}\n".format(fActual))
    fileLog.write("Nombre del archivo {}\n".format(fname))
    fileLog.write("Tamaño del archivo: {}".format(finalSize))
    fileLog.write("\n")
    if(fsize==finalSize):
        fileLog.write("La entrega del archivo fue completa")
    else:
        fileLog.write("La entrega del archivo fue incompleta")
    fileLog.write("\n")
    fileLog.write(f"Tiempo de transferencia: {round(tiempo, 4)} secs")

    fileLog.close()


class Ejecucion:
    def __init__(self):
        self.lock = threading.Lock()


    def cliente_funct(self, nombre):
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tam_bloque = 4096

        mensaje = "Estado: Listo"
        client.sendto(mensaje.encode(), (host_ip, port))

        bienvenida, addr = client.recvfrom(tam_bloque)
        print(bienvenida.decode("utf-8"))

        numCliente, addr = client.recvfrom(tam_bloque)
        dec_num_cliente = numCliente.decode("utf-8")
        print(f"Numero de cliente: {dec_num_cliente}")

        cConexiones, addr = client.recvfrom(tam_bloque)
        dec_can_conexiones = cConexiones.decode("utf-8")
        print(f"Cantidad de conexiones: {dec_can_conexiones}")

        fsize, addr = client.recvfrom(tam_bloque)
        dec_fsize = fsize.decode("utf-8")
        print(f"Tamaño archivo: {dec_fsize}")

        # ** Recibiendo el archivo
        buf_archivo = 64000

        path = 'archivosRecibidos/'
        if not os.path.isdir(path):
            os.mkdir(path)

        fname = f"Cliente{dec_num_cliente}-Prueba-{dec_can_conexiones}.txt"
        file = open(path + fname, 'wb')
        inicio = time.time()
        data, addr = client.recvfrom(buf_archivo)
        try:
            while (data):
                file.write(data)
                client.settimeout(1)
                data, addr = client.recvfrom(buf_archivo)
        except socket.timeout:
            finalSize=os.path.getsize(path + fname)
            file.close()
            client.close()
            fin = time.time()
            tiempo = fin - inicio
            generarLog(dec_fsize, finalSize, tiempo,fname,dec_num_cliente)
            print("Archivo descargado \n")

        client.close()

def worker(c, nombre):
    c.cliente_funct(nombre)


hilo = Ejecucion()
for num_cliente in range(num_clientes):
    cliente = threading.Thread(name="Cliente%s" % (num_cliente + 1),
                               target=worker,
                               args=(hilo, "Cliente%s" % (num_cliente + 1))
                               )
    cliente.start()

