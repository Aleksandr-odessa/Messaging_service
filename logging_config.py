import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(message)s- %(module)s',
        },
        'detailed': {
            'format': '%(asctime)s - %(module)s - %(lineno)d - %(message)s',
        },
        'simple': {
            'format': '%(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
            'stream': 'ext://sys.stdout',
        },
        "file_error": {
            'class': 'logging.FileHandler',
            'filename': 'error.log',
            'formatter': 'detailed',
            'delay': 'True',
        },
    },
    'loggers': {
        'log_error': {
            'handlers': ['file_error'],
            'propagate': False,
            'level': 'ERROR',
        },
       'log_debug': {
                'handlers': ['console'],
                'propagate': False,
                'level': 'DEBUG',
            },

    },
}

logging.config.dictConfig(LOGGING_CONFIG)