"""
Conversation Session Manager for Persistent AI Data Analyst.
Tracks session metadata, extracts multi-turn conversational context,
and interfaces with the LangGraph SQLite checkpointer.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ConversationTurn(BaseModel):
    """
    Single turn in a multi-turn conversation.
    """
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text or question")
    sql: Optional[str] = Field(None, description="Generated SQL if assistant turn")
    data_summary: Optional[str] = Field(None, description="Brief summary of result")
    timestamp: Optional[str] = None


class ConversationSession(BaseModel):
    """
    Complete conversational session state.
    """
    conversation_id: str
    turns: List[ConversationTurn] = Field(default_factory=list)

    def add_user_turn(self, query: str):
        self.turns.append(ConversationTurn(role="user", content=query))

    def add_assistant_turn(
        self,
        answer: str,
        sql: Optional[str] = None,
        data_summary: Optional[str] = None
    ):
        self.turns.append(
            ConversationTurn(
                role="assistant",
                content=answer,
                sql=sql,
                data_summary=data_summary
            )
        )

    def get_context_summary(self, max_turns: int = 4) -> str:
        """
        Format recent conversation history as concise string context.
        """
        if not self.turns:
            return ""

        recent = self.turns[-max_turns:]
        lines = []
        for t in recent:
            if t.role == "user":
                lines.append(f"User: \"{t.content}\"")
            else:
                sql_info = f" (SQL: `{t.sql}`)" if t.sql else ""
                lines.append(f"Assistant: \"{t.content}\"{sql_info}")

        return "\n".join(lines)
