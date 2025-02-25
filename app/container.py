import docker
from datetime import datetime, timezone
from logger import Logger
from default import default_conf

log = Logger('container')

def create_conf():
    client = docker.from_env()
    conf = dict()
    conf['default'] = default_conf
    conf['containers'] = dict()
    for container in client.containers.list(all=True):
        if container.labels.get('wakontainer.enable'):
            name = container.name
            url = container.labels.get('wakontainer.url')
            if not url:
                log.error(f"Container '{name}' misses wakontainer.url label. Ignoring this container.")
                continue
            wait_page_time = container.labels.get('wakontainer.wait_page_time')
            max_lifetime = container.labels.get('wakontainer.max_lifetime')
            conf['containers'][container.name] = {
                'url': url,
                'name': name,
                'wait_page_time': wait_page_time,
                'max_lifetime': max_lifetime
            }
    log.info(f"Using config : {conf}")
    return conf

class Container:
    def __init__(self, name):
        self.name = name
        self.logger = log

    def status(self):
        client = docker.from_env()
        self.logger.debug(f"Getting status of container {self.name}")
        try:
            c = client.containers.get(self.name)
        except docker.errors.NotFound as e:
            self.logger.error(f"No such container '{self.name}'")
            return {
                "req_state": "error",
                "msg": f"No such container '{self.name}'"
            }
        else:
            c_state = c.attrs["State"]
        started_at = c_state.get('StartedAt')
        given_date = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
        current_date = datetime.now(timezone.utc)
        since_last_start = (current_date-given_date).total_seconds()

        self.logger.debug(f"Successfully got status of container {self.name}")

        return {
          "req_state": "success",
          "running": c_state.get('Running'),
          "since_last_start": since_last_start
        }

    def stop_if_needed(self, numsec):
        # stop the container if start since more than numsec seconds
        client = docker.from_env()
        status = self.status()
        self.logger.info(f"Checking if container {self.name} should be stopped")
        if status['req_state'] == 'error':
            return status
        if not status['running']:
            self.logger.debug(f"Container {self.name} is already stopped")
            return {
                "req_state": "success",
                "msg": f"Container {self.name} already stopped"
            }
        if status['since_last_start'] > numsec:
            self.logger.debug(f"Container {self.name} should be stopped (alive since {status['since_last_start']}s when max is {numsec}s).")
            client.containers.get(self.name).stop()
            self.logger.info(f"Container {self.name} successfully stopped")
            return {
                "req_state": "success",
                "msg": f"Container stopped after being alive for {status['since_last_start']} seconds"
            }
        self.logger.debug(f"Container {self.name} does not need to be stopped (alive since {status['since_last_start']}s when max is {numsec}s).")
        return {
                "req_state": "success",
                "msg": f"Container alive for less than {numsec} seconds. No need to stop"
            }


    def stop(self):
        self.logger.info(f"Received stopping request for {self.name}")
        client = docker.from_env()
        status = self.status()
        if status['req_state'] == 'error':
            return status
        if not status['running']:
            self.logger.info(f"Container {self.name} is already stopped")
            return {
                "req_state": "success",
                "msg": "Container already stopped"
            }
        client.containers.get(self.name).stop()
        self.logger.info(f"Container {self.name} was successfully stopped")
        return {
            "req_state": "success",
            "msg": f"Container stopped after being alive for {status['since_last_start']} seconds"
        }
    
    def start(self):
        self.logger.info(f"Received starting request for {self.name}")
        client = docker.from_env()
        s = self.status()
        if s['req_state'] == "error":
            return s
        if s['running']:
            self.logger.info(f"Container {self.name} already running")
            return {
                "state": "success",
                "msg": "Already running"
            }
        self.logger.info(f"Container {self.name} started")
        client.containers.get(self.name).start()
        return {
            "state": "success",
            "msg": "Container started"
        }
