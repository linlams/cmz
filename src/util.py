# -*- coding: utf-8 -*-

import time

def cache(expiration_time=30):
    def decorator(func):
        __cache__ = [(None, 0)]

        def _(*args, **kwargs):
            now = time.time()
            result, pre_time = __cache__[0]
            print pre_time
            if now - pre_time >= expiration_time:
                result = func(*args, **kwargs)
                __cache__[0] = (result, now)
            return result

        return _

    return decorator

