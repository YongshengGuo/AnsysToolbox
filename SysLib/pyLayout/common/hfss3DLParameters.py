#coding:utf-8
#--- coding=utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 20230410
'''
用于存放HFSS复杂的Array对象，简化程序的可读性。此模块可以被其它模块引用调用预定义的Array对象。
Array List的处理建议使用arrayStruct模块
'''


'''*** 
hfss Setup array parameters'''
hfssSetup = [
    "NAME:HFSS_Setup4",
        [
            "NAME:Properties",
            "Enable:="        , "true"
        ],
        "CustomSetup:="        , False,
        "AutoSetup:="        , False,
        "SliderType:="        , "Balanced",
        "SolveSetupType:="    , "HFSS",
        "PercentRefinementPerPass:=", 30,
        "MinNumberOfPasses:="    , 1,
        "MinNumberOfConvergedPasses:=", 1,
        "UseDefaultLambda:="    , True,
        "UseMaxRefinement:="    , False,
        "MaxRefinement:="    , 1000000,
        "SaveAdaptiveCurrents:=", False,
        "SaveLastAdaptiveRadFields:=", False,
        "UseConvergenceMatrix:=", False,
        "AllEntries:="        , False,
        "AllDiagEntries:="    , False,
        "AllOffDiagEntries:="    , False,
        "MagMinThreshold:="    , 0.01,
        "ProdMajVerID:="    , -1,
        "ProjDesignSetup:="    , "",
        "ProdMinVerID:="    , -1,
        "Refine:="        , False,
        "Frequency:="        , "10GHz",
        "LambdaRefine:="    , True,
        "MeshSizeFactor:="    , 3,
        "QualityRefine:="    , True,
        "MinAngle:="        , "15deg",
        "UniformityRefine:="    , False,
        "MaxRatio:="        , 2,
        "Smooth:="        , False,
        "SmoothingPasses:="    , 5,
        "UseEdgeMesh:="        , False,
        "UseEdgeMeshAbsLength:=", False,
        "EdgeMeshRatio:="    , 0.1,
        "EdgeMeshAbsLength:="    , "1000mm",
        "LayerProjectThickness:=", "0meter",
        "UseDefeature:="    , True,
        "UseDefeatureAbsLength:=", False,
        "DefeatureRatio:="    , 1E-06,
        "DefeatureAbsLength:="    , "0mm",
        "InfArrayDimX:="    , 0,
        "InfArrayDimY:="    , 0,
        "InfArrayOrigX:="    , 0,
        "InfArrayOrigY:="    , 0,
        "InfArraySkew:="    , 0,
        "ViaNumSides:="        , 8,
        "ViaMaterial:="        , "copper",
        "Style25DVia:="        , "Mesh",
        "Replace3DTriangles:="    , True,
        "LayerSnapTol:="    , "1e-05",
        "ViaDensity:="        , 0,
        "HfssMesh:="        , True,
        "Q3dPostProc:="        , False,
        "UnitFactor:="        , 1000,
        "Verbose:="        , False,
        "NumberOfProcessors:="    , 0,
        "SmallVoidArea:="    , -0,
        "RemoveFloatingGeometry:=", False,
        "HealingOption:="    , 1,
        "InclBBoxOption:="    , 1,
        "ModelType:="        , 0,
        "ICModeAuto:="        , 1,
        "ICModeLength:="    , "50nm",
        [
            "NAME:AuxBlock"
        ],
        "DoAdaptive:="        , True,
        "Color:="        , [            "R:="            , 0,            "G:="            , 0,            "B:="            , 0],
        [
            "NAME:AdvancedSettings",
            "AccuracyLevel:="    , 2,
            "GapPortCalibration:="    , True,
            "ReferenceLengthRatio:=", 0.25,
            "RefineAreaRatio:="    , 4,
            "DRCOn:="        , False,
            "FastSolverOn:="    , False,
            "StartFastSolverAt:="    , 3000,
            "LoopTreeOn:="        , True,
            "SingularElementsOn:="    , False,
            "UseStaticPortSolver:="    , False,
            "UseThinMetalPortSolver:=", False,
            "ComputeBothEvenAndOddCPWModes:=", False,
            "ZeroMetalLayerThickness:=", 0,
            "ThinDielectric:="    , 0,
            "UseShellElements:="    , False,
            "SVDHighCompression:="    , False,
            "NumProcessors:="    , 1,
            "SolverType:="        , "Direct Solver",
            "UseHfssMUMPSSolver:="    , True,
            "RelativeResidual:="    , 1E-06,
            "EnhancedLowFreqAccuracy:=", False,
            "OrderBasis:="        , 1,
            "MaxDeltaZo:="        , 2,
            "UseRadBoundaryOnPorts:=", False,
            "SetTrianglesForWavePort:=", False,
            "MinTrianglesForWavePort:=", 100,
            "MaxTrianglesForWavePort:=", 500,
            "numprocessorsdistrib:=", 1,
            "CausalMaterials:="    , True,
            "enabledsoforopti:="    , True,
            "usehfsssolvelicense:="    , False,
            "CircuitSparamDefinition:=", False,
            "CircuitIntegrationType:=", "FFT",
            "DesignType:="        , "Generic",
            "MeshingMethod:="    , "Phi",
            "EnableDesignIntersectionCheck:=", True,
            "UseAlternativeMeshMethodsAsFallBack:=", True,
            "ModeOption:="        , "General mode",
            "BroadbandFreqOption:="    , "AutoMaxFreq",
            "BroadbandMaxNumFreq:="    , 5,
            "SaveADP:="        , False,
            "UseAdvancedDCExtrap:="    , False,
            "PhiMesherDeltaZRatio:=", 100000
        ],
        [
            "NAME:CurveApproximation",
            "ArcAngle:="        , "30deg",
            "StartAzimuth:="    , "0deg",
            "UseError:="        , False,
            "Error:="        , "0meter",
            "MaxPoints:="        , 8,
            "UnionPolys:="        , True,
            "Replace3DTriangles:="    , True
        ],
        [
            "NAME:Q3D_DCSettings",
            "SolveResOnly:="    , True,
            [
                "NAME:Cond",
                "MaxPass:="        , 10,
                "MinPass:="        , 1,
                "MinConvPass:="        , 1,
                "PerError:="        , 1,
                "PerRefine:="        , 30
            ],
            [
                "NAME:Mult",
                "MaxPass:="        , 1,
                "MinPass:="        , 1,
                "MinConvPass:="        , 1,
                "PerError:="        , 1,
                "PerRefine:="        , 30
            ],
            "Solution Order:="    , "Normal"
        ],
        [
            "NAME:AdaptiveSettings",
            "DoAdaptive:="        , True,
            "SaveFields:="        , False,
            "SaveRadFieldsOnly:="    , False,
            "MaxRefinePerPass:="    , 30,
            "MinPasses:="        , 1,
            "MinConvergedPasses:="    , 1,
            "AdaptType:="        , "kSingle",
            "Basic:="        , True,
            [
                "NAME:SingleFrequencyDataList",
                [
                    "NAME:AdaptiveFrequencyData",
                    "AdaptiveFrequency:="    , "15GHz",
                    "MaxDelta:="        , "0.05",
                    "MaxPasses:="        , 20,
                    "Expressions:="        , []
                ]
            ],
            [
                "NAME:BroadbandFrequencyDataList",
                [
                    "NAME:AdaptiveFrequencyData",
                    "AdaptiveFrequency:="    , "5GHz",
                    "MaxDelta:="        , "0.05",
                    "MaxPasses:="        , 20,
                    "Expressions:="        , []
                ],
                [
                    "NAME:AdaptiveFrequencyData",
                    "AdaptiveFrequency:="    , "10GHz",
                    "MaxDelta:="        , "0.05",
                    "MaxPasses:="        , 20,
                    "Expressions:="        , []
                ]
            ],
            [
                "NAME:MultiFrequencyDataList",
                [
                    "NAME:AdaptiveFrequencyData",
                    "AdaptiveFrequency:="    , "5GHz",
                    "MaxDelta:="        , "0.05",
                    "MaxPasses:="        , 20,
                    "Expressions:="        , []
                ],
                [
                    "NAME:AdaptiveFrequencyData",
                    "AdaptiveFrequency:="    , "10GHz",
                    "MaxDelta:="        , "0.02",
                    "MaxPasses:="        , 20,
                    "Expressions:="        , []
                ]
            ]
        ]
    ]

