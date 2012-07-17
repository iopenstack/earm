"""TODO Docstring: Say that this file ensures that the models
match published ODEs, etc."""

import unittest
from earm2.mito import chen2007BiophysJ
from earm2.mito import chen2007FEBS_direct
from earm2.mito import chen2007FEBS_indirect
from earm2.mito import cui2008_direct
from earm2.mito import cui2008_direct1
from earm2.mito import cui2008_direct2
from earm2.mito import howells2011
from pysb.bng import generate_equations
from pysb.integrate import odesolve
from pysb import *
import numpy as np
import matplotlib.pyplot as plt
import re

def convert_odes(model, p_name_map, s_name_map_by_pattern):
    """Substitutes species and parameter names using the given name mappings.

    Parameters
    ----------
    model : pysb.core.Model
        The model to be converted.
    p_name_map : dict
        A dict where the keys are the parameter names of the PySB model and the
        values are the parameter names of the original model, e.g.
        {'bind_BidT_Bcl2_kf': 'ka_tBid_Bcl2'}
    s_name_map : dict
        A dict where the keys are the string representations of the species
        from the PySB model, generated by calling str(species), and the values
        are the species names in the original model, e.g.
        {'Bid(bf=None, state=T)': 'Act'}

    Returns
    -------
    A list of strings, with one entry for each ODE in the model. Each ODE
    is represented as a string, e.g. "d[Act]/dt = ..."
    """

    generate_equations(model)

    # Get the index of each species
    s_name_map_by_num = {}
    for i, s in enumerate(model.species):
        for key in s_name_map_by_pattern:
            if key == str(s):
                s_name_map_by_num['s%d' % i] = s_name_map_by_pattern[key]

    name_map = {}
    name_map.update(p_name_map)
    name_map.update(s_name_map_by_num)

    # Substitute new names into the ODEs
    ode_list = {} 
    for i, ode in enumerate(model.odes):
        new_ode = ode.subs(name_map)
        ode_species = s_name_map_by_pattern[str(model.species[i])]
        ode_list[ode_species] = str(new_ode)
        #new_ode = 'd[%s]/dt = %s' % (s_name_map_by_num['s%d' % i], str(new_ode))
        #ode_list.append(new_ode)

    return ode_list

def odes_match(generated_odes, validated_odes):
    """Return True if the ODEs match.

    Both args are dicts, where the key is the original species name,
    and the value is the string representation of the ODE.
    """

    # Will throw a KeyError if either list contains species that are not
    # in the other
    result_list1 = [generated_odes[species] == validated_odes[species]
                   for species in generated_odes]
    result_list2 = [generated_odes[species] == validated_odes[species]
                   for species in validated_odes]
    return np.all(result_list1) and np.all(result_list2)

def convert_parameters(model, p_name_map):
    """TODO: Docstring"""
    param_list = []
    for p in model.parameters:
        if p.name in p_name_map:
            original_name = re.sub(p.name, p_name_map[p.name], p.name)
            param_list.append((original_name, p.value))
    return param_list

# Parameter mapping used by both Chen 2007 FEBS models
chenFEBS_p_name_map = {
    'one_step_BidT_BaxC_to_BidT_BaxA_kf': 'k_InBax',
    'reverse_BaxA_to_BaxC_k': 'k_Bax',
    'bind_BidT_Bcl2_kf': 'k_BH3_Bcl2',
    'bind_BidT_Bcl2_kr': 'kr_BH3Bcl2',
    'bind_BadM_Bcl2_kf': 'k_BH3_Bcl2',
    'bind_BadM_Bcl2_kr': 'kr_BH3Bcl2',
    'bind_BaxA_Bcl2_kf': 'k_Bax_Bcl2',
    'bind_BaxA_Bcl2_kr': 'kr_BaxBcl2',
    #'spontaneous_pore_BaxC_to_Bax4_kf': 'k_o',
    #'spontaneous_pore_BaxC_to_Bax4_kr': 'kr_o',
    'spontaneous_pore_BaxA_to_Bax4_kf': 'k_o',
    'spontaneous_pore_BaxA_to_Bax4_kr': 'kr_o' }

