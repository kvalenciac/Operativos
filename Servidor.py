#Autores: Katherin Valencia - Santiago Bedoya

import socket
import threading
import sys
import pickle
import os
import shutil
from time import *
from datetime import datetime

class Servidor():

  def __init__(self, host='localhost', port=4000):
    self.crearCarpeta('Clientes')
    self.clientes = []

    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.bind((host, port))
    self.socket.listen(10)
    self.socket.setblocking(False)

    aceptar = threading.Thread(target=self.aceptar_conexion)
    procesar = threading.Thread(target=self.procesar_conexion)

    aceptar.daemon = True
    procesar.daemon = True

    aceptar.start()
    procesar.start()

    while True:
      msg = input('>')
      if msg == 'salir':
        self.socket.close()
        sys.exit()

  def traerLog(self):
    self.t = datetime.now()
    self.time = 'LOG: ' + str(self.t.day) + '/' + str(self.t.month) + '/' + str(self.t.year) + '-' + str(self.t.hour) + ':' + str(self.t.minute)
    print (self.time)
    return

  def ejecutar(self, data, clienteActual):
    for cliente in self.clientes:
      try:
        if cliente[0] == clienteActual[0]:
          if data[0] == 'ls':
            path = f'clientes/{clienteActual[1][1]}/{data[1] if len(data) > 1 else ""}'
            self.traerLog()
            self.send_msg(clienteActual[0], self.list(path))
          elif data[0] == 'crear':
            if len(data) > 1:
              if data[1] not in self.list('clientes/'):
                self.crearCarpeta(f'clientes/{clienteActual[1][1]}/{data[1]}')
                self.traerLog()
                self.send_msg(clienteActual[0], f'{data[1]} creado')
              else:
                self.traerLog()
                self.send_msg(clienteActual[0], f'{data[1]} ya existe')
            else:
              self.traerLog()
              self.send_msg(clienteActual[0], "No se puede crear una carpeta sin nombre")
          elif data[0] == 'delete':
            if len(data) > 1:
              self.deleteCarpeta(f'clientes/{clienteActual[1][1]}/{data[1]}')
              self.traerLog()
              self.send_msg(clienteActual[0], f'{data[1]} eliminado')
            else:
              self.traerLog()
              self.send_msg(clienteActual[0], "No se puede eliminar una carpeta sin un nombre")
          elif data[0] == 'cargar':
            with open(f'clientes/{clienteActual[1][1]}/{data[1]}/{data[3]["name"]}.KS', 'wb') as file:
              pickle.dump(data[3], file)
              self.traerLog()
              self.send_msg(clienteActual[0], f'{data[3]["name"]} cargado')
          elif data[0] == 'descargar':
            with open(f'clientes/{clienteActual[1][1]}/{data[1]}.KS', 'rb') as file:
              file_data = pickle.load(file)
              self.traerLog()
              self.send_msg(clienteActual[0], dict(file_data))
          elif data[0] == 'eliminar':
            self.eliminarArchivo(f'{self.pwd()}/clientes/{clienteActual[1][1]}/{data[1]}.KS'.replace('/', '\\'))
            self.traerLog()
            self.send_msg(clienteActual[0], 'Archivo eliminado')
          elif data[0] == 'lanzar':
            self.lanzarApp(f'{self.pwd()}/clientes/{clienteActual[1][1]}/{data[1]}.KS'.replace('/', '\\'))
            self.traerLog()
            self.send_msg(clienteActual[0], 'App lanzada')
          elif data[0] == 'detener':
            self.eliminarArchivo(f'{self.pwd()}/clientes/{clienteActual[1][1]}/{data[1]}.KS'.replace('/', '\\'))
            self.traerLog()
            self.send_msg(clienteActual[0], 'App detenida')
        else:
          continue
      except:
        pass

  def send_msg(self, client, message):
    client.send(pickle.dumps(message))

  def aceptar_conexion(self):
    print('Aceptando Conexión...')
    while True:
      try:
        conn, address = self.socket.accept()
        conn.setblocking(False)
        self.crearCarpeta(f'clientes/{address[1]}')
        self.clientes.append((conn, address))
      except:
        pass

  def procesar_conexion(self):
    print('Procesando la conexión...')
    while True:
      if len(self.clientes) > 0:
        for client in self.clientes:
          try:
            data = pickle.loads(client[0].recv(1024))
            self.ejecutar(data, client) if data != None else None
          except:
            pass

  def list(self, address):
    try:
      lt = os.listdir(address)
      for i in range(len(lt)):
        lt[i] = lt[i].replace('.KS', '')
      return lt
    except OSError as OSe:
      print(f'Error: {OSe.filename} - {OSe.strerror}')
      return False
  
  def crearCarpeta(self, name):
    try:
      os.mkdir(name)
      return True
    except OSError as OSe:
      return OSe.filename, OSe.strerror

  def eliminarArchivo(self, fileName):
    try:
      os.remove(fileName)
      return True
    except OSError as OSe:
      print(f'Error: {OSe.filename} - {OSe.strerror}')
      return False

  def lanzarApp(self, fileName):
    try:
      file = open(fileName, "w")
      file.close()
      return True
    except OSError as OSe:
      print(f'Error: {OSe.filename} - {OSe.strerror}')
      return False

  def deleteCarpeta(self, CarpetaName):
    try:
      shutil.rmtree(CarpetaName)
      return True
    except OSError as OSe:
      print(f'Error: {OSe.filename} - {OSe.strerror}')

  def pwd(self):
    return os.getcwd()

if __name__ == '__main__': 
    Servidor() 