from typing import List

class Rim():
    """
    Attributes are pretty self explanatory and all strings, this can change if necessary
    and more can be added if necessary.

    Mostly getters and setters, not a whole lot going on here
    """
    
    def __init__(self, sku: str):
        """
        Constructor
        """
        self._mfr = ""
        self._size = ""
        self._diameter = ""
        self._width = ""
        self._lugs = ""
        self._bp = ""
        self._offset = ""
        self._style = ""
        self._finish = ""
        self._years = ""
        self._model = ""
        self._condition = ""
        self._oemID = ""
        self._sku = sku
        self._ucode = self.sku[8:]
        self._hollander = self.sku[3:8]
        self._material = ""
        self._vehicleList = []
        if self._sku[:3] == "ALY":
            self._material = "ALUMINUM"
        elif self._sku[:3] == "STL":
            self._material = "STEEL"

    def __str__(self) -> str:
        """
        Returns a formatted output string, originally created for testing
        """
        string = f"SKU: {self._sku}\nSize: {self._size}\n"
        string += f"Diameter: {self._diameter}\nOffset: {self._offset}\n"
        string += f"Finish: {self._finish}\nWidth: {self.width}\n"
        string += f"Style: {self.style}\nYears: {self.years}\n"
        string += f"OEM IDs: {self.oemID}\nMFR: {self.mfr}\n{self.model}"
        return string

    def splitReturnFirst(self, string: str) -> str:
        """
        Returns the first "word" of an input string
        """
        temp = string.split(" ")
        return str(temp[0])
    
    @property
    def material(self):
        return self._material

    @material.setter
    def material(self, value):
        self._material = value

    @property
    def hollander(self):
        return self._hollander

    @property
    def ucode(self):
        return self._ucode
        
    @property
    def oemID(self):
        return self._oemID

    @oemID.setter
    def oemID(self, value: List[str]):
        temp = []
        for i in range(len(value)):
            if value[i] not in temp or value[i] != '':
                temp.append(value[i].strip())
        self._oemID = ", ".join(temp)

    @property
    def sku(self):
        return self._sku

    @property
    def mfr(self):
        return self._mfr

    @mfr.setter
    def mfr(self, value: str):
        self._mfr = value
    
    @property
    def diameter(self):
        return self._diameter

    @diameter.setter
    def diameter(self, value: str):
        self._diameter = value

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value: str):
        self._width = value

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value: str):
        sizeSplit = value.split(" x ")
        self.diameter = str(sizeSplit[0] + '"')
        self.width = str(sizeSplit[1] + '"')
        self._size = self.diameter + " x " + self.width

    @property
    def lugs(self):
        return self._lugs

    @lugs.setter
    def lugs(self, value: str):
        self._lugs = self.splitReturnFirst(value)

    @property
    def bp(self):
        return self._bp

    @bp.setter
    def bp(self, value: str):
        self._bp = self.splitReturnFirst(value)

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value: str):
        self._offset = self.splitReturnFirst(value)
    
    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, value: str):
        self._style = value
    
    @property
    def finish(self):
        return self._finish

    @finish.setter
    def finish(self, value: str):
        self._finish = value

    @property
    def years(self):
        return self._years

    @years.setter
    def years(self, value: str):
        self._years = value

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, vehicles: list):
        mfr = []
        modelList = []
        yearsList = []
        self.vehicleList = vehicles
        for element in vehicles:
            element = element.split()
            yearsList.append(element[0])
            if element[2] not in modelList:
                temp = element[2]
                if "_" in temp:
                    modelList.append(temp.replace("_", " "))
                modelList.append(temp)
            if element[1] not in mfr:
                mfr.append(element[1])
        years = ", ".join(yearsList)
        self.years = years
        self.mfr = ", ".join(mfr)
        self._model = ", ".join(modelList)

    @property
    def vehicleList(self): return self._vehicleList

    @vehicleList.setter
    def vehicleList(self, vehicleList): self._vehicleList = vehicleList
