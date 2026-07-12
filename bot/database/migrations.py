# bot/database/migrations.py
from alembic import op
import sqlalchemy as sa
from datetime import datetime

def upgrade():
    """تحديث قاعدة البيانات"""
    # إضافة عمود new_column إلى جدول users
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))
    
    # إنشاء جدول جديد
    op.create_table(
        'settings',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('key', sa.String(100), nullable=False),
        sa.Column('value', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime, default=datetime.now)
    )

def downgrade():
    """الرجوع للتحديث"""
    op.drop_column('users', 'phone')
    op.drop_table('settings')
