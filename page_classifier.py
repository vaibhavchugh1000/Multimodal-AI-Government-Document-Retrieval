# page classifier module

def inspect_page(page) : 
    
   text=page.get_text()
   images=page.get_images(full=True)
   drawings=page.get_drawings()
   
   return {
       
       "text_present" : bool(text),
       "image_present" : bool(images),
       "image_count" : len(images),
       "drawing_count"  : len(drawings)
   }
   
def classify_page(page_info) : 
    
    if page_info["text_present"] and not page_info["image_present"] and page_info["drawing_count"]<100 : 
        
        return "text"
    
    elif page_info["image_present"] and not page_info["text_present"] and page_info["drawing_count"]<100 : 
        
        return "image"
    
    else : 
        
        return "complex"