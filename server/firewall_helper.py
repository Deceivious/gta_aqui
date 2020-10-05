import subprocess, ctypes, sys
from subprocess import PIPE
from ipaddress import ip_address

from server.users_module import get_users


def check_admin():
    """ Force to start application with admin rights """
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except AttributeError:
        is_admin = False
    if not is_admin:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)


def update_rules():
    whitelist = get_users()
    whitelist = sorted([i["registered_ip"] for i in whitelist if "registered_ip" in i])
    whitelist_lower = ["0.0.0.0"] + [str(ip_address(i) - 1) for i in whitelist]
    whitelist_upper = [str(ip_address(i) + 1) for i in whitelist] + ["255.255.255.255"]
    blacklist = list(zip(whitelist_lower, whitelist_upper))
    blacklists = ["-".join(i) for i in blacklist]
    for idx, localport in enumerate(blacklists):
        rule_name = f"AQUI_{idx}"
        p = subprocess.Popen(
            [
                "powershell",
                f'New-NetFirewallRule -DisplayName {rule_name} -Direction Inbound -Action Block '
                f'-Protocol UDP -LocalPort 6672 -LocalAddress Any -RemoteAddress {localport}'],
            shell=True, stdout=PIPE, stderr=PIPE
        )


def add_rule(user_name, remoteip, action='block', localport='6672'):
    """ Add rule to Windows Firewall """
    rule_name = f"AQUI_{user_name}"
    p = subprocess.Popen(
        [
            "powershell",
            f"netsh advfirewall firewall add rule name={rule_name} dir=in action={action} remoteip={remoteip} localport ={localport} protocol=UDP"],
        shell=True, stdout=PIPE, stderr=PIPE
    )
    return p.communicate()[0]


def delete_rule(rule_name):
    """Delete specified rule"""

    if not rule_name.startswith("AQUI_"):
        raise Exception("Non AQUI rule")
    p = subprocess.Popen(
        ["powershell", f"netsh advfirewall firewall delete rule name={rule_name}"],
        shell=True, stdout=PIPE, stderr=PIPE
    )
    output, output_error = p.communicate()
    return str(output, "utf8") + "<br>"


def get_rules():
    """Get all rules"""
    p = subprocess.Popen(
        ["powershell", "netsh advfirewall firewall show rule status=enabled name=all"], shell=True, stdout=PIPE,
        stderr=PIPE)
    output, output_err = p.communicate()
    output = str(output, "utf8").replace("\r", "")
    output = output.split("\n")
    data_dict = None
    data_list = []
    for col in output:
        if ":" not in col:
            continue
        k, v = col.split(":", 1)
        k = k.strip()
        v = v.strip()
        if k == "Rule Name":
            if data_dict is not None:
                data_list.append(data_dict)
            data_dict = {}
        data_dict[k] = v
    data_list = [i for i in data_list if i["Rule Name"].startswith("AQUI_")]
    return data_list


def delete_all_rules():
    all_rules = get_rules()
    for rule in all_rules:
        delete_rule(rule["Rule Name"])


