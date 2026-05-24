# Examples

**Real-world usage patterns and integration examples for PrivySHA**

This guide provides practical examples of how to integrate PrivySHA into various applications and workflows.

---

## 🚀 Quick Start Examples

### Basic Prompt Processing

```python
from privysha import process

# Simple processing
result = process("Hey bro analyze this dataset with john@email.com")
print(result)
# Output: "Analyze dataset for anomalies (PII masked)"
```

### With Metrics

```python
from privysha import process

result = process(
    "Hey bro analyze dataset with john@email.com", 
    return_metrics=True
)

print(f"Token reduction: {result['token_reduction']}%")
print(f"PII detected: {len(result['security_result']['masked_entities'])}")
print(f"Processing time: {result['metrics']['processing_time_ms']}ms")
```

### Multi-Provider Setup

```python
from privysha import Agent

# Configure fallbacks
agent = Agent(
    model="gpt-4o-mini",
    fallback_providers=[
        {"provider": "anthropic", "model": "claude-3-haiku"},
        {"provider": "openai", "model": "gpt-3.5-turbo"}
    ]
)

result = agent.run("Analyze user behavior data")
print("Provider used:", result["metadata"]["provider"])
print("Fallback used:", result["metadata"].get("fallback_used", False))
```

---

## 📊 Business Use Cases

### Customer Support Automation

```python
from privysha import Agent

class CustomerSupportBot:
    def __init__(self):
        self.agent = Agent(
            model="gpt-4o-mini",
            privacy=True,  # Protect customer data
            fallback_providers=[
                {"provider": "anthropic", "model": "claude-3-haiku"}
            ]
        )
    
    def handle_ticket(self, ticket_text, customer_history=None):
        """Handle customer support ticket"""
        context = customer_history or []
        
        result = self.agent.run(
            f"Support request: {ticket_text}",
            context=context,
            trace=True
        )
        
        return {
            "response": result["response"],
            "category": self._categorize_request(result),
            "urgency": self._assess_urgency(result),
            "metrics": result["optimization_metrics"]
        }
    
    def _categorize_request(self, result):
        """Categorize support request"""
        ir = result.get("ir", {})
        if "refund" in ir.get("constraints", []):
            return "billing"
        elif "technical" in ir.get("constraints", []):
            return "technical"
        else:
            return "general"
    
    def _assess_urgency(self, result):
        """Assess request urgency"""
        ir = result.get("ir", {})
        if "urgent" in ir.get("constraints", []):
            return "high"
        elif "quick" in ir.get("constraints", []):
            return "medium"
        else:
            return "low"

# Usage
support_bot = CustomerSupportBot()
ticket = "My account was charged twice, need refund"
response = support_bot.handle_ticket(ticket)
print("Category:", response["category"])
print("Urgency:", response["urgency"])
print("Response:", response["response"])
```

### Financial Analysis Dashboard

