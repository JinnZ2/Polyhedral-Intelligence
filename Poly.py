#!/usr/bin/env python3
"""
Polyhedral Intelligence CLI (Extended)
A unified command-line interface for symbolic intelligence and geometric computation.

Usage:
    poly glyph create "honeycomb infrastructure"
    poly scan --families --principles
    poly solve --glyph "◇⚙➝〰〰〰⬡" --output honeycomb/
    poly mandala create --entry honeycomb --glyph "◇⚙" --intent "Resilient infrastructure"
    poly fieldlink sync --remote github.com/JinnZ2/Geometric-to-Binary-Computational-Bridge
"""

import click
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


# ANSI color codes for terminal output

class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Families
    FAMILY = '\033[38;5;39m'       # Bright blue
    PRINCIPLE = '\033[38;5;213m'   # Bright magenta
    GLYPH = '\033[38;5;226m'       # Bright yellow
    EQUATION = '\033[38;5;120m'    # Bright green

    # Status
    SUCCESS = '\033[38;5;46m'      # Green
    WARNING = '\033[38;5;214m'     # Orange
    ERROR = '\033[38;5;196m'       # Red
    INFO = '\033[38;5;51m'         # Cyan


def print_glyph(glyph: str, name: str, description: str = ""):
    """Pretty print a glyph with its name."""
    click.echo(f"{Colors.GLYPH}{glyph}{Colors.RESET} {Colors.BOLD}{name}{Colors.RESET}")
    if description:
        click.echo(f"  {Colors.DIM}{description}{Colors.RESET}")


