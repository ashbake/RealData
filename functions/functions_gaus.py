#Module Defining Optimizing Function For splinefit_v#.py

import numpy as np
from scipy import interpolate
import matplotlib.pylab as plt
from scipy.signal import gaussian as gaus


"""Optimizing function to pass to nlopt"""
def optfunc(x,pix,flux,N,front,end,nspec,errs):
    #pull out coeff                                                 
    coef = x[0:(N+4)]
    coeff = np.concatenate((coef,np.zeros(4)),axis = 1)

    #pull out knots, append                                                          
    knots_in = x[(N+4):(N+4) + N]
    knots = np.concatenate((front,knots_in,end))

    #pull out dxm'sd
    dxm = x[(N+4) + N:(N+4)+N+nspec]

    #pull out dxb's
    dxb = x[(N+4) + N + nspec:(N+4)+ N + 2*nspec]

    #pull out scalings                                                 
    norm = x[(N+4) + N + 2*nspec:(N+4)+N + 3*nspec]

    #pull out tau's
    tau = x[(N+4)+N+3*nspec:(N+4) + N + 4*nspec]

    #pull out sigmas
    sig = x[(N+4)+N+4*nspec:(N+4)+N+5*nspec]


    #define tck, fit
    tck = (knots,coeff,3)
    longpix = np.linspace(pix[0][0],pix[0][-1],5*(len(pix[0])))
    longfit = np.zeros((nspec,len(longpix)))
    tophat = np.zeros(len(longpix))
    tophat[len(tophat)/2 - 2:len(tophat)/2 + 3] = 1.0
    fit = np.zeros((nspec,len(pix[0])))
    index = np.arange(len(pix[0]))*5 + 2
    for bake in range(0,nspec):
        lamb = longpix*dxm[bake] + dxb[bake]
#        psf = gaussian(longpix,sig[bake])
        psf = (1 + ((longpix-np.median(longpix))/sig[bake])**2)**(-1.0*4.7)         
        psf = psf/np.sum(psf)                                                                                  
        psf[0:120] = psf[275:404] = 0                                                 
        longfit[bake,:] = norm[bake]*np.convolve(np.abs(interpolate.splev(lamb, tck))**tau[bake],psf,'same')
        longfit[bake][np.where(np.abs(longfit[bake]) > 100)] = 100
        fit[bake,:] = np.convolve(longfit[bake]/5.0,tophat,'same')[index]
        
    return sum(sum(abs((flux - fit)/errs)))


"""Function to retrieve values from optimized x array"""
def get_vals(x,pix,flux,N,front,end,nspec,numpt):

    coef = x[0:(N+4)]
    coeff = np.concatenate((coef,np.zeros(4)),axis = 1)

    #define knots                                                                  
    knots_in = x[(N+4):(N+4) + N]
    knots = np.concatenate((front,knots_in,end))
    
    #pull out dxm's 
    dxm = x[(N+4) + N:(N+4)+N+nspec]

    #pull out dxb's
    dxb = x[(N+4) + N + nspec:(N+4)+ N + 2*nspec]

    #pull out scalings                                                
    norm = x[(N+4) + N + 2*nspec:(N+4)+N + 3*nspec]

    #pull out tau's               
    tau = x[(N+4)+N+3*nspec:(N+4) + N + 4*nspec]

    #pull out sigmas                                              
    sig = x[(N+4)+N+4*nspec:(N+4)+N+5*nspec]
    
    #define tck, fit                                                                                    
    tck = (knots,coeff,3)
    longpix = np.linspace(pix[0][0],pix[0][-1],5*(len(pix[0])))
    longfit = np.zeros((nspec,len(longpix)))
    tophat = np.zeros(len(longpix))
    tophat[len(tophat)/2 - 2:len(tophat)/2 + 3] = 1.0
    fit = np.zeros((nspec,len(pix[0])))
    index = np.arange(len(pix[0]))*5 + 2
    for bake in range(0,nspec):
        lamb = longpix*dxm[bake] + dxb[bake]
#        psf = gaussian(longpix,sig[bake])
        psf = (1 + ((longpix-np.median(longpix))/sig[bake])**2)**(-1.0*4.7)
        psf = psf/np.sum(psf)
        psf[0:120] = psf[275:404] = 0
        longfit[bake,:] = norm[bake]*np.convolve(np.abs(interpolate.splev(lamb, tck))**tau[bake],psf,'same')
        longfit[bake][np.where(np.abs(longfit[bake]) > 100)] = 100
        fit[bake,:] = np.convolve(longfit[bake]/5.0,tophat,'same')[index]

#    truespec = interpolate.splev(lamb, tck)
    return coeff,knots,dxm,dxb,norm,tau,sig,longfit,tck,fit

"""Given the values from the optimization, plot each fit for each
spectrum. Also plot the original spectrum"""
def plt_vals(pix,flux,fit,nspec,knots,dxm,dxb,numpt,norm,small_fit):
    for i in range(0,nspec):
        plt.figure()
        longpix = np.linspace(pix[0][0],pix[0][-1],5*(len(pix[0])))
        lamb = longpix*dxm[i] + dxb[i]
        lamb2 = pix[i]*dxm[i] + dxb[i]
        plt.plot(lamb2,flux[i]/norm[i],'go',label='data')
        plt.plot(lamb2,small_fit[i]/norm[i],label='Small Fit')
        plt.plot(lamb[10:5*numpt-10],fit[i][10:5*numpt-10]/norm[i],label='NLOPT fit')
        plt.legend(loc='best')
        plt.xlabel('Wavelength')
        plt.ylabel('Flux')
        plt.title('Spline Fit - Nlopt Fit #' + str(i))
        plt.xlim(min(knots),max(knots))
        plt.ylim(0.0,1.1)
        for j in range(0,len(knots)):
            plt.plot([knots[j],knots[j]],[.5,1.1],'y--')        
        plt.savefig('fit_i'+str(i)+'.png')
    return longpix,lamb,lamb2

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def gaussian(lamb,sig):
    fxn = (1/(sig*np.sqrt(2*np.pi)))*np.exp(-0.5*((lamb-np.median(lamb))/sig)**2)
    return fxn/sum(fxn)
