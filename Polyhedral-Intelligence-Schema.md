{
“atlas_version”: “1.0.0”,
“description”: “Polyhedral Intelligence: A mandala codex of 20 Families (icosahedron) and 12 Principles (dodecahedron)”,

“families”: [
{
“id”: “F01”,
“name”: “Resonance”,
“symbol”: “≡≡≡”,
“domain”: “Harmonics, standing waves, synchronization, natural frequencies”,
“equations”: [
{
“name”: “Wave Equation (1D Standing Wave)”,
“formula”: “y(x,t) = A sin(kx) cos(ωt)”,
“glyph”: “🎵⚡”,
“glyph_name”: “Glyph of Frozen Vibration”,
“tags”: [“standing-wave”, “harmonics”, “oscillation”]
},
{
“name”: “Kuramoto Model”,
“formula”: “θ̇ᵢ = ωᵢ + (K/N) Σⱼ sin(θⱼ - θᵢ)”,
“glyph”: “⟲⟲⟲”,
“glyph_name”: “Glyph of Phase Lock”,
“tags”: [“synchronization”, “coupled-oscillators”, “emergence”]
},
{
“name”: “Resonance Frequency”,
“formula”: “ω₀ = √(k/m)”,
“glyph”: “∿○”,
“glyph_name”: “Glyph of Natural Voice”,
“tags”: [“eigenfrequency”, “harmonic”, “oscillator”]
},
{
“name”: “Fourier Series”,
“formula”: “f(t) = a₀/2 + Σₙ[aₙcos(nωt) + bₙsin(nωt)]”,
“glyph”: “∿∿∿⊕”,
“glyph_name”: “Glyph of Harmonic Decomposition”,
“tags”: [“frequency-domain”, “decomposition”, “spectrum”]
}
]
},
{
“id”: “F02”,
“name”: “Flow”,
“symbol”: “↻”,
“domain”: “Fluid motion, laminar flow, vorticity, boundary layers”,
“equations”: [
{
“name”: “Navier-Stokes (Incompressible)”,
“formula”: “∂u/∂t + (u·∇)u = -∇p/ρ + ν∇²u + f; ∇·u = 0”,
“glyph”: “〰⇄∇”,
“glyph_name”: “Glyph of Liquid Order”,
“tags”: [“fluid-dynamics”, “momentum”, “conservation”]
},
{
“name”: “Bernoulli’s Equation”,
“formula”: “p + ½ρv² + ρgh = constant”,
“glyph”: “↗⚖↘”,
“glyph_name”: “Glyph of Energy Stream”,
“tags”: [“conservation”, “pressure”, “velocity”]
},
{
“name”: “Reynolds Number”,
“formula”: “Re = ρvL/μ = vL/ν”,
“glyph”: “〰≋”,
“glyph_name”: “Glyph of Flow Character”,
“tags”: [“dimensionless”, “turbulence-threshold”, “similarity”]
},
{
“name”: “Vorticity Equation”,
“formula”: “∂ω/∂t + (u·∇)ω = (ω·∇)u + ν∇²ω”,
“glyph”: “⟳∇”,
“glyph_name”: “Glyph of Spinning Currents”,
“tags”: [“rotation”, “vortex”, “circulation”]
}
]
},
{
“id”: “F03”,
“name”: “Information”,
“symbol”: “⊗”,
“domain”: “Shannon entropy, coding theory, information measures”,
“equations”: [
{
“name”: “Shannon Entropy”,
“formula”: “H(X) = -Σᵢ p(xᵢ) log₂ p(xᵢ)”,
“glyph”: “ℹ◧⊚”,
“glyph_name”: “Glyph of Uncertainty Measure”,
“tags”: [“information-theory”, “entropy”, “uncertainty”]
},
{
“name”: “Channel Capacity”,
“formula”: “C = B log₂(1 + S/N)”,
“glyph”: “📡⚡”,
“glyph_name”: “Glyph of Perfect Signal”,
“tags”: [“bandwidth”, “signal-processing”, “communication”]
},
{
“name”: “Kullback-Leibler Divergence”,
“formula”: “D_KL(P‖Q) = Σᵢ P(i) log[P(i)/Q(i)]”,
“glyph”: “⊗↔⊗”,
“glyph_name”: “Glyph of Distribution Distance”,
“tags”: [“divergence”, “probability”, “relative-entropy”]
},
{
“name”: “Mutual Information”,
“formula”: “I(X;Y) = H(X) + H(Y) - H(X,Y)”,
“glyph”: “⊗∩⊗”,
“glyph_name”: “Glyph of Shared Knowledge”,
“tags”: [“correlation”, “dependency”, “information-flow”]
}
]
},
{
“id”: “F04”,
“name”: “Life”,
“symbol”: “••••”,
“domain”: “Population dynamics, metabolic networks, genetic regulation”,
“equations”: [
{
“name”: “Lotka-Volterra Equations”,
“formula”: “dx/dt = αx - βxy; dy/dt = δxy - γy”,
“glyph”: “🐇🦊⟲”,
“glyph_name”: “Glyph of Predator Dance”,
“tags”: [“ecology”, “population”, “oscillation”]
},
{
“name”: “Michaelis-Menten Kinetics”,
“formula”: “v = (V_max[S])/(K_m + [S])”,
“glyph”: “⚗️🔑”,
“glyph_name”: “Glyph of Enzyme Gateway”,
“tags”: [“biochemistry”, “catalysis”, “saturation”]
},
{
“name”: “Logistic Growth”,
“formula”: “dN/dt = rN(1 - N/K)”,
“glyph”: “📈⊂”,
“glyph_name”: “Glyph of Bounded Bloom”,
“tags”: [“population”, “carrying-capacity”, “s-curve”]
},
{
“name”: “Hill Equation”,
“formula”: “θ = [L]ⁿ/(K_d + [L]ⁿ)”,
“glyph”: “⚗️ⁿ”,
“glyph_name”: “Glyph of Cooperative Binding”,
“tags”: [“cooperativity”, “allosteric”, “binding”]
}
]
},
{
“id”: “F05”,
“name”: “Energy-Thermo”,
“symbol”: “△≈”,
“domain”: “Heat transfer, entropy, thermodynamic potentials”,
“equations”: [
{
“name”: “First Law of Thermodynamics”,
“formula”: “dU = δQ - δW”,
“glyph”: “🔥⚖️”,
“glyph_name”: “Glyph of Energy Conservation”,
“tags”: [“conservation”, “energy”, “internal-energy”]
},
{
“name”: “Second Law (Entropy)”,
“formula”: “dS ≥ δQ/T”,
“glyph”: “⏳↗”,
“glyph_name”: “Glyph of Time’s Arrow”,
“tags”: [“entropy”, “irreversibility”, “disorder”]
},
{
“name”: “Heat Equation”,
“formula”: “∂T/∂t = α∇²T”,
“glyph”: “🌡️〰”,
“glyph_name”: “Glyph of Thermal Diffusion”,
“tags”: [“diffusion”, “temperature”, “parabolic-pde”]
},
{
“name”: “Carnot Efficiency”,
“formula”: “η = 1 - T_c/T_h”,
“glyph”: “⚙️🔥❄️”,
“glyph_name”: “Glyph of Maximum Work”,
“tags”: [“thermodynamics”, “efficiency”, “heat-engine”]
}
]
},
{
“id”: “F06”,
“name”: “Cognition”,
“symbol”: “⋯⋯”,
“domain”: “Neural dynamics, learning rules, cognitive models”,
“equations”: [
{
“name”: “Hopfield Network Energy”,
“formula”: “E = -½ΣᵢΣⱼ wᵢⱼsᵢsⱼ + Σᵢ θᵢsᵢ”,
“glyph”: “🧠⚡⬇️”,
“glyph_name”: “Glyph of Memory Wells”,
“tags”: [“neural-network”, “attractor”, “energy-landscape”]
},
{
“name”: “Hebbian Learning”,
“formula”: “Δwᵢⱼ = η xᵢ xⱼ”,
“glyph”: “⚡⚡➕”,
“glyph_name”: “Glyph of Neurons That Fire Together”,
“tags”: [“learning”, “plasticity”, “correlation”]
},
{
“name”: “Sigmoid Activation”,
“formula”: “σ(x) = 1/(1 + e⁻ˣ)”,
“glyph”: “〰S”,
“glyph_name”: “Glyph of Soft Decision”,
“tags”: [“activation-function”, “nonlinearity”, “neural-network”]
},
{
“name”: “Backpropagation”,
“formula”: “∂E/∂wᵢⱼ = (∂E/∂oⱼ)(∂oⱼ/∂netⱼ)(∂netⱼ/∂wᵢⱼ)”,
“glyph”: “↩️∇”,
“glyph_name”: “Glyph of Error Descent”,
“tags”: [“gradient”, “learning”, “chain-rule”]
}
]
},
{
“id”: “F07”,
“name”: “Earth-Cosmos”,
“symbol”: “◯”,
“domain”: “Planetary motion, orbital mechanics, celestial dynamics”,
“equations”: [
{
“name”: “Kepler’s Third Law”,
“formula”: “T² = (4π²/GM)a³”,
“glyph”: “🪐⟲³”,
“glyph_name”: “Glyph of Orbital Harmony”,
“tags”: [“orbital-mechanics”, “period”, “kepler”]
},
{
“name”: “Newton’s Gravitation”,
“formula”: “F = G(m₁m₂)/r²”,
“glyph”: “●●⬌”,
“glyph_name”: “Glyph of Universal Pull”,
“tags”: [“gravity”, “force”, “inverse-square”]
},
{
“name”: “Orbital Velocity”,
“formula”: “v = √(GM/r)”,
“glyph”: “⟲💨”,
“glyph_name”: “Glyph of Circular Motion”,
“tags”: [“velocity”, “orbit”, “mechanics”]
},
{
“name”: “Tidal Force”,
“formula”: “ΔF ∝ (2GMm/r³)Δr”,
“glyph”: “🌊🌙”,
“glyph_name”: “Glyph of Moon’s Grasp”,
“tags”: [“tides”, “gradient”, “differential-force”]
}
]
},
{
“id”: “F08”,
“name”: “Matter”,
“symbol”: “◆”,
“domain”: “Phase transitions, crystal structures, material properties”,
“equations”: [
{
“name”: “Ising Model”,
“formula”: “H = -J Σ_⟨i,j⟩ sᵢsⱼ - h Σᵢ sᵢ”,
“glyph”: “⬆️⬇️⬆️⬇️”,
“glyph_name”: “Glyph of Magnetic Alignment”,
“tags”: [“phase-transition”, “spin”, “magnetism”]
},
{
“name”: “BCS Gap Equation”,
“formula”: “Δ = λ∫₀^(ω_D) tanh(√(ξ² + Δ²)/(2k_BT))/√(ξ² + Δ²) dξ”,
“glyph”: “⚡⚡❄️”,
“glyph_name”: “Glyph of Superconducting Pairing”,
“tags”: [“superconductivity”, “cooper-pairs”, “gap”]
},
{
“name”: “London Equation”,
“formula”: “∇×J_s = -(n_s e²/m)B”,
“glyph”: “🧲↺”,
“glyph_name”: “Glyph of Perfect Diamagnet”,
“tags”: [“superconductivity”, “meissner-effect”, “current”]
},
{
“name”: “Drude Model”,
“formula”: “σ = ne²τ/m”,
“glyph”: “⚡〰”,
“glyph_name”: “Glyph of Electron Flow”,
“tags”: [“conductivity”, “electrons”, “classical”]
}
]
},
{
“id”: “F09”,
“name”: “Geometry”,
“symbol”: “☆”,
“domain”: “Euclidean and non-Euclidean theorems, curvature”,
“equations”: [
{
“name”: “Pythagorean Theorem”,
“formula”: “a² + b² = c²”,
“glyph”: “△²”,
“glyph_name”: “Glyph of Right Triangle”,
“tags”: [“euclidean”, “geometry”, “fundamental”]
},
{
“name”: “Gaussian Curvature”,
“formula”: “K = κ₁κ₂”,
“glyph”: “⌒⌓”,
“glyph_name”: “Glyph of Surface Bending”,
“tags”: [“differential-geometry”, “curvature”, “intrinsic”]
},
{
“name”: “Gauss-Bonnet Theorem”,
“formula”: “∫∫_M K dA + ∫_∂M κ_g ds = 2πχ(M)”,
“glyph”: “∮⚫”,
“glyph_name”: “Glyph of Topological Constraint”,
“tags”: [“topology”, “curvature”, “euler-characteristic”]
},
{
“name”: “Parallel Postulate”,
“formula”: “Through a point not on a line, exactly one parallel exists”,
“glyph”: “∥”,
“glyph_name”: “Glyph of Flat Space”,
“tags”: [“euclidean”, “axiom”, “parallel”]
}
]
},
{
“id”: “F10”,
“name”: “Particle”,
“symbol”: “⚪”,
“domain”: “Standard Model, quantum field theory, particle interactions”,
“equations”: [
{
“name”: “Dirac Equation”,
“formula”: “(iγ^μ∂_μ - m)ψ = 0”,
“glyph”: “⚛️↻”,
“glyph_name”: “Glyph of Spinning Electron”,
“tags”: [“relativistic”, “fermion”, “spin”]
},
{
“name”: “Klein-Gordon Equation”,
“formula”: “(∂²/∂t² - ∇² + m²)φ = 0”,
“glyph”: “⚪〰”,
“glyph_name”: “Glyph of Scalar Field”,
“tags”: [“relativistic”, “boson”, “scalar”]
},
{
“name”: “Yang-Mills Field Strength”,
“formula”: “F^a_μν = ∂_μA^a_ν - ∂_νA^a_μ + gf^(abc)A^b_μA^c_ν”,
“glyph”: “⚡∇⚡”,
“glyph_name”: “Glyph of Gauge Force”,
“tags”: [“gauge-theory”, “non-abelian”, “force”]
},
{
“name”: “Higgs Mechanism”,
“formula”: “V(φ) = -μ²|φ|² + λ|φ|⁴”,
“glyph”: “⚪⬇️⚡”,
“glyph_name”: “Glyph of Mass Generation”,
“tags”: [“symmetry-breaking”, “mass”, “higgs”]
}
]
},
{
“id”: “F11”,
“name”: “Engineering”,
“symbol”: “⚙”,
“domain”: “Stress/strain, circuit laws, control theory”,
“equations”: [
{
“name”: “Hooke’s Law”,
“formula”: “σ = Eε”,
“glyph”: “⟷↔”,
“glyph_name”: “Glyph of Elastic Response”,
“tags”: [“mechanics”, “elasticity”, “linear”]
},
{
“name”: “Ohm’s Law”,
“formula”: “V = IR”,
“glyph”: “⚡〰⚡”,
“glyph_name”: “Glyph of Resistive Flow”,
“tags”: [“circuits”, “electricity”, “resistance”]
},
{
“name”: “Euler-Bernoulli Beam”,
“formula”: “EI(∂⁴w/∂x⁴) = q(x)”,
“glyph”: “⎯⌒⎯”,
“glyph_name”: “Glyph of Bending Beam”,
“tags”: [“structural”, “beam”, “deflection”]
},
{
“name”: “PID Controller”,
“formula”: “u(t) = K_p e(t) + K_i∫e(τ)dτ + K_d(de/dt)”,
“glyph”: “↻⚖️”,
“glyph_name”: “Glyph of Feedback Mastery”,
“tags”: [“control”, “feedback”, “pid”]
}
]
},
{
“id”: “F12”,
“name”: “Networks”,
“symbol”: “⬡”,
“domain”: “Graph theory, network topology, percolation”,
“equations”: [
{
“name”: “Power Law Degree Distribution”,
“formula”: “P(k) ∝ k^(-γ)”,
“glyph”: “⬡⬡⬡↘”,
“glyph_name”: “Glyph of Scale-Free Network”,
“tags”: [“network”, “scale-free”, “hubs”]
},
{
“name”: “Clustering Coefficient”,
“formula”: “C = (3 × # triangles)/(# connected triples)”,
“glyph”: “△⬡”,
“glyph_name”: “Glyph of Local Cohesion”,
“tags”: [“clustering”, “graph”, “topology”]
},
{
“name”: “Percolation Threshold”,
“formula”: “p_c ≈ 1/⟨k⟩”,
“glyph”: “⬡⚡⬡”,
“glyph_name”: “Glyph of Critical Connection”,
“tags”: [“percolation”, “threshold”, “phase-transition”]
},
{
“name”: “Laplacian Matrix”,
“formula”: “L = D - A”,
“glyph”: “∇⬡”,
“glyph_name”: “Glyph of Network Structure”,
“tags”: [“graph-theory”, “spectral”, “laplacian”]
}
]
},
{
“id”: “F13”,
“name”: “Reaction”,
“symbol”: “⇑”,
“domain”: “Chemical kinetics, catalysis, rate laws”,
“equations”: [
{
“name”: “Arrhenius Equation”,
“formula”: “k = Ae^(-E_a/RT)”,
“glyph”: “🌡️⚡⬆️”,
“glyph_name”: “Glyph of Temperature Barrier”,
“tags”: [“kinetics”, “activation-energy”, “temperature”]
},
{
“name”: “Transition State Theory”,
“formula”: “k = (k_BT/h)e^(-ΔG‡/RT)”,
“glyph”: “⚗️⛰️⚗️”,
“glyph_name”: “Glyph of Activated Complex”,
“tags”: [“transition-state”, “kinetics”, “thermodynamics”]
},
{
“name”: “Mass Action Law”,
“formula”: “Rate = k[A]^m[B]^n”,
“glyph”: “⚗️×⚗️”,
“glyph_name”: “Glyph of Concentration Power”,
“tags”: [“rate-law”, “kinetics”, “concentration”]
},
{
“name”: “Autocatalytic Reaction”,
“formula”: “A + B → 2B; Rate = k[A][B]”,
“glyph”: “⚗️↻⚗️⚗️”,
“glyph_name”: “Glyph of Self-Amplification”,
“tags”: [“autocatalysis”, “feedback”, “exponential”]
}
]
},
{
“id”: “F14”,
“name”: “Measurement”,
“symbol”: “↕”,
“domain”: “Uncertainty quantification, calibration, error propagation”,
“equations”: [
{
“name”: “Standard Deviation”,
“formula”: “σ = √[Σ(xᵢ - μ)²/N]”,
“glyph”: “↕️📊”,
“glyph_name”: “Glyph of Scatter Measure”,
“tags”: [“statistics”, “variance”, “dispersion”]
},
{
“name”: “Uncertainty Propagation”,
“formula”: “δf = √[Σᵢ(∂f/∂xᵢ)²(δxᵢ)²]”,
“glyph”: “◧↗”,
“glyph_name”: “Glyph of Error Flow”,
“tags”: [“error”, “propagation”, “uncertainty”]
},
{
“name”: “Signal-to-Noise Ratio”,
“formula”: “SNR = P_signal/P_noise”,
“glyph”: “📡/〰”,
“glyph_name”: “Glyph of Clarity Index”,
“tags”: [“signal-processing”, “noise”, “quality”]
},
{
“name”: “Buckingham Pi Theorem”,
“formula”: “n - k independent dimensionless groups”,
“glyph”: “π▭”,
“glyph_name”: “Glyph of Dimensional Reduction”,
“tags”: [“dimensional-analysis”, “similarity”, “scaling”]
}
]
},
{
“id”: “F15”,
“name”: “Navigation”,
“symbol”: “◆→”,
“domain”: “Geodesics, GPS corrections, optimal routing”,
“equations”: [
{
“name”: “Haversine Formula”,
“formula”: “d = 2r arcsin(√[sin²(Δφ/2) + cos φ₁ cos φ₂ sin²(Δλ/2)])”,
“glyph”: “🌍⌒”,
“glyph_name”: “Glyph of Great Circle”,
“tags”: [“geodesy”, “distance”, “sphere”]
},
{
“name”: “Dijkstra’s Algorithm”,
“formula”: “dist[v] = min(dist[v], dist[u] + weight(u,v))”,
“glyph”: “◆→◆→◆”,
“glyph_name”: “Glyph of Shortest Path”,
“tags”: [“graph”, “pathfinding”, “optimization”]
},
{
“name”: “Geodesic Equation”,
“formula”: “d²x^μ/ds² + Γ^μ_αβ(dx^α/ds)(dx^β/ds) = 0”,
“glyph”: “⌒∇”,
“glyph_name”: “Glyph of Curved Journey”,
“tags”: [“differential-geometry”, “geodesic”, “path”]
},
{
“name”: “Kalman Filter”,
“formula”: “x̂_k = x̂_k⁻ + K_k(z_k - Hx̂_k⁻)”,
“glyph”: “↻📡”,
“glyph_name”: “Glyph of Optimal Estimate”,
“tags”: [“estimation”, “filtering”, “optimal”]
}
]
},
{
“id”: “F16”,
“name”: “Consciousness”,
“symbol”: “◎”,
“domain”: “Neural oscillations, integrated information, awareness”,
“equations”: [
{
“name”: “Integrated Information (Φ)”,
“formula”: “Φ = min I(X₁^past; X₂^present|X₃^past)”,
“glyph”: “◎∮”,
“glyph_name”: “Glyph of Conscious Unity”,
“tags”: [“consciousness”, “integration”, “iit”]
},
{
“name”: “Global Workspace Broadcasting”,
“formula”: “Attention(x) = Σᵢ wᵢ activation(xᵢ)”,
“glyph”: “◎⚡”,
“glyph_name”: “Glyph of Spotlight Mind”,
“tags”: [“attention”, “consciousness”, “broadcasting”]
},
{
“name”: “Phase-Locking Value”,
“formula”: “PLV = |⟨e^(i(θ₁(t)-θ₂(t)))⟩|”,
“glyph”: “∿∿⟲”,
“glyph_name”: “Glyph of Brain Coherence”,
“tags”: [“synchrony”, “oscillation”, “coherence”]
},
{
“name”: “Free Energy Principle”,
“formula”: “F = ⟨-ln P(s,ψ|m)⟩_Q(ψ|μ)”,
“glyph”: “◎⬇️”,
“glyph_name”: “Glyph of Prediction Error”,
“tags”: [“predictive-coding”, “bayesian”, “friston”]
}
]
},
{
“id”: “F17”,
“name”: “Turbulence”,
“symbol”: “ᘯᘰ”,
“domain”: “Unpredictable flow, sensitive dependence, fractal turbulence”,
“equations”: [
{
“name”: “Lorenz Attractor”,
“formula”: “x’ = σ(y - x); y’ = x(ρ - z) - y; z’ = xy - βz”,
“glyph”: “⟳∞◬”,
“glyph_name”: “Glyph of Butterfly Worlds”,
“tags”: [“chaos”, “attractor”, “sensitive-dependence”]
},
{
“name”: “Kolmogorov Turbulence Scaling”,
“formula”: “E(k) ∝ k^(-5/3)”,
“glyph”: “〰↘〰”,
“glyph_name”: “Glyph of Energy Cascade”,
“tags”: [“turbulence”, “spectrum”, “scaling”]
},
{
“name”: “Feigenbaum Constants”,
“formula”: “δ ≈ 4.669; α ≈ 2.5029”,
“glyph”: “⑂⑂⑂”,
“glyph_name”: “Glyph of Universal Bifurcation”,
“tags”: [“chaos”, “universality”, “period-doubling”]
},
{
“name”: “Navier-Stokes Chaos Regimes”,
“formula”: “∂u/∂t + (u·∇)u = -∇p + ν∇²u + f”,
“glyph”: “〰ᘯᘰ”,
“glyph_name”: “Glyph of Flow Unbound”,
“tags”: [“turbulence”, “chaos”, “fluid-dynamics”]
}
]
},
{
“id”: “F18”,
“name”: “Relativity”,
“symbol”: “⊗≡”,
“domain”: “Spacetime curvature, gravitational waves, relativistic effects”,
“equations”: [
{
“name”: “Einstein Field Equations”,
“formula”: “Rμν - ½Rgμν + Λgμν = (8πG/c

