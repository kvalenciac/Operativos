#Autores: Katherin Valencia - Santiago Bedoya

import socket
import threading
import sys
import pickle

class Cliente():
  def __init__(self, host='localhost', port=4000):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.connect((host, port))

    message_recive = threading.Thread(target=self.message_recive)
    message_recive.daemon = True
    message_recive.start()  

    self.download_path = ''

    while True:  

      message = input('''
        ¿Qué quiere hacer? 
          crear <nameCarpeta> -> Crear una nueva carpeta
          delete <nameCarpeta> -> Eliminar una carpeta
          ls -> Listar las carpetas  existentes
          ls <nameCarpeta> -> Listar los archivos existentes en una carpeta
          cargar <nameCarpeta> <fullFilePath> -> Cargar un archivo a la carpeta
          descargar <carpetaPath> <downloadPath> -> Descargar archivo de la carpeta
          eliminar <carpetaPath> -> Eliminar un archivo de la carpeta
          lanzar <nameApp> -> Lanzar una nueva app
          detener <nameApp> -> Detener una app
          salir -> Cerrar la conexion 
        Elije una opción: 
      ''').split(' ')

      if message[0] in ['crear', 'delete', 'ls', 'cargar', 'descargar', 'eliminar', 'lanzar', 'detener', 'salir']:
        if message[0] != 'salir':
          self.send_msg(message)
          if message[0] == 'cargar':
            if len(message) == 3:
              with open(message[2], 'rb') as file:
                message.append({"name": message[2].split('\\')[-1], "data": file.readlines()})
            elif len(message) == 2:
              print('Se necesita un archivo')
            else:
              print('Se necesita una carpeta')
              continue
          if message[0] == 'descargar':
            self.download_path = message[2]
          self.send_msg(message)
        else: 
          self.socket.close()
          sys.exit()
      else:
        print('La opción no es válida, intente de nuevo')
  
  def message_recive(self):
    while True:
      try:
        data = self.socket.recv(1024)
        recive = pickle.loads(data)
        if isinstance(recive, dict):
          with open(f'{self.download_path}/{recive["name"]}', 'wb') as file:
            file.writelines(recive["data"])
            self.download_path = ''
            continue
        print(recive) if data != None else None
      except:
        pass
  
  def send_msg(self, message):
    self.socket.send(pickle.dumps(message))

if __name__ == '__main__': 
    Cliente() 
