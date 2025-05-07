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
        self.credentials = {
            'refresh_token': AMAZON_REFRESH_TOKEN,
            'lwa_app_id': AMAZON_CLIENT_ID,
            'lwa_client_secret': AMAZON_CLIENT_SECRET,
            'lwa_options': {
                'refresh_earlier': 300  # Refresh token 5 minutes before expiration
            },
        }
        self.timezone = ZoneInfo(timezone_str)
        self.timezone_str = timezone_str
        logger.info(f"Amazon client initialized with timezone: {timezone_str}")

    def get_sales_data(self, metric_type='sales', days=30, marketplace=Marketplaces.US):
        """
        Get sales data from Amazon Seller API using Analytics API (suitable for frequent polling)

        Args:
            metric_type (str): Type of metric to retrieve - 'sales' (dollars) or 'units'
            days (int): Number of days to look back (any positive integer)
            marketplace (Marketplace): Amazon marketplace to query

        Returns:
            dict: Sales data response with both aggregate and daily time series
        """
        if not isinstance(days, int) or days <= 0:
            raise ValueError("Days parameter must be a positive integer")

        if metric_type not in ['sales', 'units']:
            raise ValueError("Metric type must be 'sales' or 'units'")

        end_date = datetime.datetime.now(self.timezone)
        start_date = end_date - datetime.timedelta(days=days)

        start_date_str = start_date.strftime('%Y-%m-%dT00:00:00%z')
        end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%S%z')

        # Convert offset from "-0700" to "-07:00"
        start_date_str = start_date_str[:-2] + ':' + start_date_str[-2:]
        end_date_str = end_date_str[:-2] + ':' + end_date_str[-2:]
        interval = (start_date_str, end_date_str)
        
        logger.info(f"Fetching {metric_type} data for interval: {interval}")

        retry_count = 0
        max_retries = 3
        while retry_count < max_retries:
            try:
                
                # Initialize the Sales Analytics API client passing credentials directly
                sales_api = Sales(
                    credentials=self.credentials,
                    marketplace=marketplace
                )

                # Use the Granularity Enum, not a string
                # Note: Enum members are typically uppercase by convention
                granularity = Granularity.DAY

                # Make the API call to get order metrics
                response = sales_api.get_order_metrics(
                    marketplaceIds=[marketplace.marketplace_id],
                    interval=interval,
                    granularity=granularity,
                    granularityTimeZone='US/Pacific'
                )

                # Process the response based on metric type
                # Check if response.payload exists and is a list
                payload = response.payload if hasattr(response, 'payload') else None
                if payload is None or not isinstance(payload, list):
                    logger.warning(f"Received unexpected payload format or empty payload: {response}")
                    # Return a default structure or raise an error based on your needs
                    return {'total_sales': 0, 'currency': 'USD', 'daily_sales': [], 'raw_data': payload} if metric_type == 'sales' else {'total_units': 0, 'daily_units': [], 'raw_data': payload}


                if metric_type == 'sales':
                    return self._process_sales_metrics(payload)
                else:  # units
                    return self._process_units_metrics(payload)
            except SellingApiForbiddenException as e:
                retry_count += 1
                logger.warning(f"Token expired (attempt {retry_count}/{max_retries}). Refreshing and retrying...")
                
                if retry_count >= max_retries:
                    logger.error("Maximum retry attempts reached. Unable to refresh token.")
                    raise
                
                # Add a short delay before retrying to allow for token refresh
                time.sleep(2)
                
                # Force token refresh by creating a new instance
                continue

            except Exception as e:
                logger.error(f"Error retrieving sales data: {str(e)}")
                raise


    def _process_sales_metrics(self, metrics_data):
        """
        Process sales amount data from order metrics

        Args:
            metrics_data (list): Order metrics data from Amazon API

        Returns:
            dict: Processed sales data with aggregate and daily time series
        """
        total_sales = 0.0 # Use float for consistency
        currency = "USD"  # Default, will be updated
        daily_sales = []

        # Sort the data by date for consistent time series
        # Handle potential missing 'interval' key gracefully
        sorted_data = sorted(metrics_data, key=lambda x: x.get('interval', '').split('--')[0] if x.get('interval') else '')

        for day_data in sorted_data:
            # Extract sales amount and currency safely
            sales_info = day_data.get('totalSales', {})
            amount = float(sales_info.get('amount', 0.0))
            current_currency = sales_info.get('currencyCode')
            if current_currency: # Update currency if found
                currency = current_currency

            # Add to total
            total_sales += amount

            # Extract the date from interval safely
            interval_str = day_data.get('interval', '')
            date = interval_str.split('T')[0] if interval_str and '--' in interval_str else 'unknown'

            # Store daily data
            day_info = {
                'date': date,
                'sales_amount': round(amount, 2), # Round daily amount too
                'currency': currency
            }
            daily_sales.append(day_info)

        return {
            'total_sales': round(total_sales, 2),
            'currency': currency,
            'daily_sales': daily_sales,
            'raw_data': metrics_data # Keep raw data for debugging if needed
        }

    def _process_units_metrics(self, metrics_data):
        """
        Process units sold data from order metrics

        Args:
            metrics_data (list): Order metrics data from Amazon API

        Returns:
            dict: Processed units data with aggregate and daily time series
        """
        total_units = 0
        daily_units = []

        # Sort the data by date for consistent time series
        # Handle potential missing 'interval' key gracefully
        sorted_data = sorted(metrics_data, key=lambda x: x.get('interval', '').split('--')[0] if x.get('interval') else '')

        for day_data in sorted_data:
            # Extract units sold safely
            units = int(day_data.get('unitCount', 0)) # Changed from 'unitsSold' to 'unitCount' based on common API response structure

            # Add to total
            total_units += units

            # Extract the date from interval safely
            interval_str = day_data.get('interval', '')
            date = interval_str.split('T')[0] if interval_str and '--' in interval_str else 'unknown'

            # Store daily data
            day_info = {
                'date': date,
                'units_sold': units
            }
            daily_units.append(day_info)

        return {
            'total_units': total_units,
            'daily_units': daily_units,
            'raw_data': metrics_data # Keep raw data for debugging if needed
        }