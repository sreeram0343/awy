"""Initial schema setup for AWY (vehicles, variants, specs, price_history, reviews, leads)

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-09-27 15:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create vehicles table
    op.create_table(
        'vehicles',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('make', sa.String(length=100), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=10), nullable=False),
        sa.Column('body_type', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('make', 'model', name='uq_vehicle_make_model')
    )
    op.create_index(op.f('ix_vehicles_make'), 'vehicles', ['make'], unique=False)
    op.create_index(op.f('ix_vehicles_model'), 'vehicles', ['model'], unique=False)
    op.create_index(op.f('ix_vehicles_category'), 'vehicles', ['category'], unique=False)
    op.create_index(op.f('ix_vehicles_body_type'), 'vehicles', ['body_type'], unique=False)

    # 2. Create variants table
    op.create_table(
        'variants',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('vehicle_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('fuel_type', sa.String(length=20), nullable=False),
        sa.Column('transmission', sa.String(length=20), nullable=False),
        sa.Column('engine_capacity_cc', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('motor_power_kw', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('battery_capacity_kwh', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vehicle_id', 'name', name='uq_variant_vehicle_name')
    )
    op.create_index(op.f('ix_variants_vehicle_id'), 'variants', ['vehicle_id'], unique=False)
    op.create_index(op.f('ix_variants_name'), 'variants', ['name'], unique=False)
    op.create_index(op.f('ix_variants_fuel_type'), 'variants', ['fuel_type'], unique=False)
    op.create_index(op.f('ix_variants_transmission'), 'variants', ['transmission'], unique=False)

    # 3. Create specs table
    op.create_table(
        'specs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('variant_id', sa.UUID(), nullable=False),
        sa.Column('seating_capacity', sa.Integer(), nullable=True),
        sa.Column('mileage_kpl', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('ev_range_km', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('ncap_rating', sa.Integer(), nullable=True),
        sa.Column('airbags_count', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('abs_type', sa.String(length=50), nullable=True),
        sa.Column('ground_clearance_mm', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('length_mm', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('width_mm', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('height_mm', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('wheelbase_mm', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('boot_space_litres', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('extra_features', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['variant_id'], ['variants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('variant_id')
    )
    op.create_index(op.f('ix_specs_variant_id'), 'specs', ['variant_id'], unique=True)
    op.create_index(op.f('ix_specs_abs_type'), 'specs', ['abs_type'], unique=False)

    # 4. Create price_history table
    op.create_table(
        'price_history',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('variant_id', sa.UUID(), nullable=False),
        sa.Column('state_code', sa.String(length=5), nullable=False),
        sa.Column('ex_showroom_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('effective_date', sa.Date(), nullable=False),
        sa.Column('source_version', sa.String(length=50), nullable=False, server_default='v1.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['variant_id'], ['variants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_price_history_variant_id'), 'price_history', ['variant_id'], unique=False)
    op.create_index(op.f('ix_price_history_state_code'), 'price_history', ['state_code'], unique=False)
    op.create_index(op.f('ix_price_history_effective_date'), 'price_history', ['effective_date'], unique=False)
    op.create_index('idx_price_history_variant_state_date', 'price_history', ['variant_id', 'state_code', 'effective_date'], unique=False)

    # 5. Create reviews table
    op.create_table(
        'reviews',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('vehicle_id', sa.UUID(), nullable=False),
        sa.Column('variant_id', sa.UUID(), nullable=True),
        sa.Column('topic', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('rating', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('chunk_hash', sa.String(length=64), nullable=False),
        sa.Column('vector_id', sa.String(length=100), nullable=True),
        sa.Column('source_version', sa.String(length=50), nullable=False, server_default='v1.0'),
        sa.Column('ingested_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['variant_id'], ['variants.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chunk_hash')
    )
    op.create_index(op.f('ix_reviews_vehicle_id'), 'reviews', ['vehicle_id'], unique=False)
    op.create_index(op.f('ix_reviews_variant_id'), 'reviews', ['variant_id'], unique=False)
    op.create_index(op.f('ix_reviews_topic'), 'reviews', ['topic'], unique=False)
    op.create_index(op.f('ix_reviews_chunk_hash'), 'reviews', ['chunk_hash'], unique=True)
    op.create_index('idx_review_vehicle_topic', 'reviews', ['vehicle_id', 'topic'], unique=False)

    # 6. Create leads table
    op.create_table(
        'leads',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('variant_id', sa.UUID(), nullable=False),
        sa.Column('user_name', sa.String(length=100), nullable=False),
        sa.Column('user_email', sa.String(length=100), nullable=False),
        sa.Column('user_phone', sa.String(length=20), nullable=False),
        sa.Column('state_code', sa.String(length=5), nullable=False),
        sa.Column('dealership_id', sa.String(length=50), nullable=False),
        sa.Column('computed_on_road_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='created'),
        sa.Column('consent_given', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('consent_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['variant_id'], ['variants.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leads_variant_id'), 'leads', ['variant_id'], unique=False)
    op.create_index(op.f('ix_leads_status'), 'leads', ['status'], unique=False)
    op.create_index('idx_leads_status_created', 'leads', ['status', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_table('leads')
    op.drop_table('reviews')
    op.drop_table('price_history')
    op.drop_table('specs')
    op.drop_table('variants')
    op.drop_table('vehicles')
