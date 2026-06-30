import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

import pipeline_config
import curator as curator_module
import researcher as researcher_module
import writer as writer_module
from curator import Curator
from delivery import TelegramDelivery
from pipeline_config import (
    PipelineConfigError,
    load_delivery_config,
    load_pipeline,
    profile_ledger_path,
    resolve_profile_name,
)
from researcher import Researcher
from writer import Writer


class PipelineConfigTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temporary_directory.name)
        self.config_path = self.project_root / "config" / "pipeline.yaml"
        self.config_path.parent.mkdir()
        for relative_path in (
            "prompts/researchers/current_brief.md",
            "prompts/researchers/gemini_brief.md",
            "prompts/researchers/openai_brief.md",
            "prompts/curators/taste_filter.md",
            "prompts/writers/message_prompt.md",
            "prompts/writers/message_layout.md",
        ):
            prompt_path = self.project_root / relative_path
            prompt_path.parent.mkdir(parents=True, exist_ok=True)
            prompt_path.write_text("prompt", encoding="utf-8")

        self.path_patches = (
            patch.object(pipeline_config, "PROJECT_ROOT", self.project_root),
            patch.object(pipeline_config, "CONFIG_PATH", self.config_path),
        )
        for path_patch in self.path_patches:
            path_patch.start()

    def tearDown(self):
        for path_patch in reversed(self.path_patches):
            path_patch.stop()
        self.temporary_directory.cleanup()

    def write_config(self, content):
        self.config_path.write_text(content, encoding="utf-8")

    def test_valid_config_assembles_stages_in_yaml_order_without_running(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    researcher_prompt_path: prompts/researchers/current_brief.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - name: writer
    provider: ollama
    model:
      name: custom-writer
      endpoint: http://localhost:9999/generate
  - name: researcher
    provider: gemini
    model:
      name: gemini-2.5-flash
      endpoint: https://gemini.example/v1beta/models
  - name: curator
    provider: gemini
    model:
      name: gemini-2.5-flash
      endpoint: https://gemini.example/v1beta/models
"""
        )

        with patch.object(Writer, "run", side_effect=AssertionError("stage executed")):
            stages = load_pipeline()

        self.assertEqual([type(stage) for stage in stages], [Writer, Researcher, Curator])
        self.assertEqual(stages[0].provider, "ollama")
        self.assertEqual(stages[0].model, "custom-writer")
        self.assertEqual(stages[0].endpoint, "http://localhost:9999/generate")
        self.assertEqual(
            stages[0].template_path,
            self.project_root / "prompts/writers/message_layout.md",
        )
        self.assertEqual(
            [stage.prompt_path for stage in stages],
            [
                self.project_root / "prompts/writers/message_prompt.md",
                self.project_root / "prompts/researchers/current_brief.md",
                self.project_root / "prompts/curators/taste_filter.md",
            ],
        )

    def test_missing_config_file_is_an_error(self):
        self.config_path.unlink(missing_ok=True)
        with self.assertRaisesRegex(PipelineConfigError, "does not exist"):
            load_pipeline()

    def test_malformed_yaml_is_an_error(self):
        self.write_config("stages: [name: researcher")
        with self.assertRaisesRegex(PipelineConfigError, "malformed"):
            load_pipeline()

    def test_config_without_stages_list_is_an_error(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    researcher_prompt_path: prompts/researchers/current_brief.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages: researcher
"""
        )
        with self.assertRaisesRegex(PipelineConfigError, "stages list"):
            load_pipeline()

    def test_stage_without_name_is_an_error(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    researcher_prompt_path: prompts/researchers/current_brief.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - provider: gemini
    model:
      name: gemini-2.5-flash
"""
        )
        with self.assertRaisesRegex(PipelineConfigError, "name"):
            load_pipeline()

    def test_model_provider_is_passed_to_researcher_and_curator(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    researcher_prompt_path: prompts/researchers/current_brief.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - name: researcher
    provider: openai
    model:
      name: gpt-4.1-mini
      endpoint: https://openai.example/responses
  - name: curator
    provider: openai
    model:
      name: gpt-4.1-mini
      endpoint: https://openai.example/responses
"""
        )

        stages = load_pipeline()

        self.assertEqual(stages[0].provider, "openai")
        self.assertEqual(stages[0].model, "gpt-4.1-mini")
        self.assertEqual(stages[0].endpoint, "https://openai.example/responses")
        self.assertEqual(stages[1].provider, "openai")
        self.assertEqual(stages[1].model, "gpt-4.1-mini")
        self.assertEqual(stages[1].endpoint, "https://openai.example/responses")

    def test_provider_specific_researcher_prompt_selects_gemini_prompt(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    researcher_prompt_path: prompts/researchers/current_brief.md
    researcher_prompt_paths:
      gemini: prompts/researchers/gemini_brief.md
      openai: prompts/researchers/openai_brief.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - name: researcher
    provider: gemini
    model:
      name: gemini-2.5-flash
      endpoint: https://gemini.example/v1beta/models
"""
        )

        stages = load_pipeline()

        self.assertEqual(
            stages[0].prompt_path,
            self.project_root / "prompts/researchers/gemini_brief.md",
        )

    def test_provider_specific_researcher_prompt_selects_openai_prompt(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    researcher_prompt_path: prompts/researchers/current_brief.md
    researcher_prompt_paths:
      gemini: prompts/researchers/gemini_brief.md
      openai: prompts/researchers/openai_brief.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - name: researcher
    provider: openai
    model:
      name: gpt-4.1-mini
      endpoint: https://openai.example/responses
"""
        )

        stages = load_pipeline()

        self.assertEqual(
            stages[0].prompt_path,
            self.project_root / "prompts/researchers/openai_brief.md",
        )

    def test_missing_provider_specific_researcher_prompt_uses_fallback(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    researcher_prompt_path: prompts/researchers/current_brief.md
    researcher_prompt_paths:
      gemini: prompts/researchers/gemini_brief.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - name: researcher
    provider: openai
    model:
      name: gpt-4.1-mini
      endpoint: https://openai.example/responses
"""
        )

        stages = load_pipeline()

        self.assertEqual(
            stages[0].prompt_path,
            self.project_root / "prompts/researchers/current_brief.md",
        )

    def test_nonexistent_selected_provider_specific_researcher_prompt_is_an_error(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    researcher_prompt_path: prompts/researchers/current_brief.md
    researcher_prompt_paths:
      openai: prompts/researchers/missing_openai.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - name: researcher
    provider: openai
    model:
      name: gpt-4.1-mini
      endpoint: https://openai.example/responses
"""
        )

        with self.assertRaisesRegex(PipelineConfigError, "prompt file does not exist"):
            load_pipeline()

    def test_unconfigured_provider_specific_researcher_prompt_is_ignored(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    researcher_prompt_path: prompts/researchers/current_brief.md
    researcher_prompt_paths:
      openai: prompts/researchers/missing_openai.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - name: researcher
    provider: gemini
    model:
      name: gemini-2.5-flash
      endpoint: https://gemini.example/v1beta/models
"""
        )

        stages = load_pipeline()

        self.assertEqual(
            stages[0].prompt_path,
            self.project_root / "prompts/researchers/current_brief.md",
        )

    def test_bandcamp_researcher_loads_without_prompt_model_or_endpoint(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - name: researcher
    provider: bandcamp
"""
        )

        stages = load_pipeline()

        self.assertEqual([type(stage) for stage in stages], [Researcher])
        self.assertEqual(stages[0].provider, "bandcamp")
        self.assertIsNone(stages[0].prompt_path)
        self.assertEqual(stages[0].model, "")
        self.assertEqual(stages[0].endpoint, "")

    def test_bandcamp_researcher_receives_configured_discovery(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - name: researcher
    provider: bandcamp
    discovery:
      category_id: 0
      tag_norm_names:
        - dub-techno
      geoname_id: 123
      slice: top
      time_facet_id: 7
      cursor: abc
      size: 12
      include_result_types:
        - a
"""
        )

        stages = load_pipeline()

        self.assertEqual(
            stages[0].discovery,
            {
                "category_id": 0,
                "tag_norm_names": ["dub-techno"],
                "geoname_id": 123,
                "slice": "top",
                "time_facet_id": 7,
                "cursor": "abc",
                "size": 12,
                "include_result_types": ["a"],
            },
        )

    def test_bandcamp_discovery_must_be_complete_and_well_formed(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - name: researcher
    provider: bandcamp
    discovery:
      category_id: 0
      tag_norm_names: []
      geoname_id: 0
      slice: new
      time_facet_id: 0
      cursor: "*"
      size: 24
      include_result_types:
        - a
"""
        )

        with self.assertRaisesRegex(PipelineConfigError, "tag_norm_names"):
            load_pipeline()

    def test_model_backed_researcher_rejects_source_discovery(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    researcher_prompt_path: prompts/researchers/current_brief.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - name: researcher
    provider: gemini
    discovery:
      category_id: 0
    model:
      name: gemini-2.5-flash
      endpoint: https://gemini.example/v1beta/models
"""
        )

        with self.assertRaisesRegex(PipelineConfigError, "Discovery configuration"):
            load_pipeline()

    def test_bandcamp_researcher_ignores_unused_prompt_paths(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    researcher_prompt_path: prompts/researchers/missing.md
    researcher_prompt_paths:
      bandcamp: prompts/researchers/also-missing.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - name: researcher
    provider: bandcamp
"""
        )

        stages = load_pipeline()

        self.assertEqual(stages[0].provider, "bandcamp")
        self.assertIsNone(stages[0].prompt_path)

    def test_unsupported_provider_for_stage_is_an_error(self):
        cases = [
            ("researcher", "ollama"),
            ("curator", "ollama"),
            ("writer", "openai"),
        ]

        for stage_name, provider in cases:
            with self.subTest(stage_name=stage_name, provider=provider):
                self.write_config(
                    f"""default_profile: sample
profiles:
  sample:
    researcher_prompt_path: prompts/researchers/current_brief.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - name: {stage_name}
    provider: {provider}
    model:
      name: unsupported-model
      endpoint: https://model.example/endpoint
"""
                )

                with self.assertRaisesRegex(PipelineConfigError, "Unsupported provider"):
                    load_pipeline()

    def test_prompt_driven_stage_without_prompt_path_is_an_error(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - name: researcher
    provider: gemini
    model:
      name: gemini-2.5-flash
      endpoint: https://gemini.example/v1beta/models
"""
        )
        with self.assertRaisesRegex(PipelineConfigError, "researcher_prompt_path"):
            load_pipeline()

    def test_writer_without_template_path_is_an_error(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    researcher_prompt_path: prompts/researchers/current_brief.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
stages:
  - name: writer
    provider: ollama
    model:
      name: custom-writer
      endpoint: http://localhost:9999/generate
"""
        )
        with self.assertRaisesRegex(PipelineConfigError, "writer_template_path"):
            load_pipeline()

    def test_unknown_stage_name_is_an_error(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    researcher_prompt_path: prompts/researchers/current_brief.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - name: broadcaster
"""
        )
        with self.assertRaisesRegex(PipelineConfigError, "Unknown stage"):
            load_pipeline()

    def test_missing_prompt_file_is_an_error(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    researcher_prompt_path: prompts/missing.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - name: researcher
    provider: gemini
    model:
      name: gemini-2.5-flash
      endpoint: https://gemini.example/v1beta/models
"""
        )
        with self.assertRaisesRegex(PipelineConfigError, "prompt file does not exist"):
            load_pipeline()

    def test_missing_writer_template_file_is_an_error(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    researcher_prompt_path: prompts/researchers/current_brief.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/missing-layout.md
stages:
  - name: writer
    provider: ollama
    model:
      name: custom-writer
      endpoint: http://localhost:9999/generate
"""
        )
        with self.assertRaisesRegex(PipelineConfigError, "template file does not exist"):
            load_pipeline()

    def test_stage_requires_top_level_provider(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    researcher_prompt_path: prompts/researchers/current_brief.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - name: researcher
    model:
      name: gemini-2.5-flash
      endpoint: https://gemini.example/v1beta/models
"""
        )
        with self.assertRaisesRegex(PipelineConfigError, "provider"):
            load_pipeline()

    def test_model_backed_stage_requires_model_name(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    researcher_prompt_path: prompts/researchers/current_brief.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - name: researcher
    provider: gemini
    model:
      endpoint: https://gemini.example/v1beta/models
"""
        )
        with self.assertRaisesRegex(PipelineConfigError, "name"):
            load_pipeline()

    def test_model_backed_stage_requires_endpoint(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    researcher_prompt_path: prompts/researchers/current_brief.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - name: researcher
    provider: gemini
    model:
      name: gemini-2.5-flash
"""
        )
        with self.assertRaisesRegex(PipelineConfigError, "endpoint"):
            load_pipeline()

    def test_model_endpoint_must_be_non_empty_string(self):
        cases = [
            "",
            "[]",
        ]

        for endpoint in cases:
            with self.subTest(endpoint=endpoint):
                self.write_config(
                    f"""default_profile: sample
profiles:
  sample:
    researcher_prompt_path: prompts/researchers/current_brief.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - name: researcher
    provider: gemini
    model:
      name: gemini-2.5-flash
      endpoint: {endpoint}
"""
                )
                with self.assertRaisesRegex(PipelineConfigError, "endpoint"):
                    load_pipeline()

    def test_explicit_profile_supplies_profile_specific_paths(self):
        finance_researcher_path = self.project_root / "prompts/researchers/market_scan.md"
        finance_curator_path = self.project_root / "prompts/curators/risk_filter.md"
        finance_writer_path = self.project_root / "prompts/writers/finance_brief.md"
        finance_template_path = self.project_root / "prompts/writers/finance_layout.md"
        for path in (
            finance_researcher_path,
            finance_curator_path,
            finance_writer_path,
            finance_template_path,
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("prompt", encoding="utf-8")

        self.write_config(
            """default_profile: sample
profiles:
  sample:
    researcher_prompt_path: prompts/researchers/current_brief.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
  finance:
    researcher_prompt_path: prompts/researchers/market_scan.md
    curator_prompt_path: prompts/curators/risk_filter.md
    writer_prompt_path: prompts/writers/finance_brief.md
    writer_template_path: prompts/writers/finance_layout.md
stages:
  - name: researcher
    provider: gemini
    model:
      name: gemini-2.5-flash
      endpoint: https://gemini.example/v1beta/models
  - name: curator
    provider: gemini
    model:
      name: gemini-2.5-flash
      endpoint: https://gemini.example/v1beta/models
  - name: writer
    provider: ollama
    model:
      name: custom-writer
      endpoint: http://localhost:9999/generate
"""
        )

        stages = load_pipeline("finance")

        self.assertEqual(
            [stage.prompt_path for stage in stages],
            [finance_researcher_path, finance_curator_path, finance_writer_path],
        )
        self.assertEqual(stages[2].template_path, finance_template_path)

    def test_unknown_profile_is_an_error(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    researcher_prompt_path: prompts/researchers/current_brief.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - name: researcher
"""
        )

        with self.assertRaisesRegex(PipelineConfigError, "Unknown profile"):
            load_pipeline("missing")

    def test_missing_default_profile_is_an_error(self):
        self.write_config(
            """profiles:
  sample:
    researcher_prompt_path: prompts/researchers/current_brief.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - name: researcher
"""
        )

        with self.assertRaisesRegex(PipelineConfigError, "default_profile"):
            load_pipeline()

    def test_resolves_default_profile_name_and_ledger_path(self):
        self.write_config(
            """default_profile: sample
profiles:
  sample:
    researcher_prompt_path: prompts/researchers/current_brief.md
    curator_prompt_path: prompts/curators/taste_filter.md
    writer_prompt_path: prompts/writers/message_prompt.md
    writer_template_path: prompts/writers/message_layout.md
stages:
  - name: researcher
"""
        )

        self.assertEqual(resolve_profile_name(), "sample")
        self.assertEqual(
            profile_ledger_path("sample"),
            self.project_root / "output" / "sample" / "ledger.json",
        )

    def test_enabled_telegram_delivery_is_loaded_separately_from_stages(self):
        self.write_config(
            """stages:
  - name: writer
    prompt_path: prompts/writers/message_prompt.md
    template_path: prompts/writers/message_layout.md
delivery:
  - provider: telegram
    enabled: true
"""
        )

        providers = load_delivery_config()

        self.assertEqual([type(provider) for provider in providers], [TelegramDelivery])

    def test_disabled_delivery_provider_is_not_loaded(self):
        self.write_config(
            """stages:
  - name: writer
    prompt_path: prompts/writers/message_prompt.md
    template_path: prompts/writers/message_layout.md
delivery:
  - provider: telegram
    enabled: false
"""
        )

        self.assertEqual(load_delivery_config(), [])

    def test_delivery_section_must_be_a_list(self):
        self.write_config(
            """stages:
  - name: writer
    prompt_path: prompts/writers/message_prompt.md
    template_path: prompts/writers/message_layout.md
delivery:
  provider: telegram
  enabled: true
"""
        )

        with self.assertRaisesRegex(PipelineConfigError, "delivery section"):
            load_delivery_config()

    def test_delivery_provider_requires_enabled_flag(self):
        self.write_config(
            """stages:
  - name: writer
    prompt_path: prompts/writers/message_prompt.md
    template_path: prompts/writers/message_layout.md
delivery:
  - provider: telegram
"""
        )

        with self.assertRaisesRegex(PipelineConfigError, "enabled"):
            load_delivery_config()


class DefaultPipelineConfigTests(unittest.TestCase):
    def selected_checked_in_profile(self):
        config = yaml.safe_load(pipeline_config.CONFIG_PATH.read_text(encoding="utf-8"))
        profiles = config.get("profiles")
        self.assertIsInstance(profiles, dict)
        self.assertTrue(profiles)
        default_profile = config.get("default_profile")
        if default_profile is not None:
            self.assertIsInstance(default_profile, str)
            self.assertIn(default_profile, profiles)
            return default_profile
        return next(iter(profiles))

    def test_default_config_defines_required_stage_order_and_prompts(self):
        stages = load_pipeline(self.selected_checked_in_profile())

        self.assertEqual([type(stage) for stage in stages], [Researcher, Curator, Writer])
        for stage in stages:
            if getattr(stage, "prompt_path", None) is not None:
                self.assertTrue(stage.prompt_path.is_file())
        self.assertTrue(stages[2].template_path.is_file())

    def test_checked_in_default_profile_is_internally_consistent_when_declared(self):
        config = yaml.safe_load(pipeline_config.CONFIG_PATH.read_text(encoding="utf-8"))
        profiles = config.get("profiles")
        self.assertIsInstance(profiles, dict)
        self.assertTrue(profiles)
        default_profile = config.get("default_profile")
        if default_profile is not None:
            self.assertIsInstance(default_profile, str)
            self.assertIn(default_profile, profiles)
            self.assertEqual(resolve_profile_name(), default_profile)

    def test_configured_stages_do_not_define_path_fallbacks(self):
        self.assertFalse(hasattr(researcher_module, "DEFAULT_PROMPT_PATH"))
        self.assertFalse(hasattr(curator_module, "DEFAULT_PROMPT_PATH"))
        self.assertFalse(hasattr(writer_module, "DEFAULT_PROMPT_PATH"))
        self.assertFalse(hasattr(writer_module, "DEFAULT_TEMPLATE_PATH"))

    def test_default_config_defines_enabled_telegram_delivery(self):
        providers = load_delivery_config()

        self.assertEqual([type(provider) for provider in providers], [TelegramDelivery])


if __name__ == "__main__":
    unittest.main()
