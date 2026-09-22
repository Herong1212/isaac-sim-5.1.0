import omni.kit.app
import omni.kit.test
import omni.stageupdate
from omni.kit.sequencer.usd import g_sequence_player, sequence_player

g_stage_update_interface = omni.stageupdate.get_stage_update_interface()


def _get_update_node_dict(name):
    update_nodes = g_stage_update_interface.get_stage_update_nodes()
    for node in update_nodes:
        node_name = node.get("name")
        if node_name == name:
            return node


class TestSequencePlayer(omni.kit.test.AsyncTestCase):
    async def test_player_instance(self):
        self.assertIsNotNone(g_sequence_player)

    async def test_player_subscription(self):
        index = g_sequence_player._get_update_node_index(sequence_player.UPDATE_NODE_ID)
        self.assertIsNotNone(index)
        _update_node_info = _get_update_node_dict(sequence_player.UPDATE_NODE_ID)
        self.assertIsNotNone(_update_node_info)
        self.assertTrue(_update_node_info.get("enabled"))

        g_sequence_player.suspend()
        _update_node_info = _get_update_node_dict(sequence_player.UPDATE_NODE_ID)
        self.assertIsNotNone(_update_node_info)
        self.assertFalse(_update_node_info.get("enabled"))

        g_sequence_player.resume()
        _update_node_info = _get_update_node_dict(sequence_player.UPDATE_NODE_ID)
        self.assertIsNotNone(_update_node_info)
        self.assertTrue(_update_node_info.get("enabled"))

    async def test_player_update(self):
        self.assertIsNone(g_sequence_player._on_update(0.0, 0.0))
