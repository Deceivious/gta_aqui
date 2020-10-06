import subprocess
from subprocess import PIPE
from ipaddress import ip_address

from server.users_module import get_users


def update_rules():
    """ Updates inbound and outgoing rules. """

    # Get whitelisted users
    whitelist = get_users()
    # Extract whitelisted IP
    whitelist = sorted([i["registered_ip"] for i in whitelist if "registered_ip" in i])
    # Generate black listed IP
    whitelist_lower = ["0.0.0.0"] + [str(ip_address(i) - 1) for i in whitelist]
    whitelist_upper = [str(ip_address(i) + 1) for i in whitelist] + ["255.255.255.255"]
    blacklist = list(zip(whitelist_lower, whitelist_upper))
    blacklists = ["-".join(i) for i in blacklist]

    for idx, localport in enumerate(blacklists):
        rule_name = f"AQUI_{idx}"

        # Add inbound rules
        p = subprocess.Popen(
            [
                "powershell",
                f'New-NetFirewallRule -DisplayName {rule_name}_in -Direction Inbound -Action Block '
                f'-Protocol UDP -LocalPort 6672 -LocalAddress Any -RemoteAddress {localport}'],
            shell=True, stdout=PIPE, stderr=PIPE
        )

        # Add outbound rules
        p = subprocess.Popen(
            [
                "powershell",
                f'New-NetFirewallRule -DisplayName {rule_name}_out -Direction Outbound -Action Block '
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

    # Check to ensure the code is not deleting any other rules
    if not rule_name.startswith("AQUI_"):
        raise Exception("Non AQUI rule")

    # Delete specified rule
    p = subprocess.Popen(
        ["powershell", f"netsh advfirewall firewall delete rule name={rule_name}"],
        shell=True, stdout=PIPE, stderr=PIPE
    )
    output, output_error = p.communicate()
    return str(output, "utf8") + "<br>"


def get_rules():
    """Get all rules"""

    # Get all rules
    p = subprocess.Popen(
        ["powershell", "netsh advfirewall firewall show rule status=enabled name=all"], shell=True, stdout=PIPE,
        stderr=PIPE)
    output, output_err = p.communicate()

    # Format rules into python dict
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

    # Filter out any rules that are not related to application
    data_list = [i for i in data_list if i["Rule Name"].startswith("AQUI_")]
    return data_list


def delete_all_rules():
    """ Deletes all rules associated with the application."""
    all_rules = get_rules()
    for rule in all_rules:
        delete_rule(rule["Rule Name"])
