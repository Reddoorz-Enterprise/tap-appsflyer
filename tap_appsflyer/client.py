import sys
import csv
import backoff
import itertools
import requests
import singer
import singer.metrics
from singer import transform
from singer import utils
from datetime import datetime, timedelta


LOGGER = singer.get_logger()
SESSION = requests.Session()

API_LIMITS = {
    "in_app_events_report": 60,  # days
    "installs_report": 60,
    "organic_installs_report": 60,
    "uninstall_events_report": 60,
    "organic_uninstall_events_report": 60,
    "partners_by_date_report": 365,
    "organic_in_app_events_report": 60,
    "ad_revenue_raw": 60,
    "ad_revenue_organic_raw": 60,
}


class RequestToCsvAdapter:
    def __init__(self, request_data):
        self.request_data_iter = request_data.iter_lines()

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.request_data_iter).decode("utf-8")

    def giveup(self, exc):
        return exc.response is not None and 400 <= exc.response.status_code < 500


class AppsflyerClient:
    # API rate limits: https://support.appsflyer.com/hc/en-us/articles/207034366-API-Policy

    def __init__(self, config):
        self.config = config
        self.base_url = "https://hq.appsflyer.com"
        self.base_url_path = "export/{app_id}"

    def _get_request_intervals(self, report_name, from_datetime, to_datetime):
        # calculate delta in seconds and divide by seconds limit
        if report_name not in API_LIMITS:
            LOGGER.error(
                "API Limit not declared for report name: {0}".format(report_name)
            )
            sys.exit(1)

        delta = to_datetime - from_datetime
        delta_secs = delta.total_seconds()
        limit_secs = API_LIMITS[report_name] * 60 * 60 * 24
        q = int(delta_secs / limit_secs)
        r = delta_secs % limit_secs

        # create a list with date intervals
        from_param, to_param = from_datetime, to_datetime
        intervals = []
        while q > 0 or r > 0:
            if q > 0:
                to_param = from_param + timedelta(seconds=limit_secs)
                intervals.append({"from": from_param, "to": to_param})
                from_param = to_param + timedelta(minutes=1)
                q = q - 1
            if q == 0 and r != 0:
                to_param = to_datetime
                intervals.append({"from": from_param, "to": to_param})
                r = 0

        return intervals

    def _iterate_x_days_in_a_time(self, from_datetime, to_datetime):
        from_param, to_param = from_datetime, to_datetime
        intervals = []
        chunk_size = 5
        delta = to_datetime - from_datetime
        diff_days = delta.days
        date_list = [
            (from_param + (timedelta(days=1) * x)) for x in range(0, diff_days + 1)
        ]
        chunked_list = [
            date_list[i - 1 : i + chunk_size]
            for i in range(0, len(date_list), chunk_size)
        ]
        for index, chunk in enumerate(chunked_list):
            if index == 0:
                intervals.append({"from": chunk[0], "to": chunk[-1]})
            else:
                intervals.append({"from": chunked_list[index - 1], "to": chunk[-1]})

        return intervals

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=5,
        # giveup=giveup,
        factor=2,
    )
    @utils.ratelimit(2, 60)
    def _request(self, url, params=None):

        params = params or {}
        headers = {}

        if "user_agent" in self.config:
            headers["User-Agent"] = self.config["user_agent"]

        req = requests.Request("GET", url, params=params, headers=headers).prepare()
        LOGGER.info(
            "GET {0} | Date interval: from {1} to {2} : retargeting : {3}:".format(
                url, params["from"], params["to"], params["reattr"]
            )
        )

        resp = SESSION.send(req)

        if resp.status_code >= 400:
            LOGGER.error("GET %s [%s - %s]", url, resp.status_code, resp.content)
            sys.exit(1)

        return resp

    def _get_url(self, report_name, report_version):
        return "/".join(
            [
                self.base_url,
                self.base_url_path.format(app_id=self.config["app_id"]),
                report_name,
                report_version,
            ]
        )

    def _parse_raw_api_params(self, from_datetime, to_datetime):
        params = dict()
        params["from"] = from_datetime.strftime("%Y-%m-%d %H:%M")
        params["to"] = to_datetime.strftime("%Y-%m-%d %H:%M")
        params["api_token"] = self.config["api_token"]

        return params

    def _parse_daily_api_params(self, from_datetime, to_datetime):
        params = dict()
        params["from"] = from_datetime.strftime("%Y-%m-%d")
        params["to"] = to_datetime.strftime("%Y-%m-%d")
        params["api_token"] = self.config["api_token"]

        return params

    def get_raw_data(
        self,
        report_name,
        report_version,
        from_datetime,
        to_datetime,
        fieldnames,
        reattr,
    ):
        # Raw data: https://support.appsflyer.com/hc/en-us/articles/360007530258-Using-Pull-API-raw-data

        req_intervals = self._iterate_x_days_in_a_time(from_datetime, to_datetime)

        csv_data_chained = []

        for req_interval in req_intervals:
            url = self._get_url(report_name, report_version)
            params = self._parse_raw_api_params(
                req_interval["from"], req_interval["to"]
            )
            params["reattr"] = reattr

            request_data = self._request(url, params)

            csv_data = RequestToCsvAdapter(request_data)
            next(csv_data)  # Skip the heading row
            csv_data_chained = itertools.chain(csv_data_chained, csv_data)

        reader = csv.DictReader(csv_data_chained, fieldnames)

        return reader

    def get_daily_report(self, start_datetime, end_datetime):
        # Agg Data: https://support.appsflyer.com/hc/en-us/articles/207034346-Using-Pull-API-aggregate-data
        pass
