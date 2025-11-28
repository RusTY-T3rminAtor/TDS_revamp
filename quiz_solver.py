import logging
import requests
import time
from datetime import datetime, timedelta
from browser_handler import BrowserHandler
from llm_handler import LLMHandler
from data_processor import DataProcessor
import json
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class QuizSolver:
    """Main class for solving quiz tasks"""
    
    def __init__(self, email, secret):
        self.email = email
        self.secret = secret
        self.browser = BrowserHandler()
        self.llm = LLMHandler()
        self.data_processor = DataProcessor()
        self.start_time = None
        self.time_limit = timedelta(minutes=3)
    
    def solve_quiz_chain(self, initial_url):
        """
        Solve a chain of quizzes starting from initial URL
        
        Args:
            initial_url: The first quiz URL to solve
        """
        self.start_time = datetime.now()
        current_url = initial_url
        quiz_count = 0
        
        logger.info(f"Starting quiz chain from: {initial_url}")
        
        while current_url and self._within_time_limit():
            quiz_count += 1
            logger.info(f"\n{'='*50}")
            logger.info(f"Solving Quiz #{quiz_count}: {current_url}")
            logger.info(f"{'='*50}")
            
            # Solve the current quiz
            result = self.solve_single_quiz(current_url)
            
            if not result:
                logger.error(f"Failed to solve quiz at {current_url}")
                break
            
            # Check if we got a new URL to continue
            current_url = result.get('next_url')
            
            if result.get('correct'):
                logger.info(f"✓ Quiz #{quiz_count} solved correctly!")
                if current_url:
                    logger.info(f"Proceeding to next quiz: {current_url}")
                else:
                    logger.info("Quiz chain completed successfully!")
                    break
            else:
                logger.warning(f"✗ Quiz #{quiz_count} answer was incorrect")
                reason = result.get('reason', 'No reason provided')
                logger.warning(f"Reason: {reason}")
                
                if current_url:
                    logger.info("Skipping to next quiz URL provided")
                else:
                    logger.info("No new URL provided, quiz chain ended")
                    break
        
        elapsed = datetime.now() - self.start_time
        logger.info(f"\nQuiz session completed. Total time: {elapsed.total_seconds():.2f}s")
        logger.info(f"Quizzes attempted: {quiz_count}")
        
        # Cleanup
        self.browser.close()
    
    def solve_single_quiz(self, quiz_url):
        """
        Solve a single quiz
        
        Args:
            quiz_url: URL of the quiz to solve
        
        Returns:
            Result dictionary from submission
        """
        try:
            # Step 1: Fetch quiz content using headless browser
            logger.info("Step 1: Fetching quiz page...")
            page_content = self.browser.fetch_page_content(quiz_url)
            
            if not page_content:
                logger.error("Failed to fetch page content")
                return None
            
            # Step 2: Extract text from the result div
            text_content = self.browser.get_text_content(quiz_url, "#result")
            if not text_content:
                # Fallback to parsing HTML
                soup = BeautifulSoup(page_content, 'html.parser')
                result_div = soup.find(id='result')
                text_content = result_div.get_text(strip=True) if result_div else page_content
            
            logger.info(f"Quiz content extracted (length: {len(text_content)} chars)")
            logger.info(f"Quiz content preview:\n{text_content[:500]}...")
            
            # Step 3: Analyze quiz using LLM
            logger.info("Step 2: Analyzing quiz with LLM...")
            analysis = self.llm.analyze_quiz(text_content)
            
            if not analysis:
                logger.error("Failed to analyze quiz")
                return None
            
            logger.info(f"Task: {analysis.get('task', 'Unknown')}")
            logger.info(f"Submit URL: {analysis.get('submit_url', 'Unknown')}")
            logger.info(f"Answer format: {analysis.get('answer_format', 'Unknown')}")
            
            # Step 4: Process any required data
            logger.info("Step 3: Processing data...")
            data_context = self._process_data_requirements(analysis)
            
            # Step 5: Solve the task
            logger.info("Step 4: Solving the task...")
            solution = self.llm.solve_task(
                analysis.get('task', ''),
                data_context
            )
            
            logger.info(f"Solution: {solution}")
            
            # Step 6: Extract and format the answer
            logger.info("Step 5: Extracting final answer...")
            answer = self.llm.extract_answer(
                solution,
                analysis.get('answer_format', 'string')
            )
            
            logger.info(f"Final answer: {answer}")
            
            # Step 7: Submit the answer
            logger.info("Step 6: Submitting answer...")
            submit_url = analysis.get('submit_url')
            
            if not submit_url:
                logger.error("No submit URL found in quiz")
                return None
            
            result = self._submit_answer(submit_url, quiz_url, answer)
            
            return result
        
        except Exception as e:
            logger.error(f"Error solving quiz: {str(e)}", exc_info=True)
            return None
    
    def _process_data_requirements(self, analysis):
        """
        Process any data requirements (downloads, scraping, etc.)
        
        Args:
            analysis: Quiz analysis from LLM
        
        Returns:
            Processed data context
        """
        data_context = "No additional data required."
        
        try:
            download_urls = analysis.get('download_urls', [])
            
            if not download_urls:
                return data_context
            
            all_data = []
            
            for url in download_urls:
                logger.info(f"Processing data from: {url}")
                
                # Download file
                filepath = self.data_processor.download_file(url)
                
                if not filepath:
                    continue
                
                # Process based on file type
                file_ext = filepath.suffix.lower()
                
                if file_ext == '.pdf':
                    content = self.data_processor.read_pdf(filepath)
                    if isinstance(content, list):  # Tables
                        for i, table in enumerate(content):
                            all_data.append(f"Table {i+1}:\n{table.to_string()}")
                    else:  # Text
                        all_data.append(content)
                
                elif file_ext == '.csv':
                    df = self.data_processor.read_csv(filepath)
                    if df is not None:
                        all_data.append(f"CSV Data:\n{df.to_string()}")
                
                elif file_ext in ['.xlsx', '.xls']:
                    df = self.data_processor.read_excel(filepath)
                    if df is not None:
                        all_data.append(f"Excel Data:\n{df.to_string()}")
                
                else:
                    # Try to read as text
                    try:
                        with open(filepath, 'r') as f:
                            all_data.append(f.read())
                    except:
                        all_data.append(f"Binary file: {filepath.name}")
            
            if all_data:
                data_context = "\n\n".join(all_data)
            
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
        
        return data_context
    
    def _submit_answer(self, submit_url, quiz_url, answer):
        """
        Submit answer to the quiz endpoint
        
        Args:
            submit_url: URL to submit to
            quiz_url: Original quiz URL
            answer: The answer to submit
        
        Returns:
            Response from server
        """
        try:
            payload = {
                "email": self.email,
                "secret": self.secret,
                "url": quiz_url,
                "answer": answer
            }
            
            logger.info(f"Submitting to: {submit_url}")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                submit_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Response: {json.dumps(result, indent=2)}")
                
                return {
                    'correct': result.get('correct', False),
                    'next_url': result.get('url'),
                    'reason': result.get('reason')
                }
            else:
                logger.error(f"Submission failed: {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Error submitting answer: {str(e)}")
            return None
    
    def _within_time_limit(self):
        """Check if we're still within the time limit"""
        if not self.start_time:
            return True
        
        elapsed = datetime.now() - self.start_time
        remaining = self.time_limit - elapsed
        
        if remaining.total_seconds() > 0:
            logger.info(f"Time remaining: {remaining.total_seconds():.1f}s")
            return True
        else:
            logger.warning("Time limit exceeded!")
            return False
