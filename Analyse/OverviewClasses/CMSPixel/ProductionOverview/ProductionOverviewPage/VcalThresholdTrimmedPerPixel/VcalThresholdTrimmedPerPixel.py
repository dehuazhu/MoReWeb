import ROOT
import AbstractClasses


class ProductionOverview(AbstractClasses.GeneralProductionOverview.GeneralProductionOverview):

    def CustomInit(self):

        self.NameSingle='VcalThresholdTrimmedPerPixel'
        self.Name='CMSPixel_ProductionOverview_%s'%self.NameSingle
        self.Title = 'Vcal Thr Trimmed {Test}'.format(Test=self.Attributes['Test'])
        self.DisplayOptions = {
            'Width': 1,
        }
        self.SubPages = []
        self.SavePlotFile = True
        self.Canvas.SetCanvasSize(400,500)

    def GenerateOverview(self):
        Rows = self.FetchData()
        ModuleIDsList = self.GetModuleIDsList(Rows)

        # define for which grades to plot histogram
        HistogramDict = {
            '0-All': {
                'Histogram': None,
                'Title': 'All',
            },
            '1-A': {
                'Histogram': None,
                'Grades': [1],
                'Color': self.GetGradeColor('A'),
                'Title': 'A',
            },
            '2-B': {
                'Histogram': None,
                'Grades': [2],
                'Color': self.GetGradeColor('B'),
                'Title': 'B',
            },
            '3-C': {
                'Histogram': None,
                'Grades': [3],
                'Color': self.GetGradeColor('C'),
                'Title': 'C',
            },
            '4-AB': {
                'Histogram': None,
                'Grades': [1, 2],
                'Title': 'A/B',
                'Show': False,
            }
        }

        # set histogram options
        HistogramOptions = {
            'RootFileHistogramName': 'VcalThresholdTrimmed',
            'GradeJsonPath': ['Chips','Chip{Chip}', 'Grading','KeyValueDictPairs.json','PixelDefectsGrade','Value'],
            'RootFilePath': ['Chips' ,'Chip{Chip}', 'VcalThresholdTrimmed', '*.root'],
            'StatsPosition': [0.50,0.88],
            'LegendPosition': [0.2, 0.88],
            'XTitle': "Threshold [VCAL]",
            'YTitle': "No. of Entries",
            'Range': [0, 100],
        }

        # define gradign cuts
        GradingCuts = [self.TestResultEnvironmentObject.GradingParameters['trimThr'] - self.TestResultEnvironmentObject.GradingParameters['tthrTol'], self.TestResultEnvironmentObject.GradingParameters['trimThr'] + self.TestResultEnvironmentObject.GradingParameters['tthrTol']]

        # draw histogram
        self.DrawPixelHistogram(Rows, ModuleIDsList, HistogramDict, HistogramOptions)

        # draw grading cuts
        CutLow = []
        for Cut in GradingCuts:
            CutLow.append(ROOT.TCutG('lLower', 2))

            CutLow[-1].SetPoint(0, Cut, -1e6)
            CutLow[-1].SetPoint(1, Cut, +1e6)
            CutLow[-1].SetLineColor(ROOT.kRed)
            CutLow[-1].SetLineStyle(2)
            CutLow[-1].Draw('same')


        self.SaveCanvas()
        HTML = self.Image(self.Attributes['ImageFile'])

        AbstractClasses.GeneralProductionOverview.GeneralProductionOverview.GenerateOverview(self)

        ROOT.gPad.SetLogy(0)
        self.DisplayErrorsList()
        return self.Boxed(HTML)

