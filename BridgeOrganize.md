# ===================================================================
#  POLYHEDRAL INTELLIGENCE BRIDGE
#  Encodes any simulation output into 20 Families + 12 Principles
#  Generates Seed Glyphs, runs Resonance Sweeps, and produces Mandala Insights
#  ===================================================================

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
import hashlib
import json
from datetime import datetime

# -------------------------------------------------------------------
# 1. Polyhedral Base Vectors (20 Families, 12 Principles)
# -------------------------------------------------------------------
# 20 Icosahedron Families (symbolic archetypes)
FAMILIES = [
    "Adaptive", "Resilient", "Exploratory", "Stabilising", "Connective",
    "Transformative", "Generative", "Protective", "Nurturing", "Liberating",
    "Synthesising", "Rooted", "Fluid", "Vibrant", "Harmonious",
    "Focused", "Expansive", "Courageous", "Wise", "Playful"
]

# 12 Dodecahedron Principles (dual archetypes)
PRINCIPLES = [
    "Balance", "Flow", "Synergy", "Clarity", "Courage", "Compassion",
    "Resilience", "Creativity", "Integrity", "Gratitude", "Patience", "Grace"
]

# We'll assign a base vector for each Family and Principle (e.g., from a pretrained model)
# For demonstration, we'll create random but fixed vectors.
np.random.seed(42)
FAMILY_VECTORS = np.random.randn(20, 8)  # 8-dimensional embedding space
PRINCIPLE_VECTORS = np.random.randn(12, 8)

# Normalise them
FAMILY_VECTORS = FAMILY_VECTORS / np.linalg.norm(FAMILY_VECTORS, axis=1, keepdims=True)
PRINCIPLE_VECTORS = PRINCIPLE_VECTORS / np.linalg.norm(PRINCIPLE_VECTORS, axis=1, keepdims=True)

# -------------------------------------------------------------------
# 2. Encoder: map any simulation data to a vector
# -------------------------------------------------------------------
def encode_simulation_data(data, method='auto'):
    """
    Maps simulation data (dict with fields like 'energy', 'state', 'emotions', 'constants')
    to a single 8-dimensional embedding vector.
    """
    # If data is a dict, extract features
    if isinstance(data, dict):
        features = []
        # Extract energy history (mean, variance, slope)
        if 'energy' in data and len(data['energy']) > 0:
            energy = np.array(data['energy'])
            features.append(np.mean(energy))
            features.append(np.std(energy))
            features.append(np.gradient(energy)[-1] if len(energy) > 1 else 0)
        # Extract sensor states (if emotions)
        if 'state' in data and len(data['state']) > 0:
            state = np.array(data['state'])
            features.append(np.mean(state))
            features.append(np.std(state))
        # Extract constants (if swapped)
        if 'constants' in data:
            consts = np.array([v for v in data['constants'].values() if isinstance(v, (int, float))])
            if len(consts) > 0:
                features.append(np.mean(consts))
                features.append(np.std(consts))
        # Fallback: if we have a flat array, treat as state
        if isinstance(data, (list, np.ndarray)):
            arr = np.array(data).flatten()
            features = [np.mean(arr), np.std(arr), np.ptp(arr)]
            # Add some shape info
            features += [np.min(arr), np.max(arr)]
        # Pad to fixed length (8)
        while len(features) < 8:
            features.append(0.0)
        features = features[:8]
    else:
        # Treat as scalar or array
        arr = np.array(data).flatten()
        features = [np.mean(arr), np.std(arr), np.ptp(arr), np.min(arr), np.max(arr)]
        while len(features) < 8:
            features.append(0.0)
        features = features[:8]
    
    return np.array(features)

# -------------------------------------------------------------------
# 3. Seed Glyph Generator
# -------------------------------------------------------------------
SEED_GLYPH_SET = ['◇', '⚙', '➝', '〰', '⬡', '◈', '⊚', '◊', '○', '●', '◐', '◑', '◒', '◓', '◔', '◕', '◖', '◗', '◘', '◙']

