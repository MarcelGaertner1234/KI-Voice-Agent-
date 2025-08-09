"""
Twilio Service
Handles phone call management, WebRTC connections, and call routing
"""
import logging
from typing import Dict, Optional, List
from datetime import datetime
import uuid
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather, Stream
from twilio.base.exceptions import TwilioRestException

from api.config import settings
from api.utils.logger import setup_logger

logger = setup_logger(__name__)


class TwilioService:
    """Service for Twilio telephony integration"""
    
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.phone_number = settings.TWILIO_PHONE_NUMBER
        self.webhook_base_url = settings.WEBHOOK_BASE_URL
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            logger.warning("Twilio credentials not configured")
            self.client = None
    
    def make_outbound_call(
        self,
        to_number: str,
        agent_id: str,
        organization_id: str,
        callback_url: Optional[str] = None
    ) -> Dict:
        """
        Initiate an outbound call
        
        Args:
            to_number: Phone number to call
            agent_id: Agent handling the call
            organization_id: Organization making the call
            callback_url: Optional webhook URL for call events
            
        Returns:
            Call details including SID
        """
        if not self.client:
            raise ValueError("Twilio client not configured")
        
        try:
            # Generate unique call ID
            call_id = str(uuid.uuid4())
            
            # Build TwiML URL with parameters
            twiml_url = f"{self.webhook_base_url}/api/v1/webhooks/twilio/voice"
            twiml_url += f"?agent_id={agent_id}&organization_id={organization_id}&call_id={call_id}"
            
            # Status callback URL
            status_callback = callback_url or f"{self.webhook_base_url}/api/v1/webhooks/twilio/status"
            
            # Make the call
            call = self.client.calls.create(
                to=to_number,
                from_=self.phone_number,
                url=twiml_url,
                status_callback=status_callback,
                status_callback_event=["initiated", "ringing", "answered", "completed"],
                status_callback_method="POST",
                record=settings.RECORD_CALLS or False,
                machine_detection="Enable" if settings.ENABLE_MACHINE_DETECTION else "Disable"
            )
            
            logger.info(f"Initiated outbound call {call.sid} to {to_number}")
            
            return {
                "call_sid": call.sid,
                "call_id": call_id,
                "to": to_number,
                "from": self.phone_number,
                "status": call.status,
                "direction": "outbound-api",
                "created_at": datetime.utcnow().isoformat()
            }
            
        except TwilioRestException as e:
            logger.error(f"Twilio error making call: {e}")
            raise ValueError(f"Failed to make call: {e.msg}")
    
    def handle_incoming_call(
        self,
        from_number: str,
        to_number: str,
        call_sid: str,
        agent_id: Optional[str] = None
    ) -> VoiceResponse:
        """
        Handle incoming call and return TwiML response
        
        Args:
            from_number: Caller's phone number
            to_number: Called number
            call_sid: Twilio call SID
            agent_id: Optional specific agent to handle call
            
        Returns:
            TwiML VoiceResponse
        """
        response = VoiceResponse()
        
        # Get agent configuration or use default
        if not agent_id:
            agent_id = settings.DEFAULT_AGENT_ID
        
        # Initial greeting (can be customized per agent)
        response.say(
            "Hello, you've reached our AI assistant. How can I help you today?",
            voice="alice",
            language="en-US"
        )
        
        # Start media stream for real-time audio processing
        stream_url = f"wss://{settings.WEBHOOK_BASE_URL.replace('https://', '').replace('http://', '')}/api/v1/websocket/media-stream"
        
        stream = Stream(
            url=stream_url,
            track="both_tracks"  # Stream both inbound and outbound audio
        )
        
        # Add custom parameters to stream
        stream.parameter(name="call_sid", value=call_sid)
        stream.parameter(name="agent_id", value=agent_id)
        stream.parameter(name="from_number", value=from_number)
        
        response.append(stream)
        
        # Start gathering speech input
        gather = Gather(
            input="speech",
            action=f"{self.webhook_base_url}/api/v1/webhooks/twilio/gather",
            method="POST",
            speechTimeout="auto",
            language="en-US",
            enhanced=True,  # Use enhanced speech recognition
            speechModel="phone_call"  # Optimized for phone calls
        )
        
        response.append(gather)
        
        return response
    
    def handle_gather_result(
        self,
        speech_result: str,
        call_sid: str,
        confidence: float
    ) -> VoiceResponse:
        """
        Handle speech recognition result from Gather
        
        Args:
            speech_result: Transcribed speech
            call_sid: Call SID
            confidence: Recognition confidence score
            
        Returns:
            TwiML response with next action
        """
        response = VoiceResponse()
        
        # Log the speech result
        logger.info(f"Speech result for {call_sid}: '{speech_result}' (confidence: {confidence})")
        
        # Process the speech through conversation service
        # This would be handled by the webhook endpoint
        # Here we just continue gathering
        
        gather = Gather(
            input="speech",
            action=f"{self.webhook_base_url}/api/v1/webhooks/twilio/gather",
            method="POST",
            speechTimeout="auto",
            enhanced=True
        )
        
        response.append(gather)
        
        return response
    
    def end_call(self, call_sid: str, reason: Optional[str] = None) -> bool:
        """
        End an active call
        
        Args:
            call_sid: Twilio call SID
            reason: Optional reason for ending call
            
        Returns:
            Success status
        """
        if not self.client:
            return False
        
        try:
            call = self.client.calls(call_sid)
            call.update(status="completed")
            logger.info(f"Ended call {call_sid}" + (f" - Reason: {reason}" if reason else ""))
            return True
        except TwilioRestException as e:
            logger.error(f"Error ending call {call_sid}: {e}")
            return False
    
    def get_call_status(self, call_sid: str) -> Optional[Dict]:
        """
        Get current status of a call
        
        Args:
            call_sid: Twilio call SID
            
        Returns:
            Call status information
        """
        if not self.client:
            return None
        
        try:
            call = self.client.calls(call_sid).fetch()
            return {
                "sid": call.sid,
                "status": call.status,
                "direction": call.direction,
                "duration": call.duration,
                "from": call.from_,
                "to": call.to,
                "start_time": call.start_time,
                "end_time": call.end_time,
                "price": call.price,
                "price_unit": call.price_unit
            }
        except TwilioRestException as e:
            logger.error(f"Error fetching call status: {e}")
            return None
    
    def get_recording_url(self, call_sid: str) -> Optional[str]:
        """
        Get recording URL for a call
        
        Args:
            call_sid: Twilio call SID
            
        Returns:
            Recording URL if available
        """
        if not self.client:
            return None
        
        try:
            recordings = self.client.recordings.list(call_sid=call_sid, limit=1)
            if recordings:
                recording = recordings[0]
                return f"https://api.twilio.com{recording.uri.replace('.json', '.mp3')}"
            return None
        except TwilioRestException as e:
            logger.error(f"Error fetching recording: {e}")
            return None
    
    def send_sms(
        self,
        to_number: str,
        message: str,
        media_url: Optional[str] = None
    ) -> Optional[str]:
        """
        Send SMS message
        
        Args:
            to_number: Recipient phone number
            message: Message text
            media_url: Optional media attachment URL
            
        Returns:
            Message SID if successful
        """
        if not self.client:
            return None
        
        try:
            params = {
                "to": to_number,
                "from_": self.phone_number,
                "body": message
            }
            
            if media_url:
                params["media_url"] = [media_url]
            
            message = self.client.messages.create(**params)
            logger.info(f"Sent SMS {message.sid} to {to_number}")
            return message.sid
            
        except TwilioRestException as e:
            logger.error(f"Error sending SMS: {e}")
            return None
    
    def validate_phone_number(self, phone_number: str) -> Dict:
        """
        Validate and get information about a phone number
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            Validation results and phone number info
        """
        if not self.client:
            return {"valid": False, "error": "Twilio client not configured"}
        
        try:
            lookup = self.client.lookups.v1.phone_numbers(phone_number).fetch(
                type=["carrier", "caller-name"]
            )
            
            return {
                "valid": True,
                "phone_number": lookup.phone_number,
                "national_format": lookup.national_format,
                "country_code": lookup.country_code,
                "carrier": lookup.carrier,
                "caller_name": lookup.caller_name
            }
            
        except TwilioRestException as e:
            logger.error(f"Phone validation error: {e}")
            return {"valid": False, "error": str(e)}
    
    def get_available_phone_numbers(
        self,
        country: str = "US",
        area_code: Optional[str] = None,
        contains: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for available phone numbers to purchase
        
        Args:
            country: Country code (e.g., "US", "GB")
            area_code: Optional area code filter
            contains: Optional pattern to search for
            
        Returns:
            List of available phone numbers
        """
        if not self.client:
            return []
        
        try:
            params = {}
            if area_code:
                params["area_code"] = area_code
            if contains:
                params["contains"] = contains
            
            numbers = self.client.available_phone_numbers(country).local.list(
                **params,
                limit=10
            )
            
            return [
                {
                    "phone_number": num.phone_number,
                    "friendly_name": num.friendly_name,
                    "locality": num.locality,
                    "region": num.region,
                    "postal_code": num.postal_code,
                    "capabilities": num.capabilities
                }
                for num in numbers
            ]
            
        except TwilioRestException as e:
            logger.error(f"Error searching phone numbers: {e}")
            return []


# Singleton instance
twilio_service = TwilioService()