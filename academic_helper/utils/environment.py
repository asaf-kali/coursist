import os
from enum import Enum


class Environment(Enum):
    local = "Local"
    dev = "Development"
    stage = "Staging"
    prod = "Production"


try:
    ENV = os.getenv("COURSIST_ENV", "local")
    ENV = Environment[ENV]
except Exception as e:
    ENV = Environment.local

print("Environment is set to [" + ENV.value + "]")


def is_prod() -> bool:
    return ENV == Environment.prod
