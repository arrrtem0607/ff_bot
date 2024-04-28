from src.database.entities.settings import Settings


class SettingsController:
    settings = Settings()

    def get_database_url(self):
        tmp_settings: Settings = self.settings
        return (f"postgresql+asyncpg://{tmp_settings.DB_USER}:{tmp_settings.DB_PASS}"
                f"@{tmp_settings.DB_HOST}:{tmp_settings.DB_PORT}/{tmp_settings.DB_NAME}")