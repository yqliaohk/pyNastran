from __future__ import (nested_scopes, generators, division, absolute_import,
                        print_function, unicode_literals)
from struct import Struct

from pyNastran.op2.op2_helper import polar_to_real_imag

#91  -> PENTANL
#2   -> BEAM
#33  -> TUBE
#92  -> CONRODNL


class ComplexElementsStressStrain(object):

    def OES_Rod1_alt(self):
        """
        genericStressReader - works on CROD_1, CELAS2_12
        stress & strain
        format_code=1 sort_code=1 (eid,axial,axial,torsion,torsion)
        """
        dt = self.nonlinear_factor
        (format1, extract) = self.getOUG_FormatStart()
        ntotal = 12
        format1 += '4f'
        format1 = bytes(format1)
        is_magnitude_phase = self.is_magnitude_phase()

        n = 0
        s = Struct(format1)
        nelements = len(self.data) // ntotal
        for i in xrange(nEntries):
            edata = self.data[n:n + ntotal]
            (eid, axialReal, axialImag, torsionReal,
                torsionImag) = s.unpack(edata)

            if is_magnitude_phase:
                (axial) = polar_to_real_imag(axialReal, axialImag)
                (torsion) = polar_to_real_imag(torsionReal, torsionImag)
            else:
                axial = complex(axialReal, axialImag)
                torsion = complex(torsionReal, torsionImag)

            #print "out = ",out
            eid = extract(eid, dt)
            self.obj.add_new_eid(dt, eid, axial, torsion)
            n += ntotal
        self.data = self.data[n:]

    def OES_Elas1_alt(self):
        """
        genericStressReader - works on CROD_1, CELAS2_12
        stress & strain
        format_code=1 sort_code=1 (eid,axial,axial,torsion,torsion)
        """
        dt = self.nonlinear_factor
        (format1, extract) = self.getOUG_FormatStart()
        nTotal = 12
        format1 += '2f'
        format1 = bytes(format1)
        is_magnitude_phase = self.is_magnitude_phase()

        n = 0
        s = Struct(format1)
        nEntries = len(self.data) // nTotal
        for i in xrange(nEntries):
            eData = self.data[n:n + nTotal]
            (eid, axialReal, axialImag) = s.unpack(eData)

            if is_magnitude_phase:
                axial = polar_to_real_imag(axialReal, axialImag)
            else:
                axial = complex(axialReal, axialImag)

            #print "out = ",out
            eid = extract(eid, dt)
            self.obj.add_new_eid(dt, eid, axial)
            n += nTotal
        self.data = self.data[n:]

    def OES_CBAR_34_alt(self):
        dt = self.nonlinear_factor
        #print "len(data) = ",len(self.data)
        assert self.num_wide == 19, 'invalid num_wide...num_wide=%s' % self.num_wide

        (format1, extract) = self.getOUG_FormatStart()
        format1 += '18f'
        format1 = bytes(format1)
        is_magnitude_phase = self.is_magnitude_phase()

        n = 0
        ntotal = 76
        s = Struct(format1)
        nelements = len(self.data) // ntotal
        for i in xrange(nelements):
            edata = self.data[n:n+ntotal]
            n += ntotal

            (eid_device, s1ar, s2ar, s3ar, s4ar, axialr,
             s1ai, s2ai, s3ai, s4ai, axiali,
             s1br, s2br, s3br, s4br,
             s1bi, s2bi, s3bi, s4bi) = s.unpack(edata)

            if is_magnitude_phase:
                s1a = polar_to_real_imag(s1ar, s1ai)
                s1b = polar_to_real_imag(s1br, s1bi)
                s2a = polar_to_real_imag(s2ar, s2ai)
                s2b = polar_to_real_imag(s2br, s2bi)
                s3a = polar_to_real_imag(s3ar, s3ai)
                s3b = polar_to_real_imag(s3br, s3bi)
                s4a = polar_to_real_imag(s4ar, s4ai)
                s4b = polar_to_real_imag(s4br, s4bi)
                axial = polar_to_real_imag(axialr, axiali)

            else:
                s1a = complex(s1ar, s1ai)
                s1b = complex(s1br, s1bi)
                s2a = complex(s2ar, s2ai)
                s2b = complex(s2br, s2bi)
                s3a = complex(s3ar, s3ai)
                s3b = complex(s3br, s3bi)
                s4a = complex(s4ar, s4ai)
                s4b = complex(s4br, s4bi)
                axial = complex(axialr, axiali)

            eid = extract(eid_device, dt)
            self.obj.add_new_eid('CBAR', dt, eid, s1a, s2a, s3a, s4a, axial,
                                                  s1b, s2b, s3b, s4b)
            #print "eid=%i s1=%i s2=%i s3=%i s4=%i axial=%-5i" %(eid,s1a,s2a,s3a,s4a,axial)
            #print "         s1=%i s2=%i s3=%i s4=%i"          %(s1b,s2b,s3b,s4b)
        self.data = self.data[n:]

    def OES_CQUAD4_33_alt(self):
        """
        GRID-ID  DISTANCE,NORMAL-X,NORMAL-Y,SHEAR-XY
        """
        dt = self.nonlinear_factor
        (format1, extract) = self.getOUG_FormatStart()
        format1 += '14f'
        format1 = bytes(format1)
        is_magnitude_phase = self.is_magnitude_phase()

        nNodes = 0  # centroid + 4 corner points

        assert self.num_wide == 15, 'invalid num_wide...num_wide=%s' % self.num_wide

        ntotal = 4 * (2 + 15 * 5)
        nelements = len(self.data) // ntotal
        n = 0
        s1 = Struct(format1)
        s2 = Struct(b'i14f')
        for i in xrange(nelements):
            edata = self.data[n:n+60]  # 4*15=60
            n += 60
            out = s1.unpack(edata)  # 15
            if self.make_op2_debug:
                self.op2_debug.write('%s\n' % (str(out)))
            (eid, fd1, sx1r, sx1i, sy1r, sy1i, txy1r, txy1i,
                  fd2, sx2r, sx2i, sy2r, sy2i, txy2r, txy2i) = out

            if is_magnitude_phase:
                sx1 = polar_to_real_imag(sx1r, sx1i)
                sx2 = polar_to_real_imag(sx2r, sx2i)
                sy1 = polar_to_real_imag(sy1r, sy1i)
                sy2 = polar_to_real_imag(sy2r, sy2i)
                txy1 = polar_to_real_imag(txy1r, txy1i)
                txy2 = polar_to_real_imag(txy2r, txy2i)
            else:
                sx1 = complex(sx1r, sx1i)
                sx2 = complex(sx2r, sx2i)
                sy1 = complex(sy1r, sy1i)
                sy2 = complex(sy2r, sy2i)
                txy1 = complex(txy1r, txy1i)
                txy2 = complex(txy2r, txy2i)

            eid = extract(eid, dt)

            #print "eid=%i grid=%s fd1=%-3.1f sx1=%s sy1=%s txy1=%s" %(eid,'C',fd1,sx1,sy1,txy1)
            #print   "             fd2=%-3.1f sx2=%s sy2=%s txy2=%s\n"       %(fd2,sx2,sy2,txy2)
            #print "nNodes = ",nNodes
            self.obj.add_new_eid('CQUAD4', dt, eid, 'CEN/4', fd1, sx1, sy1, txy1)
            self.obj.add(dt, eid, 'CEN/4', fd2, sx2, sy2, txy2)
            for nodeID in xrange(nNodes):  # nodes pts
                edata = self.data[n:n+60]  # 4*15=60
                n += 60
                out = s2.unpack(edata)
                if self.make_op2_debug:
                    self.op2_debug.write('%s\n' % (str(out)))
                (grid, fd1, sx1r, sx1i, sy1r, sy1i, txy1r, txy1i,
                       fd2, sx2r, sx2i, sy2r, sy2i, txy2r, txy2i) = out

                if is_magnitude_phase:
                    sx1 = polar_to_real_imag(sx1r, sx1i)
                    sx2 = polar_to_real_imag(sx2r, sx2i)
                    sy1 = polar_to_real_imag(sy1r, sy1i)
                    sy2 = polar_to_real_imag(sy2r, sy2i)
                    txy1 = polar_to_real_imag(txy1r, txy1i)
                    txy2 = polar_to_real_imag(txy2r, txy2i)
                else:
                    sx1 = complex(sx1r, sx1i)
                    sx2 = complex(sx2r, sx2i)
                    sy1 = complex(sy1r, sy1i)
                    sy2 = complex(sy2r, sy2i)
                    txy1 = complex(txy1r, txy1i)
                    txy2 = complex(txy2r, txy2i)

                #print "eid=%i grid=%i fd1=%i sx1=%i sy1=%i txy1=%i\n" %(eid,grid,fd1,sx1,sy1,txy1)
                #print "               fd2=%i sx2=%i sy2=%i txy2=%i\n"          %(fd2,sx2,sy2,txy2)
                self.obj.addNewNode(dt, eid, grid, fd1, sx1, sy1, txy1)
                self.obj.add(dt, eid, grid, fd2, sx2, sy2, txy2)
        self.data = self.data[n:]

    def OES_CQUAD4NL_90_alt(self):
        dt = self.nonlinear_factor
        (format1, extract) = self.getOUG_FormatStart()

        assert self.num_wide == 25, "num_wide=%s not 25" % (self.num_wide)
        nTotal = 100  # 4*25
        format1 += '24f'
        format1 = bytes(format1)

        s = Struct(format1)
        while len(self.data) >= nTotal:
            eData = self.data[0:nTotal]
            self.data = self.data[nTotal:]
            out = s.unpack(eData)  # num_wide=25
            (eid, fd1, sx1, sy1, xxx, txy1, es1, eps1, ecs1, ex1, ey1, xxx, exy1,
                  fd2, sx2, sy2, xxx, txy2, es2, eps2, ecs2, ex2, ey2, xxx, exy2) = out
            eid = extract(eid, dt)

            data = (eid, fd1, sx1, sy1, xxx, txy1, es1, eps1,
                    ecs1, ex1, ey1, xxx, exy1)
            self.obj.add_new_eid(self.element_type, dt, data)
            data = (eid, fd2, sx2, sy2, xxx, txy2, es2, eps2,
                    ecs2, ex2, ey2, xxx, exy2)
            self.obj.add(dt, data)

            #print "eid=%s axial=%s equivStress=%s totalStrain=%s effPlasticCreepStrain=%s effCreepStrain=%s linearTorsionalStresss=%s" %(eid,axial,equivStress,totalStrain,effPlasticCreepStrain,effCreepStrain,linearTorsionalStresss)

            if self.make_op2_debug:
                self.op2_debug.write('%s\n' % (str(out)))

    def OES_CBUSH1D_40_alt(self):
        dt = self.nonlinear_factor
        (format1, extract) = self.getOUG_FormatStart()
        is_magnitude_phase = self.is_magnitude_phase()

        assert self.num_wide == 9, "num_wide=%s not 9" % (self.num_wide)
        nTotal = 36  # 4*9
        format1 += '8f'
        format1 = bytes(format1)
        s = Struct(format1)
        while len(self.data) >= nTotal:
            eData = self.data[0:nTotal]
            self.data = self.data[nTotal:]

            out = s.unpack(eData)  # num_wide=25
            (eid, fer, uer, aor, aer,
                  fei, uei, aoi, aei) = out
            eid = extract(eid, dt)

            if is_magnitude_phase:
                fe = polar_to_real_imag(fer, fei)
                ue = polar_to_real_imag(uer, uei)
                ao = polar_to_real_imag(aor, aoi)
                ae = polar_to_real_imag(aer, aei)
            else:
                fe = complex(fer, fei)
                ue = complex(uer, uei)
                ao = complex(aor, aoi)
                ae = complex(aer, aei)

            self.obj.add_new_eid(self.element_type, dt, eid, fe, ue, ao, ae)

    def OES_CBUSH_102_alt(self):
        dt = self.nonlinear_factor
        (format1, extract) = self.getOUG_FormatStart()
        is_magnitude_phase = self.is_magnitude_phase()

        assert self.num_wide == 13, "num_wide=%s not 14" % (self.num_wide)
        nTotal = 52  # 4*13
        format1 += '12f'
        format1 = bytes(format1)
        s = Struct(format1)
        while len(self.data) >= nTotal:
            eData = self.data[0:nTotal]
            self.data = self.data[nTotal:]

            out = s.unpack(eData)  # num_wide=25
            (eid, txr,tyr,tzr,rxr,ryr,rzr,
                  txi,tyi,tzi,rxi,ryi,rzi) = out
            eid = extract(eid, dt)

            if is_magnitude_phase:
                tx = polar_to_real_imag(txr, txi)
                ty = polar_to_real_imag(tyr, tyi)
                tz = polar_to_real_imag(tzr, tzi)
                rx = polar_to_real_imag(rxr, rxi)
                ry = polar_to_real_imag(ryr, ryi)
                rz = polar_to_real_imag(rzr, rzi)
            else:
                tx = complex(txr, txi)
                ty = complex(tyr, tyi)
                tz = complex(tzr, tzi)
                rx = complex(rxr, rxi)
                ry = complex(ryr, ryi)
                rz = complex(rzr, rzi)

            #data = (eid, tx, ty, tz, rx, ry, rz)
            self.obj.add_new_eid(self.element_type, dt, eid, tx, ty, tz, rx, ry, rz)

    def OES_CQUAD4_144_alt(self):
        """
        GRID-ID  DISTANCE,NORMAL-X,NORMAL-Y,SHEAR-XY,ANGLE,MAJOR MINOR,VONMISES
        """
        if self.make_op2_debug:
            self.op2_debug.write('---CQUAD4_144---\n')

        #self.print_section(20)
        #term = data[0:4] CEN/
        #data = data[4:]
        #self.print_block(self.data)
        #assert self.num_wide==87,'invalid num_wide...num_wide=%s' %(self.num_wide)
        #if self.num_wide==87: # 2+(17-1)*5 = 87 -> 87*4 = 348

        if self.element_type == 144:  # CQUAD4
            ntotal = 308  # 2+15*5 = 77 -> 87*4 = 308
            nNodes = 4    # centroid + 4 corner points
            eType = 'CQUAD4'
        elif self.element_type == 64:  # CQUAD8 - done
            ntotal = 308  # 2+15*5 = 77 -> 77*4 = 308
            nNodes = 4    # centroid + 4 corner points
            eType = 'CQUAD8'
        elif self.element_type == 82:  # CQUADR
            ntotal = 308  # 2+15*5 = 77 -> 87*4 = 308
            nNodes = 4    # centroid + 4 corner points
            eType = 'CQUAD4'  # TODO write the word CQUADR

        elif self.element_type == 75:  # CTRIA6
            ntotal = 248  # 2+15*4 = 62 -> 62*4 = 248
            nNodes = 3    # centroid + 3 corner points
            eType = 'CTRIA6'
        elif self.element_type == 70:  # CTRIAR
            ntotal = 248  # 2+15*4 = 62 -> 62*4 = 248
            nNodes = 3    # centroid + 3 corner points
            eType = 'CTRIAR'  # TODO write the word CTRIAR
        else:
            raise RuntimeError('element_type=%s nTotal not defined...' %
                            (self.element_type))

        assert ntotal == self.num_wide * 4, 'eType=%s num_wide*4=%s not nTotal=%s' % (self.element_type, self.num_wide * 4, nTotal)
        dt = self.nonlinear_factor
        (format1, extract) = self.getOUG_FormatStart()
        format1 += '14f'
        format1 = bytes(format1)
        is_magnitude_phase = self.is_magnitude_phase()
        n = 0
        nelements = len(self.data) // ntotal
        gridC = 'CEN/' + str(nNodes)
        s1 = Struct(b'i4s')
        s2 = Struct(format1)
        s3 = Struct(b'i14f')
        for i in xrange(nelements):
            (eid, _) = s1.unpack(self.data[n:n+8])
            n += 8
            eid = extract(eid, dt)
            edata = self.data[n:n+60]  # 4*15
            n += 60
            out = s2.unpack(edata)  # len=15*4
            if self.make_op2_debug:
                self.op2_debug.write('%s\n' % (str(out)))
            (grid, fd1, sx1r, sx1i, sy1r, sy1i, txy1r, txy1i,
                   fd2, sx2r, sx2i, sy2r, sy2i, txy2r, txy2i) = out

            if is_magnitude_phase:
                sx1 = polar_to_real_imag(sx1r, sx1i)
                sy1 = polar_to_real_imag(sy1r, sy1i)
                sx2 = polar_to_real_imag(sx2r, sx2i)
                sy2 = polar_to_real_imag(sy2r, sy2i)
                txy1 = polar_to_real_imag(txy1r, txy1i)
                txy2 = polar_to_real_imag(txy2r, txy2i)
            else:
                sx1 = complex(sx1r, sx1i)
                sy1 = complex(sy1r, sy1i)
                sx2 = complex(sx2r, sx2i)
                sy2 = complex(sy2r, sy2i)
                txy1 = complex(txy1r, txy1i)
                txy2 = complex(txy2r, txy2i)

            self.obj.add_new_eid(eType, dt, eid, gridC, fd1, sx1, sy1, txy1)
            self.obj.add(dt, eid, gridC, fd2, sx2, sy2, txy2)
            for nodeID in xrange(nNodes):  # nodes pts
                edata = self.data[n:n+60]  # 4*15=60
                n += 60
                out = s3.unpack(edata)
                if self.make_op2_debug:
                    self.op2_debug.write('%s\n' % (str(out)))
                (grid, fd1, sx1r, sx1i, sy1r, sy1i, txy1r, txy1i,
                 fd2, sx2r, sx2i, sy2r, sy2i, txy2r, txy2i) = out

                if is_magnitude_phase:
                    sx1 = polar_to_real_imag(sx1r, sx1i)
                    sx2 = polar_to_real_imag(sx2r, sx2i)
                    sy1 = polar_to_real_imag(sy1r, sy1i)
                    sy2 = polar_to_real_imag(sy2r, sy2i)
                    txy1 = polar_to_real_imag(txy1r, txy1i)
                    txy2 = polar_to_real_imag(txy2r, txy2i)
                else:
                    sx1 = complex(sx1r, sx1i)
                    sx2 = complex(sx2r, sx2i)
                    sy1 = complex(sy1r, sy1i)
                    sy2 = complex(sy2r, sy2i)
                    txy1 = complex(txy1r, txy1i)
                    txy2 = complex(txy2r, txy2i)

                #print "eid=%i grid=%i fd1=%i sx1=%i sy1=%i txy1=%i"   %(eid,grid,fd1,sx1,sy1,txy1)
                #print "               fd2=%i sx2=%i sy2=%i txy2=%i\n"          %(fd2,sx2,sy2,txy2)
                self.obj.addNewNode(dt, eid, grid, fd1, sx1, sy1, txy1)
                self.obj.add(dt, eid, grid, fd2, sx2, sy2, txy2)

            #print '--------------------'
        self.data = self.data[n:]

    def OES_CTRIA3_74_alt(self):  # in progress
        """
        DISTANCE,NORMAL-X,NORMAL-Y,SHEAR-XY,ANGLE,MAJOR,MINOR,VONMISES
        stress is extracted at the centroid
        """
        assert self.num_wide == 15, 'invalid num_wide...num_wide=%s' % (
            self.num_wide)

        dt = self.nonlinear_factor
        (format1, extract) = self.getOUG_FormatStart()
        format1 += '14f'
        format1 = bytes(format1)
        is_magnitude_phase = self.is_magnitude_phase()

        n = 0
        s = Struct(format1)
        nelements = len(self.data) // 60
        for i in xrange(nelements):
            eData = self.data[n:n+60]  # 4*15=60
            out = s.unpack(eData)

            (eid, fd1, sx1r, sx1i, sy1r, sy1i, txy1r, txy1i,
                  fd2, sx2r, sx2i, sy2r, sy2i, txy2r, txy2i) = out

            if is_magnitude_phase:
                sx1 = polar_to_real_imag(sx1r, sx1i)
                sy1 = polar_to_real_imag(sy1r, sy1i)
                sx2 = polar_to_real_imag(sx2r, sx2i)
                sy2 = polar_to_real_imag(sy2r, sy2i)
                txy1 = polar_to_real_imag(txy1r, txy1i)
                txy2 = polar_to_real_imag(txy2r, txy2i)
            else:
                sx1 = complex(sx1r, sx1i)
                sy1 = complex(sy1r, sy1i)
                sx2 = complex(sx2r, sx2i)
                sy2 = complex(sy2r, sy2i)
                txy1 = complex(txy1r, txy1i)
                txy2 = complex(txy2r, txy2i)

            eid = extract(eid, dt)
            #print "eid=%i fd1=%i sx1=%i sy1=%i txy1=%i" %(eid,fd1,sx1,sy1,txy1)
            #print  "      fd2=%i sx2=%i sy2=%i txy2=%i\n"   %(fd2,sx2,sy2,txy2)
            self.obj.add_new_eid('CTRIA3', dt, eid, 'CEN/3', fd1, sx1, sy1, txy1)
            self.obj.add(dt, eid, 'CEN/3', fd2, sx2, sy2, txy2)
            if self.make_op2_debug:
                self.op2_debug.write('%s\n' % str(out))
            n += 60
        self.data = self.data[n:]
