import numpy as np
from . import units

class Filter(object) :
    def __init__(self) :
        self._descriptor = "filter"
        pass

    def where(self, sim) :
        return np.where(self(sim))

    def __call__(self, sim) :
        return np.ones(len(sim),dtype=bool)

    def __and__(self, f2) :
        return And(self, f2)

    def __invert__(self) :
        return Not(self)

    def __or__(self, f2) :
        return Or(self, f2)

    def __repr__(self) :
        return "Filter()"




class And(Filter) :
    def __init__(self, f1, f2) :
        self._descriptor = f1._descriptor+"&"+f2._descriptor
        self.f1 = f1
        self.f2 = f2

    def __call__(self, sim) :
        return self.f1(sim)*self.f2(sim)

    def __repr__(self) :
        return "("+repr(self.f1) + " & " + repr(self.f2)+")"

class Or(Filter) :
    def __init__(self, f1, f2) :
        self._descriptor = f1._descriptor+"|"+f2._descriptor
        self.f1 = f1
        self.f2 = f2

    def __call__(self, sim) :
        return self.f1(sim)+self.f2(sim)

    def __repr__(self) :
        return "("+repr(self.f1) + " | " + repr(self.f2)+")"

class Not(Filter) :
    def __init__(self, f) :
        self._descriptor = "~"+f._descriptor
        self.f = f

    def __call__(self, sim) :
        x = self.f(sim)
        return ~x


    def __repr__(self) :
        return "~"+repr(self.f)


class Sphere(Filter) :
    def __init__(self, radius, cen=(0,0,0)) :
        self._descriptor = "sphere"
        self.cen = np.asarray(cen)
        if self.cen.shape!=(3,) :
            raise ValueError, "Centre must be length 3 array"

        if isinstance(radius, str) :
            radius = units.Unit(radius)

        self.radius = radius

    def __call__(self, sim) :
        radius = self.radius
        if isinstance(radius, units.UnitBase) :
            radius = radius.ratio(sim["pos"].units,
                                  **sim["pos"].conversion_context())
        distance = ((sim["pos"]-self.cen)**2).sum(axis=1)
        return distance<radius**2

    def __repr__(self) :
        if isinstance(self.radius, units.UnitBase) :

            return "Sphere('%s', %s)"%(str(self.radius), repr(self.cen))
        else :
            return "Sphere(%.2e, %s)"%(self.radius, repr(self.cen))

class Disc(Filter) :
    def __init__(self, radius, height, cen=(0,0,0)) :
        self._descriptor = "disc"
        self.cen = np.asarray(cen)
        if self.cen.shape!=(3,) :
            raise ValueError, "Centre must be length 3 array"

        if isinstance(radius, str) :
            radius = units.Unit(radius)

        if isinstance(height, str):
            height = units.Unit(height)

        self.radius = radius
        self.height = height

    def __call__(self, sim) :
        radius = self.radius
        height = self.height

        if isinstance(radius, units.UnitBase) :
            radius = radius.ratio(sim["pos"].units, **sim["pos"].conversion_context())
        if isinstance(height, units.UnitBase) :
            height = height.ratio(sim["pos"].units, **sim["pos"].conversion_context())

        distance = (((sim["pos"]-self.cen)[:,:2])**2).sum(axis=1)
        return (distance<radius**2) * (np.abs(sim["z"]-self.cen[2])<height)

    def __repr__(self) :
        radius = self.radius
        height = self.height

        radius,height = [("'%s'"%str(x) if isinstance(x, units.UnitBase) else '%.2e'%x) for x in radius,height]

        return "Disc(%s, %s, %s)"%(radius, height, repr(self.cen))

class BandPass(Filter) :
    def __init__(self, prop, min, max) :
        self._descriptor = "bandpass_"+prop

        if isinstance(min, str):
            min = units.Unit(min)

        if isinstance(max, str) :
            max = units.Unit(max)

        self._prop = prop
        self._min = min
        self._max = max

    def __call__(self, sim) :
        min = self._min
        max = self._max
        prop = self._prop


        if isinstance(min, units.UnitBase) :
            min = min.ratio(sim[prop].units, **sim.conversion_context())
        if isinstance(max, units.UnitBase) :
            max = max.ratio(sim[prop].units, **sim.conversion_context())

        return ((sim[prop]>min)*(sim[prop]<max))

    def __repr__(self) :
        min, max = [("'%s'"%str(x) if isinstance(x, units.UnitBase) else '%.2e'%x) for x in self._min, self._max]
        return "BandPass('%s', %s, %s)"%(self._prop, min, max)

class HighPass(Filter) :
    def __init__(self, prop, min) :
        self._descriptor = "highpass_"+prop

        if isinstance(min, str):
            min = units.Unit(min)


        self._prop = prop
        self._min = min


    def __call__(self, sim) :
        min = self._min

        prop = self._prop


        if isinstance(min, units.UnitBase) :
            min = min.ratio(sim[prop].units, **sim.conversion_context())


        return (sim[prop]>min)

    def __repr__(self) :
        min = ("'%s'"%str(self._min) if isinstance(self._min, units.UnitBase) else '%.2e'%self._min)
        return "HighPass('%s', %s)"%(self._prop, min)


class LowPass(Filter) :
    def __init__(self, prop, max) :
        self._descriptor = "lowpass_"+prop

        if isinstance(max, str):
            max = units.Unit(max)


        self._prop = prop
        self._max = max


    def __call__(self, sim) :
        max = self._max

        prop = self._prop


        if isinstance(max, units.UnitBase) :
            max = max.ratio(sim[prop].units, **sim.conversion_context())


        return (sim[prop]<max)

    def __repr__(self) :
        max = ("'%s'"%str(self._max) if isinstance(self._max, units.UnitBase) else '%.2e'%self._max)
        return "LowPass('%s', %s)"%(self._prop, max)



def Annulus(r1, r2, cen=(0,0,0)) :
    x = Sphere(max(r1,r2),cen) & ~Sphere(min(r1,r2),cen)
    x._descriptor = "annulus"
    return x
