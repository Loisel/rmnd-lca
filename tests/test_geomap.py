import pytest
from rmnd_lca.geomap import Geomap

geomap = Geomap()


def test_ecoinvent_to_REMIND():
    # DE is in EUR
    assert geomap.ecoinvent_to_remind_location("DE") == "EUR"
    # CN is in CHA
    assert geomap.ecoinvent_to_remind_location("CN") == "CHA"


def test_REMIND_to_ecoinvent():
    # DE and CH are in EUR (at least for now)
    assert "DE" in geomap.remind_to_ecoinvent_location("EUR")
    assert "CH" in geomap.remind_to_ecoinvent_location("EUR")
    # Hongkong is in China (really?)
    assert "HK" in geomap.remind_to_ecoinvent_location("CHA")
    # Japan is in JPN
    assert "JP" in geomap.remind_to_ecoinvent_location("JPN")


def test_REMIND_to_ecoinvent_contained():
    # RU is intersecting EUR
    assert "RU" in geomap.remind_to_ecoinvent_location("EUR")
    # but lies not strictly within
    assert "RU" not in geomap.remind_to_ecoinvent_location(
        "EUR", contained=True)