'''*** 
hfss Setup sweep array parameters'''
hfssSweep = [
        "NAME:Sweep1",
        [
            "NAME:Properties",
            "Enable:="        , "true"
        ],
        [
            "NAME:Sweeps",
            "Variable:="        , "Sweep1",
            "Data:="        , "LIN 0GHz 20GHz 0.05GHz",
            "OffsetF1:="        , False,
            "Synchronize:="        , 0
        ],
        "GenerateSurfaceCurrent:=", False,
        "SaveRadFieldsOnly:="    , False,
        "ZoSelected:="        , False,
        "SAbsError:="        , 0.005,
        "ZoPercentError:="    , 1,
        "GenerateStateSpace:="    , False,
        "EnforcePassivity:="    , True,
        "PassivityTolerance:="    , 0.0001,
        "UseQ3DForDC:="        , False,
        "ResimulateDC:="    , False,
        "MaxSolutions:="    , 250,
        "InterpUseSMatrix:="    , True,
        "InterpUsePortImpedance:=", True,
        "InterpUsePropConst:="    , True,
        "InterpUseFullBasis:="    , True,
        "AdvDCExtrapolation:="    , False,
        "MinSolvedFreq:="    , "0.01GHz",
        "AutoSMatOnlySolve:="    , True,
        "MinFreqSMatrixOnlySolve:=", "1MHz",
        "CustomFrequencyString:=", "",
        "AllEntries:="        , False,
        "AllDiagEntries:="    , False,
        "AllOffDiagEntries:="    , False,
        "MagMinThreshold:="    , 0.01,
        "FreqSweepType:="    , "kInterpolating"
    ]


