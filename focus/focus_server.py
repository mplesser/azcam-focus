"""
Contains the FocusServer class.

This is the server-side version.
"""

import time

import azcam


class FocusServer(object):
    """
    Focus class for focusing a camera.

    Either the telescope or instrument may be moved for focus adjustment.
    May be used as a server or client script.
    The focus sequence performed is:
    --- expose
    --- move focus
    --- shift detector (2x last time)
    --- <repeat above steps>
    --- readout
    --- return to starting focus position
    --- save image
    """

    def __init__(self):

        #: Number of exposures in focus sequence
        self.number_exposures = 7
        #: Number of focus steps between each exposure in a frame
        self.focus_step = 30
        #: Number of rows to shift detector for each focus step
        self.detector_shift = 10
        #: current focus position
        self.focus_position = 0
        #: exposure time
        self.exposure_time = 1.0
        # focus component for motion - instrument or telescope
        self.focus_component = "instrument"
        # focus type, absolute or step
        self.focus_type = "absolute"
        # flag to not prompt
        self.set_pars_called = 0
        # delay in seconds
        self.move_delay = 3

        self.exposure = azcam.db.exposure

    def reset(self):
        """
        Reset focus object to default values.
        """

        self.exposure_time = 1.0
        self.number_exposures = 7
        self.focus_step = 30
        self.detector_shift = 10
        self.set_pars_called = 0

        return

    def abort(self):
        """
        Abort focus exposure.
        """

        self.exposure.abort()

        return

    def set_pars(
        self,
        exposure_time: float,
        number_exposures: int = 7,
        focus_step: float = 30,
        detector_shift: int = 10,
    ):
        """
        Set focus related parameters.
        """

        self.exposure_time = float(exposure_time)
        self.number_exposures = int(number_exposures)
        self.focus_step = float(focus_step)
        self.detector_shift = int(detector_shift)

        self.set_pars_called = 1

        return

    def run(
        self,
        exposure_time="prompt",
        number_exposures="prompt",
        focus_step="prompt",
        detector_shift="prompt",
    ):
        """
        Execute the focus script.
        Parameters can be "default", "prompt", or a value.
        Default values are used in focus.set_pars() was previously called.
        :param number_exposures: Number of exposures in focus sequence.
        :param focus_steps: Number of focus steps between each exposure in a frame.
        :param detector_shift: Number of rows to shift detector for each focus step.
        :param exposuretime: Exposure time i seconds.
        :return: None
        """

        if self.set_pars_called:
            pass

        else:
            if exposure_time == "prompt":
                self.exposure_time = float(
                    azcam.utils.prompt("Exposure time (sec)", self.exposure_time)
                )
            if number_exposures == "prompt":
                self.number_exposures = float(
                    azcam.utils.prompt("Number of exposures", self.number_exposures)
                )
            if focus_step == "prompt":
                self.focus_step = float(
                    azcam.utils.prompt("Focus step size", self.focus_step)
                )
            if detector_shift == "prompt":
                self.detector_shift = float(
                    azcam.utils.prompt(
                        "Number detector rows to shift", self.detector_shift
                    )
                )

        AbortFlag = 0

        # exposure time - zero not allowed for focus
        self.exposure.set_exposuretime(self.exposure_time)
        ExpTime = self.exposure.get_exposuretime()
        if ExpTime < 0.001:
            azcam.AzcamWarning("do not focus with zero exposure time")
            return

        # save parameters to be changed
        root = azcam.utils.get_par("imageroot")
        includesequencenumber = azcam.utils.get_par("imageincludesequencenumber")
        autoname = azcam.utils.get_par("imageautoname")
        autoincrementsequencenumber = azcam.utils.get_par(
            "imageautoincrementsequencenumber"
        )
        title = azcam.utils.get_par("imagetitle")
        testimage = azcam.utils.get_par("imagetest")
        imagetype = azcam.utils.get_par("imagetype")

        azcam.utils.set_par("imageroot", "focus.")
        azcam.utils.set_par("imageincludesequencenumber", 1)
        azcam.utils.set_par("imageautoname", 0)
        azcam.utils.set_par("imageautoincrementsequencenumber", 1)
        azcam.utils.set_par("imagetest", 0)
        azcam.utils.set_par("imageoverwrite", 1)

        # start
        self.exposure.begin(self.exposure_time, "object", "Focus")

        # loop over FocusNumber integrations
        FocusCurrentExposure = 1

        # get starting focus
        FocusCurrentPosition = self.focus_component.get_focus()
        FocusStartingValue = FocusCurrentPosition

        nsteps = 0  # total number of focus steps
        while FocusCurrentExposure <= self.number_exposures:

            # check for abort
            k = azcam.utils.check_keyboard(0)
            ab = azcam.db.abortflag
            if k == "q" or ab:
                AbortFlag = 1
                break

            if FocusCurrentExposure > 1:
                if self.focus_type == "step":
                    self.focus_component.set_focus(self.focus_step, 0, self.focus_type)
                    nsteps += self.focus_step
                elif self.focus_type == "absolute":
                    self.focus_component.set_focus(
                        FocusCurrentPosition + self.focus_step,
                        0,
                        self.focus_type,
                    )
                self.focus_delay()
                reply = self.focus_component.get_focus()
                FocusCurrentPosition = reply
                FocusCurrentPosition = float(FocusCurrentPosition)

                # shift detector
                self.controller.parshift(self.detector_shift)
                if FocusCurrentExposure == self.number_exposures:
                    azcam.log("Last exposure, double shifting")
                    self.controller.parshift(self.detector_shift)

            azcam.log(
                "Next exposure is %d of %d at focus position %.3f"
                % (FocusCurrentExposure, self.number_exposures, FocusCurrentPosition)
            )

            # integrate
            azcam.log("Integrating")
            try:
                self.exposure.integrate()
            except azcam.AzcamError:
                azcam.log("Focus exposure aborted")
                self.focus_component.set_focus(FocusStartingValue, 0, self.focus_type)
                azcam.utils.set_par("imageroot", root)
                azcam.utils.set_par("imageincludesequencenumber", includesequencenumber)
                azcam.utils.set_par("imageautoname", autoname)
                azcam.utils.set_par(
                    "imageautoincrementsequencenumber", autoincrementsequencenumber
                )
                azcam.utils.set_par("imagetest", testimage)
                azcam.utils.set_par("imagetitle", title)
                azcam.utils.set_par("imagetype", imagetype)
                fp = self.focus_component.get_focus()
                azcam.log("Current focus: %.3f" % fp)
                return

            # increment focus number
            FocusCurrentExposure += 1

        # set focus back to starting position
        azcam.log("Returning focus to starting value %.3f" % FocusStartingValue)
        if self.focus_type == "step":
            steps = -1 * nsteps
            self.focus_component.set_focus(
                steps, 0, self.focus_component, self.focus_type
            )
        elif self.focus_type == "absolute":
            self.focus_component.set_focus(FocusStartingValue, 0, self.focus_type)
        self.focus_delay()
        fp = self.focus_component.get_focus()
        azcam.log("Current focus: %.3f" % fp)

        if not AbortFlag:
            # readout and finish
            azcam.log("Reading out")
            self.exposure.readout()
            self.exposure.end()
        else:
            azcam.utils.set_par("ExposureFlag", azcam.db.exposureflags["NONE"])

        # finish
        azcam.utils.set_par("imageroot", root)
        azcam.utils.set_par("imageincludesequencenumber", includesequencenumber)
        azcam.utils.set_par("imageautoname", autoname)
        azcam.utils.set_par(
            "imageautoincrementsequencenumber", autoincrementsequencenumber
        )
        azcam.utils.set_par("imagetest", testimage)
        azcam.utils.set_par("imagetitle", title)
        azcam.utils.set_par("imagetype", imagetype)

        return

    def focus_delay(self):
        """
        Delays until focus stops moving.

        Delay may be set to appropriate value for each focus mechanism.
        """

        time.sleep(self.move_delay)

        return


if __name__ == "__main__":
    print("Use focus.run() instead")
