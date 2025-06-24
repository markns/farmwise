#!/usr/bin/env python3
"""
Script to load agronomy JSON data into the farmbase database.

This script loads:
- Crops from crops.json
- Pathogens from pathogens.json  
- Events from events.json
- Crop cycles from crop-cycle/*.json files

Usage:
    python scripts/load__data.py [--dry-run] [--verbose]
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any
import os

# Add the app directory to the Python path
# sys.path.insert(0, str(Path(__file__).parent.parent / "apps/farmbase/src"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from farmbase.config import settings
from farmbase.database.core import Base
from farmbase.agronomy.models import (
    Crop,
    Pathogen,
    PathogenImage,
    Event,
    CropCycle,
    CropStage,
    event_crop_association,
    event_pathogen_association,
    pathogen_crop_association,
)


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load JSON data from file."""
    print(f"Loading {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_crops_data(session, crops_data: List[Dict[str, Any]], verbose: bool = False) -> int:
    """Load crops data into database."""
    print("Loading crops data...")
    
    count = 0
    for crop_data in crops_data:
        try:
            # Check if crop already exists
            existing_crop = session.get(Crop, crop_data['host_id'])
            if existing_crop:
                if verbose:
                    print(f"  Crop {crop_data['host_id']} already exists, skipping...")
                continue
            
            crop = Crop(
                host_id=crop_data['host_id'],
                crop_cycle_length_min=crop_data['crop_cycle_length_min'],
                crop_cycle_length_max=crop_data['crop_cycle_length_max'],
                cultivation_type=crop_data['cultivation_type'],
                description=crop_data.get('description'),
                labor=crop_data['labor'],
                watering=crop_data['watering'],
                n_opt=crop_data['n_opt'],
                p_opt=crop_data['p_opt'],
                k_opt=crop_data['k_opt'],
                ph_from=crop_data['ph_from'],
                ph_to=crop_data['ph_to'],
                soil_description=crop_data.get('soil_description'),
                temp_day_growth_from=crop_data['temp_day_growth_from'],
                temp_day_growth_to=crop_data['temp_day_growth_to'],
            )
            
            session.add(crop)
            count += 1
            
            if verbose:
                print(f"  Added crop: {crop_data['host_id']}")
                
        except Exception as e:
            print(f"  Error loading crop {crop_data['host_id']}: {e}")
            continue
    
    session.commit()
    print(f"Loaded {count} crops")
    return count


def load_pathogens_data(session, pathogens_data: List[Dict[str, Any]], verbose: bool = False) -> int:
    """Load pathogens data into database."""
    print("Loading pathogens data...")
    
    count = 0
    for pathogen_data in pathogens_data:
        try:
            # Check if pathogen already exists
            existing_pathogen = session.get(Pathogen, pathogen_data['id'])
            if existing_pathogen:
                if verbose:
                    print(f"  Pathogen {pathogen_data['id']} already exists, skipping...")
                continue
            
            pathogen = Pathogen(
                id=pathogen_data['id'],
                name=pathogen_data['name'],
                name_en=pathogen_data.get('name_en'),
                scientific_name=pathogen_data.get('scientific_name'),
                pathogen_class=pathogen_data['pathogen_class'],
                severity=pathogen_data['severity'],
                spread_risk=pathogen_data['spread_risk'],
                symptoms=pathogen_data.get('symptoms'),
                trigger=pathogen_data.get('trigger'),
                chemical_treatment=pathogen_data.get('chemical_treatment'),
                alternative_treatment=pathogen_data.get('alternative_treatment'),
                preventive_measures=pathogen_data.get('preventive_measures'),
                bullet_points=pathogen_data.get('bullet_points'),
                default_image=pathogen_data.get('default_image'),
                eppo=pathogen_data.get('eppo'),
                is_activated=pathogen_data.get('is_activated', True),
                translated=pathogen_data.get('translated', False),
                version_number=pathogen_data.get('version_number'),
            )
            
            session.add(pathogen)
            session.flush()  # Get the ID
            
            # Add pathogen images
            pathogen_images = pathogen_data.get('pathogen_images', [])
            for image_data in pathogen_images:
                image = PathogenImage(
                    pathogen_id=pathogen.id,
                    file_name=image_data['file_name'],
                    url=image_data.get('url'),
                    caption=image_data.get('caption'),
                    is_default=image_data.get('is_default', False),
                )
                session.add(image)
            
            # Create crop associations
            host_ids = pathogen_data.get('host_ids', [])
            for host_id in host_ids:
                # Check if crop exists
                crop = session.get(Crop, host_id)
                if crop:
                    session.execute(
                        pathogen_crop_association.insert().values(
                            pathogen_id=pathogen.id,
                            crop_id=host_id
                        )
                    )
                elif verbose:
                    print(f"    Warning: Crop {host_id} not found for pathogen {pathogen.id}")
            
            count += 1
            
            if verbose:
                print(f"  Added pathogen: {pathogen_data['id']} - {pathogen_data['name']}")
                
        except Exception as e:
            print(f"  Error loading pathogen {pathogen_data['id']}: {e}")
            continue
    
    session.commit()
    print(f"Loaded {count} pathogens")
    return count


def load_events_data(session, events_data: List[Dict[str, Any]], verbose: bool = False) -> int:
    """Load events data into database."""
    print("Loading events data...")
    
    count = 0
    for event_data in events_data:
        try:
            # Convert event ID to string if it's an integer
            event_id = str(event_data['id'])
            
            # Check if event already exists
            existing_event = session.get(Event, event_id)
            if existing_event:
                if verbose:
                    print(f"  Event {event_id} already exists, skipping...")
                continue
            
            event = Event(
                id=event_id,
                identifier=event_data['identifier'],
                title=event_data['title'],
                description=event_data.get('description'),
                nutshell=event_data.get('nutshell'),
                event_category=event_data['event_category'],
                event_type=event_data['event_type'],
                importance=event_data.get('importance'),
                start_day=event_data.get('start_day'),
                end_day=event_data.get('end_day'),
                video_url=event_data.get('video_url'),
                translated=event_data.get('translated', False),
                image_list=event_data.get('image_list'),
                params=event_data.get('params'),
                farm_assets=event_data.get('farm_assets'),
                farm_classes=event_data.get('farm_classes'),
                farm_soils=event_data.get('farm_soils'),
                farmer_experiences=event_data.get('farmer_experiences'),
                farmer_groups=event_data.get('farmer_groups'),
                weather_limitations=event_data.get('weather_limitations'),
            )
            
            session.add(event)
            session.flush()  # Get the ID
            
            # Create crop associations
            host_ids = event_data.get('host_ids', [])
            for host_id in host_ids:
                # Check if crop exists
                crop = session.get(Crop, host_id)
                if crop:
                    session.execute(
                        event_crop_association.insert().values(
                            event_id=event.id,
                            crop_id=host_id
                        )
                    )
                elif verbose:
                    print(f"    Warning: Crop {host_id} not found for event {event.id}")
            
            # Create pathogen prevention associations
            prevent_pathogens = event_data.get('prevent_pathogens', [])
            for pathogen_id in prevent_pathogens:
                # Check if pathogen exists
                pathogen = session.get(Pathogen, pathogen_id)
                if pathogen:
                    session.execute(
                        event_pathogen_association.insert().values(
                            event_id=event.id,
                            pathogen_id=pathogen_id
                        )
                    )
                elif verbose:
                    print(f"    Warning: Pathogen {pathogen_id} not found for event {event.id}")
            
            count += 1
            
            if verbose:
                print(f"  Added event: {event_id} - {event_data['title']}")
                
        except Exception as e:
            print(f"  Error loading event {event_data['id']}: {e}")
            continue
    
    session.commit()
    print(f"Loaded {count} events")
    return count


def load_crop_cycle_data(session, cycle_data: Dict[str, Any], crop_id: str, verbose: bool = False) -> int:
    """Load a single crop cycle with stages."""
    try:
        # Check if crop exists
        crop = session.get(Crop, crop_id)
        if not crop:
            print(f"  Warning: Crop {crop_id} not found, skipping cycle")
            return 0
        
        # Create crop cycle
        cycle = CropCycle(
            crop_id=crop_id,
            name=f"{crop_id}_cycle",
            description=f"Crop cycle for {crop_id}",
            total_duration_days=sum(stage['duration'] for stage in cycle_data.get('stages', [])),
            cultivation_method="direct_seeding",  # Default from the filename pattern
        )
        
        session.add(cycle)
        session.flush()  # Get the ID
        
        # Add stages
        stages_data = cycle_data.get('stages', [])
        for i, stage_data in enumerate(stages_data):
            stage = CropStage(
                cycle_id=cycle.id,
                stage_id=stage_data['id'],
                name=stage_data['name'],
                duration_days=stage_data['duration'],
                sequence_order=i + 1,
                description=f"Stage {stage_data['name']} for {crop_id}",
            )
            session.add(stage)
        
        session.commit()
        
        if verbose:
            print(f"  Added crop cycle for {crop_id} with {len(stages_data)} stages")
        
        return 1
        
    except Exception as e:
        print(f"  Error loading crop cycle for {crop_id}: {e}")
        session.rollback()
        return 0


def main():
    """Main function to load all  data."""
    parser = argparse.ArgumentParser(description="Load  JSON data into farmbase database")
    parser.add_argument("--dry-run", action="store_true", help="Run without making database changes")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--dir", default="", help="Directory containing  JSON files")
    
    args = parser.parse_args()
    
    # Setup database connection
    # database_url = os.getenv("DATABASE_URL", "postgresql://farmbase:farmbase@localhost:5432/farmbase")
    engine = create_engine(settings.sqlalchemy_database_sync_uri)
    SessionLocal = sessionmaker(bind=engine)
    
    if not args.dry_run:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    
    try:
        _dir = Path(args.dir)
        
        if not _dir.exists():
            print(f"Error:  directory '{_dir}' not found")
            return 1
        
        total_loaded = 0
        
        # Load crops
        # crops_file = _dir / "crops.json"
        # if crops_file.exists():
        #     crops_data = load_json_file(crops_file)
        #     if not args.dry_run:
        #         total_loaded += load_crops_data(session, crops_data, args.verbose)
        #     else:
        #         print(f"[DRY RUN] Would load {len(crops_data)} crops")
        #
        # # Load pathogens
        # pathogens_file = _dir / "pathogens.json"
        # if pathogens_file.exists():
        #     pathogens_data = load_json_file(pathogens_file)
        #     if not args.dry_run:
        #         total_loaded += load_pathogens_data(session, pathogens_data, args.verbose)
        #     else:
        #         print(f"[DRY RUN] Would load {len(pathogens_data)} pathogens")
        #
        # # # Load events
        # events_file = _dir / "events.json"
        # if events_file.exists():
        #     events_data = load_json_file(events_file)
        #     if not args.dry_run:
        #         total_loaded += load_events_data(session, events_data, args.verbose)
        #     else:
        #         print(f"[DRY RUN] Would load {len(events_data)} events")
        #
        # Load crop cycles
        crop_cycle_dir = _dir / "crop-cycle"
        if crop_cycle_dir.exists():
            cycle_files = list(crop_cycle_dir.glob("*.json"))
            print(f"Found {len(cycle_files)} crop cycle files")

            for cycle_file in cycle_files:
                # Extract crop ID from filename (e.g., "As_maize_direct_seeding.json" -> "MAIZE")
                crop_id = cycle_file.stem.split('_')[1].upper() if '_' in cycle_file.stem else cycle_file.stem.upper()

                cycle_data = load_json_file(cycle_file)
                if not args.dry_run:
                    total_loaded += load_crop_cycle_data(session, cycle_data, crop_id, args.verbose)
                else:
                    stages_count = len(cycle_data.get('stages', []))
                    print(f"[DRY RUN] Would load crop cycle for {crop_id} with {stages_count} stages")

        if args.dry_run:
            print("[DRY RUN] No changes made to database")
        else:
            print(f"\nSuccessfully loaded data! Total records: {total_loaded}")
        
    except Exception as e:
        print(f"Error during data loading: {e}")
        session.rollback()
        return 1
    
    finally:
        session.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())