
import logging

class SimpleLogFormatter(logging.Formatter):
    grey='\033[97m'
    yellow='\033[93m'
    blue='\033[34m'
    red='\x1b[31;20m'
    reset='\033[00m'
    prefixFormat='[%(levelname)s][%(asctime)s](%(filename)s:%(lineno)d):'
    colorMap = {
        logging.DEBUG: grey,
        logging.INFO: blue,
        logging.WARNING: yellow,
        logging.ERROR: red,
        logging.CRITICAL: red
    }
    def format(self, record):
        color = self.colorMap.get(record.levelno)
        formatter = logging.Formatter(f'{color}{self.prefixFormat} %(message)s {self.reset}')
        return formatter.format(record)
