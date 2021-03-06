from ..Models import dbConfig
from PIL import Image, ImageFile
import datetime
import time
import os
import sys
import uuid
import shutil
from ..Models import CamTrap, Import, MetaData
import zipfile
import exifread
from pyramid import threadlocal
import subprocess
# handle error on some photo
# image file truncated
ImageFile.LOAD_TRUNCATED_IMAGES = True

'''
TODO refact process more readable 
dont need to store file before get exif
we can processing exif on tmp file 
so we store only if ok (it's a better)
def writeFileToDisk(newFile,destPath) :
    # destPath = absolutePath + filename + fileExtension
    try:   
        with open(os.path.join(destPath), 'wb') as output_file:
            shutil.copyfileobj(newFile, output_file)
        output_file.close()
    except Exception:
        raise
    return 
'''
def resizePhoto(imgPathSrc):
    basewidth = 200
    try:
        img = Image.open(imgPathSrc)
        # Fully load the image now to catch any problems with the image
        # contents.
        img.load()
    except Exception:
        # handle error on img file
        return
    wpercent = (basewidth / float(img.size[0]))  # keep ratio
    hsize = int((float(img.size[1]) * float(wpercent)))
    img.thumbnail((basewidth, hsize), Image.ANTIALIAS)

    imgPathDestTab = imgPathSrc.split('\\')  # parse path into a tab
    # insert ""new directory"" in the path lenght - 1
    imgPathDestTab.insert(len(imgPathDestTab) - 1, "thumbnails")
    imgPathDest = "\\".join(imgPathDestTab)  # concat the new path

    img.save(imgPathDest)  # save the thumbnail on the hdd

def applyJetLag(jetLag):
    pass



def dateFromExif(imagePath):
    theDate = ""
    image = open(imagePath, 'rb')
    tagsExif = exifread.process_file(image)
    for tag in tagsExif:
        if tag in ('Image DateTime'):
            theDate = str(tagsExif[tag]).encode(
                'utf8').decode(sys.stdout.encoding)
            # theDate += ".000"
            theDate = theDate.replace(":", "-", 2)
            # theDate = datetime.datetime.strptime(theDate, "%Y-%m-%d %H:%M:%S.%f")
            theDate = datetime.datetime.strptime(theDate, "%Y-%m-%d %H:%M:%S")
    if(theDate == ""):
        theDate = None
    return theDate


