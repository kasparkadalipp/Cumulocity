import pytest
import json
from dateutil.parser import parse, ParserError

with open('../data/telia/c8y_data.json', 'r', encoding='utf8') as json_file:
    c8y_data = json.load(json_file)

example_c8y_data = {
    "id": "11904",
    "type": "com_cityntel_light",
    "name": "light 95 (039A)",
    "owner": "device_com_cityntel_live",
    "creationTime": "2018-09-20T03:28:05.273+03:00",
    "lastUpdated": "2024-04-18T05:25:12.130+03:00",
    "is_device": True,
    "is_group": False,
    "depth": 1,
    "parent": "10503",
    "c8y_inventory": ["<additional custom objects>"],

    "c8y_supportedSeries": [
        {
            "fragment": "Light",
            "series": "output"
        }
    ],
    "dataAfter": "1970-01-01",
    "dataBefore": "2024-04-01",

    "lastMeasurement": "<measurement>",
    "measurementCount": 39878,

    "firstMeasurement": "<measurement>",
    "measurementCountValidation": 39878,

    "lastMeasurementValidation": "<measurement>",

    "lastEvent": "<event>",
    "eventCount": 40192,

    "firstEvent": "<event>",
    "eventCountValidation": 40192
}


@pytest.mark.parametrize("required_key", example_c8y_data.keys())
def test_key_present(required_key):
    assert all([required_key in device for device in c8y_data])


def test_unique_id():
    ids = set([device['id'] for device in c8y_data])
    assert len(ids) == len(c8y_data)


def test_valid_parent_id():
    rootDeviceParent = ''
    ids = set([device['id'] for device in c8y_data] + [rootDeviceParent])

    for device in c8y_data:
        assert device['parent'] in ids, f'Invalid device inventory structure, {device['id']}'


def test_supported_series_has_measurements():
    for device in c8y_data:
        if device['c8y_supportedSeries']:
            assert device['measurementCount'] > 0, f"{device['id']} - device should have at least 1 measurement"


def test_missing_measurement_values():
    for device in c8y_data:
        assert not device['measurementCount'] == -1, f"{device['id']}"
        assert not device['measurementCountValidation'] == -1, f"{device['id']}"


def test_missing_event_values():
    for device in c8y_data:
        assert not device['eventCount'] == -1, f"{device['id']}"
        assert not device['eventCountValidation'] == -1, f"{device['id']}"


def test_validate_measurement_count():
    for device in c8y_data:
        if -1 in [device['measurementCount'], device['measurementCountValidation']]:
            continue
        assert device['measurementCount'] == device['measurementCountValidation'], f"{device['id']}"


def test_validate_event_count():
    for device in c8y_data:
        if -1 in [device['eventCount'], device['eventCountValidation']]:
            continue
        assert device['eventCount'] == device['eventCountValidation'], f"{device['id']}"


def test_valid_time_format():
    for device in c8y_data:
        for dataObject in ['lastMeasurement', 'firstMeasurement', 'firstEvent', 'lastEvent',
                           'lastMeasurementValidation']:
            if not device[dataObject]:
                continue
            dateString = device[dataObject]['time']
            try:
                parse(dateString)
            except ParserError:
                pytest.fail(f"Parsing failed for date string: {dateString}")


def test_validate_last_and_first_measurement_order():
    for device in c8y_data:
        earliest = device['firstMeasurement']
        latest = device['lastMeasurement']
        if earliest and latest:
            assert parse(earliest['time']).date() <= parse(latest['time']).date()


def test_validate_last_and_first_event_order():
    for device in c8y_data:
        earliest = device['lastEvent']
        latest = device['firstEvent']
        if earliest and latest:
            assert parse(earliest['time']).date() <= parse(latest['time']).date()