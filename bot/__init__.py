from discord.ext.commands import Bot
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


DATABASE_USERNAME = "dbname"
DATABASE_PASSWORD = "password"
DATABASE_IP = "localhost"
DATABASE_NAME = "boredbotrewrite"


dir_path = os.path.dirname(os.path.realpath(__file__))[:-4]
engine = create_engine(f"mysql+pymysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_IP}/{DATABASE_NAME}")
session = sessionmaker(bind=engine)()

Base = declarative_base()

client = Bot(command_prefix=">", case_insensitive=True)
client.remove_command("help")


from bot import events, models, usercommands
