import asyncio
import time
from loguru import logger
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import RetryAfter, TimedOut, NetworkError
from app.config import settings

class TelegramService:
    """Thread-safe core handling message distribution, rate-limiting rules, and retry policies."""

    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.channel_id = settings.TELEGRAM_CHANNEL_ID
        
        if not self.bot_token or not self.channel_id:
            logger.error("Telegram credentials initialization incomplete inside environment configurations.")
        
        # Instantiate raw programmatic bot reference loop securely
        self._bot = Bot(token=self.bot_token)
        # Structural execution anchor targeting max throughput rate limits (Telegram rules state max ~30 msgs/sec total)
        self.last_send_time = 0.0
        self.rate_limit_delay = 1.2  # Dynamic safety spacing window delay buffer

    def _apply_rate_limiting(self):
        """Monitors transit windows locally to protect against downstream rate penalties."""
        elapsed = time.time() - self.last_send_time
        if elapsed < self.rate_limit_delay:
            sleep_needed = self.rate_limit_delay - elapsed
            logger.debug(f"Internal rate limiting: Throttling execution queue pipeline for {sleep_needed:.2f}s")
            time.sleep(sleep_needed)
        self.last_send_time = time.time()

    async def _async_send(self, html_text: str) -> tuple[bool, str | None, str | None]:
        """Runs the underlying async API transmission routines."""
        self._apply_rate_limiting()
        retries = 3
        backoff = 2.0

        for attempt in range(1, retries + 1):
            try:
                message = await self._bot.send_message(
                    chat_id=self.channel_id,
                    text=html_text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=False
                )
                logger.success(f"Payload successfully dispatched to Telegram channel channel. Msg ID: {message.message_id}")
                return True, str(message.message_id), None

            except RetryAfter as e:
                logger.warning(f"Telegram flood control hit. Backing off for {e.retry_after} seconds. Attempt {attempt}/{retries}")
                await asyncio.sleep(e.retry_after)
            except (TimedOut, NetworkError) as e:
                logger.error(f"Network degradation pattern caught during transit execution layer: {e}. Retry backoff: {backoff}s")
                if attempt == retries:
                    return False, None, str(e)
                await asyncio.sleep(backoff)
                backoff *= 2
            except Exception as e:
                logger.critical(f"Unrecoverable structural exception identified at communication pipeline: {e}")
                return False, None, str(e)
        
        return False, None, "Max delivery retry loops exhausted."

    def send_channel_message(self, html_text: str) -> tuple[bool, str | None, str | None]:
        """
        Thread-safe entry-point wrapper to transmit formatted HTML to channels.
        Returns: Tuple(is_success, telegram_message_id, error_message)
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Executing cleanly within an active asynchronous run execution lifecycle pool
            future = asyncio.run_coroutine_threadsafe(self._async_send(html_text), loop)
            return future.result()
        else:
            # Standard sequential blocking integration wrapper runtime tracking
            return asyncio.run(self._async_send(html_text))