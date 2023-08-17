import subprocess
import json
from typing import TypedDict, List, Dict

def load_word_map():
    output = subprocess.run([
        "node", 
        "-e",
        # '''
        # import('/home/murtaza/jpp/wordMap.js').then((module) => 
        #     console.log(JSON.stringify(
        #         Object.fromEntries(
        #             module.default.default("/home/murtaza/jpp/public/words.txt")
        #         )
        #     ))
        # )
        # '''
        '''
        import('/mnt/c/Users/perry/JPP_Project/jpp/wordMap.js').then((module) => 
            console.log(JSON.stringify(
                Object.fromEntries(
                    module.default.default('/mnt/c/Users/perry/JPP_Project/jpp/public/words.txt')
                )
            ))
        )
        '''
    ], capture_output=True).stdout
    return json.loads(str(output, 'utf-8'))

class WordData(TypedDict):
    moras: List[str]
    pitches: List[float]
    english: str
    peak: int
    category: str
    furiganaMap: Dict[str, str]

word_map: Dict[str, WordData] = load_word_map()
