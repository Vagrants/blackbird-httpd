#!/usr/bin/env python
# -*- encodig: utf-8 -*-
"""
Get the httpd's "server-status"
"""

import requests
import csv
import re

from blackbird.plugins import base


class ConcreteJob(base.JobBase):
    """
    This class is Called by "Executor".
    Get httpd's server-stats,
    and send to specified zabbix server.
    """

    def __init__(self, options, queue=None, logger=None):
        super(ConcreteJob, self).__init__(options, queue, logger)

    def build_items(self):
        """
        main loop
        """

        # get information from server-status
        self._get_status()

        # get configuration from server-info
        self._get_config()

        # get response time and availability
        self._get_response_time()

    def _enqueue(self, item):
        self.queue.put(item, block=False)
        self.logger.debug(
            'Inserted to queue {key}:{value}'
            ''.format(key=item.key, value=item.value)
        )

    def _request(self, url, timeout):
        """
        Request http connection and return contents.
        """

        try:
            response = requests.get(url, timeout=timeout)
        except requests.exceptions.RequestException:
            self.logger.error(
                'Can not connect to {url}'
                ''.format(url=url)
            )
            return []

        if response.status_code == 200:
            return response.content.splitlines()
        else:
            self.logger.error(
                'Can not get status from {url} status:{status}'
                ''.format(url=url, status=response.status_code)
            )
            return []

    def _get_status(self):
        """
        get information from server-status

        _ : Waiting for Connection
        S : Starting up
        R : Reading Request
        W : Sending Reply
        K : Keepalive (read)
        D : DNS Lookup
        C : Closing connection
        L : Logging
        G : Gracefully finishing
        I : Idle cleanup of worker
        . : Open slot with no current process
        """

        mapping = {
            "_":"waiting_for_connection",
            "S":"starting_up",
            "R":"reading_request",
            "W":"sending_reply",
            "K":"keepalive_read",
            "D":"DNS_lookup",
            "C":"closing_connection",
            "L":"logging",
            "G":"gracefully_finishing",
            "I":"idle_cleanup",
            ".":"no_current_process",
        }

        if self.options['ssl']:
            method = 'https://'
        else:
            method = 'http://'
        url = (
            '{method}{host}:{port}{uri}?auto'
            ''.format(
                method=method,
                host=self.options['host'],
                port=self.options['port'],
                uri=self.options['status_uri']
            )
        )

        contents = csv.reader(self._request(url=url, timeout=self.options['timeout']),
                              delimiter = ":",
                              skipinitialspace = True)
        status = {}
        for (key, value) in contents:
            if key == 'Scoreboard':
                st = {
                    "waiting_for_connection":0,
                    "starting_up":0,
                    "reading_request":0,
                    "sending_reply":0,
                    "keepalive_read":0,
                    "DNS_lookup":0,
                    "closing_connection":0,
                    "logging":0,
                    "gracefully_finishing":0,
                    "idle_cleanup":0,
                    "no_current_process":0,
                }
                for sb in value:
                    st[mapping[sb]] += 1
                status[key] = st
            else:
                status[key] = value

        for (key, value) in status.items():
            if key == "Scoreboard":
                for (sc_key, sc_val) in value.items():
                    item = HttpdItem(
                        key='scoreboard,{key}'.format(key=sc_key),
                        value=sc_val,
                        host=self.options['hostname']
                    )
                    self._enqueue(item)
            else:
                item = HttpdItem(
                    key=key.replace(' ', '_').lower(),
                    value=value,
                    host=self.options['hostname']
                )
                self._enqueue(item)

    def _get_config(self):
        """
        get information from server-info
        """
        if self.options['ssl']:
            method = 'https://'
        else:
            method = 'http://'
        url = (
            '{method}{host}:{port}{uri}?config'
            ''.format(
                method=method,
                host=self.options['host'],
                port=self.options['port'],
                uri=self.options['info_uri']
            )
        )

        for line in self._request(url=url, timeout=self.options['timeout']):
            result = re.search('MaxClients <i>(\d+)</i>', line)
            if result:
                item = HttpdItem(
                    key='maxclients',
                    value=result.group(1),
                    host=self.options['hostname']
                )
                self._enqueue(item)

    def _get_response_time(self):
        """
        get response time for check uri
        """

        # do not monitoring
        if not 'response_check_uri' in self.options:
            item = HttpdGroupItem(
                key='amount',
                value=0,
                host=self.options['hostname']
            )
            self._enqueue(item)
            return

        # do monitoring
        item = HttpdGroupItem(
            key='amount',
            value=1,
            host=self.options['hostname']
        )
        self._enqueue(item)

        if self.options['response_check_ssl']:
            method = 'https://'
        else:
            method = 'http://'

        url = (
            '{method}{host}:{port}{uri}'
            ''.format(
                method=method,
                host=self.options['response_check_host'],
                port=self.options['response_check_port'],
                uri=self.options['response_check_uri']
            )
        )

        headers = {
            'Host': self.options['response_check_vhost'],
            'User-Agent': self.options['response_check_uagent'],
        }

        with base.Timer() as timer:
            try:
                response = requests.get(url,
                                        timeout=self.options['response_check_timeout'],
                                        headers=headers)
            except requests.exceptions.RequestException:
                self.logger.error(
                    'Response check failed. Can not connect to {url}'
                    ''.format(url=url)
                )
                item = HttpdGroupItem(
                    key='available',
                    value=0,
                    host=self.options['hostname']
                )
                self._enqueue(item)
                return

        if response.status_code == 200:
            time = timer.sec
            available = 1
        else:
            self.logger.error(
                'Response check failed. Response code is {status} on {url}'
                ''.format(status=response.status_code, url=url)
            )
            time = 0
            available = 0

        item = HttpdGroupItem(
            key='available',
            value=available,
            host=self.options['hostname']
        )
        self._enqueue(item)

        item = HttpdItem(
            key='response_check,time',
            value=time,
            host=self.options['hostname']
        )
        self._enqueue(item)

        item = HttpdItem(
            key='response_check,status_code',
            value=response.status_code,
            host=self.options['hostname']
        )
        self._enqueue(item)


