import re
import csv

# Задание 1
string_1 = r'--path.settings C:\Users\Administrator\ELK\logstash-8.11.1\config --another.key qweqweqwe'
string_2 = r'--path.settings "C:\Program Files\Elastic" --another.key qweqweqwe'
string_3 = r'--path.settings C:\Program Files\Elastic --another.key qweqweqwe'


# Задание 2:
config = """
listen tcp_public
        mode tcp
        bind 10.0.210.252:9000,10.0.210.253:9000
        bind ipv4@172.30.148.13:443 ssl crt /etc/haproxy/site.pem
        bind ipv6@:80
        bind /var/run/ssl-frontend.sock user root mode 600 accept-proxy
        bind unix@ssl-frontend.sock user root mode 600 accept-proxy
        bind 2a00:f920:192::233:80
        server tcpsrv0 192.168.1.101:9999
        use_backend dghj
"""

PATTERN_TASK_1 = re.compile(r'\S\s"?(?P<patch>\w:\\.+?)\"?\s--')
PATTERN_TASK_2 = re.compile(r'bind\s(([0-9]|ipv).+(:[0-9]{2,4}))')
FIELDNAMES = ["IP", "Type", "Port"]

# Task 1
for s in [string_1, string_2, string_3]:
    print(re.search(PATTERN_TASK_1, s).group('patch'))
print()

# Task 2
ip_list = list(map(lambda l: l[0], re.findall(PATTERN_TASK_2,
                                              config)))

print(*ip_list, sep='\n')
print()


# Task 3
stuck_ips = ip_list.pop(0).split(",")
ip_list.extend(stuck_ips)

def change_mask(ip_address):
    if ip_address.startswith("ipv4"):
        return ip_address.replace('ipv4', '0.0.0.0')
    elif ip_address.startswith("ipv6"):
        return ip_address.replace('ipv6', '::')
    else:
        return ip_address

def check_ip4_or_ip6(ip_address):
    if ip_address.startswith("ipv6") or ip_address.count(":") > 1:
        return "ipv6"
    else:
        return "ipv4"

def foo(ip_address_list):
    new_ip_list = []
    IP, TYPE, PORT = FIELDNAMES
    for ip in ip_address_list:
        ip, separator, port = ip.rpartition(":")
        new_ip_list.append({IP: change_mask(ip),
                            TYPE: check_ip4_or_ip6(ip),
                            PORT: port})
    return tuple(new_ip_list)

print(*foo(ip_list), sep="\n")