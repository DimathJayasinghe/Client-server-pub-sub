import socket
import sys
def start_client():
    if len(sys.argv) != 3:
        print("Usage: python client.py <server_ip> <port>")
        sys.exit(1)

    server_ip = sys.argv[1]
    port = int(sys.argv[2])

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((server_ip, port))
        print("Connected to server at {}:{}".format(server_ip, port))
        print("Type your message (type 'terminate' to exit):")

        while True:
            message = input("You :> ")

            client_socket.send(message.encode('utf-8'))
            if message.strip().lower() == "terminate":
                print("Termination command sent. Closing connection.")
                break

    except ConnectionRefusedError:
        print("Could not connect to server at {}:{}".format(server_ip, port))
    except Exception as e:
        print("An error occurred: {}".format(e))
    finally:
        client_socket.close()

if __name__ == "__main__":
    start_client()
            