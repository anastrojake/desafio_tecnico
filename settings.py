import os


class Settings:
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'postgresql://root:root@localhost/gardeniot')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'secretkey')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'secretkeyjwt')

