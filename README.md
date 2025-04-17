# Baby-Monitor- APP 
A project developed in IOT ( Arduino Uno Wifi Rev 2 )to identify if the baby is crying or not, using Firebase as a dabatase manager and Vs Code for the AI Model and Android Studio for The APP.
How it works: The microphone detects the sounds sends it to the server who has The AI model implemented via Wifi and analyse it and sends a response (Cry or Non-CRY sound) , then our Arduino sends the data to Firebase that sends it to the App to visualize it on the App with a notification in the background when the baby is Crying.

# DataSET 
I used two dataSets already available in Github: 
For Non_Cry audios: https://github.com/karolpiczak/ESC-50
For Crying audios: https://github.com/gveres/donateacry-corpus
