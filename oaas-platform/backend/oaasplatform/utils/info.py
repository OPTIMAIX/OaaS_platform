import urllib.request
import platform
import psutil

def get_ip_public():
    external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    return external_ip

def get_cpu():
    cpu = platform.system()
    return cpu

def get_ram():
    ram = str(round(psutil.virtual_memory().total / (1024.0 **3)))+" GB"
    return ram
