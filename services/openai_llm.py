import json
import logging
from typing import Optional
from openai import AsyncOpenAI
from config import config
from services.conversation import ConversationManager

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a friendly and efficient reservation agent for Mario's Italian Kitchen, a popular Italian restaurant.

Your job is to help callers book a table reservation. You need to collect the following information:
1. Date of the reservation
2. Time of the reservation
3. Party size (number of guests)
4. Name for the reservation

Guidelines:
- Keep responses brief and conversational (1-2 sentences max)
- Be warm and friendly but efficient
- Available reservation times: 5:30 PM to 9:30 PM, in 30-minute slots
- We can accommodate parties of 1-8 people
- If a requested time is not available, suggest the closest alternatives (e.g., "I have openings at 6:45 and 7:30")
- Once you have all information, confirm the complete reservation details
- If the caller says something unclear, politely ask them to repeat

Current date context: Assume "today" is the current day, "tomorrow" is the next day, "this Saturday" refers to the upcoming Saturday, etc.

Remember: You're on a phone call, so keep responses natural and speakable. Avoid using special characters, bullet points, or formatting that doesn't work in speech."""


class OpenAILLM:
    """OpenAI GPT-4 service for conversation handling."""

    def __init__(self, model: str = "gpt-4-turbo-preview"):
        """
        Initialize OpenAI LLM.

        Args:
            model: OpenAI model to use
        """
        self.model = model
        self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)

    async def get_response(
        self,
        conversation: ConversationManager,
        user_input: str,
    ) -> str:
        """
        Get a response from the LLM based on conversation context.

        Args:
            conversation: The conversation manager with history
            user_input: The latest user input

        Returns:
            The assistant's response text
        """
        # Add user message to history
        conversation.add_user_message(user_input)

        # Build messages for API call
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add reservation context if we have partial info
        if any([
            conversation.reservation.date,
            conversation.reservation.time,
            conversation.reservation.party_size,
            conversation.reservation.name,
        ]):
            context = self._build_reservation_context(conversation)
            messages.append({"role": "system", "content": context})

        # Add conversation history
        messages.extend(conversation.get_messages_for_llm())

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=150,
                temperature=0.7,
            )

            assistant_message = response.choices[0].message.content or ""

            # Add assistant message to history
            conversation.add_assistant_message(assistant_message)

            # Try to extract reservation details from the conversation
            await self._extract_reservation_details(conversation, user_input)

            logger.info(f"LLM response: {assistant_message}")
            return assistant_message

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return "I'm sorry, I'm having trouble processing that. Could you please repeat what you said?"

    async def get_greeting(self, conversation: ConversationManager) -> str:
        """Generate the initial greeting."""
        greeting = "Hi, thanks for calling Mario's Italian Kitchen! I can help you make a reservation. What date were you thinking?"
        conversation.add_assistant_message(greeting)
        conversation.greeting_sent = True
        return greeting

    def _build_reservation_context(self, conversation: ConversationManager) -> str:
        """Build context string with current reservation state."""
        parts = ["Current reservation details collected:"]
        res = conversation.reservation

        if res.date:
            parts.append(f"- Date: {res.date}")
        if res.time:
            parts.append(f"- Time: {res.time}")
        if res.party_size:
            parts.append(f"- Party size: {res.party_size}")
        if res.name:
            parts.append(f"- Name: {res.name}")

        missing = res.get_missing_fields()
        if missing:
            parts.append(f"Still need to collect: {', '.join(missing)}")

        return "\n".join(parts)

    async def _extract_reservation_details(
        self,
        conversation: ConversationManager,
        user_input: str,
    ) -> None:
        """
        Use LLM to extract reservation details from user input.

        This is a simple extraction - in production you might use
        function calling or a more sophisticated approach.
        """
        extraction_prompt = f"""Extract any reservation details from this customer message.
Return a JSON object with these fields (use null for any not mentioned):
- date: string (e.g., "Saturday", "tomorrow", "January 15th")
- time: string (e.g., "7:30 PM", "around 7", "evening")
- party_size: number (e.g., 4, 2)
- name: string (the person's name)

Customer message: "{user_input}"

Return ONLY the JSON object, no other text."""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use faster model for extraction
                messages=[{"role": "user", "content": extraction_prompt}],
                max_tokens=100,
                temperature=0,
            )

            result = response.choices[0].message.content or "{}"

            # Clean up the response (remove markdown code blocks if present)
            result = result.strip()
            if result.startswith("```"):
                result = result.split("\n", 1)[1]
            if result.endswith("```"):
                result = result.rsplit("\n", 1)[0]
            result = result.strip()

            data = json.loads(result)

            # Update reservation with extracted details
            if data.get("date"):
                conversation.update_reservation(date=data["date"])
            if data.get("time"):
                conversation.update_reservation(time=data["time"])
            if data.get("party_size"):
                conversation.update_reservation(party_size=int(data["party_size"]))
            if data.get("name"):
                conversation.update_reservation(name=data["name"])

            logger.debug(f"Extracted reservation details: {data}")

        except (json.JSONDecodeError, Exception) as e:
            # Extraction failed, but that's okay - main conversation continues
            logger.debug(f"Could not extract reservation details: {e}")
