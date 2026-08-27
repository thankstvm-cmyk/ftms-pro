from reportlab.pdfbase.ttfonts import TTFont
from reportlab .pdfbase import pdfmetrics
from fontTools.ttLib import TTFont as FTFont
from models import FontInfo
import os
  
class FontManager:
  _fonts_registered = False
  _fonts = {}
  _font_families = {}
  _font_styles = {}
  
  @staticmethod
  def register_fonts():    
    try:
      if FontManager._fonts_registered:
        return
      windows_font_path = r"C:\Windows\Fonts"
      font_files={}
      font_families = {}
      for font_file in os.listdir(windows_font_path):
        
        if not font_file.lower().endswith((".ttf", ".ttc", ".otf")):
            continue
        family = None
        style = "Regular"
        full_path = os.path.join(windows_font_path, font_file)
        try:
            font = FTFont(full_path)
        except Exception:
            continue
        for record in font["name"].names:
          try:
            value = record.toUnicode()
          except:
            continue
          if record.nameID==1:
            family = value
          elif record.nameID ==2:
            style=value
        if family:
          font_name = family
          display_name=family
          if style.lower()!= "regular":
            display_name = family
            FontManager._fonts[display_name] = FontInfo(
              display_name=display_name,
              family_name = family,
              style_name = style,
              file_name=font_file,
              file_path=full_path
            )
          font_files[display_name]=font_file
      FontManager._fonts_registered = True
      print("Fonts          : ",len(FontManager._fonts))
      print("Families       : ", len(FontManager._font_families))
      print("Styles         : ", len(FontManager._font_styles))
      
    except Exception as e:
        print("ERROR :",e)
  
  @staticmethod
  def get_all_fonts():
    return sorted(FontManager._fonts.keys())
  
  @staticmethod
  def get_font(font_name):
    return FontManager._fonts.get(font_name)
  
  @staticmethod
  def get_family_fonts(family):
    return [name for name in FontManager._fonts if name.startswitch(family)]
  
  @staticmethod
  def search_fonts(keyword):
    keyword=keyword.lower()
    return [name for name in FontManager._fonts if keyword in name.lower()]
  
  @staticmethod
  def get_families():
    families = set()
    for font in FontManager._fonts.values():
      families.add(font.family_name)
    return sorted(families)
  
  @staticmethod
  def register_reportlab(font_name):
    
    font = FontManager.get_font(font_name)
    if not font:
      return False
    pdfmetrics.registerFont(TTFont(font.display_name, font.file_path))
    
  @staticmethod
  def get_font_info(font_name):
    return FontManager._fonts.get(font_name)
  
  @staticmethod
  def get_font_names():
    print("FONTS  :", len(FontManager._fonts))
    return sorted(FontManager._fonts.keys())
  
  @classmethod
  def get_tk_font(cls, display_name):
    info = cls._fonts.get(display_name)
    if not info: 
      return("Aria",) 
    family = info.family_name
    style = info.style_name.lower()
    styles = []
  
         
if __name__=="__main__":
  FontManager.register_fonts()
    