def checkDate(exifDate, jetLag, startDate, endDate):
    newStartDate = time.strptime(startDate, "%Y-%m-%d %H:%M:%S")
    if(endDate == "0000-00-00 00:00:00"):
        newEndDate = time.strptime(str(datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')), "%Y-%m-%d %H:%M:%S")
    else:
        newEndDate = time.strptime(endDate, "%Y-%m-%d %H:%M:%S")
    if(exifDate == None):
        timePhoto = time.strptime("1985-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    else:
        jetLagArray = jetLag['hours'].split(':')
        if jetLag['operator'] == '+':
            operator = 1
        if jetLag['operator'] == '-':
            operator = -1
        dateOrigine = datetime.datetime.strptime(str(exifDate) , "%Y-%m-%d %H:%M:%S")
        dateDecall = dateOrigine + datetime.timedelta(hours = operator*int(jetLagArray[0]) , minutes = operator*int(jetLagArray[1]), seconds = operator*int(jetLagArray[2]) )
        timePhoto = time.strptime( dateDecall.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
        # timePhoto = time.strptime(str(exifDate), "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours = operator*int(jetLagArray[0]) , minutes = operator*int(jetLagArray[1]), seconds = operator*int(jetLagArray[2]) )
    if(timePhoto >= newStartDate and timePhoto <= newEndDate):
        return True
    else:
        return False


def unzip(zipFilePath, destFolder, fk_sensor, startDate, endDate, objMetaData):
    zfile = zipfile.ZipFile(zipFilePath)
    messageErrorFiles = ""
    nbFilesTotal = 0
    nbFilesInserted = 0

    for name in zfile.namelist():
        nbFilesTotal += 1
        extType = name.split('.')
        if(extType[len(extType) - 1] in ['jpg', 'JPG', 'jpeg', 'JPEG']):
            if not os.path.isfile(destFolder + str(name)):
                with open(os.path.join(destFolder, str(name)), 'wb') as fd:
                    fd.write(zfile.read(name))
                fd.close()
                # ici on peut test
                exifDate = dateFromExif(destFolder + str(name))
                dateOrigine = datetime.datetime.strptime(str(exifDate) , "%Y-%m-%d %H:%M:%S")
                dateDecall = dateOrigine + datetime.timedelta(hours = operator*int(jetLagArray[0]) , minutes = operator*int(jetLagArray[1]), seconds = operator*int(jetLagArray[2]) )
                datePhoto = dateDecall.strftime("%Y-%m-%d %H:%M:%S")
                if(checkDate(datePhoto, startDate, endDate)):
                    AddPhotoOnSQL(fk_sensor, destFolder, name, str(
                        extType[len(extType) - 1]), datePhoto)
                    resizePhoto(str(destFolder) + str(name))
                    nbFilesInserted += 1
                else:
                    os.remove(destFolder + str(name))
                    messageErrorFiles += str(name) + \
                        'Date not valid (' + str(datePhoto) + ') <BR>'
                # datePhoto = dateFromExif(destFolder + str(name))
                # if(checkDate(datePhoto, startDate, endDate)):
                #     AddPhotoOnSQL(fk_sensor, destFolder, name, str(
                #         extType[len(extType) - 1]), datePhoto)
                #     resizePhoto(str(destFolder) + str(name))
                #     nbFilesInserted += 1
                # else:
                #     os.remove(destFolder + str(name))
                #     messageErrorFiles += str(name) + \
                #         'Date not valid (' + str(datePhoto) + ') <BR>'
            else:
                messageErrorFiles += "File : " + \
                    str(name) + " is already on the server <BR>"
            # fd.close()
        else:
            messageErrorFiles += str(name) + " not a good file <BR>"
    zfile.close()
    # rename zip file
    # zipFileTab = zipFilePath.split('.')
    os.remove(zipFilePath)
    print(" Nb files in zip " + str(nbFilesTotal))
    print(" Nb files inserted " + str(nbFilesInserted))
    return messageErrorFiles, nbFilesTotal, nbFilesInserted


def AddPhotoOnSQL(fk_sensor, path, name, extension, date_creation,startDate,endDate,user,cmdMetaData):
    # raise
    session = threadlocal.get_current_request().dbsession

    idReturned = None
    if(not path.endswith('\\')):
        path += '\\'
    try: 
        currentImport = Import(
                ImportFileName=str(name),
                ImportType = 'CAMTRAP',
                FK_User = user,
                nbRows = 1,
                nbInserted = 0,
                maxDate = datetime.datetime.strptime(endDate,"%Y-%m-%d %H:%M:%S"),
                minDate = datetime.datetime.strptime(startDate,"%Y-%m-%d %H:%M:%S") 
                )
        session.add(currentImport)
        session.flush()
        if currentImport.ID:
            currentPhoto = CamTrap(
                fk_sensor=fk_sensor,
                path=str(path),
                name=str(name),
                extension='.jpg', 
                date_creation=date_creation, 
                note=5,
                FK_Import = currentImport.ID
                )
            session.add(currentPhoto)
            session.flush()
            if currentPhoto.pk_id:
                currentMetaData = MetaData(
                    FK_CamTrap=currentPhoto.pk_id ,
                    CommandLine= ' '.join(cmdMetaData)
                )
                session.add(currentMetaData)
                session.flush()
                currentImport.nbInserted = 1
                session.add(currentImport)
                session.flush()
                return currentPhoto.pk_id,currentImport.ID,currentPhoto.pk_id
    except:
        raise
    return 


def GenName():
    return uuid.uuid4()


def createNamePath(paramsPOST):
    nouveauPath = [1, 2, 3, 4]
    cheminParse = ""
    for key, value in paramsPOST.items():
        if(key == 'UnicIdentifier'):
            nouveauPath[0] = value
        elif(key == 'StartDate'):
            nouveauPath[1] = value
        elif(key == 'EndDate'):
            nouveauPath[2] = value
        elif (key == 'Name'):
            nouveauPath[3] = value

    for tmp in nouveauPath:
        if (cheminParse == ""):
            cheminParse += tmp
        else:
            cheminParse += "_" + str(tmp)

    return cheminParse

def callExiv2(self,cmd,listFiles):
    '''
        exiv is versionned and pâth is relative to this file like ../../exiv2 
        when we get the path of this file we can construct absolute path to find exiv2.exe 
    '''
    absolutePathFile = os.path.dirname( __file__ )

    '''
        need better way and secure 
        if os change '\\' to '/' 
        if path change that's will break etcetc
    '''
    #pathCmd = absolutePathFile.replace('\\ecoreleve_server\\Views','\\exiv2\\bin\\exiv2')
    # optionsForCmd = ' -h '
    # pathFiles = 'C:\\Users\\jean-vitus\\Desktop\\PP163_09N02P\\'
    # listFiles = ['13N002F.JPG','13N021D.JPG','13N038B.JPG','13N054M.JPG','13N087F (2).JPG','13N09M28sdfdsf.JPG','13N13M28.JPG','13N004A.JPG','13N023D.JPG','13N038F.JPG','13N057A.JPG','13N087F (3).JPG','13N09M32 (2).JPG','13N146A.JPG','13N004F.JPG','13N023I.JPG','13N03M23.JPG','13N05M23.JPG','13N087F (4).JPG','13N09M32.JPG','13N148A.JPG','13N005A.JPG','13N029D (2).JPG','13N03M25.JPG','13N05M28.JPG','13N087F (5).JPG','13N102A.JPG','13N153A.JPG','13N008M.JPG','13N029D.JPG','13N03M28.JPG','13N063F.JPG','13N087F (6).JPG','13N103A.JPG','13N156A (2).JPG','13N010I.JPG','13N02M01.JPG','13N040F.JPG','13N064A.JPG','13N087F (7).JPG','13N104F.JPG','13N156A.JPG','13N012D.JPG','13N02M14(2).JPG','13N041F.JPG','13N064F.JPG','13N087F.JPG','13N104M.JPG','13N158A.JPG','13N012F.JPG','13N02M14(3).JPG','13N043D.JPG','13N066B (2).JPG','13N088D.JPG','13N105M.JPG','13N39M32 (2).JPG','13N013D (2).JPG','13N02M14.JPG','13N043I.JPG','13N066B.JPG','13N08M32 (2).JPG','13N106B.JPG','13N39M32.JPG','13N013D.JPG','13N02M23 (2).JPG','13N04M14.JPG','13N066D.JPG','13N08M32.JPG','13N108B.JPG','IMAG2425.JPG','13N016D.JPG','13N02M23.JPG','13N04M22.JPG','13N06M15.JPG','13N092F.JPG','13N108M.JPG','N113A.JPG','13N01M06.JPG','13N034F.JPG','13N04M23(2).JPG','13N074F (2).JPG','13N093A.JPG','13N110B.JPG','13N01M14(1).JPG','13N035I (2).JPG','13N04M23.JPG','13N074F (3).JPG','13N094B (3).JPG','13N111B (2).JPG','13N01M14(2).JPG','13N035I (3).JPG','13N04M26 (2).JPG','13N074F.JPG','13N094B(2).JPG','13N111B.JPG','13N01M15.JPG','13N035I.JPG','13N04M26.JPG','13N07M23.JPG','13N094B.JPG','13N117M.JPG','13N01M18.JPG','13N036A.JPG','13N050D.JPG','13N07M28 (2).JPG','13N096A.JPG','13N123B.JPG','13N01M25.JPG','13N036D.JPG','13N050F.JPG','13N07M28.JPG','13N099B.JPG','13N12M28 (2).JPG','13N01M28.JPG','13N037B.JPG','13N051A.JPG','13N082F.JPG','13N09M28 (2).JPG','13N12M28.JPG','13N020D.JPG','13N037D.JPG','13N054D.JPG','13N084F.JPG','13N09M28 (3).JPG','13N133A.JPG']
    pathCmd = absolutePathFile.replace('\\ecoreleve_server\\Views','\\exiftool')


    # for idx in range(len(listFiles)):
    #     listFiles[idx] = pathFiles+listFiles[idx]


    try:
        FNULL = open(os.devnull, 'w')
        res = subprocess.run( [ pathCmd] +cmd + listFiles , stdout=FNULL, stderr=subprocess.STDOUT )

    except Exception as e :
        FNULL.close()
        print("exiftool has failed for the following reason" + str(e) )
        self.request.response.status_code = 520
        return str(e)

    FNULL.close()
    return "ok"    


def buildCmdMetaDatasAtImport(self, metaData) :
    generatedCmd = []

    #XMP-DC START
    generatedCmd.append('-XMP-dc:Identifier='+str(metaData['image']['photoId'])) #XmpText
    generatedCmd.append('-XMP-dc:Title-x-default=Camera trap ID='+str(metaData['image']['fkSensor'])+' - Picture name='+metaData['image']['name']) #XmpText
    generatedCmd.append('-XMP-dc:Creator='+metaData['user']['TUse_FirstName']+''+metaData['user']['TUse_LastName']) #XmpSeq
    #dcterms creator
    generatedCmd.append('-XMP-dc:Contributor='+metaData['user']['TUse_FirstName']+''+metaData['user']['TUse_LastName']) #XmpBag 
    #dcterms contributor
    generatedCmd.append('-XMP-dc:Description-x-default=Log of all ecoReleve data about the picture in EN') #LangAlt
    generatedCmd.append('-XMP-dc:Description-fr=log de toutes les données de la photo dans ecoReleve en FR') #LangAlt
    generatedCmd.append('-XMP-dc:Rights-x-default= © International Fund for Houbara Conservation') #LangAlt
    #XMP-DC END

    #XMP-PRISM START 
    # generatedCmd.append('-XMP-PRISM:creationDate='+metaData['image']['dateTimeOriginalPhoto']) #LangAlt
    # generatedCmd.append('-XMP-PRISM:DateReceived='+metaData['image']['dateInsertSQL'])
    # generatedCmd.append('-XMP-PRISM:modificationDate='+metaData['image']['lastTransformationDate'])
    #XMP-PRISM END

    #XMP-PMI START
    generatedCmd.append('-XMP-pmi:sequenceName=Monitored site'+metaData['monitoredSite']['Name']+'from'+metaData['session']['startDate']+'to'+metaData['session']['endDate']) #XmpText
    generatedCmd.append('-XMP-pmi:shootID='+str(metaData['image']['shootId'])) #XmpText
    generatedCmd.append('-XMP-pmi:contactInfo=contact@reneco-hq.org') #XmpText
    # generatedCmd.append('-XMP-pmi:location='+metaData['misc']['regionAnPlaceMonitoredSite']) #XmpText
    #XMP-PMI END

    #EXIF-GPS START
    generatedCmd.append('-GPS:GPSLatitudeRef=N') 
    generatedCmd.append('-GPS:GPSLatitude='+str(metaData['monitoredSite']['LAT']))
    generatedCmd.append('-GPS:GPSLongitudeRef=E') 
    generatedCmd.append('-GPS:GPSLongitude='+str(metaData['monitoredSite']['LON']))
    generatedCmd.append('-GPS:GPSAltitudeRef=+0') 
    generatedCmd.append('-GPS:GPSDOP='+str(metaData['monitoredSite']['Precision'])) #XmpText
    generatedCmd.append('-GPS:GPSAltitude='+str(metaData['monitoredSite']['ELE'])) #XmpText
    #EXIF-GPS END

    #XMP-IPTC START
    # generatedCmd.append('-XMP-iptcCore:Location='+metaData['misc']['regionAnPlaceMonitoredSite']) #XmpTexst
    #XMP-IPTC END

    #XMP-PHOTOSHOP START
    generatedCmd.append('-XMP-Photoshop:DateCreated='+metaData['image']["dateTimeOriginalPhoto"]) #XmpText
    # generatedCmd.append('-XMP-Photoshop:Headline=Picture of'+metaData['monitoredSite'].Category+''+metaData['monitoredSite'].Name+',Lon:'+metaData['monitoredSite'].Lon+',Lat:'+metaData['monitoredSite'].Lat+', on'+metaData.pictureCreationDate+'showing'+tagList) #XmpText
    generatedCmd.append('-XMP-Photoshop:Source=RENECO '+metaData['misc']['projectName']) #XmpText
    #XMP-PHOTOSHOP END

    #XMP-XMP START
    # generatedCmd.append('-XMP-XMP:CreateDate='+metaData['image']['dateTimeCreationPhoto']) #XmpText
    # generatedCmd.append('-XMP-XMP:MetadataDate='+metaData['image']['lastDateWriteInPhoto']) #XmpText
    generatedCmd.append('-XMP-XMPRights:UsageTerms-x-default=Non commercial use only') #LangAlt
    #XMP-XMP END
    # res = subprocess.run( [ pathCmd, generatedCmd] + listFiles )

    return generatedCmd