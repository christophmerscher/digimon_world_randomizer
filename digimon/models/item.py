# Author: Tristan Challener <challenert@gmail.com>
# Copyright: please don't steal this that is all

"""
Item ROM data model.
"""


class Item:
    """
    Item data object.  Stores all data about a given
    item.
    """

    itemSort = {
            0x00 : 'HEAL',
            0x01 : 'STATUS',
            0x02 : 'FOOD',
            0x03 : 'BATTLE',
            0x04 : 'STATEVO',
            0x05 : 'PASSIVEQUEST'
            }

    consumableItems = list( range( 0x00, 0x21 ) ) + list( range( 0x26, 0x73 ) ) + [ 0x79, 0x7A, 0x7D, 0x7E, 0x7F ]
    questItems = list( range( 0x73, 0x79 ) ) + list( range( 0x7B, 0x7D ) )
    bannedItems = [ 0x53, 0x72 ]

    def __init__( self, handler, id, data ):
        """
        Separate out composite data into individual
        components.

        Keyword arguments:
        data -- List of values (unpacked from data string).
        """

        self.handler  = handler
        self.id       = id

        #decode binary data as ascii and trim trailing nulls
        self.name     = data[ 0 ].decode( 'ascii' ).rstrip( '\0' )
        self.price    = data[ 1 ]
        self.merit    = data[ 2 ]
        self.sort     = data[ 3 ]
        self.color    = data[ 4 ]
        self.dropable = data[ 5 ]

        #Exclude the Stat items, which share a sort value with the Evo items
        self.isEvo = ( self.itemSort[ self.sort ] == 'STATEVO' and id >= 0x47 )
        self.isConsumable = id in self.consumableItems

        #'Food' sort value is not used for 'Rain Plant' and 'Steak'
        self.isFood = self.itemSort[ self.sort ] == 'FOOD' or id == 0x79 or id == 0x7A

        self.isQuest = self.id in self.questItems

        self.isBanned = self.id in self.bannedItems


    def __str__( self ):
        """
        Produce a string representation of the object
        for convenient logging.
        """

        out = '{:>3d}{:>20s} {:>4d} {:>4d} {:>2d} {:>2d} {!r:>5}'.format(
                        self.id,
                        self.name,
                        self.price,
                        self.merit,
                        self.sort,
                        self.color,
                        self.dropable )

        return out


    def unpackedFormat( self ):
        """
        Produce a tuple representation of all
        of the data in the object.
        """
        repr = []

        repr.append( self.name.encode( 'ascii' ) )  # 0
        repr.append( self.price )                   # 1
        repr.append( self.merit )                   # 2
        repr.append( self.sort )                    # 3
        repr.append( self.color )                   # 4
        repr.append( self.dropable )                # 5

        return tuple( repr )
