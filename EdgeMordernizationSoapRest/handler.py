import json
import os
import boto3
from datetime import datetime
from datetime import datetime
import xmltodict


dynamodb = boto3.resource('dynamodb')
step_function = boto3.client('stepfunctions')

def convert_xml_to_json(event, context):
    """
    Input: { "requestType": "application/xml", "input": "<xml>...</xml>" }
    Output: JSON dict with parsed XML content
    """
    try:
        xml_string = event.get("input")
        parsed = xmltodict.parse(xml_string)
        print(f"Parsed XML: {json.dumps(parsed)}")  # Debug log
        
        # We must look inside the root <request> tag!
        root = parsed.get("request", {})
        
        return {
            # Added .strip() just to clean up any weird spaces from the headers
            "requestType": event.get("requestType", "application/xml").strip(), 
            "ticketDetails": root.get("ticketDetails", {}),
            "userId": root.get("userId")
        }
    except Exception as e:
        print(f"Error converting XML to JSON: {e}")
        raise e


def check_user(event, context):
    """
    Input event example from XML conversion: 
    { "userId": "user_123", "ticketDetails": {...}, "requestType": "application/xml" }
    
    Input event example directly from API Gateway (JSON): 
    { "requestType": "application/json", "input": "{\"userId\": \"user_123\", ...}" }
    """
    users_table = dynamodb.Table(os.environ['USERS_TABLE'])
    
    # --- Extract data depending on whether it's wrapped in 'input' ---
    if 'input' in event and isinstance(event['input'], str):
        # The request came straight from API Gateway as JSON
        parsed_input = json.loads(event['input'])
        user_id = parsed_input.get('userId')
        ticket_details = parsed_input.get('ticketDetails')
    else:
        # The request came from ConvertXmlToJson and is already flattened
        user_id = event.get('userId')
        ticket_details = event.get('ticketDetails')
    # ----------------------------------------------------------------------

    print(f"Checking user: {user_id} with ticket details: {json.dumps(ticket_details)}")  # Debug log
    
    try:
        response = users_table.get_item(Key={'userId': user_id})
        
        if 'Item' in response:
            return {
                'userFound': True,
                'userId': user_id,
                'userName': response['Item'].get('userName', 'Unknown'),
                'ticketDetails': ticket_details,
                'requestType': event.get("requestType")
            }
        else:
            return {'userFound': False, 'requestType': event.get("requestType")}        
    except Exception as e:
        print(f"Error checking user: {e}")
        raise e


def process_ticket(event, context):
    """
    Input event is the output from check_user:
    { "userFound": True, "userId": "...", "ticketDetails": {...} }
    """
    user_id = event.get('userId')
    user_name = event.get('userName')
    ticket_details = event.get('ticketDetails')
    
    ticket_id = ticket_details.get('ticketId')
    ticket_type = ticket_details.get('type') # Expected 'Incident' or 'Service'
    price = ticket_details.get('price')
    
    if not ticket_id or not ticket_type:
        raise ValueError("Invalid ticket details provided")

    # Select the correct table based on ticket type
    if ticket_type == 'incident':
        table_name = os.environ['INCIDENT_TABLE']
    elif ticket_type == 'service':
        table_name = os.environ['SERVICE_TABLE']
    else: raise ValueError("Unknown ticket type provided")
        
    table = dynamodb.Table(table_name)
    
    item = {
        'ticketId': ticket_id,
        'userId': user_id,
        'userName': user_name,
        'type': ticket_type,
        'price': price,
        'createdAt': datetime.utcnow().isoformat()
    }
    
    try:
        table.put_item(Item=item)
        return {
            'status': 'Success',
            'message': f'Ticket processed in {ticket_type} table',
            'ticketId': ticket_id,
            'requestType': event.get("requestType"),
            'outputHeaders': { "Content-Type": "application/json" }
        }
    except Exception as e:
        print(f"Error processing ticket: {e}")
        raise e
    
# ---------- Convert JSON to XML ----------
def convert_json_to_xml(event, context):
    """
    Input: JSON dict from process_ticket
    Output: XML string
    """
    try:
        # 1. Remove the headers from the data so they don't get converted into XML tags
        if "outputHeaders" in event:
            del event["outputHeaders"]
            
        # 2. Wrap the response in a proper SOAP Envelope structure
        soap_format = {
            "soapenv:Envelope": {
                "@xmlns:soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
                "soapenv:Body": {
                    "response": event
                }
            }
        }
        
        # 3. Convert to XML
        xml_string = xmltodict.unparse(soap_format, pretty=True)
        
        return xml_string
    except Exception as e:
        print(f"Error converting JSON to XML: {e}")
        raise e

    