# Parameter mapping used by all three Cui models
cui_p_name_map = {
    'one_step_BidT_BaxC_to_BidT_BaxA_kf': 'k1',
    'reverse_BaxA_to_BaxC_k': 'k8',
    'bind_BidT_Bcl2_kf': 'k4',
    'bind_BidT_Bcl2_kr': 'k5',
    'bind_BadM_Bcl2_kf': 'k9',
    'bind_BadM_Bcl2_kr': 'k10',
    'displace_BaxA_BidTBcl2_to_BaxABcl2_BidT_kf': 'k6',
    'displace_BaxA_BidTBcl2_to_BaxABcl2_BidT_kr': 'k7',
    'displace_BadM_BidTBcl2_to_BadMBcl2_BidT_kf': 'k11',
    'displace_BadM_BidTBcl2_to_BadMBcl2_BidT_kr': 'k12',
    'displace_BadM_BaxABcl2_to_BadMBcl2_BaxA_kf': 'k13',
    'displace_BadM_BaxABcl2_to_BadMBcl2_BaxA_kr': 'k14',
    'dimerize_Bax_kf': 'k16',
    'dimerize_Bax_kr': 'k17',
    'synthesize_BaxC_k': 'p1',
    'degrade_BaxC_k': 'u1',
    'degrade_BaxA_k': 'u2',
    'synthesize_BidT_k': 'p2',
    'degrade_BidT_k': 'u3',
    'synthesize_Bcl2_k': 'p3',
    'degrade_Bcl2_k': 'u4',
    'degrade_BidTBcl2_k': 'u5',
    'degrade_BaxBcl2_k': 'u6',
    'synthesize_BadMU_k': 'p4',
    'degrade_BadMU_k': 'u7',
    'degrade_BadBcl2_k': 'u8',
    'degrade_BaxBax_k': 'u9',
    'bind_BaxA_Bcl2_kf': 'k2',
    'bind_BaxA_Bcl2_kr': 'k3',
    'Bax_autoactivation_dimerization_k': 'k15' }

# Species mapping used by all three Cui models
cui_s_name_map = {
    'Bid(bf=None, state=T)': 'Act',
    'Bad(bf=None, state=M, serine=U)': 'Ena',
    'Bax(bf=None, s1=None, s2=None, state=C)': 'InBax',
    'Bcl2(bf=None)': 'Bcl2',
    '__source()': '__source',
    'Bax(bf=None, s1=None, s2=None, state=A)': 'AcBax',
    'Bcl2(bf=1) % Bid(bf=1, state=T)': 'ActBcl2',
    'Bad(bf=1, state=M, serine=U) % Bcl2(bf=1)': 'EnaBcl2',
    '__sink()': '__sink',
    'Bax(bf=None, s1=1, s2=2, state=A) % Bax(bf=None, s1=2, s2=1, state=A)': 'MAC',
    'Bax(bf=1, s1=None, s2=None, state=A) % Bcl2(bf=1)': 'AcBaxBcl2'}

## TESTS ===============================================================

