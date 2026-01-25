import json
import os

def hello(event, context):

    return os.environ['FIRST_NAME']
    # body = {
    #     "message": "Go Serverless v4.0! Your function executed successfully!"
    # }

    # return {"statusCode": 200, "body": json.dumps(body)}
