# WSPokerEngine

WSPokerEngine is a Python-based poker game engine that currently provides a text-based interface to simulate Texas Hold'em gameplay. It handles all aspects of the game, including card dealing, betting rounds, hand evaluation, and pot distribution.

The project is evolving into a reusable library, designed for developers to integrate poker simulations into their own applications. Future versions will focus on modularity and extensibility, allowing support for additional poker variants, AI opponents, advanced statistics, and more.

## TO RUN EXAMPLES
- run "pip install -e ."
- run "python examples/poker_game_with_callbacks.py" or "python examples/poker_game_manual_control.py"

## TODOs
- [x] Implement core logic and a working simulator for Texas Hold'em.
- [x] Refactor into a reusable library for poker simulations with a clean API.
- [ ] Write comprehensive unit tests for key components, notably hand evaluation, pot distribution, and betting mechanics.

## Ideas for Future Development
- **Support for Variants**: Extend Library to include other poker variants like Omaha or Seven-Card Stud.
- **Advanced Statistics**: Track player performance metrics, betting patterns, and win/loss ratios. Include probability estimation for winning based on current hand and community cards.
- **AI Players:** Implement AI opponents with configurable difficulty levels to simulate realistic gameplay.
- **Simulation Mode:** Enable large-scale simulations to analyze strategies, probabilities, or game balance.
- **Dynamic Configuration**: Allow developers to customize game rules, blinds structure, or starting conditions via configuration files or parameters.
- **Library Publication**: Package and publish the library on PyPI, making it accessible for developers to integrate into their projects.