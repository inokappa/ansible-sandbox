from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import json
import socket
import uuid

import logging

try:
    import watchtower
    import boto3
    HAS_CW_LOGS = True
except ImportError:
    HAS_CW_LOGS = False

from ansible.plugins.callback import CallbackBase

class CallbackModule(CallbackBase):
    """
    ansible CloudWatch Logs callback plugin
    ansible.cfg:
        callback_plugins   = <path_to_callback_plugins_folder>
        callback_whitelist = cloudwatch_logs
    and put the plugin in <path_to_callback_plugins_folder>

    Requires:
        watchtower

    This plugin makes use of the following environment variables:
        AWS_PROFILE   (optional): defaults to default
        LOG_GROUP     (optional): defaults to ansible
        LOG_STREAM    (optional): defaults to provision
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'cloudwatch_logs'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):
        super(CallbackModule, self).__init__()

        if not HAS_CW_LOGS:
            self.disabled = True
            self._display.warning("The required watchtower is not installed. "
                "pip install watchtower")
        else:
            self.logger = logging.getLogger('watchtower')
            self.logger.setLevel(logging.DEBUG)

            self.logger.addHandler(watchtower.CloudWatchLogHandler(
                boto3_session=boto3.Session(profile_name=os.getenv('AWS_PROFILE', 'default')),
                log_group=os.getenv('LOG_GROUP', 'ansible'),
                stream_name=os.getenv('LOG_STREAM', 'provision'))
            )

            self.hostname = socket.gethostname()
            self.session = str(uuid.uuid1())
            self.errors = 0

    def v2_playbook_on_start(self, playbook):
        self.playbook = playbook._file_name
        data = {
            'log_action': "ansible start",
            'status': "OK",
            'host': self.hostname,
            'session': self.session,
            'ansible_type': "start",
            'ansible_playbook': self.playbook,
        }
        self.logger.info(data)

    def v2_playbook_on_stats(self, stats):
        summarize_stat = {}
        for host in stats.processed.keys():
            summarize_stat[host] = stats.summarize(host)

        if self.errors == 0:
            status = "OK"
        else:
            status = "FAILED"

        data = {
            'log_action': "ansible stats",
            'status': status,
            'host': self.hostname,
            'session': self.session,
            'ansible_type': "finish",
            'ansible_playbook': self.playbook,
            'ansible_result': json.dumps(summarize_stat),
        }
        self.logger.info(data)

    def v2_runner_on_ok(self, result, **kwargs):
        data = {
            'log_action': "ansible ok",
            'status': "OK",
            'host': self.hostname,
            'session': self.session,
            'ansible_type': "task",
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.name,
            'ansible_task': result._task,
            'ansible_result': self._dump_results(result._result)
        }
        self.logger.info(data)

    def v2_runner_on_skipped(self, result, **kwargs):
        data = {
            'log_action': "ansible skipped",
            'status': "SKIPPED",
            'host': self.hostname,
            'session': self.session,
            'ansible_type': "task",
            'ansible_playbook': self.playbook,
            'ansible_task': result._task,
            'ansible_host': result._host.name
        }
        self.logger.info(data)

    def v2_playbook_on_import_for_host(self, result, imported_file):
        data = {
            'log_action': "ansible import",
            'status': "IMPORTED",
            'host': self.hostname,
            'session': self.session,
            'ansible_type': "import",
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.name,
            'imported_file': imported_file
        }
        self.logger.info(data)

    def v2_playbook_on_not_import_for_host(self, result, missing_file):
        data = {
            'log_action': "ansible import",
            'status': "NOT IMPORTED",
            'host': self.hostname,
            'session': self.session,
            'ansible_type': "import",
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.name,
            'missing_file': missing_file
        }
        self.logger.info(data)

    def v2_runner_on_failed(self, result, **kwargs):
        data = {
            'log_action': "ansible failed",
            'status': "FAILED",
            'host': self.hostname,
            'session': self.session,
            'ansible_type': "task",
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.name,
            'ansible_task': result._task,
            'ansible_result': self._dump_results(result._result)
        }
        self.errors += 1
        self.logger.error(data)

    def v2_runner_on_unreachable(self, result, **kwargs):
        data = {
            'log_action': "ansbile unreachable",
            'status': "UNREACHABLE",
            'host': self.hostname,
            'session': self.session,
            'ansible_type': "task",
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.name,
            'ansible_task': result._task,
            'ansible_result': self._dump_results(result._result)
        }
        self.logger.error(data)

    def v2_runner_on_async_failed(self, result, **kwargs):
        data = {
            'log_action': "ansible async",
            'status': "FAILED",
            'host': self.hostname,
            'session': self.session,
            'ansible_type': "task",
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.name,
            'ansible_task': result._task,
            'ansible_result': self._dump_results(result._result)
        }
        self.errors += 1
        self.logger.error(data)
