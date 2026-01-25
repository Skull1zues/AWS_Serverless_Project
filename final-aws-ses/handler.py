import json
import boto3
from botocore.exceptions import ClientError



ses = boto3.client("ses")




def createContact(event, context):
    print("Received event: " + json.dumps(event, indent=2))

     
    
    try:
        body = json.loads(event["body"])
        to = body.get("to")
        from_ = body.get("from")
        subject = body.get("subject")
        message = body.get("message")

        if not to or not from_ or not subject or not message:
            return {
                "headers": {
                    "Content-Type": "application/json", 
                    "Access-Control-Allow-Origin": "*",
                    'Access-Control-Allow-Methods': '*',
                    'Access-Control-Allow-Headers': '*',
                        },
                "statusCode": 400,
                "body": "Bad Request: Missing required fields."
            }

        mail_response = ses.send_email(
            Destination={
                "ToAddresses": [to],
            },
            Message={
                "Body": {
                    "Text": {"Charset": "UTF-8", "Data": message},
                },
                "Subject": {"Charset": "UTF-8", "Data": subject},
            },
            Source=from_,
        )
        print("Email sent! Message ID:", mail_response["MessageId"])
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json", 
                "Access-Control-Allow-Origin": "*",
                'Access-Control-Allow-Methods': '*',
                'Access-Control-Allow-Headers': '*',
                        },
            "body": json.dumps({"message": "Email sent successfully", "id": mail_response["MessageId"]}),
        }
    
    except ClientError as e:
        print("SES error:", e.response["Error"]["Message"])
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json", 
                "Access-Control-Allow-Origin": "*",
                'Access-Control-Allow-Methods': '*',
                'Access-Control-Allow-Headers': '*',
                        },
            "body": json.dumps({"error": e.response["Error"]["Message"]}),
        }


    except Exception as e:
        print("Error sending email:", str(e))
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json", 
                "Access-Control-Allow-Origin": "*",
                'Access-Control-Allow-Methods': '*',
                'Access-Control-Allow-Headers': '*',
                        },
            "body": json.dumps({"error": "Internal Server Error: Unable to send email."}),
        }
