"""
Factory that picks the correct back-end.
"""
import platform
import logging
from .emulator import EmulatedMatrixDisplay
from .real_matrix import RealMatrixDisplay
from ..config import DISPLAY_BACKEND

logger = logging.getLogger(__name__)

def get_display():
    # Force by env?
    if DISPLAY_BACKEND == "real":
        logger.info("Display backend forced to REAL")
        return RealMatrixDisplay()
    if DISPLAY_BACKEND == "emu":
        logger.info("Display backend forced to EMULATOR")
        return EmulatedMatrixDisplay()

    # auto-detect
    if platform.system() == "Linux" and platform.machine().startswith("arm"):
        logger.info("Auto-detected Raspberry Pi – using real matrix")
        return RealMatrixDisplay()
    logger.info("Using emulator (non-Pi platform)")
    return EmulatedMatrixDisplay()