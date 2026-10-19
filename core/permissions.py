"""Human-in-the-Loop (HITL) Permission Manager for Helper-AI.

Allows the agent to pause execution and request 1-click user authorization
for sensitive operations (e.g., social posting, system modifications, 
or handling verification challenges) before proceeding.
"""

import os
import asyncio
import time
import uuid
import logging
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger("HelperPermissions")


class PermissionRequest:
    """Represents a single pending authorization request."""

    def __init__(
        self,
        request_id: str,
        action: str,
        description: str,
        details: Dict[str, Any],
        timeout_seconds: float = 120.0
    ):
        self.request_id = request_id
        self.action = action
        self.description = description
        self.details = details
        self.timeout_seconds = timeout_seconds
        self.created_at = time.time()
        self.future: asyncio.Future[bool] = asyncio.get_event_loop().create_future()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "action": self.action,
            "description": self.description,
            "details": self.details,
            "timeout_seconds": self.timeout_seconds,
            "elapsed_seconds": round(time.time() - self.created_at, 1),
            "created_at": self.created_at
        }


class PermissionManager:
    """Manages pending approval requests between HelperAgent and the User Interface."""

    def __init__(self, unrestricted: Optional[bool] = None):
        if unrestricted is None:
            self.unrestricted_mode = os.getenv("HELPER_UNRESTRICTED_ACCESS", "true").lower() in ("true", "1", "yes")
        else:
            self.unrestricted_mode = unrestricted
        self._pending_requests: Dict[str, PermissionRequest] = {}
        self._listener: Optional[Callable[[Dict[str, Any]], None]] = None

    def set_unrestricted_mode(self, enabled: bool):
        """Enables or disables full unrestricted autonomous execution mode."""
        self.unrestricted_mode = enabled
        logger.info(f"PermissionManager unrestricted_mode set to {enabled}")

    def is_unrestricted(self) -> bool:
        return self.unrestricted_mode

    def set_listener(self, listener: Optional[Callable[[Dict[str, Any]], None]]):
        self._listener = listener

    def get_pending(self) -> Optional[Dict[str, Any]]:
        """Returns the most recent pending permission request if any."""
        if not self._pending_requests:
            return None
        # Return latest request
        latest_req = list(self._pending_requests.values())[-1]
        return latest_req.to_dict()

    async def request_permission(
        self,
        action: str,
        description: str,
        details: Optional[Dict[str, Any]] = None,
        timeout_seconds: float = 120.0
    ) -> bool:
        """
        Pauses and waits for user authorization.
        Returns True if approved, False if rejected or timed out.
        """
        request_id = str(uuid.uuid4())[:8]
        req = PermissionRequest(
            request_id=request_id,
            action=action,
            description=description,
            details=details or {},
            timeout_seconds=timeout_seconds
        )
        self._pending_requests[request_id] = req

        logger.info(f"Permission requested [ID: {request_id}] for action '{action}': {description}")

        # Check for Unrestricted Full Access Mode
        if self.unrestricted_mode:
            logger.info(f"⚡ [UNRESTRICTED ACCESS ACTIVE] Auto-approving '{action}' ({description}) without pause.")
            if self._listener:
                try:
                    payload = req.to_dict()
                    payload["auto_approved"] = True
                    payload["status"] = "auto_approved"
                    res = self._listener(payload)
                    if asyncio.iscoroutine(res):
                        asyncio.create_task(res)
                except Exception as e:
                    logger.debug(f"Listener notification error: {e}")
            self._pending_requests.pop(request_id, None)
            return True

        if self._listener:
            try:
                res = self._listener(req.to_dict())
                if asyncio.iscoroutine(res):
                    asyncio.create_task(res)
            except Exception as e:
                logger.warning(f"Error notifying permission listener: {e}")

        try:
            approved = await asyncio.wait_for(req.future, timeout=timeout_seconds)
            logger.info(f"Permission [ID: {request_id}] decided: approved={approved}")
            return approved
        except asyncio.TimeoutError:
            logger.warning(f"Permission [ID: {request_id}] timed out after {timeout_seconds}s. Auto-denying.")
            return False
        finally:
            self._pending_requests.pop(request_id, None)

    def respond(self, request_id: str, approved: bool) -> bool:
        """
        Resolves a pending permission request.
        Returns True if request was found and resolved, False otherwise.
        """
        req = self._pending_requests.get(request_id)
        if not req:
            logger.warning(f"Permission request '{request_id}' not found or already resolved.")
            return False

        if not req.future.done():
            req.future.set_result(approved)
            return True
        return False

    def cancel_all(self):
        """Cancels all pending permission requests (e.g. when agent is cancelled)."""
        for req in list(self._pending_requests.values()):
            if not req.future.done():
                req.future.set_result(False)
        self._pending_requests.clear()
