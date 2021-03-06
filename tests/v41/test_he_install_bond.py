import pytest
from pages.v41.he_install import *
from fabric.api import env, run, settings
from conf import *

host_ip = HOST_IP
host_user = HOST_USER
host_password = HOST_PASSWORD

env.host_string = host_user + '@' + host_ip
env.password = host_password

nfs_ip = NFS_IP
nfs_password = NFS_PASSWORD
nfs_storage_path = HE_INSTALL_NFS
rhvm_appliance_path = RHVM_APPLIANCE_PATH
vm_mac = HE_VM_MAC
vm_fqdn = HE_VM_FQDN
vm_ip = HE_VM_IP
vm_password = HE_VM_PASSWORD
engine_password = ENGINE_PASSWORD
auto_answer = AUTO_ANSWER


@pytest.fixture(scope="session", autouse=True)
def _environment(request):
    with settings(warn_only=True):
        cmd = "rpm -qa|grep cockpit-ovirt"
        cockpit_ovirt_version = run(cmd)

        cmd = "rpm -q imgbased"
        result = run(cmd)
        if result.failed:
            cmd = "cat /etc/redhat-release"
            redhat_release = run(cmd)
            request.config._environment.append((
                'redhat-release', redhat_release))
        else:
            cmd_imgbase = "imgbase w"
            output_imgbase = run(cmd_imgbase)
            rhvh_version = output_imgbase.split()[-1].split('+')[0]
            request.config._environment.append(('rhvh-version', rhvh_version))

        request.config._environment.append((
            'cockpit-ovirt', cockpit_ovirt_version))


@pytest.fixture(scope="module")
def firefox(request):
    pass


def test_18674(firefox):
    """
    Purpose:
        RHEVM-18667
        Setup hosted engine through ova with bond as network
    """
    # Get the bond device
    with settings(warn_only=True):
        cmd = "ls /etc/sysconfig/network-scripts | egrep 'ifcfg-bond[0-9]$' | awk -F '-' '{print $2}'"
        ret = run(cmd)
    if ret.failed:
        assert 0, "Not support this case since no bond device found"
    he_nic = ret

    # get ip addr
    with settings(warn_only=True):
        cmd = "ip -f inet addr show %s|grep inet|awk '{print $2}'|awk -F'/' '{print $1}'" % he_nic
        ret = run(cmd)
    if ret.failed:
        assert 0, "Not support this case since bond has no ip address configured"

    host_dict = {'host_ip': host_ip,
    'host_user': host_user,
    'host_password': host_password}

    nfs_dict = {
    'nfs_ip': nfs_ip,
    'nfs_password': nfs_password,
    'nfs_path': nfs_storage_path}

    install_dict = {
    'rhvm_appliance_path': rhvm_appliance_path,
    'he_nic': he_nic}

    vm_dict = {
    'vm_mac': vm_mac,
    'vm_fqdn': vm_fqdn,
    'vm_ip': vm_ip,
    'vm_password': vm_password,
    'engine_password': engine_password,
    'auto_answer': auto_answer
    }

    he_install(host_dict, nfs_dict, install_dict, vm_dict)

    # Check the hosted engine is deployed
    check_he_is_deployed(host_ip, host_user, host_password)
