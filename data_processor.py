import pandas as pd
import numpy as np
import requests
import io
import logging
from bs4 import BeautifulSoup
import PyPDF2
import base64
import json
import re
from pathlib import Path

logger = logging.getLogger(__name__)

class DataProcessor:
    """Handles data sourcing, processing, and analysis"""
    
    def __init__(self):
        self.download_dir = Path("downloads")
        self.download_dir.mkdir(exist_ok=True)
    
    def download_file(self, url, filename=None):
        """
        Download a file from URL
        
        Args:
            url: URL to download from
            filename: Optional filename to save as
        
        Returns:
            Path to downloaded file
        """
        try:
            logger.info(f"Downloading file from: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            if not filename:
                # Extract filename from URL or Content-Disposition
                if 'Content-Disposition' in response.headers:
                    cd = response.headers['Content-Disposition']
                    filename = re.findall('filename="?(.+)"?', cd)
                    filename = filename[0] if filename else 'download'
                else:
                    filename = url.split('/')[-1] or 'download'
            
            filepath = self.download_dir / filename
            filepath.write_bytes(response.content)
            logger.info(f"File downloaded to: {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            return None
    
    def read_pdf(self, filepath, page_num=None):
        """
        Read content from PDF file
        
        Args:
            filepath: Path to PDF file
            page_num: Specific page number (1-indexed), or None for all pages
        
        Returns:
            Text content or list of tables
        """
        try:
            logger.info(f"Reading PDF: {filepath}")
            
            # Try to extract tables using tabula
            try:
                import tabula
                if page_num:
                    tables = tabula.read_pdf(str(filepath), pages=page_num)
                else:
                    tables = tabula.read_pdf(str(filepath), pages='all')
                
                if tables:
                    logger.info(f"Extracted {len(tables)} table(s) from PDF")
                    return tables
            except Exception as e:
                logger.warning(f"Tabula extraction failed: {str(e)}")
            
            # Fallback to text extraction
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = []
                
                if page_num:
                    page = pdf_reader.pages[page_num - 1]  # Convert to 0-indexed
                    text_content.append(page.extract_text())
                else:
                    for page in pdf_reader.pages:
                        text_content.append(page.extract_text())
                
                logger.info("PDF text extracted")
                return '\n'.join(text_content)
        
        except Exception as e:
            logger.error(f"Error reading PDF: {str(e)}")
            return None
    
    def read_csv(self, filepath_or_url):
        """Read CSV file or URL into DataFrame"""
        try:
            if isinstance(filepath_or_url, str) and filepath_or_url.startswith('http'):
                df = pd.read_csv(filepath_or_url)
            else:
                df = pd.read_csv(filepath_or_url)
            
            logger.info(f"CSV loaded: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
        except Exception as e:
            logger.error(f"Error reading CSV: {str(e)}")
            return None
    
    def read_excel(self, filepath, sheet_name=0):
        """Read Excel file into DataFrame"""
        try:
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            logger.info(f"Excel loaded: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
        except Exception as e:
            logger.error(f"Error reading Excel: {str(e)}")
            return None
    
    def scrape_webpage(self, url):
        """
        Scrape content from a webpage
        
        Args:
            url: URL to scrape
        
        Returns:
            Dictionary with text and structured data
        """
        try:
            logger.info(f"Scraping webpage: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text
            text = soup.get_text(separator='\n', strip=True)
            
            # Extract tables
            tables = []
            for table in soup.find_all('table'):
                df = pd.read_html(str(table))[0]
                tables.append(df)
            
            result = {
                'text': text,
                'tables': tables,
                'links': [a.get('href') for a in soup.find_all('a', href=True)]
            }
            
            logger.info("Webpage scraped successfully")
            return result
        
        except Exception as e:
            logger.error(f"Error scraping webpage: {str(e)}")
            return None
    
    def analyze_data(self, df, operation):
        """
        Perform data analysis operations
        
        Args:
            df: DataFrame to analyze
            operation: Type of analysis (sum, mean, filter, sort, etc.)
        
        Returns:
            Analysis result
        """
        try:
            if operation['type'] == 'sum':
                column = operation.get('column')
                return df[column].sum() if column else df.sum()
            
            elif operation['type'] == 'mean':
                column = operation.get('column')
                return df[column].mean() if column else df.mean()
            
            elif operation['type'] == 'filter':
                condition = operation.get('condition')
                # This would need more sophisticated parsing
                return df.query(condition)
            
            elif operation['type'] == 'groupby':
                group_col = operation.get('group_column')
                agg_col = operation.get('agg_column')
                agg_func = operation.get('agg_function', 'sum')
                return df.groupby(group_col)[agg_col].agg(agg_func)
            
            logger.info(f"Analysis completed: {operation['type']}")
            return None
        
        except Exception as e:
            logger.error(f"Error analyzing data: {str(e)}")
            return None
    
    def create_visualization(self, df, viz_type='bar'):
        """
        Create a visualization and return as base64 image
        
        Args:
            df: DataFrame to visualize
            viz_type: Type of visualization (bar, line, scatter, etc.)
        
        Returns:
            Base64 encoded image
        """
        try:
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if viz_type == 'bar':
                df.plot(kind='bar', ax=ax)
            elif viz_type == 'line':
                df.plot(kind='line', ax=ax)
            elif viz_type == 'scatter':
                df.plot(kind='scatter', ax=ax)
            else:
                df.plot(ax=ax)
            
            plt.tight_layout()
            
            # Save to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close()
            
            # Encode to base64
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            data_uri = f"data:image/png;base64,{img_base64}"
            
            logger.info("Visualization created successfully")
            return data_uri
        
        except Exception as e:
            logger.error(f"Error creating visualization: {str(e)}")
            return None