```python
from privysha import Agent
import json

class FinancialAnalyzer:
    def __init__(self):
        self.agent = Agent(
            model="gpt-4o",  # Better model for financial analysis
            privacy=True,
            optimization_level="conservative",  # Preserve financial terms
            fallback_providers=[
                {"provider": "anthropic", "model": "claude-3-sonnet"}
            ]
        )
    
    def analyze_financial_statement(self, statement_data):
        """Analyze financial statement"""
        prompt = f"""
        Analyze this financial statement:
        {json.dumps(statement_data, indent=2)}
        
        Focus on:
        1. Revenue trends
        2. Expense patterns
        3. Profit margins
        4. Risk indicators
        """
        
        result = self.agent.run(prompt, trace=True)
        
        return {
            "analysis": result["response"],
            "metrics": result["optimization_metrics"],
            "security": result["security_result"],
            "recommendations": self._extract_recommendations(result)
        }
    
    def detect_anomalies(self, transaction_data):
        """Detect financial anomalies"""
        prompt = f"""
        Review these transactions for anomalies:
        {json.dumps(transaction_data, indent=2)}
        
        Look for:
        1. Unusual amounts
        2. Duplicate charges
        3. Suspicious patterns
        4. Compliance issues
        """
        
        result = self.agent.run(prompt, trace=True)
        
        return {
            "anomalies": result["response"],
            "risk_level": self._assess_risk_level(result),
            "actions": self._recommend_actions(result)
        }
    
    def _extract_recommendations(self, result):
        """Extract recommendations from analysis"""
        # Parse response for actionable recommendations
        response = result["response"]
        recommendations = []
        
        # Simple extraction - in production, use more sophisticated parsing
        if "recommend" in response.lower():
            lines = response.split('\n')
            recommendations = [line.strip() for line in lines if line.strip().startswith(('•', '-', '*'))]
        
        return recommendations
    
    def _assess_risk_level(self, result):
        """Assess risk level from analysis"""
        response = result["response"].lower()
        if "high risk" in response or "critical" in response:
            return "high"
        elif "medium risk" in response or "moderate" in response:
            return "medium"
        else:
            return "low"
    
    def _recommend_actions(self, result):
        """Recommend actions based on anomalies"""
        response = result["response"].lower()
        actions = []
        
        if "immediate" in response:
            actions.append("immediate_review")
        if "investigate" in response:
            actions.append("further_investigation")
        if "report" in response:
            actions.append("regulatory_report")
        
        return actions

# Usage
analyzer = FinancialAnalyzer()

# Analyze financial statement
statement = {
    "revenue": 1000000,
    "expenses": 750000,
    "profit": 250000,
    "quarters": [250000, 275000, 300000, 175000]
}
analysis = analyzer.analyze_financial_statement(statement)
print("Analysis:", analysis["analysis"])
print("Recommendations:", analysis["recommendations"])

# Detect anomalies
transactions = [
    {"date": "2024-01-15", "amount": 150.00, "vendor": "Office Supply"},
    {"date": "2024-01-15", "amount": 150.00, "vendor": "Office Supply"},  # Duplicate
    {"date": "2024-01-16", "amount": 50000.00, "vendor": "Unknown"}  # Unusual
]
anomalies = analyzer.detect_anomalies(transactions)
print("Risk level:", anomalies["risk_level"])
print("Actions:", anomalies["actions"])
```

---

## 🔒 Security Examples

### GDPR Compliance Handler

```python
from privysha import Agent
import re

class GDPRComplianceHandler:
    def __init__(self):
        self.agent = Agent(
            model="gpt-4o-mini",
            privacy=True,
            security_level="high",
            optimization_level="conservative"  # Preserve legal terms
        )
    
    def process_user_request(self, request, user_consent=None):
        """Process request with GDPR compliance"""
        
        # Check consent
        if not self._has_consent(request, user_consent):
            return {
                "error": "Consent required",
                "action": "request_consent"
            }
        
        # Process with privacy protection
        result = self.agent.run(request, trace=True)
        
        # Apply additional GDPR measures
        return {
            "response": result["response"],
            "data_processed": True,
            "retention_days": 30,
            "right_to_delete": True,
            "data_portability": True,
            "security_measures": result["security_result"]
        }
    
    def _has_consent(self, request, consent):
        """Check if user has given consent"""
        # Simple consent check - in production, use proper consent management
        sensitive_keywords = ["personal", "data", "information", "contact"]
        request_lower = request.lower()
        
        if any(keyword in request_lower for keyword in sensitive_keywords):
            return consent is not None and consent.get("data_processing", False)
        
        return True  # No sensitive data, no consent needed
    
    def generate_privacy_notice(self, processing_type):
        """Generate GDPR privacy notice"""
        prompt = f"""
        Generate GDPR-compliant privacy notice for {processing_type}.
        Include:
        1. Purpose of processing
        2. Legal basis
        3. Data retention period
        4. User rights
        5. Contact information
        """
        
        result = self.agent.run(prompt)
        return result["response"]

# Usage
gdpr_handler = GDPRComplianceHandler()

# Process user request with consent
user_consent = {"data_processing": True, "marketing": False}
response = gdpr_handler.process_user_request(
    "Analyze my purchase history",
    user_consent
)
print("Response:", response["response"])

# Generate privacy notice
notice = gdpr_handler.generate_privacy_notice("data analysis")
print("Privacy Notice:", notice)
```

### Content Moderation System

