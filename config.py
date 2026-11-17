import os
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'ewaste_management_secret_key_2026_default')
    
    # MySQL Database Settings
    MYSQL_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'varshitha')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'varshitha')
    MYSQL_DB = os.getenv('MYSQL_DB', 'varshitha')
    
    # Upload configuration
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
    
    # Construct SQLAlchemy Database URI
    # Default to PyMySQL driver
    @classmethod
    def get_database_uri(cls):
        # Check custom explicit DATABASE_URL if provided
        env_db_url = os.getenv('DATABASE_URL')
        if env_db_url:
            return env_db_url, "Custom Environment Database"

        # Check MySQL connectivity
        try:
            import pymysql
            conn = pymysql.connect(
                host=cls.MYSQL_HOST,
                user=cls.MYSQL_USER,
                password=cls.MYSQL_PASSWORD,
                database=cls.MYSQL_DB,
                port=cls.MYSQL_PORT,
                connect_timeout=3
            )
            conn.close()
            mysql_uri = f"mysql+pymysql://{cls.MYSQL_USER}:{cls.MYSQL_PASSWORD}@{cls.MYSQL_HOST}:{cls.MYSQL_PORT}/{cls.MYSQL_DB}?charset=utf8mb4"
            return mysql_uri, f"MySQL Server (Database: {cls.MYSQL_DB})"
        except Exception as e:
            # If specified database failed, test if ewaste_management works
            try:
                import pymysql
                conn = pymysql.connect(
                    host=cls.MYSQL_HOST,
                    user='root',
                    password='root',
                    database='ewaste_management',
                    port=cls.MYSQL_PORT,
                    connect_timeout=2
                )
                conn.close()
                return f"mysql+pymysql://root:root@{cls.MYSQL_HOST}:{cls.MYSQL_PORT}/ewaste_management?charset=utf8mb4", "MySQL Server (Database: ewaste_management)"
            except Exception:
                pass
            
            # Fallback to local SQLite if MySQL daemon is not running
            sqlite_path = os.path.join(basedir, 'ewaste_management.db')
            return f"sqlite:///{sqlite_path}", "SQLite Local Fallback (MySQL service offline)"

SQLALCHEMY_DATABASE_URI, DB_ENGINE_LABEL = Config.get_database_uri()

