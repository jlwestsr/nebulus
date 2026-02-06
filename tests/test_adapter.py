"""Tests for the PrimeAdapter."""

from pathlib import Path

from nebulus_core.platform.base import PlatformAdapter

from nebulus_prime.adapter import PrimeAdapter


class TestPrimeAdapter:
    def test_satisfies_protocol(self):
        adapter = PrimeAdapter()
        assert isinstance(adapter, PlatformAdapter)

    def test_platform_name(self):
        assert PrimeAdapter().platform_name == "prime"

    def test_llm_base_url(self):
        adapter = PrimeAdapter()
        assert "http" in adapter.llm_base_url

    def test_chroma_settings(self):
        adapter = PrimeAdapter()
        settings = adapter.chroma_settings
        assert settings["mode"] == "http"
        assert "host" in settings
        assert "port" in settings

    def test_default_model(self):
        adapter = PrimeAdapter()
        assert isinstance(adapter.default_model, str)
        assert len(adapter.default_model) > 0

    def test_data_dir(self):
        adapter = PrimeAdapter()
        assert isinstance(adapter.data_dir, Path)

    def test_services(self):
        adapter = PrimeAdapter()
        assert isinstance(adapter.services, list)
        assert len(adapter.services) > 0
