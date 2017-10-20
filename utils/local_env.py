import os
import yaml

LOCAL_ENV_PATH = '.env'


def try_initialize_local_env():
    if os.path.exists(LOCAL_ENV_PATH):
        load_env_file(LOCAL_ENV_PATH)
        return True
    return False


def load_env_file(p):
    y = yaml.load(open(p, 'r'))

    for k, v in y.items():
        # k = k.upper()
        if k in os.environ.keys():
            print("We rewrite " + str(k) in " env.")
        os.environ[k] = v
