"""
AI processor for intent analysis and code generation.
Provides intelligent query understanding and fallback code generation.
"""

import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import pandas as pd

try:
    from ..settings import settings
    from ..logging_config import get_logger, log_performance, log_error
    from ..utils.types import QueryType
except ImportError:
    from settings import settings
    from logging_config import get_logger, log_performance, log_error
    from utils.types import QueryType

logger = get_logger(__name__)

# Optional LLM imports
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.prompts import PromptTemplate
    from langchain.schema import BaseOutputParser
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logger.warning("LangChain not available. Using rule-based processing.")


class IntentAnalysisResult:
    """Result of intent analysis."""
    
    def __init__(
        self,
        intent: str,
        confidence: float,
        entities: Dict[str, Any],
        suggested_operations: List[str],
        chart_type: Optional[str] = None
    ):
        self.intent = intent
        self.confidence = confidence
        self.entities = entities
        self.suggested_operations = suggested_operations
        self.chart_type = chart_type
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'intent': self.intent,
            'confidence': self.confidence,
            'entities': self.entities,
            'suggested_operations': self.suggested_operations,
            'chart_type': self.chart_type
        }


class CodeGenerationResult:
    """Result of code generation."""
    
    def __init__(
        self,
        code: str,
        language: str,
        explanation: str,
        confidence: float,
        requires_execution: bool = True
    ):
        self.code = code
        self.language = language
        self.explanation = explanation
        self.confidence = confidence
        self.requires_execution = requires_execution
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'code': self.code,
            'language': self.language,
            'explanation': self.explanation,
            'confidence': self.confidence,
            'requires_execution': self.requires_execution
        }


