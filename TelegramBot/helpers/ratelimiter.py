from typing import Union

from pyrate_limiter import BucketFullException, Duration, Limiter, InMemoryBucket, Rate


class RateLimiter:
    """
    通过 pyrate_limiter 实现速率限制逻辑。
    (https://pypi.org/project/pyrate-limiter/)
    """

    def __init__(self) -> None:
        # 2 requests per seconds
        self.second_rate = Rate(2, Duration.SECOND)

        # 17 requests per minute.
        self.minute_rate = Rate(17, Duration.MINUTE)

        # 1000 requests per hour
        self.hourly_rate = Rate(1000, Duration.HOUR)

        # 10000 requests per day
        self.daily_rate = Rate(10000, Duration.DAY)

        self.rates = [
            self.second_rate,
            self.minute_rate,
            self.hourly_rate,
            self.daily_rate,
        ]

        self.limiter = Limiter(InMemoryBucket(self.rates))

    async def acquire(self, userid: Union[int, str]) -> bool:
        """
        获取每个用户 ID 的速率限制，并根据用户 ID 的速率限制状态返回 True / False
        基于用户名的速率限制状态。
        """

        try:
            self.limiter.try_acquire(userid)
            return False
        except BucketFullException:
            return True
