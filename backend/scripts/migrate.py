#!/usr/bin/env python3

import subprocess
import sys
import pymysql
from core import settings

def create_database():
    """Create the database if it doesn't exist."""
    print(f"Creating database '{settings.MYSQL_DATABASE}' if not exists...")
    
    try:
        connection = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=int(settings.MYSQL_PORT),
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD
        )
        
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.MYSQL_DATABASE}")
            print(f"✅ Database ready")
        
        connection.commit()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        sys.exit(1)

def run_migrations():
    """Run Alembic migrations."""
    print("Running Alembic migrations...")
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("✅ Migrations completed")
        
        subprocess.run(["alembic", "current"], check=True)
        print("✅ Current migration status shown")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_database()
    run_migrations()