class TestChen2007BiophysJ(unittest.TestCase):
    """TODO: Docstring"""

    p_name_map = {
        'one_step_BidT_BaxC_to_BidT_BaxA_kf': 'k1',
        'reverse_BaxA_to_BaxC_k': 'k2',
        'bind_BidT_Bcl2_kf': 'k5',
        'bind_BidT_Bcl2_kr': 'k6',
        'bind_BaxA_Bcl2_kf': 'k3',
        'bind_BaxA_Bcl2_kr': 'k4',
        'displace_BaxA_BidTBcl2_to_BaxABcl2_BidT_k': 'k7',
        #'displace_BaxA_BidTBcl2_to_BaxABcl2_BidT_kr': 'k8',
        'spontaneous_pore_BaxA_to_Bax4_kf': 'k9',
        'spontaneous_pore_BaxA_to_Bax4_kr': 'k10' }
    s_name_map = {
        'Bid(bf=None, state=T)': 'Act',
        'Bax(bf=None, s1=None, s2=None, state=C)': 'InBax',
        'Bcl2(bf=None)': 'Bcl2',
        'Bax(bf=None, s1=None, s2=None, state=A)': 'AcBax',
        'Bcl2(bf=1) % Bid(bf=1, state=T)': 'ActBcl2',
        'Bax(bf=1, s1=None, s2=None, state=A) % Bcl2(bf=1)': 'AcBaxBcl2',
        'Bax(bf=None, s1=1, s2=2, state=A) % Bax(bf=None, s1=3, s2=1, state=A) % Bax(bf=None, s1=4, s2=3, state=A) % Bax(bf=None, s1=2, s2=4, state=A)': 'Bax4'
    }

    def setUp(self):
        self.model = chen2007BiophysJ.model
        if self.model.parameters.get('Bid_0') is None:
            # Add initial condition for Bid
            Bid_0 = Parameter('Bid_0', 1, _export=False)
            self.model.add_component(Bid_0)
            Bid = self.model.monomers['Bid']
            self.model.initial(Bid(state='T', bf=None), Bid_0)

    def test_odes(self):
        """The ODEs generated by the PySB model match those of the paper with
        the following two caveats:

        1. In the equation for d[Bcl2]/dt, in the paper the authors group the
           terms

            + AcBaxBcl2*k4 + ActBcl2*k6'

           into the single term

            + k_Bcl2 * Bcl2_nonfree

           with the comment that "Bcl2_nonfree indicates the total concentration
           of Bcl2 associated with both activated Bax and Activator
           ([Bcl2_nonfree] = [AcBaxBcl2] + [ActBcl2]). We use k_bcl2 to
           represent the rate of non-free Bcl2 shifting to free Bcl2, assuming
           that free Bcl2 originates from both Bcl2 non-free forms at the same
           rate."

           In addition, in the legend for Table 1 (which lists parameters) they
           state that: "We set k_bcl2 (the rate of non-free Bcl2 shifting to
           free Bcl2)... equal to k6 assuming that free Bcl2 originate [sic]
           from AcBaxBcl2 at the same rate with ActBcl2."

           So, obviously this substitution of Bcl2_nonfree for AcBaxBcl2 and
           ActBcl2 works if k4 and k6 are equal, which they claim as an
           assumption; however, in their table of parameter values, they list k4
           as having a value of 0.001 s^-1, and k6 as having a value of
           0.04 s^-1.

        2. It should also be noted that the parameter for spontaneous pore
           formation, k9, has already been multiplied by 4 from its nominal
           value listed in the paper. This accounts for BNG's (appropriate)
           addition of the coefficients of 0.25 to the Bax polymerization
           forward reaction, due to the reaction being a homomeric binding
           reaction.

        3. Because the rate of displacement of Bax from Bcl2 by tBid is set
           to 0 in the original model, this reaction and its associated rate
           parameter k8 have been eliminated from the model.
        """
        ode_list = convert_odes(self.model, self.p_name_map, self.s_name_map)
        self.assertTrue(odes_match(ode_list,
           {'Act': 'AcBax*ActBcl2*k7 - Act*Bcl2*k5 + ActBcl2*k6',
            'InBax': 'AcBax*k2 - Act*InBax*k1',
            'Bcl2': '-AcBax*Bcl2*k3 + AcBaxBcl2*k4 - Act*Bcl2*k5 + ActBcl2*k6',
            'AcBax': '-1.0*AcBax**4*k9 - AcBax*ActBcl2*k7 - AcBax*Bcl2*k3 - AcBax*k2 + AcBaxBcl2*k4 + Act*InBax*k1 + 4*Bax4*k10',
            'ActBcl2': '-AcBax*ActBcl2*k7 + Act*Bcl2*k5 - ActBcl2*k6',
            'AcBaxBcl2': 'AcBax*ActBcl2*k7 + AcBax*Bcl2*k3 - AcBaxBcl2*k4',
            'Bax4': '0.25*AcBax**4*k9 - Bax4*k10'}))

    def test_parameters(self):
        """The parameter values in the test below have been verified to match
        the values listed in Table 1 of Chen et al. (2007) Biophys J."""
        param_list = convert_parameters(self.model, self.p_name_map)
        self.assertEqual(param_list, 
           [('k1', 0.5),
            ('k2', 0.1),
            ('k5', 3),
            ('k6', 0.04),
            ('k3', 2),
            ('k4', 0.001),
            ('k7', 2),
            ('k9', 8),
            ('k10', 0)])

