# Flappy Graphs: Graph Coloring Correlation

## How This Game Relates to Graph Coloring Algorithms

This document explains the deep connection between the **Flappy Graphs** game and the **Graph Coloring Problem** - a fundamental concept in Algorithm Analysis and Design (AAD).

---

## 🎯 The Graph Coloring Problem

**Graph Coloring** is the problem of assigning colors to vertices of a graph such that **no two adjacent vertices share the same color**. The minimum number of colors needed is called the **chromatic number** (χ(G)).

### Formal Definition:
Given a graph G = (V, E), find a function c: V → {1, 2, ..., k} such that:
- For every edge (u, v) ∈ E: c(u) ≠ c(v)
- Minimize k (number of colors used)

---

## 🎮 Game Mechanics as Graph Coloring

### The Graph Structure in Flappy Graphs

| Game Element | Graph Equivalent |
|--------------|------------------|
| **Gaps (Pipes)** | **Vertices** in a path graph |
| **Sequential Gaps** | **Adjacent Vertices** (connected by edges) |
| **Gap Colors** | **Vertex Colors** |
| **Bird's Path** | **A walk through the graph** |

### The Constraint

```
GAME RULE: Cannot pass through the same color twice in a row
     ↓
GRAPH RULE: Adjacent vertices cannot have the same color
```

### Visual Representation

```
Gap 1 ----edge---- Gap 2 ----edge---- Gap 3 ----edge---- Gap 4
 (Red)              (Blue)             (Red)              (Green)
   ✓                  ✓                  ✓                  ✓
   
   Adjacent gaps (vertices connected by edges) MUST have different colors!
```

---

## 🔗 Direct Correlations

### 1. **Path Graph Coloring**

The game creates a **path graph** P_n where:
- Each gap is a vertex
- Consecutive gaps are connected by an edge
- The player must navigate a properly colored path

**Path graphs have χ(P_n) = 2** for n ≥ 2, meaning they can always be colored with just 2 colors alternating. Our game uses 5 colors for variety!

### 2. **Constraint Satisfaction**

Just like graph coloring algorithms must satisfy the constraint:
```
∀(u,v) ∈ E : color(u) ≠ color(v)
```

The game enforces:
```
∀ consecutive gaps (g_i, g_{i+1}) : color(g_i) ≠ color(g_{i+1})
```

### 3. **Greedy Coloring Simulation**

The game's pipe generation mimics a **greedy coloring algorithm**:

```javascript
// Game's Greedy Color Selection (simplified)
do {
    gapColor = randomColor();
} while (gapColor === lastGapColor);  // Avoid adjacent same colors
```

This is similar to:
```python
# Welsh-Powell/Greedy Coloring
for vertex in vertices:
    color = smallest_available_color(vertex, neighbors)
    assign(vertex, color)
```

### 4. **Real-time Constraint Checking**

When the bird passes through a gap:
```javascript
if (currentGapColor === lastGapColor) {
    // CONSTRAINT VIOLATED! (like invalid coloring)
    loseLife();
}
```

This mirrors how graph coloring algorithms verify validity.

---

## 📊 Algorithms Demonstrated

### Welsh-Powell Algorithm Connection

The game's color assignment follows principles similar to **Welsh-Powell**:
1. Consider vertices (gaps) in order
2. Assign colors avoiding conflicts with neighbors
3. The game guarantees valid coloring by design

### DSatur Algorithm Connection

**DSatur** (Degree of Saturation) prioritizes vertices with most colored neighbors. In our game:
- Each new gap has exactly 1 colored neighbor (the previous gap)
- Saturation degree = 1 for all gaps after the first
- Simple constraint: just avoid the previous color

### Backtracking Connection

When the player loses a life for color conflicts:
- It's like a **backtracking step** in coloring algorithms
- "This path didn't work, try again!"
- The player (algorithm) must find a valid path through properly colored vertices

---

## 🧮 Complexity Parallels

| Aspect | Graph Coloring | Flappy Graphs |
|--------|---------------|---------------|
| **Decision Problem** | Is G k-colorable? | Can you survive with given colors? |
| **Optimization** | Minimize colors | Maximize score/survival |
| **Constraint Check** | O(E) per coloring | O(1) per gap (just check last color) |
| **NP-Hardness** | NP-Complete for k≥3 | Game difficulty increases over time! |

---

## 🎓 Educational Value

### What Players Learn:

1. **Constraint Satisfaction**: Understanding that adjacent elements cannot share properties
2. **Sequential Dependencies**: Each decision affects the next valid options
3. **Greedy Thinking**: Making locally optimal choices (avoid last color)
4. **Pattern Recognition**: Identifying valid color sequences

### Real-World Applications Demonstrated:

| Application | Graph Coloring Use | Game Parallel |
|-------------|-------------------|---------------|
| **Register Allocation** | Variables → Registers | Bird → Colored Gaps |
| **Scheduling** | Tasks → Time Slots | Gaps → Safe Passages |
| **Map Coloring** | Regions → Colors | Pipes → Gap Colors |
| **Frequency Assignment** | Transmitters → Frequencies | Sequential → Non-Adjacent |

---

## 🔬 Technical Implementation

### Color Conflict Detection
```javascript
// In checkCollisions() - Graph Coloring Constraint Check
if (birdInGap && !pipe.passedThrough) {
    if (pipe.gapColor === gameState.lastGapColor) {
        // CHROMATIC CONSTRAINT VIOLATION
        loseLife('Same color!');  // Invalid coloring!
    } else {
        // Valid coloring - vertex properly colored
        gameState.lastGapColor = pipe.gapColor;
        addScore();
    }
}
```

### Progressive Difficulty = Increasing Graph Complexity
```javascript
// Speed increases over time
currentSpeed = min(SPEED_START + (time * INCREASE_RATE), SPEED_MAX);

// Like solving larger graphs with more vertices per unit time
// More decisions per second = harder constraint satisfaction
```

---

## 📈 Scoring as Optimization

The game's scoring system mirrors graph coloring optimization:

| Scoring Element | Optimization Parallel |
|-----------------|----------------------|
| **Points per gap** | Successfully colored vertex |
| **Combo multiplier** | Efficient coloring streak |
| **Lives lost** | Backtracking penalty |
| **High score** | Best solution found |

---

## 🎯 Conclusion

**Flappy Graphs** transforms the abstract Graph Coloring Problem into an intuitive, real-time experience:

1. **Vertices** become physical gaps to fly through
2. **Edges** become the sequential nature of gameplay  
3. **Coloring constraints** become survival rules
4. **Algorithm efficiency** becomes player skill

By playing this game, users develop an intuitive understanding of:
- Why adjacent vertices need different colors
- How greedy approaches work for coloring
- The challenge of real-time constraint satisfaction
- The elegance of graph coloring in problem-solving

---

## 📚 References

- **Graph Coloring Problem**: Karp's 21 NP-Complete Problems (1972)
- **Welsh-Powell Algorithm**: Welsh & Powell (1967)
- **DSatur Algorithm**: Brélaz (1979)
- **Greedy Coloring**: Fundamental approach to approximation

---

*This game was created as a bonus feature for the AAD Final Project to demonstrate graph coloring concepts in an interactive and engaging way.*
