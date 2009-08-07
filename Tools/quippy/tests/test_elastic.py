from quippy import *
import unittest, itertools, sys, quippy, os
from quippytest import *
from quippy.elastic import *

class TestElastic(QuippyTestCase):

   """Tests of elastic constant calculation.

   We test with a cubic Silicon lattice, since this also has most of the symmetries of the lower-symmetry crystal families"""

   def setUp(self):
      self.xml="""
      <SW_params n_types="2" label="PRB_31_plus_H">
      <comment> Stillinger and Weber, Phys. Rev. B  31 p 5262 (1984), extended for other elements </comment>
      <per_type_data type="1" atomic_num="1" />
      <per_type_data type="2" atomic_num="14" />
      <per_pair_data atnum_i="1" atnum_j="1" AA="0.0" BB="0.0"
            p="0" q="0" a="1.0" sigma="1.0" eps="0.0" />
      <per_pair_data atnum_i="1" atnum_j="14" AA="8.581214" BB="0.0327827"
            p="4" q="0" a="1.25" sigma="2.537884" eps="2.1672" />
      <per_pair_data atnum_i="14" atnum_j="14" AA="7.049556277" BB="0.6022245584"
            p="4" q="0" a="1.80" sigma="2.0951" eps="2.1675" />

      <!-- triplet terms: atnum_c is the center atom, neighbours j and k -->
      <per_triplet_data atnum_c="1"  atnum_j="1"  atnum_k="1"
            lambda="21.0" gamma="1.20" eps="2.1675" />
      <per_triplet_data atnum_c="1"  atnum_j="1"  atnum_k="14"
            lambda="21.0" gamma="1.20" eps="2.1675" />
      <per_triplet_data atnum_c="1"  atnum_j="14" atnum_k="14"
            lambda="21.0" gamma="1.20" eps="2.1675" />

      <per_triplet_data atnum_c="14" atnum_j="1"  atnum_k="1"
            lambda="21.0" gamma="1.20" eps="2.1675" />
      <per_triplet_data atnum_c="14" atnum_j="1"  atnum_k="14"
            lambda="21.0" gamma="1.20" eps="2.1675" />
      <per_triplet_data atnum_c="14" atnum_j="14" atnum_k="14"
            lambda="21.0" gamma="1.20" eps="2.1675" />
      </SW_params>
      """

      self.C_ref = farray([[ 151.4276439 ,   76.57244456,   76.57244456,    0.        ,    0.        ,    0.        ],
                           [  76.57244456,  151.4276439 ,   76.57244456,    0.        ,    0.        ,    0.        ],
                           [  76.57244456,   76.57244456,  151.4276439 ,    0.        ,    0.        ,    0.        ],
                           [   0.        ,    0.        ,    0.        ,  109.85498798,    0.        ,    0.        ],
                           [   0.        ,    0.        ,    0.        ,    0.        ,  109.85498798,    0.        ],
                           [   0.        ,    0.        ,    0.        ,    0.        ,   0.        ,  109.85498798]])
      
      self.C_err_ref = farray([[ 1.73091718,  1.63682097,  1.63682097,  0.        ,  0.        ,     0.        ],
                               [ 1.63682097,  1.73091718,  1.63682097,  0.        ,  0.        ,     0.        ],
                               [ 1.63682097,  1.63682097,  1.73091718,  0.        ,  0.        ,     0.        ],
                               [ 0.        ,  0.        ,  0.        ,  1.65751232,  0.        ,     0.        ],
                               [ 0.        ,  0.        ,  0.        ,  0.        ,  1.65751232,     0.        ],
                               [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,     1.65751232]])

      self.C_ref_relaxed = farray([[ 151.28712587,   76.5394162 ,   76.5394162 ,    0.        ,
                                     0.        ,    0.        ],
                                   [  76.5394162 ,  151.28712587,   76.5394162 ,    0.        ,
                                      0.        ,    0.        ],
                                   [  76.5394162 ,   76.5394162 ,  151.28712587,    0.        ,
                                      0.        ,    0.        ],
                                   [   0.        ,    0.        ,    0.        ,   56.32421772,
                                       0.        ,    0.        ],
                                   [   0.        ,    0.        ,    0.        ,    0.        ,
                                       56.32421772,    0.        ],
                                   [   0.        ,    0.        ,    0.        ,    0.        ,
                                       0.        ,   56.32421772]])

      self.C_err_ref_relaxed = farray([[ 1.17748661,  1.33333615,  1.33333615,  0.        ,  0.        ,
                                         0.        ],
                                       [ 1.33333615,  1.17748661,  1.33333615,  0.        ,  0.        ,
                                         0.        ],
                                       [ 1.33333615,  1.33333615,  1.17748661,  0.        ,  0.        ,
                                         0.        ],
                                       [ 0.        ,  0.        ,  0.        ,  0.18959684,  0.        ,
                                         0.        ],
                                       [ 0.        ,  0.        ,  0.        ,  0.        ,  0.18959684,
                                         0.        ],
                                       [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
                                         0.18959684]])

      verbosity_push(SILENT)

   def tearDown(self):
      verbosity_pop()
      
   def testcubic_unrelaxed(self):

      pot = Potential('IP SW', self.xml)
      metapot = MetaPotential('Simple', pot)

      at0 = diamond(5.43, 14)
      metapot.minim(at0, 'cg', 1e-7, 100, do_pos=True, do_lat=True)

      strained_configs = generate_strained_configs(at0, 'cubic')
      stressed_configs = calc_stress(strained_configs, metapot, relax=False)

      C, C_err = fit_elastic_constants(stressed_configs, 'cubic', verbose=False, graphics=False)

      self.assertArrayAlmostEqual(C, self.C_ref)
      self.assertArrayAlmostEqual(C_err, self.C_err_ref)
      
   def testcubic_relaxed(self):

      pot = Potential('IP SW', self.xml)
      metapot = MetaPotential('Simple', pot)

      at0 = diamond(5.43, 14)
      metapot.minim(at0, 'cg', 1e-7, 100, do_pos=True, do_lat=True)

      strained_configs = generate_strained_configs(at0, 'cubic')
      stressed_configs = calc_stress(strained_configs, metapot, relax=True)

      C, C_err = fit_elastic_constants(stressed_configs, 'cubic', verbose=False, graphics=False)

      self.assertArrayAlmostEqual(C, self.C_ref_relaxed)
      self.assertArrayAlmostEqual(C_err, self.C_err_ref_relaxed)


   def testorthorhombic_unrelaxed(self):

      pot = Potential('IP SW', self.xml)
      metapot = MetaPotential('Simple', pot)

      at0 = diamond(5.43, 14)
      metapot.minim(at0, 'cg', 1e-7, 100, do_pos=True, do_lat=True)

      strained_configs = generate_strained_configs(at0, 'orthorhombic')
      stressed_configs = calc_stress(strained_configs, metapot, relax=False)

      C, C_err = fit_elastic_constants(stressed_configs, 'orthorhombic', verbose=False, graphics=False)

      self.assertArrayAlmostEqual(C, self.C_ref, tol=0.1)
      
   def testorthorhombic_relaxed(self):

      pot = Potential('IP SW', self.xml)
      metapot = MetaPotential('Simple', pot)

      at0 = diamond(5.43, 14)
      metapot.minim(at0, 'cg', 1e-7, 100, do_pos=True, do_lat=True)

      strained_configs = generate_strained_configs(at0, 'orthorhombic')
      stressed_configs = calc_stress(strained_configs, metapot, relax=True)

      C, C_err = fit_elastic_constants(stressed_configs, 'orthorhombic', verbose=False, graphics=False)

      self.assertArrayAlmostEqual(C, self.C_ref_relaxed, tol=0.1)

   def testmonoclinic_unrelaxed(self):

      pot = Potential('IP SW', self.xml)
      metapot = MetaPotential('Simple', pot)

      at0 = diamond(5.43, 14)
      metapot.minim(at0, 'cg', 1e-7, 100, do_pos=True, do_lat=True)

      strained_configs = generate_strained_configs(at0, 'monoclinic')
      stressed_configs = calc_stress(strained_configs, metapot, relax=False)

      C, C_err = fit_elastic_constants(stressed_configs, 'monoclinic', verbose=False, graphics=False)

      self.assertArrayAlmostEqual(C, self.C_ref, tol=0.2)
      
   def testmonoclinic_relaxed(self):

      pot = Potential('IP SW', self.xml)
      metapot = MetaPotential('Simple', pot)

      at0 = diamond(5.43, 14)
      metapot.minim(at0, 'cg', 1e-7, 100, do_pos=True, do_lat=True)

      strained_configs = generate_strained_configs(at0, 'monoclinic')
      stressed_configs = calc_stress(strained_configs, metapot, relax=True)

      C, C_err = fit_elastic_constants(stressed_configs, 'monoclinic', verbose=False, graphics=False)

      self.assertArrayAlmostEqual(C, self.C_ref_relaxed, tol=0.2)


   def testtriclinic_unrelaxed(self):

      pot = Potential('IP SW', self.xml)
      metapot = MetaPotential('Simple', pot)

      at0 = diamond(5.43, 14)
      metapot.minim(at0, 'cg', 1e-7, 100, do_pos=True, do_lat=True)

      strained_configs = generate_strained_configs(at0, 'triclinic')
      stressed_configs = calc_stress(strained_configs, metapot, relax=False)

      C, C_err = fit_elastic_constants(stressed_configs, 'triclinic', verbose=False, graphics=False)

      self.assertArrayAlmostEqual(C, self.C_ref, tol=0.2)
      
   def testtriclinic_relaxed(self):

      pot = Potential('IP SW', self.xml)
      metapot = MetaPotential('Simple', pot)

      at0 = diamond(5.43, 14)
      metapot.minim(at0, 'cg', 1e-7, 100, do_pos=True, do_lat=True)

      strained_configs = generate_strained_configs(at0, 'triclinic')
      stressed_configs = calc_stress(strained_configs, metapot, relax=True)

      C, C_err = fit_elastic_constants(stressed_configs, 'triclinic', verbose=False, graphics=False)

      self.assertArrayAlmostEqual(C, self.C_ref_relaxed, tol=0.2)



def getTestSuite():
   tl = unittest.TestLoader()
   return unittest.TestSuite(tl.loadTestsFromTestCase(TestElastic))

if __name__ == '__main__':
   suite = getTestSuite()
   unittest.TextTestRunner(verbosity=2).run(suite)
