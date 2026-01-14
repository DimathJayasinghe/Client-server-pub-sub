import socket
import sys

def start_server():
    # check port
    if len(sys.argv) !=2:
        print("Usage: python server.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    host = '0.0.0.0'

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.bind((host, port))
        server_socket.listen(1)   # only 1 connection at a time
        print("Server listening on port {}".format(port))
        

        conn, address = server_socket.accept()
        print("Connection from: {}".format(address))

        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break

            print("Received from client: {}".format(data))

            if data.strip().lower() == 'terminate':
                print("Termination command received. Closing connection.")
                break

        conn.close()
        
    except Exception as e:
        print("An error occurred: {}".format(e))
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
            