class TestChen2007FEBS_Indirect(unittest.TestCase):
    """TODO: Docstring"""
 
    s_name_map = {
        'Bid(bf=None, state=T)': 'BH3',
        'Bax(bf=None, s1=None, s2=None, state=A)': 'Bax',
        'Bcl2(bf=None)': 'Bcl2',
        'Bcl2(bf=1) % Bid(bf=1, state=T)': 'BH3Bcl2',
        'Bax(bf=1, s1=None, s2=None, state=A) % Bcl2(bf=1)': 'BaxBcl2',
        'Bax(bf=None, s1=1, s2=2, state=A) % Bax(bf=None, s1=3, s2=1, state=A) % Bax(bf=None, s1=4, s2=3, state=A) % Bax(bf=None, s1=2, s2=4, state=A)': 'MAC'}

    def setUp(self):
        self.model = chen2007FEBS_indirect.model
        if self.model.parameters.get('Bid_0') is None:
            # Add initial condition for Bid
            Bid_0 = Parameter('Bid_0', 1, _export=False)
            self.model.add_component(Bid_0)
            Bid = self.model.monomers['Bid']
            self.model.initial(Bid(state='T', bf=None), Bid_0)

    def test_odes(self):
        ode_list = convert_odes(self.model, chenFEBS_p_name_map, self.s_name_map)
        self.assertTrue(odes_match(ode_list,
           {'BH3': '-BH3*Bcl2*k_BH3_Bcl2 + BH3Bcl2*kr_BH3Bcl2',
            'Bax': '-1.0*Bax**4*k_o - Bax*Bcl2*k_Bax_Bcl2 + BaxBcl2*kr_BaxBcl2 + 4*MAC*kr_o',
            'Bcl2': '-BH3*Bcl2*k_BH3_Bcl2 + BH3Bcl2*kr_BH3Bcl2 - Bax*Bcl2*k_Bax_Bcl2 + BaxBcl2*kr_BaxBcl2',
            'BH3Bcl2': 'BH3*Bcl2*k_BH3_Bcl2 - BH3Bcl2*kr_BH3Bcl2',
            'BaxBcl2': 'Bax*Bcl2*k_Bax_Bcl2 - BaxBcl2*kr_BaxBcl2',
            'MAC': '0.25*Bax**4*k_o - MAC*kr_o'}))

class TestChen2007FEBS_Direct(unittest.TestCase):
    """TODO: Docstring"""
    s_name_map = {
        'Bid(bf=None, state=T)': 'Act',
        'Bad(bf=None, state=M, serine=U)': 'Ena',
        'Bax(bf=None, s1=None, s2=None, state=C)': 'InBax',
        'Bcl2(bf=None)': 'Bcl2',
        'Bax(bf=None, s1=None, s2=None, state=A)': 'Bax',
        'Bcl2(bf=1) % Bid(bf=1, state=T)': 'ActBcl2',
        'Bad(bf=1, state=M, serine=U) % Bcl2(bf=1)': 'EnaBcl2',
        'Bax(bf=None, s1=1, s2=2, state=A) % Bax(bf=None, s1=3, s2=1, state=A) % Bax(bf=None, s1=4, s2=3, state=A) % Bax(bf=None, s1=2, s2=4, state=A)': 'MAC'}

    def setUp(self):
        self.model = chen2007FEBS_direct.model
        if self.model.parameters.get('Bid_0') is None:
            # Add initial condition for Bid
            Bid_0 = Parameter('Bid_0', 1, _export=False)
            self.model.add_component(Bid_0)
            Bid = self.model.monomers['Bid']
            self.model.initial(Bid(state='T', bf=None), Bid_0)
        if self.model.parameters.get('Bad_0') is None:
            # Add initial condition for Bad
            Bad_0 = Parameter('Bad_0', 1, _export=False)
            self.model.add_component(Bad_0)
            Bad = self.model.monomers['Bad']
            self.model.initial(Bad(state='M', bf=None, serine='U'), Bad_0)

    def test_odes(self):
        ode_list = convert_odes(self.model, chenFEBS_p_name_map, self.s_name_map)
        self.assertTrue(odes_match(ode_list,
           {'Act': '-Act*Bcl2*k_BH3_Bcl2 + ActBcl2*kr_BH3Bcl2',
            'Ena': '-Bcl2*Ena*k_BH3_Bcl2 + EnaBcl2*kr_BH3Bcl2',
            'InBax': '-Act*InBax*k_InBax + Bax*k_Bax',
            'Bcl2': '-Act*Bcl2*k_BH3_Bcl2 + ActBcl2*kr_BH3Bcl2 - Bcl2*Ena*k_BH3_Bcl2 + EnaBcl2*kr_BH3Bcl2',
             'Bax': 'Act*InBax*k_InBax - 1.0*Bax**4*k_o - Bax*k_Bax + 4*MAC*kr_o',
             'ActBcl2': 'Act*Bcl2*k_BH3_Bcl2 - ActBcl2*kr_BH3Bcl2',
             'EnaBcl2': 'Bcl2*Ena*k_BH3_Bcl2 - EnaBcl2*kr_BH3Bcl2',
             'MAC': '0.25*Bax**4*k_o - MAC*kr_o'}))

