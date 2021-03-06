#ifndef ProtonYield_h
#define ProtonYield_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TSelector.h>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>
#include <TTreeReaderArray.h>
#include <TMath.h>
#include <TProfile2D.h>
#include <TH2.h>
#include <TF1.h>
#include <TArc.h>

// Headers needed by this particular selector

class ProtonYield : public TSelector {
 public :
  TTreeReader     fReader;  //!the tree reader
  TTree          *fChain = 0;   //!pointer to the analyzed TTree or TChain

  //Declare some doubles
  Double_t       *MMp;
  Double_t       *MMPi;
  Double_t       *MMK;

  //Declare Histograms
  TH2F           *h2missKcut_CT;
  TH2F           *h2misspicut_CT;
  TH2F           *h2ROC1_Coin_Beta_noID_kaon;
  TH2F           *h2ROC1_Coin_Beta_kaon;
  TH2F           *h2ROC1_Coin_Beta_noID_pion;
  TH2F           *h2ROC1_Coin_Beta_pion;
  TH2F           *h2ROC1_Coin_Beta_noID_proton;
  TH2F           *h2ROC1_Coin_Beta_proton;

  TH2F           *h2HMS_electron;
  TH2F           *h2HMS_electron_cut;
  TH1F           *h1SHMS_electron;
  TH1F           *h1SHMS_electron_cut;

  TH2F           *h2SHMS_AERO_HGC;
  TH2F           *h2SHMS_CAL_HGC;

  TH2F           *h2SHMSK_kaon_cut;
  TH2F           *h2SHMSK_pion_cut;

  TH2F           *h2SHMSpi_kaon_cut;
  TH2F           *h2SHMSpi_pion_cut;

  TH2F           *h2SHMSp_kaon_cut;
  TH2F           *h2SHMSp_pion_cut;

  TH2F           *h2SHMS_pion;
  TH2F           *h2SHMS_pion_cut;

  TH1F           *h1SHMS_delta;
  TH1F           *h1SHMS_delta_cut;
  TH1F           *h1HMS_delta;
  TH1F           *h1HMS_delta_cut;

  TH1F           *h1SHMS_th;
  TH1F           *h1SHMS_th_cut;
  TH1F           *h1SHMS_ph;
  TH1F           *h1SHMS_ph_cut;

  TH1F           *h1HMS_th;
  TH1F           *h1HMS_th_cut;
  TH1F           *h1HMS_ph;
  TH1F           *h1HMS_ph_cut;

  TH1F           *h1mmissK;
  TH1F           *h1mmissK_rand;
  TH1F           *h1mmissK_cut;
  TH1F           *h1mmissK_remove;

  TH1F           *h1mmisspi;
  TH1F           *h1mmisspi_rand;
  TH1F           *h1mmisspi_cut;
  TH1F           *h1mmisspi_remove;

  TH1F           *h1mmissp;
  TH1F           *h1mmissp_rand;
  TH1F           *h1mmissp_cut;
  TH1F           *h1mmissp_remove;

  TH2F           *h2WvsQ2;
  TH1F           *h1epsilon;
  TH2F           *h2tvsph_q;

  TH1F           *h1EDTM;
  TH1F           *h1TRIG5;

  TArc           *Arc[10];

  // Readers to access the data (delete the ones you do not need).
  TTreeReaderArray<Double_t> CTime_eKCoinTime_ROC1  = {fReader, "CTime.eKCoinTime_ROC1"};
  TTreeReaderArray<Double_t> CTime_ePiCoinTime_ROC1 = {fReader, "CTime.ePiCoinTime_ROC1"};
  TTreeReaderArray<Double_t> CTime_epCoinTime_ROC1  = {fReader, "CTime.epCoinTime_ROC1"};
  TTreeReaderArray<Double_t> P_gtr_beta         = {fReader, "P.gtr.beta"};
  TTreeReaderArray<Double_t> P_gtr_th           = {fReader, "P.gtr.th"};
  TTreeReaderArray<Double_t> P_gtr_ph           = {fReader, "P.gtr.ph"};
  TTreeReaderArray<Double_t> H_gtr_beta         = {fReader, "H.gtr.beta"};
  TTreeReaderArray<Double_t> H_gtr_th           = {fReader, "H.gtr.th"};
  TTreeReaderArray<Double_t> H_gtr_ph           = {fReader, "H.gtr.ph"};
  TTreeReaderArray<Double_t> H_cal_etotnorm     = {fReader, "H.cal.etotnorm"}; 
  TTreeReaderArray<Double_t> H_cer_npeSum       = {fReader, "H.cer.npeSum"};
  TTreeReaderArray<Double_t> P_cal_etotnorm     = {fReader, "P.cal.etotnorm"};
  TTreeReaderArray<Double_t> P_aero_npeSum      = {fReader, "P.aero.npeSum"};
  TTreeReaderArray<Double_t> P_hgcer_npeSum     = {fReader, "P.hgcer.npeSum"};
  TTreeReaderArray<Double_t> H_gtr_dp           = {fReader, "H.gtr.dp"};
  TTreeReaderArray<Double_t> P_gtr_dp           = {fReader, "P.gtr.dp"};
  TTreeReaderArray<Double_t> P_gtr_p            = {fReader, "P.gtr.p"};
  TTreeReaderArray<Double_t> Q2                 = {fReader, "H.kin.primary.Q2"};
  TTreeReaderArray<Double_t> W                  = {fReader, "H.kin.primary.W"};
  TTreeReaderArray<Double_t> epsilon            = {fReader, "H.kin.primary.epsilon"};
  TTreeReaderArray<Double_t> ph_q               = {fReader, "P.kin.secondary.ph_xq"};
  TTreeReaderArray<Double_t> emiss              = {fReader, "P.kin.secondary.emiss"};
  TTreeReaderArray<Double_t> pmiss              = {fReader, "P.kin.secondary.pmiss"};
  TTreeReaderArray<Double_t> MandelT            = {fReader, "P.kin.secondary.MandelT"};
  TTreeReaderValue<Int_t>    fEvtType           = {fReader, "fEvtHdr.fEvtType"};

