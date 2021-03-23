import os
class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = os.urandom(24)
    # SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_DATABASE_URI = 'postgres://iyrxjafwmybqog:047647631db0ac1b3d727d7edd5b9e4c299586131585e1b6d41b2bc98e412521@ec2-52-7-115-250.compute-1.amazonaws.com:5432/dfmfctp63eg654'