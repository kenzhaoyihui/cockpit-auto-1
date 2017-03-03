import time
import pytest
from selenium import webdriver
from pages.login_page import LoginPage
from pages.rhvh41.hosted_engine_page import HePage
from fabric.api import env, run, settings
from utils.helpers import RhevmAction
from conf import *


host_ip = HOST_IP
host_user = HOST_USER
host_password = HOST_PASSWORD
another_host = SECOND_HOST
another_password = SECOND_PASSWORD
ROOT_URI = "https://" + host_ip + ":9090"

env.host_string = host_user + '@' + host_ip
env.password = host_password

vm_fqdn = VM_FQDN
vm_ip = VM_IP
vm_password = VM_PASSWORD
engine_password = ENGINE_PASSWORD
second_nfs_path = SECOND_NFS_PATH  # Be added to hosted engine
second_host_ip = SECOND_HOST       # Second host to run hosted engine
second_password = SECOND_PASSWORD


@pytest.fixture(autouse=True)
def _environment(request):
    cmd = "rpm -qa|grep cockpit-ovirt"
    cockpit_ovirt_version = run(cmd)

    # Check whether the host is rhvh or regular host 
    cmd = "rpm -q imgbased"
    result = run(cmd)
    if result.failed:
        cmd = "cat /etc/redhat-release"
        redhat_release = run(cmd)
        request.config._environment.append(('redhat-release', redhat_release))
    else:
        cmd_imgbase = "imgbase w"
        output_imgbase = run(cmd_imgbase)
        rhvh_version = output_imgbase.split()[-1].split('+')[0]
        request.config._environment.append(('rhvh-version', rhvh_version))

    request.config._environment.append(('cockpit-ovirt', cockpit_ovirt_version))


@pytest.fixture(scope="module")
def firefox(request):
    driver = webdriver.Firefox()
    driver.implicitly_wait(20)
    root_uri = getattr(request.module, "ROOT_URI", None)
    driver.root_uri = root_uri
    yield driver
    driver.close()


def test_login(firefox):
    login_page = LoginPage(firefox)
    login_page.basic_check_elements_exists()
    login_page.login_with_credential(host_user, host_password)


def test_18669(firefox):
    """
    RHEVM-18669
        Hosted Engine status can be checked after configuration
    """
    he_page = HePage(firefox)
    he_page.check_engine_status()


def test_18670(firefox):
    """
    RHEVM-18670
        Check the vm still up after reboot node
    """
    he_page = HePage(firefox)

    # Check engine status
    he_page.check_engine_status()

    # Check VM state
    he_page.check_vm_status()



def test_18671(firefox):
    """
    RHEVM-18671
        Reboot RHVH after finished configure hosted engine
    """
    he_page = HePage(firefox)

    # Check engine status
    he_page.check_engine_status()
    time.sleep(2)

    # Check three maintenance buttons exist
    he_page.check_three_buttons()


def test_18672(firefox):
    """
    RHEVM-18672
        Verify hosted-engine cockpit show correct info after setup hosted engine with OVA
    """
    he_page = HePage(firefox)

    # Check engine status
    he_page.check_engine_status()

    # Check three maintenance buttons exist
    he_page.check_he_running_on_host(host_ip)

    # Check vm statues
    he_page.check_vm_status()


def test_18668(firefox):
    """
    RHEVM-18668
        Setup additional host
    """
    another_hostname = "cockpit-he"
    he_page = HePage(firefox)
    he_page.add_host_to_rhvm(
        vm_fqdn,
        another_host,
        another_hostname,
        another_password)
    he_page.check_additonal_host(vm_fqdn, another_hostname)
    he_page.remove_host_from_rhvm(vm_fqdn, another_hostname)


def test_18684(firefox):
    """
    RHEVM-18684
        Check if there are a large number of redundant log generation in /var/log/messages
    """
    pass


def test_18685(firefox):
    """
    RHEVM-18685
        Check there is no Hosted Engine passwords are saved in the logs as clear text
    """
    # Find the hosted engine setup log
    cmd = "find /var/log -type f |grep ovirt-hosted-engine-setup-.*.log"
    output = run(cmd)

    # Find the line contains "Enter engine admin password"
    cmd = "grep 'Enter engine admin password' %s" % output
    output = run(cmd)
    password = output.split(':')[-1]

    assert password != engine_password, "Hosted engine password is saved in the logs as clear text"