class TestCui2008_Direct(unittest.TestCase):
    def setUp(self):
        self.model = cui2008_direct.model

    def test_odes(self):
        ode_list = convert_odes(self.model, cui_p_name_map, cui_s_name_map)
        self.assertTrue(odes_match(ode_list,
            {'Act': '-Act*Bcl2*k4 - Act*EnaBcl2*k12 - Act*u3 + ActBcl2*Ena*k11 + ActBcl2*k5 + __source*p2',
             'Ena': 'Act*EnaBcl2*k12 - ActBcl2*Ena*k11 - Bcl2*Ena*k9 - Ena*u7 + EnaBcl2*k10 + __source*p4',
             'InBax': 'AcBax*k8 - Act*InBax*k1 - InBax*u1 + __source*p1',
             'Bcl2': '-Act*Bcl2*k4 + ActBcl2*k5 - Bcl2*Ena*k9 - Bcl2*u4 + EnaBcl2*k10 + __source*p3',
             '__source': '0',
             'AcBax': '-1.0*AcBax**2*k16 - AcBax*k8 - AcBax*u2 + Act*InBax*k1 + 2*MAC*k17',
             'ActBcl2': 'Act*Bcl2*k4 + Act*EnaBcl2*k12 - ActBcl2*Ena*k11 - ActBcl2*k5 - ActBcl2*u5',
             'EnaBcl2': '-Act*EnaBcl2*k12 + ActBcl2*Ena*k11 + Bcl2*Ena*k9 - EnaBcl2*k10 - EnaBcl2*u8',
             '__sink': 'AcBax*u2 + Act*u3 + ActBcl2*u5 + Bcl2*u4 + Ena*u7 + EnaBcl2*u8 + InBax*u1 + MAC*u9',
             'MAC': '0.5*AcBax**2*k16 - MAC*k17 - MAC*u9'}))

class TestCui2008_Direct1(unittest.TestCase):
    """TODO: Docstring"""
    def setUp(self):
        self.model = cui2008_direct1.model

    def test_odes(self):
        ode_list = convert_odes(self.model, cui_p_name_map, cui_s_name_map)
        self.assertTrue(odes_match(ode_list,
            {'Act': 'AcBax*ActBcl2*k6 - AcBaxBcl2*Act*k7 - Act*Bcl2*k4 - Act*EnaBcl2*k12 - Act*u3 + ActBcl2*Ena*k11 + ActBcl2*k5 + __source*p2',
             'Ena': 'AcBax*EnaBcl2*k14 - AcBaxBcl2*Ena*k13 + Act*EnaBcl2*k12 - ActBcl2*Ena*k11 - Bcl2*Ena*k9 - Ena*u7 + EnaBcl2*k10 + __source*p4',
             'InBax': 'AcBax*k8 - Act*InBax*k1 - InBax*u1 + __source*p1',
             'Bcl2': '-AcBax*Bcl2*k2 + AcBaxBcl2*k3 - Act*Bcl2*k4 + ActBcl2*k5 - Bcl2*Ena*k9 - Bcl2*u4 + EnaBcl2*k10 + __source*p3',
             '__source': '0',
             'AcBax': '-1.0*AcBax**2*k16 - AcBax*ActBcl2*k6 - AcBax*Bcl2*k2 - AcBax*EnaBcl2*k14 - AcBax*k8 - AcBax*u2 + AcBaxBcl2*Act*k7 + AcBaxBcl2*Ena*k13 + AcBaxBcl2*k3 + Act*InBax*k1 + 2*MAC*k17',
             'ActBcl2': '-AcBax*ActBcl2*k6 + AcBaxBcl2*Act*k7 + Act*Bcl2*k4 + Act*EnaBcl2*k12 - ActBcl2*Ena*k11 - ActBcl2*k5 - ActBcl2*u5',
             'EnaBcl2': '-AcBax*EnaBcl2*k14 + AcBaxBcl2*Ena*k13 - Act*EnaBcl2*k12 + ActBcl2*Ena*k11 + Bcl2*Ena*k9 - EnaBcl2*k10 - EnaBcl2*u8',
             '__sink': 'AcBax*u2 + AcBaxBcl2*u6 + Act*u3 + ActBcl2*u5 + Bcl2*u4 + Ena*u7 + EnaBcl2*u8 + InBax*u1 + MAC*u9',
             'MAC': '0.5*AcBax**2*k16 - MAC*k17 - MAC*u9',
             'AcBaxBcl2': 'AcBax*ActBcl2*k6 + AcBax*Bcl2*k2 + AcBax*EnaBcl2*k14 - AcBaxBcl2*Act*k7 - AcBaxBcl2*Ena*k13 - AcBaxBcl2*k3 - AcBaxBcl2*u6'}))

