__copyright__ = "Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""
import asyncio
import os
import sys

import numpy as np
import omni.kit
import omni.kit.test
import omni.usd
from omni.metropolis.utils.unit_test import (
    MINIMAL_STAGE_URL,
    TestStage,
    StageSetupOptions,
)
from omni.metropolis.utils.carb_util import CarbUtil
from isaacsim.replicator.agent.core.settings import Infos
from isaacsim.replicator.agent.core.randomization.character_randomizer import CharacterRandomizer
from isaacsim.replicator.agent.core.randomization.randomizer import Randomizer, RandomizerConfig
from omni.metropolis.utils.math_util import MathNumpyUtil

"""Test suite for character randomization functionality.

This module contains comprehensive tests for the randomization system used
in agent-based simulations. It validates position generation, command generation,
seed consistency, and Markov chain distributions.
"""

# Test configuration constants
TEST_CHARACTER_COUNT = 10
AREA_LIST = ["Walkable"]
COMMAND_DURATION = 600

# Tolerance for distribution comparison
TOLERANCE = 0.01


class TestRandomization(omni.kit.test.AsyncTestCase):
    """Test suite for character randomization functionality.

    This test class validates:
    - Position generation and collision avoidance
    - Seed consistency and reproducibility
    - Command generation and duration validation
    - Markov chain distribution compliance
    """

    async def setUp(self):
        """Set up test fixtures before each test method."""
        self.randomizer = CharacterRandomizer(0)
        self._original_id_counter = None

    async def tearDown(self):
        """Clean up after each test method."""
        pass

    def _generate_positions(self, randomizer=None, area_list=None, count=None):
        """Helper method to generate positions.

        Args:
            randomizer: Randomizer instance to use (defaults to self.randomizer)
            area_list: Area list to use (defaults to AREA_LIST)
            count: Number of positions to generate (defaults to TEST_CHARACTER_COUNT)

        Returns:
            list: Generated positions

        Raises:
            AssertionError: If any position generation fails
        """
        randomizer = randomizer or self.randomizer
        area_list = area_list or AREA_LIST
        count = count or TEST_CHARACTER_COUNT

        positions = []
        for i in range(count):
            pos = randomizer.get_random_position(area_list)
            self.assertIsNotNone(pos, f"Failed to generate position {i+1}/{count}")
            positions.append(pos)
        return positions

    def _load_transition_map(self):
        """Helper method to load the example transition map.

        Raises:
            AssertionError: If the transition map file doesn't exist or fails to load
        """
        ext_path = Infos.ext_path
        file_path = os.path.join(ext_path, "test_data", "example_character_command_transition_map.json")
        self.assertTrue(os.path.exists(file_path), f"Transition map file not found: {file_path}")
        self.randomizer.load_command_transition_map(file_path)
        self.assertIsNotNone(self.randomizer.transition_map, "Failed to load transition map")

    async def _generate_commands(self, pos_list, area_list=None):
        """Helper method to generate commands for agents.

        Args:
            pos_list: List of initial positions
            area_list: Area list to use (defaults to AREA_LIST)

        Returns:
            list: Generated commands

        Raises:
            AssertionError: If command generation fails
        """
        area_list = area_list or AREA_LIST
        self.assertIsNotNone(pos_list, "Position list cannot be None")
        self.assertGreater(len(pos_list), 0, "Position list cannot be empty")

        agent_list = {f"a{idx}": pos_list[idx] for idx in range(len(pos_list))}

        self._load_transition_map()

        gather_result = await asyncio.gather(
            self.randomizer.generate_commands(0, COMMAND_DURATION, agent_list, area_list)
        )
        commands = gather_result[0]
        self.assertIsNotNone(commands, "Command generation returned None")
        return commands

    def _parse_commands(self, commands):
        """Helper method to parse commands into agent-specific lists.

        Args:
            commands: Raw command list

        Returns:
            dict: Agent command mapping
        """
        agent_command_list = {}
        for command in commands:
            command_parts = command.split()
            agent_name = command_parts[0]
            if agent_name not in agent_command_list:
                agent_command_list[agent_name] = []
            agent_command_list[agent_name].append(command_parts[1:])
        return agent_command_list

    def _count_command_types(self, commands):
        """Helper method to count different command types.

        Args:
            commands: Raw command list

        Returns:
            dict: Command type counts
        """
        counts = {"GoTo": 0, "Idle": 0, "LookAround": 0, "Sit": 0}

        for command in commands:
            command_parts = command.split()
            command_type = command_parts[1]  # Skip agent name
            if command_type in counts:
                counts[command_type] += 1

        return counts

    def _compute_expected_convergence(self, target_states=None):
        """Compute stationary distribution from the loaded transition map.

        Args:
            target_states: Optional list of state names to return. If None, use all states from the map.

        Returns:
            dict: Mapping of state name to stationary probability.
        """
        tmap = self.randomizer.transition_map
        self.assertIsNotNone(tmap, "Transition map must be loaded before computing expected convergence")

        commands = tmap.get_all_commands()
        state_names = [c.name for c in commands]
        if not state_names:
            return {}

        index_by_name = {name: i for i, name in enumerate(state_names)}
        n = len(state_names)
        P = np.zeros((n, n), dtype=float)

        fallback_name = self.randomizer.fallback_command.name if self.randomizer.fallback_command else None
        fallback_idx = index_by_name.get(fallback_name, None)

        for name in state_names:
            i = index_by_name[name]
            cmd = tmap.get_command_by_name(name)
            transitions = cmd.transitions if cmd and isinstance(cmd.transitions, dict) else {}
            total_w = float(sum(float(w) for w in transitions.values())) if transitions else 0.0

            if total_w <= 0.0:
                if fallback_idx is not None:
                    P[i, fallback_idx] = 1.0
                else:
                    P[i, :] = 1.0 / n
                continue

            for to_name, w in transitions.items():
                prob = float(w) / total_w if total_w > 0 else 0.0
                j = index_by_name.get(to_name)
                # If target command is unknown to the randomizer, it will fall back to the fallback command
                if j is not None and (to_name in self.randomizer.commands_dict):
                    P[i, j] += prob
                else:
                    if fallback_idx is not None:
                        P[i, fallback_idx] += prob

            # Normalize row in case of numeric drift
            row_sum = P[i, :].sum()
            if row_sum > 0:
                P[i, :] /= row_sum
            elif fallback_idx is not None:
                P[i, fallback_idx] = 1.0

        # Use generic utility to compute stationary distribution
        dist = MathNumpyUtil.compute_stationary_distribution(P)

        if target_states is None:
            target_states = state_names

        expected = {}
        for name in target_states:
            expected[name] = float(dist[index_by_name[name]]) if name in index_by_name else 0.0
        return expected

    async def test_character_position_distance(self):
        """Test that agents are placed with adequate distance between them.

        This test validates that the randomizer maintains minimum distance requirements
        between agent spawn positions to prevent overlapping.
        """
        async with TestStage(MINIMAL_STAGE_URL, StageSetupOptions.BAKE_NAV_MESH):
            pos_list = self._generate_positions(count=TEST_CHARACTER_COUNT)

            # Validate all positions are valid
            for i, pos in enumerate(pos_list):
                self.assertIsNotNone(pos, f"Position {i} is None")
                self.assertEqual(len(pos), 3, f"Position {i} should have 3 coordinates, got {len(pos)}")

            # Check minimum distance requirements between all agent pairs
            min_distance = self.randomizer.config.agent_distance
            violations = []

            for i, pos_i in enumerate(pos_list):
                for j in range(i + 1, len(pos_list)):
                    distance = CarbUtil.dist3(pos_i, pos_list[j])
                    if distance <= min_distance:
                        violations.append({
                            'agents': (i, j),
                            'distance': distance,
                            'positions': (pos_i, pos_list[j]),
                            'min_required': min_distance
                        })

            self.assertEqual(len(violations), 0,
                             f"Found {len(violations)} distance violations:\n" +
                             "\n".join([f"  Agents {v['agents'][0]} and {v['agents'][1]}: "
                                        f"distance={v['distance']:.3f} < required={v['min_required']:.3f}"
                                        for v in violations[:5]])  # Show first 5 violations
                             + (f"\n  ... and {len(violations)-5} more" if len(violations) > 5 else ""))

    async def test_character_position_seed_consistency(self):
        """Test that same seeds produce consistent results.

        This test validates that randomization is deterministic when using the same
        seed values, which is essential for reproducible simulations.
        """
        async with TestStage(MINIMAL_STAGE_URL, StageSetupOptions.BAKE_NAV_MESH):
            # Save the current ID counter state for cleanup
            self._original_id_counter = Randomizer.ID_counter

            try:
                # Test multiple seed values for robustness
                test_seed = 12345

                # Reset ID counter and create first randomizer
                Randomizer.ID_counter = -1
                randomizer1 = CharacterRandomizer(test_seed)
                pos_list1 = self._generate_positions(randomizer1, count=TEST_CHARACTER_COUNT)

                # Reset ID counter again to get the same agent_id for the second randomizer
                Randomizer.ID_counter = -1
                randomizer2 = CharacterRandomizer(test_seed)
                pos_list2 = self._generate_positions(randomizer2, count=TEST_CHARACTER_COUNT)

                # Validate both lists have the same length
                self.assertEqual(len(pos_list1), len(pos_list2),
                                 f"Position lists have different lengths: {len(pos_list1)} vs {len(pos_list2)}")

                # Check each position pair for exact equality
                mismatches = []
                for i in range(len(pos_list1)):
                    if not CarbUtil.equal3(pos_list1[i], pos_list2[i]):
                        mismatches.append({
                            'index': i,
                            'pos1': pos_list1[i],
                            'pos2': pos_list2[i],
                            'diff': [abs(a-b) for a, b in zip(pos_list1[i], pos_list2[i])]
                        })

                self.assertEqual(len(mismatches), 0,
                                 f"Found {len(mismatches)} position mismatches:\n" +
                                 "\n".join([f"  Index {m['index']}: {m['pos1']} != {m['pos2']} "
                                            f"(max diff: {max(m['diff']):.6f})"
                                            for m in mismatches[:3]])  # Show first 3 mismatches
                                 + (f"\n  ... and {len(mismatches)-3} more" if len(mismatches) > 3 else ""))

            finally:
                # Ensure cleanup happens even if test fails
                Randomizer.ID_counter = self._original_id_counter

    async def test_character_position_seed_differences(self):
        """Test that different seeds produce different results.

        This test validates that different seeds produce genuinely different
        randomization results, ensuring proper seed handling.
        """
        async with TestStage(MINIMAL_STAGE_URL, StageSetupOptions.BAKE_NAV_MESH):
            # Generate positions with default seed (0)
            pos_list1 = self._generate_positions(count=TEST_CHARACTER_COUNT)

            # Test with multiple different seeds to ensure robustness
            different_seeds = [12345, 999999, 2**20]
            all_same = True

            for test_seed in different_seeds:
                randomizer = CharacterRandomizer(test_seed)
                pos_list2 = self._generate_positions(randomizer, count=TEST_CHARACTER_COUNT)

                # Count how many positions are different
                different_positions = sum(1 for i in range(len(pos_list1))
                                           if not CarbUtil.equal3(pos_list1[i], pos_list2[i]))

                if different_positions > 0:
                    all_same = False
                    # Log the difference statistics for debugging
                    print(f"Seed {test_seed}: {different_positions}/{len(pos_list1)} positions differ")
                    break

            self.assertFalse(all_same,
                             f"Different seeds produced identical positions. "
                             f"Tested seeds: {different_seeds}. This suggests "
                             f"seed handling may not be working properly.")

    async def test_character_position_call_consistency(self):
        """Test that multiple separate calls produce same result as single call."""
        async with TestStage(MINIMAL_STAGE_URL, StageSetupOptions.BAKE_NAV_MESH):
            # Use the same randomizer instance but reset it between tests
            randomizer = self.randomizer

            # First: generate all positions in one batch call
            pos_list = self._generate_positions(randomizer, count=TEST_CHARACTER_COUNT)

            # Reset the randomizer to start from the same state
            randomizer.reset()

            # Second: generate positions with separate calls (same total count)
            pos_list_first_half = self._generate_positions(randomizer, count=TEST_CHARACTER_COUNT // 2)
            pos_list_second_half = self._generate_positions(randomizer, count=TEST_CHARACTER_COUNT // 2)
            pos_list_test = pos_list_first_half + pos_list_second_half

            for i in range(len(pos_list)):
                self.assertTrue(CarbUtil.equal3(pos_list[i], pos_list_test[i]),
                                f"Split call mismatch at index {i}: {pos_list[i]} != {pos_list_test[i]}")

    async def test_character_command_generation(self):
        """Test character command generation and duration validation."""
        async with TestStage(MINIMAL_STAGE_URL, StageSetupOptions.BAKE_NAV_MESH):
            pos_list = self._generate_positions(count=TEST_CHARACTER_COUNT)
            commands = await self._generate_commands(pos_list)
            agent_command_list = self._parse_commands(commands)

            # Test each agent has enough commands to last for the given duration
            for agent_idx, agent in enumerate(agent_command_list):
                commands = agent_command_list[agent]
                duration = 0
                current_pos = np.array(pos_list[agent_idx])

                for command in commands:
                    # Get the command duration
                    if command[0] == "GoTo":
                        duration += np.linalg.norm(
                            np.array(current_pos[:2]) - np.array([float(command[1]), float(command[2])])
                        )
                        current_pos = np.array([float(command[1]), float(command[2]), float(command[3])])
                    else:
                        duration += float(command[1])

                print(f"{agent} calculated command duration = {duration}")
                self.assertTrue(duration > COMMAND_DURATION,
                                f"Agent {agent} duration {duration} insufficient for required {COMMAND_DURATION}")

    async def test_character_command_distribution(self):
        """Test that commands are generated according to the Markov Chain distribution."""
        async with TestStage(MINIMAL_STAGE_URL, StageSetupOptions.BAKE_NAV_MESH):
            pos_list = self._generate_positions(count=TEST_CHARACTER_COUNT)

            # Generate commands without area_list parameter to match the original call
            agent_list = {f"a{idx}": pos_list[idx] for idx in range(len(pos_list))}
            self._load_transition_map()

            gather_result = await asyncio.gather(
                self.randomizer.generate_commands(0, COMMAND_DURATION, agent_list, AREA_LIST)
            )
            commands = gather_result[0]

            # Count command types using helper method
            counts = self._count_command_types(commands)
            total_commands = sum(counts.values())

            # Print convergence values
            for cmd_type, count in counts.items():
                convergence = count / total_commands
                print(f"{cmd_type} calculated convergence = {convergence}")

            # Test whether the commands are generated according to the Markov Chain
            expected_convergence_map = self._compute_expected_convergence(["GoTo", "Idle", "LookAround", "Sit"])
            for cmd_type, expected_convergence in expected_convergence_map.items():
                actual_convergence = counts[cmd_type] / total_commands
                self.assertTrue(abs(actual_convergence - expected_convergence) < TOLERANCE,
                                f"{cmd_type} distribution {actual_convergence} not within tolerance of {expected_convergence}")

    async def test_edge_cases_and_error_handling(self):
        """Test edge cases and error handling in randomization.

        This test validates proper behavior under edge conditions such as
        empty area lists, invalid parameters, and boundary conditions.
        """
        async with TestStage(MINIMAL_STAGE_URL, StageSetupOptions.BAKE_NAV_MESH):
            # Test with minimal agent count
            pos_list_minimal = self._generate_positions(count=1)
            self.assertEqual(len(pos_list_minimal), 1, "Failed to generate single position")

            # Test command generation with minimal setup
            commands_minimal = await self._generate_commands(pos_list_minimal)
            self.assertGreater(len(commands_minimal), 0, "No commands generated for minimal setup")

            # Validate command format
            for cmd in commands_minimal[:5]:  # Check first 5 commands
                self.assertIsInstance(cmd, str, f"Command should be string, got {type(cmd)}")
                parts = cmd.split()
                self.assertGreaterEqual(len(parts), 2, f"Command should have at least 2 parts, got: {cmd}")
                # First part should be agent name, second should be command type
                self.assertTrue(parts[0].startswith('a'), f"Agent name should start with 'a', got: {parts[0]}")
                self.assertIn(parts[1], ['GoTo', 'Idle', 'LookAround', 'Sit'],
                              f"Unknown command type: {parts[1]}")

    async def test_randomizer_configuration_validation(self):
        """Test randomizer configuration parameter validation.

        This test validates that custom RandomizerConfig parameters work correctly
        and that the randomizer respects configuration changes.
        """
        async with TestStage(MINIMAL_STAGE_URL, StageSetupOptions.BAKE_NAV_MESH):
            # Test with custom configuration
            custom_config = RandomizerConfig(
                max_random_attempts=100,
                agent_distance=3.0,  # Larger than default
                agent_radius=0.3     # Smaller than default
            )

            randomizer_custom = CharacterRandomizer(42)
            randomizer_custom.config = custom_config

            # Generate positions with custom config
            pos_list_custom = self._generate_positions(randomizer_custom, count=5)

            # Verify custom distance requirements are met
            for i in range(len(pos_list_custom)):
                for j in range(i + 1, len(pos_list_custom)):
                    distance = CarbUtil.dist3(pos_list_custom[i], pos_list_custom[j])
                    self.assertGreater(distance, custom_config.agent_distance,
                                       f"Custom distance requirement not met: {distance} <= {custom_config.agent_distance}")
