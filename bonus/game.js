// Game Configuration
const CONFIG = {
    CANVAS_WIDTH: 800,
    CANVAS_HEIGHT: 600,
    BIRD_WIDTH: 40,
    BIRD_HEIGHT: 40,
    BIRD_X: 150,
    GRAVITY: 0.25,
    JUMP_STRENGTH: -7,
    MAX_FALL_SPEED: 6,
    PIPE_WIDTH: 80,
    GAP_HEIGHT: 220,
    PIPE_SPEED_START: 1.5,      // Starting speed (slow)
    PIPE_SPEED_MAX: 4.5,         // Maximum speed
    SPEED_INCREASE_RATE: 0.05,   // Speed increase per second
    PIPE_SPAWN_INTERVAL: 2500,
    MIN_PIPE_HEIGHT: 50,
    COLORS: ['#FF6B6B', '#4ECDC4', '#FFE66D', '#A8E6CF', '#FF8B94'],
    COLOR_NAMES: {
        '#FF6B6B': 'Red',
        '#4ECDC4': 'Cyan',
        '#FFE66D': 'Yellow',
        '#A8E6CF': 'Green',
        '#FF8B94': 'Pink'
    },
    INITIAL_LIVES: 3,
    POINTS_PER_PIPE: 10,
    COMBO_MULTIPLIER: 1.5,
    COLOR_CHANGE_INTERVAL: 3000,
};

// Game State
let gameState = {
    animationId: null,
    lastFrameTime: 0,
    currentScreen: 'start',
    bird: {
        y: CONFIG.CANVAS_HEIGHT / 2,
        velocity: 0,
        color: CONFIG.COLORS[0],
        colorIndex: 0
    },
    pipes: [],
    lastPipeTime: 0,
    score: 0,
    highScore: 0,
    lives: CONFIG.INITIAL_LIVES,
    combo: 0,
    maxCombo: 0,
    lastGapColor: null,
    isPaused: false,
    isGameOver: false,
    lastColorChangeTime: 0,
    gameStarted: false,
    isReady: false,
    explosions: [],
    screenFlash: 0,
    screenShake: 0,
    gameStartTime: 0,
    currentSpeed: CONFIG.PIPE_SPEED_START,
};

// DOM Elements
const canvas = document.getElementById('game-canvas');
const ctx = canvas.getContext('2d');

const screens = {
    start: document.getElementById('start-screen'),
    leaderboard: document.getElementById('leaderboard-screen'),
    game: document.getElementById('game-screen'),
    pause: document.getElementById('pause-screen'),
    gameOver: document.getElementById('game-over-screen')
};

const buttons = {
    start: document.getElementById('start-btn'),
    leaderboard: document.getElementById('leaderboard-btn'),
    backFromLeaderboard: document.getElementById('back-from-leaderboard-btn'),
    pause: document.getElementById('pause-btn'),
    resume: document.getElementById('resume-btn'),
    restartFromPause: document.getElementById('restart-from-pause-btn'),
    quit: document.getElementById('quit-btn'),
    restart: document.getElementById('restart-btn'),
    menu: document.getElementById('menu-btn')
};

const hudElements = {
    score: document.getElementById('score-display'),
    highScore: document.getElementById('high-score-display'),
    lives: document.getElementById('lives-display'),
    birdColor: document.getElementById('bird-color-display'),
    combo: document.getElementById('combo-display')
};

const gameOverElements = {
    finalScore: document.getElementById('final-score'),
    finalHighScore: document.getElementById('final-high-score'),
    maxCombo: document.getElementById('max-combo'),
    newHighScoreMsg: document.getElementById('new-high-score-msg')
};

// Initialize
function init() {
    setupCanvas();
    loadHighScore();
    attachEventListeners();
    updateHUD();
}

