import logging
import os
import signal

import netaddr

from hades.common.db import get_all_dhcp_hosts
from hades.config.loader import get_config

logger = logging.getLogger(__name__)


def reload_auth_dnsmasq():
    config = get_config(runtime_checks=True)
    pid_file = config['HADES_AUTH_DNSMASQ_PID_FILE']
    try:
        with open(pid_file, mode='rb') as f:
            data = f.readline()
    except OSError as e:
        logger.error("Could not read PID file %s: %s", pid_file, e.strerror)
        return
    try:
        pid = int(data)
    except ValueError:
        logger.error("Invalid PID in PID file %s: %s", pid_file, data)
        return
    if pid < 1:
        logger.error("Invalid PID in PID file %s: %d", pid_file, pid)
    try:
        os.kill(pid, signal.SIGHUP)
    except OSError as e:
        logger.error("Can't send SIGHUP to pid %d from PID file %s: %s", pid,
                     pid_file, e.strerror)


def generate_dhcp_host_reservations(hosts):
    for mac, ip in hosts:
        try:
            mac = netaddr.EUI(mac, dialect=netaddr.mac_unix_expanded)
        except netaddr.AddrFormatError:
            logger.error("Invalid MAC address %s", mac)
            continue
        try:
            ip = netaddr.IPAddress(ip)
        except netaddr.AddrFormatError:
            logger.error("Invalid IP address %s", ip)
            continue
        yield "{0},{1}\n".format(mac, ip)


def generate_dhcp_hosts_file():
    config = get_config(runtime_checks=True)
    logger.info("Generating DHCP hosts file")
    hosts = get_all_dhcp_hosts()
    file_name = config['HADES_AUTH_DNSMASQ_HOSTS_FILE']
    try:
        with open(file_name) as f:
            f.writelines(generate_dhcp_host_reservations(hosts))
    except OSError as e:
        logger.error("Error writing %s: %s", file_name, e.strerror)
