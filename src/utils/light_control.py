import threading
from yeelight import discover_bulbs
from yeelight import Bulb, BulbException
import logging
logger = logging.getLogger(__name__)


class DiscoverException(Exception):
    pass


class LightControl():
    __instance = None
    __lock = threading.Lock()

    def __new__(cls, *args, **kwargs) -> Bulb:
        if cls.__instance is None:
            with cls.__lock:
                # Another thread could have created the instance
                # before we acquired the lock. So check that the
                # instance is still nonexistent.
                cls.__instance = super().__new__(cls, *args, **kwargs)
                cls.__instance.discover_bulbs()
        return cls.__instance

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            # raise DiscoverException()
            result = None
            for bulb in self._bulbs:
                bulb = Bulb(bulb.get('ip'), 
                            model=bulb.get('capabilities', {}).get('model', None))
                call_func = getattr(bulb, name)
                try:
                    result = call_func(*args, **kwargs)
                except BulbException as e:
                    logger.debug(e)
                    raise
                return result

            # calling required methods with args & kwargs
            raise DiscoverException('Failed to discover bulbs')
        return wrapper

    def discover_bulbs(self):
        logger.debug('discover_bulbs()')
        self._bulbs = discover_bulbs()

        logger.debug(self._bulbs)
        if len(self._bulbs) == 0:
            self._bulbs.append({'ip': '192.168.3.30'})
        # return discover_bulbs()


if __name__ == '__main__':
    a = LightControl()
    logging.basicConfig(level=logging.DEBUG)
    logger.debug(a._bulbs)
