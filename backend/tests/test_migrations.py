import os
import tempfile
import pytest
from sqlalchemy import create_engine, inspect
from alembic.config import Config
from alembic import command


def test_alembic_migrations_lifecycle():
    """
    Verifies that Alembic migrations run cleanly from scratch (upgrade head)
    on an isolated database, create expected tables with columns and constraints,
    and can downgrade cleanly.
    """
    # Create an isolated temporary SQLite database file
    with tempfile.NamedTemporaryFile(suffix="_test_migration.db", delete=False) as tmp_file:
        tmp_db_path = tmp_file.name

    try:
        db_url = f"sqlite:///{tmp_db_path}"
        
        # Load Alembic configuration relative to backend directory
        alembic_ini_path = os.path.join(os.path.dirname(__file__), "..", "alembic.ini")
        alembic_cfg = Config(alembic_ini_path)
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)
        
        # 1. Execute full upgrade to head
        command.upgrade(alembic_cfg, "head")
        
        # 2. Inspect created schema
        engine = create_engine(db_url)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        assert "feedbacks" in tables, "feedbacks table was not created by migration"
        assert "users" in tables, "users table was not created by migration"
        assert "alembic_version" in tables, "alembic_version tracking table not found"
        
        # Verify feedbacks columns
        feedback_cols = {col["name"]: col for col in inspector.get_columns("feedbacks")}
        expected_feedback_cols = [
            "id", "source", "customer_identifier", "feedback_text",
            "category", "sentiment", "sentiment_score", "status",
            "created_at", "updated_at",
        ]
        for col_name in expected_feedback_cols:
            assert col_name in feedback_cols, f"Column {col_name} missing from feedbacks table"
            
        # Verify users columns
        user_cols = {col["name"]: col for col in inspector.get_columns("users")}
        expected_user_cols = [
            "id", "name", "email", "hashed_password", "role",
            "is_active", "created_at", "updated_at",
        ]
        for col_name in expected_user_cols:
            assert col_name in user_cols, f"Column {col_name} missing from users table"
            
        engine.dispose()
        
        # 3. Test downgrade to base
        command.downgrade(alembic_cfg, "base")
        engine_after_downgrade = create_engine(db_url)
        inspector_post = inspect(engine_after_downgrade)
        tables_post = inspector_post.get_table_names()
        
        assert "feedbacks" not in tables_post, "feedbacks table remained after downgrade"
        assert "users" not in tables_post, "users table remained after downgrade"
        engine_after_downgrade.dispose()

    finally:
        if os.path.exists(tmp_db_path):
            try:
                os.remove(tmp_db_path)
            except OSError:
                pass