function setupCanvas() {
    canvas.width = CONFIG.CANVAS_WIDTH;
    canvas.height = CONFIG.CANVAS_HEIGHT;
    
    // Scale to fit screen
    const maxWidth = window.innerWidth - 40;
    const maxHeight = window.innerHeight - 120;
    
    const scaleX = maxWidth / CONFIG.CANVAS_WIDTH;
    const scaleY = maxHeight / CONFIG.CANVAS_HEIGHT;
    const scale = Math.min(scaleX, scaleY, 1);
    
    canvas.style.width = `${CONFIG.CANVAS_WIDTH * scale}px`;
    canvas.style.height = `${CONFIG.CANVAS_HEIGHT * scale}px`;
    
    console.log('Canvas setup:', canvas.width, canvas.height, 'scale:', scale);
}

function attachEventListeners() {
    buttons.start.addEventListener('click', startGame);
    buttons.leaderboard.addEventListener('click', showLeaderboard);
    buttons.backFromLeaderboard.addEventListener('click', () => showScreen('start'));
    buttons.pause.addEventListener('click', pauseGame);
    buttons.resume.addEventListener('click', resumeGame);
    buttons.restartFromPause.addEventListener('click', restartGame);
    buttons.quit.addEventListener('click', quitToMenu);
    buttons.restart.addEventListener('click', restartGame);
    buttons.menu.addEventListener('click', quitToMenu);
    
    // Click anywhere on game screen to jump
    screens.game.addEventListener('click', function(e) {
        if (e.target !== buttons.pause) {
            handleJump();
        }
    });
    screens.game.addEventListener('touchstart', function(e) {
        if (e.target !== buttons.pause) {
            handleJump();
        }
    });
    
    // Also space bar
    document.addEventListener('keydown', (e) => {
        if (e.code === 'Space') {
            e.preventDefault();
            handleJump();
        }
    });
    
    window.addEventListener('resize', setupCanvas);
}

function showScreen(screenName) {
    Object.values(screens).forEach(screen => screen.classList.remove('active'));
    screens[screenName].classList.add('active');
    gameState.currentScreen = screenName;
}

function showLeaderboard() {
    displayLeaderboard();
    showScreen('leaderboard');
}

function startGame() {
    resetGame();
    showScreen('game');
    gameState.isReady = false;
    gameState.gameStarted = false;
    
    // Show "Get Ready" and wait for click
    renderGetReady();
}

function renderGetReady() {
    ctx.clearRect(0, 0, CONFIG.CANVAS_WIDTH, CONFIG.CANVAS_HEIGHT);
    
    // CS-themed background
    const gradient = ctx.createLinearGradient(0, 0, 0, CONFIG.CANVAS_HEIGHT);
    gradient.addColorStop(0, '#1a1a2e');
    gradient.addColorStop(0.5, '#16213e');
    gradient.addColorStop(1, '#0f3460');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, CONFIG.CANVAS_WIDTH, CONFIG.CANVAS_HEIGHT);
    
    drawCodeBackground();
    drawGrid();
    drawBird();
    
    // Get Ready text with glow
    ctx.shadowBlur = 20;
    ctx.shadowColor = '#00ff00';
    ctx.fillStyle = '#00ff00';
    ctx.font = 'bold 52px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('GET READY!', CONFIG.CANVAS_WIDTH / 2, 150);
    ctx.shadowBlur = 0;
    
    ctx.fillStyle = '#ffffff';
    ctx.font = '24px Arial';
    ctx.fillText('Click or Press Space to Flap', CONFIG.CANVAS_WIDTH / 2, 220);
    
    ctx.fillStyle = '#ff6b6b';
    ctx.fillText('Avoid same color gaps in a row!', CONFIG.CANVAS_WIDTH / 2, 260);
    
    // Pulsing start text
    const pulse = Math.sin(Date.now() / 200) * 0.3 + 0.7;
    ctx.globalAlpha = pulse;
    ctx.font = 'bold 32px Arial';
    ctx.fillStyle = '#00ffff';
    ctx.shadowBlur = 15;
    ctx.shadowColor = '#00ffff';
    ctx.fillText('[ Click to Start ]', CONFIG.CANVAS_WIDTH / 2, 350);
    ctx.shadowBlur = 0;
    ctx.globalAlpha = 1;
}

