from collections import defaultdict, deque
from time import sleep

from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase

from ..signal_rate_block import SignalRate


class TestSignalRate(NIOBlockTestCase):

    def test_rates_before_interval(self):
        blk = SignalRate()
        self.configure_block(blk, {
            "group_by": "{{$group}}",
            "report_interval": {
                "seconds": 1
            },
            "averaging_interval": {
                "seconds": 30
            },
            "log_level": "DEBUG"
        })
        blk.start()

        blk.process_signals(self._get_signals('A', 5))
        blk.process_signals(self._get_signals('B', 3))

        # Should have no signals yet
        self.assert_num_signals_notified(0)

        # After (a little more than) one second, we should be around that
        # number per second
        sleep(1.1)
        # One per group
        self.assert_num_signals_notified(2)
        self.assertAlmostEqual(
            self.last_notified[DEFAULT_TERMINAL][0].to_dict()['rate']
            if self.last_notified[DEFAULT_TERMINAL][0]
                   .to_dict()['group'] == 'A'
            else self.last_notified[DEFAULT_TERMINAL][1].to_dict()['rate'],
            5 / 1, 1)
        self.assertAlmostEqual(
            self.last_notified[DEFAULT_TERMINAL][1].to_dict()['rate']
            if self.last_notified[DEFAULT_TERMINAL][1]
                   .to_dict()['group'] == 'B'
            else self.last_notified[DEFAULT_TERMINAL][0].to_dict()['rate'],
            3 / 1, 1)

        # Wait one more second, make sure rates are about half
        sleep(1)
        # One per group - twice!
        self.assert_num_signals_notified(4)
        self.assertAlmostEqual(
            self.last_notified[DEFAULT_TERMINAL][2].to_dict()['rate']
            if self.last_notified[DEFAULT_TERMINAL][2]
                   .to_dict()['group'] == 'A'
            else self.last_notified[DEFAULT_TERMINAL][3].to_dict()['rate'],
            5 / 2, 1)
        self.assertAlmostEqual(
            self.last_notified[DEFAULT_TERMINAL][3].to_dict()['rate']
            if self.last_notified[DEFAULT_TERMINAL][3]
                   .to_dict()['group'] == 'B'
            else self.last_notified[DEFAULT_TERMINAL][2].to_dict()['rate'],
            3 / 2, 1)

        # Add some As, then wait one more second
        blk.process_signals(self._get_signals('A', 6))
        sleep(1)
        self.assertAlmostEqual(
            self.last_notified[DEFAULT_TERMINAL][4].to_dict()['rate']
            if self.last_notified[DEFAULT_TERMINAL][4]
                   .to_dict()['group'] == 'A'
            else self.last_notified[DEFAULT_TERMINAL][5].to_dict()['rate'],
            11 / 3, 1)
        self.assertAlmostEqual(
            self.last_notified[DEFAULT_TERMINAL][5].to_dict()['rate']
            if self.last_notified[DEFAULT_TERMINAL][5]
                   .to_dict()['group'] == 'B'
            else self.last_notified[DEFAULT_TERMINAL][4].to_dict()['rate'],
            3 / 3, 1)
        blk.stop()

    def test_rates_after_interval(self):
        blk = SignalRate()
        self.configure_block(blk, {
            "group_by": "{{$group}}",
            "report_interval": {
                "seconds": 1
            },
            "averaging_interval": {
                "seconds": 2
            },
            "log_level": "DEBUG"
        })
        blk.start()

        # Sleep half a second so we know these signals are included in the
        # first 2 second window
        sleep(0.5)
        blk.process_signals(self._get_signals('A', 5))
        blk.process_signals(self._get_signals('B', 3))

        # Should have no signals yet
        self.assert_num_signals_notified(0)

        # After (a little more than) one second, we should be around that
        # number per second
        sleep(0.6)
        # One per group
        self.assert_num_signals_notified(2)
        self.assertAlmostEqual(
            self.last_notified[DEFAULT_TERMINAL][0].to_dict()['rate']
            if self.last_notified[DEFAULT_TERMINAL][0]
                   .to_dict()['group'] == 'A'
            else self.last_notified[DEFAULT_TERMINAL][1].to_dict()['rate'],
            5 / 1, 1)
        self.assertAlmostEqual(
            self.last_notified[DEFAULT_TERMINAL][1].to_dict()['rate']
            if self.last_notified[DEFAULT_TERMINAL][1]
                   .to_dict()['group'] == 'B'
            else self.last_notified[DEFAULT_TERMINAL][0].to_dict()['rate'],
            3 / 1, 1)

        # Wait one more second, make sure rates are about half
        sleep(1)
        # One per group - twice!
        self.assert_num_signals_notified(4)
        self.assertAlmostEqual(
            self.last_notified[DEFAULT_TERMINAL][2].to_dict()['rate']
            if self.last_notified[DEFAULT_TERMINAL][2]
                   .to_dict()['group'] == 'A'
            else self.last_notified[DEFAULT_TERMINAL][3].to_dict()['rate'],
            5 / 2, 1)
        self.assertAlmostEqual(
            self.last_notified[DEFAULT_TERMINAL][3].to_dict()['rate']
            if self.last_notified[DEFAULT_TERMINAL][3]
                   .to_dict()['group'] == 'B'
            else self.last_notified[DEFAULT_TERMINAL][2].to_dict()['rate'],
            3 / 2, 1)

        # Add some As, then wait one more second, now we should be every
        # 2 seconds from here on
        # So we only have these As, and no more Bs
        blk.process_signals(self._get_signals('A', 6))
        sleep(1)
        self.assertAlmostEqual(
            self.last_notified[DEFAULT_TERMINAL][4].to_dict()['rate']
            if self.last_notified[DEFAULT_TERMINAL][4]
                   .to_dict()['group'] == 'A'
            else self.last_notified[DEFAULT_TERMINAL][5].to_dict()['rate'],
            6 / 2, 1)
        self.assertAlmostEqual(
            self.last_notified[DEFAULT_TERMINAL][5].to_dict()['rate']
            if self.last_notified[DEFAULT_TERMINAL][5]
                   .to_dict()['group'] == 'B'
            else self.last_notified[DEFAULT_TERMINAL][4].to_dict()['rate'],
            0 / 2, 1)

        # Sleep until the next notification, make sure everything's cleaned up
        sleep(2)
        self.assertEqual(len(blk._signal_counts['A']), 0)
        self.assertEqual(len(blk._signal_counts['B']), 0)
        self.assertAlmostEqual(
            self.last_notified[DEFAULT_TERMINAL][8].to_dict()['rate']
            if self.last_notified[DEFAULT_TERMINAL][8]
                   .to_dict()['group'] == 'A'
            else self.last_notified[DEFAULT_TERMINAL][9].to_dict()['rate'],
            0 / 2, 1)
        self.assertAlmostEqual(
            self.last_notified[DEFAULT_TERMINAL][9].to_dict()['rate']
            if self.last_notified[DEFAULT_TERMINAL][9]
                   .to_dict()['group'] == 'B'
            else self.last_notified[DEFAULT_TERMINAL][8].to_dict()['rate'],
            0 / 2, 1)
        blk.stop()

    def test_deque(self):
        blk = SignalRate()
        # Pretend that _signal_counts has this value loaded from persistence
        blk._signal_counts = defaultdict(list)
        blk._signal_counts['key1'].append((1, 1))
        blk._signal_counts['key2'].append((1, 1))
        self.assertEqual(blk._signal_counts.default_factory, list)
        self.assertTrue(isinstance(blk._signal_counts['key1'], list))
        self.assertTrue(isinstance(blk._signal_counts['key2'], list))
        self.configure_block(blk, {
        })
        self.assertEqual(blk._signal_counts.default_factory, deque)
        self.assertTrue(isinstance(blk._signal_counts['key1'], deque))
        self.assertTrue(isinstance(blk._signal_counts['key2'], deque))

    def _get_signals(self, group, count):
        return [Signal({"group": group, "val": val}) for val in range(count)]
