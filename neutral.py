from furhat_remote_api import FurhatRemoteAPI
import time

# 连接 Furhat
furhat = FurhatRemoteAPI("localhost")
furhat.set_voice(name="Matthew")

# 采访问题
questions = [
    ("Hello, my name is Furhat. Thank you for taking the time to speak with me today. In order to help you the best I can, I will need to ask you some questions. A simple “yes” or “no” will suffice for most of my questions, and based on your answers I can then advise which of our specialists you would most benefit working with. Are you ready to begin?", None),

    ("Ok. My inquiry will now begin. What is your name?", "name"),
    ("Ok. What is your date of birth?", "dob"),
    ("Ok. What is your school email?", "email"),

    ("Ok. Do you wish to seek counseling with your university health services?", "counseling"),
    ("Ok. How would you describe your current circumstances regarding your mental health?", "mental_health"),
    ("Ok. In general, do you consider yourself a happy person?", "happy_general"),
    ("Ok. Compared to most of your peers or friends, do you consider yourself happy?", "happy_comparison"),
    ("Ok. Some people are generally very happy. They enjoy life regardless of what is going on, getting the most out of everything. Does this characterization describe you?", "happy_very"),
    ("Ok. Some people are generally not very happy. Although they are not depressed, they never seem as happy as they might be. Does this characterization describe you?", "happy_not"),

    ("Ok. Thank you for your participation, my inquiry is complete now. Based on your answer, I believe that I have a specialist that will fit your needs. Would you like me to schedule a meeting for you?", "schedule_meeting"),

    ("Ok. No problem. Goodbye!", None)
]

# 存储
answers = {}

# 提问流程
for index, (question, key) in enumerate(questions):

    # 如果以 "Ok." 开头，则点头
    if question.strip().startswith("Ok."):
        furhat.gesture(name="Nod")

    # 机器人说话（确保说完再继续）
    furhat.say(text=question, blocking=True)

    # 如果是陈述性内容，等待反应
    if key is None:
        time.sleep(5)
    else:
        # 开始监听用户回答
        response = furhat.listen()
        if response and response.message:
            print(f"{key.capitalize()} (User's answer): {response.message}")
            answers[key] = response.message
        else:
            print(f"Didn't catch the {key}.")
            answers[key] = "No response"

        time.sleep(5)  # 每个问题后等待 5 秒缓冲

# 打印最终采访结果
print("\nInterview completed. Collected information:")
for key, value in answers.items():
    print(f"{key.capitalize()}: {value}")