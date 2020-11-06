import re
from dataclasses import dataclass
from typing import List, Tuple, Union, TYPE_CHECKING

from qdk_chemistry.geometry.rdkit_convert import mol_to_coordinates
from qdk_chemistry.geometry.xyz import coordinates_to_xyz

from rdkit.Chem import AllChem as Chem

if TYPE_CHECKING:
    from rdkit.Chem import Mol

FLOAT_PATTERN = "([+-]?[0-9]*[.][0-9]+)"
XYZ_PATTERN = f"(\w) {FLOAT_PATTERN} {FLOAT_PATTERN} {FLOAT_PATTERN}"

@dataclass
class Element:
    """Class for keeping track of element XYZ coordinates 
    for molecule geometry
    """
    name: str
    x: float
    y: float
    z: float

    @classmethod
    def from_tuple(cls, value: Tuple[str, float, float, float]):
        name, x, y, z = value
        return cls(name=name, x=float(x), y=float(y), z=float(z))


class Geometry(List[Element]):
    """Molecular geometry consisting of list of elements with
    XYZ coordinates
    """
    def __init__(self, *args, charge: Union[int, None] = None, **kwargs):
        self.charge = charge
        super().__init__(*args, **kwargs)

    @property
    def coordinates(self) -> Tuple[str, float, float, float]:
        """Get coordinates list of tuples (name, x, y, z)

        :return: List of coordinate tuples
        :rtype: Tuple[str, float, float, float]
        """
        return [(e.name, e.x, e.y, e.z) for e in self]

    @classmethod
    def from_mol(cls, mol: "Mol", num_confs: int = 10):
        """Constructor for creating geometry from RDKit molecule 
        object

        :param mol: RDKit molecule object
        :type mol: Mol
        :param num_confs: Number of molecular conformers to generate, defaults to 10
        :type num_confs: int, optional
        """
        # This returns a plain list of tuples (element name, x, y, z)
        coordinates = mol_to_coordinates(
            mol=mol,
            num_confs=num_confs
        )
        charge = Chem.GetFormalCharge(mol)

        return cls(
            [
                Element(name=name, x=x, y=y, z=z)
                for (name, x, y, z) in coordinates
            ], 
            charge=charge
        )
    
    @classmethod
    def from_xyz(cls, xyz: str):
        """Generate geometry portion of NWChem file from XYZ data.
        The formatting of the .xyz file format is as follows:

            <number of atoms>
            comment line
            <element> <X> <Y> <Z>
            ...

        Source: https://en.wikipedia.org/wiki/XYZ_file_format.

        :param xyz: XYZ file format
        :type xyz: str
        """
        match = re.findall(XYZ_PATTERN, xyz)
        return cls([Element.from_tuple(item) for item in match])

    def to_xyz(self):
        """Convert geometry to XYZ-formatted string
        """
        return coordinates_to_xyz(
            number_of_atoms=len(self),
            charge=self.charge,
            coordinates=self.coordinates
        )
