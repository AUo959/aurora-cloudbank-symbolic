import logging

logging.basicConfig(
    filename="logs/reflective_autonomy.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)

logger.info("Reflective Autonomy System logging initialized.")
