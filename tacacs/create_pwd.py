import os


def create_tac_pwd(pwd_raw):

    pwd_file = "/tmp/pwd.tmp"

    f = open(pwd_file, "w")
    f.write(pwd_raw + "\n")
    f.close()

    pwd = os.popen("openssl passwd -crypt -in " + pwd_file).read().split("\n")

    os.remove(pwd_file)

    return pwd[0]
