import random
import time

from Data.data_manager import *
from config import _russian_roles
from GPT_Requests.request_gpt import gpt


class Mafia:
    def __init__(self, prompt: dict, names: list, send_message_callback):
        self.prompt = prompt
        self.names = names
        self.game = True
        self.mafia = []
        self.sheriff = ""

        self.kills = None
        self.kicked = None
        self.kicked_role = None
        self.checked = None

        self.all_kills = []
        self.all_kicked = []

        self.vote_count = {

        }

        self.status_players = {

        }

        self.winner = ""
        self.send_message_callback = send_message_callback
        self.create_role_data()


        self.scene = {
        }

        self.scene_update()

    def scene_update(self):
        self.scene = {
            'Участники': f"В игре участвуют {len(self.names)} игроков: {', '.join(self.names)}. Из них затаились {len(self.mafia)} мафии. Вам предстоит найти их. Представьтесь пожалуйста.",
            'Ночь мафии': 'Начинается ночь, город засыпает, просыпается мафия, мафия выбирает кого убить',
            "Выбор мафии": f"Мафия сделала выбор",
            'Ночь шерифа': 'Мафия засыпает. Просыпается шериф выбирает кого он хочет проверить',
            'Выбор шерифа': f'Шериф сделал выбор, шериф засыпает. Наступает новый день, город просыпается, кроме {self.kills}',
            'Обсуждение': 'Обсуждение',
            'Обсуждение2': 'Продолжаем обсуждение. Последний раунд перед голосованием.',
            'Голосование': 'Обсуждение закончилось, начинает голосование, все игроки обязаны назвать имя игрока. Игрок, набравший большинство голосов выбывает.',
            'Конец голосование': f'Голосование закончилось, игрок {self.kicked} Выбывает из игры. Он был - {self.kicked_role}',
        }

    def create_role_data(self):
        clear()  # Очистка всех пользователей, которые были ранее
        available_names = self.names.copy()

        # роли мафии
        num_mafia = int(len(self.names) / 4)
        for _ in range(num_mafia):
            mafia = random.choice(available_names)
            available_names.remove(mafia)
            self.mafia.append(mafia)

        # роль шерифа
        if available_names:
            self.sheriff = random.choice(available_names)

        # Инициализируем статус и голоса для каждого игрока
        for name in self.names:
            self.status_players.setdefault(name, "play")
            self.vote_count.setdefault(name, 0)

        # Создаем данные для каждого игрока
        for name in self.names:
            role = "mafia" if name in self.mafia else "sheriff" if name == self.sheriff else "peace"
            DataCreate(name, role, self.prompt, self.mafia if role == "mafia" else None)
        DataCreate("general", "general", self.prompt)



    def kill(self, name: str):
        if name in self.status_players:  # Проверяем, существует ли игрок
            self.status_players[name] = "dead"
            self.all_kills.append(name)
            change_status(name, "dead")
            self.scene_update()
            print("\n", self.status_players, "\n")

            # Проверка на конец игры после убийства
            self.check_game_over()
        else:
            print(f"Ошибка: Игрок {name} не найден в списке игроков.")

    def kick(self, name: str):
        if name in self.status_players:  # Проверяем, существует ли игрок
            self.status_players[name] = "kicked"
            self.all_kicked.append(name)
            self.kicked = name
            self.kicked_role = "Мафия" if name in self.mafia else "Шериф" if name == self.sheriff else "Мирный"
            change_status(name, "kicked")
            self.scene_update()
            print("\n", self.status_players, "\n")

            # Проверка на конец игры после изгнания
            self.check_game_over()
        else:
            print(f"Ошибка: Игрок {name} не найден в списке игроков.")



    def answer_to_scene(self, name, scene):
        player_history = check_info(name, "history")
        player_history_str = "\n".join(player_history) if player_history else ""

        role = check_info(name, "role")
        role_name = _russian_roles[role]

        if role == "mafia":
            goals = "Ваша цель - устранить всех мирных жителей, оставаясь нераскрытым."
        elif role == "sheriff":
            goals = "Ваша цель - вычислить членов мафии и помочь мирным жителям их казнить. Ты можешь не рассказывать игрокам свою роль до появлении важной информации. Например: ты узнал игрока с ролью мафии или узнал, что игрока, которого подозревают, имеет роль мирный, таким образом ты можешь его спасти. Как действовать тебе решать"
        else:
            goals = "Ваша цель - выявить всех членов мафии и помочь другим мирным жителям их казнить."

        if scene == "Обсуждение":
            task = f"Вам нужно участвовать в обсуждении, анализировать поведение других игроков и делиться своими подозрениями.Не убивай своих напарников {", ".join(self.mafia)}. Не выбирайте умерших или выгнанных игроков, {", ".join([x for x in self.names if self.status_players[x] != 'play'])}"
        elif scene == "Обсуждение2":
            task = f"Финальное раунд перед голосованием. Делитесь подозрениями и выдвигайте претендентов на вылет. Не убивай своих напарников {", ".join(self.mafia)}. Не выбирайте умерших или выгнанных игроков, {", ".join([x for x in self.names if self.status_players[x] != 'play'])}"
        elif scene == "Голосование":
            podtask1 = f"Старайся не голосовать за своих напарников мафии {", ".join(self.mafia)}. Можешь голосовать за них, если их подозревают и чтобы отвлечь игроков от тебя"
            podtask2 = f"Вам нужно проголосовать за игрока, которого вы подозреваете в том, что он мафия. Сейчас идет голосование. Ваша задача - проголосовать за игрока, которого вы считаете мафией. Напишите *только имя* этого игрока и ничего больше (например: Егор). Не убивай своих напарников {", ".join(self.mafia)}. Не выбирайте умерших или выгнанных игроков, {", ".join([x for x in self.names if self.status_players[x] != 'play'])} "
            task = podtask1 + podtask2 if role == "mafia" else podtask2
        elif scene == "Ночь мафии" and role == "mafia":
            task = f"Вам нужно выбрать игрока, которого вы хотите убить. Напиши только имя и ничего больше (например: Егор). Не убивай своих напарников {", ".join(self.mafia)}. Не выбирайте умерших или выгнанных игроков, {", ".join([x for x in self.names if self.status_players[x] != 'play'])}"
        elif scene == "Ночь шерифа" and role == "sheriff":
            task = f"Вам нужно выбрать игрока, которого вы хотите проверить и узнать его роль. Напиши только имя и ничего больше (например: Егор). Не убивай своих напарников {", ".join(self.mafia)}. Не выбирайте умерших или выгнанных игроков, {", ".join([x for x in self.names if self.status_players[x] != 'play'])}"
        else:
            task = "В этой сцене вам нужно просто ждать и наблюдать."

        game_state = f"В игре участвуют: {', '.join([n for n in self.names if self.status_players[n] == 'play'])}. "
        dead_players = [n for n in self.names if self.status_players[n] == 'dead']
        kick_players = [n for n in self.all_kicked]
        if dead_players:
            game_state += f"Были убиты мафией: {', '.join(dead_players)}. "
        if kick_players:
            game_state += f"Выгнанные: {', '.join(kick_players)}. "


        context = f"Вы - {name}, {role_name}.\n{goals}\n{task}\n{game_state}\nИстория {name}:\n{player_history_str}"

        return (self.scene[scene], context, check_info(name, "prompt"))

    def check_game_over(self):
        """Проверка окончание игры"""
        alive_mafia = sum(1 for name in self.mafia if self.status_players.get(name) == "play")
        alive_peaceful = sum(
            1 for name in self.names if self.status_players.get(name) == "play" and name not in self.mafia
        )

        if alive_mafia >= alive_peaceful:
            self.game = False
            self.winner = "Мафия"

            self.send_message_callback("general", check_info("general", "role"),"*Игра окончена! Победила Мафия.*")
            return True

        if alive_mafia == 0:
            self.game = False
            self.winner = "Мирные жители"

            self.send_message_callback("general", check_info("general", "role"),"*Игра окончена! Победила Мафия.*")

            return True

        return False  # Игра не окончена

    def handle_voting(self):
        """голосование"""
        self.vote_count.clear()
        for name in self.names:
            if self.status_players[name] == "play":
                self.vote_count[name] = 0  # Счетчик голосов для каждого игрока

        for name in self.names:
            if self.status_players[name] == "play":
                response_data = self.answer_to_scene(name, "Голосование")
                response = gpt(self.scene["Голосование"], response_data[1], response_data[2])

                self.send_message_callback(name, check_info(name, "role"), response)
                addhistory(name, response, "Голосование")

                try:
                    # Извлекаем имя игрока, за которого голосуют
                    vote = [n for n in self.names if n in response][-1]


                    if vote:
                        self.vote_count[vote] += 1
                except Exception as e:
                    print(f"Ошибка при голосовании: {e}")

        # Определяем игрока с наибольшим количеством голосов
        if self.vote_count:
            player_with_max_votes = max(self.vote_count, key=self.vote_count.get)
            max_votes_count = self.vote_count[player_with_max_votes]

            if max_votes_count > 0:
                result = max(self.vote_count, key=self.vote_count.get)
                self.kick(result)
                print(f"Игрок {result} выгнан с {self.vote_count[result]} голосами.")
            else:
                print("Ошибка при голосовании")
        else:
            print("Голосование не состоялось. Никто не голосовал.")

    def handle_mafia_night(self):
        """Обрабатывает сцену ночи мафии."""
        mafia_votes = {}
        for name in self.names:
            mafia_votes.setdefault(name, 0)
        for name in self.names:
            if name in self.mafia and self.status_players[name] == "play":
                response_data = self.answer_to_scene(name, "Ночь мафии")
                response = gpt(self.scene["Ночь мафии"], response_data[1], response_data[2])

                self.send_message_callback(name, check_info(name, "role"), response)

                try:

                    kill_target = [n for n in self.names if n in response][-1]

                    if kill_target:
                        mafia_votes[kill_target] += 1

                    addhistory(
                        name,
                        f"{response}. Ты выбрал игрока - {kill_target} для убийства.",
                        "Ночь мафии",
                    )
                    print(f"Мафия {name} выбрала {kill_target}")

                except IndexError:
                    print(f"Ошибка: Не удалось извлечь имя жертвы из ответа мафии {name}")

        # цель с наибольшим количеством голосов
        if mafia_votes:
            if max(mafia_votes, key=mafia_votes.get) != 0:
                most_voted = max(mafia_votes, key=mafia_votes.get)
                self.kills = most_voted
                print(f"Большинство голосов мафии за {most_voted}")


                if self.kills:
                    self.kill(self.kills)
        else:
            print("Мафия не выбрала никого для убийства.")
            self.kills = None

    def run(self):
        """Запускает игровой цикл."""

        print(f"{", ".join(self.mafia)}(мафия)\t{self.sheriff}(шериф)\n")

        # Сцена представления участников (только один раз в начале)
        start_scene = "Участники"

        self.send_message_callback("general", check_info("general", "role"), f"\n{self.scene[start_scene]}")


        print(start_scene)
        for name in self.names:
            if self.status_players[name] == "play":
                response_data = self.answer_to_scene(name, start_scene)
                response = gpt(self.scene[start_scene], response_data[1], response_data[2])

                self.send_message_callback(name, check_info(name, "role"), response)

                addhistory(name, response, start_scene)
                time.sleep(1)

        # Основной игровой цикл
        while self.game:
            for scene in self.scene:
                if not self.game:  # Проверяем, не закончилась ли игра после предыдущей сцены
                    break
                if scene != 'Участники':
                    self.send_message_callback("general", check_info("general", "role"), f"\n{self.scene[scene]}")

                    print(scene)

                    if scene == "Ночь мафии":
                        self.handle_mafia_night()  # Используем новую функцию для обработки ночи мафии
                        time.sleep(1)

                    elif scene == "Голосование":
                        self.handle_voting()  # Вызываем функцию для обработки голосования
                        time.sleep(1)

                    else:
                        for name in self.names:
                            if self.status_players[name] == "play":

                                if scene == "Ночь шерифа" and name == self.sheriff:
                                    response_data = self.answer_to_scene(name, scene)
                                    response = gpt(self.scene[scene], response_data[1], response_data[2])
                                    self.send_message_callback(name, check_info(name, "role"), response)

                                    try:
                                        self.checked = [n for n in self.names if n in response][0]
                                    except IndexError:
                                        print("Ошибка: Не удалось извлечь имя жертвы из ответа мафии")
                                        self.checked = None  # Или какое-то другое значение по умолчанию

                                    if self.checked:
                                        checked_role = "Мафия" if self.checked in self.mafia else "Мирный житель"
                                        addhistory(
                                            name,
                                            f"{response}. Ты проверил игрока {self.checked}. Его роль - {checked_role}. Ты можешь использовать эту информацию, как хочешь. Можешь всем сказать, что ты шериф и попробовать доказать это. И сказать кто мафия, а кто мирный житель.",
                                            scene,
                                        )
                                        print(self.checked)

                                elif scene == "Обсуждение":
                                    response_data = self.answer_to_scene(name, scene)
                                    response = gpt(self.scene[scene], response_data[1], response_data[2])
                                    self.send_message_callback(name, check_info(name, "role"), response)
                                    addhistory(name, response, scene)

                                elif scene == "Обсуждение2":
                                    response_data = self.answer_to_scene(name, scene)
                                    response = gpt(self.scene[scene], response_data[1], response_data[2])
                                    self.send_message_callback(name, check_info(name, "role"), response)
                                    addhistory(name, response, scene)


                                elif scene == "Конец голосования":
                                    addhistory(name, self.scene[scene], scene)
                            time.sleep(1)