  TTreeReaderValue<Double_t> pEDTM              = {fReader, "T.coin.pEDTM_tdcTime"};

  ProtonYield(TTree * /*tree*/ =0) {h2missKcut_CT=0, h2misspicut_CT=0, h2ROC1_Coin_Beta_noID_kaon=0, h2ROC1_Coin_Beta_kaon=0, h2ROC1_Coin_Beta_noID_pion=0, h2ROC1_Coin_Beta_pion=0, h2ROC1_Coin_Beta_noID_proton=0, h2ROC1_Coin_Beta_proton=0,h2HMS_electron=0, h2HMS_electron_cut=0, h1SHMS_electron=0, h1SHMS_electron_cut=0, h2SHMS_AERO_HGC=0, h2SHMS_CAL_HGC=0, h2SHMSK_kaon_cut=0, h2SHMSK_pion_cut=0, h2SHMSpi_kaon_cut=0, h2SHMSpi_pion_cut=0, h2SHMSp_kaon_cut=0, h2SHMSp_pion_cut=0,h1SHMS_delta=0, h1SHMS_delta_cut=0, h1HMS_delta=0, h1HMS_delta_cut=0, h1SHMS_th=0, h1SHMS_th_cut=0, h1SHMS_ph=0, h1SHMS_ph_cut=0, h1HMS_th=0, h1HMS_th_cut=0, h1HMS_ph=0, h1HMS_ph_cut=0, h1mmissK=0,h1mmissK_rand=0, h1mmissK_cut=0, h1mmissK_remove=0, h1mmisspi=0, h1mmisspi_rand=0, h1mmisspi_cut=0, h1mmisspi_remove=0, h1mmissp=0, h1mmissp_rand=0, h1mmissp_cut=0, h1mmissp_remove=0, h2WvsQ2=0, h2tvsph_q=0, h1epsilon=0, h1EDTM=0,h1TRIG5=0;}
  virtual ~ProtonYield() { }
  virtual Int_t   Version() const { return 2; }
  virtual void    Begin(TTree *tree);
  virtual void    SlaveBegin(TTree *tree);
  virtual void    Init(TTree *tree);
  virtual Bool_t  Notify();
  virtual Bool_t  Process(Long64_t entry);
  virtual Int_t   GetEntry(Long64_t entry, Int_t getall = 0) { return fChain ? fChain->GetTree()->GetEntry(entry, getall) : 0; }
  virtual void    SetOption(const char *option) { fOption = option; }
  virtual void    SetObject(TObject *obj) { fObject = obj; }
  virtual void    SetInputList(TList *input) { fInput = input; }
  virtual TList  *GetOutputList() const { return fOutput; }
  virtual void    SlaveTerminate();
  virtual void    Terminate();

  ClassDef(ProtonYield,0);

};

#endif

#ifdef ProtonYield_cxx
void ProtonYield::Init(TTree *tree)
{
  // The Init() function is called when the selector needs to initialize
  // a new tree or chain. Typically here the reader is initialized.
  // It is normally not necessary to make changes to the generated
  // code, but the routine can be extended by the user if needed.
  // Init() will be called many times when running on PROOF
  // (once per file to be processed).

  fReader.SetTree(tree);
}

Bool_t ProtonYield::Notify()
{
  // The Notify() function is called when a new file is opened. This
  // can be either for a new TTree in a TChain or when when a new TTree
  // is started when using PROOF. It is normally not necessary to make changes
  // to the generated code, but the routine can be extended by the
  // user if needed. The return value is currently not used.

  return kTRUE;
}

#endif // #ifdef ProtonYield_cxx
