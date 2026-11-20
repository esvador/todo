from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

from app.config import settings

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def alembic_cfg(tmp_path, monkeypatch) -> Config:
    monkeypatch.setattr(settings, "database_url", f"sqlite:///{tmp_path / 'migrations.db'}")
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "alembic"))
    cfg.attributes["configure_logger"] = False
    return cfg


def test_migrations_match_models(alembic_cfg):
    """Падает, если модели изменили, а миграцию не создали."""
    command.upgrade(alembic_cfg, "head")
    command.check(alembic_cfg)


def test_migrations_downgrade_and_upgrade(alembic_cfg):
    command.upgrade(alembic_cfg, "head")
    command.downgrade(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "head")
