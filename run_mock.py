import time
from typing import Dict, Any

from main import SMCAnalyzer, RiskManager
from options_engine import OptionsEngine

def evaluate_game_theory_matrix(smc_data: Dict[str, Any], micro_data: Dict[str, Any]) -> Dict[str, float]:
    """Calculates institutional vs. retail probabilistic behavior at key SMC/GEX levels."""
    inst_buy_prob = 0.6 if smc_data.get("trend_bias") == "BULLISH" else 0.4
    retail_sell_prob = 1.0 - inst_buy_prob

    return {
        "institutional_buy_prob": inst_buy_prob,
        "institutional_sell_prob": 1.0 - inst_buy_prob,
        "retail_buy_prob": 1.0 - retail_sell_prob,
        "retail_sell_prob": retail_sell_prob
    }

def compute_payoff_matrix(smc_data: Dict[str, Any], micro_data: Dict[str, Any]) -> Dict[str, float]:
    """Constructs a payoff matrix for different market participant behaviors."""
    probs = evaluate_game_theory_matrix(smc_data, micro_data)

    long_ev = (probs["institutional_buy_prob"] * 5.0) + (probs["retail_sell_prob"] * -2.0)
    short_ev = (probs["institutional_sell_prob"] * 5.0) + (probs["retail_buy_prob"] * -2.0)

    return {"long_ev": long_ev, "short_ev": short_ev, "neutral_ev": 0.0}

def main():
    print("Iniciando simulação mock do NQZ6...")
    smc = SMCAnalyzer()
    options_engine = OptionsEngine()
    risk_manager = RiskManager()

    # Preços sequenciais para o NQZ6
    prices = [
        31250.25, 31255.50, 31248.00, 31260.25, 31265.00,
        31258.75, 31270.50, 31275.25, 31268.00, 31280.50,
        31272.25, 31285.00, 31290.75, 31282.50, 31295.25,
        31300.00, 31292.75, 31305.50, 31310.25, 31302.00
    ]

    for price in prices:
        print("-" * 50)
        print(f"Leitura de Preço NQZ6: {price}")

        # Dados mockados
        market_data = {"symbol": "NQZ6", "price": price}
        options_data = {"underlying": "NQZ6"}

        # Análise SMC
        smc_data = smc.analyze(market_data)

        # Análise de Opções
        gex = options_engine.calculate_gex(options_data)
        vanna = options_engine.calculate_vanna_nodes(options_data)
        micro_data = options_engine.analyze(options_data) # Pegamos tudo pra teoria dos jogos

        print(f"Cálculos - GEX: {gex}, Vanna: {vanna}")

        # Teoria dos Jogos
        payoffs = compute_payoff_matrix(smc_data, micro_data)
        probs = evaluate_game_theory_matrix(smc_data, micro_data)
        print(f"Probabilidades Institucionais - Compra: {probs['institutional_buy_prob']:.2f}, Venda: {probs['institutional_sell_prob']:.2f}")

        # Simulação Monte Carlo (Risk Manager)
        expected_drawdown = risk_manager.run_monte_carlo_simulation(price)
        print(f"Decisão Probabilística (Monte Carlo Expected Drawdown): {expected_drawdown:.2f}")

        time.sleep(0.1)

if __name__ == "__main__":
    main()
