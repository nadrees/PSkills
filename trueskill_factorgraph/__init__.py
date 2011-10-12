import os
import sys

PATH = os.path.realpath(__file__)
INCLUDE_PATH = os.path.dirname(PATH) + "/../"
INCLUDE_PATH = os.path.abspath(INCLUDE_PATH)

sys.path.append(PATH)
sys.path.append(INCLUDE_PATH)

import factors
import layers
import ts_factorgraph