function actuallyStartGame() {
    gameState.isReady = true;
    gameState.gameStarted = true;
    gameState.gameStartTime = performance.now();
    gameState.lastFrameTime = performance.now();
    gameState.lastPipeTime = performance.now() + 2000;
    gameState.lastColorChangeTime = performance.now();
    gameLoop(performance.now());
}

function gameLoop(currentTime) {
    if (gameState.isGameOver || gameState.isPaused) return;
    
    gameState.lastFrameTime = currentTime;
    
    updateBird();
    updatePipes(currentTime);
    updateBirdColor(currentTime);
    updateExplosions();
    checkCollisions();
    render();
    
    gameState.animationId = requestAnimationFrame(gameLoop);
}

function updateBird() {
    gameState.bird.velocity += CONFIG.GRAVITY;
    gameState.bird.velocity = Math.min(gameState.bird.velocity, CONFIG.MAX_FALL_SPEED);
    gameState.bird.y += gameState.bird.velocity;
    
    // Keep in bounds
    if (gameState.bird.y < 0) {
        gameState.bird.y = 0;
        gameState.bird.velocity = 0;
    }
    
    if (gameState.bird.y + CONFIG.BIRD_HEIGHT > CONFIG.CANVAS_HEIGHT) {
        gameState.bird.y = CONFIG.CANVAS_HEIGHT - CONFIG.BIRD_HEIGHT;
        gameState.bird.velocity = 0;
    }
}

function handleJump() {
    if (gameState.currentScreen !== 'game' || gameState.isPaused || gameState.isGameOver) return;
    
    // First click starts the game
    if (!gameState.isReady) {
        actuallyStartGame();
    }
    
    gameState.bird.velocity = CONFIG.JUMP_STRENGTH;
}

function updateBirdColor(currentTime) {
    if (currentTime - gameState.lastColorChangeTime > CONFIG.COLOR_CHANGE_INTERVAL) {
        gameState.lastColorChangeTime = currentTime;
        const newColorIndex = Math.floor(Math.random() * CONFIG.COLORS.length);
        gameState.bird.colorIndex = newColorIndex;
        gameState.bird.color = CONFIG.COLORS[newColorIndex];
        updateHUD();
    }
}

function updatePipes(currentTime) {
    if (currentTime - gameState.lastPipeTime > CONFIG.PIPE_SPAWN_INTERVAL) {
        spawnPipe();
        gameState.lastPipeTime = currentTime;
    }
    
    // Calculate current speed based on time played
    const timePlayed = (currentTime - gameState.gameStartTime) / 1000; // in seconds
    gameState.currentSpeed = Math.min(
        CONFIG.PIPE_SPEED_START + (timePlayed * CONFIG.SPEED_INCREASE_RATE),
        CONFIG.PIPE_SPEED_MAX
    );
    
    for (let i = gameState.pipes.length - 1; i >= 0; i--) {
        const pipe = gameState.pipes[i];
        pipe.x -= gameState.currentSpeed;
        
        if (pipe.x + CONFIG.PIPE_WIDTH < 0) {
            gameState.pipes.splice(i, 1);
        }
    }
}