class RuleBasedIntentAnalyzer:
    """Rule-based intent analyzer using pattern matching."""
    
    def __init__(self):
        self.intent_patterns = {
            'describe_data': [
                r'what.*columns?',
                r'show.*columns?',
                r'list.*columns?',
                r'describe.*data',
                r'data.*structure',
                r'schema'
            ],
            'show_data': [
                r'show.*rows?',
                r'display.*rows?',
                r'first.*rows?',
                r'head.*rows?',
                r'preview.*data',
                r'sample.*data'
            ],
            'aggregate_data': [
                r'total.*',
                r'sum.*',
                r'average.*',
                r'mean.*',
                r'count.*',
                r'max.*',
                r'min.*',
                r'group.*by'
            ],
            'filter_data': [
                r'filter.*',
                r'where.*',
                r'find.*',
                r'search.*',
                r'contains.*',
                r'equals.*'
            ],
            'visualize_data': [
                r'chart.*',
                r'graph.*',
                r'plot.*',
                r'bar.*chart',
                r'line.*chart',
                r'pie.*chart',
                r'scatter.*plot',
                r'histogram.*',
                r'visualize.*',
                r'create.*chart'
            ],
            'compare_data': [
                r'compare.*',
                r'difference.*',
                r'vs.*',
                r'versus.*',
                r'correlation.*',
                r'relationship.*'
            ],
            'statistical_analysis': [
                r'statistics.*',
                r'stats.*',
                r'analysis.*',
                r'correlation.*',
                r'regression.*',
                r'trend.*'
            ]
        }
        
        self.chart_patterns = {
            'bar': [r'bar.*chart', r'column.*chart', r'compare.*categories'],
            'line': [r'line.*chart', r'trend.*', r'time.*series', r'over.*time'],
            'pie': [r'pie.*chart', r'proportion.*', r'percentage.*', r'share.*'],
            'scatter': [r'scatter.*plot', r'correlation.*', r'relationship.*'],
            'histogram': [r'histogram.*', r'distribution.*', r'frequency.*'],
            'heatmap': [r'heatmap.*', r'matrix.*', r'correlation.*matrix']
        }
    
    def analyze_intent(self, question: str) -> IntentAnalysisResult:
        """
        Analyze user intent from question.
        
        Args:
            question: User question
            
        Returns:
            Intent analysis result
        """
        question_lower = question.lower()
        
        # Find matching intents
        intent_scores = {}
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    score += 1
            if score > 0:
                intent_scores[intent] = score / len(patterns)
        
        # Determine primary intent
        if intent_scores:
            primary_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[primary_intent]
        else:
            primary_intent = 'general_query'
            confidence = 0.1
        
        # Extract entities
        entities = self._extract_entities(question)
        
        # Determine chart type
        chart_type = self._determine_chart_type(question_lower)
        
        # Suggest operations
        suggested_operations = self._suggest_operations(primary_intent, entities)
        
        return IntentAnalysisResult(
            intent=primary_intent,
            confidence=confidence,
            entities=entities,
            suggested_operations=suggested_operations,
            chart_type=chart_type
        )
    
    def _extract_entities(self, question: str) -> Dict[str, Any]:
        """Extract entities from question."""
        entities = {
            'columns': [],
            'values': [],
            'operators': [],
            'aggregations': []
        }
        
        question_lower = question.lower()
        
        # Extract column names (common patterns)
        column_patterns = [
            r'column[s]?\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'([a-zA-Z_][a-zA-Z0-9_]*)\s+column',
            r'by\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'group\s+by\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        ]
        
        for pattern in column_patterns:
            matches = re.findall(pattern, question_lower)
            entities['columns'].extend(matches)
        
        # Extract aggregation functions
        agg_patterns = [
            r'(sum|total|add)\s+',
            r'(average|mean|avg)\s+',
            r'(count|number)\s+',
            r'(max|maximum|highest)\s+',
            r'(min|minimum|lowest)\s+'
        ]
        
        for pattern in agg_patterns:
            matches = re.findall(pattern, question_lower)
            entities['aggregations'].extend(matches)
        
        # Extract operators
        if 'greater than' in question_lower or '>' in question:
            entities['operators'].append('gt')
        if 'less than' in question_lower or '<' in question:
            entities['operators'].append('lt')
        if 'equals' in question_lower or '=' in question:
            entities['operators'].append('eq')
        if 'contains' in question_lower:
            entities['operators'].append('contains')
        
        return entities
    
    def _determine_chart_type(self, question_lower: str) -> Optional[str]:
        """Determine suggested chart type."""
        for chart_type, patterns in self.chart_patterns.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    return chart_type
        return None
    
    def _suggest_operations(self, intent: str, entities: Dict[str, Any]) -> List[str]:
        """Suggest operations based on intent and entities."""
        operations = []
        
        if intent == 'describe_data':
            operations.extend(['df.info()', 'df.describe()', 'df.columns.tolist()'])
        elif intent == 'show_data':
            operations.extend(['df.head()', 'df.sample()', 'df.iloc[:10]'])
        elif intent == 'aggregate_data':
            if entities['columns']:
                col = entities['columns'][0]
                operations.extend([
                    f'df["{col}"].sum()',
                    f'df["{col}"].mean()',
                    f'df["{col}"].count()'
                ])
        elif intent == 'visualize_data':
            operations.extend(['df.plot()', 'df.groupby().sum().plot()'])
        elif intent == 'compare_data':
            operations.extend(['df.corr()', 'df.groupby().sum()'])
        
        return operations


class LLMIntentAnalyzer:
    """LLM-based intent analyzer using LangChain."""
    
    def __init__(self):
        self.llm = self._initialize_llm()
        self.prompt_template = self._create_prompt_template()
    
    def _initialize_llm(self):
        """Initialize LLM based on available API keys."""
        if not LLM_AVAILABLE:
            return None
        
        try:
            if settings.google_api_key:
                return ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    google_api_key=settings.google_api_key,
                    temperature=0.1,
                    max_tokens=500
                )
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
        
        return None
    
    def _create_prompt_template(self) -> PromptTemplate:
        """Create prompt template for intent analysis."""
        template = """
        Analyze the following data analysis question and determine:
        1. Intent (describe_data, show_data, aggregate_data, filter_data, visualize_data, compare_data, statistical_analysis)
        2. Confidence (0.0 to 1.0)
        3. Entities (columns, values, operators, aggregations)
        4. Suggested operations (pandas code snippets)
        5. Chart type (bar, line, pie, scatter, histogram, heatmap, table)
        
        Question: {question}
        
        Respond in JSON format:
        {{
            "intent": "intent_name",
            "confidence": 0.8,
            "entities": {{
                "columns": ["col1", "col2"],
                "values": ["value1"],
                "operators": ["gt", "eq"],
                "aggregations": ["sum", "mean"]
            }},
            "suggested_operations": ["df['col1'].sum()", "df.groupby('col2').mean()"],
            "chart_type": "bar"
        }}
        """
        
        return PromptTemplate(
            input_variables=["question"],
            template=template
        )
    
    def analyze_intent(self, question: str) -> IntentAnalysisResult:
        """Analyze intent using LLM."""
        if not self.llm:
            # Fallback to rule-based analyzer
            rule_analyzer = RuleBasedIntentAnalyzer()
            return rule_analyzer.analyze_intent(question)
        
        try:
            prompt = self.prompt_template.format(question=question)
            response = self.llm(prompt)
            
            # Parse JSON response
            import json
            result = json.loads(response)
            
            return IntentAnalysisResult(
                intent=result.get('intent', 'general_query'),
                confidence=result.get('confidence', 0.5),
                entities=result.get('entities', {}),
                suggested_operations=result.get('suggested_operations', []),
                chart_type=result.get('chart_type')
            )
            
        except Exception as e:
            logger.error(f"LLM intent analysis failed: {e}")
            # Fallback to rule-based analyzer
            rule_analyzer = RuleBasedIntentAnalyzer()
            return rule_analyzer.analyze_intent(question)


