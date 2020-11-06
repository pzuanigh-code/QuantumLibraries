OPENMOLCAS_TEMPLATE = """
&GATEWAY
Coord
  {atomic_number}
  {mol_name}
  {geometry}
Basis={basis, default ANO-RCC-MB}
Group={symmetry, default: C1}

&SEWARD
{integral_keyword, e.g. Cholesky}

&SCF
Charge={charge}
Spin={spin}
"""

OPENMOLCAS_TEMPLATE_CASSCF = """
&RASSCF
  Charge= {charge}
  Nactel  =  {num_active_el}
  Ras2  =  {num_active_orbitals}
  Ciroot  =  {nroot} {nroot} 1
"""

OPEN_MOLCAS_TEMPLATE_BROOMBRIDGE = """
&RASSCF
  DMRG
  FCIDUMP
  TYPEINDEX
  Spin={spin}
  Charge={charge}

  RGINPUT
  nsweeps = 5
  max_bond_dimension = 500
  ENDRG
"""

def format_geometry(geometry: Geometry):
    """Format geometry into OpenMolcas format

    :param geometry: Molecular geometry
    :type geometry: Geometry
    :return: NWChem geometry format
    :rtype: str
    """
    return "\n".join(el.to_xyz() for el in geometry)
