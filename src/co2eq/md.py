class MdFile:

  def __init__( self, md_txt ):
    self.md_txt = md_txt

  def number_sections( self ):
    """ add numbers to each sections """

    section_no = 1
    subsection_no = 1
    subsubsection_no = 1
    md = ""

    for line in self.md_txt.split( '\n' ):
      if line[: 3 ] == '## ' :
        sec_no = roman.toRoman( section_no )  
        line = f"#  {sec_no} {line[ 2 : ]}"
        section_no +=1 
        subsection_no = 1
        subsubsection_no = 1
      elif line[: 4 ] == '### ' :
        sec_no = f"{roman.toRoman( section_no )}.{subsection_no}"  
        line = f"##  {sec_no} {line[ 3 : ]}"
        subsection_no += 1
        subsubsection_no = 1
      elif line[: 5 ] == '#### ' :
        sec_no = f"{roman.toRoman( section_no )}.{subsection_no}.{subsubsection_no}"  
        line = f"##  {sec_no} {line[ 3 : ]}"
        subsubsection_no += 1
      md += line + '\n' 
    self.md_txt = md

  def save( self, output_file ):
    with open( output_file, 'wt', encoding='utf8' ) as f:
      f.write( self.md_txt )


   
def embed_html( html_page, height=None, width=None):
    md =  f"<p><embed src='{html}'"
    if height is not None:
      md += f" height={height}"
    if width is not None:
      md += f" width={width}"
    md += "/></p>\n\n"
    return md

