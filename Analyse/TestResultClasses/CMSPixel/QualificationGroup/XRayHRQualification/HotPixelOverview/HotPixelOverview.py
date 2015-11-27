import ROOT
import AbstractClasses

class TestResult(AbstractClasses.GeneralTestResult.GeneralTestResult):
    def CustomInit(self):
        self.Name='CMSPixel_QualificationGroup_XRayHRQualification_HotPixelOverview_TestResult'
        self.NameSingle='HotPixelOverview'
        self.Attributes['TestedObjectType'] = 'CMSPixel_Module'

    def PopulateResultData(self):
        ROOT.gPad.SetLogy(0)
        ROOT.gStyle.SetOptStat(0)

        xBins = 8 * self.nCols
        yBins = 2 * self.nRows
        self.ResultData['Plot']['ROOTObject'] = ROOT.TH2D(self.GetUniqueID(), "", xBins, 0., xBins, yBins, 0., yBins)

        for i in self.ParentObject.ResultData['SubTestResults']['Chips'].ResultData['SubTestResults']:
            ChipTestResultObject = self.ParentObject.ResultData['SubTestResults']['Chips'].ResultData['SubTestResults'][i]
            histo = ChipTestResultObject.ResultData['SubTestResults']['HotPixelMap_{Rate}'.format(Rate=self.Attributes['Rate'])].ResultData['Plot']['ROOTObject']
            chipNo = ChipTestResultObject.Attributes['ChipNo']

            if histo:
                for col in range(self.nCols): 
                    for row in range(self.nRows):
                        result = histo.GetBinContent(col + 1, row + 1)
                        self.UpdatePlot(chipNo, col, row, result)

        if self.ResultData['Plot']['ROOTObject']:
            try:
                self.ResultData['Plot']['ROOTObject'].GetXaxis().SetTickLength(0.015)
                self.ResultData['Plot']['ROOTObject'].GetYaxis().SetTickLength(0.012)
                self.ResultData['Plot']['ROOTObject'].GetXaxis().SetAxisColor(1, 0.4)
                self.ResultData['Plot']['ROOTObject'].GetYaxis().SetAxisColor(1, 0.4)
                self.Canvas.SetFrameLineStyle(0)
                self.Canvas.SetFrameLineWidth(1)
                self.Canvas.SetFrameBorderMode(0)
                self.Canvas.SetFrameBorderSize(1)
                self.Canvas.SetCanvasSize(1784, 412)
            except:
                pass
            self.ResultData['Plot']['ROOTObject'].SetTitle("")
            self.ResultData['Plot']['ROOTObject'].GetXaxis().SetTitle("Column No.")
            self.ResultData['Plot']['ROOTObject'].GetYaxis().SetTitle("Row No.")
            self.ResultData['Plot']['ROOTObject'].GetXaxis().CenterTitle()
            self.ResultData['Plot']['ROOTObject'].GetYaxis().SetTitleOffset(1.5)
            self.ResultData['Plot']['ROOTObject'].GetYaxis().CenterTitle()
            self.ResultData['Plot']['ROOTObject'].GetZaxis().SetTitle("#hits")
            self.ResultData['Plot']['ROOTObject'].GetZaxis().SetTitleOffset(0.5)
            self.ResultData['Plot']['ROOTObject'].GetZaxis().CenterTitle()
            self.ResultData['Plot']['ROOTObject'].Draw('colz')


        self.ResultData['Plot']['Format'] = 'png'

        self.Title = 'Masked Hot Pixels {Rate}'.format(Rate=self.Attributes['Rate'])
        self.SaveCanvas()     

    def UpdatePlot(self, chipNo, col, row, value):
        result = value
        if chipNo < 8:
            tmpCol = 8 * self.nCols - 1 - chipNo * self.nCols - col
            tmpRow = 2 * self.nRows - 1 - row
        else:
            tmpCol = (chipNo % 8 * self.nCols + col)
            tmpRow = row
        # Get the data from the chip sub test result hitmap

        if result and self.verbose:
            print chipNo, col, row, '--->', tmpCol, tmpRow, result
        self.ResultData['Plot']['ROOTObject'].Fill(tmpCol, tmpRow, result)
