"""initial schema"""

from alembic import op
import sqlalchemy as sa


revision = "20260312_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sites",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("city", sa.String(length=255), nullable=False),
        sa.Column("country", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sites_name"), "sites", ["name"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("role", sa.Enum("admin", name="user_role", native_enum=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "machines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("machine_type", sa.String(length=100), nullable=False),
        sa.Column(
            "status",
            sa.Enum("idle", "running", "alert", "maintenance", name="machine_status", native_enum=False),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_machines_code"), "machines", ["code"], unique=True)
    op.create_index(op.f("ix_machines_site_id"), "machines", ["site_id"], unique=False)
    op.create_index(op.f("ix_machines_status"), "machines", ["status"], unique=False)

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("machine_id", sa.Integer(), nullable=False),
        sa.Column(
            "level",
            sa.Enum("warning", "critical", name="alert_level", native_enum=False),
            nullable=False,
        ),
        sa.Column("message", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["machine_id"], ["machines.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_alerts_is_active"), "alerts", ["is_active"], unique=False)
    op.create_index(op.f("ix_alerts_level"), "alerts", ["level"], unique=False)
    op.create_index(op.f("ix_alerts_machine_id"), "alerts", ["machine_id"], unique=False)

    op.create_table(
        "measurements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("machine_id", sa.Integer(), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=False),
        sa.Column("vibration", sa.Float(), nullable=False),
        sa.Column("power", sa.Float(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["machine_id"], ["machines.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_measurements_machine_id"), "measurements", ["machine_id"], unique=False)
    op.create_index(op.f("ix_measurements_recorded_at"), "measurements", ["recorded_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_measurements_recorded_at"), table_name="measurements")
    op.drop_index(op.f("ix_measurements_machine_id"), table_name="measurements")
    op.drop_table("measurements")
    op.drop_index(op.f("ix_alerts_machine_id"), table_name="alerts")
    op.drop_index(op.f("ix_alerts_level"), table_name="alerts")
    op.drop_index(op.f("ix_alerts_is_active"), table_name="alerts")
    op.drop_table("alerts")
    op.drop_index(op.f("ix_machines_status"), table_name="machines")
    op.drop_index(op.f("ix_machines_site_id"), table_name="machines")
    op.drop_index(op.f("ix_machines_code"), table_name="machines")
    op.drop_table("machines")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_sites_name"), table_name="sites")
    op.drop_table("sites")
