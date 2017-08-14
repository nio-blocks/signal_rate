SignalRate
==========

Pump in signals, see how fast you are pumping them in.

Properties
----------
- **averaging_interval**: The interval over which to calculate frequencies.
- **backup_interval**: Interval to backup to persistence.
- **group_by**: The value by which signals are grouped. Output signals will have *group* set to this value.
- **load_from_persistence**: hether to load the signal rate state from persistence.
- **report_interval**: The interval at which to report frequencies.

Inputs
------

Any list of signals.

Outputs
-------

A signal at the specified reporting interval with the following fields:

-   **rate**: The rate per second of the incoming signals
-   **group**: The group that the counts relate to as defined by **group_by**.

Commands
--------
- **groups**: View current state of the block's groups

Dependencies
------------