function spawnPipe() {
    const minGapY = CONFIG.MIN_PIPE_HEIGHT;
    const maxGapY = CONFIG.CANVAS_HEIGHT - CONFIG.MIN_PIPE_HEIGHT - CONFIG.GAP_HEIGHT;
    const gapY = Math.random() * (maxGapY - minGapY) + minGapY;
    
    let gapColor;
    let attempts = 0;
    do {
        const colorIndex = Math.floor(Math.random() * CONFIG.COLORS.length);
        gapColor = CONFIG.COLORS[colorIndex];
        attempts++;
    } while (gapColor === gameState.lastGapColor && CONFIG.COLORS.length > 1 && attempts < 10);
    
    gameState.pipes.push({
        x: CONFIG.CANVAS_WIDTH,
        gapY: gapY,
        gapColor: gapColor,
        scored: false,
        passedThrough: false
    });
}

function checkCollisions() {
    // Don't check collisions for first 1 second
    if (performance.now() - gameState.gameStartTime < 1000) return;
    
    const birdLeft = CONFIG.BIRD_X;
    const birdRight = CONFIG.BIRD_X + CONFIG.BIRD_WIDTH;
    const birdTop = gameState.bird.y;
    const birdBottom = gameState.bird.y + CONFIG.BIRD_HEIGHT;
    
    for (const pipe of gameState.pipes) {
        const pipeLeft = pipe.x;
        const pipeRight = pipe.x + CONFIG.PIPE_WIDTH;
        const gapTop = pipe.gapY;
        const gapBottom = pipe.gapY + CONFIG.GAP_HEIGHT;
        
        // Check if bird is overlapping with pipe
        if (birdRight > pipeLeft && birdLeft < pipeRight) {
            const inGap = birdTop >= gapTop && birdBottom <= gapBottom;
            
            if (inGap) {
                pipe.passedThrough = true;
            } else if (!pipe.scored) {
                // Hit the pipe
                pipe.scored = true;
                loseLife('Hit pipe!');
            }
        }
        
        // Award points when bird passes pipe
        if (!pipe.scored && pipe.x + CONFIG.PIPE_WIDTH < CONFIG.BIRD_X) {
            pipe.scored = true;
            
            if (pipe.passedThrough) {
                // Check color rule
                if (gameState.lastGapColor !== null && pipe.gapColor === gameState.lastGapColor) {
                    loseLife('Same color!');
                } else {
                    awardPoints();
                    gameState.lastGapColor = pipe.gapColor;
                }
            }
        }
    }
}

function awardPoints() {
    gameState.combo++;
    const points = Math.floor(CONFIG.POINTS_PER_PIPE * Math.pow(CONFIG.COMBO_MULTIPLIER, gameState.combo - 1));
    gameState.score += points;
    
    if (gameState.combo > gameState.maxCombo) {
        gameState.maxCombo = gameState.combo;
    }
    
    updateHUD();
}

function loseLife(reason) {
    if (gameState.isGameOver) return;
    
    // Create explosion at bird position
    createExplosion(CONFIG.BIRD_X + CONFIG.BIRD_WIDTH/2, gameState.bird.y + CONFIG.BIRD_HEIGHT/2, reason);
    
    gameState.lives--;
    gameState.combo = 0;
    updateHUD();
    
    // Flash screen red and shake
    gameState.screenFlash = 20;
    gameState.screenShake = 15;
    
    if (gameState.lives <= 0) {
        endGame();
    }
}

function createExplosion(x, y, reason) {
    const colors = ['#FF0000', '#FF6600', '#FFFF00', '#FF3333', '#FFFFFF', '#FF00FF', '#00FFFF'];
    const particles = [];
    
    // Create BIG burst particles
    for (let i = 0; i < 40; i++) {
        const angle = (Math.PI * 2 * i) / 40 + Math.random() * 0.3;
        const speed = 4 + Math.random() * 8;
        particles.push({
            x: x,
            y: y,
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed,
            life: 60,
            maxLife: 60,
            color: colors[Math.floor(Math.random() * colors.length)],
            size: 8 + Math.random() * 15
        });
    }
    
    // Add some sparkles
    for (let i = 0; i < 20; i++) {
        particles.push({
            x: x + (Math.random() - 0.5) * 40,
            y: y + (Math.random() - 0.5) * 40,
            vx: (Math.random() - 0.5) * 6,
            vy: (Math.random() - 0.5) * 6 - 2,
            life: 45,
            maxLife: 45,
            color: '#FFFFFF',
            size: 3 + Math.random() * 5
        });
    }
    
    gameState.explosions.push({
        particles: particles,
        text: reason === 'Same color!' ? 'WRONG COLOR!' : 'OUCH!',
        textX: x,
        textY: y - 50,
        textLife: 80,
        maxTextLife: 80
    });
}

