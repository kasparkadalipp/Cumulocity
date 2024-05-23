import instructor
import pandas as pd
import os
from openai import OpenAI
from pydantic import BaseModel
from skllm.config import SKLLMConfig
from src.utils import tqdmFormat, getPath, readFile
from tqdm import tqdm


class Measurement(BaseModel):
    description: str
    domain: str
    subdomain: str


def requestChatGPTDescription(client, message_data, model):
    return client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content":
                    'Take on the persona of a data analyst who is proficient in interpreting JSON objects and '
                    'extracting meaningful insights from them. '
                    'The user will provide JSON objects representing measurement data from a smart city IoT device.'

            },
            {
                "role": "user",
                "content": 'Ignore device specific information and concisely summarise what kind of data is being sent. '
                           'Avoid generic terms like "IoT" and "smart city". '
                           'Also provide example of a smart city domain this device belongs to.'
                           f"{message_data} "
            }
        ],
        max_retries=5,
        response_model=Measurement
    )


def transformData(model="gpt-4-turbo"):  # "gpt-3.5-turbo"
    inputData = readFile('chatGPT input.json'),

    SKLLMConfig.set_openai_key(os.getenv('OPENAI_API_KEY'))
    SKLLMConfig.set_openai_org(os.getenv('OPENAPI_ORGANIZATION_ID'))
    client = instructor.patch(OpenAI())

    result = {}
    failedRequests = []
    for deviceId, data in tqdm(inputData.items(), desc=f"requesting data for {model}", bar_format=tqdmFormat):
        try:
            response = requestChatGPTDescription(client, data, model)
            result[deviceId] = {
                'id': deviceId,
                'name': data['device'],
                'domain': response.domain,
                'description': response.description,
                'isAggregated': response.isAggregated,
                'input': data
            }
        except:
            failedRequests.append(deviceId)

    df = pd.DataFrame(result.values())
    df.to_csv(getPath(f"{model} description.csv"), encoding='utf-8-sig', index=False)
