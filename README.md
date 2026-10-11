# SUGF v3.0 - Advanced Quantitative Trading Architecture

This project is an algorithmic trading system targeting US Futures (specifically NQ/MNQ). It has been refactored into an advanced architecture designed to incorporate Smart Money Concepts (SMC), Options Market Microstructure, and Game Theory-based Execution Intelligence.

## Architectural Upgrade Overview

The system has transitioned from a monolithic skeleton script into a modular, object-oriented design. This separation of concerns allows for robust testing, scalability, and integration of complex mathematical models.

### Core Modules

1.  **`DataFeedEngine`**: Dedicated to handling asynchronous data ingestion from high-frequency market data providers (e.g., Databento, Rithmic, Tradovate). It manages normalisation of order book updates and options chain data.
2.  **`SMCAnalyzer`**: Encapsulates the logic for evaluating Smart Money Concepts, including Fair Value Gaps (FVG), Order Blocks (OB), Market Structure Shifts (MSS), and Mean Thresholds.
3.  **`OptionsMicrostructure`**: Dedicated to processing options data to derive critical levels and exposures, such as Gamma Exposure (GEX), Spot Gamma, Vanna Nodes, Zero Gamma Level (ZGL), and Call/Put Walls.
4.  **`GameTheoryAI`**: The intelligence core of the system. It uses probability models (Nash Equilibriums) and AI/RL concepts to determine the optimal strategy by analyzing payoffs between SMC context and options microstructure.
5.  **`RiskManager`**: A centralized controller for enforcing max drawdowns, position sizing, and ensuring trades comply with risk parameters before execution.
6.  **`ExecutionEngine`**: Handles order dispatch. Currently set up for manual alerts targeting prop-firm traders, but structured to easily integrate API clients in the future.
7.  **`SUGFv3Orchestrator`**: The main async event loop that synchronizes the data feeds, runs the analysis modules, queries the AI engine, and triggers the risk manager and execution engine.

## Recommended Python Libraries for Heavy Math

To implement the rigorous mathematical requirements of the `OptionsMicrostructure` and `GameTheoryAI` modules, the following libraries are recommended:

*   **`NumPy` & `SciPy`**: Essential for fast matrix operations, probability distributions, and the Black-Scholes calculations required for GEX and Vanna modeling.
*   **`Pandas` & `Polars`**: For handling time-series data and dataframe manipulations. Polars is highly recommended for low-latency dataframe operations if performance bottlenecks arise.
*   **`PyTorch` or `Scikit-Learn`**: For developing and training the RL agents or probabilistic models within the `GameTheoryAI` module.
*   **`Numba` or `Cython`**: To compile critical, CPU-intensive mathematical functions (like continuous options Greek recalculations) down to C-level speeds, bypassing the GIL.

## Architectural Blind Spots & Future Considerations

While the current architecture is robust, there are several structural aspects to consider before writing the core logic:

1.  **Blocking the Event Loop**: Heavy math calculations (like Black-Scholes for thousands of options strikes) can block the `asyncio` event loop. You must consider offloading these calculations using `ProcessPoolExecutor` or leveraging libraries like `Numba` to ensure the data ingestion loop remains unimpeded.
2.  **State Management & Persistence**: Currently, there is no persistent memory across loop iterations (other than what is explicitly held in memory). A state management solution (like Redis or an in-memory DB) might be required to track historical order blocks or complex multi-step market structure shifts.
3.  **Backtesting Decoupling**: The current architecture tightly couples live execution with analysis. To effectively train the AI and backtest strategies, the system needs an adapter layer where historical tick data can be injected into the `SUGFv3Orchestrator` identically to live data, while swapping out the `ExecutionEngine` for a simulated portfolio tracker.
4.  **Data Synchronization**: Options data and Futures tick data often arrive at different frequencies and latencies. The `DataFeedEngine` will need robust buffering and synchronization logic to ensure the `analyze` methods are evaluating a consistent state of the market.
5.  **Risk Controls on Asynchronous Responses**: Risk management is currently checked synchronously before execution. In a real environment with API execution, the risk manager needs to account for pending, unfilled orders and slippage dynamically.