function updateExplosions() {
    for (let i = gameState.explosions.length - 1; i >= 0; i--) {
        const explosion = gameState.explosions[i];
        
        // Update particles
        for (let j = explosion.particles.length - 1; j >= 0; j--) {
            const p = explosion.particles[j];
            p.x += p.vx;
            p.y += p.vy;
            p.vy += 0.15; // gentle gravity on particles
            p.vx *= 0.98; // slow down
            p.life--;
            
            if (p.life <= 0) {
                explosion.particles.splice(j, 1);
            }
        }
        
        explosion.textLife--;
        explosion.textY -= 0.8; // Float up slowly
        
        if (explosion.particles.length === 0 && explosion.textLife <= 0) {
            gameState.explosions.splice(i, 1);
        }
    }
    
    // Update screen shake
    if (gameState.screenShake > 0) {
        gameState.screenShake--;
    }
}

function drawExplosions() {
    for (const explosion of gameState.explosions) {
        // Draw particles
        for (const p of explosion.particles) {
            const alpha = p.life / p.maxLife;
            const size = p.size * (0.5 + alpha * 0.5);
            
            ctx.fillStyle = p.color;
            ctx.globalAlpha = alpha;
            ctx.beginPath();
            ctx.arc(p.x, p.y, size, 0, Math.PI * 2);
            ctx.fill();
            
            // Glow effect
            ctx.shadowBlur = 15;
            ctx.shadowColor = p.color;
            ctx.fill();
            ctx.shadowBlur = 0;
        }
        ctx.globalAlpha = 1;
        
        // Draw text with outline
        if (explosion.textLife > 0) {
            const alpha = explosion.textLife / explosion.maxTextLife;
            const scale = 1 + (1 - alpha) * 0.3;
            
            ctx.save();
            ctx.translate(explosion.textX, explosion.textY);
            ctx.scale(scale, scale);
            
            ctx.font = 'bold 36px Arial';
            ctx.textAlign = 'center';
            ctx.globalAlpha = alpha;
            
            // Outline
            ctx.strokeStyle = '#000';
            ctx.lineWidth = 4;
            ctx.strokeText(explosion.text, 0, 0);
            
            // Fill
            ctx.fillStyle = '#FF0000';
            ctx.fillText(explosion.text, 0, 0);
            
            ctx.restore();
            ctx.globalAlpha = 1;
        }
    }
    
    // Screen flash effect
    if (gameState.screenFlash > 0) {
        ctx.fillStyle = `rgba(255, 0, 0, ${gameState.screenFlash / 30})`;
        ctx.fillRect(0, 0, CONFIG.CANVAS_WIDTH, CONFIG.CANVAS_HEIGHT);
        gameState.screenFlash--;
    }
}

function updateHUD() {
    hudElements.score.textContent = gameState.score;
    hudElements.highScore.textContent = gameState.highScore;
    
    const hearts = '❤️'.repeat(Math.max(0, gameState.lives));
    const emptyHearts = '🖤'.repeat(Math.max(0, CONFIG.INITIAL_LIVES - gameState.lives));
    hudElements.lives.textContent = hearts + emptyHearts;
    
    hudElements.birdColor.style.backgroundColor = gameState.bird.color;
    hudElements.combo.textContent = `${gameState.combo}x`;
}

