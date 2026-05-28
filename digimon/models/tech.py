# Author: Tristan Challener <challenert@gmail.com>
# Copyright: please don't steal this that is all

"""
Technique ROM data model.
"""


class Tech:
    """
    Tech data object.  Stores all data about a given
    tech.  Currently only names (read ONLY)
    """

    finishers = list( range( 0x3A, 0x71 ) )
    bubbles = list( range( 0x71, 0x79 ) )
    altTechs = [ 0x30, 0x39 ]

    def __init__( self, handler, id, data ):
        """
        Separate out composite data into individual
        components.

        Keyword arguments:
        data -- List of values (unpacked from data string).
        """

        self.handler  = handler
        self.id       = id

        self.name     = 'None'
        self.tier     = 0xFF
        self.learnChance = [ 0, 0, 0 ]

        self.unkn1    = data[ 0 ]
        self.aiDist   = data[ 1 ]
        self.power    = data[ 2 ]
        self.mp3      = data[ 3 ]
        self.itime    = data[ 4 ]
        self.range    = data[ 5 ]
        self.spec     = data[ 6 ]
        self.effect   = data[ 7 ]
        self.accuracy = data[ 8 ]
        self.effChance= data[ 9 ]
        self.unkn2    = data[ 10 ]


        self.isDamaging = self.power > 0
        self.isFinisher = self.id in self.finishers
        self.isLearnable = ( not self.isFinisher ) and ( self.id not in self.bubbles )


    def __str__( self ):
        """
        Produce a string representation of the object
        for convenient logging.
        """

        out = '{:>3d} {:<20s} (Tier: {:<2d}) {:<2d}% {:<2d}% {:<2d}%\n   {:>3d} {:>3d} {:>2d} {:>5s} {:>6s} {:>7s} {:>3d} {:>3d}% {:>2d}'.format(
                        self.id,
                        self.name,
                        self.tier,
                        self.learnChance[ 0 ],
                        self.learnChance[ 1 ],
                        self.learnChance[ 2 ],
                        self.power,
                        self.mp3 * 3,
                        self.itime,
                        self.handler.getRangeName( self.range ),
                        self.handler.getSpecialtyName( self.spec ),
                        self.handler.getEffectName( self.effect ),
                        self.accuracy,
                        self.effChance,
                        self.aiDist )

        return out


    def unpackedFormat( self ):
        """
        Produce a tuple representation of all
        of the data in the object.
        """
        repr = []

        repr.append( self.unkn1 )
        repr.append( self.aiDist )
        repr.append( self.power )
        repr.append( self.mp3 )
        repr.append( self.itime )
        repr.append( self.range )
        repr.append( self.spec )
        repr.append( self.effect )
        repr.append( self.accuracy )
        repr.append( self.effChance )
        repr.append( self.unkn2 )

        return tuple( repr )

    def unpackedLearnFormat( self ):
        """
        Produce a tuple representation of the
        learn chances for the object.
        """

        return tuple( self.learnChance )


    def setName( self, name ):
        """
        Assign a name to the tech

        Keyword arguments:
        name -- Name to set.
        """

        self.name     = name
