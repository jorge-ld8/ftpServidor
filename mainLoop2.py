import os
import socket
from PyQt5 import QtWidgets, uic
from FtpServer import FtpServerRedes2
from PyQt5.QtWidgets import QFileSystemModel, QShortcut
import threading
from PyQt5 import QtGui
from PyQt5.QtGui import QIntValidator, QKeySequence


myftpserver = FtpServerRedes2()

# start app
app = QtWidgets.QApplication([])

# load .ui files
login = uic.loadUi("interfazServidor.ui")
mainPage = uic.loadUi("mainPageServidor.ui")
usersPage = uic.loadUi("usuarios.ui")
addUserPage = uic.loadUi("agregarUsuario.ui")
currUserPage = uic.loadUi("currUserPage.ui")
superUserPage = uic.loadUi("superUserPage.ui")


def gui_login():
    user = login.user.text()
    pswd = login.pswd.text()
    if len(user) == 0 or len(pswd) == 0:
        login.label.setText("Faltan datos. Intente nuevamente")
        login.user.setText("")
        login.pswd.setText("")
    elif myftpserver.validarAdmin(user, pswd):
        gui_getin()
    elif not myftpserver.validarAdmin(user, pswd):
        login.label.setText("Datos incorrectos intente nuevamente")
        login.user.setText("")
        login.pswd.setText("")


def gui_getin():
    superUserPage.hide()
    login.hide()
    mainPage.show()


def startServer():
    # myftpserver.getUsers()
    threading.Thread(target=myftpserver.run).start()
    mainPage.serverStatusLabel.setText("Server Active")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ipaddress = s.getsockname()[0]
    mainPage.ipLabel.setText("IP: " + ipaddress)
    mainPage.stopBtn.setEnabled(True)
    mainPage.startBtn.setEnabled(False)


def stopServer():
    myftpserver.stop()
    mainPage.serverStatusLabel.setText("Server not Active")
    mainPage.stopBtn.setEnabled(False)
    mainPage.startBtn.setEnabled(True)


def gui_users():
    currUserPage.hide()
    addUserPage.hide()
    mainPage.hide()
    usersPage.show()
    usersPage.usersList.clear()
    userslist: QtWidgets.QListWidget = usersPage.usersList
    userslist.setSpacing(5)
    for username, userinfo in myftpserver.authorizer.user_table.items():
        currItem = QtWidgets.QListWidgetItem(QtGui.QIcon("user.png"), username)
        userslist.addItem(currItem)
        userslist.itemClicked.connect(lambda it: gui_curr_user(it.text(), myftpserver.authorizer.user_table[it.text()]['pwd'],  myftpserver.authorizer.user_table[it.text()]['limite']))


def show_text(user):
    usersPage.label.setText(user.text())


def gui_curr_user(username, pswd, limite):
    usersPage.hide()
    currUserPage.show()
    limitEntry = currUserPage.limitEntry
    pswdEntry = currUserPage.pswdEntry

    # Colocar el limite actual
    limitEntry.setText(limite)
    pswdEntry.setText(pswd)
    currUserPage.currUserLabel.setText(username)


def backUsers():
    mainPage.show()
    usersPage.hide()


def gui_main_from_users():
    usersPage.hide()
    mainPage.show()


def gui_add_user():
    usersPage.hide()
    addUserPage.show()
    addUserPage.username.setText("")
    addUserPage.pswd1.setText("")
    addUserPage.pswd2.setText("")


def addUser():
    username = addUserPage.username.text()
    pswd1 = addUserPage.pswd1.text()
    pswd2 = addUserPage.pswd2.text()
    if pswd1 != pswd2:
        addUserPage.label.setText("Contraseñas no coinciden. Intente nuevamente")
        addUserPage.pswd1.setText("")
        addUserPage.pswd2.setText("")
    else:
        try:
            myftpserver.add_user(username, pswd1)
            gui_users()
        except ValueError:
            addUserPage.label.setText("Ocurrio un error intente nuevamente.")


def changeLimit():
    # Validador para los input fields
    limitEntry = currUserPage.limitEntry
    onlyInt = QIntValidator()
    onlyInt.setRange(1024, 10240)
    limitEntry.setValidator(onlyInt)
    username = currUserPage.currUserLabel.text()
    myftpserver.authorizer.user_table[username]['limite'] = str(limitEntry.text())
    gui_users()


def changePswd():
    pswdEntry = currUserPage.pswdEntry
    username = currUserPage.currUserLabel.text()
    myftpserver.authorizer.user_table[username]['pwd'] = str(pswdEntry.text())
    gui_users()


def deleteUser():
    myftpserver.remove_user(currUserPage.currUserLabel.text())
    gui_users()


def gui_superuser():
    mainPage.hide()
    superUserPage.show()
    model = QFileSystemModel()
    dirpath = os.getcwd() + "/FtpServerGenesis"
    model.setRootPath(dirpath)
    fileTree = superUserPage.estructuraDirectorios
    fileTree.setModel(model)
    fileTree.setRootIndex(model.index(dirpath))


def handle_salida():
    myftpserver.saveUsers()
    myftpserver.desconectarAdmin()
    login.show()
    mainPage.hide()
    login.user.setText("")
    login.pswd.setText("")


# Botones login
loginShortcut = QShortcut(QKeySequence("Return"), login)  # enter shortcut
loginShortcut.activated.connect(gui_login)
login.loginBtn.clicked.connect(gui_login)

# Botones pagina principal
mainPage.startBtn.clicked.connect(startServer)
mainPage.stopBtn.clicked.connect(stopServer)
mainPage.usersBtn.clicked.connect(gui_users)
mainPage.stopBtn.setEnabled(False)
mainPage.superUserBtn.clicked.connect(gui_superuser)
mainPage.salirBtn.clicked.connect(handle_salida)

# Botones ventana de usuario
usersPage.backBtnUsersPage.clicked.connect(gui_main_from_users)
usersPage.addUserBtnUsersPage.clicked.connect(gui_add_user)

# Botones ventana agregar usuario
addUserPage.addUserBtn.clicked.connect(addUser)
addUserPage.backBtn.clicked.connect(gui_users)

# Botones ventana usuario actual
currUserPage.changeLimitBtn.clicked.connect(changeLimit)
currUserPage.changePasswordBtn.clicked.connect(changePswd)
currUserPage.deleteUserBtn.clicked.connect(deleteUser)
currUserPage.backBtn.clicked.connect(gui_users)

# Botones ventana superusuario
superUserPage.backBtn.clicked.connect(gui_getin)

# execute
login.show()
app.exec()
