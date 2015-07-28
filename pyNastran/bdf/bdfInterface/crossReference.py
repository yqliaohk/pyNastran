"""
Links up the various cards in the BDF.

For example, with cross referencing...

.. code-block:: python

  >>> model = BDF()
  >>> model.read_bdf(bdf_filename, xref=True)

  >>> nid1 = 1
  >>> node1 = model.nodes[nid1]
  >>> node.nid
  1

  >>> node.xyz
  [1., 2., 3.]

  >>> node.Cid()
  3

  >>> node.cid
  CORD2S, 3, 1, 0., 0., 0., 0., 0., 1.,
          1., 0., 0.
  # get the position in the global frame
  >>> node.Position()
  [4., 5., 6.]

  # get the position with respect to another frame
  >>> node.PositionWRT(model, cid=2)
  [4., 5., 6.]


Without cross referencing...

.. code-block:: python

  >>> model = BDF()
  >>> model.read_bdf(bdf_filename, xref=True)

  >>> nid1 = 1
  >>> node1 = model.nodes[nid1]
  >>> node.nid
  1

  >>> node.xyz
  [1., 2., 3.]

  >>> node.Cid()
  3

  >>> node.cid
  3

  # get the position in the global frame
  >>> node.Position()
  Error!

Cross-referencing allows you to easily jump across cards and also helps
with calculating things like position, area, and mass.  The BDF is designed
around the idea of cross-referencing, so it's recommended that you use it.
"""
# pylint: disable=E1101,C0103,R0902,R0904,R0914

from __future__ import print_function
from six import iteritems, itervalues
from collections import defaultdict
import warnings
import traceback

class CrossReferenceError(RuntimeError):
    pass