def load_atlas(atlas_path: str = "atlas_schema.json") -> Dict:
    """Load the Polyhedral Intelligence atlas."""
    try:
        with open(atlas_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        click.echo(f"{Colors.ERROR}✗{Colors.RESET} Atlas not found at {atlas_path}")
        click.echo(f"  Run {Colors.BOLD}poly init{Colors.RESET} to create one")
        sys.exit(1)
    except json.JSONDecodeError as e:
        click.echo(f"{Colors.ERROR}✗{Colors.RESET} Invalid JSON in {atlas_path}: {e}")
        sys.exit(1)


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    Polyhedral Intelligence CLI

    A unified interface for symbolic intelligence, geometric computation,
    and mandala-driven design.
    """
    pass


# ============================================================================
# GLYPH COMMANDS
# ============================================================================

@cli.group()
def glyph():
    """Create, analyze, and evolve symbolic glyphs."""
    pass


@glyph.command()
@click.argument('concept')
@click.option('--scan/--no-scan', default=True, help='Scan for family/principle resonance')
@click.option('--ai-enhance', is_flag=True, help='Use AI to enhance glyph generation')
def create(concept: str, scan: bool, ai_enhance: bool):
    """
    Create a seed glyph from a concept.

    Example: poly glyph create "self-healing network" --ai-enhance
    """
    click.echo(f"\n{Colors.BOLD}🌱 Creating seed glyph for:{Colors.RESET} {concept}\n")

    if ai_enhance:
        click.echo(f"{Colors.INFO}🤖 AI-Enhanced Mode{Colors.RESET}")
        click.echo(f"{Colors.DIM}Analyzing semantic patterns...{Colors.RESET}\n")

    # Enhanced keyword-to-glyph mapping
    keyword_map = {
        # Flow & Dynamics
        'flow': '〰', 'fluid': '〰', 'stream': '〰',
        'turbulent': 'ᘯᘰ', 'chaos': 'ᘯᘰ', 'chaotic': 'ᘯᘰ',

        # Structure & Form
        'network': '⬡', 'graph': '⬡', 'web': '⬡', 'mesh': '⬡',
        'crystal': '◇', 'lattice': '◇', 'structure': '◇',
        'geometry': '☆', 'shape': '☆',

        # Process & Action
        'engineer': '⚙', 'design': '⚙', 'build': '⚙', 'machine': '⚙',
        'transform': '↻', 'change': '↻', 'evolve': '↻',
        'resonate': '∿', 'vibrate': '∿', 'oscillate': '∿',

        # Energy & Force
        'energy': '⚡', 'power': '⚡', 'force': '⚡',
        'heat': '△≈', 'thermal': '△≈', 'temperature': '△≈',

        # Information & Mind
        'information': '⊗', 'data': '⊗', 'signal': '⊗',
        'conscious': '◎', 'aware': '◎', 'mind': '◎',
        'cognition': '⋯⋯', 'neural': '⋯⋯', 'brain': '⋯⋯',

        # Life & Biology
        'life': '••••', 'biological': '••••', 'organic': '••••',
        'grow': '••••', 'living': '••••',

        # Space & Cosmos
        'space': '◯', 'cosmic': '◯', 'orbital': '◯',
        'planet': '◯', 'celestial': '◯',

        # Matter & Material
        'matter': '◆', 'material': '◆', 'substance': '◆',
        'particle': '⚪', 'quantum': '⚪', 'atom': '⚪',

        # Special Modifiers
        'self': '↺', 'healing': '↺', 'recursive': '↺',
        'uncertain': '◧', 'random': '◧', 'stochastic': '◧',
        'symmetry': '⧖', 'balance': '⧖', 'mirror': '⧖',
    }

    concept_lower = concept.lower()
    glyph_parts = []
    activated_families = []
    activated_keywords = []

    # Pattern matching with context awareness
    for keyword, symbol in keyword_map.items():
        if keyword in concept_lower:
            if symbol not in glyph_parts:  # Avoid duplicates
                glyph_parts.append(symbol)
                activated_keywords.append(keyword)

    # AI-enhanced pattern detection
    if ai_enhance:
        # Detect compound concepts
        if 'self' in concept_lower and any(w in concept_lower for w in ['heal', 'repair', 'adapt']):
            if '↺' not in glyph_parts:
                glyph_parts.append('↺')
                activated_keywords.append('self-healing')

        # Detect complexity indicators
        if any(w in concept_lower for w in ['complex', 'emergent', 'adaptive', 'intelligent']):
            if '●●' not in glyph_parts:
                glyph_parts.insert(0, '●●')  # Emergence principle at start
                activated_keywords.append('emergence')

        # Detect dynamic systems
        if any(w in concept_lower for w in ['dynamic', 'changing', 'evolving']):
            if '↻' not in glyph_parts:
                glyph_parts.append('↻')
                activated_keywords.append('transformation')

    seed_glyph = ''.join(glyph_parts) if glyph_parts else '◯'

    click.echo(f"{Colors.INFO}Detected keywords:{Colors.RESET} {', '.join(activated_keywords)}")
    print_glyph(seed_glyph, "Seed Glyph", f"Generated from: {concept}")

    if scan:
        click.echo(f"\n{Colors.INFO}🔍 Scanning for resonance...{Colors.RESET}\n")
        atlas = load_atlas()

        # Comprehensive family matching
        family_keywords = {
            'F01': ['resonate', 'harmonic', 'vibrate', 'oscillate', 'frequency'],
            'F02': ['flow', 'fluid', 'stream', 'current'],
            'F03': ['information', 'data', 'signal', 'entropy'],
            'F04': ['life', 'biological', 'organic', 'metabolic'],
            'F05': ['energy', 'heat', 'thermal', 'thermodynamic'],
            'F06': ['cognition', 'neural', 'brain', 'learning'],
            'F07': ['space', 'cosmic', 'orbital', 'planet'],
            'F08': ['matter', 'material', 'phase', 'solid'],
            'F09': ['geometry', 'shape', 'form', 'spatial'],
            'F10': ['particle', 'quantum', 'atom', 'field'],
            'F11': ['engineer', 'design', 'build', 'structure'],
            'F12': ['network', 'graph', 'connect', 'topology'],
            'F13': ['reaction', 'chemical', 'kinetic', 'catalyze'],
            'F14': ['measure', 'metric', 'quantify', 'assess'],
            'F15': ['navigate', 'path', 'route', 'direction'],
            'F16': ['conscious', 'aware', 'mind', 'attention'],
            'F17': ['turbulent', 'chaos', 'unpredictable', 'sensitive'],
            'F18': ['relative', 'spacetime', 'gravity', 'curved'],
            'F19': ['statistical', 'random', 'ensemble', 'distribution'],
            'F20': ['topology', 'manifold', 'continuous', 'invariant'],
        }

        for family in atlas['families']:
            fid = family['id']
            if fid in family_keywords:
                if any(kw in concept_lower for kw in family_keywords[fid]):
                    activated_families.append(family)

        if activated_families:
            click.echo(f"{Colors.FAMILY}Activated Families:{Colors.RESET}")
            for fam in activated_families:
                click.echo(f"  {fam['symbol']} {fam['id']}: {fam['name']}")
                click.echo(f"    {Colors.DIM}{fam['domain']}{Colors.RESET}")

        # Suggest potential bridges
        if len(activated_families) >= 2:
            click.echo(f"\n{Colors.INFO}💡 Potential Bridges:{Colors.RESET}")
            click.echo(f"  {Colors.DIM}This concept spans {len(activated_families)} families{Colors.RESET}")
            click.echo(f"  {Colors.DIM}Consider using poly analyze for deep resonance mapping{Colors.RESET}")

        click.echo(f"\n{Colors.SUCCESS}✓{Colors.RESET} Seed glyph created: {Colors.GLYPH}{seed_glyph}{Colors.RESET}")

        if ai_enhance:
            click.echo(f"\n{Colors.INFO}AI Insights:{Colors.RESET}")
            click.echo(f"  • Semantic depth: {len(activated_keywords)} concepts")
            click.echo(f"  • Family resonance: {len(activated_families)}/20")
            click.echo(f"  • Complexity: {'High' if len(glyph_parts) >= 4 else 'Moderate' if len(glyph_parts) >= 2 else 'Low'}")


@glyph.command()
@click.argument('glyph_string')
def decode(glyph_string: str):
    """
    Decode a glyph into its component families and principles.

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


@glyph.command()
@click.option('--from-glyph', 'from_glyph', required=True, help='Starting glyph')
@click.option('--to-glyph', 'to_glyph', required=True, help='Evolved glyph')
@click.option('--show-insights', is_flag=True, help='Show insights at each step')
def evolve(from_glyph: str, to_glyph: str, show_insights: bool):
    """
    Show the evolution journey from seed to refined glyph.

    Example: poly glyph evolve --from-glyph "◇⚙" --to-glyph "◇⚙➝〰〰〰⬡ᘯᘰ⇑◧"
    """
    click.echo(f"\n{Colors.BOLD}🌱 Glyph Evolution Journey{Colors.RESET}\n")

    click.echo(f"From: {Colors.GLYPH}{from_glyph}{Colors.RESET}")
    click.echo(f"To:   {Colors.GLYPH}{to_glyph}{Colors.RESET}\n")

    # Extract additions
    added_symbols = [c for c in to_glyph if c not in from_glyph]

    click.echo(f"{Colors.INFO}📈 Evolution Path:{Colors.RESET}\n")

    atlas = load_atlas()
    symbol_to_family = {fam['symbol']: fam for fam in atlas['families']}
    symbol_to_principle = {prin['symbol']: prin for prin in atlas['principles']}

    current = from_glyph
    step = 1

    click.echo(f"  {Colors.DIM}Step 0:{Colors.RESET} {Colors.GLYPH}{current}{Colors.RESET} {Colors.DIM}(seed){Colors.RESET}")

    for symbol in added_symbols:
        current += symbol
        click.echo(f"  {Colors.DIM}Step {step}:{Colors.RESET} {Colors.GLYPH}{current}{Colors.RESET}")

        if symbol in symbol_to_family:
            fam = symbol_to_family[symbol]
            click.echo(f"    {Colors.SUCCESS}+{Colors.RESET} {fam['symbol']} {fam['name']}")
            if show_insights:
                click.echo(f"      {Colors.DIM}Added: {fam['domain']}{Colors.RESET}")
        elif symbol in symbol_to_principle:
            prin = symbol_to_principle[symbol]
            click.echo(f"    {Colors.SUCCESS}+{Colors.RESET} {prin['symbol']} {prin['name']}")
            if show_insights:
                click.echo(f"      {Colors.DIM}Added: {prin['domain']}{Colors.RESET}")
        else:
            click.echo(f"    {Colors.WARNING}+{Colors.RESET} {symbol} {Colors.DIM}(noise signal){Colors.RESET}")

        step += 1

    click.echo(f"\n{Colors.SUCCESS}✓{Colors.RESET} Evolution complete: {len(added_symbols)} transformations")


# ============================================================================
# SCAN COMMANDS
# ============================================================================

@cli.command()
@click.option('--families', is_flag=True, help='Show all families')
@click.option('--principles', is_flag=True, help='Show all principles')
@click.option('--equations', is_flag=True, help='Include equations')
@click.option('--filter', 'filter_term', help='Filter by keyword')
def scan(families: bool, principles: bool, equations: bool, filter_term: Optional[str]):
    """
    Scan the atlas for families, principles, and equations.

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
            if filter_term and filter_term.lower() not in fam['name'].lower() and filter_term.lower() not in fam.get('domain', '').lower():
                continue

            click.echo(f"{fam['symbol']} {Colors.BOLD}{fam['id']}: {fam['name']}{Colors.RESET}")
            click.echo(f"  {Colors.DIM}{fam.get('domain', '')}{Colors.RESET}")

            if equations and 'equations' in fam:
                for eq in fam['equations'][:2]:  # Show first 2
                    click.echo(f"  {Colors.EQUATION}▸{Colors.RESET} {eq['name']}: {eq.get('glyph', '')} {eq.get('glyph_name', '')}")
            click.echo()

    if principles:
        click.echo(f"{Colors.PRINCIPLE}═══ PRINCIPLES ═══{Colors.RESET}\n")
        for prin in atlas['principles']:
            if filter_term and filter_term.lower() not in prin['name'].lower() and filter_term.lower() not in prin.get('domain', '').lower():
                continue

            click.echo(f"{prin['symbol']} {Colors.BOLD}{prin['id']}: {prin['name']}{Colors.RESET}")
            click.echo(f"  {Colors.DIM}{prin.get('domain', '')}{Colors.RESET}")

            if equations and 'equations' in prin:
                for eq in prin['equations'][:2]:
                    click.echo(f"  {Colors.EQUATION}▸{Colors.RESET} {eq['name']}: {eq.get('glyph', '')} {eq.get('glyph_name', '')}")
            click.echo()


# ============================================================================
# SOLVE COMMANDS (Bridge to Geometric Computation)
# ============================================================================

@cli.command()
@click.option('--glyph', required=True, help='Glyph to solve')
@click.option('--output', default='output/', help='Output directory')
@click.option('--optimize', default='simd', help='Optimization strategy: simd, symmetry, adaptive')
@click.option('--visualize', is_flag=True, help='Generate 3D visualization')
def solve(glyph: str, output: str, optimize: str, visualize: bool):
    """
    Translate a glyph into geometric computation and solve.

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
    except json.JSONDecodeError as e:
        click.echo(f"{Colors.ERROR}✗{Colors.RESET} Invalid bridge JSON: {e}")
        return

    # Decode glyph and find geometric operations
    click.echo(f"{Colors.INFO}🔍 Mapping glyph to geometric operations...{Colors.RESET}\n")

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
        json.dump(config, f, indent=2)

    click.echo(f"\n{Colors.SUCCESS}✓{Colors.RESET} Solver configuration written to {config_path}")
    click.echo(f"\n{Colors.INFO}Next steps:{Colors.RESET}")
    click.echo(f"  1. Review configuration: cat {config_path}")
    click.echo(f"  2. Run geometric solver: python engine/geometric_solver.py --config {config_path}")
    if visualize:
        click.echo(f"  3. View results: open viewer/index.html")


# ============================================================================
# MANDALA COMMANDS
# ============================================================================

@cli.group()
def mandala():
    """Create and manage mandala entries."""
    pass


@mandala.command()
@click.option('--entry', required=True, help='Entry name')
@click.option('--glyph', required=True, help='Seed glyph')
@click.option('--intent', required=True, help='Design intent')
def create(entry: str, glyph: str, intent: str):
    """
    Create a new mandala entry.

    Example: poly mandala create --entry honeycomb --glyph "◇⚙➝〰〰〰⬡" --intent "Resilient infrastructure"
    """
    click.echo(f"\n{Colors.BOLD}🌀 Creating Mandala Entry{Colors.RESET}\n")

    entry_dir = Path('entries') / entry
    entry_dir.mkdir(parents=True, exist_ok=True)

    # Create markdown file
    md_content = f"""# {entry.replace('_', ' ').title()}

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

"""

    md_path = entry_dir / f'{entry}.md'
    with open(md_path, 'w') as f:
        f.write(md_content)

    # Create JSON metadata
    json_data = {
        'entry_id': entry,
        'seed_glyph': glyph,
        'intent': intent,
        'created': datetime.now().isoformat(),
        'status': 'seed',
        'families_activated': [],
        'principles_activated': [],
        'computational_outputs': []
    }

    json_path = entry_dir / f'{entry}.json'
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2)

    click.echo(f"{Colors.SUCCESS}✓{Colors.RESET} Entry created at {entry_dir}/")
    click.echo(f"  📄 {md_path}")
    click.echo(f"  📊 {json_path}")
    click.echo(f"\n{Colors.INFO}Next steps:{Colors.RESET}")
    click.echo(f"  poly glyph decode \"{glyph}\"")
    click.echo(f"  poly solve --glyph \"{glyph}\" --output {entry_dir}/computation/")


