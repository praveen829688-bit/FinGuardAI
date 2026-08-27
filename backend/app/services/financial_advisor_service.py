from sqlalchemy.orm import Session

from app.services.financial_intelligence_service import (
    financial_intelligence_service
)


class FinancialAdvisorService:

    def generate_insights(
        self,
        db: Session,
        user_id: int
    ):
        service = financial_intelligence_service

        spending = service.spending_insights(
            db,
            user_id
        )

        health = service.financial_health(
            db,
            user_id
        )

        categories = service.category_analysis(
            db,
            user_id
        )

        monthly = service.monthly_analytics(
            db,
            user_id
        )

        insights = []

        income = float(spending.get("total_income", 0))
        expenses = float(spending.get("total_expenses", 0))
        savings = float(spending.get("savings", 0))
        savings_rate = float(spending.get("savings_rate", 0))

        # Income
        if income > 0:
            insights.append({
                "type": "INCOME",
                "priority": "NORMAL",
                "title": "Income Overview",
                "message": (
                    f"Your recorded income is {income:.2f}."
                )
            })
        else:
            insights.append({
                "type": "INCOME",
                "priority": "HIGH",
                "title": "Income Data Missing",
                "message": (
                    "No income transactions are currently recorded."
                )
            })

        # Expenses
        if income > 0 and expenses > income:
            insights.append({
                "type": "EXPENSE",
                "priority": "CRITICAL",
                "title": "Expenses Exceed Income",
                "message": (
                    "Your recorded expenses are higher than "
                    "your income. Review discretionary and "
                    "recurring expenses."
                )
            })
        else:
            insights.append({
                "type": "EXPENSE",
                "priority": "NORMAL",
                "title": "Spending Overview",
                "message": (
                    f"You have recorded {expenses:.2f} "
                    "in expenses."
                )
            })

        # Savings
        if savings_rate >= 30:
            savings_message = (
                "Your savings rate is strong. Continue "
                "maintaining disciplined spending."
            )
            savings_priority = "LOW"

        elif savings_rate >= 20:
            savings_message = (
                "Your savings rate is healthy. Consider "
                "gradually increasing your savings target."
            )
            savings_priority = "NORMAL"

        elif savings_rate >= 10:
            savings_message = (
                "Your savings rate is moderate. Look for "
                "areas where discretionary spending can "
                "be reduced."
            )
            savings_priority = "MEDIUM"

        elif savings_rate > 0:
            savings_message = (
                "Your savings rate is low. Try creating "
                "a fixed monthly savings target."
            )
            savings_priority = "HIGH"

        else:
            savings_message = (
                "There are currently no positive savings. "
                "Review expenses and establish an emergency "
                "savings target."
            )
            savings_priority = "CRITICAL"

        insights.append({
            "type": "SAVINGS",
            "priority": savings_priority,
            "title": "Savings Analysis",
            "message": savings_message
        })

        # Category
        if categories:
            top_category = categories[0]

            insights.append({
                "type": "CATEGORY",
                "priority": "NORMAL",
                "title": "Largest Spending Category",
                "message": (
                    f"Category {top_category['category']} "
                    f"accounts for "
                    f"{float(top_category['amount']):.2f} "
                    f"or "
                    f"{float(top_category.get('percentage', 0)):.2f}% "
                    "of recorded expenses."
                )
            })

        # Largest expense
        largest = spending.get("largest_expense")

        if largest:
            insights.append({
                "type": "TRANSACTION",
                "priority": "NORMAL",
                "title": "Largest Expense",
                "message": (
                    f"Your largest recorded expense is "
                    f"{float(largest['amount']):.2f} at "
                    f"{largest.get('merchant', 'Unknown merchant')}."
                )
            })

        # Financial health
        health_score = int(
            health.get("score", 0)
        )

        health_status = health.get(
            "status",
            "UNKNOWN"
        )

        insights.append({
            "type": "HEALTH",
            "priority": (
                "LOW"
                if health_score >= 85
                else "MEDIUM"
            ),
            "title": "Financial Health",
            "message": (
                f"Your financial health score is "
                f"{health_score}/100 "
                f"({health_status})."
            )
        })

        return {
            "financial_health": health,
            "insights": insights,
            "monthly_data": monthly
        }


    def generate_recommendations(
        self,
        db: Session,
        user_id: int
    ):
        service = financial_intelligence_service

        spending = service.spending_insights(
            db,
            user_id
        )

        health = service.financial_health(
            db,
            user_id
        )

        categories = service.category_analysis(
            db,
            user_id
        )

        recommendations = []

        income = float(
            spending.get("total_income", 0)
        )

        expenses = float(
            spending.get("total_expenses", 0)
        )

        savings_rate = float(
            spending.get("savings_rate", 0)
        )

        # Savings recommendation
        if income > 0:
            recommended_savings = round(
                income * 0.20,
                2
            )

            recommendations.append({
                "category": "SAVINGS",
                "priority": "HIGH",
                "title": "Build Monthly Savings",
                "recommendation": (
                    f"Consider targeting at least "
                    f"{recommended_savings:.2f} "
                    "toward savings."
                )
            })

        # Expense recommendation
        if income > 0 and expenses > income:

            recommendations.append({
                "category": "EXPENSE_CONTROL",
                "priority": "CRITICAL",
                "title": "Reduce Expenses",
                "recommendation": (
                    "Your expenses exceed recorded income. "
                    "Review non-essential spending."
                )
            })

        elif savings_rate < 20:

            recommendations.append({
                "category": "EXPENSE_CONTROL",
                "priority": "MEDIUM",
                "title": "Improve Savings Rate",
                "recommendation": (
                    "Identify recurring and discretionary "
                    "expenses that can be reduced."
                )
            })

        # Category recommendation
        if categories:

            top = categories[0]

            recommendations.append({
                "category": "SPENDING",
                "priority": "MEDIUM",
                "title": "Review Largest Category",
                "recommendation": (
                    f"Review spending in category "
                    f"{top['category']}, which represents "
                    f"{float(top.get('percentage', 0)):.2f}% "
                    "of recorded expenses."
                )
            })

        # Financial health recommendation
        health_score = int(
            health.get("score", 0)
        )

        if health_score < 50:

            recommendations.append({
                "category": "FINANCIAL_HEALTH",
                "priority": "CRITICAL",
                "title": "Improve Financial Health",
                "recommendation": (
                    "Focus on controlling expenses, "
                    "maintaining positive savings, and "
                    "building an emergency reserve."
                )
            })

        elif health_score < 70:

            recommendations.append({
                "category": "FINANCIAL_HEALTH",
                "priority": "HIGH",
                "title": "Strengthen Financial Health",
                "recommendation": (
                    "Increase savings consistency and "
                    "monitor spending categories regularly."
                )
            })

        else:

            recommendations.append({
                "category": "FINANCIAL_HEALTH",
                "priority": "LOW",
                "title": "Maintain Financial Discipline",
                "recommendation": (
                    "Continue monitoring spending and "
                    "maintaining a healthy savings rate."
                )
            })

        return {
            "recommendations": recommendations
        }


    def summary(
        self,
        db: Session,
        user_id: int
    ):
        insight_result = self.generate_insights(
            db,
            user_id
        )

        recommendation_result = (
            self.generate_recommendations(
                db,
                user_id
            )
        )

        return {
            "advisor": "FinGuard AI Financial Advisor",
            "version": "1.0",
            "financial_health": (
                insight_result["financial_health"]
            ),
            "insights": (
                insight_result["insights"]
            ),
            "recommendations": (
                recommendation_result["recommendations"]
            )
        }


financial_advisor_service = FinancialAdvisorService()
