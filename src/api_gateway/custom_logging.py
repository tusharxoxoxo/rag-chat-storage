import logging
import contextvars

# Context variable to hold the request ID
request_id_var = contextvars.ContextVar('request_id', default='NoRequestID')


# Custom filter to add request ID to log records
class RequestIDFilter(logging.Filter):
    def filter(self, record):
        # Get the request ID from the context variable
        record.request_id = request_id_var.get()
        return True


# Configure logging
logger = logging.getLogger("my_logger")
logger.setLevel(logging.INFO)

# Create a console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Define a formatter that includes the request ID
formatter = logging.Formatter('%(asctime)s - %(levelname)s - [RequestID: %(request_id)s] - %(message)s')
ch.setFormatter(formatter)

# Add the filter to the handler
ch.addFilter(RequestIDFilter())

# Add the handler to the logger
logger.addHandler(ch)