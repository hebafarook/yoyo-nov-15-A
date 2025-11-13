from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timezone
import logging
import uuid
from utils.database import db, prepare_for_mongo, parse_from_mongo
from routes.auth_routes import verify_token

router = APIRouter()
logger = logging.getLogger(__name__)
security = HTTPBearer()

class Message(BaseModel):
    id: str = None
    sender_username: str
    sender_name: str
    recipient_usernames: List[str]  # List for group messages
    recipient_type: str  # "individual", "team", "parent_group", "coach_group"
    subject: str
    message: str
    timestamp: datetime = None
    read_by: List[str] = []  # List of usernames who have read the message
    replied_to: Optional[str] = None  # Message ID if this is a reply

class MessageCreate(BaseModel):
    recipient_usernames: List[str]
    recipient_type: str = "individual"
    subject: str
    message: str
    replied_to: Optional[str] = None

@router.post("/send")
async def send_message(
    message_data: MessageCreate,
    current_user: dict = Depends(verify_token)
):
    """Send a message to one or more recipients"""
    try:
        sender_username = current_user.get('username')
        sender_role = current_user.get('role')
        user_id = current_user.get('user_id')
        
        # Get sender's full name
        sender = await db.users.find_one({"id": user_id})
        sender_name = sender.get('full_name', sender_username) if sender else sender_username
        
        # Validate recipients exist
        recipients = await db.users.find({
            "username": {"$in": message_data.recipient_usernames}
        }).to_list(length=100)
        
        if len(recipients) != len(message_data.recipient_usernames):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more recipients not found"
            )
        
        # For coaches/parents, verify they have access to send to these recipients
        if sender_role in ['coach', 'parent']:
            user_doc = await db.users.find_one({"id": user_id})
            managed_players = user_doc.get('managed_players', [])
            
            # Check if trying to message players they manage
            for recipient in recipients:
                recipient_role = recipient.get('role')
                recipient_username = recipient.get('username')
                
                # Can always message other coaches
                if recipient_role == 'coach':
                    continue
                
                # Can message players they manage
                if recipient_role == 'player' and recipient_username in managed_players:
                    continue
                
                # Can message parents of players they manage
                if recipient_role == 'parent':
                    parent_managed = recipient.get('managed_players', [])
                    # Check if there's any overlap between coach's players and parent's children
                    if any(player in managed_players for player in parent_managed):
                        continue
                
                # If none of the above, access denied
                if sender_role != 'coach':  # Coaches have broader access
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Access denied: You cannot message {recipient_username}"
                    )
        
        # Create message
        message = {
            "id": str(uuid.uuid4()),
            "sender_username": sender_username,
            "sender_name": sender_name,
            "sender_role": sender_role,
            "recipient_usernames": message_data.recipient_usernames,
            "recipient_type": message_data.recipient_type,
            "subject": message_data.subject,
            "message": message_data.message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "read_by": [],
            "replied_to": message_data.replied_to
        }
        
        # Save to database
        await db.messages.insert_one(prepare_for_mongo(message))
        
        logger.info(f"Message sent from {sender_username} to {message_data.recipient_usernames}")
        
        return {
            "message": "Message sent successfully",
            "message_id": message["id"],
            "recipients": len(message_data.recipient_usernames)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )

