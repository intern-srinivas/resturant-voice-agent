from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class ReservationState:
    """Tracks the state of a reservation during the conversation."""

    date: Optional[str] = None
    time: Optional[str] = None
    party_size: Optional[int] = None
    name: Optional[str] = None
    confirmed: bool = False

    def is_complete(self) -> bool:
        """Check if all required fields are collected."""
        return all([self.date, self.time, self.party_size, self.name])

    def get_missing_fields(self) -> list[str]:
        """Return list of fields still needed."""
        missing = []
        if not self.date:
            missing.append("date")
        if not self.time:
            missing.append("time")
        if not self.party_size:
            missing.append("party size")
        if not self.name:
            missing.append("name")
        return missing

    def to_summary(self) -> str:
        """Generate a summary of the reservation."""
        return (
            f"Reservation for {self.name}: "
            f"Party of {self.party_size} on {self.date} at {self.time}"
        )


@dataclass
class ConversationManager:
    """Manages conversation state and history for a call session."""

    call_id: str
    reservation: ReservationState = field(default_factory=ReservationState)
    messages: list[dict] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    greeting_sent: bool = False

    def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation history."""
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the conversation history."""
        self.messages.append({"role": "assistant", "content": content})

    def get_messages_for_llm(self) -> list[dict]:
        """Get messages formatted for the LLM."""
        return self.messages.copy()

    def update_reservation(
        self,
        date: Optional[str] = None,
        time: Optional[str] = None,
        party_size: Optional[int] = None,
        name: Optional[str] = None,
    ) -> None:
        """Update reservation details."""
        if date:
            self.reservation.date = date
        if time:
            self.reservation.time = time
        if party_size:
            self.reservation.party_size = party_size
        if name:
            self.reservation.name = name

    def confirm_reservation(self) -> None:
        """Mark the reservation as confirmed."""
        self.reservation.confirmed = True


# Store active conversations by call ID
active_conversations: dict[str, ConversationManager] = {}


def get_or_create_conversation(call_id: str) -> ConversationManager:
    """Get existing conversation or create a new one."""
    if call_id not in active_conversations:
        active_conversations[call_id] = ConversationManager(call_id=call_id)
    return active_conversations[call_id]


def end_conversation(call_id: str) -> Optional[ConversationManager]:
    """Remove and return a conversation when the call ends."""
    return active_conversations.pop(call_id, None)
