from holmes.config import LOG_PATH


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'console':{
            'class':'logging.StreamHandler',
            'level':'DEBUG',
            'formatter': 'verbose'
        },
        'file':{
            'class':'logging.FileHandler',
            'level':'DEBUG',
            'formatter': 'verbose',
            'filename': LOG_PATH,
            'encoding': 'utf8'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': True
        },
        'holmes': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}
