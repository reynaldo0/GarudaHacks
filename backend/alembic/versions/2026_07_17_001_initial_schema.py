"""initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-07-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'occupancy_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('train_id', sa.String(50), nullable=False),
        sa.Column('car_id', sa.Integer(), nullable=False),
        sa.Column('station_id', sa.String(50), nullable=False),
        sa.Column('occupancy_ratio', sa.Float(), server_default='0.0'),
        sa.Column('free_space_ratio', sa.Float(), server_default='1.0'),
        sa.Column('spatial_occupancy_score', sa.Float(), server_default='0.0'),
        sa.Column('density_indicator', sa.String(20), server_default='GREEN'),
        sa.Column('floor_area_m2', sa.Float(), server_default='42.0'),
        sa.Column('camera_id', sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'prediction_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('train_id', sa.String(50), nullable=False),
        sa.Column('car_id', sa.Integer(), nullable=False),
        sa.Column('predicted_occupancy_ratio', sa.Float(), server_default='0.0'),
        sa.Column('risk_score', sa.Float(), server_default='0.0'),
        sa.Column('confidence', sa.Float(), server_default='0.0'),
        sa.Column('prediction_horizon_minutes', sa.Integer(), server_default='15'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'warning_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('train_id', sa.String(50), nullable=False),
        sa.Column('car_id', sa.Integer(), nullable=False),
        sa.Column('warning_type', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'decision_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('train_id', sa.String(50), nullable=False),
        sa.Column('from_car_id', sa.Integer(), nullable=False),
        sa.Column('to_car_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('door_action', sa.String(50), nullable=True),
        sa.Column('announcement', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), server_default='0.0'),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'camera_configuration',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('camera_id', sa.String(100), nullable=False),
        sa.Column('camera_type', sa.String(50), nullable=False),
        sa.Column('zone', sa.String(50), nullable=False),
        sa.Column('car_mapping', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('url', sa.String(500), nullable=True),
        sa.Column('fps', sa.Integer(), server_default='1'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('camera_id'),
    )

    op.create_table(
        'train_configuration',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('train_id', sa.String(50), nullable=False),
        sa.Column('formation', sa.String(20), nullable=False),
        sa.Column('total_cars', sa.Integer(), nullable=False),
        sa.Column('capacity_per_car', sa.Integer(), server_default='200'),
        sa.Column('floor_area_m2', sa.Float(), server_default='42.0'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('train_id'),
    )

    op.create_table(
        'bogie_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('train_id', sa.String(50), nullable=False),
        sa.Column('car_id', sa.Integer(), nullable=False),
        sa.Column('cales_score', sa.Float(), server_default='0.0'),
        sa.Column('health_index', sa.Float(), server_default='100.0'),
        sa.Column('damage_multiplier', sa.Float(), server_default='1.0'),
        sa.Column('inspection_priority', sa.Integer(), server_default='0'),
        sa.Column('recommended_action', sa.String(100), server_default='CONTINUE_MONITORING'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'system_log',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('level', sa.String(20), nullable=False),
        sa.Column('module', sa.String(50), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('system_log')
    op.drop_table('bogie_history')
    op.drop_table('train_configuration')
    op.drop_table('camera_configuration')
    op.drop_table('decision_history')
    op.drop_table('warning_history')
    op.drop_table('prediction_history')
    op.drop_table('occupancy_history')
