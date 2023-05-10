import platform
from pathlib import Path

import pycc

from three_d_fin.cloudcompare.plugin_processing import CloudComparePluginProcessing
from three_d_fin.gui.layout import Application


class ThreeDFinCC(pycc.PythonPluginInterface):
    """Define a CloudCompare-PythonPlugin Plugin (sic.)."""

    def __init__(self):
        """Construct the object."""
        pycc.PythonPluginInterface.__init__(self)
        # Be sure to load our custom colorscale
        color_scale_path = str(
            (Path(__file__).parents[1] / "assets" / "3dfin_color_scale.xml").resolve()
        )
        pycc.ccColorScale.LoadFromXML(color_scale_path)

    def getIcon(self) -> str:
        """Get the path to the plugin icon.

        Returns
        -------
        path : str
            the string representation of the path to the plugin icon
        """
        return str(
            (Path(__file__).parents[1] / "assets" / "3dfin_logo_plugin.png").resolve()
        )

    def getActions(self) -> list[pycc.Action]:
        """List of actions exposed by the plugin."""
        return [
            pycc.Action(name="3D Forest INventory", icon=self.getIcon(), target=main)
        ]


def _create_app_and_run(
    plugin_processing: CloudComparePluginProcessing, scalar_fields: list[str]
):
    """Encapsulate the 3DFin GUI and processing.

    It also embed a custom fix for the HiDPI support that is broken when using tk
    under the CloudCompare runtime. This function allow to run the fix and the app
    on a dedicated thread thanx to pycc.RunInThread.

    Parameters
    ----------
    plugin_processing : CloudComparePluginProcessing
        The instance of FinProcessing dedicated to CloudCompare (as a plugin)
    scalar_fields : list[str]
        A list of scalar field names. These list will feed the dropdown menu
        inside the 3DFin GUI.
    """
    # FIX for HiDPI support on windows 10+
    # The "bug" was sneaky for two reasons:
    # - First, you should turn the DpiAwareness value to a counter intuitive value
    # in other context you would assume to turn Dpi awarness at least >= 1 (PROCESS_SYSTEM_DPI_AWARE)
    # but here, with TK the right value is 0 (PROCESS_DPI_UNAWARE) maybe because DPI is handled by CC process
    # - Second, you can't use the usual SetProcessDpiAwareness function here because it could not be redefined
    # when defined once somewhere (TODO: maybe we could try to redefine it at startup of CC-PythonPlugin see if it works)
    # so we have to force it for the current thread with this one:
    # TODO: we do not know how it's handled in other OSes.
    import ctypes

    awareness_code = ctypes.c_int()
    if platform.system() == "Windows" and (
        platform.release() == "10" or platform.release() == "11"
    ):
        import ctypes.wintypes  # reimport here, because sometimes it's not initialized

        ctypes.windll.shcore.GetProcessDpiAwareness(0, ctypes.byref(awareness_code))
        if awareness_code.value > 0:
            ctypes.windll.user32.SetThreadDpiAwarenessContext(
                ctypes.wintypes.HANDLE(-1)
            )
    fin_app = Application(
        plugin_processing, file_externally_defined=True, cloud_fields=scalar_fields
    )
    fin_app.run()


def main():
    """3DFin CloudCompare Plugin main action."""
    cc = pycc.GetInstance()

    entities = cc.getSelectedEntities()

    if not entities or len(entities) > 1:
        raise RuntimeError("Please select one point cloud")

    point_cloud = entities[0]

    if not isinstance(point_cloud, pycc.ccPointCloud):
        raise RuntimeError("Selected entity should be a point cloud")

    # List all scalar fields to feed dropdown menu in the interface
    scalar_fields: list[str] = []
    for i in range(point_cloud.getNumberOfScalarFields()):
        scalar_fields.append(point_cloud.getScalarFieldName(i))

    # TODO: Handle big coodinates (could be tested but maybe wait for CC API update).
    plugin_functor = CloudComparePluginProcessing(cc, point_cloud)

    cc.freezeUI(True)
    try:
        pycc.RunInThread(_create_app_and_run, plugin_functor, scalar_fields)
        # _create_app_and_run(plugin_functor, scalar_fields)
    except Exception:
        raise RuntimeError(
            "Something went wrong!"
        ) from None  # TODO: Catch exceptions into modals.
    finally:
        cc.freezeUI(False)
        cc.updateUI()