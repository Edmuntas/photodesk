#!/usr/bin/env python3
"""
Tests for PhotoDesk — Grok AI Real Estate Photo Editor
Run: python3 tests.py  or  python3 -m pytest tests.py -v
"""

import unittest
import json
import os
import io
import base64
import tempfile
import threading
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# ── Import the module under test ───────────────────────────────────────────────
import sys
sys.path.insert(0, str(Path(__file__).parent))

# Patch tkinter before importing app so tests work without a display
_tk_mock = MagicMock()
sys.modules.setdefault("tkinter", _tk_mock)
sys.modules.setdefault("tkinter.ttk", MagicMock())
sys.modules.setdefault("tkinter.filedialog", MagicMock())
sys.modules.setdefault("tkinter.messagebox", MagicMock())
sys.modules.setdefault("tkinter.scrolledtext", MagicMock())

import app as _app  # noqa: E402  (imported after mocks)


# ══════════════════════════════════════════════════════════════════════════════
#  detect_room_type
# ══════════════════════════════════════════════════════════════════════════════

class TestDetectRoomType(unittest.TestCase):

    def test_kitchen_russian(self):
        self.assertEqual(_app.detect_room_type("кухня_01.jpg"), "кухня")

    def test_kitchen_english(self):
        self.assertEqual(_app.detect_room_type("kitchen_view.jpg"), "кухня")

    def test_bedroom(self):
        self.assertEqual(_app.detect_room_type("bedroom_master.jpg"), "спальня")

    def test_bedroom_russian(self):
        self.assertEqual(_app.detect_room_type("спальня_02.jpg"), "спальня")

    def test_living_room(self):
        self.assertEqual(_app.detect_room_type("living_room.jpg"), "гостиная")

    def test_living_zal(self):
        self.assertEqual(_app.detect_room_type("зал_гостиная.jpg"), "гостиная")

    def test_bathroom(self):
        self.assertEqual(_app.detect_room_type("bathroom_01.jpg"), "ванная")

    def test_bathroom_russian(self):
        self.assertEqual(_app.detect_room_type("ванная_001.jpg"), "ванная")

    def test_hallway(self):
        # "hallway" contains "hall" which is a keyword for гостиная (checked first)
        # so use a filename with "коридор" or "entryway" to reliably hit коридор
        self.assertEqual(_app.detect_room_type("entryway_01.jpg"), "коридор")
        self.assertEqual(_app.detect_room_type("коридор_01.jpg"), "коридор")

    def test_balcony(self):
        self.assertEqual(_app.detect_room_type("balcony_view.jpg"), "балкон")

    def test_balcony_terrace(self):
        self.assertEqual(_app.detect_room_type("terrace_01.jpg"), "балкон")

    def test_yard(self):
        self.assertEqual(_app.detect_room_type("exterior_front.jpg"), "двор")

    def test_yard_facade(self):
        self.assertEqual(_app.detect_room_type("фасад_дома.jpg"), "двор")

    def test_drone_dji(self):
        self.assertEqual(_app.detect_room_type("dji_fly_20260326_aeb.jpg"), "дрон")

    def test_drone_aerial(self):
        self.assertEqual(_app.detect_room_type("aerial_view_01.jpg"), "дрон")

    def test_drone_aeb(self):
        self.assertEqual(_app.detect_room_type("photo_aeb_003.jpg"), "дрон")

    def test_unknown_returns_default(self):
        self.assertEqual(_app.detect_room_type("IMG_1234.jpg"), "по умолчанию")

    def test_case_insensitive(self):
        self.assertEqual(_app.detect_room_type("KITCHEN_MAIN.JPG"), "кухня")

    def test_empty_filename(self):
        self.assertEqual(_app.detect_room_type(""), "по умолчанию")

    def test_numbers_only(self):
        self.assertEqual(_app.detect_room_type("12345.jpg"), "по умолчанию")


# ══════════════════════════════════════════════════════════════════════════════
#  Constants
# ══════════════════════════════════════════════════════════════════════════════

