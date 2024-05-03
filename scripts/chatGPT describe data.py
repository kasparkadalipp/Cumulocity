from dotenv import load_dotenv
from skllm.config import SKLLMConfig
from tqdm import tqdm
from src.utils import readFile
from pydantic import BaseModel
from openai import OpenAI
from src.utils import tqdmFormat
import pandas as pd
import instructor
import os

load_dotenv('.env.telia')
SKLLMConfig.set_openai_key(os.getenv('OPENAI_API_KEY'))
SKLLMConfig.set_openai_org(os.getenv('OPENAPI_ORGANIZATION_ID'))

client = instructor.patch(OpenAI())
inputData = readFile('telia/chatGPT input.json')


class Measurement(BaseModel):
    description: str
    domain: str
    isAggregated: bool


def send_request(message_data, model="gpt-3.5-turbo"):  # "gpt-4-turbo"
    return client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Take on the persona of a data analyst. The user will provide JSON "
                           "objects representing measurement data from a smart city IoT device."

            },
            {
                "role": "user",
                "content": f'In one sentence describe the type of data that kind of device sends. '
                           f'Avoid referencing any specific device structures or proprietary terms and '
                           f'don\'t use generic terms like "IoT" and "smart city. {message_data}'
            }
        ],
        response_model=Measurement
    )


result = {}
failedRequests = []

for deviceId, data in tqdm(inputData.items(), desc="requesting data for gpt-3.5-turbo", bar_format=tqdmFormat):
    try:
        response = send_request(data, model="gpt-3.5-turbo")
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
df.to_csv("chatgpt 3.5 description.csv", encoding='utf-8-sig', index=False)
