import logging
from ..config import AMAZON_CLIENT_ID, AMAZON_CLIENT_SECRET, AMAZON_REFRESH_TOKEN

logger = logging.getLogger(__name__)

class AmazonClient:
    def __init__(self):
        # TODO: instantiate real SP-API client
        logger.info("Amazon client initialised")

    def get_sales_data(self) -> dict:
        """
        Returns mocked sales numbers until real API wired.
        """
        logger.debug("Fetching sales data (mocked)")
        return {"sales_today": 123, "sales_yesterday": 98}