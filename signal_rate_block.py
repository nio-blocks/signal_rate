from copy import copy
from collections import defaultdict, deque
from time import time as _time
from threading import Lock

from nio.block.base import Block
from nio.signal.base import Signal
from nio.properties import TimeDeltaProperty, VersionProperty
from nio.modules.scheduler import Job
from nio.block.mixins import GroupBy, Persistence


class SignalRate(GroupBy, Persistence, Block):

    report_interval = TimeDeltaProperty(default={"seconds": 1},
                                        title="Report Interval")
    averaging_interval = TimeDeltaProperty(default={"seconds": 5},
                                           title="Averaging Interval")
    version = VersionProperty("0.1.1")

    def __init__(self):
        super().__init__()
        self._signal_counts = defaultdict(deque)
        self._signals_lock = Lock()
        self._job = None
        self._start_time = None
        self._averaging_seconds = None

    def persisted_values(self):
        """ Overridden from persistence mixin """
        return ['_start_time', '_signal_counts']

    def configure(self, context):
        super().configure(context)
        # This is just for backwards compatability with persistence
        if self._signal_counts.default_factory == list:
            self._signal_counts.default_factory = deque
            for group in self._signal_counts:
                self._signal_counts[group] = deque(self._signal_counts[group])

    def start(self):
        super().start()
        # use _start_time if it was loaded from persistence
        self._start_time = self._start_time or _time()
        self._averaging_seconds = self.averaging_interval().total_seconds()
        self._job = Job(self.report_frequency, self.report_interval(), True)

    def process_signals(self, signals, input_id='default'):
        # Record the count for each group in this list of signals
        self.for_each_group(self.record_count, signals)

    def record_count(self, signals, group):
        """ Save the time and the counts for each group received """
        with self._signals_lock:
            self._signal_counts[group].append((_time(), len(signals)))

    def report_frequency(self):
        signals = []

        self.for_each_group(self.get_frequency, sigs_out=signals)

        self.logger.debug(
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
        total_count = sum(grp[1] for grp in signals)

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
        while len(signal_counts) and \
                ctime - signal_counts[0][0] >= self._averaging_seconds:
            signal_counts.popleft()
        return signal_counts

    def stop(self):
        if self._job:
            self._job.cancel()
        super().stop()