```python
from privysha import Agent

class ContentModerator:
    def __init__(self):
        self.agent = Agent(
            model="gpt-4o-mini",
            security_level="high",
            optimization_level="balanced"
        )
        
        # Moderation categories
        self.categories = {
            "hate": ["hate", "racist", "discriminatory"],
            "violence": ["violence", "threat", "harm"],
            "adult": ["adult", "explicit", "sexual"],
            "spam": ["spam", "advertisement", "promotion"]
        }
    
    def moderate_content(self, content):
        """Moderate content for policy violations"""
        
        prompt = f"""
        Analyze this content for policy violations:
        "{content}"
        
        Check for:
        1. Hate speech
        2. Violence or threats
        3. Adult content
        4. Spam or advertising
        5. Other policy violations
        
        Provide:
        - Risk level (low/medium/high)
        - Categories violated
        - Action needed (allow/warn/block)
        - Explanation
        """
        
        result = self.agent.run(prompt, trace=True)
        
        return {
            "content": content,
            "moderation_result": result["response"],
            "risk_level": self._extract_risk_level(result),
            "categories": self._extract_categories(result),
            "action": self._determine_action(result),
            "security_analysis": result["security_result"]
        }
    
    def _extract_risk_level(self, result):
        """Extract risk level from moderation result"""
        response = result["response"].lower()
        if "high risk" in response or "block" in response:
            return "high"
        elif "medium risk" in response or "warn" in response:
            return "medium"
        else:
            return "low"
    
    def _extract_categories(self, result):
        """Extract violated categories"""
        response = result["response"].lower()
        violated = []
        
        for category, keywords in self.categories.items():
            if any(keyword in response for keyword in keywords):
                violated.append(category)
        
        return violated
    
    def _determine_action(self, result):
        """Determine moderation action"""
        response = result["response"].lower()
        
        if "block" in response:
            return "block"
        elif "warn" in response or "review" in response:
            return "review"
        else:
            return "allow"
    
    def batch_moderate(self, content_list):
        """Moderate multiple content items"""
        results = []
        
        for content in content_list:
            moderation_result = self.moderate_content(content)
            results.append(moderation_result)
        
        return {
            "total_items": len(content_list),
            "moderated": results,
            "summary": self._generate_summary(results)
        }
    
    def _generate_summary(self, results):
        """Generate moderation summary"""
        summary = {
            "total": len(results),
            "allowed": 0,
            "warned": 0,
            "blocked": 0,
            "categories_found": set()
        }
        
        for result in results:
            action = result["action"]
            if action == "allow":
                summary["allowed"] += 1
            elif action == "review":
                summary["warned"] += 1
            elif action == "block":
                summary["blocked"] += 1
            
            summary["categories_found"].update(result["categories"])
        
        summary["categories_found"] = list(summary["categories_found"])
        return summary

# Usage
moderator = ContentModerator()

# Moderate single content
content = "This is a great product! Buy now at discount!"
result = moderator.moderate_content(content)
print("Action:", result["action"])
print("Risk level:", result["risk_level"])

# Batch moderation
content_list = [
    "Great product!",
    "Buy now!!!",
    "I hate this",
    "Check out my website"
]
batch_results = moderator.batch_moderate(content_list)
print("Summary:", batch_results["summary"])
```

---

## 🤖 Advanced AI Applications

### Multi-Agent System

