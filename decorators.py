import threading
import functools


def thread(cls):
    """Makes the wrapped function run in a seperate thread when called"""
    @functools.wraps(wrapped=cls)
    def wrap(*args, **kwargs):
        threading.Thread(target=cls, args=args, kwargs=kwargs).start()
    
    return wrap

