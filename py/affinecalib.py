def CalibrateFunc(self):
        #for each calibration marker, construct matrix to do least squares with
        numrows = 2*len(self.calibrationmarkers)
        A = numpy.zeros((numrows, 9))
        B = numpy.zeros((numrows, 1))
        # marker 1: 0,0
        # marker 2: 1,0
        # marker 3: 0,1
        # marker 4: 1,1
        #B(0),B(1) = 0   #marker 1
        B[2] = 1; B[5]=1 #marker 2,3
        B[4] = 1;
        B[6] = 0; B[7]=1 
        #B[3] = 1; B[4]=1 #marker 2,3
        #B[6] = 1; B[7]=1 #marker 4
        i = 0
        for calib in self.calibrationmarkers:
            A[2*i, 0] = calib.pos[0]; A[2*i, 1] = calib.pos[1]
            A[2*i+1, 3] = calib.pos[0]; A[2*i+1, 4] = calib.pos[1]
            A[2*i,2] = 1; A[2*i+1,5] = 1
            A[2*i,6] = -B[2*i]*calib.pos[0]
            A[2*i,7] = -B[2*i]*calib.pos[1]
            A[2*i,8] = -B[2*i]
            
            A[2*i+1,6] = -B[2*i+1]*calib.pos[0]
            A[2*i+1,7] = -B[2*i+1]*calib.pos[1]
            A[2*i+1,8] = -B[2*i+1]
            
            i = i + 1
        
        
        #create our polygon
        px = numpy.array([-1, 8, 13, -4])
        py = numpy.array([-1, 3, 11, 8])

        #compute coefficients
        
        A=numpy.bmat('1 0 0 0;1 1 0 0;1 1 1 1;1 0 1 0')
        AI = numpy.invert(A)
        a = AI*px';
	b = AI*py';

	%plot random internal points
	plot_points_in_poly(px,py,a,b);

	%classify points as internal or external
	plot_internal_and_external_points(px,py,a,b);
            
        #print "A shape: " + str(A.shape) + " and B shape: " + str(B.shape)
        #find pseudoinverse to unit frame -- least squares
        #ata = A.T*A
        U, s, V = numpy.linalg.svd(A, full_matrices=True)
        #sh = s
        #print "USV: \n" + str(U) + "\n" + str(s) + "\n" + str(V)
        #n = min(s.shape)
        #print "got n: ", str(n), " and ", str(s.shape)
        #print "U shape: " + str(U.shape) + " and V shape: " + str(V.shape)
        #for i in range(0, n):
        #    if(sh[i] != 0):
        #        sh[i] = 1.0/sh[i]
        
        #ata_inv = V.conj().T*numpy.diag(sh)*U.conj().T
        
        # get eigenvalues
        #L = numpy.dot(A.T,B)
        #L = numpy.dot(ata_inv, B)
        #print "Here we are: ", str(L.shape)
        #affine is reconstruction of lambda
        L = V[8,:].T
        #L = L / numpy.linalg.norm(L)
        H = numpy.zeros((3,3))
        for i in range(0,9):
            H[i/3,i%3] = L[i]
        #H[2,2] = 1
        self.homography = H
        
        print "Got Homography: \n", H
        print "Got L: \n", L
        print "From: \n", A
        self.W = numpy.array([H[2,0], H[2,1], 1])
        return H