#! /usr/bin/python

# 28/08/20 - Stephen Kay, University of Regina

# Python version of the proton analysis script. Now utilises uproot to select event of each type and writes them to a root file
# Intention is to apply PID/selection cutting here and plot in a separate script
# Python should allow for easier reading of databases storing timing offsets e.t.c.
# This version is specificially for running the proton analysis on data taken during summer 2019 (low energy PionLT data)

# Import relevant packages
import uproot as up
import numpy as np
import root_numpy as rnp
import pandas as pd
import root_pandas as rpd
import ROOT
import scipy
import scipy.integrate as integrate
import matplotlib.pyplot as plt
import sys, math, os, subprocess

sys.path.insert(0, 'python/')
if len(sys.argv)-1!=2:
    print("!!!!! ERROR !!!!!\n Expected 2 arguments\n Usage is with - RunNumber MaxEvents \n!!!!! ERROR !!!!!")
    sys.exit(1)
# Input params - run number and max number of events
runNum = sys.argv[1]
MaxEvent = sys.argv[2]

USER = subprocess.getstatusoutput("whoami") # Grab user info for file finding
HOST = subprocess.getstatusoutput("hostname")
if ("farm" in HOST[1]):
    REPLAYPATH = "/group/c-kaonlt/USERS/%s/hallc_replay_lt" % USER[1]
elif ("qcd" in HOST[1]):
    REPLAYPATH = "/group/c-kaonlt/USERS/%s/hallc_replay_lt" % USER[1]
elif ("lark.phys.uregina" in HOST[1]):
    REPLAYPATH = "/home/%s/work/JLab/hallc_replay_lt" % USER[1]

# Add more path setting as needed in a similar manner
OUTPATH = "%s/UTIL_PROTON/scripts/protonyield/OUTPUT" % REPLAYPATH
CUTPATH = "%s/UTIL_PROTON/DB/CUTS" % REPLAYPATH
sys.path.insert(0, '%s/UTIL_PROTON/bin/python/' % REPLAYPATH)
import kaonlt as klt

print("Running as %s on %s, hallc_replay_lt path assumed as %s" % (USER[1], HOST[1], REPLAYPATH))
rootName = "%s/UTIL_PROTON/ROOTfiles/Proton_coin_replay_production_%s_%s.root" % (REPLAYPATH, runNum, MaxEvent)

###############################################################################################################
############################### RF Timing is the only thing left in here ######################################
###############################################################################################################
TimingCutFile = "%s/UTIL_PROTON/DB/PARAM/Timing_Parameters.csv" % REPLAYPATH
TimingCutf = open(TimingCutFile)
linenum = 0 # Count line number we're on
TempPar = -1 # To check later
for line in TimingCutf: # Read all lines in the cut file
    linenum += 1 # Add one to line number at start of loop
    if(linenum > 1): # Skip first line
        line = line.partition('#')[0] # Treat anything after a # as a comment and ignore it
        line = line.rstrip()
        array = line.split(",") # Convert line into an array, anything after a comma is a new entry
        if(int(runNum) in range (int(array[0]), int(array[1])+1)): # Check if run number for file is within any of the ranges specified in the cut file
            TempPar += 2 # If run number is in range, set to non -1 value
            BunchSpacing = float(array[2]) # Bunch spacing in ns
            RF_Offset = float(array[9]) # Offset for RF timing cut
TimingCutf.close() # After scanning all lines in file, close file
if(TempPar == -1): # If value is still -1, run number provided din't match any ranges specified so exit
    print("!!!!! ERROR !!!!!\n Run number specified does not fall within a set of runs for which cuts are defined in %s\n!!!!! ERROR !!!!!" % TimingCutFile)
    sys.exit(3)
elif(TempPar > 1):
    print("!!! WARNING!!! Run number was found within the range of two (or more) line entries of %s !!! WARNING !!!" % TimingCutFile)
    print("The last matching entry will be treated as the input, you should ensure this is what you want")
###############################################################################################################

