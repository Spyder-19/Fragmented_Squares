Fragmented Squares: A Combinatorial Game (Left=Blue, Right=Red)
1. Overview
Fragmented Squares is a two-player, finite, combinatorial game with perfect information. Played on a shape composed of interconnected squares with coloured edges, players take turns removing edges corresponding to their designated colour (Blue for Left, Red for Right). The goal is to be the player who removes an edge that destroys the very last square on the board. The game follows the normal play convention, meaning the last player to make a valid move wins. Because players have different available moves (based on edge colour), this is classified as a Partisan game.

3. Game Components
•	Game Board: A predefined shape composed of interconnected squares.
•	Edges: The lines forming the squares. Each edge has a colour: Red or Blue.
•	Players: 
o	Left: Can only remove Blue edges.
o	Right: Can only remove Red edges.
•	Objective: To be the player whose move destroys the final square remaining in the shape.
4. Game Setup
•	The game begins with a specific shape made of multiple squares.
•	Every square in the initial shape must share at least one edge with another square (i.e., be connected).
•	The edges of the squares are pre-assigned as either Red or Blue.
5. Gameplay
•	Players (Left and Right) take turns making moves. Assume Left starts unless specified otherwise.
•	On their turn, a player must choose and remove exactly one edge of their assigned colour (Blue for Left, Red for Right).
•	Square Destruction: As soon as any one of a square's four edges is removed, that square is considered destroyed.
•	Consequences of Edge Removal: When an edge is removed: 
o	The edge is permanently gone.
o	Any square(s) that shared that specific edge are immediately destroyed.
•	Game End: The game ends instantly when the removal of an edge causes the destruction of the last undestroyed square in the shape.

6. Winning Condition
•	The player who removes the edge that destroys the final remaining square wins the game.
7. Game Theory Classification
•	Finite: The game must end because there's a finite number of edges, and one is removed each turn.
•	Deterministic: The outcome is solely determined by player choices; no randomness is involved.
•	Perfect Information: Both players know the complete state of the game at all times.
•	Partisan: Players have different sets of available moves based on the game state (Left can only remove Blue edges, Right can only remove Red edges).
•	Normal Play: The last player to make a legal move wins.



Example Game: Corrected L-Shape (Left=Blue, Right=Red)
Consider an L-shape made of 3 squares (A, B, C). We use the same edge colour assignments as before, but now Left targets Blue and Right targets Red.

![G3](https://github.com/user-attachments/assets/ba5ff271-0c60-4c7d-94e0-dfbacdec38d2)

Setup:
Initial State: Squares A, B, and C are undestroyed. Left player starts.

Gameplay:

![Group 16](https://github.com/user-attachments/assets/325bae6d-ab89-47a7-be93-9fcec1e567e4)


•	Turn 1 (Player: Left): Left needs to remove a Blue edge. Possible Blue edges connecting undestroyed squares are: between A and B, between A and C, top of B, right of B, left of C. Let's say Left chooses the Blue edge between Square A and Square B.
o	Result: Removing this shared edge immediately destroys both Square A and Square B.
o	Game State: Only Square C remains undestroyed. The edge between where A and B were is gone.

![Group 17](https://github.com/user-attachments/assets/331292dc-298b-4870-b91b-c62f8aabe0a7)

 
•	Turn 2 (Player: Right): Right needs to remove a Red edge. Looking at the remaining Square C, its Red edges are the right edge and the bottom edge. Right chooses the Red right edge of Square C.
o	Result: Removing this edge destroys Square C.
o	Game State: No squares remain.
 
Winner:
Right made the move (removing the right edge of C) that destroyed the last remaining square. Therefore, Right wins.
(As noted before, the specific outcome depends heavily on the board's edge colour layout and player choices if multiple moves are available.)