'''*** 
siwave Setup array parameters'''
siwavesetup =    [
        "NAME:SIwaveSYZ1",
        [
            "NAME:Properties",
            "Enable:="        , "true"
        ],
        "CustomSetup:="        , False,
        "SolveSetupType:="    , "SIwave",
        "Color:="        , [            "R:="            , 0,            "G:="            , 0,            "B:="            , 0],
        "Position:="        , 0,
        "SimSetupType:="    , "kSIwave",
        [
            "NAME:SimulationSettings",
            "Enabled:="        , True,
            "UseSISettings:="    , True,
            "UseCustomSettings:="    , False,
            "SISliderPos:="        , 1,
            "PISliderPos:="        , 1,
            [
                "NAME:SIWAdvancedSettings",
                "IncludeCoPlaneCoupling:=", True,
                "IncludeInterPlaneCoupling:=", False,
                "IncludeSplitPlaneCoupling:=", True,
                "IncludeFringeCoupling:=", True,
                "IncludeTraceCoupling:=", True,
                "XtalkThreshold:="    , "-34",
                "MaxCoupledLines:="    , 12,
                "MinVoidArea:="        , "2mm2",
                "MinPadAreaToMesh:="    , "20.377830577718mm2",
                "MinPlaneAreaToMesh:="    , "3.47856782981302e-05mm2",
                "SnapLengthThreshold:="    , "2.5um",
                "MeshAutoMatic:="    , True,
                "MeshFrequency:="    , "4GHz",
                "ReturnCurrentDistribution:=", False,
                "IncludeVISources:="    , False,
                "IncludeInfGnd:="    , False,
                "InfGndLocation:="    , "0mm",
                "PerformERC:="        , False,
                "IgnoreNonFunctionalPads:=", True
            ],
            [
                "NAME:SIWDCSettings",
                "UseDCCustomSettings:="    , False,
                "PlotJV:="        , True,
                "ComputeInductance:="    , False,
                "ContactRadius:="    , "0.1mm",
                "DCSliderPos:="        , 1
            ],
            [
                "NAME:SIWDCAdvancedSettings",
                "DcMinPlaneAreaToMesh:=", "1.0188915288859mm2",
                "DcMinVoidAreaToMesh:="    , "0.000556570852770083mm2",
                "MaxInitMeshEdgeLength:=", "5897.9384786661mm2",
                "PerformAdaptiveRefinement:=", True,
                "MaxNumPasses:="    , 5,
                "MinNumPasses:="    , 1,
                "PercentLocalRefinement:=", 20,
                "EnergyError:="        , 2,
                "MeshBws:="        , True,
                "RefineBws:="        , False,
                "MeshVias:="        , True,
                "RefineVias:="        , False,
                "NumBwSides:="        , 8,
                "NumViaSides:="        , 8
            ]
        ],
        [
            "NAME:SweepDataList"
        ]
    ]