class CodeGenerator:
    """Generates pandas/SQL code based on intent analysis."""
    
    def __init__(self):
        self.llm = self._initialize_llm()
        self.prompt_template = self._create_prompt_template()
    
    def _initialize_llm(self):
        """Initialize LLM for code generation."""
        if not LLM_AVAILABLE:
            return None
        
        try:
            if settings.google_api_key:
                return ChatGoogleGenerativeAI(
                   model="gemini-1.5-flash",
                    google_api_key=settings.google_api_key,
                    temperature=0.1,
                    max_tokens=1000
                )
        except Exception as e:
            logger.error(f"Failed to initialize LLM for code generation: {e}")
        
        return None
    
    def _create_prompt_template(self) -> PromptTemplate:
        """Create prompt template for code generation."""
        template = """
        Generate pandas code to answer the following data analysis question.
        
        Question: {question}
        Intent: {intent}
        Entities: {entities}
        Schema: {schema}
        
        Requirements:
        1. Use only safe pandas operations
        2. Handle missing data appropriately
        3. Include error handling
        4. Return result in a variable called 'result'
        5. Add comments explaining the logic
        
        Generate clean, efficient pandas code:
        """
        
        return PromptTemplate(
            input_variables=["question", "intent", "entities", "schema"],
            template=template
        )
    
    def generate_pandas_code(
        self,
        question: str,
        intent: str,
        entities: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> CodeGenerationResult:
        """Generate pandas code based on intent analysis."""
        
        if not self.llm:
            # Fallback to rule-based code generation
            return self._generate_rule_based_code(question, intent, entities, schema)
        
        try:
            prompt = self.prompt_template.format(
                question=question,
                intent=intent,
                entities=entities,
                schema=schema
            )
            
            response = self.llm(prompt)
            
            return CodeGenerationResult(
                code=response.strip(),
                language='python',
                explanation=f"Generated pandas code for {intent}",
                confidence=0.8,
                requires_execution=True
            )
            
        except Exception as e:
            logger.error(f"LLM code generation failed: {e}")
            # Fallback to rule-based generation
            return self._generate_rule_based_code(question, intent, entities, schema)
    
    def _generate_rule_based_code(
        self,
        question: str,
        intent: str,
        entities: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> CodeGenerationResult:
        """Generate code using rule-based approach."""
        
        code_parts = []
        explanation_parts = []
        
        if intent == 'describe_data':
            code_parts.append("# Get basic information about the dataset")
            code_parts.append("result = df.info()")
            explanation_parts.append("Display dataset information")
        
        elif intent == 'show_data':
            code_parts.append("# Show first few rows of data")
            code_parts.append("result = df.head(10)")
            explanation_parts.append("Display first 10 rows")
        
        elif intent == 'aggregate_data':
            if entities['columns']:
                col = entities['columns'][0]
                code_parts.append(f"# Calculate aggregation for column '{col}'")
                code_parts.append(f"result = df['{col}'].sum()")
                explanation_parts.append(f"Calculate sum of {col}")
            else:
                code_parts.append("# Get basic statistics")
                code_parts.append("result = df.describe()")
                explanation_parts.append("Display statistical summary")
        
        elif intent == 'visualize_data':
            if entities['columns'] and len(entities['columns']) >= 2:
                x_col = entities['columns'][0]
                y_col = entities['columns'][1]
                code_parts.append(f"# Create visualization")
                code_parts.append(f"result = df.groupby('{x_col}')['{y_col}'].sum()")
                explanation_parts.append(f"Group by {x_col} and sum {y_col}")
            else:
                code_parts.append("# Get data for visualization")
                code_parts.append("result = df.head(20)")
                explanation_parts.append("Get sample data for visualization")
        
        else:
            code_parts.append("# General data analysis")
            code_parts.append("result = df.head()")
            explanation_parts.append("Display sample data")
        
        code = '\n'.join(code_parts)
        explanation = '; '.join(explanation_parts)
        
        return CodeGenerationResult(
            code=code,
            language='python',
            explanation=explanation,
            confidence=0.6,
            requires_execution=True
        )


class AIProcessor:
    """Main AI processor combining intent analysis and code generation."""
    
    def __init__(self):
        self.intent_analyzer = LLMIntentAnalyzer()
        self.code_generator = CodeGenerator()
        self.rule_analyzer = RuleBasedIntentAnalyzer()
    
    def process_query(
        self,
        question: str,
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a query through intent analysis and code generation.
        
        Args:
            question: User question
            schema: Optional data schema
            
        Returns:
            Processing result dictionary
        """
        try:
            start_time = datetime.utcnow()
            
            # Analyze intent
            intent_result = self.intent_analyzer.analyze_intent(question)
            
            # Generate code
            code_result = self.code_generator.generate_pandas_code(
                question=question,
                intent=intent_result.intent,
                entities=intent_result.entities,
                schema=schema or {}
            )
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            log_performance("process_query", duration * 1000,
                          intent=intent_result.intent,
                          confidence=intent_result.confidence)
            
            return {
                'intent_analysis': intent_result.to_dict(),
                'code_generation': code_result.to_dict(),
                'processing_time_ms': duration * 1000,
                'success': True
            }
            
        except Exception as e:
            log_error(e, "AI processing failed", question=question)
            return {
                'intent_analysis': None,
                'code_generation': None,
                'error': str(e),
                'success': False
            }
    
    def analyze_intent_only(self, question: str) -> IntentAnalysisResult:
        """Analyze intent without code generation."""
        return self.intent_analyzer.analyze_intent(question)
    
    def generate_code_only(
        self,
        question: str,
        intent: str,
        entities: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> CodeGenerationResult:
        """Generate code without intent analysis."""
        return self.code_generator.generate_pandas_code(
            question, intent, entities, schema
        )


# Global AI processor instance
ai_processor: Optional[AIProcessor] = None


def initialize_ai_processor() -> AIProcessor:
    """Initialize the global AI processor."""
    global ai_processor
    ai_processor = AIProcessor()
    return ai_processor


def get_ai_processor() -> AIProcessor:
    """Get the global AI processor instance."""
    if ai_processor is None:
        raise RuntimeError("AI processor not initialized. Call initialize_ai_processor() first.")
    return ai_processor


# Example usage and testing
if __name__ == "__main__":
    # Test AI processor
    processor = AIProcessor()
    
    # Test intent analysis
    question = "What is the total revenue by category?"
    intent_result = processor.analyze_intent_only(question)
    print(f"Intent: {intent_result.intent}")
    print(f"Confidence: {intent_result.confidence}")
    print(f"Entities: {intent_result.entities}")
    print(f"Chart type: {intent_result.chart_type}")
    
    # Test code generation
    schema = {
        'columns': ['Category', 'Revenue', 'Users'],
        'dtypes': {'Category': 'object', 'Revenue': 'float64', 'Users': 'int64'}
    }
    
    code_result = processor.generate_code_only(
        question, intent_result.intent, intent_result.entities, schema
    )
    print(f"Generated code: {code_result.code}")
    print(f"Explanation: {code_result.explanation}")
    
    # Test full processing
    result = processor.process_query(question, schema)
    print(f"Processing result: {result['success']}")
