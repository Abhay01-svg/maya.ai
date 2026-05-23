"""
Response Formatter Module
Formats AI responses for better user experience
"""

class ResponseFormatter:
    def __init__(self):
        self.formatters = {
            'general_chat': self._format_general_response,
            'coding': self._format_coding_response,
            'analysis': self._format_analysis_response,
            'calculation': self._format_calculation_response,
        }
    
    def format_response(self, response, intent='general_chat', metadata=None):
        """Format response based on intent and metadata"""
        formatter = self.formatters.get(intent, self._format_general_response)
        return formatter(response, metadata)
    
    def _format_general_response(self, response, metadata):
        """Format general chat responses"""
        if isinstance(response, dict):
            return response.get('response', str(response))
        return str(response)
    
    def _format_coding_response(self, response, metadata):
        """Format coding responses with syntax highlighting hints"""
        if isinstance(response, dict):
            code = response.get('response', str(response))
        else:
            code = str(response)
        
        # Add code block markers if not present
        if '```' not in code and any(lang in code.lower() for lang in ['python', 'javascript', 'html', 'css', 'java', 'cpp']):
            code = f"```\n{code}\n```"
        
        return code
    
    def _format_analysis_response(self, response, metadata):
        """Format analysis responses"""
        if isinstance(response, dict):
            return response.get('response', str(response))
        return str(response)
    
    def _format_calculation_response(self, response, metadata):
        """Format calculation responses"""
        if isinstance(response, dict):
            result = response.get('response', str(response))
        else:
            result = str(response)
        
        # Add calculation formatting
        if '=' not in result and result.replace('.', '').replace('-', '').isdigit():
            result = f"Result: {result}"
        
        return result

# Global instance
response_formatter = ResponseFormatter()
