# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from ..convert import num_electrons

import re
import warnings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rdkit.Chem.AllChem import Mol

__all__ = [
    "geometry_from_xyz",
    "create_input_deck"
]

# Template for generating an NWChem input deck
NW_CHEM_TEMPLATE = """
start {name}

echo
{memory}

geometry units {geometry_units}
symmetry c1
{geometry}
end

basis
* library {basis}
end

charge {charge}

scf
thresh {scf_thresh:.1e}
tol2e {scf_tol2e}
{rhf}
{spin}
{nopen}
end

tce
{method}
tilesize 1
2eorb
2emet 13
nroots {num_tce_root}
thresh {tce_thresh:.1e}
end

set tce:print_integrals T
set tce:qorb {num_orb}
set tce:qela {num_el_a}
set tce:qelb {num_el_b}

task tce {driver}
"""

FLOAT_PATTERN = "([+-]?[0-9]*[.][0-9]+)"
XYZ_PATTERN = f"(\w) {FLOAT_PATTERN} {FLOAT_PATTERN} {FLOAT_PATTERN}"

def geometry_from_xyz(xyz: str):
    """Generate geometry portion of NWChem file from XYZ data.
    The formatting of the .xyz file format is as follows:

        <number of atoms>
        comment line
        <element> <X> <Y> <Z>
        ...

    Source: https://en.wikipedia.org/wiki/XYZ_file_format.

    Args:
        xyz (str): XYZ file format
    """
    match = re.findall(XYZ_PATTERN, xyz)
    return "\n".join(" ".join(item) for item in match)

def create_input_deck(
        mol_name: str, 
        geometry: str, 
        num_active_orbitals: int,
        memory: str = "memory stack 1000 mb heap 100 mb global 1000 mb noverify",
        geometry_units: str = "au", # TODO: use Enum or Pint to deal with valid units
        basis: str = "sto-3g",
        charge: int = 0,
        scf_thresh: float = 1.0e-10,
        scf_tol2e: float = 1.0e-10,
        rhf: str = "rhf",
        spin: str = "singlet",
        nopen: int = None,
        method: str = "ccsd",
        num_tce_root: int = 5,
        tce_thresh: float = 1.0e-6,
        driver: str = "energy",
        mol: "Mol" = None,
        num_active_el: int = None,
    ):
    """Generate an NWChem input deck

    Args:
        mol_name (str): Molecule name
        geometry (str): Molecule geometry in the following format (each atom on a new line):
            [Atom] [X] [Y] [Z]
        num_active_orbitals (int): Number of orbitals in molecular ground state to set active space
        memory (str, optional): Memory specification. Defaults to "memory stack 1000 mb heap 
            100 mb global 1000 mb noverify".
        geometry_units (str, optional): Units used for geometry. Defaults to "au".
        basis (str, optional): Basis to use for atoms. Defaults to "sto-3g".
        charge (int, optional): Molecule charge. Defaults to 0.
        scf_thresh (float, optional): Threshold for SCF solver with one-decimal precision. Defaults to 1.0e-10.
        scf_tol2e (float, optional): 2-electron tolerance for SCF solver
        rhf (str, optional): Restricted Hartree Fock method. Either "rhf" or "rohf". Defaults to "rhf".
        spin (str, optional): Spin property. Defaults to "singlet".
        nopen (int, optional): Number of singly occupied electron orbitals. Defaults to None.
        method (str, optional): Calculation method, either "HF", "DFT" or "ccsd". Defaults to "ccsd".
        num_tce_root (int, optional): Number of excited states. Defaults to 5.
        tce_thresh (float, optional): Threshold for TCE solver with one-decimal precision. Defaults to 1.0e-6.
        driver (str, optional): Driver method. Defaults to "energy".
        mol (Mol, optional): RDKit Molecule object to use for calculating number of electrons if 
            unspecified. Defaults to None.
        num_active_el (int, optional): Number of active electrons in molecule. This value is 
            calculated based on atomic numbers if mol is provided. Defaults to None.

    Returns:
        str: NWChem input deck formatted string
    """
    if mol is not None and num_active_el is None:
        num_active_el = num_electrons(mol)
    elif mol is None and num_active_el is None:
        raise ValueError("Cannot proceed: please provide either a Mol object or specify number of electrons")
    else:
        warnings.warn("Ignoring mol and using specified number of active electrons (num_active_el) instead.")

    nopen_str = f"nopen {nopen}" if nopen is not None else ""

    nw_chem = NW_CHEM_TEMPLATE.format(
        name=f"{mol_name}_test",
        memory=memory,
        geometry_units=geometry_units,
        geometry=geometry,
        basis=basis,
        charge=charge,
        scf_thresh=scf_thresh,
        scf_tol2e=scf_tol2e,
        rhf=rhf,
        spin=spin,
        nopen=nopen_str,
        method=method,
        num_tce_root=num_tce_root,
        tce_thresh=tce_thresh,
        num_orb=num_active_orbitals,
        num_el_a=num_active_el//2,
        num_el_b=num_active_el//2,
        driver=driver
    )

    return nw_chem