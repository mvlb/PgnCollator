from FileScanner import PgnFileScanner, PgnFile
import os

class PgnCreator(object):
	
	defaultOutputFolderName = 'Output'
	 
	def __init__(self, options={}):
		self.srcFileLocation = options.get('outdir', None)
		self.backupFileLocation = None
		self.destinationFolder = None
	
	def createOutputFolder(self):
		
		#Create directory in current path or the path specified from command line.
		if self.srcFileLocation is None:
			self.destinationFolder = os.path.join(os.getcwd(),self.defaultOutputFolderName)
		else:
			self.destinationFolder = os.path.join(self.srcFileLocation,self.defaultOutputFolderName)
		
		if not (os.path.exists(self.destinationFolder)):
			os.makedirs(self.destinationFolder)
			
	def processPgnFilesInPath(self):
		
		iPgnFileScanner = PgnFileScanner(self.srcFileLocation, self.destinationFolder)
		iPgnFileScanner.scanAndEncodePgnAsJson()
		iPgnFileScanner.decodeJSON(self.destinationFolder)
		iPgnFileScanner.createMasterPgn(self.destinationFolder)
	
						
if __name__ == "__main__":
	print "Welcome PGN Creator"
	iPgnCreator = PgnCreator({'outdir':'C:\personal\chess\Games\chess.com'})
	iPgnCreator.createOutputFolder()
	iPgnCreator.processPgnFilesInPath()
	