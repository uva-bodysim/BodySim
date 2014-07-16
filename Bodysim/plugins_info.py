"""Universal container for plugin information."""

import Bodysim.file_operations

plugins_tuple = Bodysim.file_operations.get_plugins(True)
# A map of plugins available to simulate.
plugins = plugins_tuple[0]
# A map of the units corresponding to each variable for each simulation.
unit_map = plugins_tuple[1]
