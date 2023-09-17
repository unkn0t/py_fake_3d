import logging
from engine import *

def main():
    logger = logging.getLogger()

    try:
        application = app.App()
        application.run()
    except Exception as e:
        logger.exception("Exception Occurred:  " + str(e))

if __name__ == "__main__":
    main()
