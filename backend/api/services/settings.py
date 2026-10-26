from api.config import config
from api.db import AsyncSession
from api.models.domain import AppSetting

SIGNUP_ENABLED_KEY = "signup_enabled"


class SettingsService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_signup_enabled(self) -> bool:
        """Admin override if set, else the SIGNUP_ENABLED config default"""
        setting = await self.session.get(AppSetting, SIGNUP_ENABLED_KEY)
        if setting is None:
            return config.SIGNUP_ENABLED
        return setting.value == "true"

    async def set_signup_enabled(self, enabled: bool) -> bool:
        setting = await self.session.get(AppSetting, SIGNUP_ENABLED_KEY)
        if setting is None:
            setting = AppSetting(key=SIGNUP_ENABLED_KEY, value="")
        setting.value = "true" if enabled else "false"
        self.session.add(setting)
        await self.session.commit()
        return enabled
