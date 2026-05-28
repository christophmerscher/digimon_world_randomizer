# Author: Tristan Challener <challenert@gmail.com>
# Copyright: please don't steal this that is all

"""
Digimon ROM data model.
"""

import digimon.data as data


class Digimon:
    """
    Digimon data object.  Stores all data about a given
    digimon.  (currently does not include raise data or
    evolution data)
    """

    playableDigimon = list( range( 0x01, 0x3E ) ) + [ 0x3F, 0x40, 0x41 ]


    def __init__( self, handler, id, readData ):
        """
        Separate out composite data into individual
        components.

        Keyword arguments:
        readData -- List of values (unpacked from data string).
        """

        self.handler   = handler
        self.id        = id

        #decode binary data as ascii and trim trailing nulls
        self.name      = readData[ 0 ].decode( 'ascii' ).rstrip( '\0' )
        self.models    = readData[ 1 ]
        self.radius    = readData[ 2 ]
        self.height    = readData[ 3 ]
        self.type      = readData[ 4 ]
        self.level     = readData[ 5 ]

        if self.name == "Numemon" or self.name == "Sukamon" or self.name == "Nanimon":
            self.pp = 1
        elif self.level == data.levelsByName[ "ROOKIE" ]:
            self.pp = 1
        elif self.level == data.levelsByName[ "CHAMPION" ]:
            self.pp = 2
        elif self.level == data.levelsByName["ULTIMATE" ]:
            self.pp = 3
        else:
            self.pp = 0

        #update height to store PP value
        self.height = ( self.height & 0xFFFC ) | self.pp

        self.spec = []
        for i in range( 3 ):
            self.spec.append( readData[ 6 + i ] )

        self.item      = readData[ 9 ]
        self.drop_rate = readData[ 10 ]

        self.tech = []
        for i in range( 16 ):
            self.tech.append( readData[ 11 + i ] )

        self.fromEvo = []
        for i in range( 5 ):
            self.fromEvo.append( 0xFF )

        self.toEvo = []
        for i in range( 6 ):
            self.toEvo.append( 0xFF )

        self.evoStats = []
        for i in range( 6 ):
            self.evoStats.append( 0xFFFF )

        self.evoStatReqs = []
        for i in range( 6 ):
            self.evoStatReqs.append( 0xFFFF )


        self.evoBonusDigi    = 0xFFFF
        self.evoCareMistakes = 0xFFFF
        self.evoWeight       = 0xFFFF
        self.evoDiscipline   = 0xFFFF
        self.evoHappiness    = 0xFFFF
        self.evoBattles      = -1
        self.evoTechs        = 0xFFFF
        self.evoFlags        = 0xFFFF

        self.evoMaxBattles   = True
        self.evoMaxCareMistakes = True


    def __str__( self ):
        """
        Produce a string representation of the object
        for convenient logging.
        """

        type  = self.handler.getTypeName( self.type )
        level = self.handler.getLevelName( self.level )
        item  = self.handler.getItemName( self.item )

        spec = []
        for i in range( 3 ):
            spec.append( self.handler.getSpecialtyName( self.spec[ i ] ) )

        out = '{:>3d}{:>20s} {:>5d}{:>5d}{:>5d} {:>9s} {:>11s} {:>6s} {:>6s} {:>6s} {:>12s} {:>3d}% {:>1d}\n{:>23s} '.format(
                        self.id,
                        self.name.rstrip(' \t\r\n\0'),
                        self.models,
                        self.radius,
                        self.height,
                        type,
                        level,
                        spec[ 0 ], spec[ 1 ], spec[ 2 ],
                        item,
                        self.drop_rate,
                        self.pp,
                        "" )

        for i in range( 16 ):
            if( self.tech[ i ] != 'None' ):
                out += self.handler.getTechName( self.tech[ i ] )
            if( i == 15 or self.handler.getTechName( self.tech[ i + 1 ] ) == 'None' ):
                break
            out +=  ', '

        return out


    def setEvoData( self, data ):
        """
        Separate out composite data into individual
        components and attach to existing Digimon.

        Keyword arguments:
        data -- List of values (unpacked from data string).
        """


        for i in range( 5 ):
            self.fromEvo[ i ] = data[ i ]

        for i in range( 6 ):
            self.toEvo[ i ] = data[ 5 + i ]


    def evoData( self ):
        """
        Produce a string representation of the Digimon's evo
        data for convenient logging.
        """

        out = self.name + '\nNow evolves from '

        for i in range( 5 ):
            out += self.handler.getDigimonName( self.fromEvo[ i ] ) + ' '

        out += '\nNow evolves to '

        for i in range( 6 ):
            out += self.handler.getDigimonName( self.toEvo[ i ] ) + ' '

        return out


    def setEvoStats( self, data ):
        """
        Separate out composite data into individual
        components and attach to existing Digimon.

        Keyword arguments:
        data -- List of values (unpacked from data string).
        """


        if( data[ 6 ] != self.id ):
            self.handler.logger.logError( 'Error: trying to attach evo stats for ' + str( data[ 6 ] ) + ' to ' + str( self.id ) )
            return

        for i in range( 6 ):
            self.evoStats[ i ] = data[ i ]


    def evoStatsToString( self ):
        """
        Produce a string representation of the Digimon's evo
        stats for convenient logging.
        """

        out = self.name + '\nNow gains stats: '

        for i in range( 6 ):
            out += str( self.evoStats[ i ] ) + ' '

        return out


    def setEvoReqs( self, data ):
        """
        Separate out composite data into individual
        components and attach to existing Digimon.

        Keyword arguments:
        data -- List of values (unpacked from data string).
        """

        maxBattlesFlag = 0x0001
        maxCareMistakesFlag = 0x0010

        self.evoBonusDigi = data[ 0 ]

        for i in range( 6 ):
            self.evoStatReqs[ i ] = data[ 1 + i ]

        self.evoCareMistakes = data[ 7 ]
        self.evoWeight       = data[ 8 ]
        self.evoDiscipline   = data[ 9 ]
        self.evoHappiness    = data[ 10 ]
        self.evoBattles      = data[ 11 ]
        self.evoTechs        = data[ 12 ]
        self.evoFlags        = data[ 13 ]

        self.evoMaxBattles   = ( self.evoFlags & maxBattlesFlag ) == maxBattlesFlag
        self.evoMaxCareMistakes = ( self.evoFlags & maxCareMistakesFlag ) == maxCareMistakesFlag


    def evoReqsToString( self ):
        """
        Produce a string representation of the Digimon's evo
        requirements for convenient logging.
        """

        out = self.name + '\'s evo requirements are: \n'


        out += 'Stats: {:s}{:s}{:s}{:s}{:s}{:s}'.format(
                                'HP >= ' + str( self.evoStatReqs[ 0 ] * 10 )+ '   ' if self.evoStatReqs[ 0 ] != 0xFFFF else '',
                                'MP >= ' + str( self.evoStatReqs[ 1 ] * 10 )+ '   ' if self.evoStatReqs[ 1 ] != 0xFFFF else '',
                                'OFF >= ' + str( self.evoStatReqs[ 2 ] )+ '   ' if self.evoStatReqs[ 2 ] != 0xFFFF else '',
                                'DEF >= ' + str( self.evoStatReqs[ 3 ] )+ '   ' if self.evoStatReqs[ 3 ] != 0xFFFF else '',
                                'SPD >= ' + str( self.evoStatReqs[ 4 ] )+ '   ' if self.evoStatReqs[ 4 ] != 0xFFFF else '',
                                'BRN >= ' + str( self.evoStatReqs[ 5 ] )+ '   ' if self.evoStatReqs[ 5 ] != 0xFFFF else ''
                                )

        out += '\n'

        if( self.evoCareMistakes != 0xFFFF ):
            if( self.evoMaxCareMistakes ):
                out +='Had at most ' + str( self.evoCareMistakes ) + ' care mistake(s) at current level\n'
            else:
                out +='Had at least ' + str( self.evoCareMistakes ) + ' care mistake(s) at current level\n'

        if( self.evoWeight != 0xFFFF ):
            out += 'Weight is in range ' + str( self.evoWeight - 5 ) + '-' + str( self.evoWeight + 5 ) + '\n'

        out += 'One of the following bonus requirements: \n'

        if( self.evoBonusDigi != 0xFFFF ):
            out += 'Current digimon is ' + self.handler.getDigimonName( self.evoBonusDigi ) + '\n'

        if( self.evoDiscipline != 0xFFFF ):
            out +='Discipline is at least ' + str( self.evoDiscipline ) + '\n'

        if( self.evoHappiness != 0xFFFF ):
            out +='Happiness is at least ' + str( self.evoHappiness ) + '\n'

        if( self.evoBattles != -1 ):
            if( self.evoMaxBattles ):
                out +='Particpated in at most ' + str( self.evoBattles ) + ' battle(s) at current level\n'
            else:
                out +='Participated in at least ' + str( self.evoBattles ) + ' battle(s) at current level\n'

        if( self.evoTechs != 0xFFFF ):
            out +='Learned at least ' + str( self.evoTechs ) + ' techs\n'


        return out


    def unpackedFormat( self ):
        """
        Produce a tuple representation of all
        of the data in the object.
        """
        repr = []

        repr.append( self.name.encode( 'ascii' ) )  # 0
        repr.append( self.models )                  # 1
        repr.append( self.radius )                  # 2
        repr.append( self.height )                  # 3
        repr.append( self.type )                    # 4
        repr.append( self.level )                   # 5

        for spec in self.spec:
            repr.append( spec )                     # 6 7 8

        repr.append( self.item )                    # 9
        repr.append( self.drop_rate )               # 10

        for tech in self.tech:
            repr.append( tech )                     # 11+

        return tuple( repr )


    def unpackedEvoFormat( self ):
        """
        Produce a tuple representation of the evo
        data for the object.
        """

        repr = []

        for e in self.fromEvo:
            repr.append( e )

        for e in self.toEvo:
            repr.append( e )

        return tuple( repr )


    def unpackedEvoStatsFormat( self ):
        """
        Produce a tuple representation of the evo
        stat gain data for the object.
        """

        repr = []

        for i in range( 6 ):
            repr.append( self.evoStats[ i ] )

        repr.append( self.id )

        return tuple( repr )


    def unpackedEvoReqFormat( self ):
        """
        Produce a tuple representation of the evo
        requirement data for the object.
        """

        repr = []
        repr.append( self.evoBonusDigi )

        for i in range( 6 ):
            repr.append( self.evoStatReqs[ i ] )

        repr.append( self.evoCareMistakes )
        repr.append( self.evoWeight )
        repr.append( self.evoDiscipline )
        repr.append( self.evoHappiness )
        repr.append( self.evoBattles )
        repr.append( self.evoTechs )

        flags = ( 1 if self.evoMaxBattles else 0 ) + ( 16 if self.evoMaxCareMistakes else 0 )

        repr.append( flags )

        return tuple( repr )


    def getEvoToCount( self ):
        """
        Get current number of digimon this digimon
        can evolve to.
        """

        sum = 0
        for e in self.toEvo:
            if( e != 0xFF ):
                sum += 1

        return sum


    def getEvoFromCount( self ):
        """
        Get current number of digimon this digimon
        can evolve from.
        """

        sum = 0
        for e in self.fromEvo:
            if( e != 0xFF ):
                sum += 1

        return sum


    def clearEvos( self ):
        """
        Clear all of this digimon's evos to/from.
        """

        for i in range( 5 ):
            self.fromEvo[ i ] = 0xFF

        for i in range( 6 ):
            self.toEvo[ i ] = 0xFF


    def clearEvoReqs( self ):
        """
        Clear all of this digimon's evo requirements.
        """

        for i in range( 6 ):
            self.evoStatReqs[ i ] = 0xFFFF


        self.evoBonusDigi    = 0xFFFF
        self.evoCareMistakes = 0xFFFF
        self.evoWeight       = 0xFFFF
        self.evoDiscipline   = 0xFFFF
        self.evoHappiness    = 0xFFFF
        self.evoBattles      = -1
        self.evoTechs        = 0xFFFF
        self.evoFlags        = 0xFFFF

        self.evoMaxBattles   = True
        self.evoMaxCareMistakes = True


    def updateEvosFrom( self ):
        """
        Update this digimon's list of digimon that
        can evolve into it.
        """

        evos = []
        for digi in self.handler.digimonData:
            if( self.id in digi.toEvo ):
                evos.append( digi.id )

        #This is the order in which evos are filled
        #i.e. if there are two evos, they are in
        #the 3rd slot and the 2nd slot (#2, #1)
        #Copy up to 5 evos in.  If less, fill with
        #0xFF, aka none.  Truncate extras.
        for i, j in enumerate( [ 2, 1, 3, 0, 4 ] ):
            if( i < len( evos ) ):
                self.fromEvo[ j ] = evos[ i ]
            else:
                self.fromEvo[ j ] = 0xFF


    def validEvosTo( self ):
        """
        Produce list of valid digimon IDs that this
        digimon could potentially evolve to.
        """

        #Find all digimon that are playable and one level above
        validEvos = self.handler.getPlayableDigimonByLevel( self.level + 1 )

        alwaysInvalid = [ 'Kunemon', 'Numemon', 'Sukamon', 'Nanimon', 'Vademon',
                          'Panjyamon', 'Gigadramon', 'MetalEtemon' ]
        if( not self.handler.randomizedRequirements ):
            alwaysInvalid.append( 'Devimon' )

        i = 0
        while( i < len( validEvos ) ):
            #Panjyamon, Gigadramon, and MetalEtemon don't have digivolution requirements.
            if( validEvos[ i ].name in alwaysInvalid ):
                del validEvos[ i ]
            else:
                i += 1


        return validEvos


    def addEvoTo( self, id ):
        """
        Add a new evolution target to this digimon.

        Keyword arguments:
        id -- ID of digimon to add as evolution.
        """

        #Search in the order that evos are filled
        for i in [ 2, 3, 1, 4, 0, 5 ]:
            #If this digimon already has this evo,
            #don't add it again.
            if( self.toEvo[ i ] == id ):
                break

            #If we found an empty slot and the
            #digimon doesn't have this evo, add
            #it to the list.
            if( self.toEvo[ i ] == 0xFF ):
                self.toEvo[ i ] = id
                break