@router.get("/inbox")
async def get_inbox(
    current_user: dict = Depends(verify_token),
    unread_only: bool = False
):
    """Get all messages for current user"""
    try:
        username = current_user.get('username')
        
        # Build query
        query = {"recipient_usernames": username}
        
        if unread_only:
            query["read_by"] = {"$nin": [username]}
        
        # Fetch messages
        messages = await db.messages.find(query).sort("timestamp", -1).to_list(length=200)
        
        # Parse and format messages
        inbox = []
        for msg in messages:
            parsed_msg = parse_from_mongo(msg)
            inbox.append({
                "id": parsed_msg.get("id"),
                "sender_username": parsed_msg.get("sender_username"),
                "sender_name": parsed_msg.get("sender_name"),
                "sender_role": parsed_msg.get("sender_role"),
                "subject": parsed_msg.get("subject"),
                "message": parsed_msg.get("message"),
                "timestamp": parsed_msg.get("timestamp"),
                "is_read": username in parsed_msg.get("read_by", []),
                "recipient_type": parsed_msg.get("recipient_type"),
                "recipient_count": len(parsed_msg.get("recipient_usernames", [])),
                "replied_to": parsed_msg.get("replied_to")
            })
        
        return {
            "messages": inbox,
            "total": len(inbox),
            "unread": sum(1 for m in inbox if not m["is_read"])
        }
        
    except Exception as e:
        logger.error(f"Error fetching inbox: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch inbox: {str(e)}"
        )

@router.get("/sent")
async def get_sent_messages(
    current_user: dict = Depends(verify_token)
):
    """Get all messages sent by current user"""
    try:
        username = current_user.get('username')
        
        # Fetch sent messages
        messages = await db.messages.find({
            "sender_username": username
        }).sort("timestamp", -1).to_list(length=200)
        
        # Parse and format messages
        sent = []
        for msg in messages:
            parsed_msg = parse_from_mongo(msg)
            sent.append({
                "id": parsed_msg.get("id"),
                "recipient_usernames": parsed_msg.get("recipient_usernames"),
                "recipient_type": parsed_msg.get("recipient_type"),
                "subject": parsed_msg.get("subject"),
                "message": parsed_msg.get("message"),
                "timestamp": parsed_msg.get("timestamp"),
                "read_count": len(parsed_msg.get("read_by", [])),
                "recipient_count": len(parsed_msg.get("recipient_usernames", []))
            })
        
        return {
            "messages": sent,
            "total": len(sent)
        }
        
    except Exception as e:
        logger.error(f"Error fetching sent messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch sent messages: {str(e)}"
        )

@router.get("/message/{message_id}")
async def get_message(
    message_id: str,
    current_user: dict = Depends(verify_token)
):
    """Get a specific message and mark as read"""
    try:
        username = current_user.get('username')
        
        message = await db.messages.find_one({"id": message_id})
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Check if user is sender or recipient
        sender = message.get("sender_username")
        recipients = message.get("recipient_usernames", [])
        
        if username not in recipients and username != sender:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You are not authorized to view this message"
            )
        
        # Mark as read if user is a recipient
        if username in recipients and username not in message.get("read_by", []):
            await db.messages.update_one(
                {"id": message_id},
                {"$addToSet": {"read_by": username}}
            )
        
        parsed_msg = parse_from_mongo(message)
        
        return {
            "id": parsed_msg.get("id"),
            "sender_username": parsed_msg.get("sender_username"),
            "sender_name": parsed_msg.get("sender_name"),
            "sender_role": parsed_msg.get("sender_role"),
            "recipient_usernames": parsed_msg.get("recipient_usernames"),
            "recipient_type": parsed_msg.get("recipient_type"),
            "subject": parsed_msg.get("subject"),
            "message": parsed_msg.get("message"),
            "timestamp": parsed_msg.get("timestamp"),
            "read_by": parsed_msg.get("read_by", []),
            "replied_to": parsed_msg.get("replied_to")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch message: {str(e)}"
        )

@router.delete("/message/{message_id}")
async def delete_message(
    message_id: str,
    current_user: dict = Depends(verify_token)
):
    """Delete a message (sender can delete sent, recipient can delete from inbox)"""
    try:
        username = current_user.get('username')
        
        message = await db.messages.find_one({"id": message_id})
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        sender = message.get("sender_username")
        recipients = message.get("recipient_usernames", [])
        
        # Check if user is sender or recipient
        if username not in recipients and username != sender:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You cannot delete this message"
            )
        
        # Delete the message
        await db.messages.delete_one({"id": message_id})
        
        return {"message": "Message deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete message: {str(e)}"
        )

