import requests
import time
import json
import dashscope
from dashscope import Generation
from http import HTTPStatus
import json


# bot 'qwen-plus-beta-v1'
def chat_single_qwen(question_str='please answer the question: why sun is always good',bot='qwen-plus-beta-v1'):
    time.sleep(1)
    dashscope.api_key='' # TOKEN HERE TODO

    response=Generation.call(
        model=bot,
        prompt=question_str
        )

    return response



# chat_single_qwen()