'''*** 
hfss Setup sweep array parameters'''
siwaveSweep = [
        "NAME:Sweep1",
        [
            "NAME:Properties",
            "Enable:="        , "true"
        ],
        [
            "NAME:Sweeps",
            "Variable:="        , "SIwaveSweep1",
            "Data:="        , "LIN 0MHz 10GHz 0.01GHz",
            "OffsetF1:="        , False,
            "Synchronize:="        , 0
        ],
        "Name:="        , "Sweep1",
        "Enabled:="        , True,
        "FreqSweepType:="    , "kInterpolating",
        "IsDiscrete:="        , False,
        "UseQ3DForDC:="        , False,
        "SaveFields:="        , False,
        "SaveRadFieldsOnly:="    , False,
        "RelativeSError:="    , 0.001,
        "EnforceCausality:="    , False,
        "EnforcePassivity:="    , True,
        "PassivityTolerance:="    , 0.0001,
        "FrequencyString:="    , "LIN 0MHz 10GHz 0.01GHz",
        "ComputeDCPoint:="    , False,
        "SIwaveWith3DDDM:="    , False,
        "UseHFSSSolverRegions:=", False,
        "UseHFSSSolverRegionSchGen:=", False,
        "UseHFSSSolverRegionParallelSolve:=", False,
        "NumParallelHFSSRegions:=", 1,
        "HFSSSolverRegionsSetupName:=", "<default>",
        "HFSSSolverRegionsSweepName:=", "<default>",
        "AutoSMatOnlySolve:="    , True,
        "MinFreqSMatOnlySolve:=", "1MHz",
        "MaxSolutions:="    , 250,
        "InterpUseSMatrix:="    , True,
        "InterpUsePortImpedance:=", True,
        "InterpUsePropConst:="    , True,
        "InterpUseFullBasis:="    , True,
        "FastSweep:="        , False,
        "AdaptiveSampling:="    , False,
        "EnforceDCAndCausality:=", False,
        "AdvDCExtrapolation:="    , False,
        "MinSolvedFreq:="    , "0.01GHz",
        [
            "NAME:MatrixConvEntryList"
        ],
        [
            "NAME:HFSSRegionsParallelSimConfig"
        ],
        "Frequencies:=", []
    ]

'''*** 
changeLayers array parameters'''
changeLayers =  [
            "NAME:layers",
            "Mode:="        , "Laminate",
            [
                "NAME:pps"
            ]
        ]

