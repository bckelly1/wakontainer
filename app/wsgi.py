from app import app
import multiprocessing
import gunicorn.app.base
from os import getenv

conf = {
    "number_of_workers": 3,
    "port": 8080,
    "bind_address": "127.0.0.1"
}

for varname in conf.keys():
    fromenv = getenv(f"WAKONTAINER_{varname.upper()}")
    if fromenv:
        conf[varname] = fromenv


class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

if __name__ == '__main__':
    options = {
        'bind': f"{conf['bind_address']}:{conf['port']}",
        'workers': conf['number_of_workers'],
    }
    StandaloneApplication(app, options).run()