function render() {
    // Apply screen shake
    ctx.save();
    if (gameState.screenShake > 0) {
        const shakeX = (Math.random() - 0.5) * gameState.screenShake * 2;
        const shakeY = (Math.random() - 0.5) * gameState.screenShake * 2;
        ctx.translate(shakeX, shakeY);
    }
    
    ctx.clearRect(-10, -10, CONFIG.CANVAS_WIDTH + 20, CONFIG.CANVAS_HEIGHT + 20);
    
    // CS-themed gradient background (dark blue/purple tech feel)
    const gradient = ctx.createLinearGradient(0, 0, 0, CONFIG.CANVAS_HEIGHT);
    gradient.addColorStop(0, '#1a1a2e');
    gradient.addColorStop(0.5, '#16213e');
    gradient.addColorStop(1, '#0f3460');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, CONFIG.CANVAS_WIDTH, CONFIG.CANVAS_HEIGHT);
    
    // Draw binary/code rain effect in background
    drawCodeBackground();
    
    // Draw grid pattern
    drawGrid();
    
    drawPipes();
    drawBird();
    drawExplosions();
    
    ctx.restore();
}

function drawCodeBackground() {
    ctx.font = '14px Courier New';
    ctx.fillStyle = 'rgba(0, 255, 100, 0.1)';
    
    const chars = '01{}[]<>=;Graph()Node.colorDFSBFS';
    const time = Date.now() / 1000;
    
    for (let x = 0; x < CONFIG.CANVAS_WIDTH; x += 60) {
        for (let y = 0; y < CONFIG.CANVAS_HEIGHT; y += 40) {
            const charIndex = Math.floor((x + y + time * 50) % chars.length);
            const alpha = 0.05 + Math.sin(x * 0.01 + y * 0.01 + time) * 0.03;
            ctx.fillStyle = `rgba(0, 255, 100, ${alpha})`;
            ctx.fillText(chars[charIndex], x, y);
        }
    }
}

function drawGrid() {
    ctx.strokeStyle = 'rgba(0, 255, 255, 0.1)';
    ctx.lineWidth = 1;
    
    // Vertical lines
    for (let x = 0; x < CONFIG.CANVAS_WIDTH; x += 50) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, CONFIG.CANVAS_HEIGHT);
        ctx.stroke();
    }
    
    // Horizontal lines
    for (let y = 0; y < CONFIG.CANVAS_HEIGHT; y += 50) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(CONFIG.CANVAS_WIDTH, y);
        ctx.stroke();
    }
}

function drawBird() {
    const birdX = CONFIG.BIRD_X;
    const birdY = gameState.bird.y;
    
    ctx.fillStyle = gameState.bird.color;
    ctx.beginPath();
    ctx.arc(birdX + CONFIG.BIRD_WIDTH / 2, birdY + CONFIG.BIRD_HEIGHT / 2, CONFIG.BIRD_WIDTH / 2, 0, Math.PI * 2);
    ctx.fill();
    
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    ctx.fillStyle = '#fff';
    ctx.beginPath();
    ctx.arc(birdX + CONFIG.BIRD_WIDTH * 0.65, birdY + CONFIG.BIRD_HEIGHT * 0.35, 6, 0, Math.PI * 2);
    ctx.fill();
    
    ctx.fillStyle = '#000';
    ctx.beginPath();
    ctx.arc(birdX + CONFIG.BIRD_WIDTH * 0.65, birdY + CONFIG.BIRD_HEIGHT * 0.35, 3, 0, Math.PI * 2);
    ctx.fill();
    
    ctx.fillStyle = '#FFA500';
    ctx.beginPath();
    ctx.moveTo(birdX + CONFIG.BIRD_WIDTH, birdY + CONFIG.BIRD_HEIGHT / 2);
    ctx.lineTo(birdX + CONFIG.BIRD_WIDTH + 10, birdY + CONFIG.BIRD_HEIGHT / 2 - 5);
    ctx.lineTo(birdX + CONFIG.BIRD_WIDTH + 10, birdY + CONFIG.BIRD_HEIGHT / 2 + 5);
    ctx.closePath();
    ctx.fill();
}

