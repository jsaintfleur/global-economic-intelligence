import io
import json
import tempfile
import unittest
import urllib.error
import pytest
from unittest.mock import patch
from pathlib import Path

from gei.adapters import WorldBankAdapter


class Response(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *args): return False


class AdapterTests(unittest.TestCase):
    @pytest.mark.decision("D-006")
    @pytest.mark.test_id("TEST-T-001")
    def test_raw_snapshot_is_preserved_with_checksum(self):
        payload = [{"pages":1},[{"countryiso3code":"USA","date":"2024","value":1}]]
        with tempfile.TemporaryDirectory() as directory:
            adapter = WorldBankAdapter(Path(directory), opener=lambda *_args,**_kwargs: Response(json.dumps(payload).encode()))
            result = adapter.fetch_indicator("TEST",2024,2024,"2026-01-02T00:00:00Z")
            self.assertEqual(result.snapshot.record_count, 1)
            self.assertTrue((Path(directory)/"2026-01-02"/"TEST_2024_2024.json").exists())
            self.assertEqual(len(result.snapshot.checksum_sha256),64)

    def test_cache_avoids_network(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/"2026-01-02"/"TEST_2024_2024.json";target.parent.mkdir();target.write_text("[]")
            adapter=WorldBankAdapter(Path(directory),opener=lambda *_a,**_k: self.fail("network called"))
            result=adapter.fetch_indicator("TEST",2024,2024,"2026-01-02T00:00:00Z")
            self.assertIn("cache_hit:dated_snapshot",result.warnings)

    def test_schema_change_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            adapter=WorldBankAdapter(Path(directory),opener=lambda *_a,**_k: Response(b'{}'))
            with self.assertRaises(ValueError): adapter.fetch_indicator("TEST",2024,2024,"2026-01-02T00:00:00Z")

    def test_rate_limit_and_server_error_are_retried_without_slow_test(self):
        for status in (429,500):
            calls=[]
            def opener(url,timeout):
                calls.append(url)
                if len(calls)<3:raise urllib.error.HTTPError(url,status,"failure",{},None)
                return Response(b'[{"pages":1},[]]')
            with tempfile.TemporaryDirectory() as directory,patch("gei.adapters.time.sleep"):
                result=WorldBankAdapter(Path(directory),opener=opener).fetch_indicator("TEST",2024,2024,"2026-01-02T00:00:00Z")
                self.assertEqual(len(calls),3);self.assertEqual(result.records,[])

    def test_timeout_connection_failure_and_invalid_json_surface_after_retries(self):
        failures=[TimeoutError("timeout"),urllib.error.URLError("connection")]
        for failure in failures:
            with tempfile.TemporaryDirectory() as directory,patch("gei.adapters.time.sleep"):
                adapter=WorldBankAdapter(Path(directory),retries=2,opener=lambda *_a,**_k:(_ for _ in ()).throw(failure))
                with self.assertRaises(RuntimeError):adapter.fetch_indicator("TEST",2024,2024,"2026-01-02T00:00:00Z")
        with tempfile.TemporaryDirectory() as directory,patch("gei.adapters.time.sleep"):
            adapter=WorldBankAdapter(Path(directory),retries=2,opener=lambda *_a,**_k:Response(b'not-json'))
            with self.assertRaises(RuntimeError):adapter.fetch_indicator("TEST",2024,2024,"2026-01-02T00:00:00Z")

    def test_partial_and_empty_schema_are_rejected(self):
        for raw in (b'[]',b'[{"pages":1}]',b'{}'):
            with tempfile.TemporaryDirectory() as directory:
                adapter=WorldBankAdapter(Path(directory),opener=lambda *_a,_raw=raw,**_k:Response(_raw))
                with self.assertRaises(ValueError):adapter.fetch_indicator("TEST",2024,2024,"2026-01-02T00:00:00Z")

    def test_unsafe_indicator_filename_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            adapter=WorldBankAdapter(Path(directory),opener=lambda *_a,**_k:Response(b'[{"pages":1},[]]'))
            with self.assertRaises(ValueError):adapter.fetch_indicator("../secret",2024,2024,"2026-01-02T00:00:00Z")


if __name__ == "__main__": unittest.main()
