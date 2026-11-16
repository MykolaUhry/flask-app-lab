"""Insert data into products table

Revision ID: 7e17612d24aa
Revises: fb9dd2307474
Create Date: 2026-11-17 00:08:39.201491

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7e17612d24aa'
down_revision = 'fb9dd2307474'
branch_labels = None
depends_on = None


def upgrade():
    categories = sa.table(
        'categories',
        sa.column('id', sa.Integer()),
        sa.column('name', sa.String())
    )

    products = sa.table(
        'products',
        sa.column('name', sa.String()),
        sa.column('price', sa.Float()),
        sa.column('active', sa.Boolean()),
        sa.column('category_id', sa.Integer())
    )

    op.bulk_insert(categories, [
        {'name': 'Electronics'},
        {'name': 'Books'},
        {'name': 'Clothing'}
    ])

    connection = op.get_bind()

    electronics_id = connection.execute(
        sa.select(categories.c.id)
        .where(categories.c.name == 'Electronics')
    ).scalar_one()

    books_id = connection.execute(
        sa.select(categories.c.id)
        .where(categories.c.name == 'Books')
    ).scalar_one()

    clothing_id = connection.execute(
        sa.select(categories.c.id)
        .where(categories.c.name == 'Clothing')
    ).scalar_one()

    op.bulk_insert(products, [
        {
            'name': 'Laptop',
            'price': 1200.0,
            'active': True,
            'category_id': electronics_id
        },
        {
            'name': 'Smartphone',
            'price': 800.0,
            'active': True,
            'category_id': electronics_id
        },
        {
            'name': 'Novel',
            'price': 20.0,
            'active': True,
            'category_id': books_id
        },
        {
            'name': 'T-Shirt',
            'price': 25.0,
            'active': False,
            'category_id': clothing_id
        }
    ])


def downgrade():
    op.execute("""
        DELETE FROM products
        WHERE
            (name IN ('Laptop', 'Smartphone')
             AND category_id IN (
                 SELECT id FROM categories
                 WHERE name = 'Electronics'
             ))
            OR
            (name = 'Novel'
             AND category_id IN (
                 SELECT id FROM categories
                 WHERE name = 'Books'
             ))
            OR
            (name = 'T-Shirt'
             AND category_id IN (
                 SELECT id FROM categories
                 WHERE name = 'Clothing'
             ))
    """)

    op.execute("""
        DELETE FROM categories
        WHERE name IN ('Electronics', 'Books', 'Clothing')
    """)