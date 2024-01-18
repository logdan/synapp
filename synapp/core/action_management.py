from pynput.keyboard import Key, Controller, KeyCode, HotKey
import pynput
from PyQt5.QtGui import QKeySequence



# Action should be a function that does things
class Action:
    def __init__(self, name, action):
        self.name = name
        self.execute = action


def getActionMethodList():
    d = {
        "command1": ctrlcmdshifta,
        "command2": ctrlcmdshiftequal,
    }
    return d


def getBlinkRightLeftActions():
    methodlist = getActionMethodList()
    actions = {
        "winkright": Action("command1", methodlist["command1"]),
        "winkleft": Action("command2", methodlist["command2"]),
    }
    return actions


def ctrlcmdshifta(hold=False, time=200, keyboard=Controller()):
    minus = "a"
    with keyboard.pressed(Key.cmd, Key.ctrl, Key.shift):
        keyboard.press(minus)


def ctrlcmdshiftequal(hold=False, time=200):
    keyboard = Controller()
    equal = KeyCode(vk=27)
    with keyboard.pressed(Key.cmd, Key.ctrl, Key.shift):
        keyboard.press(equal)


## key: str, key character to be pressed
## modifiers: list of modifiers to be pressed, as parsed by hotkey.parse


def press_key(key, modifiers):
    keyboard = Controller()

    with keyboard.pressed(*modifiers):
        keyboard.press(*key)
        keyboard.release(*key)


def press_pyqt_key_sequence(key_sequence: QKeySequence):
    hotkey_sequence = pyqt_key_sequence_to_pynput_command(key_sequence)
    press_key(hotkey_sequence)


def pyqt_key_sequence_to_pynput_command(key_sequence: QKeySequence):
    string = key_sequence.toString().lower()
    key_strings = string.split("+")
    for i in range(len(key_strings)):
        curr_str = key_strings[i]
        ### if longer than 1 char, it's a modifier key, so put it in <> for pynput parsing
        if len(curr_str) > 1:
            key_strings[i] = "<" + curr_str + ">"

    joiner = "+"
    pynput_hotkey_sequence = joiner.join(key_strings)

    parsed_keys = HotKey.parse(pynput_hotkey_sequence)
    keys = []
    modifiers = []
    for key in parsed_keys:
        if isinstance(key, pynput.keyboard.KeyCode):
            keys.append(key)
        else:
            modifiers.append(key)

    return keys, modifiers


def key_sequence_to_pynput_command(key_sequence: str):
    key_strings = key_sequence.split("+")
    for i in range(len(key_strings)):
        curr_str = key_strings[i]
        ### if longer than 1 char, it's a modifier key, so put it in <> for pynput parsing
        if len(curr_str) > 1:
            key_strings[i] = "<" + curr_str + ">"

    joiner = "+"
    pynput_hotkey_sequence = joiner.join(key_strings)

    parsed_keys = HotKey.parse(pynput_hotkey_sequence)
    keys = []
    modifiers = []
    for key in parsed_keys:
        if isinstance(key, pynput.keyboard.KeyCode):
            keys.append(key)
        else:
            modifiers.append(key)

    return keys, modifiers


def press_key_sequence(key_sequence: str):
    keys, modifiers = key_sequence_to_pynput_command(key_sequence)
    press_key(keys, modifiers)


# Prediction: string of prediction made. Actionset: Set of actions
def getaction(prediction, actionset):
    pass


def main():
    press_key_sequence("ctrl+cmd+shift+h")


if __name__ == "__main__":
    main()
