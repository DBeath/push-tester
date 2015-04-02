import logging
import socket
from logging.handlers import RotatingFileHandler, SysLogHandler


class ContextFilter(logging.Filter):
    hostname = socket.gethostname()

    def filter(self, record):
        record.hostname = ContextFilter.hostname
        return True


def add_logger_filehandler(app):
    """Creates a RotatingFileHandler logger"""

    file_handler = RotatingFileHandler(
        'logs/flaskfeedr.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)


def add_logger_external(app):
    """Creates a SysLogHandler logger"""

    f = ContextFilter()
    app.logger.addFilter(f)

    syslog = SysLogHandler(address=(app.config['LOG_ADDRESS'],
                                    app.config['LOG_PORT']))

    formatter = logging.Formatter(
        '%(asctime)s %(hostname)s :%(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')

    syslog.setFormatter(formatter)
    app.logger.addHandler(syslog)
