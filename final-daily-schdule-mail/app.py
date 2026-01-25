import os
import json
import uuid
import datetime
import boto3
from flask import Flask, request, Response, make_response, jsonify
from botocore.exceptions import ClientError

app = Flask(__name__)

# DynamoDB client setup
dynamodb_client = boto3.client('dynamodb')
if os.environ.get('IS_OFFLINE'):
    dynamodb_client = boto3.client(
        'dynamodb',
        region_name='localhost',
        endpoint_url='http://localhost:8000'
    )

# S3 client setup
s3 = boto3.client('s3')
bucket_name = 'soumya1998-json-bucket'
USERS_TABLE = os.environ.get('USERS_TABLE', 'default-users-table')


# ---------------- QUOTES ROUTE ----------------
@app.route('/quotes', methods=['GET'])
def getQuotes():
    try:
        object_key = 'quotes.json'
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        quotes_data = response['Body'].read().decode('utf-8')
        quotes_list = json.loads(quotes_data)

        return Response(
            json.dumps(quotes_list),
            status=200,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
    except Exception as e:
        return Response(
            json.dumps({"error": f"Failed to fetch quotes: {str(e)}"}),
            status=500,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )


# ---------------- SUBSCRIBE ROUTE ----------------
@app.route('/subscribe', methods=['POST'])
def subscribeUser():
    try:
        data = request.get_json(force=True)
        if not data or "email" not in data:
            return Response(
                json.dumps({"message": "Email is required"}),
                status=400,
                mimetype="application/json",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*"
                }
            )

        timeStamp = datetime.datetime.now().isoformat()
        params = {
            "TableName": USERS_TABLE,
            "Item": {
                "userId": {"S": uuid.uuid4().hex},
                "email": {"S": data["email"]},
                "createdAt": {"S": timeStamp},
                "subscriber": {"BOOL": True},
                "updatedAt": {"S": timeStamp}
            }
        }
        dynamodb_client.put_item(**params)

        return Response(
            json.dumps({"message": "Subscription successful"}),
            status=200,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )

    except ClientError as e:
        return Response(
            json.dumps({"message": f"DynamoDB error: {str(e)}"}),
            status=500,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
    except Exception as e:
        return Response(
            json.dumps({"message": f"Unexpected error: {str(e)}"}),
            status=500,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )


# ---------------- ERROR HANDLER ----------------
@app.errorhandler(404)
def resource_not_found(e):
    return Response(
        json.dumps({"error": "Not found!"}),
        status=404,
        mimetype="application/json",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )