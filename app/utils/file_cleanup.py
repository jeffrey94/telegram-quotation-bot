"""
Utility for managing temporary file cleanup after a specified duration.
"""

import os
import logging
import asyncio
import time
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class FileCleanupManager:
    """Manages the cleanup of temporary files after a specified time period."""
    
    def __init__(self, cleanup_time_seconds: int = 600):  # Default: 10 minutes
        """Initialize the cleanup manager.
        
        Args:
            cleanup_time_seconds: Time in seconds after which files will be deleted
        """
        self.cleanup_time_seconds = cleanup_time_seconds
        self.files_to_cleanup: Dict[str, float] = {}  # filepath -> timestamp
        self.cleanup_task: Optional[asyncio.Task] = None
        self.running = False
        logger.info(f"FileCleanupManager initialized with {cleanup_time_seconds} seconds cleanup time")
    
    def add_file(self, filepath: str) -> None:
        """Add a file to be cleaned up later.
        
        Args:
            filepath: Path to the file that needs cleanup
        """
        if not os.path.exists(filepath):
            logger.warning(f"Cannot schedule cleanup for non-existent file: {filepath}")
            return
            
        self.files_to_cleanup[filepath] = time.time()
        logger.info(f"Scheduled cleanup for file: {filepath} in {self.cleanup_time_seconds} seconds")
        
        # Ensure the cleanup task is running
        if not self.running:
            self.start_cleanup_task()
    
    def start_cleanup_task(self) -> None:
        """Start the background task for file cleanup."""
        if self.cleanup_task is None or self.cleanup_task.done():
            self.running = True
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("Started file cleanup background task")
    
    def stop_cleanup_task(self) -> None:
        """Stop the cleanup task."""
        if self.cleanup_task and not self.cleanup_task.done():
            self.running = False
            self.cleanup_task.cancel()
            logger.info("Stopped file cleanup background task")
    
    async def _cleanup_loop(self) -> None:
        """Background loop that checks for and removes expired files."""
        try:
            while self.running:
                current_time = time.time()
                files_to_remove = []
                
                # Identify files that need to be cleaned up
                for filepath, timestamp in self.files_to_cleanup.items():
                    if current_time - timestamp >= self.cleanup_time_seconds:
                        files_to_remove.append(filepath)
                
                # Remove the expired files
                for filepath in files_to_remove:
                    try:
                        # Remove from tracking dict
                        self.files_to_cleanup.pop(filepath, None)
                        
                        # Delete the file if it exists
                        if os.path.exists(filepath):
                            os.remove(filepath)
                            logger.info(f"Cleaned up temporary file: {filepath}")
                        else:
                            logger.warning(f"File already gone during cleanup: {filepath}")
                    except Exception as e:
                        logger.error(f"Error cleaning up file {filepath}: {str(e)}")
                
                # If no more files to clean up, stop the task
                if not self.files_to_cleanup:
                    logger.info("No more files to clean up, stopping cleanup task")
                    self.running = False
                    break
                
                # Sleep for a while before checking again (every 30 seconds)
                await asyncio.sleep(30)
                
        except asyncio.CancelledError:
            logger.info("File cleanup task was cancelled")
        except Exception as e:
            logger.error(f"Error in file cleanup task: {str(e)}")
            self.running = False

# Create a singleton instance for use throughout the application
cleanup_manager = FileCleanupManager()

def schedule_file_cleanup(filepath: str, cleanup_time_seconds: Optional[int] = None) -> None:
    """Schedule a file for cleanup after the specified time.
    
    Args:
        filepath: Path to the file to clean up
        cleanup_time_seconds: Custom cleanup time in seconds (uses default if None)
    """
    # If a custom time is specified, create a new manager instance
    if cleanup_time_seconds is not None and cleanup_time_seconds != cleanup_manager.cleanup_time_seconds:
        temp_manager = FileCleanupManager(cleanup_time_seconds)
        temp_manager.add_file(filepath)
        temp_manager.start_cleanup_task()
    else:
        cleanup_manager.add_file(filepath) 