```python
from privysha import Agent
import asyncio

class MultiAgentSystem:
    def __init__(self):
        # Specialized agents for different tasks
        self.analyst = Agent(
            model="gpt-4o-mini",
            optimization_level="conservative"
        )
        
        self.generator = Agent(
            model="claude-3-haiku",
            optimization_level="balanced"
        )
        
        self.validator = Agent(
            model="gpt-4o",
            optimization_level="conservative"
        )
        
        self.coordinator = Agent(
            model="gpt-4o",
            optimization_level="balanced"
        )
    
    async def complex_analysis(self, data):
        """Coordinate multiple agents for complex analysis"""
        
        # Step 1: Analysis
        analysis_task = asyncio.create_task(
            self._run_agent_async(self.analyst, f"Analyze: {data}")
        )
        
        # Step 2: Generation (based on analysis)
        analysis_result = await analysis_task
        generation_task = asyncio.create_task(
            self._run_agent_async(
                self.generator, 
                f"Generate report based on: {analysis_result['response']}"
            )
        )
        
        # Step 3: Validation
        generation_result = await generation_task
        validation_task = asyncio.create_task(
            self._run_agent_async(
                self.validator,
                f"Validate this analysis and report: {generation_result['response']}"
            )
        )
        
        # Step 4: Coordination
        validation_result = await validation_task
        coordination_prompt = f"""
        Coordinate these results into final output:
        
        Analysis: {analysis_result['response']}
        
        Generation: {generation_result['response']}
        
        Validation: {validation_result['response']}
        
        Provide:
        1. Final consolidated answer
        2. Confidence level
        3. Key insights
        4. Recommendations
        """
        
        final_result = await self._run_agent_async(
            self.coordinator, 
            coordination_prompt
        )
        
        return {
            "final_answer": final_result["response"],
            "agent_results": {
                "analyst": analysis_result,
                "generator": generation_result,
                "validator": validation_result,
                "coordinator": final_result
            },
            "processing_time": self._calculate_total_time([
                analysis_result, generation_result, 
                validation_result, final_result
            ])
        }
    
    async def _run_agent_async(self, agent, prompt):
        """Run agent asynchronously"""
        return await asyncio.get_event_loop().run_in_executor(
            None, agent.run, prompt, True
        )
    
    def _calculate_total_time(self, results):
        """Calculate total processing time"""
        return sum(
            result.get("metadata", {}).get("processing_time_ms", 0)
            for result in results
        )

# Usage
async def main():
    system = MultiAgentSystem()
    
    data = "Sales data shows 15% growth but customer complaints increased"
    result = await system.complex_analysis(data)
    
    print("Final Answer:", result["final_answer"])
    print("Processing Time:", result["processing_time"], "ms")

# Run the async example
# asyncio.run(main())
```

### Learning and Adaptation System

```python
from privysha import Agent
import json
import time

class AdaptiveAgent:
    def __init__(self):
        self.agent = Agent(
            model="gpt-4o-mini",
            routing_strategy="cost_optimized"
        )
        
        # Learning data
        self.performance_history = []
        self.user_preferences = {}
        self.optimization_history = []
    
    def adaptive_run(self, prompt, user_id=None):
        """Run with adaptive optimization"""
        
        # Load user preferences if available
        if user_id and user_id in self.user_preferences:
            prefs = self.user_preferences[user_id]
            self.agent.configure({
                "optimization_level": prefs.get("optimization", "balanced"),
                "privacy": prefs.get("privacy", True)
            })
        
        # Run with tracing
        result = self.agent.run(prompt, trace=True)
        
        # Learn from this interaction
        self._learn_from_result(result, user_id)
        
        return result
    
    def _learn_from_result(self, result, user_id):
        """Learn from interaction result"""
        
        # Record performance
        performance_data = {
            "timestamp": time.time(),
            "processing_time_ms": result.get("metadata", {}).get("processing_time_ms", 0),
            "optimization_achieved": result.get("optimization_metrics", {}).get("reduction_percentage", 0),
            "user_satisfaction": None  # Would be collected from user feedback
        }
        
        self.performance_history.append(performance_data)
        
        # Update user preferences based on patterns
        if user_id:
            self._update_user_preferences(result, user_id)
        
        # Optimize based on history
        self._optimize_based_on_history()
    
    def _update_user_preferences(self, result, user_id):
        """Update user preferences based on interaction"""
        
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}
        
        prefs = self.user_preferences[user_id]
        
        # Learn optimization preference
        opt_level = result.get("optimization_metrics", {}).get("reduction_percentage", 0)
        if opt_level > 60:
            prefs["optimization"] = "aggressive"
        elif opt_level > 30:
            prefs["optimization"] = "balanced"
        else:
            prefs["optimization"] = "conservative"
        
        # Learn privacy preference
        pii_detected = result.get("security_result", {}).get("pii_detected", [])
        if pii_detected:
            prefs["privacy"] = True
    
    def _optimize_based_on_history(self):
        """Optimize agent based on performance history"""
        
        if len(self.performance_history) < 10:
            return  # Not enough data
        
        # Analyze recent performance
        recent_history = self.performance_history[-50:]  # Last 50 interactions
        
        avg_processing_time = sum(h["processing_time_ms"] for h in recent_history) / len(recent_history)
        avg_optimization = sum(h["optimization_achieved"] for h in recent_history) / len(recent_history)
        
        # Adjust configuration based on performance
        if avg_processing_time > 2000:  # Too slow
            self.agent.configure({
                "routing_strategy": "performance_optimized"
            })
        elif avg_optimization < 30:  # Not optimizing enough
            self.agent.configure({
                "optimization_level": "aggressive"
            })
    
    def get_learning_insights(self):
        """Get insights from learning data"""
        
        if not self.performance_history:
            return "No learning data available"
        
        insights = {
            "total_interactions": len(self.performance_history),
            "avg_processing_time": sum(h["processing_time_ms"] for h in self.performance_history) / len(self.performance_history),
            "avg_optimization": sum(h["optimization_achieved"] for h in self.performance_history) / len(self.performance_history),
            "user_count": len(self.user_preferences),
            "top_optimization_preferences": self._get_top_preferences()
        }
        
        return insights
    
    def _get_top_preferences(self):
        """Get most common user preferences"""
        opt_prefs = [prefs.get("optimization", "balanced") for prefs in self.user_preferences.values()]
        
        from collections import Counter
        opt_counter = Counter(opt_prefs)
        
        return opt_counter.most_common(3)

# Usage
adaptive_agent = AdaptiveAgent()

# Simulate user interactions
for i in range(20):
    prompt = f"Analyze dataset sample {i}"
    result = adaptive_agent.adaptive_run(prompt, user_id="user123")
    
    # Simulate user feedback (in real app, this would come from UI)
    if i % 5 == 0:
        print(f"Interaction {i}: {result['optimization_metrics']['reduction_percentage']:.1f}% optimization")

# Get learning insights
insights = adaptive_agent.get_learning_insights()
print("Learning Insights:", insights)
```