class TestCui2008_Direct2(unittest.TestCase):
    """TODO: Docstring"""

    def setUp(self):
        self.model = cui2008_direct2.model

    def test_odes(self):
        ode_list = convert_odes(self.model, cui_p_name_map, cui_s_name_map)
        self.assertTrue(odes_match(ode_list,
            {'Act': 'AcBax*ActBcl2*k6 - AcBaxBcl2*Act*k7 - Act*Bcl2*k4 - Act*EnaBcl2*k12 - Act*u3 + ActBcl2*Ena*k11 + ActBcl2*k5 + __source*p2',
             'Ena': 'AcBax*EnaBcl2*k14 - AcBaxBcl2*Ena*k13 + Act*EnaBcl2*k12 - ActBcl2*Ena*k11 - Bcl2*Ena*k9 - Ena*u7 + EnaBcl2*k10 + __source*p4',
             'InBax': '-AcBax*InBax*k15 + AcBax*k8 - Act*InBax*k1 - InBax*u1 + __source*p1',
             'Bcl2': '-AcBax*Bcl2*k2 + AcBaxBcl2*k3 - Act*Bcl2*k4 + ActBcl2*k5 - Bcl2*Ena*k9 - Bcl2*u4 + EnaBcl2*k10 + __source*p3',
             '__source': '0',
             'AcBax': '-1.0*AcBax**2*k16 - AcBax*ActBcl2*k6 - AcBax*Bcl2*k2 - AcBax*EnaBcl2*k14 - AcBax*InBax*k15 - AcBax*k8 - AcBax*u2 + AcBaxBcl2*Act*k7 + AcBaxBcl2*Ena*k13 + AcBaxBcl2*k3 + Act*InBax*k1 + 2*MAC*k17',
             'ActBcl2': '-AcBax*ActBcl2*k6 + AcBaxBcl2*Act*k7 + Act*Bcl2*k4 + Act*EnaBcl2*k12 - ActBcl2*Ena*k11 - ActBcl2*k5 - ActBcl2*u5',
             'EnaBcl2': '-AcBax*EnaBcl2*k14 + AcBaxBcl2*Ena*k13 - Act*EnaBcl2*k12 + ActBcl2*Ena*k11 + Bcl2*Ena*k9 - EnaBcl2*k10 - EnaBcl2*u8',
             '__sink': 'AcBax*u2 + AcBaxBcl2*u6 + Act*u3 + ActBcl2*u5 + Bcl2*u4 + Ena*u7 + EnaBcl2*u8 + InBax*u1 + MAC*u9',
             'MAC': '0.5*AcBax**2*k16 + AcBax*InBax*k15 - MAC*k17 - MAC*u9',
             'AcBaxBcl2': 'AcBax*ActBcl2*k6 + AcBax*Bcl2*k2 + AcBax*EnaBcl2*k14 - AcBaxBcl2*Act*k7 - AcBaxBcl2*Ena*k13 - AcBaxBcl2*k3 - AcBaxBcl2*u6'}))

