'''Read multiple musicxml files using xml.etree.ElementTree library
Get all tag names for creating a database'''

import xml.etree.ElementTree as ET
import sqlite3

from requests import get

# create a table
con = sqlite3.connect('music.sqlite')
cursor = con.cursor()


tree = ET.parse('sqlite3_practice\\xmlsamples\\ActorPreludeSample.musicxml')
root = tree.getroot()
# print(root.tag) # output: score-partwise

# collect all the deepest level tags into a set, to remove duplicate
# this is for creating the table columns later on
tags = set()
texts = []
# helper method recursively check each sub-tag till find .text
def check(element):  
    # I used the following code to locate some bugs inside the xml file
    if element.text is None:         
        print(f'OOPS! {element.tag} has None text')
        return
        
    # when tag has sub-tags, the 'text' is a long space string 
    # such as "         ", so use strip() to remove all spaces first
    if element.text.strip() == "":
        # print(f 'GO DOWN {element.tag} for ')
        for kid in element:
            check(kid)
    else:        
        # print(f'{element.tag}: {element.text}')
        tag = element.tag
        text = element.text        
        tags.add(tag)
        texts.append(text)     
    return tags, texts

# get 'score-part' tags from XML file
content = root.findall('part-list/score-part') # return a list of 'score-part' tag
# print(content)
# for entry in content:
#     check(entry)   


# check each tag group, if a word is repeated often, create a new table for that category if necessary
# print(texts) 
# ouptput is not repeated often ['Piccolo', 'Picc.', 'score', 'Picc. (V2k)', '1', '73', '80', '0', 'Flutes', 'Fl.', 'score', 'Fl. (V2k)', 'wind.flutes.flute', '2', '74',...]
# print(tags) 
# output: {'pan', 'part-abbreviation', 'volume', 'midi-channel', 'instrument-sound', 'group', 'part-name', 'midi-program', 'instrument-name'}

# creat a table using the tags as column names:
# cursor.executescript('''
#     DROP TABLE IF EXISTS AP;
#     CREATE TABLE AP (
#     id integer primary key autoincrement not null unique,
#     volume text,
#     pid text,    
#     "group" text,
#     "part-abbreviation" text,
#     "instrument-sound" text,
#     "midi-channel" text,
#     "part-name" text, 
#     "midi-program" text, 
#     "instrument-name" text);''')



# helper method recursively check each sub-tag till find .text
def get_variables(element, dic):   
    # get pid from the attibute of Score-part tag only once by check dic length
    if len(dic) == 0:
        pid = element.attrib
        dic['a'] = pid.get('id')

    # I used the following code to locate some bugs inside the xml file
    if element.text is None:         
        print(f'OOPS! {element.tag} has None text')
        
    # when tag has sub-tags, the 'text' is a long space string 
    # such as "         ", so use strip() to remove all spaces first
    elif element.text.strip() == "":
        print('NEED ONE MORE LOOP DOWN')
        for kid in element:
             get_variables(kid,dic)
            
    else:     
        # print(f' {element.tag}: {element.text}')
        tag = element.tag
        text = element.text
        dic[tag] = text
        print('GO TO THE FINAL RETURN')
        return   
       
    print(f'before final return -> {dic}')
    return dic     
   
for entry in content[:2]:
    dic = get_variables(entry, dic={})
    print(dic)

# use all tags to create a table 
for entry in content: 
    # each entry needs a brand new empty dic 
    dic = get_variables(entry, dic={})
    # get all variables 
    pid = dic.get("a", "0")
    part_abrv = dic.get('part-abbreviation', "")
    group = dic.get('group', "")
    volume = dic.get('volume', "")
    midi_channel = dic.get('midi-channel', "")
    instrument_sound = dic.get('instrument-sound', "")
    part_name = dic.get('part-name', "")
    midi_program = dic.get('midi-program', "")
    instrument_name = dic.get('instrument-name', "")

    # add into table
    cursor.execute('''INSERT INTO AP 
    ("pid", "part-abbreviation", volume,  "group","midi-channel", "instrument-sound" , "part-name" , "midi-program", "instrument-name")
    VALUES (?,?,?,?,?,?,?,?,?);''', (pid, part_abrv, volume,  group,midi_channel, instrument_sound, part_name, midi_program, instrument_name) )
    con.commit()


con.close()
 

    

