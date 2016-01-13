import os
import json
import re
from datetime import datetime

class PgnFile(object):
    
    def __init__(self, fileName = None):
        self.fileName = ""
        self.filePath = ""
        self.event = ""
        self.site = ""
        self.date = ""
        self.round = ""
        self.white = ""
        self.black = ""
        self.result = ""
        self.eco = ""
        self.whiteElo = 0
        self.blackElo = 0
        self.annotator = ""
        self.plyCount = 0
        self.eventDate = ""
        self.isParsed = True
        self.userPlays = "White"
        self.moves = ""
        self.termination = ""
        self.timeControl = ""
        
    def _initialize(self, initData={}):

        self.fileName = initData.get('FileName', "")
        self.filePath = initData.get('FilePath', "")
        self.event = initData.get('Event', "")
        self.site =  initData.get('Site', "")
        
        dateStr = initData.get('Date',"2000.01.01")
        self.date = self.convertStringToDateFormat(dateStr)
         
        self.round = initData.get('Round', "")
        self.white = initData.get('White', "")
        self.black = initData.get('Black', "")
        self.result = initData.get('Result', "")
        self.eco = initData.get('Eco', "")
        self.whiteElo = initData.get('WhiteElo', 0)
        self.blackElo = initData.get('BlackElo', 0)
        self.annotator = initData.get('Annotator', "")
        self.plyCount = initData.get('PlyCount', 0)
        self.eventDate = self.date
        self.isParsed = initData.get('Parsed', False)
        self.userPlays = initData.get('UserPlays', "")
        self.termination = initData.get('Termination', "")
        self.timeControl = initData.get('TimeControl', "")
        self.moves = initData.get('Moves', "")
    
    def convertStringToDateFormat(self, str):
        
        return datetime.strptime(str, '%Y.%m.%d')

    def convertDateToStringFormat(self, date):
        
        return datetime.strftime(date, '%Y.%m.%d')    
    
    def createPgnFile(self, pgnObj, fileName):
        
        with open(fileName, 'a+') as fHandle:
            self._fillPgnMetaDataString("Event", pgnObj.event, fHandle)
            self._fillPgnMetaDataString("Site", pgnObj.site, fHandle)
            self._fillPgnMetaDataString("Date", self.convertDateToStringFormat(pgnObj.date), fHandle)
            self._fillPgnMetaDataString("Round", pgnObj.round, fHandle)
            self._fillPgnMetaDataString("White", pgnObj.white, fHandle)
            self._fillPgnMetaDataString("Black", pgnObj.black, fHandle)
            self._fillPgnMetaDataString("Result", pgnObj.result, fHandle)
            self._fillPgnMetaDataString("WhiteElo", str(pgnObj.whiteElo), fHandle)
            self._fillPgnMetaDataString("BlackElo", str(pgnObj.blackElo), fHandle)
            self._fillPgnMetaDataString("PlyCount", str(pgnObj.plyCount), fHandle)
            self._fillPgnMetaDataString("Annotator", pgnObj.annotator, fHandle)
            self._fillPgnMetaDataString("Eco", pgnObj.eco, fHandle)
            self._fillPgnMetaDataString("Termination", pgnObj.termination, fHandle)
            self._fillPgnMetaDataString("TimeControl", pgnObj.timeControl, fHandle)
            self._fillPgnMoveString(pgnObj.moves, fHandle)
                       
    def _fillPgnMetaDataString(self, str, value, fh):

            string = "[" + str + " \"" + value + "\"]" + "\n" 
            fh.write(string)

    def _fillPgnMoveString(self, value, fh):

            string = "\n" + value + "\n\n\n" 
            fh.write(string)
            
        
class PgnFileScanner(object) :
       
    def __init__(self, srcPath, destPath):
            
        self.srcPath = srcPath
        
        if self.srcPath is None:
            self.srcPath = os.getcwd()
            
        self.destPath = destPath
        self.pgnFileObjs = []
        
    def scanAndEncodePgnAsJson(self):
        
        excludeOutputDirectory = set(['Output'])
        fileData = {}
        # Create a list of all PGNs in the source path
        for root, subdirs, files in os.walk(self.srcPath) :
            #Exclude the Output Directory
            subdirs[:] = [d for d in subdirs if d not in excludeOutputDirectory]

            for file in files :
                if file.endswith(".pgn"):                   
                    fileData[file] = root                   
                    #get absolute path for the file
                    filePath = os.path.join(root, file)   
                    #Create an empty dictionary for storing the parsed contents
                    pgnDict = {}
                    moves = ""
                    captureMoves = False
                    with open(filePath,'r') as fIn:
                        for line in fIn:
                            #Captures metadata from PGN
                            searchObj = re.search(r'^[[](.*?) ["](.*?)["][]]', line, re.M|re.I)
                            if searchObj:
                                pgnDict[searchObj.group(1)] = searchObj.group(2)
                            
                            #Captures moves from PGN
                            searchObj = re.search(r'^[1][.].*', line, re.M|re.I)
                            if searchObj:
                                captureMoves = True
                            #Capture end of moves from PGN
                            searchObj = re.search(r'$[01][-][01]', line, re.M|re.I)
                            if searchObj:
                                captureMoves = False
                                
                            #Capture all moves into one huge string    
                            if(captureMoves) :
                                moves += line
                        
                        moves = moves.replace('\n','')
                        pgnDict['Moves'] = moves
                        #Write the newly formed Dictionary as a separate JSON encoded file
                        with open(os.path.join(self.destPath,file+'.game.json'),'w') as jsonPgnFileHandle:
                            json.dump(pgnDict, jsonPgnFileHandle)
                            
            
            with open(os.path.join(self.destPath,'pgn_files.json'),'w') as pgnFileHandle:
                json.dump(fileData, pgnFileHandle)

    def decodeJSON(self, srcDir):
        
        for root, subdirs, files in os.walk(srcDir) :
            
            for file in files :
                if file.endswith(".game.json"):
                    
                    fileWithPath = os.path.join(root, file)
                    with open(fileWithPath, 'r') as fIn:
                        pgnDict = {}
                        pgnDict = json.load(fIn);
                        iPgnFile = PgnFile()
                        iPgnFile._initialize(pgnDict)
                        self.pgnFileObjs.append(iPgnFile)
                        
    def createMasterPgn(self, destDir):
        
        iPgnFile = PgnFile()
        
        fileName = os.path.join(destDir, 'Master.pgn')
        
        for pgnObj in self.pgnFileObjs:
            
            iPgnFile.createPgnFile(pgnObj, fileName)             