#!/usr/bin/env python3
"""
NEXUS CLI Interface
Anchor: NEXUS-CLI-2025
Arbiter: AUo959
"""

import click
import json
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import sys

# Add module path
sys.path.insert(0, str(Path(__file__).parent))

@click.group()
@click.pass_context
def cli(ctx):
    """NEXUS Command Line Interface"""
    ctx.ensure_object(dict)
    ctx.obj['anchor'] = 'NEXUS-CLI-2025'
    ctx.obj['arbiter'] = 'AUo959'

@cli.command()
@click.option('--entity-type', default='ai_agent', help='Type of entity to spawn')
@click.option('--capabilities', default='', help='Comma-separated list of capabilities')
@click.option('--dlp-tag', default='GENERAL', help='DLP classification tag')
@click.pass_context
def spawn(ctx, entity_type, capabilities, dlp_tag):
    """Spawn a new entity in the mesh"""
    try:
        from modules.nexus.core.entity_manager import get_entity_manager, EntityType
        
        # Parse entity type
        try:
            entity_type_enum = EntityType(entity_type)
        except ValueError:
            click.echo(f"❌ Invalid entity type: {entity_type}")
            click.echo(f"Valid types: {[t.value for t in EntityType]}")
            return
        
        # Parse capabilities
        capability_list = [c.strip() for c in capabilities.split(',') if c.strip()] if capabilities else []
        
        # Spawn entity
        manager = get_entity_manager()
        entity = manager.spawn_entity(
            entity_type=entity_type_enum,
            capabilities=capability_list,
            dlp_tag=dlp_tag
        )
        
        click.echo(f"✓ Spawned {entity_type}")
        click.echo(f"  ID: {entity.entity_id}")
        click.echo(f"  Anchor: {entity.anchor}")
        click.echo(f"  State: {entity.state.value}")
        click.echo(f"  Capabilities: {entity.capabilities}")
        click.echo(f"  DLP Tag: {entity.dlp_tag}")
        
    except ImportError as e:
        click.echo(f"❌ Entity manager not available: {e}")

@cli.command()
@click.pass_context
def status(ctx):
    """Show NEXUS status"""
    # Check anchors
    anchor_registry = Path(".nexus/anchors/registry.json")
    if anchor_registry.exists():
        registry = json.loads(anchor_registry.read_text())
        
        click.echo("🌌 NEXUS Status")
        click.echo("="*50)
        click.echo(f"Primary Anchor: {registry['primary_anchor']}")
        click.echo(f"Seed: {registry['seed']}")
        click.echo(f"Arbiter: {registry['arbiter']}")
        click.echo(f"Active Anchors: {len(registry['anchors'])}")
        click.echo(f"Entropy State: {registry['entropy_state']['level']}")
        click.echo(f"Entropy Drift: {registry['entropy_state']['drift']}")
        
        # Check memory manager
        try:
            from modules.nexus.core.memory_manager import get_memory_manager
            manager = get_memory_manager()
            manifest = manager.export_manifest()
            click.echo(f"Memory Entries: {manifest['memory_count']}")
            click.echo(f"Sealed Memories: {manifest['sealed_count']}")
        except ImportError:
            click.echo("Memory Manager: Not loaded")
        
        # Check entity manager
        try:
            from modules.nexus.core.entity_manager import get_entity_manager
            entity_manager = get_entity_manager()
            entity_manifest = entity_manager.export_manifest()
            click.echo(f"Total Entities: {entity_manifest['total_entities']}")
            click.echo(f"Active Entities: {entity_manifest['active_entities']}")
            click.echo(f"Entanglements: {entity_manifest['total_entanglements']}")
        except ImportError:
            click.echo("Entity Manager: Not loaded")
            
    else:
        click.echo("NEXUS not initialized. Run bootstrap first.")

@cli.command()
@click.option('--description', default='', help='Checkpoint description')
@click.pass_context
def seal(ctx, description):
    """Seal current state as checkpoint"""
    checkpoint = {
        'description': description,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'anchor': ctx.obj['anchor'],
        'arbiter': ctx.obj['arbiter']
    }
    
    # Create hash
    checkpoint_hash = hashlib.sha256(
        json.dumps(checkpoint, sort_keys=True).encode()
    ).hexdigest()
    
    checkpoint['seal'] = checkpoint_hash
    
    # Save checkpoint
    checkpoint_path = Path(f".nexus/checkpoints/{checkpoint_hash[:16]}.json")
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.write_text(json.dumps(checkpoint, indent=2))
    
    click.echo(f"✓ State sealed: {checkpoint_hash[:32]}...")
    click.echo(f"  Description: {description}")

@cli.command()
@click.option('--key', required=True, help='Memory key to store')
@click.option('--value', required=True, help='Value to store')
@click.option('--dlp-tag', default='GENERAL', help='DLP classification tag')
@click.pass_context
def store(ctx, key, value, dlp_tag):
    """Store value in symbolic memory"""
    try:
        from modules.nexus.core.memory_manager import get_memory_manager
        manager = get_memory_manager()
        seal = manager.store(key, value, dlp_tag)
        
        click.echo(f"✓ Stored in memory")
        click.echo(f"  Key: {key}")
        click.echo(f"  Value: {value}")
        click.echo(f"  DLP Tag: {dlp_tag}")
        click.echo(f"  Seal: {seal[:32]}...")
        
    except ImportError as e:
        click.echo(f"❌ Memory manager not available: {e}")

@cli.command()
@click.option('--key', required=True, help='Memory key to retrieve')
@click.pass_context
def retrieve(ctx, key):
    """Retrieve value from symbolic memory"""
    try:
        from modules.nexus.core.memory_manager import get_memory_manager
        manager = get_memory_manager()
        value = manager.retrieve(key)
        
        if value is not None:
            click.echo(f"✓ Retrieved from memory")
            click.echo(f"  Key: {key}")
            click.echo(f"  Value: {value}")
        else:
            click.echo(f"❌ Key '{key}' not found or seal verification failed")
            
    except ImportError as e:
        click.echo(f"❌ Memory manager not available: {e}")

@cli.command()
@click.pass_context
def manifest(ctx):
    """Export memory manifest"""
    try:
        from modules.nexus.core.memory_manager import get_memory_manager
        manager = get_memory_manager()
        manifest = manager.export_manifest()
        
        click.echo("📋 Memory Manifest")
        click.echo("="*50)
        click.echo(json.dumps(manifest, indent=2))
        
    except ImportError as e:
        click.echo(f"❌ Memory manager not available: {e}")

if __name__ == '__main__':
    cli()