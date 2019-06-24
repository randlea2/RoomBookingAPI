# imported modules
from flask import Flask, jsonify, request, render_template, redirect, abort
# import testing function from test_mode.py
from test_mode import test
# import database module
import sqlite3

# api framework
app = Flask(__name__)
database = "booking.db"


class Event:

    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity

    def get_name(self):
        return self.name

    def get_capacity(self):
        return self.capacity


class Room:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity

    def get_name(self):
        return self.name

    def get_capacity(self):
        return self.capacity


class Timetable:

    @staticmethod
    def get_slot(room, day, time):
            return Timetable.create_timetable(room)[day][time]


    @staticmethod
    def get_days():
        return ["Mon", "Tues", "Wed", "Thurs", "Fri"];

    @staticmethod
    def get_time_slots():
        return ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]

    @staticmethod
    def get_rooms():
        rooms = []
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            result = cursor.execute("SELECT * from rooms").fetchall()
            for room in result:
                current_room = Room(room[0], room[1])
                rooms.append(current_room)
            return rooms

    @staticmethod
    def create_timetable(room):
        try:
            # initialize timetable
            dic = {}
            days = Timetable.get_days()
            time_slots = Timetable.get_time_slots()
            # create the room list with all the rooms in room_file.txt
            # no events at the start
            with sqlite3.connect(database) as connection:
                cursor = connection.cursor()
                result = cursor.execute("SELECT * from timetable where name = ?", (room,)).fetchone()
                i = 1
                for day in days:
                    dic[day] = {}
                    for time in time_slots:
                        dic[day][time] = result[i].split()[time_slots.index(time)]
                    i += 1

            return dic
        except:
            return "There are no rooms registered!"


