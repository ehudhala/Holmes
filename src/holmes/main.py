from logging.config import dictConfig

from holmes.scheduling import schedule_forever
from holmes.logs import LOGGING

if __name__ == '__main__':
    dictConfig(LOGGING)

    schedule_forever()