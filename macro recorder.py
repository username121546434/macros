from time import sleep, time
from tkinter import *
from tkinter import messagebox
from typing import Callable
from pynput.keyboard import Key, KeyCode
from pynput.mouse import Button as MouseButton
from pynput import mouse, keyboard
from decorators import thread
from mouse_movement import MouseMovement
from scroll import ScrollEvent
from mouse_click import MouseClick


def on_click(x: int, y: int, button: MouseButton, pressed: bool):
    print('On click')
    print(f'{x = }\n{y = }\n{pressed = }\n{button = }')

    obj = MouseClick(x, y, button, pressed)
    mouse_clicks.append(obj)
    events.append(obj)


def on_scroll(x: int, y: int, dx: int, dy: int):
    print('On Scroll')
    print(f'{x = }\n{y = }')
    print(f'{dx = }\n{dy = }')

    obj = ScrollEvent(x, y, dx, dy)
    scrolls.append(obj)
    events.append(obj)


def on_move(x: int, y: int):
    print('On Move')
    print(f'{x = }\n{y = }')

    obj = MouseMovement(x, y)
    mouse_movements.append(obj)
    events.append(obj)


def on_press(key: Key | KeyCode):
    print('On key press')
    print(f'{key = }\n{type(key) = }')

    key.created_at = time()
    key.pressed = True

    key_presses.append(key)
    events.append(key)


def on_release(key: Key | KeyCode):
    print('On key press')
    print(f'{key = }\n{type(key) = }')

    key.created_at = time()
    key.pressed = False

    key_presses.append(key)
    events.append(key)


def start_listening():
    key_listener.start()
    mouse_listener.start()


def stop_listening():
    global key_listener, mouse_listener

    key_listener.stop()
    mouse_listener.stop()

    key_listener = keyboard.Listener(on_press=on_press, on_release=on_press)
    mouse_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll, on_move=on_move)


def clear_data():
    mouse_movements.clear()
    scrolls.clear()
    events.clear()
    mouse_clicks.clear()


def event_to_func(event, list_of_events: list[MouseMovement| ScrollEvent| Key| KeyCode| MouseClick]) -> Callable[[mouse.Controller, keyboard.Controller], None]:
    event_idx = list_of_events.index(event)
    next_event = list_of_events[event_idx + 1]
    if isinstance(event, MouseMovement):
        for idx, move in enumerate(event.path):
            if next_event.created_at < move[2]: # Another event is before the next move
                return event_to_func(list_of_events[list_of_events.index(event) + 1], list_of_events)
            return lambda m, k: (setattr(m, 'position', move), sleep(event.path[idx + 1][2]-move[2]))
    elif isinstance(event, ScrollEvent):
        return lambda m, k: (m.scroll(event.dx, event.dy), sleep(next_event.created_at - event.created_at))
    elif isinstance(event, (Key, KeyCode)):
        return lambda m, k: (k.press(event) if event.pressed else k.release(event), sleep(next_event.created_at - event.created_at))
    elif isinstance(event, MouseClick):
        return lambda m, k: (m.press(event.button) if event.pressed else m.release(event.button), sleep(next_event.created_at - event.created_at))


def order_macro(macro: list[MouseMovement| ScrollEvent| Key| KeyCode| MouseClick]):
    new: list[Callable[[mouse.Controller, keyboard.Controller], None]] = []

    for event in macro:
        new.append(event_to_func(event, macro))

    return new


def play_macro():
    stop_listening()
    _play_macro(delay_state.get())


@thread
def _play_macro(delay: int):
    mouse_controller = mouse.Controller()
    keyboard_controller = keyboard.Controller()

    macro_on = True
    macro = events.copy()

    while macro_on:
        with keyboard.Events() as key_events:
            key = key_events.get(delay * 0.001)
            if key is not None:
                break
            for func in order_macro(macro):
                func(mouse_controller, keyboard_controller)

    messagebox.showinfo('Macro Stopped', 'Your macro has stopped')


mouse_movements: list[MouseMovement] = []
scrolls: list[ScrollEvent] = []
mouse_clicks: list[MouseClick] = []
events: list[MouseMovement| ScrollEvent| Key| KeyCode| MouseClick] = []
key_presses: list[Key|KeyCode] = []

key_listener = keyboard.Listener(on_press=on_press)
mouse_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll, on_move=on_move)
window = Tk()
window.config(pady=20, padx=50)
window.title('Macros')

Button(window, text='Start Recording', command=start_listening).pack()
Button(window, text='Stop Recording', command=stop_listening).pack()
Button(window, text='Delete Data', command=clear_data).pack()
Button(window, text='Play Macro', command=play_macro).pack()

delay_state = IntVar(window)
Label(window, text='Delay between each event (ms)').pack()
Spinbox(window, from_=0, to=60000, textvariable=delay_state, width=6).pack()

window.mainloop()
