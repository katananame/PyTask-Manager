import re
from django.http import HttpResponseBadRequest
from django.utils.deprecation import MiddlewareMixin


class SecurityMiddleware(MiddlewareMixin):
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|UNION|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|;|\/\*|\*\/)",
        r"('|\"|`)",
        r"(OR\s+1\s*=\s*1|AND\s+1\s*=\s*1)",
        r"(\bxp_\w+|\bsp_\w+)",
    ]
    
    XSS_PATTERNS = [
        r"(<script[^>]*>.*?</script>)",
        r"(javascript:)",
        r"(onerror\s*=)",
        r"(onload\s*=)",
        r"(<iframe[^>]*>)",
        r"(<object[^>]*>)",
        r"(<embed[^>]*>)",
    ]
    
    def process_request(self, request):
        if request.method == 'POST':
            for key, value in request.POST.items():
                if isinstance(value, str):
                    if self._contains_sql_injection(value):
                        return HttpResponseBadRequest("Обнаружена попытка SQL-инъекции")
                    if self._contains_xss(value):
                        return HttpResponseBadRequest("Обнаружена попытка XSS-атаки")
        return None
    
    def _contains_sql_injection(self, value):
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False
    
    def _contains_xss(self, value):
        for pattern in self.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False

