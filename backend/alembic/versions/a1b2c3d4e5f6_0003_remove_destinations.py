"""0003_remove_destinations

Revision ID: a1b2c3d4e5f6
Revises: 5a93ad6a8f7c
Create Date: 2026-05-09 10:00:00.000000

Rimuove l'entità Destination. Le destinazioni diventano Location di altre House.
- houses: aggiunge is_disposal
- containers: location_id → current_location_id, aggiunge destination_location_id, rimuove destination_id
- transfers: destination_id → destination_location_id (FK su locations)
- drop tabella destinations
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '5a93ad6a8f7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Aggiunge is_disposal a houses
    with op.batch_alter_table('houses', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('is_disposal', sa.Boolean(), nullable=False, server_default='0')
        )

    # 2. Aggiunge nuove colonne a containers (senza rimuovere ancora le vecchie)
    with op.batch_alter_table('containers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('current_location_id', sa.String(36), nullable=True))
        batch_op.add_column(sa.Column('destination_location_id', sa.String(36), nullable=True))

    # 3. Data migration containers: copia location_id → current_location_id
    op.execute('UPDATE containers SET current_location_id = location_id')

    # 4. Data migration containers: destination_id → destination_location_id
    #    Cerca una location con lo stesso nome nella stessa house della destination
    op.execute(
        '''
        UPDATE containers SET destination_location_id = (
            SELECT l.id FROM locations l
            INNER JOIN destinations d ON l.name = d.name AND l.house_id = d.house_id
            WHERE d.id = containers.destination_id
            LIMIT 1
        )
        WHERE destination_id IS NOT NULL
        '''
    )

    # 5. Aggiunge destination_location_id a transfers
    with op.batch_alter_table('transfers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('destination_location_id', sa.String(36), nullable=True))

    # 6. Data migration transfers: destination_id → destination_location_id
    op.execute(
        '''
        UPDATE transfers SET destination_location_id = (
            SELECT l.id FROM locations l
            INNER JOIN destinations d ON l.name = d.name AND l.house_id = d.house_id
            WHERE d.id = transfers.destination_id
            LIMIT 1
        )
        WHERE destination_id IS NOT NULL
        '''
    )

    # 7. Rimuove colonne vecchie da containers e aggiorna indici
    with op.batch_alter_table('containers', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_containers_location_id'))
        batch_op.drop_index(batch_op.f('ix_containers_destination_id'))
        batch_op.drop_column('location_id')
        batch_op.drop_column('destination_id')
        batch_op.create_index(
            batch_op.f('ix_containers_current_location_id'), ['current_location_id'], unique=False
        )
        batch_op.create_index(
            batch_op.f('ix_containers_destination_location_id'), ['destination_location_id'], unique=False
        )
        batch_op.create_foreign_key(
            'fk_containers_current_location_id', 'locations',
            ['current_location_id'], ['id'], ondelete='SET NULL'
        )
        batch_op.create_foreign_key(
            'fk_containers_destination_location_id', 'locations',
            ['destination_location_id'], ['id'], ondelete='SET NULL'
        )

    # 8. Rimuove colonna vecchia da transfers e aggiorna indici
    with op.batch_alter_table('transfers', schema=None) as batch_op:
        batch_op.drop_column('destination_id')
        batch_op.create_index(
            batch_op.f('ix_transfers_destination_location_id'), ['destination_location_id'], unique=False
        )
        batch_op.create_foreign_key(
            'fk_transfers_destination_location_id', 'locations',
            ['destination_location_id'], ['id']
        )

    # 9. Elimina tabella destinations
    op.drop_table('destinations')


def downgrade() -> None:
    # Ricrea tabella destinations (vuota — i dati non sono recuperabili)
    op.create_table(
        'destinations',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('house_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color', sa.String(7), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['house_id'], ['houses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # Ripristina transfers
    with op.batch_alter_table('transfers', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_transfers_destination_location_id'))
        batch_op.drop_constraint('fk_transfers_destination_location_id', type_='foreignkey')
        batch_op.drop_column('destination_location_id')
        batch_op.add_column(sa.Column('destination_id', sa.String(36), nullable=True))

    # Ripristina containers
    with op.batch_alter_table('containers', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_containers_current_location_id'))
        batch_op.drop_index(batch_op.f('ix_containers_destination_location_id'))
        batch_op.drop_constraint('fk_containers_current_location_id', type_='foreignkey')
        batch_op.drop_constraint('fk_containers_destination_location_id', type_='foreignkey')
        batch_op.drop_column('destination_location_id')
        batch_op.add_column(sa.Column('location_id', sa.String(36), nullable=True))
        batch_op.add_column(sa.Column('destination_id', sa.String(36), nullable=True))
        batch_op.create_index(batch_op.f('ix_containers_location_id'), ['location_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_containers_destination_id'), ['destination_id'], unique=False)

    # Copia current_location_id → location_id
    op.execute('UPDATE containers SET location_id = current_location_id')

    with op.batch_alter_table('containers', schema=None) as batch_op:
        batch_op.drop_column('current_location_id')

    # Rimuove is_disposal da houses
    with op.batch_alter_table('houses', schema=None) as batch_op:
        batch_op.drop_column('is_disposal')
