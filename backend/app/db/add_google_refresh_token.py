"""
Migration to add google_refresh_token column to users table
Run this file once to update the database schema
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings
from app.core.config import logger
import ssl


async def add_google_refresh_token_column():
    """
    Add google_refresh_token column to users table
    """
    logger.info("🔄 Starting migration: Adding google_refresh_token column...")
    
    try:
        # Create async engine with SSL support for Neon
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        engine = create_async_engine(
            settings.DATABASE_ASYNC_URL,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            connect_args={"ssl": ssl_context}
        )
        
        logger.info("✅ Database engine created successfully")
        
        # Add the column
        async with engine.begin() as conn:
            # Check if column already exists
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name = 'google_refresh_token'
            """)
            
            result = await conn.execute(check_query)
            exists = result.fetchone()
            
            if exists:
                logger.info("✓ Column google_refresh_token already exists. Skipping.")
            else:
                # Add the column
                alter_query = text("""
                    ALTER TABLE users 
                    ADD COLUMN google_refresh_token TEXT
                """)
                
                await conn.execute(alter_query)
                logger.info("✅ Successfully added google_refresh_token column to users table")
        
        await engine.dispose()
        logger.info("🎉 Migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        return False


if __name__ == "__main__":
    print("\n" + "="*70)
    print("MIGRATION: Add google_refresh_token column to users table")
    print("="*70 + "\n")
    
    result = asyncio.run(add_google_refresh_token_column())
    
    if result:
        print("\n✅ Migration completed successfully!\n")
        sys.exit(0)
    else:
        print("\n❌ Migration failed!\n")
        sys.exit(1)