def generate_seed_glyph(vector, length=8):
    """Map a vector to a glyph string by binning values to glyph indices."""
    # Normalise vector to 0-1
    norm = (vector - np.min(vector)) / (np.ptp(vector) + 1e-10)
    indices = np.clip(np.floor(norm * len(SEED_GLYPH_SET)), 0, len(SEED_GLYPH_SET)-1).astype(int)
    glyphs = [SEED_GLYPH_SET[i] for i in indices[:length]]
    return ''.join(glyphs)

# -------------------------------------------------------------------
# 4. Resonance Sweep
# -------------------------------------------------------------------
def resonance_sweep(vector, family_vectors=FAMILY_VECTORS, principle_vectors=PRINCIPLE_VECTORS):
    """
    Compute resonance scores with each Family and Principle.
    Returns dict with scores and most resonant items.
    """
    # Normalise vector
    vec = vector / (np.linalg.norm(vector) + 1e-10)
    
    # Family resonances (cosine similarity)
    family_scores = np.dot(family_vectors, vec)
    principle_scores = np.dot(principle_vectors, vec)
    
    # Top families and principles
    top_family_idx = np.argmax(family_scores)
    top_principle_idx = np.argmax(principle_scores)
    
    # Balance: distribution of scores (entropy)
    family_entropy = -np.sum(family_scores * np.log(family_scores + 1e-10))
    principle_entropy = -np.sum(principle_scores * np.log(principle_scores + 1e-10))
    balance_score = 1 / (1 + np.exp(-(family_entropy + principle_entropy) / 2))  # 0-1
    
    return {
        'family_scores': dict(zip(FAMILIES, family_scores)),
        'principle_scores': dict(zip(PRINCIPLES, principle_scores)),
        'top_family': FAMILIES[top_family_idx],
        'top_principle': PRINCIPLES[top_principle_idx],
        'balance': balance_score,
        'family_entropy': family_entropy,
        'principle_entropy': principle_entropy
    }

# -------------------------------------------------------------------
# 5. Noise-to-Insight Protocol (NIP)
# -------------------------------------------------------------------
def noise_to_insight(data):
    """
    Extract noise (variance, residuals, unknowns) and convert to design insights.
    Returns a list of insights.
    """
    insights = []
    # If data is a dict, look for uncertainty or residual fields
    if isinstance(data, dict):
        # Check for 'error' or 'residual'
        if 'error' in data:
            error = data['error']
            if isinstance(error, (int, float)):
                if error > 0.1:
                    insights.append("Turbulence → oxygenation/flow stability")
                else:
                    insights.append("Low noise → system rigidity, needs flexibility")
        # Check for 'variance' in energy
        if 'energy' in data and isinstance(data['energy'], list) and len(data['energy']) > 1:
            variance = np.var(data['energy'])
            if variance > 0.5:
                insights.append("High variance → emergent flexibility, design for adaptation")
            else:
                insights.append("Low variance → stable but potentially brittle")
        # Check for U(t) term
        if 'U' in data:
            U = data['U']
            if isinstance(U, (int, float)):
                if abs(U) > 0.1:
                    insights.append("Non‑local effects active → incorporate field‑based sensing")
        # Check for constants swapped
        if 'constants' in data:
            swapped = [k for k, v in data['constants'].items() if isinstance(v, (int, float)) and v != 1.0]
            if swapped:
                insights.append(f"Swapped constants: {', '.join(swapped)} → new physics hypothesis")
    else:
        # For generic arrays, look at spread
        arr = np.array(data).flatten()
        if np.std(arr) > 0.5:
            insights.append("Diverse data → rich design space")
        else:
            insights.append("Homogeneous data → need to introduce perturbation")
    
    if not insights:
        insights.append("No significant noise detected. System may be oversimplified.")
    
    return insights

