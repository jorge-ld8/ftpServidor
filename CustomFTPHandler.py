import os
import shutil
from pyftpdlib.handlers import FTPHandler, _strerror
from CustomAuthorizer import CustomAuthorizer
from datetime import datetime


proto_cmds = FTPHandler.proto_cmds.copy()
# SITE PSWD command to let clients change its password
proto_cmds.update(
    {'SITE PSWD': dict(perm=None, auth=True, arg=True,
      help='Syntax: SITE PSWD <SP> oldpassword newpassword (change user\' password).')}
)

# SITE SHAREFILE command to change files from user's directories
proto_cmds.update(
    {'SITE SHAREFILE': dict(perm='r', auth=True, arg=True,
      help='Syntax: SITE SHAREFILE <SP> filepath user (share a file with another user).')}
)


class MyHandler(FTPHandler):
    """
    Custom FTP Handler por Proyecto Redes II
    """

    authorizer = CustomAuthorizer()
    proto_cmds = proto_cmds

    def _get_dir_size(self, path='.'):
        total = 0
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += self._get_dir_size(entry.path)
        return total

    def on_file_received(self, file):
        if (self.fs.getsize(file) + self._get_dir_size(self.authorizer.user_table[self.username]['home'])) > float(self.authorizer.user_table[self.username]['limite']):
           self.run_as_current_user(self.fs.remove, file)
           return

    def on_login(self, username):
        with open("usersReport.txt", "a+") as f:
            f.write(f'{username}, {datetime.now()}\n')

    def ftp_SITE_PSWD(self, line: str):
        """
        Change user password
        """
        try:
            if line.count(' ') != 1:
                raise ValueError('Invalid number of arguments')
            oldpassword, newpassword = line.split(' ')
            if not self.authenticated or not self.authorizer:
                msg = "Log in with USER and PASS first."
                self.respond("530 " + msg)
                return
            else:
                if oldpassword != self.password:
                    msg = "Old password is incorrect."
                    self.respond("530" + msg)
                    return
                else:
                    self.password = newpassword
                    self.authorizer.change_user_pwd(self.username, newpassword)
                    self.respond("200 User password succesfully changed")
                    self.log(f'SITE PSWD completed for USER \'{self.username}\'')
        except ValueError as err:
            self.respond(f'501 {err}.')

    def ftp_SITE_SHAREFILE(self, line: str):
        """
            Share file with another user
        """
        try:
            if line.count(' ') != 1:
                raise ValueError("Invalid number of arguments")
        except ValueError as err:
            self.respond(f'501 {err}')

        # Get filepath and user
        filepath, user = line.split(' ')

        # try:
        #     fd = open(f'{filepath}', 'r')
        # except (EnvironmentError, FileNotFoundError) as err:
        #     self.respond(f'550 {err}')
        #     return

        # Mover archivo
        try:
            if os.name == "nt":
                delimiter = "\\"
            else:
                delimiter = "/"
            drtry = shutil.copy(f'{filepath}', f'{os.getcwd()}{delimiter}FtpServerGenesis{delimiter}{user}')
        except OSError as err:
            self.respond(f' 550 {err}')
            return
        self.respond("200 Succesfully transmitted")
        self.log(f'SITE SHAREFILE completed for user \'{self.username}\' in path {drtry}')



