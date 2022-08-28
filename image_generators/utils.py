import os


def getenv(name: str):
    value = os.getenv(name)
    if not value:
        raise RuntimeError("Environment variable {0:s} not set".format(name))
    return value