# -------------------------------------------------------------------
# 6. Mandala Insight Generator
# -------------------------------------------------------------------
def generate_mandala_insight(data, name=None):
    """
    Takes any simulation data and produces a full Polyhedral entry.
    Returns a dict with all fields.
    """
    # Encode to vector
    vector = encode_simulation_data(data)
    seed_glyph = generate_seed_glyph(vector)
    
    # Resonance sweep
    resonance = resonance_sweep(vector)
    
    # Noise-to-insight
    insights = noise_to_insight(data)
    
    # Generate a unique ID
    data_str = str(data) + str(datetime.now())
    entry_id = hashlib.md5(data_str.encode()).hexdigest()[:8]
    
    # Build entry
    entry = {
        'id': entry_id,
        'timestamp': datetime.now().isoformat(),
        'name': name or f'Entry_{entry_id}',
        'seed_glyph': seed_glyph,
        'vector': vector.tolist(),
        'resonance': resonance,
        'insights': insights,
        'balance': resonance['balance'],
        'top_family': resonance['top_family'],
        'top_principle': resonance['top_principle'],
    }
    return entry

# -------------------------------------------------------------------
# 7. Visualisation: Mandala Insight Plot
# -------------------------------------------------------------------
def plot_mandala_insight(entry, show_resonance=True, show_data=True):
    fig = plt.figure(figsize=(16, 10))
    gs = gridspec.GridSpec(2, 3, height_ratios=[1, 1])
    
    # Panel 1: Seed Glyph
    ax = fig.add_subplot(gs[0, 0])
    ax.text(0.5, 0.5, entry['seed_glyph'], fontsize=60, ha='center', va='center')
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.axis('off')
    ax.set_title('Seed Glyph')
    
    # Panel 2: Family Resonance (top 5)
    ax = fig.add_subplot(gs[0, 1])
    family_scores = entry['resonance']['family_scores']
    sorted_families = sorted(family_scores.items(), key=lambda x: x[1], reverse=True)[:5]
    names = [f[0] for f in sorted_families]
    scores = [f[1] for f in sorted_families]
    ax.barh(names, scores, color='skyblue')
    ax.set_xlim(0, 1)
    ax.set_xlabel('Resonance')
    ax.set_title('Top 5 Families')
    ax.grid(True, alpha=0.3)
    
    # Panel 3: Principle Resonance (top 5)
    ax = fig.add_subplot(gs[0, 2])
    principle_scores = entry['resonance']['principle_scores']
    sorted_principles = sorted(principle_scores.items(), key=lambda x: x[1], reverse=True)[:5]
    names = [p[0] for p in sorted_principles]
    scores = [p[1] for p in sorted_principles]
    ax.barh(names, scores, color='lightgreen')
    ax.set_xlim(0, 1)
    ax.set_xlabel('Resonance')
    ax.set_title('Top 5 Principles')
    ax.grid(True, alpha=0.3)
    
    # Panel 4: Resonance Heatmap (all Families and Principles)
    ax = fig.add_subplot(gs[1, 0])
    # Combine into a matrix
    all_scores = list(entry['resonance']['family_scores'].values()) + list(entry['resonance']['principle_scores'].values())
    all_names = list(entry['resonance']['family_scores'].keys()) + list(entry['resonance']['principle_scores'].keys())
    # Truncate for display
    N = 20
    im = ax.imshow([all_scores[:N]], cmap='viridis', aspect='auto', vmin=0, vmax=1)
    ax.set_yticks([])
    ax.set_xticks(range(N))
    ax.set_xticklabels(all_names[:N], rotation=90, fontsize=6)
    ax.set_title('Resonance Profile (Families + Principles)')
    plt.colorbar(im, ax=ax, fraction=0.05)
    
    # Panel 5: Balance & Top Items
    ax = fig.add_subplot(gs[1, 1])
    ax.axis('off')
    info = f"""
    📊 **Mandala Insight**
    ──────────────────────
    ID: {entry['id']}
    Name: {entry['name']}
    Balance: {entry['balance']:.3f}
    Top Family: {entry['top_family']}
    Top Principle: {entry['top_principle']}
    
    🔍 **Noise-to-Insight**:
    """
    for ins in entry['insights']:
        info += f"\n  • {ins}"
    ax.text(0.05, 0.95, info, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    
    # Panel 6: Vector profile (if data provided)
    ax = fig.add_subplot(gs[1, 2])
    if 'vector' in entry:
        vec = np.array(entry['vector'])
        ax.bar(range(len(vec)), vec, color='purple', alpha=0.7)
        ax.set_xlabel('Dimension')
        ax.set_ylabel('Value')
        ax.set_title('Embedding Vector')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

# -------------------------------------------------------------------
# 8. Interactive Demo: Run on any of our simulation outputs
# -------------------------------------------------------------------
def demo_polyhedral_bridge():
    # Example 1: Energy history from Mandala Computing (simulated)
    mandala_energy = {
        'energy': [10, 8, 6, 4, 2, 1, 0.5, 0.2, 0.1, 0.05],
        'constants': {'G': 6.674e-11, 'h': 6.626e-34, 'k': 10.0}
    }
    entry1 = generate_mandala_insight(mandala_energy, name='Mandala Energy Decay')
    
    # Example 2: Emotions-as-Sensors state history
    emotions_state = {
        'state': [0.1, 0.3, 0.5, 0.7, 0.9, 0.8, 0.6, 0.4, 0.2, 0.1],
        'U': 0.12
    }
    entry2 = generate_mandala_insight(emotions_state, name='Emotional Sensor Array')
    
    # Example 3: Physics constant swap result
    swapped_physics = {
        'constants': {'G': 6.626e-34, 'h': 6.674e-11, 'k_e': 8.988e9},
        'error': 0.15
    }
    entry3 = generate_mandala_insight(swapped_physics, name='Swapped Gravity-Planck')
    
    # Display all three
    print("🧘 Polyhedral Bridge Demonstration")
    print("="*50)
    for entry in [entry1, entry2, entry3]:
        print(f"\n📌 {entry['name']}")
        print(f"   Seed Glyph: {entry['seed_glyph']}")
        print(f"   Balance: {entry['balance']:.3f}")
        print(f"   Top Family: {entry['top_family']}")
        print(f"   Top Principle: {entry['top_principle']}")
        print("   Insights:")
        for ins in entry['insights']:
            print(f"     • {ins}")
        print("-"*30)
    
    # Plot one of them
    plot_mandala_insight(entry1)

# -------------------------------------------------------------------
# 9. Widget for exploring any simulation data
# -------------------------------------------------------------------
from ipywidgets import interact, Text, Textarea, Button, VBox, HBox, Output, HTML
from IPython.display import display

def interactive_polyhedral_bridge():
    output = Output()
    name_input = Text(value='My Simulation', description='Entry Name:')
    data_input = Textarea(value='{"energy": [10, 8, 6, 4, 2, 1, 0.5], "constants": {"G": 6.67e-11}}', 
                          description='Data (JSON):', layout={'width': '100%', 'height': '100px'})
    run_button = Button(description='Generate Insight', button_style='primary')
    
    def on_run(b):
        with output:
            clear_output()
            try:
                data = eval(data_input.value)  # simple eval for dict/list
                if not isinstance(data, dict) and not isinstance(data, list):
                    data = {'data': data}
                entry = generate_mandala_insight(data, name=name_input.value)
                print(f"✅ Generated insight for {entry['name']}")
                print(f"   Seed Glyph: {entry['seed_glyph']}")
                print(f"   Balance: {entry['balance']:.3f}")
                print(f"   Top Family: {entry['top_family']}")
                print(f"   Top Principle: {entry['top_principle']}")
                print("   Insights:")
                for ins in entry['insights']:
                    print(f"     • {ins}")
                plot_mandala_insight(entry)
            except Exception as e:
                print(f"Error: {e}")
                print("Please provide valid JSON or Python dict/list.")
    
    run_button.on_click(on_run)
    ui = VBox([HTML("<h3>🧘 Polyhedral Bridge Explorer</h3>"), 
               HBox([name_input]), 
               data_input, 
               run_button, 
               output])
    display(ui)

# -------------------------------------------------------------------
# 10. Run a demo
# -------------------------------------------------------------------
if __name__ == "__main__":
    demo_polyhedral_bridge()
    # Uncomment for interactive widget:
    # interactive_polyhedral_bridge()