# Read stuff from the main event tree
e_tree = up.open(rootName)["T"]
# Timing info
CTime_ePiCoinTime_ROC1 = e_tree.array("CTime.ePiCoinTime_ROC1")
CTime_eKCoinTime_ROC1 = e_tree.array("CTime.eKCoinTime_ROC1")
CTime_epCoinTime_ROC1 = e_tree.array("CTime.epCoinTime_ROC1")
P_RF_tdcTime = e_tree.array("T.coin.pRF_tdcTime")
P_hod_fpHitsTime = e_tree.array("P.hod.fpHitsTime")
# HMS info
H_gtr_beta = e_tree.array("H.gtr.beta")
H_gtr_xp = e_tree.array("H.gtr.th") # xpfp -> Theta
H_gtr_yp = e_tree.array("H.gtr.ph") # ypfp -> Phi
H_gtr_dp = e_tree.array("H.gtr.dp")
H_cal_etotnorm = e_tree.array("H.cal.etotnorm")
H_cer_npeSum = e_tree.array("H.cer.npeSum")
# SHMS info
P_gtr_beta = e_tree.array("P.gtr.beta")
P_gtr_xp = e_tree.array("P.gtr.th") # xpfp -> Theta
P_gtr_yp = e_tree.array("P.gtr.ph") # ypfp -> Phi
P_gtr_p = e_tree.array("P.gtr.p")
P_gtr_dp = e_tree.array("P.gtr.dp")
P_cal_etotnorm = e_tree.array("P.cal.etotnorm")
P_aero_npeSum = e_tree.array("P.aero.npeSum")
P_hgcer_npeSum = e_tree.array("P.hgcer.npeSum")
P_hgcer_xAtCer = e_tree.array("P.hgcer.xAtCer")
P_hgcer_yAtCer = e_tree.array("P.hgcer.yAtCer")
# Kinematic quantitites
Q2 = e_tree.array("H.kin.primary.Q2")
W = e_tree.array("H.kin.primary.W")
epsilon = e_tree.array("H.kin.primary.epsilon")
ph_q = e_tree.array("P.kin.secondary.ph_xq")
emiss = e_tree.array("P.kin.secondary.emiss")
pmiss = e_tree.array("P.kin.secondary.pmiss")
MandelT = e_tree.array("P.kin.secondary.MandelT")
MandelU = e_tree.array("P.kin.secondary.MandelU")
# Misc quantities
fEvtType = e_tree.array("fEvtHdr.fEvtType")
RFFreq = e_tree.array("MOFC1FREQ")
RFFreqDiff = e_tree.array("MOFC1DELTA")
pEDTM = e_tree.array("T.coin.pEDTM_tdcTime")
# Relevant branches now stored as NP arrays

# Define particle masses for missing mass calculation
Mp = 0.93828
MPi = 0.13957018 
MK = 0.493677
# Calculate missing mass under different particle assumptions
# NOTE, this should be modified for NON different particle assumptions in hcana, this assumes a "kaon" is specified in the kinematics file
MMpi = np.array([math.sqrt(abs((em*em)-(pm*pm))) for (em, pm) in zip(emiss, pmiss)])
MMK = np.array([math.sqrt(abs(((em+(math.sqrt((MPi*MPi)+(gtrp*gtrp)))-(math.sqrt((MK*MK)+(gtrp*gtrp))))**2)-(pm*pm))) for (em, pm, gtrp) in zip(emiss, pmiss, P_gtr_p)])
MMp = np.array([math.sqrt(abs(((em+(math.sqrt((MPi*MPi)+(gtrp*gtrp)))-(math.sqrt((Mp*Mp)+(gtrp*gtrp))))**2)-(pm*pm))) for (em, pm, gtrp) in zip(emiss, pmiss, P_gtr_p)])
# Create array of mod(BunchSpacing)(RFTime - StartTime + Offset) for all events. Offset is chosen to centre the pion peak in the distribution (need to test 2ns runs)
RF_CutDist = np.array([ ((RFTime-StartTime + RF_Offset)%(BunchSpacing)) for (RFTime, StartTime) in zip(P_RF_tdcTime, P_hod_fpHitsTime)]) # In python x % y is taking the modulo y of x

r = klt.pyRoot()
fout = '%s/UTIL_PROTON/DB/CUTS/run_type/coin_prod.cuts' % REPLAYPATH
# read in cuts file and make dictionary
c = klt.pyPlot(None)
readDict = c.read_dict(fout,runNum)
# This method calls several methods in kaonlt package. It is required to create properly formated
# dictionaries. The evaluation must be in the analysis script because the analysis variables (i.e. the
# leaves of interest) are not defined in the kaonlt package. This makes the system more flexible
# overall, but a bit more cumbersome in the analysis script. Perhaps one day a better solution will be
# implimented.
def make_cutDict(cut,inputDict=None):

    global c

    c = klt.pyPlot(readDict)
    x = c.w_dict(cut)
    print("%s" % cut)
    print("x ", x)
    
    if inputDict == None:
        inputDict = {}
        
    for key,val in readDict.items():
        if key == cut:
            inputDict.update({key : {}})

    for i,val in enumerate(x):
        tmp = x[i]
        if tmp == "":
            continue
        else:
            inputDict[cut].update(eval(tmp))
        
    return inputDict

