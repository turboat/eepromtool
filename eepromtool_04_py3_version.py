import argparse, sys #for handling command line params

# Last major update: 9-9-2014
# Minor edit, 28-9-2018

VERSION = 0.4
WARN = False
DEBUG = False

#World Manufacture Index
WMI = {'WAU':"Audi",'TRU':"Audi Hungary",'93U':"Audi Brazil",'WVW':"VW",'WV1':"VW Commercials",'WV2':"VW Bus",
       'VWV':"VW Spain",'AAV':"VW South Africa",'1VW':"VW USA",'2V4':"VW Canada",'3VW':"VW Mexico",'8AW':"VW Argentina",
       '9BW':"VW Brazil",'TMB':"Skoda",'TMP':"Skoda",'TM9':"Skoda",'VSS':"Seat"}

YEAR = {'N':"1992",'P':"1993",'R':"1994",'S':"1995",'T':"1996",'V':"1997",'W':"1998",'X':"1999",'Y':"2000",'1':"2001",
        '2':"2002",'3':"2003",'4':"2004",'5':"2005",'6':"2006",'7':"2007",'8':"2008",'9':"2009",'A':"2010",'B':"2011",
        'C':"2012",'D':"2013",'E':"2014",'F':"2015",'G':"2016",'H':"2017",'J':"2018",'K':"2019",'L':"2020",'M':"2021"}

MODEL = {'11':"Beetle (Brazilian, Mexican, Nigerian)",'13':"Scirocco 3",'14':"Caddy Mk 1 (European Golf 1 pickup)",'15':"Cabriolet (1980 Beetle, Golf 1)",
         '16':"Jetta 1 and 2 (early) or Beetle (2012-on)",'17':"Golf 1",'18':"Iltis",'19':"Golf 2 (early)",'1C':"New Beetle (US market)",'1E':"Golf 3 Cabriolet",
         '1F':"Eos",'1G':"Golf and Jetta 2 (late)",'1H':"Golf and Vento 3",'1J':"Golf and Bora 4",'1K':"Golf and Jetta 5, 6",'1T':"Touran",'1Y':"New Beetle Cabriolet",
         '24':"T3 Transporter Single/Double Cab Pickup",'25':"T3 Transporter Van, Kombi, Bus, Caravelle",'28':"LT Transporter 1",'2D':"LT Transporter 2",'2E':"Crafter",
         '2H':"Amarok",'2K':"Caddy, Caddy Maxi 3",'30':"Fox (US model ex-Brazil)",'31':"Passat 2",'32':"Santana sedan",'33':"Passat 2 Variant",'3A':"Passat 3, 4",
         '3B':"Passat 5",'3C':"Passat 6, Passat CC",'3D':"Phaeton",'50':"Corrado (early)",'53':"Scirocco 1 and 2",'5K':"Golf and Jetta 6",'5M':"Golf Plus",'5N':"Tiguan",
         '5Z':"Fox (Europe)",'60':"Corrado (late)",'6K':"Polo Classic, Variant 3",'6N':"Polo 3",'6R':"Polo 5",'6X':"Lupo",'70':"T4 Transporter Vans and Pickups",
         '74':"Taro",'7H':"T5 Transporter",'7L':"Touareg 1",'7M':"Sharan",'7P':"Touareg 2",'86':"Polo and Derby 1 and 2",'87':"Polo Coupe",'9C':"New Beetle",
         '9K':"Caddy 2 Van (ex-SEAT Ibiza)",'9N':"Polo 4",'9U':"Caddy 2 Pickup (ex-Skoda Felicia)",'AA':"Up!",'8Z':"A2",'8L':"A3 97-03",'8P':"A3 2003 on",
         '8E':"A4 01-08",'8K':"A4 2008 on",'8H':"A4 Cab",'8T':"A5",'4A':"A6 95-97",'4B':"A6 96-04",'4F':"A6 2004 on",'4D':"A8 94-03",'4E':"A8 2003 on",
         '4Z':"Allroad 00-05",'8R':"Q5",'4L':"Q7",'42':"R8",'8N':"TT 99-06",'8J':"TT 2006 on",'5J':"Fabia 07 on or: Roomster",'6Y':"Fabia 99-07",'6U':"Felicia 95-01",
         '1U':"Octavia 96-03",'1Z':"Octavia 04 on",'3U':"Superb 0108",'3T':"Superb 08 on",'5P':"Altea or: Toledo 2004 on",'6H':"Arosa",'3R':"Exeo",'6L':"Ibiza 02-08",
         '6J':"Ibiza 08 on",'1P':"Leon 05 on",'1M':"Leon 99-05/Toledo 98-04",'1L':"Toledo 91-98",}