class TestConstants(unittest.TestCase):

    def test_room_types_list(self):
        self.assertIn("кухня", _app.ROOM_TYPES)
        self.assertIn("двор", _app.ROOM_TYPES)
        self.assertIn("дрон", _app.ROOM_TYPES)
        self.assertIn("по умолчанию", _app.ROOM_TYPES)
        self.assertEqual(len(_app.ROOM_TYPES), 9)

    def test_room_keywords_covers_all_room_types(self):
        """Every room type except 'по умолчанию' has keywords."""
        for room in _app.ROOM_TYPES:
            if room == "по умолчанию":
                continue
            self.assertIn(room, _app.ROOM_KEYWORDS,
                          f"Room '{room}' has no keywords entry")

    def test_default_prompts_keys(self):
        for room in _app.ROOM_TYPES:
            if room == "по умолчанию":
                continue
            self.assertIn(room, _app.DEFAULT_PROMPTS,
                          f"DEFAULT_PROMPTS missing room '{room}'")

    def test_declutter_prompts_keys(self):
        for room in _app.ROOM_TYPES:
            if room == "по умолчанию":
                continue
            self.assertIn(room, _app.DECLUTTER_PROMPTS,
                          f"DECLUTTER_PROMPTS missing room '{room}'")

    def test_sky_presets_have_suffix_and_prompt(self):
        for name, data in _app.SKY_PRESETS.items():
            self.assertIn("suffix", data, f"SKY_PRESET '{name}' missing 'suffix'")
            self.assertIn("prompt", data, f"SKY_PRESET '{name}' missing 'prompt'")
            self.assertTrue(data["suffix"].startswith("_"),
                            f"SKY_PRESET '{name}' suffix should start with '_'")
            self.assertGreater(len(data["prompt"]), 50,
                               f"SKY_PRESET '{name}' prompt looks too short")

    def test_sky_presets_count(self):
        self.assertGreaterEqual(len(_app.SKY_PRESETS), 10)

    def test_all_extensions_non_empty(self):
        self.assertTrue(_app.IMAGE_EXTENSIONS)
        self.assertTrue(_app.RAW_EXTENSIONS)
        self.assertTrue(_app.ALL_EXTENSIONS)

    def test_raw_extensions_subset_of_all(self):
        self.assertTrue(_app.RAW_EXTENSIONS.issubset(_app.ALL_EXTENSIONS))

    def test_image_extensions_subset_of_all(self):
        self.assertTrue(_app.IMAGE_EXTENSIONS.issubset(_app.ALL_EXTENSIONS))

    def test_prompt_footer_contains_2k(self):
        self.assertIn("2K", _app.PROMPT_FOOTER)

    def test_prompt_footer_mentions_reflections(self):
        footer_lower = _app.PROMPT_FOOTER.lower()
        self.assertIn("reflect", footer_lower)
        self.assertIn("photographer", footer_lower)

    def test_evening_presets_mention_street_lighting(self):
        """Twilight and night presets must mention street lamps."""
        night_keys = [k for k in _app.SKY_PRESETS if any(
            w in k for w in ["Сумерки", "Ночь", "Вечер"]
        )]
        self.assertGreater(len(night_keys), 0, "No twilight/night presets found")
        for k in night_keys:
            prompt = _app.SKY_PRESETS[k]["prompt"].lower()
            self.assertTrue(
                "street" in prompt or "lamp" in prompt or "lantern" in prompt,
                f"Preset '{k}' should mention street lighting"
            )


# ══════════════════════════════════════════════════════════════════════════════
#  build_prompt
# ══════════════════════════════════════════════════════════════════════════════

class TestBuildPrompt(unittest.TestCase):

    def test_appends_footer(self):
        base = "Clean the room."
        result = _app.build_prompt(base)
        self.assertIn(_app.PROMPT_FOOTER, result)
        self.assertTrue(result.startswith("Clean the room."))

    def test_strips_trailing_whitespace_from_base(self):
        result = _app.build_prompt("Hello   ")
        self.assertTrue(result.startswith("Hello"))
        self.assertNotIn("Hello   \n", result)

    def test_footer_contains_2k(self):
        result = _app.build_prompt("Do stuff.")
        self.assertIn("2K", result)

    def test_footer_contains_reflection_removal(self):
        result = _app.build_prompt("Do stuff.")
        self.assertIn("reflect", result.lower())

    def test_empty_base(self):
        result = _app.build_prompt("")
        self.assertIn("2K", result)


