from PyQt5.QtCore import QObject, pyqtSignal


class Controller(QObject):
    # Signals for each property
    player_changed = pyqtSignal()
    opponent_changed = pyqtSignal()
    turn_changed = pyqtSignal()
    allowed_moves_changed = pyqtSignal()
    played_moves_changed = pyqtSignal()
    player_move_changed = pyqtSignal()
    move_sent_changed = pyqtSignal()
    opponent_move_changed = pyqtSignal()
    opponent_move_sent_changed = pyqtSignal()
    winner_changed = pyqtSignal()
    win_streak_changed = pyqtSignal()
    draw_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._attributes = {}  # Dictionary to store the actual property values
        self.initialize_properties()

    def get_attribute(self, attr_name):
        """Public method to safely get an attribute value."""
        return self._attributes.get(attr_name, None)

    def set_attribute(self, attr_name, value):
        """Public method to safely set an attribute value and emit signal."""
        print(f"Setting {attr_name} to {value} (previous: {self._attributes.get(attr_name)})")
        if self._attributes.get(attr_name) != value:
            self._attributes[attr_name] = value
            print(f"Emitting signal for {attr_name}")

            # Find and emit the signal for the property
            signal = getattr(self, f"{attr_name}_changed", None)
            if signal:
                signal.emit()

    def initialize_properties(self):
        """Initialize all properties at once with default values."""
        properties = [
            "player", "opponent", "turn", "allowed_moves",
            "played_moves", "player_move", "move_sent", "opponent_move", "opponent_move_sent",
            "winner", "win_streak", "draw"
        ]
        # Set default values for properties, you can set more appropriate defaults as needed
        default_values = {
            "player": None,
            "opponent": None,
            "turn": None,
            "allowed_moves": [],
            "played_moves": [],
            "player_move": None,
            "move_sent": False,
            "opponent_move": None,
            "opponent_move_sent": False,
            "winner": None,
            "win_streak": [],
            "draw": None
        }

        for prop in properties:
            # Initialize each attribute with its default value
            self._attributes[prop] = default_values.get(prop, None)









