import os
from collections import Counter
from src.utils import fileNamesInFolder, readFile
from src.utils import readFileContents, saveToFile
from tabulate import tabulate


def listDirectories(path):
    entries = os.listdir(path)
    directories = [entry for entry in entries if os.path.isdir(os.path.join(path, entry))]
    return directories


def createEventTypeMapping():
    alwaysPresentKeys = ["lastUpdated", "creationTime", "self", "source", "time", "id", "text", "type"]
    c8y_data = readFile('telia/c8y_data.json')
    eventTypesMapping = {device['id']: set() for device in c8y_data}

    for folder in listDirectories('../data/telia/events'):
        for file in fileNamesInFolder(f'../data/telia/events/{folder}'):
            jsonFile = readFileContents(f'../data/telia/events/{folder}/{file}')
            for device in jsonFile:
                deviceId = device['deviceId']
                if 'total' in device:
                    event = device['total']['event']
                    if event:
                        eventKeys = [key for key in event.keys() if key not in alwaysPresentKeys]
                        for key in eventKeys:
                            eventTypesMapping[deviceId].add(key)

                if 'eventByType' in device:
                    for eventByType in device['eventByType']:
                        event = eventByType['event']
                        eventKeys = [key for key in event.keys() if key not in alwaysPresentKeys]
                        for key in eventKeys:
                            eventTypesMapping[deviceId].add(key)

    data = {key: sorted(value) for key, value in eventTypesMapping.items()}
    saveToFile(data, "telia/c8y_events_id_to_fragment_mapping.json", overwrite=True)


def mappingOverview():
    jsonData = readFile("../data/telia/c8y_events_id_to_fragment_mapping.json")
    counter = Counter([tuple(value) for key, value in sorted(jsonData.items())])

    data = [(value, key) for key, value in counter.items()]
    table = tabulate(data, headers=["Count", "Fragments"], tablefmt="pipe")
    print(table)