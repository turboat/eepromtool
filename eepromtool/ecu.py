import logging
from .eepromtool import eeprom

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
        logging.warn("Parsing as ECU eeprom")
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
                logging.info("Bin starts 30 30 30 30 30 - is this a 1024kb R32 bin?")
                #R32 = True

        #set length
        self.size = 0
        for page in self.data:
            self.size += len(page)

        #Parse R32 1kb bins
        if self.size == 1024 or R32 == True:
            logging.info("Found 1024b bin - parsing as a R32 bin - experimental")
            for page in range(0x20,0x40):
                for bite in self.data[page]:
                    if bite != 0xFF:
                        R32=False
            if R32:
                logging.info("The last 512bytes are padded with 0xFF, this appears to be an R32 bin")
                self.R32 = True
                #add the padding bytes to nochecksumpages
                self.noCheckSumPages.append(0x1C)
                self.noCheckSumPages.append(0x1D)
                for page in range(0x20,0x40):
                    self.noCheckSumPages.append(page)
            else:
                logging.error("ERROR: 1024byte file detected, but the last 512bytes are not all padded with 0xFF, this file is may be a corupt dump, a cluster dump or something other than an eeprom dump, open it with a hex editor - if this is a valid eeprom please post the file and vehicle info on the thread for this tool")


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
            logging.warn("WARNING: cannot decode VIN, try setting VIN to fix")

        self.vindetail = eeprom.parsevin(self.vin)
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
            logging.warn("WARNING: cannot decode ImmmoID")

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
            logging.debug("Validating Checksum")
            minus = 1
            self.csum = True
            #FFFF - (page number - 1) - sum(first 14 bytes)
            for pageno in range(0x00,len(self.data)):
                #skip pages without a checksum
                if pageno in self.noCheckSumPages:
                    logging.debug("Skipping nochecksumpage: %0.2X" % pageno)
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
                    logging.debug("Checksum Error page: %0.2X" % pageno)
                else:
                    logging.debug("Checksum OK page: %0.2X" % pageno)
        except:
            logging.warn("WARNING: Cannot validate checksum, possible invalid input")
            self.csum = False

        if self.csum == True:
            logging.debug("Checksum OK")
        else:
            logging.debug("Checksum error or validation failure")

    def fixChecksum(self):
        """
        Fixes the checksum and sets the backup rows
        """

        #if the nfc flag is set (from the command line), return without doing checksum/backups
        if self.noFixCheckSum:
            logging.info("- Skipping page backup and checksum correction")
            return

        logging.info("- Setting backup pages")
        #do backups
        for pageno in range(0x00,len(self.data)):
            if pageno in self.backupPage:
                self.data[pageno] = self.data[pageno - 1]

        logging.info("- Correcting checksums")
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
            logging.warn("Warning: Error correcting checksum, checksums in output file may be invalid")
        outputdata = bytearray()
        for row in self.data:
            for bite in row:
                outputdata.append(bite)

        print("")
        logging.debug("Writing %dkb ECU eeprom bin to: %s" % (len(outputdata),outputfile))
        try:
            with open(outputfile,'wb') as fp:
                fp.write(outputdata)
        except:
            logging.error("Error: Could not open output file, exiting")
            exit(1)
        logging.info("- Write Successful")

    def printStatus(self):
        logging.info("EEPROM Status:")
        logging.info("- Type: %s" % self.bin_type)
        logging.info("- Version: Immo%d" % self.immover)
        if self.getVINDetail() is not "":
            logging.info("- VIN: %s (%s)" % (self.getVIN(),self.getVINDetail()))
        else:
            logging.info("- VIN: %s" % (self.getVIN()))
        logging.info("- SKC: " + self.getSKC())
        logging.info("- Immobiliser: " + self.getImmo())
        logging.info("- Checksum: " + self.getChecksum())
        logging.info("- Size: " + self.getLength())
        logging.info("- Cluster Code: " + self.getClusterCode())
        logging.info("- P0601 DTC: " + self.getDTC())
        logging.info("- Immo ID: " + self.getImmoID())
        logging.info("- Softcoding ID: " + self.getSoftcoding())
        logging.info("- Tuner Tag: " + self.getTunerTag())
        logging.info("- Flash Programming (successful): %d" % self.flashsuccessfulcount)
        logging.info("- Flash Programming (attempts): %d" % self.flashattemptcount)
        logging.info("")

    def getLength(self):
        if self.size == 512:
            return "%dbytes" % self.size
        elif self.size/1024 == 512:
            logging.warn("Size: 512kb - is this a flash bin not an eeprom bin?")
            logging.warn("Exiting")
            exit(1)
        elif self.size/1024 == 1024:
            logging.warn("Size: 1024kb - is this a flash bin not an eeprom bin?")
            logging.warn("Exiting")
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
        if self.dtc is not None:
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
            logging.info("Setting Immobiliser: On")
            if self.immo is True:
                logging.info("- Immobiliser already set On")
                return
            #Set immobiliser on
            self.data[0x1][0x2] = 0x01
            self.data[0x2][0x2] = 0x01
            logging.info("- Immobiliser On")

        else:
            logging.info("Setting Immobiliser: Off")
            if self.immo is False:
                logging.info("- Immobiliser already set Off")
                return
            #Set immo off
            self.data[0x1][0x2] = 0x02
            self.data[0x2][0x2] = 0x02
            logging.info("- Immobiliser Off")

        self.parse()
        self.write = True

    def getVIN(self):
        return self.vin

    def getVINDetail(self):
        return self.vindetail


    def setVIN(self,newvin):
        if len(newvin) is not 17:
            logging.error("ERROR: VIN number must be 17 characters")
            exit(1)
        logging.info("Setting VIN to %s" % newvin)
        bavin = bytearray(newvin,'ascii')

        self.data[0xB][0x05:0xA] = bavin[0x00:0x05]
        del bavin[0:5]
        self.data[0xD][0x00:0xC] = bavin
        try:
            a = 1
        except:
            logging.error("ERROR: Could not set VIN")
            exit(1)
        self.parse()
        self.write = True

    def getImmoID(self):
        return self.immoid
