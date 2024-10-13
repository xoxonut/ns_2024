import ssl
import socket
import subprocess
import threading
# sudo iptables -t nat -L PREROUTING -v -n --line-numbers

def add_iptables_rule():
    rule = (
        "iptables -t nat -A PREROUTING -s 192.168.75.129 "
        "-d 140.113.0.0/16 -p tcp --dport 443 -j REDIRECT --to-ports 443"
    )

    try:
        subprocess.run(rule, shell=True, check=True)
        print("iptables rule added successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error adding iptables rule: {e}")

def remove_iptables_rule():
    rule = (
        "iptables -t nat -D PREROUTING -s 192.168.75.129 "
        "-d 140.113.0.0/16 -p tcp --dport 443 -j REDIRECT --to-ports 443"
    )

    try:
        subprocess.run(rule, shell=True, check=True)
        print("iptables rule removed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error removing iptables rule: {e}")




def handle_co(client_socket):
    try:
        print('asd')
        client_socket.send(b"Hello, SSL client!")
        client_socket.close()
    except Exception as e:
        print(f"Error handling client connection: {e}")

def start_ssl_server():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="certificates/host.crt", keyfile="certificates/host.key")

    bind_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bind_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    bind_socket.bind(('0.0.0.0', 443))
    bind_socket.listen(5)
    print("SSL server listening on port 443")

    while True:
        try:
            client_socket, addr = bind_socket.accept()
            ssl_socket = context.wrap_socket(client_socket, server_side=True)
            print(f"Accepted connection from {addr}")
            external_ssock = create_ssl_connection()
            while True:
                data = external_ssock.recv(512)
                if not data:
                    break
                ssl_socket.sendall(data)
        except ssl.SSLError as e:
            print(f"SSL error occurred: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            external_ssock.close()
            ssl_socket.close()
            
def create_ssl_connection():
    # 連接到目標網站
    hostname = 'portal.nycu.edu.tw'
    port = 443

    # 創建一個 TCP/IP 套接字
    context = ssl.create_default_context()

    # 與服務器建立 TCP 連接
    external = None
    sock = socket.create_connection((hostname, port))
        # 將套接字升級為安全的 SSL 連接
        
    ssock = context.wrap_socket(sock, server_hostname=hostname)
    print(f"SSL connection established with {hostname}")
            
    
    ssock.sendall(b"GET / HTTP/1.1\r\nHost: portal.nycu.edu.tw\r\n\r\n")
            
            # 接收來自服務器的數據
    external_ssock = ssock
    return external_ssock



try:
    add_iptables_rule()
    start_ssl_server()
    
finally:
    remove_iptables_rule()