import logging

from app import Application

def main():
    logger = logging.getLogger()

    try:
        app = Application()
        app.run()
    except Exception as e:
        logger.exception("Exception Occurred:  " + str(e))

if __name__ == "__main__":
    main()