ORIGIN = {'A':"Ingolstadt, Germany",'B':"Brussels, Belgium",'D':"Bratislave, Slovakia",'E':"Emden, Germany",'G':"Gratz, Germany",'H':"Hannover, Germany",
          'K':"Osnabrueck, Germany",'M':"Mexico",'N':"Neckarsulm, Germany; Mlada Boleslav",'P':"Mosel, Germany",'R':"Martorell, Spain",'S':"Stuttgart, Germany",
          'T':"Kvasiny, Czech",'V':"Palmela, Portugal",'W':"Wolfsburg, Germany",'X':"Posnan, Poland",'Y':"Pamplona, Spain",'Z':"Pacheco, Argentina",'1':"Gyor, Hungary",'8':"Dresden; Vrchlabi"}

class ecueeprom:
    bin_type =  "ECU_eeprom"
    noFixCheckSum = False
    noCheckSumPages = [0x00,0x11,0x12,0x13,0x14]
    backupPage = [0x8,0xA,0xC,0xE,0x10,0x1F]
    write = False #set to write out eeprom after modification

    size = 0
    data = []

    immover = 3
    vin = ""
    vindetail = ""
    immoid = ""
    skc = ""
    clustercode = "" #0x34-0x3A
    softcoding = "" #0x7A 0x7B
    immoval = []

    tunertag = ""
    flashattemptcount = 0
    flashsuccessfulcount = 0

    dtc = None
    immo = None #True indicates immo is on, False is off, None is error
    csum = True #True indicates checksum is ok, false indicates checksum is wrong
    R32 = False #True indiciates that this is a R32 bin 1024kb bin with FF padding



    def __init__(self,ndata):
        if DEBUG: print("Parsing as ECU eeprom")
        self.data = ndata
        self.parse()

    def parse(self):
        R32 = False

        #try to work out of this is immo2, immo3 or immo3r32
        tmpval = self.data[0x00][0x00]
        for bite in range(0x01,0x05):
            if self.data[0x00][bite] != tmpval:
                #first 5 bytes are not the same, assume immo2 (or some new immo 3)
                self.immover = 2

        if self.immover == 3:
            if self.data[0x00][0x00] == 0x30:
                print("Bin starts 30 30 30 30 30 - is this a 1024kb R32 bin?")
                #R32 = True

        #set length
        self.size = 0
        for page in self.data:
            self.size += len(page)

        #Parse R32 1kb bins
        if self.size == 1024 or R32 == True:
            print ("Found 1024b bin - parsing as a R32 bin - experimental")
            for page in range(0x20,0x40):
                for bite in self.data[page]:
                    if bite != 0xFF:
                        R32=False
            if R32:
                print( "The last 512bytes are padded with 0xFF, this appears to be an R32 bin")
                self.R32 = True
                #add the padding bytes to nochecksumpages
                self.noCheckSumPages.append(0x1C)
                self.noCheckSumPages.append(0x1D)
                for page in range(0x20,0x40):
                    self.noCheckSumPages.append(page)
            else:
                print ("ERROR: 1024byte file detected, but the last 512bytes are not all padded with 0xFF, this file is may be a corupt dump, a cluster dump or something other than an eeprom dump, open it with a hex editor - if this is a valid eeprom please post the file and vehicle info on the thread for this tool")


        #get SKC
        hexskc = "%0.2x%0.2x" % (self.data[0x3][0x3],self.data[0x3][0x2])
        self.skc = "0%0.4d" % int(hexskc,16)

        #get death DTC
        if self.data[0x1][0xC] + self.data[0x2][0xC] > 0:
            self.dtc = "%0.2X %0.2X" % (self.data[0x1][0xC],self.data[0x2][0xC])

        #get immo
        immo1 = self.data[0x1][0x2]
        immo2 = self.data[0x2][0x2]
        if immo1 == immo2:
            #if byte 12 and byte 22 are not set the same, leave self.immo None to indicate error
            if immo1 == 0x01:
                self.immo = True
            elif immo1 == 0x02:
                self.immo = False

        #if byte 12 and 22 are not set to 0x01 or 0x02, fall through to indicate error, set immoval to the actual value for display
        self.immoval.append(immo1)
        self.immoval.append(immo2)

        #get cluster code
        self.clustercode = ""
        for i in range(0x4, 0xB):
            self.clustercode += "%0.2X " % self.data[0x3][i]

        #get VIN
        vinstring = bytearray()
        for bite in range (0x05,0xA):
            vinstring.append(self.data[0xB][bite])
        for bite in range (0x00,0xC):
            vinstring.append(self.data[0xD][bite])
        try:
            self.vin = vinstring.decode('ascii')
        except:
            print ("WARNING: cannot decode VIN, try setting VIN to fix")

        self.vindetail = parsevin(self.vin)
        #get softcoding
        hexscing = "%0.2x%0.2x" % (self.data[0x7][0xB],self.data[0x7][0xA])
        self.softcoding = "%0.4d" % int(hexscing,16)

        #get Immo ID
        immostring = bytearray()
        immostring.append(self.data[0xD][0xC])
        for bite in range (0x00,0xD):
            immostring.append(self.data[0xF][bite])
        try:
            self.immoid = immostring.decode('ascii')
        except:
            print ("WARNING: cannot decode ImmmoID")

        #get flasher tag
        try:
            self.tunertag = self.data[0x1E][0x2:0x8].decode('ascii')
        except:
            pass

        #get flash programming counts
        self.flashsuccessfulcount = self.data[0x1E][0x9]
        self.flashattemptcount = self.data[0x1E][0xA]


        #validate checksum
        self.validateChecksum()

    def validateChecksum(self):
        try:
            if DEBUG: print( "Validating Checksum")
            minus = 1
            self.csum = True
            #FFFF - (page number - 1) - sum(first 14 bytes)
            for pageno in range(0x00,len(self.data)):
                #skip pages without a checksum
                if pageno in self.noCheckSumPages:
                    if DEBUG: print ("Skipping nochecksumpage: %0.2X", pageno)
                    continue
                #if this is a backup page, use the previous page's no to calculate the checksum
                if pageno in self.backupPage:
                    minus = 2
                else:
                    minus = 1
                bytesum = 0x00
                for i in range (0, 14):
                    bytesum += self.data[pageno][i]
                calcsum = 0xFFFF - (pageno - minus) - bytesum
                #get checksum for this page from the bin
                savedsum = "%0.2X%0.2X" % (self.data[pageno][0x0F],self.data[pageno][0x0E])
                if calcsum != int(savedsum,16):
                    self.csum = False
                    if DEBUG: print ("Checksum Error page: %0.2X", pageno)
                else:
                    if DEBUG: print ("Checksum OK page: %0.2X", pageno)
        except:
            print ("WARNING: Cannot validate checksum, possible invalid input")
            self.csum = False

        if DEBUG:
            if self.csum == True:
                print ("Checksum OK")
            else:
                print ("Checksum error or validation failure")

    def fixChecksum(self):
        """
        Fixes the checksum and sets the backup rows
        """

        #if the nfc flag is set (from the command line), return without doing checksum/backups
        if self.noFixCheckSum:
            print ("- Skipping page backup and checksum correction")
            return

        print ("- Setting backup pages")
        #do backups
        for pageno in range(0x00,len(self.data)):
            if pageno in self.backupPage:
                self.data[pageno] = self.data[pageno - 1]

        print ("- Correcting checksums")
        #do checksums
        minus = 1
        self.csum = True
        #FFFF - (page number - 1) - sum(first 14 bytes)
        for pageno in range(0x00,len(self.data)):

            #skip pages without a checksum
            if pageno in self.noCheckSumPages:
                continue
            #if this is a backup page, use the previous page's no to calculate the checksum
            if pageno in self.backupPage:
                minus = 2
            else:
                minus = 1
            bytesum = 0x00
            for i in range (0, 14):
                bytesum += self.data[pageno][i]
            calcsum = 0xFFFF - (pageno - minus) - bytesum
            self.data[pageno][0x0F] = (calcsum / 256)
            self.data[pageno][0x0E] = (calcsum % 256)

    def getChecksum(self):
        if self.csum:
            return "OK"
        else:
            return "Invalid Checksum"

    def writebin(self,outputfile):
        try:
            self.fixChecksum()
        except:
            print ("Warning: Error correcting checksum, checksums in output file may be invalid")
        outputdata = bytearray()
        for row in self.data:
            for bite in row:
                outputdata.append(bite)

        print ("")
        if DEBUG: print ("Writing %dkb ECU eeprom bin to: %s", (len(outputdata),outputfile))
        try:
            with open(outputfile,'wb') as fp:
                fp.write(outputdata)
        except:
            print ("Error: Could not open output file, exiting")
            exit(1)
        print ("- Write Successful")

    def printStatus(self):
        print ("EEPROM Status:")
        print ("- Type: %s", self.bin_type)
        print ("- Version: Immo%d", self.immover)
        if self.getVINDetail() != "":
            print ("- VIN: %s (%s)", (self.getVIN(),self.getVINDetail()))
        else:
            print ("- VIN: %s", (self.getVIN()))
        print ("- SKC: " + self.getSKC())
        print ("- Immobiliser: " + self.getImmo())
        print ("- Checksum: " + self.getChecksum())
        print ("- Size: " + self.getLength())
        print ("- Cluster Code: " + self.getClusterCode())
        print ("- P0601 DTC: " + self.getDTC())
        print ("- Immo ID: " + self.getImmoID())
        print ("- Softcoding ID: " + self.getSoftcoding())
        print ("- Tuner Tag: " + self.getTunerTag())
        print ("- Flash Programming (successful): %d", self.flashsuccessfulcount)
        print ("- Flash Programming (attempts): %d", self.flashattemptcount)
        print ("")

    def getLength(self):
        if self.size == 512:
            return "%dbytes" % self.size
        elif self.size/1024 == 512:
            print ("Size: 512kb - is this a flash bin not an eeprom bin?")
            print ("Exiting")
            exit(1)
        elif self.size/1024 == 1024:
            print ("Size: 1024kb - is this a flash bin not an eeprom bin?")
            print ("Exiting")
            exit(1)
        else:
            return "%dbytes - 512bytes expected, check this is a eeprom bin" % self.size

    def getTunerTag(self):
        if self.tunertag == "":
            return "Not Set"
        else:
            return self.tunertag

    def getSoftcoding(self):
        return self.softcoding

    def getSKC(self):
        return self.skc

    def getClusterCode(self):
        return self.clustercode

    def getDTC(self):
        if self.dtc != None:
            return "set to " + self.dtc
        else:
            return "not set"

    def clearDTC(self):
        self.data[0x1c] = 0x00
        self.data[0x2c] = 0x00
        self.parse()
        self.write = True

    def getImmo(self):
        """
        Get the current setting for the immobiliser, returns text string to indicate status
        """
        if self.immo is True:
            return "On"
        elif self.immo is False:
            return "Off"
        else:
            return "Error, set Immo - Current values: 0x12 = 0x%0.2X, 0x22 = 0x%0.2X" % (self.immoval[0],self.immoval[1])

    def setImmo(self,setting):
        """
        Set the immo on or off
        """
        if setting is True:
            print ("Setting Immobiliser: On")
            if self.immo is True:
                print ("- Immobiliser already set On")
                return
            #Set immobiliser on
            self.data[0x1][0x2] = 0x01
            self.data[0x2][0x2] = 0x01
            print ("- Immobiliser On")

        else:
            print ("Setting Immobiliser: Off")
            if self.immo is False:
                print ("- Immobiliser already set Off")
                return
            #Set immo off
            self.data[0x1][0x2] = 0x02
            self.data[0x2][0x2] = 0x02
            print ("- Immobiliser Off")

        self.parse()
        self.write = True

    def getVIN(self):
        return self.vin

    def getVINDetail(self):
        return self.vindetail


    def setVIN(self,newvin):
        if len(newvin) != 17:
            print ("ERROR: VIN number must be 17 characters")
            exit(1)
        print ("Setting VIN to %s", newvin)
        bavin = bytearray(newvin,'ascii')

        self.data[0xB][0x05:0xA] = bavin[0x00:0x05]
        del bavin[0:5]
        self.data[0xD][0x00:0xC] = bavin
        try:
            a = 1
        except:
            print ("ERROR: Could not set VIN")
            exit(1)
        self.parse()
        self.write = True

    def getImmoID(self):
        return self.immoid