class XrefMesh(object):
    """
    Links up the various cards in the BDF.
    """
    def __init__(self):
        """
        The main BDF class defines all the parameters that are used.
        """
        self._ixref_errors = 0
        self._nxref_errors = 100
        self._stop_on_xref_error = True
        self._stored_xref_errors = []

    def cross_reference(self, xref=True,
                        xref_elements=True,
                        xref_nodes_with_elements=True,
                        xref_properties=True,
                        xref_masses=True,
                        xref_materials=True,
                        xref_loads=True,
                        xref_constraints=True,
                        xref_aero=True,
                        xref_sets=True):
        """
        Links up all the cards to the cards they reference

        :param xref:             cross references the model (default=True)
        :param xref_element:     set cross referencing of elements (default=True)
        :param xref_properties:  set cross referencing of properties (default=True)
        :param xref_masses       set cross referencing of CMASS/PMASS (default=True)
        :param xref_materials:   set cross referencing of materials (default=True)
        :param xref_loads:       set cross referencing of loads (default=True)
        :param xref_constraints: set cross referencing of constraints (default=True)
        :param xref_aero:        set cross referencing of CAERO/SPLINEs (default=True)
        :param xref_sets:        set cross referencing of SETx (default=True)

        To only cross-reference nodes:

        .. code-block:: python

          model = BDF()
          model.read_bdf(bdf_filename, xref=False)
          model.cross_reference(xref=True, xref_loads=False, xref_constraints=False,
                                           xref_materials=False, xref_properties=False,
                                           xref_aero=False, xref_masses=False,
                                           xref_sets=False)

        .. warning:: be careful if you call this method
        """
        if xref:
            xref_optimization = True

            self.log.debug("Cross Referencing...")
            self._cross_reference_nodes()
            self._cross_reference_coordinates()

            if xref_elements:
                self._cross_reference_elements()
            if xref_nodes_with_elements:
                self._cross_reference_nodes_with_elements()
            if xref_properties:
                self._cross_reference_properties()
            if xref_masses:
                self._cross_reference_masses()
            if xref_materials:
                self._cross_reference_materials()

            if xref_aero:
                self._cross_reference_aero()
            if xref_constraints:
                self._cross_reference_constraints()
            if xref_loads:
                self._cross_reference_loads()
            if xref_sets:
                self._cross_reference_sets()
            if xref_optimization:
                self._cross_reference_optimization()
            #self.caseControlDeck.cross_reference(self)

    def _cross_reference_constraints(self):
        """
        Links the SPCADD, SPC, SPCAX, SPCD, MPCADD, MPC cards.
        """
        for spcadd in itervalues(self.spcadds):
            self.spcObject.Add(spcadd)
            spcadd.cross_reference(self)

        for spcs in itervalues(self.spcs):
            for spc in spcs:
                self.spcObject.append(spc)
                spc.cross_reference(self)

        for mpcadd in itervalues(self.mpcadds):
            self.mpcObject.Add(mpcadd)
            mpc.cross_reference(mpcadd)

        for mpcs in itervalues(self.mpcs):
            for mpc in mpcs:
                self.mpcObject.append(mpc)
                mpc.cross_reference(self)

        for suport in self.suport:
            suport.cross_reference(self)
        for suport1_id, suport1 in iteritems(self.suport1):
            suport1.cross_reference(self)
        for se_suport in self.se_suport:
            se_suport.cross_reference(self)

    def _cross_reference_coordinates(self):
        """
        Links up all the coordinate cards to other coordinate cards and nodes
        """
        # CORD2x: links the rid to coordinate systems
        # CORD1x: links g1,g2,g3 to grid points
        for coord in itervalues(self.coords):
            coord.cross_reference(self)

        for coord in itervalues(self.coords):
            coord.setup()

    def _cross_reference_aero(self):
        """
        Links up all the aero cards
        """
        for caero in itervalues(self.caeros):
            caero.cross_reference(self)
        for paero in itervalues(self.paeros):
            paero.cross_reference(self)

        for spline in itervalues(self.splines):
            spline.cross_reference(self)
        for aecomp in itervalues(self.aecomps):
            aecomp.cross_reference(self)
        for aelist in itervalues(self.aelists):
            aelist.cross_reference(self)
        for aeparam in itervalues(self.aeparams):
            aeparam.cross_reference(self)
        for aestat in itervalues(self.aestats):
            aestat.cross_reference(self)
        #for aesurf in itervalues(self.aesurf):
            #aesurf.cross_reference(self)
        for aesurfs in itervalues(self.aesurfs):
            aesurfs.cross_reference(self)


            #'AERO',  ## aero
            #'AEROS',  ## aeros
            #'GUST',  ## gusts
            #'FLUTTER',   ## flutters
            #'FLFACT',   ## flfacts
            #'MKAERO1', 'MKAERO2',  ## mkaeros
            #'AECOMP',   ## aecomps
            #'AEFACT',   ## aefacts
            #'AELINK',   ## aelinks
            #'AELIST',   ## aelists
            #'AEPARAM',   ## aeparams
            #'AESTAT',   ## aestats
            #'AESURF',  ## aesurfs


    def _cross_reference_nodes(self):
        """
        Links the nodes to coordinate systems
        """
        gridSet = self.gridSet
        for n in itervalues(self.nodes):
            try:
                n.cross_reference(self, gridSet)
            except:
                self.log.error("Couldn't cross reference GRID.\n%s" % (str(n)))
                raise

        if self.spoints:
            self.spointi = self.spoints.createSPOINTi()

        # GRDPNT for mass calculations
        #if model.has_key()
        #for param_key, param in self.params:
            #if

    def _cross_reference_elements(self):
        """
        Links the elements to nodes, properties (and materials depending on
        the card).
        """
        for elem in itervalues(self.elements):
            try:
                elem.cross_reference(self)
            except (SyntaxError, RuntimeError, AssertionError, KeyError, ValueError) as e:
                self._ixref_errors += 1
                var = traceback.format_exception_only(type(e), e)
                self._stored_xref_errors.append((elem, var))
                if self._ixref_errors > self._nxref_errors:
                    self.pop_xref_errors()
                    #msg = "Couldn't cross reference Element.\n%s" % str(elem)
                    #self.log.error(msg)
                    #raise
        for elem in itervalues(self.rigidElements):
            try:
                elem.cross_reference(self)
            except (SyntaxError, RuntimeError, AssertionError, KeyError, ValueError) as e:
                self._ixref_errors += 1
                var = traceback.format_exception_only(type(e), e)
                self._stored_xref_errors.append((elem, var))
                if self._ixref_errors > self._nxref_errors:
                    self.pop_xref_errors()

    def _cross_reference_nodes_with_elements(self):
        """
        Links the nodes to all connected elements
        """
        nodes = defaultdict(set)
        for element in self.elements.values():
            if element.nodes is not None:
                for node in element.nodes:
                    if node is None:
                        continue
                    try:
                        nodes[node.nid].add(element)
                    except AttributeError:
                        print(element)
                        print('node = %s' % str(node))
                        raise
        for node in self.nodes.values():
            node.elements = nodes[node.nid]

    def _cross_reference_masses(self):
        """
        Links the mass to nodes, properties (and materials depending on
        the card).
        """
        for mass in itervalues(self.masses):
            try:
                mass.cross_reference(self)
            except (SyntaxError, RuntimeError, AssertionError, KeyError, ValueError) as e:
                self._ixref_errors += 1
                var = traceback.format_exception_only(type(e), e)
                self._stored_xref_errors.append((mass, var))
                if self._ixref_errors > self._nxref_errors:
                    self.pop_xref_errors()
                    #msg = "Couldn't cross reference Mass.\n%s" % str(mass)
                    #self.log.error(msg)
                    #raise

        for prop in itervalues(self.properties_mass):
            try:
                prop.cross_reference(self)
            except (SyntaxError, RuntimeError, AssertionError, KeyError, ValueError) as e:
                self._ixref_errors += 1
                var = traceback.format_exception_only(type(e), e)
                self._stored_xref_errors.append((prop, var))
                if self._ixref_errors > self._nxref_errors:
                    self.pop_xref_errors()
                    #msg = "Couldn't cross reference PropertyMass.\n%s" % (str(prop))
                    #self.log.error(msg)
                    #raise

    def _cross_reference_properties(self):
        """
        Links the properties to materials
        """
        for prop in itervalues(self.properties):
            try:
                prop.cross_reference(self)
            except (SyntaxError, RuntimeError, AssertionError, KeyError, ValueError) as e:
                self._ixref_errors += 1
                var = traceback.format_exception_only(type(e), e)
                self._stored_xref_errors.append((prop, var))
                if self._ixref_errors > self._nxref_errors:
                    self.pop_xref_errors()
                    #msg = "Couldn't cross reference Property.\n%s" % (str(prop))
                    #self.log.error(msg)
                    #raise

    def _cross_reference_materials(self):
        """
        Links the materials to materials (e.g. MAT1, CREEP)
        often this is a pass statement
        """
        for mat in itervalues(self.materials):  # MAT1
            try:
                mat.cross_reference(self)
            except (SyntaxError, RuntimeError, AssertionError, KeyError, ValueError) as e:
                self._ixref_errors += 1
                var = traceback.format_exception_only(type(e), e)
                self._stored_xref_errors.append((mat, var))
                if self._ixref_errors > self._nxref_errors:
                    self.pop_xref_errors()
                    #msg = "Couldn't cross reference Material\n%s" % (str(mat))
                    #self.log.error(msg)
                    #raise

        # CREEP - depends on MAT1
        data = [self.MATS1, self.MATS3, self.MATS8,
                self.MATT1, self.MATT2, self.MATT3, self.MATT4, self.MATT5,
                self.MATT8, self.MATT9]
        for material_deps in data:
            for mat in itervalues(material_deps):
                try:
                    mat.cross_reference(self)
                except (SyntaxError, RuntimeError, AssertionError, KeyError, ValueError) as e:
                    self._ixref_errors += 1
                    var = traceback.format_exception_only(type(e), e)
                    self._stored_xref_errors.append((mat, var))
                    if self._ixref_errors > self._nxref_errors:
                        self.pop_xref_errors()
                        #msg = "Couldn't cross reference Material\n%s" % (str(mat))
                        #self.log.error(msg)
                        #raise

    def _cross_reference_loads(self):
        """
        Links the loads to nodes, coordinate systems, and other loads.
        """
        for (lid, sid) in iteritems(self.loads):
            #self.log.debug("lid=%s sid=%s" %(lid, sid))
            for load in sid:
                try:
                    load.cross_reference(self)
                except (SyntaxError, RuntimeError, AssertionError, KeyError, ValueError) as e:
                    self._ixref_errors += 1
                    var = traceback.format_exception_only(type(e), e)
                    self._stored_xref_errors.append((load, var))
                    if self._ixref_errors > self._nxref_errors:
                        self.pop_xref_errors()
                        #self.log.error("lid=%s sid=%s" % (lid, sid))
                        #msg = "Couldn't cross reference Load\n%s" % (str(load))
                        #self.log.error(msg)
                        #raise

        for (lid, sid) in iteritems(self.dloads):
            #self.log.debug("lid=%s sid=%s" %(lid, sid))
            for load in sid:
                try:
                    load.cross_reference(self)
                except (SyntaxError, RuntimeError, AssertionError, KeyError, ValueError) as e:
                    self._ixref_errors += 1
                    var = traceback.format_exception_only(type(e), e)
                    self._stored_xref_errors.append((load, var))
                    if self._ixref_errors > self._nxref_errors:
                        self.pop_xref_errors()

        for (lid, sid) in iteritems(self.dload_entries):
            #self.log.debug("lid=%s sid=%s" %(lid, sid))
            for load in sid:
                try:
                    load.cross_reference(self)
                except (SyntaxError, RuntimeError, AssertionError, KeyError, ValueError) as e:
                    self._ixref_errors += 1
                    var = traceback.format_exception_only(type(e), e)
                    self._stored_xref_errors.append((load, var))
                    if self._ixref_errors > self._nxref_errors:
                        self.pop_xref_errors()

        self.log.debug("done with xref_loads")

    def _cross_reference_sets(self):
        for set_obj in self.asets:
            set_obj.cross_reference(self)
        for set_obj in self.bsets:
            set_obj.cross_reference(self)
        for set_obj in self.csets:
            set_obj.cross_reference(self)
        for set_obj in self.qsets:
            set_obj.cross_reference(self)
        for name, set_objs in iteritems(self.usets):
            for set_obj in set_objs:
                set_obj.cross_reference(self)

        # superelements
        for key, set_obj in iteritems(self.se_sets):
            set_obj.cross_reference(self)
        for set_obj in self.se_bsets:
            set_obj.cross_reference(self)
        for set_obj in self.se_csets:
            set_obj.cross_reference(self)
        for set_obj in self.se_qsets:
            set_obj.cross_reference(self)
        for set_obj in self.se_usets:
            set_obj.cross_reference(self)

    def _cross_reference_optimization(self):
        for key, dresp in iteritems(self.dresps):
            dresp.cross_reference(self)
        for key, dconstr in iteritems(self.dconstrs):
            dconstr.cross_reference(self)
