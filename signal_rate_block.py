from copy import copy
from collections import defaultdict
from time import time as _time
from nio.common.block.base import Block
from nio.common.discovery import Discoverable, DiscoverableType
from nio.common.signal.base import Signal
from nio.metadata.properties.timedelta import TimeDeltaProperty
from nio.modules.threading import Lock
from nio.modules.scheduler import Job
from .mixins.group_by.group_by_block import GroupBy


@Discoverable(DiscoverableType.block)
class SignalRate(GroupBy, Block):

    report_interval = TimeDeltaProperty(default={"seconds": 1},
                                        title="Report Interval")
    averaging_interval = TimeDeltaProperty(default={"seconds": 5},
                                           title="Averaging Interval")

    def __init__(self):
        super().__init__()
        self._signal_counts = defaultdict(list)
        self._signals_lock = Lock()
        self._job = None
        self._start_time = None
        self._averaging_seconds = None

    def start(self):
        self._start_time = _time()
        self._averaging_seconds = self.averaging_interval.total_seconds()
        self._job = Job(self.report_frequency, self.report_interval, True)

    def process_signals(self, signals, input_id='default'):
        # Record the count for each group in this list of signals
        self.for_each_group(self.record_count, signals)

    def record_count(self, signals, group):
        """ Save the time and the counts for each group received """
        with self._signals_lock:
            self._signal_counts[group].append((_time(), len(signals)))

    def report_frequency(self):
        signals = []

        self.for_each_group(self.get_frequency, kwargs={'sigs_out': signals})

        self._logger.debug(
            "Current counts: {}".format(self._signal_counts))

        if signals:
            self.notify_signals(signals)

    def get_frequency(self, group, sigs_out):
        """ Get the frequency for a group and add it to sigs_out """
        with self._signals_lock:
            ctime = _time()
            self._signal_counts[group] = self.trim_old_signals(
                self._signal_counts[group], ctime)

            signals = copy(self._signal_counts[group])

        # Add up all of our current counts
        total_count = sum([grp[1] for grp in signals])

        # If we haven't reached a full period, divide by elapsed time
        rate = total_count / min(
            ctime - self._start_time,
            self._averaging_seconds)

        sigs_out.append(Signal({
            "group": group,
            "rate": rate
        }))

    def trim_old_signals(self, signal_counts, ctime):
        """ Take some signal counts and get rid of old ones """
        return [(ct, c) for (ct, c) in signal_counts
                if ctime - ct < self._averaging_seconds]

    def stop(self):
        if self._job:
            self._job.cancel()
        super().stop()
