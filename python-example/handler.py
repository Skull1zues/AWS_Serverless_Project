import json
import time


def hello(event, context):
    print("hello world")
    time.sleep(4)  # Simulate a delay
    return "response"
