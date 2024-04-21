from datetime import date
from typing import Tuple

from .config import getCumulocityApi
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

c8y = getCumulocityApi()


class Measurements:
    def __init__(self, device: dict, enforceBounds=False):
        self.enforceBounds = enforceBounds
        self.deviceId = device['id']
        self.supportedFragmentAndSeries = device['c8y_supportedSeries']

        if enforceBounds:
            if device['latestMeasurement']:
                self.latestMeasurement = parse(device['latestMeasurement']['time']).date()
            if device['oldestMeasurement']:
                self.oldestMeasurement = parse(device['oldestMeasurement']['time']).date()

    def hasMeasurements(self, dateFrom: date, dateTo: date) -> bool:
        if not self.supportedFragmentAndSeries:
            return False
        if self.enforceBounds:
            if not self.latestMeasurement or not self.oldestMeasurement:
                return False
            if self.latestMeasurement < dateFrom or dateTo < self.oldestMeasurement:
                return False
        return True

    def requestLatestMeasurement(self, dateFrom: date, dateTo: date) -> dict:
        additionalParameters = {'revert': 'true'}
        response = self.requestMeasurementCount(dateFrom, dateTo, additionalParameters)
        return {'count': response['count'], 'latestMeasurement': response['measurement']}

    def requestOldestMeasurement(self, dateFrom: date, dateTo: date) -> dict:
        additionalParameters = {'revert': 'false'}
        response = self.requestMeasurementCount(dateFrom, dateTo, additionalParameters)
        return {'count': response['count'], 'oldestMeasurement': response['measurement']}

    def requestFragmentSeriesCount(self, dateFrom: date, dateTo: date, fragment: str, series: str):
        additionalParameters = {'valueFragmentType': fragment, 'valueFragmentSeries': series}
        return self.requestMeasurementCount(dateFrom, dateTo, additionalParameters)

    def requestMeasurementCount(self, dateFrom: date, dateTo: date, additionalParameters: dict = None) -> dict:
        parameters = {
            'dateFrom': dateFrom.isoformat(),
            'dateTo': dateTo.isoformat(),
            'source': self.deviceId,
            'pageSize': 1,
            'currentPage': 1,
            'withTotalPages': 'true',
            'revert': 'false',
        }
        if additionalParameters:
            parameters.update(additionalParameters)

        if self.hasMeasurements(dateFrom, dateTo):
            try:
                response = c8y.get(resource="/measurement/measurements", params=parameters)
                measurementCount = response['statistics']['totalPages']
                latestMeasurement = response['measurements']
            except KeyboardInterrupt:  # TODO better error handling
                raise KeyboardInterrupt
            except:
                measurementCount = -1
                latestMeasurement = {}
        else:
            measurementCount = 0
            latestMeasurement = {}

        if latestMeasurement:
            latestMeasurement = latestMeasurement[0]
            del latestMeasurement['self']
            del latestMeasurement['source']['self']
        return {'count': measurementCount, 'measurement': latestMeasurement}

    def requestLatestMeasurementValidation(self, dateTo: date) -> dict:
        try:
            return c8y.measurements.get_last(source=self.deviceId, before=dateTo).to_json()
        except IndexError:
            return {}


class MonthlyMeasurements:
    def __init__(self, device: dict, enforceBounds=True):
        self.cumulocity = Measurements(device, enforceBounds)

    def requestLatestMeasurement(self, year: int, month: int) -> dict:
        return self.cumulocity.requestLatestMeasurement(*requestMonthBounds(year, month))

    def requestOldestMeasurement(self, year: int, month: int) -> dict:
        return self.cumulocity.requestOldestMeasurement(*requestMonthBounds(year, month))

    def requestFragmentSeriesCount(self, year: int, month: int, fragment: str, series: str):
        dateFrom, dateTo = requestMonthBounds(year, month)
        return self.cumulocity.requestFragmentSeriesCount(dateFrom, dateTo, fragment, series)

    def requestMeasurementCount(self, year, month, additionalParameters: dict = None) -> dict:
        dateFrom, dateTo = requestMonthBounds(year, month)
        return self.cumulocity.requestMeasurementCount(dateFrom, dateTo, additionalParameters)

    @staticmethod
    def fileName(year: int, month: int) -> str:
        dateFrom, dateTo = requestMonthBounds(year, month)
        return f'c8y_measurements {dateFrom} - {dateTo}.json'


def requestMonthBounds(year: int, month: int) -> Tuple[date, date]:
    inclusiveDateFrom = date(year, month, 1)
    exclusiveDateTo = inclusiveDateFrom + relativedelta(months=1)
    return inclusiveDateFrom, exclusiveDateTo
