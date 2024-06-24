import datetime
import speech_recognition as sr
import pyttsx3
import wikipedia
import webbrowser
import wolframalpha
import warnings

# Suppress the GuessedAtParserWarning
warnings.filterwarnings("ignore", category=UserWarning, message="No parser was explicitly specified")

# Initialize the text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
activationWord = 'computer'

# Register Chrome browser
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))

appId='5R49J7-J888YX9J2V'
WolframClient=wolframalpha.Client(appId)

def speak(text, rate=120):
    print(f"Assistant: {text}")
    engine.setProperty('rate', rate)
    engine.say(text)
    engine.runAndWait()

def parseCommand():
    listener = sr.Recognizer()
    print('Listening for a command')

    with sr.Microphone() as source:
        listener.pause_threshold = 2
        input_speech = listener.listen(source)

    try:
        print('Recognizing speech...')
        query = listener.recognize_google(input_speech, language='en_gb')
        print(f'You said: {query}')
    except sr.UnknownValueError:
        print('I did not quite catch that')
        speak('I did not quite catch that')
        return 'None'
    except sr.RequestError as e:
        print(f'Could not request results; {e}')
        speak(f'Could not request results; {e}')
        return 'None'
    except Exception as exception:
        print('An error occurred')
        speak('An error occurred')
        print(exception)
        return 'None'
    return query

def search_wikipedia(query=''):
    searchResults = wikipedia.search(query)
    if not searchResults:
        print('No result found')
        return 'No result received'
    try:
        wikiPage = wikipedia.page(searchResults[0])
    except wikipedia.DisambiguationError as error:
        wikiPage = wikipedia.page(error.options[0])
    except wikipedia.PageError:
        print('No matching page found on Wikipedia.')
        return 'No matching page found on Wikipedia.'
    except Exception as e:
        print(f'An error occurred: {e}')
        return f'An error occurred: {e}'
    
    print(wikiPage.title)
    wikiSummary = str(wikiPage.summary)
    return wikiSummary

def listOrDict(var):
    if isinstance(var, list):
        return var[0]['plaintext']
    else:
        return var['plaintext']
 
def search_wolframAlpha(query=''):
    response=WolframClient.query(query)
    if response['@success']=='false':
        return 'Could not computer'
    else:
        result=''
        pod0=response['pod'][0]
        pod1=response['pod'][1]
        if (('result') in pod1['@title'].lower()) or (pod1.get('@primary', 'false') == 'true') or ('definition' in pod1['@title'].lower()):
            result=listOrDict(pod1['subpod'])
            return result.split('(')[0]
        else:
            question=listOrDict(pod0['subpod'])
            return question.split('(')[0]
            speak('Computation failed. Querying universal databank')
            return search_wikipedia(question)


if __name__ == '__main__':
    speak('All systems nominal.')
    while True:
        query = parseCommand().lower().split()
        if query[0] == activationWord:
            query.pop(0)
            # Greeting
            if query[0] == 'say':
                if 'hello' in query:
                    speak('Hello, how may I assist you today?')
                else:
                    query.pop(0)
                    speech = ' '.join(query)
                    speak(speech)
            # Navigation
            elif query[0] == 'go' and query[1] == 'to':
                speak("Redirecting...")
                query = ' '.join(query[2:])
                webbrowser.get('chrome').open_new(query)

            # Wikipedia
            elif query[0] == 'wikipedia':
                query = ' '.join(query[1:])
                speak('Searching the universal databank')
                result = search_wikipedia(query)
                speak(result)

            #Wolfman alpha
            if query[0]=='compute' or query[0]=='computer':
                query=' '.join(query[1:])
                speak('Computing')
                try:
                    result=search_wolframAlpha(query)
                    speak(result)
                except:
                    speak('Unable to compute.')
            
            # Note taking
            if query[0] == 'log':
                speak('Ready to record your note')
                newNote = ' '.join(parseCommand()).lower()  # Assuming parseCommand returns a list of words
                try:
                    now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                except AttributeError as e:
                    speak(f"Error occurred: {e}")
                    now = "unknown_time"
                try:
                    with open(f'note_{now}.txt', 'w') as newFile:
                        newFile.write(now)
                        newFile.write(' ')
                        newFile.write(newNote)
                    speak('Note written')
                except Exception as e:
                    speak(f"Failed to write note: {e}")
            if query[0] == 'exit':
                speak('Goodbye')
                break
