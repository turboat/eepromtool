# 95040 Eepromtool

95040 Eepromtool is a tool for easily displaying information in bosch m7.5 ecu eeproms and coresponding custer eeproms. This tool was written for VAG 1.8t engines using immo 3, it may also work with other engines and versions, but has limited testing. Eepromtool does not offer facility to read/write to an ecu, it is soley for viewing and modifying files that you have already.

The most recent release can be found in https://github.com/turboat/eepromtool/releases/

## Usage
Eepromtool is a command line tool, either run using 'python eepromtool_04.py' or 'eepromtool_04.exe'. To simply display the info in a bin called INFILE, use:

`eepromtool_04.exe INFILE`

For example with an ecu eeprom:

```$ eepromtool_04.exe ecu.bin 
EEPROM Status:
- Type: ECU_eeprom
- Version: Immo3
- VIN: WAULC68E52A221040 (Audi 2002 - A4 01-08, Ingolstadt, Germany)
- SKC: 01256
- Immobiliser: On
- Checksum: OK
- Size: 512bytes
- Cluster Code: 98 8A 4E AB 77 D2 A2 
- P0601 DTC: not set
- Immo ID: AUZ6Z0C0185357
- Softcoding ID: 16701
- Tuner Tag: Not Set
- Flash Programming (successful): 0
- Flash Programming (attempts): 1```

With a cluster eeprom:

```$ eepromtool_04.exe cluster.bin 
Read in 2048bytes
Detected 2kb bin, parsing as a cluster eeprom (prevent this guessing by using --force)
EEPROM Status:
- Type: Cluster
- VIN: WVWZZZ1JZ4W115023 (VW 2004 - Golf and Bora 4, Wolfsburg, Germany)
- SKC: 01629
- Cluster Code: 2F 27 CE D8 89 6D 36 
- Immo ID: VWZ7Z0C852208```
