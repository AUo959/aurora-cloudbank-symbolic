#!/usr/bin/env python3
"""
NEXUS Phase 2 CLI Extensions
Anchor: NEXUS-CLI-P2-2025
Seed: EOS_SEED_ORION
Arbiter: AUo959
"""

import click
import asyncio
import json
from pathlib import Path
from datetime import datetime
import sys

# Add module path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.nexus.core.multi_agent_coordinator import get_coordinator, CoordinationMode

@click.group()
@click.pass_context
def cli(ctx):
    """NEXUS Phase 2 CLI - Multi-Agent Coordination"""
    ctx.ensure_object(dict)
    ctx.obj['coordinator'] = get_coordinator()
    ctx.obj['anchor'] = 'NEXUS-CLI-P2-2025'

@cli.command()
@click.option('--agent-id', required=True, help='Agent identifier')
@click.option('--agent-type', default='ai_agent', help='Type of agent')
@click.option('--capabilities', default='reasoning,synthesis', help='Comma-separated capabilities')
@click.pass_context
def register(ctx, agent_id, agent_type, capabilities):
    """Register an agent in the coordination system"""
    
    async def do_register():
        coordinator = ctx.obj['coordinator']
        caps = capabilities.split(',')
        result = await coordinator.register_agent(agent_id, agent_type, caps)
        return result
        
    result = asyncio.run(do_register())
    
    if result['status'] == 'registered':
        click.echo(f"✅ Agent registered: {agent_id}")
        click.echo(f"   Type: {agent_type}")
        click.echo(f"   Capabilities: {capabilities}")
        click.echo(f"   Seal: {result['seal']}...")
    else:
        click.echo(f"⚠️ Registration failed: {result['status']}")

@cli.command()
@click.option('--sender', required=True, help='Sender agent ID')
@click.option('--recipients', required=True, help='Comma-separated recipient IDs')
@click.option('--message', required=True, help='Message content')
@click.option('--consensus', is_flag=True, help='Require consensus')
@click.pass_context
def send(ctx, sender, recipients, message, consensus):
    """Send message between agents"""
    
    async def do_send():
        coordinator = ctx.obj['coordinator']
        recipient_list = recipients.split(',')
        seal = await coordinator.send_message(sender, recipient_list, message, consensus)
        return seal
        
    seal = asyncio.run(do_send())
    click.echo(f"✅ Message sent")
    click.echo(f"   From: {sender}")
    click.echo(f"   To: {recipients}")
    click.echo(f"   Seal: {seal[:16]}...")

@cli.command()
@click.option('--proposal', required=True, help='Proposal JSON')
@click.option('--agents', required=True, help='Comma-separated agent IDs')
@click.pass_context
def consensus(ctx, proposal, agents):
    """Achieve consensus among agents"""
    
    async def do_consensus():
        coordinator = ctx.obj['coordinator']
        proposal_dict = json.loads(proposal)
        agent_list = agents.split(',')
        result = await coordinator.achieve_consensus(proposal_dict, agent_list)
        return result
        
    result = asyncio.run(do_consensus())
    
    click.echo(f"📊 Consensus Session: {result['session_id']}")
    click.echo(f"   Achieved: {result['result']['consensus_achieved']}")
    click.echo(f"   Confidence: {result['result']['confidence']:.2%}")
    click.echo(f"   Votes For: {result['result']['votes_for']}")
    click.echo(f"   Votes Against: {result['result']['votes_against']}")

@cli.command()
@click.option('--action', required=True, help='Action to coordinate')
@click.option('--agents', required=True, help='Comma-separated agent IDs')
@click.option('--mode', default='consensus', 
              type=click.Choice(['synchronous', 'consensus', 'swarm']))
@click.pass_context
def coordinate(ctx, action, agents, mode):
    """Coordinate action across multiple agents"""
    
    async def do_coordinate():
        coordinator = ctx.obj['coordinator']
        agent_list = agents.split(',')
        mode_enum = CoordinationMode(mode)
        result = await coordinator.coordinate_action(action, agent_list, mode_enum)
        return result
        
    result = asyncio.run(do_coordinate())
    
    click.echo(f"🎯 Coordination Complete")
    click.echo(f"   Action: {action}")
    click.echo(f"   Mode: {mode}")
    click.echo(f"   Agents: {len(result['agents'])}")
    click.echo(f"   Seal: {result['seal'][:16]}...")

@cli.command()
@click.pass_context
def status(ctx):
    """Show coordination system status"""
    
    coordinator = ctx.obj['coordinator']
    manifest = coordinator.export_coordination_manifest()
    
    click.echo("🌌 NEXUS Phase 2 Status")
    click.echo("="*50)
    click.echo(f"Anchor: {manifest['anchor']}")
    click.echo(f"Seed: {manifest['seed']}")
    click.echo(f"Total Agents: {manifest['coordination_stats']['total_agents']}")
    click.echo(f"Messages Queued: {manifest['coordination_stats']['messages_queued']}")
    click.echo(f"Consensus Sessions: {manifest['coordination_stats']['consensus_sessions']}")
    click.echo(f"Divergent Truths: {manifest['coordination_stats']['divergent_truths']}")
    click.echo(f"Entropy Level: {manifest['entropy_state']['current']:.3f}")
    click.echo(f"Entropy Drift: {manifest['entropy_state']['drift']:.3f}")
    
    if manifest['active_agents']:
        click.echo("\nActive Agents:")
        for agent in manifest['active_agents']:
            click.echo(f"  • {agent}")

if __name__ == '__main__':
    cli()