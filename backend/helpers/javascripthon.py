
import subprocess
import os
import re
import codecs

def compileJsthon(filePath):
    subprocess.run(["python", "-m", "metapensiero.pj", filePath], shell=True, check=True)
    directory = os.path.dirname(filePath)
    outputJsPath = f"{filePath[:-3]}.js"
    outputMapPath = f"{filePath[:-3]}.js.map"
    outputJsFile = codecs.open(outputJsPath, mode="r", encoding="utf-8")
    js ='\r\n'.join(outputJsFile.readlines())
    # add `./` and `.js` to imports (to make them functional in js)
    js = re.sub(r"from '([^']*?)'", r"from './\1.js'", js)
    # 🙈 jsthon outputs `None` in place of `null` sometimes
    js = f"const None = null\r\n{js}"
    # 🙊 jsthon doesn't convert `list` calls?
    js = f"const list = Array.from\r\n{js}"
    outputJsFile.close()
    outputMapFile = open(outputMapPath, mode="r", encoding="utf-8")
    mapFile ='\r\n'.join(outputMapFile.readlines())
    outputMapFile.close()
    os.remove(f"{filePath[:-3]}.js")
    os.remove(f"{filePath[:-3]}.js.map")
    outputDict = {}
    outputDict['js'] = js
    outputDict['map'] = mapFile
    return outputDict

    
