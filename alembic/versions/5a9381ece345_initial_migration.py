import geoalchemy2
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a9381ece345'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Execute raw SQL to handle existing objects
    conn = op.get_bind()
    
    # Create tables with IF NOT EXISTS
    conn.execute(sa.text("""
        -- Customers table
        CREATE TABLE IF NOT EXISTS customers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            api_key VARCHAR(64) NOT NULL UNIQUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create index if not exists
        CREATE INDEX IF NOT EXISTS ix_customers_api_key ON customers (api_key);
        CREATE INDEX IF NOT EXISTS ix_customers_id ON customers (id);
        
        -- Networks table
        CREATE TABLE IF NOT EXISTS networks (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            customer_id INTEGER NOT NULL REFERENCES customers(id),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create index if not exists
        CREATE INDEX IF NOT EXISTS ix_networks_id ON networks (id);
        
        -- Network versions table
        CREATE TABLE IF NOT EXISTS network_versions (
            id SERIAL PRIMARY KEY,
            network_id INTEGER NOT NULL REFERENCES networks(id),
            version_number INTEGER NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT uix_network_version UNIQUE (network_id, version_number)
        );
        
        -- Create index if not exists
        CREATE INDEX IF NOT EXISTS ix_network_versions_id ON network_versions (id);
        
        -- Nodes table
        CREATE TABLE IF NOT EXISTS nodes (
            id SERIAL PRIMARY KEY,
            network_id INTEGER NOT NULL REFERENCES networks(id),
            version_id INTEGER NOT NULL REFERENCES network_versions(id),
            external_id VARCHAR(100),
            geometry GEOMETRY(POINT, 4326) NOT NULL,
            properties JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT uix_node_network_external_version UNIQUE (network_id, external_id, version_id)
        );
        
        -- Create index if not exists
        CREATE INDEX IF NOT EXISTS ix_nodes_id ON nodes (id);
        CREATE INDEX IF NOT EXISTS idx_nodes_geometry ON nodes USING gist (geometry);
        
        -- Edges table
        CREATE TABLE IF NOT EXISTS edges (
            id SERIAL PRIMARY KEY,
            network_id INTEGER NOT NULL REFERENCES networks(id),
            version_id INTEGER NOT NULL REFERENCES network_versions(id),
            external_id VARCHAR(100),
            source_node_id INTEGER NOT NULL REFERENCES nodes(id),
            target_node_id INTEGER NOT NULL REFERENCES nodes(id),
            geometry GEOMETRY(LINESTRING, 4326) NOT NULL,
            properties JSONB,
            is_current BOOLEAN DEFAULT TRUE,
            valid_from TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            valid_to TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create index if not exists
        CREATE INDEX IF NOT EXISTS ix_edges_id ON edges (id);
        CREATE INDEX IF NOT EXISTS idx_edges_geometry ON edges USING gist (geometry);
    """))


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('edges')
    op.drop_table('nodes')
    op.drop_table('network_versions')
    op.drop_table('networks')
    op.drop_table('customers')