cutDict = make_cutDict("coin_epi_cut_all")
cutDict = make_cutDict("coin_ek_cut_all", cutDict)
cutDict = make_cutDict("coin_ep_cut_all", cutDict)
cutDict = make_cutDict("coin_ep_cut_prompt", cutDict)
cutDict = make_cutDict("coin_ep_cut_rand", cutDict)
c = klt.pyPlot(cutDict)

def coin_pions(): 
    # Define the array of arrays containing the relevant HMS and SHMS info
    NoCut_COIN_Pions = [H_gtr_beta, H_gtr_xp, H_gtr_yp, H_gtr_dp, H_cal_etotnorm, H_cer_npeSum, CTime_ePiCoinTime_ROC1, P_RF_tdcTime, P_hod_fpHitsTime, P_gtr_beta, P_gtr_xp, P_gtr_yp, P_gtr_p, P_gtr_dp, P_cal_etotnorm, P_aero_npeSum, P_hgcer_npeSum, P_hgcer_xAtCer, P_hgcer_yAtCer, MMpi, MMK, MMp, RF_CutDist, Q2, W, epsilon, MandelT, MandelU, ph_q]

    # Create array of arrays of pions after cuts, all events, prompt and random
    Cut_COIN_Pions_tmp = NoCut_COIN_Pions
    Cut_COIN_Pions_all_tmp = []
    Cut_COIN_Pions_all_noRF_tmp = []

    for arr in Cut_COIN_Pions_tmp:
        Cut_COIN_Pions_all_tmp.append(c.add_cut(arr, "coin_epi_cut_all"))
        Cut_COIN_Pions_all_noRF_tmp.append(c.add_cut(arr, "coin_epi_cut_all"))

    Cut_COIN_Pions_all = [(HBeta, Hxp, Hyp, Hdel, HCal, HCer, CTPi, RF, HodStart, PiBeta, Pixp, Piyp, PiP, PiDel, PiCal, PiAero, PiHGC, PiHGCX, PiHGCY, mm1, mm2, mm3, RFCutDist, Kin_Q2, Kin_W, Kin_eps, Kin_t, Kin_u, phq) for (HBeta, Hxp, Hyp, Hdel, HCal, HCer, CTPi, RF, HodStart, PiBeta, Pixp, Piyp, PiP, PiDel, PiCal, PiAero, PiHGC, PiHGCX, PiHGCY, mm1, mm2, mm3, RFCutDist, Kin_Q2, Kin_W, Kin_eps, Kin_t, Kin_u, phq) in zip(*Cut_COIN_Pions_all_tmp)
                    if RFCutDist > 1.4 and RFCutDist < 3]

    Cut_COIN_Pions_all_noRF = [(HBeta, Hxp, Hyp, Hdel, HCal, HCer, CTPi, RF, HodStart, PiBeta, Pixp, Piyp, PiP, PiDel, PiCal, PiAero, PiHGC, PiHGCX, PiHGCY, mm1, mm2, mm3, RFCutDist, Kin_Q2, Kin_W, Kin_eps, Kin_t, Kin_u, phq) for (HBeta, Hxp, Hyp, Hdel, HCal, HCer, CTPi, RF, HodStart, PiBeta, Pixp, Piyp, PiP, PiDel, PiCal, PiAero, PiHGC, PiHGCX, PiHGCY, mm1, mm2, mm3, RFCutDist, Kin_Q2, Kin_W, Kin_eps, Kin_t, Kin_u, phq) in zip(*Cut_COIN_Pions_all_noRF_tmp)]


    COIN_Pions = {
        "Cut_Pion_Events_All" : Cut_COIN_Pions_all,
        "Cut_Pion_Events_All_NoRF" : Cut_COIN_Pions_all_noRF,
        }

    return COIN_Pions

