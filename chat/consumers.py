import json
import logging
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()
logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time chat"""
    
    async def connect(self):
        # Get token from query parameters
        query_string = self.scope.get('query_string', b'').decode()
        
        # Parse query string properly
        try:
            parsed_qs = parse_qs(query_string)
            token = parsed_qs.get('token', [None])[0]
        except Exception as e:
            logger.error(f"Error parsing query string: {e}")
            token = None
        
        if not token:
            logger.warning("No token provided in WebSocket connection")
            await self.close()
            return
        
        # Authenticate using the token
        try:
            access_token = AccessToken(token)
            user_id = access_token.get('user_id')
            if not user_id:
                logger.warning("No user_id in token")
                await self.close()
                return
                
            self.user = await self.get_user(user_id)
            
            if self.user and self.user.is_authenticated:
                # Join user's personal group for receiving messages
                self.group_name = f"user_{self.user.id}"
                await self.channel_layer.group_add(
                    self.group_name,
                    self.channel_name
                )
                await self.accept()
                logger.info(f"WebSocket connected for user {self.user.id}")
                return
        except InvalidToken as e:
            logger.error(f"Invalid token: {e}")
        except TokenError as e:
            logger.error(f"Token error: {e}")
        except Exception as e:
            logger.error(f"Error during WebSocket authentication: {e}")
        
        # If we get here, authentication failed
        await self.close()
    
    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'chat_message':
                # Broadcast message to recipient
                recipient_id = data.get('recipient_id')
                message_content = data.get('message')
                conversation_id = data.get('conversation_id')
                
                # Send to recipient's group
                recipient_group = f"user_{recipient_id}"
                await self.channel_layer.group_send(
                    recipient_group,
                    {
                        'type': 'chat_message',
                        'message': message_content,
                        'sender_id': self.user.id,
                        'sender_username': self.user.username,
                        'conversation_id': conversation_id,
                    }
                )
                
                # Also send back to sender for confirmation
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'message_sent',
                        'message': message_content,
                        'conversation_id': conversation_id,
                    }
                )
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def chat_message(self, event):
        """Handle incoming chat message from group"""
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'conversation_id': event['conversation_id'],
        }))
    
    async def message_sent(self, event):
        """Confirm message was sent"""
        await self.send(text_data=json.dumps({
            'type': 'sent',
            'message': event['message'],
            'conversation_id': event['conversation_id'],
        }))
