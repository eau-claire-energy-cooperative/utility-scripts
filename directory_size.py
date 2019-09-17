"""Walk a directory and output the total size as well as a list of file extensions and the total size they occupy"""
import os
import os.path
import math
import argparse

#parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument('-p','--path',required=True,help='The path to start parsing')
parser.add_argument('-s','--sort',required=False,help='How to sort the list (alpha, size)',type=str,choices=['alpha','size'],default='alpha')
parser.add_argument('-u','--units',required=False,help='Units to use for display, default=GB',type=str,choices=['KB','MB','GB'],default='GB')
args = parser.parse_args()

class FileCounter:
    totalSize = 0 # the total size in bytes
    extList = {} #list of extensions and the total size

    #returns the size in bytes converted to the unit given
    def convertSize(self,byteSize,unit='MB'):
        units = {'KB': 1024, 'MB': math.pow(1024,2),'GB':math.pow(1024,3)}
        
        return byteSize/units[unit]
    
    #walk the given path, recording the file size
    def walkPath(self,aPath):
        for (dirPath, dirs, files) in os.walk(aPath):
            for aFile in files:
                #get the size and ext
                fSize = os.path.getsize(os.path.join(dirPath,aFile))
                self.totalSize = self.totalSize + fSize
                fName,fExt = os.path.splitext(aFile)
            
                if(fExt != None):
                    fExt = fExt.lower()
                    
                    #temp files are the ext
                    if(fExt == ''):
                        fExt = fName.lower()
                        
                    #if the extension already exists, add to it, otherwise just set it
                    if(fExt in self.extList):
                        self.extList[fExt] = self.extList[fExt] + fSize
                    else:
                        self.extList[fExt] = fSize

    def getTotalSize(self,unit='MB'):
        return self.convertSize(self.totalSize,unit)

    def getExtensions(self,sort='key'):
        if(sort == 'key'):
            return {k:self.extList[k] for k in sorted(self.extList.keys())}
        else:
            return {k:v for k,v in sorted(self.extList.items(), key=lambda item: item[1], reverse=True)}
                        
fCounter = FileCounter()
fCounter.walkPath(args.path)

print('Getting files from: %s' % args.path)
#print the total
print("Total directory size: %.3f%s" % (fCounter.getTotalSize(args.units),args.units))
print('')
if(args.sort == 'alpha'):
    print('Files by extension type')
    fileList = fCounter.getExtensions().items()

else:
    print('Files by extension type, sorted by size')
    fileList = fCounter.getExtensions('value').items()
    
for anExt,extSize in fileList:
    print("%s : %.3f%s" % (anExt,fCounter.convertSize(extSize,args.units),args.units))
        
