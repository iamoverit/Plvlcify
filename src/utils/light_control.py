from functools import lru_cache
import threading
import time
from yeelight import discover_bulbs
from yeelight import Bulb, BulbException
from yeelight.enums import LightType
import logging
logging.basicConfig(level=logging.DEBUG)


def get_ttl_hash(seconds=3600):
    """Return the same value withing `seconds` time period"""
    return round(time.time() / seconds)


class LightControl():
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs) -> Bulb:
        if cls._instance is None:
            with cls._lock:
                # Another thread could have created the instance
                # before we acquired the lock. So check that the
                # instance is still nonexistent.
                cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    @lru_cache
    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            result = None
            for bulb in self.discover_bulbs():
                bulb = Bulb(bulb['ip'], model=bulb['capabilities']['model'])
                call_func = getattr(bulb, name)
                try:
                    result = call_func(*args, **kwargs)
                except BulbException as e:
                    logging.debug(e)
                return result

            # calling required methods with args & kwargs
            return self
        return wrapper

    @lru_cache
    def discover_bulbs(ttl=get_ttl_hash):
        logging.debug('lru_cache: ' + str(ttl))
        return discover_bulbs()


if __name__ == '__main__':
    a = LightControl()
    a.set_color_temp(5400, light_type=LightType.Ambient)
