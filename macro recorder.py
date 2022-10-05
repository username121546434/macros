from time import sleep, time
from tkinter import *
from tkinter import messagebox
from typing import Any, Callable
from pynput.keyboard import Key, KeyCode
from pynput.mouse import Button as MouseButton
from pynput import mouse, keyboard
from utils import thread
from mouse_movement import MousePosChange
from scroll import ScrollEvent
from mouse_click import MouseClick


def on_click(x: int, y: int, button: MouseButton, pressed: bool):
    print('On click')
    print(f'{x = }\n{y = }\n{pressed = }\n{button = }')

    obj = MouseClick(x, y, button, pressed)
    events.append(obj)


def on_scroll(x: int, y: int, dx: int, dy: int):
    print('On Scroll')
    print(f'{x = }\n{y = }')
    print(f'{dx = }\n{dy = }')

    obj = ScrollEvent(x, y, dx, dy)
    events.append(obj)


def on_move(x: int, y: int):
    print('On Move')
    print(f'{x = }\n{y = }')

    obj = MousePosChange(x, y)
    events.append(obj)


def on_press(key: Key | KeyCode):
    print('On key press')
    print(f'{key = }\n{type(key) = }')

    key.created_at = time()
    key.pressed = True

    events.append(key)


def on_release(key: Key | KeyCode):
    print('On key press')
    print(f'{key = }\n{type(key) = }')

    key.created_at = time()
    key.pressed = False

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
    events.clear()


def event_to_func(event, list_of_events: list[MousePosChange | ScrollEvent | Key | KeyCode | MouseClick]) -> Callable[[mouse.Controller, keyboard.Controller], Any]:
    event_idx = list_of_events.index(event)
    try:
        next_event = list_of_events[event_idx + 1]
    except IndexError:
        next_event = None

    if next_event is not None:
        sleep_func = lambda next_event, event: sleep(next_event.created_at - event.created_at)
    else:
        sleep_func = lambda next_event, event: None
    
    if isinstance(event, MousePosChange):
        return lambda m, k: (setattr(m, 'position', (event.x, event.y)), sleep_func(next_event, event))
    elif isinstance(event, ScrollEvent):
        return lambda m, k: (m.scroll(event.dx, event.dy), sleep_func(next_event, event))
    elif isinstance(event, (Key, KeyCode)):
        return lambda m, k: (k.press(event) if event.pressed else k.release(event), sleep_func(next_event, event))
    elif isinstance(event, MouseClick):
        return lambda m, k: (m.press(event.button) if event.pressed else m.release(event.button), sleep_func(next_event, event))


def play_macro():
    stop_listening()
    _play_macro(delay_state.get(), repitions.get())


@thread
def _play_macro(delay: int, reps: int):
    mouse_controller = mouse.Controller()
    keyboard_controller = keyboard.Controller()

    macro_on = True
    macro_events = events.copy()
    rep_num = 0

    with keyboard.Events() as key_events:
        while macro_on:
            for event in macro_events:
                event_to_func(event, macro_events)(mouse_controller, keyboard_controller)
                key = key_events.get(delay * 0.001)
                if key and key.key != event:
                    macro_on = False
                    break
            rep_num += 1
            if rep_num == reps:
                break

    messagebox.showinfo('Macro Stopped', 'Your macro has stopped')


events: list[MousePosChange | ScrollEvent | Key | KeyCode | MouseClick] = []

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
Label(window, text='Delay between each event (milliseconds)').pack()
Spinbox(window, from_=1, to=float('inf'), textvariable=delay_state, width=6).pack()

repitions = IntVar(window)
Label(window, text='Amount of repitions').pack()
Spinbox(window, from_=1, to=float('inf'), textvariable=repitions, width=6).pack()

window.mainloop()
