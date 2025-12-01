# 🐦 Flappy Graphs: Fly and Color!

A fun, interactive game that teaches graph coloring concepts through gameplay! Inspired by Flappy Bird, this game adds a unique twist where players must navigate through colored gaps while following graph coloring rules.

## 🎮 Game Concept

**Flappy Graphs** combines classic arcade gameplay with graph theory education. Players control a bird that changes colors and must pass through gaps in walls. The challenge? Each gap has a color, and you cannot pass through a gap that has the same color as your previously passed gap - just like in graph coloring where adjacent nodes cannot share the same color!

## 🌟 Features

- **Dynamic Color System**: The bird periodically changes colors, representing different node choices
- **Graph Coloring Rules**: Adjacent gaps (sequential passes) must have different colors
- **Lives System**: 3 lives to master the game mechanics
- **Combo System**: Build combos by making consecutive valid color choices with increasing point multipliers
- **Persistent Leaderboard**: Track your top 10 scores with dates using local storage
- **Responsive Design**: Play on desktop, tablet, or mobile devices
- **Vibrant Arcade Theme**: Eye-catching gradients and animations

## 📋 How to Play

1. **Click or Tap** anywhere on the game screen to make the bird flap and fly upward
2. Gravity pulls the bird down continuously - keep clicking to stay airborne
3. Navigate through the colored gaps between walls
4. **CRITICAL RULE**: You cannot pass through a gap with the same color as your previous gap
5. Earn points for each valid gap you pass through
6. Build combos for multiplied points (1.5x per combo level)
7. Avoid:
   - Hitting walls (top or bottom parts)
   - Passing through gaps with conflicting colors
   - Flying off the top or bottom of the screen
8. You have 3 lives - game ends when all lives are lost

## 🎨 Color System

The game uses 5 distinct colors:
- 🔴 **Red** (#FF6B6B)
- 💙 **Cyan** (#4ECDC4)
- 💛 **Yellow** (#FFE66D)
- 💚 **Green** (#A8E6CF)
- 💗 **Pink** (#FF8B94)

Your bird's color changes every 3 seconds, and gaps are randomly assigned colors that must differ from the previous gap to ensure valid graph coloring paths.

## 🚀 Getting Started

### Prerequisites

- A modern web browser (Chrome, Firefox, Safari, Edge)
- A local web server (optional but recommended)

### Running the Game

#### Option 1: Using Python (Recommended)

```bash
# Navigate to the bonus folder
cd bonus

# Python 3
python -m http.server 8080

# Python 2
python -m SimpleHTTPServer 8080
```

Then open your browser and go to: `http://localhost:8080`

#### Option 2: Using Node.js

```bash
# Install http-server globally (one time)
npm install -g http-server

# Navigate to the bonus folder
cd bonus

# Start the server
http-server -p 8080
```

Then open your browser and go to: `http://localhost:8080`

#### Option 3: Using VS Code Live Server

1. Install the "Live Server" extension in VS Code
2. Right-click on `index.html`
3. Select "Open with Live Server"

#### Option 4: Direct File Access (May have limitations)

Simply open `index.html` directly in your browser. Note: Some browsers may restrict local storage features when opening files directly.

## 📁 File Structure

```
bonus/
├── index.html      # Game structure and UI elements
├── styles.css      # Vibrant arcade-style CSS with animations
├── game.js         # Complete game logic and mechanics
└── README.md       # This file
```

## 🎯 Game Mechanics Explained

### Graph Coloring Integration

The game implements graph coloring rules in an intuitive way:

- Each **gap** represents a **node** in a graph
- Sequential gaps you pass through are **adjacent nodes** (connected by an edge)
- The bird's color when passing through represents the **node's color assignment**
- **Adjacency constraint**: No two adjacent nodes (consecutive gaps) can have the same color

This creates a dynamic path-coloring problem where players must think ahead about valid color choices!

### Scoring System

- **Base Points**: 10 points per valid gap
- **Combo Multiplier**: 1.5x per combo level
  - 1st gap: 10 points
  - 2nd gap: 15 points
  - 3rd gap: 22 points
  - 4th gap: 33 points
  - And so on...
- Combos reset when you lose a life

### Lives System

You start with **3 lives** (❤️❤️❤️). Lose a life by:
- Hitting the top or bottom pipe sections
- Passing through a gap with the same color as the previous gap (violating graph coloring rule)
- Flying off the top or bottom edge of the screen

## 🏆 Leaderboard

The game maintains a persistent leaderboard of your top 10 scores, stored locally in your browser. Each entry includes:
- Final score
- Maximum combo achieved
- Date and time of the game

## 🎨 Technical Stack

- **HTML5**: Structure and canvas element
- **CSS3**: Responsive design with gradients and animations
- **JavaScript (Vanilla)**: Game loop, physics, collision detection, and logic
- **Canvas API**: All game rendering
- **LocalStorage API**: Score persistence

## 🔧 Customization

You can easily customize the game by modifying constants in `game.js`:

```javascript
const CONFIG = {
    CANVAS_WIDTH: 800,        // Game width
    CANVAS_HEIGHT: 600,       // Game height
    GRAVITY: 0.5,             // How fast bird falls
    JUMP_STRENGTH: -9,        // How high bird jumps
    PIPE_SPEED: 3,            // How fast obstacles move
    GAP_HEIGHT: 200,          // Size of gaps
    INITIAL_LIVES: 3,         // Starting lives
    POINTS_PER_PIPE: 10,      // Base score per gap
    COMBO_MULTIPLIER: 1.5,    // Combo bonus
    // ... and more!
};
```

## 🐛 Known Issues & Future Enhancements

### Potential Improvements
- Add difficulty levels (faster pipes, smaller gaps)
- Power-ups (extra lives, slow motion)
- Sound effects and background music
- More complex graph coloring rules (non-sequential adjacency)
- Achievements system
- Multiplayer mode

## 📚 Educational Value

This game teaches:
- **Graph Coloring**: Understanding adjacency constraints
- **Decision Making**: Planning ahead for valid color paths
- **Pattern Recognition**: Identifying valid color sequences
- **Resource Management**: Balancing risk and lives

Perfect for students learning about graph theory or anyone wanting to experience algorithms in an interactive way!

## 📄 License

This project is open source and available for educational purposes.

## 🙏 Credits

Created as a bonus feature for the AAD (Advanced Algorithms and Data Structures) Final Project.

Inspired by:
- **Flappy Bird** by Dong Nguyen (gameplay mechanics)
- **Graph Theory** (graph coloring problem)

---

## 🎮 Quick Start Guide

1. Clone/download the repository
2. Navigate to the `bonus` folder
3. Run a local server: `python -m http.server 8080`
4. Open browser to `http://localhost:8080`
5. Click "Start Game" and begin flying!

**Remember**: Never pass through a gap with the same color as your previous gap! Good luck! 🍀
