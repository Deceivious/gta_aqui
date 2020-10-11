import requests as r
import re
import ipaddress


def get_take3_ips():
    res = r.get("https://ipinfo.io/AS46555")
    res = str(res.content)
    links = re.findall('/AS46555/(.*?)(?:\'|\")', res) + ["185.56.64.0/22"]
    links = [str(i) for link in links for i in list(ipaddress.IPv4Network(link))]
    return links
