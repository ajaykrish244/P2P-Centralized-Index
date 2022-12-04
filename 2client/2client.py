import socket
import platform
import threading
import os
import datetime 
import pytz
from pathlib import Path

clientname = 'rahul'
# data = {
#         '0791':'Internet Protocol',
#         '0792':'Internet Control Message Protocol'
#     }


def add_method(server,key,data):
    dat = f"ADD {key} P2P-CI/1.0\nHost: {clientname}\nPort: {p2psockname}\nTitle: {data}\n\n"
    print(f"sent{dat}")
    server.send(bytes(dat,'utf-8'))

def list_method(server):
    dat = f"LIST ALL P2P-CI/1.0\nHost: {clientname}\nPort: {p2psockname}\n\n"
    server.send(bytes(dat,'utf-8'))

def lookup_method(server,key):
    dat = f"LOOKUP {key} P2P-CI/1.0\nHost: {clientname}\nPort: {p2psockname}\n\n"
    server.send(bytes(dat,'utf-8'))

def request(key,port,server):
    ss=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    ss.connect((socket.gethostname(), port))
    o_s=platform.system()
    dat = f"GET {key} P2P-CI/1.0\nHost: {clientname}\nOS: {o_s}\n\n"
    ss.send(bytes(dat,'utf-8')) 
    temp = ss.recv(16048, socket.MSG_PEEK)
    length = temp.find(b'\n\n')
    msg=str(ss.recv(length+2),encoding='utf-8')
    print(msg)
    lines=msg.split('\n')
    l1=lines[1]
    l1=lines[0].split(" ")
    rfcnum = l1[3]
    rfctitle=l1[1][5:]
    print(lines)
    l5=lines[5]
    with open(f"./1client/{rfcnum} {rfctitle}", 'w') as f:
        f.write(l5)
    #parse the response to make sense
    # recieved data = conn.recv(2048)
    add_method(server,rfcnum,rfctitle)

def GET(msg):
    #parse RFC number and return
    lines=msg.split('\n')
    l1=lines[0].split(" ")
    return l1[1],l1[2]

def response(cs,ip):
    print(cs)
    client_port = None
    client_port=str(cs.getpeername()[1]-1)
    try:
        p2p_file=''
        c=0
        while True:
            # cs.send(bytes(input('Enter msg:'),'utf-8'))
            temp = cs.recv(2048, socket.MSG_PEEK)
            length = temp.find(b'\n\n')
            msg=str(cs.recv(length+2),encoding='utf-8')
            print(msg)
            if msg[:2] == 'GE':
                rfcreq,version = GET(msg)
                list_of_files = os.listdir("./2client") #list of files in the current directory
                if(str.isnumeric(rfcreq)==False):
                    data="400 Bad Request"
                elif(version!='P2P-CI/1.0'):
                    data="505 P2P-CI Version Not Supported"
                else:
                    for each_file in list_of_files:
                        if each_file.startswith(str(rfcreq)):  #since its all type str you can simply use startswith
                            c=c+1
                            p2p_file=each_file
                    if(c==0):
                        data="404 Not Found"
                    else:
                        current_data_time=datetime.datetime.now(pytz.timezone('America/New_York'))
                        o_s=platform.system()
                        with open(f'./2client/{p2p_file}',"r") as f: 
                            content_length=len(f.readlines())
                        txt = Path(f'./2client/{p2p_file}').read_text()
                        txt=txt.replace('\n', ' ')
                        p2p_reponse=f"P2P-CI/1.0 200 OK {rfcreq}\n{p2p_file}\nDate: {current_data_time}\nOS: {o_s}\nContent-Length: {content_length}\nContent-Type: Text/Text\n{txt}\n\n"
                        data = p2p_reponse
                print(data)
                cs.send(bytes(data,'utf-8'))
            else:
                # Bad request response and other methods
                pass     
    except(ConnectionError or ConnectionResetError or ConnectionAbortedError):
        print(f'\n\n\nError client {client_port}\n\n\n')
        cs.close()



if __name__=='__main__':
    data = {}
    for x in os.listdir("./2client"):
        print(x)
        if x.endswith('.txt'):
            x=x[:len(x)-4]
            data[x[0:4]]=x[5:]
    print(data)
    p2p = socket.socket()
    clientip=socket.gethostbyname(socket.gethostname())
    p2p.bind((clientip,0))
    p2psockname = p2p.getsockname()[1]
    p2p.listen(5)

    def ptop():
        while True:
            print('Server listening')
            cs,ip=p2p.accept()
            # connect_new_client,(cs,ip)
            threading._start_new_thread(response,(cs,ip))

    def ptos():
        global data
        print(f"hi\n{data}")
        server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server.connect((socket.gethostname(), 7734))
        print(f'Connted to server {server.getsockname()} {server.getpeername()}')
        for key,value in data.items():
            add_method(server,key,value)  
        while True:
            # server.send(bytes("recieved",'utf-8'))
            # temp = server.recv(2048, socket.MSG_PEEK)
            # length = temp.find(b'\n\n')
            # msg=str(server.recv(length+2),encoding='utf-8')
            a = int(input('Enter Lookup(1)/List(2)/Get(3):'))
            if a == 1:
                key = input('Enter RFC number to search:')
                lookup_method(server,key)
                print(data:=server.recv(2048))
            elif a==2:
                list_method(server)
                print(data:=server.recv(2048))
            elif a==3:
                key=input("Enter RFC file to recieve:")
                clientport=int(input("Enter Client port to request transfer:"))
                request(key,clientport,server)

    t1 = threading.Thread(target =ptop)
    t2 = threading.Thread(target =ptos)
    t1.start()
    t2.start()    