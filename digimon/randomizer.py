# Author: Tristan Challener <challenert@gmail.com>
# Copyright: please don't steal this that is all

"""
High-level randomizer flow.
"""

import sys

from digimon.settings import getAllowedStarterLevels, getPriceCutoff, getRequiredGeneralSetting
from log.logger import Logger


LOG_FILENAME = 'randomize.log'
PRICE_CUTOFF_ERROR = 'Item price cutoff must be an integer. {0} is not a valid value.'


def runRandomizer( config ):
    """
    Run the complete randomization process for a parsed config.
    """

    inFile = getRequiredGeneralSetting( config, 'InputFile', 'ROM file section is required' )
    outFile = getRequiredGeneralSetting( config, 'OutputFile', 'Destination file section is required' )

    print( 'Reading data from ' + inFile + '...' )
    sys.stdout.flush()

    logger, handler = _createHandler( config, inFile )

    print( 'Modifying data...' )
    sys.stdout.flush()

    _applyRandomizationSettings( config, handler, logger )
    _writeOutput( handler, logger, outFile )
    _finishLog( handler, logger )


def _createHandler( config, inFile ):
    """
    Create the logger and ROM handler.
    """

    from digimon.handler import DigimonWorldHandler

    verbose = config[ 'general' ][ 'LogLevel' ]

    try:
        seedcfg = config[ 'general' ][ 'Seed' ]
        logger = Logger( verbose, filename=LOG_FILENAME )
        handler = DigimonWorldHandler( inFile, logger, seed=int( seedcfg ) )
    except ValueError:
        print( 'Seed must be an integer. ' + str( seedcfg ) + ' is not a valid value.' )
        raise SystemExit( 1 )
    except Exception as e:
        print( e )
        logger = Logger( verbose, filename=LOG_FILENAME )
        handler = DigimonWorldHandler( inFile, logger )

    return logger, handler


def _applyRandomizationSettings( config, handler, logger ):
    """
    Apply all enabled randomizer sections to the loaded ROM data.
    """

    if( config[ 'digimon' ][ 'Enabled' ] ):
        _randomizeDigimonData( config[ 'digimon' ], handler, logger )

    if( config[ 'techs' ][ 'Enabled' ] ):
        _randomizeTechData( config[ 'techs' ], handler )

    if( config[ 'starter' ][ 'Enabled' ] ):
        _randomizeStarters( config[ 'starter' ], handler )

    if( config[ 'recruitment' ][ 'Enabled' ] ):
        handler.randomizeRecruitments()

    if( config[ 'chests' ][ 'Enabled' ] ):
        handler.randomizeChestItems( allowEvo=config[ 'chests' ][ 'AllowEvolutionItems' ] )

    if( config[ 'tokomon' ][ 'Enabled' ] ):
        handler.randomizeTokomonItems( consumableOnly=config[ 'tokomon' ][ 'ConsumableOnly' ] )

    if( config[ 'techGifts' ][ 'Enabled' ] ):
        handler.randomizeTechGifts()

    if( config[ 'mapItems' ][ 'Enabled' ] ):
        _randomizeMapItems( config[ 'mapItems' ], handler, logger )

    if( config[ 'evolution' ][ 'Enabled' ] ):
        _randomizeEvolution( config[ 'evolution' ], handler )

    if( config[ 'patches' ][ 'Enabled' ] ):
        _applyPatchSettings( config, handler )


def _randomizeDigimonData( digimonConfig, handler, logger ):
    pricecfg = getPriceCutoff( digimonConfig )
    price = _parsePriceCutoff( pricecfg, logger )

    handler.randomizeDigimonData( dropItem=digimonConfig[ 'DroppedItem' ],
                                  dropRate=digimonConfig[ 'DropRate' ],
                                  price=price )


def _randomizeTechData( techConfig, handler ):
    handler.randomizeTechData( power=techConfig[ 'Power' ],
                               mode=techConfig[ 'RandomizationMode' ],
                               cost=techConfig[ 'Cost' ],
                               accuracy=techConfig[ 'Accuracy' ],
                               effect=techConfig[ 'Effect' ],
                               effectChance=techConfig[ 'EffectChance' ] )

    if( techConfig[ 'TypeEffectiveness' ] ):
        handler.applyPatch( 'typeEffectiveness' )