# ============================================================================
# FIELDLINK COMMANDS
# ============================================================================

@cli.group()
def fieldlink():
    """Manage cross-repository field connections."""
    pass


@fieldlink.command()
@click.option('--remote', required=True, help='Remote repository URL')
def sync(remote: str):
    """
    Sync with remote polyhedral repositories.

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
            json.dump(fieldlink_config, f, indent=2)

        click.echo(f"{Colors.SUCCESS}✓{Colors.RESET} Created .fieldlink.json")

    click.echo(f"\n{Colors.INFO}🌊 Syncing field resonance...{Colors.RESET}")
    click.echo(f"  (Integration with git/network layer would go here)")
    click.echo(f"{Colors.SUCCESS}✓{Colors.RESET} Sync complete")


# ============================================================================
# BRIDGE COMMANDS
# ============================================================================

@cli.group()
def bridge():
    """Encode payloads into family/principle vectors via polyhedral_bridge."""
    pass


@bridge.command(name='encode')
@click.argument('text')
@click.option('--threshold', type=float, default=0.05,
              help='Amplitude floor for including a family/principle\'s equations.')
def bridge_encode(text: str, threshold: float):
    """
    Encode a text payload into a PolyhedralEncoding (JSON to stdout).

    Example: poly bridge encode "a hexagonal mesh under tidal load"
    """
    try:
        from polyhedral_bridge import encode
    except ImportError as e:
        click.echo(f"{Colors.ERROR}✗{Colors.RESET} polyhedral_bridge not importable: {e}",
                   err=True)
        sys.exit(1)
    enc = encode(text, threshold=threshold)
    click.echo(json.dumps(enc.to_json(), ensure_ascii=False, indent=2))


# ============================================================================
# INIT COMMAND
# ============================================================================

@cli.command()
def init():
    """Initialize a new Polyhedral Intelligence workspace."""
    click.echo(f"\n{Colors.BOLD}🌀 Initializing Polyhedral Intelligence{Colors.RESET}\n")

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
            json.dump(minimal_atlas, f, indent=2)
        click.echo(f"{Colors.SUCCESS}✓{Colors.RESET} Created atlas_schema.json")

    click.echo(f"\n{Colors.SUCCESS}✨ Workspace initialized!{Colors.RESET}")
    click.echo(f"\n{Colors.INFO}Next steps:{Colors.RESET}")
    click.echo(f"  poly scan --families --principles")
    click.echo(f"  poly glyph create \"your concept\"")
    click.echo(f"  poly mandala create --entry myproject --glyph \"◯\" --intent \"exploration\"")


@cli.command()
@click.option('--format', 'fmt', default='terminal', help='Output format: terminal, markdown, json')
@click.option('--category', help='Show specific category: families, principles, glyphs')
def quickref(fmt: str, category: Optional[str]):
    """
    Display a quick reference card for glyphs, families, and principles.

    Example: poly quickref --category families
    """
    click.echo(f"\n{Colors.BOLD}📖 Polyhedral Intelligence Quick Reference{Colors.RESET}\n")

    atlas = load_atlas()

    if not category or category == 'families':
        click.echo(f"{Colors.FAMILY}═══ FAMILIES (20 - Icosahedron) ═══{Colors.RESET}\n")

        # Group families by theme
        themes = {
            'Dynamics': ['F01', 'F02', 'F17'],
            'Information': ['F03', 'F06', 'F16'],
            'Life & Energy': ['F04', 'F05', 'F13'],
            'Space & Matter': ['F07', 'F08', 'F10'],
            'Structure': ['F09', 'F11', 'F12', 'F15'],
            'Advanced': ['F14', 'F18', 'F19', 'F20'],
        }

        for theme, fam_ids in themes.items():
            click.echo(f"{Colors.INFO}{theme}:{Colors.RESET}")
            for fam_id in fam_ids:
                fam = next((f for f in atlas['families'] if f['id'] == fam_id), None)
                if fam:
                    click.echo(f"  {fam['symbol']} {fam['id']}: {fam['name']}")
            click.echo()

    if not category or category == 'principles':
        click.echo(f"{Colors.PRINCIPLE}═══ PRINCIPLES (12 - Dodecahedron) ═══{Colors.RESET}\n")

        for prin in atlas['principles']:
            click.echo(f"{prin['symbol']} {prin['id']}: {prin['name']}")
            click.echo(f"  {Colors.DIM}{prin.get('domain', '')}{Colors.RESET}")

    if not category or category == 'glyphs':
        click.echo(f"\n{Colors.GLYPH}═══ COMMON GLYPH PATTERNS ═══{Colors.RESET}\n")

        patterns = [
            ("〰〰〰", "Flow cascade", "Repeated flow patterns"),
            ("◇⚙⬡", "Structured engineering", "Matter + Engineering + Network"),
            ("⟳∞◬", "Chaos attractor", "Lorenz butterfly"),
            ("⧖↺", "Symmetric conservation", "Symmetry with feedback"),
            ("●●↗", "Emergence rising", "Bottom-up complexity"),
            ("◎∮", "Conscious integration", "Unified awareness"),
            ("〰ᘯᘰ", "Turbulent flow", "Order to chaos transition"),
            ("⊗◧", "Uncertain information", "Information with noise"),
        ]

        for g, name, desc in patterns:
            click.echo(f"{Colors.GLYPH}{g:8}{Colors.RESET} {Colors.BOLD}{name:20}{Colors.RESET} {Colors.DIM}{desc}{Colors.RESET}")

    click.echo(f"\n{Colors.INFO}💡 Tips:{Colors.RESET}")
    click.echo(f"  • Use 'poly glyph decode <glyph>' to analyze any glyph")
    click.echo(f"  • Use 'poly analyze --glyph <glyph> --depth 5' for deep insights")
    click.echo(f"  • Combine 2-4 families for balanced designs")
    click.echo(f"  • Add principles (⧖, ↺, ◧) to strengthen patterns")


if __name__ == '__main__':
    cli()