class HttpdItem(base.ItemBase):
    """
    Enqued item.
    """

    def __init__(self, key, value, host):
        super(HttpdItem, self).__init__(key, value, host)

        self._data = {}
        self._generate()

    @property
    def data(self):
        return self._data

    def _generate(self):
        self._data['key'] = 'httpd.stat[{0}]'.format(self.key)
        self._data['value'] = self.value
        self._data['host'] = self.host
        self._data['clock'] = self.clock


class HttpdGroupItem(base.ItemBase):
    """
    Enqued item.
    """

    def __init__(self, key, value, host):
        super(HttpdGroupItem, self).__init__(key, value, host)

        self._data = {}
        self._generate()

    @property
    def data(self):
        return self._data

    def _generate(self):
        self._data['key'] = 'httpd.group.{0}'.format(self.key)
        self._data['value'] = self.value
        self._data['host'] = self.host
        self._data['clock'] = self.clock


class Validator(base.ValidatorBase):
    """
    Validate configuration.
    """

    def __init__(self):
        self.__spec = None

    @property
    def spec(self):
        """
        "user" and "password" in spec are
        for BASIC and Digest authentication.
        """
        self.__spec = (
            "[{0}]".format(__name__),
            "host = string(default='127.0.0.1')",
            "port = integer(0, 65535, default=80)",
            "timeout = integer(0, 600, default=3)",
            "status_uri = string(default='/server-status')",
            "info_uri = string(default='/server-info')",
            "user = string(default=None)",
            "password = string(default=None)",
            "ssl = boolean(default=False)",
            "response_check_host = string(default='127.0.0.1')",
            "response_check_port = integer(0, 65535, default=80)",
            "response_check_timeout = integer(0, 600, default=3)",
            "response_check_vhost = string(default='localhost')",
            "response_check_uagent = string(default='blackbird response check')",
            "response_check_ssl = boolean(default=False)",
            "hostname = string(default={0})".format(self.detect_hostname()),
        )
        return self.__spec
