"""
Game Server
Manages multiplayer game sessions and synchronizes player positions.
"""

import socket
import threading
import pickle

# Server settings
HOST = '127.0.0.1'  # Listen on all interfaces
PORT = 50000

# Game state
players = {}  # {player_id: {"x": x, "y": y, "name": name}}
player_id_counter = 1
lock = threading.Lock()

# Game settings
PLAYER_SPEED = 5
INITIAL_X = 400
INITIAL_Y = 300


def handle_client(conn, addr, player_id):
    """
    Handle a single client connection.
    
    Args:
        conn: socket connection
        addr: client address
        player_id: unique player identifier
    """
    global players
    
    print(f"[NEW CONNECTION] Player {player_id} connected from {addr}")
    
    # Initialize player
    with lock:
        players[player_id] = {
            "x": INITIAL_X,
            "y": INITIAL_Y,
            "name": f"Player{player_id}"
        }
    
    try:
        while True:
            # Receive input from client
            data = conn.recv(1024)
            if not data:
                break
            
            # Deserialize input state
            input_state = pickle.loads(data)
            
            # Update player position based on input
            with lock:
                if player_id in players:
                    if input_state.get("w"):
                        players[player_id]["y"] -= PLAYER_SPEED
                    if input_state.get("s"):
                        players[player_id]["y"] += PLAYER_SPEED
                    if input_state.get("a"):
                        players[player_id]["x"] -= PLAYER_SPEED
                    if input_state.get("d"):
                        players[player_id]["x"] += PLAYER_SPEED
                    
                    # Update player name if provided
                    if input_state.get("name"):
                        players[player_id]["name"] = input_state["name"]
            
            # Send all player positions back to client
            with lock:
                conn.sendall(pickle.dumps(players))
    
    except ConnectionResetError:
        print(f"[CONNECTION RESET] Player {player_id} connection reset")
    except Exception as e:
        print(f"[ERROR] Player {player_id}: {e}")
    finally:
        # Remove player and close connection
        with lock:
            if player_id in players:
                del players[player_id]
        
        conn.close()
        print(f"[DISCONNECTED] Player {player_id} disconnected")
        print(f"[ACTIVE PLAYERS] {len(players)} player(s) remaining")


def start_server():
    """Start the game server."""
    global player_id_counter
    
    # Create socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind and listen
    server.bind((HOST, PORT))
    server.listen()
    
    print("=" * 60)
    print(f"[STARTED] Game server listening on {HOST}:{PORT}")
    print("=" * 60)
    print("Waiting for connections...")
    print()
    
    try:
        while True:
            # Accept new connection
            conn, addr = server.accept()
            
            # Assign player ID
            with lock:
                player_id = player_id_counter
                player_id_counter += 1
            
            # Start thread to handle this client
            thread = threading.Thread(
                target=handle_client,
                args=(conn, addr, player_id),
                daemon=True
            )
            thread.start()
            
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Server shutting down...")
    finally:
        server.close()
        print("[STOPPED] Server stopped")


if __name__ == "__main__":
    start_server()
