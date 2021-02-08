import logging as _logging

HOST_NAME = ''
USER_NAME = ''
PASSWORD = ''

TELEMETRY_NAME = 'telemetry_listener'
TELEMETRY_TOPIC = 'tel'                     # 'robotcar/diagnostics/telemetry'

COURSE_POS_NAME = 'navigation_listener'
COURSE_POS_TOPIC = 'nav'                    # 'robotcar/diagnostics/course'

CONTROL_PARAMS_NAME = 'parameters_listener'
COMMAND_TOPIC = 'comm'                      # 'robotcar/diagnostics/command'
PARAMS_TOPIC = 'param'

LOGGER_NAME = 'log_listener'
LOGGER_TOPIC = 'log'                  # 'robotcar/log'

STARTSTOP_NAME = 'start-stop_publisher'

logger = _logging.getLogger('robotlog')

