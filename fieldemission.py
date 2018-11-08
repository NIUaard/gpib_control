#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  1 08:21:58 2018

@author: ozz
set of functions for field emission calculations

the following data structure is assumed time|current|voltage
"""


#from pydefaults import *
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
#import uncertainties as un
from random import randint
#import itertools



data_type = np.dtype({'names': ['t','i', 'v'],
                      'formats': [np.double,np.double, np.double]})
    
data_type2 = np.dtype({'names': ['t','i', 'v','vs'],
                      'formats': [np.double,np.double, np.double,np.double]})
        

        

def func(E, I_c, E_c):
    return I_c * (E/E_c)**2 * np.exp(-1*(E_c/E))

def linear(x,m,c):
    return (m*x + c) 




    

def load_data(filename,data_type):
    data = np.loadtxt(open(filename), dtype=data_type)
    for i in range(len(data)):
        if data['i'][i] > 10.0:
           print "Sum values are overflowed"
           print 'overflowed current and voltage: ', data['i'][i],data['v'][i]
           data['i'][i] = 0.0
           
    return data


def get_average(data,Nsteps):
    current = []
    voltage = []
    strd_current = []
    strd_voltage = []
    for i in range(0,len(data),Nsteps):
        error = np.std(data['i'][i:i + Nsteps])
        strd_current.append(error)
        average_current = np.average(data['i'][i:i + Nsteps])
        current.append(average_current)
        error = np.std(data['v'][i:i + Nsteps])
        strd_voltage.append(error)
        average_voltage = np.average(data['v'][i:i + Nsteps])
        voltage.append(average_voltage)
    return (np.asarray(voltage),np.asarray(current),np.asarray(strd_voltage),np.asarray(strd_current))


def Plot_with_error(xaxis,yaxis,xerror,yerror,savefig=False):
    yaxis = yaxis * 1e9
    yerror = yerror * 1e9
    fig, ax = plt.subplots()
    ax.plot(xaxis,yaxis,'+',label='Exp. data')
    ax.errorbar(xaxis, yaxis,xerr=1.0,yerr=yerror, fmt='+',ecolor='r', capthick=2,label='$\sigma$')
    ax.set_ylabel(r'Current ($nA$)')
    ax.set_xlabel(r'Applied Voltage ($V$)')
    legend = ax.legend(loc=0, shadow=False, fontsize='large')
    plt.title('Measured I-V Curve')
    #legend.get_frame().set_facecolor('#00FFCC')
    fig.tight_layout()
    if savefig == True:
        name = input('file name?')
        plt.savefig(str(name),format='pdf')
    else:
        pass
    
    plt.show()

def errorfill(x, y, xerr,yerr  ,color=None, alpha_fill=0.3, ax=None):
    ax = ax if ax is not None else plt.gca()
    if color is None:
        color = ax._get_lines.color_cycle.next()
    if np.isscalar(yerr) or len(yerr) == len(y):
        ymin = y - yerr
        ymax = y + yerr
    elif len(yerr) == 2:
        ymin, ymax = yerr
    ax.plot(x, y, color=color)
    ax.fill_between(x, ymax, ymin, color=color, alpha=alpha_fill)


def longdata_plot(xaxis,yaxis):
    yaxis = yaxis * 1e9
    fig, ax = plt.subplots()
    ax.plot(xaxis,yaxis)
    ax.set_ylabel(r'Current ($nA$)', color='r')
    ax.set_xlabel(r'Time ($s$)', color='r')
    fig.tight_layout()
    plt.show()

    
def Plot_data(xaxis,yaxis,savefig=False):
    yaxis = yaxis * 1e9
    fig, ax = plt.subplots()
    ax.plot(xaxis, yaxis,'r.')
    ax.set_ylabel(r'Current ($nA$)', color='r')
    ax.set_xlabel(r'Applied Voltage ($V$)', color='r')
    fig.tight_layout()
    if savefig == True:
        name = input('file name?')
        plt.savefig(str(name),format='pdf')
    else:
        pass
    
    plt.show()
font = {'family': 'serif',
        'color':  'darkred',
        'weight': 'normal',
        'size': 16,
        }

def FNPlot(xaxis,yaxis,initial_v,cut_f, cut_i,spaceing=100e-6,stepsize=200,savefig=False):
    #assumong initial value of V = 2000
    #final_v = 14000
    #initial_v = 2000
    initial = (cut_i-initial_v)/stepsize #slicing index to begin with 
    final = (cut_f -initial_v)/stepsize
    yaxis = np.log((yaxis[initial:final])/(xaxis[initial:final]**2))
    xaxis = 1./((xaxis[initial:final])/100e-6) #electric field
    slope, intercept, r_value, p_value, std_err = stats.linregress(xaxis,yaxis)
    line = (slope * xaxis) + intercept
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    ax.plot(xaxis, yaxis,'rx',label='Exp. data')
    ax.set_ylabel(r'ln $(I / V^2)[A/V^2]$', color='r')
    ax.set_xlabel(r'$(1/E)[(V/m)^{-1}]$', color='r')
    ax.plot(xaxis,line,label='Fit')
    print 'slope =', slope, '+/-', std_err
    phi = 4.
    xmax,x,xmin = (-2.84e9 * pow(phi,1.5) )/ (slope+std_err),(-2.84e9 * pow(phi,1.5) )/ slope,(-2.84e9 * pow(phi,1.5) )/ (slope-std_err)
    print xmax,x,xmin
    print abs(xmax-x),abs(x-xmin)
    print "assuming phi = 4.0, beta = ", x ,"+/-" 
    plt.title('Fowler-Nordheim plot')
    legend = ax.legend(loc=0, shadow=False, fontsize='large')
    #ax.text(0.75E-8,-44,r'$\beta=$'+str(round(x))+' $\pm$ 1' )
    props = dict(boxstyle='round', facecolor='red', alpha=0.3)
    ax.text(0.1,0.1, r'$\beta=$'+str(round(x))+' $\pm$ 1' , transform=ax.transAxes, fontsize=20, va='baseline',
        bbox=props)
    fig.tight_layout()
    if savefig == True:
        name = input('file name?')
        plt.savefig(str(name),format='pdf')
    else:
        pass
    plt.show()


def FNPlot_newanalysis(xaxis,yaxis,xerror,yerror,spacing,cut_f,cut_i,final_v=14000,initial_v=2000,stepsize=200,savefig=False):
    initial = (cut_i-initial_v)/stepsize #slicing index to begin with 
    final = (cut_f -initial_v)/stepsize
    yaxis = yaxis[initial:final]*1e9
    yerror = yerror[initial:final]*1e9
    xaxis = (xaxis[initial:final]*1e-6)/(100.e-6)
    xerror = (xerror[initial:final]*1e-6)/(100.e-6)
    fig, ax = plt.subplots()
    popt, pcov = curve_fit(func, xaxis,yaxis)
    print pcov
    perr = np.sqrt(np.diag(pcov))
    print perr
    print 'std of I_c,E_c are presectively:',perr
    I_c, E_c = popt[0], popt[1]
    print I_c,E_c
    ax.set_ylabel(r'Current ($nA$)', color='r')
    ax.set_xlabel(r'Applied Electric Field ($MV/m$)', color='r')
    ax.errorbar(xaxis, yaxis,xerr=1.0,yerr=yerror, fmt='+',ecolor='r', capthick=2,label='$\sigma$')
    ax.plot(xaxis, func(xaxis, I_c,E_c),label='Fit')
    legend = ax.legend(loc=0, shadow=False, fontsize='large')
    props = dict(boxstyle='round', facecolor='red', alpha=0.3)
    #I_c * (E/E_c)**2 * np.exp(-1*(E_c/E))
    ax.text(0.1,0.3, r'$I_{FN} = I_c \frac{E^2}{E_c^2} \ e^{-\frac{E_c}{E}}$', transform=ax.transAxes, fontsize=20, va='baseline',
        bbox=props)
    fig.tight_layout()
    if savefig==True:
       x=input('enter 1st figure name:')
       plt.savefig(str(x),format='pdf')
    else:
        pass
    plt.show()
    phi = np.linspace(0,5,100)
    print I_c,E_c*1e6
    beta = 6.53e9 * ((phi**1.5)/(E_c*1e6))
    beta_std = (6.53e9 * ((phi**1.5)/((E_c+perr[1])*1e6)))
    print beta
    fig, ax = plt.subplots()
    betamin = beta - beta_std
    betamax = beta + beta_std
    ax.plot(phi,beta)
    ax.text(0.6,0.3, r'$\beta = 6.53 \times 10^9 \frac{\phi^{1.5}}{E_c}$', transform=ax.transAxes, fontsize=18, va='baseline',
        bbox=props)
  #  ax.text(0.6,0.1, r'$E_c = 3.426 GV/m$', transform=ax.transAxes, fontsize=18, va='baseline',
   #     bbox=props)
    
    #ax.fill_between(phi, betamin, betamax, color='r', alpha=0.3)
    #ax.errorbar(phi,beta,yerr=beta_std,label='Fit')
    #p = ax.axvspan(3.5, 4.5, facecolor='0.5', alpha=0.5,label=r'$\beta$')
    m = ax.axhspan(14.0, 16.0, facecolor='0.5', alpha=0.5,label=r'$\sigma_{\beta}$')
    legend = ax.legend(loc=0, shadow=False, fontsize='large')
    ax.set_ylabel(r'Field Enhancement $\beta$', color='b')
    ax.set_xlabel(r'Work Function $\phi(eV)$', color='b')
    if savefig==True:
        x=input('enter 2st figure name:')
        plt.savefig(str(x),format='pdf')
    else:
        pass
    plt.show()
    A_e = (I_c*1e-9)/((65.67e-6) * (10**(4.52/(phi**0.5))) * (phi**2))
    A_estd = (perr[0]*1e-9)/((65.67e-6) * (10**(4.52/(phi**0.5))) * (phi**2))
    fig,ax = plt.subplots()
    ax.plot(phi,A_e*1e-18)
    ax.set_xlabel(r'Work Function $\phi(eV)$',color='b')
    ax.set_ylabel(r'Emitter area $(m^2)$',color='b')
    A_emax = (A_estd)*1e-18
    A_emin = (A_estd)*1e-18
    ax.text(0.43,0.2, r'$A = \frac{I_c}{(65.67\times 10^{-6})(10^{(\frac{4.52}{\sqrt{\phi}})})(\phi^2)}$', transform=ax.transAxes, fontsize=18, va='baseline',
        bbox=props)
    fig.tight_layout()
    #plt.fill_between(phi, A_emax, A_emin, color='r', alpha=0.3)
    if savefig==True:
        x=input('enter 3st figure name:')
        plt.savefig(str(x),format='pdf')
    else:
        pass
    plt.show()
    return I_c,E_c

from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes

def multi_plot(xdata,ydata,xerr,yerr):
    colors = itertools.cycle(('b', 'g', 'r', 'c', 'm', 'y', 'k'))
    marker = itertools.cycle(( '+', '*', ',', 'o', '.', '1', 'p')) 
    print len(xdata),xdata[0]
    print len(ydata),ydata[0]
    if len(xdata) != len(ydata):
        print 'error'
    else:
        pass
    fig, ax = plt.subplots()
    for i in range(len(xdata)):
        xaxis = xdata[i]
        xerror = xerr[i]
        yaxis = ydata[i] * 1e9
        yerror = yerr[i] * 1e9
        ax.plot(xaxis,yaxis,marker=marker.next(),color=colors.next(),label='Exp. data '+str(i))
        ax.errorbar(xaxis, yaxis,xerr=xerror,yerr=yerror, fmt=marker.next() ,ecolor='r', capthick=2,label='$\sigma$ '+str(i))
    axins = zoomed_inset_axes(ax, 2, loc=6) # zoom-factor: 2.5, location: upper-left
    axins.plot(xdata[1], ydata[1])
    x1, x2, y1, y2 = 10000, 13000, 0, max(ydata[1]) # specify the limits
    axins.set_xlim(x1, x2) # apply the x-limits
    #axins.set_ylim(y1, y2) # apply the y-limits
    axins.xaxis.set_visible('False')
    axins.yaxis.set_visible('False')
    #from mpl_toolkits.axes_grid1.inset_locator import mark_inset
    #mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="0.5")
    ax.set_ylabel(r'Current ($nA$)')
    ax.set_xlabel(r'Applied Voltage ($V$)')
    #legend = ax.legend(loc=0, shadow=False, fontsize='large')
    #plt.title('Measured I-V Curve')
    fig.tight_layout()
    plt.draw()
    plt.show()
    
    
"""

#if __name__ == "__main__":
data = '/home/ozz/Documents/Lab_filed_emission/July/July_16/iv_monitoring_D20180716T142543'
data = load_data(data)
average = get_average(data,100)
Plot_with_error(*average)
FNPlot(average['v'],average['i'],initial_v,cut_f, cut_i,spaceing=100e-6,stepsize=200,savefig=False)
fig, ax = plt.subplots()
"""
