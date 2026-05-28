# Author: Tristan Challener <challenert@gmail.com>
# Copyright: please don't steal this that is all

"""
Registry for ROM patches that can be applied by DigimonWorldHandler.
"""


def applyPatches( handler, file ):
    """
    Apply each queued patch and report whether Toy Town special evolution
    writes need the unlock-area workaround.
    """

    toyTownWorkaround = False

    for patch, val in handler.patches:
        patchHandler = PATCH_HANDLERS.get( patch )
        if( patchHandler is None ):
            handler.logger.logError( 'Error: unknown patch "' + str( patch ) + '".' )
            continue

        methodName, useValue = patchHandler
        method = getattr( handler, methodName )
        if( useValue ):
            method( file, val )
        else:
            method( file )

        if( patch in TOY_TOWN_WORKAROUND_PATCHES ):
            toyTownWorkaround = True

    return toyTownWorkaround


PATCH_HANDLERS = {
    'fixEvoItems': ( '_applyPatchFixEvoItems', False ),
    'allowDrop': ( '_applyPatchAllowDrop', False ),
    'woah': ( '_applyPatchWoah', False ),
    'learnTierOne': ( '_applyPatchLearnTierOne', False ),
    'upLearnChance': ( '_applyPatchLearnChance', False ),
    'gabumon': ( '_applyPatchGabumon', False ),
    'giromon': ( '_applyPatchGiromon', False ),
    'spawn': ( '_applyPatchSpawn', True ),
    'hash': ( '_applyPatchIntroHash', True ),
    'intro': ( '_applyPatchIntroSkip', False ),
    'slots': ( '_applyPatchUnrigSlots', False ),
    'unlock': ( '_applyPatchUnlockAreas', False ),
    'pp': ( '_applyPatchPP', False ),
    'ogremon': ( '_applyPatchOgremonSoftlock', False ),
    'softlock': ( '_applyPatchMovementSoftlock', False ),
    'typeEffectiveness': ( '_randomizeTypeEffectiveness', False ),
    'learnmoveandcommand': ( '_applyPatchLearnMoveAndCommand', False ),
    'fixDVChips': ( '_applyPatchDVChipDescription', False ),
    'happyVending': ( '_applyPatchGuaranteeHappyShrm', False ),
}

TOY_TOWN_WORKAROUND_PATCHES = ( 'unlock', )
