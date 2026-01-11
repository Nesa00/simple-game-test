"""
Network Client
Handles connection to game server and data synchronization.
"""

import socket
import threading
import pickle
import time


class NetworkClient:
    """Manages client-server communication."""
    
    def __init__(self):
        self.socket = None
        self.connected = False
        self.running = False
        self.players = {}
        self.player_name = "Player"
        self.lock = threading.Lock()
        self.receive_thread = None
        self.connection_error = None
    
    def connect(self, host, port, username):
        """
        Connect to game server.
        
        Args:
            host: Server IP address
            port: Server port
            username: Player name
            
        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        try:
            # Close existing connection if any
            if self.socket:
                self.disconnect()
            
            # Create new socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)  # 5 second timeout for connection
            
            # Try to connect
            print(f"Connecting to {host}:{port}...")
            self.socket.connect((host, port))
            self.socket.settimeout(None)  # Remove timeout after connection
            
            self.connected = True
            self.running = True
            self.player_name = username
            self.connection_error = None
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_data, daemon=True)
            self.receive_thread.start()
            
            print(f"Connected to server at {host}:{port}")
            return (True, None)
            
        except socket.timeout:
            self.connected = False
            error_msg = "Connection timeout - server not responding"
            print(f"Connection failed: {error_msg}")
            return (False, error_msg)
            
        except ConnectionRefusedError:
            self.connected = False
            error_msg = "Connection refused - server not running"
            print(f"Connection failed: {error_msg}")
            return (False, error_msg)
            
        except Exception as e:
            self.connected = False
            error_msg = f"Connection error: {str(e)}"
            print(f"Connection failed: {error_msg}")
            return (False, error_msg)
    
    def disconnect(self):
        """Disconnect from server."""
        print("Disconnecting from server...")
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        # Wait for receive thread to finish
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=1)
        
        with self.lock:
            self.players = {}
        
        print("Disconnected")
    
    def _receive_data(self):
        """Background thread to receive game state from server."""
        while self.running and self.connected:
            try:
                data = self.socket.recv(4096)
                if not data:
                    print("Server closed connection")
                    self.connected = False
                    self.connection_error = "Server closed connection"
                    break
                
                # Deserialize player data
                with self.lock:
                    self.players = pickle.loads(data)
                    
            except ConnectionResetError:
                print("Connection reset by server")
                self.connected = False
                self.connection_error = "Connection lost"
                break
                
            except Exception as e:
                if self.running:  # Only log if not intentionally disconnecting
                    print(f"Receive error: {e}")
                    self.connected = False
                    self.connection_error = f"Network error: {str(e)}"
                break
        
        print("Receive thread stopped")
    
    def send_input(self, input_state):
        """
        Send player input to server.
        
        Args:
            input_state: dict with keys like {"w": bool, "a": bool, "s": bool, "d": bool, "name": str}
            
        Returns:
            bool: True if sent successfully
        """
        if not self.connected or not self.socket:
            return False
        
        try:
            # Add player name to input
            input_state["name"] = self.player_name
            
            # Serialize and send
            data = pickle.dumps(input_state)
            self.socket.sendall(data)
            return True
            
        except Exception as e:
            print(f"Send error: {e}")
            self.connected = False
            self.connection_error = "Failed to send data"
            return False
    
    def get_players(self):
        """
        Get current player positions.
        
        Returns:
            dict: {player_id: {"x": x, "y": y, "name": name}}
        """
        with self.lock:
            return self.players.copy()
    
    def is_connected(self):
        """Check if connected to server."""
        return self.connected
    
    def get_error(self):
        """Get last connection error message."""
        return self.connection_error
