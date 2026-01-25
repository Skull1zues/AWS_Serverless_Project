import os
import json
import boto3
import requests

# Initialize SNS client
sns = boto3.client("sns")

def publish_to_sns(message: str):
    """Publish a message to SNS topic."""
    return sns.publish(
        Message=message,
        TopicArn=os.environ.get("SNS_TOPIC_ARN")
    )

def build_email_body(identity, form):
    """Build email body string."""
    return f"Message: {form.get('message')}\n" \
           f"Name: {form.get('name')}\n" \
           f"Email: {form.get('email')}\n" \
           f"Service information: {identity.get('sourceIp')} - {identity.get('userAgent')}"

def static_mailer(event, context):
    try:
        print("EVENT::", event)

        # Parse request body
        data = json.loads(event.get("body", "{}"))

        # Build email body
        identity = event.get("requestContext", {}).get("identity", {})
        email_body = build_email_body(identity, data)

        # Publish to SNS
        publish_to_sns(email_body)

        # Call subscribe endpoint
        try:
            response = requests.post(
                "https://byclh6knwl.execute-api.ap-south-1.amazonaws.com/dev/subscribe",
                json={"email": data.get("email")}
            )
            print("Subscribe response:", response.text)
        except Exception as e:
            print("Error subscribing user:::", str(e))

        # Return Lambda response
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",  # Required for CORS
                "Access-Control-Allow-Credentials": "false"
            },
            "body": json.dumps({"message": "OK"})
        }

    except Exception as e:
        print("Unexpected error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Error: {str(e)}"})
        }