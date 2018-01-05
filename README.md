SignalRate
==========
The SignalRate block calculates the rate (number of signals per **averaging interval** at which incoming signals enter the block.

Properties
----------
- **averaging_interval**: The interval over which to calculate signal rate.
- **backup_interval**: An interval of time that specifies how often persisted data is saved.
- **group_by**: The signal attribute on the incoming signal whose values will be used to define groups on the outgoing signal.
- **load_from_persistence**: If `True`, the block’s state will be saved when the block is stopped, and reloaded once the block is restarted.
- **report_interval**: The interval at which to report the signal rate.

Inputs
------
- **default**: Any list of signals.

Outputs
-------
- **default**: A signal at the specified reporting interval with a **rate** and **group** attribute.

Commands
--------
- **groups**: View current state of the blocks groups

Dependencies
------------
None

