import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pipeline_config
from curator import Curator
from pipeline_config import PipelineConfigError, load_pipeline
from researcher import Researcher
from writer import Writer


class PipelineConfigTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temporary_directory.name)
        self.config_path = self.project_root / "config" / "pipeline.yaml"
        self.config_path.parent.mkdir()
        for relative_path in (
            "prompts/researchers/techno_news.md",
            "prompts/curators/polegroup_techno.md",
            "prompts/writers/outbound_brief.md",
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
            """stages:
  - name: writer
    prompt_path: prompts/writers/outbound_brief.md
    model:
      provider: ollama
      name: custom-writer
      endpoint: http://localhost:9999/generate
  - name: researcher
    prompt_path: prompts/researchers/techno_news.md
  - name: curator
    prompt_path: prompts/curators/polegroup_techno.md
"""
        )

        with patch.object(Writer, "run", side_effect=AssertionError("stage executed")):
            stages = load_pipeline()

        self.assertEqual([type(stage) for stage in stages], [Writer, Researcher, Curator])
        self.assertEqual(stages[0].model, "custom-writer")
        self.assertEqual(stages[0].endpoint, "http://localhost:9999/generate")
        self.assertEqual(
            [stage.prompt_path for stage in stages],
            [
                self.project_root / "prompts/writers/outbound_brief.md",
                self.project_root / "prompts/researchers/techno_news.md",
                self.project_root / "prompts/curators/polegroup_techno.md",
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
        self.write_config("stages: researcher\n")
        with self.assertRaisesRegex(PipelineConfigError, "stages list"):
            load_pipeline()

    def test_stage_without_name_is_an_error(self):
        self.write_config("stages:\n  - prompt_path: prompt.md\n")
        with self.assertRaisesRegex(PipelineConfigError, "name"):
            load_pipeline()

    def test_prompt_driven_stage_without_prompt_path_is_an_error(self):
        self.write_config("stages:\n  - name: researcher\n")
        with self.assertRaisesRegex(PipelineConfigError, "prompt_path"):
            load_pipeline()

    def test_unknown_stage_name_is_an_error(self):
        self.write_config("stages:\n  - name: broadcaster\n    prompt_path: prompt.md\n")
        with self.assertRaisesRegex(PipelineConfigError, "Unknown stage"):
            load_pipeline()

    def test_missing_prompt_file_is_an_error(self):
        self.write_config(
            "stages:\n  - name: researcher\n    prompt_path: prompts/missing.md\n"
        )
        with self.assertRaisesRegex(PipelineConfigError, "prompt file does not exist"):
            load_pipeline()

    def test_model_object_requires_provider_and_name(self):
        self.write_config(
            """stages:
  - name: researcher
    prompt_path: prompts/researchers/techno_news.md
    model:
      provider: gemini
"""
        )
        with self.assertRaisesRegex(PipelineConfigError, "name"):
            load_pipeline()


class DefaultPipelineConfigTests(unittest.TestCase):
    def test_default_config_defines_required_stage_order_and_prompts(self):
        stages = load_pipeline()

        self.assertEqual([type(stage) for stage in stages], [Researcher, Curator, Writer])
        self.assertEqual(
            [stage.prompt_path.relative_to(pipeline_config.PROJECT_ROOT).as_posix() for stage in stages],
            [
                "prompts/researchers/techno_news.md",
                "prompts/curators/polegroup_techno.md",
                "prompts/writers/outbound_brief.md",
            ],
        )


if __name__ == "__main__":
    unittest.main()
