import os
import corpkit
import dictionaries
path_to_corpkit = os.path.dirname(corpkit.__file__)
thepath, corpkitname = os.path.split(path_to_corpkit)
os.environ["PATH"] += os.pathsep + path_to_corpkit + os.pathsep + os.path.join(thepath, 'dictionaries')

from process_types import processes
