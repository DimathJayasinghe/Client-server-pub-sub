import socket
import sys
import threading

# Global list of subscribers
subscribers = []
subscribers_lock = threading.Lock()

def broadcast(message, sender_address):
    """Sends a message to all registered subscribers."""
    with subscribers_lock:
        to_remove = []
        for sub_conn, sub_addr in subscribers:
            try:
                sub_conn.send("[From {}]: {}".format(sender_address, message).encode('utf-8'))
            except Exception:
                to_remove.append((sub_conn, sub_addr))
        
        # Clean up broken connections
        for item in to_remove:
            subscribers.remove(item)

def handle_client(conn, address):
    print("[NEW CONNECTION]: {}".format(address))
    try:
        # Initial registration message
        role = conn.recv(1024).decode('utf-8').strip().upper()
        
        if role == 'SUBSCRIBER':
            with subscribers_lock:
                subscribers.append((conn, address))
            print("[SUBSCRIBER REGISTERED]: {}".format(address))
            # Wait for disconnection
            while True:
                if not conn.recv(1024):
                    break
        
        elif role == 'PUBLISHER':
            print("[PUBLISHER REGISTERED]: {}".format(address))
            while True:
                data = conn.recv(1024).decode('utf-8')
                if not data:
                    break

                print("Publisher {}: {}".format(address, data))

                if data.strip().lower() == 'terminate':
                    print("Termination command received from {}. Closing connection.".format(address))
                    break
                
                # Broadcast message to all subscribers
                broadcast(data, address)

        else:
            print("[INVALID ROLE]: {} attempted to join as {}".format(address, role))
            conn.send("ERROR: Invalid role. Use PUBLISHER or SUBSCRIBER.".encode('utf-8'))

    except Exception as e:
        print("An error occurred with {}: {}".format(address, e))
    finally:
        with subscribers_lock:
            # Remove from subscribers if it was there
            for i, (sub_conn, sub_addr) in enumerate(subscribers):
                if sub_conn == conn:
                    subscribers.pop(i)
                    break
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
            