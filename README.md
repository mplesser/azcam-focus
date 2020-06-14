# focus

*focus* is an azcam package to control focus observations used to determine optimal instrument or telescope focus positions.

`focus` is usually executed in the console window although a server-side version is available on some systems. `focus` is an instance of the *Focus* or *FocusServer* classes.

**Usage**:

`focus.command(parameters...)`

**Example**:

   `focus.set_pars()`  
   `focus.run()`

**Notes**:

   Parameters may be changed from the command line as:
   `focus.number_exposures=7` or using `focus.set_pars()`.

**Parameter Examples**:

<dl>
  <dt><strong>focus.number_exposures = 7</strong></dt>
  <dd>Number of exposures in focus sequence</dd>

  <dt><strong>focus.focus_step = 30</strong></dt>
  <dd>Number of focus steps between each exposure in a frame</dd>

  <dt><strong>focus.detector_shift = 10</strong></dt>
  <dd>Number of rows to shift detector for each focus step</dd>

  <dt><strong>focus.focus_position</strong></dt>
  <dd>Current focus position</dd>

  <dt><strong>focus.exposure_time = 1.0</strong></dt>
  <dd>Exposure time (seconds)</dd>

  <dt><strong>focus.focus_component = "instrument"</strong></dt>
  <dd>Focus component for motion - "instrument" or "telescope"</dd>

  <dt><strong>focus.focus_type = "absolute"</strong></dt>
  <dd>Focus type, "absolute" or "step"</dd>

  <dt><strong>focus.set_pars_called = 1</strong></dt>
  <dd>Flag to not prompt for focus position</dd>

  <dt><strong>focus.move_delay = 3</strong></dt>
  <dd>Delay in seconds between focus moves</dd>
</dl>

