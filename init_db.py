from db import engine, Base
from models import *

print("Connecting to TiDB...")

Base.metadata.create_all(bind=engine)

print("HackForge tables created successfully!")