import json
import socket
from constants import *

#mark constants
X = 'X'
O = 'O'

'''currently this version does not include check for winner'''

class TicTacToeServer:

    def __init__(self, HOST, PORT):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket created successfully for host.")
        self.server.bind((HOST, PORT))
        print(f"Socket bound to {HOST}:{PORT}")
        self.server.listen(2)
        print("Server listening for connections...")

        self.clients = []
        self.turn = None
        self.allowed_moves = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.block_dict = {
            1: "1",
            2: "2",
            3: "3",
            4: "4",
            5: "5",
            6: "6",
            7: "7",
            8: "8",
            9: "9"
        }
        self.counter = 0
        self.game_on = True
        self.current_player = None
        self.non_current_player = None

        self.accept_connections()

        self.game_loop()

    def accept_connections(self):
        while len(self.clients) < 2:
            connection, addr = self.server.accept()
            self.clients.append(connection)
            print(f"Client {addr} has connected")
        print("Two players have joined the game.")
        self.send_msg(PLAYER, X, self.clients[0])
        self.send_msg(PLAYER, O, self.clients[1])

    def broadcast(self, subject, msg):
        for c in self.clients:
            self.send_msg(subject, msg, c)

    def send_msg(self, subject, msg, c):
        message = {'subject': subject, 'data': msg}
        json_msg = json.dumps(message) + "\n"
        c.send(json_msg.encode('utf-8'))

    def make_move(self, move, player):
        move = int(move)
        self.block_dict[move] = X if player == self.clients[0] else O
        self.allowed_moves.remove(move)
        self.broadcast(ALLOWED, self.allowed_moves)

    def check_winner(self):
        print("Server.py = check_winner()")
        conditions = [
            [1, 2, 3], [4, 5, 6], [7, 8, 9],
            [1, 5, 9], [7, 5, 3],
            [1, 4, 7], [2, 5, 8], [3, 6, 9]
        ]

        for condition in conditions:
            if self.block_dict[condition[0]] == self.block_dict[condition[1]] == self.block_dict[condition[2]]:
                winner = self.block_dict[condition[0]]
                self.broadcast(GAME_OVER, f"{winner} + {condition}")
                print(f"Server.py : bc {winner} won with {condition}")
                # self.close_connections()
                return True

        if len(self.allowed_moves) == 0:
            self.broadcast(GAME_OVER, "d")
            print("Server.py : bc its a draw")
            # self.close_connections()
            return True

    def close_connections(self):
        for c in self.clients:
            c.close()
        self.server.close()

    def game_loop(self):

        self.broadcast(subject=ALLOWED, msg=self.allowed_moves)
        print("broadcast all allowed moves")
        self.send_msg(subject=TURN, msg=True, c=self.clients[0])
        print("sent msg to P1 - turn = True")
        self.send_msg(subject=TURN, msg=False, c=self.clients[1])
        print("sent msg to P2 - turn = False")
        self.broadcast(GAME_ON, True)
        print("Game on loop ")

        while self.game_on:

            self.turn = X if self.counter % 2 == 0 else O
            print(f"round {self.counter}: turn = {self.turn}")
            if self.turn == X:
                self.current_player = self.clients[0]
                self.non_current_player = self.clients[1]
            elif self.turn == O:
                self.current_player = self.clients[1]
                self.non_current_player = self.clients[0]
            print(f"turn {self.turn}: current player = {self.current_player}, non-current = {self.non_current_player}")

            self.send_msg(TURN, True, self.current_player)
            self.send_msg(TURN, False, self.non_current_player)
            player_move = self.current_player.recv(1024)
            if player_move:
                player_move = player_move.decode("utf-8")
                self.make_move(move=player_move, player=self.current_player)
                print(f"player made move {player_move}")
                self.send_msg(OPP_MOVE, player_move, self.non_current_player)
                print(f"player made move {player_move} sending to opponent")
                self.counter += 1
                print(f"counter = {self.counter}")
                self.broadcast(subject=ALLOWED, msg=self.allowed_moves)
                print("broadcast all allowed moves")

                if self.check_winner():
                    self.game_on = False
                    break


if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 12345
    client = TicTacToeServer(HOST, PORT)

#
#             if self.check_winner():
#                 self.game_on = False
#                 break