class clustereeprom:
    bin_type = "Cluster"
    noCheckSumPages = [0x10000]
    backupPage = [0x10000]
    write = False #set to write out eeprom after modification

    size = 0
    data = []

    vin = ""
    vindetail = ""
    immoid = ""
    skc = ""
    clustercode = "" #0x34-0x3A


    def __init__(self,ndata):
        if DEBUG: print ("Parsing as cluster eeprom")
        self.data = ndata
        self.parse()

    def parse(self):

        #set length
        self.size = 0
        for page in self.data:
            self.size += len(page)
            if len(page) > 16: print ("ERROR, long row: %d ", len(page))
            elif len(page) < 16: print ("ERROR, short row: %d " % len(page))

        #get SKC
        hexskc = "%0.2x%0.2x" % (self.data[0xC][0xD],self.data[0xC][0xC])
        self.skc = "0%d" % int(hexskc,16)

        #get cluster code
        cc1 = self.data[0x7][0x2:0x9]
        cc2 = self.data[0x7][0xA:0x18]
        cc2.append(self.data[0x8][0x0])
        cc3 = self.data[0x8][0x2:0x9]

        if cc1 != cc2:
            print ("WARNING: Cluster Code Block 1 and 2 do not match, this may indicate an error in the file, or a format not supported by this tool")
        if cc1 != cc3:
            print ("WARNING: Cluster Code Block 1 and 3 do not match, this may indicate an error in the file, or a format not supported by this tool")
        if cc2 != cc3:
            print ("WARNING: Cluster Code Block 2 and 3 do not match, this may indicate an error in the file, or a format not supported by this tool")


        self.clustercode = ""
        for i in range(0x2, 0x9):
            self.clustercode += "%0.2X " % self.data[0x7][i]

        #get VIN
        vinstring = bytearray()
        for bite in range (0x02,0x10):
            vinstring.append(self.data[0xD][bite])
        for bite in range (0x00,0x03):
            vinstring.append(self.data[0xE][bite])
        try:
            self.vin = vinstring.decode('ascii')
        except:
            print ("WARNING: cannot decode VIN, try setting VIN to fix")

        self.vindetail = parsevin(self.vin)


        #get Immo ID
        immostring = bytearray()
        for bite in range (0x02,0x0F):
            immostring.append(self.data[0xA][bite])
        try:
            self.immoid = immostring.decode('ascii')
        except:
            print ("WARNING: cannot decode ImmmoID")

    def writebin(self,outputfile):
        outputdata = bytearray()
        for row in self.data:
            count = 0
            for bite in row:
                count += 1
                outputdata.append(bite)
        print ("Writing %dkb cluster eeprom bin to: %s", (len(outputdata),outputfile))
        try:
            with open(outputfile,'wb') as fp:
                fp.write(outputdata)
        except:
            print ("Error: Could not open output file, exiting")
            exit(1)
        print ("- Write Successful")
        print ("\nThis tool cannot set checksum for cluster bins, so you must force the cluster to reset the checksum by using VCDS to update the cluster softcoding (setting it to the same value will force the update)")

    def printStatus(self):
        print ("EEPROM Status:")
        print ("- Type: %s", self.bin_type)
        if self.getVINDetail() != "":
            print ("- VIN: %s (%s)", (self.getVIN(),self.getVINDetail()))
        else:
            print ("- VIN: %s", (self.getVIN()))
        print ("- SKC: " + self.getSKC())
        print ("- Cluster Code: " + self.getClusterCode())
        print ("- Immo ID: " + self.getImmoID())
        print ("")

    def getLength(self):
        if self.size == 2048:
            return "%dbytes" % self.size
        elif self.size/1024 == 512:
            print ("Size: 512kb - is this a flash bin not an eeprom bin?")
            print ("Exiting")
            exit(1)
        elif self.size/1024 == 1024:
            print ("Size: 1024kb - is this a flash bin not an eeprom bin?")
            print ("Exiting")
            exit(1)
        else:
            return "%dbytes - 2048bytes expected, check this is an ecu eeprom bin" % self.size

    def getSKC(self):
        return self.skc

    def setSKC(self,skc):
        #sanity check
        if len(skc) > 5 or len(skc) < 4:
            print ("ERROR: SKC must be in format 0xxxx or xxxx, where x is in range 0-9")
            exit(1)
        try:
            tmp = int(skc)
        except:
            print ("ERROR: SKC must be in format 0xxxx or xxxx, where x is in range 0-9")
            exit(1)
        if len(skc) == 5 and skc[0] != "0":
            print ("ERROR: SKC must be in format 0xxxx or xxxx, where x is in range 0-9")
            exit(1)

        if len(skc) == 5:
            tskc = "%0.4x" % int(skc[0:])
        else:
            tskc = "%0.4x" % int(skc)

        print ("Setting SKC to %s", skc)
        self.data[0xC][0xC] = int(tskc[2:],16)
        self.data[0xC][0xD] = int(tskc[:2],16)
        self.data[0xC][0xE] = int(tskc[2:],16)
        self.data[0xC][0xF] = int(tskc[:2],16)
        self.data[0xD][0x0] = int(tskc[2:],16)
        self.data[0xD][0x1] = int(tskc[:2],16)


        self.parse()
        self.write = True


    def getClusterCode(self):
        return self.clustercode

    def setClusterCode(self,clustercode):

        bacc = bytearray(clustercode.replace(" ","").decode("hex"))
        self.data[0x7][2:9] = bacc
        self.data[0x7][0xA:18] = bacc[0:6]
        self.data[0x8][0x0] = bacc[6]
        self.data[0x8][2:9] = bacc

        self.parse()
        self.write = True



    def getVIN(self):
        return self.vin

    def getVINDetail(self):
        return self.vindetail

    def setVIN(self,newvin):
        if DEBUG: print ("Trying to set vin to %s (%s)", (newvin,parsevin(newvin)))
        try:
            if len(newvin) != 17:
                print ("ERROR: VIN number must be 17 characters")
                exit(1)
            print ("Setting VIN to %s", newvin)
            bavin = bytearray(newvin,'ascii')

            self.data[0xD][0x02:0x10] = bavin[0x00:0x0E]
            del bavin[0x0:0xE]
            self.data[0xE][0x00:0x03] = bavin
        except:
            print ("ERROR: Could not set VIN")
            exit(1)
        self.parse()
        self.write = True

        if DEBUG: print ("Set vin to %s", self.getVIN())

    def getImmoID(self):
        return self.immoid

    def setImmoID(self,immoid):
        if DEBUG: print ("Trying to set immo ID to %s", immoid)
        try:
            if len(immoid) != 14:
                print ("ERROR: VIN number must be 14 characters")
                exit(1)
            print ("Setting Immo ID to %s", immoid)
            baii = bytearray(immoid,'ascii')

            self.data[0xA][0x02:0x10] = baii[0x00:0x0E]
            self.data[0xB][:0xE] = baii[0x00:0x0E]
            self.data[0xB][0xE:0x10] = baii[0x00:0x02]
            self.data[0xC][:0xC] = baii[0x02:0x0E]
        except:
            print ("ERROR: Could not set Immo ID")
            exit(1)
        self.parse()
        self.write = True

        if DEBUG: print ("Set immo ID to %s", self.getImmoID())

    def pair(self,ecueepromfile):
        ecueeprombin = ecueeprom(readbin(ecueepromfile))

        #Set Vin, Immo ID, Cluster Code
        self.setVIN(ecueeprombin.getVIN())
        self.setImmoID(ecueeprombin.getImmoID())
        self.setClusterCode(ecueeprombin.getClusterCode())
        self.setSKC(ecueeprombin.getSKC())

        print ("")
        print ("Cluster updated to:")
        self.printStatus()
        self.write = True




