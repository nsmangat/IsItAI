import time

"""
Enforces a minimum interval between requests to the APi providing images
to not get rate limited
"""
class RateLimiter:    

    def __init__(self, min_interval: float, enabled: bool = True):
        self.min_interval = min_interval
        self.enabled = enabled
        self._last_request = 0

    """
    Block until enough time has passed since the last request
    Returns how many seconds we need to wait until the next request 0 if we don't need to wait
    """
    def calculate_wait_time_between_requests(self) -> float:

        if not self.enabled:
            return 0

        current_time = time.time()
        elapsed_time = current_time - self._last_request

        if elapsed_time < self.min_interval:
            wait_time = self.min_interval - elapsed_time
            print(f"Rate limiter: waiting {wait_time:.2f}s before next request")
            time.sleep(wait_time)
        else:
            wait_time = 0

        self._last_request = time.time()

        return wait_time
