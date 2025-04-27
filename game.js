// --- Constants ---
const LEFT_PLAYER = "Left (Blue)";
const RIGHT_PLAYER = "Right (Red)";
const BLUE = "blue";
const RED = "red";

const SQUARE_SIZE = 60;
const HORIZONTAL = 'H';
const VERTICAL = 'V';

// --- DOM Elements ---
const svg = document.getElementById('game-svg');
const playerTurnSpan = document.getElementById('player-turn');
const activeSquaresSpan = document.getElementById('active-squares');
const winnerDisplaySpan = document.getElementById('winner-display');
const playAgainButton = document.getElementById('play-again-button');

// --- Game State Variables ---
let allSquaresCoords = [];
let activeSquaresCoords = new Set();
let edges = {};
let currentPlayer = LEFT_PLAYER;
let winner = null;
let boardDimensions = { minR: 0, maxR: 0, minC: 0, maxC: 0, width: 0, height: 0 };

// --- Game Initialization ---

function defineShape(shapeCoords) {
    allSquaresCoords = shapeCoords.map(coord => ({...coord}));
    if (!allSquaresCoords || allSquaresCoords.length === 0) {
        console.error("Cannot initialize game with an empty shape.");
        return;
    }
    calculateBoardDimensions();
    resetGame();
}

function calculateBoardDimensions() {
    if (allSquaresCoords.length === 0) return;
    boardDimensions.minR = Math.min(...allSquaresCoords.map(sq => sq.r));
    boardDimensions.maxR = Math.max(...allSquaresCoords.map(sq => sq.r));
    boardDimensions.minC = Math.min(...allSquaresCoords.map(sq => sq.c));
    boardDimensions.maxC = Math.max(...allSquaresCoords.map(sq => sq.c));
    const cols = boardDimensions.maxC - boardDimensions.minC + 1;
    const rows = boardDimensions.maxR - boardDimensions.minR + 1;
    boardDimensions.width = (cols + 1) * SQUARE_SIZE;
    boardDimensions.height = (rows + 1) * SQUARE_SIZE;
    svg.setAttribute('viewBox', `${boardDimensions.minC * SQUARE_SIZE - SQUARE_SIZE/2} ${boardDimensions.minR*SQUARE_SIZE - SQUARE_SIZE/2} ${boardDimensions.width} ${boardDimensions.height}`);
}

function resetGame() {
    svg.innerHTML = '';
    activeSquaresCoords = new Set(allSquaresCoords.map(sq => `${sq.r},${sq.c}`));
    edges = {};
    currentPlayer = LEFT_PLAYER;
    winner = null;
    initializeBoardSVG();
    initializeEdges();
    updateInfoPanel();
    playAgainButton.style.display = 'none';
}

function initializeBoardSVG() {
    allSquaresCoords.forEach(sq => {
        const squareElement = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        const x = sq.c * SQUARE_SIZE;
        const y = sq.r * SQUARE_SIZE;
        squareElement.setAttribute('x', x);
        squareElement.setAttribute('y', y);
        squareElement.setAttribute('width', SQUARE_SIZE);
        squareElement.setAttribute('height', SQUARE_SIZE);
        squareElement.setAttribute('id', `square-${sq.r}-${sq.c}`);
        squareElement.classList.add('square-shape');
        if (!activeSquaresCoords.has(`${sq.r},${sq.c}`)) {
            squareElement.classList.add('destroyed');
        }
        svg.appendChild(squareElement);
    });
}

function initializeEdges() {
    const potentialEdges = new Set();
    allSquaresCoords.forEach(sq => {
        const r = sq.r;
        const c = sq.c;
        potentialEdges.add(getEdgeKey(r, c, HORIZONTAL));
        potentialEdges.add(getEdgeKey(r, c, VERTICAL));
        potentialEdges.add(getEdgeKey(r - 1, c, HORIZONTAL));
        potentialEdges.add(getEdgeKey(r, c - 1, VERTICAL));
    });

    potentialEdges.forEach(edgeKey => {
        if (!(edgeKey in edges)) {
            const {r, c, orientation} = parseEdgeKey(edgeKey);
            const squaresBordered = getSquaresSharingEdge(r, c, orientation);
            const bordersShape = squaresBordered.some(sq =>
                allSquaresCoords.some(shapeSq => shapeSq.r === sq.r && shapeSq.c === sq.c)
            );
            if (bordersShape) {
                const color = Math.random() < 0.5 ? RED : BLUE;
                const edgeElement = createEdgeElement(r, c, orientation, color, edgeKey);
                edges[edgeKey] = {
                    color: color,
                    exists: true,
                    element: edgeElement
                };
                svg.appendChild(edgeElement);
            }
        }
    });
}

function createEdgeElement(r, c, orientation, color, edgeKey) {
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    let x1, y1, x2, y2;
    if (orientation === HORIZONTAL) {
        x1 = c * SQUARE_SIZE;
        y1 = (r + 1) * SQUARE_SIZE;
        x2 = x1 + SQUARE_SIZE;
        y2 = y1;
    } else {
        x1 = (c + 1) * SQUARE_SIZE;
        y1 = r * SQUARE_SIZE;
        x2 = x1;
        y2 = y1 + SQUARE_SIZE;
    }
    line.setAttribute('x1', x1);
    line.setAttribute('y1', y1);
    line.setAttribute('x2', x2);
    line.setAttribute('y2', y2);
    line.setAttribute('stroke', color);
    line.classList.add('edge-line', color);
    line.dataset.edgeKey = edgeKey;
    line.addEventListener('click', handleEdgeClick);
    line.addEventListener('mouseenter', handleEdgeMouseEnter);
    line.addEventListener('mouseleave', handleEdgeMouseLeave);
    return line;
}

