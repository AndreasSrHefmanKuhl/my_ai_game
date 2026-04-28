Schaolin Vania
Schaolin Vania is a 2D Metroidvania-style platformer built with Python and Pygame. It features a dynamic level-generation system powered by an AI Agent (LLM), a persistent SQLite database for user management, and a robust state-management architecture.

🚀 Features
Dynamic AI Level Generation: Uses a LangGraph-powered agent to "cook" new levels based on the player's real-time performance data (e.g., damage dealt, combat style).

Persistent User System: Secure user registration, login, and profile management using SQLite and SHA-256 password hashing.

Advanced Player Physics: Includes gravity, collision detection, and a frame-locked animation system for combat (punching, kicking, jumping).

Entity AI: Enemies feature patrol logic, proximity detection, and "cliff-sensing" to prevent them from walking off platforms while chasing the player.

Developer Tools: Includes a standalone Tileset Viewer to inspect and index environment assets quickly.

🏗️ Architecture
The project is structured into modular components to ensure scalability and separation of concerns:

Component	Responsibility
main.py	The entry point that initializes Pygame and the Game State Manager.
GameStateManager	Handles transitions between the Menu, Loading, Gameplay, and Game Over states.
DataRepo.py	Manages asset loading (animations, tilesets) and procedural world-building.
agent.py	Orchestrates the LLM workflow to generate valid Python-list map templates.
database.py	Handles all CRUD operations for user accounts and high scores.
classes.py	Defines the physical properties and logic for all Game Objects (Player, Enemy, Boss).
🛠️ Installation & Setup
Prerequisites

Python 3.10+

Pygame CE or Pygame

OpenAI API Key (for the AI Agent)

Steps

Clone the repository:

Bash
git clone https://github.com/your-username/schaolin-vania.git
cd schaolin-vania
Install dependencies:

Bash
pip install pygame-ce python-dotenv langchain-openai langgraph
Configure Environment Variables:
Create a .env file in the root directory and add your API key:

Code-Snippet
OAI_KEY=your_openai_api_key_here
Run the Game:

Bash
python main.py
🎮 How to Play
Arrow Keys: Move Left/Right and Jump (Up).

F / G: Perform Punch or Kick attacks.

Tab: Toggle input fields in the Login menu.

Goal: Defeat all enemies in the level to trigger the AI Agent to generate the next floor. Reach Level 3 to encounter the Endboss.

🛠️ Development Tools
If you are adding new tiles to the environment, use the Tile Viewer to find the correct indices:

Bash
python config/tile_viewer.py
📜 License
This project is licensed under the MIT License - see the LICENSE file for details.