def coin_kaons(): 
    # Define the array of arrays containing the relevant HMS and SHMS info
    NoCut_COIN_Kaons = [H_gtr_beta, H_gtr_xp, H_gtr_yp, H_gtr_dp, H_cal_etotnorm, H_cer_npeSum, CTime_eKCoinTime_ROC1, P_RF_tdcTime, P_hod_fpHitsTime, P_gtr_beta, P_gtr_xp, P_gtr_yp, P_gtr_p, P_gtr_dp, P_cal_etotnorm, P_aero_npeSum, P_hgcer_npeSum, P_hgcer_xAtCer, P_hgcer_yAtCer, MMpi, MMK, MMp, RF_CutDist, Q2, W, epsilon, MandelT, MandelU, ph_q]
    # Create array of arrays of pions after cuts, all events, prompt and random
    Cut_COIN_Kaons_tmp = NoCut_COIN_Kaons
    Cut_COIN_Kaons_all_tmp = []
    Cut_COIN_Kaons_all_noRF_tmp = []

    for arr in Cut_COIN_Kaons_tmp:
        Cut_COIN_Kaons_all_tmp.append(c.add_cut(arr, "coin_ek_cut_all"))
        Cut_COIN_Kaons_all_noRF_tmp.append(c.add_cut(arr, "coin_ek_cut_all"))

    Cut_COIN_Kaons_all = [(HBeta, Hxp, Hyp, Hdel, HCal, HCer, CTK, RF, HodStart, KBeta, Kxp, Kyp, KP, KDel, KCal, KAero, KHGC, KHGCX, KHGCY, mm1, mm2, mm3, RFCutDist, Kin_Q2, Kin_W, Kin_eps, Kin_t, Kin_u, phq) for (HBeta, Hxp, Hyp, Hdel, HCal, HCer, CTK, RF, HodStart, KBeta, Kxp, Kyp, KP, KDel, KCal, KAero, KHGC, KHGCX, KHGCY, mm1, mm2, mm3, RFCutDist, Kin_Q2, Kin_W, Kin_eps, Kin_t, Kin_u, phq) in zip(*Cut_COIN_Kaons_all_tmp)
                    if RFCutDist > 1.3 and RFCutDist < 3]

    Cut_COIN_Kaons_all_noRF = [(HBeta, Hxp, Hyp, Hdel, HCal, HCer, CTK, RF, HodStart, KBeta, Kxp, Kyp, KP, KDel, KCal, KAero, KHGC, KHGCX, KHGCY, mm1, mm2, mm3, RFCutDist, Kin_Q2, Kin_W, Kin_eps, Kin_t, Kin_u, phq) for (HBeta, Hxp, Hyp, Hdel, HCal, HCer, CTK, RF, HodStart, KBeta, Kxp, Kyp, KP, KDel, KCal, KAero, KHGC, KHGCX, KHGCY, mm1, mm2, mm3, RFCutDist, Kin_Q2, Kin_W, Kin_eps, Kin_t, Kin_u, phq) in zip(*Cut_COIN_Kaons_all_noRF_tmp)]

    COIN_Kaons = {
        "Cut_Kaon_Events_All" : Cut_COIN_Kaons_all,
        "Cut_Kaon_Events_All_NoRF" : Cut_COIN_Kaons_all_noRF,
        }

    return COIN_Kaons


