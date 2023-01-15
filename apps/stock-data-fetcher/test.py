import logging

logging.basicConfig(level=logging.DEBUG)


def test():
    try:
        logging.info("Dividing by zero")
        q = 4 / 0
    except ZeroDivisionError as exc:
        # logging.exception("Error dividing by zero")
        # logging.warning(exc)
        logging.critical("Critical error dividing by zero")
        raise RuntimeError("Custom error") from exc
    finally:
        logging.info("Done")


def main():
    try:
        test()
    except RuntimeError:
        logging.exception("exception")
    except Exception:
        logging.exception("Error in main")
        raise


main()
