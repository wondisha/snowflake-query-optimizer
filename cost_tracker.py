"""
Cost tracking and ROI calculation for optimizations
"""

from datetime import datetime, timedelta
from typing import Dict, List
import json

class CostTracker:
    """Tracks Snowflake costs and optimization savings"""

    def __init__(self):
        self.credit_price = 2.0  # Default: $2 per credit
        self.storage_price_per_tb_month = 23.0  # On-demand storage
        self.history = []

    def set_credit_price(self, price: float):
        """Set the price per credit"""
        self.credit_price = price

    def calculate_query_cost(self, execution_time_ms: int, warehouse_size: str = "MEDIUM") -> float:
        """Calculate cost of a single query"""
        warehouse_credits_per_minute = {
            "XSMALL": 1,
            "SMALL": 2,
            "MEDIUM": 4,
            "LARGE": 8,
            "XLARGE": 16,
            "2XLARGE": 32,
        }

        credits_per_min = warehouse_credits_per_minute.get(warehouse_size, 4)
        execution_minutes = execution_time_ms / 60000
        credits = credits_per_min * execution_minutes

        return credits * self.credit_price

    def calculate_storage_cost(self, size_gb: int) -> Dict[str, float]:
        """Calculate monthly storage cost"""
        size_tb = size_gb / 1024
        monthly_cost = size_tb * self.storage_price_per_tb_month

        return {
            'monthly': monthly_cost,
            'annual': monthly_cost * 12,
            'size_gb': size_gb,
            'size_tb': size_tb
        }

    def calculate_optimization_roi(self, 
                                   current_cost_monthly: float,
                                   reduction_percentage: float,
                                   implementation_cost: float = 0) -> Dict:
        """Calculate ROI for an optimization"""
        
        monthly_savings = current_cost_monthly * (reduction_percentage / 100)
        annual_savings = monthly_savings * 12
        
        # Payback period (in months)
        if monthly_savings > 0:
            payback_months = implementation_cost / monthly_savings if implementation_cost > 0 else 0
        else:
            payback_months = float('inf')

        return {
            'monthly_savings': monthly_savings,
            'annual_savings': annual_savings,
            'payback_months': payback_months if payback_months != float('inf') else "Immediate",
            'roi_percent': ((annual_savings - implementation_cost) / implementation_cost * 100) if implementation_cost > 0 else 100,
            'reduction_percent': reduction_percentage
        }

    def generate_cost_report(self, 
                            database_size_gb: int,
                            query_costs_monthly: float,
                            storage_costs_monthly: float) -> Dict:
        """Generate comprehensive cost report"""
        
        total_monthly = query_costs_monthly + storage_costs_monthly
        total_annual = total_monthly * 12

        # Optimization opportunities
        opportunities = {
            'clustering': self.calculate_optimization_roi(query_costs_monthly, 30),  # 30% improvement
            'archiving': self.calculate_optimization_roi(storage_costs_monthly, 25),  # 25% improvement
            'query_optimization': self.calculate_optimization_roi(query_costs_monthly, 40),  # 40% improvement
        }

        total_annual_savings = sum(o['annual_savings'] for o in opportunities.values())

        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'monthly_cost': total_monthly,
                'annual_cost': total_annual,
                'query_costs_monthly': query_costs_monthly,
                'storage_costs_monthly': storage_costs_monthly,
            },
            'optimization_opportunities': opportunities,
            'total_potential_annual_savings': total_annual_savings,
            'efficiency_score': min(100, (total_annual_savings / total_annual) * 100) if total_annual > 0 else 0,
        }

    def track_savings(self, optimization_name: str, annual_savings: float):
        """Track implemented optimizations and their savings"""
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'optimization': optimization_name,
            'annual_savings': annual_savings
        })

    def get_savings_history(self) -> List[Dict]:
        """Get history of implemented optimizations"""
        return self.history

    def calculate_cumulative_savings(self) -> float:
        """Calculate total savings from all optimizations"""
        return sum(h['annual_savings'] for h in self.history)


# Example usage
if __name__ == "__main__":
    tracker = CostTracker()

    # Example: Database with 30TB and $2000/month in query costs
    report = tracker.generate_cost_report(
        database_size_gb=30 * 1024,
        query_costs_monthly=2000,
        storage_costs_monthly=600
    )

    print("Cost Report:")
    print(f"  Monthly Cost: ${report['summary']['monthly_cost']:.2f}")
    print(f"  Annual Cost: ${report['summary']['annual_cost']:.2f}")
    print(f"  Potential Annual Savings: ${report['total_potential_annual_savings']:.2f}")
    print(f"  Efficiency Score: {report['efficiency_score']:.1f}%")
