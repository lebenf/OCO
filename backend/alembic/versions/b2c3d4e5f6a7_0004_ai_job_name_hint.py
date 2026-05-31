# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
"""0004 ai job name hint

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-31

"""
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('ai_analysis_jobs', sa.Column('name_hint', sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column('ai_analysis_jobs', 'name_hint')