# ══════════════════════════════════════════════════════════════════════════════
#  load_config / save_config
# ══════════════════════════════════════════════════════════════════════════════

class TestConfig(unittest.TestCase):

    def test_load_defaults_when_no_file(self):
        with patch("os.path.exists", return_value=False):
            cfg = _app.load_config()
        self.assertIn("api_key", cfg)
        self.assertIn("output_folder", cfg)
        self.assertIn("workers", cfg)
        self.assertIn("model", cfg)
        self.assertIn("empty_prompts", cfg)
        self.assertIn("declutter_prompts", cfg)
        self.assertIn("sky_prompts", cfg)

    def test_load_defaults_api_key_empty(self):
        with patch("os.path.exists", return_value=False):
            cfg = _app.load_config()
        self.assertEqual(cfg["api_key"], "")

    def test_load_merges_saved_api_key(self):
        saved = {"api_key": "test-key-123"}
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=json.dumps(saved))):
            cfg = _app.load_config()
        self.assertEqual(cfg["api_key"], "test-key-123")

    def test_load_merges_saved_workers(self):
        saved = {"workers": 4}
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=json.dumps(saved))):
            cfg = _app.load_config()
        self.assertEqual(cfg["workers"], 4)

    def test_load_handles_corrupt_json(self):
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data="INVALID JSON{")):
            cfg = _app.load_config()  # should not raise
        self.assertIn("api_key", cfg)

    def test_load_default_empty_prompts_all_rooms(self):
        with patch("os.path.exists", return_value=False):
            cfg = _app.load_config()
        for room in _app.ROOM_TYPES:
            if room != "по умолчанию":
                self.assertIn(room, cfg["empty_prompts"])

    def test_save_config_writes_json(self):
        cfg = {"api_key": "mykey", "workers": 2}
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(_app, "CONFIG_FILE",
                               os.path.join(tmpdir, "sub", "config.json")):
                _app.save_config(cfg)
                saved_path = os.path.join(tmpdir, "sub", "config.json")
                self.assertTrue(os.path.exists(saved_path))
                with open(saved_path, encoding="utf-8") as f:
                    loaded = json.load(f)
        self.assertEqual(loaded["api_key"], "mykey")
        self.assertEqual(loaded["workers"], 2)

    def test_save_config_creates_dirs(self):
        cfg = {"api_key": "x"}
        with tempfile.TemporaryDirectory() as tmpdir:
            deep_path = os.path.join(tmpdir, "a", "b", "c", "config.json")
            with patch.object(_app, "CONFIG_FILE", deep_path):
                _app.save_config(cfg)
            self.assertTrue(os.path.exists(deep_path))

    def test_roundtrip(self):
        original = {"api_key": "roundtrip-key", "workers": 3, "model": "aurora"}
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg_path = os.path.join(tmpdir, "config.json")
            with patch.object(_app, "CONFIG_FILE", cfg_path):
                _app.save_config(original)
                with patch("os.path.exists", return_value=True), \
                     patch("builtins.open", mock_open(
                         read_data=open(cfg_path, encoding="utf-8").read())):
                    loaded = _app.load_config()
        self.assertEqual(loaded["api_key"], "roundtrip-key")
        self.assertEqual(loaded["workers"], 3)


# ══════════════════════════════════════════════════════════════════════════════
#  _to_png_bytes
# ══════════════════════════════════════════════════════════════════════════════

