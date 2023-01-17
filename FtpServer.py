import csv
import datetime
import socket

from CustomAuthorizer import CustomAuthorizer
from CustomFTPHandler import MyHandler
from pyftpdlib.servers import FTPServer
import os
import logging
import shutil
from socket import gethostname, gethostbyname

class FtpServerRedes2:
    def __init__(self):
        self.handler = None
        self.server = None
        self.running = False  # if the server is running or not
        self.timerun = None
        self.authorizer = CustomAuthorizer()
        self.getUsers()

    def run(self):
        # Handler initialization
        self.handler = MyHandler
        self.handler.authorizer = self.authorizer
        self.handler.banner = 'Servidor FTP listo para la transferencia de archivos'
        self.handler.max_login_attempts = 3
        self.handler.masquerade_address = '151.25.42.11'
        self.handler.passive_ports = range(60000, 65535)

        # Server initialization

        # OPCION 1
        # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # s.connect(("8.8.8.8", 80))
        # ipaddress = s.getsockname()[0]
        # self.address = (ipaddress, 2121)

        # OPCION 2
        # self.address = (gethostbyname(gethostname()), 2121)
        self.address = ("localhost", 2121)
        self.server = FTPServer(self.address, self.handler)
        self.server.max_cons = 256
        self.server.max_cons_per_ip = 5
        logging.basicConfig(filename='pyftpd.log', level=logging.INFO)

        self.running = True
        self.timerun = datetime.datetime.today()
        self.server.serve_forever(timeout=10)


    def getUsers(self):
        with open("users.csv", "r+", newline='') as f:
            reader = csv.reader(f, delimiter=',')
            cont = 0
            for user in reader:
                cont += 1
                print(str(cont) + " " + user[0])
                print(self.authorizer.user_table.keys())
                if not user[0] in self.authorizer.user_table.keys():
                    self.authorizer.add_user(*user)
    def isrunning(self):
        return self.running

    def add_user(self, user, pswd, privi='elradfmwMT', limit=1024):
        self.authorizer.add_user(user, pswd, limit, perm=str(privi))

    def remove_user(self, user):
        if self.authorizer.has_user(user):
            shutil.rmtree(self.authorizer.user_table[user]['home'])
            self.authorizer.remove_user(user)
        else:
            raise ValueError("User not found")

    def _get_dir_size(self, path='.'):
        total = 0
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += self._get_dir_size(entry.path)
        return total

    def cambiaralmacenamiento(self, user, size):
        if self.authorizer.has_user(user) and size >= 1 and self._get_dir_size(self.authorizer.user_table[user]['home']) < size:
            self.authorizer.user_table[user]['limite'] = size * 1024
        elif not self.authorizer.has_user(user):
            raise ValueError(f'Usuario \'{user}\' no encontrado')
        elif size < 1:
            raise ValueError(f'Almacenamiento por usuario debe ser > 1MB')
        elif not self._get_dir_size(self.authorizer.user_table[user]['home']) < size:
            raise ValueError("El almacenamiento actual usado es mayor que el que se desea colocar como limite")

    def imprimirUsuarios(self):
        listausuarios = self.authorizer.user_table.keys()
        print("\nUSUARIOS")
        for username in listausuarios:
            usadomb = self._get_dir_size(self.authorizer.user_table[username]['home'])/1024
            limitemb = float(self.authorizer.user_table[username]["limite"])/1024
            print(f'+\t{username}', end="")
            print(f' {usadomb:.2f}KB', end="")
            print(f' / {limitemb}KB')
        print("\n")

    def stop(self):
        # Guardar todos los usuarios en el .txt users
        with open("users.csv", "w") as f:
            writer = csv.writer(f)
            print(self.authorizer.user_table.items())
            for user, userinfo in self.authorizer.user_table.items():
                o = userinfo.pop('operms')
                h = userinfo.pop('home')
                writer.writerow([user, * userinfo.values()])
                userinfo['operms'] = o
                userinfo['home'] = h
        self.server.close_all()
        self.running = False
        return

    def validarAdmin(self, username, pswd):
        for admin in self.authorizer.admins_table:
            if admin['user'] == username and admin['password'] == pswd:
                return True
        return False