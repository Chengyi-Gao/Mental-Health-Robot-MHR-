from furhat_remote_api import FurhatRemoteAPI
import time

# 连接 Furhat
furhat = FurhatRemoteAPI("localhost")
furhat.set_voice(name="Brain")

# 回答记录
answers = {}

# 正/负关键词
positive_words = ["yes", "yeah", "of course", "sure", "absolutely", "definitely", "i do", "i am", "good", "nice", "great"]
negative_words = ["no", "not really", "i don’t", "i am not", "nah", "never", "not good", "bad", "sad", "unhappy"]

# 开场
furhat.gesture(name="BigSmile", blocking=False)
furhat.say(text="Hello, my name is Furhat. Thank you for taking the time to speak with me today.", blocking=True)

furhat.gesture(name="BrowRaise", blocking=False)
furhat.say(text="In order to help you the best I can, I will need to ask you some questions.", blocking=True)

furhat.gesture(name="Nod", blocking=False)
furhat.say(text='A simple "yes" or "no" will suffice for most of my questions, and based on your answers I can then advise which of our specialists you would most benefit working with.', blocking=True)


# Q1
furhat.say(text="Are you ready to begin?", blocking=True)
response = furhat.listen()
answers["ready"] = response.message if response and response.message else "No response"
print(f"Ready: {answers['ready']}")
time.sleep(3)

# Q2
furhat.gesture(name="Smile", blocking=False)
furhat.gesture(name="Nod", blocking=False)
furhat.say(text="Great! My inquiry will now begin. What is your name?", blocking=True)
response = furhat.listen()
user_name = response.message if response and response.message else "there"
answers["name"] = user_name
print(f"Name: {user_name}")
time.sleep(3)

# Q3
furhat.gesture(name="BigSmile", blocking=False)
furhat.say(text=f"What a lovely name!", blocking=True)

furhat.gesture(name="Wink", blocking=False)
furhat.say(text=f"It’s nice to meet you {user_name}.", blocking=True)

furhat.gesture(name="BrowRaise", blocking=False)
furhat.say(text="What is your date of birth?", blocking=True)

response = furhat.listen()
answers["dob"] = response.message if response and response.message else "No response"
print(f"DOB: {answers['dob']}")
time.sleep(3)

# Q4
furhat.say(text=f"{user_name}, could you tell me your school email?", blocking=True)
response = furhat.listen()
answers["email"] = response.message if response and response.message else "No response"
print(f"Email: {answers['email']}")
time.sleep(3)

# Q5
furhat.say(text="Wonderful. Do you wish to seek counseling with your university health services?", blocking=True)
response = furhat.listen()
answers["counseling"] = response.message if response and response.message else "No response"
print(f"Counseling: {answers['counseling']}")
time.sleep(3)

# Q6
furhat.gesture(name="Thoughtful", blocking=False)
furhat.gesture(name="BrowFrown", blocking=False)
furhat.say(text="Great! Would you describe your current circumstances regarding your mental health as good?", blocking=True)

response = furhat.listen()
msg = response.message if response and response.message else "No response"
answers["mental_health"] = msg
print(f"Mental Health: {msg}")
time.sleep(3)


if any(w in msg.lower() for w in positive_words):
    furhat.gesture(name="Smile", blocking=False)
    furhat.say(text=f"I’m happy to hear that, {user_name}.", blocking=True)
else:
    furhat.gesture(name="ExpressSad", blocking=False)
    furhat.say(text=f"I’m sorry to hear that, {user_name}.", blocking=True)
time.sleep(3)


# Q7
furhat.gesture(name="Smile", blocking=False)
furhat.gesture(name="Nod", blocking=False)
furhat.say(text="In general, do you consider yourself a happy person?", blocking=True)

response = furhat.listen()
msg = response.message if response and response.message else "No response"
answers["happy_general"] = msg
print(f"Happiness: {msg}")
time.sleep(3)


msg_lower = msg.lower() if msg else ""
if any(w in msg_lower for w in positive_words):
    furhat.gesture(name="Wink", blocking=False)
    furhat.say(text="I’m happy to hear that.", blocking=True)
elif any(w in msg_lower for w in negative_words):
    furhat.gesture(name="BrowFrown", blocking=False)
    furhat.say(text="Sorry to hear that.", blocking=True)
else:
    furhat.gesture(name="Thoughtful", blocking=False)
    furhat.say(text="Thank you for sharing.", blocking=True)
time.sleep(3)


