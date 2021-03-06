# -*- coding: utf-8 -*-
import ROOT
import AbstractClasses
import AbstractClasses.Helper.HistoGetter as HistoGetter
import array, math

class TestResult(AbstractClasses.GeneralTestResult.GeneralTestResult):
    def CustomInit(self):
        self.Name = 'CMSPixel_QualificationGroup_XRayHRQualification_Chips_Chip_ColumnUniformityEventsPerColumn_TestResult'
        self.NameSingle = 'ColumnUniformityEventsPerColumn'
        self.Attributes['TestedObjectType'] = 'CMSPixel_QualificationGroup_XRayHRQualification_ROC'
        self.ResultData['HiddenData']['EventBins'] = 0
        self.ResultData['KeyValueDictPairs'] = {
            'mu': {
                'Value':'{0:1.2f}'.format(-1),
                'Label':'μ'
            },
            'sigma':{
                'Value':'{0:1.2f}'.format(-1),
                'Label':'fit error of μ'
            },
            'NumberOfNonUniformColumnEvents':{
                'Value':'{0:1.2f}'.format(-1),
                'Label':'Non uniform 10.000 event bins'
            }
        }

    def PopulateResultData(self):
        ChipNo = self.ParentObject.Attributes['ChipNo']
        HitsVsEventsROOTObjects = {}
        Rates = self.ParentObject.ParentObject.ParentObject.Attributes['Rates']
        EventBins = 0
        EventMin = 0
        EventMax = 0
        Rate = self.Attributes['Rate']

        histogramName = self.ParentObject.ParentObject.ParentObject.ParentObject.HistoDict.get('HighRate', 'hitsVsEvtCol').format(ChipNo=self.ParentObject.Attributes['ChipNo'])
        rootFileHandle = self.ParentObject.ParentObject.ParentObject.Attributes['ROOTFiles']['HRData_{Rate}'.format(Rate=Rate)]
        self.ResultData['Plot']['ROOTObject'] = HistoGetter.get_histo(rootFileHandle, histogramName).Clone(self.GetUniqueID())

        self.ResultData['HiddenData']['EventBins'] = max(
            self.ResultData['Plot']['ROOTObject'].GetXaxis().GetLast(),EventBins)

        if self.ResultData['Plot']['ROOTObject']:
            ROOT.gStyle.SetOptStat(0)
            self.Canvas.Clear()
            self.ResultData['Plot']['ROOTObject'].SetTitle("")

            self.ResultData['Plot']['ROOTObject'].GetXaxis().SetTitle("Event")
            self.ResultData['Plot']['ROOTObject'].GetYaxis().SetTitle("Column")
            self.ResultData['Plot']['ROOTObject'].GetXaxis().CenterTitle()
            self.ResultData['Plot']['ROOTObject'].GetYaxis().SetTitleOffset(1.5)
            self.ResultData['Plot']['ROOTObject'].GetYaxis().CenterTitle()
            self.ResultData['Plot']['ROOTObject'].SetContour(100)
            self.ResultData['Plot']['ROOTObject'].Draw('colz')

            self.ResultData['Plot']['ROOTObject'].GetXaxis().SetRange(
                self.ResultData['Plot']['ROOTObject'].GetXaxis().GetFirst(),
                self.ResultData['Plot']['ROOTObject'].GetXaxis().GetLast()-1
            )

            #why a fit anyway...
            FitPol0 = ROOT.TF1("GaussFitFunction", "pol0")
            self.ResultData['Plot']['ROOTObject'].Fit(FitPol0,'RQ0')

            Mean = -1
            RMS = -1
            if FitPol0:
                Mean = FitPol0.GetParameter(0)
                RMS = FitPol0.GetParError(0) # not rms but par0 error...

            self.ResultData['Plot']['ROOTObject'].GetXaxis().SetRange(
                self.ResultData['Plot']['ROOTObject'].GetXaxis().GetFirst(),
                self.ResultData['Plot']['ROOTObject'].GetXaxis().GetLast()
            )

            self.ResultData['KeyValueDictPairs']['mu']['Value'] = '{0:1.2f}'.format(Mean)
            self.ResultData['KeyValueDictPairs']['sigma']['Value'] = '{0:1.2f}'.format(RMS)

            self.ResultData['KeyList'] += ['mu','sigma']

            NumberOfNonUniformColumnEvents = 0
            for Column in range(0, 52):
                ColumnReadoutUniformityHistogram = self.ResultData['Plot']['ROOTObject'].ProjectionX(self.GetUniqueID(), Column + 1, Column + 1)
                NEvents = ColumnReadoutUniformityHistogram.GetNbinsX()
                FirstBin = ColumnReadoutUniformityHistogram.GetXaxis().GetFirst()
                LastBin = ColumnReadoutUniformityHistogram.FindLastBinAbove(0)
                ColumnReadoutUniformityHistogram.GetXaxis().SetRange(1, LastBin - 1)

                MeanHitsPerBin = ColumnReadoutUniformityHistogram.Integral(FirstBin, LastBin) / (LastBin - FirstBin + 1)
                ReadoutUniformityOverTimeSigma = math.sqrt(MeanHitsPerBin) # poisson

                #exclude last bin
                for Event in range(0, LastBin - 1):
                    BinHits = ColumnReadoutUniformityHistogram.GetBinContent(Event + 1)

                    if( abs(BinHits-MeanHitsPerBin) > self.TestResultEnvironmentObject.GradingParameters['XRayHighRate_factor_readout_uniformity']
                        *ReadoutUniformityOverTimeSigma
                    ):
                        NumberOfNonUniformColumnEvents += 1

                ColumnReadoutUniformityHistogram.Delete()

            self.ResultData['KeyValueDictPairs']['NumberOfNonUniformColumnEvents']['Value'] = str(NumberOfNonUniformColumnEvents)
            self.ResultData['KeyList'] += ['NumberOfNonUniformColumnEvents']

            ROOT.gPad.Update()

        self.Title = 'Col. Uniformity per Event: C{ChipNo} {Rate}'.format(ChipNo=self.ParentObject.Attributes['ChipNo'], Rate=self.Attributes['Rate'])
        if self.Canvas:
            self.Canvas.SetCanvasSize(750, 750)
        self.ResultData['Plot']['Format'] = 'png'
        self.SaveCanvas()


