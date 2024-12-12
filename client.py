import json
import socket
from client_controller import Controller
from constants import *
from client_ui import UI
from PyQt5.QtWidgets import QApplication
import sys
from PyQt5.QtCore import QTimer, pyqtSignal, QObject, QThread

ALL_MOVES = [1, 2, 3, 4, 5, 6, 7, 8, 9]


class ServerListener(QObject):

    message_received = pyqtSignal(dict)
    client_connected = pyqtSignal(socket.socket)

    def __init__(self, host, port):
        super().__init__()
        print(f"Client.py :ServerListener initialized with host={host}, port={port}")
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.client.connect((host, port))  # Attempt to connect to the server
            print("Client.py :Connected to the server.")
            self.client_connected.emit(self.client)  # Emit the signal with the client socket
        except socket.error as e:
            print(f"Client.py :Failed to connect: {e}")
            self.client = None
            self.client_connected.emit(self.client)  # Emit with None if connection fails
        self.running = True

    def listen_to_server(self):
        if self.client:
            self.client_connected.emit(self.client)  # Emit once listener starts running
        try:
            buffer = ""
            while self.running:
                data = self.client.recv(1024)
                if not data:
                    self.running = False
                    break

                buffer += data.decode('utf-8')
                while "\n" in buffer:
                    message, buffer = buffer.split("\n", 1)
                    self.message_received.emit(json.loads(message))
        except Exception as e:
            print(f"Error in listener: {e}")

    def stop(self):
        """Stop the listener and close the socket."""
        self.running = False
        self.client.close()