#     ['Type: signal', 'TopBottomAssociation: Neither', 'Color: 6599935d', 'IsVisible: true', '  IsVisibleShape: true', '  IsVisiblePath: true', '  
#     IsVisiblePad: true', '  IsVisibleHole: true', '  IsVisibleComponent: true', 'IsLocked: false', 'LayerId: 1', 'Index: 1', 'LayerThickness: 4.826e-05', 
#     'IsIgnored: false', 'NumberOfSublayers: 1', 'Material0: copper', 'FillMaterial0: TOP_FILL', 'Thickness0: 0.04826mm', 'LowerElevation0: 1.98628mm']
#     
#     ['Type: dielectric', 'TopBottomAssociation: Neither', 'Color: 12632256d', 'IsVisible: false', '  IsVisibleShape: false', '  IsVisiblePath: false', '  
#     IsVisiblePad: false', '  IsVisibleHole: false', '  IsVisibleComponent: false', 'IsLocked: false', 'LayerId: 2', 'Index: 2', 'LayerThickness: 6.731e-05', 
#     'IsIgnored: false', 'NumberOfSublayers: 1', 'Material0: FR-4_3', 'FillMaterial0: ', 'Thickness0: 0.06731mm', 'LowerElevation0: 1.91897mm']
#     

signalLayer =  [
            "NAME:stackup layer",
            "Name:="        , "TOP",
            "ID:="            , 1,
            "Type:="        , "signal",
            "Top Bottom:="        , "neither",
            "Color:="        , 6599935,
            "Transparency:="    , 60,
            "Pattern:="        , 1,
            "VisFlag:="        , 127,
            "Locked:="        , False,
            "DrawOverride:="    , 0,
            "Zones:="        , [],
            [
                "NAME:Sublayer",
                "Thickness:="        , "1.2mil",
                "LowerElevation:="    , "2.08308mm",
                "Roughness:="        , "1um",
                "BotRoughness:="    , "1um",
                "SideRoughness:="    , "0um",
                "Material:="        , "copper",
                "FillMaterial:="    , "FR4_epoxy"
            ],
            "Usp:="            , False,
            [
                "NAME:Sp",
                "Sn:="            , "HFSS",
                "Sv:="            , "so(si=true, dt=2, dtv=\'0.01mm\')"
            ],
            [
                "NAME:Sp",
                "Sn:="            , "PlanarEM",
                "Sv:="            , "so(ifg=false, vly=false)"
            ],
            "Etch:="        , "0",
            "UseEtch:="        , False,
            "UseR:="        , False,
            "RMdl:="        , "Groiss",
            "NR:="            , "0um",
            "HRatio:="        , "1",
            "BRMdl:="        , "Groiss",
            "BNR:="            , "0um",
            "BHRatio:="        , "1",
            "SRMdl:="        , "Huray",
            "SNR:="            , "0.5um",
            "SHRatio:="        , "2.9"
        ]

dielectricLayer =   [
            "NAME:stackup layer",
            "Name:="        , "UNNAMED_000",
            "ID:="            , 0,
            "Type:="        , "dielectric",
            "Top Bottom:="        , "neither",
            "Color:="        , 12632256,
            "Transparency:="    , 60,
            "Pattern:="        , 1,
            "VisFlag:="        , 0,
            "Locked:="        , False,
            "DrawOverride:="    , 0,
            "Zones:="        , [],
            [
                "NAME:Sublayer",
                "Thickness:="        , "4mil",
                "LowerElevation:="    , "2.13134mm",
                "Roughness:="        , "0um",
                "BotRoughness:="    , "0um",
                "SideRoughness:="    , "0um",
                "Material:="        , "FR4_epoxy"
            ]
        ]

otherLayer = [
            "NAME:layer",
            "Name:="        , "Measures",
            "ID:="            , 15,
            "Type:="        , "measures",
            "Top Bottom:="        , "neither",
            "Color:="        , 4144959,
            "Transparency:="    , 60,
            "Pattern:="        , 1,
            "VisFlag:="        , 127,
            "Locked:="        , False,
            "DrawOverride:="    , 0
        ]

