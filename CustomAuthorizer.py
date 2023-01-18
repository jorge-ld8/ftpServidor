from pyftpdlib.authorizers import DummyAuthorizer
import os
from pyftpdlib._compat import unicode


class CustomAuthorizer(DummyAuthorizer):
    """
    Custom authorizer to add functionality for
    password change
    """
    def __init__(self):
        self.admins_table = [{'user': 'admin', 'password': 'admin123'}, {'user': 'admin2', 'password': 'admin123'}]
        super().__init__()

    def change_user_pwd(self, username, password):
        """
        Change user password by changing its entry in
        self.user_table
        """
        if self.has_user(username):
            self.user_table[username]['pwd'] = password
        else:
            raise ValueError(f'user {username} does not exist')

    def add_user(self, username, password, limit=1024, perm='elr',
                 msg_login="Login successful.", msg_quit="Goodbye."):
        """Add a user to the virtual users table.
        AuthorizerError exceptions raised on error conditions such as
        invalid permissions, missing home directory or duplicate usernames.
        Optional perm argument is a string referencing the user's
        permissions explained below:
        Read permissions:
         - "e" = change directory (CWD command)
         - "l" = list files (LIST, NLST, STAT, MLSD, MLST, SIZE, MDTM commands)
         - "r" = retrieve file from the server (RETR command)
        Write permissions:
         - "a" = append data to an existing file (APPE command)
         - "d" = delete file or directory (DELE, RMD commands)
         - "f" = rename file or directory (RNFR, RNTO commands)
         - "m" = create directory (MKD command)
         - "w" = store a file to the server (STOR, STOU commands)
         - "M" = change file mode (SITE CHMOD command)
         - "T" = update file last modified time (MFMT command)
        Optional msg_login and msg_quit arguments can be specified to
        provide customized response strings when user log-in and quit.
        """
        if os.name == "posix":
            homedir = os.getcwd() + "/" + "FtpServerGenesis" "/" + username
        else:
            homedir = os.getcwd() + "\\" + "FtpServerGenesis" + "\\" + username
        if self.has_user(username):
            raise ValueError('user %r already exists' % username)
        if not isinstance(homedir, unicode):
            homedir = homedir.decode('utf8')
        if not os.path.isdir(homedir):
            os.mkdir(os.path.realpath(homedir))
        homedir = os.path.realpath(homedir)
        self._check_permissions(username, perm)
        dic = {'pwd': str(password),
               'home': homedir,
               'limite': str(limit),
               'perm': perm,
               'operms': {},
               'msg_login': str(msg_login),
               'msg_quit': str(msg_quit),
               }
        print(username)
        print(dic.keys())
        self.user_table[username] = dic