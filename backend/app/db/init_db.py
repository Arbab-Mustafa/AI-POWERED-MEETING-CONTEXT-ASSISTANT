"""
Database Initialization Script
Creates all tables in PostgreSQL (Neon) from SQLAlchemy models
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.models.db import Base
from app.core.config import logger


async def init_database():
    """
    Initialize database by creating all tables
    """
    logger.info("🔄 Starting database initialization...")
    logger.info(f"📊 Database: {settings.DATABASE_ASYNC_URL.split('@')[1].split('/')[0]}")
    
    try:
        # Create async engine with SSL support for Neon
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        engine = create_async_engine(
            settings.DATABASE_ASYNC_URL,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            connect_args={"ssl": ssl_context}
        )
        
        logger.info("✅ Database engine created successfully")
        
        # Create all tables
        async with engine.begin() as conn:
            logger.info("🔨 Creating database tables...")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ All tables created successfully!")
        
        # Verify tables
        async with engine.connect() as conn:
            from sqlalchemy import text
            result = await conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            )
            tables = [row[0] for row in result.fetchall()]
            
            logger.info(f"📋 Created {len(tables)} tables:")
            for table in sorted(tables):
                logger.info(f"   ✓ {table}")
        
        await engine.dispose()
        logger.info("🎉 Database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        return False


async def drop_all_tables():
    """
    Drop all tables (use with caution!)
    """
    logger.warning("⚠️  DROPPING ALL TABLES - This will delete all data!")
    
    try:
        engine = create_async_engine(
            settings.DATABASE_ASYNC_URL,
            echo=settings.DEBUG
        )
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("✅ All tables dropped")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to drop tables: {str(e)}")
        return False


async def reset_database():
    """
    Drop and recreate all tables (fresh start)
    """
    logger.info("🔄 Resetting database (drop + create)...")
    
    success_drop = await drop_all_tables()
    if not success_drop:
        return False
    
    success_init = await init_database()
    return success_init


if __name__ == "__main__":
    import sys
    
    command = sys.argv[1] if len(sys.argv) > 1 else "init"
    
    if command == "init":
        asyncio.run(init_database())
    elif command == "drop":
        confirm = input("Are you sure you want to DROP ALL TABLES? (yes/no): ")
        if confirm.lower() == "yes":
            asyncio.run(drop_all_tables())
        else:
            print("Cancelled.")
    elif command == "reset":
        confirm = input("Reset database (DROP + CREATE)? (yes/no): ")
        if confirm.lower() == "yes":
            asyncio.run(reset_database())
        else:
            print("Cancelled.")
    else:
        print("Usage: python -m app.db.init_db [init|drop|reset]")
        print("  init  - Create all tables")
        print("  drop  - Drop all tables")
        print("  reset - Drop and recreate all tables")
