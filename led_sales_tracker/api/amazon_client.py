import logging
import datetime
import time
from zoneinfo import ZoneInfo
from sp_api.api import Sales
from sp_api.base import Marketplaces, Granularity
from sp_api.base.exceptions import SellingApiForbiddenException
from ..config import AMAZON_CLIENT_ID, AMAZON_CLIENT_SECRET, AMAZON_REFRESH_TOKEN

logger = logging.getLogger(__name__)

class AmazonClient:
    def __init__(self, timezone_str="America/Los_Angeles"):
        self.base_credentials = { # Renamed to avoid confusion with instance-specific creds
            'refresh_token': AMAZON_REFRESH_TOKEN,
            'lwa_app_id': AMAZON_CLIENT_ID,
            'lwa_client_secret': AMAZON_CLIENT_SECRET,
            'lwa_options': {
                'refresh_earlier': 300  # Refresh token 5 minutes before expiration
            },
        }
        self.timezone = ZoneInfo(timezone_str)
        self.timezone_str = timezone_str
        self._api_clients = {}  # Cache for {marketplace_id_str: client_instance}
        logger.info(f"Amazon client initialized with timezone: {timezone_str}. Refresh token loaded from environment.")

    def _get_sales_client(self, marketplace: Marketplaces):
        """
        Retrieves or creates a Sales API client for the given marketplace.
        Clients are cached to allow them to manage their own token state (including rotated refresh tokens).
        """
        marketplace_key = marketplace.marketplace_id # Assuming marketplace_id is a unique string

        if marketplace_key not in self._api_clients:
            logger.info(f"Creating new Sales API client for marketplace: {marketplace.name} ({marketplace_key})")
            # Pass a copy of base_credentials. The library might modify the credentials dict
            # (e.g., with an access token), though it typically handles this internally.
            # More importantly, each client instance needs its own credential state.
            client_credentials = self.base_credentials.copy()
            self._api_clients[marketplace_key] = Sales(
                credentials=client_credentials,
                marketplace=marketplace
            )
        else:
            logger.debug(f"Reusing existing Sales API client for marketplace: {marketplace.name} ({marketplace_key})")
        return self._api_clients[marketplace_key]

    def _invalidate_sales_client(self, marketplace: Marketplaces):
        """
        Removes a cached Sales API client, forcing a new one to be created on next request.
        Useful if the client's token state is believed to be irrevocably bad.
        """
        marketplace_key = marketplace.marketplace_id
        if marketplace_key in self._api_clients:
            logger.warning(f"Invalidating cached Sales API client for marketplace: {marketplace.name} ({marketplace_key})")
            del self._api_clients[marketplace_key]

    def get_sales_data(self, metric_type='sales', days=30, marketplace=Marketplaces.US):
        """
        Get sales data from Amazon Seller API using Analytics API.
        """
        if not isinstance(days, int) or days <= 0:
            raise ValueError("Days parameter must be a positive integer")
        if metric_type not in ['sales', 'units']:
            raise ValueError("Metric type must be 'sales' or 'units'")

        end_date = datetime.datetime.now(self.timezone)
        start_date = end_date - datetime.timedelta(days=days)

        # Format dates with timezone offset properly
        start_date_str = start_date.strftime('%Y-%m-%dT00:00:00%z')
        end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%S%z')
        start_date_str = start_date_str[:-2] + ':' + start_date_str[-2:]
        end_date_str = end_date_str[:-2] + ':' + end_date_str[-2:]
        interval = (start_date_str, end_date_str)
        
        logger.info(f"Fetching {metric_type} data for interval: {interval}, marketplace: {marketplace.name}")

        # Get a potentially cached, long-lived client instance
        sales_api = self._get_sales_client(marketplace)

        retry_count = 0
        max_retries = 3 # Max retries for this specific operation
        
        while retry_count < max_retries:
            try:
                # The sales_api instance, being persistent for this marketplace,
                # will manage its own access token and use its internally stored
                # (and potentially rotated) refresh token for refreshing.
                response = sales_api.get_order_metrics(
                    marketplaceIds=[marketplace.marketplace_id],
                    interval=interval,
                    granularity=Granularity.DAY, # Enum member
                    granularityTimeZone='US/Pacific' # Or self.timezone_str if appropriate for granularity
                )

                payload = response.payload if hasattr(response, 'payload') and response.payload is not None else []
                if not isinstance(payload, list):
                    logger.warning(f"Received unexpected payload format or empty payload: {response}")
                    payload = [] # Ensure payload is a list for processing functions

                if metric_type == 'sales':
                    return self._process_sales_metrics(payload)
                else:  # units
                    return self._process_units_metrics(payload)

            except SellingApiForbiddenException as e:
                retry_count += 1
                error_message = str(e)
                details_str = str(e.response.errors) if e.response and e.response.errors else "No details."
                is_expired_token_error = 'The access token you provided has expired.' in error_message or \
                                         ('details' in details_str and 'The access token you provided has expired.' in details_str)
                
                logger.warning(
                    f"SellingApiForbiddenException (Attempt {retry_count}/{max_retries}) for {marketplace.name}. "
                    f"Expired Token: {is_expired_token_error}. Error: {error_message}. Details: {details_str}"
                )
                
                if retry_count >= max_retries:
                    logger.error(
                        f"Maximum retry attempts reached for {marketplace.name}. Unable to complete operation. "
                        f"Last error: {error_message}"
                    )
                    # If all retries fail, it's possible the client's internal refresh token is bad.
                    # Invalidating it will cause a new client (using the base refresh token from .env)
                    # to be created on the *next* call to get_sales_data for this marketplace.
                    self._invalidate_sales_client(marketplace)
                    raise # Re-raise the SellingApiForbiddenException

                # For any SellingApiForbiddenException (especially expired token), we assume the library
                # will attempt to refresh its token on the next try with the same client instance.
                # The library is designed to do this.
                sleep_time = retry_count * 2 # Exponential backoff (e.g., 2, 4, 6 seconds)
                logger.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
                # No need to re-initialize sales_api, the same instance will retry.
                # If its internal refresh token is also bad, it *should* ideally bubble up
                # a more specific LWA error, but often just results in repeated "expired access token".
                continue

            except Exception as e:
                logger.error(f"Unexpected error retrieving sales data for {marketplace.name}: {str(e)}", exc_info=True)
                # For unexpected errors, you might also want to invalidate the client
                # if you suspect its state is corrupted, or just re-raise.
                # self._invalidate_sales_client(marketplace)
                raise
        
        # This part should ideally not be reached if retries and exceptions are handled.
        # If it is, it means the loop completed without returning or raising.
        logger.error(f"Exhausted retries for get_sales_data for {marketplace.name} without success or unhandled exception.")
        raise RuntimeError(f"Failed to get sales data for {marketplace.name} after {max_retries} attempts.")


    def _process_sales_metrics(self, metrics_data):
        total_sales = 0.0
        currency = "USD"
        daily_sales = []
        if not metrics_data: # Handle empty metrics_data
            return {'total_sales': 0, 'currency': currency, 'daily_sales': [], 'raw_data': metrics_data}

        sorted_data = sorted(metrics_data, key=lambda x: x.get('interval', '').split('--')[0] if x.get('interval') else '')
        for day_data in sorted_data:
            sales_info = day_data.get('totalSales', {})
            amount = float(sales_info.get('amount', 0.0))
            current_currency = sales_info.get('currencyCode')
            if current_currency: currency = current_currency
            total_sales += amount
            interval_str = day_data.get('interval', '')
            date_part = interval_str.split('--')[0]
            date = date_part.split('T')[0] if 'T' in date_part else 'unknown'
            daily_sales.append({'date': date, 'sales_amount': round(amount, 2), 'currency': currency})
        return {'total_sales': round(total_sales, 2), 'currency': currency, 'daily_sales': daily_sales, 'raw_data': metrics_data}

    def _process_units_metrics(self, metrics_data):
        total_units = 0
        daily_units = []
        if not metrics_data: # Handle empty metrics_data
            return {'total_units': 0, 'daily_units': [], 'raw_data': metrics_data}

        sorted_data = sorted(metrics_data, key=lambda x: x.get('interval', '').split('--')[0] if x.get('interval') else '')
        for day_data in sorted_data:
            units = int(day_data.get('unitCount', 0))
            total_units += units
            interval_str = day_data.get('interval', '')
            date_part = interval_str.split('--')[0]
            date = date_part.split('T')[0] if 'T' in date_part else 'unknown'
            daily_units.append({'date': date, 'units_sold': units})
        return {'total_units': total_units, 'daily_units': daily_units, 'raw_data': metrics_data}