def coin_protons(): 
    # Define the array of arrays containing the relevant HMS and SHMS info
    NoCut_COIN_Protons = [H_gtr_beta, H_gtr_xp, H_gtr_yp, H_gtr_dp, H_cal_etotnorm, H_cer_npeSum, CTime_epCoinTime_ROC1, P_RF_tdcTime, P_hod_fpHitsTime, P_gtr_beta, P_gtr_xp, P_gtr_yp, P_gtr_p, P_gtr_dp, P_cal_etotnorm, P_aero_npeSum, P_hgcer_npeSum, P_hgcer_xAtCer, P_hgcer_yAtCer, MMpi, MMK, MMp, RF_CutDist, Q2, W, epsilon, MandelT, MandelU, ph_q]
    Uncut_COIN_Protons = [(HBeta, Hxp, Hyp, Hdel, HCal, HCer, CTp, RF, HodStart, pBeta, pxp, pyp, pP, pDel, pCal, pAero, pHGC, pHGCX, pHGCY, mm1, mm2, mm3, RFCutDist, Kin_Q2, Kin_W, Kin_eps, Kin_t, Kin_u, phq) for (HBeta, Hxp, Hyp, Hdel, HCal, HCer, CTp, RF, HodStart, pBeta, pxp, pyp, pP, pDel, pCal, pAero, pHGC, pHGCX, pHGCY, mm1, mm2, mm3, RFCutDist, Kin_Q2, Kin_W, Kin_eps, Kin_t, Kin_u, phq) in zip(*NoCut_COIN_Protons)] 

    # Create array of arrays of pions after cuts, all events, prompt and random
    Cut_COIN_Protons_tmp = NoCut_COIN_Protons
    Cut_COIN_Protons_all_noRF_tmp = []
    Cut_COIN_Protons_all_tmp = []
    Cut_COIN_Protons_prompt_tmp =[]
    Cut_COIN_Protons_rand_tmp =[]

    for arr in Cut_COIN_Protons_tmp:
        Cut_COIN_Protons_all_tmp.append(c.add_cut(arr, "coin_ep_cut_all"))
        Cut_COIN_Protons_all_noRF_tmp.append(c.add_cut(arr, "coin_ep_cut_all"))
        Cut_COIN_Protons_prompt_tmp.append(c.add_cut(arr, "coin_ep_cut_prompt"))
        Cut_COIN_Protons_rand_tmp.append(c.add_cut(arr, "coin_ep_cut_rand"))

    Cut_COIN_Protons_all = [(HBeta, Hxp, Hyp, Hdel, HCal, HCer, CTp, RF, HodStart, pBeta, pxp, pyp, pP, pDel, pCal, pAero, pHGC, pHGCX, pHGCY, mm1, mm2, mm3, RFCutDist, Kin_Q2, Kin_W, Kin_eps, Kin_t, Kin_u, phq) for (HBeta, Hxp, Hyp, Hdel, HCal, HCer, CTp, RF, HodStart, pBeta, pxp, pyp, pP, pDel, pCal, pAero, pHGC, pHGCX, pHGCY, mm1, mm2, mm3, RFCutDist, Kin_Q2, Kin_W, Kin_eps, Kin_t, Kin_u, phq) in zip(*Cut_COIN_Protons_all_tmp)
                if RFCutDist < 1.65]

    Cut_COIN_Protons_all_noRF = [(HBeta, Hxp, Hyp, Hdel, HCal, HCer, CTp, RF, HodStart, pBeta, pxp, pyp, pP, pDel, pCal, pAero, pHGC, pHGCX, pHGCY, mm1, mm2, mm3, RFCutDist, Kin_Q2, Kin_W, Kin_eps, Kin_t, Kin_u, phq) for (HBeta, Hxp, Hyp, Hdel, HCal, HCer, CTp, RF, HodStart, pBeta, pxp, pyp, pP, pDel, pCal, pAero, pHGC, pHGCX, pHGCY, mm1, mm2, mm3, RFCutDist, Kin_Q2, Kin_W, Kin_eps, Kin_t, Kin_u, phq) in zip(*Cut_COIN_Protons_all_noRF_tmp)]

    Cut_COIN_Protons_prompt = [(HBeta, Hxp, Hyp, Hdel, HCal, HCer, CTp, RF, HodStart, pBeta, pxp, pyp, pP, pDel, pCal, pAero, pHGC, pHGCX, pHGCY, mm1, mm2, mm3, RFCutDist, Kin_Q2, Kin_W, Kin_eps, Kin_t, Kin_u, phq) for (HBeta, Hxp, Hyp, Hdel, HCal, HCer, CTp, RF, HodStart, pBeta, pxp, pyp, pP, pDel, pCal, pAero, pHGC, pHGCX, pHGCY, mm1, mm2, mm3, RFCutDist, Kin_Q2, Kin_W, Kin_eps, Kin_t, Kin_u, phq) in zip(*Cut_COIN_Protons_prompt_tmp)
                    if RFCutDist < 1.65]

    Cut_COIN_Protons_random = [(HBeta, Hxp, Hyp, Hdel, HCal, HCer, CTp, RF, HodStart, pBeta, pxp, pyp, pP, pDel, pCal, pAero, pHGC, pHGCX, pHGCY, mm1, mm2, mm3, RFCutDist, Kin_Q2, Kin_W, Kin_eps, Kin_t, Kin_u, phq) for (HBeta, Hxp, Hyp, Hdel, HCal, HCer, CTp, RF, HodStart, pBeta, pxp, pyp, pP, pDel, pCal, pAero, pHGC, pHGCX, pHGCY, mm1, mm2, mm3, RFCutDist, Kin_Q2, Kin_W, Kin_eps, Kin_t, Kin_u, phq) in zip(*Cut_COIN_Protons_rand_tmp)
                    if RFCutDist < 1.65]

    COIN_Protons = {
        "Uncut_Proton_Events" : Uncut_COIN_Protons,
        "Cut_Proton_Events_All" : Cut_COIN_Protons_all,
        "Cut_Proton_Events_All_NoRF" : Cut_COIN_Protons_all_noRF,
        "Cut_Proton_Events_Prompt" : Cut_COIN_Protons_prompt,
        "Cut_Proton_Events_Random" : Cut_COIN_Protons_random,
        }

    return COIN_Protons

