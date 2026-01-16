"""
Remote Controller Part for Donkeycar

Receives steering/throttle commands from a remote Python client via socket.
Save as: donkeycar/parts/remote_controller.py
"""
import socket
import struct
import json
import time
import threading
import logging

logger = logging.getLogger(__name__)


class RemoteController:
    """
    Receives steering and throttle commands from a remote client.
    Runs a TCP server that listens for commands.
    """
    def __init__(self, host='0.0.0.0', port=5001):
        """
        :param host: host to bind to (0.0.0.0 for all interfaces)
        :param port: port to listen on
        """
        self.host = host
        self.port = port
        self.running = True
        
        # Current commands (default to stop)
        self.steering = 0.0
        self.throttle = 0.0
        
        # Timeout - if no command received, stop the car
        self.last_command_time = time.time()
        self.timeout = 0.5  # seconds
        
        # Setup server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(1)
        self.server_socket.settimeout(1.0)
        
        self.client_socket = None
        
        logger.info(f"RemoteController listening on {host}:{port}")
    
    def update(self):
        """Threaded loop - accept connections and receive commands."""
        while self.running:
            # Accept new connection if needed
            if self.client_socket is None:
                try:
                    self.client_socket, addr = self.server_socket.accept()
                    self.client_socket.settimeout(0.1)
                    logger.info(f"Client connected: {addr}")
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.error(f"Accept error: {e}")
                    continue
            
            # Receive commands
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    logger.info("Client disconnected")
                    self.client_socket.close()
                    self.client_socket = None
                    self.steering = 0.0
                    self.throttle = 0.0
                    continue
                
                # Parse command (JSON format)
                cmd = json.loads(data.decode('utf-8'))
                self.steering = float(cmd.get('steering', 0.0))
                self.throttle = float(cmd.get('throttle', 0.0))
                self.last_command_time = time.time()
                
            except socket.timeout:
                pass
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON: {e}")
            except (ConnectionResetError, BrokenPipeError):
                logger.info("Client disconnected")
                self.client_socket.close()
                self.client_socket = None
                self.steering = 0.0
                self.throttle = 0.0
            except Exception as e:
                logger.error(f"Receive error: {e}")
    
    def run_threaded(self):
        """Return current steering and throttle."""
        # Safety timeout - stop if no recent commands
        if time.time() - self.last_command_time > self.timeout:
            return 0.0, 0.0
        
        return self.steering, self.throttle
    
    def run(self):
        """Non-threaded version."""
        return self.run_threaded()
    
    def shutdown(self):
        """Clean shutdown."""
        logger.info("RemoteController: shutting down")
        self.running = False
        self.steering = 0.0
        self.throttle = 0.0
        
        if self.client_socket:
            self.client_socket.close()
        self.server_socket.close()


class RemoteControllerUDP:
    """
    UDP version - lower latency, no connection overhead.
    """
    def __init__(self, host='0.0.0.0', port=5001):
        self.host = host
        self.port = port
        self.running = True
        
        self.steering = 0.0
        self.throttle = 0.0
        self.last_command_time = time.time()
        self.timeout = 0.5
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, port))
        self.socket.settimeout(0.1)
        
        logger.info(f"RemoteControllerUDP listening on {host}:{port}")
    
    def update(self):
        """Threaded loop - receive UDP commands."""
        while self.running:
            try:
                data, addr = self.socket.recvfrom(1024)
                cmd = json.loads(data.decode('utf-8'))
                self.steering = float(cmd.get('steering', 0.0))
                self.throttle = float(cmd.get('throttle', 0.0))
                self.last_command_time = time.time()
                
            except socket.timeout:
                pass
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON: {e}")
            except Exception as e:
                logger.error(f"UDP receive error: {e}")
    
    def run_threaded(self):
        """Return current steering and throttle."""
        if time.time() - self.last_command_time > self.timeout:
            return 0.0, 0.0
        return self.steering, self.throttle
    
    def run(self):
        return self.run_threaded()
    
    def shutdown(self):
        self.running = False
        self.steering = 0.0
        self.throttle = 0.0
        self.socket.close()
        logger.info("RemoteControllerUDP shutdown")