// --- Utility Functions ---

function getEdgeKey(r, c, orientation) {
    return `${r},${c},${orientation}`;
}

function parseEdgeKey(key) {
    const parts = key.split(',');
    return { r: parseInt(parts[0]), c: parseInt(parts[1]), orientation: parts[2] };
}

function getSquaresSharingEdge(r, c, orientation) {
    const squares = [];
    if (orientation === HORIZONTAL) {
        squares.push({ r: r, c: c });
        squares.push({ r: r + 1, c: c });
    } else {
        squares.push({ r: r, c: c });
        squares.push({ r: r, c: c + 1 });
    }
    return squares.filter(sq =>
        allSquaresCoords.some(shapeSq => shapeSq.r === sq.r && shapeSq.c === sq.c)
    );
}

// --- Misère Rule: Player who cannot move loses ---
function hasValidMove(player) {
    const playerColor = player === LEFT_PLAYER ? BLUE : RED;
    return Object.keys(edges).some(edgeKey => {
        const edge = edges[edgeKey];
        if (!edge || !edge.exists) return false;
        if (edge.color !== playerColor) return false;
        const {r, c, orientation} = parseEdgeKey(edgeKey);
        const squaresBordered = getSquaresSharingEdge(r, c, orientation);
        return squaresBordered.some(sq => activeSquaresCoords.has(`${sq.r},${sq.c}`));
    });
}

function isValidMove(edgeKey) {
    if (winner) return false;
    const edge = edges[edgeKey];
    if (!edge || !edge.exists) return false;
    const playerColor = currentPlayer === LEFT_PLAYER ? BLUE : RED;
    if (edge.color !== playerColor) return false;
    const {r, c, orientation} = parseEdgeKey(edgeKey);
    const squaresBordered = getSquaresSharingEdge(r, c, orientation);
    const bordersActive = squaresBordered.some(sq => activeSquaresCoords.has(`${sq.r},${sq.c}`));
    if (!bordersActive) return false;
    return true;
}

function makeMove(edgeKey) {
    if (!isValidMove(edgeKey)) {
        return;
    }
    const edge = edges[edgeKey];
    edge.exists = false;
    edge.element.classList.add('removed');
    edge.element.classList.remove('highlight');
    const {r, c, orientation} = parseEdgeKey(edgeKey);
    const squaresBordered = getSquaresSharingEdge(r, c, orientation);
    squaresBordered.forEach(sq => {
        const sqKey = `${sq.r},${sq.c}`;
        if (activeSquaresCoords.has(sqKey)) {
            activeSquaresCoords.delete(sqKey);
            const squareElement = document.getElementById(`square-${sq.r}-${sq.c}`);
            if (squareElement) {
                squareElement.classList.add('destroyed');
            }
        }
    });

    if (activeSquaresCoords.size === 0) {
        winner = currentPlayer;
        playAgainButton.style.display = 'block';
    } else {
        currentPlayer = (currentPlayer === LEFT_PLAYER) ? RIGHT_PLAYER : LEFT_PLAYER;
        if (!hasValidMove(currentPlayer)) {
            winner = (currentPlayer === LEFT_PLAYER) ? RIGHT_PLAYER : LEFT_PLAYER;
            playAgainButton.style.display = 'block';
        }
    }
    updateInfoPanel();
}

// --- UI Update Functions ---

function updateInfoPanel() {
    if (winner) {
        playerTurnSpan.textContent = '';
        winnerDisplaySpan.textContent = `Winner: ${winner}!`;
        winnerDisplaySpan.className = winner === LEFT_PLAYER ? 'left game-over' : 'right game-over';
    } else {
        playerTurnSpan.textContent = `Turn: ${currentPlayer}`;
        playerTurnSpan.className = currentPlayer === LEFT_PLAYER ? 'left' : 'right';
        winnerDisplaySpan.textContent = '';
        winnerDisplaySpan.className = '';
    }
    activeSquaresSpan.textContent = `Active Squares: ${activeSquaresCoords.size}`;
}

// --- Event Handlers ---

function handleEdgeClick(event) {
    if (winner) return;
    const edgeKey = event.target.dataset.edgeKey;
    makeMove(edgeKey);
}

function handleEdgeMouseEnter(event) {
    if (winner) return;
    const edgeKey = event.target.dataset.edgeKey;
    if (isValidMove(edgeKey)) {
        event.target.classList.add('highlight');
    }
}

function handleEdgeMouseLeave(event) {
    if (winner) return;
    event.target.classList.remove('highlight');
}

playAgainButton.addEventListener('click', resetGame);

// --- Start the Game ---
const twoByTwoShape = [{r:0, c:0}, {r:0, c:1}, {r:1, c:0}, {r:1, c:1}];
defineShape(twoByTwoShape);
