from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings

_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _ROOT / ".env"


class Settings(BaseSettings):
    sqlite_path: str = "./learner_portfolio.db"
    db_reset_on_startup: bool = False
    falkordb_host: str = "localhost"
    falkordb_port: int = 56379
    falkordb_graph: str = "knowledge_graph"
    openai_api_key: str = ""
    entra_tenant_id: str = ""
    entra_client_id: str = ""

    model_config = {"env_file": _ENV_FILE}


settings = Settings()