function drawPipes() {
    for (const pipe of gameState.pipes) {
        ctx.fillStyle = '#2ECC40';
        ctx.fillRect(pipe.x, 0, CONFIG.PIPE_WIDTH, pipe.gapY);
        ctx.strokeStyle = '#228B22';
        ctx.lineWidth = 3;
        ctx.strokeRect(pipe.x, 0, CONFIG.PIPE_WIDTH, pipe.gapY);
        
        ctx.fillStyle = '#2ECC40';
        ctx.fillRect(pipe.x, pipe.gapY + CONFIG.GAP_HEIGHT, CONFIG.PIPE_WIDTH, CONFIG.CANVAS_HEIGHT - pipe.gapY - CONFIG.GAP_HEIGHT);
        ctx.strokeStyle = '#228B22';
        ctx.strokeRect(pipe.x, pipe.gapY + CONFIG.GAP_HEIGHT, CONFIG.PIPE_WIDTH, CONFIG.CANVAS_HEIGHT - pipe.gapY - CONFIG.GAP_HEIGHT);
        
        ctx.fillStyle = pipe.gapColor;
        ctx.fillRect(pipe.x, pipe.gapY, CONFIG.PIPE_WIDTH, CONFIG.GAP_HEIGHT);
        
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 4;
        ctx.strokeRect(pipe.x, pipe.gapY, CONFIG.PIPE_WIDTH, CONFIG.GAP_HEIGHT);
        
        ctx.fillStyle = '#000';
        ctx.font = 'bold 14px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        const colorName = CONFIG.COLOR_NAMES[pipe.gapColor] || 'Color';
        ctx.fillText(colorName, pipe.x + CONFIG.PIPE_WIDTH / 2, pipe.gapY + CONFIG.GAP_HEIGHT / 2);
    }
}

function drawClouds() {
    ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
    
    const clouds = [
        { x: 100, y: 80, size: 40 },
        { x: 300, y: 150, size: 50 },
        { x: 500, y: 100, size: 45 },
        { x: 650, y: 180, size: 35 },
    ];
    
    for (const cloud of clouds) {
        ctx.beginPath();
        ctx.arc(cloud.x, cloud.y, cloud.size * 0.5, 0, Math.PI * 2);
        ctx.arc(cloud.x + cloud.size * 0.5, cloud.y, cloud.size * 0.6, 0, Math.PI * 2);
        ctx.arc(cloud.x + cloud.size, cloud.y, cloud.size * 0.5, 0, Math.PI * 2);
        ctx.fill();
    }
}

function resetGame() {
    gameState.bird = {
        y: CONFIG.CANVAS_HEIGHT / 2,
        velocity: 0,
        color: CONFIG.COLORS[0],
        colorIndex: 0
    };
    
    gameState.pipes = [];
    gameState.lastPipeTime = 0;
    gameState.score = 0;
    gameState.lives = CONFIG.INITIAL_LIVES;
    gameState.combo = 0;
    gameState.maxCombo = 0;
    gameState.lastGapColor = null;
    gameState.isPaused = false;
    gameState.isGameOver = false;
    gameState.lastColorChangeTime = 0;
    gameState.gameStarted = false;
    gameState.gameStartTime = 0;
    gameState.isReady = false;
    gameState.explosions = [];
    gameState.screenFlash = 0;
    gameState.screenShake = 0;
    gameState.currentSpeed = CONFIG.PIPE_SPEED_START;
    
    updateHUD();
}

function pauseGame() {
    gameState.isPaused = true;
    showScreen('pause');
}

function resumeGame() {
    gameState.isPaused = false;
    showScreen('game');
    gameState.lastFrameTime = performance.now();
    gameLoop(performance.now());
}

