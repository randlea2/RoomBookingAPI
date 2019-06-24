# script for the test mode within our API 
import requests
import time
import random
import sqlite3


class Client:

    def __init__(self):
        #  uri to send request
        self.uri_post = "http://127.0.0.1:5000/timetable/book"
        self.uri_get  = "http://127.0.0.1:5000/timetable/rooms"

    def get_random_day(self):
        # return a random day
        days = ["Mon", "Tues", "Wed", "Thurs", "Fri"];
        index = random.randint(0, len(days) - 1)
        return days[index]

    def get_random_time(self):
        times = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
        index = random.randint(0, len(times) - 1)
        return times[index]

    def get_random_event(self):
        events = ["lab", "lecture", "tutorial"]
        index = random.randint(0, len(events) - 1)
        return events[index]

    def get_random_room(self):
        try:
            rooms = []
            with sqlite3.connect('booking.db') as connection:
                cursor = connection.cursor()
                result = cursor.execute("SELECT * FROM rooms").fetchall()
                for room in result:
                    rooms.append(room[0])
            index = random.randint(0, len(rooms) - 1)
            return rooms[index]
        except:
            return None

    def test_mode(self, request_number):
        log_html = "<h2> test mode </h2>"
        log_html += "<p> generating {} randomly generated request.......</p>".format(request_number)
        log = "generating {} randomly generated request.......\n".format(request_number)
        start_time = time.time()
        log_html += "<p> test started at {} </p>".format(start_time)
        log += "test started at {}\n".format(start_time)
        i = 0
        while i <= request_number:
            # get request or post
            if i % 2 or not self.get_random_room():
                response = requests.get(self.uri_get)
                log_html += "<p> {} 		status: {} {} reply: get request successful </p>".format(time.time(), response.status_code, response.reason)
                log += "{} 		status: {} {} reply: get request successful\n".format(time.time(), response.status_code, response.reason)
                # update only when successful request is made
                i += 1
            # if there are rooms registered
            elif self.get_random_room():
                day = self.get_random_day()
                time_slot = self.get_random_time()
                event = self.get_random_event()
                room = self.get_random_room()
                response = requests.post(url=self.uri_post, json={"room": room, "day": day, "time": time_slot, "event": event})
                log_html += "<p> {} 		status: {} {}, reply: {}</p>".format(time.time(), response.status_code, response.reason, response.text)
                log += "{} 		status: {} {}, reply: {}\n".format(time.time(), response.status_code, response.reason, response.text)
                i += 1
            # random delay between request
            random_delay = random.uniform(0.0, 0.5)
            time.sleep(random_delay)

        end_time = time.time()
        log_html += "<p> test finished at {} </p>".format(end_time)
        log += "test finished at {}\n".format(end_time)
        total_time = end_time
        log_html += "<p> test took {} to complete! </p>".format(total_time)
        log += "test took {} to complete!".format(total_time)
        print(log)
        return log_html


def test(request_number):
    client = Client()
    return client.test_mode(request_number)


def main():
    client = Client()
    print(client.test_mode(10))


if __name__ == "__main__":
    main()



