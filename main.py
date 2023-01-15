import os
from pyftpdlib.servers import FTPServer
from CustomAuthorizer import CustomAuthorizer
from CustomFTPHandler import MyHandler
import threading
import _thread as thread
from FtpServer import FtpServerRedes2
import sys
from tkinter import *


myftpserver = FtpServerRedes2()


def menumanejoservidor():
    while True:
        print("Introduzca el numero segun la opcion")
        print("\t1.Agregar usuario")
        print("\t2.Eliminar usuario")
        print("\t3.Ver usuarios")
        print("\t4.Modificar almacenamiento de usuario")
        print("\t0.Salir")
        resp = input("\tOpcion: ")
        if resp == "1":
            nombre = input("Introduzca nombre del usuario: ")
            pswd = input("Introduzca la contraseña: ")
            pswd2 = input("Vuelva a introducir la contraseña: ")
            if pswd == pswd2:
                try:
                    myftpserver.add_user(nombre, pswd, os.getcwd() + "/" + nombre, "elradfmwMT")
                except ValueError:
                    print("No se pudo agregar al usuario. Intente nuevamente.")
            else:
                print("Contraseñas no coinciden. Intente nuevamente")
        elif resp == "2":
            nombre = input("Introduzca nombre del usuario: ")
            try:
                myftpserver.remove_user(nombre)
                print("Usuario removido exitosamente!")
            except ValueError:
                print("User not found")
        elif resp == "3":
            myftpserver.imprimirUsuarios()
        elif resp == "4":
            user = input("Introduzca el usuario: ")
            newsize = int(input("Introduzca el nuevo almacenamiento (en MB): "))
            try:
                myftpserver.cambiaralmacenamiento(user, newsize)
                print("Almacenamiento cambiado exitosamente")
            except ValueError as error:
                print(error)
        elif resp == "0":
            return


def main():
    # set a limit for connections

    while True:
        print("Bienvenido al Manejador del Servidor FTP")
        print("\t1.Iniciar Servidor")
        print("\t2.Detener Servidor")
        print("\t3.Opciones de manejo")
        print("\t0.Salir")
        opcion = input("\tIntroduzca la opcion: ")
        if opcion == "1":
            mythread = threading.Thread(target=myftpserver.run)
            mythread.start()
            print("\nServidor iniciado exitosamente\n")
        elif opcion == "2":
            myftpserver.stop()
            print("\nServidor detenido exitosamente\n")
        elif opcion == "3":
            # start ftp server
            user = input("Introduzca su usuario: ")
            pswd = input("Introdzca su contraseña: ")
            if myftpserver.validarAdmin(user, pswd):
                menumanejoservidor()
            else:
                print("Usuario / contraseña incorrecta")
            # mythread2 = threading.Thread(target=menumanejoservidor)
            # mythread2.start()
        else:
            myftpserver.stop()  # temporal. Luego se deberia hacer por separado
            return



    # thread.start_new_thread(myftpserver.run, ())
    # thread.start_new_thread(myftpserver.add_user, ('user', 'password', ".", 'elradfmwM'))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
