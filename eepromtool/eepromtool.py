import logging

class eeprom:
    def readbin(filename):
        logging.warn("Loading eeprom - %s" % filename)
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
        logging.debug("Read in %d 16 byte rows - %dbytes total" % (len(data),len(data)*16))
        logging.info("Read in %dbytes" % (len(data)*16))
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

