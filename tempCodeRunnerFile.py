
        elif "hora" in rec:
            hora = datetime.datetime.now().strftime('%I:%M %p')
            speak('Son las ' + hora)
            
            
       
        elif "significa" in rec:
            sig = rec.replace('significa', ' ')
            info = pywhatkit.info(sig)
            speak('Esto es lo que encontre en wikipedia acerca de: ' + sig)
            speak(info)
            
        elif "abrir la calculadora" in rec:
            abrir = rec.replace('abrir', ' ')
            speak("abriendo " + abrir)
            subprocess.Popen('C:\\Windows\\System32\\calc.exe')
            
        elif "abrir notepad" in rec:
            abrir = rec.replace('abrir', ' ')
            speak("abriendo " + abrir)
            subprocess.Popen('C:\\Windows\\System32\\notepad.exe')
            
        elif "abrir paint" in rec:
            abrir = rec.replace('abrir', ' ')
            speak("abriendo " + abrir)
            subprocess.Popen('C:\\Windows\\System32\\mspaint.exe')
            
        elif "abrir recortadora" in rec:
            abrir = rec.replace('abrir', ' ')
            speak("abriendo " + abrir)
            subprocess.Popen('C:\\Windows\\System32\\SnippingTool.exe')
            
        elif "abrir consola" in re