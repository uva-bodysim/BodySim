"""
Universal container for plugin information. Singleton design anti-pattern :(.
"""

import Bodysim.file_operations

plugins_tuple = Bodysim.file_operations.get_plugins(True)
plugins = plugins_tuple[0]
unit_map = plugins_tuple[1]