class TicTacToeClient(QObject):

    def __init__(self, controller_class, host, port):

        super().__init__()
        self.controller = controller_class  # Create an instance of the Controller
        self.ui = None  # We'll initialize the UI later when the game starts
        self.client = None
        self.connection_established = False

        self.player = None
        self.opponent = None
        self.turn = None
        self.allowed_moves = []
        self.played_moves = []
        self.player_move = None
        self.move_sent = False
        self.opponent_move = None
        self.opponent_move_sent = False
        self.winner = None
        self.win_streak = []
        self.draw = None

        self.controller.player_changed.connect(self.update_player)
        self.controller.opponent_changed.connect(self.update_opponent)
        self.controller.turn_changed.connect(self.update_turn)
        self.controller.allowed_moves_changed.connect(self.update_allowed_moves)
        self.controller.played_moves_changed.connect(self.update_played_moves)
        self.controller.player_move_changed.connect(self.update_player_move)
        self.controller.move_sent_changed.connect(self.update_move_sent)
        self.controller.move_sent_changed.connect(self.handle_your_move)
        self.controller.opponent_move_changed.connect(self.update_opponent_move)
        self.controller.opponent_move_sent_changed.connect(self.update_opponent_move_sent)
        self.controller.draw_changed.connect(self.update_draw)
        self.controller.winner_changed.connect(self.update_winner)
        self.controller.win_streak_changed.connect(self.update_win_streak)

        self.listener_thread = QThread()
        self.listener = ServerListener(host, port)  # Create a listener
        print("Client.py :Connecting signals...")
        self.listener.message_received.connect(self.process_message)  # Connect to message handler
        print("Client.py :Connected listener.message_received to process_message.")
        self.listener.client_connected.connect(self.set_client_socket)  # New connection signal
        print("Client.py :Connected listener.client_connected to set_client_socket.")
        self.listener.moveToThread(self.listener_thread)
        self.listener_thread.started.connect(self.listener.listen_to_server)
        print("Client.py :Listener thread setup complete. Starting thread...")
        self.listener_thread.start()

    def set_client_socket(self, client_socket):
        """Set the client socket when the connection is established."""
        if client_socket:  # Check if the socket is not None
            self.client = client_socket
            self.connection_established = True
            print("Client.py :Client socket set:", self.client)
        else:
            print("Client.py :Connection failed. Client socket is None.")

    def update_player(self):
        self.player = self.controller.get_attribute('player')
        print(f"Client.py : Player updated to: {self.player}")

    def update_opponent(self):
        self.opponent = self.controller.get_attribute('opponent')
        print(f"Client.py :Opponent updated to: {self.opponent}")

    def update_turn(self):
        self.turn = self.controller.get_attribute('turn')
        print(f"Client.py :Turn updated to: {self.turn}")

    def update_allowed_moves(self):
        self.allowed_moves = self.controller.get_attribute('allowed_moves')
        print(f"Client.py :Allowed moves updated to: {self.allowed_moves}")

    def update_played_moves(self):
        self.played_moves = self.controller.get_attribute('played_moves')
        print(f"Client.py :Played moves updated to: {self.played_moves}")

    def update_player_move(self):
        print(f"update_player() called: Controller player is {self.controller.get_attribute('player')}")
        self.player_move = self.controller.get_attribute('player_move')
        print(f"Client.py :Player move updated to: {self.player_move}")

    def update_move_sent(self):
        self.move_sent = self.controller.get_attribute('move_sent')
        print(f"Client.py :Move sent updated to: {self.move_sent}")

    def update_opponent_move(self):
        self.opponent_move = self.controller.get_attribute('opponent_move')
        print(f"Client.py :Opponent move updated to: {self.opponent_move}")

    def update_opponent_move_sent(self):
        self.opponent_move_sent = self.controller.get_attribute('opponent_move_sent')
        print(f"Client.py :Opponent move sent updated to: {self.opponent_move_sent}")

    def update_draw(self):
        self.draw = self.controller.get_attribute('draw')
        print(f"Client.py :Draw updated to: {self.draw}")

    def update_winner(self):
        self.winner = self.controller.get_attribute('winner')
        print(f"Client.py :Winner updated to: {self.winner}")

    def update_win_streak(self):
        self.win_streak = self.controller.get_attribute('win_streak')
        print(f"Client.py :Win streak updated to: {self.win_streak}")

    def launch_ui(self):
        """Launch the game UI after connecting to the server and receiving the necessary data."""
        QTimer.singleShot(0, self._show_ui)

    def _show_ui(self):
        """Internal method to show the UI."""
        self.ui = UI(self.controller)
        self.ui.show()

    def process_message(self, message):
        """Process incoming messages from the server."""

        if message["subject"] == GAME_ON:
            self.launch_ui()

        if message["subject"] == PLAYER:
            self.player = message["data"]
            print(f"Client.py :you are player {self.player}")
            self.controller.set_attribute('player', self.player)
            print(f"Client.py :set controller player to {self.controller.get_attribute('player')}")
            self.opponent = 'O' if self.player == 'X' else 'X'
            self.controller.set_attribute('opponent', self.opponent)
            print(f"Client.py :set controller opponent to {self.controller.get_attribute('opponent')}")

        if message["subject"] == ALLOWED:
            self.allowed_moves = message["data"]
            self.controller.set_attribute('allowed_moves', self.allowed_moves)

        if message["subject"] == TURN:
            self.handle_turn(message["data"])

        if message["subject"] == OPP_MOVE:
            self.opponent_move = message["data"]
            print("Client.py :recieved opponent's move from server")
            self.controller.set_attribute('opponent_move', self.opponent_move)
            print(f"Client.py :opponent's move = {self.opponent_move}")
            print(f"Client.py :controller opp move = {self.controller.get_attribute('opponent_move')}")
            self.handle_opponent_move()

        if message["subject"] == GAME_OVER:
            if message["data"] == "d":
                self.controller.set_attribute('draw', True)
            else:
                message_info = message["data"].split('+')
                winner = message_info[0]
                self.controller.set_attribute('winner', winner)
                win_streak = message_info[1]
                self.controller.set_attribute('win_streak', win_streak)

    def handle_turn(self, data):
        if data:
            self.turn = True
            self.controller.set_attribute('turn', self.turn)
            self.handle_your_move()
        else:
            self.turn = False
            self.controller.set_attribute('turn', self.turn)
            # self.handle_opponent_move()

    def handle_your_move(self):
        print("Client.py :handle_your_move() called.")
        """Handles sending the move to the server."""
        if self.client and self.connection_established:
            print("Client socket is connected.")
            if self.controller.get_attribute('move_sent'):
                print("Client.py :move has been sent")
                self.player_move = self.controller.get_attribute('player_move')
                print(f"Client.py :player move is {self.player_move}")
                self.client.send(str(self.player_move).encode('utf-8'))  # Send move via the socket
                # self.turn = False
                # self.controller.set_attribute('turn', self.turn)
                print(f"Client.py :Move sent: {self.player_move}")
            else:
                print("Client.py :Move not yet sent.")
        else:
            print("Client.py :Client socket not connected yet.")

    def handle_opponent_move(self):
        print("Client.py :handle_opponent_move() called.")
        self.opponent_move = self.controller.get_attribute('opponent_move')
        print(f"Client.py :opponent move is {self.opponent_move}")
        self.opponent_move_sent = True
        self.controller.set_attribute('opponent_move_sent', self.opponent_move_sent)
        print(f"Client.py :opponent move sent = {self.opponent_move_sent}, controller opp move sent = {self.controller.get_attribute('opponent_move_sent')}")
        # self.turn = True
        # self.controller.set_attribute('turn', self.turn)


if __name__ == "__main__":  # Initialize client
    HOST = "127.0.0.1"  # Localhost
    PORT = 12345  # Random port
    controller = Controller()
    client = TicTacToeClient(controller, HOST, PORT)


    # Start the PyQt application
    app = QApplication(sys.argv)
    sys.exit(app.exec_())
