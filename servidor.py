import socket
import os
from threading import Thread
import time
from datetime import datetime

threads = []


def crearArchivo(path, tam):
    with open(path, "wb") as f:
        f.seek(tam * 1024 ** 2)
        f.write("Infracom".encode())


def generarLog(addr, fsize, tiempo, fname, id_cliente):
    if not os.path.isdir("./logs"):
        os.mkdir("./logs")

    fActual = datetime.now()
    log = f"{fActual.year}-{fActual.month}-{fActual.day}-{fActual.hour}-{fActual.minute}-{fActual.second}-Cliente{id_cliente}-log.txt"
    fp = os.path.join('.', 'logs', 'servidor')
    if not os.path.exists(fp):
        os.mkdir(fp)
    fileLog = open(f"logs/servidor/{log}", "x")

    fileLog.write("Log {}\n".format(fActual))
    fileLog.write("Nombre del archivo {}\n".format(fname + ".txt"))
    fileLog.write("Tamaño del archivo: {}".format(fsize))
    fileLog.write("\n")
    fileLog.write(" ***************** Informacion Cliente ******************** \n")
    fileLog.write(f"* {addr} \n* Tiempo de envio: {round(tiempo, 4)} secs")

    fileLog.close()


def operate(server, addr, path, nThreads, numCliente):
    print(f"Conexion establecida con {addr}")

    server.sendto(f"Bienvenido, {addr[1]}!".encode("utf-8"), addr)  # 1
    server.sendto(f"{numCliente}".encode("utf-8"), addr)  # 2
    server.sendto(f"{nThreads}".encode("utf-8"), addr)  # 3
    fsize = os.path.getsize(path)
    server.sendto(f"{fsize}".encode("utf-8"), addr)  # 4

    buffer_size = 64000;

    inicio = time.time()
    file = open(path, "rb")
    data = file.read(buffer_size)

    actual = 0
    while (data):
        if (server.sendto(data, addr)):
            actual += 0.0625
            print(f"Enviando al cliente {numCliente} ... " + str(round(actual, 3)) + " MB")
            data = file.read(buffer_size)
    file.close()

    fin = time.time()

    tiempo = fin - inicio


    fname = f"Cliente{numCliente}-Prueba-{nThreads}"

    generarLog(addr, fsize, tiempo, fname, numCliente)


def main():
    host_ip = "localhost"
    port = 8081

    print("[*] Iniciando servidor ...")
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # *************************** Archivos del servidor ********************************
    print("Archivo tipo 1: 100 MB")
    print("Archivo tipo 2: 250 MB")
    arch = input("[/] Seleccione el tipo de archivo a enviar: (1 o 2)\n>>> ")

    path = "archivosServidor/"
    if not os.path.isdir(path):
        os.mkdir(path)

    if (arch == "1"):
        path += "archivo1.txt"
        crearArchivo(path, 100)
    else:
        path += "archivo2.txt"
        crearArchivo(path, 250)

    # * Numero de threads server
    nThreads = int(input("Ingrese el número de threads: "))

    server.bind((host_ip, port))
    print("[*] El servidor está escuchando en el puerto {p}.".format(p=port))

    # ** Manejo de los clientes
    id_client = 1;
    while True:
        data, addr = server.recvfrom(4096)  # Mensaje de listo del cliente y el ip con el estado
        print(f"Cliente numero: {id_client} {data.decode()}")
        thread = Thread(target=operate, args=(server, addr, path, nThreads, id_client))

        threads.append(thread)

        if (id_client == nThreads):
            for thr in threads:
                thr.start()
            break

        id_client += 1


if __name__ == "__main__":
    main()