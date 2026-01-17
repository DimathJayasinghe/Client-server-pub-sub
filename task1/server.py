import socket
import sys
import threading

def handle_client(conn, address):
    print("[NEW CONNECTION]: {}".format(address))
    try:
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break

            print("Received from {}: {}".format(address, data))

            if data.strip().lower() == 'terminate':
                print("Termination command received from {}. Closing connection.".format(address))
                break

    except Exception as e:
        print("An error occurred with {}: {}".format(address, e))
    finally:
        conn.close()
        print("[DISCONNECTED]: {}".format(address))




def start_server():
    # check port
    if len(sys.argv) !=2:
        print("Usage: python server.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    host = '0.0.0.0'

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print("Server listening on port {}".format(port))
    while True:
        conn, address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, address))
        client_thread.start()

        print("Active connections: {}".format(threading.active_count() - 1))        

if __name__ == "__main__":
    start_server()
            