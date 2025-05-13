from flask import Flask, request, render_template, redirect
from flask_apscheduler import APScheduler
import yaml
from datetime import datetime
from multiprocessing import Manager

from container import Container, create_conf
from logger import Logger

def read_conf(conf_path):
    with open(conf_path, 'r') as conf:
        data = yaml.safe_load(conf)
    return data

app = Flask(__name__)

manager = Manager()
shared_dict = manager.dict()
shared_dict['conf'] = create_conf()

log = Logger('app')

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# @scheduler.task('interval', id='stop_containers', seconds=shared_dict['conf']['default']['check_interval'])
def stop_containers():
    log.debug("Launching scheduled check for stopping containers")
    default_max_lifetime = shared_dict['conf']['default']['max_lifetime']
    for c_dic in shared_dict['conf'].get('containers').values():
        c_name = c_dic['name']
        c_url = c_dic['url']
        c_max_lifetime = c_dic.get('max_lifetime')
        if c_max_lifetime:
            max_lifetime = 30
        else:
            #max_lifetime = default_max_lifetime
            max_lifetime = 30
        log.info(max_lifetime)
        container = Container(c_name)
        last_req = shared_dict.get(c_url)
        if last_req:
            since_last_req = int(datetime.now().timestamp()) - int(float(last_req))
            if since_last_req > max_lifetime:
                log.info(f"Container {c_name} requested more than {max_lifetime}s ago ({since_last_req}s). Requesting stop")
                shared_dict[c_url] = None
                container.stop()
            else:
                pass
                log.info(f"Container {c_name} requested less than {max_lifetime}s ago ({since_last_req}s)")
        else:
            log.info(f"Unknown last request time for container {c_name}. Checking if stop needed")
            container.stop_if_needed(max_lifetime)

# @scheduler.task('interval', id='update_conf', seconds=shared_dict['conf']['default']['update_conf_interval'])
def update_conf():
    log.info("Launching scheduled conf update")
    shared_dict['conf'] = create_conf()

@app.route('/start')
def start():
    orig = request.headers.get('X-Forwarded-Host')
    log.info(f"Received starting request with 'X-Forwarded-Host' : '{orig}'")
    shared_dict[orig] = int(datetime.now().timestamp())
    default_wait_time = shared_dict['conf']['default']['wait_page_time']
    container = None
    for c_dic in shared_dict['conf'].get('containers').values():
        if c_dic['url'] == orig:
            log.info(f"Found corresponding container {c_dic['name']}")
            container = Container(c_dic['name'])
            container_wait_time = c_dic.get('wait_page_time')
    if not container:
        log.warning(f"Did not find corresponding container with wakontainer.url : '{orig}'")
        return render_template('404.html'), 404
    status = container.status()
    log.info(f"Container in status: {status}")
    if status['running'] == 'False':
        # log.info(f"Requesting start for container { c_dic['name']}")
        log.info(f"testing before")
        container.start()
        log.info(f"testing after")
        # log.info(f"Start command result { s['state'] } and { s['msg'] }")

        if container_wait_time:
            wait_time = container_wait_time
        else:
            wait_time = default_wait_time
        log.info(f"Container '{c_dic['name']}' successfully started, returning wait page")
        return render_template('wait.html', app_name=orig, wait_time=wait_time), 200

    if status['running'] == 'False':
        log.debug(f"Container '{c_dic['name']}' was already running")
        return redirect(f"https://{orig}")
    if status['req_state'] == 'error':
        return "Container does not exist, check syntax", 404
@app.route('/')
def default():
    orig = request.headers.get('X-Forwarded-Host')
    return redirect(f"https://{orig}")
