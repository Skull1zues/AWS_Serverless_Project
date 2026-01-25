import json
from datetime import datetime
import boto3
from io import BytesIO
from PIL import Image, ImageOps
import os
import uuid
import urllib.parse
from decimal import Decimal



s3 = boto3.client("s3")
size = int(os.environ["THUMBNAIL_SIZE"])
dbtable = str(os.environ["DYNAMODB_TABLE"])
dynamodb = boto3.resource("dynamodb", region_name=os.environ["REGION_NAME"])

def get_S3_image(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    image_content = response["Body"].read()
    image = Image.open(BytesIO(image_content))
    return image


def image_to_thumbnail(image):
    return ImageOps.fit(image, (size, size), Image.Resampling.LANCZOS)


def new_filename(key):
    key_parts = key.split(".")
    return f"{key_parts[0]}_thumbnail.png"

def upload_thumbnail_to_s3(bucket, thumbnail_key, image, size):
    out_thumbnail = BytesIO()
    image.save(out_thumbnail, format="PNG" )
    out_thumbnail.seek(0)

    response = s3.put_object(
        Body = out_thumbnail,
        Bucket = bucket,
        ContentType = "image/png",
        Key = thumbnail_key
    )
    print(response)

    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": thumbnail_key},
        ExpiresIn=3600
    )

    return url


def s3_save_thumbnail_url_to_dynamodb(url_path, img_size):
    toint = Decimal(str((img_size*0.53)/1000))
    table = dynamodb.Table(dbtable)
    response = table.put_item(
        Item={
            'id': str(uuid.uuid4()),
            'thumbnail_url': url_path,
            'approx_size_kb': toint,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    )
    return{
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(response)
    }

def s3_thumbnail_generator(event, context):
    #parce the S3 event
    print("Event: ", event)
    bucket = event["Records"][0]["s3"]["bucket"]['name']
    key = urllib.parse.unquote_plus(event["Records"][0]["s3"]["object"]["key"])
    size = event["Records"][0]["s3"]["object"]['size']

    if(not key.endswith("_thumbnail.png")):
        image = get_S3_image(bucket, key)

        thumbnail = image_to_thumbnail(image)

        thumbnail_key = new_filename(key)

        url = upload_thumbnail_to_s3(bucket, thumbnail_key,thumbnail, size)

        response = s3_save_thumbnail_url_to_dynamodb(url, size)

        return response
    
# ====== RD - (no Create), Update, Delete functions needed for this use case) ======
def s3_get_thumbnails(event, context):
    table = dynamodb.Table(dbtable)
    response = table.scan()
    print(f"Scan response: {response}")
    items = response.get('Items', [])
    # Pagination handling
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(items , cls=DecimalEncoder)
    }

def s3_get_thumbnail_by_id(event, context):
    table = dynamodb.Table(dbtable)
    thumbnail_id = event['pathParameters']['id']
    response = table.get_item(Key={'id': thumbnail_id})
    item = response.get('Item', {})
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(item, cls=DecimalEncoder)
    }

def s3_delete_thumbnail_by_id(event, context):
    table = dynamodb.Table(dbtable)
    thumbnail_id = event['pathParameters']['id']
    response = table.delete_item(Key={'id': thumbnail_id})
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'message': f'Thumbnail with id {thumbnail_id} deleted successfully.'})
    }

# Decimal encoder for DynamoDB items
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            # Convert to float or int depending on your needs
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