@router.get("/contacts")
async def get_contacts(
    current_user: dict = Depends(verify_token)
):
    """Get list of people user can message"""
    try:
        username = current_user.get('username')
        role = current_user.get('role')
        user_id = current_user.get('user_id')
        
        contacts = []
        
        # Get current user
        user = await db.users.find_one({"id": user_id})
        managed_players = user.get('managed_players', []) if user else []
        
        if role == 'player':
            # Players can message their coaches and parents
            # Find coaches who manage this player
            coaches = await db.users.find({
                "role": "coach",
                "managed_players": username
            }).to_list(length=50)
            
            for coach in coaches:
                contacts.append({
                    "username": coach.get('username'),
                    "full_name": coach.get('full_name'),
                    "role": "coach",
                    "type": "individual"
                })
            
            # Find parents who have this player as child
            parents = await db.users.find({
                "role": "parent",
                "managed_players": username
            }).to_list(length=10)
            
            for parent in parents:
                contacts.append({
                    "username": parent.get('username'),
                    "full_name": parent.get('full_name'),
                    "role": "parent",
                    "type": "individual"
                })
        
        elif role == 'parent':
            # Parents can message their children and their children's coaches
            # Get children
            children = await db.users.find({
                "username": {"$in": managed_players},
                "role": "player"
            }).to_list(length=20)
            
            for child in children:
                contacts.append({
                    "username": child.get('username'),
                    "full_name": child.get('full_name'),
                    "role": "player",
                    "type": "individual"
                })
            
            # Get coaches of their children
            coaches = await db.users.find({
                "role": "coach",
                "managed_players": {"$in": managed_players}
            }).to_list(length=50)
            
            for coach in coaches:
                contacts.append({
                    "username": coach.get('username'),
                    "full_name": coach.get('full_name'),
                    "role": "coach",
                    "type": "individual"
                })
        
        elif role == 'coach':
            # Coaches can message their players, parents of their players, and other coaches
            # Get managed players
            players = await db.users.find({
                "username": {"$in": managed_players},
                "role": "player"
            }).to_list(length=100)
            
            for player in players:
                contacts.append({
                    "username": player.get('username'),
                    "full_name": player.get('full_name'),
                    "role": "player",
                    "type": "individual"
                })
            
            # Get parents of managed players
            parents = await db.users.find({
                "role": "parent",
                "managed_players": {"$in": managed_players}
            }).to_list(length=100)
            
            for parent in parents:
                contacts.append({
                    "username": parent.get('username'),
                    "full_name": parent.get('full_name'),
                    "role": "parent",
                    "type": "individual"
                })
            
            # Get all other coaches
            other_coaches = await db.users.find({
                "role": "coach",
                "username": {"$ne": username}
            }).to_list(length=50)
            
            for coach in other_coaches:
                contacts.append({
                    "username": coach.get('username'),
                    "full_name": coach.get('full_name'),
                    "role": "coach",
                    "type": "individual"
                })
            
            # Add group options for coaches
            if managed_players:
                contacts.append({
                    "username": "all_players",
                    "full_name": "All Players (Team Broadcast)",
                    "role": "group",
                    "type": "team",
                    "members": managed_players
                })
                
                # Get parents of all managed players
                parent_usernames = [p.get('username') for p in parents]
                if parent_usernames:
                    contacts.append({
                        "username": "all_parents",
                        "full_name": "All Parents (Group Message)",
                        "role": "group",
                        "type": "parent_group",
                        "members": parent_usernames
                    })
        
        # Remove duplicates based on username
        unique_contacts = []
        seen = set()
        for contact in contacts:
            if contact['username'] not in seen:
                seen.add(contact['username'])
                unique_contacts.append(contact)
        
        return {
            "contacts": unique_contacts,
            "total": len(unique_contacts)
        }
        
    except Exception as e:
        logger.error(f"Error fetching contacts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch contacts: {str(e)}"
        )