class TestHowells2011(unittest.TestCase):
    """TODO: Docstring"""

    # Mapping of parameter names
    p_name_map = {
        'one_step_BidT_BaxC_to_BidT_BaxA_kf': 'k_Bak_cat',
        'reverse_BaxA_to_BaxC_k': 'k_Bak_inac',
        'bind_BidT_Bcl2_kf': 'ka_tBid_Bcl2',
        'bind_BidT_Bcl2_kr': 'kd_tBid_Bcl2',
        'bind_BaxA_Bcl2_kf': 'ka_Bak_Bcl2',
        'bind_BaxA_Bcl2_kr': 'kd_Bak_Bcl2',
        'displace_BaxA_BidTBcl2_to_BaxABcl2_BidT_k': 'k_tBid_rel2',
        'spontaneous_pore_BaxA_to_Bax4_kf': 'ka_Bak_poly',
        'spontaneous_pore_BaxA_to_Bax4_kr': 'kd_Bak_poly',
        'equilibrate_BadCU_to_BadMU_kf': 't_Bad_in',
        'equilibrate_BadCU_to_BadMU_kr': 't_Bad_out',
        'bind_BadM_Bcl2_kf': 'ka_Bad_Bcl2',
        'bind_BadM_Bcl2_kr': 'kd_Bad_Bcl2',
        'displace_BadM_BidTBcl2_to_BadMBcl2_BidT_k': 'k_tBid_rel1',
        'phosphorylate_Bad_k1': 'k_Bad_phos1',
        'phosphorylate_Bad_k2': 'k_Bad_phos2',
        'sequester_BadCP_to_BadC1433_k': 'k_Bad_seq',
        'release_BadC1433_to_BadCU_k': 'k_Bad_rel'}
    # Mapping of species names
    s_name_map = {
        'Bid(bf=None, state=T)': 'tBid',
        'Bax(bf=None, s1=None, s2=None, state=C)': 'Bak_inac',
        'Bcl2(bf=None)': 'Bcl2',
        'Bad(bf=None, state=M, serine=U)': 'Bad_m',
        'Bax(bf=None, s1=None, s2=None, state=A)': 'Bak',
        'Bcl2(bf=1) % Bid(bf=1, state=T)': 'tBidBcl2',
        'Bad(bf=None, state=C, serine=U)': 'Bad',
        'Bad(bf=1, state=M, serine=U) % Bcl2(bf=1)': 'BadBcl2',
        'Bad(bf=None, state=C, serine=P)': 'pBad',
        'Bax(bf=1, s1=None, s2=None, state=A) % Bcl2(bf=1)': 'BakBcl2',
        'Bax(bf=None, s1=1, s2=2, state=A) % Bax(bf=None, s1=3, s2=1, state=A) % Bax(bf=None, s1=4, s2=3, state=A) % Bax(bf=None, s1=2, s2=4, state=A)': 'Bak_poly',
        'Bad(bf=None, state=C, serine=B)': 'pBad1433'}

    def setUp(self):
        self.model = howells2011.model
        if self.model.parameters.get('Bid_0') is None:
            # Add initial condition for Bid
            Bid_0 = Parameter('Bid_0', 1, _export=False)
            self.model.add_component(Bid_0)
            Bid = self.model.monomers['Bid']
            self.model.initial(Bid(state='T', bf=None), Bid_0)

    def test_odes(self):
        """These ODEs match the ODEs listed in the paper, with the note that
        the parameter for spontaneous pore formation, ka_Bak_poly, has already
        been multiplied by 4 from its nominal value listed in the paper. This
        accounts for BNG's (appropriate) addition of the coefficients of 0.25
        to the Bak polymerization forward reaction, due to the reaction being
        a homomeric binding reaction.
        """
        ode_list = convert_odes(self.model, self.p_name_map, self.s_name_map)
        self.assertTrue(odes_match(ode_list,
            {'tBid': 'Bad_m*k_tBid_rel1*tBidBcl2 + Bak*k_tBid_rel2*tBidBcl2 - Bcl2*ka_tBid_Bcl2*tBid + kd_tBid_Bcl2*tBidBcl2',
             'Bak_inac': 'Bak*k_Bak_inac - Bak_inac*k_Bak_cat*tBid',
             'Bcl2': 'BadBcl2*k_Bad_phos2 + BadBcl2*kd_Bad_Bcl2 - Bad_m*Bcl2*ka_Bad_Bcl2 - Bak*Bcl2*ka_Bak_Bcl2 + BakBcl2*kd_Bak_Bcl2 - Bcl2*ka_tBid_Bcl2*tBid + kd_tBid_Bcl2*tBidBcl2',
             'Bad_m': 'Bad*t_Bad_in + BadBcl2*kd_Bad_Bcl2 - Bad_m*Bcl2*ka_Bad_Bcl2 - Bad_m*k_Bad_phos1 - Bad_m*k_tBid_rel1*tBidBcl2 - Bad_m*t_Bad_out',
             'Bak': '-1.0*Bak**4*ka_Bak_poly - Bak*Bcl2*ka_Bak_Bcl2 - Bak*k_Bak_inac - Bak*k_tBid_rel2*tBidBcl2 + BakBcl2*kd_Bak_Bcl2 + Bak_inac*k_Bak_cat*tBid + 4*Bak_poly*kd_Bak_poly',
             'tBidBcl2': '-Bad_m*k_tBid_rel1*tBidBcl2 - Bak*k_tBid_rel2*tBidBcl2 + Bcl2*ka_tBid_Bcl2*tBid - kd_tBid_Bcl2*tBidBcl2',
             'Bad': '-Bad*k_Bad_phos1 - Bad*t_Bad_in + Bad_m*t_Bad_out + k_Bad_rel*pBad1433',
             'BadBcl2': '-BadBcl2*k_Bad_phos2 - BadBcl2*kd_Bad_Bcl2 + Bad_m*Bcl2*ka_Bad_Bcl2 + Bad_m*k_tBid_rel1*tBidBcl2',
             'pBad': 'Bad*k_Bad_phos1 + BadBcl2*k_Bad_phos2 + Bad_m*k_Bad_phos1 - k_Bad_seq*pBad',
             'BakBcl2': 'Bak*Bcl2*ka_Bak_Bcl2 + Bak*k_tBid_rel2*tBidBcl2 - BakBcl2*kd_Bak_Bcl2',
             'Bak_poly': '0.25*Bak**4*ka_Bak_poly - Bak_poly*kd_Bak_poly',
             'pBad1433': '-k_Bad_rel*pBad1433 + k_Bad_seq*pBad'}))

    def test_parameters(self):
        """The parameter values shown in the test below have been validated
        against the list in Table 1 of Howells et al."""
        param_list = convert_parameters(self.model, self.p_name_map)
        self.assertEqual(param_list,
           [('k_Bak_cat', 0.5),
            ('k_Bak_inac', 0.1),
            ('ka_tBid_Bcl2', 3),
            ('kd_tBid_Bcl2', 0.002),
            ('ka_Bak_Bcl2', 2),
            ('kd_Bak_Bcl2', 0.002),
            ('k_tBid_rel2', 2),
            ('ka_Bak_poly', 8000),
            ('kd_Bak_poly', 5e-05),
            ('t_Bad_in', 0.01),
            ('t_Bad_out', 0.002),
            ('ka_Bad_Bcl2', 15),
            ('kd_Bad_Bcl2', 0.002),
            ('k_tBid_rel1', 5),
            ('k_Bad_phos1', 0.001),
            ('k_Bad_phos2', 0.0001),
            ('k_Bad_seq', 0.001),
            ('k_Bad_rel', 0.00087)])