def readbin(filename):
    data = []
    readmore = True
    onlyread512k = False
    with open(filename, "rb") as f:
        while readmore:
            page = f.read(16)
            if page:
                data.append(bytearray(page))
            else:
                break
            if onlyread512k:
                if len(data) == 32:
                    readmore = False
    if DEBUG: print ("Read in %d 16 byte rows - %dbytes total", (len(data),len(data)*16))
    print ("Read in %dbytes", (len(data)*16))
    return data


def parsevin(vinin):
    vinstring = ""
    try:
        #attempt to parse the vin
        vinstring += WMI[vinin[0:3]]
        vinstring += " " + YEAR[vinin[9]]
        vinstring += " - " + MODEL[vinin[6:8]]
        vinstring += ", " + ORIGIN[vinin[10]]
    except:
        pass
    return vinstring


def main():
    if WARN: print ("95040 Eeprom Tool - " + str(VERSION) + "- No warranty implied or given, manually verify all changes before saving eeprom to ECU, this tool could cause permenent damage to ECU and prevent vehicle running\n")
    parser = argparse.ArgumentParser(description='95040 Eeprom Tool ' + str(VERSION) + ' View/Modify me7.5 eeprom files')
    parser.add_argument('--in',dest='infile',help='Input eeprom bin',required=True)
    parser.add_argument('--out',dest='outfile',help='File to save eeprom to (must be supplied if changing Immo/VIN)')
    parser.add_argument('--status',dest='status',action='store_const',const=True, help='View information in eeprom, default if no other options are specified')
    parser.add_argument('--immo',dest='immo',help='Immobiliser on/off ')
    parser.add_argument('--vin',dest='vin',help='New VIN')
    parser.add_argument('--skc',dest='skc',help='New SKC')
    parser.add_argument('--cc',dest='cc',help='New Cluster Code (hex, without spaces')
    parser.add_argument('--ii',dest='ii',help='New Immo ID (hex, without spaces')
    parser.add_argument('--pair',dest='pair',help='Pair the cluster specified with the --in with a ecu eeprom given after pair')
    parser.add_argument('--fixcs',dest='fixcs',action='store_const',const=True, help='Fix checksum (default when changing Immo/VIN unless --nofixcs is specified')
    parser.add_argument('--nofixcs',dest='nofixcs',action='store_const',const=True, help='Do not correct checksum when writing out file')
    parser.add_argument('--cluster',dest='cluster',action='store_const',const=True, help='Parse a cluster bin (default is ecu bin) - override eeprom type guessing')
    parser.add_argument('--force',dest='force',action='store_const',const=True, help='Prevent the tool from guessing eeprom type')

    if DEBUG:
        print ("Debug mode active")
    #create namespace for args
    args = argparse.Namespace()

    data = ""
    eeprombin = ""
    exitnow = False

    if len(sys.argv) > 2 or len(sys.argv) == 1 or sys.argv[1][0] == '-':
        args = parser.parse_args()
    else:
        #Handle case for <program> <input file>
        args.infile = sys.argv[1]
        args.status = True
        args.outfile = False
        args.cluster = False
        args.force = False
        exitnow = True

    if args.infile:
        try:
            data = readbin(args.infile)
        except:
            print ("ERROR: Could not open input file - %s", args.infile)
            sys.exit(1)
    else:
        print ("Error: No Input file")
        sys.exit(1)

    #Attempt to autodetect if this is a cluster or ecu bin, based on size
    if not args.force:
        if not args.cluster:
            if (len(data) *16) == 2048:
                print ("Detected 2kb bin, parsing as a cluster eeprom (prevent this guessing by using --force)")
                args.cluster = True

    #Load and parse eeprom
    if not args.cluster:
        eeprombin = ecueeprom(data)
    else:
        eeprombin = clustereeprom(data)

    if not args.outfile:
        args.status = True

    if args.status:
        eeprombin.printStatus()
        if exitnow:
            sys.exit(0)

    if args.fixcs or args.immo or args.vin:
        if not args.outfile:
            print ("ERROR: Output file must be supplied when correcting checksum, setting immo or changing VIN")
            sys.exit(1)

    if args.nofixcs:
        eeprombin.noFixCheckSum = True

    if args.fixcs:
        eeprombin.write = True

    if args.immo:
        if args.cluster:
            print ("ERROR: No immo to set in cluster eeprom")
            exit(1)
        if args.immo.lower() == 'off':
            eeprombin.setImmo(False)
        elif args.immo.lower() == 'on':
            eeprombin.setImmo(True)

    if args.vin:
        eeprombin.setVIN(args.vin)

    if args.skc:
        if not args.cluster:
            print ("Not Yet Supported for ECU Bins")
        eeprombin.setSKC(args.skc)

    if args.cc:
        if not args.cluster:
            print ("Not Yet Supported for ECU Bins")
        eeprombin.setClusterCode(args.cc)

    if args.ii:
        if not args.cluster:
            print ("Not Yet Supported for ECU Bins")
        eeprombin.setImmoID(args.ii)

    if args.pair:
        eeprombin.pair(args.pair)

    if eeprombin.write:
        eeprombin.writebin(args.outfile)

    sys.exit(0)




#run main :)
if __name__ == "__main__":
    main()
