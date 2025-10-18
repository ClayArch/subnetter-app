import pytest
import ipaddress
from subnetter.core.calculator import (
    parse_ip_and_mask,
    compute_subnet,
    wildcard_from_netmask,
)


class TestParseIpAndMask:
    def test_parse_cidr_notation(self):
        ip, prefix = parse_ip_and_mask("192.168.1.0/24")
        assert str(ip) == "192.168.1.0"
        assert prefix == 24

    def test_parse_ip_and_dotted_mask(self):
        ip, prefix = parse_ip_and_mask("192.168.1.0", "255.255.255.0")
        assert str(ip) == "192.168.1.0"
        assert prefix == 24

    def test_parse_ip_and_slash_mask(self):
        ip, prefix = parse_ip_and_mask("10.0.0.0", "/8")
        assert str(ip) == "10.0.0.0"
        assert prefix == 8

    def test_missing_mask_raises_error(self):
        with pytest.raises(ValueError):
            parse_ip_and_mask("192.168.1.0")

    def test_invalid_cidr_raises_error(self):
        with pytest.raises(ValueError):
            parse_ip_and_mask("192.168.1.0", "/33")

    def test_ipv6_raises_error(self):
        with pytest.raises(ValueError):
            parse_ip_and_mask("2001:db8::/32")


class TestWildcardFromNetmask:
    def test_wildcard_24(self):
        mask = ipaddress.IPv4Address("255.255.255.0")
        wildcard = wildcard_from_netmask(mask)
        assert str(wildcard) == "0.0.0.255"

    def test_wildcard_16(self):
        mask = ipaddress.IPv4Address("255.255.0.0")
        wildcard = wildcard_from_netmask(mask)
        assert str(wildcard) == "0.0.255.255"

    def test_wildcard_32(self):
        mask = ipaddress.IPv4Address("255.255.255.255")
        wildcard = wildcard_from_netmask(mask)
        assert str(wildcard) == "0.0.0.0"


class TestComputeSubnet:
    def test_compute_subnet_24(self):
        ip = ipaddress.IPv4Address("192.168.1.0")
        info = compute_subnet(ip, 24)
        assert info.network == "192.168.1.0"
        assert info.broadcast == "192.168.1.255"
        assert info.first_host == "192.168.1.1"
        assert info.last_host == "192.168.1.254"
        assert info.total_hosts == 256
        assert info.usable_hosts == 254

    def test_compute_subnet_30(self):
        ip = ipaddress.IPv4Address("10.0.0.0")
        info = compute_subnet(ip, 30)
        assert info.total_hosts == 4
        assert info.usable_hosts == 2
        assert info.first_host == "10.0.0.1"
        assert info.last_host == "10.0.0.2"

    def test_compute_subnet_31(self):
        ip = ipaddress.IPv4Address("172.16.0.0")
        info = compute_subnet(ip, 31)
        assert info.total_hosts == 2
        assert info.usable_hosts == 2  # RFC 3021

    def test_compute_subnet_32(self):
        ip = ipaddress.IPv4Address("8.8.8.8")
        info = compute_subnet(ip, 32)
        assert info.total_hosts == 1
        assert info.usable_hosts == 1
        assert info.first_host == "8.8.8.8"