---

## 📈 Performance Monitoring

### Real-time Dashboard

```python
from privysha import Agent
import time
import json

class PerformanceDashboard:
    def __init__(self):
        self.agent = Agent(
            model="gpt-4o-mini",
            debug_level="verbose"
        )
        
        self.metrics = {
            "requests": [],
            "errors": [],
            "performance": [],
            "costs": []
        }
    
    def track_request(self, prompt, user_id=None):
        """Track request with performance metrics"""
        
        start_time = time.time()
        
        try:
            result = self.agent.run(prompt, trace=True)
            
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            # Record successful request
            request_data = {
                "timestamp": end_time,
                "user_id": user_id,
                "prompt_length": len(prompt),
                "duration_ms": duration_ms,
                "tokens_used": result.get("metadata", {}).get("tokens_used", 0),
                "optimization": result.get("optimization_metrics", {}),
                "provider": result.get("metadata", {}).get("provider"),
                "success": True
            }
            
            self.metrics["requests"].append(request_data)
            
            return result
            
        except Exception as e:
            end_time = time.time()
            
            # Record error
            error_data = {
                "timestamp": end_time,
                "user_id": user_id,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "prompt_length": len(prompt),
                "success": False
            }
            
            self.metrics["errors"].append(error_data)
            
            raise e
    
    def get_performance_summary(self, time_window_minutes=60):
        """Get performance summary for time window"""
        
        current_time = time.time()
        cutoff_time = current_time - (time_window_minutes * 60)
        
        # Filter recent requests
        recent_requests = [
            req for req in self.metrics["requests"]
            if req["timestamp"] > cutoff_time
        ]
        
        if not recent_requests:
            return {"message": "No recent requests"}
        
        # Calculate metrics
        total_requests = len(recent_requests)
        successful_requests = sum(1 for req in recent_requests if req["success"])
        avg_duration = sum(req["duration_ms"] for req in recent_requests) / total_requests
        avg_optimization = sum(
            req["optimization"].get("reduction_percentage", 0) 
            for req in recent_requests
        ) / total_requests
        
        # Provider distribution
        provider_counts = {}
        for req in recent_requests:
            provider = req.get("provider", "unknown")
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
        
        return {
            "time_window_minutes": time_window_minutes,
            "total_requests": total_requests,
            "success_rate": successful_requests / total_requests,
            "avg_duration_ms": avg_duration,
            "avg_optimization_percent": avg_optimization,
            "provider_distribution": provider_counts,
            "requests_per_minute": total_requests / time_window_minutes
        }
    
    def generate_alerts(self):
        """Generate performance alerts"""
        
        alerts = []
        recent_summary = self.get_performance_summary(10)  # Last 10 minutes
        
        if recent_summary.get("success_rate", 1.0) < 0.9:
            alerts.append({
                "level": "warning",
                "message": f"Low success rate: {recent_summary['success_rate']:.1%}",
                "recommendation": "Check provider status and configuration"
            })
        
        if recent_summary.get("avg_duration_ms", 0) > 3000:
            alerts.append({
                "level": "warning",
                "message": f"High average response time: {recent_summary['avg_duration_ms']:.0f}ms",
                "recommendation": "Consider performance-optimized routing"
            })
        
        if recent_summary.get("avg_optimization_percent", 0) < 30:
            alerts.append({
                "level": "info",
                "message": f"Low optimization: {recent_summary['avg_optimization_percent']:.1f}%",
                "recommendation": "Check optimization configuration"
            })
        
        return alerts
    
    def export_metrics(self, filename="metrics.json"):
        """Export metrics to file"""
        
        export_data = {
            "export_timestamp": time.time(),
            "metrics": self.metrics,
            "summary": self.get_performance_summary(60),
            "alerts": self.generate_alerts()
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return f"Metrics exported to {filename}"

# Usage
dashboard = PerformanceDashboard()

# Track some requests
for i in range(5):
    prompt = f"Analyze data sample {i}"
    result = dashboard.track_request(prompt, user_id=f"user_{i}")
    print(f"Request {i}: {result['optimization_metrics']['reduction_percentage']:.1f}% optimization")

# Get performance summary
summary = dashboard.get_performance_summary()
print("Performance Summary:", summary)

# Generate alerts
alerts = dashboard.generate_alerts()
print("Alerts:", alerts)

# Export metrics
dashboard.export_metrics()
```

