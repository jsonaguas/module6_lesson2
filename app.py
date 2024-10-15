from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, Schema, ValidationError
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
ma = Marshmallow(app)

def get_db_connection():
    db_name = 'ecom'
    user = 'root'
    password = '@3$p@2o2O'
    host = 'localhost'
    
    try:
        conn = mysql.connector.connect(
            user=user, 
            password=password, 
            host=host, 
            database=db_name)
        print("Connection to the MySQL DB successful")
        return conn
    except Error as e:
        print(f"Error: '{e}'") 
        return None

class MemberSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    age = fields.Integer(required=True)
    class Meta:
        fields = ('id', 'name', 'age')


class WorkoutSchemma(ma.Schema):
    sesson_id = fields.Integer(dump_only=True)
    member_id = fields.Integer(dump_only=True)
    session_date = fields.Date(required=True)
    session_time = fields.String(required=True)
    activity = fields.String(required=True)
    class Meta:
        fields = ('session_id', 'member_id', 'session_date', 'session_time', 'activity')


member_schema = MemberSchema()
members_schema = MemberSchema(many=True)
workout_schema = WorkoutSchemma()
workouts_schema = WorkoutSchemma(many=True)

@app.route('/')
def home():
    return 'Welcome to the home page'

@app.route('/members', methods=['POST'])
def add_member():
    try:
        member= member_schema.load(request.json)

    except ValidationError as err:
        return jsonify(err.messages), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}),500
    
    try:
        cursor = conn.cursor()
        query = "INSERT INTO Members (name, age) VALUES (%s, %s)"
        cursor.execute(query, (member['name'], member['age']))

        conn.commit()
        return jsonify({"message": "Member added successfully"}), 201
    except Error as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    finally:
        cursor.close()
        conn.close()

        
@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}),500
    
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM members WHERE id=%s", (id,))
    one_member = cursor.fetchone()
    cursor.close()
    conn.close()

    if one_member:
        return member_schema.jsonify(one_member)
    else:
        return jsonify({"error": "Member not found"}), 404

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    try:
        member = member_schema.load(request.json)

    except ValidationError as err:
        return jsonify(err.messages), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}),500
    
    try:
        cursor = conn.cursor()
        query = "UPDATE Members SET name=%s, age=%s WHERE id=%s"
        cursor.execute(query, (member['name'], member['age'], id))
        conn.commit()
        return jsonify({"message": "Member updated successfully"}), 200
    except Error as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    
    finally:
        cursor.close()
        conn.close()


@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}),500
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Members WHERE id=%s", (id,))
        conn.commit()
        return jsonify({"message": "Member deleted successfully"}), 200
    except Error as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/workoutsessions', methods=['GET'])
def get_workouts():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}),500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM WorkoutSessions")
    workouts = cursor.fetchall()
    cursor.close()
    conn.close()

    return workouts_schema.jsonify(workouts)

@app.route('/members/<int:member_id>/sessions', methods=['POST'])
def add_workout(member_id):
    try:
        workout= workout_schema.load(request.json)

    except ValidationError as err:
        return jsonify(err.messages), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}),500
    
    try:
        cursor = conn.cursor()
        query = '''INSERT INTO WorkoutSessions (session_date, session_time, activity) 
        VALUES (%s, %s, %s) WHERE member_id=%s'''
        cursor.execute(query, (workout['session_date'], workout['session_time'], workout['activity'], member_id))

        conn.commit()
        return jsonify({"message": "Workout added successfully"}), 201
    except Error as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/members/<int:member_id>/sessions', methods=['PUT'])
def update_workout(member_id):
    try:
        modify = member_schema.load(request.json)

    except ValidationError as err:
        return jsonify(err.messages), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}),500
    
    try:
        cursor = conn.cursor()
        query = "UPDATE WorkoutSessions SET session_date=%s, session_time=%s, activity = %s WHERE id=%s"
        cursor.execute(query, (modify['session_date'], modify['session_time'], modify['activity'], member_id))
        conn.commit()
        return jsonify({"message": "Member updated successfully"}), 200
    except Error as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    
    finally:
        cursor.close()
        conn.close()



@app.route('/members/<int:member_id>/sessionsbymember', methods=['GET'])
def get_workout_member(member_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}),500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM WorkoutSessions WHERE member_id=%s", (member_id,))
    sessions = cursor.fetchall()
    cursor.close()
    conn.close()

    return workouts_schema.jsonify(sessions)


if __name__ == '__main__':
    app.run(debug=True)