function restartGame() {
    if (gameState.animationId) {
        cancelAnimationFrame(gameState.animationId);
    }
    startGame();
}

function quitToMenu() {
    if (gameState.animationId) {
        cancelAnimationFrame(gameState.animationId);
    }
    resetGame();
    showScreen('start');
}

function endGame() {
    gameState.isGameOver = true;
    
    // Create final big explosion
    createExplosion(CONFIG.BIRD_X + CONFIG.BIRD_WIDTH/2, gameState.bird.y + CONFIG.BIRD_HEIGHT/2, 'Game Over');
    gameState.screenShake = 30;
    gameState.screenFlash = 30;
    
    // Continue rendering for a moment to show the explosion
    let frames = 0;
    const showExplosion = () => {
        if (frames < 90) { // ~1.5 seconds of explosion
            frames++;
            updateExplosions();
            render();
            requestAnimationFrame(showExplosion);
        } else {
            // Now show the game over screen
            showGameOverScreen();
        }
    };
    showExplosion();
}

function showGameOverScreen() {
    if (gameState.score > gameState.highScore) {
        gameState.highScore = gameState.score;
        saveHighScore();
        gameOverElements.newHighScoreMsg.classList.remove('hidden');
    } else {
        gameOverElements.newHighScoreMsg.classList.add('hidden');
    }
    
    saveToLeaderboard(gameState.score, gameState.maxCombo);
    
    gameOverElements.finalScore.textContent = gameState.score;
    gameOverElements.finalHighScore.textContent = gameState.highScore;
    gameOverElements.maxCombo.textContent = `${gameState.maxCombo}x`;
    
    showScreen('gameOver');
}

function loadHighScore() {
    const saved = localStorage.getItem('flappyGraphsHighScore');
    if (saved) {
        gameState.highScore = parseInt(saved, 10);
    }
}

function saveHighScore() {
    localStorage.setItem('flappyGraphsHighScore', gameState.highScore.toString());
}

function saveToLeaderboard(score, combo) {
    let leaderboard = JSON.parse(localStorage.getItem('flappyGraphsLeaderboard') || '[]');
    
    const entry = {
        score: score,
        combo: combo,
        date: new Date().toISOString()
    };
    
    leaderboard.push(entry);
    leaderboard.sort((a, b) => b.score - a.score);
    leaderboard = leaderboard.slice(0, 10);
    
    localStorage.setItem('flappyGraphsLeaderboard', JSON.stringify(leaderboard));
}

function displayLeaderboard() {
    const leaderboard = JSON.parse(localStorage.getItem('flappyGraphsLeaderboard') || '[]');
    const container = document.getElementById('leaderboard-list');
    
    if (leaderboard.length === 0) {
        container.innerHTML = '<p style="color: #aaa; text-align: center; padding: 20px;">No scores yet. Play to get on the board!</p>';
        return;
    }
    
    container.innerHTML = '';
    
    leaderboard.forEach((entry, index) => {
        const div = document.createElement('div');
        div.className = 'leaderboard-entry';
        if (index === 0) div.classList.add('top-score');
        
        const rank = document.createElement('div');
        rank.className = 'leaderboard-rank';
        rank.textContent = `#${index + 1}`;
        
        const details = document.createElement('div');
        details.className = 'leaderboard-details';
        
        const score = document.createElement('div');
        score.className = 'leaderboard-score';
        score.textContent = `${entry.score} points (${entry.combo}x combo)`;
        
        const date = document.createElement('div');
        date.className = 'leaderboard-date';
        const dateObj = new Date(entry.date);
        date.textContent = dateObj.toLocaleDateString() + ' ' + dateObj.toLocaleTimeString();
        
        details.appendChild(score);
        details.appendChild(date);
        
        div.appendChild(rank);
        div.appendChild(details);
        
        container.appendChild(div);
    });
}

init();
