from ..signal_rate_block import SignalRate
from nio.common.signal.base import Signal
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.modules.threading import sleep


class TestSignalRate(NIOBlockTestCase):

    _signal_rates = {}

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
        self.assertAlmostEqual(self._signal_rates['A'], 5 / 1, 1)
        self.assertAlmostEqual(self._signal_rates['B'], 3 / 1, 1)

        # Wait one more second, make sure rates are about half
        sleep(1)
        # One per group - twice!
        self.assert_num_signals_notified(4)
        self.assertAlmostEqual(self._signal_rates['A'], 5 / 2, 1)
        self.assertAlmostEqual(self._signal_rates['B'], 3 / 2, 1)

        # Add some As, then wait one more second
        blk.process_signals(self._get_signals('A', 6))
        sleep(1)
        self.assertAlmostEqual(self._signal_rates['A'], 11 / 3, 1)
        self.assertAlmostEqual(self._signal_rates['B'], 3 / 3, 1)

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
        self.assertAlmostEqual(self._signal_rates['A'], 5 / 1, 1)
        self.assertAlmostEqual(self._signal_rates['B'], 3 / 1, 1)

        # Wait one more second, make sure rates are about half
        sleep(1)
        # One per group - twice!
        self.assert_num_signals_notified(4)
        self.assertAlmostEqual(self._signal_rates['A'], 5 / 2, 1)
        self.assertAlmostEqual(self._signal_rates['B'], 3 / 2, 1)

        # Add some As, then wait one more second, now we should be every
        # 2 seconds from here on
        # So we only have these As, and no more Bs
        blk.process_signals(self._get_signals('A', 6))
        sleep(1)
        self.assertAlmostEqual(self._signal_rates['A'], 6 / 2, 1)
        self.assertAlmostEqual(self._signal_rates['B'], 0 / 2, 1)

        blk.stop()

    def _get_signals(self, group, count):
        return [Signal({"group": group, "val": val}) for val in range(count)]

    def signals_notified(self, signals, output_id='default'):
        for signal in signals:
            self._signal_rates[signal.group] = signal.rate
