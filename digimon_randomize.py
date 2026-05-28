# Author: Tristan Challener <challenert@gmail.com>
# Copyright: please don't steal this that is all

import argparse
import sys

from digimon.settings import SettingsError, SettingsJsonError, loadSettings


def main( argv=None ):
    """
    CLI entry point for randomizing a ROM from a JSON settings string.
    """

    if( argv is None ):
        argv = sys.argv[1:]

    args = argparse.ArgumentParser( description='Randomize Digimon World' )
    args.add_argument( '-settings', required=True, help='JSON settings string that configures the operation' )
    settings = args.parse_args( argv ).settings

    try:
        config = loadSettings( settings )
        from digimon.randomizer import runRandomizer
        runRandomizer( config )
    except SettingsJsonError as err:
        print( "Failed to parse JSON" )
        print( err.error )
        return 1
    except SettingsError as err:
        print( err )
        return 1

    return 0


if( __name__ == '__main__' ):
    raise SystemExit( main() )
