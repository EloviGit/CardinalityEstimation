# this file create a set of samplers that collect data in different ways

import numpy as np
import pandas as pd
import utils as utl
import sketches as sk


class Sampler:
    def __init__(self, name="defaultSampler", isMultiSketchSampler=True, r=2, c=2, colstr=("a", "b"), filename="Default", directoryname="results"):
        self.name = name
        self.data = np.zeros((r, c), dtype=np.float64)
        self.pd = pd.DataFrame(self.data, columns=colstr)
        self.filename = filename
        self.directoryname = directoryname
        self.isMultiSkSpl = isMultiSketchSampler

    def sample(self, sketch: sk.Sketch, r):
        pass

    def save(self, singleSketch=False):
        if (singleSketch and not self.isMultiSkSpl) or (not singleSketch and self.isMultiSkSpl):
            self.pd.to_csv("/".join([self.directoryname, utl.VersionStr, self.filename+".csv"]))


class LogScaleSampler(Sampler):
    def __init__(self, skname, datname, round:int=1, scale:int=6, split:int=100, base=10):
        super(LogScaleSampler, self).__init__("LogSampling", False, scale*split+1, round, list(range(round)))
        self.filename = "_".join([utl.RunStr, self.name, datname, skname, utl.getTimeString()])
        self.skname = skname
        self.datname = datname
        self.samplvec = utl.exp_vector(scale, split, base)
        self.dat_index = None
        self.t_index = None

    def sample(self, sketch: sk.Sketch, r):
        if sketch.name == self.skname:
            if self.dat_index is None:
                self.dat_index = sketch.snapshotColStr.index(self.datname)
            if self.t_index is None:
                self.t_index = sketch.snapshotColStr.index("t")
            datvec = sketch.snapshotHist[:sketch.snapshotHist_inx, self.dat_index]
            tvec = sketch.snapshotHist[:sketch.snapshotHist_inx, self.t_index]
            self.data[:, r] = utl.uncoupled_Logunpack(datvec, tvec, self.samplvec)


class OnlyLastSampler(Sampler):
    def __init__(self, sknames, datnames, Markname, round:int=1):
        c_names =  [skname+"_"+datname for skname in sknames for datname in datnames]
        super(OnlyLastSampler, self).__init__("OnlyLast", True, round, len(c_names), c_names)
        self.sknames = sknames
        self.datnames = datnames
        self.filename = "_".join([utl.RunStr, self.name, Markname, utl.getTimeString()])
        self.index_dict = {c_name: None for c_name in c_names}
        self.hasattr_dict = {c_name: False for c_name in c_names}

    def sample(self, sketch: sk.Sketch, r):
        if sketch.name in self.sknames:
            for datname in self.datnames:
                c_name = sketch.name + "_" + datname
                if self.hasattr_dict[c_name] or hasattr(sketch, datname):
                    self.hasattr_dict[c_name] = True
                    self.pd[c_name][r] = getattr(sketch, datname)
                else:
                    if self.index_dict[c_name] is None:
                        self.index_dict[c_name] = sketch.snapshotColStr.index(datname)
                    self.pd[c_name][r] = sketch.snapshotHist[sketch.snapshotHist_inx-1, self.index_dict[c_name]]


class FailureSampler(Sampler):
    def __init__(self, sknames, datname, Markname):
        super(FailureSampler, self).__init__("Failure", True, 1, len(sknames), sknames)
        self.sknames = sknames
        self.datname = datname
        self.filename = "_".join([utl.RunStr, self.name, Markname, utl.getTimeString()])

    def sample(self, sketch: sk.Sketch, r):
        if sketch.name in self.sknames:
            self.pd[sketch.name][0] += getattr(sketch, self.datname)