def _randomizeStarters( starterConfig, handler ):
    handler.randomizeStarters(
        useWeakestTech=starterConfig[ 'UseWeakestTech' ],
        forceDigimon=starterConfig[ 'Digimon' ],
        allowedLevels=getAllowedStarterLevels( starterConfig )
    )


def _randomizeMapItems( mapItemConfig, handler, logger ):
    pricecfg = getPriceCutoff( mapItemConfig )
    price = _parsePriceCutoff( pricecfg, logger )

    handler.randomizeMapSpawnItems( foodOnly=mapItemConfig[ 'FoodOnly' ], price=price )


def _randomizeEvolution( evolutionConfig, handler ):
    if( evolutionConfig[ 'Requirements' ] ):
        handler.randomizeEvolutionRequirements()

    handler.randomizeEvolutions( obtainAll=evolutionConfig[ 'ObtainAllMode' ] )

    if( evolutionConfig[ 'SpecialEvolutions' ] ):
        handler.randomizeSpecialEvolutions()
        handler.updateEvolutionStats()


def _applyPatchSettings( config, handler ):
    patches = config[ 'patches' ]

    if( patches[ 'EvoItemStatGain' ] ):
        handler.applyPatch( 'fixEvoItems' )

    if( patches[ 'QuestItemsDroppable' ] ):
        handler.applyPatch( 'allowDrop' )

    if( patches[ 'Woah' ] ):
        handler.applyPatch( 'woah' )

    if( patches[ 'BrainTrainTierOne' ] ):
        handler.applyPatch( 'learnTierOne' )

    if( patches[ 'JukeboxGlitch' ] ):
        handler.applyPatch( 'giromon' )

    if( patches[ 'IncreaseLearnChance' ] ):
        handler.applyPatch( 'upLearnChance' )

    if( patches[ 'Gabu' ] ):
        handler.applyPatch( 'gabumon' )

    if( patches[ 'SpawnRateEnabled' ] != '0' ):
        handler.applyPatch( 'spawn', int( patches[ 'SpawnRate' ] ) )

    if( patches[ 'ShowHashIntro' ] ):
        handler.applyPatch( 'hash', config[ 'general' ][ 'Hash' ] )

    if( patches[ 'SkipIntro' ] ):
        handler.applyPatch( 'intro' )

    if( patches[ 'UnlockAreas' ] ):
        handler.applyPatch( 'unlock' )

    if( patches[ 'UnrigSlots' ] ):
        handler.applyPatch( 'slots' )

    if( patches[ 'Softlock' ] ):
        handler.applyPatch( 'softlock' )

    if( patches[ 'LearnMoveAndCommand' ] ):
        handler.applyPatch( 'learnmoveandcommand' )

    if( patches[ 'FixDVChips' ] ):
        handler.applyPatch( 'fixDVChips' )

    if( patches[ 'HappyVending' ] ):
        handler.applyPatch( 'happyVending' )


def _parsePriceCutoff( pricecfg, logger ):
    try:
        return int( pricecfg )
    except ValueError:
        logger.fatalError( PRICE_CUTOFF_ERROR.format( str( pricecfg ) ) )


def _writeOutput( handler, logger, outFile ):
    print( 'Writing to ' + outFile + '...' )
    sys.stdout.flush()

    try:
        handler.write( outFile )
    except Exception as ex:
        logger.logError( 'System error: {0}'.format( ex ) )
        print( 'An irrecoverable error occured' )

    if( not logger.error ):
        print( 'Modifications completed successfully.  See log file for details (Warning: spoilers!).' )
        print( 'Seed was ' + str( handler.randomseed ) )
        print( 'Enter this seed in settings file to produce the same ROM again.' )
    else:
        print( 'Program ended with errors.  See log file for details.' )

    sys.stdout.flush()


def _finishLog( handler, logger ):
    logger.logAlways( logger.getHeader( 'Seed' ) )
    logger.logAlways( 'Seed was ' + str( handler.randomseed ) + '.' )
    logger.close()
    logger.rename( 'randomize-' + str( handler.randomseed ) + '.log' )
