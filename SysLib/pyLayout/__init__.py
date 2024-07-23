
from .desktop import initializeDesktop,releaseDesktop
from .primitive.component import Components
from .primitive.pin import Pins
from .definition.net import Nets
from .definition.layer import Layers
from .definition.material import Materials
from .definition.variable import Variables
from .definition.setup import Setups
from .primitive.port import Ports
from .primitive.line import Lines
from .primitive.via import Vias
from .primitive.primitive import Objects3DL
from .definition.padStack import PadStacks
from .common.complexDict import ComplexDict
from .common.arrayStruct import ArrayStruct
from .common.common import *
from .definition.componentLib import ComponentDef
from .layoutOptions import options
from .postData.solution import Solutions

from .model3D.HFSS import HFSS

##log is a globle variable
from .common.common import log,isIronpython

from .pyLayout import Layout

# version = "V0.62 20240314"
version = "V0.11.1 20240723"
log.info("pyLayout Version: %s"%version)
log.info("the lastest release on: https://github.com/YongshengGuo/pyLayout")
log.setLogLevel(logLevel="INFO")
# log.setLogLevel(logLevel="DEBUG")