'''*** 
hfssExtents array parameters'''
hfssExtents = [
                "NAME:HfssExportInfo",
                "ScriptFileName:="    , "",
                "HfssFileName:="    , "",
                "Version:="        , 2,
                "ExtentType:="        , "BboxExtent",
                "BasePolygon:="        , "",
                "BasePolygonEDBUId:="    , -1,
                "DielExtentType:="    , "ConformalExtent",
                "DielBasePolygon:="    , "",
                "DielBasePolygonEDBUId:=", -1,
                "DielExt:="        , [            "Ext:="            , "0",            "Dim:="            , False],
                "HonorUserDiel:="    , True,
                "TruncAtGnd:="        , False,
                "AirHorExt:="        , [            "Ext:="            , "1.5mm",            "Dim:="            , True],
                "AirPosZExt:="        , [            "Ext:="            , "1.5mm",            "Dim:="            , True],
                "AirNegZExt:="        , [            "Ext:="            , "1.5mm",            "Dim:="            , True],
                "SyncZExt:="        , True,
                "OpenRegionType:="    , "Radiation",
                "UseRadBound:="        , True,
                "PMLVisible:="        , False,
                "OperFreq:="        , "5GHz",
                "RadLvl:="        , 0,
                "UseStackupForZExtFact:=", True,
                "Smooth:="        , True
            ]



