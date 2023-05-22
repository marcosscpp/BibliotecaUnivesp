import os

SECRET_KEY = "univesp"

SQLALCHEMY_DATABASE_URI = \
    'mysql://{user}:{password}@{server}:{port}/{database}'.format(
        user='root',
        password='skwqvq7fkjJ2g7XmTStR',
        server='containers-us-west-14.railway.app',
        port=6602,
        database='railway'
    )


DIR_PATH = os.path.dirname(os.path.abspath(__file__)) + "/imagens"