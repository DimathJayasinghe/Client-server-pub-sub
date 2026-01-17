import socket
import sys
import threading

# Global dictionary of subscribers: topic -> list of (conn, address)
subscribers = {}
subscribers_lock = threading.Lock()

def broadcast(message, sender_address, topic):
    """Sends a message to all registered subscribers of a specific topic."""
    with subscribers_lock:
        if topic in subscribers:
            to_remove = []
            for sub_conn, sub_addr in subscribers[topic]:
                try:
                    sub_conn.send("[Topic: {}][From {}]: {}".format(topic, sender_address, message).encode('utf-8'))
                except Exception:
                    to_remove.append((sub_conn, sub_addr))
            
            # Clean up broken connections
            for item in to_remove:
                subscribers[topic].remove(item)

def handle_client(conn, address):
    print("[NEW CONNECTION]: {}".format(address))
    try:
        # Initial registration message
        # Format: ROLE TOPIC
        registration_data = conn.recv(1024).decode('utf-8').strip()
        parts = registration_data.split()
        
        if len(parts) >= 2:
            role = parts[0].upper()
            topic = parts[1]
        else:
            role = "UNKNOWN"
            topic = "UNKNOWN"

        
        if role == 'SUBSCRIBER':
            with subscribers_lock:
                if topic not in subscribers:
                    subscribers[topic] = []
                subscribers[topic].append((conn, address))
            print("[SUBSCRIBER REGISTERED]: {} for topic {}".format(address, topic))
            # Wait for disconnection
            while True:
                if not conn.recv(1024):
                    break
        
        elif role == 'PUBLISHER':
            print("[PUBLISHER REGISTERED]: {} for topic {}".format(address, topic))
            while True:
                data = conn.recv(1024).decode('utf-8')
                if not data:
                    break

                print("Publisher {} [Topic: {}]: {}".format(address, topic, data))

                if data.strip().lower() == 'terminate':
                    print("Termination command received from {}. Closing connection.".format(address))
                    break
                
                # Broadcast message to all subscribers of the topic
                broadcast(data, address, topic)

        else:
            print("[INVALID REGISTRATION]: {} sent '{}'".format(address, registration_data))
            conn.send("ERROR: Invalid registration. Use 'PUBLISHER/SUBSCRIBER TOPIC'.".encode('utf-8'))

    except Exception as e:
        print("An error occurred with {}: {}".format(address, e))
    finally:
        with subscribers_lock:
            # Remove from subscribers if it was there
            # Iterate through all topics to find and remove the connection
            for topic_name, subs in subscribers.items():
                for i, (sub_conn, sub_addr) in enumerate(subs):
                    if sub_conn == conn:
                        subs.pop(i)
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
            