def main():
    COIN_Pion_Data = coin_pions()
    COIN_Kaon_Data = coin_kaons()
    COIN_Proton_Data = coin_protons()
    # This is just the list of branches we use from the initial root file for each dict
    # I don't like re-defining this here as it's very prone to errors if you included (or removed something) earlier but didn't modify it here
    # Should base the branches to include based on some list and just repeat the list here (or call it again directly below)
    COIN_Pion_Data_Header = ["H_gtr_beta","H_gtr_xp","H_gtr_yp","H_gtr_dp","H_cal_etotnorm","H_cer_npeSum","CTime_ePiCoinTime_ROC1","P_RF_tdcTime","P_hod_fpHitsTime","P_gtr_beta","P_gtr_xp","P_gtr_yp","P_gtr_p","P_gtr_dp","P_cal_etotnorm","P_aero_npeSum","P_hgcer_npeSum","P_hgcer_xAtCer","P_hgcer_yAtCer","MMpi","MMK","MMp","RF_CutDist", "Q2", "W", "epsilon", "MandelT", "MandelU", "ph_q"]
    COIN_Kaon_Data_Header = ["H_gtr_beta","H_gtr_xp","H_gtr_yp","H_gtr_dp","H_cal_etotnorm","H_cer_npeSum","CTime_eKCoinTime_ROC1","P_RF_tdcTime","P_hod_fpHitsTime","P_gtr_beta","P_gtr_xp","P_gtr_yp","P_gtr_p","P_gtr_dp","P_cal_etotnorm","P_aero_npeSum","P_hgcer_npeSum","P_hgcer_xAtCer","P_hgcer_yAtCer","MMpi","MMK","MMp","RF_CutDist", "Q2", "W", "epsilon", "MandelT", "MandelU", "ph_q"]
    COIN_Proton_Data_Header = ["H_gtr_beta","H_gtr_xp","H_gtr_yp","H_gtr_dp","H_cal_etotnorm","H_cer_npeSum","CTime_epCoinTime_ROC1","P_RF_tdcTime","P_hod_fpHitsTime","P_gtr_beta","P_gtr_xp","P_gtr_yp","P_gtr_p","P_gtr_dp","P_cal_etotnorm","P_aero_npeSum","P_hgcer_npeSum","P_hgcer_xAtCer","P_hgcer_yAtCer","MMpi","MMK","MMp","RF_CutDist", "Q2", "W", "epsilon", "MandelT", "MandelU", "ph_q"]
    # Need to create a dict for all the branches we grab
    data = {}

    for d in (COIN_Pion_Data, COIN_Kaon_Data, COIN_Proton_Data): # Convert individual dictionaries into a "dict of dicts"
        data.update(d)
        data_keys = list(data.keys()) # Create a list of all the keys in all dicts added above, each is an array of data

    for i in range (0, len(data_keys)):
        if("Pion" in data_keys[i]):
            DFHeader=list(COIN_Pion_Data_Header)
        elif("Kaon" in data_keys[i]):
            DFHeader=list(COIN_Kaon_Data_Header)
        elif("Proton" in data_keys[i]):
            DFHeader=list(COIN_Proton_Data_Header)
        else:
            continue
            # Uncomment the line below if you want .csv file output, WARNING the files can be very large and take a long time to process!
            #pd.DataFrame(data.get(data_keys[i])).to_csv("%s/%s_%s.csv" % (OUTPATH, data_keys[i], runNum), header=DFHeader, index=False) # Convert array to panda dataframe and write to csv with correct header
        if (i == 0):
            pd.DataFrame(data.get(data_keys[i]), columns = DFHeader, index = None).to_root("%s/%s_%s_Analysed_Data.root" % (OUTPATH, runNum, MaxEvent), key ="%s" % data_keys[i])
        elif (i != 0):
            pd.DataFrame(data.get(data_keys[i]), columns = DFHeader, index = None).to_root("%s/%s_%s_Analysed_Data.root" % (OUTPATH, runNum, MaxEvent), key ="%s" % data_keys[i], mode ='a') 
                    
if __name__ == '__main__':
    main()
