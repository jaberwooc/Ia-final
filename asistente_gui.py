import speech_recognition as sr
import pyttsx3
import datetime
import pywhatkit
import chistesESP as c
import subprocess
import pandas as pd
import pickle
from scipy.stats import poisson
from tkinter import *
from PIL import Image
import threading as tr

main_window = Tk()
main_window.title('cortana IA')
main_window.geometry('800x400')
main_window.resizable(0,0)
main_window.configure(bg='#000000')
gif_path = 'images/R.gif'
info_gif =  Image.open(gif_path) 
gif_frame = info_gif.n_frames
fondo_list = [PhotoImage(file=gif_path,format=f'gif -index {i}') for i in range(gif_frame)] 
label = Label(main_window)
label.pack()

def animated_gif(index):
        frame = fondo_list[index]
        index += 1
        if index == gif_frame:
            index = 0
        label.configure(image=frame)
        main_window.after(100,animated_gif,index)

animated_gif(0)
name = "cortana"
listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice",voices[0].id)
dict_table = pickle.load(open('dict_table','rb'))
df_historical_data = pd.read_csv('clean_fifa_worldcup_matches.csv')
df_fixture = pd.read_csv('clean_fifa_worldcup_fixture.csv')
df_home = df_historical_data[['HomeTeam', 'HomeGoals', 'AwayGoals']]
df_away = df_historical_data[['AwayTeam', 'HomeGoals', 'AwayGoals']]
df_home = df_home.rename(columns={'HomeTeam':'Team', 'HomeGoals': 'GoalsScored', 'AwayGoals': 'GoalsConceded'})
df_away = df_away.rename(columns={'AwayTeam':'Team', 'HomeGoals': 'GoalsConceded', 'AwayGoals': 'GoalsScored'})
df_team_strength = pd.concat([df_home, df_away], ignore_index=True).groupby(['Team']).mean()
df_fixture_group_48 = df_fixture[:48].copy()
df_fixture_knockout = df_fixture[48:56].copy() 
df_fixture_quarter = df_fixture[56:60].copy()
df_fixture_semi = df_fixture[60:62].copy()
df_fixture_final = df_fixture[62:].copy()


for voice in voices:
    print(voice)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def mundial(home,away):

    
    if home in df_team_strength.index and away in df_team_strength.index:
     
        lamb_home = df_team_strength.at[home,'GoalsScored'] * df_team_strength.at[away,'GoalsConceded']
        lamb_away = df_team_strength.at[away,'GoalsScored'] * df_team_strength.at[home,'GoalsConceded']
        prob_home, prob_away, prob_draw = 0, 0, 0
        for x in range(0,11): 
            for y in range(0, 11):
                p = poisson.pmf(x, lamb_home) * poisson.pmf(y, lamb_away)
                if x == y:
                    prob_draw += p
                elif x > y:
                    prob_home += p
                else:
                    prob_away += p
        
        points_home = 3 * prob_home + prob_draw
        points_away = 3 * prob_away + prob_draw
        return (points_home, points_away)
    else:
        return (0, 0)



def prediccion_fasesgrps():

 
    for group in dict_table:
        teams_in_group = dict_table[group]['Team'].values
        df_fixture_group_6 = df_fixture_group_48[df_fixture_group_48['home'].isin(teams_in_group)]
        for index, row in df_fixture_group_6.iterrows():
            home, away = row['home'], row['away']
            points_home, points_away = mundial(home, away)
            dict_table[group].loc[dict_table[group]['Team'] == home, 'Pts'] += points_home
            dict_table[group].loc[dict_table[group]['Team'] == away, 'Pts'] += points_away

        dict_table[group] = dict_table[group].sort_values('Pts', ascending=False).reset_index()
        dict_table[group] = dict_table[group][['Team', 'Pts']]
        dict_table[group] = dict_table[group].round(0)
    return(dict_table)

