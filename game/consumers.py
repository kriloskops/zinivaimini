import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Question, Player, Reply


class GameConsumer(WebsocketConsumer):
    counter = 1
    player_points = {}
    def connect(self):
        self.accept()
        self.current_answer = None
        async_to_sync(self.channel_layer.group_add)("players", self.channel_name)
        self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'You are now connected ch!'
        }))
        #print(self.scope)

    
    def receive(self, text_data):
        data = json.loads(text_data)
        if (data["type"] == "identify.username"):
            self.username = data["username"]
            self.player_obj = Player.objects.get(username = self.username)
            self.player_obj.score = 0
            self.player_obj.active = True
            self.player_obj.save() 
            if (current_state == "game_started"):
                self.start_game(None)
            elif (current_state == "question_time"):
                c_question = todays_questions[current_question - 1]
                self.next_question({"question": todays_questions[current_question-1].question, "answers": [c_question.answer_1, c_question.answer_2, c_question.answer_3, c_question.answer_4]})
                self.send(text_data=json.dumps({
                    "type": "load_header"
                }))
            elif (current_state == "question_pause"):
                c_question = todays_questions[current_question - 1]
                self.next_question({"question": todays_questions[current_question-1].question, "answers": [c_question.answer_1, c_question.answer_2, c_question.answer_3, c_question.answer_4]})
                self.send(text_data=json.dumps({
                    "type": "load_header"
                }))
                self.end_question(None)
            print(f"{data['username']} has joined!")
        elif (data["type"] == "submit_answer"):
            #correct = todays_questions[current_question-1].correct_answer == data["answer"]
            # if (correct):
            #     self.player_obj.score += 1
            #     self.player_obj.save()
            
            # Reply.objects.create(player=self.player_obj, question=todays_questions[current_question-1], answer=data["answer"], day=current_day)
            # self.end_question(None, True, correct)
            self.current_answer = data["answer"]
            self.order_place = GameConsumer.counter
            GameConsumer.counter += 1
            self.send(text_data=json.dumps({
                "type": "waiting_screen"
            }))

    def start_game(self, event):
        self.send(text_data=json.dumps({
            "type": "start_game"
        }))
        GameConsumer.counter = 1
        #print(f"{self.username}: START GAME")


    def next_question(self, event):
        self.send(text_data=json.dumps({
            "type": "next_question",
            "question": event["question"],
            "answers": event["answers"],
            "question_number": current_question
        }))
        self.current_answer = None
        GameConsumer.counter = 1
        self.order_place = -1
        #print(f"{self.username}: NEXT QUESTION ({event['question']})({event['answers']})")

    def end_question(self, event):
        correct = todays_questions[current_question-1].correct_answer == self.current_answer
        is_empty = (self.current_answer == None)
        points_gained = 0
        if (correct):
            if (self.order_place == 1):
                points_gained = 10
            elif (self.order_place <= 6):
                points_gained = 9
            elif (self.order_place <= 16):
                points_gained = 8
            else:
                points_gained = 7

            self.player_obj.score += points_gained
            self.player_obj.save() 

        if (not is_empty):
            Reply.objects.create(player=self.player_obj, question=todays_questions[current_question-1], answer=self.current_answer, day=current_day)
        c_question = todays_questions[current_question - 1]
        self.send(text_data=json.dumps({
            "type": "end_question",
            "correct": correct,
            "score": self.player_obj.score,
            "is_empty": is_empty,
            "points_gained": points_gained,
            "correct_index": [c_question.answer_1, c_question.answer_2, c_question.answer_3, c_question.answer_4].index(todays_questions[current_question-1].correct_answer)
        }))
        # if (self.has_answered == None):
        #     return
        # if (beforehand == True):
        #     self.send(text_data=json.dumps({
        #         "type": "end_questio bxn",
        #         "correct": correct,
        #         "score": self.player_obj.score,
        #         "message": "You have answered incorrectly!" if not correct else "You have answered correctly!"
        #     }))
        #     self.has_answered = True
        # else:
        #     if (self.has_answered == False):
        #         self.send(text_data=json.dumps({
        #             "type": "end_question",
        #             "correct": correct,
        #             "score": self.player_obj.score,
        #             "message": "You didn't answer at all!" 
        #         }))

        #print(f"{self.username}: END QUESTION")

    def end_game(self, event):
        self.send(text_data=json.dumps({
            "type": "end_game"
        }))
        #print(f"{self.username}: END GAME")



    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("players", self.channel_name)
        self.player_obj.active = False
        self.player_obj.save() 
        print(f"{self.username} has disconnected!")


todays_questions = None
current_question = 0
current_state = "before_game"
current_day = 0

def loadTodaysQuestions(day:int):
    global todays_questions, current_state, current_question, current_day
    todays_questions = Question.objects.filter(day=day)
    todays_questions.order_by("order_num")
    current_question = 0
    current_state = "before_game"
    current_day = day


class AdminConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        
        # async_to_sync(self.channel_layer.group_add)("players", self.channel_name)
        self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'You are now connected to the admin!'                
        }))
        print("Admin has successfuly connected!")


    
    def receive(self, text_data):
        global current_question, todays_questions, current_state
        data = json.loads(text_data)

        match data['type']:
            case "load.questions":
                if (current_state != "before_game"):
                    self.send_error("The game has already started!")
                    return 
                print("load questions")
                loadTodaysQuestions(data["day"])

            case "start.game":
                if (current_state != "before_game"):
                    self.send_error("The game has already started!")
                    return 
                print("start.game")
                async_to_sync(self.channel_layer.group_send)(
                    "players",
                    {
                        "type": "start_game"
                    }
                )
                current_state = "game_started"


            case "next.question":
                if (current_state != "question_pause" and current_state != "game_started"):
                    self.send_error("It is not the pause between questions!")
                    return

                print("next.question")
                current_question += 1
                try:
                    c_question = todays_questions[current_question - 1]
                except IndexError:
                    self.send_error("No more questions available!")
                    print("index error", current_question, current_state)
                    for i in todays_questions:
                        print(i.question, end=" ")
                    return
                async_to_sync(self.channel_layer.group_send)(
                    "players",
                    {
                        "type": "next_question",
                        "question": c_question.question,
                        "answers": [c_question.answer_1, c_question.answer_2, c_question.answer_3, c_question.answer_4]
                    }
                )
                current_state = "question_time"



            case "end.question":
                if (current_state != "question_time"):
                    self.send_error("No question is currently active!")
                    return
                print("end.question")

                async_to_sync(self.channel_layer.group_send)(
                    "players",
                    {
                        "type": "end_question"
                    }
                )
                current_state = "question_pause"

            case "end.game":
                if (current_state == "before_game"):
                    self.send_error("The game isn't even started!")
                    return
                print("end.game")
                async_to_sync(self.channel_layer.group_send)(
                    "players",
                    {
                        "type": "end_game"
                    }
                )
                current_state = "before_game"

            case _:
                print(data)

    def send_error(self, error):
        self.send(text_data=json.dumps({
            "type": "error",
            "error": error
        }))

    # def start_game(self, event):
    #     print("bad")

    # def disconnect(self, close_code):
    #     async_to_sync(self.channel_layer.group_discard)("players", self.channel_name)
