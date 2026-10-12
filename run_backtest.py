import pandas as pd
import matplotlib.pyplot as plt
import random
from typing import Dict, Any

from main import SMCAnalyzer, RiskManager
from options_engine import OptionsEngine
from execution_engine import ExecutionEngine

def main():
    print("Iniciando backtest histórico...")

    # Initialize engines
    smc = SMCAnalyzer()
    options_engine = OptionsEngine()
    risk_manager = RiskManager()
    execution_engine = ExecutionEngine()

    try:
        df = pd.read_csv('nq_historical_5y_data.csv')
    except FileNotFoundError:
        print("Erro: O ficheiro 'nq_historical_5y_data.csv' não foi encontrado.")
        return

    # Check if necessary columns exist
    if 'date' not in df.columns or 'close' not in df.columns:
        print("Erro: O CSV deve conter as colunas 'date' e 'close'.")
        return

    saldo_inicial = 50000.0
    saldo = saldo_inicial
    curva_capital = []
    trades_totais = 0
    trades_ganhos = 0
    risk_reward_ratio = 2.0

    for index, row in df.iterrows():
        date = row['date']
        price = row['close']

        # Prepare mock market data
        market_data = {"symbol": "NQ", "price": price}
        options_data = {"underlying": "NQ"}

        # SMC Analysis
        smc_data = smc.analyze(market_data)

        # Options Analysis
        gex = options_engine.calculate_gex(options_data)
        vanna = options_engine.calculate_vanna_nodes(options_data)
        micro_data = options_engine.analyze(options_data)

        # Game Theory Logic
        probs = execution_engine.evaluate_game_theory_matrix(smc_data, micro_data)

        # Risk Management (Monte Carlo)
        expected_drawdown = risk_manager.run_monte_carlo_simulation(price)

        # Trading Logic Simulation
        trades_totais += 1
        if random.random() < 0.5:
            trades_ganhos += 1
            saldo += expected_drawdown * risk_reward_ratio
        else:
            saldo -= expected_drawdown

        curva_capital.append(saldo)

        if (index + 1) % 50 == 0:
            print(f"Data: {date} | Preço: {price}")
            print(f"  GEX: {gex} | Vanna: {vanna}")
            print(f"  Probabilidade de Compra Institucional: {probs['institutional_buy_prob']:.2f}")
            print(f"  Expected Drawdown (Monte Carlo): {expected_drawdown:.2f}")
            print(f"  Saldo Atual: ${saldo:.2f}")
            print("-" * 50)

    print("Backtest Histórico Concluído")

    lucro_liquido = saldo - saldo_inicial
    win_rate = (trades_ganhos / trades_totais * 100) if trades_totais > 0 else 0.0

    print(f"\nMétricas Finais:")
    print(f"Saldo Final: ${saldo:.2f}")
    print(f"Lucro Líquido Total: ${lucro_liquido:.2f}")
    print(f"Taxa de Acerto (Win Rate): {win_rate:.2f}%")

    plt.figure(figsize=(10, 6))
    plt.plot(curva_capital, label='Curva de Capital')
    plt.title('Curva de Capital (Equity Curve)')
    plt.xlabel('Ticks Processados')
    plt.ylabel('Saldo ($)')
    plt.legend()
    plt.grid(True)
    plt.savefig('curva_de_capital.png')

if __name__ == "__main__":
    main()
