# Author: Tristan Challener <challenert@gmail.com>
# Copyright: please don't steal this that is all

"""
Helpers for loading and interpreting randomizer settings.
"""

import json
from json import JSONDecodeError

from digimon.data import levels


DEFAULT_ITEM_VALUE_CUTOFF = "10000"


class SettingsError( Exception ):
    """
    Base exception for settings problems that can be shown directly
    to the user.
    """


class SettingsJsonError( SettingsError ):
    """
    Settings failed JSON parsing.
    """

    def __init__( self, error ):
        super().__init__( "Failed to parse JSON" )
        self.error = error


def loadSettings( settings ):
    """
    Parse the JSON settings passed by the GUI or CLI.
    """

    if( settings == '' ):
        raise SettingsError( 'Settings file must be provided at command line.  Use [-h] for help.' )

    try:
        return json.loads( settings )
    except JSONDecodeError as err:
        raise SettingsJsonError( err )


def getRequiredGeneralSetting( config, key, missingMessage ):
    """
    Read a required setting from the general config section.
    """

    value = config[ 'general' ][ key ]
    if( value != '' ):
        return value

    raise SettingsError( missingMessage )


def getPriceCutoff( sectionConfig ):
    """
    Read the optional value-matching cutoff for item randomization.
    """

    if( sectionConfig[ 'MatchValue' ] ):
        return sectionConfig[ 'ValuableItemCutoff' ]

    return DEFAULT_ITEM_VALUE_CUTOFF


def getAllowedStarterLevels( starterConfig ):
    """
    Convert the starter level toggles into the list of allowed level IDs.
    """

    levelsMask = [
        starterConfig[ 'Fresh' ],
        starterConfig[ 'InTraining' ],
        starterConfig[ 'Rookie' ],
        starterConfig[ 'Champion' ],
        starterConfig[ 'Ultimate' ]
    ]

    return [ level for enabled, level in zip( levelsMask, list( levels.keys() ) ) if enabled ]
