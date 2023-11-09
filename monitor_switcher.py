# Automatically switch the Dell monitor to the correct input based on the KVM state
# Assume this will run on the desktop

from operator import is_
import monitorcontrol as mc
import subprocess
import time

desktop_inputs = {
    "S2721QS": {
        "name": "DP1",
        "value": mc.InputSource.DP1,
    },  # {"name": "HDMI2", "value":mc.InputSource.HDMI2}
    "FALCON": {"name": "ANALOG1", "value": mc.InputSource.COMPOSITE2},
}
laptop_inputs = {
    "S2721QS": {"name": "HDMI1", "value": mc.InputSource.HDMI1},
    "FALCON": {"name": "ANALOG1", "value": mc.InputSource.COMPOSITE1},
}


def is_desktop_selected() -> bool:
    # we are going to determine whether this is the selected device based on whether we see the mouse
    run = subprocess.run(["powershell.exe", ".\\checkmouse.ps1"], capture_output=True)
    # if a device matching the filter 'HID-complient Mouse' is found, then there will be text in stdout
    # otherwise, there will be no text
    return len(run.stdout) > 0


last_loop_desktop_selected = is_desktop_selected()
while True:
    desktop_selected = is_desktop_selected()
    if desktop_selected == last_loop_desktop_selected:
        continue
    last_loop_desktop_selected = desktop_selected
    # the "with monitor" statement often fails if we catch it while the second monitor is switching, so we'll wrap it in a try catch
    try:
        # The monitorcontrol library wants us to use this generator to list the two monitors
        # we then have to use the "with monitor" statement to call get_vcp_capabilities to identify the Dell
        for monitor in mc.get_monitors():
            with monitor:
                capabilities = monitor.get_vcp_capabilities()
                model = capabilities.get("model", None)
                if model == "":
                    continue
                if (
                    model == "FALCON"
                ):  # We'll skip doing input changing on the samsung monitor because it's too slow
                    continue
                desktop_input = desktop_inputs[model]
                laptop_input = laptop_inputs[model]
                current_source = monitor.get_input_source()

                if desktop_selected and (
                    monitor.get_input_source() != desktop_input["value"]
                ):
                    monitor.set_input_source(desktop_input["name"])
                    print("switching to desktop input")

                if (not desktop_selected) and (
                    monitor.get_input_source() != laptop_input["value"]
                ):
                    monitor.set_input_source(laptop_input["name"])
                    print("switching to laptop input")
                print(
                    f"model = {model}, current source = {current_source}, desktop_selected = {desktop_selected}, desired source = {desktop_input['value']}"
                )
    except mc.vcp.vcp_abc.VCPError:
        print("VCP Error!")
        pass
