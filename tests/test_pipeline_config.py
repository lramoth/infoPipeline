import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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
    model:
      provider: ollama
      name: custom-writer
      endpoint: http://localhost:9999/generate
  - name: researcher
  - name: curator
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
  - model:
      provider: gemini
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
    model:
      provider: openai
      name: gpt-4.1-mini
  - name: curator
    model:
      provider: openai
      name: gpt-4.1-mini
"""
        )

        stages = load_pipeline()

        self.assertEqual(stages[0].provider, "openai")
        self.assertEqual(stages[0].model, "gpt-4.1-mini")
        self.assertEqual(stages[0].endpoint, "https://api.openai.com/v1/responses")
        self.assertEqual(stages[1].provider, "openai")
        self.assertEqual(stages[1].model, "gpt-4.1-mini")
        self.assertEqual(stages[1].endpoint, "https://api.openai.com/v1/responses")

    def test_unsupported_model_provider_for_stage_is_an_error(self):
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
    model:
      provider: {provider}
      name: unsupported-model
"""
                )

                with self.assertRaisesRegex(PipelineConfigError, "Unsupported model provider"):
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
"""
        )
        with self.assertRaisesRegex(PipelineConfigError, "template file does not exist"):
            load_pipeline()

    def test_model_object_requires_provider_and_name(self):
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
      provider: gemini
"""
        )
        with self.assertRaisesRegex(PipelineConfigError, "name"):
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
  - name: curator
  - name: writer
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
    def test_default_config_defines_required_stage_order_and_prompts(self):
        stages = load_pipeline()

        self.assertEqual([type(stage) for stage in stages], [Researcher, Curator, Writer])
        for stage in stages:
            self.assertTrue(stage.prompt_path.is_file())
        self.assertTrue(stages[2].template_path.is_file())

    def test_default_profile_is_declared(self):
        self.assertEqual(resolve_profile_name(), "techno")

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
