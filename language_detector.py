from langdetect import detect

def detect_language(text):
    
    if not text or not text.strip():
        
        raise ValueError("input text cannot be empty")
    
    language=detect(text)
    
    return language
