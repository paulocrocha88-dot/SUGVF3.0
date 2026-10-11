import os
import asyncio
import logging
import requests
from dotenv import load_dotenv
from typing import Dict, Any, Optional

load_dotenv()

class ExecutionEngine:
    """
    Execution Engine combining Game Theory probability models, AI-driven decision logic,
    and API routing architecture for fully automated order placement.
    """
    def __init__(self):
        self.logger = logging.getLogger("ExecutionEngine")
        self.broker_connected = False

        self.api_url = os.getenv("TRADOVATE_API_URL", "https://demo-api.tradovate.com/v1")
        self.username = os.getenv("TRADOVATE_USERNAME")
        self.password = os.getenv("TRADOVATE_PASSWORD")
        self.client_id = os.getenv("TRADOVATE_CLIENT_ID")
        self.client_secret = os.getenv("TRADOVATE_CLIENT_SECRET")
        self.account_id = os.getenv("TRADOVATE_ACCOUNT_ID")
        self.access_token = None

    def evaluate_game_theory_matrix(self, smc_data: Dict[str, Any], micro_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculates institutional vs. retail probabilistic behavior at key SMC/GEX levels."""
        # Placeholder implementation
        inst_buy_prob = 0.6 if smc_data.get("trend_bias") == "BULLISH" else 0.4
        retail_sell_prob = 1.0 - inst_buy_prob

        return {
            "institutional_buy_prob": inst_buy_prob,
            "institutional_sell_prob": 1.0 - inst_buy_prob,
            "retail_buy_prob": 1.0 - retail_sell_prob,
            "retail_sell_prob": retail_sell_prob
        }

    def compute_payoff_matrix(self, smc_data: Dict[str, Any], micro_data: Dict[str, Any]) -> Dict[str, float]:
        """Constructs a payoff matrix for different market participant behaviors."""
        probs = self.evaluate_game_theory_matrix(smc_data, micro_data)

        # Calculate EV based on probabilities
        long_ev = (probs["institutional_buy_prob"] * 5.0) + (probs["retail_sell_prob"] * -2.0)
        short_ev = (probs["institutional_sell_prob"] * 5.0) + (probs["retail_buy_prob"] * -2.0)

        return {"long_ev": long_ev, "short_ev": short_ev, "neutral_ev": 0.0}

    def decide_action(self, smc_data: Dict[str, Any], micro_data: Dict[str, Any], market_data: Dict[str, Any]) -> Optional[str]:
        """Returns the optimal action based on Nash Equilibrium probabilities or AI-driven decision logic."""
        self.logger.debug("Evaluating Game Theory optimal strategy...")
        payoffs = self.compute_payoff_matrix(smc_data, micro_data)
        probs = self.evaluate_game_theory_matrix(smc_data, micro_data)

        # Simple logic combining signals and probabilities
        if smc_data["trend_bias"] == "BULLISH" and market_data["price"] > micro_data["key_levels"]["zero_gamma"]:
            if payoffs["long_ev"] > 1.0 and probs["institutional_buy_prob"] > 0.5:
                return "BUY"
        elif smc_data["trend_bias"] == "BEARISH" and market_data["price"] < micro_data["key_levels"]["zero_gamma"]:
            if payoffs["short_ev"] > 1.0 and probs["institutional_sell_prob"] > 0.5:
                return "SELL"

        return None

    async def connect_broker_api(self):
        """API routing architecture utilizing Tradovate REST API."""
        self.logger.info("Connecting to Broker API (Tradovate Sandbox) via REST...")

        auth_url = f"{self.api_url}/auth/accesstokenrequest"
        payload = {
            "name": self.username,
            "password": self.password,
            "appId": "SampleApp",
            "appVersion": "1.0",
            "cid": int(self.client_id) if self.client_id and self.client_id.isdigit() else self.client_id,
            "sec": self.client_secret
        }

        try:
            # We run this in thread to not block event loop, though a small request is fast
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: requests.post(auth_url, json=payload))

            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("accessToken")
                self.broker_connected = True
                self.logger.info("Successfully authenticated with Tradovate Broker API.")
            else:
                self.logger.error(f"Failed to authenticate with Tradovate: {response.text}")
                self.broker_connected = False
        except Exception as e:
            self.logger.error(f"Error connecting to Tradovate: {e}")
            self.broker_connected = False

    async def execute_order(self, signal: str, market_data: Dict[str, Any]):
        """Places the order autonomously with zero manual intervention via Tradovate REST."""
        if not self.broker_connected or not self.access_token:
            self.logger.error("Broker API not connected. Cannot execute order.")
            return

        print("\n" + "="*70)
        self.logger.warning(f"🤖 [AUTONOMOUS EXECUTION] ORDER SENT TO BROKER 🤖")
        self.logger.warning(f"Symbol: {market_data['symbol']} | Action: {signal} | Reference Price: {market_data['price']}")

        # Prepare order
        action_map = {"BUY": "Buy", "SELL": "Sell"}
        side = action_map.get(signal)

        if not side:
            self.logger.error(f"Invalid signal {signal} for order execution.")
            return

        order_url = f"{self.api_url}/order/placeorder"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        payload = {
            "accountSpec": self.username,
            "accountId": int(self.account_id) if self.account_id and self.account_id.isdigit() else 1,
            "action": side,
            "symbol": market_data["symbol"],
            "orderQty": 1,
            "orderType": "Market",
            "isAutomated": True
        }

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(order_url, json=payload, headers=headers)
            )

            if response.status_code == 200:
                self.logger.warning(f"-> Fully automated order placement successful. Zero manual intervention.")
                self.logger.debug(f"Order response: {response.json()}")
            else:
                self.logger.error(f"Failed to place order: {response.text}")
        except Exception as e:
            self.logger.error(f"Exception during order placement: {e}")

        print("="*70 + "\n")
