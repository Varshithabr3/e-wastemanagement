import sys
import os
basedir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, basedir)

from app import engine
from sqlalchemy import text

def run_migration():
    with engine.connect() as conn:
        res = conn.execute(text('DESCRIBE recycling_centres;')).fetchall()
        existing_rc_cols = [r[0] for r in res]
        print('Current recycling_centres columns:', existing_rc_cols)
        
        if 'district' not in existing_rc_cols:
            conn.execute(text('ALTER TABLE recycling_centres ADD COLUMN district VARCHAR(100) NULL AFTER city;'))
            print('Added district column.')
        if 'pincode' not in existing_rc_cols:
            conn.execute(text('ALTER TABLE recycling_centres ADD COLUMN pincode VARCHAR(15) NULL AFTER district;'))
            print('Added pincode column.')
        if 'facility_type' not in existing_rc_cols:
            conn.execute(text("ALTER TABLE recycling_centres ADD COLUMN facility_type VARCHAR(80) NOT NULL DEFAULT 'Authorized Recycler' AFTER state;"))
            print('Added facility_type column.')

        res_u = conn.execute(text('DESCRIBE users;')).fetchall()
        existing_u_cols = [r[0] for r in res_u]
        print('Current users columns:', existing_u_cols)
        if 'reset_token' not in existing_u_cols:
            conn.execute(text('ALTER TABLE users ADD COLUMN reset_token VARCHAR(100) NULL;'))
            print('Added reset_token column to users.')
        if 'reset_token_expiry' not in existing_u_cols:
            conn.execute(text('ALTER TABLE users ADD COLUMN reset_token_expiry DATETIME NULL;'))
            print('Added reset_token_expiry column to users.')
            
        conn.commit()
        print('Database migration completed successfully!')

if __name__ == '__main__':
    run_migration()

