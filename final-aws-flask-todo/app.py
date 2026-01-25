import os

import boto3, uuid
from flask import Flask, jsonify, make_response, request
import time, datetime
# from mangum import Mangum

app = Flask(__name__)

import os
region = os.environ["REGION_NAME"] 
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TODO_TABLE"])

@app.route("/todos", methods=["POST"])
def create_todo():
    data = request.get_json(force=True)
    if not data or not isinstance(data.get("todo"), str):
        return jsonify({"error": "Validation Failed"}), 400

    timestamp = int(time.time())
    todo_id = str(uuid.uuid1())

    item = {
        "id": todo_id,
        "todo": data["todo"],
        "checked": False,
        "createdAt": timestamp,
        "updatedAt": timestamp,
    }

    table.put_item(Item=item)
    return jsonify(item), 201

@app.route("/todos/list", methods=["GET"])
def list_todos():
    resp = table.scan()
    return jsonify(resp["Items"]), 200

@app.route("/todos/<id>", methods=["GET"])
def get_todo(id):
    try:
        resp = table.get_item(Key={"id": id})
    except Exception as e:
        print(e)
        return jsonify({"error": "Internal Server Error"}), 500

    item = resp.get("Item")
    if item:
        return jsonify(item), 200
    else:
        return jsonify({"error": "Todo not found"}), 404




@app.route("/todos/update/<id>", methods=["PUT"])
def update_todo(id):
    data = request.get_json(force=True)

    # Validation
    if not isinstance(data.get("todo"), str) or not isinstance(data.get("checked"), bool):
        print("Value of todo or checked is invalid")
        return jsonify({"error": "Invalid input"}), 400

    datetime_str = datetime.datetime.utcnow().isoformat()

    try:
        resp = table.update_item(
            Key={"id": id},
            ExpressionAttributeNames={
                "#todo_text": "todo"
            },
            ExpressionAttributeValues={
                ":todo": data["todo"],
                ":checked": data["checked"],
                ":updatedAt": datetime_str
            },
            UpdateExpression="SET #todo_text = :todo, checked = :checked, updatedAt = :updatedAt",
            ReturnValues="ALL_NEW"
        )
    except Exception as e:
        print(e)
        return jsonify({"error": "Internal Server Error"}), 500

    return jsonify(resp.get("Attributes")), 200


@app.route("/todos/delete/<id>", methods=["DELETE"])
def delete_todo(id):
    try:
        # Delete item by primary key
        table.delete_item(
            Key={"id": id},
            ConditionExpression="attribute_exists(id)"  # ensures item exists
        )
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return jsonify({"error": "Todo not found"}), 404

    return jsonify({"data": "Deletion Successful!"}), 200

# Lambda entrypoint


# def handler(event, context):
#     return awsgi.response(app, event, context)
# handler = Mangum(app,lifespan="off")
