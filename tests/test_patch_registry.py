# Author: Christoph Merscher <dev@fmerscher.com>

import unittest

import digimon.patch_registry as patch_registry


class FakeLogger:
    def __init__( self ):
        self.errors = []

    def logError( self, message ):
        self.errors.append( message )


class FakePatchHandler:
    def __init__( self, patches ):
        self.patches = patches
        self.logger = FakeLogger()
        self.calls = []

    def _applyPatchFixEvoItems( self, file ):
        self.calls.append( ( 'fixEvoItems', file ) )

    def _applyPatchSpawn( self, file, val ):
        self.calls.append( ( 'spawn', file, val ) )

    def _applyPatchIntroHash( self, file, val ):
        self.calls.append( ( 'hash', file, val ) )

    def _applyPatchUnlockAreas( self, file ):
        self.calls.append( ( 'unlock', file ) )


class PatchRegistryTests( unittest.TestCase ):
    def test_dispatches_patch_methods_and_reports_toy_town_workaround( self ):
        file = object()
        handler = FakePatchHandler( [
            ( 'fixEvoItems', 0 ),
            ( 'spawn', 77 ),
            ( 'hash', 'settings-hash' ),
            ( 'unlock', 0 ),
        ] )

        toyTownWorkaround = patch_registry.applyPatches( handler, file )

        self.assertTrue( toyTownWorkaround )
        self.assertEqual(
            handler.calls,
            [
                ( 'fixEvoItems', file ),
                ( 'spawn', file, 77 ),
                ( 'hash', file, 'settings-hash' ),
                ( 'unlock', file ),
            ]
        )
        self.assertEqual( handler.logger.errors, [] )

    def test_unknown_patch_logs_error_and_keeps_applying_known_patches( self ):
        file = object()
        handler = FakePatchHandler( [
            ( 'missingPatch', 0 ),
            ( 'spawn', 3 ),
        ] )

        toyTownWorkaround = patch_registry.applyPatches( handler, file )

        self.assertFalse( toyTownWorkaround )
        self.assertEqual( handler.calls, [ ( 'spawn', file, 3 ) ] )
        self.assertEqual( len( handler.logger.errors ), 1 )
        self.assertIn( 'missingPatch', handler.logger.errors[ 0 ] )


if( __name__ == '__main__' ):
    unittest.main()
