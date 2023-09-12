import math
import numpy as np
import CoolProp.CoolProp as CP

class Pump:
    
    """
    Class to handle pump calculations. It is one of elements that power systems are build like heat exchangers, pipes and pumps.
    
    Obligatory inputs:
    T_in - temperature of liquid at pump inlet, C
    p_in - pressure of liquid at pump inlet, kPa(a)
    p_out - pressure of liquid at pump outlet, kPa(a)
    mf - mass flow of working fluid, kg/s
    medium - working fluid ex. Water, Toluene, R1233zd(E), etc.
    """
    
    def __init__(self, T_in, p_in, p_out, mf,medium):
        self.T_in = T_in
        self.p_in = p_in
        self.p_out = p_out
        self.mf = mf
        self.medium = medium
        
        """Calculation of basic thermodynamic properties for use in other calculations in class.
        
        Sources:
        * https://en.wikipedia.org/wiki/List_of_thermodynamic_properties
        * https://en.wikipedia.org/wiki/State_function
        
        Outputs:
        h_in - specific enthalpy at pump inlet, kJ/kg
        s_in - specific entropy at pump inlet, kJ/(kg*K) or kJ/(kg*C) where K is temperature in K-Kelvins or C - Celciuss degres
        
        h_out_s - specific enthalpy at pump outlet after isentropic expansion (eta_iT=1.0), kJ/kg
        s_out_s - specific entropy at pump outlet after isentropic expansion (eta_iT=1.0), kJ/(kg*K) or kJ/(kg*C) where K is temperature in K-Kelvins or C - Celciuss degres
        T_out_s - temperature at pump outlet after isentropic expansion (eta_iT=1.0), C
        """
        
        'Parameters at pump inlet'
        self.h_in = CP.PropsSI('Hmass', 'T', self.T_in+273.15, 'P', self.p_in*1000, self.medium)/1000
        self.s_in = CP.PropsSI('Smass', 'T', self.T_in+273.15, 'P', self.p_in*1000, self.medium)/1000
        
        'Parameters at pump outlet after isentropic expansion (eta_iT=1.0), kJ/(kg*K) or kJ/(kg*C) where K is temperature in K-Kelvins or C - Celciuss degres'
        self.s_out_s = self.s_in 
        self.h_out_s = CP.PropsSI('Hmass', 'Smass', self.s_out_s*1000, 'P', self.p_out*1000, self.medium)/1000
        self.T_out_s = CP.PropsSI('T', 'Smass', self.s_out_s*1000, 'P', self.p_out*1000, self.medium)-273.15
        
        self.rho_in = CP.PropsSI('Dmass', 'Hmass', self.h_in*1000, 'P', self.p_in*1000, self.medium)
        self.V_in = mf/self.rho_in
        
    def power(self, eta_iP):
            
        """
        Calculates internal power output of pump according to given internal efficiency.
        In case of using iterative calculations, the change of inlet and outlet parameters will not affect the interal pump efficiency.
        
        Inputs:
        T_in - liquid temperature at pump inelt, C
        p_in - liquid pressure at pump inlet, kPa(a)
        p_out - presure at pump outlet, kPa(a)
        mf - medium (liquid) flow through pump, kg/s
        medium - type of medium flowing through ex. 'Toluene', 'Water'
        eta_iT - fixed internal efficeincy of pump 0.0-1.0, -
        
        Main outputs:
        N_iT - internal power generated by pump, kW
        T_out - temperature of medium at pump ouitlet, C
        
        Other outputs:
        h_in - enthalpy of liquid at pump inlet, kJ/kg
        s_in - entropy of liquid at pump inlet, kJ/(kg*C) or kJ/(kg*K)
        h_out - enthalpy of liquid at pump outlet, kJ/kg
        h_out_s - enthalpy of liquid at pump outlet after ideal (eta = 1.0) expansion in pump, kJ/kg
        s_out - entropy of vapur at pump outlet
        s_out_s - entropy of liquid at pump outlet after ideal (eta = 1.0) expansion in pump, kJ/(kg*C) or kJ/(kg*K)
        """
        self.eta_iP = eta_iP
        self.h_out = self.h_in+(self.h_out_s-self.h_in)/self.eta_iP
        self.T_out = CP.PropsSI('T', 'Hmass', self.h_out*1000, 'P', self.p_out*1000, self.medium)-273.15
        self.s_out = CP.PropsSI('Smass', 'T', self.T_out+273.15, 'P', self.p_out*1000, self.medium)/1000
        self.N_iP = self.mf*(self.h_out-self.h_in)

    def off_design(self, T_in_off, p_in_off, p_out_off, mf_off):
        
        """
        Ahlgren F, Mondejar ME, Genrup M, Thern M. Waste Heat Recovery in a Cruise Vessel
        in the Baltic Sea by Using an Organic Rankine Cycle: A Case Study. Journal of
        Engineering for Gas Turbines and Power 2016;138:11702, doi:10.1115/1.4031145
        """
        self.T_in_off = T_in_off
        self.p_in_off = p_in_off
        self.p_out_off = p_out_off
        self.mf_off = mf_off
        
        self.h_in_off = CP.PropsSI('Hmass', 'T', self.T_in_off+273.15, 'P', self.p_in_off*1000, self.medium)/1000
        self.s_in_off = CP.PropsSI('Smass', 'T', self.T_in_off+273.15, 'P', self.p_in_off*1000, self.medium)/1000
        
        self.s_out_s_off = self.s_in_off 
        self.h_out_s_off = CP.PropsSI('Hmass', 'Smass', self.s_out_s_off*1000, 'P', self.p_out_off*1000, self.medium)/1000
        self.T_out_s_off = CP.PropsSI('T', 'Smass', self.s_out_s_off*1000, 'P', self.p_out_off*1000, self.medium)-273.15
        
        self.rho_in_off = CP.PropsSI('Dmass', 'Hmass', self.h_in_off*1000, 'P', p_in_off*1000, self.medium)
        self.V_in_off = mf_off/self.rho_in_off
        
        self.eta_iP_off = (-0.168*(self.V_in/self.V_in_off)**3-0.0336*(self.V_in/self.V_in_off)**2+0.6317*(self.V_in/self.V_in_off)+0.5699)*self.eta_iP
        
        self.h_out_off = self.h_in_off+(self.h_out_s_off-self.h_in_off)/self.eta_iP_off
        self.T_out_off = CP.PropsSI('T', 'Hmass', self.h_out_off*1000, 'P', self.p_out_off*1000, self.medium)-273.15
        self.s_out_off = CP.PropsSI('Smass', 'T', self.T_out_off+273.15, 'P', self.p_out_off*1000, self.medium)/1000
        self.N_iP_off = self.mf_off*(self.h_out_off-self.h_in_off)