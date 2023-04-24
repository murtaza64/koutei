import subprocess
import json

def load_word_map():
    output = subprocess.run([
        "node", 
        "-e",
        '''
        import('/home/murtaza/jpp/wordMap.js').then((module) => 
            console.log(JSON.stringify(
                Object.fromEntries(
                    module.default.default("/home/murtaza/jpp/public/words.txt")
                )
            ))
        )
        '''
    ], capture_output=True).stdout
    return json.loads(str(output, 'utf-8'))

word_map = load_word_map()
