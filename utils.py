import threading
import functools


def thread(func):
    """Makes the wrapped function run in a seperate thread when called"""
    @functools.wraps(wrapped=func)
    def wrap(*args, **kwargs):
        threading.Thread(target=func, args=args, kwargs=kwargs).start()
    
    return wrap

