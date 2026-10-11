import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import apply_zh_tw as tool


class PatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / 'Cargo.toml').write_text('[package]\nname = "herdr"\n', encoding='utf-8')
        manifest = Path(tool.__file__).with_name('translations_zh_TW.json')
        self.mapping = json.loads(manifest.read_text(encoding='utf-8'))
        self.manifest = manifest
        for rel, pairs in self.mapping.items():
            file = self.root / rel
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text('\n'.join('const VALUE: &str = "'+key+'";' for key in pairs) + '\n#[cfg(test)]\nmod tests { const TEST: &str = "settings"; }\n', encoding='utf-8')
        ui = self.root / 'src/ui/widgets.rs'
        ui.parent.mkdir(parents=True, exist_ok=True)
        ui.write_text('use ratatui::{\n    layout::Rect,\n};\n\nuse crate::app::state::Palette;\n\nfn widget(hint: &str, label: &str) {\n   let a = format!(" {hint} {label} ").chars().count() as u16;\n   let b = format!(" {label} ").chars().count() as u16;\n}\n',encoding='utf-8')

    def tearDown(self):
        self.temp.cleanup()

    def test_manifest_placeholders_unchanged(self):
        for file, pairs in self.mapping.items():
            for old, new in pairs.items():
                self.assertEqual(tool.placeholders(old),tool.placeholders(new),(file,old))

    @patch('apply_zh_tw.command', side_effect=[tool.UPSTREAM_COMMIT, ''])
    def test_dry_run_does_not_modify_sources(self, _):
        before = (self.root/'src/client/shell/global_menu.rs').read_bytes()
        report = tool.apply(self.root, self.manifest, dry_run=True)
        self.assertEqual(report['applied_keys'],sum(len(m) for m in self.mapping.values()))
        self.assertFalse(report['missing_keys'])
        self.assertEqual(before,(self.root/'src/client/shell/global_menu.rs').read_bytes())

    @patch('apply_zh_tw.command', side_effect=[tool.UPSTREAM_COMMIT, ''])
    def test_apply_changes_target_but_not_test_module(self, _):
        report = tool.apply(self.root, self.manifest)
        self.assertFalse(report['missing_keys'])
        text=(self.root/'src/client/shell/global_menu.rs').read_text(encoding='utf-8')
        self.assertIn('"設定"', text)
        self.assertIn('mod tests { const TEST: &str = "settings"; }', text)
        ui=(self.root/'src/ui/widgets.rs').read_text(encoding='utf-8')
        self.assertEqual(ui.count('.as_str().width()'),2)
        self.assertIn('use unicode_width::UnicodeWidthStr;',ui)

    @patch('apply_zh_tw.command', return_value='wrong_revision')
    def test_reject_wrong_revision(self, _):
        with self.assertRaisesRegex(RuntimeError,'Requires exact'):
            tool.apply(self.root,self.manifest)

    @patch('apply_zh_tw.command', side_effect=[tool.UPSTREAM_COMMIT,' M src/a.rs'])
    def test_refuse_existing_edits(self,_):
        with self.assertRaisesRegex(RuntimeError,'not clean'):
            tool.apply(self.root,self.manifest)


if __name__ == '__main__':
    unittest.main()