---

## 🎯 Best Practices

### Error Handling

```python
from privysha import Agent
from privysha.exceptions import PrivySHAError

def robust_agent_call(prompt, max_retries=3):
    """Robust agent call with error handling"""
    
    agent = Agent(
        model="gpt-4o-mini",
        fallback_providers=[
            {"provider": "anthropic", "model": "claude-3-haiku"}
        ]
    )
    
    for attempt in range(max_retries):
        try:
            result = agent.run(prompt, trace=True)
            
            # Validate result quality
            if validate_result_quality(result):
                return result
            else:
                print(f"Attempt {attempt + 1}: Low quality result, retrying...")
                
        except PrivySHAError as e:
            print(f"Attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
    
    return None

def validate_result_quality(result):
    """Validate result quality"""
    
    # Check if response is meaningful
    response = result.get("response", "")
    if len(response) < 10:
        return False
    
    # Check optimization was applied
    opt_metrics = result.get("optimization_metrics", {})
    if opt_metrics.get("reduction_percentage", 0) < 10:
        return False
    
    # Check for errors
    if "error" in response.lower():
        return False
    
    return True
```

### Configuration Management

```python
from privysha import Agent
import yaml

class ConfigurableAgent:
    def __init__(self, config_file="config.yaml"):
        self.config = self._load_config(config_file)
        self.agent = Agent(**self.config["agent"])
    
    def _load_config(self, config_file):
        """Load configuration from file"""
        
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self._default_config()
    
    def _default_config(self):
        """Default configuration"""
        return {
            "agent": {
                "model": "gpt-4o-mini",
                "privacy": True,
                "optimization_level": "balanced",
                "fallback_providers": [
                    {"provider": "anthropic", "model": "claude-3-haiku"}
                ]
            }
        }
    
    def update_config(self, new_config):
        """Update configuration"""
        
        self.config.update(new_config)
        self.agent.configure(**self.config["agent"])
    
    def save_config(self, config_file="config.yaml"):
        """Save configuration to file"""
        
        with open(config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)

# Usage
agent = ConfigurableAgent("production_config.yaml")

# Update configuration
agent.update_config({
    "agent": {
        "optimization_level": "aggressive",
        "routing_strategy": "cost_optimized"
    }
})

# Save updated configuration
agent.save_config()
```

---

## 🎯 Next Steps

Now that you've seen real-world examples:

1. **[Check FAQ](faq.md)** - Common questions and answers
2. **[Learn Contributing](contributing.md)** - How to contribute examples
3. **[Review Roadmap](roadmap.md)** - Future example categories
4. **[API Reference](api-reference.md)** - Complete API documentation

---

*Ready to contribute your own examples? Check out the [Contributing guide](contributing.md)!*
