SignalRate
=======

Pump in signals, see how fast you are pumping them in.

Properties
--------------
-   **report_interval** (timedelta): The interval at which to report frequencies.
-   **averaging_interval** (timedelta): The interval over which to calculate frequencies.
-   **group_by**: Expression proprety. The value by which signals are grouped. Output signals will have *group* set to this value.


Dependencies
----------------
[GroupBy Block Supplement](https://github.com/nio-blocks/block_supplements/tree/master/group_by)

Commands
----------------
None

Input
-------
Any list of signals.

Output
---------

-   **rate**: The rate per second of the incoming signals
-   **group**: The group that the counts relate to as defined by **group_by**.
