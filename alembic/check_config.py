from alembic.config import Config

config = Config("alembic.ini")

print("Archivo:", config.config_file_name)
print("URL:", config.get_main_option("sqlalchemy.url"))