for group in dict_table:
    group_winner = dict_table[group].loc[0, 'Team']
    runners_up = dict_table[group].loc[1, 'Team']
    df_fixture_knockout.replace({f'Winners {group}':group_winner,
                                 f'Runners-up {group}':runners_up}, inplace=True)

df_fixture_knockout['winner'] = '?'

def get_winner(df_fixture_updated):
    for index, row in df_fixture_updated.iterrows():
        home, away = row['home'], row['away']
        points_home, points_away = mundial(home, away)
        if points_home > points_away:
            winner = home
        else:
            winner = away
        df_fixture_updated.loc[index, 'winner'] = winner
    return df_fixture_updated



def update_table(df_fixture_round_1, df_fixture_round_2):
    for index, row in df_fixture_round_1.iterrows():
        winner = df_fixture_round_1.loc[index, 'winner']
        match = df_fixture_round_1.loc[index, 'score']
        df_fixture_round_2.replace({f'Winners {match}':winner}, inplace=True)
    df_fixture_round_2['winner'] = '?'
    return df_fixture_round_2


     



def listen():
    try:
        with sr.Microphone() as source:
            speak ("Hola en que te puedo ayudar..")
            voice = listener.listen(source)
            rec = listener.recognize_google(voice,language='es-ES')
            rec = rec.lower()

            if name in rec:
             print(rec)

    except:
        pass
    return rec

def run():
        rec = listen()
        if "reproduce" in rec:
            music = rec.replace('reproduce', ' ')
            pywhatkit.playonyt(music)
            speak(music)

        elif "busca" in rec:
            bus = rec.replace('busca', ' ')
            pywhatkit.search(bus)
            speak('Buscando' + bus)

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
            
        elif "abrir consola" in rec:
            abrir = rec.replace('abrir', ' ')
            speak("abriendo " + abrir)
            subprocess.Popen('C:\\Windows\\System32\\cmd.exe')
       
        elif "abrir control panel" in rec:
            abrir = rec.replace('abrir', ' ')
            speak("abriendo " + abrir)
            subprocess.Popen('C:\\Windows\\System32\\control.exe')
            
        elif "abrir word pad" in rec:
            abrir = rec.replace('abrir', ' ')
            speak("abriendo " + abrir)
            subprocess.Popen('C:\\Windows\\System32\\write.exe')
        elif "dime un chiste" in rec:
            chiste = c.get_random_chiste()
            speak(chiste)
        
        elif "fases" in rec:
            speak(prediccion_fasesgrps())

        elif "octavos " in rec:
            prediccion_fasesgrps()
            speak(get_winner(df_fixture_knockout))

        elif "cuartos" in rec:
            prediccion_fasesgrps()
            get_winner(df_fixture_knockout)
            update_table(df_fixture_knockout, df_fixture_quarter)
            speak(get_winner(df_fixture_quarter))

        elif "semifinal" in rec:
            prediccion_fasesgrps()
            get_winner(df_fixture_knockout)
            update_table(df_fixture_knockout, df_fixture_quarter)
            get_winner(df_fixture_quarter)
            update_table(df_fixture_quarter, df_fixture_semi)
            speak(get_winner(df_fixture_semi))

        elif "quién ganará" in rec:
            prediccion_fasesgrps()
            get_winner(df_fixture_knockout)
            update_table(df_fixture_knockout, df_fixture_quarter)
            get_winner(df_fixture_quarter)
            update_table(df_fixture_quarter, df_fixture_semi)
            get_winner(df_fixture_semi)
            update_table(df_fixture_semi, df_fixture_final)
            speak(get_winner(df_fixture_final))

        else:
         speak("Vuelve a intentarlo, no reconozco: " + rec)
        return run()


button = Button(main_window,text="Escuchar",fg='white',bg='#00FF00',font=('Arial',15,'bold'),command=run)

button.pack(pady=10)
main_window.mainloop()



