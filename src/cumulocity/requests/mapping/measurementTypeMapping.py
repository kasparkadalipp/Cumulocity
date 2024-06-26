from src.utils import listFileNames, readFile, saveToFile, listDirectories
from collections import Counter
from tabulate import tabulate


def createMeasurementMapping():
    c8y_data = readFile('c8y_data.json')
    eventTypesMapping = {device['id']: set() for device in c8y_data}
    for folder in listDirectories('measurements'):
        for fileName in listFileNames(folder):
            for device in readFile(fileName):
                deviceId = device['deviceId']
                # if 'total' in device:
                #     measurement = device['total']['measurement']
                #     if measurement:
                #         eventTypesMapping[deviceId].add(measurement['type'])

                if 'fragmentSeries' in device:
                    for fragmentSeries in device['fragmentSeries']:
                        measurement = fragmentSeries['measurement']
                        if measurement:
                            eventTypesMapping[deviceId].add((measurement['type'], fragmentSeries['fragment'], fragmentSeries['series']))

                if 'typeFragmentSeries' in device:
                    for typeFragmentSeries in device['typeFragmentSeries']:
                        measurement = typeFragmentSeries['measurement']
                        if measurement:
                            eventTypesMapping[deviceId].add((measurement['type'], typeFragmentSeries['fragment'], typeFragmentSeries['series']))

    data = {key: sorted(value) for key, value in eventTypesMapping.items()}
    saveToFile(data, f"measurements/c8y_measurements_id_to_type_mapping.json")


def mappingOverview():
    jsonData = readFile("measurements/c8y_measurements_id_to_type_mapping.json")
    data = []
    for key, value in jsonData.items():
        deviceTypes = set()
        for measurementType, fragment, series in value:
            deviceTypes.add(measurementType)
        data.append(tuple(sorted(deviceTypes)))
    counter = Counter([tuple(value) for value in sorted(data)])

    data = [(value, key) for key, value in counter.items()]
    table = tabulate(data, headers=["Count", "Types"], tablefmt="pipe")
    print(table)
