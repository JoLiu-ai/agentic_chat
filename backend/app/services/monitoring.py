import time
import logging

logger = logging.getLogger(__name__)

class MonitoringService:
    def log_request(self, session_id: str, endpoint: str, duration: float, status: str):
        logger.info(f"Request: session_id={session_id}, endpoint={endpoint}, duration={duration:.4f}s, status={status}")
        # In a real app, this would write to a DB or Prometheus
