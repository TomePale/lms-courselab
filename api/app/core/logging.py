import logging


def setup_logging(debug: bool = False) -> None:
    """Jednom pri pokretanju: razina i oblik zapisa za cijelu aplikaciju."""
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