def howells_figure2ab(model):
    """Reproduce Figure 2a/b from Howells (2011)."""
    model.parameters['Bcl2_0'].value = 0.1  # Total Bcl2
    model.parameters['Bax_0'].value = 0.2   # Total Bax
    model.parameters['Bid_0'].value = 0.018 # Total tBid
    model.parameters['Bad_0'].value = 0.025 # Total Bad
    Bcl2_free_0 = Parameter('Bcl2_free_0',
            model.parameters['Bcl2_0'].value -
            model.parameters['Bid_0'].value, _export=False) # free Bcl2
    model.add_component(Bcl2_free_0)

    # Reset initial conditions
    model.initial_conditions = []
    c = model.all_components()
    # pBad1433_0 = total Bad
    model.initial(c['Bad'](bf=None, state='C', serine='B'), c['Bad_0'])
    # Bax_inac_0 = total Bax
    model.initial(c['Bax'](bf=None, s1=None, s2=None, state='C'),
                       c['Bax_0'])
    # tBid:Bcl2_0 = total tBid
    model.initial(c['Bid'](state='T', bf=1) % c['Bcl2'](bf=1),
                       c['Bid_0'])
    # Bcl2_free = Bcl2_0 - tBid_0
    model.initial(c['Bcl2'](bf=None), Bcl2_free_0)

    t = np.linspace(0, 300*60, 101)
    x = odesolve(model, t)
    plt.figure()
    plt.ion()
    t = t / 60
    plt.plot(t, x['Bax4_'], label='Bak_poly')
    plt.plot(t, x['Bcl2_'], label='Bcl2')
    plt.plot(t, x['pBad1433_'], label='pBad:14-3-3')
    plt.plot(t, x['Bad_Bcl2_'], label='Bad:Bcl2')
    plt.plot(t, x['Bax_Bcl2_'], label='Bax:Bcl2')
    plt.legend(loc='upper right')


if __name__ == '__main__':
    unittest.main()
