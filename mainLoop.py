from tkinter import *
from tkinter import ttk
from FtpServer import FtpServerRedes2
import threading
import sched, time
import datetime
import signal, sys
from pages import Page1, Page2, Page3


# Run server
def runServer(currLabel):
    threading.Thread(target=myFtpServer.run).start()
    btnStop.configure(state="normal")


def stopServer(currLabel):
    myFtpServer.stop()
    btnStop.configure(state="disabled")
    labelEstado.configure(text='00:00:00')


def changeTime():
    if myFtpServer.isrunning():
        currentTime = datetime.datetime.now() - myFtpServer.timerun
        labelEstado.configure(text=f'{str(int(currentTime.seconds/3600)).zfill(2)}:{str(int(int(currentTime.seconds/60) % 60)).zfill(2)}:{str(currentTime.seconds % 60).zfill(2)}')


def handler(signum, frame):
    print(f'Signal Recieved {datetime.datetime.now()}')
    changeTime()
    signal.setitimer(signal.ITIMER_REAL, 1)


# Servidor FTP subclase del FTPServer() de pyftpdlib by giampaolo
myFtpServer = FtpServerRedes2()

# Constantes
COLUMN_SIZE = 200
ROW_SIZE = 60

# Scheduler
# myscheduler = sched.scheduler(time.time, time.sleep)
# myscheduler.enterabs(2, 0, action=changeTime

# root
root = Tk()
root.title("FTPServer")
root.geometry("600x600")

# Main Frame
mainView = Frame(root)
mainView.pack(side="top", expand=True)
p1 = Page1()
p2 = Page2()
p3 = Page3()

topFrame = Frame(mainView)
mainFrame = Frame(mainView)

p1.place(in_=mainFrame)
p2.place(in_=mainFrame)
p3.place(in_=mainFrame)

b1 = Button(topFrame, text="Page 1", command=p1.show)
b2 = Button(topFrame, text="Page 2", command=p2.show)
b3 = Button(topFrame, text="Page 3", command=p3.show)

b1.grid(column=0)
b2.grid(column=0)
b3.grid(column=0)

p1.show()

# loginFrame = Frame(mainFrame)


# Configuracion columnas
root.columnconfigure(0, minsize=COLUMN_SIZE)
root.columnconfigure(1, minsize=COLUMN_SIZE)
root.columnconfigure(2, minsize=COLUMN_SIZE)

# Configuracion filas
root.rowconfigure(0, minsize=60)
root.rowconfigure(1, minsize=60)
root.rowconfigure(2, minsize=60)

# Label titulo
labelTitulo = Label(root, text="Servidor FTP")
labelTitulo.grid(row=0, column=1, columnspan=1)

# Label estado
# datetime.datetime.now() - myFtpServer.timerun)
labelEstado = Label(root, text='00:00:00')
labelEstado.grid(row=2, column=1, columnspan=1)

# Boton de iniciar servidor
btnStart = Button(root, text="Start Server", command=lambda: runServer(labelEstado), fg="green",)
btnStart.grid(row=1, column=0)

# Boton de detener servidor
btnStop = Button(root, text="Stop Server", command=lambda: stopServer(labelEstado), fg="red", state=DISABLED)
btnStop.grid(row=1, column=2)

# Señales para actualizar el tiempo
signal.signal(signal.SIGALRM, handler=handler)
signal.setitimer(signal.ITIMER_REAL, 1)

# Loop principal que ejecuta la app
root.mainloop()