# Q8
furhat.gesture(name="Smile", blocking=False)
furhat.gesture(name="BrowRaise", blocking=False)
furhat.say(text="Compared to most of your peers or friends, do you consider yourself happy?", blocking=True)

response = furhat.listen()
msg = response.message if response and response.message else "No response"
answers["happy_comparison"] = msg
print(f"Peer Comparison: {msg}")
time.sleep(3)

msg_lower = msg.lower() if msg else ""
if any(w in msg_lower for w in positive_words):
    furhat.gesture(name="Nod", blocking=False)
    furhat.gesture(name="Smile", blocking=False)
    furhat.say(text="Alright, that’s good.", blocking=True)
elif any(w in msg_lower for w in negative_words):
    furhat.gesture(name="Thoughtful", blocking=False)
    furhat.gesture(name="BrowFrown", blocking=False)
    furhat.say(text="I understand, happiness can be hard to maintain.", blocking=True)
else:
    furhat.gesture(name="Nod", blocking=False)
    furhat.say(text="Thanks for your honesty.", blocking=True)
time.sleep(3)


# Q9
furhat.gesture(name="Surprise", blocking=False)
furhat.gesture(name="GazeAway", blocking=False)
furhat.say(text="Some people are generally very happy. They enjoy life regardless of what is going on, getting the most out of everything. Does this characterization describe you?", blocking=True)

response = furhat.listen()
msg = response.message if response and response.message else "No response"
answers["happy_very"] = msg
print(f"Very Happy: {msg}")
time.sleep(3)

msg_lower = msg.lower() if msg else ""
if any(w in msg_lower for w in positive_words):
    furhat.gesture(name="Oh", blocking=False)
    furhat.gesture(name="Smile", blocking=False)
    furhat.say(text="That's great to hear!", blocking=True)
elif any(w in msg_lower for w in negative_words):
    furhat.gesture(name="CloseEyes", blocking=False)
    furhat.gesture(name="Thoughtful", blocking=False)
    furhat.say(text="I totally get it, but that might be something we can work on together!", blocking=True)
else:
    furhat.gesture(name="Roll", blocking=False)
    furhat.say(text="Thanks for letting me know.", blocking=True)
time.sleep(3)


# Q10
furhat.gesture(name="Blink", blocking=False)
furhat.gesture(name="Thoughtful", blocking=False)
furhat.say(text="Some people are generally not very happy. Although they are not depressed, they never seem as happy as they might be. Does this characterization describe you?", blocking=True)

response = furhat.listen()
msg = response.message if response and response.message else "No response"
answers["happy_not"] = msg
print(f"Not Very Happy: {msg}")
time.sleep(3)

msg_lower = msg.lower() if msg else ""
if any(w in msg_lower for w in positive_words):
    furhat.gesture(name="ExpressSad", blocking=False)
    furhat.say(text=f"I'm sorry to hear that, {user_name}. I hope this doesn't impact your everyday life in a significant way.", blocking=True)
elif any(w in msg_lower for w in negative_words):
    furhat.gesture(name="BigSmile", blocking=False)
    furhat.gesture(name="Nod", blocking=False)
    furhat.say(text="I'm happy to hear that!", blocking=True)
else:
    furhat.gesture(name="BrowFrown", blocking=False)
    furhat.say(text="Thanks for telling me.", blocking=True)
time.sleep(3)


# Q11
furhat.gesture(name="Smile", blocking=False)
furhat.gesture(name="Nod", blocking=False)
furhat.say(
    text="Thank you for your participation, my inquiry is complete now. Based on your answer, I believe that I have a specialist that will fit your needs. Would you like me to schedule a meeting for you?",
    blocking=True
)

response = furhat.listen()
msg = response.message if response and response.message else "No response"
answers["schedule_meeting"] = msg
print(f"Schedule Meeting: {msg}")
time.sleep(3)


msg_lower = msg.lower() if msg else ""
if any(w in msg_lower for w in positive_words):
    furhat.gesture(name="Smile", blocking=False)
    furhat.gesture(name="Nod", blocking=False)
    furhat.say(text="Great, I will schedule the meeting and send the details to your school email. Goodbye!", blocking=True)
elif any(w in msg_lower for w in negative_words):
    furhat.gesture(name="Nod", blocking=False)
    furhat.say(text="No problem. You can always reach out if you change your mind. Goodbye!", blocking=True)
else:
    furhat.gesture(name="Thoughtful", blocking=False)
    furhat.say(text="Okay, thank you for your response. Goodbye!", blocking=True)
time.sleep(3)


# 总结
print("\nInterview Summary:")
for key, value in answers.items():
    print(f"{key.capitalize()}: {value}")