'''*** 
padStackData array parameters'''
padStackData = [
    "NAME:VIA10-BGA",
    "ModTime:="        , 0,
    "Library:="        , "",
    "ModSinceLib:="        , False,
    "LibLocation:="        , "Project",
    [
        "NAME:psd",
        "nam:=", "VIA10-BGA",
        "lib:=", "",
        "mat:=", "",
        "plt:=", "100",
        [
            "NAME:pds",
            [
                "NAME:lgm",
                "lay:=", "TOP",
                "id:=", 1,
                "pad:=", ["shp:=", "Cir","Szs:=", ["20mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "ant:=", ["shp:=", "No","Szs:=", [],"X:=", "0mm","Y:=", "0mm","R:=", "0deg"],
                "thm:=", ["shp:=", "No","Szs:=", [],"X:=", "0mm","Y:=", "0mm","R:=", "0deg"],
                "X:=", "0",
                "Y:=", "0",
                "dir:=", "No"
            ],
            [
                "NAME:lgm",
                "lay:=", "Default",
                "id:=", 2,
                "pad:=", ["shp:=", "Cir","Szs:=", ["20mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "ant:=", ["shp:=", "Cir","Szs:=", ["30mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "thm:=", ["shp:=", "No","Szs:=", [],"X:=", "0mm","Y:=", "0mm","R:=", "0deg"],
                "X:=", "0",
                "Y:=", "0",
                "dir:=", "No"
            ],
            [
                "NAME:lgm",
                "lay:=", "GND02",
                "id:=", 3,
                "pad:=", ["shp:=", "Cir","Szs:=", ["20mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "ant:=", ["shp:=", "Cir","Szs:=", ["30mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "thm:=", ["shp:=", "No","Szs:=", [],"X:=", "0mm","Y:=", "0mm","R:=", "0deg"],
                "X:=", "0",
                "Y:=", "0",
                "dir:=", "No"
            ],
            [
                "NAME:lgm",
                "lay:=", "ART03",
                "id:=", 4,
                "pad:=", ["shp:=", "Cir","Szs:=", ["20mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "ant:=", ["shp:=", "Cir","Szs:=", ["30mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "thm:=", ["shp:=", "No","Szs:=", [],"X:=", "0mm","Y:=", "0mm","R:=", "0deg"],
                "X:=", "0",
                "Y:=", "0",
                "dir:=", "No"
            ],
            [
                "NAME:lgm",
                "lay:=", "GND04",
                "id:=", 5,
                "pad:=", ["shp:=", "Cir","Szs:=", ["20mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "ant:=", ["shp:=", "Cir","Szs:=", ["30mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "thm:=", ["shp:=", "No","Szs:=", [],"X:=", "0mm","Y:=", "0mm","R:=", "0deg"],
                "X:=", "0",
                "Y:=", "0",
                "dir:=", "No"
            ],
            [
                "NAME:lgm",
                "lay:=", "ART05",
                "id:=", 6,
                "pad:=", ["shp:=", "Cir","Szs:=", ["20mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "ant:=", ["shp:=", "Cir","Szs:=", ["30mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "thm:=", ["shp:=", "No","Szs:=", [],"X:=", "0mm","Y:=", "0mm","R:=", "0deg"],
                "X:=", "0",
                "Y:=", "0",
                "dir:=", "No"
            ],
            [
                "NAME:lgm",
                "lay:=", "POWER06",
                "id:=", 7,
                "pad:=", ["shp:=", "Cir","Szs:=", ["20mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "ant:=", ["shp:=", "Cir","Szs:=", ["30mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "thm:=", ["shp:=", "No","Szs:=", [],"X:=", "0mm","Y:=", "0mm","R:=", "0deg"],
                "X:=", "0",
                "Y:=", "0",
                "dir:=", "No"
            ],
            [
                "NAME:lgm",
                "lay:=", "POWER07",
                "id:=", 8,
                "pad:=", ["shp:=", "Cir","Szs:=", ["20mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "ant:=", ["shp:=", "Cir","Szs:=", ["30mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "thm:=", ["shp:=", "No","Szs:=", [],"X:=", "0mm","Y:=", "0mm","R:=", "0deg"],
                "X:=", "0",
                "Y:=", "0",
                "dir:=", "No"
            ],
            [
                "NAME:lgm",
                "lay:=", "POWER08",
                "id:=", 9,
                "pad:=", ["shp:=", "Cir","Szs:=", ["20mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "ant:=", ["shp:=", "Cir","Szs:=", ["30mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "thm:=", ["shp:=", "No","Szs:=", [],"X:=", "0mm","Y:=", "0mm","R:=", "0deg"],
                "X:=", "0",
                "Y:=", "0",
                "dir:=", "No"
            ],
            [
                "NAME:lgm",
                "lay:=", "GND09",
                "id:=", 10,
                "pad:=", ["shp:=", "Cir","Szs:=", ["20mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "ant:=", ["shp:=", "Cir","Szs:=", ["30mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "thm:=", ["shp:=", "No","Szs:=", [],"X:=", "0mm","Y:=", "0mm","R:=", "0deg"],
                "X:=", "0",
                "Y:=", "0",
                "dir:=", "No"
            ],
            [
                "NAME:lgm",
                "lay:=", "ART10",
                "id:=", 11,
                "pad:=", ["shp:=", "Cir","Szs:=", ["20mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "ant:=", ["shp:=", "Cir","Szs:=", ["30mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "thm:=", ["shp:=", "No","Szs:=", [],"X:=", "0mm","Y:=", "0mm","R:=", "0deg"],
                "X:=", "0",
                "Y:=", "0",
                "dir:=", "No"
            ],
            [
                "NAME:lgm",
                "lay:=", "GND11",
                "id:=", 12,
                "pad:=", ["shp:=", "Cir","Szs:=", ["20mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "ant:=", ["shp:=", "Cir","Szs:=", ["30mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "thm:=", ["shp:=", "No","Szs:=", [],"X:=", "0mm","Y:=", "0mm","R:=", "0deg"],
                "X:=", "0",
                "Y:=", "0",
                "dir:=", "No"
            ],
            [
                "NAME:lgm",
                "lay:=", "ART12",
                "id:=", 13,
                "pad:=", ["shp:=", "Cir","Szs:=", ["20mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "ant:=", ["shp:=", "Cir","Szs:=", ["30mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "thm:=", ["shp:=", "No","Szs:=", [],"X:=", "0mm","Y:=", "0mm","R:=", "0deg"],
                "X:=", "0",
                "Y:=", "0",
                "dir:=", "No"
            ],
            [
                "NAME:lgm",
                "lay:=", "GND13",
                "id:=", 14,
                "pad:=", ["shp:=", "Cir","Szs:=", ["20mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "ant:=", ["shp:=", "Cir","Szs:=", ["30mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "thm:=", ["shp:=", "No","Szs:=", [],"X:=", "0mm","Y:=", "0mm","R:=", "0deg"],
                "X:=", "0",
                "Y:=", "0",
                "dir:=", "No"
            ],
            [
                "NAME:lgm",
                "lay:=", "BOTTOM",
                "id:=", 15,
                "pad:=", ["shp:=", "Cir","Szs:=", ["20mil"],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "ant:=", ["shp:=", "No","Szs:=", [],"X:=", "0mm","Y:=", "0mm","R:=", "0deg"],
                "thm:=", ["shp:=", "No","Szs:=", [],"X:=", "0mm","Y:=", "0mm","R:=", "0deg"],
                "X:=", "0",
                "Y:=", "0",
                "dir:=", "No"
            ]
        ],
        "hle:=", [                "shp:=", "Cir",                "Szs:=", ["10mil"],                "X:=", "0mil",                "Y:=", "0mil",                "R:=", "0deg"],
        "hRg:=", "UTL",
        "sbsh:="        , "None",
        "sbpl:="        , "abv",
        "sbr:=", "0mm",
        "sb2:=", "0mm",
        "sbn:=", ""
    ],
    "ppl:=", []
]

'''*** 
solderBall array parameters'''
solderBall =[
                "NAME:AllTabs",
                [
                    "NAME:BaseElementTab",
                    [
                        "NAME:PropServers", 
                        "U3"
                    ],
                    [
                        "NAME:ChangedProps",
                        [
                            "NAME:Model Info",
                            "ExtraText:="        , "",
                            [
                                "NAME:Model",
                                "IOProp:=", ["CompPropEnabled:=", True,"Pid:=", -1,"Pmo:=", "0","CompPropType:=", 2,"PinPairRLC:=", ["RLCModelType:=", 0],
                                             "SolderBallProp:=", ["sbsh:=", "Sph","sbh:=", "0.07mm","sbr:=", "0.05mm","sb2:=", "0.06mm","sbn:=", "solder"],
                                             "PortProp:=", ["rh:=", "0","rsa:=", True,"rsx:=", "0","rsy:=", "0"]],
                                "CompType:=", 0
                            ]
                        ]
                    ]
                ]
            ]

'''*** 
material array parameters'''
material =     [
        "NAME:Material1",
        "CoordinateSystemType:=", "Cartesian",
        "BulkOrSurfaceType:="    , 1,
        [
            "NAME:PhysicsTypes",
            "set:="            , ["Electromagnetic","Thermal","Structural"]
        ],
        "permittivity:="    , "1",
        "permeability:="    , "1",
        "conductivity:="    , "0",
        "dielectric_loss_tangent:=", "0",
        "magnetic_loss_tangent:=", "0",
        "thermal_conductivity:=", "0",
        "saturation_mag:="    , "0tesla",
        "mass_density:="    , "0",
        "specific_heat:="    , "0",
        "youngs_modulus:="    , "0",
        "poissons_ratio:="    , "0"
    ]


'''*** 
RLCModle array parameters'''
RLCModle =    [
        "NAME:AllTabs",
        [
            "NAME:BaseElementTab",
            [
                "NAME:PropServers", 
                "C3L2"
            ],
            [
                "NAME:ChangedProps",
                [
                    "NAME:Model Info",
                    "ExtraText:="        , "",
                    [
                        [
                        "NAME:Model",
                        "RLCProp:=", ["CompPropEnabled:=", True,"Pid:=", -1,"Pmo:=", "0","CompPropType:=", 0,"PinPairRLC:=", 
                        ["RLCModelType:=", 0,  #0: rlc, 1:s-parameter
                            "ppr:=", ["p1:=", "1","p2:=", "2",
                            "rlc:=", [
                            "r:=", "0ohm","re:=", True,
                            "l:=", "0H","le:=", True,
                            "c:=", "1e-05farad","ce:=", True,
                            "p:=", False,"lyr:=", 1],
                            "NetRef:=", "GND","CosimDefintion:=", "NPort Model"
                        ]]],
                        "CompType:=", 3
                        ]
                    ]
                ]
            ]
        ]
    ]


'''***'''