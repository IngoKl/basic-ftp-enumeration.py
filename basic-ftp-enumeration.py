#!/bin/python3

import sys
import socket
from ftplib import FTP
from ftplib import error_perm

try:
    host = sys.argv[1]
except:
    sys.exit('Please run: python ftp_enum IP [username] [password]')

log = []

server_software = ''
banner = ''
welcome = ''
username = 'anonymous'
password = 'anonymous@domain.local'
anonymous = False

try:
    username = sys.argv[2]
    password = sys.argv[3]
except:
    pass

def guess_server(banner):
    patterns = [
        ('Home Ftp Server', 'Home FTP Server'),
        ('FileZilla', 'FileZilla Server'),
        ('vsFTPd', 'vsFTPd'),
        ('Microsoft', 'Microsoft FTP Server')
    ]

    for pattern, server in patterns:
        if pattern in banner:
            server_software = server
            log.append(('Server Software (Guess)', server_software))

def print_log():
    print(f'== {host} ({username}:{password}) ==\n')
    for check, result in log:
        if type(result) == list:
            print(f'[+] {check}\n')
            for _ in result:
                print(_)
            print('\n')
        else:
            print(f'[+] {check}\n{result}\n')

# Banner
try:
    s = socket.socket()
    s.connect((host, 21))
    banner = str(s.recv(1024))
    log.append(('Banner', banner))

    # Use Banner
    guess_server(banner)
except:
    log.append(('Banner', 'No'))

# FTP Connectivity and Welcome
try:
    ftp = FTP(host)
    log.append(('FTP Connected', 'Yes'))

    welcome = str(ftp.getwelcome())
    log.append(('Welcome', welcome))

except:
    log.append(('FTP Connected', 'No'))
    print_log()
    sys.exit()

# Anonymous Login
with FTP(host) as ftp:
    try:
        response = ftp.login()
        anonymous = True
        log.append(('Anonymous Login', 'Yes'))
    except:
        log.append(('Anonymous Login', 'No'))

# FEAT
with FTP(host) as ftp:
    try:
        stat = str(ftp.sendcmd('FEAT').replace('\n', ''))
        log.append(('FEAT', stat))
    except:
        pass

# SYST
if anonymous == True or username != 'anonymous':
    with FTP(host) as ftp:
        try:
            ftp.login(username, password)
            stat = str(ftp.sendcmd('SYST'))
            log.append(('SYST', stat))
        except:
            pass

# Directory Listing
if anonymous == True or username != 'anonymous':
    with FTP(host) as ftp:
        try:
            ftp.login(username, password)
            ls = []
            ftp.dir(ls.append)
            log.append(('Directory Listing', ls))
        except error_perm:
            log.append(('Directory Listing', 'Permission Error'))
        except:
            log.append(('Directory Listing', 'Error'))

# Directory
if anonymous == True or username != 'anonymous':
    with FTP(host) as ftp:
        try:
            ftp.login(username, password)
            log.append(('Current Directory', str(ftp.pwd())))
        except:
            pass

# Directory Traversal
if anonymous == True or username != 'anonymous':

    targets = [
        'C:\\xampp\\passwords.txt',
        '..\\..\\..\\..\\..\\..\\Windows\\System32\\drivers\\etc\\hosts',
        'C:\\Windows\\System32\\drivers\\etc\\hosts',
        '/etc/passwd',
        '../../../../../etc/passwd'
    ]
    results = []

    with FTP(host) as ftp:
        ftp.login(username, password)

        for target in targets:
            try:
                size = ftp.size(target)
                results.append((target, f'Yes {size}'))
            except error_perm:
                results.append((target, f'No'))

        log.append(('Directory Traversal', results))

print_log()
