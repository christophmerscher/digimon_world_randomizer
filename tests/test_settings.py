# Author: Christoph Merscher <dev@fmerscher.com>

import io
import json
import unittest
from contextlib import redirect_stdout

import digimon.data as data
from digimon_randomize import main
from digimon.settings_schema import SettingsValidationError, validateSettings
from digimon.settings import (
    DEFAULT_ITEM_VALUE_CUTOFF,
    SettingsError,
    SettingsJsonError,
    getAllowedStarterLevels,
    getPriceCutoff,
    getRequiredGeneralSetting,
    loadSettings,
)


def _validConfig():
    return {
        'general': {
            'InputFile': 'input.bin',
            'OutputFile': 'output.bin',
            'LogLevel': 'casual',
            'Hash': 'abc123',
        },
        'digimon': {
            'Enabled': False,
            'DroppedItem': False,
            'DropRate': False,
            'MatchValue': False,
            'ValuableItemCutoff': 1000,
        },
        'techs': {
            'Enabled': False,
            'RandomizationMode': 'random',
            'Power': False,
            'Cost': False,
            'Accuracy': False,
            'Effect': False,
            'EffectChance': False,
            'TypeEffectiveness': False,
        },
        'starter': {
            'Enabled': False,
            'UseWeakestTech': False,
            'Fresh': False,
            'InTraining': False,
            'Rookie': True,
            'Champion': False,
            'Ultimate': False,
            'Digimon': 'Random',
        },
        'recruitment': {
            'Enabled': False,
        },
        'chests': {
            'Enabled': False,
            'AllowEvolutionItems': False,
        },
        'tokomon': {
            'Enabled': False,
            'ConsumableOnly': False,
        },
        'techGifts': {
            'Enabled': False,
        },
        'mapItems': {
            'Enabled': False,
            'FoodOnly': False,
            'MatchValue': False,
            'ValuableItemCutoff': 1000,
        },
        'evolution': {
            'Enabled': False,
            'Requirements': False,
            'SpecialEvolutions': False,
            'ObtainAllMode': False,
        },
        'patches': {
            'Enabled': False,
            'EvoItemStatGain': False,
            'QuestItemsDroppable': False,
            'BrainTrainTierOne': False,
            'JukeboxGlitch': False,
            'IncreaseLearnChance': False,
            'SpawnRateEnabled': False,
            'SpawnRate': 3,
            'ShowHashIntro': False,
            'SkipIntro': False,
            'Woah': False,
            'Gabu': False,
            'Softlock': False,
            'UnlockAreas': False,
            'UnrigSlots': False,
            'LearnMoveAndCommand': False,
            'FixDVChips': False,
            'HappyVending': False,
        },
    }


class SettingsTests( unittest.TestCase ):
    def test_load_settings_reports_empty_and_invalid_json( self ):
        with self.assertRaises( SettingsError ):
            loadSettings( '' )

        with self.assertRaises( SettingsJsonError ):
            loadSettings( '{' )

    def test_required_general_setting_preserves_original_validation( self ):
        config = { 'general': { 'InputFile': 'in.bin', 'OutputFile': '' } }

        self.assertEqual( getRequiredGeneralSetting( config, 'InputFile', 'missing' ), 'in.bin' )

        with self.assertRaisesRegex( SettingsError, 'output missing' ):
            getRequiredGeneralSetting( config, 'OutputFile', 'output missing' )

    def test_price_cutoff_defaults_when_value_matching_is_disabled( self ):
        self.assertEqual(
            getPriceCutoff( { 'MatchValue': False, 'ValuableItemCutoff': 250 } ),
            DEFAULT_ITEM_VALUE_CUTOFF
        )
        self.assertEqual(
            getPriceCutoff( { 'MatchValue': True, 'ValuableItemCutoff': 250 } ),
            250
        )

    def test_allowed_starter_levels_follow_original_toggle_order( self ):
        starterConfig = {
            'Fresh': True,
            'InTraining': False,
            'Rookie': True,
            'Champion': False,
            'Ultimate': True,
        }

        self.assertEqual(
            getAllowedStarterLevels( starterConfig ),
            [
                data.levelsByName[ 'FRESH' ],
                data.levelsByName[ 'ROOKIE' ],
                data.levelsByName[ 'ULTIMATE' ],
            ]
        )

    def test_validate_settings_accepts_gui_settings_shape( self ):
        validateSettings( _validConfig() )

    def test_validate_settings_reports_missing_required_section( self ):
        config = _validConfig()
        del config[ 'techs' ]

        with self.assertRaises( SettingsValidationError ) as context:
            validateSettings( config )

        self.assertIn( '$.techs is required', str( context.exception ) )

    def test_validate_settings_reports_wrong_type_and_bounds( self ):
        config = _validConfig()
        config[ 'patches' ][ 'SpawnRate' ] = 'fast'
        config[ 'digimon' ][ 'ValuableItemCutoff' ] = 10001

        with self.assertRaises( SettingsValidationError ) as context:
            validateSettings( config )

        self.assertIn( '$.patches.SpawnRate must be integer', str( context.exception ) )
        self.assertIn( '$.digimon.ValuableItemCutoff must be at most 10000', str( context.exception ) )

    def test_validate_settings_reports_empty_required_file_paths( self ):
        config = _validConfig()
        config[ 'general' ][ 'InputFile' ] = ''
        config[ 'general' ][ 'OutputFile' ] = ''

        with self.assertRaises( SettingsValidationError ) as context:
            validateSettings( config )

        self.assertIn( '$.general.InputFile must not be empty', str( context.exception ) )
        self.assertIn( '$.general.OutputFile must not be empty', str( context.exception ) )

    def test_validate_settings_reports_cross_field_rules( self ):
        config = _validConfig()
        del config[ 'general' ][ 'Hash' ]
        config[ 'patches' ][ 'ShowHashIntro' ] = True
        config[ 'starter' ][ 'Enabled' ] = True
        config[ 'starter' ][ 'Rookie' ] = False

        with self.assertRaises( SettingsValidationError ) as context:
            validateSettings( config )

        self.assertIn( '$.general.Hash is required when $.patches.ShowHashIntro is true', str( context.exception ) )
        self.assertIn( '$.starter must enable at least one starter level', str( context.exception ) )

    def test_main_validates_schema_before_running_randomizer( self ):
        config = _validConfig()
        del config[ 'techs' ]
        output = io.StringIO()

        with redirect_stdout( output ):
            result = main( [ '-settings', json.dumps( config ) ] )

        self.assertEqual( result, 1 )
        self.assertIn( 'Settings validation failed', output.getvalue() )
        self.assertIn( '$.techs is required', output.getvalue() )


if( __name__ == '__main__' ):
    unittest.main()
