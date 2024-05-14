import os


def is_testing_environment() -> bool:
    """
    Check if the current environment is a testing environment.
    """
    return not os.getenv('GAE_ENV', '').startswith('standard')
