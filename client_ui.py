from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel
from PyQt5 import uic
import sys
from client_controller import Controller
from PyQt5.QtCore import QTimer


class UI(QMainWindow):

    def __init__(self, controller):
        super().__init__()

        self.controller = controller

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
        self.controller.turn_changed.connect(self.game_play)
        self.controller.allowed_moves_changed.connect(self.update_allowed_moves)
        self.controller.played_moves_changed.connect(self.update_played_moves)
        self.controller.player_move_changed.connect(self.update_player_move)
        self.controller.move_sent_changed.connect(self.update_move_sent)
        self.controller.opponent_move_changed.connect(self.update_opponent_move)
        self.controller.opponent_move_changed.connect(self.game_play)
        self.controller.opponent_move_sent_changed.connect(self.update_opponent_move_sent)
        self.controller.opponent_move_sent_changed.connect(self.game_play)
        self.controller.draw_changed.connect(self.update_draw)
        self.controller.winner_changed.connect(self.update_winner)
        self.controller.win_streak_changed.connect(self.update_win_streak)

        self.button_1 = None
        self.button_2 = None
        self.button_3 = None
        self.button_4 = None
        self.button_5 = None
        self.button_6 = None
        self.button_7 = None
        self.button_8 = None
        self.button_9 = None

        self.start_over_button = None
        self.label = None

        self.buttons_list = []
        self.block_dict = {}

        # Initialize the UI
        self.init_ui()

    def update_player(self):
        print(f"Client_UI.py :update_player() called: Controller player is {self.controller.get_attribute('player')}")
        self.player = self.controller.get_attribute('player')
        print(f"Client_UI.py :Player updated to: {self.player}")

    def update_opponent(self):
        self.opponent = self.controller.get_attribute('opponent')
        print(f"Client_UI.py :Opponent updated to: {self.opponent}")

    def update_turn(self):
        self.turn = self.controller.get_attribute('turn')
        print(f"Client_UI.py :Turn updated to: {self.turn}")

    def update_allowed_moves(self):
        self.allowed_moves = self.controller.get_attribute('allowed_moves')
        print(f"Client_UI.py :Allowed moves updated to: {self.allowed_moves}")

    def update_played_moves(self):
        self.played_moves = self.controller.get_attribute('played_moves')
        print(f"Client_UI.py :Played moves updated to: {self.played_moves}")

    def update_player_move(self):
        self.player_move = self.controller.get_attribute('player_move')
        print(f"Client_UI.py :Player move updated to: {self.player_move}")

    def update_move_sent(self):
        self.move_sent = self.controller.get_attribute('move_sent')
        print(f"Client_UI.py :Move sent updated to: {self.move_sent}")

    def update_opponent_move(self):
        self.opponent_move = self.controller.get_attribute('opponent_move')
        print(f"Client_UI.py :Opponent move updated to: {self.opponent_move}")

    def update_opponent_move_sent(self):
        self.opponent_move_sent = self.controller.get_attribute('opponent_move_sent')
        print(f"Client_UI.py :Opponent move sent updated to: {self.opponent_move_sent}")

    def update_draw(self):
        self.draw = self.controller.get_attribute('draw')
        print(f"Client_UI.py :Draw updated to: {self.draw}")

    def update_winner(self):
        self.winner = self.controller.get_attribute('winner')
        print(f"Client_UI.py :Winner updated to: {self.winner}")

    def update_win_streak(self):
        self.win_streak = self.controller.get_attribute('win_streak')
        print(f"Client_UI.py :Win streak updated to: {self.win_streak}")

    def init_ui(self):
        """Set up the UI components."""
        # Load the UI file
        try:
            uic.loadUi("toe_grid.ui", self)
            print("Client_UI.py :UI loaded successfully")
        except Exception as e:
            print(f"Client_UI.py :Error loading UI: {e}")

        # Define the buttons
        self.button_1 = self.findChild(QPushButton, "pushButton_1")
        self.button_2 = self.findChild(QPushButton, "pushButton_2")
        self.button_3 = self.findChild(QPushButton, "pushButton_3")
        self.button_4 = self.findChild(QPushButton, "pushButton_4")
        self.button_5 = self.findChild(QPushButton, "pushButton_5")
        self.button_6 = self.findChild(QPushButton, "pushButton_6")
        self.button_7 = self.findChild(QPushButton, "pushButton_7")
        self.button_8 = self.findChild(QPushButton, "pushButton_8")
        self.button_9 = self.findChild(QPushButton, "pushButton_9")

        self.label = self.findChild(QLabel, "label")
        self.turn = self.controller.get_attribute('turn')

        # Define block clicker action
        self.buttons_list = [
            self.button_1, self.button_2, self.button_3,
            self.button_4, self.button_5, self.button_6,
            self.button_7, self.button_8, self.button_9
        ]

        self.block_dict = {
            1: self.button_1,
            2: self.button_2,
            3: self.button_3,
            4: self.button_4,
            5: self.button_5,
            6: self.button_6,
            7: self.button_7,
            8: self.button_8,
            9: self.button_9
        }

        for button in self.buttons_list:
            button.clicked.connect(lambda _, b=button: self.game_play(b))

        if self.turn:
            self.enable_board()
            self.label.setText("Your turn")
        else:
            self.disable_board()
            self.label.setText("Opponent turn")

        # Show the UI
        self.show()

    def disable_board(self):
        for button in self.buttons_list:
            button.setEnabled(False)

    def enable_board(self):
        for n in self.controller.get_attribute('allowed_moves'):
            button = self.block_dict[n]
            button.setEnabled(True)

    def check_win_or_draw(self):
        print("check_win_or_draw() called")
        self.update_winner()

        if self.winner:
            print(f"{self.winner} = winner")
            self.update_win_streak()
            print(f"Win streak: {self.win_streak}")

            # Check if win_streak contains valid integers
            for n in self.win_streak:
                # Skip invalid or non-numeric values
                try:
                    n_int = int(n)  # Ensure that n is a valid number
                    button = self.block_dict[n_int]
                    print(f"button {n_int} = {button} ")
                    button.setStyleSheet('QPushButton {color: #FFD700;}')
                    print(f"button {n_int} color changed")
                except ValueError:
                    print(f"Invalid value in win_streak: {n}, skipping.")
                    continue

            self.label.setText(f"{self.winner} WON!")
            print("label changed")
            self.disable_board()
            return True
        print("no winner, checking draw")
        self.update_draw()
        if self.draw:
            print("draw = True")
            self.label.setText("It's a draw!")
            print("changed label")
            return True
        else:
            print("no win or draw")
            return False

    def game_play(self, button=None):

        if self.turn:
            self.enable_board()
            self.label.setText("Your turn")

            if button:
                self.your_move(button)

                print("player made move, check for win or draw")

                # Delayed check for win/draw after the signals have been processed
                if QTimer.singleShot(100, self.check_win_or_draw):  # Delay the check by 100ms
                    exit()
                else:
                    print("no win or draw - continue")

                    self.turn = False  # Immediately switch turn
                    self.controller.set_attribute('turn', self.turn)
                    self.disable_board()
                    self.label.setText("Opponent's turn")

        else:
            self.disable_board()
            self.label.setText("Opponent's turn")

            if self.opponent_move_sent:
                self.handle_opponent_move()
                print("player made move, check for win or draw")

                # Delayed check for win/draw after the signals have been processed
                if QTimer.singleShot(100, self.check_win_or_draw):  # Delay the check by 100ms
                    exit()
                else:
                    print("no win or draw - continue")
                    self.opponent_move_sent = False
                    self.controller.set_attribute('opponent_move_sent', self.opponent_move_sent)

    def your_move(self, button):
        self.update_player()
        print(f"Client_UI.py :Inside your_move: Player is {self.player}")
        button_number = int(button.objectName().replace('pushButton_', ""))
        print(f"Client_UI.py :player {self.player} chose {button_number}")
        self.controller.set_attribute('player_move', button_number)
        self.controller.set_attribute('move_sent', True)

        if self.player == 'X':
            button.setStyleSheet('QPushButton {color: #1f00ff;}')
        else:
            button.setStyleSheet('QPushButton {color: #ff0046;}')

        button.setText(self.player)
        self.turn = False
        self.controller.set_attribute("turn", self.turn)

    def handle_opponent_move(self):
        self.update_opponent()
        print(f"Client_UI.py :handle_opponent_move() called")

        self.opponent_move = self.controller.get_attribute('opponent_move')
        print(f"Client_UI.py :opp move is {self.opponent_move}")

        button = self.block_dict[int(self.opponent_move)]
        print(f"Client_UI.py :the button = {button}")

        if self.opponent == 'X':
            button.setStyleSheet('QPushButton {color: #1f00ff;}')
            print(f"Client_UI.py :opp button = blue")
        else:
            button.setStyleSheet('QPushButton {color: #ff0046;}')
            print(f"Client_UI.py :opp button = red")

        print(f"Client_UI.py :opponent mark = {self.opponent}")
        button.setText(self.opponent)
        print(f"Client_UI.py :made opp move to board")

        self.controller.set_attribute('move_sent', False)
        self.turn = True
        self.controller.set_attribute("turn", self.turn)


