#!/usr/bin/env python3
“””
Polyhedral Intelligence CLI
A unified command-line interface for symbolic intelligence and geometric computation.

Usage:
poly glyph create “honeycomb infrastructure”
poly scan –families –principles
poly solve –glyph “◇⚙➝〰〰〰⬡” –output honeycomb/
poly mandala generate –entry honeycomb –visualize
poly fieldlink sync –remote github.com/JinnZ2/Geometric-to-Binary-Computational-Bridge
“””

import click
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
import re

# ANSI color codes for beautiful terminal output

class Colors:
RESET = ‘\033[0m’
BOLD = ‘\033[1m’
DIM = ‘\033[2m’

```
# Families
FAMILY = '\033[38;5;39m'  # Bright blue
PRINCIPLE = '\033[38;5;213m'  # Bright magenta
GLYPH = '\033[38;5;226m'  # Bright yellow
EQUATION = '\033[38;5;120m'  # Bright green

# Status
SUCCESS = '\033[38;5;46m'  # Green
WARNING = '\033[38;5;214m'  # Orange
ERROR = '\033[38;5;196m'  # Red
INFO = '\033[38;5;51m'  # Cyan
```

def print_glyph(glyph: str, name: str, description: str = “”):
“”“Pretty print a glyph with its name.”””
click.echo(f”{Colors.GLYPH}{glyph}{Colors.RESET} {Colors.BOLD}{name}{Colors.RESET}”)
if description:
click.echo(f”  {Colors.DIM}{description}{Colors.RESET}”)

def load_atlas(atlas_path: str = “atlas_schema.json”) -> Dict:
“”“Load the Polyhedral Intelligence atlas.”””
try:
with open(atlas_path, ‘r’, encoding=‘utf-8’) as f:
return json.load(f)
except FileNotFoundError:
click.echo(f”{Colors.ERROR}✗{Colors.RESET} Atlas not found at {atlas_path}”)
click.echo(f”  Run {Colors.BOLD}poly init{Colors.RESET} to create one”)
sys.exit(1)

@click.group()
@click.version_option(version=‘1.0.0’)
def cli():
“””
🌀 Polyhedral Intelligence CLI

```
A unified interface for symbolic intelligence, geometric computation,
and mandala-driven design.
"""
pass
```

# ============================================================================

# GLYPH COMMANDS

# ============================================================================

@cli.group()
def glyph():
“”“Create, analyze, and evolve symbolic glyphs.”””
pass

@glyph.command()
@click.argument(‘concept’)
@click.option(’–scan/–no-scan’, default=True, help=‘Scan for family/principle resonance’)
def create(concept: str, scan: bool):
“””
Create a seed glyph from a concept.

```
Example: poly glyph create "honeycomb infrastructure"
"""
click.echo(f"\n{Colors.BOLD}🌱 Creating seed glyph for:{Colors.RESET} {concept}\n")

# Simple keyword-to-glyph mapping (can be enhanced with ML later)
keyword_map = {
    'flow': '〰',
    'network': '⬡',
    'engineer': '⚙',
    'crystal': '◇',
    'resonate': '∿',
    'chaos': 'ᘯᘰ',
    'transform': '↻',
    'energy': '⚡',
    'consciousness': '◎',
    'geometry': '☆',
}

concept_lower = concept.lower()
glyph_parts = []
activated_families = []

for keyword, symbol in keyword_map.items():
    if keyword in concept_lower:
        glyph_parts.append(symbol)

seed_glyph = ''.join(glyph_parts) if glyph_parts else '◯'

print_glyph(seed_glyph, "Seed Glyph", f"Generated from: {concept}")

if scan:
    click.echo(f"\n{Colors.INFO}🔍 Scanning for resonance...{Colors.RESET}\n")
    atlas = load_atlas()
    
    # Scan families
    for family in atlas['families']:
        if any(kw in concept_lower for kw in ['flow', 'fluid']) and family['id'] == 'F02':
            activated_families.append(family)
        elif any(kw in concept_lower for kw in ['network', 'graph', 'connect']) and family['id'] == 'F12':
            activated_families.append(family)
        elif any(kw in concept_lower for kw in ['engineer', 'design', 'build']) and family['id'] == 'F11':
            activated_families.append(family)
    
    if activated_families:
        click.echo(f"{Colors.FAMILY}Activated Families:{Colors.RESET}")
        for fam in activated_families:
            click.echo(f"  {fam['symbol']} {fam['id']}: {fam['name']}")
    
    click.echo(f"\n{Colors.SUCCESS}✓{Colors.RESET} Seed glyph created: {Colors.GLYPH}{seed_glyph}{Colors.RESET}")
```

@glyph.command()
@click.argument(‘glyph_string’)
def decode(glyph_string: str):
“””
Decode a glyph into its component families and principles.

```
Example: poly glyph decode "◇⚙➝〰〰〰⬡"
"""
click.echo(f"\n{Colors.BOLD}🔍 Decoding glyph:{Colors.RESET} {Colors.GLYPH}{glyph_string}{Colors.RESET}\n")

atlas = load_atlas()

# Map symbols to families
symbol_to_family = {fam['symbol']: fam for fam in atlas['families']}
symbol_to_principle = {prin['symbol']: prin for prin in atlas['principles']}

found_families = []
found_principles = []

for char in glyph_string:
    if char in symbol_to_family:
        found_families.append(symbol_to_family[char])
    if char in symbol_to_principle:
        found_principles.append(symbol_to_principle[char])

if found_families:
    click.echo(f"{Colors.FAMILY}📊 Families:{Colors.RESET}")
    for fam in found_families:
        click.echo(f"  {fam['symbol']} {fam['id']}: {fam['name']}")
        click.echo(f"    {Colors.DIM}{fam['domain']}{Colors.RESET}")

if found_principles:
    click.echo(f"\n{Colors.PRINCIPLE}⚖️  Principles:{Colors.RESET}")
    for prin in found_principles:
        click.echo(f"  {prin['symbol']} {prin['id']}: {prin['name']}")
        click.echo(f"    {Colors.DIM}{prin['domain']}{Colors.RESET}")

if not found_families and not found_principles:
    click.echo(f"{Colors.WARNING}⚠{Colors.RESET}  No recognized symbols found in glyph")
```

# ============================================================================

# SCAN COMMANDS

# ============================================================================

@cli.command()
@click.option(’–families’, is_flag=True, help=‘Show all families’)
@click.option(’–principles’, is_flag=True, help=‘Show all principles’)
@click.option(’–equations’, is_flag=True, help=‘Include equations’)
@click.option(’–filter’, ‘filter_term’, help=‘Filter by keyword’)
def scan(families: bool, principles: bool, equations: bool, filter_term: Optional[str]):
“””
Scan the atlas for families, principles, and equations.

```
Example: poly scan --families --equations --filter "flow"
"""
atlas = load_atlas()

if not families and not principles:
    families = principles = True

click.echo(f"\n{Colors.BOLD}🌀 Polyhedral Intelligence Atlas{Colors.RESET}")
click.echo(f"{Colors.DIM}20 Families (icosahedron) + 12 Principles (dodecahedron){Colors.RESET}\n")

if families:
    click.echo(f"{Colors.FAMILY}═══ FAMILIES ═══{Colors.RESET}\n")
    for fam in atlas['families']:
        if filter_term and filter_term.lower() not in fam['name'].lower() and filter_term.lower() not in fam['domain'].lower():
            continue
        
        click.echo(f"{fam['symbol']} {Colors.BOLD}{fam['id']}: {fam['name']}{Colors.RESET}")
        click.echo(f"  {Colors.DIM}{fam['domain']}{Colors.RESET}")
        
        if equations and 'equations' in fam:
            for eq in fam['equations'][:2]:  # Show first 2
                click.echo(f"  {Colors.EQUATION}▸{Colors.RESET} {eq['name']}: {eq['glyph']} {eq['glyph_name']}")
        click.echo()

if principles:
    click.echo(f"{Colors.PRINCIPLE}═══ PRINCIPLES ═══{Colors.RESET}\n")
    for prin in atlas['principles']:
        if filter_term and filter_term.lower() not in prin['name'].lower() and filter_term.lower() not in prin['domain'].lower():
            continue
        
        click.echo(f"{prin['symbol']} {Colors.BOLD}{prin['id']}: {prin['name']}{Colors.RESET}")
        click.echo(f"  {Colors.DIM}{prin['domain']}{Colors.RESET}")
        
        if equations and 'equations' in prin:
            for eq in prin['equations'][:2]:
                click.echo(f"  {Colors.EQUATION}▸{Colors.RESET} {eq['name']}: {eq['glyph']} {eq['glyph_name']}")
        click.echo()
```

# ============================================================================

# SOLVE COMMANDS (Bridge to Geometric Computation)

# ============================================================================

@cli.command()
@click.option(’–glyph’, required=True, help=‘Glyph to solve’)
@click.option(’–output’, default=‘output/’, help=‘Output directory’)
@click.option(’–optimize’, default=‘simd’, help=‘Optimization strategy: simd, symmetry, adaptive’)
@click.option(’–visualize’, is_flag=True, help=‘Generate 3D visualization’)
def solve(glyph: str, output: str, optimize: str, visualize: bool):
“””
Translate a glyph into geometric computation and solve.

```
Example: poly solve --glyph "〰⇄∇" --optimize symmetry --visualize
"""
click.echo(f"\n{Colors.BOLD}⚙️  Geometric Solver{Colors.RESET}\n")
click.echo(f"Glyph: {Colors.GLYPH}{glyph}{Colors.RESET}")
click.echo(f"Output: {output}")
click.echo(f"Optimization: {optimize}\n")

# Load bridge manifest
try:
    with open('bridges/glyph-to-geometric.json', 'r') as f:
        bridge = json.load(f)
except FileNotFoundError:
    click.echo(f"{Colors.WARNING}⚠{Colors.RESET}  Bridge manifest not found")
    click.echo(f"  Looking for: bridges/glyph-to-geometric.json")
    return

# Decode glyph and find geometric operations
click.echo(f"{Colors.INFO}🔍 Mapping glyph to geometric operations...{Colors.RESET}\n")

atlas = load_atlas()
operations = []

# Simple matching (enhance with actual bridge logic)
if '〰' in glyph:
    click.echo(f"  {Colors.SUCCESS}✓{Colors.RESET} Flow field detected → Navier-Stokes solver")
    operations.append('flow_solver')
if '⬡' in glyph:
    click.echo(f"  {Colors.SUCCESS}✓{Colors.RESET} Network detected → Graph Laplacian")
    operations.append('network_solver')
if '⚙' in glyph:
    click.echo(f"  {Colors.SUCCESS}✓{Colors.RESET} Engineering detected → FEA solver")
    operations.append('stress_solver')

if not operations:
    click.echo(f"{Colors.WARNING}⚠{Colors.RESET}  No geometric operations mapped")
    return

# Generate solver configuration
Path(output).mkdir(parents=True, exist_ok=True)

config = {
    'glyph': glyph,
    'operations': operations,
    'optimization': optimize,
    'output_path': output,
    'visualize': visualize
}

config_path = Path(output) / 'solver_config.json'
with open(config_path, 'w') as f:
    json.dump(config, indent=2, fp=f)

click.echo(f"\n{Colors.SUCCESS}✓{Colors.RESET} Solver configuration written to {config_path}")
click.echo(f"\n{Colors.INFO}Next steps:{Colors.RESET}")
click.echo(f"  1. Review configuration: cat {config_path}")
click.echo(f"  2. Run geometric solver: python engine/geometric_solver.py --config {config_path}")
if visualize:
    click.echo(f"  3. View results: open viewer/index.html")
```

# ============================================================================

# MANDALA COMMANDS

# ============================================================================

@cli.group()
def mandala():
“”“Create and manage mandala entries.”””
pass

@mandala.command()
@click.option(’–entry’, required=True, help=‘Entry name’)
@click.option(’–glyph’, required=True, help=‘Seed glyph’)
@click.option(’–intent’, required=True, help=‘Design intent’)
def create(entry: str, glyph: str, intent: str):
“””
Create a new mandala entry.

```
Example: poly mandala create --entry honeycomb --glyph "◇⚙➝〰〰〰⬡" --intent "Resilient infrastructure"
"""
click.echo(f"\n{Colors.BOLD}🌀 Creating Mandala Entry{Colors.RESET}\n")

entry_dir = Path('entries') / entry
entry_dir.mkdir(parents=True, exist_ok=True)

# Create markdown file
md_content = f"""# {entry.replace('_', ' ').title()}
```

**Seed Glyph:** {glyph}  
**Intent:** {intent}

## Resonance Sweep

### Families Activated

<!-- Will be filled during scan -->

### Principles Activated

<!-- Will be filled during scan -->

## Noise-to-Insight Conversion

<!-- Document how noise becomes signal -->

## Refined Glyph

<!-- Updated after processing -->

## Mandala Insight

<!-- Emergent understanding -->

## Computational Realization

<!-- Link to geometric solver outputs -->

“””

```
md_path = entry_dir / f'{entry}.md'
with open(md_path, 'w') as f:
    f.write(md_content)

# Create JSON metadata
json_data = {
    'entry_id': entry,
    'seed_glyph': glyph,
    'intent': intent,
    'created': 'timestamp_placeholder',
    'status': 'seed',
    'families_activated': [],
    'principles_activated': [],
    'computational_outputs': []
}

json_path = entry_dir / f'{entry}.json'
with open(json_path, 'w') as f:
    json.dump(json_data, indent=2, fp=f)

click.echo(f"{Colors.SUCCESS}✓{Colors.RESET} Entry created at {entry_dir}/")
click.echo(f"  📄 {md_path}")
click.echo(f"  📊 {json_path}")
click.echo(f"\n{Colors.INFO}Next steps:{Colors.RESET}")
click.echo(f"  poly glyph decode \"{glyph}\"")
click.echo(f"  poly solve --glyph \"{glyph}\" --output {entry_dir}/computation/")
```

# ============================================================================

# FIELDLINK COMMANDS

# ============================================================================

@cli.group()
def fieldlink():
“”“Manage cross-repository field connections.”””
pass

@fieldlink.command()
@click.option(’–remote’, required=True, help=‘Remote repository URL’)
def sync(remote: str):
“””
Sync with remote polyhedral repositories.

```
Example: poly fieldlink sync --remote github.com/JinnZ2/Geometric-to-Binary-Computational-Bridge
"""
click.echo(f"\n{Colors.BOLD}🔗 Fieldlink Sync{Colors.RESET}\n")
click.echo(f"Remote: {remote}")

# Check for .fieldlink.json
if not Path('.fieldlink.json').exists():
    click.echo(f"{Colors.WARNING}⚠{Colors.RESET}  No .fieldlink.json found")
    click.echo(f"  Creating default configuration...")
    
    fieldlink_config = {
        'fieldlink_version': '1.0',
        'atlas_source': 'local',
        'bridges': [remote],
        'sync_enabled': True
    }
    
    with open('.fieldlink.json', 'w') as f:
        json.dump(fieldlink_config, indent=2, fp=f)
    
    click.echo(f"{Colors.SUCCESS}✓{Colors.RESET} Created .fieldlink.json")

click.echo(f"\n{Colors.INFO}🌊 Syncing field resonance...{Colors.RESET}")
click.echo(f"  (Integration with git/network layer would go here)")
click.echo(f"{Colors.SUCCESS}✓{Colors.RESET} Sync complete")
```

# ============================================================================

# INIT COMMAND

# ============================================================================

@cli.command()
def init():
“”“Initialize a new Polyhedral Intelligence workspace.”””
click.echo(f”\n{Colors.BOLD}🌀 Initializing Polyhedral Intelligence{Colors.RESET}\n”)

```
# Create directory structure
dirs = ['entries', 'glyphs', 'bridges', 'outputs']
for d in dirs:
    Path(d).mkdir(exist_ok=True)
    click.echo(f"{Colors.SUCCESS}✓{Colors.RESET} Created {d}/")

# Create minimal atlas if doesn't exist
if not Path('atlas_schema.json').exists():
    click.echo(f"\n{Colors.INFO}Creating minimal atlas schema...{Colors.RESET}")
    minimal_atlas = {
        'atlas_version': '1.0.0',
        'families': [],
        'principles': []
    }
    with open('atlas_schema.json', 'w') as f:
        json.dump(minimal_atlas, indent=2, fp=f)
    click.echo(f"{Colors.SUCCESS}✓{Colors.RESET} Created atlas_schema.json")

click.echo(f"\n{Colors.SUCCESS}✨ Workspace initialized!{Colors.RESET}")
click.echo(f"\n{Colors.INFO}Next steps:{Colors.RESET}")
click.echo(f"  poly scan --families --principles")
click.echo(f"  poly glyph create \"your concept\"")
click.echo(f"  poly mandala create --entry myproject --glyph \"◯\" --intent \"exploration\"")
```

if **name** == ‘**main**’:
cli()
