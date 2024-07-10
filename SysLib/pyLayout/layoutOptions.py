#--- coding=utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 20231107

from .common.complexDict import ComplexDict

options = ComplexDict({
    
    "H3DL_CutExpansion": "10mm",
    "H3DL_backdrillStub": "8mil",
    #--- Net classify
    "H3DL_PowerNetReg": ".*VDD.*,.*VCC.*",
    "H3DL_GNDNetReg": ".*GND.*,.*VSS.*",
    "H3DL_SignetNetReg": "None",
    "H3DL_IgnoreNetReg": ".*NC.*",
    #--- RLC
    "H3DL_ResistorReg": "R\\d+",
    "H3DL_InductorReg": "L\\d+",
    "H3DL_CapacitorReg": "C\\d+",
    #--- Solder
    "H3DL_solderBallHeightRatio":0.7,
    "H3DL_solderBallWidthRatio":0.6,
    "H3DL_Default":None
})

