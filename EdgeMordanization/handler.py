import json
import os
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')

def check_user(event, context):
    """
    Input event example: 
    { "userId": "user_123", "ticketDetails": {...} }
    """
    users_table = dynamodb.Table(os.environ['USERS_TABLE'])
    
    user_id = event.get('userId')
    ticket_details = event.get('ticketDetails')
    
    try:
        response = users_table.get_item(Key={'userId': user_id})
        
        if 'Item' in response:
            return {
                'userFound': True,
                'userId': user_id,
                'userName': response['Item'].get('userName', 'Unknown'),
                'ticketDetails': ticket_details
            }
        else:
            return {
                'userFound': False
            }
            
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
            'ticketId': ticket_id
        }
    except Exception as e:
        print(f"Error processing ticket: {e}")
        raise e