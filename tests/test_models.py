# Author: Christoph Merscher <dev@fmerscher.com>

import unittest

import digimon.data as data
from digimon.models import Digimon, Item, Tech


class FakeLogger:
    def __init__( self ):
        self.errors = []

    def logError( self, message ):
        self.errors.append( message )


class FakeHandler:
    def __init__( self ):
        self.logger = FakeLogger()
        self.randomizedRequirements = False
        self.digimonData = []

    def getTypeName( self, id ):
        return "type-" + str( id )

    def getLevelName( self, id ):
        return "level-" + str( id )

    def getItemName( self, id ):
        return "item-" + str( id )

    def getSpecialtyName( self, id ):
        return "spec-" + str( id )

    def getTechName( self, id ):
        if( id == 0xFF ):
            return "None"
        return "tech-" + str( id )

    def getDigimonName( self, id ):
        return "digimon-" + str( id )

    def getPlayableDigimonByLevel( self, level ):
        return [ digi for digi in self.digimonData if digi.level == level ]

    def getRangeName( self, id ):
        return "range-" + str( id )

    def getEffectName( self, id ):
        return "effect-" + str( id )


def _encodedName( name ):
    return name.encode( 'ascii' ) + ( b'\0' * ( 20 - len( name ) ) )


def _makeDigimon( id=3, name='Agumon', level=data.levelsByName[ 'ROOKIE' ], height=0x1234 ):
    handler = FakeHandler()
    readData = (
        _encodedName( name ),
        123,
        4,
        height,
        1,
        level,
        0,
        1,
        2,
        5,
        30,
        *range( 16 )
    )

    return Digimon( handler, id, readData )


class DigimonModelTests( unittest.TestCase ):
    def test_parses_core_fields_and_packs_updated_height( self ):
        digi = _makeDigimon()

        self.assertEqual( digi.name, 'Agumon' )
        self.assertEqual( digi.models, 123 )
        self.assertEqual( digi.radius, 4 )
        self.assertEqual( digi.pp, 1 )
        self.assertEqual( digi.height, 0x1235 )
        self.assertEqual( digi.spec, [ 0, 1, 2 ] )
        self.assertEqual( digi.item, 5 )
        self.assertEqual( digi.drop_rate, 30 )
        self.assertEqual( digi.tech, list( range( 16 ) ) )

        self.assertEqual(
            digi.unpackedFormat(),
            ( b'Agumon', 123, 4, 0x1235, 1, data.levelsByName[ 'ROOKIE' ],
              0, 1, 2, 5, 30, *range( 16 ) )
        )

    def test_prosperity_points_match_original_level_rules( self ):
        cases = (
            ( 'Numemon', data.levelsByName[ 'FRESH' ], 1 ),
            ( 'Agumon', data.levelsByName[ 'ROOKIE' ], 1 ),
            ( 'Greymon', data.levelsByName[ 'CHAMPION' ], 2 ),
            ( 'MetalGreymon', data.levelsByName[ 'ULTIMATE' ], 3 ),
            ( 'Botamon', data.levelsByName[ 'FRESH' ], 0 ),
        )

        for name, level, expectedPP in cases:
            with self.subTest( name=name ):
                digi = _makeDigimon( name=name, level=level, height=0x1200 )
                self.assertEqual( digi.pp, expectedPP )
                self.assertEqual( digi.height & 0x0003, expectedPP )

    def test_evolution_data_round_trips_through_unpackers( self ):
        digi = _makeDigimon( id=12 )

        digi.setEvoData( tuple( range( 11 ) ) )
        self.assertEqual( digi.fromEvo, [ 0, 1, 2, 3, 4 ] )
        self.assertEqual( digi.toEvo, [ 5, 6, 7, 8, 9, 10 ] )
        self.assertEqual( digi.unpackedEvoFormat(), tuple( range( 11 ) ) )

        digi.setEvoStats( ( 10, 20, 30, 40, 50, 60, 12 ) )
        self.assertEqual( digi.evoStats, [ 10, 20, 30, 40, 50, 60 ] )
        self.assertEqual( digi.unpackedEvoStatsFormat(), ( 10, 20, 30, 40, 50, 60, 12 ) )

        digi.setEvoReqs( ( 99, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 0x0011 ) )
        self.assertTrue( digi.evoMaxBattles )
        self.assertTrue( digi.evoMaxCareMistakes )
        self.assertEqual(
            digi.unpackedEvoReqFormat(),
            ( 99, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 17 )
        )

    def test_evolution_helpers_preserve_slot_ordering( self ):
        source = _makeDigimon( id=1, level=data.levelsByName[ 'ROOKIE' ] )
        target = _makeDigimon( id=2, level=data.levelsByName[ 'CHAMPION' ] )
        other = _makeDigimon( id=3, level=data.levelsByName[ 'ROOKIE' ] )

        source.toEvo[ 2 ] = target.id
        other.toEvo[ 3 ] = target.id
        target.handler.digimonData = [ source, target, other ]

        target.updateEvosFrom()

        self.assertEqual( target.fromEvo, [ 0xFF, 3, 1, 0xFF, 0xFF ] )


class ItemModelTests( unittest.TestCase ):
    def test_parses_item_flags_and_packs_values( self ):
        item = Item( FakeHandler(), 0x47, ( _encodedName( 'EvoItem' ), 1000, 2, 0x04, 3, True ) )

        self.assertEqual( item.name, 'EvoItem' )
        self.assertTrue( item.isEvo )
        self.assertTrue( item.isConsumable )
        self.assertFalse( item.isQuest )
        self.assertFalse( item.isBanned )
        self.assertEqual( item.unpackedFormat(), ( b'EvoItem', 1000, 2, 0x04, 3, True ) )

    def test_special_food_and_banned_item_rules_are_preserved( self ):
        steak = Item( FakeHandler(), 0x7A, ( _encodedName( 'Steak' ), 500, 0, 0x00, 0, False ) )
        banned = Item( FakeHandler(), 0x53, ( _encodedName( 'Banned' ), 500, 0, 0x00, 0, False ) )

        self.assertTrue( steak.isFood )
        self.assertTrue( banned.isBanned )


class TechModelTests( unittest.TestCase ):
    def test_parses_tech_fields_and_packs_values( self ):
        tech = Tech( FakeHandler(), 0x10, ( 1, 2, 100, 4, 5, 1, 0, 2, 95, 50, 11 ) )

        self.assertTrue( tech.isDamaging )
        self.assertFalse( tech.isFinisher )
        self.assertTrue( tech.isLearnable )
        self.assertEqual( tech.unpackedFormat(), ( 1, 2, 100, 4, 5, 1, 0, 2, 95, 50, 11 ) )

        tech.learnChance = [ 10, 20, 30 ]
        tech.setName( 'Giga Freeze' )

        self.assertEqual( tech.name, 'Giga Freeze' )
        self.assertEqual( tech.unpackedLearnFormat(), ( 10, 20, 30 ) )

    def test_finisher_and_bubble_moves_are_not_learnable( self ):
        finisher = Tech( FakeHandler(), 0x3A, ( 0, 0, 100, 0, 0, 1, 0, 0, 0, 0, 0 ) )
        bubble = Tech( FakeHandler(), 0x71, ( 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0 ) )

        self.assertTrue( finisher.isFinisher )
        self.assertFalse( finisher.isLearnable )
        self.assertFalse( bubble.isLearnable )


if( __name__ == '__main__' ):
    unittest.main()
