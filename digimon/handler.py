# Author: Tristan Challener <challenert@gmail.com>
# Copyright: please don't steal this that is all

"""
Handler that stores all data to be written to the ROM.
"""

import digimon.data as data, digimon.util as util
import digimon.patch_registry as patch_registry
from digimon.models import Digimon, Item, Tech
import script.util as scrutil
from log.logger import Logger

import random, struct, sys, math
from shutil import copyfile


class DigimonWorldHandler:
    """
    Digimon World handler class.  Holds all data
    that can be modified and written out to the
    file.
    """

    #       Endianness                      Size (packed/not)
    # @     native                          native
    # =     native                          standard
    # <     little-endian                   standard
    # >     big-endian                      standard
    # !     network (= big-endian)          standard

    #       Type
    # x     pad byte
    # c     char
    # b     signed char
    # B     unsigned char
    # ?     _Bool
    # h     short
    # H     unsigned short
    # i     int
    # I     unsigned int
    # l     long
    # L     unsigned long
    # q     long long
    # Q     unsigned long long
    # f     float
    # d     double
    # s     char[]
    # p     char[]
    # P     void *

    def __init__( self, filename, logger: Logger, seed=None ):
        """
        Load ROM data into cache so that it can be read
        and manipulated.

        Keyword arguments:
        filename -- Name of file to read.
        seed -- Randomizer seed.
        """

        self.randomizedRequirements = False
        self.logger = logger

        self.patches = []

        self.randomseed = seed
        if( seed == None ):
            self.randomseed = random.randrange( sys.maxsize )
        random.seed( a=self.randomseed )

        #Advance the RNG when logging is set to race to
        #prevent cheating
        if( logger.verbose == 'race' ):
            random.randint( 0, 1 )

        self.inFilename = filename

        try:
            file = open( filename, 'r' + 'b' )
        except IOError:
            self.logger.fatalError( 'Error: input file could not be read (it probably doesn\'t exist)\nMake sure the filename and relative path in settings.ini \'Input\' are correct.' )

        with file:
            #------------------------------------------------------
            # Read in tech data
            #------------------------------------------------------

            self.logger.log( self.logger.getHeader( 'Read Tech Data' ) )

            #Read in full item data block
            data_read = util.readDataWithExclusions( file,
                                                     data.techDataBlockOffset,
                                                     data.techDataBlockSize,
                                                     data.techDataExclusionOffsets,
                                                     data.techDataExclusionSize )

            #Parse data block
            data_unpacked = util.unpackDataArray( data_read,
                                                  data.techDataFormat,
                                                  data.techDataBlockCount )

            #Store data in item objects
            self.techData = []
            for i, data_tuple in enumerate( data_unpacked ):
                self.techData.append( Tech( self, i, data_tuple ) )
                self.techData[ i ].setName( data.techs[ i ] )


            #------------------------------------------------------
            # Read in tech tier list
            #------------------------------------------------------

            #Read in tier list data block
            data_read = util.readDataWithExclusions( file,
                                                     data.techTierListBlockOffset,
                                                     data.techTierListBlockSize,
                                                     data.techTierListExclusionOffsets,
                                                     data.techTierListExclusionSize )

            #Parse data block
            data_unpacked = util.unpackDataArray( data_read,
                                                  data.techTierListFormat,
                                                  data.techTierListBlockCount )

            #Extract tiers for all techs
            for data_tuple in data_unpacked:
                for i, techID in enumerate( data_tuple ):
                    self.techData[ techID ].tier = i + 1


            #------------------------------------------------------
            # Read in tech learn chances (battle)
            #------------------------------------------------------

            #Read in tech learn chance data block
            data_read = util.readDataWithExclusions( file,
                                                     data.techLearnBlockOffset,
                                                     data.techLearnBlockSize,
                                                     data.techLearnExclusionOffsets,
                                                     data.techLearnExclusionSize )

            #Parse data block
            data_unpacked = util.unpackDataArray( data_read,
                                                  data.techLearnFormat,
                                                  data.techLearnBlockCount )

            #Extract learn chance for all learnable techs
            for techID, data_tuple in enumerate( data_unpacked ):
                self.techData[ techID ].learnChance = list( data_tuple )

            for tech in self.techData:
                self.logger.log( str( tech ) )


            #------------------------------------------------------
            # Read in tech learn chances (brain)
            #------------------------------------------------------
            
            #Read in brain learn chance data block
            data_read = util.readDataWithExclusions( file,
                                                     data.techBrainBlockOffset,
                                                     data.techBrainBlockSize,
                                                     data.techBrainExclusionOffsets,
                                                     data.techBrainExclusionSize )

            #Parse data block
            data_unpacked = util.unpackDataArray( data_read,
                                                  data.techLearnFormat,
                                                  data.techBrainBlockCount )

            #Create list, where index is tier and tuple is specialty number
            self.brainLearn = []
            for data_tuple in data_unpacked:
                self.brainLearn.append( list( data_tuple ) )

            self.logger.log( "Brain training learn chances:" )
            for index, learnRate in enumerate( self.brainLearn ):
                self.logger.log( "Tier " + str( index + 1 ) + ": " + str( learnRate ) )


            #------------------------------------------------------
            # Read in item data
            #------------------------------------------------------

            self.logger.log( self.logger.getHeader( 'Read Item Data' ) )

            #Read in full item data block
            data_read = util.readDataWithExclusions( file,
                                                     data.itemDataBlockOffset,
                                                     data.itemDataBlockSize,
                                                     data.itemDataExclusionOffsets,
                                                     data.itemDataExclusionSize )

            #Parse data block
            data_unpacked = util.unpackDataArray( data_read,
                                                  data.itemDataFormat,
                                                  data.itemDataBlockCount )

            #Store data in item objects
            self.itemData = []
            for i, data_tuple in enumerate( data_unpacked ):
                self.itemData.append( Item( self, i, data_tuple ) )
                self.logger.log( str( self.itemData[ i ] ) )
            
            self.itemData[125].price = 9999
            self.itemData[126].price = 5000
            self.itemData[127].price = 9999


            #------------------------------------------------------
            # Read in digimon data
            #------------------------------------------------------

            self.logger.log( self.logger.getHeader( 'Read Digimon Data' ) )

            #Read in full digimon stats data block
            data_read = util.readDataWithExclusions( file,
                                                     data.digimonDataBlockOffset,
                                                     data.digimonDataBlockSize,
                                                     data.digimonDataExclusionOffsets,
                                                     data.digimonDataExclusionSize )

            #Parse data block
            data_unpacked = util.unpackDataArray( data_read,
                                                  data.digimonDataFormat,
                                                  data.digimonDataBlockCount )

            #Store data in digimon objects
            self.digimonData = []
            for i, data_tuple in enumerate( data_unpacked ):
                self.digimonData.append( Digimon( self, i, data_tuple ) )
                self.logger.log( str( self.digimonData[ i ] ) + '\n' )


            #------------------------------------------------------
            # Read in evo data
            #------------------------------------------------------

            self.logger.log( self.logger.getHeader( 'Read Evolution Data' ) )

            #Read in evo to/from data block
            data_read = util.readDataWithExclusions( file,
                                                     data.evoToFromBlockOffset,
                                                     data.evoToFromBlockSize,
                                                     data.evoToFromExclusionOffsets,
                                                     data.evoToFromExclusionSize )

            #Parse data block
            data_unpacked = util.unpackDataArray( data_read,
                                                  data.evoToFromFormat,
                                                  data.evoToFromBlockCount )

            #Store data in digimon objects
            for i, data_tuple in enumerate( data_unpacked ):
                #Index from 1 because player (ID#0) does not have evo entries
                self.digimonData[ 1 + i ].setEvoData( data_tuple )
                self.logger.log( self.digimonData[ 1 + i ].evoData() + '\n' )


            self.logger.log( self.logger.getHeader( 'Read Evolution Stat Gain Data' ) )

            #Read in evo stats data block
            data_read = util.readDataWithExclusions( file,
                                                     data.evoStatsBlockOffset,
                                                     data.evoStatsBlockSize,
                                                     data.evoStatsExclusionOffsets,
                                                     data.evoStatsExclusionSize )

            #Parse data block
            data_unpacked = util.unpackDataArray( data_read,
                                                  data.evoStatsFormat,
                                                  data.evoStatsBlockCount )

            #Store data in digimon objects
            for i, data_tuple in enumerate( data_unpacked ):
                self.digimonData[ i ].setEvoStats( data_tuple )
                self.logger.log( self.digimonData[ i ].evoStatsToString() + '\n' )

            self.logger.log( self.logger.getHeader( 'Read Evolution Requirements Data' ) )

            #Read in evo requirements data block
            data_read = util.readDataWithExclusions( file,
                                                     data.evoReqsBlockOffset,
                                                     data.evoReqsBlockSize,
                                                     data.evoReqsExclusionOffsets,
                                                     data.evoReqsExclusionSize )

            #Parse data block
            data_unpacked = util.unpackDataArray( data_read,
                                                  data.evoReqsFormat,
                                                  data.evoReqsBlockCount )

            #Store data in digimon objects
            for i, data_tuple in enumerate( data_unpacked ):
                self.digimonData[ i ].setEvoReqs( data_tuple )
                self.logger.log( self.digimonData[ i ].evoReqsToString() + '\n' )


            #------------------------------------------------------
            # Read in starter data
            #------------------------------------------------------

            self.logger.log( self.logger.getHeader( 'Read Starter Data' ) )

            self.starterID = []
            self.starterTech = []
            self.starterTechSlot = []

            for i in [ 0, 1 ]:
                #Read in first starter digimon ID
                file.seek( data.starterSetDigimonOffset[ i ], 0 )
                self.starterID.append( struct.unpack( data.digimonIDFormat, file.read( 1 ) )[0] )
                self.logger.log( self.digimonData[ self.starterID[ i ] ].name )

                #Read in first starter learned tech ID
                file.seek( data.starterLearnTechOffset[ i ], 0 )
                self.starterTech.append( struct.unpack( data.techIDFormat, file.read( 1 ) )[0] )
                self.logger.log( '0x' + format( self.starterTech[ i ], '02x' ) + ' = tech ID' )

                #Read in first starter learned tech slot
                file.seek( data.starterEquipAnimOffset[ i ], 0 )
                self.starterTechSlot.append( util.animIDTechSlot( struct.unpack( data.animIDFormat, file.read( 1 ) )[0] ) )
                self.logger.log( '0x' + format( self.starterTechSlot[ i ], '02x' ) + ' = tech slot' )


            #------------------------------------------------------
            # Read in recruitment data
            #------------------------------------------------------

            self.logger.log( self.logger.getHeader( 'Read Recruitment Data' ) )

            self.recruitData = {}

            err = False
            for ( ofsts, names, trigger, digi ) in data.recruitOffsets:
                verifiedOfsts = []
                for ofst in ofsts:
                    file.seek( ofst, 0 )
                    value = struct.unpack( data.recruitFormat,
                                           file.read( struct.calcsize( data.recruitFormat ) ) )[0]
                    if( value != trigger ):
                        self.logger.logError( 'Error: Looking for recruit trigger check, found incorrect value: ' + str( value ) + ' @ ' + format( ofst, '08x' ) )
                        err = True
                    else:
                        verifiedOfsts.append( ofst )

                for nameOfst in names:
                    file.seek( nameOfst, 0 )
                    name = scrutil.encode( self.getDigimonName( digi ) )
                    nameInFile = file.read( len( name ) )

                    if( name != nameInFile ):
                        self.logger.logError( 'Error: Looking for recruit' + self.getDigimonName( digi ) +
                                              ', found incorrect value: ' + scrutil.decode( nameInFile ) + 
                                              ' @ ' + format( nameOfst, '08x' ) )
                        err = True

                self.recruitData[ trigger ] = ( tuple( verifiedOfsts ), digi, names )

            if( not err ):
                self.logger.log( 'All recruitment check values verified.' )


            #------------------------------------------------------
            # Read in special evolution data
            #------------------------------------------------------

            self.logger.log( self.logger.getHeader( 'Read Special Evolution Data' ) )

            self.specEvos = {}

            err = False
            for ofsts, checkVal, fromVal in data.specEvoOffsets:
                for ofst in ofsts:
                    file.seek( ofst, 0 )
                    id = struct.unpack( data.specEvoFormat,
                                        file.read( struct.calcsize( data.specEvoFormat ) ) )[0]
                    if( id != checkVal ):
                        self.logger.logError( 'Error: Looking for spec evo, found incorrect value: ' + str( id ) + ' @ ' + format( ofst, '08x' ) )
                        err = True

                self.specEvos[ ofsts ] = ( checkVal, fromVal )

            if( not err ):
                self.logger.log( 'All special evolutions verified.' )


            #------------------------------------------------------
            # Read in chest item data
            #------------------------------------------------------

            self.logger.log( self.logger.getHeader( 'Read Chest Item Data' ) )

            self.chestItems = {}

            for ofst in data.chestItemOffsets:
                file.seek( ofst, 0 )
                cmd, item = struct.unpack( data.chestItemFormat,
                                           file.read( struct.calcsize( data.chestItemFormat ) ) )
                if( cmd != scrutil.spawnChest ):
                    self.logger.logError( 'Error: Looking for chest item, found incorrect command: ' + str( cmd ) + ' @ ' + format( ofst, '08x' ) )
                else:
                    self.chestItems[ ofst ] = item

            for item in self.chestItems.values():
                self.logger.log( 'Chest contains: \'' + self.itemData[ item ].name + '\'' )

            #------------------------------------------------------
            # Read in map item spawn data
            #------------------------------------------------------

            self.logger.log( self.logger.getHeader( 'Read Map Item Data' ) )

            self.mapItems = {}

            for ofst in data.mapItemOffsets:
                file.seek( ofst, 0 )
                cmd, item = struct.unpack( data.mapItemFormat,
                                           file.read( struct.calcsize( data.mapItemFormat ) ) )
                if( cmd != scrutil.spawnItem ):
                    self.logger.logError( 'Error: Looking for map item, found incorrect command: ' + str( cmd ) + ' @ ' + format( ofst, '08x' ) )
                else:
                    self.logger.log( ' \'' + self.itemData[ item ].name + '\' spawns on the map.' )
                    self.mapItems[ ofst ] = item


            #------------------------------------------------------
            # Read in Tokomon item data
            #------------------------------------------------------

            self.logger.log( self.logger.getHeader( 'Read Tokomon Item Data' ) )

            self.tokoItems = {}

            for ofst in data.tokoItemOffsets:
                file.seek( ofst, 0 )
                cmd, item, count = struct.unpack( data.tokoItemFormat,
                                                  file.read( struct.calcsize( data.tokoItemFormat ) ) )
                if( cmd != scrutil.giveItem ):
                    self.logger.logError( 'Error: Looking for Tokomon item, found incorrect command: ' + str( cmd ) + ' @ ' + format( ofst, '08x' ) )
                else:
                    self.tokoItems[ ofst ] = ( item, count )

            for ( item, count ) in self.tokoItems.values():
                self.logger.log( 'Tokomon gives: ' + str( count ) + 'x \'' + self.itemData[ item ].name + '\'' )


            #------------------------------------------------------
            # Read in tech gift data
            #------------------------------------------------------

            self.logger.log( self.logger.getHeader( 'Read Tech Gift Data' ) )

            self.techGifts = {}

            for i, ofst in enumerate( data.learnMoveOffsets ):
                file.seek( ofst, 0 )
                cmd, tech = struct.unpack( data.learnMoveFormat,
                                           file.read( struct.calcsize( data.learnMoveFormat ) ) )
                if( cmd != scrutil.learnMove ):
                    self.logger.logError( 'Error: Looking for tech learning gift, found incorrect command: ' + str( cmd ) + ' @ ' + format( ofst, '08x' ) )
                else:
                    self.techGifts[ ( ofst, data.checkMoveOffsets[ i ] ) ] = tech

            for tech in self.techGifts.values():
                self.logger.log( 'Tech gift: ' + str( count ) + 'x \'' + self.getTechName( tech ) + '\'' )


            #------------------------------------------------------
            # Read in jukebox track names
            #------------------------------------------------------
            #Read in tier list data block
            self.trackNames = util.readDataWithExclusions( file,
                                                           data.trackNameBlockOffset,
                                                           data.trackNameBlockSize,
                                                           data.trackNameExclusionOffsets,
                                                           data.trackNameExclusionSize )


    def write( self, filename ):
        """
        Write all ROM data back to binary file.

        Keyword arguments:
        filename -- Output file name.
        """

        #If we have a different destination file, create a copy to edit
        if( self.inFilename != filename ):
            copyfile( self.inFilename, filename )

        try:
            file = open( filename, 'r+' + 'b' )
        except IOError:
            self.logger.fatalError( 'Error: output file could not be read (it probably doesn\'t exist)\nMake sure the filename and relative path in settings.ini \'Output\' are correct.' )

        with  file:
            #------------------------------------------------------
            # Apply patches
            #------------------------------------------------------

            self.logger.logChange( self.logger.getHeader( 'Apply Patches' ) )
            
            # Reset button and custom tick function hack
            self._applyPatchUnifyEvoTargetFunction( file )
            self._applyPatchResetButton( file )

            toyTownWorkaround = patch_registry.applyPatches( self, file )


            #------------------------------------------------------
            # Write out tech data
            #------------------------------------------------------

            #Pack digimon data into buffer
            data_unpacked = []
            for tech in self.techData:
                data_unpacked.append( tech.unpackedFormat() )

            data_packed = util.packDataArray( data_unpacked, data.techDataFormat )

            #Set all digimon data
            util.writeDataWithExclusions( file,
                                          data_packed,
                                          data.techDataBlockOffset,
                                          data.techDataBlockSize,
                                          data.techDataExclusionOffsets,
                                          data.techDataExclusionSize )


            #------------------------------------------------------
            # Write out tech learn chance data
            #------------------------------------------------------

            #Pack battle tech learn chance data into buffer
            data_unpacked = []
            for tech in self.techData:
                if( not tech.isLearnable ):
                    continue

                data_unpacked.append( tech.unpackedLearnFormat() )

            data_packed = util.packDataArray( data_unpacked, data.techLearnFormat )

            #Set battle tech learn chance data
            util.writeDataWithExclusions( file,
                                          data_packed,
                                          data.techLearnBlockOffset,
                                          data.techLearnBlockSize,
                                          data.techLearnExclusionOffsets,
                                          data.techLearnExclusionSize )

            #Pack brain train tech learn chance data into buffer
            data_unpacked = []
            for chances in self.brainLearn:
                data_unpacked.append( tuple( chances ) )

            data_packed = util.packDataArray( data_unpacked, data.techBrainFormat )

            #Set brain train tech learn chance data
            util.writeDataWithExclusions( file,
                                          data_packed,
                                          data.techBrainBlockOffset,
                                          data.techBrainBlockSize,
                                          data.techBrainExclusionOffsets,
                                          data.techBrainExclusionSize )


            #------------------------------------------------------
            # Write out digimon data
            #------------------------------------------------------

            #Pack digimon data into buffer
            data_unpacked = []
            for digi in self.digimonData:
                data_unpacked.append( digi.unpackedFormat() )

            data_packed = util.packDataArray( data_unpacked, data.digimonDataFormat )

            #Set all digimon data
            util.writeDataWithExclusions( file,
                                          data_packed,
                                          data.digimonDataBlockOffset,
                                          data.digimonDataBlockSize,
                                          data.digimonDataExclusionOffsets,
                                          data.digimonDataExclusionSize )


            #------------------------------------------------------
            # Write out digimon evo data
            #------------------------------------------------------

            #Pack digimon evo data into buffer
            data_unpacked = []
            partners = range( 1, data.lastPartnerDigimon - 2 )
            for i, digi in enumerate( self.digimonData ):
                if i in partners:
                    data_unpacked.append( digi.unpackedEvoFormat() )

            data_packed = util.packDataArray( data_unpacked, data.evoToFromFormat )


            #Set all digimon evo data
            util.writeDataWithExclusions( file,
                                          data_packed,
                                          data.evoToFromBlockOffset,
                                          data.evoToFromBlockSize,
                                          data.evoToFromExclusionOffsets,
                                          data.evoToFromExclusionSize )


            #Pack digimon evo stat gain data into buffer
            data_unpacked = []
            partners = range( 0, data.lastPartnerDigimon + 1 )
            for i, digi in enumerate( self.digimonData ):
                if i in partners:
                    data_unpacked.append( digi.unpackedEvoStatsFormat() )

            data_packed = util.packDataArray( data_unpacked, data.evoStatsFormat )


            #Set all digimon evo stat gain data
            util.writeDataWithExclusions( file,
                                          data_packed,
                                          data.evoStatsBlockOffset,
                                          data.evoStatsBlockSize,
                                          data.evoStatsExclusionOffsets,
                                          data.evoStatsExclusionSize )


            #Pack digimon evo requirement data into buffer
            data_unpacked = []
            partners = range( 0, data.lastPartnerDigimon - 2 )
            for i, digi in enumerate( self.digimonData ):
                if i in partners:
                    data_unpacked.append( digi.unpackedEvoReqFormat() )

            data_packed = util.packDataArray( data_unpacked, data.evoReqsFormat )


            #Set all digimon evo requirement data
            util.writeDataWithExclusions( file,
                                          data_packed,
                                          data.evoReqsBlockOffset,
                                          data.evoReqsBlockSize,
                                          data.evoReqsExclusionOffsets,
                                          data.evoReqsExclusionSize )





            #------------------------------------------------------
            # Write out item data
            #------------------------------------------------------

            #Pack digimon data into buffer
            data_unpacked = []
            for item in self.itemData:
                data_unpacked.append( item.unpackedFormat() )

            data_packed = util.packDataArray( data_unpacked, data.itemDataFormat )

            #Set all digimon data
            util.writeDataWithExclusions( file,
                                          data_packed,
                                          data.itemDataBlockOffset,
                                          data.itemDataBlockSize,
                                          data.itemDataExclusionOffsets,
                                          data.itemDataExclusionSize )


            #------------------------------------------------------
            # Write out starter data
            #------------------------------------------------------

            for i in [ 0, 1 ]:
                #Set digimon ID for starter
                util.writeDataToFile( file,
                                      data.starterSetDigimonOffset[ i ],
                                      struct.pack( data.digimonIDFormat, self.starterID[ i ] ),
                                      self.logger )

                #Set digimon ID to check when learning
                #starter's first tech (must match starter!)
                util.writeDataToFile( file,
                                      data.starterChkDigimonOffset[ i ],
                                      struct.pack( data.digimonIDFormat, self.starterID[ i ] ),
                                      self.logger )

                #Set tech ID for first starter to learn
                util.writeDataToFile( file,
                                      data.starterLearnTechOffset[ i ],
                                      struct.pack( data.techIDFormat, self.starterTech[ i ] ),
                                      self.logger )

                #Set animation ID to equip as first stater's
                #first tech
                util.writeDataToFile( file,
                                      data.starterEquipAnimOffset[ i ],
                                      struct.pack( data.animIDFormat, util.techSlotAnimID( self.starterTechSlot[ i ] ) ),
                                      self.logger )

            util.writeDataToFile( file,
                                  data.starterStatChkDigimonOffset,
                                  struct.pack( data.digimonIDFormat, self.starterID[ 0 ] ),
                                  self.logger )


            #------------------------------------------------------
            # Write out recruitment data
            #------------------------------------------------------

            #Set trigger in each recruitment check
            for trigger in self.recruitData:
                for ofst in self.recruitData[ trigger ][ 0 ]:
                    util.writeDataToFile( file,
                                          ofst,
                                          struct.pack( data.recruitFormat, trigger ),
                                          self.logger )

                currentName = self.getDigimonName( trigger - 200 )
                nameToWrite = self.getDigimonName( self.recruitData[ trigger ][ 1 ] )[ :len( currentName ) ]

                for nameOfst in self.recruitData[ trigger ][ 2 ]:
                    util.writeDataToFile( file,
                                          nameOfst,
                                          scrutil.encode( nameToWrite ),
                                          self.logger )

            #------------------------------------------------------
            # Write out special evolution data
            #------------------------------------------------------

            #Set trigger in each recruitment check
            for ofsts in self.specEvos:
                val = self.specEvos[ ofsts ][ 0 ]
                for ofst in ofsts:
                    if ofst == 0x140479ED and toyTownWorkaround:
                        continue
                    util.writeDataToFile( file,
                                          ofst,
                                          struct.pack( data.specEvoFormat, val ),
                                          self.logger )

            #------------------------------------------------------
            # Write out chest item data
            #------------------------------------------------------

            #Set item IDs in chests
            for ofst, item in self.chestItems.items():
                util.writeDataToFile( file,
                                      ofst,
                                      struct.pack( data.chestItemFormat, scrutil.spawnChest, item ),
                                      self.logger )

            #------------------------------------------------------
            # Write out map spawn item data
            #------------------------------------------------------

            #Set item spawns in maps
            for ofst, item in self.mapItems.items():
                util.writeDataToFile( file,
                                      ofst,
                                      struct.pack( data.mapItemFormat, scrutil.spawnItem, item ),
                                      self.logger )

            #------------------------------------------------------
            # Write out Tokomon item data
            #------------------------------------------------------

            #Set item IDs and counts for Tokomon
            for ofst, ( item, count ) in self.tokoItems.items():
                util.writeDataToFile( file,
                                      ofst,
                                      struct.pack( data.tokoItemFormat, scrutil.giveItem, item, count ),
                                      self.logger )

            #------------------------------------------------------
            # Write out tech gift data
            #------------------------------------------------------

            #Set check and learn tech for tech gifts
            for ( learnOfst, checkOfst ), tech in self.techGifts.items():
                util.writeDataToFile( file,
                                      learnOfst,
                                      struct.pack( data.learnMoveFormat, scrutil.learnMove, tech ),
                                      self.logger )

                util.writeDataToFile( file,
                                      checkOfst,
                                      struct.pack( data.checkMoveFormat, tech ),
                                      self.logger )

            #------------------------------------------------------
            # Write out jukebox track names
            #------------------------------------------------------

            #Set jukebox track names
            util.writeDataWithExclusions( file,
                                          self.trackNames,
                                          data.trackNameBlockOffset,
                                          data.trackNameBlockSize,
                                          data.trackNameExclusionOffsets,
                                          data.trackNameExclusionSize )


    def applyPatch( self, patch, val=0 ):
        """
        Set specified patch to be applied to the ROM.

        Keyword arguments:
        patch -- one of the following:
                 'fixEvoItems'  Make evo items give stats + lifetime
        """

        self.patches.append( tuple( [ patch, val ] ) )


    def randomizeDigimonData( self, dropItem=False, dropRate=False, price=1000 ):
        """
        Randomize digimon data.

        Keyword arguments:
        dropItem -- Randomize dropped item?
        dropRate -- Randomize item drop chance?
        """

        self.logger.logChange( self.logger.getHeader( 'Randomize Digimon Data' ) )

        for digi in self.digimonData:
            if( dropItem ):
                digi.item = self._getRandomItem( consumableOnly=True,
                                                             notQuest=True,
                                                             notEvo=True,
                                                             matchValueOf=digi.item,
                                                             matchValue=price )

            if( dropRate ):
                rate = digi.drop_rate

                #Seperately handle 100% drops and never create new 100% drops
                defaultRates = [ 1, 5, 10, 20, 25, 30, 40, 50 ]
                chooseFromRates = [ 1, 1, 1, 5, 10, 20, 25, 30, 40, 50, 50, 50 ]

                #don't change the 100% drops away from being 100%
                if( rate == 0 ):
                    newRate = random.choice( defaultRates )
                    digi.drop_rate = newRate
                elif( rate != 100 ):
                    i = defaultRates.index( rate ) + 2
                    newRate = random.choice( chooseFromRates[ i - 2 : i + 3 ] )
                    digi.drop_rate = newRate

            self.logger.logChange( 'Set {:s} to drop {:s} {:d}% of the time'.format( digi.name,
                                                                                     self.getItemName( digi.item ),
                                                                                     digi.drop_rate ) )


    def randomizeTechData( self, mode='shuffle', power=False, cost=False, accuracy=False, effect=False, effectChance=False ):
        """
        Randomize tech data.

        Keyword arguments:
        mode -- shuffle = use vanilla vales, random = modify vanilla values
        power -- Randomize power?
        cost -- Randomize the mp cost?
        accuracy -- Randomize the accuracy?
        effect -- Randomize the effect?
        effectChance -- Randomize the chance of the effect happening?
        """

        self.logger.logChange( self.logger.getHeader( 'Randomize Tech Data' ) )

        for tech in self.techData:
            if( not tech.isLearnable ):
                continue

            if( power ):
                if( tech.power > 0 ):
                    swapWith = self.techData[ self._getRandomTech( learnableOnly=True, damagingOnly=True ) ]
                    tech.power, swapWith.power =  swapWith.power, tech.power

            if( cost ):
                swapWith = self.techData[ self._getRandomTech( learnableOnly=True ) ]
                tech.mp3, swapWith.mp3 =  swapWith.mp3, tech.mp3

            if( accuracy ):
                swapWith = self.techData[ self._getRandomTech( learnableOnly=True ) ]
                tech.accuracy, swapWith.accuracy =  swapWith.accuracy, tech.accuracy

            if( effect ):
                #50% chance of no effect or random effect
                if( random.randint( 0, 1 ) > 0 and not power == 0 ):
                    tech.effect = random.randint( 1, 4 )
                else:
                    tech.effect = 0
                    tech.effChance = 0

            if( effectChance ):
                #if no effect, set chance to zero
                if( tech.effect == 0 ):
                    tech.effChance = 0
                else:
                    #otherwise, random chance up to 70%
                    tech.effChance = random.randint( 1, 70 )

        if( mode != 'shuffle' ):
            for tech in self.techData:
                if( power ):
                    percent = random.randint( 70, 130 )
                    tech.power = int( min( ( tech.power * percent ) / 100, 999 ) )

                if( cost and ( tech.power != 0 )  ):
                    factor = random.randint( 10, 140 )
                    tech.mp3 = int( min( ( factor * tech.power ) / 300, 255 ) )

                if( accuracy ):
                    val = random.randint( 0, 99 )
                    if( val < 10 ):
                        tech.accuracy = random.randint( 33, 60 )
                    elif( val < 50 ):
                        tech.accuracy = random.randint( 50, 80 )
                    elif( val < 90 ):
                        tech.accuracy = random.randint( 75, 100 )
                    else:
                        tech.accuracy = 100


        #This has to be at the end due to power/mp/accuracy swapping around
        for tech in self.techData:
            if( not tech.isLearnable ):
                continue
            self.logger.logChange( '{:<2d} Set \'{:s}\' to {:d} power {:d} MP with {:d} accuracy\n   {:s} {:d}% of the time.  Learn chance {:d}%-{:d}%-{:d}%'.format(
                                                             tech.id,
                                                             tech.name,
                                                             tech.power,
                                                             tech.mp3 * 3,
                                                             tech.accuracy,
                                                             self.getEffectName( tech.effect ),
                                                             tech.effChance,
                                                             tech.learnChance[ 0 ],
                                                             tech.learnChance[ 1 ],
                                                             tech.learnChance[ 2 ] ) )


    def randomizeStarters( 
        self, 
        useWeakestTech=True, 
        forceDigimon="Random",
        allowedLevels=[ data.levelsByName[ 'ROOKIE' ] ] 
    ):
        """
        Set starters to two random different rookie Digimon.
        """

        self.logger.logChange( self.logger.getHeader( 'Randomize Starters' ) )

        allowedSet = []
        for level in allowedLevels:
            allowedSet += self.getPlayableDigimonByLevel( level )

        prevFirst = self.starterID[ 0 ]
        firstDigi = allowedSet[ random.randint( 0, len( allowedSet ) - 1) ]
        while firstDigi == prevFirst:
            firstDigi = allowedSet[ random.randint( 0, len( allowedSet ) - 1 ) ]

        prevSecond = self.starterID[ 1 ]
        secondDigi = firstDigi
        while secondDigi == firstDigi or secondDigi == prevSecond:
            secondDigi = allowedSet[ random.randint( 0, len( allowedSet ) - 1 ) ]

        #Do this after the above so that selecting digimon doesn't change the rest of the seed
        forcedDigimon = self.getDigimonByName( forceDigimon )
        if forcedDigimon is not None:
            firstDigi = forcedDigimon

        self.starterID[ 0 ] = firstDigi.id
        self.logger.logChange( 'First starter set to ' + firstDigi.name )

        self.starterID[ 1 ] = secondDigi.id
        self.logger.logChange( 'Second starter set to ' +  secondDigi.name )

        self._setStarterTechs( useWeakestTech )


    def randomizeChestItems( self, allowEvo=False ):
        """
        Randomize items in chests.

        Keyword arguments:
        allowEvo -- Include or exclude evolution items from
                    the pool of items to choose from.
        """

        self.logger.logChange( self.logger.getHeader( 'Randomize Chest Items' ) )

        #for each chest, choose a random allowed item from data
        for key in list( self.chestItems ):
            randID = self._getRandomItem( notQuest=True, notEvo=( not allowEvo ) )

            pre = self.chestItems[ key ]
            self.chestItems[ key ] = self.itemData[ randID ].id
            self.logger.logChange( 'Changed chest item from ' + self.itemData[ pre ].name + ' to ' + self.itemData[ self.chestItems[ key ] ].name )


    def randomizeTokomonItems( self, consumableOnly=True ):
        """
        Randomize items (and quantity) that Tokomon gives.

        Keyword arguments:
        allowEvo -- Include or exclude evolution items from
                    the pool of items to choose from.
        """

        self.logger.logChange( self.logger.getHeader( 'Randomize Tokomon Items' ) )

        #for each tokomon item, choose a random allowed item
        #and a random quantity
        for key in list( self.tokoItems ):
            randID = self._getRandomItem( notQuest=True, notEvo=True, consumableOnly=consumableOnly )

            #choose random number 1-3.  Make valuable items less likely
            #to come in large numbers
            randCount = random.randint( 1, 3 )
            if( self.itemData[ randID ].price >= 1000 and randCount > 1 ):
                randCount = random.randint( 1, 3 )
            elif( self.itemData[ randID ].price < 1000 and randCount == 1 ):
                randCount = random.randint( 1, 3 )

            preItem, preCount = self.tokoItems[ key ]
            self.tokoItems[ key ] = ( self.itemData[ randID ].id, randCount )

            self.logger.logChange( 'Changed Tokomon item from ' + str( preCount )  + 'x \'' + self.itemData[ preItem ].name +
                                                         ' to ' + str( randCount ) + 'x \'' + self.itemData[ self.tokoItems[ key ][0] ].name + '\'' )


    def randomizeMapSpawnItems( self, foodOnly=False, price=1000 ):
        """
        Randomize items that appear on maps.  Match value using price.
        If foodOnly is set, replace food items only with other food
        items.

        Keyword arguments:
        foodOnly -- Only replace food items with other food items
        """

        self.logger.logChange( self.logger.getHeader( 'Randomize Map Items' ) )

        #for each map spawn, choose a random allowed item from data
        for key in list( self.mapItems ):
            id = self.mapItems[ key ]

            #if foodOnly is set, swap food items only for other food items
            fo = foodOnly and self.itemData[ id ].isFood

            randID = self._getRandomItem( foodOnly=fo, consumableOnly=True, notQuest=True, notEvo=True, matchValueOf=id, matchValue=price )

            pre = self.mapItems[ key ]
            self.mapItems[ key ] = self.itemData[ randID ].id
            self.logger.logChange( 'Changed map item from ' + self.itemData[ pre ].name + ' to ' + self.itemData[ self.mapItems[ key ] ].name )


    def randomizeTechGifts( self ):
        """
        Randomize techs that are taught by Seadramon and the tech taught
        in Beetle Land.
        """

        self.logger.logChange( self.logger.getHeader( 'Randomize Tech Gifts' ) )

        #for each tech gift, choose a random usable tech
        for key in list( self.techGifts ):
            randID = self._getRandomTech( learnableOnly=True )

            pre = self.techGifts[ key ]
            self.techGifts[ key ] = self.techData[ randID ].id
            self.logger.logChange( 'Changed tech gift from ' + self.getTechName( pre ) + ' to ' + self.getTechName( self.techGifts[ key ] ) )


    def randomizeEvolutions( self, obtainAll=False ):
        """
        Randomize the lists of evolutions that each digimon
        is capable of.
        """

        self.logger.logChange( self.logger.getHeader( 'Randomize Evolutions' ) )

        for digi in self.digimonData:
            digi.clearEvos()

        #Freshes each get one in-training target, no repeats (with obtainAll)
        freshes = self.getPlayableDigimonByLevel( data.levelsByName[ 'FRESH' ] )
        validEvos = freshes[ 0 ].validEvosTo()
        for digi in freshes:
            randID = random.randint( 0, len( validEvos ) - 1 )
            digi.addEvoTo( validEvos[ randID ].id )
            if( obtainAll ):
                del validEvos[ randID ]

        #In-trainings each get two Rookie targets, no repeats (with obtainAll)
        inTrainings = self.getPlayableDigimonByLevel( data.levelsByName[ 'IN-TRAINING' ] )
        validEvos = inTrainings[ 0 ].validEvosTo()
        for digi in inTrainings:
            digi.updateEvosFrom()
            while( digi.getEvoToCount() < 2 ):
                randID = random.randint( 0, len( validEvos ) - 1 )
                digi.addEvoTo( validEvos[ randID ].id )
                if( obtainAll ):
                    del validEvos[ randID ]

        #Assign each champion to at least one rookie first if obtainAll is set
        rookies = self.getPlayableDigimonByLevel( data.levelsByName[ 'ROOKIE' ] )

        if( obtainAll ):
            validEvos = rookies[ 0 ].validEvosTo()
            while( len( validEvos ) > 0 ):
                digi = random.choice( rookies )
                count = digi.getEvoToCount()
                digi.addEvoTo( validEvos[ 0 ].id )
                if( count < digi.getEvoToCount() ):
                    del validEvos[ 0 ]

        #Rookies get 4-6 Champion targets.
        validEvos = rookies[ 0 ].validEvosTo()
        for digi in rookies:
            count = random.randint( 4, 6 )
            digi.updateEvosFrom()
            while( digi.getEvoToCount() < count ):
                randID = random.randint( 0, len( validEvos ) - 1 )
                digi.addEvoTo( validEvos[ randID ].id )


        #Assign each ultimate to at least one champion first if obtainAll is set
        champions = self.getPlayableDigimonByLevel( data.levelsByName[ 'CHAMPION' ], excludeSpecials=True )

        if( obtainAll ):
            validEvos = champions[ 0 ].validEvosTo()
            while( len( validEvos ) > 0 ):
                digi = random.choice( champions )
                count = digi.getEvoToCount()
                digi.addEvoTo( validEvos[ 0 ].id )
                if( count < digi.getEvoToCount() ):
                    del validEvos[ 0 ]

        #Champions get 1-2 Ultimate targets.
        validEvos = rookies[ 0 ].validEvosTo()
        for digi in champions:
            count = random.randint( 1, 2 )
            digi.updateEvosFrom()
            validEvos = digi.validEvosTo()
            while( digi.getEvoToCount() < count ):
                randID = random.randint( 0, len( validEvos ) - 1 )
                digi.addEvoTo( validEvos[ randID ].id )

        #Ultimate just need to have their from evos updated.
        ultimates = self.getPlayableDigimonByLevel( data.levelsByName[ 'ULTIMATE' ], excludeSpecials=True )
        for digi in ultimates:
            digi.updateEvosFrom()

        self.logger.logChange( 'Changed digimon evolutions to the following: ' )
        for i in range( 1, data.lastPartnerDigimon + 1 ):
            self.logger.logChange( 'Changed evolutions for ' + self.digimonData[ i ].evoData() + '\n' )


    def randomizeEvolutionRequirements( self ):
        """
        Randomize the requirements for evolving to each digimon.
        """

        self.logger.logChange( self.logger.getHeader( 'Randomize Evolution Requirements' ) )

        self.randomizedRequirements = True

        for digi in self.digimonData:
            if( digi.id > data.lastPartnerDigimon - 3 ):
                continue

            if( digi.level == data.levelsByName[ 'FRESH' ] ):
                digi.clearEvoReqs()
                continue

            elif( digi.level == data.levelsByName[ 'IN-TRAINING' ] ):
                digi.clearEvoReqs()
                continue

            elif( digi.level == data.levelsByName[ 'ROOKIE' ] ):
                if( digi.name == 'Kunemon' ):
                    digi.clearEvoReqs()
                    continue

                digi.clearEvoReqs()
                digi.evoBonusDigi = digi.fromEvo[ 2 ]
                digi.evoStatReqs = self._getRandomStatRequirements( digi.level )
                digi.evoCareMistakes = 0
                digi.evoMaxCareMistakes = False
                digi.evoWeight = 15
                digi.evoTechs = 0
                digi.evoBattles = -2
                digi.evoMaxBattles = False

            elif( digi.level == data.levelsByName[ 'CHAMPION' ] ):
                if( digi.name in [ 'Numemon', 'Sukamon', 'Nanimon', ] ):
                    digi.clearEvoReqs()
                    continue

                digi.clearEvoReqs()
                digi.evoStatReqs = self._getRandomStatRequirements( digi.level )

                digi.evoMaxCareMistakes = random.choice( [ True, False ] )
                if( digi.evoMaxCareMistakes ):
                    digi.evoCareMistakes = random.randint( 0, 6 )
                else:
                    digi.evoCareMistakes = random.randint( 2, 6 )

                digi.evoWeight = random.randint( 1, 10 ) * 5

                digi.evoTechs = random.randint( 10, 35 )
                numBonusReqs = 1

                if( random.randint( 0, 99 ) < 10 ):
                    digi.evoDiscipline = random.randint( 50, 95 )
                    numBonusReqs += 1

                if( random.randint( 0, 99 ) < 10 ):
                    digi.evoDiscipline = random.randint( 45, 85 )
                    numBonusReqs += 1

                if( random.randint( 0, 99 ) < 30 ):
                    digi.evoMaxBattles = random.choice( [ True, False ] )
                    if( digi.evoMaxBattles ):
                        digi.evoBattles = random.randint( 2, 15 )
                    else:
                        digi.evoBattles = random.randint( 2, 15 )
                    numBonusReqs += 1

                if( random.randint( 0, 99 ) < 10 or numBonusReqs < 2 ):
                    digi.evoBonusDigi = digi.fromEvo[ 2 ]
                    numBonusReqs += 1

            elif( digi.level == data.levelsByName[ 'ULTIMATE' ] ):
                if( digi.name in [ 'Vademon', 'WereGarurumon' ] ):
                    digi.clearEvoReqs()
                    continue

                digi.clearEvoReqs()
                digi.evoStatReqs = self._getRandomStatRequirements( digi.level )

                digi.evoMaxCareMistakes = random.choice( [ True, False ] )
                if( digi.evoMaxCareMistakes ):
                    digi.evoCareMistakes = random.randint( 0, 15 )
                else:
                    digi.evoCareMistakes = random.randint( 5, 15 )

                digi.evoWeight = random.randint( 1, 14 ) * 5

                digi.evoTechs = random.randint( 21, 50 )
                numBonusReqs = 1

                if( random.randint( 0, 99 ) < 10 ):
                    digi.evoDiscipline = random.randint( 90, 100 )
                    numBonusReqs += 1

                if( random.randint( 0, 99 ) < 10 ):
                    digi.evoDiscipline = random.randint( 90, 100 )
                    numBonusReqs += 1

                if( random.randint( 0, 99 ) < 30 ):
                    digi.evoMaxBattles = random.choice( [ True, False ] )
                    if( digi.evoMaxBattles ):
                        digi.evoBattles = random.randint( 0, 15 )
                    else:
                        digi.evoBattles = random.randint( 5, 20 ) * 5
                    numBonusReqs += 1

                if( random.randint( 0, 99 ) < 10 or numBonusReqs < 2 ):
                    digi.evoBonusDigi = digi.fromEvo[ 2 ]
                    numBonusReqs += 1

        for i in range( 1, data.lastPartnerDigimon + 1 ):
            self.logger.logChange( 'Changed requirements for ' + self.digimonData[ i ].evoReqsToString() + '\n' )


    def updateEvolutionStats( self ):
        """
        Updates evolution requirements for evolving to certain
        digimon.
        """

        devimon = None

        for digi in self.digimonData:
            if( digi.name != 'Devimon' ):
                continue

            devimon = digi
            break

        devimon.evoStats[ 0 ] = 1500
        devimon.evoStats[ 1 ] = 2000
        devimon.evoStats[ 2 ] = 250
        devimon.evoStats[ 3 ] = 100
        devimon.evoStats[ 4 ] = 150
        devimon.evoStats[ 5 ] = 200

        self.logger.logChange( 'Set Devimon stat gains to: 1500  2000  250  100  150  200' )


    def randomizeSpecialEvolutions( self ):
        """
        Randomize the target digimon for all special evolutions.
        """

        self.logger.logChange( self.logger.getHeader( 'Randomize Special Evolutions' ) )

        for ofsts in self.specEvos:
            id = self.specEvos[ ofsts ][ 0 ]
            fromID = self.specEvos[ ofsts ][ 1 ]
            newID = random.choice( self.getPlayableDigimonByLevel( self.digimonData[ id ].level ) ).id
            while( newID == id or newID == fromID ):
                newID = random.choice( self.getPlayableDigimonByLevel( self.digimonData[ id ].level ) ).id

            self.specEvos[ ofsts ] = ( newID, fromID )

            self.logger.logChange( 'Changed special evolution for ' + self.getDigimonName( id ) + ' to ' + self.getDigimonName( newID ) )


    def randomizeRecruitments( self ):
        """
        Randomize the digimon that is recruited when each
        event is accomplished (e.g. defeat Gabumon, recruit
        Frigimon)
        """

        self.logger.logChange( self.logger.getHeader( 'Randomize Recruitments' ) )

        #randomly shuffle all recruits
        for triggerA in self.recruitData:
            triggerB = random.choice( list( self.recruitData ) )

            ofstsA = self.recruitData[ triggerA ]
            ofstsB = self.recruitData[ triggerB ]

            self.recruitData[ triggerA ], self.recruitData[ triggerB ] = ofstsB, ofstsA

        #check whether this arrangement is 100PP-safe
        if( not self._validateRecruitments() ):
            self.randomizeRecruitments()

        #rewrite PP calculation function
        self.applyPatch( 'pp' )

        #write new pp value into least significant 2 bytes of digimon height
        for trigger in self.recruitData:
            oldDigi = self.digimonData[ trigger - 200 ]
            newDigi = self.digimonData[ self.recruitData[ trigger ][ 1 ] ]

            oldDigi.height = ( oldDigi.height & 0xFFFC ) | newDigi.pp

        #prevent ogremon 2 softlock
        self.applyPatch( 'ogremon' )

        #print changes
        for trigger in self.recruitData:
            oldDigi = self.digimonData[ trigger - 200 ]
            newDigi = self.digimonData[ self.recruitData[ trigger ][ 1 ] ]
            self.logger.logChange( oldDigi.name + ' now recruits ' + newDigi.name +
                                   ' and gives ' + str( oldDigi.height & 0x0003 ) + ' pp' )
            self.logger.logChange( oldDigi.name + ' now has height: ' + str( oldDigi.height ) )


    def getPlayableDigimonByLevel( self, level, excludeSpecials=False ):
        """
        Get a list of digimon with a specified level.

        Keyword arguments:
        level -- Level of digimon to get.
        """

        out = []

        for digi in self.digimonData:
            if( digi.level == level and digi.id in digi.playableDigimon ):
                if( excludeSpecials and digi.name in [ 'Panjyamon', 'Gigadramon', 'MetalEtemon' ] ):
                    continue
                out.append( digi )

        return out


    def getDigimonName( self, id ):
        """
        Get digimon name from data.

        Keyword arguments:
        id -- Digimon ID to get name for.
        """

        if( id < len( self.digimonData ) ):
            return self.digimonData[ id ].name
        else:
            return '---'

    
    def getDigimonByName( self, name ):
        """
        Get digimon from data that matches name.

        Keyword arguments:
        name -- Digimon to retrieve.
        """

        for digi in self.digimonData:
            if digi.name == name:
                return digi
        
        return None



    def getItemName( self, id ):
        """
        Get item name from data.

        Keyword arguments:
        id -- Item ID to get name for.
        """

        if( id < len( self.itemData ) ):
            return self.itemData[ id ].name
        else:
            return 'None'


    def getTechName( self, id ):
        """
        Get tech name from data.

        Keyword arguments:
        id -- Tech ID to get name for.
        """

        if( id < len( data.techs ) ):
            return data.techs[ id ]
        else:
            return 'None'


    def getTypeName( self, id ):
        """
        Get type name from data.

        Keyword arguments:
        id -- Type ID to get name for.
        """

        return util.typeIDToName( id )


    def getSpecialtyName( self, id ):
        """
        Get type name from data.

        Keyword arguments:
        id -- Specialty ID to get name for.
        """

        return util.specIDToName( id )


    def getLevelName( self, id ):
        """
        Get level name from data.

        Keyword arguments:
        id -- Level ID to get name for.
        """

        return util.levelIDToName( id )


    def getRangeName( self, id ):
        """
        Get range name from data.

        Keyword arguments:
        id -- Range ID to get name for.
        """

        if( id in data.ranges ):
            return data.ranges[ id ]
        return "UNDEF"


    def getEffectName( self, id ):
        """
        Get effect name from data.

        Keyword arguments:
        id -- Effect ID to get name for.
        """

        if( id in data.effects ):
            return data.effects[ id ]
        return "NONE"


    def _getRandomItem( self, foodOnly=False, consumableOnly=False, notEvo=False, notQuest=False, matchValueOf=None, matchValue=1000 ):
        """
        Get a random item that satisfies the conditions.

        Keyword arguments:
        foodOnly -- Only allow food items
        consumableOnly -- Only allow consumable items
        notEvo -- Exclude evolution items
        notQuest -- Exclude quest items
        matchValueOf -- Only items that are on the same side of the low-value price cutoff
        """

        randID = 0
        valid = False
        while( not valid ):
            randID = random.randint( 0, len( self.itemData ) - 1 )
            item = self.itemData[ randID ]
            valid = True

            if( item.isBanned ):
                valid = False

            if( foodOnly and not item.isFood ):
                valid = False

            if( consumableOnly and not item.isConsumable ):
                valid = False

            if( notEvo and item.isEvo ):
                valid = False

            if( notQuest and not item.dropable ):
                valid = False


            if( matchValueOf is not None ):
                itemToMatch = self.itemData[ matchValueOf ]
                if( ( item.price < matchValue ) != ( itemToMatch.price < matchValue ) ):
                    valid = False


        return randID


    def _getRandomTech( self, learnableOnly=False, notFinisher=False, damagingOnly=False ):
        """
        Get a random tech that satisfies the conditions.

        Keyword arguments:
        learnableOnly -- Only moves that can be learned
        notFinisher -- Exclude finishers
        damagingOnly -- Only moves that deal damage
        """

        randID = 0
        valid = False
        while( not valid ):
            randID = random.randint( 0, len( self.techData ) - 1 )
            tech = self.techData[ randID ]
            valid = True

            if( notFinisher and tech.isFinisher ):
                valid = False

            if( damagingOnly and not tech.isDamaging ):
                valid = False

            if( learnableOnly and not tech.isLearnable ):
                valid = False

        return randID


    def _setStarterTechs( self, useWeakest=True ):
        """
        Set starter techs to either weakest or random.

        Keyword arguments:
        default -- If true, use the lowest tier move available.
                   Otherwise, pick one at random.
        """

        for i in [ 0, 1 ]:
            #Find the lowest tier damaging tech that the digimon
            #can use
            if( useWeakest ):
                lowestTier = 0xFF
                lowestTierID = 0
                for slot, techID in enumerate( self.digimonData[ self.starterID[ i ] ].tech ) :
                    if( self.getTechName( techID ) != 'None' and self.getTechName( techID ) != 'Counter' ):
                        tier = self.techData[ techID ].tier
                        if( self.techData[ techID ].isDamaging and not self.techData[ techID ].isFinisher and tier < lowestTier ):
                            lowestTier = tier
                            lowestTierID = techID
                            lowestTierSlot = slot + 1
                self.starterTech[ i ] = lowestTierID
                self.starterTechSlot[ i ] = lowestTierSlot
                self.logger.logChange( 'Starter tech set to ' + self.getTechName( self.starterTech[ i ] )
                                     + ' (' + self.digimonData[ self.starterID[ i ] ].name + '\'s slot ' + str( self.starterTechSlot[ i ] ) + ')' )
            #Select a random learnable damaging tech
            else:
                randID = random.randint( 0, 15 )
                techID = self.digimonData[ self.starterID[ i ] ].tech[ randID ]
                while( self.getTechName( techID ) == 'None' or self.getTechName( techID ) == 'Counter' or not self.techData[ techID ].isDamaging or self.techData[ techID ].isFinisher ):
                    randID = random.randint( 0, 15 )
                    techID = self.digimonData[ self.starterID[ i ] ].tech[ randID ]
                    self.logger.log( self.getTechName( techID ) )
                self.starterTech[ i ] = techID
                self.starterTechSlot[ i ] = randID + 1
                self.logger.logChange( 'Starter tech set to ' + self.getTechName( self.starterTech[ i ] )
                                     + ' (' + self.digimonData[ self.starterID[ i ] ].name
                                     + '\'s slot ' + str( self.starterTechSlot[ i ] ) + ')' )


    def _getRandomStatRequirements( self, level ):
        """
        Get random stat requirements to evolve to a digimon of
        the given level.

        Keyword arguments:
        level -- Digimon level for which to get stat requirements.
        """


        stats = []
        statRequirements = [ 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF ]
        statsToChooseFrom = [ 0, 1, 2, 3, 4, 5 ]

        if( level == data.levelsByName[ 'ROOKIE' ] ):
            numStats = 3

            for _ in range( 0, numStats ):
                val = random.choice( statsToChooseFrom )
                statsToChooseFrom.remove( val )
                stats.append( val )

            for stat in stats:
                statRequirements[ stat ] = 1

            return statRequirements

        elif( level == data.levelsByName[ 'CHAMPION' ] ):
            numStats = random.randint( 1, 4 )

            for _ in range( 0, numStats ):
                val = random.choice( statsToChooseFrom )
                statsToChooseFrom.remove( val )
                stats.append( val )

            for stat in stats:
                statRequirements[ stat ] = 100

        elif( level == data.levelsByName[ 'ULTIMATE' ] ):
            numStats = random.randint( 4, 6 )

            for _ in range( 0, numStats ):
                val = random.choice( statsToChooseFrom )
                statsToChooseFrom.remove( val )
                stats.append( val )

            #30% chance for the stats to be "hard"
            hard = random.randint( 0, 99 ) > 70

            for stat in stats:
                if( hard ):
                    statRequirements[ stat ] = random.randint( 3, 7 ) * 100
                else:
                    statRequirements[ stat ] = random.randint( 2, 5 ) * 100

        return statRequirements


    def _validateRecruitments( self ):
        """
        Check whether the current recruitment randomization is valid
        (beatable).
        """

        factorialTownDigis = [ 'Numemon', 'MetalMamemon', 'Andromon', 'Giromon' ]

        for trigger in self.recruitData:
            recruited = self.getDigimonName( trigger - 200 )
            showedUp = self.getDigimonName( self.recruitData[ trigger ][ 1 ] )

            if( showedUp == 'Whamon' ):
                if( recruited in factorialTownDigis and not recruited == 'Nanimon' ):
                    return False

        return True

    def _applyPatchFixEvoItems( self, file ):
        """
        Change evo items to give stats and lifetime.
        """

        util.writeDataToFile( file,
                              data.evoItemPatchOffset,
                              struct.pack( data.evoitemPatchFormat, data.evoItemPatchValue ),
                              self.logger )
        self.logger.logChange( 'Patched evo items to increase stats and lifetime.' )


    def _applyPatchAllowDrop( self, file ):
        """
        Allow all items to be dropped form the item menu.
        """

        for item in self.itemData:
            item.dropable = True

        self.logger.logChange( 'Patched quest items to be dropable from the menu.' )


    def _applyPatchWoah( self, file, text="Oh shit!" ):
        """
        Change "Woah!" to something else.
        """

        util.writeDataToFile( file,
                              data.woahPatchOffset,
                              struct.pack( data.woahPatchFormat, text[ :8 ].encode( 'ascii' ) ),
                              self.logger )
        self.logger.logChange( 'Patched "Woah!" to be "' + text + '".' )


    def _applyPatchLearnTierOne( self, file ):
        """
        Make tier one move learnable in brain training (30% chance).
        """

        self.brainLearn[ 0 ][ 0 ] = 30
        self.logger.logChange( 'Patched brain training to make tier 1 moves learnable with a 30% success rate.' )


    def _applyPatchLearnChance( self, file ):
        """
        Increase chance of learning techs in battle.
        """

        for tech in self.techData:
            for i, val in enumerate( tech.learnChance ):
                tech.learnChance[ i ] = val * 2

        for chances in self.brainLearn:
            for i, val in enumerate( chances ):
                chances[ i ] = ( val * 2 ) if ( val != 0 ) else ( 5 )

        self.logger.logChange( 'Patched learn chance (battle and brain) to be twice as high.' )


    def _applyPatchGabumon( self, file ):
        """
        Increase Gabumon.
        """

        for ofst, val in data.gabuPatchWrites:
            util.writeDataToFile( file,
                                  ofst,
                                  struct.pack( data.gabuPatchFormat, val ),
                                  self.logger )

        self.logger.logChange( 'Patched enemy Gabumon to be unreasonably strong.' )


    def _applyPatchGiromon( self, file ):
        """
        Fix Giromon/jukebox crash glitch.
        """

        trackLen = 0
        for i in range( 0, len( self.trackNames ) ):
            if( self.trackNames[ i ] == b'\0' ):
                trackLen = 0
            else:
                trackLen += 1
                if( trackLen > 24 ):
                    self.trackNames = self.trackNames[ :i ] + b'\0' + self.trackNames[ i+1: ]

        self.logger.logChange( 'Patched out Giromon/jukebox glitch.' )
        

    def _applyPatchSpawn( self, file, val ):
        """
        Set spawn rate for Mamemon, etc. to specified percentage.
        """
        
        #Mamemon, Piximon, and MMamemon use a 0-99 random
        val = min( 100, max( 1, val ) )
        largePercent = val - 1
        
        #Otamamon uses a 0-2 random
        smallPercent = math.floor( val / 33 )
        
        for ofst in data.spawnRateMamemonOffset:
            util.writeDataToFile( file,
                                  ofst,
                                  struct.pack( data.spawnRateFormat, largePercent ),
                                  self.logger )
        
        
        for ofst in data.spawnRatePiximonOffset:
            util.writeDataToFile( file,
                                  ofst,
                                  struct.pack( data.spawnRateFormat, largePercent ),
                                  self.logger )
                                  
        
        for ofst in data.spawnRateMMamemonOffset:
            util.writeDataToFile( file,
                                  ofst,
                                  struct.pack( data.spawnRateFormat, largePercent ),
                                  self.logger )
                                  
        
        for ofst in data.spawnRateOtamamonOffset:
            util.writeDataToFile( file,
                                  ofst,
                                  struct.pack( data.spawnRateFormat, smallPercent ),
                                  self.logger )

        self.logger.logChange( 'Updated Piximon, Mamemon, MetalMamemon, and Otamamon spawn rates.' )


    def _applyPatchIntroHash( self, file, hash ):
        """
        Write settings hash value to script in Jijimon intro.
        """

        # Write on two lines with a newline character in between
        util.writeDataToFile( file,
                                data.introHashOffset,
                                scrutil.encode( hash[:16] + '\n' + hash[15:]+ "   " ),
                                self.logger )

        self.logger.logChange( 'Inserted settings hash into intro dialogue.' )


    def _applyPatchIntroSkip( self, file ):
        """
        Skip many of the textboxes in the intro dialogue
        """

        # Write jumps to skip majority of intro dialog
        util.writeDataToFile( file,
                              data.introSkipOutsideOffset,
                              scrutil.compile( "jumpTo", data.introSkipOutsideDest ),
                              self.logger )
        util.writeDataToFile( file,
                              data.introSkipInsideOffset,
                              scrutil.compile( "jumpTo", data.introSkipInsideDest ),
                              self.logger )

        self.logger.logChange( 'Modified intro scenes to remove most of the dialogue.' )


    def _applyPatchUnrigSlots( self, file ):
        """
        Overwrite one instruction in each bonus training function to short-circuit all
        of the "rigging" logic, making slots skill-based.
        """

        # Write new instruction to both training slots functions
        util.writeDataToFile( file,
                              data.unrigSlotsOffset,
                              struct.pack( data.unrigSlotsFormat, data.unrigSlotsValue ),
                              self.logger )

        util.writeDataToFile( file,
                              data.unrigSlots2Offset,
                              struct.pack( data.unrigSlots2Format, data.unrigSlots2Value ),
                              self.logger )

        self.logger.logChange( 'Un-rigged slots.' )


    def _applyPatchPP( self, file ):
        """
        Write new PP calculation function to code.  Reads the new PP value from the least
        significant two bytes of each digimon's height value.
        """

        # Write new instructions to prosperity point calculation function
        util.writeDataToFile( file,
                            data.rewritePPOffset,
                            struct.pack( data.rewritePPFormat, *data.rewritePPValue ),
                            self.logger )

        self.logger.logChange( 'Updated PP calculation function.' )


    def _applyPatchUnlockAreas( self, file ):
        """
        Remove the digimon type locks on Greylord's Mansion and Ice 
        Sanctuary.
        """

        #Overwrite jumps into area lock script with non-jumps
        for ofst in data.unlockGreylordOffset:
            util.writeDataToFile( file,
                                  ofst,
                                  struct.pack( data.unlockTypeLockFormat, data.unlockGreylordValue ),
                                  self.logger )
        for ofst in data.unlockIceOffset:
            util.writeDataToFile( file,
                                  ofst,
                                  struct.pack( data.unlockTypeLockFormat, data.unlockIceValue ),
                                  self.logger )
        for ofst in data.unlockToyTownOffset:
            util.writeDataToFile( file,
                                  ofst,
                                  struct.pack( data.unlockToyTownFormat, data.unlockToyTownValue ),
                                  self.logger )

        self.logger.logChange( "Removed digimon type locks on Greylord's Mansion, Ice Sanctuary and Toy Town." )


    def _applyPatchOgremonSoftlock( self, file ):
        """
        Prevent softlock in the Ogremon 2 room when Ogremon 3 is 
        completed before Ogremon 2.
        """

        #Overwrite Ogremon 3 trigger check with Shellmon recruited check
        for ofst in data.ogremonSoftlockOffset:
            util.writeDataToFile( file,
                                  ofst,
                                  struct.pack( data.ogremonSoftlockFormat, data.ogremonSoftlockValue ),
                                  self.logger )
                                  
        self.logger.logChange( "Applied Ogremon softlock fix" )
		
    def _applyPatchMovementSoftlock( self, file ):
        """
        Prevents entityMoveTo/entityWalkTo softlocks
        """
        
        for ofst in data.fixRotationSLOffset:
            util.writeDataToFile( file, 
                                  ofst,
                                  struct.pack( data.fixRotationSLFormat, data.fixRotationSLValue ),
                                  self.logger )
                                  
        for ofst in data.fixMoveToSLOffset:
            util.writeDataToFile( file, 
                                  ofst,
                                  struct.pack( data.fixMoveToSLFormat, data.fixMoveToSLValue ),
                                  self.logger )
        
        for ofst in data.fixToyTownSLOffset:
            util.writeDataToFile( file,
                                  ofst,
                                  struct.pack( data.fixToyTownSLFormat, data.fixToyTownSLValue ),
                                  self.logger )
                                  
        for ofst in data.fixLeoCaveSLOffset:
            util.writeDataToFile( file,
                                  ofst,
                                  struct.pack( data.fixLeoCaveSLFormat, data.fixLeoCaveSLValue ),
                                  self.logger )
        
        self.logger.logChange( "Applied 4 movement softlock patches." )
        
    def _applyPatchUnifyEvoTargetFunction( self, file ):
        """
        Unified two functions that repeat most of their code,
        freeing memory for other uses.
        """
        
        for ofst, value in data.evoTargetUnifyHack.items():
            util.writeDataToFile( file,
                                  ofst,
                                  struct.pack( data.evoTargetUnifyHackFormat, value ),
                                  self.logger )
        self.logger.logChange( "Unified evoTarget functions." )
    
    def _applyPatchResetButton( self, file ):
        """
        Adds a button combination that reboots the game.
        """
        
        util.writeDataToFile( file,
                              data.customTickFunctionOffset,
                              struct.pack( data.customTickFunctionFormat, *data.customTickFunctionValue ),
                              self.logger )
        
        util.writeDataToFile( file,
                              data.customTickHookOffset,
                              struct.pack( data.customTickHookFormat, data.customTickHookValue ),
                              self.logger )
        
        self.logger.logChange( "Added custom function and hook for it" )

    def _randomizeTypeEffectiveness( self, file ):
        """
        Randomizes type effectiveness to a random value between 2 and 20
        """

        self.logger.logChange( "Changing type effectivness chart" )

        options = [ 2, 5, 10, 15, 20 ]

        for type1 in range(0, 7):
            row = ""
            
            for type2 in range(0, 7):
                newValue = random.choice(options) # random.randint(2, 20)
                offset =  type1 * 7 + type2
                util.writeDataToFile( file,
                                      data.typeEffectivenessOffset + offset,
                                      struct.pack( data.typeEffectivenessFormat, newValue),
                                      self.logger )
                row = row + str(newValue) + " "
            
            self.logger.logChange( row )
        
        self.logger.logChange( "Randomized type effectiveness" )

    def _applyPatchLearnMoveAndCommand( self, file ):
        """
        Removes the command learning text to allow learning a move and a command
        in the same training session.
        """

        util.writeDataToFile(   file,
                                data.learnMoveAndCommandOffset,
                                struct.pack( data.learnMoveAndCommandFormat, *data.learnMoveAndCommandValue ),
                                self.logger )

        self.logger.logChange( "Fixing move learning at brains training.")

    def _applyPatchDVChipDescription( self, file ):
        """
        Fixes the description of DV Chips to reflect what they're actually doing.
        """

        util.writeDataToFile( file,
                              data.DVChipAOffset,
                              struct.pack( data.DVChipAFormat, data.DVChipAValue[ :26 ].encode( 'ascii' ) ),
                              self.logger )

        util.writeDataToFile( file,
                              data.DVChipDOffset,
                              struct.pack( data.DVChipDFormat, data.DVChipDValue[ :26 ].encode( 'ascii' ) ),
                              self.logger )

        util.writeDataToFile( file,
                              data.DVChipEOffset,
                              struct.pack( data.DVChipEFormat, data.DVChipEValue[ :26 ].encode( 'ascii' ) ),
                              self.logger )

    def _applyPatchGuaranteeHappyShrm( self, file ):
        util.writeDataToFile( file,
                              data.happyMushroomVendingOffset1,
                              struct.pack( data.happyMushroomVendingFormat1, data.happyMushroomVendingValue1.encode( 'shift_jis' ) ),
                              self.logger )

        util.writeDataToFile( file,
                              data.happyMushroomVendingOffset2,
                              struct.pack( data.happyMushroomVendingFormat2, data.happyMushroomVendingValue2.encode( 'ascii' ) ),
                              self.logger )

        util.writeDataToFile( file,
                              data.happyMushroomVendingOffset3,
                              struct.pack( data.happyMushroomVendingPriceFormat, data.happyMushroomVendingPriceValue ),
                              self.logger )

        util.writeDataToFile( file,
                              data.happyMushroomVendingOffset4,
                              struct.pack( data.happyMushroomVendingPriceFormat, data.happyMushroomVendingPriceValue ),
                              self.logger )

        for ofst in data.happyMushroomVendingOffset5:
            util.writeDataToFile( file,
                                  ofst,
                                  struct.pack( data.happyMushroomVendingFormat5, data.happyMushroomVendingValue5 ),
                                  self.logger )
