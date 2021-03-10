import json
import os

from nornir_netbox.plugins.inventory.netbox import NBInventory
from nornir_netbox.plugins.inventory.netbox import NetBoxInventory2

# We need import below to load fixtures
import pytest  # noqa


BASE_PATH = os.path.dirname(__file__)
VERSIONS = ["2.3.5", "2.8.9"]


def _create_mock(requests_mock, pagination, version, application, resource, **kwargs):
    """initialises mock objects for testcase"""
    if not pagination:
        with open(f"{BASE_PATH}/mocked/{version}/{resource}.json", "r") as f:
            requests_mock.get(
                f"http://localhost:8080/api/{application}/{resource}/?limit=0",
                json=json.load(f),
                headers={"Content-type": "application/json"},
            )
    else:
        for offset in range(3):
            with open(
                f"{BASE_PATH}/mocked/{version}/{resource}-{offset}.json", "r"
            ) as f:
                url = f"http://localhost:8080/api/{application}/{resource}/?limit=0"
                requests_mock.get(
                    f"{url}&offset={offset}" if offset else url,
                    json=json.load(f),
                    headers={"Content-type": "application/json"},
                )


def get_inv(requests_mock, plugin, pagination, version, **kwargs):

    _create_mock(requests_mock, pagination, version, "dcim", "devices")
    _create_mock(requests_mock, False, version, "dcim", "platforms")
    if kwargs.get("include_vms", None):
        _create_mock(
            requests_mock, pagination, version, "virtualization", "virtual-machines"
        )

    return plugin(**kwargs).load()


class TestNBInventory(object):
    plugin = NBInventory

    @pytest.mark.parametrize("version", VERSIONS)
    def test_inventory(self, requests_mock, version):
        inv = get_inv(requests_mock, self.plugin, False, version)
        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/expected.json", "r"
        ) as f:
            expected = json.load(f)
        assert expected == inv.dict()

    @pytest.mark.parametrize("version", VERSIONS)
    def test_inventory_pagination(self, requests_mock, version):
        inv = get_inv(requests_mock, self.plugin, True, version)
        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/expected.json", "r"
        ) as f:
            expected = json.load(f)
        assert expected == inv.dict()


class TestNetBoxInventory2(TestNBInventory):
    plugin = NetBoxInventory2

    # only on NetBoxInventory2 and NetBox 2.8.9
    @pytest.mark.parametrize("version", ["2.8.9"])
    def test_inventory_include_vms(self, requests_mock, version):
        inv = get_inv(requests_mock, self.plugin, False, version, include_vms=True)
        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/vms-expected.json", "r"
        ) as f:
            expected = json.load(f)
        assert expected == inv.dict()

    @pytest.mark.parametrize("version", ["2.8.9"])
    def test_inventory_include_vms_pagination(self, requests_mock, version):
        inv = get_inv(requests_mock, self.plugin, True, version, include_vms=True)
        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/vms-expected.json", "r"
        ) as f:
            expected = json.load(f)
        assert expected == inv.dict()

    @pytest.mark.parametrize("version", ["2.8.9"])
    def test_inventory_use_platform_slug(self, requests_mock, version):
        inv = get_inv(
            requests_mock, self.plugin, False, version, use_platform_slug=True
        )
        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/expected_use_platform_slug.json",
            "r",
        ) as f:
            expected = json.load(f)
        assert expected == inv.dict()

    @pytest.mark.parametrize("version", ["2.8.9"])
    def test_inventory_use_platform_slug_include_vms(self, requests_mock, version):
        inv = get_inv(
            requests_mock,
            self.plugin,
            False,
            version,
            use_platform_slug=True,
            include_vms=True,
        )
        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/vms-expected_use_platform_slug.json",
            "r",
        ) as f:
            expected = json.load(f)
        assert expected == inv.dict()

    @pytest.mark.parametrize("version", ["2.8.9"])
    def test_inventory_use_napalm(self, requests_mock, version):
        inv = get_inv(
            requests_mock, self.plugin, False, version, use_napalm=True
        )
        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/expected_use_napalm.json",
            "r",
        ) as f:
            expected = json.load(f)
        assert expected == inv.dict()