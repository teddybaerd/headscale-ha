"""Exercise the removal hook without requiring a Home Assistant installation."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock

# Compile the actual hook; HA imports/setup are outside this unit's scope.
source = Path(__file__).parents[1] / 'custom_components/headscale_monitor/__init__.py'
module = ast.parse(source.read_text())
hook = next(n for n in module.body if isinstance(n, ast.AsyncFunctionDef) and n.name == 'async_remove_config_entry_device')

class HeadscaleError(Exception):
    pass

namespace = {'DOMAIN': 'headscale_monitor', 'HeadscaleError': HeadscaleError}
exec(compile(ast.Module(body=[hook], type_ignores=[]), str(source), 'exec'), namespace)
remove = namespace['async_remove_config_entry_device']

class RemovalTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = SimpleNamespace(nodes=AsyncMock(return_value={}))
        self.entry = SimpleNamespace(entry_id='entry', runtime_data=SimpleNamespace(client=self.client, hub_device_id='hub', data={}))
        self.device = SimpleNamespace(id='device', identifiers={('headscale_monitor', 'entry_42')})

    async def test_absent_node_can_be_removed(self):
        self.entry.runtime_data.data = {'42': {}}
        self.assertTrue(await remove(None, self.entry, self.device))
        self.client.nodes.assert_awaited_once()

    async def test_offline_or_returned_node_is_protected(self):
        self.client.nodes.return_value = {'42': {'online': False}}
        self.assertFalse(await remove(None, self.entry, self.device))

    async def test_failed_verification_is_protected(self):
        self.client.nodes.side_effect = HeadscaleError('authentication or connection error')
        self.assertFalse(await remove(None, self.entry, self.device))

    async def test_hub_and_foreign_devices_are_protected(self):
        for device in [SimpleNamespace(id='hub', identifiers={('headscale_monitor','entry')}), SimpleNamespace(id='foreign', identifiers={('headscale_monitor','other_42')}), SimpleNamespace(id='bad', identifiers={('headscale_monitor','entry_')})]:
            self.assertFalse(await remove(None, self.entry, device))
        self.client.nodes.assert_not_awaited()

    async def test_unloaded_entry_is_protected(self):
        self.entry.runtime_data = None
        self.assertFalse(await remove(None, self.entry, self.device))

    async def test_any_registered_identifier_prevents_removal(self):
        self.device.identifiers.add(('headscale_monitor','entry_43'))
        self.client.nodes.return_value = {'43': {}}
        self.assertFalse(await remove(None, self.entry, self.device))
