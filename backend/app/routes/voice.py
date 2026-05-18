"""
Voice route placeholder — actual processing is in /voice-command (ai.py).
This module can be extended for audio file upload + STT in the future.
"""
from fastapi import APIRouter

router = APIRouter(tags=["Voice"])

# /voice-command is registered in ai.py router.
# This file is reserved for future audio upload / STT endpoints.
