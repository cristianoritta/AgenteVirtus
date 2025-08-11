"""Adicionar tabela de configurações do sistema

Revision ID: 20241201_add_system_config
Revises: 53588b45571b
Create Date: 2024-12-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20241201_add_system_config'
down_revision = '53588b45571b'
branch_labels = None
depends_on = None


def upgrade():
    # Criar tabela de configurações do sistema
    op.create_table('system_config',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chave', sa.String(length=100), nullable=False),
        sa.Column('valor', sa.Text(), nullable=True),
        sa.Column('descricao', sa.String(length=255), nullable=True),
        sa.Column('data_criacao', sa.DateTime(), nullable=True),
        sa.Column('data_atualizacao', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chave')
    )
    
    # Inserir configuração padrão do banco de dados
    op.execute("""
        INSERT INTO system_config (chave, valor, descricao, data_criacao, data_atualizacao)
        VALUES ('database_path', 'instance/agente_virtus.db', 'Caminho do arquivo do banco de dados', 
                datetime('now'), datetime('now'))
    """)


def downgrade():
    op.drop_table('system_config')