class API:

    def __init__(self):
        app.run(host="127.0.0.1", port="5000", threaded=True)

    @app.route("/", methods=["GET", "POST"])
    def display_timetable():
        if request.method == "POST":
            option = request.values.get('redirect')
            if option == "room_timetable":
                return redirect("/timetable/room")
            elif option == "availability":
                return redirect("/timetable/available")
            elif option == "test_mode":
                return redirect("/timetable/admin/test/mode")
            elif option == "room_list":
                return redirect("/timetable/rooms")
            elif option == "error_handling":
                return redirect("/timetable/admin/test/error")
            elif option == "add_room":
                return redirect("/timetable/room/add")
            else:
                return redirect("/timetable/book")
        else:
            return render_template("index.html")

    # error handling
    # not found
    @app.errorhandler(404)
    def page_not_found(page):
        uri_list = []
        for rule in app.url_map.iter_rules():
            if ":" not in rule.rule:
                uri_list.append(rule.rule)
        return render_template('404.html', uri_list=uri_list), 404

    # server fault
    @app.errorhandler(500)
    def overload(page):
        print(page)
        return render_template('500.html'), 500

    # bad request
    @app.errorhandler(400)
    def bad_request(page):
        return render_template('400.html'), 400

    @app.route("/timetable/room", methods=["POST", "GET"])
    def room_timetable():
        if request.method == "POST":
            try:
                room_number = request.values.get('room')
                return render_template("timetable.html", timetable=Timetable.create_timetable(room_number),room_number=room_number, time_slots=Timetable.get_time_slots(), days=Timetable.get_days())
            except:
                return "There are currently no rooms!"
        else:
            return render_template("room.html", room_names=Timetable.get_rooms())

    @app.route("/timetable/book", methods=["GET", "POST", "PUT"])
    def book_room():
        try:
            if request.method == "POST":
                # check if form data or json
                if request.get_json() is None:
                    room = request.values.get('room')
                    time = request.values.get('time')
                    day = request.values.get('day')
                    event = request.values.get('event')
                    with sqlite3.connect(database) as connection:
                        cursor = connection.cursor()
                        result = cursor.execute("SELECT * from timetable where name = ?", (room,)).fetchone()
                        time_index = Timetable.get_time_slots().index(time)
                        day_index = Timetable.get_days().index(day) + 1
                        current_day_events = result[day_index].split()
                        current_event = current_day_events[time_index]
                        if current_event == "Free":
                            current_day_events[time_index] = event
                            update_query = 'UPDATE timetable set {} = ? where name = ?'.format(day)
                            str_day_events = " ".join(current_day_events)
                            cursor.execute(update_query, (str_day_events, room))
                            check = cursor.execute("SELECT * from timetable where name = ?", (room,)).fetchall()
                            return "Room {} has been booked for {} on {} at {}".format(room, event, day, time)
                        else:
                            return "Room {} is not available on {} at {}".format(room, day, time)
                else:
                    booking_details = request.get_json()
                    # get the booking information from json passed to server
                    room = booking_details["room"]
                    day = booking_details["day"]
                    time = booking_details["time"]
                    event = booking_details["event"]
                    with sqlite3.connect(database) as connection:
                        cursor = connection.cursor()
                        result = cursor.execute("SELECT * from timetable where name = ?", (room,)).fetchone()
                        time_index = Timetable.get_time_slots().index(time)
                        day_index = Timetable.get_days().index(day) + 1
                        current_day_events = result[day_index].split()
                        current_event = current_day_events[time_index]
                        if current_event == "Free":
                            current_day_events[time_index] = event
                            update_query = 'UPDATE timetable set {} = ? where name = ?'.format(day)
                            str_day_events = " ".join(current_day_events)
                            cursor.execute(update_query, (str_day_events, room))
                            check = cursor.execute("SELECT * from timetable where name = ?", (room,)).fetchall()
                            return "Room {} has been booked for {} on {} at {}".format(room, event, day, time)
                        else:
                            return "Room {} is not available on {} at {}".format(room, day, time)
            else:
                return render_template("book.html", time_slots=Timetable.get_time_slots(), days=Timetable.get_days(), rooms=Timetable.get_rooms())
        except:
            return "There are no rooms currently!"

    @app.route('/timetable/available', methods=["GET", "POST"])
    def index():
        try:
            if request.method == 'POST':
                    # get form data
                    room = request.values.get('room')
                    time = request.values.get('time')
                    day = request.values.get('day')
                    time_slot = Timetable.get_slot(room, day, time)
                    # check if time slot is free or not
                    if time_slot == "Free":
                        return "<h2> Result: Available  </h2> {} is available for {} at {}".format(room, day, time)
                    else:
                        return "<h2> Result: Not Available </h2> {} has event: {} on {} at {}".format(room, time_slot, day, time)
            else:
                return render_template("available.html", time_slots=Timetable.get_time_slots(), days=Timetable.get_days(),
                                       rooms=Timetable.get_rooms())
        except:
            return "There are no rooms currently!"

    @app.route("/timetable/rooms", methods=["GET"])
    def rooms():
        room_list = []
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            result = cursor.execute("SELECT * FROM rooms").fetchall()
            for room in result:
                room_list.append(room)
        return render_template("room_list.html", room_list=room_list)

    @app.route("/timetable/room/add", methods=["GET", "POST"])
    def add_room():
        if request.method == "POST":
            try:
                # get room number from form
                name = request.values.get('name')
                capacity = int(request.values.get('capacity'))
                with sqlite3.connect(database) as connection:
                    cursor = connection.cursor()
                    # check if room already exist
                    check = cursor.execute("SELECT * FROM rooms where name = ?", (name,)).fetchone()
                    if check is not None:
                        return "Room {} already exist....".format(name)
                    else:
                        # initialize the timetable to be free
                        default_timetable = "Free " * 10
                        cursor.execute(''' INSERT OR IGNORE INTO rooms values(?, ?)''', (name, capacity,))
                        cursor.execute(''' INSERT OR IGNORE INTO timetable values(?, ?,?, ?, ? ,?)''', (name, default_timetable, default_timetable, default_timetable, default_timetable, default_timetable))
                        return "Room: {} successfully added!".format(name)
            except Exception as e:
                if e.__class__.__name__ == "value_error":
                    return "Please enter a number...."
                else:
                    return "Somethings went wrong, please try again...."
        else:
            return render_template("add_room.html")





    @app.route("/timetable/room/<string:room_number>", methods=["GET"])
    def fetch_room(room_number):
        # testing purposes may or may not be used
        # different response depending which user agent is requesting data e.g browser, command line
        if "python" in str(request.user_agent):
            return jsonify(Timetable.createTimetable(room_number))
        else:
            return render_template("timetable.html", timetable=Timetable.create_timetable(room_number),
                                   time_slots=Timetable.get_time_slots(), days=Timetable.get_days())

    @app.route("/timetable/<string:room_number>&<string:day>&<string:time>", methods=["get"])
    def check_timetable(room_number, day, time):
        # check the availability of a room
        time_slot = Timetable.create_timetable(room_number)[day][time]
        if time_slot == "free":
            return "<h2> result </h2> {} is available for {} at {}".format(room_number, day, time)
        else:
            return "<h2> result </h2> {} has event: {} on {} at {}".format(room_number, time_slot, day, time)

    @app.route("/timetable/admin/test/mode", methods=["GET", "POST"])
    def run_test_mode():
        if request.method == "POST":
            # try except if a number not entered
            # get number of request from user
            request_number = int(request.values.get('request_number'))
            # call the test function from imported test_mode.py
            return test(request_number)
        else:
            return render_template("test.html")

    @app.route("/timetable/admin/test/error", methods=["GET", "POST"])
    def generate_error():
        if request.method == "POST":
            # get error number from form
            error_number = int(request.values.get('error_choice'))
            abort(error_number)
        else:
            return render_template("error.html")


if __name__ == "__main__":
    # create database tables if not exist
    init_connection = sqlite3.connect(database)
    init_cursor = init_connection.cursor()
    init_cursor.execute('''CREATE TABLE if not exists  rooms (
    name primary key,
    capacity integer default 0)''')
    init_cursor.execute('''create table if not exists  timetable (
    name primary key,
    Mon text,
    Tues text,
    Wed text,
    Thurs text,
    Fri text )''')
    init_connection.close()
    # start api
    API()
