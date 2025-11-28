import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class LLMHandler:
    """Handles interactions with LLM (OpenAI or Groq)"""
    
    def __init__(self):
        # Check for Groq API key first, fallback to OpenAI
        groq_key = os.getenv('GROQ_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        
        if groq_key:
            # Use Groq (free tier available)
            self.api_key = groq_key
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.model = "llama-3.3-70b-versatile"  # Fast and capable Groq model
            logger.info("Using Groq API")
        elif openai_key:
            # Use OpenAI
            self.api_key = openai_key
            self.client = OpenAI(api_key=self.api_key)
            self.model = "gpt-4o-mini"
            logger.info("Using OpenAI API")
        else:
            logger.error("Neither GROQ_API_KEY nor OPENAI_API_KEY found in environment variables")
            raise ValueError("GROQ_API_KEY or OPENAI_API_KEY is required")
    
    def analyze_quiz(self, quiz_content):
        """
        Analyze quiz content and extract the task
        
        Args:
            quiz_content: HTML or text content of the quiz
        
        Returns:
            Dictionary with task analysis
        """
        try:
            prompt = f"""Analyze this quiz content and extract:
1. The main task/question
2. Any URLs or files to download
3. The submit URL
4. The expected answer format (boolean, number, string, file, JSON object)
5. Step-by-step instructions to solve it

Quiz content:
{quiz_content}

Respond in JSON format:
{{
    "task": "description of the task",
    "download_urls": ["url1", "url2"],
    "submit_url": "submission endpoint",
    "answer_format": "type of answer expected",
    "steps": ["step1", "step2", ...]
}}
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes quiz tasks and extracts structured information."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            logger.info("Quiz analysis completed successfully")
            return result
        
        except Exception as e:
            logger.error(f"Error analyzing quiz: {str(e)}")
            return None
    
    def solve_task(self, task_description, data_context):
        """
        Use LLM to solve a specific task
        
        Args:
            task_description: Description of the task
            data_context: Any data or context needed
        
        Returns:
            Solution to the task
        """
        try:
            prompt = f"""Task: {task_description}

Data/Context:
{data_context}

Provide the answer directly. If it's a calculation, show your work briefly then give the final answer.
If it requires data analysis, describe your approach and provide the result.
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert data analyst. Provide accurate, concise answers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1  # Low temperature for consistency
            )
            
            solution = response.choices[0].message.content
            logger.info("Task solution generated")
            return solution
        
        except Exception as e:
            logger.error(f"Error solving task: {str(e)}")
            return None
    
    def extract_answer(self, solution, expected_format):
        """
        Extract the final answer from the solution
        
        Args:
            solution: LLM's solution text
            expected_format: Expected format (number, string, boolean, etc.)
        
        Returns:
            Formatted answer
        """
        try:
            prompt = f"""Extract the final answer from this solution and format it as {expected_format}.

Solution:
{solution}

Return ONLY the answer value, nothing else. No explanation.
For numbers, return just the number.
For strings, return just the string without quotes.
For booleans, return true or false.
For JSON, return the JSON object.
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You extract and format answers precisely."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Try to convert to appropriate type
            if expected_format == "number":
                try:
                    # Try int first, then float
                    if '.' in answer:
                        return float(answer)
                    else:
                        return int(answer)
                except:
                    return answer
            elif expected_format == "boolean":
                return answer.lower() in ['true', 'yes', '1']
            elif expected_format in ["json", "object"]:
                import json
                try:
                    return json.loads(answer)
                except:
                    return answer
            
            return answer
        
        except Exception as e:
            logger.error(f"Error extracting answer: {str(e)}")
            return solution  # Return original solution as fallback
