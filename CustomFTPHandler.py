import os
import shutil
from pyftpdlib.handlers import FTPHandler
from CustomAuthorizer import CustomAuthorizer

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

    def ftp_STOU(self, line):
        super().ftp_STOU(line)


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
            drtry = shutil.copy(f'{filepath}', f'/home/jorgegetsmad/PycharmProjects/pythonProject1/{user}')
        except OSError as err:
            self.respond(f' 550 {err}')
            return
        self.respond("200 Succesfully transmitted")
        self.log(f'SITE SHAREFILE completed for user \'{self.username}\' in path {drtry}')