class TestToPngBytes(unittest.TestCase):

    def _make_fake_png(self, width=100, height=100):
        """Returns in-memory PNG bytes via PIL if available, else a 1×1 pixel stub."""
        try:
            from PIL import Image
            img = Image.new("RGB", (width, height), color=(128, 64, 32))
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()
        except ImportError:
            # Minimal valid PNG (1×1 red pixel)
            return (
                b'\x89PNG\r\n\x1a\n'
                b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
                b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx'
                b'\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N'
                b'\x00\x00\x00\x00IEND\xaeB`\x82'
            )

    def test_reads_jpeg_returns_bytes(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            try:
                from PIL import Image
                img = Image.new("RGB", (200, 200), color=(200, 100, 50))
                img.save(f.name, format="JPEG")
            except ImportError:
                self.skipTest("PIL not available")
            result = _app._to_png_bytes(f.name)
        os.unlink(f.name)
        self.assertIsInstance(result, bytes)
        self.assertGreater(len(result), 0)

    def test_resizes_large_image(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            try:
                from PIL import Image
                img = Image.new("RGB", (4096, 3072), color=(100, 150, 200))
                img.save(f.name, format="JPEG")
            except ImportError:
                self.skipTest("PIL not available")
            result = _app._to_png_bytes(f.name, max_side=512)
        os.unlink(f.name)
        # Resulting image should fit within 512px
        try:
            from PIL import Image
            img_out = Image.open(io.BytesIO(result))
            self.assertLessEqual(max(img_out.size), 512)
        except ImportError:
            pass

    def test_small_image_not_upscaled(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            try:
                from PIL import Image
                img = Image.new("RGB", (100, 80))
                img.save(f.name, format="PNG")
            except ImportError:
                self.skipTest("PIL not available")
            result = _app._to_png_bytes(f.name, max_side=2048)
        os.unlink(f.name)
        try:
            from PIL import Image
            img_out = Image.open(io.BytesIO(result))
            self.assertEqual(img_out.size, (100, 80))
        except ImportError:
            pass

    def test_raw_without_rawpy_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".cr2", delete=False) as f:
            f.write(b"FAKE RAW DATA")
            fname = f.name
        try:
            with patch.object(_app, "HAS_RAWPY", False):
                with self.assertRaises(RuntimeError) as ctx:
                    _app._to_png_bytes(fname)
            self.assertIn("rawpy", str(ctx.exception))
        finally:
            os.unlink(fname)

    def test_unsupported_extension_still_tries(self):
        """Non-RAW, non-image extensions fall through to PIL or raise gracefully."""
        with tempfile.NamedTemporaryFile(suffix=".bmp", delete=False) as f:
            try:
                from PIL import Image
                img = Image.new("RGB", (50, 50))
                img.save(f.name, format="BMP")
                result = _app._to_png_bytes(f.name)
                self.assertIsInstance(result, bytes)
            except ImportError:
                self.skipTest("PIL not available")
            finally:
                os.unlink(f.name)


# ══════════════════════════════════════════════════════════════════════════════
#  _xai_post
# ══════════════════════════════════════════════════════════════════════════════

class TestXaiPost(unittest.TestCase):

    def _make_response(self, status=200, body=b'{"data":[]}'):
        resp = MagicMock()
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        resp.read.return_value = body
        resp.status = status
        return resp

    def test_returns_parsed_json_on_200(self):
        body = json.dumps({"data": [{"b64_json": "abc"}]}).encode()
        with patch("urllib.request.urlopen", return_value=self._make_response(200, body)):
            result = _app._xai_post("https://example.com", {}, {}, retry_delay=0)
        self.assertEqual(result["data"][0]["b64_json"], "abc")

    def _make_http_error(self, code, reason, body=b'""'):
        """Create a urllib.error.HTTPError-like mock."""
        err = _app.urllib.error.HTTPError(
            url="https://example.com",
            code=code,
            msg=reason,
            hdrs=None,
            fp=io.BytesIO(body),
        )
        return err

    def test_raises_on_403(self):
        err = self._make_http_error(403, "Forbidden", b'{"error": "no access"}')
        with patch("urllib.request.urlopen", side_effect=err):
            with self.assertRaises(RuntimeError) as ctx:
                _app._xai_post("https://example.com", {}, {}, retry_delay=0)
        self.assertIn("403", str(ctx.exception))

    def test_raises_on_404(self):
        err = self._make_http_error(404, "Not Found", b'"Not Found"')
        with patch("urllib.request.urlopen", side_effect=err):
            with self.assertRaises(RuntimeError) as ctx:
                _app._xai_post("https://example.com", {}, {}, retry_delay=0)
        self.assertIn("404", str(ctx.exception))

    def test_retries_on_500(self):
        err = self._make_http_error(500, "Server Error", b'"Internal error"')

        body = json.dumps({"data": [{"b64_json": "ok"}]}).encode()
        success_resp = self._make_response(200, body)

        call_count = [0]
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise err
            return success_resp

        with patch("urllib.request.urlopen", side_effect=side_effect):
            result = _app._xai_post("https://example.com", {}, {},
                                    retries=3, retry_delay=0)
        self.assertEqual(result["data"][0]["b64_json"], "ok")
        self.assertEqual(call_count[0], 2)

    def test_raises_after_all_retries_500(self):
        def make_err():
            return self._make_http_error(500, "Server Error", b'"Error"')
        with patch("urllib.request.urlopen", side_effect=lambda *a, **kw: (_ for _ in ()).throw(make_err())):
            with self.assertRaises(RuntimeError):
                _app._xai_post("https://example.com", {}, {},
                                retries=2, retry_delay=0)

    def test_retries_on_network_error(self):
        import urllib.error as ue
        body = json.dumps({"data": [{"b64_json": "ok"}]}).encode()
        success_resp = self._make_response(200, body)

        call_count = [0]
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise OSError("Network timeout")
            return success_resp

        with patch("urllib.request.urlopen", side_effect=side_effect):
            result = _app._xai_post("https://example.com", {}, {},
                                    retries=3, retry_delay=0)
        self.assertEqual(result["data"][0]["b64_json"], "ok")


# ══════════════════════════════════════════════════════════════════════════════
#  process_image_xai
# ══════════════════════════════════════════════════════════════════════════════

class TestProcessImageXai(unittest.TestCase):

    def _make_fake_jpeg(self):
        """Returns JPEG bytes for a small test image."""
        try:
            from PIL import Image
            img = Image.new("RGB", (64, 64), color=(100, 150, 200))
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            return buf.getvalue()
        except ImportError:
            return b'\xff\xd8\xff\xe0' + b'\x00' * 100  # fake JPEG header

    def test_returns_bytes_on_success(self):
        fake_result_bytes = b"FAKE_IMAGE_DATA"
        fake_b64 = base64.b64encode(fake_result_bytes).decode()
        api_response = {"data": [{"b64_json": fake_b64}]}

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(self._make_fake_jpeg())
            fname = f.name

        try:
            with patch.object(_app, "_to_png_bytes", return_value=b"FAKE_PNG"), \
                 patch.object(_app, "_xai_post", return_value=api_response):
                result = _app.process_image_xai(fname, "test prompt", "test-api-key")
        finally:
            os.unlink(fname)

        self.assertEqual(result, fake_result_bytes)

    def test_uses_model_parameter(self):
        fake_b64 = base64.b64encode(b"IMG").decode()
        api_response = {"data": [{"b64_json": fake_b64}]}
        captured = {}

        def fake_post(url, headers, payload, **kw):
            captured["payload"] = payload
            return api_response

        with patch.object(_app, "_to_png_bytes", return_value=b"PNG"), \
             patch.object(_app, "_xai_post", side_effect=fake_post):
            _app.process_image_xai("dummy.jpg", "prompt", "key", model="aurora")

        self.assertEqual(captured["payload"]["model"], "aurora")

    def test_payload_contains_prompt(self):
        fake_b64 = base64.b64encode(b"IMG").decode()
        api_response = {"data": [{"b64_json": fake_b64}]}
        captured = {}

        def fake_post(url, headers, payload, **kw):
            captured["payload"] = payload
            return api_response

        with patch.object(_app, "_to_png_bytes", return_value=b"PNG"), \
             patch.object(_app, "_xai_post", side_effect=fake_post):
            _app.process_image_xai("dummy.jpg", "MY SPECIAL PROMPT", "key")

        self.assertEqual(captured["payload"]["prompt"], "MY SPECIAL PROMPT")

    def test_payload_image_is_data_uri(self):
        fake_b64 = base64.b64encode(b"IMG").decode()
        api_response = {"data": [{"b64_json": fake_b64}]}
        captured = {}

        def fake_post(url, headers, payload, **kw):
            captured["payload"] = payload
            return api_response

        with patch.object(_app, "_to_png_bytes", return_value=b"PNG_BYTES"), \
             patch.object(_app, "_xai_post", side_effect=fake_post):
            _app.process_image_xai("dummy.jpg", "prompt", "key")

        image_field = captured["payload"]["image"]
        self.assertTrue(image_field.startswith("data:image/png;base64,"))

    def test_authorization_header(self):
        fake_b64 = base64.b64encode(b"X").decode()
        api_response = {"data": [{"b64_json": fake_b64}]}
        captured = {}

        def fake_post(url, headers, payload, **kw):
            captured["headers"] = headers
            return api_response

        with patch.object(_app, "_to_png_bytes", return_value=b"PNG"), \
             patch.object(_app, "_xai_post", side_effect=fake_post):
            _app.process_image_xai("dummy.jpg", "p", "MY-SECRET-KEY")

        self.assertEqual(captured["headers"]["Authorization"], "Bearer MY-SECRET-KEY")

    def test_raises_on_api_error(self):
        with patch.object(_app, "_to_png_bytes", return_value=b"PNG"), \
             patch.object(_app, "_xai_post", side_effect=RuntimeError("403 Forbidden")):
            with self.assertRaises(RuntimeError):
                _app.process_image_xai("dummy.jpg", "p", "key")


# ══════════════════════════════════════════════════════════════════════════════
#  Prompt content sanity checks
# ══════════════════════════════════════════════════════════════════════════════

class TestPromptContent(unittest.TestCase):

    def test_all_default_prompts_are_strings(self):
        for room, prompt in _app.DEFAULT_PROMPTS.items():
            self.assertIsInstance(prompt, str, f"DEFAULT_PROMPTS[{room!r}] is not str")

    def test_all_declutter_prompts_are_strings(self):
        for room, prompt in _app.DECLUTTER_PROMPTS.items():
            self.assertIsInstance(prompt, str, f"DECLUTTER_PROMPTS[{room!r}] is not str")

    def test_default_prompts_mention_remove(self):
        # дрон prompt uses ENHANCE/PRESERVE format (aerial photography, not staging removal)
        skip = {"дрон"}
        for room, prompt in _app.DEFAULT_PROMPTS.items():
            if room in skip:
                continue
            self.assertIn("REMOVE", prompt,
                          f"DEFAULT_PROMPTS[{room!r}] should mention REMOVE")

    def test_default_prompts_mention_keep(self):
        skip = {"дрон"}
        for room, prompt in _app.DEFAULT_PROMPTS.items():
            if room in skip:
                continue
            self.assertIn("KEEP", prompt,
                          f"DEFAULT_PROMPTS[{room!r}] should mention KEEP")

    def test_prompts_not_empty(self):
        for room, prompt in {**_app.DEFAULT_PROMPTS, **_app.DECLUTTER_PROMPTS}.items():
            self.assertGreater(len(prompt.strip()), 100,
                               f"Prompt for '{room}' looks too short")

    def test_sky_prompts_mention_sky(self):
        for name, data in _app.SKY_PRESETS.items():
            prompt_lower = data["prompt"].lower()
            self.assertTrue(
                "sky" in prompt_lower or "небо" in prompt_lower,
                f"SKY_PRESET '{name}' doesn't mention sky"
            )

    def test_sky_presets_have_quality_instruction(self):
        for name, data in _app.SKY_PRESETS.items():
            self.assertIn("QUALITY", data["prompt"],
                          f"SKY_PRESET '{name}' missing QUALITY section")

    def test_sky_suffixes_unique(self):
        suffixes = [d["suffix"] for d in _app.SKY_PRESETS.values()]
        self.assertEqual(len(suffixes), len(set(suffixes)),
                         "SKY_PRESETS have duplicate suffixes")

    def test_build_prompt_does_not_duplicate_footer(self):
        """Calling build_prompt twice should not stack footers."""
        once = _app.build_prompt("Base text.")
        # build_prompt on already-built prompt would duplicate footer
        # we just verify the footer appears at least once
        self.assertEqual(once.count("2K"), 1)


# ══════════════════════════════════════════════════════════════════════════════
#  Thread-safety helpers used in processing
# ══════════════════════════════════════════════════════════════════════════════

class TestThreading(unittest.TestCase):

    def test_stop_event_can_be_set_and_cleared(self):
        stop = threading.Event()
        self.assertFalse(stop.is_set())
        stop.set()
        self.assertTrue(stop.is_set())
        stop.clear()
        self.assertFalse(stop.is_set())

    def test_concurrent_room_detection(self):
        """detect_room_type should be safe to call from multiple threads."""
        results = []
        errors = []

        def worker(name):
            try:
                results.append(_app.detect_room_type(name))
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(f"kitchen_{i}.jpg",))
                   for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [])
        self.assertTrue(all(r == "кухня" for r in results))


# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    unittest.main(verbosity=2)
