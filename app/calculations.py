from datetime import datetime, timedelta
from .models import FinancialInput, MonthlyProjection, ProjectionResponse
from fastapi import HTTPException
from typing import Dict, Any, List

def calculate_projections(data: FinancialInput) -> ProjectionResponse:
    """Calculate financial projections based on input data"""
    
    # Calculate initial values
    total_monthly_commitments = sum(c.amount for c in data.monthly_commitments)
    net_monthly_salary = data.gross_monthly_salary * (1 - data.tax_rate)
    initial_monthly_savings = net_monthly_salary - total_monthly_commitments
    
    if initial_monthly_savings < 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Monthly expenses (${total_monthly_commitments:,.2f}) exceed net salary (${net_monthly_salary:,.2f}). You have a monthly deficit of ${abs(initial_monthly_savings):,.2f}"
        )
    
    monthly_projections = []
    monthly_summaries = []  # Changed from yearly_summaries to monthly_summaries
    current_savings = data.current_savings
    
    start_date = datetime.now().replace(day=1)
    
    for month_num in range(data.projection_months):  # Changed from data.projection_years * 12 to data.projection_months
        current_date = start_date + timedelta(days=30.44 * month_num)
        year = current_date.year
        month = current_date.month
        
        # Apply inflation to salary and commitments
        inflation_factor = (1 + data.inflation_rate) ** (month_num / 12)
        adjusted_gross_salary = data.gross_monthly_salary * inflation_factor
        adjusted_net_salary = adjusted_gross_salary * (1 - data.tax_rate)
        
        # Adjust commitments for inflation
        adjusted_commitments = []
        total_adjusted_commitments = 0
        for commitment in data.monthly_commitments:
            adjusted_amount = commitment.amount * inflation_factor
            total_adjusted_commitments += adjusted_amount
            adjusted_commitments.append({
                "name": commitment.name,
                "original_amount": commitment.amount,
                "adjusted_amount": adjusted_amount,
                "category": commitment.category
            })
        
        # Calculate monthly savings
        monthly_savings = adjusted_net_salary - total_adjusted_commitments
        
        # Calculate current savings (compound monthly)
        current_savings = current_savings + monthly_savings
        
        projection = MonthlyProjection(
            month=month,
            year=year,
            date=current_date.strftime("%Y-%m-%d"),
            gross_salary=adjusted_gross_salary,
            net_salary=adjusted_net_salary,
            total_commitments=total_adjusted_commitments,
            monthly_savings=monthly_savings,
            total_savings=current_savings,
            commitment_breakdown=adjusted_commitments
        )
        
        monthly_projections.append(projection)
        
        # Create monthly summary for each month
        monthly_summary = {
            "month": month,
            "year": year,
            "date": current_date.strftime("%Y-%m-%d"),
            "gross_income": adjusted_gross_salary,
            "net_income": adjusted_net_salary,
            "total_commitments": total_adjusted_commitments,
            "monthly_saved": monthly_savings,
            "total_savings": current_savings
        }
        monthly_summaries.append(monthly_summary)
    
    # Calculate summary statistics
    total_savings = current_savings
    final_projection = monthly_projections[-1]
    
    summary = {
        "initial_savings": data.current_savings,
        "total_savings": total_savings,
        "initial_monthly_savings": initial_monthly_savings,
        "final_monthly_savings": final_projection.monthly_savings,
        "projection_period_months": data.projection_months,
        "average_monthly_savings": sum(p.monthly_savings for p in monthly_projections) / len(monthly_projections),
        "financial_independence_months": None
    }
    
    # Calculate when savings could sustain lifestyle (basic financial independence)
    monthly_expenses = total_monthly_commitments
    for i, projection in enumerate(monthly_projections):
        if projection.total_savings >= (monthly_expenses * 12 * 25):  # 25x annual expenses rule
            summary["financial_independence_months"] = i + 1
            break
    
    return ProjectionResponse(
        summary=summary,
        monthly_projections=monthly_projections,
        monthly_summary=monthly_summaries
    )